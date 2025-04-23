from enum import Enum
from ..EmitNode import EmitNode

class ReadOnlyIndoorPropagationCouplingNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def table_data(self):
        """ Table"
        "Table consists of 3 columns."
        "Frequency: 
        "    Value should be between 1 and 1e+11."
        "Power Loss Coefficient: 
        "    Value should be between 0 and 100."
        "Floor Penetration Loss (dB): 
        "    Value should be between 0 and 1000."
        """
        return self._get_table_data()

    @property
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enabled")
        return val

    @property
    def antenna_a(self) -> EmitNode:
        """Antenna A
        "First antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property("Antenna A")
        return val

    @property
    def antenna_b(self) -> EmitNode:
        """Antenna B
        "Second antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property("Antenna B")
        return val

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enable Refinement")
        return val

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Adaptive Sampling")
        return val

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property("Refinement Domain")
        return val

    class BuildingTypeOption(Enum):
        RESIDENTIAL_APARTMENT = "Residential Apartment"
        RESIDENTIAL_HOUSE = "Residential House"
        OFFICE_BUILDING = "Office Building"
        COMMERCIAL_BUILDING = "Commercial Building"
        CUSTOM_BUILDING = "Custom Building"

    @property
    def building_type(self) -> BuildingTypeOption:
        """Building Type
        "Specify the building type for the Indoor Propagation model."
        "        """
        val = self._get_property("Building Type")
        val = self.BuildingTypeOption[val]
        return val

    @property
    def number_of_floors(self) -> int:
        """Number of Floors
        "The number of floors separating the antennas.."
        "Value should be between 1 and 3."
        """
        val = self._get_property("Number of Floors")
        return val

    @property
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin
        "Sets a custom fading margin to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Custom Fading Margin")
        return val

    @property
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch
        "Sets a margin for polarization mismatch to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Polarization Mismatch")
        return val

    @property
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss
        "Sets a margin for pointing error loss to be applied to all coupling defined by this node."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Pointing Error Loss")
        return val

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

    @property
    def fading_availability(self) -> float:
        """Fading Availability
        "The probability that the propagation loss in dB is below its median value plus the margin."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Fading Availability")
        return val

    @property
    def std_deviation(self) -> float:
        """Std Deviation
        "Standard deviation modeling the random amount of shadowing loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Std Deviation")
        return val

    @property
    def include_rain_attenuation(self) -> bool:
        """Include Rain Attenuation
        "Adds a margin for rain attenuation to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Include Rain Attenuation")
        return val

    @property
    def rain_availability(self) -> float:
        """Rain Availability
        "Percentage of time attenuation due to range is < computed margin (range from 99-99.999%)."
        "Value should be between 99 and 99.999."
        """
        val = self._get_property("Rain Availability")
        return val

    @property
    def rain_rate(self) -> float:
        """Rain Rate
        "Rain rate (mm/hr) exceeded for 0.01% of the time."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Rain Rate")
        return val

    @property
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle
        "Polarization tilt angle of the transmitted signal relative to the horizontal."
        "Value should be between 0 and 180."
        """
        val = self._get_property("Polarization Tilt Angle")
        return val

    @property
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption
        "Adds a margin for atmospheric absorption due to oxygen/water vapor to the computed coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Include Atmospheric Absorption")
        return val

    @property
    def temperature(self) -> float:
        """Temperature
        "Air temperature in degrees Celsius."
        "Value should be between -273 and 100."
        """
        val = self._get_property("Temperature")
        return val

    @property
    def total_air_pressure(self) -> float:
        """Total Air Pressure
        "Total air pressure."
        "Value should be between 0 and 2000."
        """
        val = self._get_property("Total Air Pressure")
        return val

    @property
    def water_vapor_concentration(self) -> float:
        """Water Vapor Concentration
        "Water vapor concentration."
        "Value should be between 0 and 2000."
        """
        val = self._get_property("Water Vapor Concentration")
        return val

