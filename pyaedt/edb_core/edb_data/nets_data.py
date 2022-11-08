from pyaedt.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyaedt.edb_core.edb_data.primitives_data import EDBPrimitives
from pyaedt.generic.general_methods import pyaedt_function_handler


class EDBNetsData(object):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_net = edb.core_nets.nets["GND"]
    >>> edb_net.name # Class Property
    >>> edb_net.GetName() # EDB Object Property
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
        self._core_components = core_app.core_components
        self._core_primitive = core_app.core_primitives
        self.net_object = raw_net

    @property
    def name(self):
        """Return the Net Name.

        Returns
        -------
        str
        """
        return self.net_object.GetName()

    @name.setter
    def name(self, val):
        self.net_object.SetName(val)

    @property
    def primitives(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        return [EDBPrimitives(i, self._app) for i in self.net_object.Primitives]

    @property
    def padstack_instances(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`"""
        return [EDBPadstackInstance(i, self._app) for i in self.net_object.PadstackInstances]

    @property
    def is_power_ground(self):
        """Either to get/set boolean for power/ground net.

        Returns
        -------
        bool
        """
        return self.net_object.IsPowerGround()

    @is_power_ground.setter
    def is_power_ground(self, val):
        if isinstance(val, bool):
            self.net_object.SetIsPowerGround(val)
        else:
            raise AttributeError("Value has to be a boolean.")

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

    @pyaedt_function_handler
    def delete(self):
        """Delete this net from layout."""
        self.net_object.Delete()

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

        self._app.core_nets.plot(
            self.name,
            layers=layers,
            show_legend=show_legend,
            save_plot=save_plot,
            outline=outline,
            size=size,
        )
