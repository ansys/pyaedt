import xml.etree.cElementTree as ET


class PadstackHoleDef(object):
    def __init__(self):
        self.name = ""
        self.diameter = 0.0
        self.plating_status = PlatingStatus().PLATED
        self.plus_tol = 0.0
        self.minus_tol = 0.0
        self.x = 0.0
        self.y = 0.0

    def write_xml(self, padstackdef):
        if padstackdef:
            padstack_hole = ET.SubElement(padstackdef, "PadstackHoleDef")
            padstack_hole.set("name", self.name)
            padstack_hole.set("diameter", self.diameter)
            padstack_hole.set("platingStatus", self.plating_status)
            padstack_hole.set("plusTol", self.plus_tol)
            padstack_hole.set("minusTol", self.minus_tol)
            padstack_hole.set("x", self.x)
            padstack_hole.set("y", self.y)


class PlatingStatus(object):
    (PLATED) = range(1)
