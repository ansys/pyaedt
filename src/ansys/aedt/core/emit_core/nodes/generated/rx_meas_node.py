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


class RxMeasNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def file(self) -> str:
        """Name of the measurement source.

        Value should be a full file path.
        """
        val = self._get_property("File")
        return val

    @property
    def source_file(self) -> str:
        """Name of the measurement source.

        Value should be a full file path.
        """
        val = self._get_property("Source File")
        return val

    @property
    def receive_frequency(self) -> float:
        """Channel associated with the measurement file."""
        val = self._get_property("Receive Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    class MeasurementModeOption(Enum):
        AUDIO_SINAD = "Audio SINAD"
        DIGITAL_BER = "Digital BER"
        GPS_CNR = "GPS CNR"

    @property
    def measurement_mode(self) -> MeasurementModeOption:
        """Defines the mode for the receiver measurement."""
        val = self._get_property("Measurement Mode")
        val = self.MeasurementModeOption[val.upper()]
        return val

    @measurement_mode.setter
    def measurement_mode(self, value: MeasurementModeOption):
        self._set_property("Measurement Mode", f"{value.value}")

    @property
    def sinad_threshold(self) -> float:
        """SINAD Threshold used for the receiver measurements.

        Value should be between 5 and 20.
        """
        val = self._get_property("SINAD Threshold")
        return float(val)

    @sinad_threshold.setter
    def sinad_threshold(self, value: float):
        self._set_property("SINAD Threshold", f"{value}")

    @property
    def gps_cnr_threshold(self) -> float:
        """GPS CNR Threshold used for the receiver measurements.

        Value should be between 15 and 30.
        """
        val = self._get_property("GPS CNR Threshold")
        return float(val)

    @gps_cnr_threshold.setter
    def gps_cnr_threshold(self, value: float):
        self._set_property("GPS CNR Threshold", f"{value}")

    @property
    def ber_threshold(self) -> float:
        """BER Threshold used for the receiver measurements.

        Value should be between -12 and -1.
        """
        val = self._get_property("BER Threshold")
        return float(val)

    @ber_threshold.setter
    def ber_threshold(self, value: float):
        self._set_property("BER Threshold", f"{value}")

    @property
    def default_intended_power(self) -> bool:
        """Specify the intended signal.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Default Intended Power")
        return val == "true"

    @default_intended_power.setter
    def default_intended_power(self, value: bool):
        self._set_property("Default Intended Power", f"{str(value).lower()}")

    @property
    def intended_signal_power(self) -> float:
        """Specify the power level of the intended signal.

        Value should be between -140 and -50.
        """
        val = self._get_property("Intended Signal Power")
        return float(val)

    @intended_signal_power.setter
    def intended_signal_power(self, value: float):
        self._set_property("Intended Signal Power", f"{value}")

    @property
    def freq_deviation(self) -> float:
        """Specify the frequency deviation of the intended signal.

        Value should be between 1000 and 200000.
        """
        val = self._get_property("Freq. Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @freq_deviation.setter
    def freq_deviation(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Freq. Deviation", f"{value}")

    @property
    def modulation_depth(self) -> float:
        """Specify the modulation depth of the intended signal.

        Value should be between 10 and 100.
        """
        val = self._get_property("Modulation Depth")
        return float(val)

    @modulation_depth.setter
    def modulation_depth(self, value: float):
        self._set_property("Modulation Depth", f"{value}")

    @property
    def measure_selectivity(self) -> bool:
        """Enable/disable the measurement of the receiver's selectivity.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Measure Selectivity")
        return val == "true"

    @measure_selectivity.setter
    def measure_selectivity(self, value: bool):
        self._set_property("Measure Selectivity", f"{str(value).lower()}")

    @property
    def measure_mixer_products(self) -> bool:
        """Enable/disable the measurement of the receiver's mixer products.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Measure Mixer Products")
        return val == "true"

    @measure_mixer_products.setter
    def measure_mixer_products(self, value: bool):
        self._set_property("Measure Mixer Products", f"{str(value).lower()}")

    @property
    def max_rf_order(self) -> int:
        """Max RF Order of the mixer products to measure.

        Value should be greater than 1.
        """
        val = self._get_property("Max RF Order")
        return int(val)

    @max_rf_order.setter
    def max_rf_order(self, value: int):
        self._set_property("Max RF Order", f"{value}")

    @property
    def max_lo_order(self) -> int:
        """Max LO Order of the mixer products to measure.

        Value should be greater than 1.
        """
        val = self._get_property("Max LO Order")
        return int(val)

    @max_lo_order.setter
    def max_lo_order(self, value: int):
        self._set_property("Max LO Order", f"{value}")

    @property
    def include_if(self) -> bool:
        """Enable/disable the measurement of the IF channel.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Include IF")
        return val == "true"

    @include_if.setter
    def include_if(self, value: bool):
        self._set_property("Include IF", f"{str(value).lower()}")

    @property
    def measure_saturation(self) -> bool:
        """Enable/disable measurement of the receiver's saturation level.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Measure Saturation")
        return val == "true"

    @measure_saturation.setter
    def measure_saturation(self, value: bool):
        self._set_property("Measure Saturation", f"{str(value).lower()}")

    @property
    def use_ams_limits(self) -> bool:
        """Allow AMS to determine the limits for measuring saturation.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use AMS Limits")
        return val == "true"

    @use_ams_limits.setter
    def use_ams_limits(self, value: bool):
        self._set_property("Use AMS Limits", f"{str(value).lower()}")

    @property
    def start_frequency(self) -> float:
        """Starting frequency for the measurement sweep.

        Value should be greater than 1e6.
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @start_frequency.setter
    def start_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Start Frequency", f"{value}")

    @property
    def stop_frequency(self) -> float:
        """Stopping frequency for the measurement sweep.

        Value should be less than 6e9.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @stop_frequency.setter
    def stop_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Stop Frequency", f"{value}")

    @property
    def samples(self) -> int:
        """Number of measurement samples for each frequency.

        Value should be between 2 and 100.
        """
        val = self._get_property("Samples")
        return int(val)

    @samples.setter
    def samples(self, value: int):
        self._set_property("Samples", f"{value}")

    @property
    def exclude_mixer_products_below_noise(self) -> bool:
        """Include/Exclude Mixer Products below the noise.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Exclude Mixer Products Below Noise")
        return val == "true"

    @exclude_mixer_products_below_noise.setter
    def exclude_mixer_products_below_noise(self, value: bool):
        self._set_property("Exclude Mixer Products Below Noise", f"{str(value).lower()}")

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._get_property("Enabled")

    @enabled.setter
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")
