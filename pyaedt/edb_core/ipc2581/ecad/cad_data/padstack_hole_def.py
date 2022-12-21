from pyaedt.generic.general_methods import ET


class PadstackHoleDef(object):
    """Class describing an ICP2581 padstack hole definition."""

    def __init__(self):
        self.name = ""
        self.diameter = 0
        self.plating_status = "PLATED"
        self.plus_tol = 0
        self.minus_tol = 0
        self.x = 0
        self.y = 0

    def write_xml(self, padstackdef):  # pragma no cover
        padstack_hole = ET.SubElement(padstackdef, "PadstackHoleDef")
        padstack_hole.set("name", self.name)
        padstack_hole.set("diameter", str(self.diameter))
        padstack_hole.set("platingStatus", str(self.plating_status))
        padstack_hole.set("plusTol", str(self.plus_tol))
        padstack_hole.set("minusTol", str(self.minus_tol))
        padstack_hole.set("x", str(self.x))
        padstack_hole.set("y", str(self.y))
