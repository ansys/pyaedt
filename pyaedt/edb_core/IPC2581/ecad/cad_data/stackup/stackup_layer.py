import xml.etree.cElementTree as ET


class StackupLayer(object):
    def __init__(self):
        self.layer_name = ""
        self.thickness = 0.0
        self.tol_minus = 0.0
        self.tol_plus = 0.0
        self.sequence = ""
        self.spec_ref = ""

    def write_xml(self, stackup_group):
        if stackup_group:
            stackup_layer = ET.SubElement(stackup_group, "StackupLayer")
            stackup_layer.set("layerOrGroupRef", self.layer_name)
            stackup_layer.set("thickness", self.thickness)
            stackup_layer.set("tolPlus", self.tol_plus)
            stackup_layer.set("tolMinus", self.tol_minus)
            stackup_layer.set("tolMinus", self.sequence)
            spec_ref = ET.SubElement(stackup_layer, "SpecRef")
            spec_ref.set("id", self.spec_ref)
