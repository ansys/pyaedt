from pyaedt.generic.general_methods import ET


class PadstackPadDef(object):
    """Class describing an IPC2581 padstack definition."""

    def __init__(self):
        self.layer_ref = ""
        self.pad_use = "REGULAR"
        self.x = 0.0
        self.y = 0.0
        self.primitive_ref = "CIRCLE_DEFAULT"

    def write_xml(self, padstack_def):  # pragma no cover
        pad_def = ET.SubElement(padstack_def, "PadstackPadDef")
        pad_def.set("layerRef", self.layer_ref)
        pad_def.set("padUse", self.pad_use)
        location = ET.SubElement(pad_def, "Location")
        location.set("x", str(self.x))
        location.set("y", str(self.y))
        standard_primitive = ET.SubElement(pad_def, "StandardPrimitiveRef")
        standard_primitive.set("id", self.primitive_ref)


class PadUse(object):
    (Regular, Antipad, Thermal) = range(0, 3)
