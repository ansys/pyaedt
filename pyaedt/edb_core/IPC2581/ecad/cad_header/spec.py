import xml.etree.cElementTree as ET


class Spec(object):
    """Class describing layer."""

    def __init__(self):
        self.name = ""
        self.material = ""
        self.layer_type = ""
        self.conductivity = ""
        self.dielectric_constant = ""
        self.loss_tangent = ""
        self.embedded = ""

    def write_xml(self, ecad_header):
        if ecad_header:
            spec = ET.SubElement(ecad_header, "Spec")
            spec.set("name", self.name)
            material = ET.SubElement(spec, "General")
            material.set("type", "MATERIAL")
            material_set = ET.SubElement(material, "Property")
            material_set.set("text", self.material)
            layer_type = ET.SubElement(spec, "General")
            layer_type.set("type", "OTHER")
            layer_type.set("comment", "LAYER_TYPE")
            layer_type_set = ET.SubElement(layer_type, "Property")
            layer_type_set.set("text", self.layer_type)
            conductivity = ET.SubElement(spec, "Conductor")
            conductivity.set("type", "CONDUCTIVITY")
            conductivity_set = ET.SubElement(conductivity, "General")
            conductivity_set.set("value", self.conductivity)
            conductivity_set.set("unit", "MHO/CM")
            dielectric = ET.SubElement(spec, "Dielectric")
            dielectric.set("type", "DIELECTRIC_CONSTANT")
            dielectric_set = ET.SubElement(dielectric, "Property")
            dielectric_set.set("value", self.dielectric_constant)
            loss_tg = ET.SubElement(spec, "Dielectric")
            loss_tg.set("type", "LOSS_TANGENT")
            loss_tg_set = ET.SubElement(loss_tg, "Property")
            loss_tg_set.set("value", self.loss_tangent)
            embedded = ET.SubElement(spec, "General")
            embedded.set("type", "OTHER")
            embedded.set("comment", "LAYER_EMBEDDED_STATUS")
            embedded_set = ET.SubElement(embedded, "Property")
            embedded_set.set("text", self.embedded)
