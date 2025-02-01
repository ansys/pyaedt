from ..EmitNode import *

class MultiplexerBand(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

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
        val = self.TypeOption[val]
        return val
    @type.setter
    def type(self, value: TypeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Type=' + value.value])

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the multiplexer band."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val
    @filename.setter
    def filename(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Multiplexer pass band insertion loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Insertion Loss')
        return val
    @insertion_loss.setter
    def insertion_loss(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Insertion Loss=' + value])

    @property
    def stop_band_attenuation(self) -> float:
        """Stop band Attenuation
        "Stop-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Stop band Attenuation')
        return val
    @stop_band_attenuation.setter
    def stop_band_attenuation(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Stop band Attenuation=' + value])

    @property
    def max_pass_band(self) -> float:
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Pass Band')
        return val
    @max_pass_band.setter
    def max_pass_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max Pass Band=' + value])

    @property
    def min_stop_band(self) -> float:
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Min Stop Band')
        return val
    @min_stop_band.setter
    def min_stop_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Min Stop Band=' + value])

    @property
    def max_stop_band(self) -> float:
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Max Stop Band')
        return val
    @max_stop_band.setter
    def max_stop_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max Stop Band=' + value])

    @property
    def min_pass_band(self) -> float:
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Min Pass Band')
        return val
    @min_pass_band.setter
    def min_pass_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Min Pass Band=' + value])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Stop Band')
        return val
    @lower_stop_band.setter
    def lower_stop_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Lower Stop Band=' + value])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Cutoff')
        return val
    @lower_cutoff.setter
    def lower_cutoff(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Lower Cutoff=' + value])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Cutoff')
        return val
    @higher_cutoff.setter
    def higher_cutoff(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Higher Cutoff=' + value])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Stop Band')
        return val
    @higher_stop_band.setter
    def higher_stop_band(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Higher Stop Band=' + value])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val
