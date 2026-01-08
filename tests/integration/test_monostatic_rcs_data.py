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

import ast
import logging
from pathlib import Path
from unittest.mock import mock_open
from unittest.mock import patch

import pandas as pd
import pytest

from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSData

FILE_PATH = "dummy.json"

JSON_CONTENT_HDF = (
    '{"solution": "Trihedral_RCS", "monostatic_file": "rcs_data.h5", "model_units": "mm", "frequency_units": "GHz"}'
)
CONTENT = ast.literal_eval(JSON_CONTENT_HDF)
COLUMNS = ["MyName", "Column2", "Column3"]
VALUES = [12, 42]
VALUE_LOG_ERROR = "Value not available."
FREQUENCY_LOG_ERROR = "Frequency not available."
WINDOW_LOG_ERROR = "Invalid value for `window`. The value must be 'Flat', 'Hamming', or 'Hann'."

mock_df = pd.DataFrame(
    data=[[12, 42, 0], [34, 56, 1]],  # Example data
    columns=COLUMNS,
    index=pd.MultiIndex.from_tuples([("100Hz", "Level1"), ("200Hz", "Level2")], names=["Freq", "OtherLevel"]),
)


@pytest.fixture
def rcs_setup():
    with (
        patch("pandas.read_hdf") as mock_read_hdf,
        patch("pathlib.Path.is_file") as mock_is_file,
        patch("pathlib.Path.open", new_callable=mock_open, read_data=JSON_CONTENT_HDF) as mock_open_path,
    ):
        mock_is_file.return_value = True
        mock_read_hdf.return_value = mock_df  # Usar un DataFrame real aquí
        yield {"read_hdf": mock_read_hdf, "is_file": mock_is_file, "open": mock_open_path}


def test_success_with_existing_file(rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    assert isinstance(mono_rcs_data.raw_data, pd.DataFrame)
    assert CONTENT == mono_rcs_data.metadata
    assert COLUMNS[0] == mono_rcs_data.name
    assert "Trihedral_RCS" == mono_rcs_data.solution
    assert Path(FILE_PATH) == mono_rcs_data.input_file
    assert "GHz" == mono_rcs_data.frequency_units
    assert ["100Hz", "200Hz"] == mono_rcs_data.frequencies
    assert mono_rcs_data.frequency is None
    assert mono_rcs_data.available_incident_wave_theta is None
    assert mono_rcs_data.available_incident_wave_phi is None
    assert "dB20" == mono_rcs_data.data_conversion_function
    assert "Flat" == mono_rcs_data.window
    assert 1024 == mono_rcs_data.window_size
    assert "Horizontal" == mono_rcs_data.aspect_range
    assert 512 == mono_rcs_data.upsample_range
    assert 64 == mono_rcs_data.upsample_azimuth


@patch.object(MonostaticRCSData, "available_incident_wave_theta", new_callable=lambda: VALUES)
def test_set_incident_wave_theta_success(mock_property, caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.incident_wave_theta = 12

    assert not any((caplog.records[i].message == VALUE_LOG_ERROR for i in range(len(caplog.records))))


@patch.object(MonostaticRCSData, "available_incident_wave_theta", new_callable=lambda: VALUES)
def test_set_incident_wave_theta_failure(mock_property, caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.incident_wave_theta = 13

    assert any((caplog.records[i].message == VALUE_LOG_ERROR for i in range(len(caplog.records))))


@patch.object(MonostaticRCSData, "available_incident_wave_phi", new_callable=lambda: VALUES)
def test_set_incident_wave_phi_success(mock_property, caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.incident_wave_phi = 12

    assert not any((caplog.records[i].message == VALUE_LOG_ERROR for i in range(len(caplog.records))))


@patch.object(MonostaticRCSData, "available_incident_wave_phi", new_callable=lambda: VALUES)
def test_set_incident_wave_phi_failure(mock_property, caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.incident_wave_phi = 13

    assert any((caplog.records[i].message == VALUE_LOG_ERROR for i in range(len(caplog.records))))


@patch.object(MonostaticRCSData, "frequencies", new_callable=lambda: VALUES)
def test_set_frequency_failure(mock_property, caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.frequency = 13

    assert any((caplog.records[i].message == FREQUENCY_LOG_ERROR for i in range(len(caplog.records))))


@patch.object(MonostaticRCSData, "frequencies", new_callable=lambda: VALUES)
def test_set_frequency_success(mock_property, caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.frequency = "12 GHz"

    assert not any((caplog.records[i].message == FREQUENCY_LOG_ERROR for i in range(len(caplog.records))))


def test_set_window_success(caplog, rcs_setup):
    mono_rcs_data = MonostaticRCSData(input_file=FILE_PATH)

    with caplog.at_level(logging.ERROR, logger="Global"):
        mono_rcs_data.window = "Dummy"

    assert any((caplog.records[i].message == WINDOW_LOG_ERROR for i in range(len(caplog.records))))
