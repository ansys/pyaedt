from ..EmitNode import *

class ReadOnlyCable(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property('Filename')
        return val

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property('Noise Temperature')
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

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
        val = self.TypeOption[val]
        return val

    @property
    def length(self) -> float:
        """Length
        "Length of cable."
        "Units options: pm, nm, um, mm, cm, dm, meter, meters, km, mil, in, ft, yd."
        "Value should be between 0 and 500."
        """
        val = self._get_property('Length')
        val = self._convert_from_default_units(float(val), "Length Unit")
        return val

    @property
    def loss_per_length(self) -> float:
        """Loss Per Length
        "Cable loss per unit length (dB/meter)."
        "Value should be between 0 and 20."
        """
        val = self._get_property('Loss Per Length')
        return val

    @property
    def measurement_length(self) -> float:
        """Measurement Length
        "Length of the cable used for the measurements."
        "Units options: pm, nm, um, mm, cm, dm, meter, meters, km, mil, in, ft, yd."
        "Value should be between 0 and 500."
        """
        val = self._get_property('Measurement Length')
        val = self._convert_from_default_units(float(val), "Length Unit")
        return val

    @property
    def resistive_loss_constant(self) -> float:
        """Resistive Loss Constant
        "Coaxial cable resistive loss constant."
        "Value should be between 0 and 2."
        """
        val = self._get_property('Resistive Loss Constant')
        return val

    @property
    def dielectric_loss_constant(self) -> float:
        """Dielectric Loss Constant
        "Coaxial cable dielectric loss constant."
        "Value should be between 0 and 1."
        """
        val = self._get_property('Dielectric Loss Constant')
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property('Warnings')
        return val

