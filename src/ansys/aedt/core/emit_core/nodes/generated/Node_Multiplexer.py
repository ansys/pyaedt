class Node_Multiplexer(GenericEmitNode):
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
        "Name of file defining the multiplexer."
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
    def get_type(self):
        """Type
        "Type of multiplexer model. Options include: By File (one measured or simulated file for the device) or By Pass Band (parametric or file-based definition for each pass band)."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
    def set_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
        (
            PARAMETRIC = "By Pass Band"
            BYFILE = "By File"
        )

    @property
    def get_port_1_location(self):
        """Port 1 Location
        "Defines the orientation of the multiplexer.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Port 1 Location')
    def set_port_1_location(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Port 1 Location=' + value])
    class Port1LocationOption(Enum):
        (
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"
        )

    @property
    def get_flip_ports_vertically(self):
        """Flip Ports Vertically
        "Reverses the port order on the multi-port side of the multiplexer.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Flip Ports Vertically')
    def set_flip_ports_vertically(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Flip Ports Vertically=' + value])

    @property
    def get_warnings(self):
        """Warnings
        "Warning(s) for this node."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')

