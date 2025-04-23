from ..EmitNode import EmitNode

class ReadOnlyCustomCouplingNode(EmitNode):
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
        "Table consists of 2 columns."
        "Frequency: 
        "    Value should be between 1 and 1e+11."
        "Value (dB): 
        "    Value should be between -1000 and 0."
        """
        return self._get_table_data()

    @property
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enabled")
        return val # type: ignore

    @property
    def antenna_a(self) -> EmitNode:
        """Antenna A
        "First antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property("Antenna A")
        return val # type: ignore

    @property
    def antenna_b(self) -> EmitNode:
        """Antenna B
        "Second antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property("Antenna B")
        return val # type: ignore

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enable Refinement")
        return val # type: ignore

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Adaptive Sampling")
        return val # type: ignore

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property("Refinement Domain")
        return val # type: ignore

