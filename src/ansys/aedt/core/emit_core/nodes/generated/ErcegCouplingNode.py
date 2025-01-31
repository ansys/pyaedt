from ..GenericEmitNode import *
class ErcegCouplingNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enabled')
        key_val_pair = [i for i in props if 'Enabled=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enabled.setter
    def enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Refinement')
        key_val_pair = [i for i in props if 'Enable Refinement=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @enable_refinement.setter
    def enable_refinement(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Adaptive Sampling')
        key_val_pair = [i for i in props if 'Adaptive Sampling=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @adaptive_sampling.setter
    def adaptive_sampling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Refinement Domain')
        key_val_pair = [i for i in props if 'Refinement Domain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @refinement_domain.setter
    def refinement_domain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

    @property
    def terrain_category(self):
        """Terrain Category
        "Specify the terrain category type for the Erceg model."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Terrain Category')
        key_val_pair = [i for i in props if 'Terrain Category=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @terrain_category.setter
    def terrain_category(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Terrain Category=' + value])
    class TerrainCategoryOption(Enum):
            TYPEA = "Type A"
            TYPEB = "Type B"
            TYPEC = "Type C"

    @property
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin
        "Sets a custom fading margin to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Custom Fading Margin')
        key_val_pair = [i for i in props if 'Custom Fading Margin=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @custom_fading_margin.setter
    def custom_fading_margin(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Custom Fading Margin=' + value])

    @property
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch
        "Sets a margin for polarization mismatch to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Polarization Mismatch')
        key_val_pair = [i for i in props if 'Polarization Mismatch=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @polarization_mismatch.setter
    def polarization_mismatch(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Polarization Mismatch=' + value])

    @property
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss
        "Sets a margin for pointing error loss to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pointing Error Loss')
        key_val_pair = [i for i in props if 'Pointing Error Loss=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @pointing_error_loss.setter
    def pointing_error_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pointing Error Loss=' + value])

    @property
    def fading_type(self):
        """Fading Type
        "Specify the type of fading to include."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Fading Type')
        key_val_pair = [i for i in props if 'Fading Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @fading_type.setter
    def fading_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Fading Type=' + value])
    class FadingTypeOption(Enum):
            NOFADING = "None"
            FASTFADINGONLY = "Fast Fading Only"
            SHADOWINGONLY = "Shadowing Only"
            SHADOWINGANDFASTFADING = "Fast Fading and Shadowing"

    @property
    def fading_availability(self) -> float:
        """Fading Availability
        "The probability that the propagation loss in dB is below its median value plus the margin."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Fading Availability')
        key_val_pair = [i for i in props if 'Fading Availability=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @fading_availability.setter
    def fading_availability(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Fading Availability=' + value])

    @property
    def std_deviation(self) -> float:
        """Std Deviation
        "Standard deviation modeling the random amount of shadowing loss."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Std Deviation')
        key_val_pair = [i for i in props if 'Std Deviation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @std_deviation.setter
    def std_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Std Deviation=' + value])

    @property
    def include_rain_attenuation(self) -> bool:
        """Include Rain Attenuation
        "Adds a margin for rain attenuation to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include Rain Attenuation')
        key_val_pair = [i for i in props if 'Include Rain Attenuation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @include_rain_attenuation.setter
    def include_rain_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include Rain Attenuation=' + value])

    @property
    def rain_availability(self) -> float:
        """Rain Availability
        "Percentage of time attenuation due to range is < computed margin (range from 99-99.999%)."
        "Value should be between 99 and 99.999."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Rain Availability')
        key_val_pair = [i for i in props if 'Rain Availability=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @rain_availability.setter
    def rain_availability(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Rain Availability=' + value])

    @property
    def rain_rate(self) -> float:
        """Rain Rate
        "Rain rate (mm/hr) exceeded for 0.01% of the time."
        "Value should be between 0 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Rain Rate')
        key_val_pair = [i for i in props if 'Rain Rate=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @rain_rate.setter
    def rain_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Rain Rate=' + value])

    @property
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle
        "Polarization tilt angle of the transmitted signal relative to the horizontal."
        "Value should be between 0 and 180."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Polarization Tilt Angle')
        key_val_pair = [i for i in props if 'Polarization Tilt Angle=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @polarization_tilt_angle.setter
    def polarization_tilt_angle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Polarization Tilt Angle=' + value])

    @property
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption
        "Adds a margin for atmospheric absorption due to oxygen/water vapor to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include Atmospheric Absorption')
        key_val_pair = [i for i in props if 'Include Atmospheric Absorption=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @include_atmospheric_absorption.setter
    def include_atmospheric_absorption(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include Atmospheric Absorption=' + value])

    @property
    def temperature(self) -> float:
        """Temperature
        "Air temperature in degrees Celsius."
        "Value should be between -273 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Temperature')
        key_val_pair = [i for i in props if 'Temperature=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @temperature.setter
    def temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Temperature=' + value])

    @property
    def total_air_pressure(self) -> float:
        """Total Air Pressure
        "Total air pressure."
        "Value should be between 0 and 2000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Total Air Pressure')
        key_val_pair = [i for i in props if 'Total Air Pressure=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @total_air_pressure.setter
    def total_air_pressure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Total Air Pressure=' + value])

    @property
    def water_vapor_concentration(self) -> float:
        """Water Vapor Concentration
        "Water vapor concentration."
        "Value should be between 0 and 2000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Water Vapor Concentration')
        key_val_pair = [i for i in props if 'Water Vapor Concentration=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @water_vapor_concentration.setter
    def water_vapor_concentration(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Water Vapor Concentration=' + value])

