from ..EmitNode import *

class ReadOnlyMultiplexer(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the multiplexer."
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
            PARAMETRIC = "By Pass Band"
            BYFILE = "By File"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of multiplexer model. Options include: By File (one measured or simulated file for the device) or By Pass Band (parametric or file-based definition for each pass band)."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val]
        return val

    class Port1LocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def port_1_location(self) -> Port1LocationOption:
        """Port 1 Location
        "Defines the orientation of the multiplexer.."
        "        """
        val = self._get_property('Port 1 Location')
        val = self.Port1LocationOption[val]
        return val

    @property
    def flip_ports_vertically(self) -> bool:
        """Flip Ports Vertically
        "Reverses the port order on the multi-port side of the multiplexer.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Flip Ports Vertically')
        return val

    @property
    def ports(self):
        """Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values."
        "        """
        val = self._get_property('Ports')
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

