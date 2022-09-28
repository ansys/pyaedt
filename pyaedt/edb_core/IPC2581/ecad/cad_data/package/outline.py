import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon


class Outline:
    def __init__(self):
        self.polygon = Polygon()
        self.line_ref = ""
        self.pickup_point = ["0.0", "0.0"]

    def write_xml(self, package):
        if package:
            outline = ET.SubElement(package)
            polygon = ET.SubElement(outline, "Polygon")
            polygon_begin = ET.SubElement(polygon, "PolyBegin")
            polygon_begin.set("x", self.polygon.poly_steps[0].x)
            polygon_begin.set("y", self.polygon.poly_steps[0].y)
            for poly_step in self.polygon.poly_steps[1:]:
                polygon_segment = ET.SubElement(polygon, "PolyStepSegment")
                polygon_segment.set("x", self.poly_step.x)
                polygon_segment.set("y", self.poly_step.y)
            line_desc_ref = ET.SubElement(outline, "LineDescRef")
            line_desc_ref.set("id", self.line_ref)
