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


class Band(EmitNode):
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

    @property
    def use_dd_1494_mode(self) -> bool:
        """Uses DD-1494 parameters to define the Tx/Rx spectrum.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use DD-1494 Mode")
        return val == "true"

    @use_dd_1494_mode.setter
    def use_dd_1494_mode(self, value: bool):
        self._set_property("Use DD-1494 Mode", f"{str(value).lower()}")

    @property
    def use_emission_designator(self) -> bool:
        """Use Emission Designator.

        Uses the Emission Designator to define the bandwidth and modulation.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Emission Designator")
        return val == "true"

    @use_emission_designator.setter
    def use_emission_designator(self, value: bool):
        self._set_property("Use Emission Designator", f"{str(value).lower()}")

    @property
    def emission_designator(self) -> str:
        """Emission Designator.

        Enter the Emission Designator to define the bandwidth and modulation.
        """
        val = self._get_property("Emission Designator")
        return val

    @emission_designator.setter
    def emission_designator(self, value: str):
        self._set_property("Emission Designator", f"{value}")

    @property
    def emission_designator_ch_bw(self) -> float:
        """Channel Bandwidth based off the emission designator."""
        val = self._get_property("Emission Designator Ch. BW")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def emit_modulation_type(self) -> str:
        """Modulation based off the emission designator."""
        val = self._get_property("EMIT Modulation Type")
        return val

    @property
    def override_emission_designator_bw(self) -> bool:
        """Override Emission Designator BW.

        Enables the 3 dB channel bandwidth to equal a value < emission
        designator bandwidth.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Override Emission Designator BW")
        return val == "true"

    @override_emission_designator_bw.setter
    def override_emission_designator_bw(self, value: bool):
        self._set_property("Override Emission Designator BW", f"{str(value).lower()}")

    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth.

        Value should be greater than 1.
        """
        val = self._get_property("Channel Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @channel_bandwidth.setter
    def channel_bandwidth(self, value: float | str):
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
    def modulation(self) -> ModulationOption:
        """Modulation used for the transmitted/received signal."""
        val = self._get_property("Modulation")
        val = self.ModulationOption[val.upper()]
        return val

    @modulation.setter
    def modulation(self, value: ModulationOption):
        self._set_property("Modulation", f"{value.value}")

    @property
    def max_modulating_freq(self) -> float:
        """Maximum modulating frequency: helps determine spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Max Modulating Freq.")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_modulating_freq.setter
    def max_modulating_freq(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Modulating Freq.", f"{value}")

    @property
    def modulation_index(self) -> float:
        """AM modulation index: helps determine spectral profile.

        Value should be between 0.01 and 1.
        """
        val = self._get_property("Modulation Index")
        return float(val)

    @modulation_index.setter
    def modulation_index(self, value: float):
        self._set_property("Modulation Index", f"{value}")

    @property
    def bit_rate(self) -> float:
        """Maximum bit rate: helps determine width of spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Bit Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return float(val)

    @bit_rate.setter
    def bit_rate(self, value: float | str):
        value = self._convert_to_internal_units(value, "Data Rate")
        self._set_property("Bit Rate", f"{value}")

    @property
    def sidelobes(self) -> int:
        """Number of sidelobes in spectral profile.

        Value should be greater than 0.
        """
        val = self._get_property("Sidelobes")
        return int(val)

    @sidelobes.setter
    def sidelobes(self, value: int):
        self._set_property("Sidelobes", f"{value}")

    @property
    def freq_deviation(self) -> float:
        """FM/FSK frequency deviation: helps determine spectral profile.

        Value should be greater than 1.
        """
        val = self._get_property("Freq. Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @freq_deviation.setter
    def freq_deviation(self, value: float | str):
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
        PSK_8 = "PSK-8"
        PSK_16 = "PSK-16"
        PSK_32 = "PSK-32"
        PSK_64 = "PSK-64"

    @property
    def psk_type(self) -> PSKTypeOption:
        """PSK modulation order: helps determine spectral profile."""
        val = self._get_property("PSK Type")
        val = self.PSKTypeOption[val.upper()]
        return val

    @psk_type.setter
    def psk_type(self, value: PSKTypeOption):
        self._set_property("PSK Type", f"{value.value}")

    class FSKTypeOption(Enum):
        FSK_2 = "FSK-2"
        FSK_4 = "FSK-4"
        FSK_8 = "FSK-8"

    @property
    def fsk_type(self) -> FSKTypeOption:
        """FSK modulation order: helps determine spectral profile."""
        val = self._get_property("FSK Type")
        val = self.FSKTypeOption[val.upper()]
        return val

    @fsk_type.setter
    def fsk_type(self, value: FSKTypeOption):
        self._set_property("FSK Type", f"{value.value}")

    class QAMTypeOption(Enum):
        QAM_4 = "QAM-4"
        QAM_16 = "QAM-16"
        QAM_64 = "QAM-64"
        QAM_256 = "QAM-256"
        QAM_1024 = "QAM-1024"

    @property
    def qam_type(self) -> QAMTypeOption:
        """QAM modulation order: helps determine spectral profile."""
        val = self._get_property("QAM Type")
        val = self.QAMTypeOption[val.upper()]
        return val

    @qam_type.setter
    def qam_type(self, value: QAMTypeOption):
        self._set_property("QAM Type", f"{value.value}")

    class APSKTypeOption(Enum):
        APSK_4 = "APSK-4"
        APSK_16 = "APSK-16"
        APSK_64 = "APSK-64"
        APSK_256 = "APSK-256"
        APSK_1024 = "APSK-1024"

    @property
    def apsk_type(self) -> APSKTypeOption:
        """APSK modulation order: helps determine spectral profile."""
        val = self._get_property("APSK Type")
        val = self.APSKTypeOption[val.upper()]
        return val

    @apsk_type.setter
    def apsk_type(self, value: APSKTypeOption):
        self._set_property("APSK Type", f"{value.value}")

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
    def tx_offset(self) -> float:
        """Frequency offset between Tx and Rx channels.

        Value should be less than 100e9.
        """
        val = self._get_property("Tx Offset")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @tx_offset.setter
    def tx_offset(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Tx Offset", f"{value}")

    class RadarTypeOption(Enum):
        CW = "CW"
        FM_CW = "FM-CW"
        FM_PULSE = "FM Pulse"
        NON_FM_PULSE = "Non-FM Pulse"
        PHASE_CODED = "Phase Coded"

    @property
    def radar_type(self) -> RadarTypeOption:
        """Radar type: helps determine spectral profile."""
        val = self._get_property("Radar Type")
        val = self.RadarTypeOption[val.upper()]
        return val

    @radar_type.setter
    def radar_type(self, value: RadarTypeOption):
        self._set_property("Radar Type", f"{value.value}")

    @property
    def hopping_radar(self) -> bool:
        """True for hopping radars; false otherwise.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Hopping Radar")
        return val == "true"

    @hopping_radar.setter
    def hopping_radar(self, value: bool):
        self._set_property("Hopping Radar", f"{str(value).lower()}")

    @property
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement.

        Procurement date: helps determine spectral profile, particularly the
        roll-off.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Post October 2020 Procurement")
        return val == "true"

    @post_october_2020_procurement.setter
    def post_october_2020_procurement(self, value: bool):
        self._set_property("Post October 2020 Procurement", f"{str(value).lower()}")

    @property
    def hop_range_min_freq(self) -> float:
        """Sets the minimum frequency of the hopping range.

        Value should be between 1.0 and 100.0e9.
        """
        val = self._get_property("Hop Range Min Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @hop_range_min_freq.setter
    def hop_range_min_freq(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Hop Range Min Freq", f"{value}")

    @property
    def hop_range_max_freq(self) -> float:
        """Sets the maximum frequency of the hopping range.

        Value should be between 1.0 and 100.0e9.
        """
        val = self._get_property("Hop Range Max Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @hop_range_max_freq.setter
    def hop_range_max_freq(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Hop Range Max Freq", f"{value}")

    @property
    def pulse_duration(self) -> float:
        """Pulse duration.

        Value should be greater than 0.0.
        """
        val = self._get_property("Pulse Duration")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @pulse_duration.setter
    def pulse_duration(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Pulse Duration", f"{value}")

    @property
    def pulse_rise_time(self) -> float:
        """Pulse rise time.

        Value should be greater than 0.0.
        """
        val = self._get_property("Pulse Rise Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @pulse_rise_time.setter
    def pulse_rise_time(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Pulse Rise Time", f"{value}")

    @property
    def pulse_fall_time(self) -> float:
        """Pulse fall time.

        Value should be greater than 0.0.
        """
        val = self._get_property("Pulse Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @pulse_fall_time.setter
    def pulse_fall_time(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("Pulse Fall Time", f"{value}")

    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse repetition rate [pulses/sec].

        Value should be greater than 1.0.
        """
        val = self._get_property("Pulse Repetition Rate")
        return float(val)

    @pulse_repetition_rate.setter
    def pulse_repetition_rate(self, value: float):
        self._set_property("Pulse Repetition Rate", f"{value}")

    @property
    def number_of_chips(self) -> float:
        """Total number of chips (subpulses) contained in the pulse.

        Value should be greater than 1.0.
        """
        val = self._get_property("Number of Chips")
        return float(val)

    @number_of_chips.setter
    def number_of_chips(self, value: float):
        self._set_property("Number of Chips", f"{value}")

    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse compression ratio.

        Value should be greater than 1.0.
        """
        val = self._get_property("Pulse Compression Ratio")
        return float(val)

    @pulse_compression_ratio.setter
    def pulse_compression_ratio(self, value: float):
        self._set_property("Pulse Compression Ratio", f"{value}")

    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp period for the FM/CW radar.

        Value should be greater than 0.0.
        """
        val = self._get_property("FM Chirp Period")
        val = self._convert_from_internal_units(float(val), "Time")
        return float(val)

    @fm_chirp_period.setter
    def fm_chirp_period(self, value: float | str):
        value = self._convert_to_internal_units(value, "Time")
        self._set_property("FM Chirp Period", f"{value}")

    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation.

        Total frequency deviation for the carrier frequency for the FM/CW radar.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("FM Freq Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @fm_freq_deviation.setter
    def fm_freq_deviation(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("FM Freq Deviation", f"{value}")

    @property
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
    def fm_freq_dev_bandwidth(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("FM Freq Dev Bandwidth", f"{value}")
