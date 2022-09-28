import math
import xml.etree.cElementTree as ET


class Polygon(object):
    def __init__(self):
        self.is_void = False
        self.poly_steps = []
        self.solid_fill_id = ""
        self.cutout = []

    def add_poly_step(self, poly_step=None):
        if not isinstance(poly_step, PolyStep):
            return False
        self.poly_steps.append(poly_step)

    def add_cutout(self, cutout):
        if not isinstance(cutout, Cutout):
            return False
        self.cutout.append(cutout)

    def write_xml(self, feature):
        if feature:
            contour = ET.SubElement(feature, "Contour")
            polygon = ET.SubElement(contour, "Polygon")
            polygon_begin = ET.SubElement(polygon, "PolyBegin")
            polygon_begin.set("x", self.polygon.poly_steps[0].x)
            polygon_begin.set("y", self.polygon.poly_steps[0].y)
            for poly_step in self.polygon.poly_steps[1:]:
                poly_step.write_xml(polygon)
            for cutout in self.cutout:
                cutout.write_xml(contour)


class Cutout(Polygon):
    def __init__(self):
        Polygon.__init__(self)

    def write_xml(self, contour):
        if contour:
            cutout = ET.SubElement(contour, "Cutout")
            cutout_begin = ET.SubElement(cutout, "PolyBegin")
            cutout_begin.set("x", self.poly_steps[0].x)
            cutout_begin.set("y", self.poly_steps[0].y)
            for poly_step in self.poly_steps[1:]:
                if poly_step.poly_type == 1:
                    poly = ET.SubElement(cutout, "PolyStepSegment")
                    poly.set("x", poly_step.x)
                    poly.set("y", poly_step.y)
                elif poly_step.poly_type == 2:
                    poly = ET.SubElement(cutout, "PolyStepCurve")
                    poly.set("x", poly_step.x)
                    poly.set("y", poly_step.y)
                    poly.set("centerX", poly_step.center_X)
                    poly.set("centerY", poly_step.center_y)
                    poly.set("clockwise", poly_step.clock_wise)


class PolyStep(object):
    def __init__(self):
        self.poly_type = PolyType().Segment
        self.x = 0.0
        self.y = 0.0
        self.center_X = 0.0
        self.center_y = 0.0
        self.clock_wise = False

    def write_xml(self, polygon):
        if polygon:
            if self.poly_type == 1:
                poly = ET.SubElement(polygon, "PolyStepSegment")
                poly.set("x", self.x)
                poly.set("y", self.y)
            elif self.poly_type == 2:
                poly = ET.SubElement(polygon, "PolyStepCurve")
                poly.set("x", self.x)
                poly.set("y", self.y)
                poly.set("centerX", self.center_X)
                poly.set("centerY", self.center_y)
                poly.set("clockwise", self.clock_wise)


class PolyType(object):
    (Segment, Curve) = range(0, 2)


class Curve(object):
    def __init__(self):
        self.center_X = 0.0
        self.center_y = 0.0
        self.clock_wise = False


class Arc(object):
    @staticmethod
    def get_arc_radius_angle(h, c):
        if not isinstance(h, float) and isinstance(c, float):
            return False
        r = h / 2 + math.pow(c, 2) / (8 * h)
        theta = 2 * math.asin(c / (2 * r))
        return r, theta
