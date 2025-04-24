from ..EmitNode import *

class ReadOnlyCouplingLinkNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling link."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enabled')
        val = (val == 'true')
        return val

    @property
    def ports(self):
        """Ports
        "Maps each port in the link to an antenna in the project."
        "A list of values."
        "        """
        val = self._get_property('Ports')
        return val

