# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path

# Import required modules
from pyaedt import TwinBuilder
from pyaedt.generic.filesystem import Scratch
import gc
import os

netlist1 = "netlist_small.cir"


class TestClass:
    def setup_class(self):
        project_name = "TwinBuilderProject"
        design_name = "TwinBuilderDesign1"
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            netlist_file1 = os.path.join(local_path, "example_models", netlist1)
            self.local_scratch.copyfile(netlist_file1)
            self.aedtapp = TwinBuilder(project_name, design_name)

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        assert self.aedtapp.close_project(self.aedtapp.project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_resistor(self):
        id = self.aedtapp.modeler.schematic.create_resistor("Resistor1", 10, [0, 0])
        assert id.parameters["R"] == "10"

    def test_02_create_inductor(self):
        id = self.aedtapp.modeler.schematic.create_inductor("Inductor1", 1.5, [0.25, 0])
        assert id.parameters["L"] == "1.5"

    def test_03_create_capacitor(self):
        id = self.aedtapp.modeler.schematic.create_capacitor("Capacitor1", 7.5, [0.5, 0])
        assert id.parameters["C"] == "7.5"

    def test_04_create_diode(self):
        id = self.aedtapp.modeler.schematic.create_diode("Diode1")
        assert id.parameters["VF"] == "0.8V"

    def test_05_create_npn(self):
        name = self.aedtapp.modeler.schematic.create_npn("NPN")
        # Get component info by part name
        assert name.parameters["VF"] == "0.8V"

    def test_06_create_pnp(self):
        id = self.aedtapp.modeler.schematic.create_pnp("PNP")
        assert id.parameters["VF"] == "0.8V"

    def test_07_import_netlist(self):
        self.aedtapp.insert_design("SchematicImport")
        assert self.aedtapp.create_schematic_from_netlist(os.path.join(self.local_scratch.path, netlist1))

    def test_08_set_hmax(self):
        assert self.aedtapp.set_hmax("5ms")

    def test_09_set_hmin(self):
        assert self.aedtapp.set_hmin("0.2ms")

    def test_10_set_hmin(self):
        assert self.aedtapp.set_hmin("2s")

    def test_11_set_end_time(self):
        assert self.aedtapp.set_end_time("5s")

    def test_12_catalog(self):
        comp_catalog = self.aedtapp.modeler.components.components_catalog
        assert not comp_catalog["Capacitors"]
        assert comp_catalog["Aircraft Electrical VHDLAMS\\Basic:lowpass_filter"].props
        assert comp_catalog["Aircraft Electrical VHDLAMS\\Basic:lowpass_filter"].place("LP1")

    def test_13_create_periodic_pulse_wave(self):
        id = self.aedtapp.modeler.schematic.create_periodic_waveform_source("P1", "PULSE", 200, 20, 0, 0, [0.75, 0])
        assert id.parameters["AMPL"] == "200"
        assert id.parameters["FREQ"] == "20"
