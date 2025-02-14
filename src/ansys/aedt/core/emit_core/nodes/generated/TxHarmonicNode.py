from ..EmitNode import *

class TxHarmonicNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,'Csv')

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    class HarmonicTableUnitsOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"

    @property
    def harmonic_table_units(self) -> HarmonicTableUnitsOption:
        """Harmonic Table Units
        "Specifies the units for the Harmonics."
        "        """
        val = self._get_property('Harmonic Table Units')
        val = self.HarmonicTableUnitsOption[val]
        return val

    @harmonic_table_units.setter
    def harmonic_table_units(self, value: HarmonicTableUnitsOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Harmonic Table Units=' + value.value])

