"""
EdbSiwave Class
-------------------

This class manages Edb Siwave and related methods

Disclaimer
==========

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**



"""
import clr
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name
from System import Convert, String
from System import Double, Array
from System.Collections.Generic import List


class EdBSiwave(object):
    """EdbSiwave Object
    """

    @property
    def siwave_source(self):
        return self.parent.edblib.SIwave.SiwaveSourceMethods

    @property
    def siwave_setup(self):
        return self.parent.edblib.SIwave.SiwaveSimulationSetupMethods

    @property
    def builder(self):
        return self.parent.builder

    @property
    def edb(self):
        return self.parent.edb

    @property
    def active_layout(self):
        return self.parent.active_layout

    @property
    def cell(self):
        return self.parent.cell

    @property
    def db(self):
        return self.parent.db


    def __init__(self, parent):
        self.parent =parent

    @aedt_exception_handler
    def create_circuit_port(self, positive_component_name, positive_net_name, negative_component_name=None,
                              negative_net_name="GND", impedance_value=50, port_name=""):
        """
        Create a  Circuit Port

        :param positive_component_name: Name of the positive component
        :param positive_net_name: Name of positive net name
        :param negative_component_name:  Name of the negative component. if None, it will be the positive name
        :param negative_net_name: Name of negative net name
        :param impedance_value: port impedance value
        :param port_name: optional port name
        :return: Bool
        """

        if not negative_component_name:
            negative_component_name = positive_component_name
        self.siwave_source.CreateCircuitPort(self.builder, positive_component_name,
                                              positive_net_name, negative_component_name,
                                              negative_net_name, str(impedance_value), port_name)
        return True

    @aedt_exception_handler
    def create_voltage_source(self, positive_component_name, positive_net_name, negative_component_name=None,
                              negative_net_name="GND", current_value=3.3, phase_value=0,source_name=""):
        """Create a Voltage Source

        :param positive_component_name: Name of the positive component
        :param positive_net_name: Name of positive net name
        :param negative_component_name:  Name of the negative component. if None, it will be the positive name
        :param negative_net_name: Name of negative net name
        :param current_value: Voltage Value
        :param phase_value: Optional Phase Value
        :param source_name: optional port name
        :return: Bool
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        self.siwave_source.CreateVoltageSource(self.builder, positive_component_name,
                                                positive_net_name, negative_component_name,
                                                negative_net_name, str(current_value)+"V", str(phase_value), source_name)

    @aedt_exception_handler
    def add_siwave_ac_analysis(self, accuracy_level=1, decade_count=10, sweeptype=1, start_freq=1, stop_freq=1e9, step_freq=1e6, discre_sweep=False):
        """
        Add Siwave AC Analysis


        :param accuracy_level:
        :param decade_count:
        :param sweeptype:
        :param start_freq:
        :param stop_freq:
        :param step_freq:
        :param discre_sweep:
        :return:
        """
        self.siwave_setup.AddACSimSetup(self.builder, accuracy_level, str(decade_count), sweeptype, str(start_freq), str(stop_freq), str(step_freq), discre_sweep)
        return True

    @aedt_exception_handler
    def add_siwave_dc_analysis(self, accuracy_level=1):
        """
        Add Siwave DC Analysis


        :param accuracy_level: Accuracy Level
        :return: Bool
        """

        self.siwave_setup.AddDCSimSetup(self.builder, accuracy_level)
        return True
