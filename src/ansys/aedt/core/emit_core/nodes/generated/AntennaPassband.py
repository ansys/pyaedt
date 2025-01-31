from ..GenericEmitNode import *
class AntennaPassband(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

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
    def enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def passband_loss(self) -> float:
        """Passband Loss
        "Passband loss."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Passband Loss')
        key_val_pair = [i for i in props if 'Passband Loss=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @passband_loss.setter
    def passband_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Passband Loss=' + value])

    @property
    def out_of_band_attenuation(self) -> float:
        """Out of Band Attenuation
        "Out of band antenna loss."
        "Value should be between 0 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Out of Band Attenuation')
        key_val_pair = [i for i in props if 'Out of Band Attenuation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Out of Band Attenuation=' + value])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Stop Band')
        key_val_pair = [i for i in props if 'Lower Stop Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @lower_stop_band.setter
    def lower_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Stop Band=' + value])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Cutoff')
        key_val_pair = [i for i in props if 'Lower Cutoff=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @lower_cutoff.setter
    def lower_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Cutoff=' + value])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Cutoff')
        key_val_pair = [i for i in props if 'Higher Cutoff=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @higher_cutoff.setter
    def higher_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Cutoff=' + value])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Stop Band')
        key_val_pair = [i for i in props if 'Higher Stop Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @higher_stop_band.setter
    def higher_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Stop Band=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
        key_val_pair = [i for i in props if 'Notes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @notes.setter
    def notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

