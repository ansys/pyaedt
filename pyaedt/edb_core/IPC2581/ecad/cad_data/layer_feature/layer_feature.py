import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.layer_feature.feature import Feature
from pyaedt.edb_core.IPC2581.ecad.cad_data.layer_feature.feature import FeatureType


class LayerFeature(object):
    def __init__(self, ipc):
        self._ipc = ipc
        self.layer_name = ""
        self.color = ""
        self._features = []

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        if isinstance(value, list):
            if len([feat for feat in value if isinstance(feat, Feature)]) == len(value):
                self._features = value

    def add_feature(self, obj_instance=None):
        if obj_instance:
            feature = Feature(self._ipc)
            feature.net = obj_instance.net_name
            if obj_instance.type == "Polygon":
                feature.feature_type = FeatureType.Polygon
                feature.polygon.add_poly_step(obj_instance)
            elif obj_instance.type == "Path":
                feature.feature_type = FeatureType.Path
                feature.path.add_path_step(obj_instance)
            self._features.append(feature)
        else:
            return False

    def write_xml(self, step):
        if step:
            layer_feature = ET.SubElement(step, "LayerFeature")
            layer_feature.set("layerRef", self.layer_name)
            color_set = ET.SubElement(layer_feature, "Set")
            color_ref = ET.SubElement(color_set, "ColorRef")
            color_ref.set("id", self.color)
            for feature in self.features:
                feature.write_xml(layer_feature)
