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

from textwrap import dedent
from tkinter import TclError
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.icepak.power_map_from_csv import EXTENSION_TITLE
from ansys.aedt.core.extensions.icepak.power_map_from_csv import IcepakCSVFormatError
from ansys.aedt.core.extensions.icepak.power_map_from_csv import PowerMapFromCSVExtension
from ansys.aedt.core.extensions.icepak.power_map_from_csv import PowerMapFromCSVExtensionData
from ansys.aedt.core.extensions.icepak.power_map_from_csv import extract_info

MOCK_CSV_PATH = "/mock/path/power_map.csv"


@pytest.fixture
def invalid_csv_missing_source(tmp_path):
    """Fixture without source part."""
    content = dedent("""\
        # Sources Polygon Object.1
        #Name,Total source value,Total source value units
    """)
    f = tmp_path / "invalid_geom.csv"
    f.write_text(content)
    return f


@pytest.fixture
def invalid_csv_missing_geometric(tmp_path):
    """Fixture without geometric part."""
    content = dedent("""\
        # Sources Polygon Object.1
        #Name,Total source value,Total source value units
        name,temp_total,temp_total_units
        power_map_0,1,W

        # Sources Polygon
        #
    """)
    f = tmp_path / "invalid_geom.csv"
    f.write_text(content)
    return f


@pytest.fixture
def invalid_csv_missing_unit(tmp_path):
    """Fixture without geometric part."""
    content = dedent("""\
        # Sources Polygon Object.1
        #Name,Total source value,Total source value units
        name,temp_total,temp_total_units
        power_map_0,1

        # Sources Polygon
        #
    """)
    f = tmp_path / "invalid_geom.csv"
    f.write_text(content)
    return f


@pytest.fixture
def valid_csv(tmp_path):
    """Fixture with valid CSV content."""
    content = dedent("""\
        # Sources Polygon Object.1,
        #Name,Total source value,Total source value units
        name,temp_total,temp_total_units
        power_map_0,1,W
        power_map_1,2,W
        ,,
        # Sources Polygon,,,,,,,,,,,,,,,,,
        #,,,,,,,,,,,,,,,,,
        name,volume_flag,split_flag,changes,nverts,plane,height,xoff,yoff,zoff,vert1,tvert1,vert2,tvert2,vert3,tvert3,vert4,tvert4
        power_map_0,0,0,0,4,2,0,0,0,0,0.00200000 -0.0008000 0,,0.00200000 -0.0009000 0,,0.00180000 -0.0009000 0,,0.00180000 -0.0008000 0,
        power_map_1,0,0,0,4,2,0,0,0,0,0.00200000 -0.0009000 0,,0.00200000 -0.0010000 0,,0.00180000 -0.0010000 0,,0.00180000 -0.0009000 0,
    """)  # noqa: E501
    f = tmp_path / "valid_geom.csv"
    f.write_text(content)
    return f


@pytest.fixture
def patched_askopenfilename(valid_csv):
    """Fixture that patches tkinter.filedialog.askopenfilename to return our CSV."""
    with patch("tkinter.filedialog.askopenfilename", return_value=str(valid_csv)):
        yield valid_csv


def test_power_map_from_csv_default(mock_icepak_app):
    """Test instantiation of the PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert PowerMapFromCSVExtensionData() == extension.data
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename", return_value=MOCK_CSV_PATH)
def test_power_map_from_csv_file_selection(mock_askopenfilename, mock_icepak_app):
    """Test file selection in the PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    browse_button = extension._widgets["browse_file_button"]
    browse_button.invoke()
    entry = extension._widgets["browse_file_entry"]
    assert entry.get() == MOCK_CSV_PATH

    extension.root.destroy()


def test_power_map_from_csv_failure_on_file_path_checks(mock_icepak_app):
    """Test failure when file path checks fail in PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    create_button = extension._widgets["create_button"]
    with pytest.raises(TclError):
        create_button.invoke()

    extension.root.destroy()


def test_power_map_from_csv_success(patched_askopenfilename, mock_icepak_app):
    """Test successful creation of power map from CSV in PowerMapFromCSVExtension."""
    extension = PowerMapFromCSVExtension(withdraw=True)

    browse_button = extension._widgets["browse_file_button"]
    browse_button.invoke()
    create_button = extension._widgets["create_button"]
    create_button.invoke()

    assert patched_askopenfilename == extension.data.file_path
    assert {"power_map_0": "1", "power_map_1": "2"} == extension.data.source_value_info
    assert {"power_map_0": "W", "power_map_1": "W"} == extension.data.source_unit_info
    assert [
        {
            "name": "power_map_0",
            "vertices": [
                "0.00200000 -0.0008000 0",
                "",
                "0.00200000 -0.0009000 0",
                "",
                "0.00180000 -0.0009000 0",
                "",
                "0.00180000 -0.0008000 0",
                "",
            ],
        },
        {
            "name": "power_map_1",
            "vertices": [
                "0.00200000 -0.0009000 0",
                "",
                "0.00200000 -0.0010000 0",
                "",
                "0.00180000 -0.0010000 0",
                "",
                "0.00180000 -0.0009000 0",
                "",
            ],
        },
    ] == extension.data.geometric_info


def test_extract_info_missing_source(invalid_csv_missing_source):
    """Test that extract_info raises an error when the source part is missing."""
    with pytest.raises(IcepakCSVFormatError):
        extract_info(invalid_csv_missing_source)


def test_extract_info_missing_geometry(invalid_csv_missing_geometric):
    """Test that extract_info raises an error when the geometric part is missing."""
    with pytest.raises(IcepakCSVFormatError):
        extract_info(invalid_csv_missing_geometric)


def test_extract_info_missing_unit(invalid_csv_missing_unit):
    """Test that extract_info raises an error when the unit part is missing."""
    with pytest.raises(IcepakCSVFormatError):
        extract_info(invalid_csv_missing_unit)
