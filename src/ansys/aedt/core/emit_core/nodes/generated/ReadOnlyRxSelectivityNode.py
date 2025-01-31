from ..GenericEmitNode import *
class ReadOnlyRxSelectivityNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def use_arithmetic_mean(self) -> bool:
        """Use Arithmetic Mean
        "Uses arithmetic mean to center bandwidths about the tuned channel frequency."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Arithmetic Mean')
        key_val_pair = [i for i in props if 'Use Arithmetic Mean=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

