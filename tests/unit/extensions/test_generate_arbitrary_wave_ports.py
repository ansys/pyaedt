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
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import ArbitraryWavePortExtension
from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import ArbitraryWavePortExtensionData
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_arbitrary_wave_port_extension_default(
    mock_hfss_3d_layout_app,
) -> None:
    """Test instantiation of the Arbitrary Wave Port extension."""
    extension = ArbitraryWavePortExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_arbitrary_wave_port_extension_generate_button(
    mock_hfss_3d_layout_app,
) -> None:
    """Test the Generate button in the Arbitrary Wave Port extension."""
    extension = ArbitraryWavePortExtension(withdraw=True)

    # Set some values in the widgets
    extension.work_dir_entry.insert(tkinter.END, "/test/work/dir")
    extension.source_file_entry.insert(tkinter.END, "/test/source/file.aedb")
    extension.mounting_side_combo.current(1)  # Set to "bottom"
    extension.import_edb_variable.set(False)

    extension.root.nametowidget("generate").invoke()
    data: ArbitraryWavePortExtensionData = extension.data

    assert "/test/work/dir" == data.working_path
    assert "/test/source/file.aedb" == data.source_path
    assert "bottom" == data.mounting_side
    assert not data.import_edb


def test_arbitrary_wave_port_extension_browse_functions(
    mock_hfss_3d_layout_app,
) -> None:
    """Test the browse functions in the Arbitrary Wave Port extension."""
    extension = ArbitraryWavePortExtension(withdraw=True)

    # Test that widgets exist and can be accessed
    assert extension.work_dir_entry is not None
    assert extension.source_file_entry is not None
    assert extension.mounting_side_combo is not None
    assert extension.import_edb_variable is not None

    # Test widget defaults
    assert "top" == extension.mounting_side_combo.get()
    assert extension.import_edb_variable.get()

    extension.root.destroy()


def test_arbitrary_wave_port_extension_data_validation() -> None:
    """Test data validation for the Arbitrary Wave Port extension."""
    # Test with empty working path
    data = ArbitraryWavePortExtensionData(working_path="", source_path="/test/source")

    with pytest.raises(AEDTRuntimeError) as exc_info:
        from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import main

        main(data)
    assert "No working path provided" in str(exc_info.value)

    # Test with empty source path
    data = ArbitraryWavePortExtensionData(working_path="/test/work", source_path="")

    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)
    assert "No source path provided" in str(exc_info.value)


def test_arbitrary_wave_port_extension_widget_interaction(
    mock_hfss_3d_layout_app,
) -> None:
    """Test widget interaction in the Arbitrary Wave Port extension."""
    extension = ArbitraryWavePortExtension(withdraw=True)

    # Test text entry widgets
    test_work_dir = "/path/to/work/directory"
    test_source_path = "/path/to/source/file.aedb"

    extension.work_dir_entry.insert(tkinter.END, test_work_dir)
    extension.source_file_entry.insert(tkinter.END, test_source_path)

    # Verify content is set correctly
    assert test_work_dir == extension.work_dir_entry.get("1.0", tkinter.END).strip()
    assert test_source_path == extension.source_file_entry.get("1.0", tkinter.END).strip()

    # Test combobox
    extension.mounting_side_combo.current(1)  # Select "bottom"
    assert "bottom" == extension.mounting_side_combo.get()

    # Test checkbox
    extension.import_edb_variable.set(False)
    assert not extension.import_edb_variable.get()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.filedialog.askdirectory")
def test_arbitrary_wave_port_browse_work_dir(mock_askdirectory, mock_hfss_3d_layout_app) -> None:
    """Test the browse work directory function."""
    # Set up the mock to return a test directory path
    test_directory = "/test/work/directory"
    mock_askdirectory.return_value = test_directory

    extension = ArbitraryWavePortExtension(withdraw=True)

    # Call the private method
    extension._ArbitraryWavePortExtension__browse_work_dir()

    # Verify the directory was inserted into the entry widget
    assert test_directory == extension.work_dir_entry.get("1.0", tkinter.END).strip()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.filedialog.askdirectory")
@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.filedialog.askopenfilename")
def test_arbitrary_wave_port_browse_source_file(mock_askopenfilename, mock_askdirectory, mock_hfss_3d_layout_app) -> None:
    """Test the browse source file function."""
    test_file_path = "/test/source/file.aedb"
    test_dir_path = "/test/source/folder.aedb"

    extension = ArbitraryWavePortExtension(withdraw=True)

    # Test with import_edb = False (should use askopenfilename)
    extension.import_edb_variable.set(False)
    mock_askopenfilename.return_value = test_file_path

    extension._ArbitraryWavePortExtension__browse_source_file()

    assert test_file_path == extension.source_file_entry.get("1.0", tkinter.END).strip()

    # Clear the entry for next test
    extension.source_file_entry.delete("1.0", tkinter.END)

    # Test with import_edb = True (should use askdirectory)
    extension.import_edb_variable.set(True)
    mock_askdirectory.return_value = test_dir_path

    extension._ArbitraryWavePortExtension__browse_source_file()

    assert test_dir_path == extension.source_file_entry.get("1.0", tkinter.END).strip()

    extension.root.destroy()
