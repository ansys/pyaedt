import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import PolyStep


class Path(object):
    def __init__(self):
        self.location_x = 0.0
        self.location_y = 0.0
        self._polysteps = []
        self.line_width = ""
        self.width_ref_id = ""

    @property
    def polyline(self):
        return self._polyline

    @polyline.setter
    def polyline(self, value):
        if isinstance(value, list):
            if len([stp for stp in value if isinstance(stp, PolyStep)]) == len(value):
                self._polysteps = value

    def add_poly_step_to_polyline(self, poly_step=None):
        if isinstance(poly_step, PolyStep):
            self._polysteps.append(poly_step)

    def write_xml(self, feature):
        if feature:
            polyline = ET.SubElement(feature, "Polyline")
            polyline_begin = ET.SubElement(polyline, "PolyBegin")
            polyline_begin.set("x", self.path.polyline[0].x)
            polyline_begin.set("y", self.path.polyline[0].y)
            for poly_step in self.path.polyline[1:]:
                poly_step.write_xml()


class PathStep(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
