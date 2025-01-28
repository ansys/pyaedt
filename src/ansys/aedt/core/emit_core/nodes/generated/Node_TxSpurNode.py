class Node_TxSpurNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,'Csv')

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def get_enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def get_spur_table_units(self):
        """Spur Table Units
        "Specifies the units for the Spurs."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spur Table Units')
    def set_spur_table_units(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spur Table Units=' + value])
    class SpurTableUnitsOption(Enum):
        (
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"
        )

