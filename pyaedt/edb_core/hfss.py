"""
This module contains the ``Edb3DLayout`` class.
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


class Edb3DLayout(object):
    """Edb3DLayout class."""

    def __init__(self, parent):
        self.parent = parent

    @property
    def _hfss_terminals(self):
        return self.parent.edblib.HFSS3DLayout.HFSSTerminalMethods

    @property
    def _hfss_ic_methods(self):
        return self.parent.edblib.HFSS3DLayout.ICMethods

    @property
    def _hfss_setup(self):
        return self.parent.edblib.HFSS3DLayout.HFSSSetup

    @property
    def _hfss_mesh_setup(self):
        return self.parent.edblib.HFSS3DLayout.Meshing

    @property
    def _sweep_methods(self):
        return self.parent.edblib.SimulationSetup.SweepMethods

    @property
    def _edb(self):
        return self.parent.edb

    @property
    def _active_layout(self):
        return self.parent.active_layout

    @property
    def _cell(self):
        return self.parent.cell

    @property
    def _db(self):
        return self.parent.db

    @property
    def _builder(self):
        return self.parent.builder

    @aedt_exception_handler
    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------
        dict
            Dictionary of trace width data.
        """
        mesh =  self._hfss_mesh_setup.GetMeshOperation(self._builder)
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
        if self._hfss_terminals.CreateHfssPorts(self._builder, pinList):
            return True

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
            ref_des_list = [net_list]
        for ref in ref_des_list:
            for pinname, pin in self.parent.core_components.components[ref].pins.items():
                if pin.net in net_list and pin.pin.IsLayoutPin():
                   port_name = "{}_{}_{}".format(ref,pin.net,pin.pin.GetName())
                   if "IronPython" in sys.version or ".NETFramework" in sys.version:
                       res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange()
                   else:
                       res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange(None, None)
                   if self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(self._active_layout, pin.pin.GetNet(), port_name, pin.pin, toLayer_pos):
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
        if "IronPython" in sys.version or ".NETFramework" in sys.version:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange()
        else:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange(None, None)
        if not portname:
            portname = generate_unique_name("Port_" + pinpos.GetNet().GetName())
        edbpointTerm_pos = self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(self._active_layout, pinpos.GetNet(),
                                                                          portname, pinpos,
                                                                          toLayer_pos)
        if edbpointTerm_pos:
            return True
        else:
            return False


