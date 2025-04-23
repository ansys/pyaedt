from enum import Enum
from ..EmitNode import EmitNode

class MultiplexerBand(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    class TypeOption(Enum):
        BY_FILE = "By File"
        LOW_PASS = "Low Pass"
        HIGH_PASS = "High Pass"
        BAND_PASS = "Band Pass"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of multiplexer pass band to define. The pass band can be defined by file (measured or simulated data) or using one of EMIT's parametric models."
        "        """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val # type: ignore

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Type={value.value}"])

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the multiplexer band."
        "Value should be a full file path."
        """
        val = self._get_property("Filename")
        return val # type: ignore

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Filename={value}"])

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Multiplexer pass band insertion loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Insertion Loss")
        return val # type: ignore

    @insertion_loss.setter
    def insertion_loss(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Insertion Loss={value}"])

    @property
    def stop_band_attenuation(self) -> float:
        """Stop band Attenuation
        "Stop-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property("Stop band Attenuation")
        return val # type: ignore

    @stop_band_attenuation.setter
    def stop_band_attenuation(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Stop band Attenuation={value}"])

    @property
    def max_pass_band(self) -> float:
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Max Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @max_pass_band.setter
    def max_pass_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Max Pass Band={value}"])

    @property
    def min_stop_band(self) -> float:
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Min Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @min_stop_band.setter
    def min_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Min Stop Band={value}"])

    @property
    def max_stop_band(self) -> float:
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Max Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @max_stop_band.setter
    def max_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Max Stop Band={value}"])

    @property
    def min_pass_band(self) -> float:
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Min Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @min_pass_band.setter
    def min_pass_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Min Pass Band={value}"])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @lower_stop_band.setter
    def lower_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Lower Stop Band={value}"])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @lower_cutoff.setter
    def lower_cutoff(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Lower Cutoff={value}"])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @higher_cutoff.setter
    def higher_cutoff(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Higher Cutoff={value}"])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @higher_stop_band.setter
    def higher_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Higher Stop Band={value}"])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property("Warnings")
        return val # type: ignore

