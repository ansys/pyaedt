class Node_TxSpectralProfNode(GenericEmitNode):
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
    def get_spectrum_type(self):
        """Spectrum Type
        "Specifies EMI Margins to calculate."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spectrum Type')
    def set_spectrum_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spectrum Type=' + value])
    class SpectrumTypeOption(Enum):
        (
            BOTH = "Narrowband & Broadband"
            BROADBANDONLY = "Broadband Only"
        )

    @property
    def get_tx_power(self):
        """Tx Power
        "Method used to specify the power."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Power')
    def set_tx_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Power=' + value])
    class TxPowerOption(Enum):
        (
            PEAK_POWER = "Peak Power"
            AVERAGE_POWER = "Average Power"
        )

    @property
    def get_peak_power(self):
        """Peak Power
        "Tx's carrier frequency peak power."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Peak Power')
    def set_peak_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Peak Power=' + value])

    @property
    def get_average_power(self):
        """Average Power
        "Tx's fundamental level specified by average power."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Average Power')
    def set_average_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Average Power=' + value])

    @property
    def get_output_voltage_peak(self):
        """Output Voltage Peak
        "Output High Voltage Level: maximum voltage of the digital signal."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Output Voltage Peak')
    def set_output_voltage_peak(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Output Voltage Peak=' + value])

    @property
    def get_include_phase_noise(self):
        """Include Phase Noise
        "Include oscillator phase noise in Tx spectral profile."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include Phase Noise')
    def set_include_phase_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include Phase Noise=' + value])

    @property
    def get_tx_broadband_noise(self):
        """Tx Broadband Noise
        "Transmitters broadband noise level."
        "Value should be less than 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Broadband Noise')
    def set_tx_broadband_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Broadband Noise=' + value])

    @property
    def get_harmonic_taper(self):
        """Harmonic Taper
        "Taper type used to set amplitude of harmonics."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Taper')
    def set_harmonic_taper(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Taper=' + value])
    class HarmonicTaperOption(Enum):
        (
            CONSTANT = "Constant"
            MIL_STD_461G = "MIL-STD-461G"
            MIL_STD_461G_NAVY = "MIL-STD-461G Navy"
            DUFF_MODEL = "Duff Model"
        )

    @property
    def get_harmonic_amplitude(self):
        """Harmonic Amplitude
        "Amplitude (relative to the carrier power) of harmonics."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Amplitude')
    def set_harmonic_amplitude(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Amplitude=' + value])

    @property
    def get_harmonic_slope(self):
        """Harmonic Slope
        "Rate of decrease for harmonics' amplitudes (dB/decade)."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Slope')
    def set_harmonic_slope(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Slope=' + value])

    @property
    def get_harmonic_intercept(self):
        """Harmonic Intercept
        "Amplitude intercept at the fundamental (dBc)."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Harmonic Intercept')
    def set_harmonic_intercept(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Harmonic Intercept=' + value])

    @property
    def get_enable_harmonic_bw_expansion(self):
        """Enable Harmonic BW Expansion
        "If (True), bandwidth of harmonics increases proportional to the harmonic number."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Harmonic BW Expansion')
    def set_enable_harmonic_bw_expansion(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Harmonic BW Expansion=' + value])

    @property
    def get_number_of_harmonics(self):
        """Number of Harmonics
        "Maximum number of harmonics modeled."
        "Value should be between 1 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Harmonics')
    def set_number_of_harmonics(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Number of Harmonics=' + value])

    @property
    def get__2nd_harmonic_level(self):
        """2nd Harmonic Level
        "Amplitude (relative to the carrier power) of the 2nd harmonic."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'2nd Harmonic Level')
    def set__2nd_harmonic_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['2nd Harmonic Level=' + value])

    @property
    def get__3rd_harmonic_level(self):
        """3rd Harmonic Level
        "Amplitude (relative to the carrier power) of the 3rd harmonic."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'3rd Harmonic Level')
    def set__3rd_harmonic_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['3rd Harmonic Level=' + value])

    @property
    def get_other_harmonic_levels(self):
        """Other Harmonic Levels
        "Amplitude (relative to the carrier power) of the higher order harmonics."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Other Harmonic Levels')
    def set_other_harmonic_levels(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Other Harmonic Levels=' + value])

    @property
    def get_perform_tx_intermod_analysis(self):
        """Perform Tx Intermod Analysis
        "Performs a non-linear intermod analysis for the Tx."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Perform Tx Intermod Analysis')
    def set_perform_tx_intermod_analysis(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Perform Tx Intermod Analysis=' + value])

    @property
    def get_internal_amp_gain(self):
        """Internal Amp Gain
        "Internal Tx Amplifier's Gain."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Internal Amp Gain')
    def set_internal_amp_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Internal Amp Gain=' + value])

    @property
    def get_noise_figure(self):
        """Noise Figure
        "Internal Tx Amplifier's noise figure."
        "Value should be between 0 and 50."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Figure')
    def set_noise_figure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def get_amplifier_saturation_level(self):
        """Amplifier Saturation Level
        "Internal Tx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Amplifier Saturation Level')
    def set_amplifier_saturation_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Amplifier Saturation Level=' + value])

    @property
    def get__1_db_point_ref_input_(self):
        """1-dB Point, Ref. Input 
        "Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB saturates the internal Tx amplifier."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1-dB Point, Ref. Input ')
    def set__1_db_point_ref_input_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input =' + value])

    @property
    def get_ip3_ref_input(self):
        """IP3, Ref. Input
        "Internal Tx Amplifier's 3rd order intercept point."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'IP3, Ref. Input')
    def set_ip3_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def get_reverse_isolation(self):
        """Reverse Isolation
        "Internal Tx Amplifier's Reverse Isolation."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Reverse Isolation')
    def set_reverse_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

    @property
    def get_max_intermod_order(self):
        """Max Intermod Order
        "Internal Tx Amplifier's maximum intermod order to compute."
        "Value should be between 3 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Intermod Order')
    def set_max_intermod_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

