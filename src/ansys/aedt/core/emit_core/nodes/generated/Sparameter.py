from ..GenericEmitNode import *
class Sparameter(GenericEmitNode):
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
    def file(self) -> str:
        """File
        "S-Parameter file defining the component."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')
        key_val_pair = [i for i in props if 'File=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @file.setter
    def file(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['File=' + value])

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
    def radio_side_ports(self):
        """Radio Side Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Radio Side Ports')
        key_val_pair = [i for i in props if 'Radio Side Ports=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val.split('|')
    @radio_side_ports.setter
    def radio_side_ports(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Radio Side Ports=' + value])
    class RadioSidePortsOption(Enum):
            PORTNAMES = "::PortNames"

    @property
    def antenna_side_ports(self):
        """Antenna Side Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Side Ports')
        key_val_pair = [i for i in props if 'Antenna Side Ports=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val.split('|')
    @antenna_side_ports.setter
    def antenna_side_ports(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna Side Ports=' + value])
    class AntennaSidePortsOption(Enum):
            PORTNAMES = "::PortNames"

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

