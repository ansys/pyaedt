import xml.etree.cElementTree as ET


class Layer(object):
    def __init__(self):
        self.name = ""
        self._layer_function = ""
        self._layer_side = ""
        self._layer_polarity = ""

    @property
    def layer_function(self):
        return self._layer_function

    @layer_function.setter
    def layer_function(self, value):
        self._layer_function = value

    @property
    def layer_side(self):
        return self._layer_side

    @layer_side.setter
    def layer_side(self, value):
        self._layer_side = value

    @property
    def layer_polarity(self):
        return self._layer_polarity

    @layer_polarity.setter
    def layer_polarity(self, value):
        self._layer_polarity = value

    def write_xml(self, cad_data):
        layer = ET.SubElement(cad_data, "Layer")
        layer.set("name", self.name)
        layer.set("layerFunction", self.layer_function)
        layer.set("side", self.layer_side)
        layer.set("polarity", self.layer_polarity)
