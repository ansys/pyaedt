class Node_TR_Switch(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
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
    def get_filename(self):
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
    def set_filename(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def get_noise_temperature(self):
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Temperature')
    def set_noise_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def get_tx_port(self):
        """Tx Port
        "Specifies which port on the TR Switch is part of the Tx path.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tx Port')
    def set_tx_port(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tx Port=' + value])
    class TxPortOption(Enum):
        (
            _0 = "Port 1"
            _1 = "Port 2"
        )

    @property
    def get_common_port_location(self):
        """Common Port Location
        "Defines the orientation of the tr switch.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Common Port Location')
    def set_common_port_location(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Common Port Location=' + value])
    class CommonPortLocationOption(Enum):
        (
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"
        )

    @property
    def get_insertion_loss(self):
        """Insertion Loss
        "TR Switch in-band loss in forward direction.."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Insertion Loss')
    def set_insertion_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Insertion Loss=' + value])

    @property
    def get_finite_isolation(self):
        """Finite Isolation
        "Use a finite isolation. If disabled, the  tr switch model is ideal (infinite isolation).."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Finite Isolation')
    def set_finite_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Finite Isolation=' + value])

    @property
    def get_isolation(self):
        """Isolation
        "TR Switch reverse isolation (i.e., loss between the Tx/Rx ports).."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Isolation')
    def set_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Isolation=' + value])

    @property
    def get_finite_bandwidth(self):
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  tr switch model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Finite Bandwidth')
    def set_finite_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Finite Bandwidth=' + value])

    @property
    def get_out_of_band_attenuation(self):
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Out-of-band Attenuation')
    def set_out_of_band_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Out-of-band Attenuation=' + value])

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

