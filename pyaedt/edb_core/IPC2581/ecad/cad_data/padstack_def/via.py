class Via(object):
    def __init__(self):
        self.name = ""
        self.net = ""
        self.hole_name = ""
        self.diameter = ""
        self.x = ""
        self.y = ""

    #
    # def write_xml(self, via):
    #     if via:
    #         via = ET.SubElement(padstack_def, "PadstackPadDef")
    #         pad_def.set("layerRef", self.layer_ref)
    #         pad_def.set("padUse", self.pad_use)
    #         location = ET.SubElement(pad_def, "Location")
    #         location.set("x", self.x)
    #         location.set("y", self.y)
    #         standard_primitive = ET.SubElement(pad_def, "StandardPrimitiveRef")
    #         standard_primitive.set("id", self.primitive_ref)
