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


class Waveform:
    def __init__(self):
        self.__tx_incident_power = 1.0
        self.__rx_noise_db = None
        self.__rx_gain_db = None
        self.__mode_delay = "center_chirp"
        self.__tx_multiplex = "simultaneous"

        # What is this?
        sideLobeLevelDb = 50.0
        self.range_specs = "hann," + str(sideLobeLevelDb)
        self.distance_specs = "hann," + str(sideLobeLevelDb)

        self.mode = "default"
        self.output = "default"

    @property
    def mode_delay(self):
        return self.__mode_delay

    @property
    def tx_multiplex(self):
        return self.__tx_multiplex

    @property
    def tx_incident_power(self):
        return self.__tx_incident_power

    @property
    def rx_noise_db(self):
        return self.__rx_noise_db

    @property
    def rx_gain_db(self):
        return self.__rx_gain_db


class RangeDopplerWaveform(Waveform):
    def __init__(self):
        super().__init__()

        self.mode = "pulse_doppler"
        self.output = "range_doppler"

        self.center_frequency = 77e9

        # System
        self.__bandwidth = 1e9
        self.__frequency_samples = 101
        self.__cpi_duration = 1.0e-3
        self.__pulse_cpi = 201
        self.__pulse_interval = self.cpi_duration / self.pulse_cpi

        # Performance
        self.__range_resolution = None
        self.__range_period = None
        self.__velocity_resolution = None
        self.__velocity_period = None

        # Domains
        self.velocity_domain = None
        self.range_domain = None
        self.pulse_domain = None
        self.frequency_domain = None

        # Update performance values
        self.system_to_performance(
            bandwidth=self.bandwidth,
            frequency_samples=self.frequency_samples,
            cpi_duration=self.cpi_duration,
            pulse_cpi=self.pulse_cpi,
        )

    @property
    def bandwidth(self):
        return self.__bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self.__bandwidth = value
        self.system_to_performance(bandwidth=value)

    @property
    def frequency_samples(self):
        return self.__frequency_samples

    @frequency_samples.setter
    def frequency_samples(self, value):
        self.__frequency_samples = value
        self.system_to_performance(frequency_samples=value)

    @property
    def cpi_duration(self):
        return self.__cpi_duration

    @cpi_duration.setter
    def cpi_duration(self, value):
        self.__cpi_duration = value
        self.system_to_performance(cpi_duration=value)

    @property
    def pulse_cpi(self):
        return self.__pulse_cpi

    @pulse_cpi.setter
    def pulse_cpi(self, value):
        self.__pulse_cpi = value
        self.system_to_performance(pulse_cpi=value)

    @property
    def range_resolution(self):
        return self.__range_resolution

    @range_resolution.setter
    def range_resolution(self, value):
        self.__range_resolution = value
        self.performance_to_system(range_resolution=value)

    @property
    def range_period(self):
        return self.__range_period

    @range_period.setter
    def range_period(self, value):
        self.__range_period = value
        self.performance_to_system(range_period=value)

    @property
    def velocity_resolution(self):
        return self.__velocity_resolution

    @velocity_resolution.setter
    def velocity_resolution(self, value):
        self.__velocity_resolution = value
        self.performance_to_system(velocity_resolution=value)

    @property
    def velocity_period(self):
        return self.__velocity_period

    @velocity_period.setter
    def velocity_period(self, value):
        self.__velocity_period = value
        self.performance_to_system(velocity_period=value)

    @property
    def wavelength(self):
        return SpeedOfLight / self.center_frequency

    @property
    def pulse_interval(self):
        return self.__pulse_interval

    def system_to_performance(self, bandwidth=None, frequency_samples=None, cpi_duration=None, pulse_cpi=None):
        if bandwidth is not None:
            self.__bandwidth = bandwidth
        if frequency_samples is not None:
            self.__frequency_samples = frequency_samples
        if cpi_duration is not None:
            self.__cpi_duration = cpi_duration
        if pulse_cpi is not None:
            self.__pulse_cpi = pulse_cpi

        # Performance
        self.__range_resolution = SpeedOfLight / self.bandwidth / 2
        self.__range_period = self.frequency_samples * self.range_resolution
        self.__velocity_resolution = self.wavelength / (2 * self.cpi_duration)
        self.__velocity_period = self.wavelength / (2 * self.pulse_interval)

        self.__pulse_interval = self.cpi_duration / self.pulse_cpi

    def performance_to_system(
        self, range_resolution=None, range_period=None, velocity_resolution=None, velocity_period=None
    ):
        if range_resolution is not None:
            self.__range_resolution = range_resolution
        if range_period is not None:
            self.__range_period = range_period
        if velocity_resolution is not None:
            self.__velocity_resolution = velocity_resolution
        if velocity_period is not None:
            self.__velocity_period = velocity_period
            self.__pulse_interval = self.wavelength / (2 * self.velocity_period)

        # Performance
        self.__bandwidth = SpeedOfLight / (2 * self.range_resolution)
        self.__frequency_samples = int(self.range_period / self.range_resolution)
        self.__cpi_duration = self.wavelength / (2 * self.velocity_resolution)
        self.__pulse_cpi = int(self.cpi_duration / self.pulse_interval)
