from ..EmitNode import *

class Cable(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Filename={value}'])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @noise_temperature.setter
    def noise_temperature(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Noise Temperature={value}'])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Notes={value}'])

    class TypeOption(Enum):
            BYFILE = "By File"
            CONSTANT = "Constant Loss"
            COAXIAL = "Coaxial Cable"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of cable to use. Options include: By File (measured or simulated), Constant Loss, or Coaxial Cable."
        "        """
        val = self._get_property('Type')
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Type={value.value}'])

    @property
    def length(self) -> float:
        """Length
        "Length of cable."
        "Value should be between 0 and 500."
        """
        val = self._get_property('Length')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @length.setter
    def length(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Length={value}'])

    @property
    def loss_per_length(self) -> float:
        """Loss Per Length
        "Cable loss per unit length (dB/meter)."
        "Value should be between 0 and 20."
        """
        val = self._get_property('Loss Per Length')
        return val

    @loss_per_length.setter
    def loss_per_length(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Loss Per Length={value}'])

    @property
    def measurement_length(self) -> float:
        """Measurement Length
        "Length of the cable used for the measurements."
        "Value should be between 0 and 500."
        """
        val = self._get_property('Measurement Length')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @measurement_length.setter
    def measurement_length(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Measurement Length={value}'])

    @property
    def resistive_loss_constant(self) -> float:
        """Resistive Loss Constant
        "Coaxial cable resistive loss constant."
        "Value should be between 0 and 2."
        """
        val = self._get_property('Resistive Loss Constant')
        return val

    @resistive_loss_constant.setter
    def resistive_loss_constant(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Resistive Loss Constant={value}'])

    @property
    def dielectric_loss_constant(self) -> float:
        """Dielectric Loss Constant
        "Coaxial cable dielectric loss constant."
        "Value should be between 0 and 1."
        """
        val = self._get_property('Dielectric Loss Constant')
        return val

    @dielectric_loss_constant.setter
    def dielectric_loss_constant(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,[f'Dielectric Loss Constant={value}'])

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

