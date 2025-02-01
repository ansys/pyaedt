from ..EmitNode import *

class CouplingLinkNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

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
        return val
    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def ports(self):
        """Ports
        "Maps each port in the link to an antenna in the project."
        "A list of values."
        "        """
        val = self._get_property('Ports')
        return val
    @ports.setter
    def ports(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Ports=' + value])

