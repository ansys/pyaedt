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

import numpy as np

from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.antenna import Antenna
from ansys.aedt.core.perceive_em.modules.waveform import Waveform


class AntennaMode:
    """Antenna mode instance"""

    def __init__(self, antenna_device, waveform=None, name="Mode"):
        """
        Initialize the antenna mope instance.

        Parameters
        ----------
        antenna_device : :class:`ansys.aedt.core.perceive_em.modules.antenna_device.AntennaDevice`
            Mode instance.
        waveform : :class:`ansys.aedt.core.perceive_em.modules.waveform.Waveform`, optional
            Waveform assigned to the antenna mode.
        name : str, optional
            The name of the mode. If not provided, 'Mode' is used.
            If the name already exists in the scene, the name is changed until a unique name is found.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        """
        # Internal properties

        # Perceive EM API
        if waveform is None:
            # Default values
            self.__waveform = Waveform()
        # elif isinstance(waveform, dict):
        #     self.__waveform = Waveform.from_dict(waveform)
        else:
            self.__waveform = waveform

        self._app = antenna_device._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        self._logger = self._app._logger

        # Private properties

        # Perceive EM objects
        self.__device_node = antenna_device.scene_node
        self.__mode_node = None

        # Antenna mode properties
        self.__platform_name = antenna_device.platform_name
        self.__device_name = antenna_device.name

        self.range_pixels = 256
        self.doppler_pixels = 128
        self.center_velocity = 0.0

        self.antennas_rx = {}
        self.antennas_tx = {}

        # Perceive EM node
        # Create node
        self.__mode_node = self._add_mode_node()

        # Platform name. This is using Perceive EM API to set the Name of the node
        self.name = name

        self.output_types = {
            "range_doppler": self._rss.ResponseType.RANGE_DOPPLER,
            "freq_pulse": self._rss.ResponseType.FREQ_PULSE,
            "adc_samples": self._rss.ResponseType.ADC_SAMPLES,
        }

        # Antenna Mode does not have coordinate system

    @property
    @perceive_em_function_handler
    def name(self) -> str:
        """Mode name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.name
        """
        return self._api.name(self.mode_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.mode_node, value)

    @property
    def waveform(self):
        """Waveform assigned.

        Returns
        -------
        Waveform

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.waveform
        """
        return self.__waveform

    @property
    def device_node(self):
        """Antenna device node.

        Returns
        -------
        SceneNode

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.device_node
        """
        return self.__device_node

    @property
    def platform_name(self) -> str:
        """Antenna platform name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.platform_name
        """
        return self.__platform_name

    @property
    def device_name(self):
        """Antenna device name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.device_name
        """
        return self.__device_name

    @property
    def mode_node(self):
        """Mode node.

        Returns
        -------
        ModeNode

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.mode_node
        """
        return self.__mode_node

    def add_antenna(self, properties=None, name="antenna"):
        """Add antenna to mode.

        Parameters:
        ------------
        properties : :class:`ansys.aedt.core.perceive_em.modules.antenna.Transceiver`
            Transceiver.
        name : str, optional
            Antenna name. If not provided, 'antenna' is used.
            If the name already exists in the mode, the name is changed until a unique name is found.

        Returns
        -------
        list

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> new_antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(new_antenna_device)
        >>> antenna_mode.add_antenna()
        """
        if name in self.antennas_tx or name in self.antennas_rx:
            name = generate_unique_name("antenna")
            while name in self.antennas_tx or name in self.antennas_rx:  # pragma: no cover
                name = generate_unique_name(name)

        if properties is None:
            properties = []

        if not isinstance(properties, list):
            properties = [properties]

        antennas = []
        for prop in properties:
            name = prop.name
            if name in self.antennas_tx or name in self.antennas_rx:
                while prop.name in self.antennas_tx or prop.name in self.antennas_rx:
                    prop.name = generate_unique_name(name)
                self._logger.warning(f"{name} already exists. New name is {prop.name}")
            antenna = Antenna(mode=self, properties=prop)
            if antenna.is_receiver:
                self.antennas_rx[antenna.name] = antenna
            else:
                self.antennas_tx[antenna.name] = antenna
            antennas.append(antenna)
        return antennas

    def update(self):
        """Update waveform settings."""
        # Apply settings
        if self.waveform.mode_delay == "center_chirp":
            mode_delay = self._rss.ModeDelayReference.CENTER_CHIRP
        else:
            mode_delay = self._rss.ModeDelayReference.FIRST_CHIRP

        self._set_start_delay(mode_delay)

        if self.waveform.tx_incident_power != 1.0:
            self._set_tx_incident_power(self.waveform.tx_incident_power)
        if self.waveform.rx_noise_db:
            self._set_rx_thermal_noise(self.waveform.rx_noise_db)
        if self.waveform.rx_gain_db:
            self._set_rx_channel_gain(self.waveform.rx_gain_db)

        if self.waveform.mode == "pulse_doppler":
            self._set_pulsed_doppler_waveform()
        # else:
        #     if self.waveform.mode == "fmcw":
        #         self._set_chirp_sequence_fmcw()

        if self.waveform.output in ["range_doppler", "doppler_range"]:
            if len(self.antennas_tx) > 0:
                self._activate_range_doppler_response()

    def get_response_domains(self):
        """Get waveform settings from response domains."""
        output = self.waveform.output
        if output == "range_doppler" or output == "doppler_range":
            _, self.waveform.velocity_domain, self.waveform.range_domain = self._response_domains(
                self.output_types["range_doppler"]
            )

            self.waveform.pulse_domain = np.linspace(
                -self.waveform.cpi_duration / 2, self.waveform.cpi_duration / 2, num=self.waveform.pulse_cpi
            )
            self.waveform.frequency_domain = np.linspace(
                self.waveform.center_frequency - self.waveform.bandwidth / 2,
                self.waveform.center_frequency + self.waveform.bandwidth / 2,
                num=self.waveform.frequency_samples,
            )
        else:
            if output == "adc_samples":
                # NOT IMPLEMENTED
                _, self.waveform.pulse_domain, self.waveform.frequency_domain = self._response_domains(
                    self.output_types["adc_samples"]
                )

            elif output == "freq_pulse":
                # NOT IMPLEMENTED
                _, self.waveform.pulse_domain, self.waveform.frequency_domain = self._response_domains(
                    self.output_types["freq_pulse"]
                )

            rng_res = SpeedOfLight / 2 / self.waveform.bandwidth
            self.waveform.max_range = rng_res * self.waveform.frequency_samples
            self.waveform.range_domain = np.linspace(
                0, self.waveform.max_range, num=int(self.waveform.max_range / rng_res)
            )
            self.waveform.velocity_resolution = (
                SpeedOfLight / 2 / self.waveform.cpi_duration / self.waveform.center_frequency
            )
            self.waveform.velocity_win = self.waveform.velocity_resolution * self.waveform.frequency_samples
            self.waveform.velocity_domain = np.linspace(
                -self.waveform.velocity_win,
                self.waveform.velocity_win,
                num=int(self.waveform.velocity_win / self.waveform.velocity_resolution),
            )
            self.waveform.fast_time_domain = self.waveform.range_domain / SpeedOfLight

    # Internal Perceive EM API objects
    @perceive_em_function_handler
    def _response_domains(self, response_type):
        return self._api.responseDomains(self.mode_node, response_type)

    @perceive_em_function_handler
    def _radar_mode_node(self):
        """Create a new radar device node instance.

        This method instantiates a new, unregistered `RadarMode` object
        from the radar sensor scenario. It does not automatically add it to the scene.

        Returns
        -------
        RadarDevice
            A new radar device node instance.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em._device_node()
        """
        return self._rss.RadarMode()

    @perceive_em_function_handler
    def _add_mode_node(self):
        """Create and add a new radar device node to the simulation.

        This method creates a new `RadarDevice` using the API and adds it directly
        to the radar sensor scenario.

        Returns
        -------
        RadarDevice
            The radar device node that was added to the simulation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em._add_device_node()
        """
        node = self._radar_mode_node()
        self._api.addRadarMode(node, self.device_node)
        return node

    @perceive_em_function_handler
    def _enable(self, enable=True):
        self._api.setRadarModeActive(self.mode_node, enable)
        return True

    @perceive_em_function_handler
    def _set_mode_active(self, status=True):
        return self._api.setRadarModeActive(self.mode_node, status)

    @perceive_em_function_handler
    def _set_start_delay(self, mode_delay):
        return self._api.setRadarModeStartDelay(self.mode_node, 0.0, mode_delay)

    @perceive_em_function_handler
    def _set_tx_incident_power(self, tx_incident_power):
        return self._api.setRadarModeTxIncidentPower(self.mode_node, tx_incident_power)

    @perceive_em_function_handler
    def _set_rx_thermal_noise(self, rx_noise_db):
        return self._api.setRadarModeRxThermalNoise(self.mode_node, True, rx_noise_db)

    @perceive_em_function_handler
    def _set_rx_channel_gain(self, rx_gain_db):
        rx_gain_type = self._rss.RxChannelGainSpecType.USER_DEFINED
        return self._api.setRadarModeRxChannelGain(self.mode_node, rx_gain_type, rx_gain_db)

    @perceive_em_function_handler
    def _set_pulsed_doppler_waveform(self):
        if self.waveform.tx_multiplex == "simultaneous":
            tx_multiplex = self._rss.TxMultiplex.SIMULTANEOUS
        else:
            tx_multiplex = self._rss.TxMultiplex.INTERLEAVED

        return self._api.setPulseDopplerWaveformSysSpecs(
            self.mode_node,
            self.waveform.center_frequency,
            self.waveform.bandwidth,
            self.waveform.frequency_samples,
            self.waveform.pulse_interval,
            self.waveform.pulse_cpi,
            tx_multiplex,
        )

    @perceive_em_function_handler
    # def _set_chirp_sequence_fmcw(self):
    #     chirp_type = self._rss.FmcwChirpType.ASCENDING_RAMP
    #
    #     if self.waveform.tx_multiplex == "simultaneous":
    #         tx_multiplex = self._rss.TxMultiplex.SIMULTANEOUS
    #     else:
    #         tx_multiplex = self._rss.TxMultiplex.INTERLEAVED
    #
    #     return self._api.setChirpSequenceFMCWFromSysSpecs(
    #         self.mode_node,
    #         chirp_type,
    #         self.waveform.center_frequency,
    #         self.waveform.bandwidth,
    #         self.waveform.adc_sample_rate,
    #         self.waveform.frequency_samples,
    #         self.waveform.pulse_interval,
    #         self.waveform.pulse_cpi,
    #         self.waveform.is_iq_channel,
    #         tx_multiplex,
    #     )

    @perceive_em_function_handler
    def _activate_range_doppler_response(self):
        return self._api.activateRangeDopplerResponse(
            self.mode_node,
            self.range_pixels,
            self.doppler_pixels,
            self.center_velocity,
            self.waveform.range_specs,
            self.waveform.distance_specs,
        )
