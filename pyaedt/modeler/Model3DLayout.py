import os
import time

from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.edb import Edb
from pyaedt.generic.general_methods import aedt_exception_handler, _retry_ntimes, is_ironpython, _pythonver, \
    inside_desktop
from pyaedt.modules.LayerStackup import Layers
from pyaedt.modeler.Modeler import Modeler
from pyaedt.modeler.Primitives3DLayout import Geometries3DLayout, Primitives3DLayout


class Modeler3DLayout(Modeler):
    """Manages Modeler 3D layouts.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``hfss3dlayout.modeler``).

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3DLayout.FieldAnalysis3DLayout`
            Inherited parent object.

    Examples
    --------
    >>> from pyaedt import Hfss3dLayout
    >>> hfss = Hfss3dLayout()
    >>> my_modeler = hfss.modeler
    """

    def __init__(self, app):
        self._app = app
        self._oeditor = self._app._odesign.SetActiveEditor("Layout")
        self.logger.info("Loading Modeler.")
        Modeler.__init__(self, app)
        self.logger.info("Modeler loaded.")
        self._primitivesDes = self._app.project_name + self._app.design_name
        edb_folder = os.path.join(self._app.project_path, self._app.project_name + ".aedb")
        edb_file = os.path.join(edb_folder, "edb.def")
        self._edb = None
        if os.path.exists(edb_file) or (inside_desktop and is_ironpython):
            if os.path.exists(edb_file):
                self._mttime = os.path.getmtime(edb_file)
            else:
                self._mttime = 0
            time.sleep(1)
            self._edb = Edb(
                edb_folder,
                self._app.design_name,
                True,
                self._app._aedt_version,
                isaedtowned=True,
                oproject=self._app.oproject,
            )
        else:
            self._mttime = 0
        self.logger.info("EDB loaded.")
        self.layers = Layers(self, roughnessunits="um")
        self.logger.info("Layers loaded.")
        self._primitives = Primitives3DLayout(self)
        self.logger.info("Primitives loaded.")
        self.layers.refresh_all_layers()

        pass

    @property
    def oeditor(self):
        """Oeditor Module.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("Layout")"""
        return self._oeditor

    @property
    def edb(self):
        """EBD.

        Returns
        -------
        :class:`pyaedt.edb.Edb`
             EDB.

        """
        if not (inside_desktop and is_ironpython):
            edb_folder = os.path.join(self._app.project_path, self._app.project_name + ".aedb")
            edb_file = os.path.join(edb_folder, "edb.def")
            if os.path.exists(edb_file):
                _mttime = os.path.getmtime(edb_file)
            else:
                _mttime = 0
            if _mttime != self._mttime:
                if self._edb:
                    self._edb.close_edb()
                self._edb = Edb(
                    edb_folder,
                    self._app.design_name,
                    True,
                    self._app._aedt_version,
                    isaedtowned=True,
                    oproject=self._app.oproject,
                )
                self._mttime = _mttime
        return self._edb

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @aedt_exception_handler
    def fit_all(self):
        """Fit all.

        References
        ----------

        >>> oEditor.ZoomToFit()
        """
        try:
            self._desktop.RestoreWindow()
            self.oeditor.ZoomToFit()
        except:
            self._desktop.RestoreWindow()

    @property
    def model_units(self):
        """Model units.

        References
        ----------

        >>> oEditor.GetActiveUnits
        >>> oEditor.SetActivelUnits
        """
        return _retry_ntimes(10, self.oeditor.GetActiveUnits)

    @model_units.setter
    def model_units(self, units):
        assert units in AEDT_UNITS["Length"], "Invalid units string {0}.".format(units)
        """ Set the model units as a string e.g. "mm" """
        self.oeditor.SetActivelUnits(["NAME:Units Parameter", "Units:=", units, "Rescale:=", False])

    @property
    def primitives(self):
        """Primitives."""
        if self._primitivesDes != self._app.project_name + self._app.design_name:
            self._primitives = Primitives3DLayout(self)
            self._primitivesDes = self._app.project_name + self._app.design_name
        return self._primitives

    @property
    def obounding_box(self):
        """Bounding box.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        return self.oeditor.GetModelBoundingBox()

    @aedt_exception_handler
    def _arg_with_dim(self, value, units=None):
        if isinstance(value, str):
            val = value
        else:
            if units is None:
                units = self.model_units
            val = "{0}{1}".format(value, units)

        return val

    def _pos_with_arg(self, pos, units=None):
        posx = self._arg_with_dim(pos[0], units)
        if len(pos) < 2:
            posy = self._arg_with_dim(0, units)
        else:
            posy = self._arg_with_dim(pos[1], units)
        if len(pos) < 3:
            posz = self._arg_with_dim(0, units)
        else:
            posz = self._arg_with_dim(pos[2], units)

        return posx, posy, posz

    @aedt_exception_handler
    def change_property(self, property_object, property_name, property_value, property_tab="BaseElementTab"):
        """Change an oeditor property.

        Parameters
        ----------
        property_object : str
            Property Obcject name. It can be the name of excitation or field reporter. Eg. ``FieldsReporter:Mag_H``,
            ``Excitations:Port1``.
        property_name : str
            Property name. Eg. ``Rotation Angle``
        property_value : str, list
            Property value. It's a string in case of single value. and a list of 3 elements in case of [X,Y,Z]
        property_tab : str
            Name of the tab to update. Default ``BaseElementTab``. Other options are ``EM Design``,
            ``FieldsPostProcessorTab``.

        Returns
        -------
        bool
            ``True`` if successful.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if isinstance(property_value, list) and len(property_value) == 3:
            xpos, ypos, zpos = self._pos_with_arg(property_value)
            self.oeditor.ChangeProperty(
                ["NAME:AllTabs", ["NAME:" + property_tab, ["NAME:PropServers", property_object], ["NAME:ChangedProps", [
                    "NAME:" + property_name, "X:=", xpos, "Y:=", ypos, "Z:=", zpos]]]])
        elif isinstance(property_value, (str, float, int)):
            posx = self._arg_with_dim(property_value, self.model_units)
            self.oeditor.ChangeProperty(
                ["NAME:AllTabs", ["NAME:"+property_tab, ["NAME:PropServers", property_object],
                                  ["NAME:ChangedProps", ["NAME:"+property_name, "Value:=", posx]]]])
        else:
            self.logger.error("Wrong Property Value")
            return False
        self.logger.info("Property {} Changed correctly.".format(property_name))
        return True

    @aedt_exception_handler
    def change_clip_plane_position(self, clip_name, position):
        """Change the Clip Plane position.

        Parameters
        ----------
        clip_name : str
            clip plane name.
        position : list
            List of [X,Y,Z] position

        Returns
        -------
        bool
            ``True`` if successful.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        return self.change_property(clip_name, "Location", position)

    @aedt_exception_handler
    def colinear_heal(self, selection, tolerance=0.1):
        """Remove small edges of one or more primitives.

        Parameters
        ----------
        selection : str or list
            One or more primitives to heal.
        tolerance :  float, optional
            Tolerance value. The default is ``0.1``.

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.


        References
        ----------

        >>> oEditor.Heal


        Examples
        --------
        >>> from pyaedt import Hfss3dLayout
        >>> h3d=Hfss3dLayout(specified_version="2021.2")
        >>> h3d.modeler.layers.add_layer("TOP")
        >>> l1=h3d.modeler.primitives.create_line("TOP", [[0,0],[100,0]],  0.5, name="poly_1")
        >>> l2=h3d.modeler.primitives.create_line("TOP", [[100,0],[120,-35]],  0.5, name="poly_2")
        >>> h3d.modeler.unite([l1,l2])
        >>> h3d.modeler.colinear_heal("poly_2", 0.25)
        True
        """
        if isinstance(selection, str):
            selection = [selection]
        self.oeditor.Heal(
            [
                "NAME:Repair",
                "Selection:=",
                selection,
                "Type:=",
                "Colinear",
                "Tol:=",
                self.primitives.arg_with_dim(tolerance),
            ]
        )
        return True

    @aedt_exception_handler
    def expand(self, object_to_expand, size=1, expand_type="ROUND", replace_original=False):
        """Expand the object by a specific size.

        Parameters
        ----------
        object_to_expand : str
            Name of the object to expand.
        size : float, optional
            Size of the expansion. The default is ``1``.
        expand_type : str, optional
            Type of the expansion. Options are ``"ROUND"``, ``"MITER"``, and
            ``"CORNER"``. The default is ``"ROUND"``.
        replace_original : bool, optional
             Whether to replace the original object. The default is ``False``, in which case
             a new object is created.

        Returns
        -------
        str
            Name of the object.

        References
        ----------

        >>> oEditor.Expand


        Examples
        --------
        >>> from pyaedt import Hfss3dLayout
        >>> h3d=Hfss3dLayout(specified_version="2021.2")
        >>> h3d.modeler.layers.add_layer("TOP")
        >>> h3d.modeler.primitives.create_rectangle("TOP", [20,20],[50,50], name="rect_1")
        >>> h3d.modeler.primitives.create_line("TOP",[[25,25],[40,40]], name="line_3")
        >>> out1 = h3d.modeler.expand("line_3")
        >>> print(out1)
        line_4

        """
        layer = _retry_ntimes(10, self.oeditor.GetPropertyValue, "BaseElementTab", object_to_expand, "PlacementLayer")
        poly = self.oeditor.GetPolygonDef(object_to_expand).GetPoints()
        pos = [poly[0].GetX(), poly[0].GetY()]
        geom_names = self.oeditor.FindObjectsByPoint(self.oeditor.Point().Set(pos[0], pos[1]), layer)
        self.oeditor.Expand(
            self.primitives.arg_with_dim(size), expand_type, replace_original, ["NAME:elements", object_to_expand]
        )
        if not replace_original:
            new_geom_names = [
                i
                for i in self.oeditor.FindObjectsByPoint(self.oeditor.Point().Set(pos[0], pos[1]), layer)
                if i not in geom_names
            ]
            if self.primitives.is_outside_desktop:
                self.primitives._geometries[new_geom_names[0]] = Geometries3DLayout(self.primitives, new_geom_names[0])
            return new_geom_names[0]
        return object_to_expand

    @aedt_exception_handler
    def import_cadence_brd(self, brd_filename, edb_path=None, edb_name=None):
        """Import a Cadence board.

        Parameters
        ----------
        brd_filename : str
            Full path and name of the BRD file to import.
        edb_path : str, optional
            Path where the EDB is to be created. The default is ``None``, in which
            case the project directory is used.
        edb_name : str, optional
            name of the EDB. The default is ``None``, in which
            case the board name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oImportExport.ImportExtracta
        """
        if not edb_path:
            edb_path = self.projdir
        if not edb_name:
            name = os.path.basename(brd_filename)
            edb_name = os.path.splitext(name)[0]

        self._oimportexport.ImportExtracta(
            brd_filename, os.path.join(edb_path, edb_name + ".aedb"), os.path.join(edb_path, edb_name + ".xml")
        )
        self._app.oproject = self._app._desktop.GetActiveProject().GetName()
        self._app._odesign = None
        return True

    @aedt_exception_handler
    def modeler_variable(self, value):
        """Retrieve a modeler variable.

        Parameters
        ----------
        value :

        Returns
        -------

        """
        if isinstance(value, str if _pythonver >= 3 else basestring):
            return value
        else:
            return str(value) + self.model_units

    @aedt_exception_handler
    def import_ipc2581(self, ipc_filename, edb_path=None, edb_name=None):
        """Import an IPC file.

        Parameters
        ----------
        ipc_filename :
            Full path and name of the IPC file.
        edb_path : str, optional
            Path where the EDB is to be created. The default is ``None``, in which
            case the project directory is used.
        edb_name : str, optional
            Name of the EDB. The default is ``None``, in which
            case the board name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oImportExport.ImportIPC
        """
        if not edb_path:
            edb_path = self.projdir
        if not edb_name:
            name = os.path.basename(ipc_filename)
            edb_name = os.path.splitext(name)[0]

        self._oimportexport.ImportIPC(
            ipc_filename, os.path.join(edb_path, edb_name + ".aedb"), os.path.join(edb_path, edb_name + ".xml")
        )
        self._app.oproject = self._app._desktop.GetActiveProject().GetName()
        self._app._odesign = None
        return True

    @aedt_exception_handler
    def subtract(self, blank, tool):
        """Subtract objects from one or more names.

        Parameters
        ----------
        blank : str
            Name of the geometry to subtract from.
        tool : str or list
            One or more names of the geometries to subtract.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Subtract
        """
        vArg1 = ["NAME:primitives", blank]
        if isinstance(tool, list):
            for el in tool:
                vArg1.append(el)
        else:
            vArg1.append(tool)
        if self.oeditor is not None:
            self.oeditor.Subtract(vArg1)
        if isinstance(tool, list):
            for el in tool:
                if self.primitives.is_outside_desktop:
                    self.primitives._geometries.pop(el)
        else:
            if self.primitives.is_outside_desktop:
                self.primitives._geometries.pop(tool)
        return True

    @aedt_exception_handler
    def unite(self, objectlists):
        """Unite objects from names.

        Parameters
        ----------
        objectlists : list
            List of objects to unite.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Unite
        """
        vArg1 = ["NAME:primitives"]
        if len(objectlists) >= 2:
            for el in objectlists:
                vArg1.append(el)
            self.oeditor.Unite(vArg1)
            for el in objectlists:
                if not self.oeditor.FindObjects("Name", el):
                    if self.primitives.is_outside_desktop:
                        self.primitives._geometries.pop(el)
            return True
        else:
            self.logger.error("Input list must contain at least two elements.")
            return False

    @aedt_exception_handler
    def intersect(self, objectlists):
        """Intersect objects from names.

        Parameters
        ----------
        objectlists : list
            List of objects to intersect.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Intersect
        """
        vArg1 = ["NAME:primitives"]
        if len(objectlists) >= 2:
            for el in objectlists:
                vArg1.append(el)
            self.oeditor.Intersect(vArg1)
            for el in objectlists:
                if not self.oeditor.FindObjects("Name", el):
                    if self.primitives.is_outside_desktop:
                        self.primitives._geometries.pop(el)
            return True
        else:
            self.logger.error("Input list must contain at least two elements.")
            return False

    @aedt_exception_handler
    def duplicate(self, objectlists, count, direction_vector):
        """Duplicate one or more elements along a vector.

        Parameters
        ----------
        objectlists : list
            List of elements to duplicate.
        count : int

        direction_vector : list
            List of ``[x, y]`` coordinates for the direction vector.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Duplicate
        """
        if isinstance(objectlists, str):
            objectlists = [objectlists]
        self.oeditor.Duplicate(
            ["NAME:options", "count:=", count], ["NAME:elements", ",".join(objectlists)], direction_vector
        )
        return True

    @aedt_exception_handler
    def set_temperature_dependence(
            self,
            include_temperature_dependence=True,
            enable_feedback=True,
            ambient_temp=22,
            create_project_var=False,
    ):
        """Set the temperature dependence for the design.

        Parameters
        ----------
        include_temperature_dependence : bool, optional
            Set the temperature setting for the design. The default is ``True``.
        enable_feedback : bool, optional
            Enable the feedback. The default is ``True``.
        ambient_temp : float, optional
            Ambient temperature. The default is ``22``.
        create_project_var : bool, optional
            Whether to create a project variable for the ambient temperature.
            The default is ``False``. If ``True,`` ``$AmbientTemp`` is created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetTemperatureSettings
        """
        self.logger.info("Set the temperature dependence for the design.")
        if create_project_var:
            self._app.variable_manager["$AmbientTemp"] = str(ambient_temp) + "cel"
            var = "$AmbientTemp"
        else:
            var = str(ambient_temp) + "cel"
        vargs1 = [
            "NAME:TemperatureSettings",
            "IncludeTempDependence:=", include_temperature_dependence,
            "EnableFeedback:=", enable_feedback,
            "Temperature:=", var,
        ]
        try:
            self._odesign.SetTemperatureSettings(vargs1)
        except:
            self.logger.error("Failed to enable the temperature dependence.")
            return False
        else:
            self.logger.info("Assigned Objects Temperature")
            return True
