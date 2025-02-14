from ..EmitNode import *

class ReadOnlyRfSystemGroup(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enable_passive_noise(self) -> bool:
        """Enable Passive Noise
        "If true, the noise contributions of antennas and passive components are included in cosite simulation. Note: Antenna and passive component noise is always included in link analysis simulation.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Passive Noise')
        return val

    @property
    def enforce_thermal_noise_floor(self) -> bool:
        """Enforce Thermal Noise Floor
        "If true, all broadband noise is limited by the thermal noise floor (-174 dBm/Hz)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enforce Thermal Noise Floor')
        return val

