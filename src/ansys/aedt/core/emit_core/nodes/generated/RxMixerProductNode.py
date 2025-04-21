from ..EmitNode import *

class RxMixerProductNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,"Csv")

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"enabled= + {value}"])

    class MixerProductTaperOption(Enum):
        CONSTANT = "Constant"
        MIL_STD_461G = "MIL-STD-461G"
        DUFF_MODEL = "Duff Model"

    @property
    def mixer_product_taper(self) -> MixerProductTaperOption:
        """Mixer Product Taper
        "Taper for setting amplitude of mixer products."
        "        """
        val = self._get_property("Mixer Product Taper")
        val = self.MixerProductTaperOption[val]
        return val

    @mixer_product_taper.setter
    def mixer_product_taper(self, value: MixerProductTaperOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mixer Product Taper={value.value}"])

    @property
    def mixer_product_susceptibility(self) -> float:
        """Mixer Product Susceptibility
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        val = self._get_property("Mixer Product Susceptibility")
        return val

    @mixer_product_susceptibility.setter
    def mixer_product_susceptibility(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mixer Product Susceptibility={value}"])

    @property
    def spurious_rejection(self) -> float:
        """Spurious Rejection
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        val = self._get_property("Spurious Rejection")
        return val

    @spurious_rejection.setter
    def spurious_rejection(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Spurious Rejection={value}"])

    @property
    def minimum_tuning_frequency(self) -> float:
        """Minimum Tuning Frequency
        "Minimum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Minimum Tuning Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @minimum_tuning_frequency.setter
    def minimum_tuning_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Minimum Tuning Frequency={value}"])

    @property
    def maximum_tuning_frequency(self) -> float:
        """Maximum Tuning Frequency
        "Maximum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Maximum Tuning Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @maximum_tuning_frequency.setter
    def maximum_tuning_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Maximum Tuning Frequency={value}"])

    @property
    def mixer_product_slope(self) -> float:
        """Mixer Product Slope
        "Rate of decrease for amplitude of Rx's local oscillator harmonics (dB/decade)."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Mixer Product Slope")
        return val

    @mixer_product_slope.setter
    def mixer_product_slope(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mixer Product Slope={value}"])

    @property
    def mixer_product_intercept(self) -> float:
        """Mixer Product Intercept
        "Mixer product intercept (dBc)."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Mixer Product Intercept")
        return val

    @mixer_product_intercept.setter
    def mixer_product_intercept(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mixer Product Intercept={value}"])

    @property
    def bandwidth_80_db(self) -> float:
        """Bandwidth 80 dB
        "Bandwidth where Rx's susceptibility envelope is 80 dB above in-band susceptibility level."
        "Value should be greater than 1."
        """
        val = self._get_property("Bandwidth 80 dB")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @bandwidth_80_db.setter
    def bandwidth_80_db(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Bandwidth 80 dB={value}"])

    @property
    def image_rejection(self) -> float:
        """Image Rejection
        "Image frequency amplitude (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        val = self._get_property("Image Rejection")
        return val

    @image_rejection.setter
    def image_rejection(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Image Rejection={value}"])

    @property
    def maximum_rf_harmonic_order(self) -> int:
        """Maximum RF Harmonic Order
        "Maximum order of RF frequency."
        "Value should be between 1 and 100."
        """
        val = self._get_property("Maximum RF Harmonic Order")
        return val

    @maximum_rf_harmonic_order.setter
    def maximum_rf_harmonic_order(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Maximum RF Harmonic Order={value}"])

    @property
    def maximum_lo_harmonic_order(self) -> int:
        """Maximum LO Harmonic Order
        "Maximum order of the LO frequency."
        "Value should be between 1 and 100."
        """
        val = self._get_property("Maximum LO Harmonic Order")
        return val

    @maximum_lo_harmonic_order.setter
    def maximum_lo_harmonic_order(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Maximum LO Harmonic Order={value}"])

    class MixingModeOption(Enum):
        LO_ABOVE_TUNED_RF_FREQUENCY = "LO Above Tuned (RF) Frequency"
        LO_BELOW_TUNED_RF_FREQUENCY = "LO Below Tuned (RF) Frequency"
        LO_ABOVEBELOW_TUNED_RF_FREQUENCY = "LO Above/Below Tuned (RF) Frequency"

    @property
    def mixing_mode(self) -> MixingModeOption:
        """Mixing Mode
        "Specifies whether the IF frequency is > or < RF channel frequency."
        "        """
        val = self._get_property("Mixing Mode")
        val = self.MixingModeOption[val]
        return val

    @mixing_mode.setter
    def mixing_mode(self, value: MixingModeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mixing Mode={value.value}"])

    @property
    def first_if_frequency(self):
        """First IF Frequency
        "Intermediate frequency for Rx's 1st conversion stage."
        "Value should be a mathematical expression."
        """
        val = self._get_property("First IF Frequency")
        return val

    @first_if_frequency.setter
    def first_if_frequency(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"First IF Frequency={value}"])

    @property
    def rf_transition_frequency(self) -> float:
        """RF Transition Frequency
        "RF Frequency Transition point."
        "        """
        val = self._get_property("RF Transition Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @rf_transition_frequency.setter
    def rf_transition_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"RF Transition Frequency={value}"])

    class UseHighLOOption(Enum):
        ABOVE_TRANSITION_FREQUENCY = "Above Transition Frequency"
        BELOW_TRANSITION_FREQUENCY = "Below Transition Frequency"

    @property
    def use_high_lo(self) -> UseHighLOOption:
        """Use High LO
        "Use High LO above/below the transition frequency."
        "        """
        val = self._get_property("Use High LO")
        val = self.UseHighLOOption[val]
        return val

    @use_high_lo.setter
    def use_high_lo(self, value: UseHighLOOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Use High LO={value.value}"])

    class MixerProductTableUnitsOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVE = "Relative"

    @property
    def mixer_product_table_units(self) -> MixerProductTableUnitsOption:
        """Mixer Product Table Units
        "Specifies the units for the Mixer Products."
        "        """
        val = self._get_property("Mixer Product Table Units")
        val = self.MixerProductTableUnitsOption[val]
        return val

    @mixer_product_table_units.setter
    def mixer_product_table_units(self, value: MixerProductTableUnitsOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mixer Product Table Units={value.value}"])

