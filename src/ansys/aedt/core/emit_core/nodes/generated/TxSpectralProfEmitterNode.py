from ..EmitNode import *

class TxSpectralProfEmitterNode(EmitNode):
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
        return self._oRevisionData.GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def output_voltage_peak(self) -> float:
        """Output Voltage Peak
        "Output High Voltage Level: maximum voltage of the digital signal."
        "        """
        val = self._get_property('Output Voltage Peak')
        val = self._convert_from_internal_units(float(val), "Voltage")
        return val

    @output_voltage_peak.setter
    def output_voltage_peak(self, value : float|str):
        value = self._convert_to_internal_units(value, "Voltage")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Output Voltage Peak=' + f"{value}"])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Include Phase Noise=' + value])

    @property
    def tx_broadband_noise(self) -> float:
        """Tx Broadband Noise
        "Transmitters broadband noise level."
        "Value should be less than 1000."
        """
        val = self._get_property('Tx Broadband Noise')
        return val

    @tx_broadband_noise.setter
    def tx_broadband_noise(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Tx Broadband Noise=' + value])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Perform Tx Intermod Analysis=' + value])

    @property
    def internal_amp_gain(self) -> float:
        """Internal Amp Gain
        "Internal Tx Amplifier's Gain."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property('Internal Amp Gain')
        return val

    @internal_amp_gain.setter
    def internal_amp_gain(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Internal Amp Gain=' + value])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Internal Tx Amplifier's noise figure."
        "Value should be between 0 and 50."
        """
        val = self._get_property('Noise Figure')
        return val

    @noise_figure.setter
    def noise_figure(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def amplifier_saturation_level(self) -> float:
        """Amplifier Saturation Level
        "Internal Tx Amplifier's Saturation Level."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Amplifier Saturation Level')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @amplifier_saturation_level.setter
    def amplifier_saturation_level(self, value : float|str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Amplifier Saturation Level=' + f"{value}"])

    @property
    def p1_db_point_ref_input_(self) -> float:
        """P1-dB Point, Ref. Input 
        "Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB saturates the internal Tx amplifier."
        "Value should be between -200 and 200."
        """
        val = self._get_property('P1-dB Point, Ref. Input ')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @p1_db_point_ref_input_.setter
    def p1_db_point_ref_input_(self, value : float|str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['P1-dB Point, Ref. Input =' + f"{value}"])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "Internal Tx Amplifier's 3rd order intercept point."
        "Value should be between -200 and 200."
        """
        val = self._get_property('IP3, Ref. Input')
        val = self._convert_from_internal_units(float(val), "Power")
        return val

    @ip3_ref_input.setter
    def ip3_ref_input(self, value : float|str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + f"{value}"])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Internal Tx Amplifier's Reverse Isolation."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Reverse Isolation')
        return val

    @reverse_isolation.setter
    def reverse_isolation(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

