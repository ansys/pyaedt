# -*- coding: utf-8 -*-
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Modeler import Modeler
from pyaedt.modeler.Object3d import CircuitComponent
from pyaedt.modeler.Primitives3DLayout import Primitives3DLayout
from pyaedt.modeler.PrimitivesEmit import EmitComponent
from pyaedt.modeler.PrimitivesEmit import EmitComponents
from pyaedt.modeler.PrimitivesMaxwellCircuit import MaxwellCircuitComponents
from pyaedt.modeler.PrimitivesNexxim import NexximComponents
from pyaedt.modeler.PrimitivesTwinBuilder import TwinBuilderComponents
from pyaedt.modules.LayerStackup import Layers


class ModelerCircuit(Modeler):
    """ModelerCircuit class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`

    Examples
    --------
    >>> from pyaedt import Circuit
    >>> app = Circuit()
    >>> my_modeler = app.modeler
    """

    def __init__(self, app):
        self._app = app
        self.o_def_manager = self._app.odefinition_manager
        Modeler.__init__(self, app)

    @property
    def o_component_manager(self):
        """Component manager object."""
        return self._app.o_component_manager

    @property
    def o_model_manager(self):
        """Model manager object."""
        return self._app.o_model_manager

    @property
    def oeditor(self):
        """Oeditor Module.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("SchematicEditor")"""
        return self._app.oeditor

    @property
    def obounding_box(self):
        """Bounding box.

        References
        ----------

        >>> oEditor.GetModelBoundingBox()"""
        return self.oeditor.GetModelBoundingBox()

    @pyaedt_function_handler()
    def zoom_to_fit(self):
        """Zoom To Fit.

        References
        ----------

        >>> oEditor.ZoomToFit
        """
        self.oeditor.ZoomToFit()

    @pyaedt_function_handler()
    def connect_schematic_components(self, firstcomponent, secondcomponent, pinnum_first=2, pinnum_second=1):
        """Connect schematic components.

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

        References
        ----------

        >>> oEditor.CreateWire
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

    @pyaedt_function_handler()
    def _get_components_selections(self, selections, return_as_list=True):
        sels = []
        if not isinstance(selections, list):
            selections = [selections]
        for sel in selections:
            if isinstance(sel, int):
                sels.append(self.schematic.components[sel].composed_name)
            elif isinstance(sel, (CircuitComponent, EmitComponent)):
                sels.append(sel.composed_name)
            else:
                for el in list(self.schematic.components.values()):
                    if sel in [el.InstanceName, el.composed_name, el.name]:
                        sels.append(el.composed_name)
        if not return_as_list:
            return ", ".join(sels)
        return sels


class ModelerNexxim(ModelerCircuit):
    """ModelerNexxim class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self._schematic = NexximComponents(self)
        self._layouteditor = None
        self.layers = Layers(self, roughnessunits="um")
        self._primitives = Primitives3DLayout(app)

    @property
    def layouteditor(self):
        """Return the Circuit Layout Editor.

        References
        ----------

        >>> oDesign.SetActiveEditor("Layout")
        """
        return self._app.layouteditor

    @property
    def schematic(self):
        """Schematic Component.

        Returns
        -------
        :class:`pyaedt.modeler.PrimitivesNexxim.NexximComponents`
        """
        return self._schematic

    @property
    def components(self):
        """Schematic Component.

        .. deprecated:: 0.4.13
           Use :func:`Circuit.modeler.schematic` instead.

        Returns
        -------
        :class:`pyaedt.modeler.PrimitivesNexxim.NexximComponents`
        """
        return self._schematic

    @property
    def edb(self):
        """EDB.

        Returns
        -------
        :class:`pyaedt.Edb`
            edb_core object if it exists.

        """
        # TODO Check why it crashes when multiple circuits are created
        return None

    @property
    def model_units(self):
        """Model units.

        References
        ----------

        >>> oEditor.GetActiveUnits
        >>> oEditor.SetActiveUnits
        """
        return _retry_ntimes(10, self.layouteditor.GetActiveUnits)

    @property
    def layout(self):
        """Primitives.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives3DLayout.Primitives3DLayout`

        """
        if self._app.design_type == "Twin Builder":
            return
        return self._primitives

    @property
    def primitives(self):
        """Primitives.

        .. deprecated:: 0.4.13
           Use :func:`Circuit.modeler.layout` instead.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives3DLayout.Primitives3DLayout`

        """
        return self._primitives

    @model_units.setter
    def model_units(self, units):
        assert units in AEDT_UNITS["Length"], "Invalid units string {0}".format(units)
        """ Set the model units as a string e.g. "mm" """
        self.oeditor.SetActivelUnits(["NAME:Units Parameter", "Units:=", units, "Rescale:=", False])

    @pyaedt_function_handler()
    def move(self, selections, pos, units="meter"):
        """Move the selections by ``[x, y]``.

        Parameters
        ----------
        selections : list
            List of the selections.
        pos : list
            Offset for the ``[x, y]`` axis.
        units : str
            Offset for the Y axis.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Move
        """
        sels = self._get_components_selections(selections)
        if not sels:
            self.logger.error("No Component Found.")
            return False
        x_location = AEDT_UNITS["Length"][units] * float(pos[0])
        y_location = AEDT_UNITS["Length"][units] * float(pos[1])

        self.oeditor.Move(
            ["NAME:Selections", "Selections:=", sels],
            [
                "NAME:MoveParameters",
                "xdelta:=",
                x_location,
                "ydelta:=",
                y_location,
                "Disconnect:=",
                False,
                "Rubberband:=",
                False,
            ],
        )
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oEditor.Rotate
        """
        sels = self._get_components_selections(selections)
        if not sels:
            self.logger.error("No Component Found.")
            return False

        self.oeditor.Rotate(
            ["NAME:Selections", "Selections:=", sels],
            [
                "NAME:RotateParameters",
                "Degrees:=",
                degrees,
                "Disconnect:=",
                False,
                "Rubberband:=",
                False,
            ],
        )
        return True


class ModelerTwinBuilder(ModelerCircuit):
    """ModelerTwinBuilder class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisTwinBuilder.AnalysisTwinBuilder`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self._components = TwinBuilderComponents(self)

    @property
    def components(self):
        """
        .. deprecated:: 0.4.13
           Use :func:`TwinBuilder.modeler.schematic` instead.

        """
        return self._components

    @property
    def schematic(self):
        """Schematic Object.

        Returns
        -------
        :class:`pyaedt.modeler.PrimitivesTwinBuilder.TwinBuilderComponents`

        """
        return self._components


class ModelerEmit(ModelerCircuit):
    """ModelerEmit class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisEmit`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self.components = EmitComponents(app, self)


class ModelerMaxwellCircuit(ModelerCircuit):
    """ModelerMaxwellCircuit class.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisMaxwellCircuit`

    """

    def __init__(self, app):
        self._app = app
        ModelerCircuit.__init__(self, app)
        self._components = MaxwellCircuitComponents(self)

    @property
    def schematic(self):
        """Schematic Object.

        Returns
        -------
        :class:`pyaedt.modeler.PrimitivesMaxwellCircuit.MaxwellCircuitComponents`

        """
        return self._components
