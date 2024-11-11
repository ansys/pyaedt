# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

import os
import shutil

from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSData

# from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSPlotter
import pandas as pd
import pytest

from tests import TESTS_GENERAL_PATH

test_subfolder = "T49"


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestClass:

    def test_01_rcs_data(self, local_scratch):
        dir_original = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder)
        data_dir = os.path.join(local_scratch.path, "rcs_files")
        shutil.copytree(dir_original, data_dir)
        metadata_file = os.path.join(data_dir, "rcs_metadata.json")
        rcs_data = MonostaticRCSData(input_file=metadata_file)

        assert isinstance(rcs_data.raw_data, pd.DataFrame)

        assert isinstance(rcs_data.metadata, dict)

        assert rcs_data.name == "HH"
        assert rcs_data.solution == "Trihedral_RCS"
        assert os.path.isfile(rcs_data.input_file)
        assert rcs_data.frequency_units == "GHz"
        assert len(rcs_data.frequencies) == 52

        assert rcs_data.available_incident_wave_theta.size == 52
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[0]

        rcs_data.incident_wave_theta = 88.0
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[0]

        rcs_data.incident_wave_theta = rcs_data.available_incident_wave_theta[1]
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[1]

        assert rcs_data.frequency == rcs_data.frequencies[0]

        rcs_data.frequency = f"{rcs_data.frequencies[1]}GHz"
        assert rcs_data.frequency == rcs_data.frequencies[1]

        rcs_data.frequency = rcs_data.frequencies[2]
        assert rcs_data.frequency == rcs_data.frequencies[2]

        rcs_data.frequency = 8.0
        assert rcs_data.frequency == rcs_data.frequencies[2]

        assert rcs_data.data_conversion_function == "dB20"
        rcs_data.data_conversion_function = "abs"
        assert rcs_data.data_conversion_function == "abs"

        assert rcs_data.window == "Flat"

        rcs_data.window = "Hamming"
        assert rcs_data.window == "Hamming"

        assert rcs_data.window_size == 1024
        rcs_data.window_size = 512
        assert rcs_data.window_size == 512

        assert rcs_data.aspect_range == "Horizontal"
        rcs_data.aspect_range = "Vertical"
        assert rcs_data.aspect_range == "Vertical"

        assert rcs_data.upsample_range == 512
        rcs_data.upsample_range = 24
        assert rcs_data.upsample_range == 24

        assert rcs_data.upsample_azimuth == 64
        rcs_data.upsample_azimuth = 32
        assert rcs_data.upsample_azimuth == 32

        assert isinstance(rcs_data.rcs, float)

        assert isinstance(rcs_data.rcs_active_theta_phi, pd.DataFrame)
        assert isinstance(rcs_data.rcs_active_frequency, pd.DataFrame)
        assert isinstance(rcs_data.rcs_active_theta, pd.DataFrame)
        assert isinstance(rcs_data.rcs_active_phi, pd.DataFrame)

        assert isinstance(rcs_data.range_profile, pd.DataFrame)
        assert isinstance(rcs_data.waterfall, pd.DataFrame)

        assert isinstance(rcs_data.isar_2d, pd.DataFrame)
        rcs_data.aspect_range = "Horizontal"
        assert isinstance(rcs_data.isar_2d, pd.DataFrame)
