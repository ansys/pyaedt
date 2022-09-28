import xml.etree.cElementTree as ET


class RefDes(object):
    def __init__(self):
        self.name = ""
        self.packaged_def = ""
        self.populate = "True"
        self.placement_layer = ""

    def write_xml(self, bom_item):
        if bom_item:
            refdes = ET.SubElement(bom_item, "RefDes")
            refdes.set("name", self.name)
            refdes.set("packageRef", self.packaged_def)
            refdes.set("populate", self.populate)
            refdes.set("layerRef", self.placement_layer)


