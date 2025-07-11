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

from pathlib import Path
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.icepak.power_map_from_csv import EXTENSION_TITLE
from ansys.aedt.core.extensions.icepak.power_map_from_csv import PowerMapFromCSVExtension
from ansys.aedt.core.extensions.icepak.power_map_from_csv import PowerMapFromCSVExtensionData
from ansys.aedt.core.extensions.misc import ExtensionCommon

MOCK_CSV_PATH = "/mock/path/power_map.csv"
# MOCK_EXAMPLE_PATH = "/mock/path/configuration.toml"
# MOCK_CONTENT = "Dummy content"
# MOCK_TOML_CONTENT = {
#     "stacked_vias": {
#         "type_1": {"param1": "value1"},
#     },
#     "signals": {
#         "sig_1": {"stacked_vias": "type_1"},
#     },
#     "differential_signals": {
#         "diff_1": {"stacked_vias": "type_1"},
#     },
# }
# MOCK_CALL_OPEN = mock_open(read_data=MOCK_CONTENT)
# ORIGINAL_CALL_OPEN = open


# @pytest.fixture
# def toml_file_path(tmp_path):
#     """Fixture to create a temporary TOML file with mock content."""
#     file_path = tmp_path / "config.toml"
#     with file_path.open("w") as f:
#         toml.dump(MOCK_TOML_CONTENT, f)
#     return file_path


# @pytest.fixture
# def mock_aedt_classes():
#     """Fixture to mock AEDT classes used in the ViaDesignExtension tests."""
#     with (
#         patch("ansys.aedt.core.extensions.project.via_design.Hfss3dLayout") as mock_hfss_3d,
#         patch("ansys.aedt.core.extensions.misc.Desktop") as mock_desktop,
#         patch("ansys.aedt.core.extensions.project.via_design.ViaDesignBackend") as mock_backend,
#     ):
#         mock_hfss_3d_instance = MagicMock()
#         mock_hfss_3d.return_value = mock_hfss_3d_instance

#         mock_desktop_instance = MagicMock()
#         mock_desktop.return_value = mock_desktop_instance

#         mock_backend_instance = MagicMock()
#         mock_backend.return_value = mock_backend_instance

#         yield {
#             "hfss": mock_hfss_3d,
#             "hfss_instance": mock_hfss_3d_instance,
#             "desktop": mock_desktop,
#             "desktop_instance": mock_desktop_instance,
#             "backend": mock_backend,
#             "backend_instance": mock_backend_instance,
#         }


# def conditional_open(file=None, mode="r", *args, **kwargs):
#     """Conditional open function to handle file opening based on file type."""
#     if file is None or str(file).endswith(".toml"):
#         return MOCK_CALL_OPEN(file, mode, *args, **kwargs)
#     else:
#         return ORIGINAL_CALL_OPEN(file, mode, *args, **kwargs)
@pytest.fixture
def mock_aedt_app():
    """Fixture to mock AEDT application for CutoutExtension tests."""
    with (
        patch("ansys.aedt.core.extensions.misc.Desktop") as mock_desktop,
        patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application,
    ):
        mock_design = MagicMock()
        mock_design.GetDesignType.return_value = "Icepak"

        mock_desktop_instance = MagicMock()
        mock_desktop_instance.active_design.return_value = mock_design
        mock_desktop.return_value = mock_desktop_instance

        mock_aedt_application_instance = MagicMock()
        mock_aedt_application.return_value = mock_aedt_application_instance

        yield mock_aedt_application_instance


def test_power_map_from_csv_default(mock_aedt_app):
    """Test instantiation of the PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert PowerMapFromCSVExtensionData() == extension.data
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename", return_value=MOCK_CSV_PATH)
def test_power_map_from_csv_file_selection(mock_askopenfilename, mock_aedt_app):
    """Test file selection in the PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    browse_button = extension._widgets["browse_file_button"]
    browse_button.invoke()
    entry = extension._widgets["browse_file_entry"]
    assert entry.get() == MOCK_CSV_PATH

    extension.root.destroy()


def test_power_map_from_csv_failure_on_file_path_checks(mock_aedt_app):
    """Test failure when file path checks fail in PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    create_button = extension._widgets["create_button"]
    with pytest.raises(TclError):
        create_button.invoke()

    extension.root.destroy()


@patch("pathlib.Path.is_file", return_value=True)
@patch("tkinter.filedialog.askopenfilename", return_value=MOCK_CSV_PATH)
def test_power_map_from_csv_success(mock_is_file, mock_askopenfilename, mock_aedt_app):
    """Test successful creation of power map from CSV in PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    browse_button = extension._widgets["browse_file_button"]
    browse_button.invoke()
    create_button = extension._widgets["create_button"]
    create_button.invoke()

    assert Path(MOCK_CSV_PATH) == extension.data.file_path
