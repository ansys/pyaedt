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

from enum import Enum

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.internal.checks import min_aedt_version


class Filter(EmitNode):
    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = True

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node"""
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node"""
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def filename(self) -> str:
        """Name of file defining the outboard component.

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    @min_aedt_version("2025.2")
    def filename(self, value: str):
        self._set_property("Filename", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def noise_temperature(self) -> float:
        """System Noise temperature (K) of the component.

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return float(val)

    @noise_temperature.setter
    @min_aedt_version("2025.2")
    def noise_temperature(self, value: float):
        self._set_property("Noise Temperature", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    @min_aedt_version("2025.2")
    def notes(self, value: str):
        self._set_property("Notes", f"{value}")

    class FilterTypeOption(Enum):
        BY_FILE = "ByFile"
        LOW_PASS = "LowPass"  # nosec
        HIGH_PASS = "HighPass"  # nosec
        BAND_PASS = "BandPass"  # nosec
        BAND_STOP = "BandStop"
        TUNABLE_BANDPASS = "TunableBandpass"
        TUNABLE_BANDSTOP = "TunableBandstop"

    @property
    @min_aedt_version("2025.2")
    def filter_type(self) -> FilterTypeOption:
        """Filter Type.

        Type of filter to define. The filter can be defined by file (measured or
        simulated data) or using one of EMIT's parametric models.
        """
        val = self._get_property("Filter Type")
        val = self.FilterTypeOption[val.upper()]
        return val

    @filter_type.setter
    @min_aedt_version("2025.2")
    def filter_type(self, value: FilterTypeOption):
        self._set_property("Filter Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def insertion_loss(self) -> float:
        """Filter pass band loss.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss")
        return float(val)

    @insertion_loss.setter
    @min_aedt_version("2025.2")
    def insertion_loss(self, value: float):
        self._set_property("Insertion Loss", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def stop_band_attenuation(self) -> float:
        """Filter stop band loss (attenuation).

        Value should be less than 200.
        """
        val = self._get_property("Stop band Attenuation")
        return float(val)

    @stop_band_attenuation.setter
    @min_aedt_version("2025.2")
    def stop_band_attenuation(self, value: float):
        self._set_property("Stop band Attenuation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def max_pass_band(self) -> float:
        """Maximum pass band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Max Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_pass_band.setter
    @min_aedt_version("2025.2")
    def max_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Pass Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def min_stop_band(self) -> float:
        """Minimum stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Min Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @min_stop_band.setter
    @min_aedt_version("2025.2")
    def min_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Min Stop Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def max_stop_band(self) -> float:
        """Maximum stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Max Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_stop_band.setter
    @min_aedt_version("2025.2")
    def max_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Stop Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def min_pass_band(self) -> float:
        """Minimum pass band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Min Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @min_pass_band.setter
    @min_aedt_version("2025.2")
    def min_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Min Pass Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bp_lower_stop_band(self) -> float:
        """Bandpass filter lower stop band frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Lower Stop Band")
        else:
            val = self._get_property("BP Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bp_lower_stop_band.setter
    @min_aedt_version("2025.2")
    def bp_lower_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassLowerStopBandFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bp_lower_cutoff(self) -> float:
        """Bandpass filter lower cutoff frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Lower Cutoff")
        else:
            val = self._get_property("BP Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bp_lower_cutoff.setter
    @min_aedt_version("2025.2")
    def bp_lower_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassLowerCutoffFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bp_higher_cutoff(self) -> float:
        """Bandpass filter higher cutoff frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Higher Cutoff")
        else:
            val = self._get_property("BP Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bp_higher_cutoff.setter
    @min_aedt_version("2025.2")
    def bp_higher_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassHigherCutoffFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bp_higher_stop_band(self) -> float:
        """Bandpass filter higher stop band frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Higher Stop Band")
        else:
            val = self._get_property("BP Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bp_higher_stop_band.setter
    @min_aedt_version("2025.2")
    def bp_higher_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassHigherStopBandFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bs_lower_cutoff(self) -> float:
        """Band stop filter lower cutoff frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Lower Cutoff")
        else:
            val = self._get_property("BS Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bs_lower_cutoff.setter
    @min_aedt_version("2025.2")
    def bs_lower_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopLowerCutoffFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bs_lower_stop_band(self) -> float:
        """Band stop filter lower stop band frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Lower Stop Band")
        else:
            val = self._get_property("BS Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bs_lower_stop_band.setter
    @min_aedt_version("2025.2")
    def bs_lower_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopLowerStopBandFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bs_higher_stop_band(self) -> float:
        """Band stop filter higher stop band frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Higher Stop Band")
        else:
            val = self._get_property("BS Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bs_higher_stop_band.setter
    @min_aedt_version("2025.2")
    def bs_higher_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopHigherStopBandFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bs_higher_cutoff(self) -> float:
        """Band stop filter higher cutoff frequency.

        Value should be between 1 and 100e9.
        """
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            val = self._get_property("Higher Cutoff")
        else:
            val = self._get_property("BS Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bs_higher_cutoff.setter
    @min_aedt_version("2025.2")
    def bs_higher_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopHigherCutoffFrequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def lowest_tuned_frequency(self) -> float:
        """Lowest tuned frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Lowest Tuned Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @lowest_tuned_frequency.setter
    @min_aedt_version("2025.2")
    def lowest_tuned_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Lowest Tuned Frequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def highest_tuned_frequency(self) -> float:
        """Highest tuned frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Highest Tuned Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @highest_tuned_frequency.setter
    @min_aedt_version("2025.2")
    def highest_tuned_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Highest Tuned Frequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def percent_bandwidth(self) -> float:
        """Tunable filter 3-dB bandwidth.

        Value should be between 0.001 and 100.
        """
        val = self._get_property("Percent Bandwidth")
        return float(val)

    @percent_bandwidth.setter
    @min_aedt_version("2025.2")
    def percent_bandwidth(self, value: float):
        self._set_property("Percent Bandwidth", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def shape_factor(self) -> float:
        """Ratio defining the filter rolloff.

        Value should be between 1 and 100.
        """
        val = self._get_property("Shape Factor")
        return float(val)

    @shape_factor.setter
    @min_aedt_version("2025.2")
    def shape_factor(self, value: float):
        self._set_property("Shape Factor", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def warnings(self) -> str:
        """Warning(s) for this node."""
        val = self._get_property("Warnings")
        return val
