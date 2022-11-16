import math
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
            self.features.append(feature)
        else:
            return False

    def add_component_padstack_instance_feature(self, component=None, top_bottom_layers=[]):
        if component:
            cmp_x = self._ipc.from_meter_to_units(component.center[0], self._ipc.units)
            cmp_y = self._ipc.from_meter_to_units(component.center[1], self._ipc.units)
            _cos = math.cos(component.rotation)
            _sin = math.sin(component.rotation)
            for _, pin in component.pins.items():
                is_via = False
                if not pin.start_layer == pin.stop_layer:
                    is_via = True
                pin_x = self._ipc.from_meter_to_units(pin.position[0], self._ipc.units)
                pin_y = self._ipc.from_meter_to_units(pin.position[1], self._ipc.units)
                pad_x = cmp_x + (pin_x * _cos - pin_y * _sin)
                pad_y = cmp_y + (pin_x * _sin + pin_y * _cos)
                cmp_rot_deg = component.rotation * 180 / math.pi
                mirror = False
                rotation = cmp_rot_deg + pin.rotation * 180 / math.pi
                if component.placement_layer == top_bottom_layers[-1]:
                    mirror = True
                    rotation = -cmp_rot_deg - pin.rotation * 180 / math.pi
                feature = Feature(self._ipc)
                feature.feature_type = FeatureType.Padstack
                feature.net = pin.net_name
                feature.padstack_instance.net = pin.net_name
                feature.padstack_instance.pin = pin.name
                feature.padstack_instance.x = pad_x
                feature.padstack_instance.y = pad_y
                feature.padstack_instance.rotation = rotation
                feature.padstack_instance.mirror = mirror
                feature.padstack_instance.isvia = is_via
                feature.padstack_instance.refdes = component.refdes
                feature.padstack_instance.standard_primimtive_ref = self._get_primitive_ref(
                    pin.padstack_definition, component.placement_layer
                )
                self.features.append(feature)

    def _get_primitive_ref(self, padstack_def=None, layer=None):
        if padstack_def and layer:
            for pad_def in self._ipc.ecad.cad_data.cad_data_step.padstack_defs[padstack_def].padstack_pad_def:
                if pad_def.layer_ref == layer:
                    return pad_def.primitive_ref
            return "default_value"

    def write_xml(self, step):
        if step:
            layer_feature = ET.SubElement(step, "LayerFeature")
            layer_feature.set("layerRef", self.layer_name)
            color_set = ET.SubElement(layer_feature, "Set")
            color_ref = ET.SubElement(color_set, "ColorRef")
            color_ref.set("id", self.color)
            for feature in self.features:
                feature.write_xml(layer_feature)
