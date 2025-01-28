
from ..GenericEmitNode import GenericEmitNode
from enum import Enum

class Node_Amplifier(GenericEmitNode):
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
    def get_filename(self):
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
    def set_filename(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def get_noise_temperature(self):
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Temperature')
    def set_noise_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def get_amplifier_type(self):
        """Amplifier Type
        "Configures the amplifier as a Tx or Rx amplifier."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Amplifier Type')
    def set_amplifier_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Amplifier Type=' + value])

    class AmplifierTypeOption(Enum):
        TRANSMIT_AMPLIFIER = "Transmit Amplifier"
        RECEIVE_AMPLIFIER = "Receive Amplifier"

    @property
    def get_gain(self):
        """Gain
        "Amplifier in-band gain."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Gain')
    def set_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Gain=' + value])

    @property
    def get_center_frequency(self):
        """Center Frequency
        "Center frequency of amplifiers operational bandwidth."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Center Frequency')
    def set_center_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Center Frequency=' + value])

    @property
    def get_bandwidth(self):
        """Bandwidth
        "Frequency region where the gain applies."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Bandwidth')
    def set_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Bandwidth=' + value])

    @property
    def get_noise_figure(self):
        """Noise Figure
        "Amplifier noise figure."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Figure')
    def set_noise_figure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def get_saturation_level(self):
        """Saturation Level
        "Saturation level."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Saturation Level')
    def set_saturation_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Saturation Level=' + value])

    @property
    def get__1_db_point_ref_input(self):
        """1-dB Point, Ref. Input
        "Incoming signals > this value saturate the amplifier."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1-dB Point, Ref. Input')
    def set__1_db_point_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input=' + value])

    @property
    def get_ip3_ref_input(self):
        """IP3, Ref. Input
        "3rd order intercept point."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'IP3, Ref. Input')
    def set_ip3_ref_input(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def get_shape_factor(self):
        """Shape Factor
        "Ratio defining the selectivity of the amplifier."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Shape Factor')
    def set_shape_factor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Shape Factor=' + value])

    @property
    def get_reverse_isolation(self):
        """Reverse Isolation
        "Amplifier reverse isolation."
        "Value should be between 0 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Reverse Isolation')
    def set_reverse_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

    @property
    def get_max_intermod_order(self):
        """Max Intermod Order
        "Maximum order of intermods to compute."
        "Value should be between 3 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Intermod Order')
    def set_max_intermod_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

