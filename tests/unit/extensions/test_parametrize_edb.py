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
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import ParametrizeEdbExtension
from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import ParametrizeEdbExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_aedt_app(mock_hfss_3d_layout_app):
    """Fixture to create a mock AEDT application."""
    mock_active_project = MagicMock()
    mock_active_project.GetPath.return_value = "/path/to/project"
    mock_active_project.GetName.return_value = "test_project"

    mock_active_design = MagicMock()
    mock_active_design.GetName.return_value = "cell;test_design"

    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_active_project
    mock_desktop.active_design.return_value = mock_active_design

    # Mock EDB
    mock_edb = MagicMock()
    mock_edb.nets.nets.keys.return_value = ["net1", "net2", "GND", "VCC"]

    with patch("ansys.aedt.core.Desktop") as mock_desktop_class:
        mock_desktop_class.return_value = mock_desktop
        mock_edb_patch = "ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb.Edb"
        with patch(mock_edb_patch) as mock_edb_class:
            mock_edb_class.return_value = mock_edb
            yield mock_desktop


def test_parametrize_edb_extension_default(mock_aedt_app):
    """Test instantiation of the Parametrize EDB extension."""
    extension = ParametrizeEdbExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_parametrize_edb_extension_generate_button(mock_aedt_app):
    """Test Generate button in the Parametrize EDB extension."""
    extension = ParametrizeEdbExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()
    data: ParametrizeEdbExtensionData = extension.data

    assert data.parametrize_layers is True
    assert data.parametrize_materials is True
    assert data.parametrize_padstacks is True
    assert data.parametrize_traces is True
    assert data.expansion_polygon_mm == 0.0
    assert data.expansion_void_mm == 0.0
    assert data.relative_parametric is True


def test_parametrize_edb_extension_data_defaults():
    """Test default values in ParametrizeEdbExtensionData."""
    data = ParametrizeEdbExtensionData()

    assert data.aedb_path == ""
    assert data.design_name == ""
    assert data.parametrize_layers is True
    assert data.parametrize_materials is True
    assert data.parametrize_padstacks is True
    assert data.parametrize_traces is True
    assert data.nets_filter == []
    assert data.expansion_polygon_mm == 0.0
    assert data.expansion_void_mm == 0.0
    assert data.relative_parametric is True
    assert data.project_name == ""


def test_parametrize_edb_extension_custom_values(mock_aedt_app):
    """Test setting custom values in the extension."""
    extension = ParametrizeEdbExtension(withdraw=True)

    # Set custom values
    extension.project_name_entry.delete(0, tkinter.END)
    extension.project_name_entry.insert(0, "custom_project")

    extension.relative_var.set(0)
    extension.layers_var.set(0)
    extension.materials_var.set(0)
    extension.padstacks_var.set(0)
    extension.traces_var.set(0)

    extension.polygons_entry.delete("1.0", tkinter.END)
    extension.polygons_entry.insert(tkinter.END, "1.5")

    extension.voids_entry.delete("1.0", tkinter.END)
    extension.voids_entry.insert(tkinter.END, "2.0")

    # Select some nets
    extension.nets_listbox.selection_set(0, 1)

    extension.root.nametowidget("generate").invoke()
    data: ParametrizeEdbExtensionData = extension.data

    assert data.project_name == "custom_project"
    assert data.relative_parametric is False
    assert data.parametrize_layers is False
    assert data.parametrize_materials is False
    assert data.parametrize_padstacks is False
    assert data.parametrize_traces is False
    assert data.expansion_polygon_mm == 1.5
    assert data.expansion_void_mm == 2.0
    assert len(data.nets_filter) == 2


@patch("tkinter.messagebox.showerror")
def test_parametrize_edb_extension_exceptions(mock_showerror, mock_aedt_app):
    """Test exceptions in the Parametrize EDB extension."""
    # Test empty project name
    extension = ParametrizeEdbExtension(withdraw=True)
    extension.project_name_entry.delete(0, tkinter.END)
    extension.project_name_entry.insert(0, "")

    extension.root.nametowidget("generate").invoke()
    mock_showerror.assert_called()
    args = mock_showerror.call_args[0]
    assert "Error" in args[0]
    assert "Project name cannot be empty" in args[1]

    # Test negative polygon expansion
    mock_showerror.reset_mock()
    extension = ParametrizeEdbExtension(withdraw=True)
    extension.polygons_entry.delete("1.0", tkinter.END)
    extension.polygons_entry.insert(tkinter.END, "-1.0")

    extension.root.nametowidget("generate").invoke()
    mock_showerror.assert_called()
    args = mock_showerror.call_args[0]
    assert "Error" in args[0]
    assert "Polygon expansion cannot be negative" in args[1]

    # Test negative void expansion
    mock_showerror.reset_mock()
    extension = ParametrizeEdbExtension(withdraw=True)
    extension.voids_entry.delete("1.0", tkinter.END)
    extension.voids_entry.insert(tkinter.END, "-2.0")

    extension.root.nametowidget("generate").invoke()
    mock_showerror.assert_called()
    args = mock_showerror.call_args[0]
    assert "Error" in args[0]
    assert "Void expansion cannot be negative" in args[1]

    # Test invalid expansion value
    mock_showerror.reset_mock()
    extension = ParametrizeEdbExtension(withdraw=True)
    extension.polygons_entry.delete("1.0", tkinter.END)
    extension.polygons_entry.insert(tkinter.END, "invalid")

    extension.root.nametowidget("generate").invoke()
    mock_showerror.assert_called()
    args = mock_showerror.call_args[0]
    assert "Error" in args[0]
    assert "could not convert string to float" in args[1]


@patch("ansys.aedt.core.Desktop")
def test_parametrize_edb_extension_no_active_project(mock_desktop_class, mock_aedt_app):
    """Test exception when no active project is found."""
    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = None
    mock_desktop_class.return_value = mock_desktop

    with pytest.raises(AEDTRuntimeError):
        ParametrizeEdbExtension(withdraw=True)


@patch("ansys.aedt.core.Desktop")
def test_parametrize_edb_extension_no_active_design(mock_desktop_class, mock_aedt_app):
    """Test exception when no active design is found."""
    mock_active_project = MagicMock()
    mock_active_project.GetPath.return_value = "/path/to/project"
    mock_active_project.GetName.return_value = "test_project"

    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_active_project
    mock_desktop.active_design.return_value = None
    mock_desktop_class.return_value = mock_desktop

    with pytest.raises(AEDTRuntimeError):
        ParametrizeEdbExtension(withdraw=True)


@patch("ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb.Edb")
@patch("ansys.aedt.core.Desktop")
def test_parametrize_edb_extension_edb_failure(mock_desktop_class, mock_edb_class, mock_aedt_app):
    """Test exception when EDB fails to load."""
    mock_active_project = MagicMock()
    mock_active_project.GetPath.return_value = "/path/to/project"
    mock_active_project.GetName.return_value = "test_project"

    mock_active_design = MagicMock()
    mock_active_design.GetName.return_value = "cell;test_design"

    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_active_project
    mock_desktop.active_design.return_value = mock_active_design
    mock_desktop_class.return_value = mock_desktop

    mock_edb_class.side_effect = Exception("EDB load failed")

    with pytest.raises(AEDTRuntimeError):
        ParametrizeEdbExtension(withdraw=True)


@patch("tkinter.messagebox.showerror")
def test_parametrize_edb_extension_show_error_message(mock_showerror, mock_aedt_app):
    """Test show_error_message method."""
    extension = ParametrizeEdbExtension(withdraw=True)

    extension.show_error_message("Test error message")
    mock_showerror.assert_called_once_with("Error", "Test error message")

    extension.root.destroy()


# Test main function
@patch("ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb.Hfss3dLayout")
@patch("ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb.Edb")
@patch("ansys.aedt.core.Desktop")
def test_main_function_with_valid_data(mock_desktop_class, mock_edb_class, mock_hfss3dlayout):
    """Test main function with valid data."""
    data = ParametrizeEdbExtensionData(
        aedb_path="/path/to/test.aedb",
        design_name="test_design",
        project_name="test_parametric",
        expansion_polygon_mm=1.0,
        expansion_void_mm=0.5,
    )

    # Mock all external dependencies
    mock_desktop = MagicMock()
    mock_edb = MagicMock()
    mock_desktop_class.return_value = mock_desktop
    mock_edb_class.return_value = mock_edb

    result = main(data)

    assert result is True
    mock_edb.auto_parametrize_design.assert_called_once()
    mock_edb.close.assert_called_once()
    mock_edb.close.assert_called_once()


def test_main_function_negative_polygon_expansion():
    """Test main function with negative polygon expansion."""
    data = ParametrizeEdbExtensionData(
        expansion_polygon_mm=-1.0,
    )

    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)

    assert "Polygon expansion cannot be negative" in str(exc_info.value)


def test_main_function_negative_void_expansion():
    """Test main function with negative void expansion."""
    data = ParametrizeEdbExtensionData(
        expansion_void_mm=-1.0,
    )

    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)

    assert "Void expansion cannot be negative" in str(exc_info.value)


def test_main_function_empty_project_name():
    """Test main function with empty project name."""
    data = ParametrizeEdbExtensionData(
        project_name="",
    )

    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)

    assert "Project name cannot be empty" in str(exc_info.value)


@patch("ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb.Hfss3dLayout")
@patch("ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb.Edb")
@patch("ansys.aedt.core.Desktop")
def test_main_function_no_aedb_path(mock_desktop_class, mock_edb_class, mock_hfss3dlayout):
    """Test main function without aedb path."""
    data = ParametrizeEdbExtensionData(
        aedb_path="",
        project_name="test_project",
    )

    # Mock AEDT
    mock_active_project = MagicMock()
    mock_active_project.GetPath.return_value = "/path/to/project"
    mock_active_project.GetName.return_value = "test_project"

    mock_active_design = MagicMock()
    mock_active_design.GetName.return_value = "cell;test_design"

    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_active_project
    mock_desktop.active_design.return_value = mock_active_design

    mock_edb = MagicMock()
    mock_desktop_class.return_value = mock_desktop
    mock_edb_class.return_value = mock_edb

    result = main(data)

    assert result is True
    mock_edb.auto_parametrize_design.assert_called_once()
    mock_edb.close.assert_called_once()


@patch("ansys.aedt.core.Desktop")
def test_main_function_no_active_project(mock_desktop_class):
    """Test main function when no active project is found."""
    data = ParametrizeEdbExtensionData(
        aedb_path="",
        project_name="test_project",
    )

    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = None
    mock_desktop_class.return_value = mock_desktop

    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)

    assert "No active project found in AEDT" in str(exc_info.value)


@patch("ansys.aedt.core.Desktop")
def test_main_function_no_active_design(mock_desktop_class):
    """Test main function when no active design is found."""
    data = ParametrizeEdbExtensionData(
        aedb_path="",
        project_name="test_project",
    )

    mock_active_project = MagicMock()
    mock_active_project.GetPath.return_value = "/path/to/project"
    mock_active_project.GetName.return_value = "test_project"

    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_active_project
    mock_desktop.active_design.return_value = None
    mock_desktop_class.return_value = mock_desktop

    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)

    assert "No active design found in AEDT" in str(exc_info.value)
