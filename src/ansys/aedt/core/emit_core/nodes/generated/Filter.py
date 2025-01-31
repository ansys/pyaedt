from ..GenericEmitNode import *
class Filter(GenericEmitNode):
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
        "Type of filter to define. The filter can be defined by file (measured or simulated data) or using one of EMIT's parametric models."
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
            LOWPASS = "Low Pass"
            HIGHPASS = "High Pass"
            BANDPASS = "Band Pass"
            BANDSTOP = "Band Stop"
            TUNABLEBANDPASS = "Tunable Bandpass"
            TUNABLEBANDSTOP = "Tunable Bandstop"

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Filter pass band loss."
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
    def stop_band_attenuation(self) -> float:
        """Stop band Attenuation
        "Filter stop band loss (attenuation)."
        "Value should be less than 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop band Attenuation')
        key_val_pair = [i for i in props if 'Stop band Attenuation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @stop_band_attenuation.setter
    def stop_band_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop band Attenuation=' + value])

    @property
    def max_pass_band(self) -> float:
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Pass Band')
        key_val_pair = [i for i in props if 'Max Pass Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_pass_band.setter
    def max_pass_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Pass Band=' + value])

    @property
    def min_stop_band(self) -> float:
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min Stop Band')
        key_val_pair = [i for i in props if 'Min Stop Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @min_stop_band.setter
    def min_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min Stop Band=' + value])

    @property
    def max_stop_band(self) -> float:
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Stop Band')
        key_val_pair = [i for i in props if 'Max Stop Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_stop_band.setter
    def max_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Stop Band=' + value])

    @property
    def min_pass_band(self) -> float:
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min Pass Band')
        key_val_pair = [i for i in props if 'Min Pass Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @min_pass_band.setter
    def min_pass_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min Pass Band=' + value])

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
    def lower_cutoff_(self) -> float:
        """Lower Cutoff 
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Cutoff ')
        key_val_pair = [i for i in props if 'Lower Cutoff =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @lower_cutoff_.setter
    def lower_cutoff_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Cutoff =' + value])

    @property
    def lower_stop_band_(self) -> float:
        """Lower Stop Band 
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Stop Band ')
        key_val_pair = [i for i in props if 'Lower Stop Band =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @lower_stop_band_.setter
    def lower_stop_band_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Stop Band =' + value])

    @property
    def higher_stop_band_(self) -> float:
        """Higher Stop Band 
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Stop Band ')
        key_val_pair = [i for i in props if 'Higher Stop Band =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @higher_stop_band_.setter
    def higher_stop_band_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Stop Band =' + value])

    @property
    def higher_cutoff_(self) -> float:
        """Higher Cutoff 
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Cutoff ')
        key_val_pair = [i for i in props if 'Higher Cutoff =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @higher_cutoff_.setter
    def higher_cutoff_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Cutoff =' + value])

    @property
    def lowest_tuned_frequency_(self) -> float:
        """Lowest Tuned Frequency 
        "Lowest tuned frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lowest Tuned Frequency ')
        key_val_pair = [i for i in props if 'Lowest Tuned Frequency =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @lowest_tuned_frequency_.setter
    def lowest_tuned_frequency_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lowest Tuned Frequency =' + value])

    @property
    def highest_tuned_frequency_(self) -> float:
        """Highest Tuned Frequency 
        "Highest tuned frequency."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Highest Tuned Frequency ')
        key_val_pair = [i for i in props if 'Highest Tuned Frequency =' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @highest_tuned_frequency_.setter
    def highest_tuned_frequency_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Highest Tuned Frequency =' + value])

    @property
    def percent_bandwidth(self) -> float:
        """Percent Bandwidth
        "Tunable filter 3-dB bandwidth."
        "Value should be between 0.001 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Percent Bandwidth')
        key_val_pair = [i for i in props if 'Percent Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @percent_bandwidth.setter
    def percent_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Percent Bandwidth=' + value])

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        "Ratio defining the filter rolloff."
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

