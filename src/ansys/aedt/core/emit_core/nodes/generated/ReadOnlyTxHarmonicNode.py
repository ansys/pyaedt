from ..EmitNode import *

class ReadOnlyTxHarmonicNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    class HarmonicTableUnitsOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"

    @property
    def harmonic_table_units(self) -> HarmonicTableUnitsOption:
        """Harmonic Table Units
        "Specifies the units for the Harmonics."
        "        """
        val = self._get_property('Harmonic Table Units')
        val = self.HarmonicTableUnitsOption[val.upper()]
        return val

