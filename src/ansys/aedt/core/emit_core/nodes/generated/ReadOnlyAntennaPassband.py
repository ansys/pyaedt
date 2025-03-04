from ..EmitNode import *

class ReadOnlyAntennaPassband(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def passband_loss(self) -> float:
        """Passband Loss
        "Passband loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Passband Loss')
        return val

    @property
    def out_of_band_attenuation(self) -> float:
        """Out of Band Attenuation
        "Out of band antenna loss."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Out of Band Attenuation')
        return val

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Stop Band')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Cutoff')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Cutoff')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Stop Band')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

