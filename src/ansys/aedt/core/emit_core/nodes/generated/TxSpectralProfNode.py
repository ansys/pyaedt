from ..GenericEmitNode import *
class TxSpectralProfNode(GenericEmitNode):
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
    def spectrum_type(self):
        """Spectrum Type
        "Specifies EMI Margins to calculate."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spectrum Type')
        key_val_pair = [i for i in props if 'Spectrum Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @spectrum_type.setter
    def spectrum_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spectrum Type=' + value])
    class SpectrumTypeOption(Enum):
            BOTH = "Narrowband & Broadband"
            BROADBANDONLY = "Broadband Only"

    @property
    def tx_power(self):
        """Tx Power
        "Method used to specify the power."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Power')
        key_val_pair = [i for i in props if 'Tx Power=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @tx_power.setter
    def tx_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Power=' + value])
    class TxPowerOption(Enum):
            PEAK_POWER = "Peak Power"
            AVERAGE_POWER = "Average Power"

    @property
    def peak_power(self) -> float:
        """Peak Power
        "Tx's carrier frequency peak power."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Peak Power')
        key_val_pair = [i for i in props if 'Peak Power=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @peak_power.setter
    def peak_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Peak Power=' + value])

    @property
    def average_power(self) -> float:
        """Average Power
        "Tx's fundamental level specified by average power."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Average Power')
        key_val_pair = [i for i in props if 'Average Power=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @average_power.setter
    def average_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Average Power=' + value])

    @property
    def output_voltage_peak(self) -> float:
        """Output Voltage Peak
        "Output High Voltage Level: maximum voltage of the digital signal."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Output Voltage Peak')
        key_val_pair = [i for i in props if 'Output Voltage Peak=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @output_voltage_peak.setter
    def output_voltage_peak(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Output Voltage Peak=' + value])

    @property
    def include_phase_noise(self) -> bool:
        """Include Phase Noise
        "Include oscillator phase noise in Tx spectral profile."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include Phase Noise')
        key_val_pair = [i for i in props if 'Include Phase Noise=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @include_phase_noise.setter
    def include_phase_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include Phase Noise=' + value])

    @property
    def tx_broadband_noise(self) -> float:
        """Tx Broadband Noise
        "Transmitters broadband noise level."
        "Value should be less than 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Broadband Noise')
        key_val_pair = [i for i in props if 'Tx Broadband Noise=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @tx_broadband_noise.setter
    def tx_broadband_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Broadband Noise=' + value])

    @property
    def harmonic_taper(self):
        """Harmonic Taper
        "Taper type used to set amplitude of harmonics."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Taper')
        key_val_pair = [i for i in props if 'Harmonic Taper=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @harmonic_taper.setter
    def harmonic_taper(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Taper=' + value])
    class HarmonicTaperOption(Enum):
            CONSTANT = "Constant"
            MIL_STD_461G = "MIL-STD-461G"
            MIL_STD_461G_NAVY = "MIL-STD-461G Navy"
            DUFF_MODEL = "Duff Model"

    @property
    def harmonic_amplitude(self) -> float:
        """Harmonic Amplitude
        "Amplitude (relative to the carrier power) of harmonics."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Amplitude')
        key_val_pair = [i for i in props if 'Harmonic Amplitude=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @harmonic_amplitude.setter
    def harmonic_amplitude(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Amplitude=' + value])

    @property
    def harmonic_slope(self) -> float:
        """Harmonic Slope
        "Rate of decrease for harmonics' amplitudes (dB/decade)."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Slope')
        key_val_pair = [i for i in props if 'Harmonic Slope=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @harmonic_slope.setter
    def harmonic_slope(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Slope=' + value])

    @property
    def harmonic_intercept(self) -> float:
        """Harmonic Intercept
        "Amplitude intercept at the fundamental (dBc)."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Intercept')
        key_val_pair = [i for i in props if 'Harmonic Intercept=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @harmonic_intercept.setter
    def harmonic_intercept(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Intercept=' + value])

    @property
    def enable_harmonic_bw_expansion(self) -> bool:
        """Enable Harmonic BW Expansion
        "If (True), bandwidth of harmonics increases proportional to the harmonic number."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Harmonic BW Expansion')
        key_val_pair = [i for i in props if 'Enable Harmonic BW Expansion=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enable_harmonic_bw_expansion.setter
    def enable_harmonic_bw_expansion(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Harmonic BW Expansion=' + value])

    @property
    def number_of_harmonics(self) -> int:
        """Number of Harmonics
        "Maximum number of harmonics modeled."
        "Value should be between 1 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Harmonics')
        key_val_pair = [i for i in props if 'Number of Harmonics=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @number_of_harmonics.setter
    def number_of_harmonics(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Number of Harmonics=' + value])

    @property
    def _2nd_harmonic_level(self) -> float:
        """2nd Harmonic Level
        "Amplitude (relative to the carrier power) of the 2nd harmonic."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'2nd Harmonic Level')
        key_val_pair = [i for i in props if '2nd Harmonic Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_2nd_harmonic_level.setter
    def _2nd_harmonic_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['2nd Harmonic Level=' + value])

    @property
    def _3rd_harmonic_level(self) -> float:
        """3rd Harmonic Level
        "Amplitude (relative to the carrier power) of the 3rd harmonic."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'3rd Harmonic Level')
        key_val_pair = [i for i in props if '3rd Harmonic Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_3rd_harmonic_level.setter
    def _3rd_harmonic_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['3rd Harmonic Level=' + value])

    @property
    def other_harmonic_levels(self) -> float:
        """Other Harmonic Levels
        "Amplitude (relative to the carrier power) of the higher order harmonics."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Other Harmonic Levels')
        key_val_pair = [i for i in props if 'Other Harmonic Levels=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @other_harmonic_levels.setter
    def other_harmonic_levels(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Other Harmonic Levels=' + value])

    @property
    def perform_tx_intermod_analysis(self) -> bool:
        """Perform Tx Intermod Analysis
        "Performs a non-linear intermod analysis for the Tx."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Perform Tx Intermod Analysis')
        key_val_pair = [i for i in props if 'Perform Tx Intermod Analysis=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @perform_tx_intermod_analysis.setter
    def perform_tx_intermod_analysis(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Perform Tx Intermod Analysis=' + value])

    @property
    def internal_amp_gain(self) -> float:
        """Internal Amp Gain
        "Internal Tx Amplifier's Gain."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Internal Amp Gain')
        key_val_pair = [i for i in props if 'Internal Amp Gain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @internal_amp_gain.setter
    def internal_amp_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Internal Amp Gain=' + value])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Internal Tx Amplifier's noise figure."
        "Value should be between 0 and 50."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Figure')
        key_val_pair = [i for i in props if 'Noise Figure=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @noise_figure.setter
    def noise_figure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def amplifier_saturation_level(self) -> float:
        """Amplifier Saturation Level
        "Internal Tx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Amplifier Saturation Level')
        key_val_pair = [i for i in props if 'Amplifier Saturation Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @amplifier_saturation_level.setter
    def amplifier_saturation_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Amplifier Saturation Level=' + value])

    @property
    def _1_db_point_ref_input_(self) -> float:
        """1-dB Point, Ref. Input 
        "Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB saturates the internal Tx amplifier."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1-dB Point, Ref. Input ')
        key_val_pair = [i for i in props if '1-dB Point, Ref. Input =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_1_db_point_ref_input_.setter
    def _1_db_point_ref_input_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input =' + value])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "Internal Tx Amplifier's 3rd order intercept point."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'IP3, Ref. Input')
        key_val_pair = [i for i in props if 'IP3, Ref. Input=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @ip3_ref_input.setter
    def ip3_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Internal Tx Amplifier's Reverse Isolation."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Reverse Isolation')
        key_val_pair = [i for i in props if 'Reverse Isolation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @reverse_isolation.setter
    def reverse_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Internal Tx Amplifier's maximum intermod order to compute."
        "Value should be between 3 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Intermod Order')
        key_val_pair = [i for i in props if 'Max Intermod Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_intermod_order.setter
    def max_intermod_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

