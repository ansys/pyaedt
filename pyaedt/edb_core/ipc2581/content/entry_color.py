from pyaedt.edb_core.ipc2581.content.color import Color
from pyaedt.generic.general_methods import ET


class EntryColor(object):
    def __init__(self):
        self.name = ""
        self.color = Color()

    def write_xml(self, color=None):  # pragma no cover
        entry_color = ET.SubElement(color, "EntryColor")
        entry_color.set("id", self.name)
        self.color.write_xml(entry_color)
