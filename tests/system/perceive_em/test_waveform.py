# ruff: noqa: E402

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

from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
from ansys.aedt.core.perceive_em.modules.waveform import Waveform


def test_waveform():
    wf = Waveform()
    assert wf.mode_delay == "center_chirp"
    wf.mode_delay = "first_chirp"
    assert wf.mode_delay == "first_chirp"
    assert wf.tx_multiplex == "simultaneous"
    wf.tx_multiplex = "individual"
    assert wf.tx_multiplex == "individual"
    assert wf.tx_incident_power == 1.0
    wf.tx_incident_power = 2.0
    assert wf.tx_incident_power == 2.0
    assert wf.rx_noise_db is None
    wf.rx_noise_db = 2.0
    assert wf.rx_noise_db == 2.0
    assert wf.rx_gain_db is None
    wf.rx_gain_db = 2.0
    assert wf.rx_gain_db == 2.0


def test_range_doppler_waveform():
    wf = RangeDopplerWaveform()

    # Check defaults
    assert wf.mode == "pulse_doppler"
    assert wf.output == "range_doppler"
    assert wf.center_frequency == 77e9
    assert wf.bandwidth == 1e9
    assert wf.frequency_samples == 101
    assert wf.cpi_duration == 1.0e-3
    assert wf.pulse_cpi == 201

    # Check dependent properties
    expected_wavelength = SpeedOfLight / 77e9
    assert abs(wf.wavelength - expected_wavelength) < 1e-6

    expected_range_resolution = SpeedOfLight / (2 * wf.bandwidth)
    assert abs(wf.range_resolution - expected_range_resolution) < 1e-6

    expected_pulse_interval = wf.cpi_duration / wf.pulse_cpi
    assert abs(wf.pulse_interval - expected_pulse_interval) < 1e-12

    # Modify system parameters
    wf.bandwidth = 2e9
    assert wf.bandwidth == 2e9
    assert abs(wf.range_resolution - (SpeedOfLight / (2 * 2e9))) < 1e-6

    wf.frequency_samples = 200
    assert wf.frequency_samples == 200
    assert abs(wf.range_period - (wf.frequency_samples * wf.range_resolution)) < 1e-3

    wf.cpi_duration = 2e-3
    assert wf.cpi_duration == 2e-3
    assert abs(wf.velocity_resolution - (wf.wavelength / (2 * 2e-3))) < 1e-6

    wf.pulse_cpi = 100
    assert wf.pulse_cpi == 100
    assert abs(wf.pulse_interval - (wf.cpi_duration / 100)) < 1e-12

    # Modify performance parameters
    wf.range_resolution = 0.15
    assert wf.range_resolution == 0.15
    assert abs(wf.bandwidth - (SpeedOfLight / (2 * 0.15))) < 1.0

    wf.range_period = 100
    assert wf.range_period == 100
    assert wf.frequency_samples == int(100 / 0.15)

    wf.velocity_resolution = 0.2
    assert wf.velocity_resolution == 0.2
    assert abs(wf.cpi_duration - (wf.wavelength / (2 * 0.2))) < 1e-6

    wf.velocity_period = 10
    assert wf.velocity_period == 10
    assert abs(wf.pulse_interval - (wf.wavelength / (2 * 10))) < 1e-12
    assert wf.pulse_cpi == int(wf.cpi_duration / wf.pulse_interval)
