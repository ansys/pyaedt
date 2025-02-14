from ..EmitNode import *

class ReadOnlySparameter(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def file(self) -> str:
        """File
        "S-Parameter file defining the component."
        "Value should be a full file path."
        """
        val = self._get_property('File')
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

    @property
    def radio_side_ports(self):
        """Radio Side Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values."
        "        """
        val = self._get_property('Radio Side Ports')
        return val

    @property
    def antenna_side_ports(self):
        """Antenna Side Ports
        "Assigns the child port nodes to the multiplexers ports."
        "A list of values."
        "        """
        val = self._get_property('Antenna Side Ports')
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

