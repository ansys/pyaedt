from pyaedt.generic.general_methods import ET


class StackupLayer(object):
    def __init__(self):
        self.layer_name = ""
        self.thickness = 0
        self.tol_minus = 0
        self.tol_plus = 0
        self.sequence = ""
        self.spec_ref = "SPEC_{}".format(self.layer_name)

    def write_xml(self, stackup_group):  # pragma no cover
        stackup_layer = ET.SubElement(stackup_group, "StackupLayer")
        stackup_layer.set("layerOrGroupRef", self.layer_name)
        stackup_layer.set("thickness", str(self.thickness))
        stackup_layer.set("tolPlus", str(self.tol_plus))
        stackup_layer.set("tolMinus", str(self.tol_minus))
        stackup_layer.set("sequence", self.sequence)
        spec_ref = ET.SubElement(stackup_layer, "SpecRef")
        spec_ref.set("id", self.layer_name)
