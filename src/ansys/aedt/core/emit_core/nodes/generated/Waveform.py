from ..EmitNode import *

class Waveform(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Port={value}'])

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
        val = self.WaveformOption[val.upper()]
        return val

    @waveform.setter
    def waveform(self, value: WaveformOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Waveform={value.value}'])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Start Frequency={value}'])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Stop Frequency={value}'])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Channel Spacing={value}'])

    @property
    def clock_duty_cycle(self) -> float:
        """Clock Duty Cycle
        "Clock signals duty cycle."
        "Value should be between 0.001 and 1."
        """
        val = self._get_property('Clock Duty Cycle')
        return val

    @clock_duty_cycle.setter
    def clock_duty_cycle(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Clock Duty Cycle={value}'])

    @property
    def clock_risefall_time(self) -> float:
        """Clock Rise/Fall Time
        "Clock signals rise/fall time."
        "Value should be greater than 0."
        """
        val = self._get_property('Clock Rise/Fall Time')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @clock_risefall_time.setter
    def clock_risefall_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Clock Rise/Fall Time={value}'])

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
        val = self.SpreadingTypeOption[val.upper()]
        return val

    @spreading_type.setter
    def spreading_type(self, value: SpreadingTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Spreading Type={value.value}'])

    @property
    def spread_percentage(self) -> float:
        """Spread Percentage
        "Peak-to-peak spread percentage."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Spread Percentage')
        return val

    @spread_percentage.setter
    def spread_percentage(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Spread Percentage={value}'])

    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum
        "Value should be a full file path."
        """
        val = self._get_property('Imported Spectrum')
        return val

    @imported_spectrum.setter
    def imported_spectrum(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Imported Spectrum={value}'])

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
        val = self._convert_from_internal_units(float(val), "Resistance")
        return val

    @system_impedance.setter
    def system_impedance(self, value : float|str):
        value = self._convert_to_internal_units(value, "Resistance")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'System Impedance={value}'])

    @property
    def advanced_extraction_params(self) -> bool:
        """Advanced Extraction Params
        "Show/hide advanced extraction params."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Advanced Extraction Params')
        val = (val == 'true')
        return val

    @advanced_extraction_params.setter
    def advanced_extraction_params(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Advanced Extraction Params={value}'])

    @property
    def nb_window_size(self) -> float:
        """NB Window Size
        "Window size for computing the moving average during narrowband signal detection."
        "Value should be greater than 3."
        """
        val = self._get_property('NB Window Size')
        return val

    @nb_window_size.setter
    def nb_window_size(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'NB Window Size={value}'])

    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor
        "Reduces the number of frequency points used for the broadband noise."
        "Value should be greater than 1."
        """
        val = self._get_property('BB Smoothing Factor')
        return val

    @bb_smoothing_factor.setter
    def bb_smoothing_factor(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'BB Smoothing Factor={value}'])

    @property
    def nb_detector_threshold(self) -> float:
        """NB Detector Threshold
        "Narrowband Detector threshold standard deviation."
        "Value should be between 2 and 10."
        """
        val = self._get_property('NB Detector Threshold')
        return val

    @nb_detector_threshold.setter
    def nb_detector_threshold(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'NB Detector Threshold={value}'])

    class AlgorithmOption(Enum):
            FFT = "FFT"
            FOURIER_TRANSFORM = "Fourier Transform"

    @property
    def algorithm(self) -> AlgorithmOption:
        """Algorithm
        "Algorithm used to transform the imported time domain spectrum."
        "        """
        val = self._get_property('Algorithm')
        val = self.AlgorithmOption[val.upper()]
        return val

    @algorithm.setter
    def algorithm(self, value: AlgorithmOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Algorithm={value.value}'])

    @property
    def start_time(self) -> float:
        """Start Time
        "Initial time of the imported spectrum."
        "Value should be greater than 0."
        """
        val = self._get_property('Start Time')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @start_time.setter
    def start_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Start Time={value}'])

    @property
    def stop_time(self) -> float:
        """Stop Time
        "Final time of the imported time domain spectrum."
        "        """
        val = self._get_property('Stop Time')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @stop_time.setter
    def stop_time(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Stop Time={value}'])

    @property
    def max_frequency(self) -> float:
        """Max Frequency
        "Frequency cutoff of the imported time domain spectrum."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Frequency')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @max_frequency.setter
    def max_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Max Frequency={value}'])

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
        val = self.WindowTypeOption[val.upper()]
        return val

    @window_type.setter
    def window_type(self, value: WindowTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Window Type={value.value}'])

    @property
    def kaiser_parameter(self) -> float:
        """Kaiser Parameter
        "Shape factor applied to the transform."
        "Value should be greater than 0."
        """
        val = self._get_property('Kaiser Parameter')
        return val

    @kaiser_parameter.setter
    def kaiser_parameter(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Kaiser Parameter={value}'])

    @property
    def adjust_coherent_gain(self) -> bool:
        """Adjust Coherent Gain
        "Shape factor applied to the transform."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adjust Coherent Gain')
        val = (val == 'true')
        return val

    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Adjust Coherent Gain={value}'])

    @property
    def data_rate(self) -> float:
        """Data Rate
        "Maximum data rate: helps determine shape of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Data Rate')
        val = self._convert_from_internal_units(float(val), "Data Rate")
        return val

    @data_rate.setter
    def data_rate(self, value : float|str):
        value = self._convert_to_internal_units(value, "Data Rate")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Data Rate={value}'])

    @property
    def num_of_bits(self) -> int:
        """Num of Bits
        "Length of the Pseudo Random Binary Sequence."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('Num of Bits')
        return val

    @num_of_bits.setter
    def num_of_bits(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Num of Bits={value}'])

    @property
    def use_envelope(self) -> bool:
        """Use Envelope
        "Model the waveform as a worst case envelope.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Envelope')
        val = (val == 'true')
        return val

    @use_envelope.setter
    def use_envelope(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Use Envelope={value}'])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Min Pts/Null={value}'])

    @property
    def delay_skew(self) -> float:
        """Delay Skew
        "Delay Skew of the differential signal pairs."
        "Value should be greater than 0."
        """
        val = self._get_property('Delay Skew')
        val = self._convert_from_internal_units(float(val), "Time")
        return val

    @delay_skew.setter
    def delay_skew(self, value : float|str):
        value = self._convert_to_internal_units(value, "Time")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Delay Skew={value}'])

