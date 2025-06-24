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
    """
    Base class representing a generic waveform configuration.

    This class provides basic transmitter and receiver settings,
    along with specifications for signal processing windows.
    """

    def __init__(self):
        """
        Initialize the Waveform with default parameters.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import Waveform
        >>> waveform = Waveform()
        """
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
    def mode_delay(self) -> str:
        """Mode delay.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import Waveform
        >>> waveform = Waveform()
        >>> waveform.mode_delay
        """
        return self.__mode_delay

    @property
    def tx_multiplex(self):
        """Transmission multiplexing mode.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import Waveform
        >>> waveform = Waveform()
        >>> waveform.tx_multiplex
        """
        return self.__tx_multiplex

    @property
    def tx_incident_power(self):
        """Transmitted signal power.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import Waveform
        >>> waveform = Waveform()
        >>> waveform.tx_incident_power
        """
        return self.__tx_incident_power

    @property
    def rx_noise_db(self):
        """Receiver noise level in decibels.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import Waveform
        >>> waveform = Waveform()
        >>> waveform.rx_noise_db
        """
        return self.__rx_noise_db

    @property
    def rx_gain_db(self):
        """Receiver gain level in decibels.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import Waveform
        >>> waveform = Waveform()
        >>> waveform.rx_gain_db
        """
        return self.__rx_gain_db


class RangeDopplerWaveform(Waveform):
    """Waveform for range-Doppler radar processing."""

    def __init__(self):
        """Initialize the range-Doppler waveform with default parameters.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        """
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
    def bandwidth(self) -> float:
        """System bandwidth in Hz.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.bandwidth
        """
        return self.__bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self.__bandwidth = value
        self.system_to_performance(bandwidth=value)

    @property
    def frequency_samples(self) -> int:
        """Number of frequency domain samples.

        Returns
        -------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.frequency_samples
        """
        return self.__frequency_samples

    @frequency_samples.setter
    def frequency_samples(self, value):
        self.__frequency_samples = value
        self.system_to_performance(frequency_samples=value)

    @property
    def cpi_duration(self) -> float:
        """Coherent processing interval in seconds.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.cpi_duration
        """
        return self.__cpi_duration

    @cpi_duration.setter
    def cpi_duration(self, value):
        self.__cpi_duration = value
        self.system_to_performance(cpi_duration=value)

    @property
    def pulse_cpi(self) -> int:
        """Number of pulses per coherent processing interval.

        Returns
        -------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.pulse_cpi
        """
        return self.__pulse_cpi

    @pulse_cpi.setter
    def pulse_cpi(self, value):
        self.__pulse_cpi = value
        self.system_to_performance(pulse_cpi=value)

    @property
    def range_resolution(self) -> float:
        """Range resolution in meters.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.range_resolution
        """
        return self.__range_resolution

    @range_resolution.setter
    def range_resolution(self, value):
        self.__range_resolution = value
        self.performance_to_system(range_resolution=value)

    @property
    def range_period(self) -> float:
        """Maximum measurable range period.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.range_period
        """
        return self.__range_period

    @range_period.setter
    def range_period(self, value):
        self.__range_period = value
        self.performance_to_system(range_period=value)

    @property
    def velocity_resolution(self) -> float:
        """Velocity resolution in m/s.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.velocity_resolution
        """
        return self.__velocity_resolution

    @velocity_resolution.setter
    def velocity_resolution(self, value):
        self.__velocity_resolution = value
        self.performance_to_system(velocity_resolution=value)

    @property
    def velocity_period(self) -> float:
        """Maximum measurable velocity period.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.velocity_period
        """
        return self.__velocity_period

    @velocity_period.setter
    def velocity_period(self, value):
        self.__velocity_period = value
        self.performance_to_system(velocity_period=value)

    @property
    def wavelength(self) -> float:
        """Wavelength derived from center frequency.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.wavelength
        """
        return SpeedOfLight / self.center_frequency

    @property
    def pulse_interval(self) -> float:
        """Interval between radar pulses.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> waveform.pulse_interval
        """
        return self.__pulse_interval

    def system_to_performance(
        self,
        bandwidth: float = None,
        frequency_samples: float = None,
        cpi_duration: float = None,
        pulse_cpi: int = None,
    ):
        """Convert system parameters to performance characteristics.

        Parameters
        ----------
        bandwidth : float, optional
        frequency_samples : int, optional
        cpi_duration : float, optional
        pulse_cpi : int, optional

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> old_range = waveform.range_resolution
        >>> waveform.system_to_performance(bandwidth=1e6)
        >>> new_range = waveform.range_resolution
        """
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
        """Convert performance characteristics to system parameters.

        Parameters
        ----------
        range_resolution : float, optional
        range_period : float, optional
        velocity_resolution : float, optional
        velocity_period : float, optional

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> waveform = RangeDopplerWaveform()
        >>> old_bandwidth = waveform.bandwidth
        >>> waveform.performance_to_system(range_resolution=0.1)
        >>> new_bandwidth = waveform.bandwidth
        """
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
