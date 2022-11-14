import xml.etree.cElementTree as ET


class Path(object):
    def __init__(self):
        self.location_x = 0.0
        self.location_y = 0.0
        self.polysteps = []
        self.line_width = ""
        self.width_ref_id = ""

    def add_path_step(self, path_step=None):
        if path_step:
            self.line_width = path_step.primitive_object.GetWidth()  # Add unit converter

            path_pt = PathStep()
            for pt in list(path_step.primitive_object.GetPolygonData().Points):
                path_pt.x = pt.X.ToDouble()  # add unit converter
                path_pt.y = pt.Y.ToDouble()  # add unit converter
                self.polysteps.append(path_pt)

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
