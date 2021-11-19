"""
This module contains the `EdbHfss` class.
"""
from pyaedt.edb_core.general import convert_netdict_to_pydict
from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name, is_ironpython


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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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
                if pin.net in net_list and pin.pin.IsLayoutPin():
                    port_name = "{}_{}_{}".format(ref, pin.net, pin.pin.GetName())
                    if is_ironpython:
                        res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange()
                    else:
                        res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange(None, None)
                    if self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
                        self._active_layout, pin.pin.GetNet(), port_name, pin.pin, toLayer_pos
                    ):
                        coax.append(port_name)
        return coax

    @aedt_exception_handler
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
