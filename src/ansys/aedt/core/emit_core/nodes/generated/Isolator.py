from ..GenericEmitNode import *
class Isolator(GenericEmitNode):
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
    def type(self):
        """Type
        "Type of isolator model to use. Options include: By File (measured or simulated) or Parametric."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
        key_val_pair = [i for i in props if 'Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @type.setter
    def type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
            BYFILE = "By File"
            PARAMETRIC = "Parametric"

    @property
    def port_1_location(self):
        """Port 1 Location
        "Defines the orientation of the isolator.."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Port 1 Location')
        key_val_pair = [i for i in props if 'Port 1 Location=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @port_1_location.setter
    def port_1_location(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Port 1 Location=' + value])
    class Port1LocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Isolator in-band loss in forward direction.."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Insertion Loss')
        key_val_pair = [i for i in props if 'Insertion Loss=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @insertion_loss.setter
    def insertion_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Insertion Loss=' + value])

    @property
    def finite_reverse_isolation(self) -> bool:
        """Finite Reverse Isolation
        "Use a finite reverse isolation. If disabled, the  isolator model is ideal (infinite reverse isolation).."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Finite Reverse Isolation')
        key_val_pair = [i for i in props if 'Finite Reverse Isolation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @finite_reverse_isolation.setter
    def finite_reverse_isolation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Finite Reverse Isolation=' + value])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Isolator reverse isolation (i.e., loss in the reverse direction).."
        "Value should be between 0 and 100."
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
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  isolator model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Finite Bandwidth')
        key_val_pair = [i for i in props if 'Finite Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @finite_bandwidth.setter
    def finite_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Finite Bandwidth=' + value])

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
    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Out-of-band Attenuation=' + value])

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
    @lower_stop_band.setter
    def lower_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Stop Band=' + value])

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
    @lower_cutoff.setter
    def lower_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Cutoff=' + value])

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
    @higher_cutoff.setter
    def higher_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Cutoff=' + value])

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
    @higher_stop_band.setter
    def higher_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Stop Band=' + value])

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

