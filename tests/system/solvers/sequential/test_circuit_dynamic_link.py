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


import shutil
from typing import TYPE_CHECKING

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_SEQUENTIAL_PATH
from tests.conftest import NON_GRAPHICAL
from tests.conftest import SKIP_CIRCUITS

if TYPE_CHECKING:
    from ansys.aedt.core.modeler.circuits.object_3d_circuit import CircuitComponent

TEST_SUBFOLDER = "circuit_dynamic_link"
TEST_PROJECT_NAME = "Dynamic_Link"
SRC_USB = "uUSB"

SRC_PROJECT_NAME = "USB_Connector_231"
LINKED_PROJECT_NAME = "Filter_Board_231"

LAYOUT_DESIGN_NAME = "layout_cutout"
Q2D_Q3D_NAME = "q2d_q3d"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def usb_app(add_app_example):
    app = add_app_example(project=SRC_PROJECT_NAME, application=Hfss, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def circuit_app(add_app_example):
    app = add_app_example(project=TEST_PROJECT_NAME, application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q3d_app(add_app_example):
    app = add_app_example(project=Q2D_Q3D_NAME, application=Q3d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q2d_app(add_app_example):
    app = add_app_example(project=Q2D_Q3D_NAME, application=Q2d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_pin_names(usb_app, add_app):
    app = add_app(application=Circuit, project=usb_app.project_name, close_projects=False)
    pin_names = app.get_source_pin_names(SRC_USB, SRC_PROJECT_NAME, port_selector=2)
    assert len(pin_names) == 4
    assert "usb_P_pcb" in pin_names


@pytest.mark.skipif(SKIP_CIRCUITS, reason="Skipped because Desktop is crashing")
def test_add_subcircuits_3dlayout(circuit_app):
    hfss3Dlayout_comp = circuit_app.modeler.schematic.add_subcircuit_3dlayout(LAYOUT_DESIGN_NAME)
    assert hfss3Dlayout_comp.id == 86
    assert hfss3Dlayout_comp


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical.")
def test_add_subcircuits_hfss_link(circuit_app, add_app_example):
    app = add_app_example(project=SRC_PROJECT_NAME, application=Hfss, subfolder=TEST_SUBFOLDER, close_projects=False)
    hfss_comp = circuit_app.modeler.schematic.add_subcircuit_dynamic_link(app, name=SRC_USB)
    assert hfss_comp.id == 86
    assert circuit_app.modeler.schematic.refresh_dynamic_link(SRC_USB)
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical")
def test_set_sim_option_on_hfss_subcircuit(usb_app, add_app):
    app = add_app(application=Circuit, project=usb_app.project_name, close_projects=False)
    hfss_comp = app.modeler.schematic.add_subcircuit_dynamic_link(usb_app, name="uUSB")
    assert app.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
    assert app.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="interpolate")
    assert not app.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="not_good")


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical")
def test_set_sim_solution_on_hfss_subcircuit(usb_app, add_app):
    app = add_app(application=Circuit, project=usb_app.project_name, close_projects=False)
    hfss_comp = app.modeler.schematic.add_subcircuit_dynamic_link(usb_app, name="uUSB")
    assert app.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp)


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical")
def test_assign_excitations(add_app):
    app = add_app(application=Circuit)
    app.modeler.schematic.create_interface_port("Excitation_1", [0, 0])
    app.modeler.schematic.create_interface_port("Excitation_2", ["500mil", 0])
    filepath = TESTS_SEQUENTIAL_PATH / "example_models" / TEST_SUBFOLDER / "frequency_dependent_source.fds"
    ports_list = ["Excitation_1", "Excitation_2"]
    assert app.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, str(filepath))

    filepath = TESTS_SEQUENTIAL_PATH / "example_models" / TEST_SUBFOLDER / "frequency_dependent_source1.fds"
    ports_list = ["Excitation_1", "Excitation_2"]
    assert not app.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, str(filepath))

    filepath = TESTS_SEQUENTIAL_PATH / "example_models" / TEST_SUBFOLDER / "frequency_dependent_source.fds"
    ports_list = ["Excitation_1", "Excitation_3"]
    assert not app.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, str(filepath))

    ports_list = ["Excitation_1"]
    assert app.assign_voltage_sinusoidal_excitation_to_ports(ports_list)
    app.close_project(save=False)


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical")
def test_q2d_link(q2d_app, add_app):
    cir = add_app(application=Circuit, close_projects=False)
    c1 = cir.modeler.schematic.add_subcircuit_dynamic_link(q2d_app, extrusion_length=25)
    assert c1
    assert len(c1.pins) == 6
    assert c1.parameters["Length"] == "25mm"
    assert c1.parameters["r1"] == "0.3mm"
    cir.close_project(save=False)


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical")
def test_q3d_link(q3d_app, add_app):
    cir = add_app(application=Circuit, project=q3d_app.project_name, close_projects=False)

    q3d_comp = cir.modeler.schematic.add_subcircuit_dynamic_link(q3d_app, solution_name="Setup1 : LastAdaptive")
    assert q3d_comp
    assert len(q3d_comp.pins) == 4


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical")
def test_hfss_link(q3d_app, add_app):
    app = add_app(application=Circuit, project=q3d_app.project_name, close_projects=False)
    hfss_app = add_app(application=Hfss, project=q3d_app.project_name, close_projects=False)
    comp = app.modeler.schematic.add_subcircuit_dynamic_link(hfss_app, solution_name="Setup1 : Sweep")
    assert comp
    assert len(comp.pins) == 2
    assert app.modeler.schematic.add_subcircuit_dynamic_link(hfss_app, solution_name="Setup2 : Sweep", tline_port="1")


@pytest.mark.skipif(is_linux, reason="Method not working in Linux")
def test_siwave_link(aedt_app, test_tmp_dir):
    model_o = TESTS_SEQUENTIAL_PATH / "example_models" / TEST_SUBFOLDER / "siwave_syz.siw"
    model = shutil.copy2(model_o, test_tmp_dir / "siwave_syz.siw")
    model_results_o = TESTS_SEQUENTIAL_PATH / "example_models" / TEST_SUBFOLDER / "siwave_syz.siwaveresults"
    shutil.copytree(model_results_o, test_tmp_dir / "siwave_syz.siwaveresults")

    siw_comp = aedt_app.modeler.schematic.add_siwave_dynamic_link(model)
    assert siw_comp
    assert len(siw_comp.pins) == 4


@pytest.mark.skipif(SKIP_CIRCUITS, reason="Skipped because Desktop is crashing")
def test_create_interface_port(aedt_app):
    page_port = aedt_app.modeler.schematic.create_page_port(name="Port12", location=[0, -0.50])
    interface_port = aedt_app.modeler.schematic.create_interface_port(name="Port12", location=[0.3, -0.50])
    second_page_port = aedt_app.modeler.schematic.create_page_port(name="Port12", location=[0.45, -0.5])
    second_interface_port = aedt_app.modeler.schematic.create_interface_port(name="Port122", location=[0.6, -0.50])
    assert not aedt_app.modeler.schematic.create_interface_port(name="Port122", location=[0.6, -0.50])
    assert page_port.composed_name != second_page_port.composed_name
    assert page_port.composed_name != interface_port.name
    assert page_port.composed_name != second_interface_port.name
    assert interface_port.name != second_interface_port.name


def test_q3d_rlgc_link(q3d_app, add_app):
    cir = add_app(application=Circuit, project=q3d_app.project_name, close_projects=False)

    q3d_comp = cir.modeler.schematic.add_q3d_rlgc(q3d_app)
    assert isinstance(q3d_comp, CircuitComponent)
    assert len(q3d_comp.pins) == 6


def test_q3d_rlgc_link_design_name(q3d_app, add_app):
    cir = add_app(application=Circuit, project=q3d_app.project_name, close_projects=False)

    with pytest.raises(ValueError):
        cir.modeler.schematic.add_q3d_rlgc("dummy", solution_name="dummy")

    with pytest.raises(ValueError):
        cir.modeler.schematic.add_q3d_rlgc(q3d_app.design_name)

    with pytest.raises(AEDTRuntimeError):
        cir.modeler.schematic.add_q3d_rlgc("Terminal", solution_name="Setup1 : LastAdaptive")

    q3d_comp = cir.modeler.schematic.add_q3d_rlgc(q3d_app.design_name, solution_name="Setup1 : LastAdaptive")
    assert isinstance(q3d_comp, CircuitComponent)
    assert len(q3d_comp.pins) == 6


def test_q3d_rlgc_link_exception(usb_app, add_app):
    cir = add_app(application=Circuit, project=usb_app.project_name, close_projects=False)

    with pytest.raises(ValueError):
        cir.modeler.schematic.add_q3d_rlgc(usb_app)
