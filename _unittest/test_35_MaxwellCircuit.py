import os

import pytest

from pyaedt import Maxwell2d
from pyaedt import MaxwellCircuit
from pyaedt.generic.constants import SOLUTIONS


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="MaxwellCircuitProject", design_name="MaxwellCircuitDesign1", application=MaxwellCircuit)
    app.modeler.schematic_units = "mil"
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

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
        assert self.aedtapp.modeler.schematic.create_diode("Diode1")

    def test_05_create_winding(self):
        assert self.aedtapp.modeler.schematic.create_winding("mywinding")

    def test_06_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_07_export_netlist(self, add_app):
        design_name = "ExportCircuitNetlist"
        self.aedtapp.insert_design(design_name)
        self.aedtapp.modeler.schematic_units = "mil"
        ind = self.aedtapp.modeler.schematic.create_inductor("Inductor1", 1.5, [-1000, 1000])
        res = self.aedtapp.modeler.schematic.create_resistor("Resistor1", 10, [1000, 1000])
        gnd = self.aedtapp.modeler.schematic.create_gnd([0.0, 0.0])
        v_source = self.aedtapp.modeler.schematic.create_component(
            component_library="Sources", component_name="IPulse", location=[-2000, 500]
        )
        i_source = self.aedtapp.modeler.schematic.create_component(
            component_library="Sources", component_name="VPulse", location=[2000, 500]
        )
        ind.pins[1].connect_to_component(res.pins[0], use_wire=True)
        ind.pins[0].connect_to_component(v_source.pins[1], use_wire=True)
        v_source.pins[0].connect_to_component(gnd.pins[0], use_wire=True)
        gnd.pins[0].connect_to_component(i_source.pins[0], use_wire=True)
        i_source.pins[1].connect_to_component(res.pins[1], use_wire=True)
        netlist_file = os.path.join(self.local_scratch.path, "export_netlist.sph")
        assert self.aedtapp.export_netlist_from_schematic(netlist_file) == netlist_file
        assert os.path.exists(netlist_file)
        netlist_file_invalid = os.path.join(self.local_scratch.path, "export_netlist.sh")
        assert not self.aedtapp.export_netlist_from_schematic(netlist_file_invalid)
        m2d = add_app(design_name="test", application=Maxwell2d)
        m2d.solution_type = SOLUTIONS.Maxwell2d.TransientZ
        m2d.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
        m2d.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
        m2d.assign_coil(input_object=["Circle_inner"])
        m2d.assign_winding(coil_terminals=["Circle_inner"], name="Ext_Wdg", winding_type="External")
        assert m2d.edit_external_circuit(netlist_file, self.aedtapp.design_name)
