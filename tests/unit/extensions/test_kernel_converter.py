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

from ansys.aedt.core.extensions.common.kernel_converter import EXTENSION_TITLE
from ansys.aedt.core.extensions.common.kernel_converter import KernelConverterExtension
from ansys.aedt.core.extensions.common.kernel_converter import KernelConverterExtensionData
from ansys.aedt.core.extensions.common.kernel_converter import _check_missing
from ansys.aedt.core.extensions.common.kernel_converter import _convert_3d_component
from ansys.aedt.core.extensions.common.kernel_converter import _convert_aedt
from ansys.aedt.core.extensions.common.kernel_converter import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def desktop():
    """Fixture to mock Desktop."""
    with patch("ansys.aedt.core.extensions.common.kernel_converter.Desktop") as mock_desktop_class:
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.aedt_process_id = 12345
        mock_desktop_instance.design_list.return_value = ["Design1", "Design2"]
        mock_desktop_instance.odesktop.NewProject.return_value = MagicMock()
        mock_desktop_class.return_value = mock_desktop_instance
        yield mock_desktop_instance


@pytest.fixture
def mock_app():
    """Fixture to mock AEDT application."""
    mock_app_instance = MagicMock()
    mock_app_instance.design_type = "HFSS"
    mock_app_instance.design_name = "TestDesign"
    mock_app_instance.working_directory = tempfile.gettempdir()
    mock_app_instance.modeler.object_names = ["Object1", "Object2"]
    mock_app_instance.modeler.unclassified_names = []
    mock_app_instance.oproject.CopyDesign.return_value = True
    mock_app_instance.oproject.Paste.return_value = True
    mock_app_instance.save_project.return_value = True

    # Mock the 3D component insertion
    mock_component = MagicMock()
    mock_component.edit_definition.return_value = mock_app_instance
    mock_app_instance.modeler.insert_3d_component.return_value = mock_component
    mock_app_instance.modeler.create_3dcomponent.return_value = True

    return mock_app_instance


def test_kernel_converter_extension_default(mock_app) -> None:
    """Test instantiation of the Kernel Converter extension."""
    extension = KernelConverterExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    # Check that all widgets are created
    assert extension.file_path_entry is not None
    assert extension.password_entry is not None
    assert extension.application_combo is not None
    assert extension.solution_combo is not None

    extension.root.destroy()


def test_kernel_converter_extension_data_class() -> None:
    """Test the KernelConverterExtensionData dataclass."""
    data = KernelConverterExtensionData()

    assert data.password == ""  # nosec
    assert data.application == "HFSS"
    assert data.solution == "Modal"
    assert data.file_path == ""

    # Test with custom values
    custom_data = KernelConverterExtensionData(
        password="test_password", application="Maxwell 3D", solution="Transient", file_path="/path/to/file.aedt"
    )

    assert custom_data.password == "test_password"  # nosec
    assert custom_data.application == "Maxwell 3D"
    assert custom_data.solution == "Transient"
    assert custom_data.file_path == "/path/to/file.aedt"


def test_kernel_converter_extension_convert_button(mock_app) -> None:
    """Test the Convert button in the Kernel Converter extension."""
    extension = KernelConverterExtension(withdraw=True)

    # Set some test values
    extension.file_path_entry.insert(tkinter.END, "/path/to/test.aedt")
    extension.password_entry.insert(0, "test_password")
    extension.application_combo.set("Maxwell 3D")
    extension.solution_combo.set("Transient")

    # Mock the root.destroy to prevent actual destruction during test
    extension.root.destroy = MagicMock()

    # Invoke the convert button
    extension.root.nametowidget("convert").invoke()

    data: KernelConverterExtensionData = extension.data

    assert data.file_path == "/path/to/test.aedt"
    assert data.password == "test_password"  # nosec
    assert data.application == "Maxwell 3D"
    assert data.solution == "Transient"


def test_kernel_converter_extension_browse_files(mock_app) -> None:
    """Test the browse files functionality."""
    extension = KernelConverterExtension(withdraw=True)

    # Mock filedialog.askopenfilename
    with patch("ansys.aedt.core.extensions.common.kernel_converter.filedialog.askopenfilename") as mock_dialog:
        mock_dialog.return_value = "/path/to/selected/file.aedt"

        extension._browse_files()

        # Check that the file path was inserted
        file_path = extension.file_path_entry.get("1.0", tkinter.END).strip()
        assert file_path == "/path/to/selected/file.aedt"

        # Test with no file selected
        mock_dialog.return_value = ""
        extension.file_path_entry.delete("1.0", tkinter.END)

        extension._browse_files()

        # Check that the file path entry remains empty
        file_path = extension.file_path_entry.get("1.0", tkinter.END).strip()
        assert file_path == ""

    extension.root.destroy()


def test_kernel_converter_extension_update_solutions(mock_app) -> None:
    """Test the solution update functionality when application changes."""
    extension = KernelConverterExtension(withdraw=True)

    # Test HFSS solutions
    extension.application_combo.set("HFSS")
    extension._update_solutions()
    hfss_solutions = extension.solution_combo["values"]
    assert len(hfss_solutions) > 0

    # Test Maxwell 3D solutions
    extension.application_combo.set("Maxwell 3D")
    extension._update_solutions()
    maxwell_solutions = extension.solution_combo["values"]
    assert len(maxwell_solutions) > 0

    # Test Q3D Extractor solutions
    extension.application_combo.set("Q3D Extractor")
    extension._update_solutions()
    q3d_solutions = extension.solution_combo["values"]
    assert len(q3d_solutions) > 0

    # Test Icepak solutions
    extension.application_combo.set("Icepak")
    extension._update_solutions()
    icepak_solutions = extension.solution_combo["values"]
    assert len(icepak_solutions) > 0

    # Test with invalid application
    extension.application_combo.set("Invalid App")
    extension._update_solutions()
    # Should not crash

    extension.root.destroy()


def test_main_function_no_file_path() -> None:
    """Test main function with no file path."""
    data = KernelConverterExtensionData(file_path="")

    with pytest.raises(AEDTRuntimeError, match="No file path provided to the extension."):
        main(data)


@patch("ansys.aedt.core.extensions.common.kernel_converter.search_files")
@patch("ansys.aedt.core.extensions.common.kernel_converter.Desktop")
@patch("ansys.aedt.core.extensions.common.kernel_converter._convert_aedt")
@patch("ansys.aedt.core.extensions.common.kernel_converter._convert_3d_component")
def test_main_function_with_directory(
    mock_convert_3d_component, mock_convert_aedt, mock_desktop_class, mock_search_files, mock_app
) -> None:
    """Test main function with directory path."""
    # Mock search_files to return test files
    mock_search_files.side_effect = [
        ["/path/to/test1.a3dcomp", "/path/to/test2.a3dcomp"],
        ["/path/to/test3.aedt", "/path/to/test4.aedt"],
    ]

    # Mock Desktop
    mock_desktop_instance = MagicMock()
    mock_desktop_class.return_value = mock_desktop_instance

    data = KernelConverterExtensionData(file_path="/path/to/directory")

    # Mock os.path.isdir to return True
    with patch("os.path.isdir", return_value=True):
        result = main(data)

    assert result is True
    assert mock_search_files.call_count == 2
    mock_desktop_instance.release_desktop.assert_called()


@patch("ansys.aedt.core.extensions.common.kernel_converter.Desktop")
@patch("ansys.aedt.core.extensions.common.kernel_converter._convert_aedt")
def test_main_function_with_single_file(mock_convert_aedt, mock_desktop_class, mock_app) -> None:
    """Test main function with single file path."""
    # Mock Desktop
    mock_desktop_instance = MagicMock()
    mock_desktop_class.return_value = mock_desktop_instance

    data = KernelConverterExtensionData(file_path="/path/to/test.aedt")

    # Mock os.path.isdir to return False
    with patch("os.path.isdir", return_value=False):
        result = main(data)

    assert result is True
    mock_convert_aedt.assert_called_once()
    mock_desktop_instance.release_desktop.assert_called()


@patch("ansys.aedt.core.extensions.common.kernel_converter.Desktop")
@patch("ansys.aedt.core.extensions.common.kernel_converter._convert_3d_component")
def test_main_function_with_3d_component(mock_convert_3d, mock_desktop_class, mock_app) -> None:
    """Test main function with 3D component file."""
    # Mock Desktop
    mock_desktop_instance = MagicMock()
    mock_desktop_class.return_value = mock_desktop_instance

    data = KernelConverterExtensionData(file_path="/path/to/test.a3dcomp")

    # Mock os.path.isdir to return False
    with patch("os.path.isdir", return_value=False):
        result = main(data)

    assert result is True
    mock_convert_3d.assert_called_once()
    mock_desktop_instance.release_desktop.assert_called()


@patch("ansys.aedt.core.extensions.common.kernel_converter.Desktop")
def test_main_function_with_exception_handling(mock_desktop_class, caplog) -> None:
    """Test main function exception handling."""
    # Mock Desktop
    mock_desktop_instance = MagicMock()
    mock_desktop_class.return_value = mock_desktop_instance

    data = KernelConverterExtensionData(file_path="/path/to/test.aedt")

    # Mock os.path.isdir to return False
    with patch("os.path.isdir", return_value=False):
        # Mock _convert_aedt to raise an exception
        with patch(
            "ansys.aedt.core.extensions.common.kernel_converter._convert_aedt", side_effect=Exception("Test error")
        ):
            result = main(data)

    assert result is True
    # Check that error was logged
    assert "Failed to convert" in caplog.text


def test_check_missing_function_unsupported_design_type(mock_app) -> None:
    """Test _check_missing function with unsupported design type."""
    input_object = mock_app
    output_object = mock_app
    output_object.design_type = "Unsupported"

    result = _check_missing(input_object, output_object, "/path/to/file.aedt")

    assert result is None


@patch("ansys.aedt.core.generic.file_utils.read_csv")
@patch("ansys.aedt.core.generic.file_utils.write_csv")
@patch("os.path.exists")
def test_check_missing_function_with_missing_objects(mock_exists, mock_write_csv, mock_read_csv, mock_app) -> None:
    """Test _check_missing function with missing objects."""
    input_object = mock_app
    input_object.modeler.object_names = ["Object1", "Object2", "Object3"]
    input_object.modeler.export_3d_model.return_value = True

    output_object = mock_app
    output_object.design_type = "HFSS"
    output_object.design_name = "TestDesign"
    output_object.modeler.object_names = ["Object1"]  # Missing objects
    output_object.modeler.unclassified_names = ["Object2"]
    output_object.modeler.import_3d_cad.return_value = True

    # Mock history for Object2
    mock_history = MagicMock()
    mock_history.children = {"Operation1": MagicMock(props={"Suppress Command": False})}
    output_object.modeler.__getitem__.return_value.history.return_value = mock_history

    mock_exists.return_value = False  # CSV file doesn't exist

    result = _check_missing(input_object, output_object, "/path/to/file.aedt")

    assert result[1] is True  # Success flag
    mock_write_csv.assert_called_once()


@patch("ansys.aedt.core.extensions.common.kernel_converter.Hfss")
@patch("ansys.aedt.core.extensions.common.kernel_converter.get_pyaedt_app")
@patch("ansys.aedt.core.extensions.common.kernel_converter._check_missing")
@patch("ansys.aedt.core.extensions.common.kernel_converter.generate_unique_name")
@patch("os.path.exists")
def test_convert_3d_component_function(
    mock_exists, mock_generate_name, mock_check_missing, mock_get_app, mock_hfss_class, mock_app
) -> None:
    """Test _convert_3d_component function."""
    # Setup mocks
    mock_exists.return_value = False
    mock_generate_name.return_value = "unique_name"
    mock_check_missing.return_value = ("error.csv", True)

    mock_desktop_input = MagicMock()
    mock_desktop_input.aedt_process_id = 12345
    mock_desktop_output = MagicMock()
    mock_desktop_output.aedt_process_id = 67890
    mock_desktop_output.DeleteProject.return_value = True

    mock_hfss_instance = mock_app
    mock_hfss_class.return_value = mock_hfss_instance
    mock_get_app.return_value = mock_hfss_instance

    data = KernelConverterExtensionData(
        file_path="/path/to/test.a3dcomp", password="test_password", application="HFSS", solution="Modal"
    )

    _convert_3d_component(data, mock_desktop_output, mock_desktop_input)

    # Verify that the required methods were called
    mock_hfss_instance.modeler.insert_3d_component.assert_called_once()
    mock_hfss_instance.modeler.create_3dcomponent.assert_called_once()
    mock_check_missing.assert_called_once()


@patch("ansys.aedt.core.extensions.common.kernel_converter.get_pyaedt_app")
@patch("ansys.aedt.core.extensions.common.kernel_converter._check_missing")
@patch("ansys.aedt.core.extensions.common.kernel_converter.generate_unique_name")
@patch("os.path.exists")
@patch("os.path.splitext")
@patch("os.path.split")
def test_convert_aedt_function(
    mock_split, mock_splitext, mock_exists, mock_generate_name, mock_check_missing, mock_get_app, mock_app
) -> None:
    """Test _convert_aedt function."""
    # Setup mocks
    mock_exists.return_value = False
    mock_generate_name.return_value = "unique_name"
    mock_check_missing.return_value = ("error.csv", True)
    mock_split.return_value = ("path", "test.aedt")
    mock_splitext.return_value = ("test", ".aedt")

    mock_desktop_input = MagicMock()
    mock_desktop_input.design_list.return_value = ["Design1"]
    mock_desktop_input.load_project.return_value = True
    mock_desktop_input.odesktop.CloseProject.return_value = True

    mock_desktop_output = MagicMock()
    mock_desktop_output.odesktop.NewProject.return_value = MagicMock()

    mock_app_instance = mock_app
    mock_get_app.return_value = mock_app_instance

    data = KernelConverterExtensionData(file_path="/path/to/test.aedt")

    _convert_aedt(data, mock_desktop_output, mock_desktop_input)

    # Verify that the required methods were called
    mock_desktop_input.load_project.assert_called_once()
    mock_app_instance.oproject.CopyDesign.assert_called_once()
    mock_check_missing.assert_called_once()
    mock_app_instance.save_project.assert_called_once()


def test_convert_3d_component_different_applications(mock_app) -> None:
    """Test _convert_3d_component with different application types."""
    with (
        patch("ansys.aedt.core.extensions.common.kernel_converter.Icepak") as mock_icepak,
        patch("ansys.aedt.core.extensions.common.kernel_converter.Maxwell3d") as mock_maxwell,
        patch("ansys.aedt.core.extensions.common.kernel_converter.Q3d") as mock_q3d,
        patch("ansys.aedt.core.extensions.common.kernel_converter.get_pyaedt_app"),
        patch("ansys.aedt.core.extensions.common.kernel_converter._check_missing"),
        patch("os.path.exists", return_value=False),
    ):
        mock_desktop_input = MagicMock()
        mock_desktop_input.aedt_process_id = 12345
        mock_desktop_output = MagicMock()
        mock_desktop_output.aedt_process_id = 67890
        mock_desktop_output.DeleteProject.return_value = True

        # Configure mock apps
        for mock_app_class in [mock_icepak, mock_maxwell, mock_q3d]:
            mock_app_class.return_value = mock_app

        # Test different applications
        test_cases = [("Icepak", mock_icepak), ("Maxwell 3D", mock_maxwell), ("Q3D Extractor", mock_q3d)]

        for app_name, mock_class in test_cases:
            data = KernelConverterExtensionData(
                file_path="/path/to/test.a3dcomp", application=app_name, solution="Modal"
            )

            _convert_3d_component(data, mock_desktop_output, mock_desktop_input)
            mock_class.assert_called()


@patch("ansys.aedt.core.generic.file_utils.read_csv")
@patch("ansys.aedt.core.generic.file_utils.write_csv")
@patch("os.path.exists")
def test_check_missing_function_with_unclassified_objects_history(mock_exists, mock_write_csv, mock_read_csv) -> None:
    """Test _check_missing function with unclassified objects history."""
    # Create separate mock objects for input and output
    input_object = MagicMock()
    input_object.modeler.object_names = ["Object1", "Object2"]

    output_object = MagicMock()
    output_object.design_type = "HFSS"
    output_object.design_name = "TestDesign"

    # Object2 is unclassified but not in final object_names
    output_object.modeler.object_names = ["Object1"]
    output_object.modeler.unclassified_names = ["Object2"]

    # Mock history for Object2 with an operation that has Suppress Command
    mock_operation = MagicMock()
    mock_operation.props = {"Suppress Command": False}

    mock_history = MagicMock()
    mock_history.children = {"Operation1": mock_operation}

    mock_object = MagicMock()
    mock_object.history.return_value = mock_history
    output_object.modeler.__getitem__.return_value = mock_object

    mock_exists.return_value = False

    result = _check_missing(input_object, output_object, "/path/to/file.aedt")

    assert result[1] is True
    # Verify the Suppress Command was set to True
    assert mock_operation.props["Suppress Command"] is True
    mock_write_csv.assert_called_once()
