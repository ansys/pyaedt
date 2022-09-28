import xml.etree.cElementTree as ET


class LogicalNet(object):
    def __init__(self):
        self.name = ""
        self.pin_ref = []

    def write_xml(self, step):
        if step:
            logical_net = ET.SubElement(step, "LogicalNet")
            logical_net.set("name", self.name)
            for pin in self.pin_ref:
                pin.write_xml(logical_net)


class PinRef(object):
    def __init__(self):
        self.pin = ""
        self.component_ref = ""

    def write_xml(self, logical_net):
        if logical_net:
            pin_ref = ET.SubElement(logical_net, "PinRef")
            pin_ref.set("pin", self.pin)
            pin_ref.set("componentRef", self.component_ref)
