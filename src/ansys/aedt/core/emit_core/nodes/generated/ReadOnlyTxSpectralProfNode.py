from ..EmitNode import *

class ReadOnlyTxSpectralProfNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    class SpectrumTypeOption(Enum):
            BOTH = "Narrowband & Broadband"
            BROADBANDONLY = "Broadband Only"

    @property
    def spectrum_type(self) -> SpectrumTypeOption:
        """Spectrum Type
        "Specifies EMI Margins to calculate."
        "        """
        val = self._get_property('Spectrum Type')
        val = self.SpectrumTypeOption[val.upper()]
        return val

    class TxPowerOption(Enum):
            PEAK_POWER = "Peak Power"
            AVERAGE_POWER = "Average Power"

    @property
    def tx_power(self) -> TxPowerOption:
        """Tx Power
        "Method used to specify the power."
        "        """
        val = self._get_property('Tx Power')
        val = self.TxPowerOption[val.upper()]
        return val

    @property
    def peak_power(self) -> float:
        """Peak Power
        "Tx's carrier frequency peak power."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Peak Power')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @property
    def average_power(self) -> float:
        """Average Power
        "Tx's fundamental level specified by average power."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Average Power')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @property
    def include_phase_noise(self) -> bool:
        """Include Phase Noise
        "Include oscillator phase noise in Tx spectral profile."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include Phase Noise')
        val = (val == 'true')
        return val

    @property
    def tx_broadband_noise(self) -> float:
        """Tx Broadband Noise
        "Transmitters broadband noise level."
        "Value should be less than 1000."
        """
        val = self._get_property('Tx Broadband Noise')
        return val

    class HarmonicTaperOption(Enum):
            CONSTANT = "Constant"
            MIL_STD_461G = "MIL-STD-461G"
            MIL_STD_461G_NAVY = "MIL-STD-461G Navy"
            DUFF_MODEL = "Duff Model"

    @property
    def harmonic_taper(self) -> HarmonicTaperOption:
        """Harmonic Taper
        "Taper type used to set amplitude of harmonics."
        "        """
        val = self._get_property('Harmonic Taper')
        val = self.HarmonicTaperOption[val.upper()]
        return val

    @property
    def harmonic_amplitude(self) -> float:
        """Harmonic Amplitude
        "Amplitude (relative to the carrier power) of harmonics."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Harmonic Amplitude')
        return val

    @property
    def harmonic_slope(self) -> float:
        """Harmonic Slope
        "Rate of decrease for harmonics' amplitudes (dB/decade)."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Harmonic Slope')
        return val

    @property
    def harmonic_intercept(self) -> float:
        """Harmonic Intercept
        "Amplitude intercept at the fundamental (dBc)."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Harmonic Intercept')
        return val

    @property
    def enable_harmonic_bw_expansion(self) -> bool:
        """Enable Harmonic BW Expansion
        "If (True), bandwidth of harmonics increases proportional to the harmonic number."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Harmonic BW Expansion')
        val = (val == 'true')
        return val

    @property
    def number_of_harmonics(self) -> int:
        """Number of Harmonics
        "Maximum number of harmonics modeled."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('Number of Harmonics')
        return val

    @property
    def _2nd_harmonic_level(self) -> float:
        """2nd Harmonic Level
        "Amplitude (relative to the carrier power) of the 2nd harmonic."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('2nd Harmonic Level')
        return val

    @property
    def _3rd_harmonic_level(self) -> float:
        """3rd Harmonic Level
        "Amplitude (relative to the carrier power) of the 3rd harmonic."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('3rd Harmonic Level')
        return val

    @property
    def other_harmonic_levels(self) -> float:
        """Other Harmonic Levels
        "Amplitude (relative to the carrier power) of the higher order harmonics."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Other Harmonic Levels')
        return val

    @property
    def perform_tx_intermod_analysis(self) -> bool:
        """Perform Tx Intermod Analysis
        "Performs a non-linear intermod analysis for the Tx."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Perform Tx Intermod Analysis')
        val = (val == 'true')
        return val

    @property
    def internal_amp_gain(self) -> float:
        """Internal Amp Gain
        "Internal Tx Amplifier's Gain."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Internal Amp Gain')
        return val

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Internal Tx Amplifier's noise figure."
        "Value should be between 0 and 50."
        """
        val = self._get_property('Noise Figure')
        return val

    @property
    def amplifier_saturation_level(self) -> float:
        """Amplifier Saturation Level
        "Internal Tx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Amplifier Saturation Level')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @property
    def p1_db_point_ref_input_(self) -> float:
        """P1-dB Point, Ref. Input 
        "Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB saturates the internal Tx amplifier."
        "Value should be between -200 and 200."
        """
        val = self._get_property('P1-dB Point, Ref. Input ')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "Internal Tx Amplifier's 3rd order intercept point."
        "Value should be between -200 and 200."
        """
        val = self._get_property('IP3, Ref. Input')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Internal Tx Amplifier's Reverse Isolation."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Reverse Isolation')
        return val

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Internal Tx Amplifier's maximum intermod order to compute."
        "Value should be between 3 and 20."
        """
        val = self._get_property('Max Intermod Order')
        return val

