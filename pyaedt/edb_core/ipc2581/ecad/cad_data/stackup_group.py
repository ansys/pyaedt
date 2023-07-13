from pyaedt.edb_core.ipc2581.ecad.cad_data.layer import Layer
from pyaedt.edb_core.ipc2581.ecad.cad_data.stackup_layer import StackupLayer
from pyaedt.generic.general_methods import ET


class StackupGroup(object):
    def __init__(self):
        self.name = "GROUP_PRIMARY"
        self.thickness = 0
        self.tol_plus = 0
        self.tol_minus = 0
        self._stackup_layers = []

    @property
    def stackup_layers(self):
        return self._stackup_layers

    @stackup_layers.setter
    def stackup_layers(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([lay for lay in value if isinstance(lay, Layer)]):
                self._stackup_layers = value

    def add_stackup_layer(
        self, layer_name="", thickness="", tol_minus="0.0", tol_plus="0.0", sequence=""
    ):  # pragma no cover
        stackup_layer = StackupLayer()
        stackup_layer.layer_name = layer_name
        stackup_layer.thickness = thickness
        stackup_layer.tol_plus = tol_plus
        stackup_layer.tol_minus = tol_minus
        stackup_layer.sequence = sequence
        self._stackup_layers.append(stackup_layer)

    def write_xml(self, stackup):  # pragma no cover
        stackup_group = ET.SubElement(stackup, "StackupGroup")
        stackup_group.set("name", "GROUP_PRIMARY")
        stackup_group.set("thickness", str(self.thickness))
        stackup_group.set("tolPlus", str(self.tol_plus))
        stackup_group.set("tolMinus", str(self.tol_minus))
        for layer in self.stackup_layers:
            layer.write_xml(stackup_group)
