import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.package.assembly_drawing import (
    AssemblyDrawing,
)
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.outline import Outline
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.pin import Pin
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import PolyStep


class Package(object):
    """Class describing IPC2581 package definition."""

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
        self.pickup_point = [0.0, 0.0]

    @property
    def pins(self):  # pragma no cover
        return self._pins

    @pins.setter
    def pins(self, value):
        if isinstance(value, list):
            if len([pin for pin in value if isinstance(pin, Pin)]) == len(value):
                self._pins = value

    def add_pin(self, number=0, x=0.0, y=0.0, primitive_ref=""):  # pragma no cover
        added_pin = Pin()
        added_pin.x = x
        added_pin.y = y
        added_pin.number = number
        added_pin.primitive_def = primitive_ref
        self.pins.append(added_pin)

    def add_component_outline(self, component):
        if component:
            _bbox = component.bounding_box
            component_bounding_box = [
                self._ipc.from_meter_to_units(_bbox[0], self._ipc.units),
                self._ipc.from_meter_to_units(_bbox[1], self._ipc.units),
                self._ipc.from_meter_to_units(_bbox[2], self._ipc.units),
                self._ipc.from_meter_to_units(_bbox[3], self._ipc.units),
            ]
            poly_step1 = PolyStep()
            poly_step2 = PolyStep()
            poly_step3 = PolyStep()
            poly_step4 = PolyStep()
            poly_step1.x = component_bounding_box[0]
            poly_step1.y = component_bounding_box[1]
            poly_step2.x = component_bounding_box[2]
            poly_step2.y = component_bounding_box[1]
            poly_step3.x = component_bounding_box[2]
            poly_step3.y = component_bounding_box[3]
            poly_step4.x = component_bounding_box[0]
            poly_step4.y = component_bounding_box[3]
            self.outline.polygon.poly_steps = [poly_step1, poly_step2, poly_step3, poly_step4]
            try:
                self._ipc.content.dict_line["ROUND_0"] = 0.0
            except:
                pass
            self.outline.line_ref = "ROUND_0"

    def write_xml(self, step):  # pragma no cover
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
