import xml.etree.cElementTree as ET


class LayerRef(object):
    def __init__(self):
        self.name = ""

    def write_xml(self, content=None):
        if content:
            layer_ref = ET.SubElement(content, "LayerRef")
            layer_ref.set("name", self.name)
