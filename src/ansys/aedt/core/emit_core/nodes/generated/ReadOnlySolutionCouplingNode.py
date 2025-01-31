from ..GenericEmitNode import *
class ReadOnlySolutionCouplingNode(GenericEmitNode):
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
        "Enable/Disable coupling (A sweep disabled in HFSS/Layout cannot be enabled in EMIT)."
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

