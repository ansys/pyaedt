
from ..GenericEmitNode import GenericEmitNode

class Node_CouplingsNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def get_minimum_allowed_coupling(self):
        """Minimum Allowed Coupling
        "Global minimum allowed coupling value. All computed coupling within this project will be >= this value."
        "Value should be between -1000 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minimum Allowed Coupling')
    def set_minimum_allowed_coupling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minimum Allowed Coupling=' + value])

    @property
    def get_global_default_coupling(self):
        """Global Default Coupling
        "Default antenna-to-antenna coupling loss value."
        "Value should be between -1000 and 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Global Default Coupling')
    def set_global_default_coupling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Global Default Coupling=' + value])

    @property
    def get_antenna_tags(self):
        """Antenna Tags
        "All tags currently used by all antennas in the project."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Tags')

