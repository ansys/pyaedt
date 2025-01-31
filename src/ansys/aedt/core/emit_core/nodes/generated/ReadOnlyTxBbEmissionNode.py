from ..GenericEmitNode import *
class ReadOnlyTxBbEmissionNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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

    @property
    def noise_behavior(self):
        """Noise Behavior
        "Specifies the behavior of the parametric noise profile."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Behavior')
        key_val_pair = [i for i in props if 'Noise Behavior=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class NoiseBehaviorOption(Enum):
            ABSOLUTE = "Absolute"
            RELATIVEBANDWIDTH = "Relative (Bandwidth)"
            RELATIVEOFFSET = "Relative (Offset)"
            BROADBANDEQUATION = "Equation"

    @property
    def use_log_linear_interpolation(self) -> bool:
        """Use Log-Linear Interpolation
        "If true, linear interpolation in the log domain is used. If false, linear interpolation in the linear domain is used.."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Log-Linear Interpolation')
        key_val_pair = [i for i in props if 'Use Log-Linear Interpolation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

