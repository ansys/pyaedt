import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_header.spec import Spec


class CadHeader(object):
    """Class describing layer stackup."""

    def __init__(self):
        self.specs = []
        self.units = ""

    @property
    def specs(self):
        return self.specs

    @specs.setter
    def specs(self, value):
        if isinstance(value, list):
            if len([spec for spec in value if isinstance(spec, Spec)]) == len(value):
                self._specs = value

    def add_spec(
        self, name="", material="", layer_type="", conductivity="", dielectric_constant="", loss_tg="", embedded=""
    ):
        spec = Spec()
        spec.name = name
        spec.material = material
        spec.conductivity = conductivity
        spec.dielectric_constant = dielectric_constant
        spec.layer_type = layer_type
        spec.loss_tangent = loss_tg
        spec.embedded = embedded
        self._specs.append(spec)

    def write_xml(self, ecad):
        if ecad:
            cad_header = ET.SubElement(ecad, "CadHeader")
            cad_header.set("units", self.units)
            for spec in self.specs:
                spec.write_xml(cad_header)
