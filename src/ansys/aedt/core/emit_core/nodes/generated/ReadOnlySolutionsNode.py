from ..EmitNode import EmitNode

class ReadOnlySolutionsNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling (A setup disabled in HFSS/Layout cannot be enabled in EMIT)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enabled")
        return val

