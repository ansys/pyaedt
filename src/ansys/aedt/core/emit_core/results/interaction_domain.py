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

import warnings

from ansys.aedt.core.emit_core.emit_constants import EMIT_INTERNAL_UNITS
import ansys.aedt.core.generic.constants as consts
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class InteractionDomain:
    def __init__(self, emit_obj):
        self.emit_project = emit_obj
        """EMIT project."""

        self.current_revision = None
        """Current active Revision."""

        self.revisions = []
        """List of all result revisions. Only one loaded at a time."""

        self.design = emit_obj.desktop_class.active_design(emit_obj.odesktop.GetActiveProject())
        """Active design for the EMIT project."""

        self.aedt_version = int(self.emit_project.aedt_version_id[-3:])

        self.interferer_band_names = []
        """List of interferer band names."""

        self.interferer_channel_frequencies = []
        """List of interferer channel frequencies."""

        self.interferer_names = []
        """List of interferer names."""

        self.rx_band_name = ""
        """Receiver band name."""

        self.rx_channel_frequency = 0
        """Receiver channel frequency."""

        self.rx_name = ""
        """Receiver name."""

    @pyaedt_function_handler()
    def set_receiver(self, name: str, band_name: str, freq: float, units: str):
        """
        Set the receiver radio name, band name, and channel frequency.

        Parameters
        ----------
        name : str
            Name of the receiver radio.
        band_name : str
            Name of the receiver band.
        freq : float
            Channel frequency of the receiver.
        units : str
            Units of the channel frequency.

        Returns
        -------
        None
        """
        self.rx_name = name
        self.rx_band_name = band_name

        if units not in EMIT_INTERNAL_UNITS["Freq"]:
            err_msg = f"Unit {units} is not valid for frequency. Valid units are: {EMIT_INTERNAL_UNITS['Freq']}"
            warnings.warn(err_msg)

        converted_freq = consts.unit_converter(freq, "Freq", units, EMIT_INTERNAL_UNITS["Freq"])
        self.rx_channel_frequency = converted_freq

    @pyaedt_function_handler()
    def set_interferer(self, name: str, band_name: str, freq: float, units: str):
        """
        Set a single interferer radio name, band name, and channel frequency.

        Parameters
        ----------
        name : str
            Name of the interferer radio.
        band_name : str
            Name of the interferer band.
        freq : float
            Channel frequency of the interferer.
        units : str
            Units of the channel frequency.

        Returns
        -------
        None

        """
        self.interferer_names = []
        self.interferer_names.append(name)
        self.interferer_band_names = []
        self.interferer_band_names.append(band_name)
        self.interferer_channel_frequencies = []

        if units not in EMIT_INTERNAL_UNITS["Freq"]:
            err_msg = f"Unit {units} is not valid for frequency. Valid units are: {EMIT_INTERNAL_UNITS['Freq']}"
            warnings.warn(err_msg)

        converted_freq = consts.unit_converter(freq, "Freq", units, EMIT_INTERNAL_UNITS["Freq"])
        self.interferer_channel_frequencies.append(converted_freq)

    @pyaedt_function_handler()
    def set_interferers(self, names: list, band_names: list, freqs: list, units: str):
        """
        Set multiple interferer radio names, band names, and channel frequencies.

        Parameters
        ----------
        names : list
            List of interferer radio names.
        band_names : list
            List of interferer band names.
        freqs : list
            List of channel frequencies of the interferers.
        units : str
            Units of the channel frequencies.

        Returns
        -------
        None

        """
        if len(band_names) > 0 and len(band_names) != len(names):
            err_msg = "When assigning bands you must assign one band per interferer."
            warnings.warn(err_msg)
        if len(freqs) > 0 and len(freqs) != len(band_names):
            err_msg = "When assigning channels you must assign one channel per band."
            warnings.warn(err_msg)

        self.interferer_names = names
        self.interferer_band_names = band_names

        if units not in EMIT_INTERNAL_UNITS["Freq"]:
            err_msg = f"Unit {units} is not valid for frequency. Valid units are: {EMIT_INTERNAL_UNITS['Freq']}"
            warnings.warn(err_msg)

        converted_freqs = [consts.unit_converter(freq, "Freq", units, EMIT_INTERNAL_UNITS["Freq"]) for freq in freqs]

        self.interferer_channel_frequencies = converted_freqs

    @pyaedt_function_handler()
    def get_receiver_channel_frequency(self, units: str) -> float:
        """
        Get the receiver channel frequency in the specified units.

        Parameters
        ----------
        units : str
            Units of the channel frequency to return.

        Returns
        -------
        converted_freq : float
            Receiver channel frequency in the specified units.
        """
        if units not in EMIT_INTERNAL_UNITS["Freq"]:
            err_msg = f"Unit {units} is not valid for frequency. Valid units are: {EMIT_INTERNAL_UNITS['Freq']}"
            warnings.warn(err_msg)

        converted_freq = consts.unit_converter(self.rx_channel_frequency, "Freq", units, EMIT_INTERNAL_UNITS["Freq"])
        return converted_freq

    @pyaedt_function_handler()
    def get_interferer_channel_frequencies(self, units: str) -> list:
        """
        Get the interferer channel frequencies in the specified units.

        Parameters
        ----------
        units : str
            Units of the channel frequencies to return.

        Returns
        -------
        converted_freqs : list
            List of interferer channel frequencies in the specified units.
        """
        if units not in EMIT_INTERNAL_UNITS["Freq"]:
            err_msg = f"Unit {units} is not valid for frequency. Valid units are: {EMIT_INTERNAL_UNITS['Freq']}"
            warnings.warn(err_msg)

        converted_freqs = [
            consts.unit_converter(freq, "Freq", units, EMIT_INTERNAL_UNITS["Freq"])
            for freq in self.interferer_channel_frequencies
        ]
        return converted_freqs

    def is_single_instance(self):
        """
        Check if the Interaction Domain instance is fully defined for a single
        receiver and one or more interferers.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if the instance is fully defined, False otherwise.

        """
        if not self.rx_name or not self.rx_band_name or self.rx_channel_frequency < 0:
            return False
        if not self.interferer_names or not self.interferer_band_names or not self.interferer_channel_frequencies:
            return False
        if any(not name for name in self.interferer_names):
            return False
        if any(not band for band in self.interferer_band_names):
            return False
        if any(freq < 0 for freq in self.interferer_channel_frequencies):
            return False
        return True
