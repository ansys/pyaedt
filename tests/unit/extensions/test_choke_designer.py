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

import tempfile
import tkinter
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtension
from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtensionData
from ansys.aedt.core.modeler.advanced_cad.choke import Choke


@pytest.fixture
def sample_choke_config():
    """Fixture to provide a sample choke configuration."""
    return {
        "Number of Windings": {
            "1": True,
            "2": False,
            "3": False,
            "4": False,
        },
        "Layer": {"Simple": True, "Double": False, "Triple": False},
        "Layer Type": {"Separate": True, "Linked": False},
        "Similar Layer": {"Similar": True, "Different": False},
        "Mode": {"Differential": True, "Common": False},
        "Wire Section": {
            "None": False,
            "Hexagon": False,
            "Octagon": False,
            "Circle": True,
        },
        "Core": {
            "Name": "Core",
            "Material": "ferrite",
            "Inner Radius": 15,
            "Outer Radius": 25,
            "Height": 12,
            "Chamfer": 0.8,
        },
        "Outer Winding": {
            "Name": "Winding",
            "Material": "copper",
            "Inner Radius": 16,
            "Outer Radius": 24,
            "Height": 10,
            "Wire Diameter": 1.5,
            "Turns": 20,
            "Coil Pit(deg)": 0.1,
            "Occupation(%)": 0,
        },
        "Mid Winding": {
            "Turns": 25,
            "Coil Pit(deg)": 0.1,
            "Occupation(%)": 0,
        },
        "Inner Winding": {
            "Turns": 4,
            "Coil Pit(deg)": 0.1,
            "Occupation(%)": 0,
        },
        "Settings": {"Units": "mm"},
        "Create Component": {"True": True, "False": False},
    }


@pytest.fixture
def invalid_choke_config():
    """Fixture to provide an invalid choke configuration."""
    return {
        "Core": {
            "Name": "Core",
            "Material": "ferrite",
            "Inner Radius": 30,  # Invalid: larger than outer radius
            "Outer Radius": 20,
            "Height": -5,  # Invalid: negative height
            "Chamfer": 0.8,
        },
        "Outer Winding": {
            "Name": "Winding",
            "Material": "copper",
            "Inner Radius": 25,  # Invalid: larger than outer radius
            "Outer Radius": 20,
            "Height": 10,
            "Wire Diameter": -1.5,  # Invalid: negative diameter
            "Turns": 20,
            "Coil Pit(deg)": 0.1,
            "Occupation(%)": 0,
        },
    }


def test_choke_designer_extension_data_class() -> None:
    """Test ChokeDesignerExtensionData class."""
    choke = Choke()
    data = ChokeDesignerExtensionData(choke=choke)

    assert data.choke is choke
    assert isinstance(data.choke, Choke)


def test_choke_designer_extension_with_custom_choke(mock_hfss_app) -> None:
    """Test instantiation with a custom choke configuration."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Modify choke configuration
    extension.choke.core["Inner Radius"] = 15
    extension.choke.core["Outer Radius"] = 25
    extension.choke.number_of_windings = {
        "1": False,
        "2": True,
        "3": False,
        "4": False,
    }

    assert extension.choke.core["Inner Radius"] == 15
    assert extension.choke.core["Outer Radius"] == 25
    assert extension.choke.number_of_windings["2"] is True
    assert extension.choke.number_of_windings["1"] is False

    extension.root.destroy()


def test_validate_configuration_valid(mock_hfss_app, sample_choke_config) -> None:
    extension = ChokeDesignerExtension(withdraw=True)
    extension.choke = Choke.from_dict(sample_choke_config)
    with patch("tkinter.messagebox.showerror") as mock_error:
        # Should not raise an error
        assert extension.validate_configuration(extension.choke) is True
        mock_error.assert_not_called()

    extension.root.destroy()


def test_validate_configuration_missing_attributes(mock_hfss_app) -> None:
    """Test validation with missing attributes."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Create an incomplete choke object
    incomplete_choke = MagicMock()
    del incomplete_choke.core  # Remove core attribute

    with patch("tkinter.messagebox.showerror") as mock_error:
        result = extension.validate_configuration(incomplete_choke)
        assert result is False
        mock_error.assert_called_once()
        args, kwargs = mock_error.call_args
        assert "Validation error:" in args[1]

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
def test_save_configuration_success(mock_filedialog, sample_choke_config, mock_hfss_app) -> None:
    """Test successful configuration save."""
    with tempfile.NamedTemporaryFile(suffix=".json", prefix="test_config_", delete=False) as temp_file:
        temp_file_path = temp_file.name
    mock_filedialog.return_value = temp_file_path

    extension = ChokeDesignerExtension(withdraw=True)
    extension.choke = Choke.from_dict(sample_choke_config)

    with patch.object(extension.choke, "export_to_json") as mock_export:
        with patch("tkinter.messagebox.showinfo") as mock_info:
            extension.save_configuration()

            mock_export.assert_called_once_with(temp_file_path)
            mock_info.assert_called_once_with("Success", "Configuration saved successfully.")

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
def test_save_configuration_validation_failure(mock_filedialog, mock_hfss_app) -> None:
    """Test save configuration with validation failure."""
    with tempfile.NamedTemporaryFile(suffix=".json", prefix="test_config_", delete=False) as temp_file:
        temp_file_path = temp_file.name
    mock_filedialog.return_value = temp_file_path

    extension = ChokeDesignerExtension(withdraw=True)
    extension.choke.core["Inner Radius"] = 30
    extension.choke.core["Outer Radius"] = 20  # Invalid configuration

    with patch("tkinter.messagebox.showerror") as mock_error:
        extension.save_configuration()

        # Should be called twice: once from validate_configuration, once from save_configuration
        assert mock_error.call_count == 2

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
def test_save_configuration_export_failure(mock_filedialog, sample_choke_config, mock_hfss_app) -> None:
    """Test save configuration with export failure."""
    with tempfile.NamedTemporaryFile(suffix=".json", prefix="test_config_", delete=False) as temp_file:
        temp_file_path = temp_file.name
    mock_filedialog.return_value = temp_file_path

    extension = ChokeDesignerExtension(withdraw=True)
    extension.choke = Choke.from_dict(sample_choke_config)

    with patch.object(
        extension.choke,
        "export_to_json",
        side_effect=Exception("Export failed"),
    ):
        with patch("tkinter.messagebox.showerror") as mock_error:
            extension.save_configuration()

            mock_error.assert_called_once()
            args, kwargs = mock_error.call_args
            assert "Failed to save configuration" in args[1]
            assert "Export failed" in args[1]

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename")
def test_load_configuration_no_file_selected(mock_filedialog, mock_hfss_app) -> None:
    """Test load configuration when no file is selected."""
    mock_filedialog.return_value = ""  # User cancels file dialog

    extension = ChokeDesignerExtension(withdraw=True)

    with patch("ansys.aedt.core.generic.file_utils.read_json") as mock_read_json:
        extension.load_configuration()
        mock_read_json.assert_not_called()

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename")
@patch("ansys.aedt.core.generic.file_utils.read_json")
def test_load_configuration_validation_failure(
    mock_read_json,
    mock_filedialog,
    invalid_choke_config,
    mock_hfss_app,
) -> None:
    """Test load configuration with validation failure."""
    with tempfile.NamedTemporaryFile(suffix=".json", prefix="test_config_", delete=False) as temp_file:
        temp_file_path = temp_file.name
    mock_filedialog.return_value = temp_file_path
    mock_read_json.return_value = invalid_choke_config

    extension = ChokeDesignerExtension(withdraw=True)

    with patch("tkinter.messagebox.showerror") as mock_error:
        extension.load_configuration()

        # Should be called twice: once from validate_configuration, once from load_configuration
        assert mock_error.call_count >= 1

    extension.root.destroy()


def test_update_config(mock_hfss_app) -> None:
    """Test updating boolean configuration options."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Create a StringVar to simulate radio button selection
    selected_option = tkinter.StringVar(value="2")

    # Test updating number_of_windings
    extension.update_config("number_of_windings", selected_option)

    assert extension.choke.number_of_windings["1"] is False
    assert extension.choke.number_of_windings["2"] is True
    assert extension.choke.number_of_windings["3"] is False
    assert extension.choke.number_of_windings["4"] is False

    extension.root.destroy()


def test_update_parameter_config(mock_hfss_app) -> None:
    """Test updating parameter configuration from entry widget."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Create a mock entry widget
    mock_entry = MagicMock()
    mock_entry.get.return_value = "25.5"

    extension.update_parameter_config("core", "Inner Radius", mock_entry)

    assert extension.choke.core["Inner Radius"] == 25.5

    # Test with string value
    mock_entry.get.return_value = "ferrite_new"
    extension.update_parameter_config("core", "Material", mock_entry)

    assert extension.choke.core["Material"] == "ferrite_new"

    # Test with invalid value
    mock_entry.get.return_value = "invalid_float"
    extension.update_parameter_config("core", "Inner Radius", mock_entry)

    # Should not crash and value should be assigned as string since
    # it's not a valid float
    assert extension.choke.core["Inner Radius"] == "invalid_float"

    extension.root.destroy()


def test_update_radio_buttons(mock_hfss_app) -> None:
    """Test updating radio button selections."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Setup mock selected_options
    extension.selected_options = {}
    for category in extension.boolean_categories:
        extension.selected_options[category] = tkinter.StringVar()

    # Modify choke configuration
    extension.choke.number_of_windings = {
        "1": False,
        "2": True,
        "3": False,
        "4": False,
    }
    extension.choke.layer = {
        "Simple": False,
        "Double": True,
        "Triple": False,
    }

    extension.update_radio_buttons()

    assert extension.selected_options["number_of_windings"].get() == "2"
    assert extension.selected_options["layer"].get() == "Double"

    extension.root.destroy()


def test_update_entries(mock_hfss_app) -> None:
    """Test updating entry widgets."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Setup mock entries
    mock_entry1 = MagicMock()
    mock_entry2 = MagicMock()
    extension.entries_dict = {
        ("Core", "Inner Radius"): mock_entry1,
        ("Core", "Material"): mock_entry2,
    }

    # Modify choke configuration
    extension.choke.core["Inner Radius"] = 15.5
    extension.choke.core["Material"] = "new_material"

    extension.update_entries()

    mock_entry1.delete.assert_called_with(0, tkinter.END)
    mock_entry1.insert.assert_called_with(0, "15.5")
    mock_entry2.delete.assert_called_with(0, tkinter.END)
    mock_entry2.insert.assert_called_with(0, "new_material")

    extension.root.destroy()


def test_callback_success(mock_hfss_app) -> None:
    """Test successful callback execution."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Mock validation to return True
    with patch.object(extension, "validate_configuration", return_value=True):
        with patch.object(extension.root, "destroy") as mock_destroy:
            extension.callback()

            assert extension.flag is True
            assert isinstance(extension.data, ChokeDesignerExtensionData)
            assert extension.data.choke is extension.choke
            mock_destroy.assert_called_once()


def test_callback_validation_failure(mock_hfss_app) -> None:
    """Test callback with validation failure."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Mock validation to return False
    with patch.object(extension, "validate_configuration", return_value=False):
        with patch.object(extension.root, "destroy") as mock_destroy:
            extension.callback()

            assert extension.flag is True  # Flag is set regardless
            mock_destroy.assert_not_called()  # Root should not be destroyed


def test_create_boolean_options(mock_hfss_app) -> None:
    """Test creation of boolean option radio buttons."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Create a parent frame
    parent = tkinter.Frame(extension.root)

    extension.create_boolean_options(parent)

    # Check that selected_options are created for boolean categories
    assert len(extension.selected_options) == len(extension.boolean_categories)

    # Check that all categories have StringVar objects
    for category in extension.boolean_categories:
        if hasattr(extension.choke, category):
            assert category in extension.selected_options
            assert isinstance(
                extension.selected_options[category],
                tkinter.StringVar,
            )

    extension.root.destroy()


def test_create_parameter_inputs(mock_hfss_app) -> None:
    """Test creation of parameter input widgets."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Create a parent frame
    parent = tkinter.Frame(extension.root)

    extension.create_parameter_inputs(parent, "Core")

    # Check that entries are created for core parameters
    core_fields = extension.choke.core.keys()
    for field in core_fields:
        assert ("Core", field) in extension.entries_dict
        assert hasattr(extension.entries_dict[("Core", field)], "get")  # Should be Entry widget

    extension.root.destroy()


def test_create_parameter_inputs_invalid_category(mock_hfss_app) -> None:
    """Test creation of parameter inputs with invalid category."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Create a parent frame
    parent = tkinter.Frame(extension.root)

    # Test with invalid category
    initial_entries_count = len(extension.entries_dict)
    extension.create_parameter_inputs(parent, "InvalidCategory")

    # Should not create any new entries
    assert len(extension.entries_dict) == initial_entries_count

    extension.root.destroy()


def test_extension_ui_components(mock_hfss_app) -> None:
    """Test that the extension UI components are properly created."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Check that the main UI components exist
    assert extension.root.winfo_exists()

    # The extension should have its main content added
    children = extension.root.winfo_children()
    assert len(children) > 0

    extension.root.destroy()


def test_choke_designer_extension_data_defaults(mock_hfss_app) -> None:
    """Test ChokeDesignerExtensionData with default values."""
    data = ChokeDesignerExtensionData()

    assert data.choke is None


def test_choke_configuration_persistence(mock_hfss_app) -> None:
    """Test that choke configuration changes persist."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Modify configuration
    original_radius = extension.choke.core["Inner Radius"]
    extension.choke.core["Inner Radius"] = 99.9

    assert extension.choke.core["Inner Radius"] == 99.9
    assert extension.choke.core["Inner Radius"] != original_radius

    extension.root.destroy()


def test_category_map_completeness(mock_hfss_app) -> None:
    """Test that category map covers all expected categories."""
    extension = ChokeDesignerExtension(withdraw=True)

    expected_categories = [
        "core",
        "outer_winding",
        "mid_winding",
        "inner_winding",
        "settings",
    ]
    actual_categories = list(extension.category_map.values())

    for category in expected_categories:
        assert category in actual_categories

    extension.root.destroy()


def test_boolean_categories_completeness(mock_hfss_app) -> None:
    """Test that boolean categories list is complete."""
    extension = ChokeDesignerExtension(withdraw=True)

    expected_boolean_categories = [
        "number_of_windings",
        "layer",
        "layer_type",
        "similar_layer",
        "mode",
        "create_component",
        "wire_section",
    ]

    for category in expected_boolean_categories:
        assert category in extension.boolean_categories

    extension.root.destroy()
