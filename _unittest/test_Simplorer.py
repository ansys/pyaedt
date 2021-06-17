# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Simplorer
from pyaedt.generic.filesystem import Scratch
import gc
import os
netlist1 = 'netlist_small.cir'

class TestSimplorer:

    def setup_class(self):
        project_name = "SimplorerProject"
        design_name = "SimplorerDesign1"
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            netlist_file1 = os.path.join(local_path, 'example_models', netlist1)
            self.local_scratch.copyfile(netlist_file1)

            self.aedtapp = Simplorer(project_name, design_name)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_resistor(self):
        id = self.aedtapp.modeler.components.create_resistor("Resistor1", 10, 0, 0)[0]
        assert self.aedtapp.modeler.components[id].R == 10

    def test_02_create_inductor(self):
        id = self.aedtapp.modeler.components.create_inductor("Inductor1", 1.5, 0.25, 0)[0]
        assert self.aedtapp.modeler.components[id].L == 1.5

    def test_03_create_capacitor(self):
        id = self.aedtapp.modeler.components.create_capacitor("Capacitor1", 7.5, 0.5, 0)[0]
        assert self.aedtapp.modeler.components[id].C == 7.5

    def test_04_create_diode(self):
        id = self.aedtapp.modeler.components.create_diode("Diode1", xpos=-0.25)[0]
        assert self.aedtapp.modeler.components[id].Info == "D"

    def test_05_create_npn(self):
        name = self.aedtapp.modeler.components.create_npn("NPN", ypos=0.25)[1]
        # Get component info by part name
        assert self.aedtapp.modeler.components[name].Info == "BJT"

    def test_06_create_pnp(self):
        id = self.aedtapp.modeler.components.create_pnp("PNP", ypos=-0.25)[0]
        assert self.aedtapp.modeler.components[id].Info == "BJT"

    def test_07_import_netlist(self):
        self.aedtapp.insert_design("SchematicImport")
        assert self.aedtapp.create_schematic_from_netlist(os.path.join(self.local_scratch.path, netlist1))

    def test_08_set_hmax(self):
        assert self.aedtapp.set_hmax("5ms")

    def test_09_set_hmin(self):
        assert self.aedtapp.set_hmax("0.2ms")

    def test_10_set_hmin(self):
        assert self.aedtapp.set_hmax("2s")