import xml.etree.cElementTree as ET

class Color(object):
    def __init__(self):
        self._r = 0
        self._g = 0
        self._b = 0

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        if isinstance(value, int):
            self._r = value

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value):
        if isinstance(value, int):
            self._g = value

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        if isinstance(value, int):
            self._b = value

    def write_xml(self, entry_color=None):
        if isinstance(entry_color):
            color = ET.SubElement(entry_color, "Color")
            color.set("r", str(self.r))
            color.set("g", str(self.g))
            color.set("b", str(self.b))
