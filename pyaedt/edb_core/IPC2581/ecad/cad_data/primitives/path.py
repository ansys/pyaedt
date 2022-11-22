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

    def add_path_step(self, feature=None, path_step=None):
        self.line_width = self._ipc.from_meter_to_units(path_step.primitive_object.GetWidth(), self._ipc.units)
        self.width_ref_id = "ROUND_{}".format(self.line_width)
        if not self.width_ref_id in self._ipc.content.dict_line.dict_lines:
            entry_line = EntryLine()
            entry_line.line_width = self.line_width
            self._ipc.content.dict_line.dict_lines[self.width_ref_id] = entry_line
        path_pt = PathStep()
        for pt in list(path_step.primitive_object.GetPolygonData().Points):
            path_pt.x = str(self._ipc.from_meter_to_units(pt.X.ToDouble(), self._ipc.units))
            path_pt.y = str(self._ipc.from_meter_to_units(pt.Y.ToDouble(), self._ipc.units))
            feature.path.polysteps.append(path_pt)

    def write_xml(self, net_root):
        feature = ET.SubElement(net_root, "Features")
        polyline = ET.SubElement(feature, "Polyline")
        polyline_begin = ET.SubElement(polyline, "PolyBegin")
        polyline_begin.set("x", str(self._ipc.from_meter_to_units(self.polysteps[0].x, self._ipc.units)))
        polyline_begin.set("y", str(self._ipc.from_meter_to_units(self.polysteps[0].y, self._ipc.units)))
        for poly_step in self.polysteps[1:]:
            poly_step_segment = ET.SubElement(polyline, "PolyStepSegment")
            poly_step_segment.set("x", str(self._ipc.from_meter_to_units(poly_step.x, self._ipc.units)))
            poly_step_segment.set("y", str(self._ipc.from_meter_to_units(poly_step.y, self._ipc.units)))
        line_disc_ref = ET.SubElement(polyline, "LineDescRef")
        line_disc_ref.set("id", self.width_ref_id)


class PathStep(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
