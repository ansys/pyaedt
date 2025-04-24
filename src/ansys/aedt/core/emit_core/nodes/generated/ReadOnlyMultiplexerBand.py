from ..EmitNode import *

class ReadOnlyMultiplexerBand(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    class TypeOption(Enum):
            BYFILE = "By File"
            LOWPASS = "Low Pass"
            HIGHPASS = "High Pass"
            BANDPASS = "Band Pass"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of multiplexer pass band to define. The pass band can be defined by file (measured or simulated data) or using one of EMIT's parametric models."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val.upper()]
        return val

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the multiplexer band."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Multiplexer pass band insertion loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Insertion Loss')
        return val

    @property
    def stop_band_attenuation(self) -> float:
        """Stop band Attenuation
        "Stop-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Stop band Attenuation')
        return val

    @property
    def max_pass_band(self) -> float:
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Pass Band')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def min_stop_band(self) -> float:
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Min Stop Band')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def max_stop_band(self) -> float:
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Stop Band')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def min_pass_band(self) -> float:
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Min Pass Band')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Stop Band')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Cutoff')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Cutoff')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Stop Band')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

