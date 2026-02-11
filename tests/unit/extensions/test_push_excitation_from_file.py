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

from ansys.aedt.core.extensions.hfss.push_excitation_from_file import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss.push_excitation_from_file import PushExcitationExtension
from ansys.aedt.core.extensions.hfss.push_excitation_from_file import PushExcitationExtensionData
from ansys.aedt.core.extensions.hfss.push_excitation_from_file import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_main_function_exceptions() -> None:
    """Test exceptions in the main function."""
    # Test with no choice
    data = PushExcitationExtensionData(choice="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with no file path
    data = PushExcitationExtensionData(choice="Port1", file_path="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with non-existent file
    data = PushExcitationExtensionData(choice="Port1", file_path="nonexistent.csv")
    with pytest.raises(AEDTRuntimeError):
        main(data)


@pytest.fixture
def mock_hfss_app_with_excitations(mock_hfss_app):
    """Fixture to create a mock AEDT application with excitations."""
    mock_hfss_app.excitation_names = ["Port1", "Port2"]
    yield mock_hfss_app


def test_push_excitation_extension_default(mock_hfss_app_with_excitations) -> None:
    """Test instantiation of the Push Excitation extension."""
    extension = PushExcitationExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_push_excitation_extension_generate_button(mock_hfss_app_with_excitations) -> None:
    """Test the generate button in the Push Excitation extension."""
    extension = PushExcitationExtension(withdraw=True)

    # Set a test file path
    extension.file_entry.delete("1.0", tkinter.END)
    extension.file_entry.insert(tkinter.END, "test_file.csv")

    # Mock file existence
    with patch("pathlib.Path.is_file", return_value=True):
        extension.root.nametowidget("generate").invoke()

    data: PushExcitationExtensionData = extension.data

    # The first excitation should be selected by default
    assert "Port1" == data.choice
    assert "test_file.csv" == data.file_path


def test_push_excitation_extension_exceptions(
    mock_hfss_app_with_excitations,
) -> None:
    """Test exceptions in the Push Excitation extension."""
    # Test exception when no excitations exist
    mock_hfss_app_with_excitations.excitation_names = []
    with pytest.raises(AEDTRuntimeError):
        PushExcitationExtension(withdraw=True)

    # Reset to valid state
    mock_hfss_app_with_excitations.excitation_names = ["Port1", "Port2"]

    # Test exception when no port is selected
    extension = PushExcitationExtension(withdraw=True)
    extension.port_combo.set("")
    extension.file_entry.delete("1.0", tkinter.END)
    extension.file_entry.insert(tkinter.END, "valid_file.csv")

    with patch("pathlib.Path.is_file", return_value=True):
        with pytest.raises(TclError):
            extension.root.nametowidget("generate").invoke()

    # Test exception when no file is selected
    extension = PushExcitationExtension(withdraw=True)
    extension.file_entry.delete("1.0", tkinter.END)

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test exception when file doesn't exist
    extension = PushExcitationExtension(withdraw=True)
    extension.file_entry.delete("1.0", tkinter.END)
    extension.file_entry.insert(tkinter.END, "nonexistent_file.csv")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()


def test_push_excitation_extension_browse_files(
    mock_hfss_app_with_excitations,
) -> None:
    """Test the browse files functionality."""
    extension = PushExcitationExtension(withdraw=True)

    # Mock filedialog
    with patch("tkinter.filedialog.askopenfilename", return_value="selected_file.csv"):
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


def test_push_excitation_extension_wrong_design_type() -> None:
    """Test exception when design type is not HFSS."""
    mock_hfss_app = MagicMock()
    mock_hfss_app.design_type = "Maxwell3D"

    from ansys.aedt.core.extensions.misc import ExtensionCommon

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_property.return_value = mock_hfss_app

        with pytest.raises(AEDTRuntimeError):
            PushExcitationExtension(withdraw=True)
