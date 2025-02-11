from ..EmitNode import *

class ReadOnlyTxNbEmissionNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    class NarrowbandBehaviorOption(Enum):
            ABSOLUTE = "Absolute Freqs and Power"
            RELATIVEBANDWIDTH = "Relative Freqs and Attenuation"

    @property
    def narrowband_behavior(self) -> NarrowbandBehaviorOption:
        """Narrowband Behavior
        "Specifies the behavior of the parametric narrowband emissions mask."
        "        """
        val = self._get_property('Narrowband Behavior')
        val = self.NarrowbandBehaviorOption[val]
        return val

    @property
    def measurement_frequency(self) -> float:
        """Measurement Frequency
        "Measurement frequency for the absolute freq/amp pairs.."
        "        """
        val = self._get_property('Measurement Frequency')
        return val

