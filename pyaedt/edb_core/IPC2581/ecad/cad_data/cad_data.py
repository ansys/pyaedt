import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.ecad.cad_data.stackup.layer import Layer
from pyaedt.edb_core.IPC2581.ecad.cad_data.stackup.stackup import Stackup
from pyaedt.edb_core.IPC2581.ecad.cad_data.step import Step


class CadData(object):
    def __init__(self, ecad):
        self.design_name = ecad.design_name
        self._layers = []
        self.stackup = Stackup()
        self.cad_data_step = Step(self)

    @property
    def layers(self):
        return self._layers

    @layers.setter
    def layers(self, value):
        if isinstance(value, list):
            if len([lay for lay in value if isinstance(lay, Layer)]):
                self._layers = value

    def add_layer(self, layer_name="", layer_function="", layer_side="internal", polarity="positive"):
        layer = Layer()
        layer.name = layer_name
        layer.layer_function = layer_function
        layer.layer_side = layer_side
        layer.layer_polarity = polarity
        self.layers.append(layer)

    def write_xml(self, ecad):
        if ecad:
            cad_data = ET.SubElement(ecad, "CadData")
            for layer in self.layers:
                layer.write_xml(cad_data)
            for step in self.cad_data_step:
                step.write_xml(cad_data)
