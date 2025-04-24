# -*- coding: utf-8 -*-
#
# Copyright(C) 2021 - 2025 ANSYS, Inc. and /or its affiliates.
# SPDX - License - Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from enum import Enum
from ..EmitNode import EmitNode

class ReadOnlyWaveform(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def port(self):
        """Port
        Radio Port associated with this Band

                """
        val = self._get_property("Port")
        return val # type: ignore

    class WaveformOption(Enum):
        PERIODIC_CLOCK = "Periodic Clock" # eslint-disable-line no-eval
        SPREAD_SPECTRUM_CLOCK = "Spread Spectrum Clock" # eslint-disable-line no-eval
        PRBS = "PRBS" # eslint-disable-line no-eval
        PRBS_PERIODIC = "PRBS (Periodic)" # eslint-disable-line no-eval
        IMPORTED = "Imported" # eslint-disable-line no-eval

    @property
    def waveform(self) -> WaveformOption:
        """Waveform
        Modulation used for the transmitted/received signal

                """
        val = self._get_property("Waveform")
        val = self.WaveformOption[val.upper()]
        return val # type: ignore

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        First frequency for this band

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        Last frequency for this band

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        Spacing between channels within this band

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Channel Spacing")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def clock_duty_cycle(self) -> float:
        """Clock Duty Cycle
        Clock signals duty cycle

        Value should be between 0.001 and 1.
        """
        val = self._get_property("Clock Duty Cycle")
        return val # type: ignore

    @property
    def clock_risefall_time(self) -> float:
        """Clock Rise/Fall Time
        Clock signals rise/fall time

        Value should be greater than 0.
        """
        val = self._get_property("Clock Rise/Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    class SpreadingTypeOption(Enum):
        LOW_SPREAD = "Low Spread" # eslint-disable-line no-eval
        CENTER_SPREAD = "Center Spread" # eslint-disable-line no-eval
        HIGH_SPREAD = "High Spread" # eslint-disable-line no-eval

    @property
    def spreading_type(self) -> SpreadingTypeOption:
        """Spreading Type
        Type of spreading employed by the Spread Spectrum Clock

                """
        val = self._get_property("Spreading Type")
        val = self.SpreadingTypeOption[val.upper()]
        return val # type: ignore

    @property
    def spread_percentage(self) -> float:
        """Spread Percentage
        Peak-to-peak spread percentage

        Value should be between 0 and 100.
        """
        val = self._get_property("Spread Percentage")
        return val # type: ignore

    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum
        Value should be a full file path.
        """
        val = self._get_property("Imported Spectrum")
        return val # type: ignore

    @property
    def raw_data_format(self) -> str:
        """Raw Data Format
        Format of the imported raw data

                """
        val = self._get_property("Raw Data Format")
        return val # type: ignore

    @property
    def system_impedance(self) -> float:
        """System Impedance
        System impedance for the imported data

        Value should be between 0 and 1e+06.
        """
        val = self._get_property("System Impedance")
        val = self._convert_from_internal_units(float(val), "Resistance")
        return val # type: ignore

    @property
    def advanced_extraction_params(self) -> bool:
        """Advanced Extraction Params
        Show/hide advanced extraction params

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Advanced Extraction Params")
        val = (val == 'true')
        return val # type: ignore

    @property
    def nb_window_size(self) -> float:
        """NB Window Size
        Window size for computing the moving average during narrowband signal
         detection

        Value should be greater than 3.
        """
        val = self._get_property("NB Window Size")
        return val # type: ignore

    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor
        Reduces the number of frequency points used for the broadband noise

        Value should be greater than 1.
        """
        val = self._get_property("BB Smoothing Factor")
        return val # type: ignore

    @property
    def nb_detector_threshold(self) -> float:
        """NB Detector Threshold
        Narrowband Detector threshold standard deviation

        Value should be between 2 and 10.
        """
        val = self._get_property("NB Detector Threshold")
        return val # type: ignore

    class AlgorithmOption(Enum):
        FFT = "FFT" # eslint-disable-line no-eval
        FOURIER_TRANSFORM = "Fourier Transform" # eslint-disable-line no-eval

    @property
    def algorithm(self) -> AlgorithmOption:
        """Algorithm
        Algorithm used to transform the imported time domain spectrum

                """
        val = self._get_property("Algorithm")
        val = self.AlgorithmOption[val.upper()]
        return val # type: ignore

    @property
    def start_time(self) -> float:
        """Start Time
        Initial time of the imported spectrum

        Value should be greater than 0.
        """
        val = self._get_property("Start Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @property
    def stop_time(self) -> float:
        """Stop Time
        Final time of the imported time domain spectrum

                """
        val = self._get_property("Stop Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @property
    def max_frequency(self) -> float:
        """Max Frequency
        Frequency cutoff of the imported time domain spectrum

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Max Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    class WindowTypeOption(Enum):
        RECTANGULAR = "Rectangular" # eslint-disable-line no-eval
        BARTLETT = "Bartlett" # eslint-disable-line no-eval
        BLACKMAN = "Blackman" # eslint-disable-line no-eval
        HAMMING = "Hamming" # eslint-disable-line no-eval
        HANNING = "Hanning" # eslint-disable-line no-eval
        KAISER = "Kaiser" # eslint-disable-line no-eval
        LANZCOS = "Lanzcos" # eslint-disable-line no-eval
        WELCH = "Welch" # eslint-disable-line no-eval
        WEBER = "Weber" # eslint-disable-line no-eval

    @property
    def window_type(self) -> WindowTypeOption:
        """Window Type
        Windowing scheme used for importing time domain spectrum

                """
        val = self._get_property("Window Type")
        val = self.WindowTypeOption[val.upper()]
        return val # type: ignore

    @property
    def kaiser_parameter(self) -> float:
        """Kaiser Parameter
        Shape factor applied to the transform

        Value should be greater than 0.
        """
        val = self._get_property("Kaiser Parameter")
        return val # type: ignore

    @property
    def adjust_coherent_gain(self) -> bool:
        """Adjust Coherent Gain
        Shape factor applied to the transform

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Adjust Coherent Gain")
        val = (val == 'true')
        return val # type: ignore

    @property
    def data_rate(self) -> float:
        """Data Rate
        Maximum data rate: helps determine shape of spectral profile

        Value should be greater than 1.
        """
        val = self._get_property("Data Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return val # type: ignore

    @property
    def num_of_bits(self) -> int:
        """Num of Bits
        Length of the Pseudo Random Binary Sequence

        Value should be between 1 and 1000.
        """
        val = self._get_property("Num of Bits")
        return val # type: ignore

    @property
    def use_envelope(self) -> bool:
        """Use Envelope
        Model the waveform as a worst case envelope.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Envelope")
        val = (val == 'true')
        return val # type: ignore

    @property
    def min_ptsnull(self) -> int:
        """Min Pts/Null
        Minimum number of points to use between each null frequency

        Value should be between 2 and 50.
        """
        val = self._get_property("Min Pts/Null")
        return val # type: ignore

    @property
    def delay_skew(self) -> float:
        """Delay Skew
        Delay Skew of the differential signal pairs

        Value should be greater than 0.
        """
        val = self._get_property("Delay Skew")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

