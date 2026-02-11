# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import pytest

from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import MaxwellCircuit
from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
from ansys.aedt.core.internal.checks import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH

TEST_SUBFOLDER = "T35"

NETLIST1 = "netlist.sph"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=MaxwellCircuit)
    app.modeler.schematic_units = "mil"
    yield app
    app.close_project(app.project_name)


def test_create_resistor(aedt_app) -> None:
    resistor = aedt_app.modeler.schematic.create_resistor("Resistor1", 10, [0, 0])
    assert resistor.parameters["R"] == "10"


def test_create_inductor(aedt_app) -> None:
    inductor = aedt_app.modeler.schematic.create_inductor("Inductor1", 1.5, [1000, 0])
    assert inductor.parameters["L"] == "1.5"


def test_create_capacitor(aedt_app) -> None:
    capacitor = aedt_app.modeler.schematic.create_capacitor("Capacitor1", 7.5, [2000, 0])
    assert capacitor.parameters["C"] == "7.5"


def test_create_diode(aedt_app) -> None:
    assert aedt_app.modeler.schematic.create_diode("Diode1")


def test_create_winding(aedt_app) -> None:
    assert aedt_app.modeler.schematic.create_winding("mywinding")


def test_set_variable(aedt_app) -> None:
    aedt_app.variable_manager.set_variable("var_test", expression="123")
    aedt_app["var_test"] = "234"
    assert "var_test" in aedt_app.variable_manager.design_variable_names
    assert aedt_app.variable_manager.design_variables["var_test"].expression == "234"


def test_export_netlist(aedt_app, add_app, test_tmp_dir) -> None:
    aedt_app.modeler.schematic_units = "mil"
    ind = aedt_app.modeler.schematic.create_inductor("Inductor1", 1.5, [-1000, 1000])
    res = aedt_app.modeler.schematic.create_resistor("Resistor1", 10, [1000, 1000])
    gnd = aedt_app.modeler.schematic.create_gnd([0.0, 0.0])
    v_source = aedt_app.modeler.schematic.create_component(
        component_library="Sources", component_name="IPulse", location=[-2000, 500]
    )
    i_source = aedt_app.modeler.schematic.create_component(
        component_library="Sources", component_name="VPulse", location=[2000, 500]
    )
    ind.pins[1].connect_to_component(res.pins[0], use_wire=True)
    ind.pins[0].connect_to_component(v_source.pins[1], use_wire=True)
    v_source.pins[0].connect_to_component(gnd.pins[0], use_wire=True)
    gnd.pins[0].connect_to_component(i_source.pins[0], use_wire=True)
    i_source.pins[1].connect_to_component(res.pins[1], use_wire=True)
    netlist_file = test_tmp_dir / "export_netlist.sph"
    assert aedt_app.export_netlist_from_schematic(str(netlist_file)) == str(netlist_file)
    assert netlist_file.exists()
    netlist_file_invalid = test_tmp_dir / "export_netlist.sh"
    assert not aedt_app.export_netlist_from_schematic(str(netlist_file_invalid))
    m2d = add_app(design="test", application=Maxwell2d, project=aedt_app.project_name, close_projects=False)
    m2d.solution_type = SolutionsMaxwell2D.TransientZ
    m2d.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
    m2d.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
    m2d.assign_coil(assignment=["Circle_inner"])
    m2d.assign_winding(assignment=["Circle_inner"], winding_type="External", name="Ext_Wdg")
    assert m2d.edit_external_circuit(str(netlist_file), aedt_app.design_name)
    with pytest.raises(AEDTRuntimeError):
        m2d.edit_external_circuit(str(netlist_file), "invalid")
    netlist_file_2 = test_tmp_dir / "export_netlist_2.sph"
    v_source.parameters["Name"] = "VSource"
    i_source.parameters["Name"] = "ISource"
    aedt_app.export_netlist_from_schematic(str(netlist_file_2))
    assert m2d.edit_external_circuit(str(netlist_file_2), aedt_app.design_name)


def test_import_netlist(aedt_app) -> None:
    netlist_file1 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / NETLIST1
    aedt_app.insert_design("SchematicImport")
    aedt_app.modeler.schematic.limits_mils = 5000
    assert aedt_app.create_schematic_from_netlist(str(netlist_file1))
