class Node_RfSystemGroup(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def get_enable_passive_noise(self):
        """Enable Passive Noise
        "If true, the noise contributions of antennas and passive components are included in cosite simulation. Note: Antenna and passive component noise is always included in link analysis simulation.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Passive Noise')
    def set_enable_passive_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Passive Noise=' + value])

    @property
    def get_enforce_thermal_noise_floor(self):
        """Enforce Thermal Noise Floor
        "If true, all broadband noise is limited by the thermal noise floor (-174 dBm/Hz)."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enforce Thermal Noise Floor')
    def set_enforce_thermal_noise_floor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enforce Thermal Noise Floor=' + value])

