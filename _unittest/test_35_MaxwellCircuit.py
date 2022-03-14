# Setup paths for module imports
from _unittest.conftest import BasisTest
from pyaedt import MaxwellCircuit


class TestClass(BasisTest, object):
    def setup_class(self):
        project_name = "MaxwellCircuitProject"
        design_name = "MaxwellCircuitDesign1"
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(
            self, project_name=project_name, design_name=design_name, application=MaxwellCircuit
        )

    def teardown_class(self):
        BasisTest.my_teardown(self)

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
        assert self.aedtapp.modeler.schematic.create_diode("Diode1")

    def test_05_create_winding(self):
        assert self.aedtapp.modeler.schematic.create_winding("mywinding")
