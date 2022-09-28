import xml.etree.cElementTree as ET


class Component(object):
    def __init__(self):
        self.refdes = ""
        self.package_ref = ""
        self.layer_ref = ""
        self.part = ""
        self.mount_type = "SMT"
        self.stand_off = "0.0"
        self.height = "0.0"
        self.location = ["0.0", "0.0"]
        self.rotation = "0.0"
        self.type = Type().Rlc
        self.value = ""

    def write_xml(self, step):
        if step:
            component = ET.SubElement(step, "Component")
            component.set("refDes", self.refdes)
            component.set("packageRef", self.package_ref)
            component.set("layerRef", self.layer_ref)
            component.set("part", self.package_ref)
            component.set("mountType", self.mount_type)
            component.set("standoff", self.stand_off)
            component.set("height", self.height)
            non_standard_attribute = ET.SubElement(component, "NonstandardAttribute")
            non_standard_attribute.set("name", "VALUE")
            non_standard_attribute.set("value", self.value)
            non_standard_attribute.set("type", "STRING")
            xform = ET.SubElement(component, "Xform")
            xform.set("rotation", self.rotation)
            location = ET.SubElement(component, "Location")
            location.set("x", self.location[0])
            location.set("y", self.location[1])


class Type(object):
    (Rlc, Discrete) = range(0, 2)
