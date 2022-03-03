"""
This module contains these clases: `CircuitPort`, `CurrentSource`, `EdbSiwave`,
`PinGroup`, `ResistorSource`, `Source`, `SourceType`, and `VoltageSource`.
"""
import os
import time
import warnings

from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler

try:
    from System import String
    from System.Collections.Generic import Dictionary
except ImportError:
    if os.name != "posix":
        warnings.warn("This module requires pythonnet.")


class SiwaveDCSetupTemplate(object):
    """Siwave DC Settings Data Class.

    This class contains all the settings for a Siwave DC Analysis and
    is used as input

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb  = Edb("pathtoaedb", edbversion="2021.2")
    >>> settings = edb.core_siwave.get_siwave_dc_setup_template()
    >>> settings.accuracy_level = 0
    >>> settings.use_dc_custom_settings  = True
    >>> settings.name = "myDCIR_3"
    >>> settings.pos_term_to_ground = "I1"
    >>> settings.neg_term_to_ground = "V1"
    >>> edb.core_siwave.add_siwave_dc_analysis(settings)
    """

    def __init__(self):
        self.name = "DC IR 1"
        self.dcreport_show_active_devices = True
        self.export_dcthermal_data = False
        self.full_dcreport_path = ""
        self.use_loopres_forperpin = True
        self.via_report_path = ""
        self.compute_inductance = True
        self.accuracy_level = 1
        self.plotjv = True
        self.min_passes = 1
        self.max_passes = 5
        self.percent_localrefinement = 20
        self.energy_error = 2
        self.refine_bondwires = False
        self.refine_vias = False
        self.num_bondwire_sides = 8
        self.num_via_sides = 8
        self.mesh_bondwires = False
        self.mesh_vias = False
        self.perform_adaptive_refinement = False
        self.use_dc_custom_settings = False
        self._source_terms_to_ground = None
        self._pos_term_to_ground = []
        self._neg_term_to_ground = []

    @property
    def pos_term_to_ground(self):
        """Set positive terminals to ground.

        Parameters
        ----------
        terms : list, str
            List of terminals with positive nodes to ground.
        """
        return self._pos_term_to_ground

    @pos_term_to_ground.setter
    def pos_term_to_ground(self, terms):
        if not isinstance(terms, list):
            self._pos_term_to_ground = [terms]
        else:
            self._pos_term_to_ground = terms

    @property
    def neg_term_to_ground(self):
        """Set negative terminals to ground.

        Parameters
        ----------
        terms : list, str
            List of terminals with negative nodes to ground.
        """
        return self._neg_term_to_ground

    @neg_term_to_ground.setter
    def neg_term_to_ground(self, terms):
        if not isinstance(terms, list):
            self._neg_term_to_ground = [terms]
        else:
            self._neg_term_to_ground = terms

    @property
    def source_terms_to_ground(self):
        """Terminals with positive or negative grounded terminals."""
        a = Dictionary[String, int]()
        for el in self._neg_term_to_ground:
            a[el] = 1
        for el in self._pos_term_to_ground:
            a[el] = 2
        self._source_terms_to_ground = a
        return self._source_terms_to_ground


class SourceType(object):
    """Manages source types."""

    (Port, CurrentSource, VoltageSource, Resistor) = (1, 2, 3, 4)


class PinGroup(object):
    """Manages pin groups."""

    def __init__(self):
        self._name = ""
        self._component = ""
        self._node_pins = []
        self._net = ""

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


class Source(object):
    """Manages sources."""

    def __init__(self):
        self._name = ""
        self._type = SourceType.Port
        self._positive_node = PinGroup()
        self._negative_node = PinGroup()
        self._do_pin_grouping = True

    @property
    def name(self):
        """Name."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self):
        """Type."""
        return self._type

    @type.setter
    def type(self, value):
        self.type = value

    @property
    def positive_node(self):
        """Positive node."""
        return self._positive_node

    @positive_node.setter
    def positive_node(self, value):
        self._positive_node = value

    @property
    def negative_node(self):
        """Negative node."""
        return self._negative_node

    @negative_node.setter
    def negative_node(self, value):
        self._negative_node = value

    @property
    def do_pin_grouping(self):
        """Do pin groupings."""
        return self._do_pin_grouping

    @do_pin_grouping.setter
    def do_pin_grouping(self, value):
        self._do_pin_grouping = value


class CircuitPort(Source):
    """Manages a circuit port."""

    def __init(self):
        super(CircuitPort, self).__init__()
        self._impedance = "50"
        self._type = SourceType.Port

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
        return self.type


class VoltageSource(Source):
    """Manages a voltage source."""

    def __init__(self):
        super(VoltageSource, self).__init__()
        self._magnitude = "1V"
        self._phase = "0Deg"
        self._impedance = "0.05"
        self._type = SourceType.VoltageSource

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
        return self.source_type


class CurrentSource(Source):
    """Manages a current source."""

    def __init__(self):
        super(CurrentSource, self).__init__()
        self._magnitude = "0.1A"
        self._phase = "0Deg"
        self._impedance = "1e7"
        self._type = SourceType.CurrentSource

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
        return self.source_type


class ResistorSource(Source):
    """Manages a resistor source."""

    def __init__(self):
        super(ResistorSource, self).__init__()
        self._rvalue = "50"
        self._type = SourceType.Resistor

    @property
    def rvalue(self):
        """Resistance value."""
        return self._rvalue

    @rvalue.setter
    def rvalue(self, value):
        self._rv = value

    @property
    def source_type(self):
        """Source type."""
        return self.source_type


class EdbSiwave(object):
    """Manages EDB functionalities for SIwave.

    Parameters
    ----------
    edb_class : :class:`pyaedt.edb.Edb`
        Inherited parent object.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_siwave = edbapp.core_siwave
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def _siwave_source(self):
        """SIwave source."""
        return self._pedb.edblib.SIwave.SiwaveSourceMethods

    @property
    def _siwave_setup(self):
        """SIwave setup."""
        return self._pedb.edblib.SIwave.SiwaveSimulationSetupMethods

    @property
    def _builder(self):
        """Builder."""
        return self._pedb.builder

    @property
    def _edb(self):
        """EDB."""
        return self._pedb.edb

    @property
    def _edb_value(self):
        """EDB."""
        return self._pedb.edb_value

    @property
    def _logger(self):
        """EDB."""
        return self._pedb.logger

    @property
    def _active_layout(self):
        """Active layout."""
        return self._pedb.active_layout

    @property
    def _cell(self):
        """Cell."""
        return self._pedb.active_cell

    @property
    def _db(self):
        """ """
        return self._pedb.db

    @pyaedt_function_handler()
    def _create_terminal_on_pins(self, source):
        """Create a terminal on pins.

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource or ResistorSource
            Name of the source.

        """
        pos_pin = source.positive_node.node_pins
        neg_pin = source.negative_node.node_pins

        if is_ironpython:
            res, fromLayer_pos, toLayer_pos = pos_pin.GetLayerRange()
            res, fromLayer_neg, toLayer_neg = neg_pin.GetLayerRange()
        else:
            res, fromLayer_pos, toLayer_pos = source.positive_node.node_pins.GetLayerRange(None, None)
            res, fromLayer_neg, toLayer_neg = source.negative_node.node_pins.GetLayerRange(None, None)
        pos_pingroup_terminal = _retry_ntimes(
            10,
            self._edb.Cell.Terminal.PadstackInstanceTerminal.Create,
            self._active_layout,
            pos_pin.GetNet(),
            pos_pin.GetName(),
            pos_pin,
            toLayer_pos,
        )
        time.sleep(0.5)
        neg_pingroup_terminal = _retry_ntimes(
            20,
            self._edb.Cell.Terminal.PadstackInstanceTerminal.Create,
            self._active_layout,
            neg_pin.GetNet(),
            neg_pin.GetName(),
            neg_pin,
            toLayer_neg,
        )
        if source.type == SourceType.Port:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.impedance))
            pos_pingroup_terminal.SetIsCircuitPort(True)
            neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)
        elif source.type == SourceType.CurrentSource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except Exception as e:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.type == SourceType.VoltageSource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.type == SourceType.Resistor:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.rvalue))
            Rlc = self._edb.Utility.Rlc()
            Rlc.CEnabled = False
            Rlc.LEnabled = False
            Rlc.REnabled = True
            Rlc.R = self._edb_value(source.rvalue)
            pos_pingroup_terminal.SetRlcBoundaryParameters(Rlc)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)
        else:
            pass
        return pos_pingroup_terminal.GetName()

    @pyaedt_function_handler()
    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create a circuit port on a pin.

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
        >>> pins = edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_siwave.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")

        Returns
        -------
        str
            Port Name.

        """
        circuit_port = CircuitPort()
        circuit_port.positive_node.net = pos_pin.GetNet().GetName()
        circuit_port.negative_node.net = neg_pin.GetNet().GetName()
        circuit_port.impedance = impedance

        if not port_name:
            port_name = "Port_{}_{}_{}_{}".format(
                pos_pin.GetComponent().GetName(),
                pos_pin.GetNet().GetName(),
                neg_pin.GetComponent().GetName(),
                neg_pin.GetNet().GetName(),
            )
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_pin.GetComponent()
        circuit_port.positive_node.node_pins = pos_pin
        circuit_port.negative_node.component_node = neg_pin.GetComponent()
        circuit_port.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(circuit_port)

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
        >>> pins = edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_siwave.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")
        """

        voltage_source = VoltageSource()
        voltage_source.positive_node.net = pos_pin.GetNet().GetName()
        voltage_source.negative_node.net = neg_pin.GetNet().GetName()
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        if not source_name:
            source_name = "VSource_{}_{}_{}_{}".format(
                pos_pin.GetComponent().GetName(),
                pos_pin.GetNet().GetName(),
                neg_pin.GetComponent().GetName(),
                neg_pin.GetNet().GetName(),
            )
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_pin.GetComponent()
        voltage_source.positive_node.node_pins = pos_pin
        voltage_source.negative_node.component_node = neg_pin.GetComponent()
        voltage_source.negative_node.node_pins = pos_pin
        return self._create_terminal_on_pins(voltage_source)

    @pyaedt_function_handler()
    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        Parameters
        ----------
        pos_pin : Object
            Positive pin.
        neg_pin : Object
            Negative pin.
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
        >>> pins = edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_siwave.create_current_source_on_pin(pins[0], pins[1], 50, "source_name")
        """
        current_source = CurrentSource()
        current_source.positive_node.net = pos_pin.GetNet().GetName()
        current_source.negative_node.net = neg_pin.GetNet().GetName()
        current_source.magnitude = current_value
        current_source.phase = phase_value
        if not source_name:
            source_name = "ISource_{}_{}_{}_{}".format(
                pos_pin.GetComponent().GetName(),
                pos_pin.GetNet().GetName(),
                neg_pin.GetComponent().GetName(),
                neg_pin.GetNet().GetName(),
            )
        current_source.name = source_name
        current_source.positive_node.component_node = pos_pin.GetComponent()
        current_source.positive_node.node_pins = pos_pin
        current_source.negative_node.component_node = neg_pin.GetComponent()
        current_source.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(current_source)

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
            Name of the resistor.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_siwave.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        resistor = ResistorSource()
        resistor.positive_node.net = pos_pin.GetNet().GetName()
        resistor.negative_node.net = neg_pin.GetNet().GetName()
        resistor.magnitude = rvalue
        if not resistor_name:
            resistor_name = "Res_{}_{}_{}_{}".format(
                pos_pin.GetComponent().GetName(),
                pos_pin.GetNet().GetName(),
                neg_pin.GetComponent().GetName(),
                neg_pin.GetNet().GetName(),
            )
        resistor.name = resistor_name
        resistor.positive_node.component_node = pos_pin.GetComponent()
        resistor.positive_node.node_pins = pos_pin
        resistor.negative_node.component_node = neg_pin.GetComponent()
        resistor.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(resistor)

    @pyaedt_function_handler()
    def _check_gnd(self, component_name):
        negative_net_name = None
        if self._pedb.core_nets.is_net_in_component(component_name, "GND"):
            negative_net_name = "GND"
        elif self._pedb.core_nets.is_net_in_component(component_name, "PGND"):
            negative_net_name = "PGND"
        elif self._pedb.core_nets.is_net_in_component(component_name, "AGND"):
            negative_net_name = "AGND"
        elif self._pedb.core_nets.is_net_in_component(component_name, "DGND"):
            negative_net_name = "DGND"
        if not negative_net_name:
            raise ValueError("No GND, PGND, AGND, DGND found. Please setup the negative net name manually.")
        return negative_net_name

    @pyaedt_function_handler()
    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
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
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        impedance_value : float, optional
            Port impedance value. The default is ``50``.
        port_name : str, optional
            Name of the port. The default is ``""``.

        Returns
        -------
        str
            The name of the port.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_siwave.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        circuit_port = CircuitPort()
        circuit_port.positive_node.net = positive_net_name
        circuit_port.negative_node.net = negative_net_name
        circuit_port.impedance = impedance_value
        pos_node_cmp = self._pedb.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.core_components.get_pin_from_component(negative_component_name, negative_net_name)
        if port_name == "":
            port_name = "Port_{}_{}_{}_{}".format(
                positive_component_name, positive_net_name, negative_component_name, negative_net_name
            )
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_node_cmp
        circuit_port.positive_node.node_pins = pos_node_pins
        circuit_port.negative_node.component_node = neg_node_cmp
        circuit_port.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(circuit_port)

    @pyaedt_function_handler()
    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
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
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_siwave.create_voltage_source_on_net("U2A5","V1P5_S3","U2A5","GND",3.3,0,"source_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        voltage_source = VoltageSource()
        voltage_source.positive_node.net = positive_net_name
        voltage_source.negative_node.net = negative_net_name
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        pos_node_cmp = self._pedb.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.core_components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Vsource_{}_{}_{}_{}".format(
                positive_component_name, positive_net_name, negative_component_name, negative_net_name
            )
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_node_cmp
        voltage_source.positive_node.node_pins = pos_node_pins
        voltage_source.negative_node.component_node = neg_node_cmp
        voltage_source.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(voltage_source)

    @pyaedt_function_handler()
    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
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
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_siwave.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        current_source = CurrentSource()
        current_source.positive_node.net = positive_net_name
        current_source.negative_node.net = negative_net_name
        current_source.magnitude = current_value
        current_source.phase = phase_value
        pos_node_cmp = self._pedb.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.core_components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Port_{}_{}_{}_{}".format(
                positive_component_name, positive_net_name, negative_component_name, negative_net_name
            )
        current_source.name = source_name
        current_source.positive_node.component_node = pos_node_cmp
        current_source.positive_node.node_pins = pos_node_pins
        current_source.negative_node.component_node = neg_node_cmp
        current_source.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(current_source)

    @pyaedt_function_handler()
    def create_resistor_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
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
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            The name of the resistor.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_siwave.create_resistor_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 1, "resistor_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        resistor = ResistorSource()
        resistor.positive_node.net = positive_net_name
        resistor.negative_node.net = negative_net_name
        resistor.magnitude = rvalue
        pos_node_cmp = self._pedb.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.core_components.get_pin_from_component(negative_component_name, negative_net_name)

        if resistor_name == "":
            resistor_name = "Port_{}_{}_{}_{}".format(
                positive_component_name, positive_net_name, negative_component_name, negative_net_name
            )
        resistor.name = resistor_name
        resistor.positive_node.component_node = pos_node_cmp
        resistor.positive_node.node_pins = pos_node_pins
        resistor.negative_node.component_node = neg_node_cmp
        resistor.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(resistor)

    @pyaedt_function_handler()
    def create_exec_file(self):
        """Create an executable file."""
        workdir = os.path.dirname(self._pedb.edbpath)
        file_name = os.path.join(workdir, os.path.splitext(os.path.basename(self._pedb.edbpath))[0] + ".exec")
        if os.path.isfile(file_name):
            os.remove(file_name)
        f = open(file_name, "w")
        return f

    @pyaedt_function_handler()
    def add_siwave_ac_analysis(
        self,
        accuracy_level=1,
        decade_count=10,
        sweeptype=1,
        start_freq=1,
        stop_freq=1e9,
        step_freq=1e6,
        discrete_sweep=False,
    ):
        """Add a SIwave AC analysis to EDB.

        Parameters
        ----------
        accuracy_level : int, optional
           Level of accuracy. The default is ``1``.
        decade_count : int
            The default is ``10``.
        sweeptype : int, optional
            Type of the sweep. The default is ``1``.
        start_freq : float, optional
            Starting frequency. The default is ``1``.
        stop_freq : float, optional
            Stopping frequency. The default is ``1e9``.
        step_freq : float, optional
            Frequency size of the step. The default is ``1e6``.
        discrete_sweep : bool, optonal
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._siwave_setup.AddACSimSetup(
            self._cell,
            accuracy_level,
            str(decade_count),
            sweeptype,
            str(start_freq),
            str(stop_freq),
            str(step_freq),
            discrete_sweep,
        )
        exec_file = self.create_exec_file()
        exec_file.write("ExecAcSim\n")
        exec_file.close()
        return True

    @pyaedt_function_handler()
    def add_siwave_syz_analysis(
        self,
        accuracy_level=1,
        decade_count=10,
        sweeptype=1,
        start_freq=1,
        stop_freq=1e9,
        step_freq=1e6,
        discrete_sweep=False,
    ):
        """Add a SIwave SYZ analysis.

        Parameters
        ----------
        accuracy_level : int, optional
           Level of accuracy. The default is ``1``.
        decade_count : int, optional
            Number of points to calculate in each decade. The default is ``10``.
        sweeptype : int, optional
            Type of the sweep. The default is ``1``.
        start_freq : float, optional
            Starting frequency. The default is ``1``.
        stop_freq : float, optional
            Stopping frequency. The default is ``1e9``.
        step_freq : float, optional
            Frequency size of the step. The default is ``1e6``.
        discrete_sweep : bool, optonal
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        self._siwave_setup.AddSYZSimSetup(
            self._cell,
            accuracy_level,
            str(decade_count),
            sweeptype,
            str(start_freq),
            str(stop_freq),
            str(step_freq),
            discrete_sweep,
        )
        exec_file = self.create_exec_file()
        exec_file.write("ExecSyzSim\n")
        exec_file.write("SaveSiw\n")
        exec_file.close()
        return True

    @pyaedt_function_handler()
    def get_siwave_dc_setup_template(self):
        """Get the siwave dc template.

        Returns
        -------
        pyaedt.edb_core.siwave.SiwaveDCSetupTemplate
        """
        return SiwaveDCSetupTemplate()

    @pyaedt_function_handler()
    def add_siwave_dc_analysis(self, setup_settings=SiwaveDCSetupTemplate()):
        """Create a Siwave DC Analysis in EDB.

        If Setup is present it will be deleted and replaced by new
        actual settings.

        .. note::
           Source Reference to Ground settings works only from 2021.2

        Parameters
        ----------
        setup_settings : pyaedt.edb_core.siwave.SiwaveDCSetupTemplate

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb("pathtoaedb", edbversion="2021.2")
        >>> edb.core_siwave.add_siwave_ac_analysis()
        >>> settings = edb.core_siwave.get_siwave_dc_setup_template()
        >>> settings.accuracy_level = 0
        >>> settings.use_dc_custom_settings  = True
        >>> settings.name = "myDCIR_3"
        >>> settings.pos_term_to_ground = "I1"
        >>> settings.neg_term_to_ground = "V1"
        >>> edb.core_siwave.add_siwave_dc_analysis2(settings)

        """
        sim_setup_info = self._pedb.simsetupdata.SimSetupInfo[
            self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings
        ]()
        sim_setup_info.Name = setup_settings.name
        sim_setup_info.SimulationSettings.DCIRSettings.DCReportShowActiveDevices = (
            setup_settings.dcreport_show_active_devices
        )
        sim_setup_info.SimulationSettings.DCIRSettings.ExportDCThermalData = setup_settings.export_dcthermal_data
        sim_setup_info.SimulationSettings.DCIRSettings.FullDCReportPath = setup_settings.full_dcreport_path
        sim_setup_info.SimulationSettings.DCIRSettings.UseLoopResForPerPin = setup_settings.use_loopres_forperpin
        sim_setup_info.SimulationSettings.DCIRSettings.ViaReportPath = setup_settings.via_report_path
        sim_setup_info.SimulationSettings.DCSettings.ComputeInductance = setup_settings.compute_inductance
        sim_setup_info.SimulationSettings.DCSettings.DCSliderPos = setup_settings.accuracy_level
        sim_setup_info.SimulationSettings.DCSettings.PlotJV = setup_settings.plotjv
        sim_setup_info.SimulationSettings.DCAdvancedSettings.MinNumPasses = setup_settings.min_passes
        sim_setup_info.SimulationSettings.DCAdvancedSettings.MaxNumPasses = setup_settings.max_passes
        sim_setup_info.SimulationSettings.DCAdvancedSettings.PercentLocalRefinement = (
            setup_settings.percent_localrefinement
        )
        sim_setup_info.SimulationSettings.DCAdvancedSettings.EnergyError = setup_settings.energy_error
        sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineBws = setup_settings.refine_bondwires
        sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineVias = setup_settings.refine_vias
        sim_setup_info.SimulationSettings.DCAdvancedSettings.NumViaSides = setup_settings.num_via_sides
        sim_setup_info.SimulationSettings.DCAdvancedSettings.NumBwSides = setup_settings.num_bondwire_sides
        sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshBws = setup_settings.mesh_bondwires
        sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshVias = setup_settings.mesh_vias
        sim_setup_info.SimulationSettings.DCAdvancedSettings.PerformAdaptiveRefinement = (
            setup_settings.perform_adaptive_refinement
        )
        sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = setup_settings.use_dc_custom_settings
        sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = setup_settings.source_terms_to_ground
        simulationSetup = self._edb.Utility.SIWaveDCIRSimulationSetup(sim_setup_info)
        if self._cell.AddSimulationSetup(simulationSetup):
            exec_file = self.create_exec_file()
            exec_file.write("ExecDcSim\n")
            exec_file.close()
            return True
        else:
            self._cell.DeleteSimulationSetup(setup_settings.name)
            if self._cell.AddSimulationSetup(simulationSetup):
                exec_file = self.create_exec_file()
                exec_file.write("ExecDcSim\n")
                exec_file.close()
                return True
        return False

    @pyaedt_function_handler()
    def create_pin_group_terminal(self, source):
        """Create a pin group terminal.

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource, or ResistorSource
            Name of the source.

        """
        pos_pin_group = self._pedb.core_components.create_pingroup_from_pins(source.positive_node.node_pins)
        neg_pin_group = self._pedb.core_components.create_pingroup_from_pins(source.negative_node.node_pins)
        pos_node_net = self._pedb.core_nets.get_net_by_name(source.positive_node.net)
        neg_node_net = self._pedb.core_nets.get_net_by_name(source.negative_node.net)
        pos_pingroup_term_name = generate_unique_name(source.name + "_P_", n=3)
        neg_pingroup_term_name = generate_unique_name(source.name + "_N_", n=3)
        pos_pingroup_terminal = _retry_ntimes(
            10,
            self._edb.Cell.Terminal.PinGroupTerminal.Create,
            self._active_layout,
            pos_node_net,
            pos_pingroup_term_name,
            pos_pin_group[1],
            False,
        )
        time.sleep(0.5)
        neg_pingroup_terminal = _retry_ntimes(
            20,
            self._edb.Cell.Terminal.PinGroupTerminal.Create,
            self._active_layout,
            neg_node_net,
            neg_pingroup_term_name,
            neg_pin_group[1],
            False,
        )

        if source.type == SourceType.Port:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.impedance))
            pos_pingroup_terminal.SetIsCircuitPort(True)
            neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.type == SourceType.CurrentSource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb.Utility.Value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except Exception as e:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.type == SourceType.VoltageSource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.type == SourceType.Resistor:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb_value(source.rvalue))
            Rlc = self._edb.Utility.Rlc()
            Rlc.CEnabled = False
            Rlc.LEnabled = False
            Rlc.REnabled = True
            Rlc.R = self._edb_value(source.rvalue)
            pos_pingroup_terminal.SetRlcBoundaryParameters(Rlc)

        else:
            pass
        return pos_pingroup_terminal.GetName()
