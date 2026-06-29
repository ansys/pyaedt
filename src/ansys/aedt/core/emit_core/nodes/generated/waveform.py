# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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


class Waveform(EmitNode):
    """Provide waveform."""

    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.parent

        """
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform_copy = waveform.duplicate("Waveform_Copy")

        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """
        Delete this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.delete()

        """
        self._delete()

    @min_aedt_version("2025.2")
    def import_tx_measurement(self, file_name: str) -> EmitNode:
        """
        Import a Measurement from a File...

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> tx_meas = waveform.import_tx_measurement(r"C:\\Measurements\\tx_measurement.csv")

        """
        return self._import(file_name, "TxMeasurement")

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """
        Enabled state for this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.enabled = True

        """
        return self._get_property("Enabled") == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    class WaveformOption(Enum):
        PERIODIC_CLOCK = "Periodic Clock"
        SPREAD_SPECTRUM_CLOCK = "Spread Spectrum"
        PRBS = "PRBS"
        PRBS_PERIODIC = "PRBS (Periodic)"
        IMPORTED = "Imported"

    @property
    @min_aedt_version("2025.2")
    def waveform(self) -> WaveformOption:
        """
        Modulation used for the transmitted/received signal.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.waveform = wf.WaveformOption.SPREAD_SPECTRUM_CLOCK

        """
        val = self._get_property("Waveform")
        val = self.WaveformOption[val.upper()]
        return val

    @waveform.setter
    @min_aedt_version("2025.2")
    def waveform(self, value: WaveformOption) -> None:
        self._set_property("Waveform", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def start_frequency(self) -> float:
        """
        First frequency for this band.

        Value should be between 1 and 100e9.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.start_frequency = "2.4 GHz"

        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @start_frequency.setter
    @min_aedt_version("2025.2")
    def start_frequency(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Start Frequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def clock_duty_cycle(self) -> float:
        """
        Clock signals duty cycle.

        Value should be between 0.001 and 1.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.clock_duty_cycle = 0.5

        """
        val = self._get_property("Clock Duty Cycle")
        return float(val)

    @clock_duty_cycle.setter
    @min_aedt_version("2025.2")
    def clock_duty_cycle(self, value: float) -> None:
        self._set_property("Clock Duty Cycle", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def clock_risefall_time(self) -> float:
        """
        Clock signals rise/fall time.

        Value should be greater than 0.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.clock_risefall_time = "100 ps"

        """
        val = self._get_property("Clock Rise/Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @clock_risefall_time.setter
    @min_aedt_version("2025.2")
    def clock_risefall_time(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Clock Rise/Fall Time", f"{value}")

    class SpreadingTypeOption(Enum):
        LOW_SPREAD = "Low Spread"
        CENTER_SPREAD = "Center Spread"
        HIGH_SPREAD = "High Spread"

    @property
    @min_aedt_version("2025.2")
    def spreading_type(self) -> SpreadingTypeOption:
        """
        Type of spreading employed by the Spread Spectrum Clock.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> wf = emitter.get_waveforms()[0]
        >>> wf.spreading_type = wf.SpreadingTypeOption.CENTER_SPREAD

        """
        val = self._get_property("Spreading Type")
        val = self.SpreadingTypeOption[val.upper()]
        return val

    @spreading_type.setter
    @min_aedt_version("2025.2")
    def spreading_type(self, value: SpreadingTypeOption) -> None:
        self._set_property("Spreading Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def spread_percentage(self) -> float:
        """
        Peak-to-peak spread percentage.

        Value should be between 0 and 100.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.spread_percentage = 5.0

        """
        val = self._get_property("Spread Percentage")
        return float(val)

    @spread_percentage.setter
    @min_aedt_version("2025.2")
    def spread_percentage(self, value: float) -> None:
        self._set_property("Spread Percentage", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def imported_spectrum(self) -> str:
        """
        Imported Spectrum.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.imported_spectrum = "Spectrum1"

        """
        val = self._get_property("Imported Spectrum")
        return val

    @imported_spectrum.setter
    @min_aedt_version("2025.2")
    def imported_spectrum(self, value: str) -> None:
        self._set_property("Imported Spectrum", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def raw_data_format(self) -> str:
        """
        Format of the imported raw data.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.raw_data_format

        """
        val = self._get_property("Raw Data Format")
        return val

    @property
    @min_aedt_version("2025.2")
    def system_impedance(self) -> float:
        """
        System impedance for the imported data.

        Value should be between 0.0 and 1.0e6.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.system_impedance = "50ohm"

        """
        val = self._get_property("System Impedance")
        val = self._convert_from_internal_units(float(val), "Resistance")
        return float(val)

    @system_impedance.setter
    @min_aedt_version("2025.2")
    def system_impedance(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Resistance")
        self._set_property("System Impedance", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def advanced_extraction_params(self) -> bool:
        """
        Show/hide advanced extraction params.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.advanced_extraction_params = True

        """
        val = self._get_property("Advanced Extraction Params")
        return val == "true"

    @advanced_extraction_params.setter
    @min_aedt_version("2025.2")
    def advanced_extraction_params(self, value: bool) -> None:
        self._set_property("Advanced Extraction Params", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def nb_window_size(self) -> float:
        """
        NB Window Size.

        Window size for computing the moving average during narrowband signal
        detection.

        Value should be greater than 3.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.nb_window_size = 5

        """
        val = self._get_property("NB Window Size")
        return float(val)

    @nb_window_size.setter
    @min_aedt_version("2025.2")
    def nb_window_size(self, value: float) -> None:
        self._set_property("NB Window Size", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bb_smoothing_factor(self) -> float:
        """
        BB Smoothing Factor.

        Reduces the number of frequency points used for the broadband noise.

        Value should be greater than 1.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.bb_smoothing_factor = 4

        """
        val = self._get_property("BB Smoothing Factor")
        return float(val)

    @bb_smoothing_factor.setter
    @min_aedt_version("2025.2")
    def bb_smoothing_factor(self, value: float) -> None:
        self._set_property("BB Smoothing Factor", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def nb_detector_threshold(self) -> float:
        """
        Narrowband Detector threshold standard deviation.

        Value should be between 2 and 10.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.nb_detector_threshold = 3

        """
        val = self._get_property("NB Detector Threshold")
        return float(val)

    @nb_detector_threshold.setter
    @min_aedt_version("2025.2")
    def nb_detector_threshold(self, value: float) -> None:
        self._set_property("NB Detector Threshold", f"{value}")

    class AlgorithmOption(Enum):
        FFT = "FFT"
        FOURIER_TRANSFORM = "Fourier Transform"

    @property
    @min_aedt_version("2025.2")
    def algorithm(self) -> AlgorithmOption:
        """
        Algorithm used to transform the imported time domain spectrum.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.algorithm = waveform.AlgorithmOption.FFT

        """
        val = self._get_property("Algorithm")
        val = self.AlgorithmOption[val.upper()]
        return val

    @algorithm.setter
    @min_aedt_version("2025.2")
    def algorithm(self, value: AlgorithmOption) -> None:
        self._set_property("Algorithm", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def start_time(self) -> float:
        """
        Initial time of the imported spectrum.

        Value should be greater than 0.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.start_time = "1ns"

        """
        val = self._get_property("Start Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @start_time.setter
    @min_aedt_version("2025.2")
    def start_time(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Start Time", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def stop_time(self) -> float:
        """
        Final time of the imported time domain spectrum.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.stop_time = "10ns"

        """
        val = self._get_property("Stop Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @stop_time.setter
    @min_aedt_version("2025.2")
    def stop_time(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Stop Time", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def max_frequency(self) -> float:
        """
        Frequency cutoff of the imported time domain spectrum.

        Value should be between 1.0 and 100.0e9.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.max_frequency = "1GHz"

        """
        val = self._get_property("Max Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_frequency.setter
    @min_aedt_version("2025.2")
    def max_frequency(self, value: float | str) -> None:
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
    @min_aedt_version("2025.2")
    def window_type(self) -> WindowTypeOption:
        """
        Windowing scheme used for importing time domain spectrum.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.window_type = waveform.WindowTypeOption.KAISER

        """
        val = self._get_property("Window Type")
        val = self.WindowTypeOption[val.upper()]
        return val

    @window_type.setter
    @min_aedt_version("2025.2")
    def window_type(self, value: WindowTypeOption) -> None:
        self._set_property("Window Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def kaiser_parameter(self) -> float:
        """
        Shape factor applied to the transform.

        Value should be greater than 0.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.kaiser_parameter = 2.0

        """
        val = self._get_property("Kaiser Parameter")
        return float(val)

    @kaiser_parameter.setter
    @min_aedt_version("2025.2")
    def kaiser_parameter(self, value: float) -> None:
        self._set_property("Kaiser Parameter", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def adjust_coherent_gain(self) -> bool:
        """
        Shape factor applied to the transform.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.adjust_coherent_gain = True

        """
        val = self._get_property("Adjust Coherent Gain")
        return val == "true"

    @adjust_coherent_gain.setter
    @min_aedt_version("2025.2")
    def adjust_coherent_gain(self, value: bool) -> None:
        self._set_property("Adjust Coherent Gain", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def data_rate(self) -> float:
        """
        Maximum data rate: helps determine shape of spectral profile.

        Value should be greater than 1.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.data_rate = "1Mbps"

        """
        val = self._get_property("Data Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return float(val)

    @data_rate.setter
    @min_aedt_version("2025.2")
    def data_rate(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Data Rate")
        self._set_property("Data Rate", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def num_of_bits(self) -> int:
        """
        Length of the Pseudo Random Binary Sequence.

        Value should be between 1 and 1000.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.num_of_bits = 31

        """
        val = self._get_property("Num of Bits")
        return int(val)

    @num_of_bits.setter
    @min_aedt_version("2025.2")
    def num_of_bits(self, value: int) -> None:
        self._set_property("Num of Bits", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def use_envelope(self) -> bool:
        """
        Model the waveform as a worst case envelope.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.use_envelope = True

        """
        val = self._get_property("Use Envelope")
        return val == "true"

    @use_envelope.setter
    @min_aedt_version("2025.2")
    def use_envelope(self, value: bool) -> None:
        self._set_property("Use Envelope", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def min_ptsnull(self) -> int:
        """
        Minimum number of points to use between each null frequency.

        Value should be between 2 and 50.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveform = emitter.get_waveforms()[0]
        >>> waveform.min_ptsnull = 4

        """
        val = self._get_property("Min Pts/Null")
        return int(val)

    @min_ptsnull.setter
    @min_aedt_version("2025.2")
    def min_ptsnull(self, value: int) -> None:
        self._set_property("Min Pts/Null", f"{value}")
