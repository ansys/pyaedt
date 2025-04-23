from enum import Enum
from ..EmitNode import EmitNode

class PowerDivider(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

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
    def filename(self) -> str:
        """Filename
        "Name of file defining the Power Divider."
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
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Noise Temperature")
        return val # type: ignore

    @noise_temperature.setter
    def noise_temperature(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Noise Temperature={value}"])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property("Notes")
        return val # type: ignore

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Notes={value}"])

    class TypeOption(Enum):
        BY_FILE = "By File"
        P3_DB = "P3 dB"
        RESISTIVE = "Resistive"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of Power Divider model to use. Options include: By File (measured or simulated), 3 dB (parametric), and Resistive (parametric)."
        "        """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val # type: ignore

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Type={value.value}"])

    class OrientationOption(Enum):
        DIVIDER = "Divider"
        COMBINER = "Combiner"

    @property
    def orientation(self) -> OrientationOption:
        """Orientation
        "Defines the orientation of the Power Divider.."
        "        """
        val = self._get_property("Orientation")
        val = self.OrientationOption[val]
        return val # type: ignore

    @orientation.setter
    def orientation(self, value: OrientationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Orientation={value.value}"])

    @property
    def insertion_loss_above_ideal(self) -> float:
        """Insertion Loss Above Ideal
        "Additional loss beyond the ideal insertion loss. The ideal insertion loss is 3 dB for the 3 dB Divider and 6 dB for the Resistive Divider.."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Insertion Loss Above Ideal")
        return val # type: ignore

    @insertion_loss_above_ideal.setter
    def insertion_loss_above_ideal(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Insertion Loss Above Ideal={value}"])

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation
        "Use a finite isolation between output ports. If disabled, the Power Divider isolation is ideal (infinite isolation between output ports).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Finite Isolation")
        return val # type: ignore

    @finite_isolation.setter
    def finite_isolation(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Finite Isolation={value}"])

    @property
    def isolation(self) -> float:
        """Isolation
        "Power Divider isolation between output ports.."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Isolation")
        return val # type: ignore

    @isolation.setter
    def isolation(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Isolation={value}"])

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  Power Divider model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Finite Bandwidth")
        return val # type: ignore

    @finite_bandwidth.setter
    def finite_bandwidth(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Finite Bandwidth={value}"])

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property("Out-of-band Attenuation")
        return val # type: ignore

    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Out-of-band Attenuation={value}"])

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

