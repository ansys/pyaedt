from pyaedt.edb_core.ipc2581.ecad.spec import Spec
from pyaedt.generic.general_methods import ET


class CadHeader(object):
    """Class describing a layer stackup."""

    def __init__(self):
        self._specs = []
        self.units = ""

    @property
    def specs(self):
        return self._specs

    def add_spec(
        self, name="", material="", layer_type="", conductivity="", dielectric_constant="", loss_tg="", embedded=""
    ):  # pragma no cover
        spec = Spec()
        spec.name = name
        spec.material = material
        spec.conductivity = conductivity
        spec.dielectric_constant = dielectric_constant
        spec.layer_type = layer_type
        spec.loss_tangent = loss_tg
        spec.embedded = embedded
        self.specs.append(spec)

    def write_xml(self, ecad):  # pragma no cover
        cad_header = ET.SubElement(ecad, "CadHeader")
        cad_header.set("units", self.units)
        for spec in self.specs:
            spec.write_xml(cad_header)
