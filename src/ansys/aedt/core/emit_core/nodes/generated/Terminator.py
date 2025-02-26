from ..EmitNode import *

class Terminator(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

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
        "Name of file defining the Terminator."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @noise_temperature.setter
    def noise_temperature(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Notes=' + value])

    class TypeOption(Enum):
            BYFILE = "By File"
            PARAMETRIC = "Parametric"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of terminator model to use. Options include: By File (measured or simulated) or Parametric."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Type=' + value.value])

    class PortLocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def port_location(self) -> PortLocationOption:
        """Port Location
        "Defines the orientation of the terminator.."
        "        """
        val = self._get_property('Port Location')
        val = self.PortLocationOption[val]
        return val

    @port_location.setter
    def port_location(self, value: PortLocationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Port Location=' + value.value])

    @property
    def vswr(self) -> float:
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the terminator and the connected component (RF System, Antenna, etc)."
        "Value should be between 1 and 100."
        """
        val = self._get_property('VSWR')
        return val

    @vswr.setter
    def vswr(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['VSWR=' + value])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

