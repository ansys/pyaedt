from ..EmitNode import *

class TxSpectralProfNode(EmitNode):
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
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    class SpectrumTypeOption(Enum):
            BOTH = "Narrowband & Broadband"
            BROADBANDONLY = "Broadband Only"

    @property
    def spectrum_type(self) -> SpectrumTypeOption:
        """Spectrum Type
        "Specifies EMI Margins to calculate."
        "        """
        val = self._get_property('Spectrum Type')
        val = self.SpectrumTypeOption[val]
        return val

    @spectrum_type.setter
    def spectrum_type(self, value: SpectrumTypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Spectrum Type=' + value.value])

    class TxPowerOption(Enum):
            PEAK_POWER = "Peak Power"
            AVERAGE_POWER = "Average Power"

    @property
    def tx_power(self) -> TxPowerOption:
        """Tx Power
        "Method used to specify the power."
        "        """
        val = self._get_property('Tx Power')
        val = self.TxPowerOption[val]
        return val

    @tx_power.setter
    def tx_power(self, value: TxPowerOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Tx Power=' + value.value])

    @property
    def peak_power(self) -> float:
        """Peak Power
        "Tx's carrier frequency peak power."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Peak Power')
        return val

    @peak_power.setter
    def peak_power(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Peak Power=' + value])

    @property
    def average_power(self) -> float:
        """Average Power
        "Tx's fundamental level specified by average power."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Average Power')
        return val

    @average_power.setter
    def average_power(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Average Power=' + value])

    @property
    def output_voltage_peak(self) -> float:
        """Output Voltage Peak
        "Output High Voltage Level: maximum voltage of the digital signal."
        "        """
        val = self._get_property('Output Voltage Peak')
        return val

    @output_voltage_peak.setter
    def output_voltage_peak(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Output Voltage Peak=' + value])

    @property
    def include_phase_noise(self) -> bool:
        """Include Phase Noise
        "Include oscillator phase noise in Tx spectral profile."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include Phase Noise')
        return val

    @include_phase_noise.setter
    def include_phase_noise(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Include Phase Noise=' + value])

    @property
    def tx_broadband_noise(self) -> float:
        """Tx Broadband Noise
        "Transmitters broadband noise level."
        "Value should be less than 1000."
        """
        val = self._get_property('Tx Broadband Noise')
        return val

    @tx_broadband_noise.setter
    def tx_broadband_noise(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Tx Broadband Noise=' + value])

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
        val = self.HarmonicTaperOption[val]
        return val

    @harmonic_taper.setter
    def harmonic_taper(self, value: HarmonicTaperOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Harmonic Taper=' + value.value])

    @property
    def harmonic_amplitude(self) -> float:
        """Harmonic Amplitude
        "Amplitude (relative to the carrier power) of harmonics."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Harmonic Amplitude')
        return val

    @harmonic_amplitude.setter
    def harmonic_amplitude(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Harmonic Amplitude=' + value])

    @property
    def harmonic_slope(self) -> float:
        """Harmonic Slope
        "Rate of decrease for harmonics' amplitudes (dB/decade)."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Harmonic Slope')
        return val

    @harmonic_slope.setter
    def harmonic_slope(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Harmonic Slope=' + value])

    @property
    def harmonic_intercept(self) -> float:
        """Harmonic Intercept
        "Amplitude intercept at the fundamental (dBc)."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Harmonic Intercept')
        return val

    @harmonic_intercept.setter
    def harmonic_intercept(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Harmonic Intercept=' + value])

    @property
    def enable_harmonic_bw_expansion(self) -> bool:
        """Enable Harmonic BW Expansion
        "If (True), bandwidth of harmonics increases proportional to the harmonic number."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Harmonic BW Expansion')
        return val

    @enable_harmonic_bw_expansion.setter
    def enable_harmonic_bw_expansion(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enable Harmonic BW Expansion=' + value])

    @property
    def number_of_harmonics(self) -> int:
        """Number of Harmonics
        "Maximum number of harmonics modeled."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('Number of Harmonics')
        return val

    @number_of_harmonics.setter
    def number_of_harmonics(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Number of Harmonics=' + value])

    @property
    def _2nd_harmonic_level(self) -> float:
        """2nd Harmonic Level
        "Amplitude (relative to the carrier power) of the 2nd harmonic."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('2nd Harmonic Level')
        return val

    @_2nd_harmonic_level.setter
    def _2nd_harmonic_level(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['2nd Harmonic Level=' + value])

    @property
    def _3rd_harmonic_level(self) -> float:
        """3rd Harmonic Level
        "Amplitude (relative to the carrier power) of the 3rd harmonic."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('3rd Harmonic Level')
        return val

    @_3rd_harmonic_level.setter
    def _3rd_harmonic_level(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['3rd Harmonic Level=' + value])

    @property
    def other_harmonic_levels(self) -> float:
        """Other Harmonic Levels
        "Amplitude (relative to the carrier power) of the higher order harmonics."
        "Value should be between -1000 and 0."
        """
        val = self._get_property('Other Harmonic Levels')
        return val

    @other_harmonic_levels.setter
    def other_harmonic_levels(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Other Harmonic Levels=' + value])

    @property
    def perform_tx_intermod_analysis(self) -> bool:
        """Perform Tx Intermod Analysis
        "Performs a non-linear intermod analysis for the Tx."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Perform Tx Intermod Analysis')
        return val

    @perform_tx_intermod_analysis.setter
    def perform_tx_intermod_analysis(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Perform Tx Intermod Analysis=' + value])

    @property
    def internal_amp_gain(self) -> float:
        """Internal Amp Gain
        "Internal Tx Amplifier's Gain."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Internal Amp Gain')
        return val

    @internal_amp_gain.setter
    def internal_amp_gain(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Internal Amp Gain=' + value])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Internal Tx Amplifier's noise figure."
        "Value should be between 0 and 50."
        """
        val = self._get_property('Noise Figure')
        return val

    @noise_figure.setter
    def noise_figure(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def amplifier_saturation_level(self) -> float:
        """Amplifier Saturation Level
        "Internal Tx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Amplifier Saturation Level')
        return val

    @amplifier_saturation_level.setter
    def amplifier_saturation_level(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Amplifier Saturation Level=' + value])

    @property
    def _1_db_point_ref_input_(self) -> float:
        """1-dB Point, Ref. Input 
        "Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB saturates the internal Tx amplifier."
        "Value should be between -200 and 200."
        """
        val = self._get_property('1-dB Point, Ref. Input ')
        return val

    @_1_db_point_ref_input_.setter
    def _1_db_point_ref_input_(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input =' + value])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "Internal Tx Amplifier's 3rd order intercept point."
        "Value should be between -200 and 200."
        """
        val = self._get_property('IP3, Ref. Input')
        return val

    @ip3_ref_input.setter
    def ip3_ref_input(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Internal Tx Amplifier's Reverse Isolation."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Reverse Isolation')
        return val

    @reverse_isolation.setter
    def reverse_isolation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Internal Tx Amplifier's maximum intermod order to compute."
        "Value should be between 3 and 20."
        """
        val = self._get_property('Max Intermod Order')
        return val

    @max_intermod_order.setter
    def max_intermod_order(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

