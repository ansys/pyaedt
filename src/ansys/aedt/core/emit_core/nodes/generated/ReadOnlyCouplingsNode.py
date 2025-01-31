from ..GenericEmitNode import *
class ReadOnlyCouplingsNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def minimum_allowed_coupling(self) -> float:
        """Minimum Allowed Coupling
        "Global minimum allowed coupling value. All computed coupling within this project will be >= this value."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minimum Allowed Coupling')
        key_val_pair = [i for i in props if 'Minimum Allowed Coupling=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def global_default_coupling(self) -> float:
        """Global Default Coupling
        "Default antenna-to-antenna coupling loss value."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Global Default Coupling')
        key_val_pair = [i for i in props if 'Global Default Coupling=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def antenna_tags(self) -> str:
        """Antenna Tags
        "All tags currently used by all antennas in the project."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Tags')
        key_val_pair = [i for i in props if 'Antenna Tags=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

