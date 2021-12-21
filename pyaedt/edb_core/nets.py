from __future__ import absolute_import
import warnings
import random
import time

from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name

try:
    from matplotlib import pyplot as plt
except ImportError:
    if not is_ironpython:
        warnings.warn(
            "The Matplotlib module is required to run some functionalities.\n" "Install with \npip install matplotlib"
        )
    pass


class EdbNets(object):
    """Manages EDB functionalities for nets.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.core_nets
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def _builder(self):
        """ """
        return self._pedb.builder

    @property
    def _edb(self):
        """ """
        return self._pedb.edb

    @property
    def _active_layout(self):
        """ """
        return self._pedb.active_layout

    @property
    def _cell(self):
        """ """
        return self._pedb.cell

    @property
    def db(self):
        """Db object."""
        return self._pedb.db

    @property
    def _padstack_methods(self):
        """ """
        return self._pedb.edblib.Layout.PadStackMethods

    @property
    def _logger(self):
        """Edb logger."""
        return self._pedb.logger

    @property
    def _nets_methods(self):
        """ """
        return self._pedb.edblib.Layout.NetsMethods

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        dict
            Dictionary of nets.
        """
        nets = {}
        for net in self._active_layout.Nets:
            nets[net.GetName()] = net
        return nets

    @property
    def signal_nets(self):
        """Signal nets.

        Returns
        -------
        dict
            Dictionary of signal nets.
        """
        nets = {}
        for net, value in self.nets.items():
            if not value.IsPowerGround():
                nets[net] = value
        return nets

    @property
    def power_nets(self):
        """Power nets.

        Returns
        -------
        dict
            Dictionary of power nets.
        """
        nets = {}
        for net, value in self.nets.items():
            if value.IsPowerGround():
                nets[net] = value
        return nets

    @aedt_exception_handler
    def plot(self, nets, layers=None, color_by_layer=True, save_plot=None, outline=None):
        """Plot a Net to Matplotlib 2D Chart.

        Parameters
        ----------
        nets : str, list
            Name of the net or list of nets to plot. If `None` all nets will be plotted.
        layers : str, list
            Name of the layers on which plot. If `None` all the signal layers will be considered.
        color_by_layer : bool
            If `True` then the plot will be colored by layer.
            If `False` the plot will be colored by net.
        save_plot : str, optional
            If `None` the plot will be shown.
            If a path is entered the plot will be saved to such path.
        outline : list, optional
            List of points of the outline to plot.
        """
        start_time = time.time()
        if is_ironpython:
            self._logger.warning("Plot functionalities are enabled only in CPython.")
            return False
        if not layers:
            layers = list(self._pedb.core_stackup.signal_layers.keys())
        if not nets:
            nets = list(self.nets.keys())
        labels = {}
        fig, ax = plt.subplots(figsize=(20, 10))
        if outline:
            x1 = [i[0] for i in outline]
            y1 = [i[1] for i in outline]
            plt.fill(x1, y1, c="b", label="Outline", alpha=0.3)

        if isinstance(nets, str):
            nets = [nets]
        for path in self._pedb.core_primitives.paths:
            net_name = path.GetNet().GetName()
            layer_name = path.GetLayer().GetName()
            if net_name in nets and layer_name in layers:
                my_net_points = path.GetPolygonData().Points
                x = []
                y = []
                for point in list(my_net_points):
                    if point.Y.ToDouble() < 1e100:
                        x.append(point.X.ToDouble())
                        y.append(point.Y.ToDouble())
                if not x:
                    continue
                if color_by_layer:
                    label = "Layer " + layer_name
                    if label not in labels:
                        color = path.GetLayer().GetColor()
                        try:
                            c = tuple([color.Item1 / 255, color.Item2 / 255, color.Item3 / 255])
                        except:
                            c = "b"
                        labels[label] = c
                        plt.fill(x, y, c=labels[label], label=label, alpha=0.3)
                    else:
                        plt.fill(x, y, c=labels[label], alpha=0.3)
                else:
                    label = "Net " + net_name
                    if label not in labels:
                        labels[label] = tuple(
                            [
                                round(random.uniform(0, 1), 3),
                                round(random.uniform(0, 1), 3),
                                round(random.uniform(0, 1), 3),
                            ]
                        )
                        plt.fill(x, y, c=labels[label], label=label, alpha=0.3)
                    else:
                        plt.fill(x, y, c=labels[label], alpha=0.3)

        for poly in self._pedb.core_primitives.polygons:
            net_name = poly.GetNet().GetName()
            layer_name = poly.GetLayer().GetName()
            if net_name in nets and layer_name in layers:

                my_net_points = poly.GetPolygonData().Points
                x = []
                y = []
                for point in list(my_net_points):
                    if point.Y.ToDouble() < 1e100:
                        x.append(point.X.ToDouble())
                        y.append(point.Y.ToDouble())
                if not x:
                    continue
                if color_by_layer:
                    label = "Layer " + layer_name
                    if label not in labels:
                        color = poly.GetLayer().GetColor()
                        try:
                            c = tuple([color.Item1 / 255, color.Item2 / 255, color.Item3 / 255])
                        except:
                            c = "b"
                        labels[label] = c
                        plt.fill(x, y, c=labels[label], label=label, alpha=0.3)
                    else:
                        plt.fill(x, y, c=labels[label], alpha=0.3)
                else:
                    label = "Net " + net_name
                    if label not in labels:
                        labels[label] = tuple(
                            [
                                round(random.uniform(0, 1), 3),
                                round(random.uniform(0, 1), 3),
                                round(random.uniform(0, 1), 3),
                            ]
                        )
                        plt.fill(x, y, c=labels[label], label=label, alpha=0.3)
                    else:
                        plt.fill(x, y, c=labels[label], alpha=0.3)

                for void in poly.Voids:
                    v_points = void.GetPolygonData().Points
                    x1 = []
                    y1 = []
                    for point in list(v_points):
                        if point.Y.ToDouble() < 1e100:
                            x1.append(point.X.ToDouble())
                            y1.append(point.Y.ToDouble())
                    if x1:
                        if "Voids" not in labels:
                            labels["Voids"] = "black"
                            plt.fill(x1, y1, c="black", alpha=1, label="Voids")
                        else:
                            plt.fill(x1, y1, c="black", alpha=1)

        ax.set(xlabel="X (m)", ylabel="Y (m)", title=self._pedb.active_cell.GetName())
        ax.legend()
        end_time = time.time() - start_time
        self._logger.info("Plot Generation time %s seconds", round(end_time, 3))
        if save_plot:
            plt.savefig(save_plot)
        else:
            plt.show()

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
        if isinstance(netname_list, str):
            netname_list = [netname_list]
        power_nets_names = list(self.power_nets.keys())
        for netname in netname_list:
            if netname in power_nets_names:
                return True
        return False

    @aedt_exception_handler
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
        for refdes, comp_obj in self._pedb.core_components.inductors.items():

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

    @aedt_exception_handler
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

        component_list = []
        rats = self._pedb.core_components.get_rats()
        for net in net_group:
            for el in rats:
                if net in el["net_name"]:
                    i = 0
                    for n in el["net_name"]:
                        if n == net:
                            df = [el["refdes"][i], el["pin_name"][i], net]
                            component_list.append(df)
                        i += 1

        component_type = []
        for el in component_list:
            refdes = el[0]
            comp_type = self._pedb.core_components._cmp[refdes].type
            component_type.append(comp_type)
            el.append(comp_type)

            comp_partname = self._pedb.core_components._cmp[refdes].partname
            el.append(comp_partname)
            pins = self._pedb.core_components.get_pin_from_component(cmpName=refdes, netName=el[2])
            el.append("-".join([i.GetName() for i in pins]))

        component_list_columns = ["refdes", "pin_name", "net_name", "component_type", "component_partname", "pin_list"]
        return component_list, component_list_columns, net_group

    @aedt_exception_handler
    def get_net_by_name(self, net_name):
        """Find a net by name."""
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
        if isinstance(netlist, str):
            netlist = [netlist]
        nets_deleted = []
        for net in netlist:
            try:
                edb_net = self._edb.Cell.Net.FindByName(self._active_layout, net)
                if edb_net is not None:
                    edb_net.Delete()
                    nets_deleted.append(net)
                    self._logger.info("Net %s Deleted", net)
            except:
                pass

        return nets_deleted

    @aedt_exception_handler
    def find_or_create_net(self, net_name=""):
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
        if not net_name:
            net_name = generate_unique_name("NET_")
            net = self._edb.Cell.Net.Create(self._active_layout, net_name)
        else:
            net = self._edb.Cell.Net.FindByName(self._active_layout, net_name)
            if net.IsNull():
                net = self._edb.Cell.Net.Create(self._active_layout, net_name)
        return net

    @aedt_exception_handler
    def is_net_in_component(self, component_name, net_name):
        """Check if a net belongs to a component.

        Parameters
        ----------
        component_name : str
            Name of the component.
        net_name : str
            Name of the net.

        Returns
        -------
        bool
            ``True`` if the net is found in component pins.

        """
        if component_name not in self._pedb.core_components.components:
            return False
        for net in self._pedb.core_components.components[component_name].nets:
            if net_name == net:
                return True
        return False
