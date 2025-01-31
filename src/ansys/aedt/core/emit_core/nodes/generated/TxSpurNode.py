from ..GenericEmitNode import *
class TxSpurNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
    def enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def spur_table_units(self):
        """Spur Table Units
        "Specifies the units for the Spurs."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spur Table Units')
        key_val_pair = [i for i in props if 'Spur Table Units=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @spur_table_units.setter
    def spur_table_units(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spur Table Units=' + value])
    class SpurTableUnitsOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"

