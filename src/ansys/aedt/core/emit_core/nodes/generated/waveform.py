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


class Waveform(EmitNode):
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

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._get_property("Enabled")

    @enabled.setter
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")

    class WaveformOption(Enum):
        PERIODIC_CLOCK = "Periodic Clock"
        SPREAD_SPECTRUM_CLOCK = "Spread Spectrum Clock"
        PRBS = "PRBS"
        PRBS_PERIODIC = "PRBS (Periodic)"
        IMPORTED = "Imported"

    @property
    def waveform(self) -> WaveformOption:
        """Modulation used for the transmitted/received signal."""
        val = self._get_property("Waveform")
        val = self.WaveformOption[val.upper()]
        return val

    @waveform.setter
    def waveform(self, value: WaveformOption):
        self._set_property("Waveform", f"{value.value}")

    @property
    def start_frequency(self) -> float:
        """First frequency for this band.

        Value should be between 1 and 100e9.
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
        """Last frequency for this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @stop_frequency.setter
    def stop_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Stop Frequency", f"{value}")

    @property
    def channel_spacing(self) -> float:
        """Spacing between channels within this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Channel Spacing")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @channel_spacing.setter
    def channel_spacing(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Channel Spacing", f"{value}")

    @property
    def clock_duty_cycle(self) -> float:
        """Clock signals duty cycle.

        Value should be between 0.001 and 1.0.
        """
        val = self._get_property("Clock Duty Cycle")
        return float(val)

    @clock_duty_cycle.setter
    def clock_duty_cycle(self, value: float):
        self._set_property("Clock Duty Cycle", f"{value}")

    @property
    def clock_risefall_time(self) -> float:
        """Clock signals rise/fall time.

        Value should be greater than 0.0.
        """
        val = self._get_property("Clock Rise/Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @clock_risefall_time.setter
    def clock_risefall_time(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Clock Rise/Fall Time", f"{value}")

    class SpreadingTypeOption(Enum):
        LOW_SPREAD = "Low Spread"
        CENTER_SPREAD = "Center Spread"
        HIGH_SPREAD = "High Spread"

    @property
    def spreading_type(self) -> SpreadingTypeOption:
        """Type of spreading employed by the Spread Spectrum Clock."""
        val = self._get_property("Spreading Type")
        val = self.SpreadingTypeOption[val.upper()]
        return val

    @spreading_type.setter
    def spreading_type(self, value: SpreadingTypeOption):
        self._set_property("Spreading Type", f"{value.value}")

    @property
    def spread_percentage(self) -> float:
        """Peak-to-peak spread percentage.

        Value should be between 0 and 100.
        """
        val = self._get_property("Spread Percentage")
        return float(val)

    @spread_percentage.setter
    def spread_percentage(self, value: float):
        self._set_property("Spread Percentage", f"{value}")

    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum."""
        val = self._get_property("Imported Spectrum")
        return val

    @imported_spectrum.setter
    def imported_spectrum(self, value: str):
        self._set_property("Imported Spectrum", f"{value}")

    @property
    def raw_data_format(self) -> str:
        """Format of the imported raw data."""
        val = self._get_property("Raw Data Format")
        return val

    @property
    def system_impedance(self) -> float:
        """System impedance for the imported data.

        Value should be between 0.0 and 1.0e6.
        """
        val = self._get_property("System Impedance")
        val = self._convert_from_internal_units(float(val), "Resistance")
        return float(val)

    @system_impedance.setter
    def system_impedance(self, value: float | str):
        value = self._convert_to_internal_units(value, "Resistance")
        self._set_property("System Impedance", f"{value}")

    @property
    def advanced_extraction_params(self) -> bool:
        """Show/hide advanced extraction params.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Advanced Extraction Params")
        return val == "true"

    @advanced_extraction_params.setter
    def advanced_extraction_params(self, value: bool):
        self._set_property("Advanced Extraction Params", f"{str(value).lower()}")

    @property
    def nb_window_size(self) -> float:
        """NB Window Size.

        Window size for computing the moving average during narrowband signal
        detection.

        Value should be greater than 3.
        """
        val = self._get_property("NB Window Size")
        return float(val)

    @nb_window_size.setter
    def nb_window_size(self, value: float):
        self._set_property("NB Window Size", f"{value}")

    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor.

        Reduces the number of frequency points used for the broadband noise.

        Value should be greater than 1.
        """
        val = self._get_property("BB Smoothing Factor")
        return float(val)

    @bb_smoothing_factor.setter
    def bb_smoothing_factor(self, value: float):
        self._set_property("BB Smoothing Factor", f"{value}")

    @property
    def nb_detector_threshold(self) -> float:
        """Narrowband Detector threshold standard deviation.

        Value should be between 2 and 10.
        """
        val = self._get_property("NB Detector Threshold")
        return float(val)

    @nb_detector_threshold.setter
    def nb_detector_threshold(self, value: float):
        self._set_property("NB Detector Threshold", f"{value}")

    class AlgorithmOption(Enum):
        FFT = "FFT"
        FOURIER_TRANSFORM = "Fourier Transform"

    @property
    def algorithm(self) -> AlgorithmOption:
        """Algorithm used to transform the imported time domain spectrum."""
        val = self._get_property("Algorithm")
        val = self.AlgorithmOption[val.upper()]
        return val

    @algorithm.setter
    def algorithm(self, value: AlgorithmOption):
        self._set_property("Algorithm", f"{value.value}")

    @property
    def start_time(self) -> float:
        """Initial time of the imported spectrum.

        Value should be greater than 0.0.
        """
        val = self._get_property("Start Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @start_time.setter
    def start_time(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Start Time", f"{value}")

    @property
    def stop_time(self) -> float:
        """Final time of the imported time domain spectrum."""
        val = self._get_property("Stop Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @stop_time.setter
    def stop_time(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Stop Time", f"{value}")

    @property
    def max_frequency(self) -> float:
        """Frequency cutoff of the imported time domain spectrum.

        Value should be between 1.0 and 100.0e9.
        """
        val = self._get_property("Max Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_frequency.setter
    def max_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Frequency", f"{value}")

    class WindowTypeOption(Enum):
        RECTANGULAR = "Rectangular"
        BARTLETT = "Bartlett"
        BLACKMAN = "Blackman"
        HAMMING = "Hamming"
        HANNING = "Hanning"
        KAISER = "Kaiser"
        LANZCOS = "Lanzcos"
        WELCH = "Welch"
        WEBER = "Weber"

    @property
    def window_type(self) -> WindowTypeOption:
        """Windowing scheme used for importing time domain spectrum."""
        val = self._get_property("Window Type")
        val = self.WindowTypeOption[val.upper()]
        return val

    @window_type.setter
    def window_type(self, value: WindowTypeOption):
        self._set_property("Window Type", f"{value.value}")

    @property
    def kaiser_parameter(self) -> float:
        """Shape factor applied to the transform.

        Value should be greater than 0.0.
        """
        val = self._get_property("Kaiser Parameter")
        return float(val)

    @kaiser_parameter.setter
    def kaiser_parameter(self, value: float):
        self._set_property("Kaiser Parameter", f"{value}")

    @property
    def adjust_coherent_gain(self) -> bool:
        """Shape factor applied to the transform.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Adjust Coherent Gain")
        return val == "true"

    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value: bool):
        self._set_property("Adjust Coherent Gain", f"{str(value).lower()}")

    @property
    def data_rate(self) -> float:
        """Maximum data rate: helps determine shape of spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Data Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return float(val)

    @data_rate.setter
    def data_rate(self, value: float | str):
        value = self._convert_to_internal_units(value, "Data Rate")
        self._set_property("Data Rate", f"{value}")

    @property
    def num_of_bits(self) -> int:
        """Length of the Pseudo Random Binary Sequence.

        Value should be between 1 and 1000.
        """
        val = self._get_property("Num of Bits")
        return int(val)

    @num_of_bits.setter
    def num_of_bits(self, value: int):
        self._set_property("Num of Bits", f"{value}")

    @property
    def use_envelope(self) -> bool:
        """Model the waveform as a worst case envelope.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Envelope")
        return val == "true"

    @use_envelope.setter
    def use_envelope(self, value: bool):
        self._set_property("Use Envelope", f"{str(value).lower()}")

    @property
    def min_ptsnull(self) -> int:
        """Minimum number of points to use between each null frequency.

        Value should be between 2 and 50.
        """
        val = self._get_property("Min Pts/Null")
        return int(val)

    @min_ptsnull.setter
    def min_ptsnull(self, value: int):
        self._set_property("Min Pts/Null", f"{value}")

    @property
    def delay_skew(self) -> float:
        """Delay Skew of the differential signal pairs.

        Value should be greater than 0.0.
        """
        val = self._get_property("Delay Skew")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @delay_skew.setter
    def delay_skew(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Delay Skew", f"{value}")
