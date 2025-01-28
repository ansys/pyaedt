class Node_TxMeasNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def get_file(self):
        """File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')

    @property
    def get_source_file(self):
        """Source File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Source File')

    @property
    def get_transmit_frequency(self):
        """Transmit Frequency
        "Channel associated with the measurement file."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Transmit Frequency')

    @property
    def get_use_ams_limits(self):
        """Use AMS Limits
        "Allow AMS to define the frequency limits for the measurements."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use AMS Limits')
    def set_use_ams_limits(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use AMS Limits=' + value])

    @property
    def get_start_frequency(self):
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Value should be between 1e6 and TxStopFreq."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start Frequency')
    def set_start_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start Frequency=' + value])

    @property
    def get_stop_frequency(self):
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Value should be between TxStartFreq and 6e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop Frequency')
    def set_stop_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop Frequency=' + value])

    @property
    def get_exclude_harmonics_below_noise(self):
        """Exclude Harmonics Below Noise
        "Include/Exclude Harmonics below the noise."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Exclude Harmonics Below Noise')
    def set_exclude_harmonics_below_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Exclude Harmonics Below Noise=' + value])

    @property
    def get_enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

