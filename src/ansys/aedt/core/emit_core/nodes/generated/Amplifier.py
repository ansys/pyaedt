from ..GenericEmitNode import *
class Amplifier(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
        key_val_pair = [i for i in props if 'Filename=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @filename.setter
    def filename(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Temperature')
        key_val_pair = [i for i in props if 'Noise Temperature=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @noise_temperature.setter
    def noise_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
        key_val_pair = [i for i in props if 'Notes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @notes.setter
    def notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def amplifier_type(self):
        """Amplifier Type
        "Configures the amplifier as a Tx or Rx amplifier."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Amplifier Type')
        key_val_pair = [i for i in props if 'Amplifier Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @amplifier_type.setter
    def amplifier_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Amplifier Type=' + value])
    class AmplifierTypeOption(Enum):
            TRANSMIT_AMPLIFIER = "Transmit Amplifier"
            RECEIVE_AMPLIFIER = "Receive Amplifier"

    @property
    def gain(self) -> float:
        """Gain
        "Amplifier in-band gain."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Gain')
        key_val_pair = [i for i in props if 'Gain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @gain.setter
    def gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Gain=' + value])

    @property
    def center_frequency(self) -> float:
        """Center Frequency
        "Center frequency of amplifiers operational bandwidth."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Center Frequency')
        key_val_pair = [i for i in props if 'Center Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @center_frequency.setter
    def center_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Center Frequency=' + value])

    @property
    def bandwidth(self) -> float:
        """Bandwidth
        "Frequency region where the gain applies."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Bandwidth')
        key_val_pair = [i for i in props if 'Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @bandwidth.setter
    def bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Bandwidth=' + value])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Amplifier noise figure."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Figure')
        key_val_pair = [i for i in props if 'Noise Figure=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @noise_figure.setter
    def noise_figure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def saturation_level(self) -> float:
        """Saturation Level
        "Saturation level."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Saturation Level')
        key_val_pair = [i for i in props if 'Saturation Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @saturation_level.setter
    def saturation_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Saturation Level=' + value])

    @property
    def _1_db_point_ref_input(self) -> float:
        """1-dB Point, Ref. Input
        "Incoming signals > this value saturate the amplifier."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1-dB Point, Ref. Input')
        key_val_pair = [i for i in props if '1-dB Point, Ref. Input=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_1_db_point_ref_input.setter
    def _1_db_point_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input=' + value])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "3rd order intercept point."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'IP3, Ref. Input')
        key_val_pair = [i for i in props if 'IP3, Ref. Input=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @ip3_ref_input.setter
    def ip3_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        "Ratio defining the selectivity of the amplifier."
        "Value should be between 1 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Shape Factor')
        key_val_pair = [i for i in props if 'Shape Factor=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @shape_factor.setter
    def shape_factor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Shape Factor=' + value])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Amplifier reverse isolation."
        "Value should be between 0 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Reverse Isolation')
        key_val_pair = [i for i in props if 'Reverse Isolation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @reverse_isolation.setter
    def reverse_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Maximum order of intermods to compute."
        "Value should be between 3 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Intermod Order')
        key_val_pair = [i for i in props if 'Max Intermod Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_intermod_order.setter
    def max_intermod_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

