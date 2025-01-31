from ..GenericEmitNode import *
class ReadOnlyFiveGChannelModel(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

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

    @property
    def environment(self):
        """Environment
        "Specify the environment for the 5G channel model."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Environment')
        key_val_pair = [i for i in props if 'Environment=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class EnvironmentOption(Enum):
            URBANMICROCELL = "Urban Microcell"
            URBANMACROCELL = "Urban Macrocell"
            RURALMACROCELL = "Rural Macrocell"

    @property
    def los(self) -> bool:
        """LOS
        "True if the operating environment is line-of-sight."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'LOS')
        key_val_pair = [i for i in props if 'LOS=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def include_bpl(self) -> bool:
        """Include BPL
        "Includes building penetration loss if true."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include BPL')
        key_val_pair = [i for i in props if 'Include BPL=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def nyu_bpl_model(self):
        """NYU BPL Model
        "Specify the NYU Building Penetration Loss model."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'NYU BPL Model')
        key_val_pair = [i for i in props if 'NYU BPL Model=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class NYUBPLModelOption(Enum):
            LOWLOSSMODEL = "Low-loss model"
            HIGHLOSSMODEL = "High-loss model"

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

