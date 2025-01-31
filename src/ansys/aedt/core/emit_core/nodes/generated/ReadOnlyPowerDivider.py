from ..GenericEmitNode import *
class ReadOnlyPowerDivider(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the Power Divider."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
        key_val_pair = [i for i in props if 'Filename=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

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

    @property
    def type(self):
        """Type
        "Type of Power Divider model to use. Options include: By File (measured or simulated), 3 dB (parametric), and Resistive (parametric)."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
        key_val_pair = [i for i in props if 'Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class TypeOption(Enum):
            BYFILE = "By File"
            _3DB = "3 dB"
            RESISTIVE = "Resistive"

    @property
    def orientation(self):
        """Orientation
        "Defines the orientation of the Power Divider.."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation')
        key_val_pair = [i for i in props if 'Orientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class OrientationOption(Enum):
            RADIOSIDE = "Divider"
            ANTENNASIDE = "Combiner"

    @property
    def insertion_loss_above_ideal(self) -> float:
        """Insertion Loss Above Ideal
        "Additional loss beyond the ideal insertion loss. The ideal insertion loss is 3 dB for the 3 dB Divider and 6 dB for the Resistive Divider.."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Insertion Loss Above Ideal')
        key_val_pair = [i for i in props if 'Insertion Loss Above Ideal=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation
        "Use a finite isolation between output ports. If disabled, the Power Divider isolation is ideal (infinite isolation between output ports).."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Finite Isolation')
        key_val_pair = [i for i in props if 'Finite Isolation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def isolation(self) -> float:
        """Isolation
        "Power Divider isolation between output ports.."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Isolation')
        key_val_pair = [i for i in props if 'Isolation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  Power Divider model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Finite Bandwidth')
        key_val_pair = [i for i in props if 'Finite Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Out-of-band Attenuation')
        key_val_pair = [i for i in props if 'Out-of-band Attenuation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Stop Band')
        key_val_pair = [i for i in props if 'Lower Stop Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Cutoff')
        key_val_pair = [i for i in props if 'Lower Cutoff=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Cutoff')
        key_val_pair = [i for i in props if 'Higher Cutoff=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Stop Band')
        key_val_pair = [i for i in props if 'Higher Stop Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')
        key_val_pair = [i for i in props if 'Warnings=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

