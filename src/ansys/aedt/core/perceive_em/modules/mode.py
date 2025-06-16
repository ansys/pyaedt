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

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.antenna import Antenna
from ansys.aedt.core.perceive_em.modules.antenna import ParametricBeam


class AntennaMode:
    """"""

    def __init__(self, antenna_device, waveform=None, name="Mode"):
        # Internal properties

        # Perceive EM API
        if waveform is None:
            # Default values
            self.__waveform = Waveform()
        elif isinstance(waveform, dict):
            self.__waveform = Waveform.from_dict(waveform)
        else:
            self.__waveform = waveform

        self._app = antenna_device._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        # self._logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__device_node = antenna_device.device_node
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

        self.response_types = {
            "range_doppler": self._rss.ResponseType.RANGE_DOPPLER,
            "freq_pulse": self._rss.ResponseType.FREQ_PULSE,
            "adc_samples": self._rss.ResponseType.ADC_SAMPLES,
        }

        # Antenna Mode does not have coordinate system

    @property
    @perceive_em_function_handler
    def name(self):
        """Actor name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.name
        """
        return self._api.name(self.mode_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.mode_node, value)

    @property
    def waveform(self):
        return self.__waveform

    @property
    def device_node(self):
        """Reference to the device node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__device_node

    @property
    def platform_name(self):
        """Reference to the platform node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__platform_name

    @property
    def device_name(self):
        """Device name associated with the actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__device_name

    @property
    def mode_node(self):
        """The Perceive EM node associated with this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__mode_node

    def add_antenna(self, name, properties=None):
        if name is None or name in self.antennas_tx or name in self.antennas_rx:
            name = generate_unique_name("Antenna")
            while name in self.antennas_tx or name in self.antennas_rx:  # pragma: no cover
                name = generate_unique_name(name)

        if properties is None:
            properties = []

        if not isinstance(properties, list):
            properties = [properties]

        antennas = []
        for prop in properties:
            antenna = Antenna(mode=self, name=name, properties=prop)
            if antenna.is_receiver:
                self.antennas_rx[antenna.name] = antenna
            else:
                self.antennas_tx[antenna.name] = antenna
            antennas.append(antenna)
        return antennas

    def update(self):
        # Apply settings
        if self.waveform.mode_delay == "center_chirp":
            mode_delay = self._rss.ModeDelayReference.CENTER_CHIRP
        else:
            mode_delay = self._rss.ModeDelayReference.FIRST_CHIRP

        self._set_start_delay(mode_delay)

        if self.waveform.tx_incident_power != 1.0:
            self._set_tx_incident_power(self.waveform.tx_incident_power)
        if self.waveform.rx_noise_db:
            self._set_thermal_noise(self.waveform.rx_noise_db)
        if self.waveform.rx_gain_db:
            self._set_rx_channel_gain(self.waveform.rx_gain_db)

        if self.waveform.mode == "pulseddoppler":
            self._set_pulsed_doppler_waveform()
        else:
            if self.waveform.mode == "fmcw":
                self._set_chirp_sequence_fmcw()

        if self.waveform.output in ["rangedoppler", "dopplerrange"]:
            if len(self.antennas_tx) > 0:
                self._activate_range_doppler_response()

    def get_response_domains(self):
        output = self.waveform.output
        if output == "rangedoppler" or output == "dopplerrange":
            ret, self.waveform.velocity_domain, self.waveform.range_domain = self._response_domains(
                self.response_types["range_doppler"]
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
                ret, self.waveform.pulse_domain, self.waveform.frequency_domain = self._response_domains(
                    self.response_types["adc_samples"]
                )

            elif output == "freqpulse":
                ret, self.waveform.pulse_domain, self.waveform.frequency_domain = self._response_domains(
                    self.response_types["freq_pulse"]
                )

            rng_res = 2.99792458e8 / 2 / self.waveform.bandwidth
            self.waveform.max_range = rng_res * self.waveform.frequency_samples
            self.waveform.range_domain = np.linspace(
                0, self.waveform.max_range, num=int(self.waveform.max_range / rng_res)
            )
            self.waveform.velocity_resolution = (
                2.99792458e8 / 2 / self.waveform.cpi_duration / self.waveform.center_frequency
            )
            self.waveform.velocity_win = self.waveform.velocity_resolution * self.waveform.frequency_samples
            self.waveform.velocity_domain = np.linspace(
                -self.waveform.velocity_win,
                self.waveform.velocity_win,
                num=int(self.waveform.velocity_win / self.waveform.velocity_resolution),
            )
            self.waveform.fast_time_domain = self.waveform.range_domain / 2.99792458e8

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
    def _set_chirp_sequence_fmcw(self):
        chirp_type = rss_py.FmcwChirpType.ASCENDING_RAMP

        if self.waveform.tx_multiplex == "simultaneous":
            tx_multiplex = self._rss.TxMultiplex.SIMULTANEOUS
        else:
            tx_multiplex = self._rss.TxMultiplex.INTERLEAVED

        return self._api.setChirpSequenceFMCWFromSysSpecs(
            self.mode_node,
            chirp_type,
            self.waveform.center_frequency,
            self.waveform.bandwidth,
            self.waveform.adc_sample_rate,
            self.waveform.frequency_samples,
            self.waveform.pulse_interval,
            self.waveform.pulse_cpi,
            self.waveform.is_iq_channel,
            tx_multiplex,
        )

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


@dataclass
class Waveform:
    velocity_domain: float = None
    range_domain: float = None
    frequency_domain: float = None
    pulse_domain: float = None
    range_specs: str = "hann," + str(50.0)
    distance_specs: str = "hann," + str(50)
    mode: str = "pulseddoppler"
    output: str = "rangedoppler"
    center_frequency: float = 77e9
    bandwidth: float = 1e9
    frequency_samples: int = 101
    pulse_cpi: int = 201
    cpi_duration: float = 1.0e-3
    pulse_interval: float = cpi_duration / pulse_cpi
    mode_delay: str = "center_chirp"
    tx_multiplex: str = "simultaneous"
    adc_sample_rate: float = 50.0e6
    is_iq_channel: bool = True
    tx_incident_power: float = 1.0
    rx_noise_db: float = None
    rx_gain_db: float = None

    @classmethod
    def from_dict(cls, data):
        """
        A class method that creates a Waveform instance from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the waveform data.

        Returns
        -------
        Waveform
            The created Waveform instance.

        Examples
        --------
        >>> from ansys.aedt.core.generic.file_utils import read_json
        >>> from ansys.aedt.core.perceive_em.scene.antenna_device import Waveform
        >>> waveform_dict = read_json("waveform.json")
        >>> waveform_props = Waveform.from_dict(materiwaveform_dictal_dict)
        """
        if "mode" in data.keys():
            mode = data.get("mode").lower().strip()
            if mode not in ["pulseddoppler", "fmcw"]:
                raise ValueError("Invalid mode. Available modes are: PulsedDoppler, and FMCW")
        else:
            mode = "pulseddoppler"

        if "output" in data.keys():
            output = data.get("output").lower().strip()
            if output not in ["freqpulse", "rangedoppler", "adc_samples"]:
                raise ValueError("Invalid mode. Available modes are: FreqPulse, RangeDoppler, and ADC_SAMPLES")
        else:
            output = "freqpulse"

        if "center_frequency" in data.keys():
            center_frequency = data.get("center_frequency")
        else:
            center_frequency = 76.5e9

        if "bandwidth" in data.keys():
            bandwidth = data.get("bandwidth")
        else:
            bandwidth = 1.0e9

        if "frequency_samples" in data.keys():
            frequency_samples = data.get("frequency_samples")
        else:
            frequency_samples = 101

        if "pulse_cpi" in data.keys():
            pulse_cpi = data.get("pulse_cpi")
        else:
            pulse_cpi = 201

        if "cpi_duration" in data.keys():
            if "pulse_interval" in data.keys():
                logger.info("Both cpi_duration and pulse_interval are defined. Using cpi_duration.")
            cpi_duration = data.get("cpi_duration")
            pulse_interval = cpi_duration / cls.pulse_cpi
        else:
            if "pulse_interval" in data.keys():
                pulse_interval = data.get("pulse_interval")
            else:
                pulse_interval = cls.cpi_duration / cls.pulse_cpi
            cpi_duration = 1.0e-3

        if "mode_delay" in data.keys():
            if data.get("mode_delay").lower().strip() == "first_chirp":
                mode_delay = "first_chirp"
            else:
                mode_delay = "center_chirp"
        else:
            mode_delay = "first_chirp"

        if "tx_multiplex" in data.keys():
            if data.get("tx_multiplex").lower().strip() == "simultaneous":
                tx_multiplex = "simultaneous"
            else:
                tx_multiplex = "interleaved"
        else:
            tx_multiplex = "simultaneous"

        if "adc_sample_rate" in data.keys():
            adc_sample_rate = data.get("adc_sample_rate")
        else:
            adc_sample_rate = 50.0e6

        if "is_iq_channel" in data.keys():
            is_iq_channel = data.get("is_iq_channel")
        else:
            is_iq_channel = True

        if "tx_incident_power" in data.keys():
            tx_incident_power = data.get("tx_incident_power")
        else:
            tx_incident_power = 1.0

        if "rx_noise_db" in data.keys():
            rx_noise_db = data.get("rx_noise_db")
        else:
            rx_noise_db = None

        if "rx_gain_db" in data.keys():
            rx_gain_db = data.get("rx_gain_db")
        else:
            rx_gain_db = None

        return cls(
            velocity_domain=data.get("velocity_domain", None),
            range_domain=data.get("range_domain", None),
            frequency_domain=data.get("frequency_domain", None),
            pulse_domain=data.get("pulse_domain", None),
            range_specs=data.get("range_specs", "hann," + str(50.0)),
            mode=mode,
            output=output,
            center_frequency=center_frequency,
            bandwidth=bandwidth,
            frequency_samples=frequency_samples,
            pulse_cpi=pulse_cpi,
            cpi_duration=cpi_duration,
            pulse_interval=pulse_interval,
            mode_delay=mode_delay,
            tx_multiplex=tx_multiplex,
            adc_sample_rate=adc_sample_rate,
            is_iq_channel=is_iq_channel,
            tx_incident_power=tx_incident_power,
            rx_noise_db=rx_noise_db,
            rx_gain_db=rx_gain_db,
        )

    def to_dict(self) -> dict:
        """
        Convert object to a dictionary.

        Returns
        -------
        dict
            Dictionary containing the material properties.
        """
        return {
            "velocity_domain": self.velocity_domain,
            "range_domain": self.range_domain,
            "frequency_domain": self.frequency_domain,
            "pulse_domain": self.pulse_domain,
            "range_specs": self.range_specs,
            "mode": self.mode,
            "output": self.output,
            "center_frequency": self.center_frequency,
            "bandwidth": self.bandwidth,
            "frequency_samples": self.frequency_samples,
            "pulse_cpi": self.pulse_cpi,
            "cpi_duration": self.cpi_duration,
            "pulse_interval": self.pulse_interval,
            "mode_delay": self.mode_node,
            "tx_multiplex": self.tx_multiplex,
            "adc_sample_rate": self.adc_sample_rate,
            "is_iq_channel": self.is_iq_channel,
            "tx_incident_power": self.tx_incident_power,
            "rx_noise_db": self.rx_noise_db,
            "rx_gain_db": self.rx_gain_db,
        }
