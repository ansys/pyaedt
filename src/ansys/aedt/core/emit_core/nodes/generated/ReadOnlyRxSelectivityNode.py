from ..EmitNode import EmitNode

class ReadOnlyRxSelectivityNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def use_arithmetic_mean(self) -> bool:
        """Use Arithmetic Mean
        "Uses arithmetic mean to center bandwidths about the tuned channel frequency."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Use Arithmetic Mean")
        return val

