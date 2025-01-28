class Node_Band(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def get_enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def get_port(self):
        """Port
        "Radio Port associated with this Band."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Port')
    def set_port(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Port=' + value])
    class PortOption(Enum):
        (
            ::PARENT::ANTENNASIDEPORTS = "::Parent::AntennaSidePorts"
        )

    @property
    def get_use_dd_1494_mode(self):
        """Use DD-1494 Mode
        "Uses DD-1494 parameters to define the Tx/Rx spectrum."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use DD-1494 Mode')
    def set_use_dd_1494_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use DD-1494 Mode=' + value])

    @property
    def get_use_emission_designator(self):
        """Use Emission Designator
        "Uses the Emission Designator to define the bandwidth and modulation."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Emission Designator')
    def set_use_emission_designator(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Emission Designator=' + value])

    @property
    def get_emission_designator(self):
        """Emission Designator
        "Enter the Emission Designator to define the bandwidth and modulation."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Emission Designator')
    def set_emission_designator(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Emission Designator=' + value])

    @property
    def get_emission_designator_ch_bw(self):
        """Emission Designator Ch. BW
        "Channel Bandwidth based off the emission designator."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Emission Designator Ch. BW')

    @property
    def get_emit_modulation_type(self):
        """EMIT Modulation Type
        "Modulation based off the emission designator."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'EMIT Modulation Type')

    @property
    def get_override_emission_designator_bw(self):
        """Override Emission Designator BW
        "Enables the 3 dB channel bandwidth to equal a value < emission designator bandwidth."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Override Emission Designator BW')
    def set_override_emission_designator_bw(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Override Emission Designator BW=' + value])

    @property
    def get_channel_bandwidth(self):
        """Channel Bandwidth
        "Channel Bandwidth."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Channel Bandwidth')
    def set_channel_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Channel Bandwidth=' + value])

    @property
    def get_modulation(self):
        """Modulation
        "Modulation used for the transmitted/received signal."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Modulation')
    def set_modulation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Modulation=' + value])
    class ModulationOption(Enum):
        (
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
        )

    @property
    def get_waveform(self):
        """Waveform
        "Modulation used for the transmitted/received signal."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveform')
    def set_waveform(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Waveform=' + value])
    class WaveformOption(Enum):
        (
            PERIODIC_CLOCK = "Periodic Clock"
            SPREAD_SPECTRUM = "Spread Spectrum Clock"
            PRBS = "PRBS"
            PRBS_PERIODIC = "PRBS (Periodic)"
            IMPORTED = "Imported"
        )

    @property
    def get_max_modulating_freq(self):
        """Max Modulating Freq.
        "Maximum modulating frequency: helps determine spectral profile."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Modulating Freq.')
    def set_max_modulating_freq(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Modulating Freq.=' + value])

    @property
    def get_modulation_index(self):
        """Modulation Index
        "AM modulation index: helps determine spectral profile."
        "Value should be between 0.01 and 1."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Modulation Index')
    def set_modulation_index(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Modulation Index=' + value])

    @property
    def get_freq_deviation(self):
        """Freq. Deviation
        "Frequency deviation: helps determine spectral profile."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Freq. Deviation')
    def set_freq_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Freq. Deviation=' + value])

    @property
    def get_bit_rate(self):
        """Bit Rate
        "Maximum bit rate: helps determine width of spectral profile."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Bit Rate')
    def set_bit_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Bit Rate=' + value])

    @property
    def get_sidelobes(self):
        """Sidelobes
        "Number of sidelobes in spectral profile."
        "Value should be between 0 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Sidelobes')
    def set_sidelobes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Sidelobes=' + value])

    @property
    def get_freq_deviation_(self):
        """Freq. Deviation 
        "FSK frequency deviation: helps determine spectral profile."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Freq. Deviation ')
    def set_freq_deviation_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Freq. Deviation =' + value])

    @property
    def get_psk_type(self):
        """PSK Type
        "PSK modulation order: helps determine spectral profile."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'PSK Type')
    def set_psk_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['PSK Type=' + value])
    class PSKTypeOption(Enum):
        (
            BPSK = "BPSK"
            QPSK = "QPSK"
            _8_PSK = "8-PSK"
            _16_PSK = "16-PSK"
            _32_PSK = "32-PSK"
            _64_PSK = "64-PSK"
        )

    @property
    def get_fsk_type(self):
        """FSK Type
        "FSK modulation order: helps determine spectral profile."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FSK Type')
    def set_fsk_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FSK Type=' + value])
    class FSKTypeOption(Enum):
        (
            _2_FSK = "2-FSK"
            _4_FSK = "4-FSK"
            _8_FSK = "8-FSK"
        )

    @property
    def get_qam_type(self):
        """QAM Type
        "QAM modulation order: helps determine spectral profile."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'QAM Type')
    def set_qam_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['QAM Type=' + value])
    class QAMTypeOption(Enum):
        (
            _4_QAM = "4-QAM"
            _16_QAM = "16-QAM"
            _64_QAM = "64-QAM"
            _256_QAM = "256-QAM"
            _1024_QAM = "1024-QAM"
        )

    @property
    def get_apsk_type(self):
        """APSK Type
        "APSK modulation order: helps determine spectral profile."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'APSK Type')
    def set_apsk_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['APSK Type=' + value])
    class APSKTypeOption(Enum):
        (
            _4_APSK = "4-APSK"
            _16_APSK = "16-APSK"
            _64_APSK = "64-APSK"
            _256_APSK = "256-APSK"
            _1024_APSK = "1024-APSK"
        )

    @property
    def get_start_frequency(self):
        """Start Frequency
        "First frequency for this band."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start Frequency')
    def set_start_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start Frequency=' + value])

    @property
    def get_stop_frequency(self):
        """Stop Frequency
        "Last frequency for this band."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop Frequency')
    def set_stop_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop Frequency=' + value])

    @property
    def get_channel_spacing(self):
        """Channel Spacing
        "Spacing between channels within this band."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Channel Spacing')
    def set_channel_spacing(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Channel Spacing=' + value])

    @property
    def get_tx_offset(self):
        """Tx Offset
        "Frequency offset between Tx and Rx channels."
        "Value should be between ::TxOffsetMin and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Offset')
    def set_tx_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Offset=' + value])

    @property
    def get_clock_duty_cycle(self):
        """Clock Duty Cycle
        "Clock signals duty cycle."
        "Value should be between 0.001 and 1.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Clock Duty Cycle')
    def set_clock_duty_cycle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Clock Duty Cycle=' + value])

    @property
    def get_clock_risefall_time(self):
        """Clock Rise/Fall Time
        "Clock signals rise/fall time."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Clock Rise/Fall Time')
    def set_clock_risefall_time(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Clock Rise/Fall Time=' + value])

    @property
    def get_spreading_type(self):
        """Spreading Type
        "Type of spreading employed by the Spread Spectrum Clock."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spreading Type')
    def set_spreading_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spreading Type=' + value])
    class SpreadingTypeOption(Enum):
        (
            LOW_SPREAD = "Low Spread"
            CENTER_SPREAD = "Center Spread"
            HIGH_SPREAD = "High Spread"
        )

    @property
    def get_spread_percentage(self):
        """Spread Percentage
        "Peak-to-peak spread percentage."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spread Percentage')
    def set_spread_percentage(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spread Percentage=' + value])

    @property
    def get_imported_spectrum(self):
        """Imported Spectrum
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Imported Spectrum')
    def set_imported_spectrum(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Imported Spectrum=' + value])

    @property
    def get_raw_data_format(self):
        """Raw Data Format
        "Format of the imported raw data."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Raw Data Format')

    @property
    def get_system_impedance(self):
        """System Impedance
        "System impedance for the imported data."
        "Value should be between 0.0 and 1.0e6."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'System Impedance')
    def set_system_impedance(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['System Impedance=' + value])

    @property
    def get_advanced_extraction_params(self):
        """Advanced Extraction Params
        "Show/hide advanced extraction params."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Advanced Extraction Params')
    def set_advanced_extraction_params(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Advanced Extraction Params=' + value])

    @property
    def get_nb_window_size(self):
        """NB Window Size
        "Window size for computing the moving average during narrowband signal detection."
        "Value should be greater than 3."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'NB Window Size')
    def set_nb_window_size(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['NB Window Size=' + value])

    @property
    def get_bb_smoothing_factor(self):
        """BB Smoothing Factor
        "Reduces the number of frequency points used for the broadband noise."
        "Value should be greater than 1."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BB Smoothing Factor')
    def set_bb_smoothing_factor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BB Smoothing Factor=' + value])

    @property
    def get_nb_detector_threshold(self):
        """NB Detector Threshold
        "Narrowband Detector threshold standard deviation."
        "Value should be between 2 and 10."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'NB Detector Threshold')
    def set_nb_detector_threshold(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['NB Detector Threshold=' + value])

    @property
    def get_algorithm(self):
        """Algorithm
        "Algorithm used to transform the imported time domain spectrum."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Algorithm')
    def set_algorithm(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Algorithm=' + value])
    class AlgorithmOption(Enum):
        (
            FFT = "FFT"
            FOURIER_TRANSFORM = "Fourier Transform"
        )

    @property
    def get_start(self):
        """Start
        "Initial time of the imported spectrum."
        "Value should be between 0.0 and ::TDStartMax."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start')
    def set_start(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start=' + value])

    @property
    def get_stop(self):
        """Stop
        "Final time of the imported time domain spectrum."
        "Value should be between ::TDStopMin and ::TDStopMax."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop')
    def set_stop(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop=' + value])

    @property
    def get_max_frequency(self):
        """Max Frequency
        "Frequency cutoff of the imported time domain spectrum."
        "Value should be between 1.0 and 100.0e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Frequency')
    def set_max_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Frequency=' + value])

    @property
    def get_window_type(self):
        """Window Type
        "Windowing scheme used for importing time domain spectrum."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Window Type')
    def set_window_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Window Type=' + value])
    class WindowTypeOption(Enum):
        (
            RECTANGULAR = "Rectangular"
            BARTLETT = "Bartlett"
            BLACKMAN = "Blackman"
            HAMMING = "Hamming"
            HANNING = "Hanning"
            KAISER = "Kaiser"
            LANZCOS = "Lanzcos"
            WELCH = "Welch"
            WEBER = "Weber"
        )

    @property
    def get_kaiser_parameter(self):
        """Kaiser Parameter
        "Shape factor applied to the transform."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Kaiser Parameter')
    def set_kaiser_parameter(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Kaiser Parameter=' + value])

    @property
    def get_adjust_coherent_gain(self):
        """Adjust Coherent Gain
        "Shape factor applied to the transform."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Adjust Coherent Gain')
    def set_adjust_coherent_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Adjust Coherent Gain=' + value])

    @property
    def get_data_rate(self):
        """Data Rate
        "Maximum data rate: helps determine shape of spectral profile."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Data Rate')
    def set_data_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Data Rate=' + value])

    @property
    def get__of_bits(self):
        """# of Bits
        "Length of the Pseudo Random Binary Sequence."
        "Value should be between 1 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'# of Bits')
    def set__of_bits(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['# of Bits=' + value])

    @property
    def get_use_envelope(self):
        """Use Envelope
        "Model the waveform as a worst case envelope.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Envelope')
    def set_use_envelope(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Envelope=' + value])

    @property
    def get_min_ptsnull(self):
        """Min Pts/Null
        "Minimum number of points to use between each null frequency."
        "Value should be between 2 and 50."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min Pts/Null')
    def set_min_ptsnull(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min Pts/Null=' + value])

    @property
    def get_delay_skew(self):
        """Delay Skew
        "Delay Skew of the differential signal pairs."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Delay Skew')
    def set_delay_skew(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Delay Skew=' + value])

    @property
    def get_radar_type(self):
        """Radar Type
        "Radar type: helps determine spectral profile."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Radar Type')
    def set_radar_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Radar Type=' + value])
    class RadarTypeOption(Enum):
        (
            CW = "CW"
            FM_CW = "FM-CW"
            FM_PULSE = "FM Pulse"
            NON_FM_PULSE = "Non-FM Pulse"
            PHASE_CODED = "Phase Coded"
        )

    @property
    def get_hopping_radar(self):
        """Hopping Radar
        "True for hopping radars; false otherwise."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Hopping Radar')
    def set_hopping_radar(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Hopping Radar=' + value])

    @property
    def get_post_october_2020_procurement(self):
        """Post October 2020 Procurement
        "Procurement date: helps determine spectral profile, particularly the roll-off."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Post October 2020 Procurement')
    def set_post_october_2020_procurement(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Post October 2020 Procurement=' + value])

    @property
    def get_hop_range_min_freq(self):
        """Hop Range Min Freq
        "Sets the minimum frequency of the hopping range."
        "Value should be between 1.0 and 100.0e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Hop Range Min Freq')
    def set_hop_range_min_freq(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Hop Range Min Freq=' + value])

    @property
    def get_hop_range_max_freq(self):
        """Hop Range Max Freq
        "Sets the maximum frequency of the hopping range."
        "Value should be between 1.0 and 100.0e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Hop Range Max Freq')
    def set_hop_range_max_freq(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Hop Range Max Freq=' + value])

    @property
    def get_pulse_duration(self):
        """Pulse Duration
        "Pulse duration."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Duration')
    def set_pulse_duration(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Duration=' + value])

    @property
    def get_pulse_rise_time(self):
        """Pulse Rise Time
        "Pulse rise time."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Rise Time')
    def set_pulse_rise_time(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Rise Time=' + value])

    @property
    def get_pulse_fall_time(self):
        """Pulse Fall Time
        "Pulse fall time."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Fall Time')
    def set_pulse_fall_time(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Fall Time=' + value])

    @property
    def get_pulse_repetition_rate(self):
        """Pulse Repetition Rate
        "Pulse repetition rate [pulses/sec]."
        "Value should be greater than 1.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Repetition Rate')
    def set_pulse_repetition_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Repetition Rate=' + value])

    @property
    def get_number_of_chips(self):
        """Number of Chips
        "Total number of chips (subpulses) contained in the pulse."
        "Value should be greater than 1.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Chips')
    def set_number_of_chips(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Number of Chips=' + value])

    @property
    def get_pulse_compression_ratio(self):
        """Pulse Compression Ratio
        "Pulse compression ratio."
        "Value should be greater than 1.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Compression Ratio')
    def set_pulse_compression_ratio(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Compression Ratio=' + value])

    @property
    def get_fm_chirp_period(self):
        """FM Chirp Period
        "FM Chirp period for the FM/CW radar."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FM Chirp Period')
    def set_fm_chirp_period(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FM Chirp Period=' + value])

    @property
    def get_fm_freq_deviation(self):
        """FM Freq Deviation
        "Total frequency deviation for the carrier frequency for the FM/CW radar."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FM Freq Deviation')
    def set_fm_freq_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FM Freq Deviation=' + value])

    @property
    def get_fm_freq_dev_bandwidth(self):
        """FM Freq Dev Bandwidth
        "Bandwidth of freq deviation for FM modulated pulsed waveform (total freq shift during pulse duration)."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FM Freq Dev Bandwidth')
    def set_fm_freq_dev_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FM Freq Dev Bandwidth=' + value])

