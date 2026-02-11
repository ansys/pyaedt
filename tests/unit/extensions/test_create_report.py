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

import tkinter
from tkinter import TclError

import pytest

from ansys.aedt.core.extensions.common.create_report import EXTENSION_TITLE
from ansys.aedt.core.extensions.common.create_report import CreateReportExtension
from ansys.aedt.core.extensions.common.create_report import CreateReportExtensionData


def test_create_report_extension_default() -> None:
    """Test instantiation of the Create Report extension."""
    try:
        extension = CreateReportExtension(withdraw=True)
        assert EXTENSION_TITLE == extension.root.title()
        assert "light" == extension.root.theme
        extension.root.destroy()
    except TclError:
        # Expected in headless environments
        pytest.skip("Tkinter not available in headless environment")


def test_create_report_extension_generate_button() -> None:
    """Test the generate button functionality."""
    extension = CreateReportExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()
    data: CreateReportExtensionData = extension.data

    assert "CustomReport" == data.report_name
    assert data.open_report
    assert "" == data.save_path  # Default empty save path


def test_create_report_extension_custom_values() -> None:
    """Test custom report name, checkbox values, and save path."""
    extension = CreateReportExtension(withdraw=True)
    report_name_entry = extension._widgets["report_name_entry"]
    save_path_entry = extension._widgets["save_path_entry"]
    # Change report name
    report_name_entry.delete("1.0", tkinter.END)
    report_name_entry.insert(tkinter.END, "CustomReport")

    # Uncheck open report
    extension._widgets["open_report_var"].set(False)

    # Set custom save path
    save_path_entry.delete("1.0", tkinter.END)
    save_path_entry.insert(tkinter.END, "/custom/path")

    extension.root.nametowidget("generate").invoke()
    data: CreateReportExtensionData = extension.data

    assert "CustomReport" == data.report_name
    assert not data.open_report
    assert "/custom/path" == data.save_path


def test_create_report_extension_empty_name() -> None:
    """Test behavior with empty report name."""
    extension = CreateReportExtension(withdraw=True)

    # Clear report name
    extension._widgets["report_name_entry"].delete("1.0", tkinter.END)

    extension.root.nametowidget("generate").invoke()
    data: CreateReportExtensionData = extension.data

    assert "" == data.report_name
    assert data.open_report
    assert "" == data.save_path  # Should still be empty


def test_create_report_extension_data_class() -> None:
    """Test the CreateReportExtensionData class."""
    # Test default values
    data = CreateReportExtensionData()
    assert "CustomReport" == data.report_name
    assert data.open_report
    assert "" == data.save_path

    # Test custom values
    data = CreateReportExtensionData(
        report_name="CustomReport",
        open_report=False,
        save_path="",
    )
    assert "CustomReport" == data.report_name
    assert not data.open_report
    assert "" == data.save_path


def test_create_report_extension_ui_elements() -> None:
    """Test UI elements are properly created."""
    try:
        extension = CreateReportExtension(withdraw=True)

        # Check widgets exist
        assert extension._widgets["report_name_entry"] is not None
        assert extension._widgets["open_report_var"] is not None
        assert extension._widgets["save_path_entry"] is not None

        # Check default values
        report_name = extension._widgets["report_name_entry"].get("1.0", tkinter.END).strip()
        assert "CustomReport" == report_name
        assert extension._widgets["open_report_var"].get()

        save_path = extension._widgets["save_path_entry"].get("1.0", tkinter.END).strip()
        assert "" == save_path

        extension.root.destroy()
    except TclError:
        # Expected in headless environments
        pytest.skip("Tkinter not available in headless environment")


def test_create_report_extension_callback_function() -> None:
    """Test the callback function sets data correctly."""
    extension = CreateReportExtension(withdraw=True)

    # Modify values
    extension._widgets["report_name_entry"].delete("1.0", tkinter.END)
    extension._widgets["report_name_entry"].insert(tkinter.END, "TestCallback")
    extension._widgets["open_report_var"].set(False)

    extension._widgets["save_path_entry"].delete("1.0", tkinter.END)
    extension._widgets["save_path_entry"].insert(tkinter.END, "/callback/path")

    # Trigger callback
    extension.root.nametowidget("generate").invoke()

    # Check data was set
    assert extension.data is not None
    assert "TestCallback" == extension.data.report_name
    assert "/callback/path" == extension.data.save_path


def test_create_report_extension_save_path_functionality() -> None:
    """Test the save path UI functionality."""
    extension = CreateReportExtension(withdraw=True)

    # Test default empty save path
    save_path = extension._widgets["save_path_entry"].get("1.0", tkinter.END).strip()
    assert "" == save_path

    # Set a custom save path
    test_path = ""
    extension._widgets["save_path_entry"].delete("1.0", tkinter.END)
    extension._widgets["save_path_entry"].insert(tkinter.END, test_path)

    # Verify the path was set
    saved_path = extension._widgets["save_path_entry"].get("1.0", tkinter.END).strip()
    assert test_path == saved_path

    # Test data capture with custom save path
    extension.root.nametowidget("generate").invoke()
    assert extension.data is not None
    assert test_path == extension.data.save_path
