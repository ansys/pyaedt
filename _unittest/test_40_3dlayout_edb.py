import os

# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path
import gc

# Import required modules
from pyaedt import Hfss3dLayout
from pyaedt.generic.filesystem import Scratch

test_project_name = "Galileo_t23"
original_project_name = "Galileo_t23"


class TestClass:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:

            example_project = os.path.join(local_path, "example_models", original_project_name + ".aedt")

            self.test_project = self.local_scratch.copyfile(example_project, os.path.join(self.local_scratch.path,
                                                                                          test_project_name + ".aedt"))

            self.local_scratch.copyfolder(
                os.path.join(local_path, "example_models", original_project_name + ".aedb"),
                os.path.join(self.local_scratch.path, test_project_name + ".aedb"),
            )
            try:
                self.aedtapp = Hfss3dLayout(self.test_project)
            except:
                self.aedtapp = None

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        self.aedtapp.close_project(test_project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def test_01_get_components(self):
        comp = self.aedtapp.modeler.primitives.components
        assert len(comp) > 0
        assert comp["L3A1"].object_units == "mm"
        assert comp["L3A1"].get_angle()
        assert comp["L3A1"].get_location()
        assert comp["L3A1"].get_placement_layer()
        assert comp["L3A1"].get_part()
        assert comp["L3A1"].get_part_type()
        assert comp["L3A1"].set_property_value("Angle", "0deg")

    def test_02_get_geometries(self):
        geo = self.aedtapp.modeler.primitives.geometries
        assert len(geo) > 0
        assert geo["line_1983"].object_units == "mm"
        assert geo["line_1983"].get_placement_layer()
        assert geo["line_1983"].set_lock_position(True)
        assert geo["line_1983"].set_lock_position(False)
        assert geo["line_1983"].set_layer("PWR")
        assert geo["line_1983"].set_net_name("VCC")

    def test_03_get_pins(self):
        pins = self.aedtapp.modeler.primitives.pins
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
