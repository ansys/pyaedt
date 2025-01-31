from ..GenericEmitNode import *
class Band(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def port(self):
        """Port
        "Radio Port associated with this Band."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Port')
        key_val_pair = [i for i in props if 'Port=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @port.setter
    def port(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Port=' + value])
    class PortOption(Enum):
            PARENTANTENNASIDEPORTS = "::Parent::AntennaSidePorts"

    @property
    def use_dd_1494_mode(self) -> bool:
        """Use DD-1494 Mode
        "Uses DD-1494 parameters to define the Tx/Rx spectrum."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use DD-1494 Mode')
        key_val_pair = [i for i in props if 'Use DD-1494 Mode=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @use_dd_1494_mode.setter
    def use_dd_1494_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use DD-1494 Mode=' + value])

    @property
    def use_emission_designator(self) -> bool:
        """Use Emission Designator
        "Uses the Emission Designator to define the bandwidth and modulation."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Emission Designator')
        key_val_pair = [i for i in props if 'Use Emission Designator=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @use_emission_designator.setter
    def use_emission_designator(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Emission Designator=' + value])

    @property
    def emission_designator(self) -> str:
        """Emission Designator
        "Enter the Emission Designator to define the bandwidth and modulation."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Emission Designator')
        key_val_pair = [i for i in props if 'Emission Designator=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @emission_designator.setter
    def emission_designator(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Emission Designator=' + value])

    @property
    def emission_designator_ch_bw(self) -> float:
        """Emission Designator Ch. BW
        "Channel Bandwidth based off the emission designator."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Emission Designator Ch. BW')
        key_val_pair = [i for i in props if 'Emission Designator Ch. BW=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def emit_modulation_type(self) -> str:
        """EMIT Modulation Type
        "Modulation based off the emission designator."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'EMIT Modulation Type')
        key_val_pair = [i for i in props if 'EMIT Modulation Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def override_emission_designator_bw(self) -> bool:
        """Override Emission Designator BW
        "Enables the 3 dB channel bandwidth to equal a value < emission designator bandwidth."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Override Emission Designator BW')
        key_val_pair = [i for i in props if 'Override Emission Designator BW=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @override_emission_designator_bw.setter
    def override_emission_designator_bw(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Override Emission Designator BW=' + value])

    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth
        "Channel Bandwidth."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Channel Bandwidth')
        key_val_pair = [i for i in props if 'Channel Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @channel_bandwidth.setter
    def channel_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Channel Bandwidth=' + value])

    @property
    def modulation(self):
        """Modulation
        "Modulation used for the transmitted/received signal."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Modulation')
        key_val_pair = [i for i in props if 'Modulation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @modulation.setter
    def modulation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Modulation=' + value])
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
    def waveform(self):
        """Waveform
        "Modulation used for the transmitted/received signal."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveform')
        key_val_pair = [i for i in props if 'Waveform=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @waveform.setter
    def waveform(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Waveform=' + value])
    class WaveformOption(Enum):
            PERIODIC_CLOCK = "Periodic Clock"
            SPREAD_SPECTRUM = "Spread Spectrum Clock"
            PRBS = "PRBS"
            PRBS_PERIODIC = "PRBS (Periodic)"
            IMPORTED = "Imported"

    @property
    def max_modulating_freq(self) -> float:
        """Max Modulating Freq.
        "Maximum modulating frequency: helps determine spectral profile."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Modulating Freq.')
        key_val_pair = [i for i in props if 'Max Modulating Freq.=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_modulating_freq.setter
    def max_modulating_freq(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Modulating Freq.=' + value])

    @property
    def modulation_index(self) -> float:
        """Modulation Index
        "AM modulation index: helps determine spectral profile."
        "Value should be between 0.01 and 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Modulation Index')
        key_val_pair = [i for i in props if 'Modulation Index=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @modulation_index.setter
    def modulation_index(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Modulation Index=' + value])

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Freq. Deviation')
        key_val_pair = [i for i in props if 'Freq. Deviation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @freq_deviation.setter
    def freq_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Freq. Deviation=' + value])

    @property
    def bit_rate(self) -> float:
        """Bit Rate
        "Maximum bit rate: helps determine width of spectral profile."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Bit Rate')
        key_val_pair = [i for i in props if 'Bit Rate=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @bit_rate.setter
    def bit_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Bit Rate=' + value])

    @property
    def sidelobes(self) -> int:
        """Sidelobes
        "Number of sidelobes in spectral profile."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Sidelobes')
        key_val_pair = [i for i in props if 'Sidelobes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @sidelobes.setter
    def sidelobes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Sidelobes=' + value])

    @property
    def freq_deviation_(self) -> float:
        """Freq. Deviation 
        "FSK frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Freq. Deviation ')
        key_val_pair = [i for i in props if 'Freq. Deviation =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @freq_deviation_.setter
    def freq_deviation_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Freq. Deviation =' + value])

    @property
    def psk_type(self):
        """PSK Type
        "PSK modulation order: helps determine spectral profile."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'PSK Type')
        key_val_pair = [i for i in props if 'PSK Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @psk_type.setter
    def psk_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['PSK Type=' + value])
    class PSKTypeOption(Enum):
            BPSK = "BPSK"
            QPSK = "QPSK"
            _8_PSK = "8-PSK"
            _16_PSK = "16-PSK"
            _32_PSK = "32-PSK"
            _64_PSK = "64-PSK"

    @property
    def fsk_type(self):
        """FSK Type
        "FSK modulation order: helps determine spectral profile."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FSK Type')
        key_val_pair = [i for i in props if 'FSK Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @fsk_type.setter
    def fsk_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FSK Type=' + value])
    class FSKTypeOption(Enum):
            _2_FSK = "2-FSK"
            _4_FSK = "4-FSK"
            _8_FSK = "8-FSK"

    @property
    def qam_type(self):
        """QAM Type
        "QAM modulation order: helps determine spectral profile."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'QAM Type')
        key_val_pair = [i for i in props if 'QAM Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @qam_type.setter
    def qam_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['QAM Type=' + value])
    class QAMTypeOption(Enum):
            _4_QAM = "4-QAM"
            _16_QAM = "16-QAM"
            _64_QAM = "64-QAM"
            _256_QAM = "256-QAM"
            _1024_QAM = "1024-QAM"

    @property
    def apsk_type(self):
        """APSK Type
        "APSK modulation order: helps determine spectral profile."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'APSK Type')
        key_val_pair = [i for i in props if 'APSK Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @apsk_type.setter
    def apsk_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['APSK Type=' + value])
    class APSKTypeOption(Enum):
            _4_APSK = "4-APSK"
            _16_APSK = "16-APSK"
            _64_APSK = "64-APSK"
            _256_APSK = "256-APSK"
            _1024_APSK = "1024-APSK"

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "First frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start Frequency')
        key_val_pair = [i for i in props if 'Start Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @start_frequency.setter
    def start_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start Frequency=' + value])

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Last frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop Frequency')
        key_val_pair = [i for i in props if 'Stop Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @stop_frequency.setter
    def stop_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop Frequency=' + value])

    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        "Spacing between channels within this band."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Channel Spacing')
        key_val_pair = [i for i in props if 'Channel Spacing=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @channel_spacing.setter
    def channel_spacing(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Channel Spacing=' + value])

    @property
    def tx_offset(self) -> float:
        """Tx Offset
        "Frequency offset between Tx and Rx channels."
        "Value should be less than 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Offset')
        key_val_pair = [i for i in props if 'Tx Offset=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @tx_offset.setter
    def tx_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Offset=' + value])

    @property
    def clock_duty_cycle(self) -> float:
        """Clock Duty Cycle
        "Clock signals duty cycle."
        "Value should be between 0.001 and 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Clock Duty Cycle')
        key_val_pair = [i for i in props if 'Clock Duty Cycle=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @clock_duty_cycle.setter
    def clock_duty_cycle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Clock Duty Cycle=' + value])

    @property
    def clock_risefall_time(self) -> float:
        """Clock Rise/Fall Time
        "Clock signals rise/fall time."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Clock Rise/Fall Time')
        key_val_pair = [i for i in props if 'Clock Rise/Fall Time=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @clock_risefall_time.setter
    def clock_risefall_time(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Clock Rise/Fall Time=' + value])

    @property
    def spreading_type(self):
        """Spreading Type
        "Type of spreading employed by the Spread Spectrum Clock."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spreading Type')
        key_val_pair = [i for i in props if 'Spreading Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @spreading_type.setter
    def spreading_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spreading Type=' + value])
    class SpreadingTypeOption(Enum):
            LOW_SPREAD = "Low Spread"
            CENTER_SPREAD = "Center Spread"
            HIGH_SPREAD = "High Spread"

    @property
    def spread_percentage(self) -> float:
        """Spread Percentage
        "Peak-to-peak spread percentage."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spread Percentage')
        key_val_pair = [i for i in props if 'Spread Percentage=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @spread_percentage.setter
    def spread_percentage(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spread Percentage=' + value])

    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Imported Spectrum')
        key_val_pair = [i for i in props if 'Imported Spectrum=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @imported_spectrum.setter
    def imported_spectrum(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Imported Spectrum=' + value])

    @property
    def raw_data_format(self) -> str:
        """Raw Data Format
        "Format of the imported raw data."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Raw Data Format')
        key_val_pair = [i for i in props if 'Raw Data Format=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def system_impedance(self) -> float:
        """System Impedance
        "System impedance for the imported data."
        "Value should be between 0 and 1e+06."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'System Impedance')
        key_val_pair = [i for i in props if 'System Impedance=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @system_impedance.setter
    def system_impedance(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['System Impedance=' + value])

    @property
    def advanced_extraction_params(self) -> bool:
        """Advanced Extraction Params
        "Show/hide advanced extraction params."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Advanced Extraction Params')
        key_val_pair = [i for i in props if 'Advanced Extraction Params=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @advanced_extraction_params.setter
    def advanced_extraction_params(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Advanced Extraction Params=' + value])

    @property
    def nb_window_size(self) -> float:
        """NB Window Size
        "Window size for computing the moving average during narrowband signal detection."
        "Value should be greater than 3."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'NB Window Size')
        key_val_pair = [i for i in props if 'NB Window Size=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @nb_window_size.setter
    def nb_window_size(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['NB Window Size=' + value])

    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor
        "Reduces the number of frequency points used for the broadband noise."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BB Smoothing Factor')
        key_val_pair = [i for i in props if 'BB Smoothing Factor=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @bb_smoothing_factor.setter
    def bb_smoothing_factor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BB Smoothing Factor=' + value])

    @property
    def nb_detector_threshold(self) -> float:
        """NB Detector Threshold
        "Narrowband Detector threshold standard deviation."
        "Value should be between 2 and 10."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'NB Detector Threshold')
        key_val_pair = [i for i in props if 'NB Detector Threshold=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @nb_detector_threshold.setter
    def nb_detector_threshold(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['NB Detector Threshold=' + value])

    @property
    def algorithm(self):
        """Algorithm
        "Algorithm used to transform the imported time domain spectrum."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Algorithm')
        key_val_pair = [i for i in props if 'Algorithm=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @algorithm.setter
    def algorithm(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Algorithm=' + value])
    class AlgorithmOption(Enum):
            FFT = "FFT"
            FOURIER_TRANSFORM = "Fourier Transform"

    @property
    def start(self) -> float:
        """Start
        "Initial time of the imported spectrum."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start')
        key_val_pair = [i for i in props if 'Start=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @start.setter
    def start(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start=' + value])

    @property
    def stop(self) -> float:
        """Stop
        "Final time of the imported time domain spectrum."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop')
        key_val_pair = [i for i in props if 'Stop=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @stop.setter
    def stop(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop=' + value])

    @property
    def max_frequency(self) -> float:
        """Max Frequency
        "Frequency cutoff of the imported time domain spectrum."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Frequency')
        key_val_pair = [i for i in props if 'Max Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_frequency.setter
    def max_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Frequency=' + value])

    @property
    def window_type(self):
        """Window Type
        "Windowing scheme used for importing time domain spectrum."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Window Type')
        key_val_pair = [i for i in props if 'Window Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @window_type.setter
    def window_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Window Type=' + value])
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
    def kaiser_parameter(self) -> float:
        """Kaiser Parameter
        "Shape factor applied to the transform."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Kaiser Parameter')
        key_val_pair = [i for i in props if 'Kaiser Parameter=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @kaiser_parameter.setter
    def kaiser_parameter(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Kaiser Parameter=' + value])

    @property
    def adjust_coherent_gain(self) -> bool:
        """Adjust Coherent Gain
        "Shape factor applied to the transform."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Adjust Coherent Gain')
        key_val_pair = [i for i in props if 'Adjust Coherent Gain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Adjust Coherent Gain=' + value])

    @property
    def data_rate(self) -> float:
        """Data Rate
        "Maximum data rate: helps determine shape of spectral profile."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Data Rate')
        key_val_pair = [i for i in props if 'Data Rate=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @data_rate.setter
    def data_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Data Rate=' + value])

    @property
    def _of_bits(self) -> int:
        """# of Bits
        "Length of the Pseudo Random Binary Sequence."
        "Value should be between 1 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'# of Bits')
        key_val_pair = [i for i in props if '# of Bits=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_of_bits.setter
    def _of_bits(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['# of Bits=' + value])

    @property
    def use_envelope(self) -> bool:
        """Use Envelope
        "Model the waveform as a worst case envelope.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Envelope')
        key_val_pair = [i for i in props if 'Use Envelope=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @use_envelope.setter
    def use_envelope(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Envelope=' + value])

    @property
    def min_ptsnull(self) -> int:
        """Min Pts/Null
        "Minimum number of points to use between each null frequency."
        "Value should be between 2 and 50."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min Pts/Null')
        key_val_pair = [i for i in props if 'Min Pts/Null=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @min_ptsnull.setter
    def min_ptsnull(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min Pts/Null=' + value])

    @property
    def delay_skew(self) -> float:
        """Delay Skew
        "Delay Skew of the differential signal pairs."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Delay Skew')
        key_val_pair = [i for i in props if 'Delay Skew=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @delay_skew.setter
    def delay_skew(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Delay Skew=' + value])

    @property
    def radar_type(self):
        """Radar Type
        "Radar type: helps determine spectral profile."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Radar Type')
        key_val_pair = [i for i in props if 'Radar Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @radar_type.setter
    def radar_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Radar Type=' + value])
    class RadarTypeOption(Enum):
            CW = "CW"
            FM_CW = "FM-CW"
            FM_PULSE = "FM Pulse"
            NON_FM_PULSE = "Non-FM Pulse"
            PHASE_CODED = "Phase Coded"

    @property
    def hopping_radar(self) -> bool:
        """Hopping Radar
        "True for hopping radars; false otherwise."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Hopping Radar')
        key_val_pair = [i for i in props if 'Hopping Radar=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @hopping_radar.setter
    def hopping_radar(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Hopping Radar=' + value])

    @property
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement
        "Procurement date: helps determine spectral profile, particularly the roll-off."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Post October 2020 Procurement')
        key_val_pair = [i for i in props if 'Post October 2020 Procurement=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @post_october_2020_procurement.setter
    def post_october_2020_procurement(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Post October 2020 Procurement=' + value])

    @property
    def hop_range_min_freq(self) -> float:
        """Hop Range Min Freq
        "Sets the minimum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Hop Range Min Freq')
        key_val_pair = [i for i in props if 'Hop Range Min Freq=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @hop_range_min_freq.setter
    def hop_range_min_freq(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Hop Range Min Freq=' + value])

    @property
    def hop_range_max_freq(self) -> float:
        """Hop Range Max Freq
        "Sets the maximum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Hop Range Max Freq')
        key_val_pair = [i for i in props if 'Hop Range Max Freq=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @hop_range_max_freq.setter
    def hop_range_max_freq(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Hop Range Max Freq=' + value])

    @property
    def pulse_duration(self) -> float:
        """Pulse Duration
        "Pulse duration."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Duration')
        key_val_pair = [i for i in props if 'Pulse Duration=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @pulse_duration.setter
    def pulse_duration(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Duration=' + value])

    @property
    def pulse_rise_time(self) -> float:
        """Pulse Rise Time
        "Pulse rise time."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Rise Time')
        key_val_pair = [i for i in props if 'Pulse Rise Time=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @pulse_rise_time.setter
    def pulse_rise_time(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Rise Time=' + value])

    @property
    def pulse_fall_time(self) -> float:
        """Pulse Fall Time
        "Pulse fall time."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Fall Time')
        key_val_pair = [i for i in props if 'Pulse Fall Time=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @pulse_fall_time.setter
    def pulse_fall_time(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Fall Time=' + value])

    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse Repetition Rate
        "Pulse repetition rate [pulses/sec]."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Repetition Rate')
        key_val_pair = [i for i in props if 'Pulse Repetition Rate=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @pulse_repetition_rate.setter
    def pulse_repetition_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Repetition Rate=' + value])

    @property
    def number_of_chips(self) -> float:
        """Number of Chips
        "Total number of chips (subpulses) contained in the pulse."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Chips')
        key_val_pair = [i for i in props if 'Number of Chips=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @number_of_chips.setter
    def number_of_chips(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Number of Chips=' + value])

    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse Compression Ratio
        "Pulse compression ratio."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pulse Compression Ratio')
        key_val_pair = [i for i in props if 'Pulse Compression Ratio=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @pulse_compression_ratio.setter
    def pulse_compression_ratio(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pulse Compression Ratio=' + value])

    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp Period
        "FM Chirp period for the FM/CW radar."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FM Chirp Period')
        key_val_pair = [i for i in props if 'FM Chirp Period=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @fm_chirp_period.setter
    def fm_chirp_period(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FM Chirp Period=' + value])

    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation
        "Total frequency deviation for the carrier frequency for the FM/CW radar."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FM Freq Deviation')
        key_val_pair = [i for i in props if 'FM Freq Deviation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @fm_freq_deviation.setter
    def fm_freq_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FM Freq Deviation=' + value])

    @property
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth
        "Bandwidth of freq deviation for FM modulated pulsed waveform (total freq shift during pulse duration)."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'FM Freq Dev Bandwidth')
        key_val_pair = [i for i in props if 'FM Freq Dev Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @fm_freq_dev_bandwidth.setter
    def fm_freq_dev_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['FM Freq Dev Bandwidth=' + value])

