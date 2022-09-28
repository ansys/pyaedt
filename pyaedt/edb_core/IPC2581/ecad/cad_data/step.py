import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.component.component import Component
from pyaedt.edb_core.IPC2581.ecad.cad_data.layer_feature.layer_feature import LayerFeature
from pyaedt.edb_core.IPC2581.ecad.cad_data.logical_net.logical_net import LogicalNet
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.package import Package
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_def import PadstackDef
from pyaedt.edb_core.IPC2581.ecad.cad_data.phy_net.phy_net import PhyNet
from pyaedt.edb_core.IPC2581.ecad.cad_data.profile import Profile


class Step(object):
    def __init__(self):
        self._padstack_defs = []
        self._profile = Profile()
        self._packages = []
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

    def add_padstack_def(self, padstack_def=None):
        if isinstance(padstack_def, PadstackDef):
            self._padstack_defs.append(padstack_def)
            return True
        return False

    def add_package(self, package=None):
        if isinstance(package, Package):
            self._packages.append(package)
            return True
        return False

    def add_component(self, component=None):
        if isinstance(component, Component):
            self._components.append(component)
            return True
        return False

    def add_layer_feature(self, layer_feature=None):
        if isinstance(layer_feature, LayerFeature):
            self._layer_features.append(layer_feature)
            return True
        return False

    def write_xml(self, cad_data):
        if cad_data:
            step = ET.SubElement(cad_data, "Step")
            step.set("name", self.design_name)
            for padsatck_def in self.padstack_defs:
                padsatck_def.write_xml(step)
            for package in self.packages:
                package.write_xml(step)
            for component in self.components:
                component.write_xml(step)
            for logical_net in self.logical_nets:
                logical_net.write_xml(step)
