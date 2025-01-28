class Node_RxMixerProductNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,'Csv')

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def get_enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def get_mixer_product_taper(self):
        """Mixer Product Taper
        "Taper for setting amplitude of mixer products."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Taper')
    def set_mixer_product_taper(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Taper=' + value])
    class MixerProductTaperOption(Enum):
        (
            CONSTANT = "Constant"
            MIL_STD_461G = "MIL-STD-461G"
            DUFF_MODEL = "Duff Model"
        )

    @property
    def get_mixer_product_susceptibility(self):
        """Mixer Product Susceptibility
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Susceptibility')
    def set_mixer_product_susceptibility(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Susceptibility=' + value])

    @property
    def get_spurious_rejection(self):
        """Spurious Rejection
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spurious Rejection')
    def set_spurious_rejection(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spurious Rejection=' + value])

    @property
    def get_minimum_tuning_frequency(self):
        """Minimum Tuning Frequency
        "Minimum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minimum Tuning Frequency')
    def set_minimum_tuning_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minimum Tuning Frequency=' + value])

    @property
    def get_maximum_tuning_frequency(self):
        """Maximum Tuning Frequency
        "Maximum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 100e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Maximum Tuning Frequency')
    def set_maximum_tuning_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Maximum Tuning Frequency=' + value])

    @property
    def get_mixer_product_slope(self):
        """Mixer Product Slope
        "Rate of decrease for amplitude of Rx's local oscillator harmonics (dB/decade)."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Slope')
    def set_mixer_product_slope(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Slope=' + value])

    @property
    def get_mixer_product_intercept(self):
        """Mixer Product Intercept
        "Mixer product intercept (dBc)."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Intercept')
    def set_mixer_product_intercept(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Intercept=' + value])

    @property
    def get__80_db_bandwidth(self):
        """80 dB Bandwidth
        "Bandwidth where Rx's susceptibility envelope is 80 dB above in-band susceptibility level."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'80 dB Bandwidth')
    def set__80_db_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['80 dB Bandwidth=' + value])

    @property
    def get_image_rejection(self):
        """Image Rejection
        "Image frequency amplitude (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Image Rejection')
    def set_image_rejection(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Image Rejection=' + value])

    @property
    def get_maximum_rf_harmonic_order(self):
        """Maximum RF Harmonic Order
        "Maximum order of RF frequency."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Maximum RF Harmonic Order')
    def set_maximum_rf_harmonic_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Maximum RF Harmonic Order=' + value])

    @property
    def get_maximum_lo_harmonic_order(self):
        """Maximum LO Harmonic Order
        "Maximum order of the LO frequency."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Maximum LO Harmonic Order')
    def set_maximum_lo_harmonic_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Maximum LO Harmonic Order=' + value])

    @property
    def get_mixing_mode(self):
        """Mixing Mode
        "Specifies whether the IF frequency is > or < RF channel frequency."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixing Mode')
    def set_mixing_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixing Mode=' + value])
    class MixingModeOption(Enum):
        (
            ABOVETUNEDFREQUENCY = "LO Above Tuned (RF) Frequency"
            BELOWTUNEDFREQUENCY = "LO Below Tuned (RF) Frequency"
            BOTHTUNEDFREQUENCIES = "LO Above/Below Tuned (RF) Frequency"
        )

    @property
    def get__1st_if_frequency(self):
        """1st IF Frequency
        "Intermediate frequency for Rx's 1st conversion stage."
        "Value should be a mathematical expression."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1st IF Frequency')
    def set__1st_if_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1st IF Frequency=' + value])

    @property
    def get_rf_transition_frequency(self):
        """RF Transition Frequency
        "RF Frequency Transition point."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'RF Transition Frequency')
    def set_rf_transition_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['RF Transition Frequency=' + value])

    @property
    def get_use_high_lo(self):
        """Use High LO
        "Use High LO above/below the transition frequency."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use High LO')
    def set_use_high_lo(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use High LO=' + value])
    class UseHighLOOption(Enum):
        (
            ABOVETRANSITION = "Above Transition Frequency"
            BELOWTRANSITION = "Below Transition Frequency"
        )

    @property
    def get_mixer_product_table_units(self):
        """Mixer Product Table Units
        "Specifies the units for the Mixer Products."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Table Units')
    def set_mixer_product_table_units(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Table Units=' + value])
    class MixerProductTableUnitsOption(Enum):
        (
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"
        )

