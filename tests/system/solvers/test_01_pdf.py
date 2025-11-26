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

import json
import os
from pathlib import Path
import tempfile

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.visualization.plot.pdf import AnsysReport
from ansys.aedt.core.visualization.post.compliance import VirtualCompliance
from ansys.aedt.core.visualization.post.compliance import VirtualComplianceGenerator
from tests import TESTS_SOLVERS_PATH
from tests.conftest import desktop_version

tol = 1e-12
test_project_name = "ANSYS-HSD_V1_0_test"
test_subfolder = "T01"
test_circuit_name = "Switching_Speed_FET_And_Diode_Solved"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(test_project_name, application=Circuit, subfolder=str(Path(test_subfolder) / "compliance"))
    yield app
    app.odesktop.SetTempDirectory(tempfile.gettempdir())
    app.close_project(save=False)


@pytest.fixture()
def circuit_test(add_app):
    app = add_app(project_name=test_circuit_name, design_name="Diode", application=Circuit, subfolder=test_subfolder)
    yield app
    app.odesktop.SetTempDirectory(tempfile.gettempdir())
    app.close_project(save=False)


def test_create_pdf(local_scratch):
    report = AnsysReport(design_name="Design1", project_name="Coaxial")
    report.aedt_version = desktop_version
    assert "AnsysTemplate" in report.template_name
    report.template_name = "AnsysTemplate"
    assert report.project_name == "Coaxial"
    report.project_name = "Coaxial1"
    assert report.project_name == "Coaxial1"
    assert report.design_name == "Design1"
    report.design_name = "Design2"
    assert report.design_name == "Design2"
    report.create()
    report.add_section()
    report.add_chapter("Chapter 1")
    report.add_sub_chapter("C1")
    report.add_text("ciao")
    report.add_text("hola", True, True)
    report.add_empty_line(2)
    report.add_page_break()
    report.add_image(
        str(Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "Coax_HFSS.jpg"), "Coaxial Cable"
    )
    report.add_section(portrait=False, page_format="a3")
    report.add_table("MyTable", [["x", "y"], ["0", "1"], ["2", "3"], ["10", "20"]])
    report.add_section()
    report.add_chart([0, 1, 2, 3, 4, 5], [10, 20, 4, 30, 40, 12], "Freq", "Val", "MyTable")
    report.add_toc()
    report.save_pdf(local_scratch.path, "my_firstpdf.pdf")
    assert (Path(local_scratch.path) / "my_firstpdf.pdf").exists()


def test_create_pdf_schematic(circuit_test):
    report = AnsysReport()
    report.create()
    assert report.add_project_info(circuit_test)


def test_virtual_compliance(aedtapp, local_scratch):
    template = (
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "general_compliance_template.json"
    )
    template = local_scratch.copyfile(template)
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "ContourEyeDiagram_Custom.json"
    )
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "spisim_erl.cfg"
    )
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "Sparameter_Custom.json"
    )
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "Sparameter_Insertion_Custom.json"
    )
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH)
        / "example_models"
        / test_subfolder
        / "compliance"
        / "StatisticalEyeDiagram_Custom.json"
    )
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "EyeDiagram_Custom.json"
    )

    with open(template, "r+") as f:
        data = json.load(f)
        data["general"]["project"] = str(Path(aedtapp.project_path) / (aedtapp.project_name + ".aedt"))
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    compliance_folder = Path(local_scratch.path) / "vc"
    os.makedirs(compliance_folder, exist_ok=True)
    vc = VirtualComplianceGenerator("Test_full", "Diff_Via")
    vc.dut_image = Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "nets.jpg"
    vc.project_file = aedtapp.project_file
    vc.add_report_from_folder(
        input_folder=Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance",
        design_name="Circuit1",
        group_plots=True,
        project=aedtapp.project_file,
    )
    if is_windows:
        vc.add_erl_parameters(
            design_name=aedtapp.design_name,
            config_file=compliance_folder / "config.cfg",
            traces=["RX1", "RX3"],
            pins=[
                [
                    "X1_A5_PCIe_Gen4_RX1_P",
                    "X1_A6_PCIe_Gen4_RX1_N",
                    "U1_AR25_PCIe_Gen4_RX1_P",
                    "U1_AP25_PCIe_Gen4_RX1_N",
                ],
                [7, 8, 18, 17],
            ],
            pass_fail=True,
            pass_fail_criteria=3,
            name="ERL",
        )
    local_scratch.copyfile(
        Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "compliance" / "skew.json",
        Path(compliance_folder) / "skew.json",
    )
    vc.add_report_derived_parameter(
        design_name="skew",
        parameter="skew",
        config_file=compliance_folder / "skew.json",
        traces=["V(V_Rx)", "V(V_Rx8)"],
        report_type="time",
        pass_fail_criteria=0.2,
        name="Differential Skew",
    )
    vc.save_configuration(compliance_folder / "main.json")
    assert (compliance_folder / "main.json").exists()
    v = VirtualCompliance(aedtapp.desktop_class, compliance_folder / "main.json")
    assert v.create_compliance_report(close_project=False)


def test_spisim_raw_read(local_scratch):
    from ansys.aedt.core.visualization.post.spisim import SpiSimRawRead

    raw_file = Path(TESTS_SOLVERS_PATH) / "example_models" / test_subfolder / "SerDes_Demo_02_Thru.s4p_ERL.raw"
    raw_file = local_scratch.copyfile(raw_file)

    raw_file = SpiSimRawRead(raw_file)
    assert raw_file.get_raw_property()
    assert len(raw_file.get_raw_property("Variables"))
    assert raw_file.trace_names
    assert len(raw_file["time"])
    assert len(raw_file.get_trace(0))
    assert len(raw_file.get_wave(raw_file.trace_names[0])) == len(raw_file.get_axis())
    assert raw_file.__len__() > 0
