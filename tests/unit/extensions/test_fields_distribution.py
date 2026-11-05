# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
import tkinter
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import numpy as np
import pytest

from ansys.aedt.core.extensions.maxwell3d.fields_distribution import EXTENSION_TITLE
from ansys.aedt.core.extensions.maxwell3d.fields_distribution import TEXT_MAX_LINES
from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtension
from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main


@pytest.mark.parametrize("mock_maxwell_3d_app", ["2026.1"], indirect=True)
def test_extension_default_with_point(mock_maxwell_3d_app) -> None:
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
def test_extension_default_without_point(mock_maxwell_3d_app) -> None:
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


def test_extension_data_initialization() -> None:
    """Test the FieldsDistributionExtensionData initialization."""
    data = FieldsDistributionExtensionData()

    assert data.points_file == ""
    assert data.export_file == ""
    assert data.export_option == "Ohmic loss"
    assert data.objects_list == []
    assert data.solution_option == ""


def test_extension_data_post_init() -> None:
    """Test the post_init method of FieldsDistributionExtensionData."""
    data = FieldsDistributionExtensionData(objects_list=None)

    # Should initialize with empty list
    assert data.objects_list == []

    # Test with existing list
    data2 = FieldsDistributionExtensionData(objects_list=["Object1", "Object2"])
    assert data2.objects_list == ["Object1", "Object2"]


def test_extension_design_type_check(mock_maxwell_3d_app) -> None:
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


def test_extension_ui_widgets(mock_maxwell_3d_app) -> None:
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

        # The preview plot button has been removed
        assert "preview_button" not in extension._widgets

        extension.root.destroy()


def test_text_size_method(mock_maxwell_3d_app) -> None:
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
        mock_entry.configure.assert_called_with(height=1)
        mock_entry.delete.assert_called_with("1.0", tkinter.END)
        mock_entry.insert.assert_called_with(tkinter.END, short_path)

        # Test long path: height grows to fit the whole path
        long_path = "very_long_path_name_that_exceeds_fifty_characters_definitely.txt"
        extension._text_size(long_path, mock_entry)
        mock_entry.configure.assert_called_with(height=2)

        # Test very long path: height is capped
        extension._text_size("a" * 1000, mock_entry)
        mock_entry.configure.assert_called_with(height=TEXT_MAX_LINES)

        extension.root.destroy()


def test_populate_listbox_method(mock_maxwell_3d_app) -> None:
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


def test_extension_data_extraction(mock_maxwell_3d_app) -> None:
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


def test_extension_error_handling(mock_maxwell_3d_app) -> None:
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


@pytest.mark.parametrize("mock_maxwell_2d_app", ["2026.1"], indirect=True)
def test_extension_with_maxwell_2d(mock_maxwell_2d_app) -> None:
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


def test_callback_export(mock_maxwell_3d_app) -> None:
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


def test_callback_export_no_selection(mock_maxwell_3d_app) -> None:
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


def test_save_as_files_callback(mock_maxwell_3d_app) -> None:
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


def test_browse_points_file(mock_maxwell_3d_app) -> None:
    """Test that the points file button selects an existing PTS file."""
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
        patch("tkinter.filedialog.askopenfilename", return_value="/imported/points.pts") as mock_filedialog,
        patch("tkinter.Toplevel") as mock_toplevel,
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        extension._widgets["export_points_button"].invoke()

        mock_filedialog.assert_called_once_with(
            initialdir="/",
            title="Select Points File",
            filetypes=[("Points file", "*.pts")],
        )
        mock_toplevel.assert_not_called()
        sample_text = extension._widgets["sample_points_entry"].get("1.0", tkinter.END).strip()
        assert sample_text == "/imported/points.pts"

        extension.root.destroy()


def test_browse_points_file_cancelled(mock_maxwell_3d_app) -> None:
    """Test that cancelling the points file dialog keeps the sample points entry unchanged."""
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
        patch("tkinter.filedialog.askopenfilename", return_value="") as mock_filedialog,
    ):
        extension = FieldsDistributionExtension(withdraw=True)

        extension._widgets["export_points_button"].invoke()

        mock_filedialog.assert_called_once()
        assert extension._widgets["sample_points_entry"].get("1.0", tkinter.END).strip() == ""

        extension.root.destroy()


def test_main_export_tab_file(tmp_path):
    """Test main function exports .tab file using write_csv with tab delimiter."""
    # Create a fake .fld file that main() will read
    fld_content = "Header line 1\nHeader line 2\n1.0 2.0 3.0\n4.0 5.0 6.0\n"
    fld_path = tmp_path / "output.fld"
    fld_path.write_text(fld_content)

    tab_path = tmp_path / "output.tab"

    data = FieldsDistributionExtensionData(
        export_file=str(tab_path),
        export_option="Ohmic loss",
        objects_list=["Object1"],
        solution_option="Setup1 : LastAdaptive",
    )

    # Mock Desktop and get_pyaedt_app
    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "Project1"
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Design1"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    mock_aedtapp = MagicMock()
    mock_aedtapp.design_type = "Maxwell 3D"

    # Mock the setup so it appears solved
    mock_setup = MagicMock()
    mock_setup.name = "Setup1"
    mock_setup.is_solved = True
    mock_aedtapp.setups = [mock_setup]

    with (
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.get_pyaedt_app",
            return_value=mock_aedtapp,
        ),
        patch("ansys.aedt.core.extensions.maxwell3d.fields_distribution.write_csv") as mock_write_csv,
    ):
        result = main(data)

    assert result is True
    mock_write_csv.assert_called_once_with(
        str(tab_path), [["1.0", "2.0", "3.0"], ["4.0", "5.0", "6.0"]], delimiter="\t"
    )


def test_main_export_csv_file(tmp_path):
    """Test main function exports .csv file using write_csv with default comma delimiter."""
    fld_content = "Header line 1\nHeader line 2\n1.0 2.0 3.0\n4.0 5.0 6.0\n"
    fld_path = tmp_path / "output.fld"
    fld_path.write_text(fld_content)

    csv_path = tmp_path / "output.csv"

    data = FieldsDistributionExtensionData(
        export_file=str(csv_path),
        export_option="Ohmic loss",
        objects_list=["Object1"],
        solution_option="Setup1 : LastAdaptive",
    )

    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "Project1"
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Design1"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    mock_aedtapp = MagicMock()
    mock_aedtapp.design_type = "Maxwell 3D"

    mock_setup = MagicMock()
    mock_setup.name = "Setup1"
    mock_setup.is_solved = True
    mock_aedtapp.setups = [mock_setup]

    with (
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.get_pyaedt_app",
            return_value=mock_aedtapp,
        ),
        patch("ansys.aedt.core.extensions.maxwell3d.fields_distribution.write_csv") as mock_write_csv,
    ):
        result = main(data)

    assert result is True
    mock_write_csv.assert_called_once_with(str(csv_path), [["1.0", "2.0", "3.0"], ["4.0", "5.0", "6.0"]])


def test_main_export_npy_file(tmp_path):
    """Test main function exports .npy file using numpy save."""
    fld_content = "Header line 1\nHeader line 2\n1.0 2.0 3.0\n4.0 5.0 6.0\n"
    fld_path = tmp_path / "output.fld"
    fld_path.write_text(fld_content)

    npy_path = tmp_path / "output.npy"

    data = FieldsDistributionExtensionData(
        export_file=str(npy_path),
        export_option="Ohmic loss",
        objects_list=["Object1"],
        solution_option="Setup1 : LastAdaptive",
    )

    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "Project1"
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Design1"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    mock_aedtapp = MagicMock()
    mock_aedtapp.design_type = "Maxwell 3D"

    mock_setup = MagicMock()
    mock_setup.name = "Setup1"
    mock_setup.is_solved = True
    mock_aedtapp.setups = [mock_setup]

    with (
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.get_pyaedt_app",
            return_value=mock_aedtapp,
        ),
        patch("ansys.aedt.core.extensions.maxwell3d.fields_distribution.np.save") as mock_np_save,
    ):
        result = main(data)

    assert result is True
    mock_np_save.assert_called_once()
    saved_path = mock_np_save.call_args[0][0]
    saved_array = mock_np_save.call_args[0][1]
    assert saved_path == Path(str(npy_path))
    expected = np.array([["1.0", "2.0", "3.0"], ["4.0", "5.0", "6.0"]])
    np.testing.assert_array_equal(saved_array, expected)


def test_main_export_unsupported_suffix(tmp_path):
    """Test main function raises error for unsupported file extension."""
    fld_content = "Header line 1\nHeader line 2\n1.0 2.0 3.0\n4.0 5.0 6.0\n"
    fld_path = tmp_path / "output.fld"
    fld_path.write_text(fld_content)

    bad_path = tmp_path / "output.xyz"

    data = FieldsDistributionExtensionData(
        export_file=str(bad_path),
        export_option="Ohmic loss",
        objects_list=["Object1"],
        solution_option="Setup1 : LastAdaptive",
    )

    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "Project1"
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Design1"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    mock_aedtapp = MagicMock()
    mock_aedtapp.design_type = "Maxwell 3D"

    mock_setup = MagicMock()
    mock_setup.name = "Setup1"
    mock_setup.is_solved = True
    mock_aedtapp.setups = [mock_setup]

    with (
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.get_pyaedt_app",
            return_value=mock_aedtapp,
        ),
        pytest.raises(Exception, match=r"\.xyz is not supported"),
    ):
        main(data)


def _transient_extension_mocks(mock_app) -> None:
    """Configure a mocked transient Maxwell design."""
    mock_app.solution_type = "Transient"
    mock_app.modeler.objects_by_name = {"Object1": MagicMock(), "Object2": MagicMock()}
    mock_app.existing_analysis_sweeps = ["Setup1 : Transient"]
    expressions = {
        "Fields": {"Mag_B": "", "Ohmic_Loss": ""},
        "Time Averaged Fields": {"Loss_Density": "", "Core_Loss": "", "Avg_Ohmic_Loss": ""},
    }
    mock_app.post.fields_calculator.get_expressions = MagicMock(
        side_effect=lambda field_type=None: expressions[field_type]
    )


def test_transient_widgets(mock_maxwell_3d_app) -> None:
    """Test transient widgets and time averaged toggle."""
    _transient_extension_mocks(mock_maxwell_3d_app)
    extension = FieldsDistributionExtension(withdraw=True)

    export_lb = extension._widgets["export_options_lb"]
    assert export_lb.get(0, tkinter.END) == ("Mag_B", "Ohmic_Loss")
    assert extension._widgets["time_label"].cget("text") == "Time:"
    assert not extension._widgets["start_time_entry"].winfo_ismapped()
    assert not extension._widgets["start_time_entry"].grid_info()

    extension._widgets["time_averaged_check"].invoke()
    assert export_lb.get(0, tkinter.END) == ("Loss_Density", "Core_Loss", "Avg_Ohmic_Loss")
    assert extension._widgets["time_label"].cget("text") == "Stop time:"
    assert extension._widgets["start_time_entry"].grid_info()

    extension._widgets["time_averaged_check"].invoke()
    assert export_lb.get(0, tkinter.END) == ("Mag_B", "Ohmic_Loss")
    assert extension._widgets["time_label"].cget("text") == "Time:"
    assert not extension._widgets["start_time_entry"].grid_info()

    extension.root.destroy()


@pytest.mark.parametrize("mock_maxwell_3d_app", ["2025.2"], indirect=True)
def test_transient_widgets_without_time_averaged(mock_maxwell_3d_app) -> None:
    """Test that the time averaged option is not available before AEDT 2026.1."""
    _transient_extension_mocks(mock_maxwell_3d_app)
    mock_maxwell_3d_app.post.available_report_quantities.return_value = ["Mag_B"]
    mock_vector_fields = {"Maxwell 3D": ["Vector_B"], "Maxwell 2D": ["B_Vector"]}

    with (
        patch("builtins.open", mock_open(read_data=json.dumps(mock_vector_fields))),
        patch("json.load", return_value=mock_vector_fields),
    ):
        extension = FieldsDistributionExtension(withdraw=True)

    assert "time_entry" in extension._widgets
    assert "time_averaged_check" not in extension._widgets
    assert "start_time_entry" not in extension._widgets

    extension.root.destroy()


def test_non_transient_widgets(mock_maxwell_3d_app) -> None:
    """Test that transient widgets are not created for non transient designs."""
    mock_maxwell_3d_app.solution_type = "Magnetostatic"
    mock_maxwell_3d_app.modeler.objects_by_name = {"Object1": MagicMock()}
    mock_maxwell_3d_app.existing_analysis_sweeps = ["Setup1 : LastAdaptive"]
    mock_maxwell_3d_app.post.fields_calculator.get_expressions = MagicMock(return_value=["Mag_B"])
    extension = FieldsDistributionExtension(withdraw=True)

    assert "transient_frame" not in extension._widgets
    assert "time_entry" not in extension._widgets

    extension.root.destroy()


def test_callback_export_transient_fields(mock_maxwell_3d_app) -> None:
    """Test export callback for fields at a given time."""
    _transient_extension_mocks(mock_maxwell_3d_app)
    extension = FieldsDistributionExtension(withdraw=True)

    extension._widgets["export_file_entry"].insert(tkinter.END, "/path/to/output.csv")
    extension._widgets["export_options_lb"].selection_set(0)
    extension._widgets["time_entry"].insert(0, "10ms")
    extension._widgets["export_button"].invoke()

    assert extension.data.export_option == "Mag_B"
    assert extension.data.field_type == "Fields"
    assert extension.data.time == "10ms"
    assert extension.data.solution_option == "Setup1 : Transient"


def test_callback_export_time_averaged_fields(mock_maxwell_3d_app) -> None:
    """Test export callback for time averaged fields."""
    _transient_extension_mocks(mock_maxwell_3d_app)
    extension = FieldsDistributionExtension(withdraw=True)

    extension._widgets["time_averaged_check"].invoke()
    extension._widgets["export_file_entry"].insert(tkinter.END, "/path/to/output.csv")
    extension._widgets["export_options_lb"].selection_set(0)
    extension._widgets["start_time_entry"].delete(0, tkinter.END)
    extension._widgets["start_time_entry"].insert(0, "5ms")
    extension._widgets["time_entry"].insert(0, "20ms")
    extension._widgets["export_button"].invoke()

    assert extension.data.export_option == "Loss_Density"
    assert extension.data.field_type == "Time Averaged Fields"
    assert extension.data.time == "20ms"
    assert extension.data.start_time == "5ms"


def test_callback_export_time_averaged_fields_no_time(mock_maxwell_3d_app) -> None:
    """Test export callback for time averaged fields without stop time."""
    _transient_extension_mocks(mock_maxwell_3d_app)

    with patch("tkinter.messagebox.showerror") as mock_error:
        extension = FieldsDistributionExtension(withdraw=True)
        extension._widgets["time_averaged_check"].invoke()
        extension._widgets["export_file_entry"].insert(tkinter.END, "/path/to/output.csv")
        extension._widgets["export_options_lb"].selection_set(0)
        extension._widgets["export_button"].invoke()

        mock_error.assert_called_with("Error", "Please specify the start and stop times for time averaged fields.")
        assert extension.data is None

    extension.root.destroy()


def _mock_main_app():
    """Create mocks for the main function."""
    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value.GetName.return_value = "Project1"
    mock_desktop.active_design.return_value.GetName.return_value = "Design1"
    mock_aedtapp = MagicMock()
    mock_aedtapp.design_type = "Maxwell 3D"
    mock_setup = MagicMock()
    mock_setup.name = "Setup1"
    mock_setup.is_solved = True
    mock_aedtapp.setups = [mock_setup]
    return mock_desktop, mock_aedtapp


@pytest.mark.parametrize("points_file", ["", "points.pts"])
def test_main_export_time_averaged_fields(tmp_path, points_file):
    """Test main function exports time averaged fields with and without sample points."""
    fld_path = tmp_path / "output.fld"
    fld_path.write_text("Header line 1\nHeader line 2\n1.0 2.0 3.0\n")
    csv_path = tmp_path / "output.csv"

    data = FieldsDistributionExtensionData(
        points_file=points_file,
        export_file=str(csv_path),
        export_option="Loss_Density",
        objects_list=["Object1"],
        solution_option="Setup1 : Transient",
        field_type="Time Averaged Fields",
        time="20ms",
        start_time="5ms",
    )
    mock_desktop, mock_aedtapp = _mock_main_app()
    mock_aedtapp.solution_type = "Transient"
    mock_aedtapp.setups[0].is_solved = False

    with (
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.maxwell3d.fields_distribution.get_pyaedt_app",
            return_value=mock_aedtapp,
        ),
        patch("ansys.aedt.core.extensions.maxwell3d.fields_distribution.write_csv"),
    ):
        assert main(data)

    mock_aedtapp.post.export_field_file.assert_not_called()
    if points_file:
        mock_aedtapp.post.export_transient_field_file_on_points.assert_called_once_with(
            quantity="Loss_Density",
            time="20ms",
            sample_points=points_file,
            solution="Setup1 : Transient",
            output_file=str(fld_path),
            field_type="Time Averaged Fields",
            start_time="5ms",
        )
        mock_aedtapp.post.export_transient_field_file.assert_not_called()
    else:
        mock_aedtapp.post.export_transient_field_file.assert_called_once_with(
            quantity="Loss_Density",
            time="20ms",
            solution="Setup1 : Transient",
            output_file=str(fld_path),
            assignment="Object1",
            objects_type="Surf",
            field_type="Time Averaged Fields",
            start_time="5ms",
        )
        mock_aedtapp.post.export_transient_field_file_on_points.assert_not_called()


def test_main_time_averaged_fields_no_time(tmp_path):
    """Test main function raises an error when time averaged fields have no stop time."""
    data = FieldsDistributionExtensionData(
        export_file=str(tmp_path / "output.csv"),
        export_option="Loss_Density",
        solution_option="Setup1 : Transient",
        field_type="Time Averaged Fields",
    )
    with pytest.raises(Exception, match="No stop time specified for time averaged fields."):
        main(data)
