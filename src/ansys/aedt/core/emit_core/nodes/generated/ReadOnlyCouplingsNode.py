from ..EmitNode import EmitNode

class ReadOnlyCouplingsNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def minimum_allowed_coupling(self) -> float:
        """Minimum Allowed Coupling
        "Global minimum allowed coupling value. All computed coupling within this project will be >= this value."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property("Minimum Allowed Coupling")
        return val

    @property
    def global_default_coupling(self) -> float:
        """Global Default Coupling
        "Default antenna-to-antenna coupling loss value."
        "Value should be between -1000 and 0."
        """
        val = self._get_property("Global Default Coupling")
        return val

    @property
    def antenna_tags(self) -> str:
        """Antenna Tags
        "All tags currently used by all antennas in the project."
        "        """
        val = self._get_property("Antenna Tags")
        return val

