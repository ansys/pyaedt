from ..EmitNode import *

class TxNbEmissionNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,"Csv")

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"enabled= + {value}"])

    class NarrowbandBehaviorOption(Enum):
        ABSOLUTE_FREQS_AND_POWER = "Absolute Freqs and Power"
        RELATIVE_FREQS_AND_ATTENUATION = "Relative Freqs and Attenuation"

    @property
    def narrowband_behavior(self) -> NarrowbandBehaviorOption:
        """Narrowband Behavior
        "Specifies the behavior of the parametric narrowband emissions mask."
        "        """
        val = self._get_property("Narrowband Behavior")
        val = self.NarrowbandBehaviorOption[val]
        return val

    @narrowband_behavior.setter
    def narrowband_behavior(self, value: NarrowbandBehaviorOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Narrowband Behavior={value.value}"])

    @property
    def measurement_frequency(self) -> float:
        """Measurement Frequency
        "Measurement frequency for the absolute freq/amp pairs.."
        "        """
        val = self._get_property("Measurement Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @measurement_frequency.setter
    def measurement_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Measurement Frequency={value}"])

