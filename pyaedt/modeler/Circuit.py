

import os

from ..generic.general_methods import generate_unique_name, aedt_exception_handler, retry_ntimes
from ..application.Variables import AEDT_units
from ..edb import Edb
from .Modeler import Modeler
from .PrimitivesSimplorer import SimplorerComponents
from .PrimitivesNexxim import NexximComponents
from .Primitives3DLayout import Primitives3DLayout
from ..modules.LayerStackup import Layers


class ModelerCircuit(Modeler):
    """ModelerCircuit class."""

    def __init__(self, parent):
        self._parent = parent
        Modeler.__init__(self, parent)

    @property
    def oeditor(self):
        """ """
        return self.odesign.SetActiveEditor("SchematicEditor")

    @property
    def obounding_box(self):
        """ """
        return self.oeditor.GetModelBoundingBox()

    @property
    def o_def_manager(self):
        """ """
        return self._parent.oproject.GetDefinitionManager()

    @property
    def o_component_manager(self):
        """ """
        return self.o_def_manager.GetManager("Component")

    @property
    def o_model_manager(self):
        """ """
        return self.o_def_manager.GetManager("Model")

    @aedt_exception_handler
    def connect_schematic_components(self, firstcomponent, secondcomponent, pinnum_first=2, pinnum_second=1):
        """

        Parameters
        ----------
        firstcomponent :
            
        secondcomponent :
            
        pinnum_first :
             The default is ``2``.
        pinnum_second :
             The default is ``1``.

        Returns
        -------

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
    """ModelerNexxim class."""

    def __init__(self, parent):
        self._parent = parent
        ModelerCircuit.__init__(self, parent)
        self.components = NexximComponents(parent, self)

        self.layers = Layers(parent, self, roughnessunits="um")
        self._primitives = Primitives3DLayout(self._parent, self)
        self._primitivesDes = self._parent.project_name + self._parent.design_name
        edb_folder = os.path.join(self._parent.project_path, self._parent.project_name + ".aedb")
        edb_file = os.path.join(edb_folder, "edb.def")
        if os.path.exists(edb_file):
            self._mttime = os.path.getmtime(edb_file)
            try:
                self._edb = Edb(edb_folder, self._parent.design_name, True, self._parent._aedt_version, isaedtowned=True,
                                oproject=self._parent.oproject)
            except:
                self._edb = None
        else:
            self._mttime = 0

    @property
    def edb(self):
        """

        Returns
        -------
        Edb
            edb_core object if it exists.
        """
        if self._parent.design_type == "Twin Builder":
            return
        edb_folder = os.path.join(self._parent.project_path, self._parent.project_name + ".aedb")
        edb_file = os.path.join(edb_folder, "edb.def")
        _mttime = os.path.getmtime(edb_file)
        if _mttime != self._mttime:
            self._edb = Edb(edb_folder, self._parent.design_name, True, self._parent._aedt_version,
                            isaedtowned=True, oproject=self._parent.oproject)
            self._mttime = _mttime
        return self._edb

    @property
    def layouteditor(self):
        if self._parent.design_type == "Twin Builder":
            return
        return self.odesign.SetActiveEditor("Layout")

    @property
    def model_units(self):
        return retry_ntimes(10, self.layouteditor.GetActiveUnits)

    @property
    def primitives(self):
        """

        Returns
        -------
        Primitives3DLayout
        """
        if self._parent.design_type == "Twin Builder":
            return
        if self._primitivesDes != self._parent.project_name + self._parent.design_name:
            self._primitives = Primitives3DLayout(self._parent, self)
            self._primitivesDes = self._parent.project_name + self._parent.design_name
        return self._primitives

    @model_units.setter
    def model_units(self, units):
        """Set circuit model units.

        Parameters
        ----------
        units : str
            Units for the circuit model.
            
        """
        assert units in AEDT_units["Length"], "Invalid units string {0}".format(units)
        ''' Set the model units as a string e.g. "mm" '''
        self.oeditor.SetActivelUnits(
            [
                "NAME:Units Parameter",
                "Units:=", units,
                "Rescale:=", False
            ])

    @aedt_exception_handler
    def move(self, selections, posx, posy):
        """Move the selections by x, y.

        Parameters
        ----------
        selections : list
            List of the selections.
        posx :
            Offset for the X axis.
        posy :
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
            [
                "NAME:Selections",
                "Selections:=", sels
            ],
            [
                "NAME:MoveParameters",
                "xdelta:=", posx,
                "ydelta:=", posy,
                "Disconnect:=", False,
                "Rubberband:=", False
            ])
        return True

    @aedt_exception_handler
    def rotate(self, selections, degrees=90):
        """Rotate the selections by degrees.

        Parameters
        ----------
        selections : list
            List of the selections.
        degrees : optional
            Rotation angle. The default is ``90``.

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
            [
                "NAME:Selections",
                "Selections:=", sels
            ],
            [
                "NAME:RotateParameters",
                "Degrees:=", degrees,
                "Disconnect:=", False,
                "Rubberband:=", False
            ])
        return True


class ModelerSimplorer(ModelerCircuit):
    """ """

    def __init__(self, parent):
        self._parent = parent
        ModelerCircuit.__init__(self, parent)
        self.components = SimplorerComponents(parent, self)

class ModelerEmit(ModelerCircuit):
    """ModelerEmit class. """

    def __init__(self, parent):
        self._parent = parent
        ModelerCircuit.__init__(self, parent)
