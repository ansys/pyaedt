from ..GenericEmitNode import *
class ReadOnlyRxSusceptibilityProfNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def sensitivity_units(self):
        """Sensitivity Units
        "Units to use for the Rx Sensitivity."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Sensitivity Units')
        key_val_pair = [i for i in props if 'Sensitivity Units=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class SensitivityUnitsOption(Enum):
            DBM = "dBm"
            DBUV = "dBuV"
            MILLIWATTS = "milliwatts"
            MICROVOLTS = "microvolts"

    @property
    def min_receive_signal_pwr_(self) -> float:
        """Min. Receive Signal Pwr 
        "Received signal power level at the Rx's antenna terminal."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min. Receive Signal Pwr ')
        key_val_pair = [i for i in props if 'Min. Receive Signal Pwr =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def snr_at_rx_signal_pwr(self) -> float:
        """SNR at Rx Signal Pwr
        "Signal-to-Noise Ratio (dB) at specified received signal power at the Rx's antenna terminal."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SNR at Rx Signal Pwr')
        key_val_pair = [i for i in props if 'SNR at Rx Signal Pwr=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def processing_gain(self) -> float:
        """Processing Gain
        "Rx processing gain (dB) of (optional) despreader."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Processing Gain')
        key_val_pair = [i for i in props if 'Processing Gain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def apply_pg_to_narrowband_only(self) -> bool:
        """Apply PG to Narrowband Only
        "Processing gain captures the despreading effect and applies to NB signals only (not BB noise) when enabled."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Apply PG to Narrowband Only')
        key_val_pair = [i for i in props if 'Apply PG to Narrowband Only=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def saturation_level(self) -> float:
        """Saturation Level
        "Rx input saturation level."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Saturation Level')
        key_val_pair = [i for i in props if 'Saturation Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def rx_noise_figure(self) -> float:
        """Rx Noise Figure
        "Rx noise figure (dB)."
        "Value should be between 0 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Rx Noise Figure')
        key_val_pair = [i for i in props if 'Rx Noise Figure=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def receiver_sensitivity_(self) -> float:
        """Receiver Sensitivity 
        "Rx minimum sensitivity level (dBm)."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Receiver Sensitivity ')
        key_val_pair = [i for i in props if 'Receiver Sensitivity =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def snrsinad_at_sensitivity_(self) -> float:
        """SNR/SINAD at Sensitivity 
        "SNR or SINAD at the specified sensitivity level."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SNR/SINAD at Sensitivity ')
        key_val_pair = [i for i in props if 'SNR/SINAD at Sensitivity =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def perform_rx_intermod_analysis(self) -> bool:
        """Perform Rx Intermod Analysis
        "Performs a non-linear intermod analysis for the Rx."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Perform Rx Intermod Analysis')
        key_val_pair = [i for i in props if 'Perform Rx Intermod Analysis=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def amplifier_saturation_level(self) -> float:
        """Amplifier Saturation Level
        "Internal Rx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Amplifier Saturation Level')
        key_val_pair = [i for i in props if 'Amplifier Saturation Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def _1_db_point_ref_input_(self) -> float:
        """1-dB Point, Ref. Input 
        "Rx's 1 dB Compression Point - total power > P1dB saturates the receiver."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1-dB Point, Ref. Input ')
        key_val_pair = [i for i in props if '1-dB Point, Ref. Input =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "Internal Rx Amplifier's 3rd order intercept point."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'IP3, Ref. Input')
        key_val_pair = [i for i in props if 'IP3, Ref. Input=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Internal Rx Amplifier's maximum intermod order to compute."
        "Value should be between 3 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Intermod Order')
        key_val_pair = [i for i in props if 'Max Intermod Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

