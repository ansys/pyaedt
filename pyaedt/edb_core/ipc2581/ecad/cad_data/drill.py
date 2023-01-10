from pyaedt.generic.general_methods import ET


class Drill(object):
    """Class describing an ICP2581 drill feature."""

    def __init__(self):
        self.net = ""
        self.component = ""
        self.geometry = "VIA"
        self.hole_name = ""
        self.diameter = ""
        self.plating_status = "VIA"
        self.plus_tol = "0.0"
        self.min_tol = "0.0"
        self.x = "0.0"
        self.y = "0.0"

    def write_xml(self, net):  # pragma no cover
        net.set("geometry", "VIA")
        color_ref = ET.SubElement(net, "ColorRef")
        color_ref.set("id", "")
        hole = ET.SubElement(net, "Hole")
        hole.set("name", self.hole_name)
        hole.set("diameter", str(self.diameter))
        hole.set("platingStatus", "VIA")
        hole.set("plusTol", str(self.plus_tol))
        hole.set("minusTol", str(self.min_tol))
        hole.set("x", str(self.x))
        hole.set("y", str(self.y))
