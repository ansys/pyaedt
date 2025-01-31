from ..GenericEmitNode import *
class RfSystemGroup(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enable_passive_noise(self) -> bool:
        """Enable Passive Noise
        "If true, the noise contributions of antennas and passive components are included in cosite simulation. Note: Antenna and passive component noise is always included in link analysis simulation.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Passive Noise')
        key_val_pair = [i for i in props if 'Enable Passive Noise=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enable_passive_noise.setter
    def enable_passive_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Passive Noise=' + value])

    @property
    def enforce_thermal_noise_floor(self) -> bool:
        """Enforce Thermal Noise Floor
        "If true, all broadband noise is limited by the thermal noise floor (-174 dBm/Hz)."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enforce Thermal Noise Floor')
        key_val_pair = [i for i in props if 'Enforce Thermal Noise Floor=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enforce_thermal_noise_floor.setter
    def enforce_thermal_noise_floor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enforce Thermal Noise Floor=' + value])

