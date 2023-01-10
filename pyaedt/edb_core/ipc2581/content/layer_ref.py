from pyaedt.generic.general_methods import ET


class LayerRef(object):
    def __init__(self):
        self.name = ""

    def write_xml(self, content=None):  # pragma no cover
        layer_ref = ET.SubElement(content, "LayerRef")
        layer_ref.set("name", self.name)
