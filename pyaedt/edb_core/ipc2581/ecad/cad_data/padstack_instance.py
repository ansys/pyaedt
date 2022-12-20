from pyaedt.generic.general_methods import ET


class PadstackInstance(object):
    """Class describing an IPC2581 padstack instance."""

    def __init__(self):
        self.isvia = False
        self.padstack_def = ""
        self.standard_primimtive_ref = ""
        self.pin = ""
        self.x = ""
        self.y = ""
        self.rotation = ""
        self.refdes = ""
        self.net = ""
        self.mirror = False

    def write_xml(self, net_root):  # pragma no cover
        if self.isvia:
            net_root.set("testPoint", "false")
            net_root.set("plate", "true")
            net_root.set("padUsage", "VIA")
            non_standard_attribute = ET.SubElement(net_root, "NonstandardAttribute")
            non_standard_attribute.set("name", "PADSTACK_USAGE")
            non_standard_attribute.set("value", "Through")
            non_standard_attribute.set("type", "STRING")
            pad = ET.SubElement(net_root, "Pad")
            pad.set("padstackDefRef", self.padstack_def)
            xform = ET.SubElement(pad, "Xform")
            xform.set("rotation", "0")
            xform.set("mirror", str(self.mirror).lower())
            location = ET.SubElement(pad, "Location")
            location.set("x", str(self.x))
            location.set("y", str(self.y))
            primitive_ref = ET.SubElement(pad, "StandardPrimitiveRef")
            primitive_ref.set("id", self.standard_primimtive_ref)
            if self.refdes:
                pin_ref = ET.SubElement(pad, "PinRef")
                pin_ref.set("pin", self.pin)
                pin_ref.set("componentRef", self.refdes)
        else:
            net_root.set("testPoint", "false")
            net_root.set("plate", "true")
            non_standard_attribute = ET.SubElement(net_root, "NonstandardAttribute")
            non_standard_attribute.set("name", "PADSTACK_USAGE")
            non_standard_attribute.set("value", "Through")
            non_standard_attribute.set("type", "STRING")
            pad = ET.SubElement(net_root, "Pad")
            pad.set("padstackDefRef", self.padstack_def)
            xform = ET.SubElement(pad, "Xform")
            xform.set("rotation", str(self.rotation))
            xform.set("mirror", str(self.mirror).lower())
            location = ET.SubElement(pad, "Location")
            location.set("x", str(self.x))
            location.set("y", str(self.y))
            primitive_ref = ET.SubElement(pad, "StandardPrimitiveRef")
            primitive_ref.set("id", self.standard_primimtive_ref)
            if self.refdes:
                pin_ref = ET.SubElement(pad, "PinRef")
                pin_ref.set("pin", self.pin)
                pin_ref.set("componentRef", self.refdes)
