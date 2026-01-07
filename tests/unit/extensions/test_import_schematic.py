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

import tkinter
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.circuit.import_schematic import EXTENSION_TITLE
from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicData
from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicExtension
from ansys.aedt.core.extensions.misc import ExtensionCircuitCommon


@pytest.fixture
def mock_aedt_app():
    """Fixture to create a mock AEDT application."""
    mock_aedt_application = MagicMock()
    mock_aedt_application.design_type = "Circuit Design"

    with patch.object(
        ExtensionCircuitCommon, "aedt_application", new_callable=PropertyMock
    ) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_import_schematic_extension_default(mock_desktop, mock_aedt_app):
    """Test instantiation of the Import Schematic extension."""
    mock_desktop.return_value = MagicMock()

    extension = ImportSchematicExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme
    assert extension._text_widget is not None

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("tkinter.filedialog.askopenfilename")
def test_import_schematic_browse_button(mock_filedialog, mock_desktop, mock_aedt_app):
    """Test the browse button functionality."""
    mock_desktop.return_value = MagicMock()
    mock_filedialog.return_value = "/path/to/test_file.asc"

    extension = ImportSchematicExtension(withdraw=True)

    # Simulate clicking the browse button
    browse_button = extension.root.nametowidget("!button")
    browse_button.invoke()

    # Check that the file path was inserted into the text widget
    file_path = extension._text_widget.get("1.0", tkinter.END).strip()
    assert "/path/to/test_file.asc" == file_path

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("pathlib.Path.exists")
def test_import_schematic_import_button_valid_file(mock_exists, mock_desktop, mock_aedt_app):
    """Test the import button with a valid file."""
    mock_desktop.return_value = MagicMock()
    mock_exists.return_value = True

    extension = ImportSchematicExtension(withdraw=True)

    # Insert a valid file path
    extension._text_widget.insert(tkinter.END, "/path/to/valid_file.asc")

    # Mock the destroy method to capture the data before window closes
    original_destroy = extension.root.destroy
    captured_data = None

    def mock_destroy():
        nonlocal captured_data
        captured_data = extension.data
        # Don't actually destroy to avoid issues in test

    extension.root.destroy = mock_destroy

    # Simulate clicking the import button
    import_button = extension.root.nametowidget("!button2")
    import_button.invoke()

    assert captured_data is not None
    assert isinstance(captured_data, ImportSchematicData)
    assert "/path/to/valid_file.asc" == captured_data.file_extension

    # Restore and clean up
    extension.root.destroy = original_destroy
    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("pathlib.Path.exists")
def test_import_schematic_import_button_invalid_file(mock_exists, mock_desktop, mock_aedt_app):
    """Test the import button with an invalid file."""
    mock_desktop.return_value = MagicMock()
    mock_exists.return_value = False

    extension = ImportSchematicExtension(withdraw=True)

    # Insert an invalid file path
    extension._text_widget.insert(tkinter.END, "/path/to/nonexistent_file.asc")

    # Simulate clicking the import button - should raise TclError
    import_button = extension.root.nametowidget("!button2")

    with pytest.raises(tkinter.TclError, match="/path/to/nonexistent_file.asc"):
        import_button.invoke()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_import_schematic_data_defaults(mock_desktop, mock_aedt_app):
    """Test ImportSchematicData default values."""
    data = ImportSchematicData()

    assert "" == data.file_extension


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_import_schematic_extension_ui_elements(mock_desktop, mock_aedt_app):
    """Test that all UI elements are properly created."""
    mock_desktop.return_value = MagicMock()

    extension = ImportSchematicExtension(withdraw=True)

    # Check that the main components exist
    widgets = extension.root.winfo_children()
    assert len(widgets) >= 4  # Label, text widget, browse button, import button

    # Verify text widget properties
    assert 40 == extension._text_widget.cget("width")
    assert 1 == extension._text_widget.cget("height")

    extension.root.destroy()
