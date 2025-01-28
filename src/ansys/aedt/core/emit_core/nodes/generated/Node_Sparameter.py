class Node_Sparameter(GenericEmitNode):
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
    def get_file(self):
        """File
        "S-Parameter file defining the component."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')
    def set_file(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['File=' + value])

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
    def get_radio_side_ports(self):
        """Radio Side Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values, delimited with pipe ('|')."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Radio Side Ports')
    def set_radio_side_ports(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Radio Side Ports=' + value])
    class RadioSidePortsOption(Enum):
        (
            ::PORTNAMES = "::PortNames"
        )

    @property
    def get_antenna_side_ports(self):
        """Antenna Side Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values, delimited with pipe ('|')."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Side Ports')
    def set_antenna_side_ports(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna Side Ports=' + value])
    class AntennaSidePortsOption(Enum):
        (
            ::PORTNAMES = "::PortNames"
        )

    @property
    def get_warnings(self):
        """Warnings
        "Warning(s) for this node."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')

