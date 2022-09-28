import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.BOM.characteristics import Characteristics
from pyaedt.edb_core.IPC2581.BOM.refdes import RefDes


class BomItem(object):
    def __init__(self):
        self.part_name = ""
        self.quantity = "1"
        self.pin_count = "1"
        self.category = "ELECTRICAL"
        self.refdes_list = []
        self.charactistics = Characteristics()

    def write_xml(self, bom):
        if bom:
            bom_item = ET.SubElement(bom, "BomItem")
            bom_item.set("OEMDesignNumberRef", self.part_name)
            bom_item.set("quantity", self.quantity)
            bom_item.set("pinCount", self.pin_count)
            bom_item.set("category", self.category)
            bom_item.set("category", self.category)
            for refdes in self.refdes_list:
                refdes.write_xml(bom)
            self.charactistics.write_xml(bom)

    def add_refdes(self, component_name=None, package_def=None, populate=True, placement_layer=""):
            refdes = RefDes()
            refdes.name = component_name
            refdes.populate = populate
            refdes.packaged_def = package_def
            refdes.placement_layer = placement_layer
            self.refdes_list.append(refdes)
