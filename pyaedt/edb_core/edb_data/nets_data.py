from pyaedt.edb_core.dotnet.database import NetDotNet
from pyaedt.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyaedt.edb_core.edb_data.primitives_data import cast

# from pyaedt.generic.general_methods import property
from pyaedt.generic.general_methods import pyaedt_function_handler


class EDBNetsData(NetDotNet):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_net = edb.nets.nets["GND"]
    >>> edb_net.name # Class Property
    >>> edb_net.name # EDB Object Property
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            try:
                return getattr(self.net_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, raw_net, core_app):
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self.net_object = raw_net
        NetDotNet.__init__(self, self._app, raw_net)

    @property
    def primitives(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        return [cast(i, self._app) for i in self.net_object.Primitives]

    @property
    def padstack_instances(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`"""
        name = self.name
        return [
            EDBPadstackInstance(i, self._app) for i in self.net_object.PadstackInstances if i.GetNet().GetName() == name
        ]

    @property
    def components(self):
        """Return the list of components that touch the net.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
        """
        comps = {}
        for el, val in self._core_components.components.items():
            if self.name in val.nets:
                comps[el] = val
        return comps

    @pyaedt_function_handler()
    def plot(
        self,
        layers=None,
        show_legend=True,
        save_plot=None,
        outline=None,
        size=(2000, 1000),
    ):
        """Plot a net to Matplotlib 2D chart.

        Parameters
        ----------
        layers : str, list, optional
            Name of the layers to include in the plot. If `None` all the signal layers will be considered.
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

        self._app.nets.plot(
            self.name,
            layers=layers,
            show_legend=show_legend,
            save_plot=save_plot,
            outline=outline,
            size=size,
        )

    @pyaedt_function_handler()
    def get_smallest_trace_width(self):
        """Retrieve the smallest trace width from paths.

        Returns
        -------
        float
            Trace smallest width.
        """
        current_value = 1e10
        for prim in self.net_object.Primitives:
            if "GetWidth" in dir(prim):
                width = prim.GetWidth()
                if width < current_value:
                    current_value = width
        return current_value

    @pyaedt_function_handler
    def get_extended_net(self, resistor_below=10, inductor_below=1, capacitor_above=1, exception_list=None):
        # type: (int | float, int | float, int |float, list) -> dict
        """Get extended net and associated components.

        Parameters
        ----------
        resistor_below : int, float, optional
            Threshold of resistor value. Search extended net across resistors which has value lower than the threshold.
        inductor_below : int, float, optional
            Threshold of inductor value. Search extended net across inductances which has value lower than the
            threshold.
        capacitor_above : int, float, optional
            Threshold of capacitor value. Search extended net across capacitors which has value higher than the
            threshold.
        exception_list : list, optional
            List of components which bypass threshold check.
        Returns
        -------
        list[
            dict[str, :class: `pyaedt.edb_core.edb_data.nets_data.EDBNetsData`],
            dict[str, :class: `pyaedt.edb_core.edb_data.components_data.EDBComponent`],
            dict[str, :class: `pyaedt.edb_core.edb_data.components_data.EDBComponent`],
            ]
        Examples
        --------
        >>> from pyaedt import Edb
        >>> app = Edb()
        >>> app.nets["BST_V3P3_S5"].get_extended_net()
        """
        if exception_list is None:
            exception_list = []
        all_nets = self._app.nets.nets
        nets = {self.name: all_nets[self.name]}
        rlc_serial = {}
        comps = {}

        def get_net_list(net_name, _net_list, _rlc_serial, _comp, exception_list):
            edb_net = all_nets[net_name]
            for refdes, val in edb_net.components.items():
                if not val.is_enabled:
                    continue

                if refdes in exception_list:
                    pass
                elif val.type == "Inductor" and val.rlc_values[1] < inductor_below and val.is_enabled:
                    pass
                elif val.type == "Resistor" and val.rlc_values[0] < resistor_below and val.is_enabled:
                    pass
                elif val.type == "Capacitor" and val.rlc_values[2] > capacitor_above and val.is_enabled:
                    pass
                else:
                    _comp[refdes] = val
                    continue

                _rlc_serial[refdes] = val
                for net in val.nets:
                    if net not in _net_list:
                        _net_list[net] = all_nets[net]
                        get_net_list(net, _net_list, _rlc_serial, _comp, exception_list)

        get_net_list(self.name, nets, rlc_serial, comps, exception_list)

        return [nets, rlc_serial, comps]
