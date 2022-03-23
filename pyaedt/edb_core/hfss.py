"""
This module contains the `EdbHfss` class.
"""
from pyaedt.edb_core.general import convert_netdict_to_pydict
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler


class EdbHfss(object):
    """Manages EDB functionalities for 3D layouts.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edb_hfss = edb_3dedbapp.core_hfss
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def _hfss_terminals(self):
        return self._pedb.edblib.HFSS3DLayout.HFSSTerminalMethods

    @property
    def _hfss_ic_methods(self):
        return self._pedb.edblib.HFSS3DLayout.ICMethods

    @property
    def _hfss_setup(self):
        return self._pedb.edblib.HFSS3DLayout.HFSSSetup

    @property
    def _hfss_mesh_setup(self):
        return self._pedb.edblib.HFSS3DLayout.Meshing

    @property
    def _sweep_methods(self):
        return self._pedb.edblib.SimulationSetup.SweepMethods

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def _edb(self):
        return self._pedb.edb

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _cell(self):
        return self._pedb.cell

    @property
    def _db(self):
        return self._pedb.db

    @property
    def _builder(self):
        return self._pedb.builder

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    @pyaedt_function_handler()
    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------
        dict
            Dictionary of trace width data.
        """
        mesh = self._hfss_mesh_setup.GetMeshOperation(self._active_layout)
        if mesh.Item1:
            return convert_netdict_to_pydict(mesh.Item2)
        else:
            return {}

    @pyaedt_function_handler()
    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create Circuit Port on Pin.

        Parameters
        ----------
        pos_pin : Object
            Edb Pin
        neg_pin : Object
            Edb Pin
        impedance : float
            Port Impedance
        port_name : str, optional
            Port Name

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_circuit_port_on_pin(pins[0], pins[1],50,"port_name")

        Returns
        -------
        str
            Port Name.

        """
        return self._pedb.core_siwave.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    @pyaedt_function_handler()
    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_voltage_source_on_pin(pins[0], pins[1],50,"source_name")
        """
        return self._pedb.core_siwave.create_voltage_source_on_pin(
            pos_pin, neg_pin, voltage_value, phase_value, source_name
        )

    @pyaedt_function_handler()
    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_current_source_on_pin(pins[0], pins[1],50,"source_name")
        """

        return self._pedb.core_siwave.create_current_source_on_pin(
            pos_pin, neg_pin, current_value, phase_value, source_name
        )

    @pyaedt_function_handler()
    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            Name of the Resistor.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        return self._pedb.core_siwave.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    @pyaedt_function_handler()
    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        impedance_value=50,
        port_name="",
    ):
        """Create a circuit port on a NET.
        It groups all pins belonging to the specified net and then applies the port on PinGroups.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``"GND"``.
        impedance_value : float, optional
            Port impedance value. The default is ``50``.
        port_name : str, optional
            Name of the port. The default is ``""``.

        Returns
        -------
        str
            Port Name

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_hfss.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        return self._pedb.core_siwave.create_circuit_port_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            impedance_value,
            port_name,
        )

    @pyaedt_function_handler()
    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        voltage_value=3.3,
        phase_value=0,
        source_name="",
    ):
        """Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net. The default is ``"GND"``.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_hfss.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")
        """
        return self._pedb.core_siwave.create_voltage_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            voltage_value,
            phase_value,
            source_name,
        )

    @pyaedt_function_handler()
    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        current_value=0.1,
        phase_value=0,
        source_name="",
    ):
        """Create a current source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net. The default is ``"GND"``.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_hfss.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")
        """
        return self._pedb.core_siwave.create_current_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            current_value,
            phase_value,
            source_name,
        )

    @pyaedt_function_handler()
    def create_resistor_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        rvalue=1,
        resistor_name="",
    ):
        """Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net. The default is ``"GND"``.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            Resistor Name

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_hfss.create_resistor_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 1, "resistor_name")
        """
        return self._pedb.core_siwave.create_resistor_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            rvalue,
            resistor_name,
        )

    @pyaedt_function_handler()
    def create_coax_port_on_component(self, ref_des_list, net_list):
        """Create a coaxial port on a component or component list on a net or net list.

        .. note::
           The name of the new coaxial port is automatically assigned.

        Parameters
        ----------
        ref_des_list : list, str
            List of one or more reference designators.

        net_list : list, str
            List of one or more nets.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        coax = []
        if not isinstance(ref_des_list, list):
            ref_des_list = [ref_des_list]
        if not isinstance(net_list, list):
            net_list = [net_list]
        for ref in ref_des_list:
            for pinname, pin in self._pedb.core_components.components[ref].pins.items():
                if pin.net_name in net_list and pin.pin.IsLayoutPin():
                    port_name = "{}_{}_{}".format(ref, pin.net_name, pin.pin.GetName())
                    if is_ironpython:
                        res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange()  # pragma: no cover
                    else:
                        res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange(None, None)
                    if self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
                        self._active_layout, pin.pin.GetNet(), port_name, pin.pin, toLayer_pos
                    ):
                        coax.append(port_name)
        return coax

    @pyaedt_function_handler()
    def create_hfss_ports_on_padstack(self, pinpos, portname=None):
        """Create a HFSS port on a padstack.

        Parameters
        ----------
        pinpos :
            Position of the pin.

        portname : str, optional
             Name of the port. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if is_ironpython:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange()
        else:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange(None, None)
        if not portname:
            portname = generate_unique_name("Port_" + pinpos.GetNet().GetName())
        edbpointTerm_pos = self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
            self._active_layout, pinpos.GetNet(), portname, pinpos, toLayer_pos
        )
        if edbpointTerm_pos:
            return True
        else:
            return False

    @pyaedt_function_handler()
    def create_lumped_port_on_trace(
        self,
        nets=None,
        reference_layer=None,
        return_points_only=False,
        polygon_trace_threshhold=300e-6,
        digit_resolution=6,
        point_list=None,
    ):
        """Create an edge port on traces.

        Parameters
        ----------
        nets : list, optional
            List of nets, str or Edb net.

        reference_layer : str, Edb layer.
             Name or Edb layer object.

        return_points_only : bool, optional
            Use this boolean when you want to return only the points from the edges and not creating ports. Default
            value is ``False``.

        polygon_trace_threshhold : float, optional
            Used only when selected nets are routed as polygon. The value gives the algorithm the threshold
            of the polygon width at the design border for considering placing an edge port. The default value is
            ``300-e6``.

        digit_resolution : int, optional
            The number of digits carried for the edge location accuracy. The default value is ``6``.

        point_list : list(tuples), optional
            The list of points where to define ports. The port evaluation is done for each net provided and if a point
            belongs to a center line points from a path or a polygon then the port will be created. If the point is not
            found the ports  will be skipped. If point_list is None, the algorithm will try to find the edges from
            traces or polygons touching the layout bounding box.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = [self._edb.Cell.Net.FindByName(self._active_layout, nets)]
            elif isinstance(nets, self._edb.Cell.Net):
                nets = [nets]
        else:
            temp_nets = []
            for nn in nets:
                if isinstance(nn, str):
                    temp_nets.append(self._edb.Cell.Net.FindByName(self._active_layout, nn))
                elif isinstance(nn, self._edb.Cell.Net):
                    temp_nets.append(nn)
            nets = temp_nets
        if point_list:
            if isinstance(point_list, tuple):
                point_list = [point_list]
        edges_pts = []
        if nets:
            if isinstance(reference_layer, str):
                try:
                    reference_layer = self._pedb.core_stackup.signal_layers[reference_layer]._layer
                except:
                    raise Exception("Failed to get the layer {}".format(reference_layer))
            if not isinstance(reference_layer, self._edb.Cell.ILayerReadOnly):
                return False
            layout = nets[0].GetLayout()
            layout_bbox = self.get_layout_bounding_box(layout, digit_resolution)
            for net in nets:
                net_primitives = list(net.Primitives)
                net_paths = [
                    pp for pp in net_primitives if pp.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Path
                ]
                net_poly = [
                    pp
                    for pp in net_primitives
                    if pp.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Polygon
                ]
                for path in net_paths:
                    trace_path_pts = list(path.GetCenterLine().Points)
                    port_name = "{}_{}".format(net.GetName(), path.GetId())
                    if point_list:
                        for _pt in point_list:
                            if isinstance(_pt, tuple):
                                found_pt = [
                                    p
                                    for p in trace_path_pts
                                    if round(p.X.ToDouble(), 6) == round(_pt[0], 6)
                                    and round(p.Y.ToDouble(), 6) == round(_pt[1], 6)
                                ]
                                if found_pt:
                                    pt = self._edb.Geometry.PointData(
                                        self._get_edb_value(_pt[0]), self._get_edb_value(_pt[1])
                                    )
                                    if not self._hfss_terminals.CreateEdgePort(path, pt, reference_layer, port_name):
                                        raise Exception(
                                            "edge port creation failed on point {}, {}".format(
                                                str(pt.X.ToDouble()), str(pt.Y.ToDouble())
                                            )
                                        )
                    else:
                        for pt in trace_path_pts:
                            _pt = [round(pt.X.ToDouble(), digit_resolution), round(pt.Y.ToDouble(), digit_resolution)]
                            if bool(set(_pt) & set(layout_bbox)):
                                if return_points_only:
                                    edges_pts.append(_pt)
                                else:
                                    if not self._hfss_terminals.CreateEdgePort(
                                        path, pt, reference_layer, port_name
                                    ):  # pragma: no cover
                                        raise Exception(
                                            "edge port creation failed on point {}, {}".format(str(pt[0]), str(_pt[1]))
                                        )
                for poly in net_poly:
                    pt_list = list(poly.GetPolygonData().Points)
                    points_at_border = [
                        pt
                        for pt in pt_list
                        if round(pt.X.ToDouble(), digit_resolution) in layout_bbox
                        or round(pt.Y.ToDouble(), digit_resolution) in layout_bbox
                    ]
                    pt_at_left = [
                        pt for pt in points_at_border if round(pt.X.ToDouble(), digit_resolution) == layout_bbox[0]
                    ]
                    pt_at_left_values = [pt.Y.ToDouble() for pt in pt_at_left]
                    if pt_at_left_values:
                        left_edge_length = abs(max(pt_at_left_values) - min(pt_at_left_values))
                        if polygon_trace_threshhold >= left_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt_at_left)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly, convert_py_list_to_net_list(pt_at_left), reference_layer, port_name
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))

                    pt_at_bottom = [
                        pt for pt in points_at_border if round(pt.Y.ToDouble(), digit_resolution) == layout_bbox[1]
                    ]
                    pt_at_bottom_values = [pt.X.ToDouble() for pt in pt_at_bottom]
                    if pt_at_bottom_values:
                        bot_edge_length = abs(max(pt_at_bottom_values) - min(pt_at_bottom_values))
                        if polygon_trace_threshhold >= bot_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt_at_bottom)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly, convert_py_list_to_net_list(pt_at_bottom), reference_layer, port_name
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))

                    pt_at_right = [
                        pt for pt in points_at_border if round(pt.X.ToDouble(), digit_resolution) == layout_bbox[2]
                    ]
                    pt_at_right_values = [pt.Y.ToDouble() for pt in pt_at_right]
                    if pt_at_right_values:
                        right_edge_length = abs(max(pt_at_right_values) - min(pt_at_right_values))
                        if polygon_trace_threshhold >= right_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt_at_right)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly, convert_py_list_to_net_list(pt_at_right), reference_layer, port_name
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))

                    pt_at_top = [
                        pt for pt in points_at_border if round(pt.Y.ToDouble(), digit_resolution) == layout_bbox[3]
                    ]
                    pt_at_top_values = [pt.X.ToDouble() for pt in pt_at_top]
                    if pt_at_top_values:
                        top_edge_length = abs(max(pt_at_top_values) - min(pt_at_top_values))
                        if polygon_trace_threshhold >= top_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt - pt_at_top)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly, convert_py_list_to_net_list(pt_at_top), reference_layer, port_name
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))
            if return_points_only:
                return edges_pts
        return True

    @pyaedt_function_handler()
    def get_layout_bounding_box(self, layout=None, digit_resolution=6):
        """Evaluate the layout bounding box.

        Parameters
        ----------
        layout :
            Edb layout.

        digit_resolution : int, optional
            Digit Resolution. The default value is ``6``.
        Returns
        -------
        list
            [lower left corner X, lower left corner, upper right corner X, upper right corner Y]
        """
        if layout == None:
            return False
        layout_obj_instances = layout.GetLayoutInstance().GetAllLayoutObjInstances()
        tuple_list = []
        for lobj in layout_obj_instances.Items:
            lobj_bbox = lobj.GetLayoutInstanceContext().GetBBox(False)
            tuple_list.append(lobj_bbox)
        _bbox = self._edb.Geometry.PolygonData.GetBBoxOfBoxes(convert_py_list_to_net_list(tuple_list))
        layout_bbox = [
            round(_bbox.Item1.X.ToDouble(), digit_resolution),
            round(_bbox.Item1.Y.ToDouble(), digit_resolution),
            round(_bbox.Item2.X.ToDouble(), digit_resolution),
            round(_bbox.Item2.Y.ToDouble(), digit_resolution),
        ]
        return layout_bbox
