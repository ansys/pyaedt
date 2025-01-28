class Node_RxSusceptibilityProfNode(GenericEmitNode):
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
    def get_sensitivity_units(self):
        """Sensitivity Units
        "Units to use for the Rx Sensitivity."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Sensitivity Units')
    def set_sensitivity_units(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Sensitivity Units=' + value])
    class SensitivityUnitsOption(Enum):
        (
            DBM = "dBm"
            DBUV = "dBuV"
            MILLIWATTS = "milliwatts"
            MICROVOLTS = "microvolts"
        )

    @property
    def get_min_receive_signal_pwr_(self):
        """Min. Receive Signal Pwr 
        "Received signal power level at the Rx's antenna terminal."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min. Receive Signal Pwr ')
    def set_min_receive_signal_pwr_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min. Receive Signal Pwr =' + value])

    @property
    def get_snr_at_rx_signal_pwr(self):
        """SNR at Rx Signal Pwr
        "Signal-to-Noise Ratio (dB) at specified received signal power at the Rx's antenna terminal."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SNR at Rx Signal Pwr')
    def set_snr_at_rx_signal_pwr(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['SNR at Rx Signal Pwr=' + value])

    @property
    def get_processing_gain(self):
        """Processing Gain
        "Rx processing gain (dB) of (optional) despreader."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Processing Gain')
    def set_processing_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Processing Gain=' + value])

    @property
    def get_apply_pg_to_narrowband_only(self):
        """Apply PG to Narrowband Only
        "Processing gain captures the despreading effect and applies to NB signals only (not BB noise) when enabled."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Apply PG to Narrowband Only')
    def set_apply_pg_to_narrowband_only(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Apply PG to Narrowband Only=' + value])

    @property
    def get_saturation_level(self):
        """Saturation Level
        "Rx input saturation level."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Saturation Level')
    def set_saturation_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Saturation Level=' + value])

    @property
    def get_rx_noise_figure(self):
        """Rx Noise Figure
        "Rx noise figure (dB)."
        "Value should be between 0 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Rx Noise Figure')
    def set_rx_noise_figure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Rx Noise Figure=' + value])

    @property
    def get_receiver_sensitivity_(self):
        """Receiver Sensitivity 
        "Rx minimum sensitivity level (dBm)."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Receiver Sensitivity ')
    def set_receiver_sensitivity_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Receiver Sensitivity =' + value])

    @property
    def get_snrsinad_at_sensitivity_(self):
        """SNR/SINAD at Sensitivity 
        "SNR or SINAD at the specified sensitivity level."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SNR/SINAD at Sensitivity ')
    def set_snrsinad_at_sensitivity_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['SNR/SINAD at Sensitivity =' + value])

    @property
    def get_perform_rx_intermod_analysis(self):
        """Perform Rx Intermod Analysis
        "Performs a non-linear intermod analysis for the Rx."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Perform Rx Intermod Analysis')
    def set_perform_rx_intermod_analysis(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Perform Rx Intermod Analysis=' + value])

    @property
    def get_amplifier_saturation_level(self):
        """Amplifier Saturation Level
        "Internal Rx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Amplifier Saturation Level')
    def set_amplifier_saturation_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Amplifier Saturation Level=' + value])

    @property
    def get__1_db_point_ref_input_(self):
        """1-dB Point, Ref. Input 
        "Rx's 1 dB Compression Point - total power > P1dB saturates the receiver."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1-dB Point, Ref. Input ')
    def set__1_db_point_ref_input_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input =' + value])

    @property
    def get_ip3_ref_input(self):
        """IP3, Ref. Input
        "Internal Rx Amplifier's 3rd order intercept point."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'IP3, Ref. Input')
    def set_ip3_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def get_max_intermod_order(self):
        """Max Intermod Order
        "Internal Rx Amplifier's maximum intermod order to compute."
        "Value should be between 3 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Intermod Order')
    def set_max_intermod_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

