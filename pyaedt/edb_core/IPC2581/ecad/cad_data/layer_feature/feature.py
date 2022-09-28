import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.drill import Drill
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_def import PadstackDef
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_instance import PadstackInstance
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.path import Path
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon


class Feature(object):
    def __init__(self):
        self.feature_type = self.FeatureType().Polygon
        self.net = ""
        self.x = 0.0
        self.y = 0.0
        self.polygon = Polygon()
        self._cutouts = []
        self.path = Path()
        self.pad = PadstackDef()
        self.padstack_instance = PadstackInstance()
        self.drill = Drill()

    @property
    def cutouts(self):
        return self._cutouts

    @cutouts.setter
    def cutouts(self, value):
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, Polygon)]) == len(value):
                self._cutouts = value

    def add_cutout(self, cutout=None):
        if isinstance(cutout, Polygon):
            self._cutouts.append(cutout)

    def write_xml(self, layer_feature):
        if layer_feature:
            net = ET.SubElement("Set")
            net.set("net", self.net)
            feature = ET.SubElement(net, "Features")
            location = ET.SubElement(feature, "Location")
            location.set("x", self.x)
            location.set("y", self.y)
            if self.feature_type == self.FeatureType.Polygon:
                for polygon in self.polygon:
                    polygon.write_xml(feature)
            elif self.feature_type == self.FeatureType.Paths:
                for path in self.path:
                    path.write_xml(feature)

    class FeatureType:
        (Polygon, Paths, Padstack, Via, Drill) = range(0, 5)
