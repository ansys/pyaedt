from enum import Enum
from ..EmitNode import EmitNode

class FiveGChannelModel(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

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
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enabled")
        return val

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Enabled={value}"])

    @property
    def base_antenna(self) -> EmitNode:
        """Base Antenna
        "First antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property("Base Antenna")
        return val

    @base_antenna.setter
    def base_antenna(self, value: EmitNode):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Base Antenna={value}"])

    @property
    def mobile_antenna(self) -> EmitNode:
        """Mobile Antenna
        "Second antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property("Mobile Antenna")
        return val

    @mobile_antenna.setter
    def mobile_antenna(self, value: EmitNode):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Mobile Antenna={value}"])

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enable Refinement")
        return val

    @enable_refinement.setter
    def enable_refinement(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Enable Refinement={value}"])

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Adaptive Sampling")
        return val

    @adaptive_sampling.setter
    def adaptive_sampling(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Adaptive Sampling={value}"])

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property("Refinement Domain")
        return val

    @refinement_domain.setter
    def refinement_domain(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Refinement Domain={value}"])

    class EnvironmentOption(Enum):
        URBAN_MICROCELL = "Urban Microcell"
        URBAN_MACROCELL = "Urban Macrocell"
        RURAL_MACROCELL = "Rural Macrocell"

    @property
    def environment(self) -> EnvironmentOption:
        """Environment
        "Specify the environment for the 5G channel model."
        "        """
        val = self._get_property("Environment")
        val = self.EnvironmentOption[val]
        return val

    @environment.setter
    def environment(self, value: EnvironmentOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Environment={value.value}"])

    @property
    def los(self) -> bool:
        """LOS
        "True if the operating environment is line-of-sight."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("LOS")
        return val

    @los.setter
    def los(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"LOS={value}"])

    @property
    def include_bpl(self) -> bool:
        """Include BPL
        "Includes building penetration loss if true."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Include BPL")
        return val

    @include_bpl.setter
    def include_bpl(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Include BPL={value}"])

    class NYUBPLModelOption(Enum):
        LOW_LOSS_MODEL = "Low-loss model"
        HIGH_LOSS_MODEL = "High-loss model"

    @property
    def nyu_bpl_model(self) -> NYUBPLModelOption:
        """NYU BPL Model
        "Specify the NYU Building Penetration Loss model."
        "        """
        val = self._get_property("NYU BPL Model")
        val = self.NYUBPLModelOption[val]
        return val

    @nyu_bpl_model.setter
    def nyu_bpl_model(self, value: NYUBPLModelOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"NYU BPL Model={value.value}"])

    @property
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin
        "Sets a custom fading margin to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Custom Fading Margin")
        return val

    @custom_fading_margin.setter
    def custom_fading_margin(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Custom Fading Margin={value}"])

    @property
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch
        "Sets a margin for polarization mismatch to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Polarization Mismatch")
        return val

    @polarization_mismatch.setter
    def polarization_mismatch(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Polarization Mismatch={value}"])

    @property
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss
        "Sets a margin for pointing error loss to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Pointing Error Loss")
        return val

    @pointing_error_loss.setter
    def pointing_error_loss(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Pointing Error Loss={value}"])

    class FadingTypeOption(Enum):
        NONE = "None"
        FAST_FADING_ONLY = "Fast Fading Only"
        SHADOWING_ONLY = "Shadowing Only"
        FAST_FADING_AND_SHADOWING = "Fast Fading and Shadowing"

    @property
    def fading_type(self) -> FadingTypeOption:
        """Fading Type
        "Specify the type of fading to include."
        "        """
        val = self._get_property("Fading Type")
        val = self.FadingTypeOption[val]
        return val

    @fading_type.setter
    def fading_type(self, value: FadingTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Fading Type={value.value}"])

    @property
    def fading_availability(self) -> float:
        """Fading Availability
        "The probability that the propagation loss in dB is below its median value plus the margin."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Fading Availability")
        return val

    @fading_availability.setter
    def fading_availability(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Fading Availability={value}"])

    @property
    def std_deviation(self) -> float:
        """Std Deviation
        "Standard deviation modeling the random amount of shadowing loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Std Deviation")
        return val

    @std_deviation.setter
    def std_deviation(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Std Deviation={value}"])

    @property
    def include_rain_attenuation(self) -> bool:
        """Include Rain Attenuation
        "Adds a margin for rain attenuation to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Include Rain Attenuation")
        return val

    @include_rain_attenuation.setter
    def include_rain_attenuation(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Include Rain Attenuation={value}"])

    @property
    def rain_availability(self) -> float:
        """Rain Availability
        "Percentage of time attenuation due to range is < computed margin (range from 99-99.999%)."
        "Value should be between 99 and 99.999."
        """
        val = self._get_property("Rain Availability")
        return val

    @rain_availability.setter
    def rain_availability(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Rain Availability={value}"])

    @property
    def rain_rate(self) -> float:
        """Rain Rate
        "Rain rate (mm/hr) exceeded for 0.01% of the time."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Rain Rate")
        return val

    @rain_rate.setter
    def rain_rate(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Rain Rate={value}"])

    @property
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle
        "Polarization tilt angle of the transmitted signal relative to the horizontal."
        "Value should be between 0 and 180."
        """
        val = self._get_property("Polarization Tilt Angle")
        return val

    @polarization_tilt_angle.setter
    def polarization_tilt_angle(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Polarization Tilt Angle={value}"])

    @property
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption
        "Adds a margin for atmospheric absorption due to oxygen/water vapor to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Include Atmospheric Absorption")
        return val

    @include_atmospheric_absorption.setter
    def include_atmospheric_absorption(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Include Atmospheric Absorption={value}"])

    @property
    def temperature(self) -> float:
        """Temperature
        "Air temperature in degrees Celsius."
        "Value should be between -273 and 100."
        """
        val = self._get_property("Temperature")
        return val

    @temperature.setter
    def temperature(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Temperature={value}"])

    @property
    def total_air_pressure(self) -> float:
        """Total Air Pressure
        "Total air pressure."
        "Value should be between 0 and 2000."
        """
        val = self._get_property("Total Air Pressure")
        return val

    @total_air_pressure.setter
    def total_air_pressure(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Total Air Pressure={value}"])

    @property
    def water_vapor_concentration(self) -> float:
        """Water Vapor Concentration
        "Water vapor concentration."
        "Value should be between 0 and 2000."
        """
        val = self._get_property("Water Vapor Concentration")
        return val

    @water_vapor_concentration.setter
    def water_vapor_concentration(self, value : float)
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Water Vapor Concentration={value}"])

