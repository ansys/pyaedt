from ..EmitNode import *

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
        return self._oRevisionData.GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def port(self):
        """Port
        "Radio Port associated with this Band."
        "        """
        val = self._get_property('Port')
        return val

    @port.setter
    def port(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Port=' + value])

    @property
    def use_dd_1494_mode(self) -> bool:
        """Use DD-1494 Mode
        "Uses DD-1494 parameters to define the Tx/Rx spectrum."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use DD-1494 Mode')
        return val

    @use_dd_1494_mode.setter
    def use_dd_1494_mode(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Use DD-1494 Mode=' + value])

    @property
    def use_emission_designator(self) -> bool:
        """Use Emission Designator
        "Uses the Emission Designator to define the bandwidth and modulation."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Emission Designator')
        return val

    @use_emission_designator.setter
    def use_emission_designator(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Use Emission Designator=' + value])

    @property
    def emission_designator(self) -> str:
        """Emission Designator
        "Enter the Emission Designator to define the bandwidth and modulation."
        "        """
        val = self._get_property('Emission Designator')
        return val

    @emission_designator.setter
    def emission_designator(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Emission Designator=' + value])

    @property
    def emission_designator_ch_bw(self) -> float:
        """Emission Designator Ch. BW
        "Channel Bandwidth based off the emission designator."
        "        """
        val = self._get_property('Emission Designator Ch. BW')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def emit_modulation_type(self) -> str:
        """EMIT Modulation Type
        "Modulation based off the emission designator."
        "        """
        val = self._get_property('EMIT Modulation Type')
        return val

    @property
    def override_emission_designator_bw(self) -> bool:
        """Override Emission Designator BW
        "Enables the 3 dB channel bandwidth to equal a value < emission designator bandwidth."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Override Emission Designator BW')
        return val

    @override_emission_designator_bw.setter
    def override_emission_designator_bw(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Override Emission Designator BW=' + value])

    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth
        "Channel Bandwidth."
        "Value should be greater than 1."
        """
        val = self._get_property('Channel Bandwidth')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @channel_bandwidth.setter
    def channel_bandwidth(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Channel Bandwidth=' + f"{value}"])

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
        val = self._get_property('Modulation')
        val = self.ModulationOption[val]
        return val

    @modulation.setter
    def modulation(self, value: ModulationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Modulation=' + value.value])

    @property
    def max_modulating_freq(self) -> float:
        """Max Modulating Freq.
        "Maximum modulating frequency: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Max Modulating Freq.')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @max_modulating_freq.setter
    def max_modulating_freq(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Max Modulating Freq.=' + f"{value}"])

    @property
    def modulation_index(self) -> float:
        """Modulation Index
        "AM modulation index: helps determine spectral profile."
        "Value should be between 0.01 and 1."
        """
        val = self._get_property('Modulation Index')
        return val

    @modulation_index.setter
    def modulation_index(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Modulation Index=' + value])

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Freq. Deviation')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @freq_deviation.setter
    def freq_deviation(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Freq. Deviation=' + f"{value}"])

    @property
    def bit_rate(self) -> float:
        """Bit Rate
        "Maximum bit rate: helps determine width of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Bit Rate')
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return val

    @bit_rate.setter
    def bit_rate(self, value : float|str):
        value = self._convert_to_internal_units(value, "Data Rate")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Bit Rate=' + f"{value}"])

    @property
    def sidelobes(self) -> int:
        """Sidelobes
        "Number of sidelobes in spectral profile."
        "Value should be greater than 0."
        """
        val = self._get_property('Sidelobes')
        return val

    @sidelobes.setter
    def sidelobes(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Sidelobes=' + value])

    @property
    def freq_deviation_(self) -> float:
        """Freq. Deviation 
        "FSK frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Freq. Deviation ')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @freq_deviation_.setter
    def freq_deviation_(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Freq. Deviation =' + f"{value}"])

    class PSKTypeOption(Enum):
            BPSK = "BPSK"
            QPSK = "QPSK"
            _8_PSK = "8-PSK"
            _16_PSK = "16-PSK"
            _32_PSK = "32-PSK"
            _64_PSK = "64-PSK"

    @property
    def psk_type(self) -> PSKTypeOption:
        """PSK Type
        "PSK modulation order: helps determine spectral profile."
        "        """
        val = self._get_property('PSK Type')
        val = self.PSKTypeOption[val]
        return val

    @psk_type.setter
    def psk_type(self, value: PSKTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['PSK Type=' + value.value])

    class FSKTypeOption(Enum):
            _2_FSK = "2-FSK"
            _4_FSK = "4-FSK"
            _8_FSK = "8-FSK"

    @property
    def fsk_type(self) -> FSKTypeOption:
        """FSK Type
        "FSK modulation order: helps determine spectral profile."
        "        """
        val = self._get_property('FSK Type')
        val = self.FSKTypeOption[val]
        return val

    @fsk_type.setter
    def fsk_type(self, value: FSKTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['FSK Type=' + value.value])

    class QAMTypeOption(Enum):
            _4_QAM = "4-QAM"
            _16_QAM = "16-QAM"
            _64_QAM = "64-QAM"
            _256_QAM = "256-QAM"
            _1024_QAM = "1024-QAM"

    @property
    def qam_type(self) -> QAMTypeOption:
        """QAM Type
        "QAM modulation order: helps determine spectral profile."
        "        """
        val = self._get_property('QAM Type')
        val = self.QAMTypeOption[val]
        return val

    @qam_type.setter
    def qam_type(self, value: QAMTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['QAM Type=' + value.value])

    class APSKTypeOption(Enum):
            _4_APSK = "4-APSK"
            _16_APSK = "16-APSK"
            _64_APSK = "64-APSK"
            _256_APSK = "256-APSK"
            _1024_APSK = "1024-APSK"

    @property
    def apsk_type(self) -> APSKTypeOption:
        """APSK Type
        "APSK modulation order: helps determine spectral profile."
        "        """
        val = self._get_property('APSK Type')
        val = self.APSKTypeOption[val]
        return val

    @apsk_type.setter
    def apsk_type(self, value: APSKTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['APSK Type=' + value.value])

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "First frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Start Frequency')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @start_frequency.setter
    def start_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Start Frequency=' + f"{value}"])

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Last frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Stop Frequency')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @stop_frequency.setter
    def stop_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Stop Frequency=' + f"{value}"])

    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        "Spacing between channels within this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Channel Spacing')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @channel_spacing.setter
    def channel_spacing(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Channel Spacing=' + f"{value}"])

    @property
    def tx_offset(self) -> float:
        """Tx Offset
        "Frequency offset between Tx and Rx channels."
        "Value should be less than 1e+11."
        """
        val = self._get_property('Tx Offset')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @tx_offset.setter
    def tx_offset(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Tx Offset=' + f"{value}"])

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
        val = self._get_property('Radar Type')
        val = self.RadarTypeOption[val]
        return val

    @radar_type.setter
    def radar_type(self, value: RadarTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Radar Type=' + value.value])

    @property
    def hopping_radar(self) -> bool:
        """Hopping Radar
        "True for hopping radars; false otherwise."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Hopping Radar')
        return val

    @hopping_radar.setter
    def hopping_radar(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Hopping Radar=' + value])

    @property
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement
        "Procurement date: helps determine spectral profile, particularly the roll-off."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Post October 2020 Procurement')
        return val

    @post_october_2020_procurement.setter
    def post_october_2020_procurement(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Post October 2020 Procurement=' + value])

    @property
    def hop_range_min_freq(self) -> float:
        """Hop Range Min Freq
        "Sets the minimum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Hop Range Min Freq')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @hop_range_min_freq.setter
    def hop_range_min_freq(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Hop Range Min Freq=' + f"{value}"])

    @property
    def hop_range_max_freq(self) -> float:
        """Hop Range Max Freq
        "Sets the maximum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Hop Range Max Freq')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @hop_range_max_freq.setter
    def hop_range_max_freq(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Hop Range Max Freq=' + f"{value}"])

    @property
    def pulse_duration(self) -> float:
        """Pulse Duration
        "Pulse duration."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Duration')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @pulse_duration.setter
    def pulse_duration(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Duration=' + f"{value}"])

    @property
    def pulse_rise_time(self) -> float:
        """Pulse Rise Time
        "Pulse rise time."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Rise Time')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @pulse_rise_time.setter
    def pulse_rise_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Rise Time=' + f"{value}"])

    @property
    def pulse_fall_time(self) -> float:
        """Pulse Fall Time
        "Pulse fall time."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Fall Time')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @pulse_fall_time.setter
    def pulse_fall_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Fall Time=' + f"{value}"])

    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse Repetition Rate
        "Pulse repetition rate [pulses/sec]."
        "Value should be greater than 1."
        """
        val = self._get_property('Pulse Repetition Rate')
        return val

    @pulse_repetition_rate.setter
    def pulse_repetition_rate(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Repetition Rate=' + value])

    @property
    def number_of_chips(self) -> float:
        """Number of Chips
        "Total number of chips (subpulses) contained in the pulse."
        "Value should be greater than 1."
        """
        val = self._get_property('Number of Chips')
        return val

    @number_of_chips.setter
    def number_of_chips(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Number of Chips=' + value])

    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse Compression Ratio
        "Pulse compression ratio."
        "Value should be greater than 1."
        """
        val = self._get_property('Pulse Compression Ratio')
        return val

    @pulse_compression_ratio.setter
    def pulse_compression_ratio(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Compression Ratio=' + value])

    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp Period
        "FM Chirp period for the FM/CW radar."
        "Value should be greater than 0."
        """
        val = self._get_property('FM Chirp Period')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @fm_chirp_period.setter
    def fm_chirp_period(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['FM Chirp Period=' + f"{value}"])

    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation
        "Total frequency deviation for the carrier frequency for the FM/CW radar."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('FM Freq Deviation')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @fm_freq_deviation.setter
    def fm_freq_deviation(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['FM Freq Deviation=' + f"{value}"])

    @property
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth
        "Bandwidth of freq deviation for FM modulated pulsed waveform (total freq shift during pulse duration)."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('FM Freq Dev Bandwidth')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @fm_freq_dev_bandwidth.setter
    def fm_freq_dev_bandwidth(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['FM Freq Dev Bandwidth=' + f"{value}"])

