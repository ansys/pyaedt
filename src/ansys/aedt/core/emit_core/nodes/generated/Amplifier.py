from ..EmitNode import *

class Amplifier(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

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
        val = self._get_property('Filename')
        return val

    @filename.setter
    def filename(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @noise_temperature.setter
    def noise_temperature(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    @notes.setter
    def notes(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Notes=' + value])

    class AmplifierTypeOption(Enum):
            TRANSMIT_AMPLIFIER = "Transmit Amplifier"
            RECEIVE_AMPLIFIER = "Receive Amplifier"

    @property
    def amplifier_type(self) -> AmplifierTypeOption:
        """Amplifier Type
        "Configures the amplifier as a Tx or Rx amplifier."
        "        """
        val = self._get_property('Amplifier Type')
        val = self.AmplifierTypeOption[val]
        return val

    @amplifier_type.setter
    def amplifier_type(self, value: AmplifierTypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Amplifier Type=' + value.value])

    @property
    def gain(self) -> float:
        """Gain
        "Amplifier in-band gain."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Gain')
        return val

    @gain.setter
    def gain(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Gain=' + value])

    @property
    def center_frequency(self) -> float:
        """Center Frequency
        "Center frequency of amplifiers operational bandwidth."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Center Frequency')
        return val

    @center_frequency.setter
    def center_frequency(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Center Frequency=' + value])

    @property
    def bandwidth(self) -> float:
        """Bandwidth
        "Frequency region where the gain applies."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Bandwidth')
        return val

    @bandwidth.setter
    def bandwidth(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Bandwidth=' + value])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        "Amplifier noise figure."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Noise Figure')
        return val

    @noise_figure.setter
    def noise_figure(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Noise Figure=' + value])

    @property
    def saturation_level(self) -> float:
        """Saturation Level
        "Saturation level."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Saturation Level')
        return val

    @saturation_level.setter
    def saturation_level(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Saturation Level=' + value])

    @property
    def _1_db_point_ref_input(self) -> float:
        """1-dB Point, Ref. Input
        "Incoming signals > this value saturate the amplifier."
        "Value should be between -200 and 200."
        """
        val = self._get_property('1-dB Point, Ref. Input')
        return val

    @_1_db_point_ref_input.setter
    def _1_db_point_ref_input(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['1-dB Point, Ref. Input=' + value])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        "3rd order intercept point."
        "Value should be between -200 and 200."
        """
        val = self._get_property('IP3, Ref. Input')
        return val

    @ip3_ref_input.setter
    def ip3_ref_input(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['IP3, Ref. Input=' + value])

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        "Ratio defining the selectivity of the amplifier."
        "Value should be between 1 and 100."
        """
        val = self._get_property('Shape Factor')
        return val

    @shape_factor.setter
    def shape_factor(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Shape Factor=' + value])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Amplifier reverse isolation."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Reverse Isolation')
        return val

    @reverse_isolation.setter
    def reverse_isolation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Reverse Isolation=' + value])

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        "Maximum order of intermods to compute."
        "Value should be between 3 and 20."
        """
        val = self._get_property('Max Intermod Order')
        return val

    @max_intermod_order.setter
    def max_intermod_order(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max Intermod Order=' + value])

