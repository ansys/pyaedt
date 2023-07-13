from pyaedt.edb_core.ipc2581.ecad.cad_data.layer import Layer
from pyaedt.edb_core.ipc2581.ecad.cad_data.stackup import Stackup
from pyaedt.edb_core.ipc2581.ecad.cad_data.step import Step
from pyaedt.generic.general_methods import ET


class CadData(object):
    def __init__(self, ecad, edb, units, ipc):
        self.design_name = ecad.design_name
        self._pedb = edb
        self._ipc = ipc
        self.units = units
        self._layers = []
        self.stackup = Stackup()
        self.cad_data_step = Step(self, edb, self.units, self._ipc)

    @property
    def layers(self):
        return self._layers

    def add_layer(
        self, layer_name="", layer_function="", layer_side="internal", polarity="positive"
    ):  # pragma no cover
        layer = Layer()
        layer.name = layer_name
        layer.layer_function = layer_function
        layer.layer_side = layer_side
        layer.layer_polarity = polarity
        self.layers.append(layer)

    def write_xml(self, ecad):  # pragma no cover
        self.design_name = self._pedb.cell_names[0]
        cad_data = ET.SubElement(ecad, "CadData")
        for layer in self.layers:
            layer.write_xml(cad_data)
        self.stackup.write_xml(cad_data)
        self.cad_data_step.write_xml(cad_data)
