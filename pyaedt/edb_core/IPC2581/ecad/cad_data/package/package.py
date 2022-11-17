import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.package.assembly_drawing import (
    AssemblyDrawing,
)
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.outline import Outline
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.pin import Pin


class Package(object):
    def __init__(self, ipc):
        self._ipc = ipc
        self.name = ""
        self.type = "OTHER"
        self.pin_one = "1"
        self.pin_orientation = "OTHER"
        self.height = 0.1
        self.assembly_drawing = AssemblyDrawing(self._ipc)
        self.outline = Outline(self._ipc)
        self._pins = []

    @property
    def pins(self):
        return self._pins

    @pins.setter
    def pins(self, value):
        if isinstance(value, list):
            if len([pin for pin in value if isinstance(pin, Pin)]) == len(value):
                self._pins = value

    def add_pin(self, number=0, x=0.0, y=0.0, primitive_ref=""):
        added_pin = Pin()
        added_pin.x = x
        added_pin.y = y
        added_pin.number = number
        added_pin.primitive_def = primitive_ref
        self.pins.append(added_pin)

    def write_xml(self, step):
        package = ET.SubElement(step, "Package")
        package.set("name", self.name)
        package.set("type", self.type)
        package.set("pinOne", self.pin_one)
        package.set("pinOneOrientation", self.pin_orientation)
        package.set("height", self.height)
        self.outline.write_xml(package)
        self.assembly_drawing.write_xml(step)
        for pin in self.pins:
            pin.write_xml(package)
