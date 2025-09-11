# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2021 - 2025 ANSYS, Inc. and /or its affiliates.
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


class Filter(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def filename(self) -> str:
        """Name of file defining the outboard component.

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    def filename(self, value: str):
        self._set_property("Filename", f"{value}")

    @property
    def noise_temperature(self) -> float:
        """System Noise temperature (K) of the component.

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return float(val)

    @noise_temperature.setter
    def noise_temperature(self, value: float):
        self._set_property("Noise Temperature", f"{value}")

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._set_property("Notes", f"{value}")

    class TypeOption(Enum):
        BY_FILE = "By File"
        LOW_PASS = "Low Pass"  # nosec
        HIGH_PASS = "High Pass"  # nosec
        BAND_PASS = "Band Pass"  # nosec
        BAND_STOP = "Band Stop"
        TUNABLE_BANDPASS = "Tunable Bandpass"
        TUNABLE_BANDSTOP = "Tunable Bandstop"

    @property
    def type(self) -> TypeOption:
        """Type.

        Type of filter to define. The filter can be defined by file (measured or
        simulated data) or using one of EMIT's parametric models.
        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._set_property("Type", f"{value.value}")

    @property
    def insertion_loss(self) -> float:
        """Filter pass band loss.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss")
        return float(val)

    @insertion_loss.setter
    def insertion_loss(self, value: float):
        self._set_property("Insertion Loss", f"{value}")

    @property
    def stop_band_attenuation(self) -> float:
        """Filter stop band loss (attenuation).

        Value should be less than 200.
        """
        val = self._get_property("Stop band Attenuation")
        return float(val)

    @stop_band_attenuation.setter
    def stop_band_attenuation(self, value: float):
        self._set_property("Stop band Attenuation", f"{value}")

    @property
    def max_pass_band(self) -> float:
        """Maximum pass band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Max Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_pass_band.setter
    def max_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Pass Band", f"{value}")

    @property
    def min_stop_band(self) -> float:
        """Minimum stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Min Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @min_stop_band.setter
    def min_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Min Stop Band", f"{value}")

    @property
    def max_stop_band(self) -> float:
        """Maximum stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Max Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_stop_band.setter
    def max_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Stop Band", f"{value}")

    @property
    def min_pass_band(self) -> float:
        """Minimum pass band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Min Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @min_pass_band.setter
    def min_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Min Pass Band", f"{value}")

    @property
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
    def bp_lower_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassLowerStopBandFrequency", f"{value}")

    @property
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
    def bp_lower_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassLowerCutoffFrequency", f"{value}")

    @property
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
    def bp_higher_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassHigherCutoffFrequency", f"{value}")

    @property
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
    def bp_higher_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandPassHigherStopBandFrequency", f"{value}")

    @property
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
    def bs_lower_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopLowerCutoffFrequency", f"{value}")

    @property
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
    def bs_lower_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopLowerStopBandFrequency", f"{value}")

    @property
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
    def bs_higher_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopHigherStopBandFrequency", f"{value}")

    @property
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
    def bs_higher_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("BandStopHigherCutoffFrequency", f"{value}")

    @property
    def lowest_tuned_frequency(self) -> float:
        """Lowest tuned frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Lowest Tuned Frequency ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @lowest_tuned_frequency.setter
    def lowest_tuned_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Lowest Tuned Frequency ", f"{value}")

    @property
    def highest_tuned_frequency(self) -> float:
        """Highest tuned frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Highest Tuned Frequency ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @highest_tuned_frequency.setter
    def highest_tuned_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Highest Tuned Frequency ", f"{value}")

    @property
    def percent_bandwidth(self) -> float:
        """Tunable filter 3-dB bandwidth.

        Value should be between 0.001 and 100.
        """
        val = self._get_property("Percent Bandwidth")
        return float(val)

    @percent_bandwidth.setter
    def percent_bandwidth(self, value: float):
        self._set_property("Percent Bandwidth", f"{value}")

    @property
    def shape_factor(self) -> float:
        """Ratio defining the filter rolloff.

        Value should be between 1 and 100.
        """
        val = self._get_property("Shape Factor")
        return float(val)

    @shape_factor.setter
    def shape_factor(self, value: float):
        self._set_property("Shape Factor", f"{value}")

    @property
    def warnings(self) -> str:
        """Warning(s) for this node."""
        val = self._get_property("Warnings")
        return val
