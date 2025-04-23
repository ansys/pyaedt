from enum import Enum
from ..EmitNode import EmitNode

class ReadOnlyTxNbEmissionNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    class NarrowbandBehaviorOption(Enum):
        ABSOLUTE_FREQS_AND_POWER = "Absolute Freqs and Power"
        RELATIVE_FREQS_AND_ATTENUATION = "Relative Freqs and Attenuation"

    @property
    def narrowband_behavior(self) -> NarrowbandBehaviorOption:
        """Narrowband Behavior
        "Specifies the behavior of the parametric narrowband emissions mask."
        "        """
        val = self._get_property("Narrowband Behavior")
        val = self.NarrowbandBehaviorOption[val]
        return val

    @property
    def measurement_frequency(self) -> float:
        """Measurement Frequency
        "Measurement frequency for the absolute freq/amp pairs.."
        "        """
        val = self._get_property("Measurement Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

