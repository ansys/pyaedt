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


class Band(EmitNode):
    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node."""
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = ""):
        """Duplicate this node"""
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node"""
        self._delete()

    @min_aedt_version("2025.2")
    def import_rx_measurement(self, file_name: str):
        """Import a Measurement from a File..."""
        return self._import(file_name, "RxMeasurement")

    @min_aedt_version("2025.2")
    def import_tx_measurement(self, file_name: str):
        """Import a Measurement from a File..."""
        return self._import(file_name, "TxMeasurement")

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._get_property("Enabled") == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def use_dd_1494_mode(self) -> bool:
        """Uses DD-1494 parameters to define the Tx/Rx spectrum.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use DD-1494 Mode")
        return val == "true"

    @use_dd_1494_mode.setter
    @min_aedt_version("2025.2")
    def use_dd_1494_mode(self, value: bool) -> None:
        self._set_property("Use DD-1494 Mode", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def use_emission_designator(self) -> bool:
        """Use Emission Designator.

        Uses the Emission Designator to define the bandwidth and modulation.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Emission Designator")
        return val == "true"

    @use_emission_designator.setter
    @min_aedt_version("2025.2")
    def use_emission_designator(self, value: bool) -> None:
        self._set_property("Use Emission Designator", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def emission_designator(self) -> str:
        """Emission Designator.

        Enter the Emission Designator to define the bandwidth and modulation.
        """
        val = self._get_property("Emission Designator")
        return val

    @emission_designator.setter
    @min_aedt_version("2025.2")
    def emission_designator(self, value: str) -> None:
        self._set_property("Emission Designator", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def emission_designator_ch_bw(self) -> float:
        """Channel Bandwidth based off the emission designator."""
        val = self._get_property("Emission Designator Ch. BW")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    @min_aedt_version("2025.2")
    def emit_modulation_type(self) -> str:
        """Modulation based off the emission designator."""
        val = self._get_property("EMIT Modulation Type")
        return val

    @property
    @min_aedt_version("2025.2")
    def override_emission_designator_bw(self) -> bool:
        """Override Emission Designator BW.

        Enables the 3 dB channel bandwidth to equal a value < emission
        designator bandwidth.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Override Emission Designator BW")
        return val == "true"

    @override_emission_designator_bw.setter
    @min_aedt_version("2025.2")
    def override_emission_designator_bw(self, value: bool) -> None:
        self._set_property("Override Emission Designator BW", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth.

        Value should be greater than 1.
        """
        val = self._get_property("Channel Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @channel_bandwidth.setter
    @min_aedt_version("2025.2")
    def channel_bandwidth(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Channel Bandwidth", f"{value}")

    class ModulationOption(Enum):
        GENERIC = "Generic"
        AM = "AM"
        LSB = "LSB"
        USB = "USB"
        FM = "FM"
        FSK = "FSK"
        MSK = "MSK"
        PSK = "PSK"
        QAM = "QAM"
        APSK = "APSK"
        RADAR = "Radar"

    @property
    @min_aedt_version("2025.2")
    def modulation(self) -> ModulationOption:
        """Modulation used for the transmitted/received signal."""
        val = self._get_property("Modulation")
        val = self.ModulationOption[val.upper()]
        return val

    @modulation.setter
    @min_aedt_version("2025.2")
    def modulation(self, value: ModulationOption) -> None:
        self._set_property("Modulation", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def max_modulating_freq(self) -> float:
        """Maximum modulating frequency: helps determine spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Max Modulating Freq.")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_modulating_freq.setter
    @min_aedt_version("2025.2")
    def max_modulating_freq(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Modulating Freq.", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def modulation_index(self) -> float:
        """AM modulation index: helps determine spectral profile.

        Value should be between 0.01 and 1.
        """
        val = self._get_property("Modulation Index")
        return float(val)

    @modulation_index.setter
    @min_aedt_version("2025.2")
    def modulation_index(self, value: float) -> None:
        self._set_property("Modulation Index", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def bit_rate(self) -> float:
        """Maximum bit rate: helps determine width of spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Bit Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return float(val)

    @bit_rate.setter
    @min_aedt_version("2025.2")
    def bit_rate(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Data Rate")
        self._set_property("Bit Rate", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def sidelobes(self) -> int:
        """Number of sidelobes in spectral profile.

        Value should be greater than 0.
        """
        val = self._get_property("Sidelobes")
        return int(val)

    @sidelobes.setter
    @min_aedt_version("2025.2")
    def sidelobes(self, value: int) -> None:
        self._set_property("Sidelobes", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def freq_deviation(self) -> float:
        """FM/FSK frequency deviation: helps determine spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Freq. Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @freq_deviation.setter
    @min_aedt_version("2025.2")
    def freq_deviation(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        if int(self._emit_obj.aedt_version_id[-3:]) < 261:
            if self.modulation == self.ModulationOption.FM:
                self._set_property("FMFreqDev", f"{value}")
            else:
                self._set_property("FSKFreqDev", f"{value}")
        else:
            self._set_property("Freq. Deviation", f"{value}")

    class PSKTypeOption(Enum):
        BPSK = "BPSK"
        QPSK = "QPSK"
        PSK_8 = "8-PSK"
        PSK_16 = "16-PSK"
        PSK_32 = "32-PSK"
        PSK_64 = "64-PSK"

    @property
    @min_aedt_version("2025.2")
    def psk_type(self) -> PSKTypeOption:
        """PSK modulation order: helps determine spectral profile."""
        val = self._get_property("PSK Type")
        val = self.PSKTypeOption[val.upper()]
        return val

    @psk_type.setter
    @min_aedt_version("2025.2")
    def psk_type(self, value: PSKTypeOption) -> None:
        self._set_property("PSK Type", f"{value.value}")

    class FSKTypeOption(Enum):
        FSK_2 = "2-FSK"
        FSK_4 = "4-FSK"
        FSK_8 = "8-FSK"

    @property
    @min_aedt_version("2025.2")
    def fsk_type(self) -> FSKTypeOption:
        """FSK modulation order: helps determine spectral profile."""
        val = self._get_property("FSK Type")
        val = self.FSKTypeOption[val.upper()]
        return val

    @fsk_type.setter
    @min_aedt_version("2025.2")
    def fsk_type(self, value: FSKTypeOption) -> None:
        self._set_property("FSK Type", f"{value.value}")

    class QAMTypeOption(Enum):
        QAM_4 = "4-QAM"
        QAM_16 = "16-QAM"
        QAM_64 = "64-QAM"
        QAM_256 = "256-QAM"
        QAM_1024 = "1024-QAM"

    @property
    @min_aedt_version("2025.2")
    def qam_type(self) -> QAMTypeOption:
        """QAM modulation order: helps determine spectral profile."""
        val = self._get_property("QAM Type")
        val = self.QAMTypeOption[val.upper()]
        return val

    @qam_type.setter
    @min_aedt_version("2025.2")
    def qam_type(self, value: QAMTypeOption) -> None:
        self._set_property("QAM Type", f"{value.value}")

    class APSKTypeOption(Enum):
        APSK_4 = "4-APSK"
        APSK_16 = "16-APSK"
        APSK_64 = "64-APSK"
        APSK_256 = "256-APSK"
        APSK_1024 = "1024-APSK"

    @property
    @min_aedt_version("2025.2")
    def apsk_type(self) -> APSKTypeOption:
        """APSK modulation order: helps determine spectral profile."""
        val = self._get_property("APSK Type")
        val = self.APSKTypeOption[val.upper()]
        return val

    @apsk_type.setter
    @min_aedt_version("2025.2")
    def apsk_type(self, value: APSKTypeOption) -> None:
        self._set_property("APSK Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def start_frequency(self) -> float:
        """First frequency for this band.

        Value should be between 1 and 100e9.
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
    def stop_frequency(self) -> float:
        """Last frequency for this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @stop_frequency.setter
    @min_aedt_version("2025.2")
    def stop_frequency(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Stop Frequency", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def channel_spacing(self) -> float:
        """Spacing between channels within this band.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Channel Spacing")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @channel_spacing.setter
    @min_aedt_version("2025.2")
    def channel_spacing(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Channel Spacing", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def tx_offset(self) -> float:
        """Frequency offset between Tx and Rx channels.

        Value should be less than 100e9.
        """
        val = self._get_property("Tx Offset")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @tx_offset.setter
    @min_aedt_version("2025.2")
    def tx_offset(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Tx Offset", f"{value}")

    class RadarTypeOption(Enum):
        CW = "CW"
        FM_CW = "FM-CW"
        FM_PULSE = "FM Pulse"
        NON_FM_PULSE = "Non-FM Pulse"
        PHASE_CODED = "Phase Coded"

    @property
    @min_aedt_version("2025.2")
    def radar_type(self) -> RadarTypeOption:
        """Radar type: helps determine spectral profile."""
        val = self._get_property("Radar Type")
        val = self.RadarTypeOption[val.upper()]
        return val

    @radar_type.setter
    @min_aedt_version("2025.2")
    def radar_type(self, value: RadarTypeOption) -> None:
        self._set_property("Radar Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def hopping_radar(self) -> bool:
        """True for hopping radars; false otherwise.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Hopping Radar")
        return val == "true"

    @hopping_radar.setter
    @min_aedt_version("2025.2")
    def hopping_radar(self, value: bool) -> None:
        self._set_property("Hopping Radar", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement.

        Procurement date: helps determine spectral profile, particularly the
        roll-off.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Post October 2020 Procurement")
        return val == "true"

    @post_october_2020_procurement.setter
    @min_aedt_version("2025.2")
    def post_october_2020_procurement(self, value: bool) -> None:
        self._set_property("Post October 2020 Procurement", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def hop_range_min_freq(self) -> float:
        """Sets the minimum frequency of the hopping range.

        Value should be between 1.0 and 100.0e9.
        """
        val = self._get_property("Hop Range Min Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @hop_range_min_freq.setter
    @min_aedt_version("2025.2")
    def hop_range_min_freq(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Hop Range Min Freq", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def hop_range_max_freq(self) -> float:
        """Sets the maximum frequency of the hopping range.

        Value should be between 1.0 and 100.0e9.
        """
        val = self._get_property("Hop Range Max Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @hop_range_max_freq.setter
    @min_aedt_version("2025.2")
    def hop_range_max_freq(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Hop Range Max Freq", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def pulse_duration(self) -> float:
        """Pulse duration.

        Value should be greater than 0.0.
        """
        val = self._get_property("Pulse Duration")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @pulse_duration.setter
    @min_aedt_version("2025.2")
    def pulse_duration(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Pulse Duration", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def pulse_rise_time(self) -> float:
        """Pulse rise time.

        Value should be greater than 0.0.
        """
        val = self._get_property("Pulse Rise Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @pulse_rise_time.setter
    @min_aedt_version("2025.2")
    def pulse_rise_time(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Pulse Rise Time", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def pulse_fall_time(self) -> float:
        """Pulse fall time.

        Value should be greater than 0.0.
        """
        val = self._get_property("Pulse Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @pulse_fall_time.setter
    @min_aedt_version("2025.2")
    def pulse_fall_time(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Pulse Fall Time", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def pulse_repetition_rate(self) -> float:
        """Pulse repetition rate [pulses/sec].

        Value should be greater than 1.0.
        """
        val = self._get_property("Pulse Repetition Rate")
        return float(val)

    @pulse_repetition_rate.setter
    @min_aedt_version("2025.2")
    def pulse_repetition_rate(self, value: float) -> None:
        self._set_property("Pulse Repetition Rate", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def number_of_chips(self) -> float:
        """Total number of chips (subpulses) contained in the pulse.

        Value should be greater than 1.0.
        """
        val = self._get_property("Number of Chips")
        return float(val)

    @number_of_chips.setter
    @min_aedt_version("2025.2")
    def number_of_chips(self, value: float) -> None:
        self._set_property("Number of Chips", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def pulse_compression_ratio(self) -> float:
        """Pulse compression ratio.

        Value should be greater than 1.0.
        """
        val = self._get_property("Pulse Compression Ratio")
        return float(val)

    @pulse_compression_ratio.setter
    @min_aedt_version("2025.2")
    def pulse_compression_ratio(self, value: float) -> None:
        self._set_property("Pulse Compression Ratio", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def fm_chirp_period(self) -> float:
        """FM Chirp period for the FM/CW radar.

        Value should be greater than 0.0.
        """
        val = self._get_property("FM Chirp Period")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @fm_chirp_period.setter
    @min_aedt_version("2025.2")
    def fm_chirp_period(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("FM Chirp Period", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation.

        Total frequency deviation for the carrier frequency for the FM/CW radar.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("FM Freq Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @fm_freq_deviation.setter
    @min_aedt_version("2025.2")
    def fm_freq_deviation(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("FM Freq Deviation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth.

        Bandwidth of freq deviation for FM modulated pulsed waveform (total freq
        shift during pulse duration).

        Value should be between 1 and 100e9.
        """
        val = self._get_property("FM Freq Dev Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @fm_freq_dev_bandwidth.setter
    @min_aedt_version("2025.2")
    def fm_freq_dev_bandwidth(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("FM Freq Dev Bandwidth", f"{value}")
