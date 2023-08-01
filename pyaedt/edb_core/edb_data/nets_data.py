from pyaedt.edb_core.dotnet.database import DifferentialPairDotNet
from pyaedt.edb_core.dotnet.database import ExtendedNetDotNet
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
            ]
        Examples
        --------
        >>> from pyaedt import Edb
        >>> app = Edb()
        >>> app.nets["BST_V3P3_S5"].get_extended_net()
        """
        for name, obj in self._app.extended_nets.extended_nets.items():
            if self.name in obj.nets:
                return obj


class EDBExtendedNetData(ExtendedNetDotNet):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_extended_net = edb.nets.extended_nets["GND"]
    >>> edb_extended_net.name # Class Property
    """

    def __init__(self, core_app, raw_extended_net=None):
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self._core_nets = core_app.nets
        ExtendedNetDotNet.__init__(self, self._app, raw_extended_net)

    @property
    def nets(self):
        return {name: self._core_nets[name] for name in self.api_nets}

    @property
    def components(self):
        comps = {}
        for name, obj in self.nets.items():
            comps.update(obj.components)
        return comps

    @property
    def rlc(self):
        return {name: comp for name, comp in self.components.items() if comp.type in ["Inductor", "Resistor", "Capacitor"]}

    @property
    def serial_rlc(self):
        comps_common = {}
        nets = self.nets
        for net in nets:
            comps_common.update(
                {
                    i: v
                    for i, v in self._app._nets[net].components.items()
                    if list(set(v.nets).intersection(nets)) != [net]
                }
            )
        return comps_common

    @pyaedt_function_handler
    def add_nets(self, net_names: list[str]):
        flag = True
        for i in net_names:
            flag = flag and self.add_net(i)
        return flag


class EDBDifferentialPairData(DifferentialPairDotNet):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb.differential_pairs.differential_pairs
    """

    def __init__(self, core_app, api_object=None):
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self._core_nets = core_app.nets
        DifferentialPairDotNet.__init__(self, self._app, api_object)

    @property
    def positive_net(self):
        return EDBNetsData(self.api_positive_net, self._app)

    @property
    def negative_net(self):
        return EDBNetsData(self.api_negative_net, self._app)
