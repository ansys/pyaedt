import os

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt import Hfss3dLayout
from pyaedt import is_linux

test_subfolder = "T40"
original_project_name = "ANSYS-HSD_V1"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=original_project_name, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def flipchip(add_app):
    app = add_app(
        project_name="Package", design_name="FlipChip_TopBot", application=Hfss3dLayout, subfolder=test_subfolder
    )
    return app


@pytest.fixture(scope="class")
def dcir_example_project(add_app):
    app = add_app(project_name="ANSYS-HSD_V1_dcir", application=Hfss3dLayout, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch, aedtapp):
    design_name = aedtapp.design_name
    return design_name, None


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, flipchip, dcir_example_project, local_scratch, examples):
        self.aedtapp = aedtapp
        self.flipchip = flipchip
        self.dcir_example_project = dcir_example_project
        self.local_scratch = local_scratch
        self.design_name = examples[0]

    def test_01_get_components(self):
        comp = self.aedtapp.modeler.components
        assert len(comp) > 0
        assert comp["L10"].object_units == "mm"
        assert comp["L10"].angle == "4.71238898038469"
        comp["L10"].angle = "90deg"
        assert comp["L10"].angle == "90deg"
        comp["L10"].angle = "4.71238898038469"
        assert comp["L10"].location[0] == 105.99999882
        assert comp["L10"].location[1] == 44.0000009
        comp["L10"].location = [1.0, 0.0]
        assert comp["L10"].location[0] == 1.0  # bug in component location
        comp["L10"].location = [105.99999882, 44.0000009]
        assert comp["L10"].placement_layer == "1_Top"
        assert comp["L10"].part == "WE-Coil-PD4-S"
        assert comp["L10"].part_type == "Inductor"
        assert comp["L10"].set_property_value("Angle", "0deg")
        assert comp["L10"].create_clearance_on_component(1e-6)
        assert comp["L10"].absolute_angle == 0.0
        comp["L10"].enabled = False
        assert not comp["L10"].enabled
        comp["L10"].enabled = True
        assert comp["L10"].enabled
        comp["R13"].enabled = False
        assert not comp["R13"].enabled
        comp["R13"].enabled = True
        assert comp["R13"].enabled
        comp["C10"].enabled = False
        assert not comp["C10"].enabled
        comp["C10"].enabled = True

        assert comp["U1"].enabled
        assert comp["J1"].enabled

        r5 = comp["R13"]
        assert r5.model
        assert r5.model.res == "3.57kOhm"
        assert r5.model.cap == "0"
        assert r5.model.ind == "0"
        assert r5.model.is_parallel == False

    def test_02a_get_geometries(self):
        line = self.aedtapp.modeler.geometries["line_209"]
        assert line.edges
        assert isinstance(line.edge_by_point([0, 0]), int)
        assert line.points
        assert line.points
        assert line.is_closed
        poly = self.aedtapp.modeler.geometries["poly_1872"]
        assert poly.edges
        assert poly.points
        assert poly.bottom_edge_x == 0
        assert poly.bottom_edge_y == 1
        assert poly.top_edge_x == 2
        assert poly.top_edge_y == 3
        assert poly.placement_layer == "1_Top"
        assert poly.obounding_box
        poly.placement_layer = "16_Bottom"
        assert poly.placement_layer == "16_Bottom"
        poly.placement_layer = "1_Top"
        assert poly.net_name == "----"
        assert not poly.negative
        assert not poly.is_void
        assert not poly.lock_position
        assert poly.is_closed
        assert len(self.aedtapp.modeler.geometries) > 0
        rect = self.aedtapp.modeler.rectangles["rect_5951"]
        assert rect.point_a
        assert rect.point_b
        assert rect.two_point_description
        assert not rect.center
        rect.two_point_description = False
        assert rect.center
        assert rect.height
        rect.two_point_description = True
        assert rect.point_a
        circle = self.aedtapp.modeler.circles["circle_5952"]
        assert circle.center
        assert circle.radius
        circle.radius = "2.5mm"
        assert circle.radius == "2.5mm"

    def test_02b_geo_units(self):
        assert self.aedtapp.modeler.geometries["line_209"].object_units == "mm"

    def test_02c_geo_layer(self):
        assert self.aedtapp.modeler.geometries["line_209"].placement_layer
        assert len(self.aedtapp.modeler.layers.drawing_layers) > 0
        assert len(self.aedtapp.modeler.layers.all_signal_layers) > 0
        assert len(self.aedtapp.modeler.layers.all_diel_layers) > 0
        assert len(self.aedtapp.modeler.stackup.all_signal_layers) == len(self.aedtapp.modeler.stackup.signals)
        assert len(self.aedtapp.modeler.stackup.all_diel_layers) == len(self.aedtapp.modeler.stackup.dielectrics)
        assert len(self.aedtapp.modeler.stackup.stackup_layers) == len(self.aedtapp.modeler.stackup.drawings)
        assert len(self.aedtapp.modeler.layers.all_signal_layers) + len(
            self.aedtapp.modeler.layers.all_diel_layers
        ) == len(self.aedtapp.modeler.layers.stackup_layers)
        assert isinstance(self.aedtapp.modeler.layers.all_signal_layers[0].name, str)
        assert isinstance(self.aedtapp.modeler.layers.all_diel_layers[0].name, str)

    def test_02d_geo_lock(self):
        self.aedtapp.modeler.geometries["line_209"].lock_position = True
        assert self.aedtapp.modeler.geometries["line_209"].lock_position == True
        self.aedtapp.modeler.geometries["line_209"].lock_position = False
        assert self.aedtapp.modeler.geometries["line_209"].lock_position == False

    def test_02e_geo_setter(self):
        self.aedtapp.modeler.geometries["line_209"].layer = "PWR"
        assert self.aedtapp.modeler.geometries["line_209"].layer == "PWR"
        self.aedtapp.modeler.geometries["line_209"].net_name = "VCC"
        assert self.aedtapp.modeler.geometries["line_209"].net_name == "VCC"

    def test_03_get_pins(self):
        pins = self.aedtapp.modeler.pins
        assert len(pins) > 0
        assert pins["L10-1"].object_units == "mm"
        assert pins["L10-1"].componentname == "L10"
        assert pins["L10-1"].is_pin
        assert pins["L10-1"].angle == "90deg" or pins["L10-1"].angle == "-270deg"
        assert pins["L10-1"].location[0] != 0
        assert pins["L10-1"].start_layer == "1_Top"
        assert pins["L10-1"].stop_layer == "1_Top"

    def test_03B_get_vias(self):
        vias = self.aedtapp.modeler.vias
        assert len(vias) > 0
        assert vias["Via1920"].object_units == "mm"
        assert not vias["Via1920"].is_pin
        assert vias["Via1920"].angle == "0deg"
        assert vias["Via1920"].location[0] > 0
        assert vias["Via1920"].start_layer == "1_Top"
        assert vias["Via1920"].stop_layer == "16_Bottom"
        assert vias["Via1920"].holediam == "0.1499997mm"

    def test_03C_voids(self):
        assert len(self.aedtapp.modeler.voids) > 0
        poly = self.aedtapp.modeler.polygons["poly_2084"]
        assert len(poly.polygon_voids) > 0

    def test_04_add_mesh_operations(self):
        self.aedtapp.create_setup("HFSS")
        setup1 = self.aedtapp.mesh.assign_length_mesh("HFSS", "PWR", "GND")
        setup2 = self.aedtapp.mesh.assign_skin_depth("HFSS", "PWR", "GND")
        assert setup1
        assert setup2
        setup1.props["RestrictElem"] = False
        assert setup1.update()
        assert self.aedtapp.mesh.delete_mesh_operations("HFSS", setup1.name)

    def test_05_change_property(self):
        ports = self.aedtapp.create_ports_on_component_by_nets(
            "U1",
            "DDR4_DQS0_P",
        )
        assert self.aedtapp.modeler.change_property(
            "Excitations:{}".format(ports[0].name), "Impedance", "49ohm", "EM Design"
        )

    def test_06_assign_spice_model(self):
        model_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32ER72A225KA35_25C_0V.sp")
        assert self.aedtapp.modeler.set_spice_model(
            component_name="C1", model_path=model_path, subcircuit_name="GRM32ER72A225KA35_25C_0V"
        )

    def test_07_nets(self):
        nets = self.aedtapp.modeler.nets
        assert nets["GND"].name == "GND"
        assert len(nets) > 0
        assert len(nets["GND"].components) > 0

    def test_07a_nets_count(self):
        nets = self.aedtapp.modeler.nets
        power_nets = self.aedtapp.modeler.power_nets
        signal_nets = self.aedtapp.modeler.signal_nets
        no_nets = self.aedtapp.modeler.no_nets
        assert len(nets) == len(power_nets) + len(signal_nets) + len(no_nets)

    def test_08_merge(self, add_app):
        tol = 1e-12
        brd = add_app(application=Hfss3dLayout, project_name=self.flipchip.project_name, design_name="Dummy_Board")
        comp = brd.modeler.merge_design(self.flipchip, rotation=90)
        assert comp.location[0] == 0.0
        assert comp.rotation_axis == "Z"
        comp.rotation_axis = "X"
        assert comp.rotation_axis == "X"
        comp.rotation_axis = "Z"
        comp.rotation_axis_direction = [0, 0, 1.2]
        assert comp.rotation_axis_direction == [0, 0, 1.2]
        assert not comp.is_flipped
        comp.is_flipped = True
        assert comp.is_flipped
        comp.is_flipped = False
        assert comp.location[0] == 0.0
        assert comp.location[1] == 0.0
        assert comp.angle == "90deg"
        comp.location = [0.1, 0.2]
        if config["desktopVersion"] > "2022.2":
            assert (comp.location[0] - 100.0) < tol
            assert (comp.location[1] - 200.0) < tol
        else:
            assert (comp.location[0] - 0.1) < tol
            assert (comp.location[1] - 0.2) < tol

    def test_10_change_stackup(self):
        assert self.aedtapp.modeler.layers.change_stackup_type("Multizone", 4)
        assert len(self.aedtapp.modeler.layers.zones) == 3
        assert self.aedtapp.modeler.layers.change_stackup_type("Overlap")
        assert self.aedtapp.modeler.layers.change_stackup_type("Laminate")
        assert not self.aedtapp.modeler.layers.change_stackup_type("lami")

    @pytest.mark.skipif(config["NonGraphical"], reason="Not running in non-graphical mode")
    def test_11_export_picture(self):
        assert os.path.exists(self.aedtapp.post.export_model_picture(orientation="top"))

    def test_12_objects_by_net(self):
        poly_on_gnd = self.aedtapp.modeler.objects_by_net("GND", "poly")
        assert len(poly_on_gnd) > 0
        assert self.aedtapp.modeler.geometries[poly_on_gnd[0]].net_name == "GND"

    def test_13_objects_by_layer(self):
        lines_on_top = self.aedtapp.modeler.objects_by_layer("1_Top", "line")
        assert len(lines_on_top) > 0
        assert self.aedtapp.modeler.geometries[lines_on_top[0]].placement_layer == "1_Top"

    def test_14_set_solderball(self):
        assert not self.aedtapp.modeler.components["U1"].die_enabled
        assert not self.aedtapp.modeler.components["U1"].die_type
        assert self.aedtapp.modeler.components["U1"].set_die_type()
        assert self.aedtapp.modeler.components["U1"].set_solderball("Cyl")
        assert self.aedtapp.modeler.components["U1"].solderball_enabled
        assert self.aedtapp.modeler.components["U1"].set_solderball(None)
        assert not self.aedtapp.modeler.components["U1"].solderball_enabled
        assert not self.aedtapp.modeler.components["L10"].set_solderball(None)
        assert self.aedtapp.modeler.components["J1"].set_solderball("Sph")

    def test_15_3dplacement(self):
        self.aedtapp.insert_design("placement_3d")
        l1 = self.aedtapp.modeler.layers.add_layer("BOTTOM", "signal", thickness="5mil")
        self.aedtapp.modeler.layers.add_layer("diel", "dielectric", thickness="121mil", material="FR4_epoxy")
        self.aedtapp.modeler.layers.add_layer("TOP", "signal", thickness="5mil", isnegative=True)
        tol = 1e-12
        encrypted_model_path = os.path.join(local_path, "example_models", test_subfolder, "SMA_RF_Jack.a3dcomp")
        comp = self.aedtapp.modeler.place_3d_component(
            encrypted_model_path, 1, placement_layer="TOP", component_name="my_connector", pos_x=0.001, pos_y=0.002
        )
        assert (comp.location[0] - 1.017) < tol
        assert (comp.location[1] - 2) < tol
        assert comp.angle == "0deg"
        assert comp.placement_layer == "TOP"
        comp.placement_layer = "bottom"
        assert comp.placement_layer == "BOTTOM"
        comp.angle = "10deg"
        assert comp.angle == "10deg"
        assert comp.component_name == "my_connector"
        assert len(self.aedtapp.modeler.components_3d) == 1
        comp2 = self.aedtapp.modeler.place_3d_component(
            encrypted_model_path, 1, component_name="my_connector2", pos_x=0.001, pos_y=0.002, pos_z=1
        )
        assert comp2.location[2] == 1.0

    def test_16_differential_ports(self):
        self.aedtapp.set_active_design(self.design_name)
        pins = self.aedtapp.modeler.components["R3"].pins
        assert self.aedtapp.create_differential_port(pins[0], pins[1], "test_differential", deembed=True)
        assert "test_differential" in self.aedtapp.port_list

    def test_17_ports_on_components_nets(self):
        component = self.aedtapp.modeler.components["J1"]
        nets = [
            self.aedtapp.modeler.pins[i].net_name
            for i in component.pins
            if "GND" not in self.aedtapp.modeler.pins[i].net_name and self.aedtapp.modeler.pins[i].net_name != ""
        ]
        ports_before = len(self.aedtapp.port_list)
        ports = self.aedtapp.create_ports_on_component_by_nets(
            "J1",
            nets,
        )
        assert ports
        ports_after = len(self.aedtapp.port_list)
        assert ports_after - ports_before == len(nets)
        ports[0].name = "port_test"
        assert ports[0].name == "port_test"
        assert ports[0].props["Port"] == "port_test"
        ports[0].props["Port"] = "port_test2"
        assert ports[0].name == "port_test2"

    def test_18_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_19_dcir(self):
        import pandas as pd

        self.dcir_example_project.analyze()
        setup = self.dcir_example_project.get_setup("SIwaveDCIR1")
        assert setup.is_solved
        assert self.dcir_example_project.get_dcir_solution_data("SIwaveDCIR1", "RL", "Path Resistance")
        assert self.dcir_example_project.get_dcir_solution_data("SIwaveDCIR1", "Vias", "Current")
        solution_data = self.dcir_example_project.get_dcir_solution_data("SIwaveDCIR1", "Sources", "Voltage")
        assert self.dcir_example_project.post.available_report_quantities(is_siwave_dc=True, context="")
        assert self.dcir_example_project.post.create_report(
            self.dcir_example_project.post.available_report_quantities(is_siwave_dc=True, context="RL")[0],
            setup_sweep_name="SIwaveDCIR1",
            domain="DCIR",
            context="RL",
        )
        assert isinstance(self.dcir_example_project.get_dcir_element_data_loop_resistance("SIwaveDCIR1"), pd.DataFrame)
        assert isinstance(self.dcir_example_project.get_dcir_element_data_current_source("SIwaveDCIR1"), pd.DataFrame)

    def test_20_change_options(self):
        assert self.aedtapp.change_options()
        assert self.aedtapp.change_options(color_by_net=False)
        assert not self.aedtapp.change_options(color_by_net=None)

    def test_21_show_extent(self):
        assert self.aedtapp.show_extent()
        assert self.aedtapp.show_extent(show=False)
        assert not self.aedtapp.show_extent(show=None)

    def test_22_change_design_settings(self):
        assert (
            self.aedtapp.get_oo_property_value(self.aedtapp.odesign, "Design Settings", "DCExtrapolation") == "Standard"
        )
        assert self.aedtapp.change_design_settings({"UseAdvancedDCExtrap": True})
        assert (
            self.aedtapp.get_oo_property_value(self.aedtapp.odesign, "Design Settings", "DCExtrapolation") == "Advanced"
        )
