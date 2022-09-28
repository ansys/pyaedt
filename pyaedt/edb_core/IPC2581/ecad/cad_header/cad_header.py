import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_header.spec import Spec


class CadHeader(object):
    """Class describing layer stackup."""
    def __init__(self):
        self.specs = []
        self.units = ""

    @property
    def specs(self):
        return self.units

    @specs.setter
    def specs(self, value):
        if isinstance(value, list):
            if len([spec for spec in value if isinstance(spec, Spec)]) == len(value):
                self._specs = value

    def add_spec(self, spec=None):
        if isinstance(spec, Spec):
            self._specs.append(spec)

    def write_xml(self, ecad):
        if ecad:
            cad_header = ET.SubElement(ecad, "CadHeader")
            cad_header.set("units", self.units)
            for spec in self.specs:
                spec.write_xml(cad_header)
