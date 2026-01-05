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

import json
from pathlib import Path
import shutil

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.visualization.plot.pdf import AnsysReport
from ansys.aedt.core.visualization.post.compliance import VirtualCompliance
from ansys.aedt.core.visualization.post.compliance import VirtualComplianceGenerator
from tests import TESTS_SOLVERS_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "T01"
ANSYS_HSD_V1_0 = "ANSYS-HSD_V1_0_test"

TEST_CIRCUIT = "Switching_Speed_FET_And_Diode_Solved"


@pytest.fixture
def aedt_app(add_app_example):
    app = add_app_example(
        project=ANSYS_HSD_V1_0,
        application=Circuit,
        subfolder=TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance",
    )
    yield app
    app.close_project(save=False)


@pytest.fixture
def circuit_test(add_app_example):
    app = add_app_example(project=TEST_CIRCUIT, design="Diode", application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


def test_create_pdf(test_tmp_dir):
    report = AnsysReport(design_name="Design1", project_name="Coaxial")
    report.aedt_version = DESKTOP_VERSION
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
        str(Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "Coax_HFSS.jpg"), "Coaxial Cable"
    )
    report.add_section(portrait=False, page_format="a3")
    report.add_table("MyTable", [["x", "y"], ["0", "1"], ["2", "3"], ["10", "20"]])
    report.add_section()
    report.add_chart([0, 1, 2, 3, 4, 5], [10, 20, 4, 30, 40, 12], "Freq", "Val", "MyTable")
    report.add_toc()
    report.save_pdf(test_tmp_dir, "my_firstpdf.pdf")
    output = test_tmp_dir / "my_firstpdf.pdf"
    assert output.exists()


def test_create_pdf_schematic(circuit_test):
    report = AnsysReport()
    report.create()
    assert report.add_project_info(circuit_test)


def test_virtual_compliance(aedt_app, test_tmp_dir):
    example_template = (
        TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "general_compliance_template.json"
    )
    template = shutil.copy2(example_template, test_tmp_dir / "general_compliance_template.json")

    template2 = TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "ContourEyeDiagram_Custom.json"
    shutil.copy2(template2, test_tmp_dir / "ContourEyeDiagram_Custom.json")

    template3 = TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "spisim_erl.cfg"
    shutil.copy2(template3, test_tmp_dir / "spisim_erl.cfg")

    template4 = TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "Sparameter_Custom.json"
    shutil.copy2(template4, test_tmp_dir / "Sparameter_Custom.json")

    template5 = (
        TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "Sparameter_Insertion_Custom.json"
    )
    shutil.copy2(template5, test_tmp_dir / "Sparameter_Insertion_Custom.json")

    template6 = (
        TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "StatisticalEyeDiagram_Custom.json"
    )
    shutil.copy2(template6, test_tmp_dir / "StatisticalEyeDiagram_Custom.json")

    template7 = TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "EyeDiagram_Custom.json"
    shutil.copy2(template7, test_tmp_dir / "EyeDiagram_Custom.json")

    with open(template, "r+") as f:
        data = json.load(f)
        data["general"]["project"] = str(Path(aedt_app.project_path) / (aedt_app.project_name + ".aedt"))
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    compliance_folder = test_tmp_dir / "vc"
    compliance_folder.mkdir(parents=True, exist_ok=True)
    net_image_original = Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "nets.jpg"
    net_image = shutil.copy2(net_image_original, test_tmp_dir / "nets.jpg")

    vc = VirtualComplianceGenerator("Test_full", "Diff_Via")
    vc.dut_image = str(net_image)
    vc.project_file = aedt_app.project_file
    vc.add_report_from_folder(
        input_folder=test_tmp_dir,
        design_name="Circuit1",
        group_plots=True,
        project=aedt_app.project_file,
    )
    if is_windows:
        vc.add_erl_parameters(
            design_name=aedt_app.design_name,
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

    skew_file = TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "compliance" / "skew.json"
    shutil.copy2(skew_file, compliance_folder / "skew.json")

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
    v = VirtualCompliance(aedt_app.desktop_class, compliance_folder / "main.json")
    assert v.create_compliance_report(close_project=False)


def test_spisim_raw_read(test_tmp_dir):
    from ansys.aedt.core.visualization.post.spisim import SpiSimRawRead

    example_raw_file = TESTS_SOLVERS_PATH / "example_models" / TEST_SUBFOLDER / "SerDes_Demo_02_Thru.s4p_ERL.raw"
    raw_file = shutil.copy2(example_raw_file, test_tmp_dir / "SerDes_Demo_02_Thru.s4p_ERL.raw")

    raw_file = SpiSimRawRead(raw_file)
    assert raw_file.get_raw_property()
    assert len(raw_file.get_raw_property("Variables"))
    assert raw_file.trace_names
    assert len(raw_file["time"])
    assert len(raw_file.get_trace(0))
    assert len(raw_file.get_wave(raw_file.trace_names[0])) == len(raw_file.get_axis())
    assert raw_file.__len__() > 0
