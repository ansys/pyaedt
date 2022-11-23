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
        self.is_drill_feature = False

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
                feature.path.add_path_step(feature, obj_instance)
            self.features.append(feature)
        else:
            return False

    def add_via_instance_feature(self, padstack_inst=None, padstackdef=None):
        if padstack_inst and padstackdef:
            feature = Feature(self._ipc)
            feature.padstack_instance.net = padstack_inst.net_name
            feature.padstack_instance.isvia = True
            feature.feature_type = FeatureType.PadstackInstance
            feature.padstack_instance.x = self._ipc.from_meter_to_units(padstack_inst.position[0], self._ipc.units)
            feature.padstack_instance.y = self._ipc.from_meter_to_units(padstack_inst.position[1], self._ipc.units)
            feature.padstack_instance.diameter = padstackdef.hole_finished_size
            feature.padstack_instance.hole_name = padstack_inst.padstack_definition
            feature.padstack_instance.name = padstack_inst.name
            self.features.append(feature)

    def add_drill_feature(self, via, diameter=0.0):
        feature = Feature(self._ipc)
        feature.feature_type = FeatureType.Drill
        feature.drill.net = via.net_name
        feature.drill.x = self._ipc.from_meter_to_units(via.position[0], self._ipc.units)
        feature.drill.y = self._ipc.from_meter_to_units(via.position[1], self._ipc.units)
        feature.drill.diameter = self._ipc.from_meter_to_units(diameter, self._ipc.units)
        self.features.append(feature)

    def add_component_padstack_instance_feature(self, component=None, pin=None, top_bottom_layers=[]):
        if component:
            cmp_x = self._ipc.from_meter_to_units(component.center[0], self._ipc.units)
            cmp_y = self._ipc.from_meter_to_units(component.center[1], self._ipc.units)
            _cos = math.cos(component.rotation)
            _sin = math.sin(component.rotation)
            if pin:
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
                feature.feature_type = FeatureType.PadstackInstance
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
        layer_feature = ET.SubElement(step, "LayerFeature")
        layer_feature.set("layerRef", self.layer_name)
        color_set = ET.SubElement(layer_feature, "Set")
        color_ref = ET.SubElement(color_set, "ColorRef")
        color_ref.set("id", self.color)
        for feature in self.features:
            feature.write_xml(layer_feature)
