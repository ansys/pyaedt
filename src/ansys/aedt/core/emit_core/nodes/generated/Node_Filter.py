class Node_Filter(GenericEmitNode):
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
    def get_type(self):
        """Type
        "Type of filter to define. The filter can be defined by file (measured or simulated data) or using one of EMIT's parametric models."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
    def set_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
        (
            BYFILE = "By File"
            LOWPASS = "Low Pass"
            HIGHPASS = "High Pass"
            BANDPASS = "Band Pass"
            BANDSTOP = "Band Stop"
            TUNABLEBANDPASS = "Tunable Bandpass"
            TUNABLEBANDSTOP = "Tunable Bandstop"
        )

    @property
    def get_insertion_loss(self):
        """Insertion Loss
        "Filter pass band loss."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Insertion Loss')
    def set_insertion_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Insertion Loss=' + value])

    @property
    def get_stop_band_attenuation(self):
        """Stop band Attenuation
        "Filter stop band loss (attenuation)."
        "Value should be between ::InsertionLoss and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop band Attenuation')
    def set_stop_band_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop band Attenuation=' + value])

    @property
    def get_max_pass_band(self):
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Pass Band')
    def set_max_pass_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Pass Band=' + value])

    @property
    def get_min_stop_band(self):
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min Stop Band')
    def set_min_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min Stop Band=' + value])

    @property
    def get_max_stop_band(self):
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max Stop Band')
    def set_max_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max Stop Band=' + value])

    @property
    def get_min_pass_band(self):
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min Pass Band')
    def set_min_pass_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Min Pass Band=' + value])

    @property
    def get_lower_stop_band(self):
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Stop Band')
    def set_lower_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Stop Band=' + value])

    @property
    def get_lower_cutoff(self):
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Cutoff')
    def set_lower_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Cutoff=' + value])

    @property
    def get_higher_cutoff(self):
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Cutoff')
    def set_higher_cutoff(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Cutoff=' + value])

    @property
    def get_higher_stop_band(self):
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Stop Band')
    def set_higher_stop_band(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Stop Band=' + value])

    @property
    def get_lower_cutoff_(self):
        """Lower Cutoff 
        "Lower cutoff frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Cutoff ')
    def set_lower_cutoff_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Cutoff =' + value])

    @property
    def get_lower_stop_band_(self):
        """Lower Stop Band 
        "Lower stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lower Stop Band ')
    def set_lower_stop_band_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lower Stop Band =' + value])

    @property
    def get_higher_stop_band_(self):
        """Higher Stop Band 
        "Higher stop band frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Stop Band ')
    def set_higher_stop_band_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Stop Band =' + value])

    @property
    def get_higher_cutoff_(self):
        """Higher Cutoff 
        "Higher cutoff frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Higher Cutoff ')
    def set_higher_cutoff_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Higher Cutoff =' + value])

    @property
    def get_lowest_tuned_frequency_(self):
        """Lowest Tuned Frequency 
        "Lowest tuned frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Lowest Tuned Frequency ')
    def set_lowest_tuned_frequency_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Lowest Tuned Frequency =' + value])

    @property
    def get_highest_tuned_frequency_(self):
        """Highest Tuned Frequency 
        "Highest tuned frequency."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Highest Tuned Frequency ')
    def set_highest_tuned_frequency_(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Highest Tuned Frequency =' + value])

    @property
    def get_percent_bandwidth(self):
        """Percent Bandwidth
        "Tunable filter 3-dB bandwidth."
        "Value should be between 0.001 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Percent Bandwidth')
    def set_percent_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Percent Bandwidth=' + value])

    @property
    def get_shape_factor(self):
        """Shape Factor
        "Ratio defining the filter rolloff."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Shape Factor')
    def set_shape_factor(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Shape Factor=' + value])

    @property
    def get_warnings(self):
        """Warnings
        "Warning(s) for this node."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')

