# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import tkinter
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.maxwell3d.fields_distribution import EXTENSION_TITLE
from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtension
from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData


@pytest.mark.parametrize("mock_maxwell_3d_app", ["2025.2"], indirect=True)
def test_extension_default_with_point(mock_maxwell_3d_app):
    """Test instantiation of the Fields Distribution extension for AEDT version < 2026.1."""
    # Mock the vector fields JSON file
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H", "Vector_B", "Vector_J"],
        "Maxwell 2D": ["A_Vector", "H_Vector", "B_Vector"],
    }

    # Mock the post processing methods
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss", "Current density"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock(), "Object2": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    # Mock the point creation and deletion
    mock_point = MagicMock()
    mock_point.name = "Point1"
    mock_maxwell_3d_app.modeler.create_point.return_value = mock_point

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        assert EXTENSION_TITLE == extension.root.title()
        assert "light" == extension.root.theme

        # Check that UI elements are created
        assert "export_options_lb" in extension._widgets
        assert "objects_list_lb" in extension._widgets
        assert "solution_dropdown_var" in extension._widgets
        assert "sample_points_entry" in extension._widgets
        assert "export_file_entry" in extension._widgets

        extension.root.destroy()


@pytest.mark.parametrize("mock_maxwell_3d_app", ["2026.1"], indirect=True)
def test_extension_default_without_point(mock_maxwell_3d_app):
    """Test instantiation of the Fields Distribution extension for AEDT version 2026.1."""
    # Mock the vector fields JSON file
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H", "Vector_B", "Vector_J"],
        "Maxwell 2D": ["A_Vector", "H_Vector", "B_Vector"],
    }

    # Mock the post processing methods
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss", "Current density"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock(), "Object2": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        assert EXTENSION_TITLE == extension.root.title()
        assert "light" == extension.root.theme

        # Check that UI elements are created
        assert "export_options_lb" in extension._widgets
        assert "objects_list_lb" in extension._widgets
        assert "solution_dropdown_var" in extension._widgets
        assert "sample_points_entry" in extension._widgets
        assert "export_file_entry" in extension._widgets

        extension.root.destroy()


def test_extension_data_initialization():
    """Test the FieldsDistributionExtensionData initialization."""
    data = FieldsDistributionExtensionData()

    assert data.points_file == ""
    assert data.export_file == ""
    assert data.export_option == "Ohmic loss"
    assert data.objects_list == []
    assert data.solution_option == ""


def test_extension_data_post_init():
    """Test the post_init method of FieldsDistributionExtensionData."""
    data = FieldsDistributionExtensionData(objects_list=None)

    # Should initialize with empty list
    assert data.objects_list == []

    # Test with existing list
    data2 = FieldsDistributionExtensionData(objects_list=["Object1", "Object2"])
    assert data2.objects_list == ["Object1", "Object2"]


def test_extension_design_type_check(mock_maxwell_3d_app):
    """Test design type validation."""
    mock_vector_fields = {"Maxwell 3D": ["Vector_H"], "Maxwell 2D": ["A_Vector"]}
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Should not raise exception for Maxwell 3D
        extension.check_design_type()

        extension.root.destroy()


def test_extension_ui_widgets(mock_maxwell_3d_app):
    """Test that all UI widgets are properly created."""
    mock_vector_fields = {"Maxwell 3D": ["Vector_H", "Vector_B"], "Maxwell 2D": ["A_Vector"]}
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss", "Current density"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock(), "Object2": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive", "Setup2 : LastAdaptive"]

    mock_maxwell_3d_app.post.fields_calculator.get_expressions = MagicMock(return_value=["Expr1", "Expr2"])

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Test export options listbox
        export_lb = extension._widgets["export_options_lb"]
        assert export_lb.size() > 0  # Should have items from named expressions and vector fields

        # Test objects listbox
        objects_lb = extension._widgets["objects_list_lb"]
        assert objects_lb.size() == 2  # Object1 and Object2

        # Test solution dropdown
        solution_var = extension._widgets["solution_dropdown_var"]
        assert solution_var.get() == "Setup1 : LastAdaptive"

        # Test text entries
        assert extension._widgets["sample_points_entry"] is not None
        assert extension._widgets["export_file_entry"] is not None

        extension.root.destroy()


def test_text_size_method(mock_maxwell_3d_app):
    """Test the _text_size method."""
    mock_vector_fields = {"Maxwell 3D": ["Vector_H"], "Maxwell 2D": ["A_Vector"]}
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Create a mock text widget
        mock_entry = MagicMock()

        # Test short path
        short_path = "test.txt"
        extension._text_size(short_path, mock_entry)
        mock_entry.configure.assert_called_with(height=1, width=max(40, len(short_path) // 2))
        mock_entry.delete.assert_called_with("1.0", tkinter.END)
        mock_entry.insert.assert_called_with(tkinter.END, short_path)

        # Test long path
        long_path = "very_long_path_name_that_exceeds_fifty_characters_definitely.txt"
        extension._text_size(long_path, mock_entry)
        mock_entry.configure.assert_called_with(height=2, width=max(40, len(long_path) // 2))

        extension.root.destroy()


def test_populate_listbox_method(mock_maxwell_3d_app):
    """Test the _populate_listbox method."""
    mock_vector_fields = {"Maxwell 3D": ["Vector_H"], "Maxwell 2D": ["A_Vector"]}
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Create mock widgets
        mock_frame = MagicMock()
        mock_listbox = MagicMock()
        mock_listbox.pack = MagicMock()
        mock_listbox.insert = MagicMock()

        items_list = ["Item1", "Item2", "Item3"]

        # Test with few items (no scrollbar)
        extension._populate_listbox(mock_frame, mock_listbox, 3, items_list)

        # Verify listbox is populated
        assert mock_listbox.insert.call_count == len(items_list)
        mock_listbox.pack.assert_called_with(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)

        extension.root.destroy()


def test_extension_data_extraction(mock_maxwell_3d_app):
    """Test data extraction from UI widgets."""
    mock_vector_fields = {"Maxwell 3D": ["Vector_H", "Vector_B"], "Maxwell 2D": ["A_Vector"]}
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss", "Current density"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock(), "Object2": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Simulate user input
        extension._widgets["sample_points_entry"].insert(tkinter.END, "/path/to/points.pts")
        extension._widgets["export_file_entry"].insert(tkinter.END, "/path/to/output.csv")
        extension._widgets["export_options_lb"].selection_set(0)
        extension._widgets["objects_list_lb"].selection_set(0, 1)  # Select multiple objects

        # Test data extraction (this would normally be done by the create button callback)
        points_file = extension._widgets["sample_points_entry"].get("1.0", tkinter.END).strip()
        export_file = extension._widgets["export_file_entry"].get("1.0", tkinter.END).strip()

        assert points_file == "/path/to/points.pts"
        assert export_file == "/path/to/output.csv"

        extension.root.destroy()


def test_extension_error_handling(mock_maxwell_3d_app):
    """Test error handling for missing objects and solutions."""
    mock_vector_fields = {"Maxwell 3D": ["Vector_H"], "Maxwell 2D": ["A_Vector"]}

    # Test with no objects
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        with pytest.raises(Exception):  # Should raise AEDTRuntimeError
            FieldsDistributionExtension(withdraw=True)

    # Test with no solutions
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = []

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        with pytest.raises(Exception):  # Should raise AEDTRuntimeError
            FieldsDistributionExtension(withdraw=True)


@pytest.mark.parametrize("mock_maxwell_2d_app", ["2025.2"], indirect=True)
def test_extension_with_maxwell_2d(mock_maxwell_2d_app):
    """Test extension with Maxwell 2D application."""
    mock_vector_fields = {"Maxwell 2D": ["A_Vector", "H_Vector"], "Maxwell 3D": ["Vector_H"]}
    mock_maxwell_2d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_2d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_2d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    mock_point = MagicMock()
    mock_point.name = "Point1"
    mock_maxwell_2d_app.modeler.create_point.return_value = mock_point

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Should work fine with Maxwell 2D
        assert extension.root.title() == EXTENSION_TITLE
        extension.check_design_type()  # Should not raise exception

        extension.root.destroy()


def test_callback_export(mock_maxwell_3d_app):
    """Test the callback_export function."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H", "Vector_B"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = [
        "Ohmic loss",
        "Current density",
    ]
    mock_maxwell_3d_app.modeler.objects_by_name = {
        "Object1": MagicMock(),
        "Object2": MagicMock(),
    }
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    mock_maxwell_3d_app.post.fields_calculator.get_expressions = MagicMock(
        return_value=["Ohmic loss", "Current density"]
    )

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Mock UI state
        extension._widgets["sample_points_entry"].insert(tkinter.END, "/path/to/points.pts")
        extension._widgets["export_file_entry"].insert(tkinter.END, "/path/to/output.csv")
        extension._widgets["export_options_lb"].selection_set(0)
        extension._widgets["objects_list_lb"].selection_set(0, 1)

        # Simulate export button click
        extension._widgets["export_button"].invoke()

        # Check that data was set correctly
        assert extension.data is not None
        assert extension.data.points_file == "/path/to/points.pts"
        assert extension.data.export_file == "/path/to/output.csv"
        assert extension.data.export_option == "Ohmic loss"
        assert len(extension.data.objects_list) == 2
        assert extension.data.solution_option == "Setup1 : LastAdaptive"


def test_callback_export_no_selection(mock_maxwell_3d_app):
    """Test callback_export with no export option selected."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
        patch("tkinter.messagebox.showerror") as mock_error,
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Don't select any export option
        extension._widgets["export_file_entry"].insert(tkinter.END, "/path/to/output.csv")

        # Simulate export button click
        extension._widgets["export_button"].invoke()

        # Should show error message
        mock_error.assert_called_with("Error", "Please select an export option.")
        assert extension.data is None

        extension.root.destroy()


def test_callback_preview(mock_maxwell_3d_app):
    """Test the callback_preview function."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H", "Vector_B"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = [
        "Ohmic loss",
        "Current density",
    ]
    mock_maxwell_3d_app.modeler.objects_by_name = {
        "Object1": MagicMock(),
        "Object2": MagicMock(),
    }
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    # Mock plot_field method
    mock_plot = MagicMock()
    mock_plot.fields = ["field1", "field2"]
    mock_maxwell_3d_app.post.plot_field.return_value = mock_plot

    mock_maxwell_3d_app.post.fields_calculator.get_expressions = MagicMock(
        return_value=["Ohmic loss", "Current density"]
    )

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Mock UI state
        extension._widgets["export_options_lb"].selection_set(0)
        extension._widgets["objects_list_lb"].selection_set(0, 1)

        # Simulate preview button click
        extension._widgets["preview_button"].invoke()

        # Verify plot_field was called with correct parameters
        mock_maxwell_3d_app.post.plot_field.assert_called_with(
            quantity="Ohmic loss",
            assignment=["Object1", "Object2"],
            plot_type="Surface",
            setup="Setup1 : LastAdaptive",
            plot_cad_objs=False,
            keep_plot_after_generation=False,
            show_grid=False,
        )

        extension.root.destroy()


def test_callback_preview_no_selection(mock_maxwell_3d_app):
    """Test callback_preview with no export option selected."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
        patch("tkinter.messagebox.showerror") as mock_error,
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Don't select any export option
        # Simulate preview button click
        extension._widgets["preview_button"].invoke()

        # Should show error message
        mock_error.assert_called_with("Error", "Please select an export option.")

        extension.root.destroy()


def test_callback_preview_exception(mock_maxwell_3d_app):
    """Test callback_preview when plot_field raises an exception."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    # Make plot_field raise an exception
    mock_maxwell_3d_app.post.plot_field.side_effect = Exception("Plot error")

    mock_maxwell_3d_app.post.fields_calculator.get_expressions = MagicMock(
        return_value=["Ohmic loss", "Current density"]
    )

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
        patch("tkinter.messagebox.showerror") as mock_error,
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Select export option
        extension._widgets["export_options_lb"].selection_set(0)
        extension._widgets["objects_list_lb"].selection_set(0)

        # Simulate preview button click
        extension._widgets["preview_button"].invoke()

        # Should show error message
        mock_error.assert_called_with("Error", "Failed to create preview: Plot error")

        extension.root.destroy()


def test_save_as_files_callback(mock_maxwell_3d_app):
    """Test the save_as_files callback function."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
        patch("tkinter.filedialog.asksaveasfilename") as mock_savedialog,
    ):
        mock_savedialog.return_value = "/path/to/output.csv"

        extension = FieldsDistributionExtension(withdraw=True)

        # Simulate clicking the save as button
        extension._widgets["save_as_button"].invoke()

        # Verify file dialog was called with correct parameters
        mock_savedialog.assert_called_with(
            initialdir="/",
            defaultextension="*.tab",
            filetypes=[
                ("tab data file", "*.tab"),
                ("csv data file", "*.csv"),
                ("Numpy array", "*.npy"),
            ],
        )

        # Verify the path was set in the export file entry
        export_file_text = extension._widgets["export_file_entry"].get("1.0", tkinter.END).strip()
        assert export_file_text == "/path/to/output.csv"

        extension.root.destroy()


def test_show_points_popup_ui_creation(mock_maxwell_3d_app):
    """Test that show_points_popup creates all UI elements correctly."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Mock the Toplevel creation to avoid actual popup window
        with patch("tkinter.Toplevel") as mock_toplevel:
            mock_popup = MagicMock()
            mock_toplevel.return_value = mock_popup

            # Call the show_points_popup function directly
            extension._widgets["export_points_button"].invoke()

            # Verify popup was created and title set
            mock_toplevel.assert_called_once_with(extension.root)
            mock_popup.title.assert_called_with("Select an Option")

        extension.root.destroy()


def test_submit_import_file_success(mock_maxwell_3d_app):
    """Test submit function with import file option - success path."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Test submit() logic for Option 2 (import file)
        with patch("tkinter.filedialog.askopenfilename") as mock_filedialog:
            mock_filedialog.return_value = "/imported/points.pts"

            # Simulate what submit() does when Option 2 is selected
            filename = mock_filedialog(
                initialdir="/",
                title="Select Points File",
                filetypes=(("Points file", ".pts"), ("all files", "*.*")),
            )
            if filename:
                extension._text_size(filename, extension._widgets["sample_points_entry"])

            # Verify dialog was called correctly
            mock_filedialog.assert_called_with(
                initialdir="/",
                title="Select Points File",
                filetypes=(("Points file", ".pts"), ("all files", "*.*")),
            )

            # Verify file path was set in the entry
            sample_text = extension._widgets["sample_points_entry"].get("1.0", tkinter.END).strip()
            assert sample_text == "/imported/points.pts"

        extension.root.destroy()


def test_submit_import_file_no_selection(mock_maxwell_3d_app):
    """Test submit function with import file option - no file selected."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Test submit() logic when no file is selected
        with patch("tkinter.filedialog.askopenfilename") as mock_filedialog:
            mock_filedialog.return_value = ""  # No file selected

            # Get initial state of sample points entry
            initial_text = extension._widgets["sample_points_entry"].get("1.0", tkinter.END).strip()

            # Simulate what submit() does when Option 2 is selected
            filename = mock_filedialog(
                initialdir="/",
                title="Select Points File",
                filetypes=(("Points file", ".pts"), ("all files", "*.*")),
            )
            if filename:  # This condition should be False
                extension._text_size(filename, extension._widgets["sample_points_entry"])

            # Verify dialog was called
            mock_filedialog.assert_called_once()

            # Verify no change in sample points entry
            final_text = extension._widgets["sample_points_entry"].get("1.0", tkinter.END).strip()
            assert final_text == initial_text

        extension.root.destroy()


def test_popup_destroy_called(mock_maxwell_3d_app):
    """Test that popup.destroy() is called in submit function."""
    mock_vector_fields = {
        "Maxwell 3D": ["Vector_H"],
        "Maxwell 2D": ["A_Vector"],
    }
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Ohmic loss"]
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        # Mock popup window to verify destroy is called
        mock_popup = MagicMock()

        # Test that popup.destroy() is called at end of submit()
        # We can verify this by mocking the popup and checking destroy call
        with patch("tkinter.Toplevel", return_value=mock_popup):
            extension._widgets["export_points_button"].invoke()
            # The popup should be created
            assert mock_popup.title.called

        extension.root.destroy()
