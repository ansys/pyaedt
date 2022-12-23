from pyaedt.edb_core.ipc2581.content.content import Content
from pyaedt.generic.general_methods import ET


class FillDesc(Content):
    def __init__(self):
        self.id = ""
        self.fill_property = ""

    def write_xml(self, dict_fill=None):  # pragma no cover
        if dict_fill:
            fill = ET.SubElement(dict_fill, "EntryFillDesc")
            fill.set("id", self.id)
            fill_desc = ET.SubElement(fill, "FillDesc")
            fill_desc.set("fillProperty", self.fill_property)
