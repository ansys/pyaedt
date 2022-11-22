import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.drill import Drill
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_instance import (
    PadstackInstance,
)
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.path import Path
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon


class Feature(object):
    def __init__(self, ipc):
        self._ipc = ipc
        self.feature_type = FeatureType().Polygon
        self.net = ""
        self.x = 0.0
        self.y = 0.0
        self.polygon = Polygon(self._ipc)
        self._cutouts = []
        self.path = Path(self._ipc)
        # self.pad = PadstackDef()
        self.padstack_instance = PadstackInstance()
        self.drill = Drill()
        # self.via = Via()

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
        net = ET.SubElement(layer_feature, "Set")
        net.set("net", self.net)
        if self.feature_type == FeatureType.Polygon:
            self.polygon.write_xml(net)
        elif self.feature_type == FeatureType.Path:
            self.path.write_xml(net)
        elif self.feature_type == FeatureType.PadstackInstance:
            self.padstack_instance.write_xml(net)


class FeatureType:
    (Polygon, Path, PadstackInstance, Drill) = range(0, 4)
