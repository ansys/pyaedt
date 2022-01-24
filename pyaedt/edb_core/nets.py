from __future__ import absolute_import
import warnings
import time
import math

from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.generic.constants import CSS4_COLORS
from pyaedt.edb_core.EDB_Data import EDBNetsData

if not is_ironpython:
    try:
        from matplotlib import pyplot as plt
        from matplotlib.path import Path
        from matplotlib.patches import PathPatch
    except ImportError:
        mess = "The Matplotlib module is required to run some functionalities.\n"
        mess += "Install with \npip install matplotlib"
        warnings.warn(mess)
    except:
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
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBNets`]
            Dictionary of nets.
        """
        nets = {}
        for net in self._active_layout.Nets:
            nets[net.GetName()] = EDBNetsData(net, self._pedb)
        return nets

    @property
    def signal_nets(self):
        """Signal nets.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBNets`]
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
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBNets`]
            Dictionary of power nets.
        """
        nets = {}
        for net, value in self.nets.items():
            if value.IsPowerGround():
                nets[net] = value
        return nets

    @staticmethod
    def _eval_arc_points(p1, p2, h, n=6, tol=1e-12):
        """Get the points of the arc

        Parameters
        ----------
        p1 : list
            Arc starting point.
        p2 : list
            Arc ending point.
        h : float
            Arc height.
        n : int
            Number of points to generate along the arc.
        tol : float
            Geometric tolerance.

        Returns
        -------
        list
            points generated along the arc.
        """
        # fmt: off
        if abs(h) < tol:
            return [], []
        elif h > 0:
            reverse = False
            x1 = p1[0]
            y1 = p1[1]
            x2 = p2[0]
            y2 = p2[1]
        else:
            reverse = True
            x1 = p2[0]
            y1 = p2[1]
            x2 = p1[0]
            y2 = p1[1]
            h *= -1
        xa = (x2-x1) / 2
        ya = (y2-y1) / 2
        xo = x1 + xa
        yo = y1 + ya
        a = math.sqrt(xa**2 + ya**2)
        if a < tol:
            return [], []
        r = (a**2)/(2*h) + h/2
        if abs(r-a) < tol:
            b = 0
            th = 2 * math.asin(1)  # chord angle
        else:
            b = math.sqrt(r**2 - a**2)
            th = 2 * math.asin(a/r)  # chord angle

        # center of the circle
        xc = xo + b*ya/a
        yc = yo - b*xa/a

        alpha = math.atan2((y1-yc), (x1-xc))
        xr = []
        yr = []
        for i in range(n):
            i += 1
            dth = (i/(n+1)) * th
            xi = xc + r * math.cos(alpha-dth)
            yi = yc + r * math.sin(alpha-dth)
            xr.append(xi)
            yr.append(yi)

        if reverse:
            xr.reverse()
            yr.reverse()
        # fmt: on
        return xr, yr

    def _get_points_for_plot(self, my_net_points):
        """
        Get the points to be plot
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            # point = my_net_points[i]
            if not point.IsArc():
                x.append(point.X.ToDouble())
                y.append(point.Y.ToDouble())
                # i += 1
            else:
                arc_h = point.GetArcHeight().ToDouble()
                p1 = [my_net_points[i-1].X.ToDouble(), my_net_points[i-1].Y.ToDouble()]
                if i+1 < len(my_net_points):
                    p2 = [my_net_points[i+1].X.ToDouble(), my_net_points[i+1].Y.ToDouble()]
                else:
                    p2 = [my_net_points[0].X.ToDouble(), my_net_points[0].Y.ToDouble()]
                x_arc, y_arc = self._eval_arc_points(p1, p2, arc_h)
                x.extend(x_arc)
                y.extend(y_arc)
                # i += 1
        # fmt: on
        return x, y

    @aedt_exception_handler
    def plot(
        self, nets, layers=None, color_by_net=False, show_legend=True, save_plot=None, outline=None, size=(2000, 1000)
    ):
        """Plot a Net to Matplotlib 2D Chart.

        Parameters
        ----------
        nets : str, list
            Name of the net or list of nets to plot. If `None` all nets will be plotted.
        layers : str, list, optional
            Name of the layers to include in the plot. If `None` all the signal layers will be considered.
        color_by_net : bool, optional
            If `True`  the plot will be colored by net.
            If `False` the plot will be colored by layer. (default)
        show_legend : bool, optional
            If `True` the legend is shown in the plot. (default)
            If `False` the legend is not shown.
        save_plot : str, optional
            If `None` the plot will be shown.
            If a file path is specified the plot will be saved to such file.
        outline : list, optional
            List of points of the outline to plot.
        size : tuple, optional
            Image size in pixel (width, height).
        """
        start_time = time.time()
        if is_ironpython:
            self._logger.warning("Plot functionalities are enabled only in CPython.")
            return False
        if not layers:
            layers = list(self._pedb.core_stackup.signal_layers.keys())
        if not nets:
            nets = list(self.nets.keys())
        label_colors = {}
        color_index = 0
        dpi = 100.0
        figsize = (size[0] / dpi, size[1] / dpi)
        fig, ax = plt.subplots(figsize=figsize)
        if outline:
            x1 = [i[0] for i in outline]
            y1 = [i[1] for i in outline]
            plt.fill(x1, y1, c="b", label="Outline", alpha=0.3)

        if isinstance(nets, str):
            nets = [nets]

        for path in self._pedb.core_primitives.paths:
            net_name = path.net_name
            layer_name = path.layer_name
            if net_name in nets and layer_name in layers:
                x, y = path.points()
                if not x:
                    continue
                if not color_by_net:
                    label = "Layer " + layer_name
                    if label not in label_colors:
                        color = path.layer.GetColor()
                        try:
                            c = (color.Item1 / 255, color.Item2 / 255, color.Item3 / 255)
                            label_colors[label] = c
                        except:
                            label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                            color_index += 1
                            if color_index >= len(CSS4_COLORS):
                                color_index = 0
                        plt.fill(x, y, c=label_colors[label], label=label, alpha=0.4)
                    else:
                        plt.fill(x, y, c=label_colors[label], alpha=0.4)
                else:
                    label = "Net " + net_name
                    if label not in label_colors:
                        label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                        plt.fill(x, y, c=label_colors[label], label=label, alpha=0.4)
                    else:
                        plt.fill(x, y, c=label_colors[label], alpha=0.4)

        for poly in self._pedb.core_primitives.polygons:
            if poly.is_void:
                continue
            net_name = poly.net_name
            layer_name = poly.layer_name
            if net_name in nets and layer_name in layers:
                xt, yt = poly.points()
                if not xt:
                    continue
                x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
                vertices = [(i, j) for i, j in zip(x, y)]
                codes = [Path.LINETO for _ in vertices]
                codes[0] = Path.MOVETO
                vertices.append((0, 0))
                codes.append(Path.CLOSEPOLY)

                for void in poly.voids:
                    xvt, yvt = void.points()
                    if xvt:
                        xv, yv = GeometryOperators.orient_polygon(xvt, yvt, clockwise=False)
                        tmpV = [(i, j) for i, j in zip(xv, yv)]
                        vertices.extend(tmpV)
                        tmpC = [Path.LINETO for _ in tmpV]
                        tmpC[0] = Path.MOVETO
                        codes.extend(tmpC)
                        vertices.append((0, 0))
                        codes.append(Path.CLOSEPOLY)

                # create Path object from vertices and codes
                path = Path(vertices, codes)

                if not color_by_net:
                    label = "Layer " + layer_name
                    if label not in label_colors:
                        color = poly.GetLayer().GetColor()
                        try:
                            c = (color.Item1 / 255, color.Item2 / 255, color.Item3 / 255)
                            label_colors[label] = c
                        except:
                            label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                            color_index += 1
                            if color_index >= len(CSS4_COLORS):
                                color_index = 0
                        # create patch from path
                        patch = PathPatch(path, color=label_colors[label], alpha=0.4, label=label)
                    else:
                        # create patch from path
                        patch = PathPatch(path, color=label_colors[label], alpha=0.4)
                else:
                    label = "Net " + net_name
                    if label not in label_colors:
                        label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                        # create patch from path
                        patch = PathPatch(path, color=label_colors[label], alpha=0.4, label=label)
                    else:
                        # create patch from path
                        patch = PathPatch(path, color=label_colors[label], alpha=0.4)

                # plot the patch
                ax.add_patch(patch)

        ax.set(xlabel="X (m)", ylabel="Y (m)", title=self._pedb.active_cell.GetName())
        if show_legend:
            ax.legend()
        ax.axis("equal")
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
            pins = self._pedb.core_components.get_pin_from_component(component=refdes, netName=el[2])
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
