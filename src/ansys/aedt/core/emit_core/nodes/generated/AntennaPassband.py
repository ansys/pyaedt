from ..EmitNode import *

class AntennaPassband(EmitNode):
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

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

    @property
    def passband_loss(self) -> float:
        """Passband Loss
        "Passband loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Passband Loss')
        return val

    @passband_loss.setter
    def passband_loss(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Passband Loss=' + value])

    @property
    def out_of_band_attenuation(self) -> float:
        """Out of Band Attenuation
        "Out of band antenna loss."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Out of Band Attenuation')
        return val

    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Out of Band Attenuation=' + value])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Stop Band')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @lower_stop_band.setter
    def lower_stop_band(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Lower Stop Band=' + f"{value}"])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Lower Cutoff')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @lower_cutoff.setter
    def lower_cutoff(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Lower Cutoff=' + f"{value}"])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Cutoff')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @higher_cutoff.setter
    def higher_cutoff(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Higher Cutoff=' + f"{value}"])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Higher Stop Band')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @higher_stop_band.setter
    def higher_stop_band(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Higher Stop Band=' + f"{value}"])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Notes=' + value])

