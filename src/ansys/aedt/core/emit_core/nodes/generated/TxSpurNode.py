from ..EmitNode import *

class TxSpurNode(EmitNode):
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

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    class SpurTableUnitsOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"

    @property
    def spur_table_units(self) -> SpurTableUnitsOption:
        """Spur Table Units
        "Specifies the units for the Spurs."
        "        """
        val = self._get_property('Spur Table Units')
        val = self.SpurTableUnitsOption[val]
        return val

    @spur_table_units.setter
    def spur_table_units(self, value: SpurTableUnitsOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Spur Table Units=' + value.value])

