# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import tkinter
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import PushExcitation3DLayoutExtension
from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import PushExcitation3DLayoutExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_main_function_exceptions():
    """Test exceptions in the main function."""
    # Test with no choice
    data = PushExcitation3DLayoutExtensionData(choice="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with no file path
    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with non-existent file
    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="nonexistent.csv")
    with pytest.raises(AEDTRuntimeError):
        main(data)


@pytest.fixture
def mock_hfss3dl_app_with_excitations(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout application with
    excitations.
    """
    mock_hfss_3d_layout_app.excitation_names = ["Port1", "Port2"]
    yield mock_hfss_3d_layout_app


def test_push_excitation_3dlayout_extension_default(
    mock_hfss3dl_app_with_excitations,
):
    """Test instantiation of the Push Excitation 3D Layout extension."""
    extension = PushExcitation3DLayoutExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_push_excitation_3dlayout_extension_generate_button(
    mock_hfss3dl_app_with_excitations,
):
    """Test the generate button in the Push Excitation 3D Layout
    extension.
    """
    extension = PushExcitation3DLayoutExtension(withdraw=True)

    # Set a test file path
    extension.file_entry.delete("1.0", tkinter.END)
    extension.file_entry.insert(tkinter.END, "test_file.csv")

    # Mock file existence
    with patch("pathlib.Path.is_file", return_value=True):
        extension.root.nametowidget("generate").invoke()

    data: PushExcitation3DLayoutExtensionData = extension.data

    # The first excitation should be selected by default
    assert "Port1" == data.choice
    assert "test_file.csv" == data.file_path


def test_push_excitation_3dlayout_extension_exceptions(
    mock_hfss3dl_app_with_excitations,
):
    """Test exceptions in the Push Excitation 3D Layout extension."""
    # Test exception when no excitations exist
    mock_hfss3dl_app_with_excitations.excitation_names = []
    with pytest.raises(AEDTRuntimeError):
        PushExcitation3DLayoutExtension(withdraw=True)

    # Reset to valid state
    mock_hfss3dl_app_with_excitations.excitation_names = [
        "Port1",
        "Port2",
    ]

    # Test exception when no port is selected
    extension = PushExcitation3DLayoutExtension(withdraw=True)
    extension.port_combo.set("")
    extension.file_entry.delete("1.0", tkinter.END)
    extension.file_entry.insert(tkinter.END, "valid_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        with pytest.raises(TclError):
            extension.root.nametowidget("generate").invoke()

    # Test exception when no file is selected
    extension = PushExcitation3DLayoutExtension(withdraw=True)
    extension.file_entry.delete("1.0", tkinter.END)

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test exception when file doesn't exist
    extension = PushExcitation3DLayoutExtension(withdraw=True)
    extension.file_entry.delete("1.0", tkinter.END)
    extension.file_entry.insert(tkinter.END, "nonexistent_file.csv")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()


def test_push_excitation_3dlayout_extension_browse_files(
    mock_hfss3dl_app_with_excitations,
):
    """Test the browse files functionality."""
    extension = PushExcitation3DLayoutExtension(withdraw=True)

    # Mock filedialog
    with patch(
        "tkinter.filedialog.askopenfilename",
        return_value="selected_file.csv",
    ):
        extension.browse_files()

    # Verify the file path was set
    file_content = extension.file_entry.get("1.0", tkinter.END).strip()
    assert "selected_file.csv" == file_content

    # Test when no file is selected
    with patch("tkinter.filedialog.askopenfilename", return_value=""):
        extension.browse_files()

    # File content should remain the same
    file_content = extension.file_entry.get("1.0", tkinter.END).strip()
    assert "selected_file.csv" == file_content


def test_push_excitation_3dlayout_extension_wrong_design_type():
    """Test exception when design type is not HFSS 3D Layout."""
    mock_app = MagicMock()
    mock_app.design_type = "HFSS"

    from ansys.aedt.core.extensions.misc import ExtensionCommon

    with patch.object(
        ExtensionCommon,
        "aedt_application",
        new_callable=PropertyMock,
    ) as mock_property:
        mock_property.return_value = mock_app

        with pytest.raises(AEDTRuntimeError):
            PushExcitation3DLayoutExtension(withdraw=True)


@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.get_pyaedt_app")
def test_main_function_success(mock_get_pyaedt_app, mock_desktop):
    """Test successful execution of main function."""
    # Mock the desktop and apps
    mock_app = MagicMock()
    mock_desktop.return_value = mock_app

    mock_project = MagicMock()
    mock_project.GetName.return_value = "test_project"
    mock_app.active_project.return_value = mock_project

    mock_design = MagicMock()
    mock_design.GetDesignType.return_value = "HFSS 3D Layout Design"
    mock_design.GetName.return_value = "test_design;test_layout"
    mock_app.active_design.return_value = mock_design

    mock_hfss3dl = MagicMock()
    mock_hfss3dl.design_type = "HFSS 3D Layout Design"
    mock_hfss3dl.logger = MagicMock()
    mock_get_pyaedt_app.return_value = mock_hfss3dl

    # Create test data
    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="test_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        result = main(data)

    assert result is True
    mock_hfss3dl.edit_source_from_file.assert_called_once_with(
        source="Port1", input_file="test_file.csv", is_time_domain=True
    )


@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.ansys.aedt.core.Desktop")
def test_main_function_no_active_project(mock_desktop):
    """Test main function when no active project exists."""
    mock_app = MagicMock()
    mock_desktop.return_value = mock_app
    mock_app.active_project.return_value = None

    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="test_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        with pytest.raises(AEDTRuntimeError, match="No active project found"):
            main(data)


@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.ansys.aedt.core.Desktop")
def test_main_function_no_active_design(mock_desktop):
    """Test main function when no active design exists."""
    mock_app = MagicMock()
    mock_desktop.return_value = mock_app

    mock_project = MagicMock()
    mock_project.GetName.return_value = "test_project"
    mock_app.active_project.return_value = mock_project
    mock_app.active_design.return_value = None

    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="test_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        with pytest.raises(AEDTRuntimeError, match="No active design found"):
            main(data)


@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.ansys.aedt.core.Desktop")
def test_main_function_wrong_design_type(mock_desktop):
    """Test main function with wrong design type."""
    mock_app = MagicMock()
    mock_desktop.return_value = mock_app

    mock_project = MagicMock()
    mock_project.GetName.return_value = "test_project"
    mock_app.active_project.return_value = mock_project

    mock_design = MagicMock()
    mock_design.GetDesignType.return_value = "HFSS"
    mock_app.active_design.return_value = mock_design

    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="test_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        with pytest.raises(
            AEDTRuntimeError,
            match="This extension only works with HFSS 3D Layout designs",
        ):
            main(data)


@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl.get_pyaedt_app")
def test_main_function_wrong_app_design_type(mock_get_pyaedt_app, mock_desktop):
    """Test main function when pyaedt app has wrong design type."""
    # Mock the desktop and apps
    mock_app = MagicMock()
    mock_desktop.return_value = mock_app

    mock_project = MagicMock()
    mock_project.GetName.return_value = "test_project"
    mock_app.active_project.return_value = mock_project

    mock_design = MagicMock()
    mock_design.GetDesignType.return_value = "HFSS 3D Layout Design"
    mock_design.GetName.return_value = "test_design;test_layout"
    mock_app.active_design.return_value = mock_design

    mock_hfss3dl = MagicMock()
    mock_hfss3dl.design_type = "HFSS"  # Wrong design type
    mock_get_pyaedt_app.return_value = mock_hfss3dl

    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="test_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        with pytest.raises(
            AEDTRuntimeError,
            match="This extension only works with HFSS 3D Layout designs",
        ):
            main(data)


def test_push_excitation_3dlayout_extension_data_dataclass():
    """Test the PushExcitation3DLayoutExtensionData dataclass."""
    # Test default values
    data = PushExcitation3DLayoutExtensionData()
    assert data.choice == ""
    assert data.file_path == ""

    # Test with values
    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="test.csv")
    assert data.choice == "Port1"
    assert data.file_path == "test.csv"
