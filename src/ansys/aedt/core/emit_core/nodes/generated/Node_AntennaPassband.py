class Node_AntennaPassband(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def get_passband_loss(self):
        """Passband Loss
        "Passband loss."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Passband Loss')
    def set_passband_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Passband Loss=' + value])

    @property
    def get_out_of_band_attenuation(self):
        """Out of Band Attenuation
        "Out of band antenna loss."
        "Value should be between 0 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Out of Band Attenuation')
    def set_out_of_band_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Out of Band Attenuation=' + value])

    @property
    def get_lower_stop_band(self):
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Stop Band')
    def set_lower_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Stop Band=' + value])

    @property
    def get_lower_cutoff(self):
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Cutoff')
    def set_lower_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Cutoff=' + value])

    @property
    def get_higher_cutoff(self):
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Cutoff')
    def set_higher_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Cutoff=' + value])

    @property
    def get_higher_stop_band(self):
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Stop Band')
    def set_higher_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Stop Band=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

