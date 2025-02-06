# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import MaxwellCircuit
from ansys.aedt.core.generic.constants import SOLUTIONS
import pytest

from tests import TESTS_GENERAL_PATH

test_subfolder = "T35"

netlist1 = "netlist.sph"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="MaxwellCircuitProject", design_name="MaxwellCircuitDesign1", application=MaxwellCircuit)
    app.modeler.schematic_units = "mil"
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    netlist_file1 = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, netlist1)
    return [netlist_file1]


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
        m2d.assign_coil(assignment=["Circle_inner"])
        m2d.assign_winding(assignment=["Circle_inner"], winding_type="External", name="Ext_Wdg")
        assert m2d.edit_external_circuit(netlist_file, self.aedtapp.design_name)

    def test_08_import_netlist(self):
        self.aedtapp.insert_design("SchematicImport")
        self.aedtapp.modeler.schematic.limits_mils = 5000
        assert self.aedtapp.create_schematic_from_netlist(self.netlist_file1)
