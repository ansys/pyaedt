from ..GenericEmitNode import *
class Multiplexer(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def add_multiplexer_pass_band(self):
        """Add a New Multiplexer Band to this Multiplexer"""
        return self._add_child_node("MultiplexerBand")

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
    def filename(self) -> str:
        """Filename
        "Name of file defining the multiplexer."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
        key_val_pair = [i for i in props if 'Filename=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @filename.setter
    def filename(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Temperature')
        key_val_pair = [i for i in props if 'Noise Temperature=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @noise_temperature.setter
    def noise_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

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

    @property
    def type(self):
        """Type
        "Type of multiplexer model. Options include: By File (one measured or simulated file for the device) or By Pass Band (parametric or file-based definition for each pass band)."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
        key_val_pair = [i for i in props if 'Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @type.setter
    def type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
            PARAMETRIC = "By Pass Band"
            BYFILE = "By File"

    @property
    def port_1_location(self):
        """Port 1 Location
        "Defines the orientation of the multiplexer.."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Port 1 Location')
        key_val_pair = [i for i in props if 'Port 1 Location=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @port_1_location.setter
    def port_1_location(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Port 1 Location=' + value])
    class Port1LocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def flip_ports_vertically(self) -> bool:
        """Flip Ports Vertically
        "Reverses the port order on the multi-port side of the multiplexer.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Flip Ports Vertically')
        key_val_pair = [i for i in props if 'Flip Ports Vertically=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @flip_ports_vertically.setter
    def flip_ports_vertically(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Flip Ports Vertically=' + value])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')
        key_val_pair = [i for i in props if 'Warnings=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

