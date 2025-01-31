from ..GenericEmitNode import *
class TxNbEmissionNode(GenericEmitNode):
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
    def narrowband_behavior(self):
        """Narrowband Behavior
        "Specifies the behavior of the parametric narrowband emissions mask."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Narrowband Behavior')
        key_val_pair = [i for i in props if 'Narrowband Behavior=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @narrowband_behavior.setter
    def narrowband_behavior(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Narrowband Behavior=' + value])
    class NarrowbandBehaviorOption(Enum):
            ABSOLUTE = "Absolute Freqs and Power"
            RELATIVEBANDWIDTH = "Relative Freqs and Attenuation"

    @property
    def measurement_frequency(self) -> float:
        """Measurement Frequency
        "Measurement frequency for the absolute freq/amp pairs.."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measurement Frequency')
        key_val_pair = [i for i in props if 'Measurement Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @measurement_frequency.setter
    def measurement_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measurement Frequency=' + value])

