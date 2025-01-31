from ..GenericEmitNode import *
class RxMixerProductNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,'Csv')

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def mixer_product_taper(self):
        """Mixer Product Taper
        "Taper for setting amplitude of mixer products."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Taper')
        key_val_pair = [i for i in props if 'Mixer Product Taper=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mixer_product_taper.setter
    def mixer_product_taper(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Taper=' + value])
    class MixerProductTaperOption(Enum):
            CONSTANT = "Constant"
            MIL_STD_461G = "MIL-STD-461G"
            DUFF_MODEL = "Duff Model"

    @property
    def mixer_product_susceptibility(self) -> float:
        """Mixer Product Susceptibility
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Susceptibility')
        key_val_pair = [i for i in props if 'Mixer Product Susceptibility=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mixer_product_susceptibility.setter
    def mixer_product_susceptibility(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Susceptibility=' + value])

    @property
    def spurious_rejection(self) -> float:
        """Spurious Rejection
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Spurious Rejection')
        key_val_pair = [i for i in props if 'Spurious Rejection=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @spurious_rejection.setter
    def spurious_rejection(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Spurious Rejection=' + value])

    @property
    def minimum_tuning_frequency(self) -> float:
        """Minimum Tuning Frequency
        "Minimum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minimum Tuning Frequency')
        key_val_pair = [i for i in props if 'Minimum Tuning Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @minimum_tuning_frequency.setter
    def minimum_tuning_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minimum Tuning Frequency=' + value])

    @property
    def maximum_tuning_frequency(self) -> float:
        """Maximum Tuning Frequency
        "Maximum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 1e+11."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Maximum Tuning Frequency')
        key_val_pair = [i for i in props if 'Maximum Tuning Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @maximum_tuning_frequency.setter
    def maximum_tuning_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Maximum Tuning Frequency=' + value])

    @property
    def mixer_product_slope(self) -> float:
        """Mixer Product Slope
        "Rate of decrease for amplitude of Rx's local oscillator harmonics (dB/decade)."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Slope')
        key_val_pair = [i for i in props if 'Mixer Product Slope=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mixer_product_slope.setter
    def mixer_product_slope(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Slope=' + value])

    @property
    def mixer_product_intercept(self) -> float:
        """Mixer Product Intercept
        "Mixer product intercept (dBc)."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Intercept')
        key_val_pair = [i for i in props if 'Mixer Product Intercept=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mixer_product_intercept.setter
    def mixer_product_intercept(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Intercept=' + value])

    @property
    def _80_db_bandwidth(self) -> float:
        """80 dB Bandwidth
        "Bandwidth where Rx's susceptibility envelope is 80 dB above in-band susceptibility level."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'80 dB Bandwidth')
        key_val_pair = [i for i in props if '80 dB Bandwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_80_db_bandwidth.setter
    def _80_db_bandwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['80 dB Bandwidth=' + value])

    @property
    def image_rejection(self) -> float:
        """Image Rejection
        "Image frequency amplitude (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Image Rejection')
        key_val_pair = [i for i in props if 'Image Rejection=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @image_rejection.setter
    def image_rejection(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Image Rejection=' + value])

    @property
    def maximum_rf_harmonic_order(self) -> int:
        """Maximum RF Harmonic Order
        "Maximum order of RF frequency."
        "Value should be between 1 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Maximum RF Harmonic Order')
        key_val_pair = [i for i in props if 'Maximum RF Harmonic Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @maximum_rf_harmonic_order.setter
    def maximum_rf_harmonic_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Maximum RF Harmonic Order=' + value])

    @property
    def maximum_lo_harmonic_order(self) -> int:
        """Maximum LO Harmonic Order
        "Maximum order of the LO frequency."
        "Value should be between 1 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Maximum LO Harmonic Order')
        key_val_pair = [i for i in props if 'Maximum LO Harmonic Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @maximum_lo_harmonic_order.setter
    def maximum_lo_harmonic_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Maximum LO Harmonic Order=' + value])

    @property
    def mixing_mode(self):
        """Mixing Mode
        "Specifies whether the IF frequency is > or < RF channel frequency."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixing Mode')
        key_val_pair = [i for i in props if 'Mixing Mode=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mixing_mode.setter
    def mixing_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixing Mode=' + value])
    class MixingModeOption(Enum):
            ABOVETUNEDFREQUENCY = "LO Above Tuned (RF) Frequency"
            BELOWTUNEDFREQUENCY = "LO Below Tuned (RF) Frequency"
            BOTHTUNEDFREQUENCIES = "LO Above/Below Tuned (RF) Frequency"

    @property
    def _1st_if_frequency(self):
        """1st IF Frequency
        "Intermediate frequency for Rx's 1st conversion stage."
        "Value should be a mathematical expression."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'1st IF Frequency')
        key_val_pair = [i for i in props if '1st IF Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @_1st_if_frequency.setter
    def _1st_if_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['1st IF Frequency=' + value])

    @property
    def rf_transition_frequency(self) -> float:
        """RF Transition Frequency
        "RF Frequency Transition point."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'RF Transition Frequency')
        key_val_pair = [i for i in props if 'RF Transition Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @rf_transition_frequency.setter
    def rf_transition_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['RF Transition Frequency=' + value])

    @property
    def use_high_lo(self):
        """Use High LO
        "Use High LO above/below the transition frequency."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use High LO')
        key_val_pair = [i for i in props if 'Use High LO=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @use_high_lo.setter
    def use_high_lo(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use High LO=' + value])
    class UseHighLOOption(Enum):
            ABOVETRANSITION = "Above Transition Frequency"
            BELOWTRANSITION = "Below Transition Frequency"

    @property
    def mixer_product_table_units(self):
        """Mixer Product Table Units
        "Specifies the units for the Mixer Products."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mixer Product Table Units')
        key_val_pair = [i for i in props if 'Mixer Product Table Units=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mixer_product_table_units.setter
    def mixer_product_table_units(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mixer Product Table Units=' + value])
    class MixerProductTableUnitsOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"

