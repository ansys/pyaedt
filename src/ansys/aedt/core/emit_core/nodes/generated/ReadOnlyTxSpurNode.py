from enum import Enum
from ..EmitNode import EmitNode

class ReadOnlyTxSpurNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def table_data(self):
        """ Table"
        "Table consists of 3 columns."
        "Frequency (MHz): 
        "    Value should be a mathematical expression."
        "Bandwidth: 
        "    Value should be greater than 1."
        "Power: 
        "    Value should be between -200 and 150."
        """
        return self._get_table_data()

    class SpurTableUnitsOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVE = "Relative"

    @property
    def spur_table_units(self) -> SpurTableUnitsOption:
        """Spur Table Units
        "Specifies the units for the Spurs."
        "        """
        val = self._get_property("Spur Table Units")
        val = self.SpurTableUnitsOption[val]
        return val

