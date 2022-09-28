from pyaedt.edb_core.IPC2581.content.color import Color
import xml.etree.cElementTree as ET

class EntryColor(object):
    def __init__(self):
        self.name = ""
        self.color = Color()

    def write_xml(self, color=None):
        if color:
            entry_color = ET.SubElement(color, "EntryColor")
            entry_color.set("id", self.name)
            self.color.write_xml(entry_color)