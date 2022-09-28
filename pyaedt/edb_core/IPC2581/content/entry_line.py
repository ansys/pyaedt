import xml.etree.cElementTree as ET


class EntryLine(object):
    def __init__(self):
        self._line_end = "ROUND"
        self.line_width = ""

    def write_xml(self, dictionnary_line):
        if dictionnary_line:
            entry_line = ET.SubElement(dictionnary_line, "EntryLineDesc")
            entry_line.set("id", "{}_{}".format(self._line_end, self.line_width))
            line_desc = ET.SubElement(entry_line, "LineDesc")
            line_desc.set("lineEnd", self._line_end)
            line_desc.set("lineWidth", self.line_width)
