# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.common.create_report import CreateReportExtension
from ansys.aedt.core.extensions.common.create_report import CreateReportExtensionData
from ansys.aedt.core.extensions.common.create_report import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_create_report_generate_button(add_app):
    """Test the Generate button in the Create Report extension."""
    aedt_app = add_app(application=Hfss)

    # Create a simple setup to have some reportable data
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")

    # Create a simple boundary and setup for reporting
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    extension = CreateReportExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()

    assert "CustomReport" == extension.data.report_name
    assert extension.data.open_report
    assert "" == extension.data.save_path  # Default empty save path
    assert main(extension.data)

    # Check if report was generated
    file = f"{extension.data.report_name}.pdf"
    report_path = Path(aedt_app.working_directory) / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)


def test_create_report_custom_name(add_app):
    """Test creating a report with custom name."""
    data = CreateReportExtensionData(
        report_name="CustomReportName",
        open_report=False,
        save_path="",
    )

    aedt_app = add_app(
        application=Hfss,
        project="create_report_custom",
        design="test_custom",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    assert main(data)

    # Check if report was generated
    file = f"{data.report_name}.pdf"
    report_path = Path(aedt_app.working_directory) / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)


def test_create_report_empty_name_exception():
    """Test exception thrown when report name is empty."""
    data = CreateReportExtensionData(report_name="", open_report=False, save_path="")

    with pytest.raises(AEDTRuntimeError) as excinfo:
        main(data)

    assert "Report name cannot be empty" in str(excinfo.value)


def test_create_report_different_design_types(add_app):
    """Test report creation for different design types."""
    # Test HFSS 3D Layout Design (should set design_name to None)
    data = CreateReportExtensionData(report_name="Layout_Report", open_report=False, save_path="")

    # Create mock design type for testing
    aedt_app = add_app(
        application=Hfss,
        project="create_report_layout",
        design="layout_test",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    assert main(data)

    # Check if report was generated
    file = f"{data.report_name}.pdf"
    report_path = Path(aedt_app.working_directory) / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)


def test_create_report_with_plots(add_app):
    """Test report creation when plots exist."""
    data = CreateReportExtensionData(report_name="ReportWithPlots", open_report=False, save_path="")

    aedt_app = add_app(
        application=Hfss,
        project="create_report_plots",
        design="plots_test",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    setup = aedt_app.create_setup("TestSetup")

    # Create a simple plot report
    aedt_app.post.create_report(
        "dB(S(1,1))",
        setup.name,
        variations=None,
        primary_sweep_variable="Freq",
        plot_name="S11_Plot",
    )

    assert main(data)

    # Check if report was generated
    file = f"{data.report_name}.pdf"
    report_path = Path(aedt_app.working_directory) / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)


def test_create_report_open_report_false(add_app):
    """Test report creation with open_report set to False."""
    data = CreateReportExtensionData(report_name="NoOpenReport", open_report=False, save_path="")

    aedt_app = add_app(
        application=Hfss,
        project="create_report_no_open",
        design="no_open_test",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    # Should not try to open the file
    assert main(data)

    # Check if report was generated
    file = f"{data.report_name}.pdf"
    report_path = Path(aedt_app.working_directory) / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)


def test_create_report_extension_ui_integration(add_app):
    """Test the full extension UI integration."""
    aedt_app = add_app(
        application=Hfss,
        project="create_report_ui",
        design="ui_test",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    extension = CreateReportExtension(withdraw=True)

    # Test UI default values
    default_name = extension._widgets["report_name_entry"].get("1.0", "end-1c")
    assert default_name == "CustomReport"
    assert extension._widgets["open_report_var"].get()

    # Test default save path is empty
    default_save_path = extension._widgets["save_path_entry"].get("1.0", "end-1c")
    assert default_save_path == ""

    # Test button click
    extension.root.nametowidget("generate").invoke()

    # Verify data was set correctly
    assert extension.data is not None
    assert "CustomReport" == extension.data.report_name
    assert extension.data.open_report
    assert "" == extension.data.save_path  # Default save path
    aedt_app.close_project(save=False)


def test_create_report_custom_save_path(add_app, test_tmp_dir):
    """Test creating a report with custom save path."""
    aedt_app = add_app(
        application=Hfss,
        project="create_report_custom_path",
        design="test_custom_path",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    data = CreateReportExtensionData(
        report_name="CustomPathReport",
        open_report=False,
        save_path=test_tmp_dir,
    )

    assert main(data)

    # Check if report was generated
    file = f"{data.report_name}.pdf"
    report_path = test_tmp_dir / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)


def test_create_report_empty_save_path_default(add_app):
    """Test that empty save path defaults to working directory."""
    aedt_app = add_app(
        application=Hfss,
        project="create_report_empty_path",
        design="test_empty_path",
    )

    # Create a simple setup
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="TestBox")
    aedt_app.assign_radiation_boundary_to_objects("TestBox")
    aedt_app.create_setup("TestSetup")

    data = CreateReportExtensionData(
        report_name="EmptyPathReport",
        open_report=False,
        save_path="",  # Empty save path
    )

    assert main(data)

    # Check if report was generated
    file = f"{data.report_name}.pdf"
    report_path = Path(aedt_app.working_directory) / file
    assert report_path.is_file()

    aedt_app.close_project(save=False)
