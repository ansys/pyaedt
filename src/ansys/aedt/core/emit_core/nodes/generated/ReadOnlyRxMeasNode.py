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

from enum import Enum

from ..EmitNode import EmitNode


class ReadOnlyRxMeasNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def file(self) -> str:
        """File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        val = self._get_property("File")
        return val  # type: ignore

    @property
    def source_file(self) -> str:
        """Source File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        val = self._get_property("Source File")
        return val  # type: ignore

    @property
    def receive_frequency(self) -> float:
        """Receive Frequency
        "Channel associated with the measurement file."
        " """
        val = self._get_property("Receive Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    class MeasurementModeOption(Enum):
        AUDIO_SINAD = "Audio SINAD"
        DIGITAL_BER = "Digital BER"
        GPS_CNR = "GPS CNR"

    @property
    def measurement_mode(self) -> MeasurementModeOption:
        """Measurement Mode
        "Defines the mode for the receiver measurement."
        " """
        val = self._get_property("Measurement Mode")
        val = self.MeasurementModeOption[val]
        return val  # type: ignore

    @property
    def sinad_threshold(self) -> float:
        """SINAD Threshold
        "SINAD Threshold used for the receiver measurements."
        "Value should be between 5 and 20."
        """
        val = self._get_property("SINAD Threshold")
        return val  # type: ignore

    @property
    def gps_cnr_threshold(self) -> float:
        """GPS CNR Threshold
        "GPS CNR Threshold used for the receiver measurements."
        "Value should be between 15 and 30."
        """
        val = self._get_property("GPS CNR Threshold")
        return val  # type: ignore

    @property
    def ber_threshold(self) -> float:
        """BER Threshold
        "BER Threshold used for the receiver measurements."
        "Value should be between -12 and -1."
        """
        val = self._get_property("BER Threshold")
        return val  # type: ignore

    @property
    def default_intended_power(self) -> bool:
        """Default Intended Power
        "Specify the intended signal."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Default Intended Power")
        return val  # type: ignore

    @property
    def intended_signal_power(self) -> float:
        """Intended Signal Power
        "Specify the power level of the intended signal."
        "Value should be between -140 and -50."
        """
        val = self._get_property("Intended Signal Power")
        return val  # type: ignore

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Specify the frequency deviation of the intended signal."
        "Value should be between 1000 and 200000."
        """
        val = self._get_property("Freq. Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @property
    def modulation_depth(self) -> float:
        """Modulation Depth
        "Specify the modulation depth of the intended signal."
        "Value should be between 10 and 100."
        """
        val = self._get_property("Modulation Depth")
        return val  # type: ignore

    @property
    def measure_selectivity(self) -> bool:
        """Measure Selectivity
        "Enable/disable the measurement of the receiver's selectivity."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Measure Selectivity")
        return val  # type: ignore

    @property
    def measure_mixer_products(self) -> bool:
        """Measure Mixer Products
        "Enable/disable the measurement of the receiver's mixer products."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Measure Mixer Products")
        return val  # type: ignore

    @property
    def max_rf_order(self) -> int:
        """Max RF Order
        "Max RF Order of the mixer products to measure."
        "Value should be greater than 1."
        """
        val = self._get_property("Max RF Order")
        return val  # type: ignore

    @property
    def max_lo_order(self) -> int:
        """Max LO Order
        "Max LO Order of the mixer products to measure."
        "Value should be greater than 1."
        """
        val = self._get_property("Max LO Order")
        return val  # type: ignore

    @property
    def include_if(self) -> bool:
        """Include IF
        "Enable/disable the measurement of the IF channel."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Include IF")
        return val  # type: ignore

    @property
    def measure_saturation(self) -> bool:
        """Measure Saturation
        "Enable/disable measurement of the receiver's saturation level."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Measure Saturation")
        return val  # type: ignore

    @property
    def use_ams_limits(self) -> bool:
        """Use AMS Limits
        "Allow AMS to determine the limits for measuring saturation."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Use AMS Limits")
        return val  # type: ignore

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Value should be greater than 1e+06."
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Value should be less than 6e+09."
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val  # type: ignore

    @property
    def samples(self) -> int:
        """Samples
        "Number of measurement samples for each frequency."
        "Value should be between 2 and 100."
        """
        val = self._get_property("Samples")
        return val  # type: ignore

    @property
    def exclude_mixer_products_below_noise(self) -> bool:
        """Exclude Mixer Products Below Noise
        "Include/Exclude Mixer Products below the noise."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Exclude Mixer Products Below Noise")
        return val  # type: ignore
