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


import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.generic.settings import is_linux
from tests import TESTS_GENERAL_PATH
from tests.conftest import config

test_subfloder = "T22"
test_project_name = "Dynamic_Link"
src_design_name = "uUSB"
if config["desktopVersion"] > "2022.2":
    src_project_name = "USB_Connector_231"
    linked_project_name = "Filter_Board_231"
else:
    src_project_name = "USB_Connector"
    linked_project_name = "Filter_Board"

layout_design_name = "layout_cutout"


@pytest.fixture()
def aedtapp(add_app, local_scratch):
    example_project_name = test_project_name + ".aedt"
    example_project = TESTS_GENERAL_PATH / "example_models" / test_subfloder / example_project_name
    test_project = local_scratch.copyfile(example_project)
    test_project_name_edb = test_project_name + ".aedb"
    local_scratch.copyfolder(
        TESTS_GENERAL_PATH / "example_models" / test_subfloder / test_project_name_edb,
        local_scratch.path / test_project_name_edb,
    )
    linked_project_aedt_name = linked_project_name + ".aedt"
    linked_project_aedb_name = linked_project_name + ".aedb"
    linked_project = TESTS_GENERAL_PATH / "example_models" / test_subfloder / linked_project_aedt_name
    test_lkd_project = local_scratch.copyfile(linked_project)
    local_scratch.copyfolder(
        TESTS_GENERAL_PATH / "example_models" / test_subfloder / linked_project_aedb_name,
        local_scratch.path / linked_project_aedb_name,
    )

    with open(example_project, "rb") as fh:
        temp = fh.read().splitlines()

    with open(test_project, "wb") as outf:
        found = False
        for line in temp:
            if not found:
                if "Filter_Board.aedt" in line.decode("utf-8"):
                    line = f"\t\t\t\tfilename='{test_lkd_project.replace(chr(92), '/')}'\n".encode()
                    found = True
            outf.write(line + b"\n")

    app = add_app(application=Circuit, project_name=test_project, just_open=True)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture()
def usb_app(add_app):
    app = add_app(project_name=src_project_name, application=Circuit, subfolder=test_subfloder)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture()
def circuit_app(add_app):
    app = add_app(project_name=test_project_name, application=Circuit, subfolder=test_subfloder)
    yield app
    app.close_project(app.project_name, save=False)


# @pytest.fixture()
# def examples(local_scratch):
#     source_project = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, src_project_name + ".aedt")
#     src_project_file = local_scratch.copyfile(source_project)
#     q3d = local_scratch.copyfile(os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, "q2d_q3d.aedt"))
#     return src_project_file, q3d


# @pytest.fixture(autouse=True)
# def init(self, local_scratch, examples):
#     self.local_scratch = local_scratch
#     self.src_project_file = examples[0]
#     self.q3d = examples[1]


def test_pin_names(usb_app):
    pin_names = usb_app.get_source_pin_names(src_design_name, src_project_name, port_selector=2)
    assert len(pin_names) == 4
    assert "usb_P_pcb" in pin_names


@pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
def test_add_subcircuits_3dlayout(circuit_app):
    hfss3Dlayout_comp = circuit_app.modeler.schematic.add_subcircuit_3dlayout(layout_design_name)
    assert hfss3Dlayout_comp.id == 86
    assert hfss3Dlayout_comp


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical.")
def test_add_subcircuits_hfss_link(usb_app):
    hfss_comp = usb_app.modeler.schematic.add_subcircuit_dynamic_link(usb_app, comp_name=src_design_name)
    assert hfss_comp.id == 86
    assert usb_app.modeler.schematic.refresh_dynamic_link(src_design_name)


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_set_sim_option_on_hfss_subcircuit(aedtapp):
    hfss_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(aedtapp, comp_name="uUSB")
    assert aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
    assert aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="interpolate")
    assert not aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="not_good")


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_set_sim_solution_on_hfss_subcircuit(aedtapp):
    hfss_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(aedtapp, comp_name="uUSB")
    assert aedtapp.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp)


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_assign_excitations(aedtapp):
    aedtapp.modeler.schematic.create_interface_port("Excitation_1", [0, 0])
    aedtapp.modeler.schematic.create_interface_port("Excitation_2", ["500mil", 0])
    filepath = TESTS_GENERAL_PATH / "example_models" / test_subfloder / "frequency_dependent_source.fds"
    ports_list = ["Excitation_1", "Excitation_2"]
    assert aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, str(filepath))

    filepath = TESTS_GENERAL_PATH / "example_models" / test_subfloder / "frequency_dependent_source1.fds"
    ports_list = ["Excitation_1", "Excitation_2"]
    assert not aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, str(filepath))

    filepath = TESTS_GENERAL_PATH / "example_models" / test_subfloder / "frequency_dependent_source.fds"
    ports_list = ["Excitation_1", "Excitation_3"]
    assert not aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, str(filepath))

    ports_list = ["Excitation_1"]
    assert aedtapp.assign_voltage_sinusoidal_excitation_to_ports(ports_list)


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_q2d_link(add_app, aedtapp):
    q2d = add_app(application=Q2d, just_open=True)
    c1 = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(q2d, extrusion_length=25)
    assert c1
    assert len(c1.pins) == 6
    assert c1.parameters["Length"] == "25mm"
    assert c1.parameters["r1"] == "0.3mm"


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_q3d_link(add_app, aedtapp):
    q3d = add_app(application=Q3d, just_open=True)

    q3d_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(q3d, solution_name="Setup1 : LastAdaptive")
    assert q3d_comp
    assert len(q3d_comp.pins) == 4


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_hfss_link(add_app, aedtapp):
    q3d = add_app(application=Q3d, just_open=True)

    hfss_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(q3d, solution_name="Setup1 : Sweep")
    assert hfss_comp
    assert len(hfss_comp.pins) == 2
    hfss2 = add_app(project_name=q3d, just_open=True)
    assert aedtapp.modeler.schematic.add_subcircuit_dynamic_link(hfss2, solution_name="Setup2 : Sweep", tline_port="1")


@pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
def test_siwave_link(aedtapp, local_scratch):
    model = TESTS_GENERAL_PATH / "example_models" / test_subfloder / "siwave_syz.siw"
    model_out = local_scratch.copyfile(model)
    local_scratch.copyfolder(model + "averesults", local_scratch.path / "siwave_syz.siwaveresults")
    siw_comp = aedtapp.modeler.schematic.add_siwave_dynamic_link(model_out)
    assert siw_comp
    assert len(siw_comp.pins) == 4


@pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
def test_create_interface_port(aedtapp):
    page_port = aedtapp.modeler.components.create_page_port(name="Port12", location=[0, -0.50])
    interface_port = aedtapp.modeler.components.create_interface_port(name="Port12", location=[0.3, -0.50])
    second_page_port = aedtapp.modeler.components.create_page_port(name="Port12", location=[0.45, -0.5])
    second_interface_port = aedtapp.modeler.components.create_interface_port(name="Port122", location=[0.6, -0.50])
    assert not aedtapp.modeler.components.create_interface_port(name="Port122", location=[0.6, -0.50])
    assert page_port.composed_name != second_page_port.composed_name
    assert page_port.composed_name != interface_port.name
    assert page_port.composed_name != second_interface_port.name
    assert interface_port.name != second_interface_port.name
