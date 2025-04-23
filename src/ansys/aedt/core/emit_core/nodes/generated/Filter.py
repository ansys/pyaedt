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

from ..EmitNode import EmitNode


class Filter(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property("Filename")
        return val  # type: ignore

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Filename={value}"])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Noise Temperature")
        return val  # type: ignore

    @noise_temperature.setter
    def noise_temperature(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Noise Temperature={value}"])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        " """
        val = self._get_property("Notes")
        return val  # type: ignore

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Notes={value}"])

    class TypeOption(Enum):
        BY_FILE = "By File"
        LOW_PASS = "Low Pass"
        HIGH_PASS = "High Pass"
        BAND_PASS = "Band Pass"
        BAND_STOP = "Band Stop"
        TUNABLE_BANDPASS = "Tunable Bandpass"
        TUNABLE_BANDSTOP = "Tunable Bandstop"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of filter to define. The filter can be defined by file (measured or simulated data) or using one of EMIT's parametric models."
        " """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val  # type: ignore

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Type={value.value}"])

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Filter pass band loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Insertion Loss")
        return val  # type: ignore

    @insertion_loss.setter
    def insertion_loss(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Insertion Loss={value}"])

    @property
    def stop_band_attenuation(self) -> float:
        """Stop band Attenuation
        "Filter stop band loss (attenuation)."
        "Value should be less than 200."
        """
        val = self._get_property("Stop band Attenuation")
        return val  # type: ignore

    @stop_band_attenuation.setter
    def stop_band_attenuation(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Stop band Attenuation={value}"])

    @property
    def max_pass_band(self) -> float:
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Max Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @max_pass_band.setter
    def max_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Max Pass Band={value}"])

    @property
    def min_stop_band(self) -> float:
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Min Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @min_stop_band.setter
    def min_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Min Stop Band={value}"])

    @property
    def max_stop_band(self) -> float:
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Max Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @max_stop_band.setter
    def max_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Max Stop Band={value}"])

    @property
    def min_pass_band(self) -> float:
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Min Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @min_pass_band.setter
    def min_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Min Pass Band={value}"])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @lower_stop_band.setter
    def lower_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Lower Stop Band={value}"])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @lower_cutoff.setter
    def lower_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Lower Cutoff={value}"])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @higher_cutoff.setter
    def higher_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Higher Cutoff={value}"])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @higher_stop_band.setter
    def higher_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Higher Stop Band={value}"])

    @property
    def lower_cutoff_(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @lower_cutoff_.setter
    def lower_cutoff_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Lower Cutoff ={value}"])

    @property
    def lower_stop_band_(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @lower_stop_band_.setter
    def lower_stop_band_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Lower Stop Band ={value}"])

    @property
    def higher_stop_band_(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @higher_stop_band_.setter
    def higher_stop_band_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Higher Stop Band ={value}"])

    @property
    def higher_cutoff_(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @higher_cutoff_.setter
    def higher_cutoff_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Higher Cutoff ={value}"])

    @property
    def lowest_tuned_frequency_(self) -> float:
        """Lowest Tuned Frequency
        "Lowest tuned frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lowest Tuned Frequency ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @lowest_tuned_frequency_.setter
    def lowest_tuned_frequency_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Lowest Tuned Frequency ={value}"])

    @property
    def highest_tuned_frequency_(self) -> float:
        """Highest Tuned Frequency
        "Highest tuned frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Highest Tuned Frequency ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @highest_tuned_frequency_.setter
    def highest_tuned_frequency_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Highest Tuned Frequency ={value}"])

    @property
    def percent_bandwidth(self) -> float:
        """Percent Bandwidth
        "Tunable filter 3-dB bandwidth."
        "Value should be between 0.001 and 100."
        """
        val = self._get_property("Percent Bandwidth")
        return val  # type: ignore

    @percent_bandwidth.setter
    def percent_bandwidth(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Percent Bandwidth={value}"])

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        "Ratio defining the filter rolloff."
        "Value should be between 1 and 100."
        """
        val = self._get_property("Shape Factor")
        return val  # type: ignore

    @shape_factor.setter
    def shape_factor(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Shape Factor={value}"])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        " """
        val = self._get_property("Warnings")
        return val  # type: ignore
