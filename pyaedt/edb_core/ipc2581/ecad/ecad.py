from pyaedt.edb_core.ipc2581.ecad.cad_data.cad_data import CadData
from pyaedt.edb_core.ipc2581.ecad.cad_header import CadHeader
from pyaedt.generic.general_methods import ET


class Ecad(object):
    def __init__(self, ipc, edb, units):
        self.design_name = "Design"
        self.units = units
        self.cad_header = CadHeader()
        self._ipc = ipc
        self.cad_data = CadData(self, edb, units, self._ipc)
        self._pedb = edb

    def write_xml(self, root):  # pragma no cover
        ecad = ET.SubElement(root, "Ecad")
        ecad.set("name", self.design_name)
        self.cad_header.write_xml(ecad)
        self.cad_data.write_xml(ecad)
