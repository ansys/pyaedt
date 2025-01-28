class Node_FiveGChannelModel(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
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
    def get_enabled(self):
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def get_enable_refinement(self):
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Enable Refinement')
    def set_enable_refinement(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def get_adaptive_sampling(self):
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Adaptive Sampling')
    def set_adaptive_sampling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def get_refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Refinement Domain')
    def set_refinement_domain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

    @property
    def get_environment(self):
        """Environment
        "Specify the environment for the 5G channel model."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Environment')
    def set_environment(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Environment=' + value])
    class EnvironmentOption(Enum):
        (
            URBANMICROCELL = "Urban Microcell"
            URBANMACROCELL = "Urban Macrocell"
            RURALMACROCELL = "Rural Macrocell"
        )

    @property
    def get_los(self):
        """LOS
        "True if the operating environment is line-of-sight."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'LOS')
    def set_los(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['LOS=' + value])

    @property
    def get_include_bpl(self):
        """Include BPL
        "Includes building penetration loss if true."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include BPL')
    def set_include_bpl(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include BPL=' + value])

    @property
    def get_nyu_bpl_model(self):
        """NYU BPL Model
        "Specify the NYU Building Penetration Loss model."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'NYU BPL Model')
    def set_nyu_bpl_model(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['NYU BPL Model=' + value])
    class NYUBPLModelOption(Enum):
        (
            LOWLOSSMODEL = "Low-loss model"
            HIGHLOSSMODEL = "High-loss model"
        )

    @property
    def get_custom_fading_margin(self):
        """Custom Fading Margin
        "Sets a custom fading margin to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Custom Fading Margin')
    def set_custom_fading_margin(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Custom Fading Margin=' + value])

    @property
    def get_polarization_mismatch(self):
        """Polarization Mismatch
        "Sets a margin for polarization mismatch to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Polarization Mismatch')
    def set_polarization_mismatch(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Polarization Mismatch=' + value])

    @property
    def get_pointing_error_loss(self):
        """Pointing Error Loss
        "Sets a margin for pointing error loss to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Pointing Error Loss')
    def set_pointing_error_loss(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Pointing Error Loss=' + value])

    @property
    def get_fading_type(self):
        """Fading Type
        "Specify the type of fading to include."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Fading Type')
    def set_fading_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Fading Type=' + value])
    class FadingTypeOption(Enum):
        (
            NOFADING = "None"
            FASTFADINGONLY = "Fast Fading Only"
            SHADOWINGONLY = "Shadowing Only"
            SHADOWINGANDFASTFADING = "Fast Fading and Shadowing"
        )

    @property
    def get_fading_availability(self):
        """Fading Availability
        "The probability that the propagation loss in dB is below its median value plus the margin."
        "Value should be between 0.0 and 100.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Fading Availability')
    def set_fading_availability(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Fading Availability=' + value])

    @property
    def get_std_deviation(self):
        """Std Deviation
        "Standard deviation modeling the random amount of shadowing loss."
        "Value should be between 0.0 and 100.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Std Deviation')
    def set_std_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Std Deviation=' + value])

    @property
    def get_include_rain_attenuation(self):
        """Include Rain Attenuation
        "Adds a margin for rain attenuation to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include Rain Attenuation')
    def set_include_rain_attenuation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include Rain Attenuation=' + value])

    @property
    def get_rain_availability(self):
        """Rain Availability
        "Percentage of time attenuation due to range is < computed margin (range from 99-99.999%)."
        "Value should be between 99 and 99.999."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Rain Availability')
    def set_rain_availability(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Rain Availability=' + value])

    @property
    def get_rain_rate(self):
        """Rain Rate
        "Rain rate (mm/hr) exceeded for 0.01% of the time."
        "Value should be between 0.0 and 1000.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Rain Rate')
    def set_rain_rate(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Rain Rate=' + value])

    @property
    def get_polarization_tilt_angle(self):
        """Polarization Tilt Angle
        "Polarization tilt angle of the transmitted signal relative to the horizontal."
        "Value should be between 0.0 and 180.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Polarization Tilt Angle')
    def set_polarization_tilt_angle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Polarization Tilt Angle=' + value])

    @property
    def get_include_atmospheric_absorption(self):
        """Include Atmospheric Absorption
        "Adds a margin for atmospheric absorption due to oxygen/water vapor to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include Atmospheric Absorption')
    def set_include_atmospheric_absorption(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include Atmospheric Absorption=' + value])

    @property
    def get_temperature(self):
        """Temperature
        "Air temperature in degrees Celsius."
        "Value should be between -273.0 and 100.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Temperature')
    def set_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Temperature=' + value])

    @property
    def get_total_air_pressure(self):
        """Total Air Pressure
        "Total air pressure."
        "Value should be between 0.0 and 2000.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Total Air Pressure')
    def set_total_air_pressure(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Total Air Pressure=' + value])

    @property
    def get_water_vapor_concentration(self):
        """Water Vapor Concentration
        "Water vapor concentration."
        "Value should be between 0.0 and 2000.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Water Vapor Concentration')
    def set_water_vapor_concentration(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Water Vapor Concentration=' + value])

