from ..EmitNode import *

class Circulator(EmitNode):
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
        "Name of file defining the Isolator/Circulator."
        "Value should be a full file path."
        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Filename={value}"])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Noise Temperature")
        return val

    @noise_temperature.setter
    def noise_temperature(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Noise Temperature={value}"])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Notes={value}"])

    class TypeOption(Enum):
        BY_FILE = "By File"
        PARAMETRIC = "Parametric"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of circulator model to use. Options include: By File (measured or simulated) or Parametric."
        "        """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Type={value.value}"])

    class Port1LocationOption(Enum):
        RADIO_SIDE = "Radio Side"
        ANTENNA_SIDE = "Antenna Side"

    @property
    def port_1_location(self) -> Port1LocationOption:
        """Port 1 Location
        "Defines the orientation of the circulator.."
        "        """
        val = self._get_property("Port 1 Location")
        val = self.Port1LocationOption[val]
        return val

    @port_1_location.setter
    def port_1_location(self, value: Port1LocationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Port 1 Location={value.value}"])

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Circulator in-band loss in forward direction.."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Insertion Loss")
        return val

    @insertion_loss.setter
    def insertion_loss(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Insertion Loss={value}"])

    @property
    def finite_reverse_isolation(self) -> bool:
        """Finite Reverse Isolation
        "Use a finite reverse isolation. If disabled, the  circulator model is ideal (infinite reverse isolation).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Finite Reverse Isolation")
        return val

    @finite_reverse_isolation.setter
    def finite_reverse_isolation(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Finite Reverse Isolation={value}"])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        "Circulator reverse isolation (i.e., loss in the reverse direction).."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Reverse Isolation")
        return val

    @reverse_isolation.setter
    def reverse_isolation(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Reverse Isolation={value}"])

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  circulator model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Finite Bandwidth")
        return val

    @finite_bandwidth.setter
    def finite_bandwidth(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Finite Bandwidth={value}"])

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property("Out-of-band Attenuation")
        return val

    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Out-of-band Attenuation={value}"])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @lower_stop_band.setter
    def lower_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Lower Stop Band={value}"])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @lower_cutoff.setter
    def lower_cutoff(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Lower Cutoff={value}"])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @higher_cutoff.setter
    def higher_cutoff(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Higher Cutoff={value}"])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @higher_stop_band.setter
    def higher_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f"Higher Stop Band={value}"])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property("Warnings")
        return val

