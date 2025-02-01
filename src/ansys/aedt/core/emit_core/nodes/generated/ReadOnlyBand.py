from ..EmitNode import *

class ReadOnlyBand(EmitNode):
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
    def port(self):
        """Port
        "Radio Port associated with this Band."
        "        """
        val = self._get_property('Port')
        return val
    @property
    def use_dd_1494_mode(self) -> bool:
        """Use DD-1494 Mode
        "Uses DD-1494 parameters to define the Tx/Rx spectrum."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use DD-1494 Mode')
        return val
    @property
    def use_emission_designator(self) -> bool:
        """Use Emission Designator
        "Uses the Emission Designator to define the bandwidth and modulation."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Emission Designator')
        return val
    @property
    def emission_designator(self) -> str:
        """Emission Designator
        "Enter the Emission Designator to define the bandwidth and modulation."
        "        """
        val = self._get_property('Emission Designator')
        return val
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
    @property
    def channel_bandwidth(self) -> float:
        """Channel Bandwidth
        "Channel Bandwidth."
        "Value should be greater than 1."
        """
        val = self._get_property('Channel Bandwidth')
        return val
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
    @property
    def max_modulating_freq(self) -> float:
        """Max Modulating Freq.
        "Maximum modulating frequency: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Max Modulating Freq.')
        return val
    @property
    def modulation_index(self) -> float:
        """Modulation Index
        "AM modulation index: helps determine spectral profile."
        "Value should be between 0.01 and 1."
        """
        val = self._get_property('Modulation Index')
        return val
    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Freq. Deviation')
        return val
    @property
    def bit_rate(self) -> float:
        """Bit Rate
        "Maximum bit rate: helps determine width of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Bit Rate')
        return val
    @property
    def sidelobes(self) -> int:
        """Sidelobes
        "Number of sidelobes in spectral profile."
        "Value should be greater than 0."
        """
        val = self._get_property('Sidelobes')
        return val
    @property
    def freq_deviation_(self) -> float:
        """Freq. Deviation 
        "FSK frequency deviation: helps determine spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Freq. Deviation ')
        return val
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
    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "First frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Start Frequency')
        return val
    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Last frequency for this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Stop Frequency')
        return val
    @property
    def channel_spacing(self) -> float:
        """Channel Spacing
        "Spacing between channels within this band."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Channel Spacing')
        return val
    @property
    def tx_offset(self) -> float:
        """Tx Offset
        "Frequency offset between Tx and Rx channels."
        "Value should be less than 1e+11."
        """
        val = self._get_property('Tx Offset')
        return val
    @property
    def clock_duty_cycle(self) -> float:
        """Clock Duty Cycle
        "Clock signals duty cycle."
        "Value should be between 0.001 and 1."
        """
        val = self._get_property('Clock Duty Cycle')
        return val
    @property
    def clock_risefall_time(self) -> float:
        """Clock Rise/Fall Time
        "Clock signals rise/fall time."
        "Value should be greater than 0."
        """
        val = self._get_property('Clock Rise/Fall Time')
        return val
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
    @property
    def spread_percentage(self) -> float:
        """Spread Percentage
        "Peak-to-peak spread percentage."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Spread Percentage')
        return val
    @property
    def imported_spectrum(self) -> str:
        """Imported Spectrum
        "Value should be a full file path."
        """
        val = self._get_property('Imported Spectrum')
        return val
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
    @property
    def advanced_extraction_params(self) -> bool:
        """Advanced Extraction Params
        "Show/hide advanced extraction params."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Advanced Extraction Params')
        return val
    @property
    def nb_window_size(self) -> float:
        """NB Window Size
        "Window size for computing the moving average during narrowband signal detection."
        "Value should be greater than 3."
        """
        val = self._get_property('NB Window Size')
        return val
    @property
    def bb_smoothing_factor(self) -> float:
        """BB Smoothing Factor
        "Reduces the number of frequency points used for the broadband noise."
        "Value should be greater than 1."
        """
        val = self._get_property('BB Smoothing Factor')
        return val
    @property
    def nb_detector_threshold(self) -> float:
        """NB Detector Threshold
        "Narrowband Detector threshold standard deviation."
        "Value should be between 2 and 10."
        """
        val = self._get_property('NB Detector Threshold')
        return val
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
    @property
    def start(self) -> float:
        """Start
        "Initial time of the imported spectrum."
        "Value should be greater than 0."
        """
        val = self._get_property('Start')
        return val
    @property
    def stop(self) -> float:
        """Stop
        "Final time of the imported time domain spectrum."
        "        """
        val = self._get_property('Stop')
        return val
    @property
    def max_frequency(self) -> float:
        """Max Frequency
        "Frequency cutoff of the imported time domain spectrum."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Frequency')
        return val
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
    @property
    def kaiser_parameter(self) -> float:
        """Kaiser Parameter
        "Shape factor applied to the transform."
        "Value should be greater than 0."
        """
        val = self._get_property('Kaiser Parameter')
        return val
    @property
    def adjust_coherent_gain(self) -> bool:
        """Adjust Coherent Gain
        "Shape factor applied to the transform."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adjust Coherent Gain')
        return val
    @property
    def data_rate(self) -> float:
        """Data Rate
        "Maximum data rate: helps determine shape of spectral profile."
        "Value should be greater than 1."
        """
        val = self._get_property('Data Rate')
        return val
    @property
    def _of_bits(self) -> int:
        """# of Bits
        "Length of the Pseudo Random Binary Sequence."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('# of Bits')
        return val
    @property
    def use_envelope(self) -> bool:
        """Use Envelope
        "Model the waveform as a worst case envelope.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Envelope')
        return val
    @property
    def min_ptsnull(self) -> int:
        """Min Pts/Null
        "Minimum number of points to use between each null frequency."
        "Value should be between 2 and 50."
        """
        val = self._get_property('Min Pts/Null')
        return val
    @property
    def delay_skew(self) -> float:
        """Delay Skew
        "Delay Skew of the differential signal pairs."
        "Value should be greater than 0."
        """
        val = self._get_property('Delay Skew')
        return val
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
    @property
    def hopping_radar(self) -> bool:
        """Hopping Radar
        "True for hopping radars; false otherwise."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Hopping Radar')
        return val
    @property
    def post_october_2020_procurement(self) -> bool:
        """Post October 2020 Procurement
        "Procurement date: helps determine spectral profile, particularly the roll-off."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Post October 2020 Procurement')
        return val
    @property
    def hop_range_min_freq(self) -> float:
        """Hop Range Min Freq
        "Sets the minimum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Hop Range Min Freq')
        return val
    @property
    def hop_range_max_freq(self) -> float:
        """Hop Range Max Freq
        "Sets the maximum frequency of the hopping range."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Hop Range Max Freq')
        return val
    @property
    def pulse_duration(self) -> float:
        """Pulse Duration
        "Pulse duration."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Duration')
        return val
    @property
    def pulse_rise_time(self) -> float:
        """Pulse Rise Time
        "Pulse rise time."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Rise Time')
        return val
    @property
    def pulse_fall_time(self) -> float:
        """Pulse Fall Time
        "Pulse fall time."
        "Value should be greater than 0."
        """
        val = self._get_property('Pulse Fall Time')
        return val
    @property
    def pulse_repetition_rate(self) -> float:
        """Pulse Repetition Rate
        "Pulse repetition rate [pulses/sec]."
        "Value should be greater than 1."
        """
        val = self._get_property('Pulse Repetition Rate')
        return val
    @property
    def number_of_chips(self) -> float:
        """Number of Chips
        "Total number of chips (subpulses) contained in the pulse."
        "Value should be greater than 1."
        """
        val = self._get_property('Number of Chips')
        return val
    @property
    def pulse_compression_ratio(self) -> float:
        """Pulse Compression Ratio
        "Pulse compression ratio."
        "Value should be greater than 1."
        """
        val = self._get_property('Pulse Compression Ratio')
        return val
    @property
    def fm_chirp_period(self) -> float:
        """FM Chirp Period
        "FM Chirp period for the FM/CW radar."
        "Value should be greater than 0."
        """
        val = self._get_property('FM Chirp Period')
        return val
    @property
    def fm_freq_deviation(self) -> float:
        """FM Freq Deviation
        "Total frequency deviation for the carrier frequency for the FM/CW radar."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('FM Freq Deviation')
        return val
    @property
    def fm_freq_dev_bandwidth(self) -> float:
        """FM Freq Dev Bandwidth
        "Bandwidth of freq deviation for FM modulated pulsed waveform (total freq shift during pulse duration)."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('FM Freq Dev Bandwidth')
        return val
