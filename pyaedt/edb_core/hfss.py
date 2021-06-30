"""
This module contains the ``Edb3DLayout`` class.
"""

import warnings
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name


try:
    import clr
    from System import Convert, String
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires pythonnet.')


class Edb3DLayout(object):
    """Edb3DLayout class."""

    @property
    def hfss_terminals(self):
        return self.parent.edblib.HFSS3DLayout.HFSSTerminalMethods

    @property
    def hfss_ic_methods(self):
        return self.parent.edblib.HFSS3DLayout.ICMethods

    @property
    def hfss_setup(self):
        return self.parent.edblib.HFSS3DLayout.HFSSSetup

    @property
    def hfss_mesh_setup(self):
        return self.parent.edblib.HFSS3DLayout.Meshing

    @property
    def sweep_methods(self):
        return self.parent.edblib.SimulationSetup.SweepMethods

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

    @property
    def builder(self):
        return self.parent.builder

    def __init__(self, parent):
        self.parent = parent

    @aedt_exception_handler
    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------
        dict
            Dictionary of trace width data.
        """
        mesh =  self.hfss_mesh_setup.GetMeshOperation(self.builder)
        if mesh.Item1:
            return convert_netdict_to_pydict(mesh.Item2)
        else:
            return {}

    @aedt_exception_handler
    def create_circuit_port(self, pin_list):
        """Create a circuit port.

        Parameters
        ----------
        pin_list : list
            Pin object or a pin list object.          

        Returns
        -------
        list
           List of names of the created ports.
        
        """
        pinList = convert_py_list_to_net_list(pin_list)
        if self.hfss_terminals.CreateHfssPorts(self.builder, pinList):
            return True

    @aedt_exception_handler
    def create_coax_port_on_component(self, ref_des_list, net_list):
        """Create a coaxial port on a component or component list on a net or net list.
        
        .. note::
           The name of the new coaxial port is automatically assigned.

        Parameters
        ----------
        ref_des_list : list
            List of one or more reference designators.
            
        net_list : list
            List of one or more nets.  

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        ref_desList = convert_py_list_to_net_list(ref_des_list)
        netList = convert_py_list_to_net_list(net_list)
        if self.hfss_terminals.CreateCoaxPortOnComponent(self.builder, ref_desList, netList):
            return True

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
        if "IronPython" in sys.version or ".NETFramework" in sys.version:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange()
        else:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange(None, None)
        if not portname:
            portname = generate_unique_name("Port_" + pinpos.GetNet().GetName())
        edbpointTerm_pos = self.edb.Cell.Terminal.PadstackInstanceTerminal.Create(self.active_layout, pinpos.GetNet(),
                                                                          portname, pinpos,
                                                                          toLayer_pos)
        if edbpointTerm_pos:
            return True
        else:
            return False
