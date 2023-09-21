import os

from _unittest.conftest import NONGRAPHICAL
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
from _unittest.conftest import new_thread
import pytest

from pyaedt import Desktop
from pyaedt import TwinBuilder
from pyaedt.generic.general_methods import is_linux

test_subfolder = "T34"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="TwinBuilderProject", design_name="TwinBuilderDesign1", application=TwinBuilder)
    app.modeler.schematic_units = "mil"
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    netlist1 = os.path.join(local_path, "../_unittest/example_models", test_subfolder, "netlist_small.cir")
    netlist_file1 = local_scratch.copyfile(netlist1)
    return netlist_file1, None


@pytest.fixture(scope="module", autouse=True)
def desktop():
    d = Desktop(desktop_version, NONGRAPHICAL, new_thread)
    d.disable_autosave()
    d.odesktop.SetDesktopConfiguration("Twin Builder")
    d.odesktop.SetSchematicEnvironment(1)
    yield d
    d.odesktop.SetDesktopConfiguration("All")
    d.odesktop.SetSchematicEnvironment(0)
    d.release_desktop(True, True)


@pytest.mark.skipif(is_linux, reason="Emit API fails on linux.")
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch, examples):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.netlist_file1 = examples[0]

    def test_01_create_resistor(self):
        id = self.aedtapp.modeler.schematic.create_resistor("Resistor1", 10, [0, 0])
        assert id.parameters["R"] == "10"

    def test_02_create_inductor(self):
        id = self.aedtapp.modeler.schematic.create_inductor("Inductor1", 1.5, [1000, 0])
        assert id.parameters["L"] == "1.5"

    def test_03_create_capacitor(self):
        id = self.aedtapp.modeler.schematic.create_capacitor("Capacitor1", 7.5, [2000, 0])
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
        assert self.aedtapp.create_schematic_from_netlist(self.netlist_file1)

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
        id = self.aedtapp.modeler.schematic.create_periodic_waveform_source("P1", "PULSE", 200, 20, 0, 0, [3000, 0])
        assert id.parameters["AMPL"] == "200"
        assert id.parameters["FREQ"] == "20"

    def test_14_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"
