import xml.etree.cElementTree as ET


class Pin(object):
    def __init__(self):
        self.number = ""
        self.electrical_type = "ELECTRICAL"
        self.x = 0.0
        self.y = 0.0
        self.rotation = 0.0
        self.primitive_def = ""
        self.is_via = False

    def write_xml(self, package):
        pin = ET.SubElement("Pin")
        pin.set("number", self.number)
        pin.set("type", "THRU")
        pin.set("electricalType", self.electrical_type)


class Type(object):
    (Thru, Surface) = range(0, 2)
