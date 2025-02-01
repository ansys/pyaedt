from ..EmitNode import *

class PropagationLossCouplingNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

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
        val = self._get_property('Enabled')
        return val
    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def antenna_a(self) -> EmitNode:
        """Antenna A
        "First antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property('Antenna A')
        return val
    @antenna_a.setter
    def antenna_a(self, value: EmitNode):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna A=' + value])

    @property
    def antenna_b(self) -> EmitNode:
        """Antenna B
        "Second antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property('Antenna B')
        return val
    @antenna_b.setter
    def antenna_b(self, value: EmitNode):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna B=' + value])

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Refinement')
        return val
    @enable_refinement.setter
    def enable_refinement(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adaptive Sampling')
        return val
    @adaptive_sampling.setter
    def adaptive_sampling(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property('Refinement Domain')
        return val
    @refinement_domain.setter
    def refinement_domain(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

    @property
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin
        "Sets a custom fading margin to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Custom Fading Margin')
        return val
    @custom_fading_margin.setter
    def custom_fading_margin(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Custom Fading Margin=' + value])

    @property
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch
        "Sets a margin for polarization mismatch to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Polarization Mismatch')
        return val
    @polarization_mismatch.setter
    def polarization_mismatch(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Polarization Mismatch=' + value])

    @property
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss
        "Sets a margin for pointing error loss to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Pointing Error Loss')
        return val
    @pointing_error_loss.setter
    def pointing_error_loss(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Pointing Error Loss=' + value])

    class FadingTypeOption(Enum):
            NOFADING = "None"
            FASTFADINGONLY = "Fast Fading Only"
            SHADOWINGONLY = "Shadowing Only"
            SHADOWINGANDFASTFADING = "Fast Fading and Shadowing"
    @property
    def fading_type(self) -> FadingTypeOption:
        """Fading Type
        "Specify the type of fading to include."
        "        """
        val = self._get_property('Fading Type')
        val = self.FadingTypeOption[val]
        return val
    @fading_type.setter
    def fading_type(self, value: FadingTypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Fading Type=' + value.value])

    @property
    def fading_availability(self) -> float:
        """Fading Availability
        "The probability that the propagation loss in dB is below its median value plus the margin."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Fading Availability')
        return val
    @fading_availability.setter
    def fading_availability(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Fading Availability=' + value])

    @property
    def std_deviation(self) -> float:
        """Std Deviation
        "Standard deviation modeling the random amount of shadowing loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Std Deviation')
        return val
    @std_deviation.setter
    def std_deviation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Std Deviation=' + value])

    @property
    def include_rain_attenuation(self) -> bool:
        """Include Rain Attenuation
        "Adds a margin for rain attenuation to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include Rain Attenuation')
        return val
    @include_rain_attenuation.setter
    def include_rain_attenuation(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Include Rain Attenuation=' + value])

    @property
    def rain_availability(self) -> float:
        """Rain Availability
        "Percentage of time attenuation due to range is < computed margin (range from 99-99.999%)."
        "Value should be between 99 and 99.999."
        """
        val = self._get_property('Rain Availability')
        return val
    @rain_availability.setter
    def rain_availability(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Rain Availability=' + value])

    @property
    def rain_rate(self) -> float:
        """Rain Rate
        "Rain rate (mm/hr) exceeded for 0.01% of the time."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Rain Rate')
        return val
    @rain_rate.setter
    def rain_rate(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Rain Rate=' + value])

    @property
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle
        "Polarization tilt angle of the transmitted signal relative to the horizontal."
        "Value should be between 0 and 180."
        """
        val = self._get_property('Polarization Tilt Angle')
        return val
    @polarization_tilt_angle.setter
    def polarization_tilt_angle(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Polarization Tilt Angle=' + value])

    @property
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption
        "Adds a margin for atmospheric absorption due to oxygen/water vapor to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include Atmospheric Absorption')
        return val
    @include_atmospheric_absorption.setter
    def include_atmospheric_absorption(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Include Atmospheric Absorption=' + value])

    @property
    def temperature(self) -> float:
        """Temperature
        "Air temperature in degrees Celsius."
        "Value should be between -273 and 100."
        """
        val = self._get_property('Temperature')
        return val
    @temperature.setter
    def temperature(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Temperature=' + value])

    @property
    def total_air_pressure(self) -> float:
        """Total Air Pressure
        "Total air pressure."
        "Value should be between 0 and 2000."
        """
        val = self._get_property('Total Air Pressure')
        return val
    @total_air_pressure.setter
    def total_air_pressure(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Total Air Pressure=' + value])

    @property
    def water_vapor_concentration(self) -> float:
        """Water Vapor Concentration
        "Water vapor concentration."
        "Value should be between 0 and 2000."
        """
        val = self._get_property('Water Vapor Concentration')
        return val
    @water_vapor_concentration.setter
    def water_vapor_concentration(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Water Vapor Concentration=' + value])

