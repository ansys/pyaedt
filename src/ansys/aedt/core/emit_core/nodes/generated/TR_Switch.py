from ..EmitNode import *

class TR_Switch(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

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

    class TxPortOption(Enum):
            _0 = "Port 1"
            _1 = "Port 2"

    @property
    def tx_port(self) -> TxPortOption:
        """Tx Port
        "Specifies which port on the TR Switch is part of the Tx path.."
        "        """
        val = self._get_property('Tx Port')
        val = self.TxPortOption[val]
        return val

    @tx_port.setter
    def tx_port(self, value: TxPortOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Tx Port=' + value.value])

    class CommonPortLocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def common_port_location(self) -> CommonPortLocationOption:
        """Common Port Location
        "Defines the orientation of the tr switch.."
        "        """
        val = self._get_property('Common Port Location')
        val = self.CommonPortLocationOption[val]
        return val

    @common_port_location.setter
    def common_port_location(self, value: CommonPortLocationOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Common Port Location=' + value.value])

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "TR Switch in-band loss in forward direction.."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Insertion Loss')
        return val

    @insertion_loss.setter
    def insertion_loss(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Insertion Loss=' + value])

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation
        "Use a finite isolation. If disabled, the  tr switch model is ideal (infinite isolation).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Finite Isolation')
        return val

    @finite_isolation.setter
    def finite_isolation(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Finite Isolation=' + value])

    @property
    def isolation(self) -> float:
        """Isolation
        "TR Switch reverse isolation (i.e., loss between the Tx/Rx ports).."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Isolation')
        return val

    @isolation.setter
    def isolation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Isolation=' + value])

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  tr switch model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Finite Bandwidth')
        return val

    @finite_bandwidth.setter
    def finite_bandwidth(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Finite Bandwidth=' + value])

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Out-of-band Attenuation')
        return val

    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Out-of-band Attenuation=' + value])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Stop Band')
        return val

    @lower_stop_band.setter
    def lower_stop_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Lower Stop Band=' + value])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Cutoff')
        return val

    @lower_cutoff.setter
    def lower_cutoff(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Lower Cutoff=' + value])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Cutoff')
        return val

    @higher_cutoff.setter
    def higher_cutoff(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Higher Cutoff=' + value])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Stop Band')
        return val

    @higher_stop_band.setter
    def higher_stop_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Higher Stop Band=' + value])

