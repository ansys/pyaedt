from ..EmitNode import *

class ReadOnlyRxMixerProductNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    class MixerProductTaperOption(Enum):
            CONSTANT = "Constant"
            MIL_STD_461G = "MIL-STD-461G"
            DUFF_MODEL = "Duff Model"

    @property
    def mixer_product_taper(self) -> MixerProductTaperOption:
        """Mixer Product Taper
        "Taper for setting amplitude of mixer products."
        "        """
        val = self._get_property('Mixer Product Taper')
        val = self.MixerProductTaperOption[val]
        return val

    @property
    def mixer_product_susceptibility(self) -> float:
        """Mixer Product Susceptibility
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Mixer Product Susceptibility')
        return val

    @property
    def spurious_rejection(self) -> float:
        """Spurious Rejection
        "Mixer product amplitudes (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Spurious Rejection')
        return val

    @property
    def minimum_tuning_frequency(self) -> float:
        """Minimum Tuning Frequency
        "Minimum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Minimum Tuning Frequency')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def maximum_tuning_frequency(self) -> float:
        """Maximum Tuning Frequency
        "Maximum tuning frequency of Rx's local oscillator."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Maximum Tuning Frequency')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def mixer_product_slope(self) -> float:
        """Mixer Product Slope
        "Rate of decrease for amplitude of Rx's local oscillator harmonics (dB/decade)."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Mixer Product Slope')
        return val

    @property
    def mixer_product_intercept(self) -> float:
        """Mixer Product Intercept
        "Mixer product intercept (dBc)."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Mixer Product Intercept')
        return val

    @property
    def _80_db_bandwidth(self) -> float:
        """80 dB Bandwidth
        "Bandwidth where Rx's susceptibility envelope is 80 dB above in-band susceptibility level."
        "Value should be greater than 1."
        """
        val = self._get_property('80 dB Bandwidth')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def image_rejection(self) -> float:
        """Image Rejection
        "Image frequency amplitude (relative to the in-band susceptibility)."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Image Rejection')
        return val

    @property
    def maximum_rf_harmonic_order(self) -> int:
        """Maximum RF Harmonic Order
        "Maximum order of RF frequency."
        "Value should be between 1 and 100."
        """
        val = self._get_property('Maximum RF Harmonic Order')
        return val

    @property
    def maximum_lo_harmonic_order(self) -> int:
        """Maximum LO Harmonic Order
        "Maximum order of the LO frequency."
        "Value should be between 1 and 100."
        """
        val = self._get_property('Maximum LO Harmonic Order')
        return val

    class MixingModeOption(Enum):
            ABOVETUNEDFREQUENCY = "LO Above Tuned (RF) Frequency"
            BELOWTUNEDFREQUENCY = "LO Below Tuned (RF) Frequency"
            BOTHTUNEDFREQUENCIES = "LO Above/Below Tuned (RF) Frequency"

    @property
    def mixing_mode(self) -> MixingModeOption:
        """Mixing Mode
        "Specifies whether the IF frequency is > or < RF channel frequency."
        "        """
        val = self._get_property('Mixing Mode')
        val = self.MixingModeOption[val]
        return val

    @property
    def _1st_if_frequency(self):
        """1st IF Frequency
        "Intermediate frequency for Rx's 1st conversion stage."
        "Value should be a mathematical expression."
        """
        val = self._get_property('1st IF Frequency')
        return val

    @property
    def rf_transition_frequency(self) -> float:
        """RF Transition Frequency
        "RF Frequency Transition point."
        "        """
        val = self._get_property('RF Transition Frequency')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    class UseHighLOOption(Enum):
            ABOVETRANSITION = "Above Transition Frequency"
            BELOWTRANSITION = "Below Transition Frequency"

    @property
    def use_high_lo(self) -> UseHighLOOption:
        """Use High LO
        "Use High LO above/below the transition frequency."
        "        """
        val = self._get_property('Use High LO')
        val = self.UseHighLOOption[val]
        return val

    class MixerProductTableUnitsOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVE = "Relative"

    @property
    def mixer_product_table_units(self) -> MixerProductTableUnitsOption:
        """Mixer Product Table Units
        "Specifies the units for the Mixer Products."
        "        """
        val = self._get_property('Mixer Product Table Units')
        val = self.MixerProductTableUnitsOption[val]
        return val

