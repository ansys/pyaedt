class Node_Terminator(GenericEmitNode):
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
        "Name of file defining the Terminator."
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
        "Type of terminator model to use. Options include: By File (measured or simulated) or Parametric."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
    def set_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
        (
            BYFILE = "By File"
            PARAMETRIC = "Parametric"
        )

    @property
    def get_port_location(self):
        """Port Location
        "Defines the orientation of the terminator.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Port Location')
    def set_port_location(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Port Location=' + value])
    class PortLocationOption(Enum):
        (
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"
        )

    @property
    def get_vswr(self):
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the terminator and the connected component (RF System, Antenna, etc)."
        "Value should be between 1.0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'VSWR')
    def set_vswr(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['VSWR=' + value])

    @property
    def get_warnings(self):
        """Warnings
        "Warning(s) for this node."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')

