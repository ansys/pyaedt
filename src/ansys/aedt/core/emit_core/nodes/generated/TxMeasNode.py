from ..GenericEmitNode import *
class TxMeasNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def file(self) -> str:
        """File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')
        key_val_pair = [i for i in props if 'File=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def source_file(self) -> str:
        """Source File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Source File')
        key_val_pair = [i for i in props if 'Source File=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def transmit_frequency(self) -> float:
        """Transmit Frequency
        "Channel associated with the measurement file."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Transmit Frequency')
        key_val_pair = [i for i in props if 'Transmit Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def use_ams_limits(self) -> bool:
        """Use AMS Limits
        "Allow AMS to define the frequency limits for the measurements."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use AMS Limits')
        key_val_pair = [i for i in props if 'Use AMS Limits=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @use_ams_limits.setter
    def use_ams_limits(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use AMS Limits=' + value])

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Value should be greater than 1e+06."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start Frequency')
        key_val_pair = [i for i in props if 'Start Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @start_frequency.setter
    def start_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start Frequency=' + value])

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Value should be less than 6e+09."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop Frequency')
        key_val_pair = [i for i in props if 'Stop Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @stop_frequency.setter
    def stop_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop Frequency=' + value])

    @property
    def exclude_harmonics_below_noise(self) -> bool:
        """Exclude Harmonics Below Noise
        "Include/Exclude Harmonics below the noise."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Exclude Harmonics Below Noise')
        key_val_pair = [i for i in props if 'Exclude Harmonics Below Noise=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @exclude_harmonics_below_noise.setter
    def exclude_harmonics_below_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Exclude Harmonics Below Noise=' + value])

    @property
    def enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

