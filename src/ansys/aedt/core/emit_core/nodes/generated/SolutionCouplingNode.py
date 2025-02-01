from ..EmitNode import *

class SolutionCouplingNode(EmitNode):
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
        "Enable/Disable coupling (A sweep disabled in HFSS/Layout cannot be enabled in EMIT)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enabled')
        return val
    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Refinement')
        return val
    @enable_refinement.setter
    def enable_refinement(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adaptive Sampling')
        return val
    @adaptive_sampling.setter
    def adaptive_sampling(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property('Refinement Domain')
        return val
    @refinement_domain.setter
    def refinement_domain(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

