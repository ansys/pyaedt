
from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modeler.PrimitivesCircuit import CircuitComponents


class SimplorerComponents(CircuitComponents):
    """SimplorerComponents class.

    This class is for managing all circuit components for Simplorer.

    Parameters
    ----------
    parent :

    modeler :

    Examples
    --------
    Basic usage demonstrated with a Simplorer design:

    >>> from pyaedt import Simplorer
    >>> aedtapp = Simplorer()
    >>> prim = aedtapp.modeler.schematic
    """

    @property
    def design_libray(self):
        """Design Library."""
        return "Simplorer Elements"

    @property
    def tab_name(self):
        """Tab name."""
        return "Quantities"

    @aedt_exception_handler
    def __getitem__(self, partname):
        """Get object id from a string or integer.

        Parameters
        ----------
        partname : int or str
            ID or name of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        """
        if isinstance(partname, int):
            return self.components[partname]
        for el in self.components:
            if self.components[el].name == partname or self.components[el].composed_name == partname or el == partname:
                return self.components[el]

        return None

    def __init__(self, modeler):
        CircuitComponents.__init__(self, modeler)
        self._app = modeler._app
        self._modeler = modeler
        self._currentId = 0
        pass

    @aedt_exception_handler
    def create_resistor(self, compname=None, value=50, location=[], angle=0, use_instance_id_netlist=False):
        """Create a resistor.

        Parameters
        ----------
        compname : str, optional
            Name of the resistor. The default is ``None``.
        value : float, optional
            Value for the resistor. The default is ``50``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_component(
            compname,
            component_library="Basic Elements\\Circuit\\Passive Elements",
            component_name="R",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("R", value)

        return id

    @aedt_exception_handler
    def create_inductor(self, compname=None, value=50, location=[], angle=0, use_instance_id_netlist=False):
        """Create an inductor.

        Parameters
        ----------
        compname : str, optional
            Name of the inductor. The default is ``None``.
        value : float, optional
            Value for the inductor. The default is ``50``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_component(
            compname,
            component_library="Basic Elements\\Circuit\\Passive Elements",
            component_name="L",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("L", value)
        return id

    @aedt_exception_handler
    def create_capacitor(self, compname=None, value=50, location=[], angle=0, use_instance_id_netlist=False):
        """Create a capacitor.

        Parameters
        ----------
        compname : str, optional
            Name of the capacitor. The default is ``None``.
        value : float, optional
            Value for the capacitor. The default is ``50``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_component(
            compname,
            component_library="Basic Elements\\Circuit\\Passive Elements",
            component_name="C",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("C", value)
        return id

    @aedt_exception_handler
    def create_diode(
        self, compname=None, model_name="required", location=[], angle=0, use_instance_id_netlist=False
    ):
        """Create a diode.

        Parameters
        ----------
        compname : str, optional
            Name of the diode. The default is ``None``.
        model_name : str, optional
            Name of the model. The default is ``"required"``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_component(
            compname,
            component_library="Basic Elements\\Circuit\\Semiconductors System Level",
            component_name="D",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )
        return id

    @aedt_exception_handler
    def create_npn(self, compname=None, location=[], angle=0, use_instance_id_netlist=False):
        """Create an NPN transistor.

        Parameters
        ----------
        compname : str, optional
            Name of the NPN transistor. The default is ``None``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_component(
            compname,
            component_library="Basic Elements\\Circuit\\Semiconductors System Level",
            component_name="BJT",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )
        return id

    @aedt_exception_handler
    def create_pnp(self, compname=None, location=[], angle=0, use_instance_id_netlist=False):
        """Create a PNP transistor.

        Parameters
        ----------
        compname : str, optional
            Name of the PNP transistor. The default is ``None``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_component(
            compname,
            component_library="Basic Elements\\Circuit\\Semiconductors System Level",
            component_name="BJT",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        return id
