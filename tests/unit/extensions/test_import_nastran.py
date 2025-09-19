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

import tkinter
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.common.import_nastran import EXTENSION_TITLE
from ansys.aedt.core.extensions.common.import_nastran import ImportNastranExtension
from ansys.aedt.core.extensions.common.import_nastran import ImportNastranExtensionData
from ansys.aedt.core.extensions.common.import_nastran import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_import_nastran_extension_default():
    """Test instantiation of the Import Nastran extension."""
    extension = ImportNastranExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename")
def test_import_nastran_extension_import_button(mock_askopenfilename):
    """Test the Import button in the Import Nastran extension."""
    mock_file_path = "/mock/path/test_file.nas"
    mock_askopenfilename.return_value = mock_file_path

    extension = ImportNastranExtension(withdraw=True)

    # Simulate file selection
    extension.root.nametowidget("browse_button").invoke()

    # Set decimation factor
    extension._ImportNastranExtension__decimation_text.delete("1.0", tkinter.END)
    extension._ImportNastranExtension__decimation_text.insert(tkinter.END, "0.1")

    # Enable lightweight option
    extension._ImportNastranExtension__lightweight_var.set(1)

    # Disable planar option
    extension._ImportNastranExtension__planar_var.set(0)

    # Mock the file existence check
    with patch("pathlib.Path.is_file", return_value=True):
        extension.root.nametowidget("import_button").invoke()

    data: ImportNastranExtensionData = extension.data

    assert data.decimate == 0.1
    assert data.lightweight is True
    assert data.planar is False
    assert data.file_path == mock_file_path


@patch("tkinter.filedialog.askopenfilename")
def test_import_nastran_switch_to_dark_theme(mock_askopenfilename):
    """Test theme toggle button when switching to dark theme."""
    extension = ImportNastranExtension(withdraw=True)
    assert extension.root.theme == "light"

    toggle_theme = extension.root.nametowidget("theme_button_frame.theme_toggle_button")
    toggle_theme.invoke()

    assert extension.root.theme == "dark"

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename")
def test_import_nastran_switch_to_light_theme(mock_askopenfilename):
    """Test theme toggle button when switching to light theme."""
    extension = ImportNastranExtension(withdraw=True)

    # Switch to dark first
    toggle_theme = extension.root.nametowidget("theme_button_frame.theme_toggle_button")
    toggle_theme.invoke()
    assert extension.root.theme == "dark"

    # Switch back to light
    toggle_theme.invoke()
    assert extension.root.theme == "light"

    extension.root.destroy()


def test_main_function_exceptions():
    """Test exceptions thrown by the main function."""
    # Test no file path
    data = ImportNastranExtensionData(file_path="")
    with pytest.raises(AEDTRuntimeError, match="No file path provided"):
        main(data)

    # Test file not found
    data = ImportNastranExtensionData(file_path="/nonexistent/file.nas")
    with pytest.raises(AEDTRuntimeError, match="File .* not found"):
        main(data)

    # Test invalid decimation factor
    data = ImportNastranExtensionData(file_path="/mock/path/test.nas", decimate=1.5)
    with pytest.raises(AEDTRuntimeError, match="Decimation factor must be between 0 and 0.9"):
        main(data)

    data = ImportNastranExtensionData(file_path="/mock/path/test.nas", decimate=-0.1)
    with pytest.raises(AEDTRuntimeError, match="Decimation factor must be between 0 and 0.9"):
        main(data)


@patch("ansys.aedt.core.Desktop")
@patch("pathlib.Path.is_file", return_value=True)
def test_main_function_no_active_project(mock_is_file, mock_desktop):
    """Test main function with no active project."""
    mock_desktop_instance = mock_desktop.return_value
    mock_desktop_instance.active_project.return_value = None

    data = ImportNastranExtensionData(file_path="/mock/path/test.nas")

    with pytest.raises(AEDTRuntimeError, match="No active project found"):
        main(data)


@patch("ansys.aedt.core.Desktop")
@patch("pathlib.Path.is_file", return_value=True)
def test_main_function_no_active_design(mock_is_file, mock_desktop):
    """Test main function with no active design."""
    mock_desktop_instance = mock_desktop.return_value
    mock_project = mock_desktop_instance.active_project.return_value
    mock_project.GetName.return_value = "TestProject"
    mock_desktop_instance.active_design.return_value = None

    data = ImportNastranExtensionData(file_path="/mock/path/test.nas")

    with pytest.raises(AEDTRuntimeError, match="No active design found"):
        main(data)
