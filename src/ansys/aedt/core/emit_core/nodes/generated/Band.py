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

class Band(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, 'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"enabled= + {value}"])

    @property
    def port(self):
        """Port
        Radio Port associated with this Band

                """
        val = self._get_property("Port")
        return val # type: ignore

    @port.setter
    def port(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Port={value}"])

    @property
    def use_dd_1494_mode(self) -> bool:
        """Use DD-1494 Mode
        Uses DD-1494 parameters to define the Tx/Rx spectrum

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use DD-1494 Mode")
        return val # type: ignore

    @use_dd_1494_mode.setter
    def use_dd_1494_mode(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Use DD-1494 Mode={value}"])

    @property
    def use_emission_designator(self) -> bool:
        """Use Emission Designator
        Uses the Emission Designator to define the bandwidth and modulation

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Emission Designator")
        return val # type: ignore

    @use_emission_designator.setter
    def use_emission_designator(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Use Emission Designator={value}"])

    @property
    def emission_designator(self) -> str:
        """Emission Designator
        Enter the Emission Designator to define the bandwidth and modulation

                """
        val = self._get_property("Emission Designator")
        return val # type: ignore

    @emission_designator.setter
    def emission_designator(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Emission Designator={value}"])

    @property
    def emission_designator_ch_bw(self) -> float:
        """Emission Designator Ch. BW
        Channel Bandwidth based off the emission designator

                """
        val = self._get_property("Emission Designator Ch. BW")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def emit_modulation_type(self) -> str:
        """EMIT Modulation Type
        Modulation based off the emission designator

                """
        val = self._get_property("EMIT Modulation Type")
        return val # type: ignore

    @property
    def override_emission_designator_bw(self) -> bool:
        """Override Emission Designator BW
        Enables the 3 dB channel bandwidth to equal a value < emission
         designator bandwidth

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Override Emission Designator BW")
        return val # type: ignore

    @override_emission_designator_bw.setter
    def override_emission_designator_bw(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Override Emission Designator BW={value}"])

    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth
        Channel Bandwidth

        Value should be greater than 1.
        """
        val = self._get_property("Channel Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @channel_bandwidth.setter
    def channel_bandwidth(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Channel Bandwidth={value}"])

    class ModulationOption(Enum):
        GENERIC = "Generic" # eslint-disable-line no-eval
        AM = "AM" # eslint-disable-line no-eval
        LSB = "LSB" # eslint-disable-line no-eval
        USB = "USB" # eslint-disable-line no-eval
        FM = "FM" # eslint-disable-line no-eval
        FSK = "FSK" # eslint-disable-line no-eval
        MSK = "MSK" # eslint-disable-line no-eval
        PSK = "PSK" # eslint-disable-line no-eval
        QAM = "QAM" # eslint-disable-line no-eval
        APSK = "APSK" # eslint-disable-line no-eval
        RADAR = "Radar" # eslint-disable-line no-eval

    @property
    def modulation(self) -> ModulationOption:
        """Modulation
        Modulation used for the transmitted/received signal

                """
        val = self._get_property("Modulation")
        val = self.ModulationOption[val]
        return val # type: ignore

    @modulation.setter
    def modulation(self, value: ModulationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Modulation={value.value}"])

    @property
    def max_modulating_freq(self) -> float:
        """Max Modulating Freq.
        Maximum modulating frequency: helps determine spectral profile

        Value should be greater than 1.
        """
        val = self._get_property("Max Modulating Freq.")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @max_modulating_freq.setter
    def max_modulating_freq(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Max Modulating Freq.={value}"])

    @property
    def modulation_index(self) -> float:
        """Modulation Index
        AM modulation index: helps determine spectral profile

        Value should be between 0.01 and 1.
        """
        val = self._get_property("Modulation Index")
        return val # type: ignore

    @modulation_index.setter
    def modulation_index(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Modulation Index={value}"])

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        Frequency deviation: helps determine spectral profile

        Value should be greater than 1.
        """
        val = self._get_property("Freq. Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @freq_deviation.setter
    def freq_deviation(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Freq. Deviation={value}"])

    @property
    def bit_rate(self) -> float:
        """Bit Rate
        Maximum bit rate: helps determine width of spectral profile

        Value should be greater than 1.
        """
        val = self._get_property("Bit Rate")
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return val # type: ignore

    @bit_rate.setter
    def bit_rate(self, value : float|str):
        value = self._convert_to_internal_units(value, "Data Rate")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Bit Rate={value}"])

    @property
    def sidelobes(self) -> int:
        """Sidelobes
        Number of sidelobes in spectral profile

        Value should be greater than 0.
        """
        val = self._get_property("Sidelobes")
        return val # type: ignore

    @sidelobes.setter
    def sidelobes(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Sidelobes={value}"])

    @property
    def freq_deviation_(self) -> float:
        """Freq. Deviation 
        FSK frequency deviation: helps determine spectral profile

        Value should be greater than 1.
        """
        val = self._get_property("Freq. Deviation ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @freq_deviation_.setter
    def freq_deviation_(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Freq. Deviation ={value}"])

    class PSKTypeOption(Enum):
        BPSK = "BPSK" # eslint-disable-line no-eval
        QPSK = "QPSK" # eslint-disable-line no-eval
        PSK_8 = "PSK-8" # eslint-disable-line no-eval
        PSK_16 = "PSK-16" # eslint-disable-line no-eval
        PSK_32 = "PSK-32" # eslint-disable-line no-eval
        PSK_64 = "PSK-64" # eslint-disable-line no-eval

    @property
    def psk_type(self) -> PSKTypeOption:
        """PSK Type
        PSK modulation order: helps determine spectral profile

                """
        val = self._get_property("PSK Type")
        val = self.PSKTypeOption[val]
        return val # type: ignore

    @psk_type.setter
    def psk_type(self, value: PSKTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"PSK Type={value.value}"])

    class FSKTypeOption(Enum):
        FSK_2 = "FSK-2" # eslint-disable-line no-eval
        FSK_4 = "FSK-4" # eslint-disable-line no-eval
        FSK_8 = "FSK-8" # eslint-disable-line no-eval

    @property
    def fsk_type(self) -> FSKTypeOption:
        """FSK Type
        FSK modulation order: helps determine spectral profile

                """
        val = self._get_property("FSK Type")
        val = self.FSKTypeOption[val]
        return val # type: ignore

    @fsk_type.setter
    def fsk_type(self, value: FSKTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"FSK Type={value.value}"])

    class QAMTypeOption(Enum):
        QAM_4 = "QAM-4" # eslint-disable-line no-eval
        QAM_16 = "QAM-16" # eslint-disable-line no-eval
        QAM_64 = "QAM-64" # eslint-disable-line no-eval
        QAM_256 = "QAM-256" # eslint-disable-line no-eval
        QAM_1024 = "QAM-1024" # eslint-disable-line no-eval

    @property
    def qam_type(self) -> QAMTypeOption:
        """QAM Type
        QAM modulation order: helps determine spectral profile

                """
        val = self._get_property("QAM Type")
        val = self.QAMTypeOption[val]
        return val # type: ignore

    @qam_type.setter
    def qam_type(self, value: QAMTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"QAM Type={value.value}"])

    class APSKTypeOption(Enum):
        APSK_4 = "APSK-4" # eslint-disable-line no-eval
        APSK_16 = "APSK-16" # eslint-disable-line no-eval
        APSK_64 = "APSK-64" # eslint-disable-line no-eval
        APSK_256 = "APSK-256" # eslint-disable-line no-eval
        APSK_1024 = "APSK-1024" # eslint-disable-line no-eval

    @property
    def apsk_type(self) -> APSKTypeOption:
        """APSK Type
        APSK modulation order: helps determine spectral profile

                """
        val = self._get_property("APSK Type")
        val = self.APSKTypeOption[val]
        return val # type: ignore

    @apsk_type.setter
    def apsk_type(self, value: APSKTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"APSK Type={value.value}"])

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        First frequency for this band

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @start_frequency.setter
    def start_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Start Frequency={value}"])

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        Last frequency for this band

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @stop_frequency.setter
    def stop_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Stop Frequency={value}"])

    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        Spacing between channels within this band

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Channel Spacing")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @channel_spacing.setter
    def channel_spacing(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Channel Spacing={value}"])

    @property
    def tx_offset(self) -> float:
        """Tx Offset
        Frequency offset between Tx and Rx channels

        Value should be less than 1e+11.
        """
        val = self._get_property("Tx Offset")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @tx_offset.setter
    def tx_offset(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Tx Offset={value}"])

    class RadarTypeOption(Enum):
        CW = "CW" # eslint-disable-line no-eval
        FM_CW = "FM-CW" # eslint-disable-line no-eval
        FM_PULSE = "FM Pulse" # eslint-disable-line no-eval
        NON_FM_PULSE = "Non-FM Pulse" # eslint-disable-line no-eval
        PHASE_CODED = "Phase Coded" # eslint-disable-line no-eval

    @property
    def radar_type(self) -> RadarTypeOption:
        """Radar Type
        Radar type: helps determine spectral profile

                """
        val = self._get_property("Radar Type")
        val = self.RadarTypeOption[val]
        return val # type: ignore

    @radar_type.setter
    def radar_type(self, value: RadarTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Radar Type={value.value}"])

    @property
    def hopping_radar(self) -> bool:
        """Hopping Radar
        True for hopping radars; false otherwise

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Hopping Radar")
        return val # type: ignore

    @hopping_radar.setter
    def hopping_radar(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Hopping Radar={value}"])

    @property
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement
        Procurement date: helps determine spectral profile, particularly the
         roll-off

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Post October 2020 Procurement")
        return val # type: ignore

    @post_october_2020_procurement.setter
    def post_october_2020_procurement(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Post October 2020 Procurement={value}"])

    @property
    def hop_range_min_freq(self) -> float:
        """Hop Range Min Freq
        Sets the minimum frequency of the hopping range

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Hop Range Min Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @hop_range_min_freq.setter
    def hop_range_min_freq(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Hop Range Min Freq={value}"])

    @property
    def hop_range_max_freq(self) -> float:
        """Hop Range Max Freq
        Sets the maximum frequency of the hopping range

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Hop Range Max Freq")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @hop_range_max_freq.setter
    def hop_range_max_freq(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Hop Range Max Freq={value}"])

    @property
    def pulse_duration(self) -> float:
        """Pulse Duration
        Pulse duration

        Value should be greater than 0.
        """
        val = self._get_property("Pulse Duration")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @pulse_duration.setter
    def pulse_duration(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Pulse Duration={value}"])

    @property
    def pulse_rise_time(self) -> float:
        """Pulse Rise Time
        Pulse rise time

        Value should be greater than 0.
        """
        val = self._get_property("Pulse Rise Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @pulse_rise_time.setter
    def pulse_rise_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Pulse Rise Time={value}"])

    @property
    def pulse_fall_time(self) -> float:
        """Pulse Fall Time
        Pulse fall time

        Value should be greater than 0.
        """
        val = self._get_property("Pulse Fall Time")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @pulse_fall_time.setter
    def pulse_fall_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Pulse Fall Time={value}"])

    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse Repetition Rate
        Pulse repetition rate [pulses/sec]

        Value should be greater than 1.
        """
        val = self._get_property("Pulse Repetition Rate")
        return val # type: ignore

    @pulse_repetition_rate.setter
    def pulse_repetition_rate(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Pulse Repetition Rate={value}"])

    @property
    def number_of_chips(self) -> float:
        """Number of Chips
        Total number of chips (subpulses) contained in the pulse

        Value should be greater than 1.
        """
        val = self._get_property("Number of Chips")
        return val # type: ignore

    @number_of_chips.setter
    def number_of_chips(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Number of Chips={value}"])

    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse Compression Ratio
        Pulse compression ratio

        Value should be greater than 1.
        """
        val = self._get_property("Pulse Compression Ratio")
        return val # type: ignore

    @pulse_compression_ratio.setter
    def pulse_compression_ratio(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Pulse Compression Ratio={value}"])

    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp Period
        FM Chirp period for the FM/CW radar

        Value should be greater than 0.
        """
        val = self._get_property("FM Chirp Period")
        val = self._convert_from_internal_units(float(val), "Time")
        return val # type: ignore

    @fm_chirp_period.setter
    def fm_chirp_period(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"FM Chirp Period={value}"])

    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation
        Total frequency deviation for the carrier frequency for the FM/CW radar

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("FM Freq Deviation")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @fm_freq_deviation.setter
    def fm_freq_deviation(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"FM Freq Deviation={value}"])

    @property
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth
        Bandwidth of freq deviation for FM modulated pulsed waveform (total freq
         shift during pulse duration)

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("FM Freq Dev Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @fm_freq_dev_bandwidth.setter
    def fm_freq_dev_bandwidth(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"FM Freq Dev Bandwidth={value}"])

