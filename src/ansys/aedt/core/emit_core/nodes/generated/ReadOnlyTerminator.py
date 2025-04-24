from ..EmitNode import *

class ReadOnlyTerminator(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the Terminator."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    class TypeOption(Enum):
            BYFILE = "By File"
            PARAMETRIC = "Parametric"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of terminator model to use. Options include: By File (measured or simulated) or Parametric."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val.upper()]
        return val

    class PortLocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def port_location(self) -> PortLocationOption:
        """Port Location
        "Defines the orientation of the terminator.."
        "        """
        val = self._get_property('Port Location')
        val = self.PortLocationOption[val.upper()]
        return val

    @property
    def vswr(self) -> float:
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the terminator and the connected component (RF System, Antenna, etc)."
        "Value should be between 1 and 100."
        """
        val = self._get_property('VSWR')
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

