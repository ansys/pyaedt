import xml.etree.cElementTree as ET


class Layer(object):
    def __init__(self):
        self.name = ""
        self._layer_function = Function().Conductor
        self._layer_side = LayerSide().Top
        self._layer_polarity = LayerPolarity().Positive

    @property
    def layer_function(self):
        return self._layer_function

    @layer_function.setter
    def layer_function(self, value):
        if isinstance(value, int):
            self._layer_function = value

    @property
    def layer_side(self):
        return self._layer_side

    @layer_side.setter
    def layer_side(self, value):
        if isinstance(value, int):
            self._layer_side = value

    @property
    def layer_polarity(self):
        return self._layer_polarity

    @layer_polarity.setter
    def layer_polarity(self, value):
        if isinstance(value, int):
            self._layer_polarity = value

    def write_xml(self, cad_data):
        if cad_data:
            layer = ET.SubElement(cad_data, "Layer")
            layer.set("name", self.name)
            layer.set("layerFunction", self.layer_function)
            layer.set("side", self.layer_side)
            layer.set("polarity", self.layer_polarity)


class Function(object):
    (Conductor, Dielpreg, Plane, Drill) = range(0, 4)


class LayerSide(object):
    (Top, Internal, Bottom, All) = range(0, 4)


class LayerPolarity(object):
    (Positive, Negative) = range(0, 2)
