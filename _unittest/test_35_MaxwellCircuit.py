# Setup paths for module imports
import os

from _unittest.conftest import BasisTest
from pyaedt import Maxwell2d
from pyaedt import MaxwellCircuit
from pyaedt.generic.constants import SOLUTIONS


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

    def test_06_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_07_export_netlist(self):
        design_name = "ExportCircuitNetlist"
        self.aedtapp.insert_design(design_name)
        ind = self.aedtapp.modeler.schematic.create_inductor("Inductor1", 1.5, [-0.02, 0.02])
        res = self.aedtapp.modeler.schematic.create_resistor("Resistor1", 10, [0.02, 0.02])
        gnd = self.aedtapp.modeler.schematic.create_gnd([0.0, 0.0])
        v_source = self.aedtapp.modeler.schematic.create_component(
            component_library="Sources", component_name="IPulse", location=[-0.04, 0.01]
        )
        i_source = self.aedtapp.modeler.schematic.create_component(
            component_library="Sources", component_name="VPulse", location=[0.04, 0.01]
        )
        ind.pins[1].connect_to_component(res.pins[0])
        ind.pins[0].connect_to_component(v_source.pins[1])
        v_source.pins[0].connect_to_component(gnd.pins[0])
        gnd.pins[0].connect_to_component(i_source.pins[0])
        i_source.pins[1].connect_to_component(res.pins[1])
        netlist_file = os.path.join(self.local_scratch.path, "export_netlist.sph")
        assert self.aedtapp.create_netlist_from_schematic(netlist_file)[0] == netlist_file
        assert self.aedtapp.create_netlist_from_schematic(netlist_file)[1] == design_name
        assert os.path.exists(netlist_file)
        netlist_file_invalid = os.path.join(self.local_scratch.path, "export_netlist.sh")
        assert not self.aedtapp.create_netlist_from_schematic(netlist_file_invalid)
        m2d = Maxwell2d(designname="test")
        m2d.solution_type = SOLUTIONS.Maxwell2d.TransientZ
        m2d.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
        m2d.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
        m2d.assign_coil(input_object=["Circle_inner"])
        m2d.assign_winding(coil_terminals=["Circle_inner"], name="Ext_Wdg", winding_type="External")
        assert m2d.edit_external_circuit(netlist_file, design_name)
        assert not m2d.edit_external_circuit(netlist_file_invalid, design_name)
