import os

# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss3dLayout
from pyaedt.generic.filesystem import Scratch

test_project_name = "Galileo_t23"
original_project_name = "Galileo_t23"


class TestClass:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:

            example_project = os.path.join(local_path, "example_models", original_project_name + ".aedt")

            self.test_project = self.local_scratch.copyfile(
                example_project, os.path.join(self.local_scratch.path, test_project_name + ".aedt")
            )

            self.local_scratch.copyfolder(
                os.path.join(local_path, "example_models", original_project_name + ".aedb"),
                os.path.join(self.local_scratch.path, test_project_name + ".aedb"),
            )
            self.local_scratch.copyfolder(
                os.path.join(local_path, "example_models", "Package.aedb"),
                os.path.join(self.local_scratch.path, "Package2.aedb"),
            )
        self.aedtapp = Hfss3dLayout(self.test_project)
        self.aedtapp.modeler.geometries

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        for proj in self.aedtapp.project_list:
            try:
                self.aedtapp.close_project(proj, False)
            except:
                pass
        self.local_scratch.remove()
        del self.aedtapp

    def test_01_get_components(self):
        comp = self.aedtapp.modeler.components
        assert len(comp) > 0
        assert comp["L3A1"].object_units == "mm"
        assert comp["L3A1"].get_angle()
        assert comp["L3A1"].get_location()
        assert comp["L3A1"].get_placement_layer()
        assert comp["L3A1"].get_part()
        assert comp["L3A1"].get_part_type()
        assert comp["L3A1"].set_property_value("Angle", "0deg")

    def test_02a_get_geometries(self):
        line = self.aedtapp.modeler.geometries["line_1983"]
        assert len(self.aedtapp.modeler.geometries) > 0

    def test_02b_geo_units(self):
        assert self.aedtapp.modeler.geometries["line_1983"].object_units == "mm"

    def test_02c_geo_layer(self):
        assert self.aedtapp.modeler.geometries["line_1983"].get_placement_layer()

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
        assert pins["L3A1-1"].get_angle()
        assert pins["L3A1-1"].get_location()
        assert pins["L3A1-1"].get_start_layer()
        assert pins["L3A1-1"].get_stop_layer()

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
        hfss3d = Hfss3dLayout(os.path.join(self.local_scratch.path, "Package2.aedb", "edb.def"))
        assert hfss3d.modeler.merge_design(self.aedtapp)
        self.aedtapp.odesktop.CloseProject(hfss3d.project_name)
