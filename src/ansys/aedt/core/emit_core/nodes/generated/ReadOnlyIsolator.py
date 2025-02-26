from ..EmitNode import *

class ReadOnlyIsolator(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    class TypeOption(Enum):
            BYFILE = "By File"
            PARAMETRIC = "Parametric"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of isolator model to use. Options include: By File (measured or simulated) or Parametric."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val]
        return val

    class Port1LocationOption(Enum):
            RADIOSIDE = "Radio Side"
            ANTENNASIDE = "Antenna Side"

    @property
    def port_1_location(self) -> Port1LocationOption:
        """Port 1 Location
        "Defines the orientation of the isolator.."
        "        """
        val = self._get_property('Port 1 Location')
        val = self.Port1LocationOption[val]
        return val

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Isolator in-band loss in forward direction.."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Insertion Loss')
        return val

    @property
    def finite_reverse_isolation(self) -> bool:
        """Finite Reverse Isolation
        "Use a finite reverse isolation. If disabled, the  isolator model is ideal (infinite reverse isolation).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Finite Reverse Isolation')
        return val

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Isolator reverse isolation (i.e., loss in the reverse direction).."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Reverse Isolation')
        return val

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  isolator model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Finite Bandwidth')
        return val

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Out-of-band Attenuation')
        return val

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Stop Band')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Cutoff')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Cutoff')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Stop Band')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

