import re
from pyaedt import pyaedt_function_handler
from pyaedt.edb_core.edb_data.connectable import Connectable
from pyaedt.edb_core.edb_data.nets_data import EDBNetsData
from pyaedt.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyaedt.edb_core.edb_data.primitives_data import cast


class Terminal(Connectable):

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._reference_object = None

    @property
    def _port_post_processing_prop(self):
        """Get port post processing properties."""
        return self._edb_object.GetPortPostProcessingProp

    @property
    def do_renormalize(self):
        """Determine whether port renormalization is enabled."""
        return self._edb_object.DoRenormalize

    @do_renormalize.setter
    def do_renormalize(self, value):
        self._edb_object.DoRenormalize = value

    @property
    def name(self):
        """Port Name.

        Returns
        -------
        str
        """
        return self._edb_terminal.GetName()

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            if not any(port for port in list(self._pedb.excitations.keys()) if port == value):
                self._edb_object.SetName(value)
            else:
                self._pedb.logger.warning("An existing port already has this same name. A port name must be unique.")

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
        """
        return self.net.name

    @property
    def net(self):
        """Net Object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`
        """
        return EDBNetsData(self._edb_object.GetNet(), self._pedb)

    @property
    def terminal_type(self):
        """Terminal Type.

        Returns
        -------
        int
        """
        return self._edb_object.GetTerminalType()

    @property
    def boundary_type(self):
        """Boundary Type.

        Returns
        -------
        int
        """
        return self._edb_object.GetBoundaryType()

    @property
    def impedance(self):
        """Impedance of the port."""
        return self._edb_object.GetImpedance().ToDouble()

    @impedance.setter
    def impedance(self, value):
        self._edb_object.SetImpedance(self._pedb.edb_value(value))

    @property
    def reference_object(self):
        """This returns the object assigned as reference. It can be a primitive or a padstack instance.


        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance` or
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        if not self._reference_object:
            term = self._edb_object
            try:
                if self.terminal_type == self._pedb.edb_api.cell.terminal.TerminalType.EdgeTerminal:
                    edges = self._edb_object.GetEdges()
                    edgeType = edges[0].GetEdgeType()
                    if edgeType == self._pedb.edb_api.cell.terminal.EdgeType.PadEdge:
                        self._reference_object = self.get_pad_edge_terminal_reference_pin()
                    else:
                        self._reference_object = self.get_edge_terminal_reference_primitive()
                elif self.terminal_type == self._pedb.edb_api.cell.terminal.TerminalType.PinGroupTerminal:
                    self._reference_object = self.get_pin_group_terminal_reference_pin()
                elif self.terminal_type == self._pedb.edb_api.cell.terminal.TerminalType.PointTerminal:
                    self._reference_object = self.get_point_terminal_reference_primitive()
                elif self.terminal_type == self._pedb.edb_api.cell.terminal.TerminalType.PadstackInstanceTerminal:
                    self._reference_object = self.get_padstack_terminal_reference_pin()
                else:
                    self._pedb.logger.warning(
                        "Invalid Terminal Type={}".format(term.GetTerminalType())
                    )  # pragma: no cover
            except:
                pass
        return self._reference_object

    @property
    def reference_net_name(self):
        """Net name to which reference_object belongs."""
        try:
            ref_obj = self._reference_object if self._reference_object else self.reference_object
            if ref_obj:
                return ref_obj.net_name
        except:
            pass
        return ""

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

        if self._edb_object.GetIsCircuitPort():
            return self.get_pin_group_terminal_reference_pin()
        _, padStackInstance, layer = self._edb_object.GetParameters()

        # Get the pastack instance of the terminal
        compInst = self._edb_object.GetComponent()
        pins = self._pedb.components.get_pin_from_component(compInst.GetName())
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

        refTerm = self._edb_object.GetReferenceTerminal()
        if self._edb_object.GetTerminalType() == self._pedb.edb_api.cell.terminal.TerminalType.PinGroupTerminal:
            padStackInstance = self._edb_object.GetPinGroup().GetPins()[0]
            pingroup = refTerm.GetPinGroup()
            refPinList = pingroup.GetPins()
            return self._get_closest_pin(padStackInstance, refPinList, gnd_net_name_preference)
        elif (
            self._edb_object.GetTerminalType()
            == self._pedb.edb_api.cell.terminal.TerminalType.PadstackInstanceTerminal
        ):
            _, padStackInstance, layer = self._edb_object.GetParameters()
            if refTerm.GetTerminalType() == self._pedb.edb_api.cell.terminal.TerminalType.PinGroupTerminal:
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

        ref_layer = self._edb_object.GetReferenceLayer()
        edges = self._edb_object.GetEdges()
        _, prim_value, point_data = edges[0].GetParameters()
        X = point_data.X
        Y = point_data.Y
        shape_pd = self._pedb.edb_api.geometry.point_data(X, Y)
        layer_name = ref_layer.GetName()
        for primitive in self._pedb.layout.primitives:
            if primitive.GetLayer().GetName() == layer_name or not layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if prim_shape_data.PointInPolygon(shape_pd):
                    return cast(primitive, self._pedb)
        return None  # pragma: no cover

    @pyaedt_function_handler()
    def get_point_terminal_reference_primitive(self):
        """Find and return the primitive reference for the point terminal or the padstack instance.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance` or
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """

        ref_term = self._edb_object.GetReferenceTerminal()  # return value is type terminal
        _, point_data, layer = ref_term.GetParameters()
        X = point_data.X
        Y = point_data.Y
        shape_pd = self._pedb.edb_api.geometry.point_data(X, Y)
        layer_name = layer.GetName()
        for primitive in self._pedb.layout.primitives:
            if primitive.GetLayer().GetName() == layer_name:
                prim_shape_data = primitive.GetPolygonData()
                if prim_shape_data.PointInPolygon(shape_pd):
                    return cast(primitive, self._pedb)
        for vias in self._pedb.padstacks.instances.values():
            if layer_name in vias.layer_range_names:
                plane = self._pedb.modeler.Shape(
                    "rectangle", pointA=vias.position, pointB=vias.padstack_definition.bounding_box[1]
                )
                rectangle_data = vias._pedb.modeler.shape_to_polygon_data(plane)
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
        comp_inst = self._edb_object.GetComponent()
        pins = self._pedb.components.get_pin_from_component(comp_inst.GetName())
        try:
            edges = self._edb_object.GetEdges()
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
            power_ground_net_names = [net for net in self._pedb.nets.power_nets.keys()]
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


class ExcitationPorts(Terminal):
    """Manages excitation properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from EDB.


    Examples
    --------
    This example shows how to access the ``ExcitationPorts`` class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> exc = edb.excitations
    >>> print(exc["Port1"].name)
    """

    def __init__(self, pedb, edb_terminal):
        Terminal.__init__(self, pedb, edb_terminal)

    @property
    def _edb_properties(self):
        p = self._edb_object.GetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS")
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self._edb_object.SetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS", value)

    @property
    def hfss_type(self):
        """HFSS port type."""
        temp = re.search(r"'HFSS Type'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return txt.split("=")[1].replace("'", "")
        else:  # pragma: no cover
            return None

    @property
    def horizontal_extent_factor(self):
        """Horizontal extent factor."""
        temp = re.search(r"'Horizontal Extent Factor'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return float(txt.split("=")[1].replace("'", ""))
        else:  # pragma: no cover
            return None

    @horizontal_extent_factor.setter
    def horizontal_extent_factor(self, value):
        new_arg = r"'Horizontal Extent Factor'='{}'".format(value)
        if self.horizontal_extent_factor:
            p = re.sub(r"'Horizontal Extent Factor'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def vertical_extent_factor(self):
        """Vertical extent factor."""
        temp = re.search(r"'Vertical Extent Factor'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return float(txt.split("=")[1].replace("'", ""))
        return None  # pragma: no cover

    @vertical_extent_factor.setter
    def vertical_extent_factor(self, value):
        new_arg = r"'Vertical Extent Factor'='{}'".format(value)
        if self.vertical_extent_factor:
            p = re.sub(r"'Vertical Extent Factor'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def radial_extent_factor(self):
        """Radial extent factor."""
        temp = re.search(r"'Radial Extent Factor'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return float(txt.split("=")[1].replace("'", ""))
        return None  # pragma: no cover

    @radial_extent_factor.setter
    def radial_extent_factor(self, value):
        new_arg = r"'Radial Extent Factor'='{}'".format(value)
        if self.radial_extent_factor:
            p = re.sub(r"'Radial Extent Factor'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def pec_launch_width(self):
        """Launch width for the printed electronic component (PEC)."""
        temp = re.search(r"'PEC Launch Width'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return txt.split("=")[1].replace("'", "")
        else:  # pragma: no cover
            return None

    @pec_launch_width.setter
    def pec_launch_width(self, value):
        new_arg = r"'PEC Launch Width'='{}'".format(value)
        if self.pec_launch_width:
            p = re.sub(r"'PEC Launch Width'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def impedance(self):
        """Impedance of the port."""
        return self._edb_object.GetImpedance().ToDouble()

    @property
    def is_circuit(self):
        """Whether it is a circuit port."""
        return self._edb_object.GetIsCircuitPort()

    @property
    def magnitude(self):
        """Magnitude."""
        return self._edb_object.GetSourceAmplitude().ToDouble()

    @property
    def phase(self):
        """Phase."""
        return self._edb_object.GetSourcePhase().ToDouble()

    @property
    def renormalize(self):
        """Whether renormalize is active."""
        return self._edb_object.GetPortPostProcessingProp().DoRenormalize

    @property
    def deembed(self):
        """Whether deembed is active."""
        return self._edb_object.GetPortPostProcessingProp().DoDeembed

    @property
    def deembed_gapport_inductance(self):
        """Inductance value of the deembed gap port."""
        return self._edb_object.GetPortPostProcessingProp().DoDeembedGapL

    @property
    def deembed_length(self):
        """Deembed Length."""
        return self._edb_object.GetPortPostProcessingProp().DeembedLength.ToDouble()

    @property
    def renormalize_z0(self):
        """Renormalize Z0 value (real, imag)."""
        return (
            self._edb_object.GetPortPostProcessingProp().RenormalizionZ0.ToComplex().Item1,
            self._edb_object.GetPortPostProcessingProp().RenormalizionZ0.ToComplex().Item2,
        )


class ExcitationSources(Terminal):
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
        Terminal.__init__(self, pedb, edb_terminal)

    @property
    def magnitude(self):
        """Get the magnitude of the source."""
        return self._edb_object.GetSourceAmplitude().ToDouble()

    @magnitude.setter
    def magnitude(self, value):
        self._edb_object.SetSourceAmplitude(self._edb.utility.value(value))

    @property
    def phase(self):
        """Get the phase of the source."""
        return self._edb_object.GetSourcePhase().ToDouble()

    @phase.setter
    def phase(self, value):
        self._edb_object.SetSourcePhase(self._edb.utility.value(value))


class ExcitationProbes(Terminal):
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
        Terminal.__init__(self, pedb, edb_terminal)


class ExcitationBundle:
    """Manages multi terminal excitation properties."""

    def __init__(self, pedb, edb_bundle_terminal):
        self._pedb = pedb
        self._edb_bundle_terminal = edb_bundle_terminal

    @property
    def name(self):
        """Port Name."""
        return self._edb_bundle_terminal.GetName()

    @property
    def edb(self):  # pragma: no cover
        """Get edb."""
        return self._pedb.edb_api

    @property
    def terminals(self):
        """Get terminals belonging to this excitation."""
        return {i.GetName(): ExcitationPorts(self._pedb, i) for i in list(self._edb_bundle_terminal.GetTerminals())}

    @property
    def reference_net_name(self):
        """Reference Name. Not applicable to Differential pairs."""
        return


class ExcitationDifferential(ExcitationBundle):
    """Manages differential excitation properties."""

    def __init__(self, pedb, edb_boundle_terminal):
        ExcitationBundle.__init__(self, pedb, edb_boundle_terminal)

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
             Name of the net.
        """
        return self._edb_bundle_terminal.GetNet().GetName()

    @property
    def net(self):
        """Net object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`
        """
        return EDBNetsData(self._edb_bundle_terminal.GetNet(), self._pedb)
