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

from ansys.aedt.core import Circuit
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.generic.settings import is_linux
import pytest

from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import config

test_subfloder = "T22"
test_project_name = "Dynamic_Link"
src_design_name = "uUSB"
if config["desktopVersion"] > "2022.2":
    src_project_name = "USB_Connector_231"
    linked_project_name = "Filter_Board_231"
else:
    src_project_name = "USB_Connector"
    linked_project_name = "Filter_Board"


@pytest.fixture(scope="class", autouse=True)
def dummy_prj(add_app):
    app = add_app("Dummy_license_checkout_prj")
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def aedtapp(add_app, local_scratch):
    example_project = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, test_project_name + ".aedt")
    test_project = local_scratch.copyfile(example_project)
    local_scratch.copyfolder(
        os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, test_project_name + ".aedb"),
        os.path.join(local_scratch.path, test_project_name + ".aedb"),
    )

    linked_project = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, linked_project_name + ".aedt")
    test_lkd_project = local_scratch.copyfile(linked_project)
    local_scratch.copyfolder(
        os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, linked_project_name + ".aedb"),
        os.path.join(local_scratch.path, linked_project_name + ".aedb"),
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
    app.close_project(app.project_name)


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    source_project = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, src_project_name + ".aedt")
    src_project_file = local_scratch.copyfile(source_project)
    q3d = local_scratch.copyfile(os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, "q2d_q3d.aedt"))
    return src_project_file, q3d


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, examples):
        self.local_scratch = local_scratch
        self.src_project_file = examples[0]
        self.q3d = examples[1]

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_02_add_subcircuits_3dlayout(self, aedtapp):
        layout_design = "layout_cutout"
        hfss3Dlayout_comp = aedtapp.modeler.schematic.add_subcircuit_3dlayout(layout_design)
        assert hfss3Dlayout_comp.id == 86
        assert hfss3Dlayout_comp

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical.")
    def test_03_add_subcircuits_hfss_link(self, add_app, aedtapp):
        pin_names = aedtapp.get_source_pin_names(src_design_name, src_project_name, self.src_project_file, 2)
        assert len(pin_names) == 4
        assert "usb_P_pcb" in pin_names
        hfss = add_app(project_name=self.src_project_file, design_name="uUSB", just_open=True)
        hfss_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(hfss, comp_name="uUSB")
        assert hfss_comp.id == 87
        assert hfss_comp.composed_name == "CompInst@uUSB;87;3"

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_04_refresh_dynamic_link(self, aedtapp):
        assert aedtapp.modeler.schematic.refresh_dynamic_link("uUSB")

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_05_set_sim_option_on_hfss_subcircuit(self, aedtapp):
        hfss_comp = "CompInst@uUSB;87;3"
        assert aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
        assert aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="interpolate")
        assert not aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="not_good")

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_06_set_sim_solution_on_hfss_subcircuit(self, aedtapp):
        hfss_comp = "CompInst@uUSB;87;3"
        assert aedtapp.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp)

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_07_create_page_port_and_interface_port(self, aedtapp):
        hfss_comp_id = 1
        hfss3Dlayout_comp_id = 3
        hfssComp_pins = aedtapp.modeler.schematic.get_pins(hfss_comp_id)
        assert type(hfssComp_pins) is list
        assert len(hfssComp_pins) == 4
        hfss_pin2location = {}
        for pin in hfssComp_pins:
            hfss_pin2location[pin] = aedtapp.modeler.schematic.get_pin_location(hfss_comp_id, pin)
            assert len(hfss_pin2location[pin]) == 2

        hfss3DlayoutComp_pins = aedtapp.modeler.schematic.get_pins(hfss3Dlayout_comp_id)
        assert type(hfssComp_pins) is list
        assert len(hfssComp_pins) == 4
        hfss3Dlayout_pin2location = {}
        for pin in hfss3DlayoutComp_pins:
            hfss3Dlayout_pin2location[pin] = aedtapp.modeler.schematic.get_pin_location(hfss3Dlayout_comp_id, pin)
            assert len(hfss3Dlayout_pin2location[pin]) == 2

        # Link 1 Creation
        portname = aedtapp.modeler.schematic.create_page_port(
            "Link1", [hfss3Dlayout_pin2location["usb_N_conn"][0], hfss3Dlayout_pin2location["usb_N_conn"][1]], 180
        )
        assert "Link1" in portname.composed_name
        portname = aedtapp.modeler.schematic.create_page_port(
            "Link1",
            [hfss_pin2location["J3B2.3.USBH2_DP_CH"][0], hfss_pin2location["J3B2.3.USBH2_DP_CH"][1]],
            90,
        )
        assert "Link1" in portname.composed_name

        # Link 2 Creation
        portname = aedtapp.modeler.schematic.create_page_port(
            "Link2", [hfss3Dlayout_pin2location["usb_N_pcb"][0], hfss3Dlayout_pin2location["usb_N_pcb"][1]], 180
        )
        assert "Link2" in portname.composed_name
        portname = aedtapp.modeler.schematic.create_page_port(
            "Link2",
            [hfss_pin2location["L3M1.3.USBH2_DN_CH"][0], hfss_pin2location["L3M1.3.USBH2_DN_CH"][1]],
            270,
        )
        assert "Link2" in portname.composed_name

        # Ports Creation
        portname = aedtapp.modeler.schematic.create_interface_port(
            "Excitation_1", [hfss3Dlayout_pin2location["USB_VCC_T1"][0], hfss3Dlayout_pin2location["USB_VCC_T1"][1]]
        )
        assert "Excitation_1" in portname.name
        portname = aedtapp.modeler.schematic.create_interface_port(
            "Excitation_2", [hfss3Dlayout_pin2location["usb_P_pcb"][0], hfss3Dlayout_pin2location["usb_P_pcb"][1]]
        )
        assert "Excitation_2" in portname.name
        portname = aedtapp.modeler.schematic.create_interface_port(
            "Port_1",
            [hfss_pin2location["L3M1.2.USBH2_DP_CH"][0], hfss_pin2location["L3M1.2.USBH2_DP_CH"][1]],
        )
        assert "Port_1" in portname.name
        portname = aedtapp.modeler.schematic.create_interface_port(
            "Port_2",
            [hfss_pin2location["J3B2.2.USBH2_DN_CH"][0], hfss_pin2location["J3B2.2.USBH2_DN_CH"][1]],
        )
        assert "Port_2" in portname.name

        portname = aedtapp.modeler.schematic.create_interface_port(
            "Port_remove",
            [hfss_pin2location["J3B2.2.USBH2_DN_CH"][0], hfss_pin2location["J3B2.2.USBH2_DN_CH"][1]],
        )
        aedtapp.design_excitations[portname.name].delete()

        assert "Port_remove" not in aedtapp.excitation_names

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_08_assign_excitations(self, aedtapp):
        filepath = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, "frequency_dependent_source.fds")
        ports_list = ["Excitation_1", "Excitation_2"]
        assert aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, filepath)

        filepath = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, "frequency_dependent_source1.fds")
        ports_list = ["Excitation_1", "Excitation_2"]
        assert not aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, filepath)

        filepath = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, "frequency_dependent_source.fds")
        ports_list = ["Excitation_1", "Excitation_3"]
        assert not aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, filepath)

        ports_list = ["Excitation_1"]
        assert aedtapp.assign_voltage_sinusoidal_excitation_to_ports(ports_list)

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_10_q2d_link(self, add_app, aedtapp):
        q2d = add_app(application=Q2d, project_name=self.q3d, just_open=True)
        c1 = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(q2d, extrusion_length=25)
        assert c1
        assert len(c1.pins) == 6
        assert c1.parameters["Length"] == "25mm"
        assert c1.parameters["r1"] == "0.3mm"

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_10_q3d_link(self, add_app, aedtapp):
        q3d = add_app(application=Q3d, project_name=self.q3d, just_open=True)

        q3d_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(q3d, solution_name="Setup1 : LastAdaptive")
        assert q3d_comp
        assert len(q3d_comp.pins) == 4

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_10_hfss_link(self, add_app, aedtapp):
        hfss = add_app(project_name=self.q3d, just_open=True)

        hfss_comp = aedtapp.modeler.schematic.add_subcircuit_dynamic_link(hfss, solution_name="Setup1 : Sweep")
        assert hfss_comp
        assert len(hfss_comp.pins) == 2
        hfss2 = add_app(project_name=self.q3d, just_open=True)
        assert aedtapp.modeler.schematic.add_subcircuit_dynamic_link(
            hfss2, solution_name="Setup2 : Sweep", tline_port="1"
        )

    @pytest.mark.skipif(config["NonGraphical"] and is_linux, reason="Method not working in Linux and Non graphical")
    def test_11_siwave_link(self, aedtapp):
        model = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfloder, "siwave_syz.siw")
        model_out = self.local_scratch.copyfile(model)
        self.local_scratch.copyfolder(
            model + "averesults", os.path.join(self.local_scratch.path, "siwave_syz.siwaveresults")
        )
        siw_comp = aedtapp.modeler.schematic.add_siwave_dynamic_link(model_out)
        assert siw_comp
        assert len(siw_comp.pins) == 4

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_12_create_interface_port(self, aedtapp):
        page_port = aedtapp.modeler.components.create_page_port(name="Port12", location=[0, -0.50])
        interface_port = aedtapp.modeler.components.create_interface_port(name="Port12", location=[0.3, -0.50])
        second_page_port = aedtapp.modeler.components.create_page_port(name="Port12", location=[0.45, -0.5])
        second_interface_port = aedtapp.modeler.components.create_interface_port(name="Port122", location=[0.6, -0.50])
        assert not aedtapp.modeler.components.create_interface_port(name="Port122", location=[0.6, -0.50])
        assert page_port.composed_name != second_page_port.composed_name
        assert page_port.composed_name != interface_port.name
        assert page_port.composed_name != second_interface_port.name
        assert interface_port.name != second_interface_port.name
