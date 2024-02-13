from pyaedt.generic.general_methods import ET


class Bom(object):
    def __init__(self, edb):
        self._edb = edb
        self.name = self._edb.cell_names[0]
        self.revision = "1.0"
        self.step_ref = "1.0"
        self.bom_items = []

    def write_xml(self, root):  # pragma no cover
        bom = ET.SubElement(root, "Bom")
        bom.set("name", self.name)
        bom_header = ET.SubElement(bom, "BomHeader")
        bom_header.set("assembly", self.name)
        bom_header.set("revision", self.revision)
        step_ref = ET.SubElement(bom_header, "StepRef")
        step_ref.set("name", self.name)
        for bom_item in self.bom_items:
            bom_item.write_xml(bom)
