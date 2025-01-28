class Node_TxNbEmissionNode(GenericEmitNode):
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
    def get_narrowband_behavior(self):
        """Narrowband Behavior
        "Specifies the behavior of the parametric narrowband emissions mask."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Narrowband Behavior')
    def set_narrowband_behavior(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Narrowband Behavior=' + value])
    class NarrowbandBehaviorOption(Enum):
        (
            ABSOLUTE = "Absolute Freqs and Power"
            RELATIVEBANDWIDTH = "Relative Freqs and Attenuation"
        )

    @property
    def get_measurement_frequency(self):
        """Measurement Frequency
        "Measurement frequency for the absolute freq/amp pairs.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measurement Frequency')
    def set_measurement_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measurement Frequency=' + value])

