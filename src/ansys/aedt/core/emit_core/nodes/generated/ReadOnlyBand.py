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

class ReadOnlyBand(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def port(self):
        """Port
        "Radio Port associated with this Band."
        "        """
        val = self._get_property("Port")
        return val # type: ignore

    @property
    def use_dd_1494_mode(self) -> bool:
        """Use DD-1494 Mode
        "Uses DD-1494 parameters to define the Tx/Rx spectrum."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Use DD-1494 Mode")
        return val # type: ignore

    @property
    def use_emission_designator(self) -> bool:
        """Use Emission Designator
        "Uses the Emission Designator to define the bandwidth and modulation."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Use Emission Designator")
        return val # type: ignore

    @property
    def emission_designator(self) -> str:
        """Emission Designator
        "Enter the Emission Designator to define the bandwidth and modulation."
        "        """
        val = self._get_property("Emission Designator")
        return val # type: ignore

    @property
    def emission_designator_ch_bw(self) -> float:
        """Emission Designator Ch. BW
        "Channel Bandwidth based off the emission designator."
        "        """
        val = self._get_property("Emission Designator Ch. BW")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def emit_modulation_type(self) -> str:
        """EMIT Modulation Type
        "Modulation based off the emission designator."
        "        """
        val = self._get_property("EMIT Modulation Type")
        return val # type: ignore

    @property
    def override_emission_designator_bw(self) -> bool:
        """Override Emission Designator BW
        "Enables the 3 dB channel bandwidth to equal a value < emission designator bandwidth."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Override Emission Designator BW")
        return val # type: ignore

    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth
        "Channel Bandwidth."
        "Value should be greater than 1."
        """
        val = self._get_property("Channel Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

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
        """Modulation
        "Modulation used for the transmitted/received signal."
        "        """
        val = self._get_property("Modulation")
        val = self.ModulationOption[val]
        return val # type: ignore

    @property
    def max_modulating_freq(self) -> float:
        """Max Modulating Freq.
        "Maximum modulating frequency: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property("Max Modulating Freq.")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def modulation_index(self) -> float:
        """Modulation Index
        "AM modulation index: helps determine spectral profile."
        "Value should be between 0.01 and 1."
        """
        val = self._get_property("Modulation Index")
        return val # type: ignore

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property("Freq. Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def bit_rate(self) -> float:
        """Bit Rate
        "Maximum bit rate: helps determine width of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property("Bit Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return val # type: ignore

    @property
    def sidelobes(self) -> int:
        """Sidelobes
        "Number of sidelobes in spectral profile."
        "Value should be greater than 0."
        """
        val = self._get_property("Sidelobes")
        return val # type: ignore

    @property
    def freq_deviation_(self) -> float:
        """Freq. Deviation 
        "FSK frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property("Freq. Deviation ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    class PSKTypeOption(Enum):
        BPSK = "BPSK"
        QPSK = "QPSK"
        PSK_8 = "PSK-8"
        PSK_16 = "PSK-16"
        PSK_32 = "PSK-32"
        PSK_64 = "PSK-64"

    @property
    def psk_type(self) -> PSKTypeOption:
        """PSK Type
        "PSK modulation order: helps determine spectral profile."
        "        """
        val = self._get_property("PSK Type")
        val = self.PSKTypeOption[val]
        return val # type: ignore

    class FSKTypeOption(Enum):
        FSK_2 = "FSK-2"
        FSK_4 = "FSK-4"
        FSK_8 = "FSK-8"

    @property
    def fsk_type(self) -> FSKTypeOption:
        """FSK Type
        "FSK modulation order: helps determine spectral profile."
        "        """
        val = self._get_property("FSK Type")
        val = self.FSKTypeOption[val]
        return val # type: ignore

    class QAMTypeOption(Enum):
        QAM_4 = "QAM-4"
        QAM_16 = "QAM-16"
        QAM_64 = "QAM-64"
        QAM_256 = "QAM-256"
        QAM_1024 = "QAM-1024"

    @property
    def qam_type(self) -> QAMTypeOption:
        """QAM Type
        "QAM modulation order: helps determine spectral profile."
        "        """
        val = self._get_property("QAM Type")
        val = self.QAMTypeOption[val]
        return val # type: ignore

    class APSKTypeOption(Enum):
        APSK_4 = "APSK-4"
        APSK_16 = "APSK-16"
        APSK_64 = "APSK-64"
        APSK_256 = "APSK-256"
        APSK_1024 = "APSK-1024"

    @property
    def apsk_type(self) -> APSKTypeOption:
        """APSK Type
        "APSK modulation order: helps determine spectral profile."
        "        """
        val = self._get_property("APSK Type")
        val = self.APSKTypeOption[val]
        return val # type: ignore

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "First frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Last frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        "Spacing between channels within this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Channel Spacing")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def tx_offset(self) -> float:
        """Tx Offset
        "Frequency offset between Tx and Rx channels."
        "Value should be less than 1e+11."
        """
        val = self._get_property("Tx Offset")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    class RadarTypeOption(Enum):
        CW = "CW"
        FM_CW = "FM-CW"
        FM_PULSE = "FM Pulse"
        NON_FM_PULSE = "Non-FM Pulse"
        PHASE_CODED = "Phase Coded"

    @property
    def radar_type(self) -> RadarTypeOption:
        """Radar Type
        "Radar type: helps determine spectral profile."
        "        """
        val = self._get_property("Radar Type")
        val = self.RadarTypeOption[val]
        return val # type: ignore

    @property
    def hopping_radar(self) -> bool:
        """Hopping Radar
        "True for hopping radars; false otherwise."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Hopping Radar")
        return val # type: ignore

    @property
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement
        "Procurement date: helps determine spectral profile, particularly the roll-off."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Post October 2020 Procurement")
        return val # type: ignore

    @property
    def hop_range_min_freq(self) -> float:
        """Hop Range Min Freq
        "Sets the minimum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Hop Range Min Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def hop_range_max_freq(self) -> float:
        """Hop Range Max Freq
        "Sets the maximum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Hop Range Max Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def pulse_duration(self) -> float:
        """Pulse Duration
        "Pulse duration."
        "Value should be greater than 0."
        """
        val = self._get_property("Pulse Duration")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @property
    def pulse_rise_time(self) -> float:
        """Pulse Rise Time
        "Pulse rise time."
        "Value should be greater than 0."
        """
        val = self._get_property("Pulse Rise Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @property
    def pulse_fall_time(self) -> float:
        """Pulse Fall Time
        "Pulse fall time."
        "Value should be greater than 0."
        """
        val = self._get_property("Pulse Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse Repetition Rate
        "Pulse repetition rate [pulses/sec]."
        "Value should be greater than 1."
        """
        val = self._get_property("Pulse Repetition Rate")
        return val # type: ignore

    @property
    def number_of_chips(self) -> float:
        """Number of Chips
        "Total number of chips (subpulses) contained in the pulse."
        "Value should be greater than 1."
        """
        val = self._get_property("Number of Chips")
        return val # type: ignore

    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse Compression Ratio
        "Pulse compression ratio."
        "Value should be greater than 1."
        """
        val = self._get_property("Pulse Compression Ratio")
        return val # type: ignore

    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp Period
        "FM Chirp period for the FM/CW radar."
        "Value should be greater than 0."
        """
        val = self._get_property("FM Chirp Period")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation
        "Total frequency deviation for the carrier frequency for the FM/CW radar."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("FM Freq Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth
        "Bandwidth of freq deviation for FM modulated pulsed waveform (total freq shift during pulse duration)."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("FM Freq Dev Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

