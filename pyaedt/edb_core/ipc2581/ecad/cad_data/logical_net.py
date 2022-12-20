from pyaedt.generic.general_methods import ET


class LogicalNet(object):
    """Class describing an IPC2581 logical net."""

    def __init__(self):
        self.name = ""
        self.pin_ref = []

    def write_xml(self, step):  # pragma no cover
        if step:
            logical_net = ET.SubElement(step, "LogicalNet")
            logical_net.set("name", self.name)
            for pin in self.pin_ref:
                pin.write_xml(logical_net)

    def get_pin_ref_def(self):  # pragma no cover
        return PinRef()


class PinRef(object):
    """Class describing an IPC2581 logical net."""

    def __init__(self):
        self.pin = ""
        self.component_ref = ""

    def write_xml(self, logical_net):  # pragma no cover
        pin_ref = ET.SubElement(logical_net, "PinRef")
        pin_ref.set("pin", self.pin)
        pin_ref.set("componentRef", self.component_ref)
