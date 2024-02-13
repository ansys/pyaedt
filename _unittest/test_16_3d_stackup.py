import pytest


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="Test_16")
    return app


@pytest.fixture(scope="class")
def st(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    return stckp3d


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, st, local_scratch):
        self.aedtapp = aedtapp
        self.st = st
        self.local_scratch = local_scratch

    def test_01_create_stackup(self):
        self.st.dielectic_x_postion = "10mm"
        gnd = self.st.add_ground_layer("gnd1")
        self.st.add_dielectric_layer("diel1", thickness=1)
        assert self.st.thickness.numeric_value == 1.035
        assert self.st.thickness.units == "mm"
        lay1 = self.st.add_signal_layer("lay1", thickness=0.07)
        self.st.add_dielectric_layer("diel2", thickness=1.2)
        top = self.st.add_signal_layer("top")
        self.st.add_dielectric_layer("diel3", thickness=1.2)
        p1 = self.st.add_signal_layer("p1", thickness=0)
        gnd2 = self.st.add_ground_layer("gnd2", thickness=0)
        assert gnd
        assert lay1
        assert top
        assert p1
        assert gnd2
        assert len(self.st.dielectrics) == 3
        assert len(self.st.grounds) == 2
        assert len(self.st.signals) == 3
        assert self.st.start_position.numeric_value == 0.0

    def test_02_line(self):
        top = self.st.stackup_layers["top"]
        gnd = self.st.stackup_layers["gnd1"]
        line1 = top.add_trace(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)
        assert line1
        line2 = top.add_trace(
            line_length=90,
            is_electrical_length=True,
            line_width=50,
            is_impedance=True,
            line_position_x=20,
            line_position_y=20,
            frequency=1e9,
        )
        assert line1.create_lumped_port(gnd, opposite_side=True)
        assert line2
        assert line2._added_length_calcul
        assert line2.frequency.numeric_value == 1e9
        assert line2.substrate_thickness.numeric_value == 1.2
        assert abs(line1.width.numeric_value - 3.0) < 1e-9
        assert line2.permittivity.evaluated_value == 4.4
        assert line2._permittivity

    def test_03_padstackline(self):
        p1 = self.st.add_padstack("Massimo", material="aluminum")
        p1.plating_ratio = 0.7
        with pytest.raises(ValueError):
            p1.set_start_layer("non_existing_layer")
        assert p1.set_start_layer("lay1")
        assert p1.set_stop_layer("top")
        p1.set_all_pad_value(1)
        p1.set_all_antipad_value(3)
        assert p1.padstacks_by_layer["top"].layer_name == "top"
        assert p1.padstacks_by_layer["top"].pad_radius == 1
        assert p1.padstacks_by_layer["top"].antipad_radius == 3
        p1.padstacks_by_layer["top"].pad_radius = 2
        p1.padstacks_by_layer["top"].antipad_radius = 2.5
        assert p1.padstacks_by_layer["top"].pad_radius == 2
        assert p1.padstacks_by_layer["top"].antipad_radius == 2.5
        p1.num_sides = 8
        assert p1.num_sides == 8
        via = p1.add_via(50, 50)
        assert via
        assert len(self.st.padstacks) == 1

    def test_04_patch(self):
        top = self.st.stackup_layers["top"]
        gnd = self.st.stackup_layers["gnd1"]
        line1 = self.st.objects_by_layer["top"][0]
        patch = top.add_patch(
            1e9,
            patch_width=22,
            patch_length=10,
            patch_position_x=line1.position_x.numeric_value + line1.length.numeric_value,
            patch_position_y=line1.position_y.numeric_value,
        )
        assert patch.width.numeric_value == 22
        patch.set_optimal_width()
        assert patch.width.numeric_value == 91.2239398980667
        assert self.st.resize_around_element(patch)
        assert patch.create_lumped_port(gnd)

    def test_05_polygon(self):
        lay1 = self.st.stackup_layers["top"]
        gnd = self.st.stackup_layers["gnd2"]

        poly = lay1.add_polygon([[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]])
        poly2 = lay1.add_polygon([[6, 6], [6, 7], [7, 7], [7, 6]], is_void=True)
        assert poly
        assert poly2
        poly3 = gnd.add_polygon([[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]])

        poly4 = gnd.add_polygon([[6, 6], [6, 7], [7, 7], [7, 6]], is_void=True)
        assert poly3
        assert poly4

    def test_05_resize(self):
        assert self.st.resize(20)
        assert self.st.dielectric_x_position
        self.st.dielectric_x_position = "10mm"
        assert self.st.dielectric_x_position.evaluated_value == "10.0mm"
        assert self.st.dielectric_x_position.value == 0.01
        assert self.st.dielectric_x_position.numeric_value == 10.0
        assert self.st.dielectric_y_position
        self.st.dielectric_y_position = "10mm"
        assert self.st.dielectric_y_position.evaluated_value == "10.0mm"

    def test_06_hide_variables(self):
        assert self.st.dielectric_x_position.hide_variable()
        assert self.st.dielectric_x_position.read_only_variable()
        assert self.st.dielectric_x_position.hide_variable(False)
        assert self.st.dielectric_x_position.read_only_variable(False)

    def test_07_ml_patch(self):
        top = self.st.stackup_layers["top"]
        gnd = self.st.stackup_layers["gnd1"]
        width = 1e3 * 3e8 / (2 * 1e9 * ((2.2 + 1) / 2) ** (1 / 2))
        patch2 = top.ml_patch(1e9, patch_width=width, patch_position_x=0, patch_position_y=0)
        patch2.create_lumped_port(gnd, opposite_side=True)
        assert self.st.resize_around_element(patch2)

    def test_08_duplicated_parametrized_material(self):
        diel = self.st.stackup_layers["diel1"]
        assert diel.duplicated_material.permittivity
        assert diel.duplicated_material.permeability
        assert diel.duplicated_material.conductivity
        assert diel.duplicated_material.dielectric_loss_tangent
        assert diel.duplicated_material.magnetic_loss_tangent
