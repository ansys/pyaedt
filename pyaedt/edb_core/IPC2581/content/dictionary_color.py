import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.content.entry_color import EntryColor


class DictionaryColor(object):
    def __init__(self):
        self._dict_colors = []

    @property
    def dict_colors(self):
        return self._dict_colors

    @dict_colors.setter
    def dict_colors(self, value):
        if isinstance(value, list):
            self._dict_colors = value

    def add_color(self, name="", r=1, g=1, b=1):
        entry_color = EntryColor()
        entry_color.name = name
        entry_color.color.r = r
        entry_color.color.g = g
        entry_color.color.b = b
        self._dict_colors.append(entry_color)

    def write_xml(self, content=None):
        if content:
            dict_color = ET.SubElement(content, "DictionaryColor")
            for _color in self.dict_colors:
                _color.write_xml(dict_color)
