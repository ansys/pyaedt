from __future__ import absolute_import
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


class EdbNets(object):
    """EdbNets class"""

    def __init__(self, parent):
        self.parent = parent

    @property
    def _builder(self):
        """ """
        return self.parent.builder

    @property
    def _edb(self):
        """ """
        return self.parent.edb

    @property
    def _edb_value(self):
        """ """
        return self.parent.edb_value

    @property
    def _active_layout(self):
        """ """
        return self.parent.active_layout

    @property
    def _cell(self):
        """ """
        return self.parent.cell

    @property
    def db(self):
        """ """
        return self.parent.db

    @property
    def _padstack_methods(self):
        """ """
        return self.parent.edblib.Layout.PadStackMethods

    @property
    def _messenger(self):
        """ """
        return self.parent._messenger

    @property
    def _nets_methods(self):
        """ """
        return self.parent.edblib.Layout.NetsMethods

    @property
    def nets(self):
        """Nets.
        
        Returns
        -------
        dict
            Dictionary of nets.
        """
        if self._builder:
            return convert_netdict_to_pydict(self._nets_methods.GetNetDict(self._builder))

    @property
    def signal_nets(self):
        """Signal nets.
        
        Return
        ------
        dict
            Dictionary of signal nets.
        """
        if self._builder:
            return convert_netdict_to_pydict(self._nets_methods.GetSignalNetDict(self._builder))

    @property
    def power_nets(self):
        """Power nets.
        
        Returns
        -------
        dict
            Dictionary of power nets.
        """
        if self._builder:
            return convert_netdict_to_pydict(self._nets_methods.GetPowerNetDict(self._builder))

    @aedt_exception_handler
    def is_power_gound_net(self, netname_list):
        """Determine if one of the  nets in a list is power or ground.

        Parameters
        ----------
        netname_list : list
            List of net names.

        Returns
        -------
        bool
            ``True`` when one of the net names is ``"power"`` or ``"ground"``, ``False`` otherwise.
        """
        if self._builder:
            return self._nets_methods.IsPowerGroundNetInList(self._builder, netname_list)

    def get_dcconnected_net_list(self, ground_nets=["GND"]):
        """Retrieve the nets connected to DC through inductors.
        
        .. note::
           Only inductors are considered.

        Parameters
        ----------
        ground_nets : list, optional
            List of ground nets. The default is ``["GND"]``.

        Returns
        -------
        list
            List of nets connected to DC through inductors. 
        """
        temp_list = []
        for refdes, comp_obj in self.parent.core_components.inductors.items():

            numpins = comp_obj.numpins

            if numpins == 2:
                nets = comp_obj.nets
                if not set(nets).intersection(set(ground_nets)):
                    temp_list.append(set(nets))
                else:
                    pass

        dcconnected_net_list = []

        while not not temp_list:
            s = temp_list.pop(0)
            interseciton_flag = False
            for i in temp_list:
                if not not s.intersection(i):
                    i.update(s)
                    interseciton_flag = True

            if not interseciton_flag:
                dcconnected_net_list.append(s)

        return dcconnected_net_list

    def get_powertree(self, power_net_name, ground_nets):
        """Retrieve the power tree.

        Parameters
        ----------
        power_net_name : str
            Name of the power net.
        ground_nets :
            

        Returns
        -------

        """
        flag_in_ng = False
        net_group = []
        for ng in self.get_dcconnected_net_list(ground_nets):
            if power_net_name in ng:
                flag_in_ng = True
                net_group.extend(ng)
                break

        if not flag_in_ng:
            net_group.append(power_net_name)

        df_list = []
        rats = self.parent.core_components.get_rats()
        for net in net_group:
            for el in rats:
                if net in el['net_name']:
                    i = 0
                    for n in el['net_name']:
                        if n == net:
                            df = [el['refdes'][i], el['pin_name'][i],net ]
                            df_list.append(df)
                        i += 1

        component_type = []
        for el in df_list:
            refdes = el[0]
            comp_type = self.parent.core_components._cmp[refdes].type
            component_type.append(comp_type)
            el.append(comp_type)
        return df_list, net_group

    @aedt_exception_handler
    def get_net_by_name(self, net_name):
        edb_net = self._edb.Cell.Net.FindByName(self._active_layout, net_name)
        if edb_net is not None:
            return edb_net

    @aedt_exception_handler
    def delete_nets(self, netlist):
        """Delete one or more nets from EDB.
       
        Parameters
        ----------
        netlist : str or list
            One or more nets to delete.

        Returns
        -------
        list
            List of nets that were deleted.

        Examples
        --------
        
        >>> deleted_nets = edb_core.core_nets.delete_nets(["Net1","Net2"])
        """
        if type(netlist) is str:
            netlist=[netlist]
        nets_deleted =[]
        for net in netlist:
            try:
                edb_net = self._edb.Cell.Net.FindByName(self._active_layout, net)
                if edb_net is not None:
                    edb_net.Delete()
                    nets_deleted.append(net)
                    self._messenger.add_info_message("Net {} Deleted".format(net))
            except:
                pass

        return nets_deleted

    def find_or_create_net(self, net_name=''):
        """Find or create the net with the given name in the layout.

        Parameters
        ----------
        net_name : str, optional
            Name of the net to find or create. The default is ``""``.

        Returns
        -------
        object
            Net Object
        """

        net = self._edb.Cell.Net.FindByName(self._active_layout, net_name)
        if net.IsNull():
            net = self._edb.Cell.Net.Create(self._active_layout, net_name)
        return net


