from pyaedt.generic.general_methods import ET


class Pin(object):
    """Class describing an ICP2581 component pin."""

    def __init__(self):
        self.number = ""
        self.electrical_type = "ELECTRICAL"
        self.x = 0.0
        self.y = 0.0
        self.rotation = 0.0
        self.primitive_def = ""
        self.is_via = False

    def write_xml(self, package):  # pragma no cover
        pin = ET.SubElement(package, "Pin")
        pin.set("number", str(self.number))
        pin.set("type", "THRU")
        pin.set("electricalType", self.electrical_type)
        xform = ET.SubElement(pin, "Xform")
        xform.set("rotation", str(self.rotation))
        location = ET.SubElement(pin, "Location")
        location.set("x", str(self.x))
        location.set("y", str(self.y))
        primitive_ref = ET.SubElement(pin, "StandardPrimitiveRef")
        primitive_ref.set("id", self.primitive_def)


class Type(object):
    (Thru, Surface) = range(0, 2)
