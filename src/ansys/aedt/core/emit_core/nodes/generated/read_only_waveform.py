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
from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode

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
        """Radio Port associated with this Band."""
        val = self._get_property("Port")
        return val

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

    @property
    def start_frequency(self) -> float:
        """First frequency for this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def stop_frequency(self) -> float:
        """Last frequency for this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def channel_spacing(self) -> float:
        """Spacing between channels within this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Channel Spacing")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def clock_duty_cycle(self) -> float:
        """Clock signals duty cycle.

        Value should be between 0.001 and 1.0.
        """
        val = self._get_property("Clock Duty Cycle")
        return float(val)

    @property
    def clock_risefall_time(self) -> float:
        """Clock signals rise/fall time.

        Value should be greater than 0.0.
        """
        val = self._get_property("Clock Rise/Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

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

    @property
    def spread_percentage(self) -> float:
        """Peak-to-peak spread percentage.

        Value should be between 0 and 100.
        """
        val = self._get_property("Spread Percentage")
        return float(val)

    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum."""
        val = self._get_property("Imported Spectrum")
        return val

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

    @property
    def advanced_extraction_params(self) -> bool:
        """Show/hide advanced extraction params.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Advanced Extraction Params")
        return (val == "true")

    @property
    def nb_window_size(self) -> float:
        """NB Window Size.

        Window size for computing the moving average during narrowband signal
        detection.

        Value should be greater than 3.
        """
        val = self._get_property("NB Window Size")
        return float(val)

    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor.

        Reduces the number of frequency points used for the broadband noise.

        Value should be greater than 1.
        """
        val = self._get_property("BB Smoothing Factor")
        return float(val)

    @property
    def nb_detector_threshold(self) -> float:
        """Narrowband Detector threshold standard deviation.

        Value should be between 2 and 10.
        """
        val = self._get_property("NB Detector Threshold")
        return float(val)

    class AlgorithmOption(Enum):
        FFT = "FFT"
        FOURIER_TRANSFORM = "Fourier Transform"

    @property
    def algorithm(self) -> AlgorithmOption:
        """Algorithm used to transform the imported time domain spectrum."""
        val = self._get_property("Algorithm")
        val = self.AlgorithmOption[val.upper()]
        return val

    @property
    def start_time(self) -> float:
        """Initial time of the imported spectrum.

        Value should be greater than 0.0.
        """
        val = self._get_property("Start Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @property
    def stop_time(self) -> float:
        """Final time of the imported time domain spectrum."""
        val = self._get_property("Stop Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @property
    def max_frequency(self) -> float:
        """Frequency cutoff of the imported time domain spectrum.

        Value should be between 1.0 and 100.0e9.
        """
        val = self._get_property("Max Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

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

    @property
    def kaiser_parameter(self) -> float:
        """Shape factor applied to the transform.

        Value should be greater than 0.0.
        """
        val = self._get_property("Kaiser Parameter")
        return float(val)

    @property
    def adjust_coherent_gain(self) -> bool:
        """Shape factor applied to the transform.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Adjust Coherent Gain")
        return (val == "true")

    @property
    def data_rate(self) -> float:
        """Maximum data rate: helps determine shape of spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Data Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return float(val)

    @property
    def num_of_bits(self) -> int:
        """Length of the Pseudo Random Binary Sequence.

        Value should be between 1 and 1000.
        """
        val = self._get_property("Num of Bits")
        return int(val)

    @property
    def use_envelope(self) -> bool:
        """Model the waveform as a worst case envelope.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Envelope")
        return (val == "true")

    @property
    def min_ptsnull(self) -> int:
        """Minimum number of points to use between each null frequency.

        Value should be between 2 and 50.
        """
        val = self._get_property("Min Pts/Null")
        return int(val)

    @property
    def delay_skew(self) -> float:
        """Delay Skew of the differential signal pairs.

        Value should be greater than 0.0.
        """
        val = self._get_property("Delay Skew")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

