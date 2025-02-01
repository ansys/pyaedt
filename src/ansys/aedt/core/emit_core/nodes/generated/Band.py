from ..EmitNode import *

class Band(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'enabled')
    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def port(self):
        """Port
        "Radio Port associated with this Band."
        "        """
        val = self._get_property('Port')
        return val
    @port.setter
    def port(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Port=' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Use DD-1494 Mode=' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Use Emission Designator=' + value])

    @property
    def emission_designator(self) -> str:
        """Emission Designator
        "Enter the Emission Designator to define the bandwidth and modulation."
        "        """
        val = self._get_property('Emission Designator')
        return val
    @emission_designator.setter
    def emission_designator(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Emission Designator=' + value])

    @property
    def emission_designator_ch_bw(self) -> float:
        """Emission Designator Ch. BW
        "Channel Bandwidth based off the emission designator."
        "        """
        val = self._get_property('Emission Designator Ch. BW')
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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Override Emission Designator BW=' + value])

    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth
        "Channel Bandwidth."
        "Value should be greater than 1."
        """
        val = self._get_property('Channel Bandwidth')
        return val
    @channel_bandwidth.setter
    def channel_bandwidth(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Channel Bandwidth=' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Modulation=' + value.value])

    class WaveformOption(Enum):
            PERIODIC_CLOCK = "Periodic Clock"
            SPREAD_SPECTRUM = "Spread Spectrum Clock"
            PRBS = "PRBS"
            PRBS_PERIODIC = "PRBS (Periodic)"
            IMPORTED = "Imported"
    @property
    def waveform(self) -> WaveformOption:
        """Waveform
        "Modulation used for the transmitted/received signal."
        "        """
        val = self._get_property('Waveform')
        val = self.WaveformOption[val]
        return val
    @waveform.setter
    def waveform(self, value: WaveformOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Waveform=' + value.value])

    @property
    def max_modulating_freq(self) -> float:
        """Max Modulating Freq.
        "Maximum modulating frequency: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Max Modulating Freq.')
        return val
    @max_modulating_freq.setter
    def max_modulating_freq(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max Modulating Freq.=' + value])

    @property
    def modulation_index(self) -> float:
        """Modulation Index
        "AM modulation index: helps determine spectral profile."
        "Value should be between 0.01 and 1."
        """
        val = self._get_property('Modulation Index')
        return val
    @modulation_index.setter
    def modulation_index(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Modulation Index=' + value])

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Freq. Deviation')
        return val
    @freq_deviation.setter
    def freq_deviation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Freq. Deviation=' + value])

    @property
    def bit_rate(self) -> float:
        """Bit Rate
        "Maximum bit rate: helps determine width of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Bit Rate')
        return val
    @bit_rate.setter
    def bit_rate(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Bit Rate=' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Sidelobes=' + value])

    @property
    def freq_deviation_(self) -> float:
        """Freq. Deviation 
        "FSK frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Freq. Deviation ')
        return val
    @freq_deviation_.setter
    def freq_deviation_(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Freq. Deviation =' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['PSK Type=' + value.value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['FSK Type=' + value.value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['QAM Type=' + value.value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['APSK Type=' + value.value])

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "First frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Start Frequency')
        return val
    @start_frequency.setter
    def start_frequency(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Start Frequency=' + value])

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Last frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Stop Frequency')
        return val
    @stop_frequency.setter
    def stop_frequency(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Stop Frequency=' + value])

    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        "Spacing between channels within this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Channel Spacing')
        return val
    @channel_spacing.setter
    def channel_spacing(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Channel Spacing=' + value])

    @property
    def tx_offset(self) -> float:
        """Tx Offset
        "Frequency offset between Tx and Rx channels."
        "Value should be less than 1e+11."
        """
        val = self._get_property('Tx Offset')
        return val
    @tx_offset.setter
    def tx_offset(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Tx Offset=' + value])

    @property
    def clock_duty_cycle(self) -> float:
        """Clock Duty Cycle
        "Clock signals duty cycle."
        "Value should be between 0.001 and 1."
        """
        val = self._get_property('Clock Duty Cycle')
        return val
    @clock_duty_cycle.setter
    def clock_duty_cycle(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Clock Duty Cycle=' + value])

    @property
    def clock_risefall_time(self) -> float:
        """Clock Rise/Fall Time
        "Clock signals rise/fall time."
        "Value should be greater than 0."
        """
        val = self._get_property('Clock Rise/Fall Time')
        return val
    @clock_risefall_time.setter
    def clock_risefall_time(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Clock Rise/Fall Time=' + value])

    class SpreadingTypeOption(Enum):
            LOW_SPREAD = "Low Spread"
            CENTER_SPREAD = "Center Spread"
            HIGH_SPREAD = "High Spread"
    @property
    def spreading_type(self) -> SpreadingTypeOption:
        """Spreading Type
        "Type of spreading employed by the Spread Spectrum Clock."
        "        """
        val = self._get_property('Spreading Type')
        val = self.SpreadingTypeOption[val]
        return val
    @spreading_type.setter
    def spreading_type(self, value: SpreadingTypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Spreading Type=' + value.value])

    @property
    def spread_percentage(self) -> float:
        """Spread Percentage
        "Peak-to-peak spread percentage."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Spread Percentage')
        return val
    @spread_percentage.setter
    def spread_percentage(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Spread Percentage=' + value])

    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum
        "Value should be a full file path."
        """
        val = self._get_property('Imported Spectrum')
        return val
    @imported_spectrum.setter
    def imported_spectrum(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Imported Spectrum=' + value])

    @property
    def raw_data_format(self) -> str:
        """Raw Data Format
        "Format of the imported raw data."
        "        """
        val = self._get_property('Raw Data Format')
        return val
    @property
    def system_impedance(self) -> float:
        """System Impedance
        "System impedance for the imported data."
        "Value should be between 0 and 1e+06."
        """
        val = self._get_property('System Impedance')
        return val
    @system_impedance.setter
    def system_impedance(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['System Impedance=' + value])

    @property
    def advanced_extraction_params(self) -> bool:
        """Advanced Extraction Params
        "Show/hide advanced extraction params."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Advanced Extraction Params')
        return val
    @advanced_extraction_params.setter
    def advanced_extraction_params(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Advanced Extraction Params=' + value])

    @property
    def nb_window_size(self) -> float:
        """NB Window Size
        "Window size for computing the moving average during narrowband signal detection."
        "Value should be greater than 3."
        """
        val = self._get_property('NB Window Size')
        return val
    @nb_window_size.setter
    def nb_window_size(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['NB Window Size=' + value])

    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor
        "Reduces the number of frequency points used for the broadband noise."
        "Value should be greater than 1."
        """
        val = self._get_property('BB Smoothing Factor')
        return val
    @bb_smoothing_factor.setter
    def bb_smoothing_factor(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['BB Smoothing Factor=' + value])

    @property
    def nb_detector_threshold(self) -> float:
        """NB Detector Threshold
        "Narrowband Detector threshold standard deviation."
        "Value should be between 2 and 10."
        """
        val = self._get_property('NB Detector Threshold')
        return val
    @nb_detector_threshold.setter
    def nb_detector_threshold(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['NB Detector Threshold=' + value])

    class AlgorithmOption(Enum):
            FFT = "FFT"
            FOURIER_TRANSFORM = "Fourier Transform"
    @property
    def algorithm(self) -> AlgorithmOption:
        """Algorithm
        "Algorithm used to transform the imported time domain spectrum."
        "        """
        val = self._get_property('Algorithm')
        val = self.AlgorithmOption[val]
        return val
    @algorithm.setter
    def algorithm(self, value: AlgorithmOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Algorithm=' + value.value])

    @property
    def start(self) -> float:
        """Start
        "Initial time of the imported spectrum."
        "Value should be greater than 0."
        """
        val = self._get_property('Start')
        return val
    @start.setter
    def start(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Start=' + value])

    @property
    def stop(self) -> float:
        """Stop
        "Final time of the imported time domain spectrum."
        "        """
        val = self._get_property('Stop')
        return val
    @stop.setter
    def stop(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Stop=' + value])

    @property
    def max_frequency(self) -> float:
        """Max Frequency
        "Frequency cutoff of the imported time domain spectrum."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Frequency')
        return val
    @max_frequency.setter
    def max_frequency(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max Frequency=' + value])

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
        """Window Type
        "Windowing scheme used for importing time domain spectrum."
        "        """
        val = self._get_property('Window Type')
        val = self.WindowTypeOption[val]
        return val
    @window_type.setter
    def window_type(self, value: WindowTypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Window Type=' + value.value])

    @property
    def kaiser_parameter(self) -> float:
        """Kaiser Parameter
        "Shape factor applied to the transform."
        "Value should be greater than 0."
        """
        val = self._get_property('Kaiser Parameter')
        return val
    @kaiser_parameter.setter
    def kaiser_parameter(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Kaiser Parameter=' + value])

    @property
    def adjust_coherent_gain(self) -> bool:
        """Adjust Coherent Gain
        "Shape factor applied to the transform."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adjust Coherent Gain')
        return val
    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Adjust Coherent Gain=' + value])

    @property
    def data_rate(self) -> float:
        """Data Rate
        "Maximum data rate: helps determine shape of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Data Rate')
        return val
    @data_rate.setter
    def data_rate(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Data Rate=' + value])

    @property
    def _of_bits(self) -> int:
        """# of Bits
        "Length of the Pseudo Random Binary Sequence."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('# of Bits')
        return val
    @_of_bits.setter
    def _of_bits(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['# of Bits=' + value])

    @property
    def use_envelope(self) -> bool:
        """Use Envelope
        "Model the waveform as a worst case envelope.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Envelope')
        return val
    @use_envelope.setter
    def use_envelope(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Use Envelope=' + value])

    @property
    def min_ptsnull(self) -> int:
        """Min Pts/Null
        "Minimum number of points to use between each null frequency."
        "Value should be between 2 and 50."
        """
        val = self._get_property('Min Pts/Null')
        return val
    @min_ptsnull.setter
    def min_ptsnull(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Min Pts/Null=' + value])

    @property
    def delay_skew(self) -> float:
        """Delay Skew
        "Delay Skew of the differential signal pairs."
        "Value should be greater than 0."
        """
        val = self._get_property('Delay Skew')
        return val
    @delay_skew.setter
    def delay_skew(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Delay Skew=' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Radar Type=' + value.value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Hopping Radar=' + value])

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
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Post October 2020 Procurement=' + value])

    @property
    def hop_range_min_freq(self) -> float:
        """Hop Range Min Freq
        "Sets the minimum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Hop Range Min Freq')
        return val
    @hop_range_min_freq.setter
    def hop_range_min_freq(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Hop Range Min Freq=' + value])

    @property
    def hop_range_max_freq(self) -> float:
        """Hop Range Max Freq
        "Sets the maximum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Hop Range Max Freq')
        return val
    @hop_range_max_freq.setter
    def hop_range_max_freq(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Hop Range Max Freq=' + value])

    @property
    def pulse_duration(self) -> float:
        """Pulse Duration
        "Pulse duration."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Duration')
        return val
    @pulse_duration.setter
    def pulse_duration(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Duration=' + value])

    @property
    def pulse_rise_time(self) -> float:
        """Pulse Rise Time
        "Pulse rise time."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Rise Time')
        return val
    @pulse_rise_time.setter
    def pulse_rise_time(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Rise Time=' + value])

    @property
    def pulse_fall_time(self) -> float:
        """Pulse Fall Time
        "Pulse fall time."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Fall Time')
        return val
    @pulse_fall_time.setter
    def pulse_fall_time(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Fall Time=' + value])

    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse Repetition Rate
        "Pulse repetition rate [pulses/sec]."
        "Value should be greater than 1."
        """
        val = self._get_property('Pulse Repetition Rate')
        return val
    @pulse_repetition_rate.setter
    def pulse_repetition_rate(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Repetition Rate=' + value])

    @property
    def number_of_chips(self) -> float:
        """Number of Chips
        "Total number of chips (subpulses) contained in the pulse."
        "Value should be greater than 1."
        """
        val = self._get_property('Number of Chips')
        return val
    @number_of_chips.setter
    def number_of_chips(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Number of Chips=' + value])

    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse Compression Ratio
        "Pulse compression ratio."
        "Value should be greater than 1."
        """
        val = self._get_property('Pulse Compression Ratio')
        return val
    @pulse_compression_ratio.setter
    def pulse_compression_ratio(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Pulse Compression Ratio=' + value])

    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp Period
        "FM Chirp period for the FM/CW radar."
        "Value should be greater than 0."
        """
        val = self._get_property('FM Chirp Period')
        return val
    @fm_chirp_period.setter
    def fm_chirp_period(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['FM Chirp Period=' + value])

    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation
        "Total frequency deviation for the carrier frequency for the FM/CW radar."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('FM Freq Deviation')
        return val
    @fm_freq_deviation.setter
    def fm_freq_deviation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['FM Freq Deviation=' + value])

    @property
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth
        "Bandwidth of freq deviation for FM modulated pulsed waveform (total freq shift during pulse duration)."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('FM Freq Dev Bandwidth')
        return val
    @fm_freq_dev_bandwidth.setter
    def fm_freq_dev_bandwidth(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['FM Freq Dev Bandwidth=' + value])

