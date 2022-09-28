import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.content.content import Content


class FillDesc(Content):
    def __init__(self):
        self.id = ""
        self.fill_property = ""

    def write_xml(self, dict_fill=None):
        if dict_fill:
            fill = ET.SubElement(dict_fill, "EntryFillDesc")
            fill.set("id", self.id)
            fill_desc = ET.SubElement(fill, "FillDesc")
            fill_desc.set("fillProperty", self.fill_property)
