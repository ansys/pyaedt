import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.cad_data import CadData
from pyaedt.edb_core.IPC2581.ecad.cad_header.cad_header import CadHeader


class Ecad(object):
    def __init__(self, ipc, edb):
        self.design_name = "Design"
        self.cad_header = CadHeader()
        self.cad_data = CadData(self, edb)
        self._ipc = ipc
        self._pedb = edb

    def write_xml(self, root):
        if root:
            ecad = ET.SubElement(root, "Ecad")
            ecad.set("name", self.design_name)
            cad_header = ET.SubElement(ecad, CadHeader)
            cad_header.set("units", self._ipc.units)
            self.cad_header.write_xml(ecad)
            self.cad_data.write_xml(ecad)
