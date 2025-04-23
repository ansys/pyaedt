from enum import Enum
from ..EmitNode import EmitNode

class ReadOnlyTxBbEmissionNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def table_data(self):
        """Tx Broadband Noise Profile Table"
        "Table consists of 2 columns."
        "Frequency (MHz): 
        "    Value should be a mathematical expression."
        "Amplitude (dBm/Hz): 
        "    Value should be between -200 and 150."
        """
        return self._get_table_data()

    class NoiseBehaviorOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVE_BANDWIDTH = "Relative (Bandwidth)"
        RELATIVE_OFFSET = "Relative (Offset)"
        EQUATION = "Equation"

    @property
    def noise_behavior(self) -> NoiseBehaviorOption:
        """Noise Behavior
        "Specifies the behavior of the parametric noise profile."
        "        """
        val = self._get_property("Noise Behavior")
        val = self.NoiseBehaviorOption[val]
        return val # type: ignore

    @property
    def use_log_linear_interpolation(self) -> bool:
        """Use Log-Linear Interpolation
        "If true, linear interpolation in the log domain is used. If false, linear interpolation in the linear domain is used.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Use Log-Linear Interpolation")
        return val # type: ignore

