import re

from pyaedt import pyaedt_function_handler
from pyaedt.edb_core.edb_data.nets_data import EDBNetsData
from pyaedt.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyaedt.edb_core.edb_data.primitives_data import EDBPrimitives
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
        self._positive_node = PinGroup()
        self._negative_node = PinGroup()
        self._amplitude = 1.0
        self._phase = 0.0
        self._impedance = 1.0
        self._r = 1.0
        self._l = 0.0
        self._c = 0.0
        self._create_physical_resistor = True
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
        if isinstance(value, (Node, PinGroup)):
            self._positive_node = value

    @property
    def negative_node(self):  # pragma: no cover
        """Negative node of the source."""
        return self._negative_node

    @negative_node.setter
    def negative_node(self, value):  # pragma: no cover
        if isinstance(value, (Node, PinGroup)):
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


class PinGroup(object):
    """Manages pin groups."""

    def __init__(self, name="", edb_pin_group=None, pedb=None):
        self._pedb = pedb
        self._edb_pin_group = edb_pin_group
        self._name = name
        self._component = ""
        self._node_pins = []
        self._net = ""

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def name(self):
        """Name."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def component(self):
        """Component."""
        return self._component

    @component.setter
    def component(self, value):
        self._component = value

    @property
    def node_pins(self):
        """Node pins."""
        return self._node_pins

    @node_pins.setter
    def node_pins(self, value):
        self._node_pins = value

    @property
    def net(self):
        """Net."""
        return self._net

    @net.setter
    def net(self, value):
        self._net = value

    def _create_terminal(self, is_reference=False):
        pg_term = self._edb_pin_group.GetPinGroupTerminal()
        if pg_term.IsNull():
            return self._pedb.edb.Cell.Terminal.PinGroupTerminal.Create(
                self._active_layout,
                self._edb_pin_group.GetNet(),
                self.name,
                self._edb_pin_group,
                is_reference,
            )
        else:
            return pg_term

    def create_current_source_terminal(self, magnitude=1, phase=0):
        terminal = self._create_terminal()
        terminal.SetBoundaryType(self._pedb.edb.Cell.Terminal.BoundaryType.kCurrentSource)
        terminal.SetSourceAmplitude(self._pedb.edb_value(magnitude))
        terminal.SetSourcePhase(self._pedb.edb.Utility.Value(phase))
        return terminal

    def create_voltage_source_terminal(self, magnitude=1, phase=0):
        terminal = self._create_terminal()
        terminal.SetBoundaryType(self._pedb.edb.Cell.Terminal.BoundaryType.kVoltageSource)
        terminal.SetSourceAmplitude(self._pedb.edb_value(magnitude))
        terminal.SetSourcePhase(self._pedb.edb.Utility.Value(phase))
        return terminal


class CircuitPort(Source, object):
    """Manages a circuit port."""

    def __init__(self, impedance="50"):
        self._impedance = impedance
        Source.__init__(self)
        self._source_type = SourceType.CircPort

    @property
    def impedance(self):
        """Impedance."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value

    @property
    def get_type(self):
        """Get type."""
        return self._source_type


class VoltageSource(Source):
    """Manages a voltage source."""

    def __init__(self):
        super(VoltageSource, self).__init__()
        self._magnitude = "1V"
        self._phase = "0Deg"
        self._impedance = "0.05"
        self._source_type = SourceType.Vsource

    @property
    def magnitude(self):
        """Magnitude."""
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value

    @property
    def phase(self):
        """Phase."""
        return self._phase

    @phase.setter
    def phase(self, value):
        self._phase = value

    @property
    def impedance(self):
        """Impedance."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class CurrentSource(Source):
    """Manages a current source."""

    def __init__(self):
        super(CurrentSource, self).__init__()
        self._magnitude = "0.1A"
        self._phase = "0Deg"
        self._impedance = "1e7"
        self._source_type = SourceType.Isource

    @property
    def magnitude(self):
        """Magnitude."""
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value

    @property
    def phase(self):
        """Phase."""
        return self._phase

    @phase.setter
    def phase(self, value):
        self._phase = value

    @property
    def impedance(self):
        """Impedance."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class DCTerminal(Source):
    """Manages a dc terminal source."""

    def __init__(self):
        super(DCTerminal, self).__init__()

        self._source_type = SourceType.DcTerminal

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class ResistorSource(Source):
    """Manages a resistor source."""

    def __init__(self):
        super(ResistorSource, self).__init__()
        self._rvalue = "50"
        self._source_type = SourceType.Rlc

    @property
    def rvalue(self):
        """Resistance value."""
        return self._rvalue

    @rvalue.setter
    def rvalue(self, value):
        self._rvalue = value

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class CommonExcitation(object):
    def __init__(self, pedb, edb_terminal):
        self._pedb = pedb
        self._edb_terminal = edb_terminal

    @property
    def _edb(self):
        return self._pedb.edb

    @property
    def name(self):
        """Port Name.

        Returns
        -------
        str
        """
        return self._edb_terminal.GetName()

    @property
    def net_name(self):
        """Net Name.

        Returns
        -------
        str
        """
        return self._edb_terminal.GetNet().GetName()

    @property
    def net(self):
        """Net Object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`
        """
        return EDBNetsData(self._edb_terminal.GetNet(), self._pedb)

    @property
    def terminal_type(self):
        """Terminal Type.

        Returns
        -------
        int
        """
        return self._edb_terminal.GetTerminalType()

    @property
    def boundary_type(self):
        """Boundary Type.

        Returns
        -------
        int
        """
        return self._edb_terminal.GetBoundaryType()


class ExcitationPorts(CommonExcitation):
    """Manages excitation properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        Edb object from Edblib.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from Edb.


    Examples
    --------
    This example shows how to access this class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> exc = edb.excitations
    >>> print(exc["Port1"].name)
    """

    def __init__(self, pedb, edb_terminal):
        CommonExcitation.__init__(self, pedb, edb_terminal)
        self._reference_object = None

    @property
    def _edb_properties(self):
        p = self._edb_terminal.GetProductSolverOption(self._edb.ProductId.Designer, "HFSS")
        return p

    @property
    def hfss_type(self):
        """Get hfss port type."""
        txt = re.search(r"'HFSS Type'='.*?'", self._edb_properties).group()
        return txt.split("=")[1].replace("'", "")

    @property
    def horizontal_extent_factor(self):
        """Get horizontal extent factor."""
        txt = re.search(r"'Horizontal Extent Factor'='.*?'", self._edb_properties).group()
        return float(txt.split("=")[1].replace("'", ""))

    @property
    def vertical_extent_factor(self):
        """Get vertical extent factor."""
        txt = re.search(r"'Vertical Extent Factor'='.*?'", self._edb_properties).group()
        return float(txt.split("=")[1].replace("'", ""))

    @property
    def radial_extent_factor(self):
        """Get radial extent factor."""
        txt = re.search(r"'Radial Extent Factor'='.*?'", self._edb_properties).group()
        return float(txt.split("=")[1].replace("'", ""))

    @property
    def pec_launch_width(self):
        """Get pec launch width."""
        txt = re.search(r"'PEC Launch Width'='.*?'", self._edb_properties).group()
        return txt.split("=")[1].replace("'", "")

    @property
    def impedance(self):
        """Impedance of the port."""
        return self._edb_terminal.GetImpedance().ToDouble()

    @property
    def is_circuit(self):
        """Return ``True`` if is a circuit port."""
        return self._edb_terminal.GetIsCircuitPort()

    @property
    def magnitude(self):
        """Magnitude."""
        return self._edb_terminal.GetSourceAmplitude().ToDouble()

    @property
    def phase(self):
        """Phase."""
        return self._edb_terminal.GetSourcePhase().ToDouble()

    @property
    def renormalize(self):
        """Either if renormalize is active or not."""
        return self._edb_terminal.GetPortPostProcessingProp().DoRenormalize

    @property
    def deembed(self):
        """Either if deembed is active or not."""
        return self._edb_terminal.GetPortPostProcessingProp().DoDeembed

    @property
    def deembed_gapport_inductance(self):
        """Deembed Gap Port Inductance value."""
        return self._edb_terminal.GetPortPostProcessingProp().DoDeembedGapL

    @property
    def deembed_length(self):
        """Deembed Length."""
        return self._edb_terminal.GetPortPostProcessingProp().DeembedLength.ToDouble()

    @property
    def renormalize_z0(self):
        """Renormalize Z0 value (real, imag)."""
        return (
            self._edb_terminal.GetPortPostProcessingProp().RenormalizionZ0.ToComplex().Item1,
            self._edb_terminal.GetPortPostProcessingProp().RenormalizionZ0.ToComplex().Item2,
        )

    @property
    def reference_object(self):
        """This returns the object assigned as reference. It can be a primitive or a padstack instance.


        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance` or
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        if not self._reference_object:
            term = self._edb_terminal
            if self.terminal_type == self._pedb.edb.Cell.Terminal.TerminalType.EdgeTerminal:
                edges = self._edb_terminal.GetEdges()
                edgeType = edges[0].GetEdgeType()
                if edgeType == self._pedb.edb.Cell.Terminal.EdgeType.PadEdge:
                    self._reference_object = self.get_pad_edge_terminal_reference_pin()
                else:
                    self._reference_object = self.get_edge_terminal_reference_primitive()
            elif self.terminal_type == self._pedb.edb.Cell.Terminal.TerminalType.PinGroupTerminal:
                self._reference_object = self.get_pin_group_terminal_reference_pin()
            elif self.terminal_type == self._pedb.edb.Cell.Terminal.TerminalType.PointTerminal:
                self._reference_object = self.get_point_terminal_reference_primitive()
            elif self.terminal_type == self._pedb.edb.Cell.Terminal.TerminalType.PadstackInstanceTerminal:
                self._reference_object = self.get_padstack_terminal_reference_pin()
            else:
                self._pedb.logger.warning("Invalid Terminal Type={}".format(term.GetTerminalType()))  # pragma: no cover
        return self._reference_object

    @property
    def reference_net_name(self):
        """Net name to which reference_object belongs."""
        ref_obj = self._reference_object if self._reference_object else self.reference_object
        if ref_obj:
            return ref_obj.net_name
        return  # pragma: no cover

    @pyaedt_function_handler()
    def get_padstack_terminal_reference_pin(self, gnd_net_name_preference=None):
        """Get a list of pad stacks instances and serves Coax wave ports,
        pingroup terminals, PadEdge terminals.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstack_data.EDBPadstackInstance`
        """

        if self._edb_terminal.GetIsCircuitPort():
            return self.get_pin_group_terminal_reference_pin()
        _, padStackInstance, layer = self._edb_terminal.GetParameters()

        # Get the pastack instance of the terminal
        compInst = self._edb_terminal.GetComponent()
        pins = self._pedb.core_components.get_pin_from_component(compInst.GetName())
        return self._get_closest_pin(padStackInstance, pins, gnd_net_name_preference)

    @pyaedt_function_handler()
    def get_pin_group_terminal_reference_pin(self, gnd_net_name_preference=None):
        """Return a list of pins and serves terminals connected to pingroups.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstack_data.EDBPadstackInstance`
        """

        refTerm = self._edb_terminal.GetReferenceTerminal()
        if self._edb_terminal.GetTerminalType() == self._pedb.edb.Cell.Terminal.TerminalType.PinGroupTerminal:
            padStackInstance = self._edb_terminal.GetPinGroup().GetPins()[0]
            pingroup = refTerm.GetPinGroup()
            refPinList = pingroup.GetPins()
            return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
        elif self._edb_terminal.GetTerminalType() == self._pedb.edb.Cell.Terminal.TerminalType.PadstackInstanceTerminal:
            _, padStackInstance, layer = self._edb_terminal.GetParameters()
            if refTerm.GetTerminalType() == self._pedb.edb.Cell.Terminal.TerminalType.PinGroupTerminal:
                pingroup = refTerm.GetPinGroup()
                refPinList = pingroup.GetPins()
                return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
            else:
                try:
                    returnOK, refTermPSI, layer = refTerm.GetParameters()
                    return EDBPadstackInstance(refTermPSI, self._pedb)
                except AttributeError:
                    return None
        return None  # pragma: no cover

    @pyaedt_function_handler()
    def get_edge_terminal_reference_primitive(self):
        """Check and  return a primitive instance that serves Edge ports,
        wave ports and coupled edge ports that are directly connedted to primitives.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """

        ref_layer = self._edb_terminal.GetReferenceLayer()
        edges = self._edb_terminal.GetEdges()
        _, prim_value, point_data = edges[0].GetParameters()
        X = point_data.X
        Y = point_data.Y
        shape_pd = self._pedb.edb.Geometry.PointData(X, Y)
        layer_name = ref_layer.GetName()
        for primitive in self._pedb.active_layout.Primitives:
            if primitive.GetLayer().GetName() == layer_name or not layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if prim_shape_data.PointInPolygon(shape_pd):
                    return EDBPrimitives(primitive, self._pedb)
        return None  # pragma: no cover

    @pyaedt_function_handler()
    def get_point_terminal_reference_primitive(self):
        """Find and return the primitive reference for the point terminal or the padstack instance.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance` or
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """

        ref_term = self._edb_terminal.GetReferenceTerminal()  # return value is type terminal
        _, point_data, layer = ref_term.GetParameters()
        X = point_data.X
        Y = point_data.Y
        shape_pd = self._pedb.edb.Geometry.PointData(X, Y)
        layer_name = layer.GetName()
        for primitive in self._pedb.active_layout.Primitives:
            if primitive.GetLayer().GetName() == layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if prim_shape_data.PointInPolygon(shape_pd):
                    return EDBPrimitives(primitive, self._pedb)
        for vias in self._pedb.core_padstack.padstack_instances.values():
            if layer_name in vias.layer_range_names:
                plane = self._pedb.core_primitives.Shape(
                    "rectangle", pointA=vias.position, pointB=vias.padstack_definition.bounding_box[1]
                )
                rectangle_data = vias._pedb.core_primitives.shape_to_polygon_data(plane)
                if rectangle_data.PointInPolygon(shape_pd):
                    return vias
        return None

    @pyaedt_function_handler()
    def get_pad_edge_terminal_reference_pin(self, gnd_net_name_preference=None):
        """Get the closest pin padstack instances and serves any edge terminal connected to a pad.

        Parameters
        ----------
        gnd_net_name_preference : str, optional
            Preferred reference net name. Optianal, default is `None` which will auto compute the gnd name.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`
        """
        comp_inst = self._edb_terminal.GetComponent()
        pins = self._pedb.core_components.get_pin_from_component(comp_inst.GetName())
        try:
            edges = self._edb_terminal.GetEdges()
        except AttributeError:
            return None
        _, pad_edge_pstack_inst, pad_edge_layer, pad_edge_polygon_data = edges[0].GetParameters()
        return self._get_closest_pin(pad_edge_pstack_inst, pins, gnd_net_name_preference)

    @pyaedt_function_handler()
    def _get_closest_pin(self, ref_pin, pin_list, gnd_net=None):
        _, pad_stack_inst_point, rotation = ref_pin.GetPositionAndRotation()  # get the xy of the padstack
        if gnd_net is not None:
            power_ground_net_names = [gnd_net]
        else:
            power_ground_net_names = [net for net in self._pedb.core_nets.power_nets.keys()]
        comp_ref_pins = [i for i in pin_list if i.GetNet().GetName() in power_ground_net_names]
        if len(comp_ref_pins) == 0:
            self._pedb.logger.error(
                "Terminal with PadStack Instance Name {} component has no reference pins.".format(ref_pin.GetName())
            )  # pragma: no cover
            return None  # pragma: no cover
        closest_pin_distance = None
        pin_obj = None
        for pin in comp_ref_pins:  # find the distance to all the pins to the terminal pin
            if pin.GetName() == ref_pin.GetName():  # skip the reference psi
                continue  # pragma: no cover
            _, pin_point, rotation = pin.GetPositionAndRotation()
            distance = pad_stack_inst_point.Distance(pin_point)
            if closest_pin_distance is None:
                closest_pin_distance = distance
                pin_obj = pin
            elif closest_pin_distance < distance:
                continue
            else:
                closest_pin_distance = distance
                pin_obj = pin
        if pin_obj:
            return EDBPadstackInstance(pin_obj, self._pedb)


class ExcitationSources(CommonExcitation):
    """Manage sources properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        Edb object from Edblib.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from Edb.



    Examples
    --------
    This example shows how to access this class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> all_sources = edb.sources
    >>> print(all_sources["VSource1"].name)

    """

    def __init__(self, pedb, edb_terminal):
        CommonExcitation.__init__(self, pedb, edb_terminal)

    @property
    def magnitude(self):
        """Get the magnitude of the source."""
        return self._edb_terminal.GetSourceAmplitude().ToDouble()

    @property
    def phase(self):
        """Get the phase of the source."""
        return self._edb_terminal.GetSourcePhase().ToDouble()


class ExcitationProbes(CommonExcitation):
    """Manage probes properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        Edb object from Edblib.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from Edb.


    Examples
    --------
    This example shows how to access this class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> probes = edb.probes
    >>> print(probes["Probe1"].name)
    """

    def __init__(self, pedb, edb_terminal):
        CommonExcitation.__init__(self, pedb, edb_terminal)


class ExcitationDifferential:
    """Manage differential excitation properties."""

    def __init__(self, pedb, edb_boundle_terminal):
        self._pedb = pedb
        self._edb_boundle_terminal = edb_boundle_terminal

    @property
    def name(self):
        """Port Name."""
        return self._edb_boundle_terminal.GetName()

    @property
    def edb(self):  # pragma: no cover
        """Get edb."""
        return self._pedb.edb

    @property
    def terminals(self):
        """Get terminals belonging to this excitation."""
        return {i.GetName(): ExcitationPorts(self._pedb, i) for i in list(self.edb_boundle_terminal.GetTerminals())}

    @property
    def reference_net_name(self):
        """Reference Name. Not applicable to Differential pairs."""
        return
