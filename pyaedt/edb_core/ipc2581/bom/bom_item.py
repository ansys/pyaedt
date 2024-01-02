from pyaedt.edb_core.ipc2581.bom.characteristics import Characteristics
from pyaedt.edb_core.ipc2581.bom.refdes import RefDes
from pyaedt.generic.general_methods import ET


class BomItem(object):
    def __init__(self):
        self.part_name = ""
        self.quantity = "1"
        self.pin_count = "1"
        self.category = "ELECTRICAL"
        self.refdes_list = []
        self.charactistics = Characteristics()

    def write_xml(self, bom):  # pragma no cover
        bom_item = ET.SubElement(bom, "BomItem")
        bom_item.set("OEMDesignNumberRef", self.part_name)
        bom_item.set("quantity", str(self.quantity))
        bom_item.set("pinCount", str(self.pin_count))
        bom_item.set("category", self.category)
        bom_item.set("category", self.category)
        for refdes in self.refdes_list:
            refdes.write_xml(bom_item)
        self.charactistics.write_xml(bom_item)

    def add_refdes(self, component_name=None, package_def=None, populate=True, placement_layer=""):  # pragma no cover
        refdes = RefDes()
        refdes.name = component_name
        refdes.populate = str(populate)
        refdes.packaged_def = package_def
        refdes.placement_layer = placement_layer
        self.refdes_list.append(refdes)
