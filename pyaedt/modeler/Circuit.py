from pyaedt.application.Variables import AEDT_units
from pyaedt.generic.general_methods import aedt_exception_handler, retry_ntimes
from pyaedt.modules.LayerStackup import Layers
from pyaedt.modeler.Modeler import Modeler
from pyaedt.modeler.Primitives3DLayout import Primitives3DLayout
from pyaedt.modeler.PrimitivesEmit import EmitComponents
from pyaedt.modeler.PrimitivesNexxim import NexximComponents
from pyaedt.modeler.PrimitivesSimplorer import SimplorerComponents


class ModelerCircuit(Modeler):
    """ModelerCircuit class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`

    """

    def __init__(self, app):
        self._app = app
        self.oeditor = self._odesign.SetActiveEditor("SchematicEditor")
        self.o_def_manager = self._app.odefinition_manager
        self.o_component_manager = self.o_def_manager.GetManager("Component")
        self.o_model_manager = self.o_def_manager.GetManager("Model")

        Modeler.__init__(self, app)

    @property
    @aedt_exception_handler
    def obounding_box(self):
        """Bounding box."""
        return self.oeditor.GetModelBoundingBox()

    @aedt_exception_handler
    def connect_schematic_components(self, firstcomponent, secondcomponent, pinnum_first=2, pinnum_second=1):
        """Connect schematic components.Modd

        Parameters
        ----------
        firstcomponent : str
           Starting (right) component.
        secondcomponent : str
           Ending (left) component for the connection line.
        pinnum_first : str, optional
             Number of the pin at which to terminate the connection from the right end of the
             starting component. The default is ``2``.
        pinnum_second : str, optional
             Number of the pin at which to termiante the connection from the left end of the
             ending component. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        obj1 = self.components[firstcomponent]
        if "Port" in obj1.composed_name:
            pos1 = self.oeditor.GetPropertyValue("BaseElementTab", obj1.composed_name, "Component Location").split(", ")
            pos1 = [float(i.strip()[:-3]) * 0.0000254 for i in pos1]
            if "GPort" in obj1.composed_name:
                pos1[1] += 0.00254
        else:
            pins1 = self.components.get_pins(firstcomponent)
            pos1 = self.components.get_pin_location(firstcomponent, pins1[pinnum_first - 1])
        obj2 = self.components[secondcomponent]
        if "Port" in obj2.composed_name:
            pos2 = self.oeditor.GetPropertyValue("BaseElementTab", obj2.composed_name, "Component Location").split(", ")
            pos2 = [float(i.strip()[:-3]) * 0.0000254 for i in pos2]
            if "GPort" in obj2.composed_name:
                pos2[1] += 0.00254

        else:
            pins2 = self.components.get_pins(secondcomponent)
            pos2 = self.components.get_pin_location(secondcomponent, pins2[pinnum_second - 1])
        self.components.create_wire([pos1, pos2])
        return True


class ModelerNexxim(ModelerCircuit):
    """ModelerNexxim class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self.components = NexximComponents(self)
        self.layouteditor = None
        if self._app.design_type != "Twin Builder":
            self.layouteditor = self._odesign.SetActiveEditor("Layout")
            self._odesign.SetActiveEditor("SchematicEditor")
        self.layers = Layers(self, roughnessunits="um")
        self._primitives = Primitives3DLayout(self)
        self._primitivesDes = self._app.project_name + self._app.design_name

    @property
    @aedt_exception_handler
    def edb(self):
        """EDB.

        Returns
        -------
        :class:`pyaedt.Edb`
            edb_core object if it exists.

        """
        # TODO Check while it crashes when multiple circuits are created
        return None

    @property
    @aedt_exception_handler
    def model_units(self):
        """Model units."""
        return retry_ntimes(10, self.layouteditor.GetActiveUnits)

    @property
    @aedt_exception_handler
    def primitives(self):
        """Primitives.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives3DLayout.Primitives3DLayout`

        """
        if self._app.design_type == "Twin Builder":
            return
        if self._primitivesDes != self._app.project_name + self._app.design_name:
            self._primitives = Primitives3DLayout(self)
            self._primitivesDes = self._app.project_name + self._app.design_name
        return self._primitives

    @model_units.setter
    def model_units(self, units):
        assert units in AEDT_units["Length"], "Invalid units string {0}".format(units)
        """ Set the model units as a string e.g. "mm" """
        self.oeditor.SetActivelUnits(["NAME:Units Parameter", "Units:=", units, "Rescale:=", False])

    @aedt_exception_handler
    def move(self, selections, posx, posy):
        """Move the selections by ``[x, y]``.

        Parameters
        ----------
        selections : list
            List of the selections.
        posx : float
            Offset for the X axis.
        posy : float
            Offset for the Y axis.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if type(selections) is str:
            selections = [selections]
        sels = []
        for sel in selections:
            for el in list(self.components.components.values()):
                if sel == el.InstanceName:
                    sels.append(self.components.components[el.id].composed_name)

        self.oeditor.Move(
            ["NAME:Selections", "Selections:=", sels],
            ["NAME:MoveParameters", "xdelta:=", posx, "ydelta:=", posy, "Disconnect:=", False, "Rubberband:=", False],
        )
        return True

    @aedt_exception_handler
    def rotate(self, selections, degrees=90):
        """Rotate the selections by degrees.

        Parameters
        ----------
        selections : list
            List of the selections.
        degrees : optional
            Angle rotation in degrees. The default is ``90``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        sels = []
        for sel in selections:
            for el in list(self.components.components.values()):
                if sel == el.InstanceName:
                    sels.append(self.components.components[el.id].composed_name)
        self.oeditor.Rotate(
            ["NAME:Selections", "Selections:=", sels],
            ["NAME:RotateParameters", "Degrees:=", degrees, "Disconnect:=", False, "Rubberband:=", False],
        )
        return True


class ModelerSimplorer(ModelerCircuit):
    """ModelerSimplorer class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisSimplorer.FieldAnalysisSimplorer`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self.components = SimplorerComponents(self)


class ModelerEmit(ModelerCircuit):
    """ModelerEmit class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisSimplorer.FieldAnalysisSimplorer`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self.components = EmitComponents(app, self)

