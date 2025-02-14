from ..EmitNode import *

class PowerDivider(EmitNode):
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
        "Name of file defining the Power Divider."
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

    class TypeOption(Enum):
            BYFILE = "By File"
            _3DB = "3 dB"
            RESISTIVE = "Resistive"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of Power Divider model to use. Options include: By File (measured or simulated), 3 dB (parametric), and Resistive (parametric)."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Type=' + value.value])

    class OrientationOption(Enum):
            RADIOSIDE = "Divider"
            ANTENNASIDE = "Combiner"

    @property
    def orientation(self) -> OrientationOption:
        """Orientation
        "Defines the orientation of the Power Divider.."
        "        """
        val = self._get_property('Orientation')
        val = self.OrientationOption[val]
        return val

    @orientation.setter
    def orientation(self, value: OrientationOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation=' + value.value])

    @property
    def insertion_loss_above_ideal(self) -> float:
        """Insertion Loss Above Ideal
        "Additional loss beyond the ideal insertion loss. The ideal insertion loss is 3 dB for the 3 dB Divider and 6 dB for the Resistive Divider.."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Insertion Loss Above Ideal')
        return val

    @insertion_loss_above_ideal.setter
    def insertion_loss_above_ideal(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Insertion Loss Above Ideal=' + value])

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation
        "Use a finite isolation between output ports. If disabled, the Power Divider isolation is ideal (infinite isolation between output ports).."
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
        "Power Divider isolation between output ports.."
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
        "Use a finite bandwidth. If disabled, the  Power Divider model is ideal (infinite bandwidth).."
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

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

