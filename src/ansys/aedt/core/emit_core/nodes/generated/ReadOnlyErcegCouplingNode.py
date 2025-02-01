from ..EmitNode import *

class ReadOnlyErcegCouplingNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

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
        val = self._get_property('Enabled')
        return val
    @property
    def base_antenna(self) -> EmitNode:
        """Base Antenna
        "First antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property('Base Antenna')
        return val
    @property
    def mobile_antenna(self) -> EmitNode:
        """Mobile Antenna
        "Second antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property('Mobile Antenna')
        return val
    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Refinement')
        return val
    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adaptive Sampling')
        return val
    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property('Refinement Domain')
        return val
    class TerrainCategoryOption(Enum):
            TYPEA = "Type A"
            TYPEB = "Type B"
            TYPEC = "Type C"
    @property
    def terrain_category(self) -> TerrainCategoryOption:
        """Terrain Category
        "Specify the terrain category type for the Erceg model."
        "        """
        val = self._get_property('Terrain Category')
        val = self.TerrainCategoryOption[val]
        return val
    @property
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin
        "Sets a custom fading margin to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Custom Fading Margin')
        return val
    @property
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch
        "Sets a margin for polarization mismatch to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Polarization Mismatch')
        return val
    @property
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss
        "Sets a margin for pointing error loss to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Pointing Error Loss')
        return val
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
    @property
    def fading_availability(self) -> float:
        """Fading Availability
        "The probability that the propagation loss in dB is below its median value plus the margin."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Fading Availability')
        return val
    @property
    def std_deviation(self) -> float:
        """Std Deviation
        "Standard deviation modeling the random amount of shadowing loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Std Deviation')
        return val
    @property
    def include_rain_attenuation(self) -> bool:
        """Include Rain Attenuation
        "Adds a margin for rain attenuation to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include Rain Attenuation')
        return val
    @property
    def rain_availability(self) -> float:
        """Rain Availability
        "Percentage of time attenuation due to range is < computed margin (range from 99-99.999%)."
        "Value should be between 99 and 99.999."
        """
        val = self._get_property('Rain Availability')
        return val
    @property
    def rain_rate(self) -> float:
        """Rain Rate
        "Rain rate (mm/hr) exceeded for 0.01% of the time."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Rain Rate')
        return val
    @property
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle
        "Polarization tilt angle of the transmitted signal relative to the horizontal."
        "Value should be between 0 and 180."
        """
        val = self._get_property('Polarization Tilt Angle')
        return val
    @property
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption
        "Adds a margin for atmospheric absorption due to oxygen/water vapor to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include Atmospheric Absorption')
        return val
    @property
    def temperature(self) -> float:
        """Temperature
        "Air temperature in degrees Celsius."
        "Value should be between -273 and 100."
        """
        val = self._get_property('Temperature')
        return val
    @property
    def total_air_pressure(self) -> float:
        """Total Air Pressure
        "Total air pressure."
        "Value should be between 0 and 2000."
        """
        val = self._get_property('Total Air Pressure')
        return val
    @property
    def water_vapor_concentration(self) -> float:
        """Water Vapor Concentration
        "Water vapor concentration."
        "Value should be between 0 and 2000."
        """
        val = self._get_property('Water Vapor Concentration')
        return val
