from ..GenericEmitNode import *
class CustomCouplingNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,'Csv')

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enabled')
        key_val_pair = [i for i in props if 'Enabled=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Refinement')
        key_val_pair = [i for i in props if 'Enable Refinement=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enable_refinement.setter
    def enable_refinement(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Adaptive Sampling')
        key_val_pair = [i for i in props if 'Adaptive Sampling=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @adaptive_sampling.setter
    def adaptive_sampling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Refinement Domain')
        key_val_pair = [i for i in props if 'Refinement Domain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @refinement_domain.setter
    def refinement_domain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

