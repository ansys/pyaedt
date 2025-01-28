class Node_TxBbEmissionNode(GenericEmitNode):
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
    def get_noise_behavior(self):
        """Noise Behavior
        "Specifies the behavior of the parametric noise profile."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Behavior')
    def set_noise_behavior(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Behavior=' + value])
    class NoiseBehaviorOption(Enum):
        (
            ABSOLUTE = "Absolute"
            RELATIVEBANDWIDTH = "Relative (Bandwidth)"
            RELATIVEOFFSET = "Relative (Offset)"
            BROADBANDEQUATION = "Equation"
        )

    @property
    def get_use_log_linear_interpolation(self):
        """Use Log-Linear Interpolation
        "If true, linear interpolation in the log domain is used. If false, linear interpolation in the linear domain is used.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Log-Linear Interpolation')
    def set_use_log_linear_interpolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Log-Linear Interpolation=' + value])

