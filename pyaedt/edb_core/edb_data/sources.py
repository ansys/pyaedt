from pyaedt.generic.constants import NodeType
from pyaedt.generic.constants import SourceType


class Node(object):
    """Provides for handling nodes for Siwave sources."""

    def __init__(self):
        self._component = None
        self._net = None
        self._node_type = NodeType.Positive
        self._name = ""

    @property
    def component(self):  # pragma: no cover
        """Component name containing the node."""
        return self._component

    @component.setter
    def component(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._component = value

    @property
    def net(self):  # pragma: no cover
        """Net of the node."""
        return self._net

    @net.setter
    def net(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._net = value

    @property
    def node_type(self):  # pragma: no cover
        """Type of the node."""
        return self._node_type

    @node_type.setter
    def node_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._node_type = value

    @property
    def name(self):  # pragma: no cover
        """Name of the node."""
        return self._name

    @name.setter
    def name(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._name = value

    def _json_format(self):  # pragma: no cover
        dict_out = {}
        for k, v in self.__dict__.items():
            dict_out[k[1:]] = v
        return dict_out

    def _read_json(self, node_dict):  # pragma: no cover
        for k, v in node_dict.items():
            self.__setattr__(k, v)


class Source(object):
    """Provides for handling Siwave sources."""

    def __init__(self):
        self._name = ""
        self._source_type = SourceType.Vsource
        self._positive_node = Node()
        self._negative_node = Node()
        self._amplitude = 1.0
        self._phase = 0.0
        self._impedance = 1.0
        self._r = 1.0
        self._l = 0.0
        self._c = 0.0
        self._create_physical_resistor = True
        self._config_init()

    def _config_init(self):
        self._positive_node.node_type = int(NodeType.Positive)
        self._positive_node.name = "pos_term"
        self._negative_node.node_type = int(NodeType.Negative)
        self._negative_node.name = "neg_term"

    @property
    def name(self):  # pragma: no cover
        """Source name."""
        return self._name

    @name.setter
    def name(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._name = value

    @property
    def source_type(self):  # pragma: no cover
        """Source type."""
        return self._source_type

    @source_type.setter
    def source_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._source_type = value
            if value == 3:
                self._impedance = 1e-6
            if value == 4:
                self._impedance = 5e7
            if value == 5:
                self._r = 1.0
                self._l = 0.0
                self._c = 0.0

    @property
    def positive_node(self):  # pragma: no cover
        """Positive node of the source."""
        return self._positive_node

    @positive_node.setter
    def positive_node(self, value):  # pragma: no cover
        if isinstance(value, Node):
            self._positive_node = value

    @property
    def negative_node(self):  # pragma: no cover
        """Negative node of the source."""
        return self._negative_node

    @negative_node.setter
    def negative_node(self, value):  # pragma: no cover
        if isinstance(value, Node):
            self._negative_node = value
            #

    @property
    def amplitude(self):  # pragma: no cover
        """Amplitude value of the source. Either amperes for current source or volts for
        voltage source."""
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._amplitude = value

    @property
    def phase(self):  # pragma: no cover
        """Phase of the source."""
        return self._phase

    @phase.setter
    def phase(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._phase = value

    @property
    def impedance(self):  # pragma: no cover
        """Impedance values of the source."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._impedance = value

    @property
    def r_value(self):
        return self._r

    @r_value.setter
    def r_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._r = value

    @property
    def l_value(self):
        return self._l

    @l_value.setter
    def l_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._l = value

    @property
    def c_value(self):
        return self._c

    @c_value.setter
    def c_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._c = value

    @property
    def create_physical_resistor(self):
        return self._create_physical_resistor

    @create_physical_resistor.setter
    def create_physical_resistor(self, value):
        if isinstance(value, bool):
            self._create_physical_resistor = value

    def _json_format(self):  # pragma: no cover
        dict_out = {}
        for k, v in self.__dict__.items():
            if k == "_positive_node" or k == "_negative_node":
                nodes = v._json_format()
                dict_out[k[1:]] = nodes
            else:
                dict_out[k[1:]] = v
        return dict_out

    def _read_json(self, source_dict):  # pragma: no cover
        for k, v in source_dict.items():
            if k == "positive_node":
                self.positive_node._read_json(v)
            elif k == "negative_node":
                self.negative_node._read_json(v)
            else:
                self.__setattr__(k, v)
