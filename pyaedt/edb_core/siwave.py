"""
This module contains the ``EdbSiwave`` class.
"""

import warnings
import os
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name

try:
    import clr
    from System import Convert, String
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires pythonnet.')


class SourceType(object):
    (Port, CurrentSource, VoltageSource, Resistor) = (1, 2, 3, 4)


class PinGroup(object):

    def __init__(self):
        self._name = ""
        self._component = ""
        self._node_pins = []
        self._net = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def component(self):
        return self._component

    @component.setter
    def component(self, value):
        self._component = value

    @property
    def node_pins(self):
        return self._node_pins

    @node_pins.setter
    def node_pins(self, value):
        self._node_pins = value

    @property
    def net(self):
        return self._net

    @net.setter
    def net(self, value):
        self._net = value


class Source(object):

    def __init__(self):
        self._name = ""
        self._type = SourceType.Port
        self._positive_node = PinGroup()
        self._negative_node = PinGroup()
        self._do_pin_grouping = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,value):
        self._name = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self,value):
        self.type = value

    @property
    def positive_node(self):
        return self._positive_node

    @positive_node.setter
    def positive_node(self,value):
        self._positive_node = value

    @property
    def negative_node(self):
        return self._negative_node

    @negative_node.setter
    def negative_node(self,value):
        self._negative_node = value

    @property
    def do_pin_grouping(self):
        return self._do_pin_grouping

    @do_pin_grouping.setter
    def do_pin_grouping(self,value):
        self._do_pin_grouping = value


class CircuitPort(Source):
    def __init(self):
        super(CircuitPort, self).__init__()
        self._impedance = "50"
        self._type = SourceType.Port

    @property
    def impedance(self):
        return self._impedance

    @impedance.setter
    def impedance(self,value):
        self._impedance = value

    @property
    def get_type(self):
        return self.type


class VoltageSource(Source):
    def __init__(self):
        super(VoltageSource, self).__init__()
        self._magnitude = "1V"
        self._phase = "0Deg"
        self._impedance = "0.05"
        self._type = SourceType.VoltageSource

    @property
    def magnitude(self):
        return  self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self,value):
        self._phase = value

    @property
    def impedance(self):
        return self._impedance

    @impedance.setter
    def impedance(self,value):
        self._impedance = value

    @property
    def source_type(self):
        return self.source_type


class CurrentSource(Source):
    def __init__(self):
        super(CurrentSource, self).__init__()
        self._magnitude = "0.1A"
        self._phase = "0Deg"
        self._impedance = "1e7"
        self._type = SourceType.CurrentSource

    @property
    def magnitude(self):
        return  self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self,value):
        self._phase = value

    @property
    def impedance(self):
        return self._impedance

    @impedance.setter
    def impedance(self,value):
        self._impedance = value

    @property
    def source_type(self):
        return self.source_type


class ResistorSource(Source):
    def __init__(self):
        super(ResistorSource, self).__init__()
        self._rvalue = "50"
        self._type = SourceType.Resistor

    @property
    def rvalue(self):
        return  self._rvalue

    @rvalue.setter
    def rvalue(self, value):
        self._rv = value

    @property
    def source_type(self):
        return self.source_type


class EdbSiwave(object):
    """EdbSiwave class.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", "project name", "release version")
    >>> edbapp.core_siwave

    """

    def __init__(self, parent):
        self.parent = parent

    @property
    def _siwave_source(self):
        """ """
        return self.parent.edblib.SIwave.SiwaveSourceMethods

    @property
    def _siwave_setup(self):
        """ """
        return self.parent.edblib.SIwave.SiwaveSimulationSetupMethods

    @property
    def _builder(self):
        """ """
        return self.parent.builder

    @property
    def _edb(self):
        """ """
        return self.parent.edb

    @property
    def _active_layout(self):
        """ """
        return self.parent.active_layout

    @property
    def _cell(self):
        """ """
        return self.parent.cell

    @property
    def _db(self):
        """ """
        return self.parent.db


    @aedt_exception_handler
    def create_circuit_port(self, positive_component_name, positive_net_name, negative_component_name=None,
                              negative_net_name="GND", impedance_value=50, port_name=""):
        """
        Create a circuit port.
        
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
        port_name: str, optional
            Name of the port.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_siwave.create_circuit_port("U2A5","V1P5_S3","U2A5","GND",50,"port_name")
        """
        circuit_port = CircuitPort()
        circuit_port.positive_node.net = positive_net_name
        circuit_port.negative_node.net = negative_net_name
        circuit_port.impedance = impedance_value
        if not negative_component_name:
            negative_component_name = positive_component_name
        pos_node_cmp = self.parent.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self.parent.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self.parent.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self.parent.core_components.get_pin_from_component(negative_component_name, negative_net_name)


        if port_name == "":
            port_name = "Port_{}_{}_{}_{}".format(positive_component_name,positive_net_name,negative_component_name,negative_net_name)
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_node_cmp
        circuit_port.positive_node.node_pins = pos_node_pins
        circuit_port.negative_node.component_node = neg_node_cmp
        circuit_port.negative_node.node_pins = neg_node_pins
        self.create_pin_group_terminal(circuit_port)
        return True


    @aedt_exception_handler
    def create_voltage_source(self, positive_component_name, positive_net_name, negative_component_name=None,
                              negative_net_name="GND", voltage_value=3.3, phase_value=0,source_name=""):
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
        bool
            ``True`` when successful, ``False`` when failed.
            
        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_siwave.create_voltage_source("U2A5","V1P5_S3","U2A5","GND",3.3,0,"source_name")
        """
        voltage_source = VoltageSource()
        voltage_source.positive_node.net = positive_net_name
        voltage_source.negative_node.net = negative_net_name
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        pos_node_cmp = self.parent.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self.parent.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self.parent.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self.parent.core_components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Vsource_{}_{}_{}_{}".format(positive_component_name, positive_net_name, negative_component_name,
                                                  negative_net_name)
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_node_cmp
        voltage_source.positive_node.node_pins = pos_node_pins
        voltage_source.negative_node.component_node = neg_node_cmp
        voltage_source.negative_node.node_pins = neg_node_pins
        self.create_pin_group_terminal(voltage_source)
        return  True

    @aedt_exception_handler
    def create_current_source(self, positive_component_name, positive_net_name, negative_component_name=None,
                              negative_net_name="GND", current_value=0.1, phase_value=0, source_name=""):
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
        phase_value: optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_siwave.create_current_source("U2A5","V1P5_S3","U2A5","GND",0.1,0,"source_name")   
        """
        current_source = CurrentSource()
        current_source.positive_node.net = positive_net_name
        current_source.negative_node.net = negative_net_name
        current_source.magnitude = current_value
        current_source.phase = phase_value
        pos_node_cmp = self.parent.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self.parent.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self.parent.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self.parent.core_components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Port_{}_{}_{}_{}".format(positive_component_name, positive_net_name, negative_component_name,
                                                    negative_net_name)
        current_source.name = source_name
        current_source.positive_node.component_node = pos_node_cmp
        current_source.positive_node.node_pins = pos_node_pins
        current_source.negative_node.component_node = neg_node_cmp
        current_source.negative_node.node_pins = neg_node_pins
        self.create_pin_group_terminal(current_source)
        return True

    @aedt_exception_handler
    def create_resistor(self, positive_component_name, positive_net_name, negative_component_name=None,
                              negative_net_name="GND", rvalue=1, resistor_name=""):
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
            Value for the resistance. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        Examples
        --------
        
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_siwave.create_resistor("U2A5", "V1P5_S3", "U2A5", "GND", 1, "resistor_name")        
        """
        resistor = ResistorSource()
        resistor.positive_node.net = positive_net_name
        resistor.negative_node.net = negative_net_name
        resistor.magnitude = rvalue
        pos_node_cmp = self.parent.core_components.get_component_by_name(positive_component_name)
        neg_node_cmp = self.parent.core_components.get_component_by_name(negative_component_name)
        pos_node_pins = self.parent.core_components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self.parent.core_components.get_pin_from_component(negative_component_name, negative_net_name)

        if resistor_name == "":
            resistor_name = "Port_{}_{}_{}_{}".format(positive_component_name, positive_net_name, negative_component_name,
                                                    negative_net_name)
        resistor.name = resistor_name
        resistor.positive_node.component_node = pos_node_cmp
        resistor.positive_node.node_pins = pos_node_pins
        resistor.negative_node.component_node = neg_node_cmp
        resistor.negative_node.node_pins = neg_node_pins
        self.create_pin_group_terminal(resistor)
        return True

    @aedt_exception_handler
    def create_exec_file(self):
        workdir = os.path.dirname(self.parent.edbpath)
        file_name = os.path.join(workdir,os.path.splitext(os.path.basename(self.parent.edbpath))[0] + '.exec')
        if os.path.isfile(file_name):
            os.remove(file_name)
        f = open(file_name,"w")
        return f

    @aedt_exception_handler
    def add_siwave_ac_analysis(self, accuracy_level=1, decade_count=10, sweeptype=1, start_freq=1, stop_freq=1e9, step_freq=1e6, discrete_sweep=False):
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
            Stopping frequency. The default is ``1``.
        step_freq : float, optional
            Frequency size of the step. The default is ``1e9``.
        discrete_sweep: bool, optonal
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.  
        """
        self._siwave_setup.AddACSimSetup(self._builder, accuracy_level, str(decade_count), sweeptype, str(start_freq), str(stop_freq), str(step_freq), discrete_sweep)
        exec_file = self.create_exec_file()
        exec_file.write("ExecAcSim\n")
        exec_file.close()
        return True

    @aedt_exception_handler
    def add_siwave_syz_analysis(self, accuracy_level=1, decade_count=10, sweeptype=1, start_freq=1, stop_freq=1e9,
                               step_freq=1e6, discrete_sweep=False):
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
            Stopping frequency. The default is ``1``.
        step_freq : float, optional
            Frequency size of the step. The default is ``1e6``.
        discrete_sweep: bool, optonal
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.       
        """

        self._siwave_setup.AddSYZSimSetup(self._builder, accuracy_level, str(decade_count), sweeptype, str(start_freq),
                                        str(stop_freq), str(step_freq), discrete_sweep)
        exec_file = self.create_exec_file()
        exec_file.write("ExecSyzSim\n")
        exec_file.write("SaveSiw\n")
        exec_file.close()
        return True

    @aedt_exception_handler
    def add_siwave_dc_analysis(self, accuracy_level=1):
        """Add a SIwave DC analysis.

        Parameters
        ----------
        accuracy_level : int, optional
            Level of accuracy. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._siwave_setup.AddDCSimSetup(self._builder, accuracy_level)
        exec_file = self.create_exec_file()
        exec_file.write("ExecDcSim\n")
        exec_file.close()
        return True

    @aedt_exception_handler
    def create_pin_group_terminal(self, source):
        pos_pin_group = self.parent.core_components.create_pingroup_from_pins(source.positive_node.node_pins)
        neg_pin_group = self.parent.core_components.create_pingroup_from_pins(source.negative_node.node_pins)
        pos_node_net = self.parent.core_nets.get_net_by_name(source.positive_node.net)
        neg_node_net = self.parent.core_nets.get_net_by_name(source.negative_node.net)
        pos_pingroup_term_name = "{}_{}".format(source.positive_node.net,source.name)
        neg_pingroup_term_name = "{}_{}".format(source.negative_node.net,source.name)
        pos_pingroup_terminal = self._edb.Cell.Terminal.PinGroupTerminal.Create(self._active_layout,pos_node_net,pos_pingroup_term_name , pos_pin_group[1], False)
        neg_pingroup_terminal = self._edb.Cell.Terminal.PinGroupTerminal.Create(self._active_layout,neg_node_net,neg_pingroup_term_name , neg_pin_group[1], False)

        if source.type == SourceType.Port:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb.Utility.Value(source.impedance))
            pos_pingroup_terminal.SetIsCircuitPort(True)
            neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)

        elif source.type == SourceType.CurrentSource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kCurrentSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb.Utility.Value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb.Utility.Value(source.phase))
            pos_pingroup_terminal.SetIsCircuitPort(True)
            neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)

        elif source.type == SourceType.VoltageSource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.kVoltageSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb.Utility.Value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb.Utility.Value(source.phase))
            pos_pingroup_terminal.SetIsCircuitPort(True)
            neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)

        elif source.type == SourceType.Resistor:
            pos_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.RlcBoundary)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            pos_pingroup_terminal.SetSourceAmplitude(self._edb.Utility.Value(source.rvalue))
            pos_pingroup_terminal.SetIsCircuitPort(True)
            neg_pingroup_terminal.SetIsCircuitPort(True)
            Rlc = self._edb.Utility.Rlc()
            Rlc.CEnabled = False
            Rlc.LEnabled = False
            Rlc.REnabled = True
            Rlc.R = source.rvalue
            pos_pingroup_terminal.SetRlcBoundaryParameters(Rlc)

        else:
            pass
