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

import pathlib
from pathlib import Path
import shutil

import pytest

from ansys.aedt.core.visualization.advanced.frtm_visualization import FRTMData
from ansys.aedt.core.visualization.advanced.frtm_visualization import FRTMPlotter
from ansys.aedt.core.visualization.advanced.frtm_visualization import get_results_files
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
from tests import TESTS_VISUALIZATION_PATH

test_subfolder = "FRTM"


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pytest.fixture(scope="class")
def setup_test_data(request, local_scratch):
    """Fixture to set up the test data directory and file before running the test class."""
    dir_original = Path(TESTS_VISUALIZATION_PATH) / "example_models" / test_subfolder
    input_dir = Path(local_scratch.path) / "frtm_files"
    shutil.copytree(dir_original, input_dir)

    request.cls.input_dir = input_dir
    request.cls.input_dir_with_index = input_dir / "with_index"
    request.cls.input_dir_without_index = input_dir / "without_index"

    yield


@pytest.mark.usefixtures("setup_test_data")
class TestClass:
    def test_get_results_files_with_index(self):
        assert not get_results_files(self.input_dir)
        results_files = get_results_files(self.input_dir_with_index)
        assert isinstance(results_files, dict)
        assert len(results_files) == 11
        assert isinstance(results_files[0.0], pathlib.Path)
        assert Path(results_files[0.0]).is_file()

    def test_get_results_files_without_index(self):
        results_files = get_results_files(self.input_dir_without_index)
        assert isinstance(results_files, dict)
        assert len(results_files) == 1
        assert isinstance(results_files[832], pathlib.Path)
        assert Path(results_files[832]).is_file()

    def test_window(self):
        results_files = get_results_files(self.input_dir_with_index)
        metadata_file_pulse = results_files[0.0]
        frtm_pulse = FRTMData(input_file=metadata_file_pulse)

        win_flat, win_flat_sum = frtm_pulse.window_function()
        assert len(win_flat) == 512
        assert win_flat_sum

        win_han, win_han_sum = frtm_pulse.window_function("Hann", 128)
        assert len(win_han) == 128
        assert win_han_sum

        win_hamming, win_hamming_sum = frtm_pulse.window_function("Hamming", 128)
        assert len(win_hamming) == 128
        assert win_hamming_sum

    def test_frtm_data(self):
        with pytest.raises(FileNotFoundError, match="FRTM file does not exist."):
            FRTMData(input_file="invented")

        # Load FRTM Pulse
        results_files = get_results_files(self.input_dir_with_index)
        metadata_file_pulse = results_files[0.0]
        frtm_pulse = FRTMData(input_file=metadata_file_pulse)
        assert isinstance(frtm_pulse.all_data, dict)
        assert frtm_pulse.dlxcd_version == 1
        assert frtm_pulse.row_count == 50000
        assert frtm_pulse.col_count == 2
        assert frtm_pulse.col_header1 == "ScatSgnlReal"
        assert frtm_pulse.col_header2 == "ScatSgnlImag"
        assert frtm_pulse.binary_record_length == 16
        assert frtm_pulse.binary_start_byte == 1602
        assert frtm_pulse.binary_byte_type_line == "doubledouble"
        assert frtm_pulse.radar_waveform == "PulseDoppler"
        assert frtm_pulse.radar_channels == "I+QLead"
        assert frtm_pulse.time_start
        assert frtm_pulse.time_stop
        assert frtm_pulse.cpi_frames == 200
        assert len(frtm_pulse.time_sweep) == 200
        assert frtm_pulse.cpi_duration
        assert frtm_pulse.pulse_repetition_frequency
        assert frtm_pulse.time_duration
        assert frtm_pulse.frequency_domain_type == "LinearSweep"
        assert frtm_pulse.frequency_start
        assert frtm_pulse.frequency_stop
        assert frtm_pulse.frequency_number == 250
        assert len(frtm_pulse.frequency_sweep) == 250
        assert frtm_pulse.frequency_delta
        assert frtm_pulse.frequency_bandwidth
        assert frtm_pulse.frequency_center
        assert len(frtm_pulse.antenna_names) == 2
        assert frtm_pulse.channel_number == 1
        assert len(frtm_pulse.coupling_combos) == 1
        assert len(frtm_pulse.channel_names) == 1
        channel_names = frtm_pulse.channel_names[0]
        assert len(frtm_pulse.all_data[channel_names][0]) == 250
        assert frtm_pulse.range_resolution
        assert frtm_pulse.range_maximum
        assert frtm_pulse.velocity_resolution
        assert frtm_pulse.velocity_maximum
        assert frtm_pulse.data_conversion_function == "dB20"
        frtm_pulse.data_conversion_function = "abs"
        assert frtm_pulse.data_conversion_function == "abs"

        # Load FRTM Chirp
        results_files = get_results_files(self.input_dir_without_index)
        metadata_file_chirp = results_files[832]
        frtm_chirp = FRTMData(input_file=metadata_file_chirp)
        assert isinstance(frtm_chirp.all_data, dict)
        assert frtm_chirp.row_count == 26800
        assert frtm_chirp.col_count == 1
        assert frtm_chirp.col_header1 == "ScatSgnlReal"
        assert frtm_chirp.col_header2 is None
        assert frtm_chirp.binary_record_length == 8
        assert frtm_chirp.binary_start_byte == 1728
        assert frtm_chirp.binary_byte_type_line == "double"
        assert frtm_chirp.radar_waveform == "CS-FMCW"
        assert frtm_chirp.radar_channels == "I"
        assert frtm_chirp.time_start
        assert frtm_chirp.time_stop
        assert frtm_chirp.cpi_frames == 200
        assert len(frtm_chirp.time_sweep) == 200
        assert frtm_chirp.cpi_duration
        assert frtm_chirp.pulse_repetition_frequency
        assert frtm_chirp.time_duration
        assert frtm_chirp.frequency_domain_type == "LinearSweep"
        assert frtm_chirp.frequency_start
        assert frtm_chirp.frequency_stop
        assert frtm_chirp.frequency_number == 67
        assert len(frtm_chirp.frequency_sweep) == 67
        assert frtm_chirp.frequency_delta
        assert frtm_chirp.frequency_bandwidth
        assert frtm_chirp.frequency_center
        assert len(frtm_chirp.antenna_names) == 2
        assert frtm_chirp.channel_number == 1
        assert len(frtm_chirp.coupling_combos) == 1
        assert len(frtm_chirp.channel_names) == 1
        channel_names = frtm_chirp.channel_names[0]
        assert len(frtm_chirp.all_data[channel_names][0]) == 134
        assert frtm_chirp.range_resolution
        assert frtm_chirp.range_maximum
        assert frtm_chirp.velocity_resolution
        assert frtm_chirp.velocity_maximum
        assert frtm_chirp.data_conversion_function == "dB20"
        frtm_chirp.data_conversion_function = "abs"
        assert frtm_chirp.data_conversion_function == "abs"

    def test_range_profile(self):
        results_files = get_results_files(self.input_dir_with_index)
        metadata_file_pulse = results_files[0.0]
        frtm_data = FRTMData(input_file=metadata_file_pulse)
        channel_name = frtm_data.channel_names[0]
        data_channel_1 = frtm_data.all_data[channel_name]
        data_cpi_0 = data_channel_1[0]

        range_doppler_1 = frtm_data.range_profile(data_cpi_0)
        assert len(range_doppler_1) == 250

        range_doppler_2 = frtm_data.range_profile(data_cpi_0, window="Flat", window_size=128)
        assert len(range_doppler_2) == 128

        range_doppler_3 = frtm_data.range_profile(data_cpi_0, window="Flat", window_size=512, oversampling=2)
        assert len(range_doppler_3) == 1024

    def test_range_doppler(self):
        results_files = get_results_files(self.input_dir_with_index)
        metadata_file_pulse = results_files[0.0]
        frtm_data = FRTMData(input_file=metadata_file_pulse)

        range_doppler_data_1 = frtm_data.range_doppler()
        assert range_doppler_data_1.shape == (250, 200)

        range_doppler_data_2 = frtm_data.range_doppler(range_bins=100, doppler_bins=100)
        assert range_doppler_data_2.shape == (100, 100)

        range_doppler_data_3 = frtm_data.range_doppler(range_bins=512, doppler_bins=512)
        assert range_doppler_data_3.shape == (512, 512)

    def test_plotter(self):
        results_files = get_results_files(self.input_dir_with_index)

        doppler_data_frames = {}
        doppler_data = None
        for frame, data_frame in results_files.items():
            doppler_data = FRTMData(data_frame)
            doppler_data_frames[frame] = doppler_data

        # Single FRTM file
        assert FRTMPlotter(frtm_data=doppler_data)

        # Multiple frames
        frtm_data = FRTMPlotter(frtm_data=doppler_data_frames)
        assert len(frtm_data.all_data) == 11
        assert len(frtm_data.frames) == 11

    def test_range_profile_plotter(self):
        results_files = get_results_files(self.input_dir_with_index)
        doppler_data_frames = {}
        for frame, data_frame in results_files.items():
            doppler_data = FRTMData(data_frame)
            doppler_data_frames[frame] = doppler_data

        frtm_plotter = FRTMPlotter(frtm_data=doppler_data_frames)

        with pytest.raises(ValueError):
            frtm_plotter.plot_range_profile(channel="invented")

        with pytest.raises(ValueError):
            frtm_plotter.plot_range_profile(cpi_frame=500)

        # Animation plot
        range_profile1 = frtm_plotter.plot_range_profile(show=False, animation=True)
        assert isinstance(range_profile1, ReportPlotter)

        # Overlap all plots
        range_profile2 = frtm_plotter.plot_range_profile(show=False, animation=False)
        assert isinstance(range_profile2, ReportPlotter)

        range_profile3 = frtm_plotter.plot_range_profile(show=False, frame=frtm_plotter.frames[0])
        assert isinstance(range_profile3, ReportPlotter)

    def test_range_doppler_plotter(self):
        results_files = get_results_files(self.input_dir_with_index)
        doppler_data_frames = {}
        for frame, data_frame in results_files.items():
            doppler_data = FRTMData(data_frame)
            doppler_data_frames[frame] = doppler_data

        frtm_plotter = FRTMPlotter(frtm_data=doppler_data_frames)

        with pytest.raises(ValueError):
            frtm_plotter.plot_range_profile(channel="invented")

        # Animation plot
        range_doppler1 = frtm_plotter.plot_range_doppler(show=False)
        assert isinstance(range_doppler1, ReportPlotter)

        # Overlap all plots
        range_doppler2 = frtm_plotter.plot_range_doppler(show=False, frame=frtm_plotter.frames[0])
        assert isinstance(range_doppler2, ReportPlotter)
