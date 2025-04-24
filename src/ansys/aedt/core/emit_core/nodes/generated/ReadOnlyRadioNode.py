from ..EmitNode import *

class ReadOnlyRadioNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def table_data(self):
        """ Table"
        "Table consists of 2 columns."
        "Name: 
        "            "Type: 
        "            """
        return self._get_table_data()

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

