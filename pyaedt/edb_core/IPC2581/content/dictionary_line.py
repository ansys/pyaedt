import xml.etree.cElementTree as ET
from pyaedt.edb_core.IPC2581.content.entry_line import EntryLine


class DictionaryLine(object):
    def __init__(self, content):
        self._dict_lines = []
        self.unit = content.units

    @property
    def dict_lines(self):
        return self._dict_lines

    @dict_lines.setter
    def dict_lines(self, value):
        if isinstance(value, EntryLine):
            self._dict_lines = value

    def add_line(self, width=None):
        if width:
            line = EntryLine()
            line._line_width = width
            self._dict_lines.append(line)

    def write_xml(self, content=None):
        if content:
            dict_line = ET.SubElement(content, "DictionaryLineDesc")
            dict_line.set("units", self.units)
            for line in self._dict_lines:
                line.write_xml()
