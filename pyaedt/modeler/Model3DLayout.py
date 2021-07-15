import os

from ..generic.general_methods import retry_ntimes, aedt_exception_handler
from ..application.Variables import AEDT_units
from ..edb import Edb
from .Modeler import Modeler
from .Primitives3DLayout import Primitives3DLayout, Geometries3DLayout
from ..modules.LayerStackup import Layers
import sys

class Modeler3DLayout(Modeler):
    """Modeler3DLayout class.

    Parameters
    ----------
    parent :

    """
    def __init__(self, parent):
        self._parent = parent
        self._messenger.add_info_message("Loading Modeler")
        Modeler.__init__(self, parent)
        self._messenger.add_info_message("Modeler Loaded")
        self._primitivesDes = self._parent.project_name + self._parent.design_name
        edb_folder = os.path.join(self._parent.project_path, self._parent.project_name + ".aedb")
        edb_file = os.path.join(edb_folder, "edb.def")
        self._edb = None
        if os.path.exists(edb_file):
            self._mttime = os.path.getmtime(edb_file)
            self._edb = Edb(edb_folder, self._parent.design_name, True, self._parent._aedt_version, isaedtowned=True,
                            oproject=self._parent.oproject)
        else:
            self._mttime = 0
        self._messenger.add_info_message("EDB Loaded")

        self.layers = Layers(self._parent,self, roughnessunits="um")
        self._messenger.add_info_message("Layers Loaded")
        self._primitives = Primitives3DLayout(self._parent, self)
        self._messenger.add_info_message("Primitives Loaded")
        self.layers.refresh_all_layers()

        pass

    @property
    def edb(self):
        """EBD.

        Returns
        -------
        :class:'pyaedt.Edb`
             EDB.

        """
        if os.name != "posix":
            edb_folder = os.path.join(self._parent.project_path, self._parent.project_name + ".aedb")
            edb_file = os.path.join(edb_folder, "edb.def")
            _mttime = os.path.getmtime(edb_file)
            if _mttime != self._mttime:
                if self._edb:
                    self._edb.close_edb()
                self._edb = Edb(edb_folder, self._parent.design_name, True, self._parent._aedt_version,
                                isaedtowned=True, oproject=self._parent.oproject)
                self._mttime = _mttime
        return self._edb

    @property
    def _messenger(self):
        """Messenger."""
        return self._parent._messenger

    @property
    def oeditor(self):
        """Layout."""
        return self._parent.odesign.SetActiveEditor("Layout")

    @aedt_exception_handler
    def fit_all(self):
        """Fit all."""
        self.oeditor.ZoomToFit()

    @property
    def model_units(self):
        """Model units."""
        return retry_ntimes(10, self.oeditor.GetActiveUnits)

    @model_units.setter
    def model_units(self, units):
        """

        Parameters
        ----------
        units :
            

        Returns
        -------

        """
        assert units in AEDT_units["Length"], "Invalid units string {0}".format(units)
        ''' Set the model units as a string e.g. "mm" '''
        self.oeditor.SetActivelUnits(
            [
                "NAME:Units Parameter",
                "Units:=", units,
                "Rescale:=", False
            ])

    @property
    def primitives(self):
        """Primitives."""
        if self._primitivesDes != self._parent.project_name + self._parent.design_name:
            self._primitives = Primitives3DLayout(self._parent, self)
            self._primitivesDes = self._parent.project_name + self._parent.design_name
        return self._primitives

    @property
    def obounding_box(self):
        """Bounding box."""
        return self.oeditor.GetModelBoundingBox()


    @aedt_exception_handler
    def colinear_heal(self, selection, tolerance=0.1):
        """Remove small edges of one or more primitives.

        Parameters
        ----------
        selection : str or list
            One or more primitives to heal.
        tolerance :  float, optional
            Tolerance value. The default is `0.1`.

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Hfss3dLayout
        >>> h3d=Hfss3dLayout(specified_version="2021.1")
        >>> h3d.modeler.layers.add_layer("TOP")
        >>> l1=h3d.modeler.primitives.create_line("TOP", [[0,0],[100,0]],  0.5, name="poly_1")
        >>> l2=h3d.modeler.primitives.create_line("TOP", [[100,0],[120,-35]],  0.5, name="poly_2")
        >>> h3d.modeler.unite([l1,l2])
        >>> h3d.modeler.colinear_heal("poly_2", 0.25)
        True

        """
        if isinstance(selection, str):
            selection = [selection]
        self.oeditor.Heal(["NAME:Repair", "Selection:=", selection, "Type:=", "Colinear", "Tol:=",
                           self.primitives.arg_with_dim(tolerance)])
        return True



    @aedt_exception_handler
    def expand(self, object_to_expand,  size=1, expand_type="ROUND", replace_original=False):
        """Expand the object by a specific size.

        Parameters
        ----------
        object_to_expand: str
            Name of the object to expand.
        size: float, optional
            Size of the expansion. The default is ``1``.
        expand_type: str, optional
            Type of the expansion. Options are ``"ROUND"``, ``"MITER"``, and
            ``"CORNER"``. The default is ``"ROUND"``.
        replace_original : bool, optional
             Whether to replace the original object. The default is ``False``, in which case
             a new object is created.

        Returns
        -------
        str
            Name of the object.

        Examples
        --------
        >>> from pyaedt import Hfss3dLayout
        >>> h3d=Hfss3dLayout(specified_version="2021.1")
        >>> h3d.modeler.layers.add_layer("TOP")
        >>> h3d.modeler.primitives.create_rectangle("TOP", [20,20],[50,50], name="rect_1")
        >>> h3d.modeler.primitives.create_line("TOP",[[25,25],[40,40]], name="line_3")
        >>> out1 = h3d.modeler.expand("line_3")
        >>> print(out1)
        line_4

        """
        layer = retry_ntimes(10, self.oeditor.GetPropertyValue, "BaseElementTab", object_to_expand, 'PlacementLayer')
        poly = self.oeditor.GetPolygonDef(object_to_expand).GetPoints()
        pos = [poly[0].GetX(), poly[0].GetY()]
        geom_names = self.oeditor.FindObjectsByPoint(self.oeditor.Point().Set(pos[0],pos[1]), layer)
        self.oeditor.Expand(self.primitives.arg_with_dim(size), expand_type, replace_original,
                            ["NAME:elements", object_to_expand])
        if not replace_original:
            new_geom_names = [i for i in self.oeditor.FindObjectsByPoint(self.oeditor.Point().Set(pos[0],pos[1]), layer) if i not in geom_names]
            if self.primitives.isoutsideDesktop:
                self.primitives._geometries[new_geom_names[0]] = Geometries3DLayout(self, new_geom_names[0])
            return new_geom_names[0]
        return object_to_expand


    @aedt_exception_handler
    def import_cadence_brd(self, brd_filename, edb_path=None, edb_name=None):
        """Import a cadence board.

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

        """
        if not edb_path:
            edb_path = self.projdir
        if not edb_name:
            name = os.path.basename(brd_filename)
            edb_name = os.path.splitext(name)[0]

        self.oimportexport.ImportExtracta(brd_filename, os.path.join(edb_path, edb_name + ".aedb"),
                                          os.path.join(edb_path, edb_name + ".xml"))
        self._parent.oproject = self.desktop.GetActiveProject().GetName()
        self._parent.odesign = None

        # name = self._parent.project_name
        # prjpath = self._parent.project_path
        # self._parent.close_project(self._parent.project_name, True)
        #
        # self._parent.load_project(os.path.join(prjpath, name+".aedt"))

        return True

    @aedt_exception_handler
    def modeler_variable(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        if isinstance(value, str if int(sys.version_info[0]) >= 3 else basestring):
            return value
        else:
            return str(value) + self.model_units

    @aedt_exception_handler
    def import_ipc2581(self, ipc_filename, edb_path=None, edb_name=None):
        """Import an IPC file.

        Parameters
        ----------
        ipc_filename :
            Full path and name of the IPC file to import.
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

        """
        if not edb_path:
            edb_path = self.projdir
        if not edb_name:
            name = os.path.basename(ipc_filename)
            edb_name = os.path.splitext(name)[0]

        self.oimportexport.ImportIPC(ipc_filename, os.path.join(edb_path, edb_name + ".aedb"),
                                     os.path.join(edb_path, edb_name + ".xml"))
        self._parent.oproject = self.desktop.GetActiveProject().GetName()
        self._parent.odesign = None
        return True

    @aedt_exception_handler
    def subtract(self, blank, tool):
        """Subtract objects from one or more names.

        Parameters
        ----------
        blank : str
            Name of the geometry to subtract from.
        tool : str or list
            One or more names of the geometries to be subtracted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        vArg1 = ['NAME:primitives', blank]
        if type(tool) is list:
            for el in tool:
                vArg1.append(el)
        else:
            vArg1.append(tool)
        if self.oeditor is not None:
            self.oeditor.Subtract(vArg1)
        if type(tool) is list:
            for el in tool:
                if self.primitives.isoutsideDesktop:
                    self.primitives._geometries.pop(el)
        else:
            if self.primitives.isoutsideDesktop:
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

        """
        vArg1 = ['NAME:primitives']
        if len(objectlists) >= 2:
            for el in objectlists:
                vArg1.append(el)
            self.oeditor.Unite(vArg1)
            for el in objectlists:
                if not self.oeditor.FindObjects("Name", el):
                    if self.primitives.isoutsideDesktop:
                        self.primitives._geometries.pop(el)
            return True
        else:
            self._messenger.add_error_message("Input list must contain at least 2 elements")
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

        """
        vArg1 = ['NAME:primitives']
        if len(objectlists) >= 2:
            for el in objectlists:
                vArg1.append(el)
            self.oeditor.Intersect(vArg1)
            for el in objectlists:
                if not self.oeditor.FindObjects("Name", el):
                    if self.primitives.isoutsideDesktop:
                        self.primitives._geometries.pop(el)
            return True
        else:
            self._messenger.add_error_message("Input list must contain at least 2 elements")
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
            List of `[x, y]` coordinates for the direction vector.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if isinstance(objectlists, str):
            objectlists = [objectlists]
        self.oeditor.Duplicate(
            [
                "NAME:options",
                "count:="	, count
            ],
            [
                "NAME:elements",
                ",".join(objectlists)
            ], direction_vector)
        return True
