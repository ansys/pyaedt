from pyaedt.edb_core.ipc2581.ecad.cad_data.polygon import Polygon
from pyaedt.generic.general_methods import ET


class AssemblyDrawing(object):
    """Class describing an IPC2581 assembly drawing."""

    def __init__(self, ipc):
        self._ipc = ipc
        self.polygon = Polygon(self._ipc)
        self.line_ref = ""

    def write_xml(self, package):  # pragma no cover
        assembly_drawing = ET.SubElement(package, "AssemblyDrawing")
        outline = ET.SubElement(assembly_drawing, "Outline")
        polygon = ET.SubElement(outline, "Polygon")
        polygon_begin = ET.SubElement(polygon, "PolyBegin")
        if self.polygon.poly_steps:
            polygon_begin.set("x", str(self.polygon.poly_steps[0].x))
            polygon_begin.set("y", str(self.polygon.poly_steps[0].y))
            for poly_step in self.polygon.poly_steps[1:]:
                polygon_segment = ET.SubElement(polygon, "PolyStepSegment")
                polygon_segment.set("x", str(poly_step.x))
                polygon_segment.set("y", str(poly_step.y))
        line_desc_ref = ET.SubElement(outline, "LineDescRef")
        line_desc_ref.set("id", self.line_ref)
