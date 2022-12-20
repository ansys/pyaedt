from pyaedt.edb_core.ipc2581.content.content import Content
from pyaedt.edb_core.ipc2581.content.fill import FillDesc
from pyaedt.generic.general_methods import ET


class DictionaryFill(Content):
    def __init__(self):
        self._dict_fill = {}

    @property
    def dict_fill(self):
        return self._dict_fill

    @dict_fill.setter
    def dict_fill(self, value):  # pragma no cover
        if isinstance(value, list):
            self._dict_fill = value

    def add_fill(self, value):  # pragma no cover
        if isinstance(value, FillDesc):
            self._dict_fill.append(value)

    def write_xml(self, content=None):  # pragma no cover
        if content:
            dict_fill = ET.SubElement(content, "DictionaryFillDesc")
            dict_fill.set("units", self.units)
            for fill in self._dict_fill.keys():
                self._dict_fill[fill].write_xml()
