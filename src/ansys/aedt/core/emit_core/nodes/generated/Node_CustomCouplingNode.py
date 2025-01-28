class Node_CustomCouplingNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
    def get_enabled(self):
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def get_enable_refinement(self):
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Refinement')
    def set_enable_refinement(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def get_adaptive_sampling(self):
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Adaptive Sampling')
    def set_adaptive_sampling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def get_refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Refinement Domain')
    def set_refinement_domain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

