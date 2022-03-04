import os

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Setup paths for module imports
from _unittest.conftest import local_path, BasisTest, desktop_version

# Import required modules
from pyaedt import Hfss3dLayout

test_project_name = "Galileo_t23"
original_project_name = "Galileo_t23"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=original_project_name, application=Hfss3dLayout)
        self.tmp = self.aedtapp.modeler.geometries
        example_project = os.path.join(local_path, "example_models", "Package.aedb")
        src_file = os.path.join(local_path, "example_models", "Package.aedt")
        dest_file = os.path.join(self.local_scratch.path, "Package_test_40.aedt")
        self.target_path = os.path.join(self.local_scratch.path, "Package_test_40.aedb")
        self.local_scratch.copyfolder(example_project, self.target_path)
        self.package_file = self.local_scratch.copyfile(src_file, dest_file)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_get_components(self):
        comp = self.aedtapp.modeler.components
        assert len(comp) > 0
        assert comp["L3A1"].object_units == "mm"
        assert comp["L3A1"].angle == "0deg"
        assert comp["L3A1"].location[1] == 0.0381
        assert comp["L3A1"].placement_layer == "TOP"
        assert comp["L3A1"].part == "A32422-019"
        assert comp["L3A1"].part_type == "Inductor"
        assert comp["L3A1"].set_property_value("Angle", "0deg")
        assert comp["L3A1"].enabled(False)
        assert comp["L3A1"].enabled(True)
        assert comp["R13"].enabled(False)
        assert comp["R13"].enabled(True)
        assert comp["C3B14"].enabled(False)
        assert comp["C3B14"].enabled(True)
        assert not comp["U3B2"].enabled(False)
        assert not comp["J2"].enabled(False)
        assert not comp["FB1M1"].enabled(False)

    def test_02a_get_geometries(self):
        line = self.aedtapp.modeler.geometries["line_1983"]
        assert len(self.aedtapp.modeler.geometries) > 0

    def test_02b_geo_units(self):
        assert self.aedtapp.modeler.geometries["line_1983"].object_units == "mm"

    def test_02c_geo_layer(self):
        assert self.aedtapp.modeler.geometries["line_1983"].get_placement_layer()
        assert len(self.aedtapp.modeler.layers.drawing_layers) > 0

    def test_02d_geo_lock(self):
        assert self.aedtapp.modeler.geometries["line_1983"].set_lock_position(True)
        assert self.aedtapp.modeler.geometries["line_1983"].set_lock_position(False)

    def test_02e_geo_setter(self):
        assert self.aedtapp.modeler.geometries["line_1983"].set_layer("PWR")
        assert self.aedtapp.modeler.geometries["line_1983"].set_net_name("VCC")

    def test_03_get_pins(self):
        pins = self.aedtapp.modeler.pins
        assert len(pins) > 0
        assert pins["L3A1-1"].object_units == "mm"
        assert pins["L3A1-1"].angle == "180deg"
        assert pins["L3A1-1"].location[0] > 0
        assert pins["L3A1-1"].start_layer == "TOP"
        assert pins["L3A1-1"].stop_layer == "TOP"

    def test_04_add_mesh_operations(self):
        self.aedtapp.create_setup("HFSS")
        setup1 = self.aedtapp.mesh.assign_length_mesh("HFSS", "PWR", "GND")
        setup2 = self.aedtapp.mesh.assign_skin_depth("HFSS", "PWR", "GND")
        assert setup1
        assert setup2
        setup1.props["Enabled"] = False
        assert setup1.update()
        assert self.aedtapp.mesh.delete_mesh_operations("HFSS", setup1.name)

    def test_05_change_property(self):
        assert self.aedtapp.modeler.change_property("Excitations:J2B3-2", "Impedance", "49ohm", "EM Design")

    def test_06_assign_spice_model(self):
        model_path = os.path.join(self.local_scratch.path, test_project_name + ".aedb", "GRM32ER72A225KA35_25C_0V.sp")
        assert self.aedtapp.modeler.set_spice_model(
            component_name="C3A3", model_path=model_path, subcircuit_name="GRM32ER72A225KA35_25C_0V"
        )

    def test_07_nets(self):
        nets = self.aedtapp.modeler.nets
        assert nets["GND"].name == "GND"
        assert len(nets) > 0

    def test_08_merge(self):
        tol = 1e-12
        hfss3d = Hfss3dLayout(self.package_file, "FlipChip_TopBot", specified_version=desktop_version)
        brd = Hfss3dLayout(hfss3d.project_name, "Dummy_Board", specified_version=desktop_version)
        comp = brd.modeler.merge_design(hfss3d, rotation=90)
        assert comp.location[0] == 0.0
        assert comp.location[1] == 0.0
        assert comp.angle == "90deg"
        comp.location = [0.1, 0.2]
        assert (comp.location[0] - 0.1) < tol
        assert (comp.location[1] - 0.2) < tol
        hfss3d.close_project(saveproject=False)

    @pytest.mark.skipif(os.name != "posix", reason="Not running in non graphical mode. Tested only in Linux machine")
    def test_09_3dplacement(self):  # pragma: no cover
        assert len(self.aedtapp.modeler.components_3d) == 2
        tol = 1e-12
        encrypted_model_path = os.path.join(local_path, "example_models", "connector.a3dcomp")
        comp = self.aedtapp.modeler.place_3d_component(
            encrypted_model_path, 4, placement_layer="TOP", component_name="my_connector", pos_x=0.001, pos_y=0.002
        )
        assert (comp.location[0] - 0.001) < tol
        assert (comp.location[1] - 0.002) < tol
        assert comp.angle == "0deg"
        assert comp.placement_layer == "TOP"
        comp.placement_layer = "bottom"
        assert comp.placement_layer == "BOTTOM"
        comp.angle = "10deg"
        assert comp.angle == "10deg"
        assert comp.component_name == "my_connector"
