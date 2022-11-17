import math
import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.component.component import Component
from pyaedt.edb_core.IPC2581.ecad.cad_data.layer_feature.layer_feature import (
    LayerFeature,
)
from pyaedt.edb_core.IPC2581.ecad.cad_data.logical_net.logical_net import LogicalNet
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.package import Package
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_def import PadstackDef
from pyaedt.edb_core.IPC2581.ecad.cad_data.phy_net.phy_net import PhyNet
from pyaedt.edb_core.IPC2581.ecad.cad_data.profile import Profile


class Step(object):
    def __init__(self, caddata, edb, units, ipc):
        self.design_name = caddata.design_name
        self._pedb = edb
        self._ipc = ipc
        self.units = units
        self._cad_data = caddata
        self._padstack_defs = {}
        self._profile = Profile()
        self._packages = {}
        self._components = []
        self._logical_nets = []
        self._physical_nets = []
        self._layer_features = []

    @property
    def padstack_defs(self):
        return self._padstack_defs

    @padstack_defs.setter
    def padstack_defs(self, value):
        if isinstance(value, list):
            if len([pad for pad in value if isinstance(pad, PadstackDef)]) == len(value):
                self._padstack_defs = value

    @property
    def packages(self):
        return self._packages

    @packages.setter
    def packages(self, value):
        if isinstance(value, list):
            if len([pkg for pkg in value if isinstance(pkg, Package)]) == len(value):
                self._packages = value

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        if isinstance(value, list):
            if len([cmp for cmp in value if isinstance(cmp, Component)]) == len(value):
                self._components = value

    @property
    def logical_nets(self):
        return self._logical_nets

    @logical_nets.setter
    def add_logical_net(self, value):
        if isinstance(value, LogicalNet):
            self._logical_nets.append(value)

    @property
    def layer_features(self):
        return self._layer_features

    @layer_features.setter
    def layer_features(self, value):
        if isinstance(value, list):
            if len(
                [
                    feat
                    for feat in value
                    if isinstance(
                        feat,
                    )
                ]
            ):
                self._layer_features = value

    @property
    def physical_nets(self):
        return self._physical_nets

    @physical_nets.setter
    def physical_nets(self, value):
        if isinstance(value, list):
            if len([phy_net for phy_net in value if isinstance(phy_net, PhyNet)]) == len(value):
                self._physical_nets = value

    def add_physical_net(self, phy_net=None):
        if isinstance(phy_net, PhyNet):
            self._physical_nets.append(phy_net)
            return True
        return False

    def add_padstack_def(self, padstackdef=None):
        if isinstance(padstackdef, PadstackDef):
            self._padstack_defs.append(padstackdef)

    def add_component(self, component=None):
        # adding component add package in Step
        if component:
            if not component.part_name in self._packages:
                component_bounding_box = component.bounding_box
                middle_point_x = (component_bounding_box[0] + component_bounding_box[2]) / 2
                middle_point_y = (component_bounding_box[1] + component_bounding_box[3]) / 2
                component_transform = component.edbcomponent.GetTransform()
                component_rotation = component_transform.Rotation.ToDouble()
                if component_rotation > math.pi:
                    component_rotation -= math.pi
                middle_point_x = middle_point_x - component_transform.XOffset.ToDouble()
                middle_point_y = middle_point_y - component_transform.YOffset.ToDouble()
                av_x = middle_point_x * math.cos(component_rotation) + middle_point_y * math.sin(component_rotation)
                av_y = middle_point_y * math.cos(component_rotation) - middle_point_y * math.sin(component_rotation)
                if component.placement_layer == list(component._pedb.stackup.signal_layers.values())[-1].name:
                    av_x = -av_x
                package = Package(self._ipc)
                package.name = component.part_name
                package.height = ""
                package.type = component.type
                pin_number = 0
                for _, pin in component.pins.items():
                    geometry_type, pad_parameters, pos_x, pos_y, rot = self._pedb.core_padstack.get_pad_parameters(
                        pin._edb_padstackinstance, "TOP", 0
                    )
                    pos_x = self._ipc.from_meter_to_units(pos_x - av_x, self.units)
                    pos_y = self._ipc.from_meter_to_units(pos_y - av_y, self.units)
                    primitive_ref = ""
                    if geometry_type == 1:
                        primitive_ref = "CIRC_{}".format(pad_parameters[0])
                    elif geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(pad_parameters[0], pad_parameters[0])
                    elif geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(pad_parameters[0], pad_parameters[1])
                    elif geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(pad_parameters[0], pad_parameters[1], pad_parameters[2])
                    if primitive_ref:
                        package.add_pin(number=pin_number, x=pos_x, y=pos_y, primitive_ref=primitive_ref)
                    pin_number += 1
                self.packages[package.name] = package
            ipc_component = Component()
            ipc_component.type = component.type
            try:
                ipc_component.value = component.value
            except:
                pass
            ipc_component.refdes = component.refdes
            ipc_component.location = component.center
            ipc_component.rotation = component.rotation
            ipc_component.package_ref = component.part_name
            ipc_component.part = component.part_name
            ipc_component.layer_ref = component.placement_layer
            self.components.append(ipc_component)

    def add_layer_feature(self, layer=None, top_bottom_layers=[]):
        if layer.type == "signal":
            layer_feature = LayerFeature(self._ipc)
            layer_feature.layer_name = layer.name
            layer_feature.color = layer.color
            for poly in layer._pclass._pedb.core_primitives.polygons_by_layer[layer.name]:
                layer_feature.add_feature(poly)
            path_list = [
                layout_obj
                for layout_obj in layer._pclass._pedb.core_primitives.primitives_by_layer[layer.name]
                if layout_obj.type == "Path"
            ]
            for path in path_list:
                layer_feature.add_feature(path)
            self.layer_features.append(layer_feature)
            if layer.name in top_bottom_layers:
                for comp_instance in [
                    cmp
                    for cmp in list(self._pedb.core_components.components.values())
                    if cmp.placement_layer == layer.name
                ]:
                    layer_feature.add_component_padstack_instance_feature(comp_instance, top_bottom_layers)
                    self.layer_features.append(layer_feature)
            # trying with via as pin as well
            vias = [via for via in list(self._pedb.core_padstack.padstack_instances.values())]
            for via in vias:
                padstack_def = self._pedb.core_padstack.padstacks[via.padstack_definition]
                # if layer.name in padstack_def.pad_by_layer:
                #    layer_feature.add_via_instance_feature(via, layer.name)
                layer_feature.add_via_instance_feature(via, padstack_def)
                self.layer_features.append(layer_feature)

    def add_drill_layer_feature(self, via_list=None, layer_feature_name=""):
        if via_list:
            drill_layer_feature = LayerFeature(self._ipc)
            drill_layer_feature.is_drill_feature = True
            drill_layer_feature.layer_name = layer_feature_name
            for via in via_list:
                try:
                    via_diameter = self._pedb.core_padstack.padstacks[via.padstack_definition].hole_properties[0]
                    drill_layer_feature.add_drill_feature(
                        via, self._ipc.from_meter_to_units(via_diameter, self._ipc.units)
                    )
                except:
                    pass
            self.layer_features.append(drill_layer_feature)

    def write_xml(self, cad_data):
        step = ET.SubElement(cad_data, "Step")
        step.set("name", self.design_name)
        for padsatck_def in list(self.padstack_defs.values()):
            padsatck_def.write_xml(step)
        for package in list(self.packages.values()):
            package.write_xml(step)
        for component in list(self.components.values()):
            component.write_xml(step)
        for logical_net in self.logical_nets:
            logical_net.write_xml(step)
