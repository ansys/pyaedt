import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.content.entry_line import EntryLine


class Path(object):
    def __init__(self, ipc):
        self._ipc = ipc
        self.location_x = 0.0
        self.location_y = 0.0
        self.polysteps = []
        self.entry_line = EntryLine()
        self.width_ref_id = ""

    def add_path_step(self, path_step=None):
        if path_step:
            self.line_width = self._ipc.from_meter_to_units(path_step.primitive_object.GetWidth(), self._ipc.units)
            self.width_ref_id = "ROUND_{}".format(self.line_width)
            if not self.width_ref_id in self._ipc.content.dict_line.dict_lines:
                entry_line = EntryLine()
                entry_line.line_width = self.line_width
                self._ipc.content.dict_line.dict_lines[self.width_ref_id] = entry_line
            path_pt = PathStep()
            for pt in list(path_step.primitive_object.GetPolygonData().Points):
                path_pt.x = self._ipc.from_meter_to_units(pt.X.ToDouble(), self._ipc.units)
                path_pt.y = self._ipc.from_meter_to_units(pt.Y.ToDouble(), self._ipc.units)
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
