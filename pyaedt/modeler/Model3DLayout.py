import os

from ..generic.general_methods import retry_ntimes, aedt_exception_handler
from ..application.Variables import AEDT_units
from ..edb import Edb
from .Modeler import Modeler
from .Primitives3DLayout import Primitives3DLayout
from ..modules.LayerStackup import Layers
import sys

class Modeler3DLayout(Modeler):
    """ """
    def __init__(self, parent):
        self._parent = parent
        self.messenger.add_info_message("Loading Modeler")
        Modeler.__init__(self, parent)
        self.messenger.add_info_message("Modeler Loaded")
        self._primitivesDes = self._parent.project_name + self._parent.design_name
        edb_folder = os.path.join(self._parent.project_path, self._parent.project_name + ".aedb")
        edb_file = os.path.join(edb_folder, "edb.def")
        if os.path.exists(edb_file):
            self._mttime = os.path.getmtime(edb_file)
            self._edb = Edb(edb_folder, self._parent.design_name, True, self._parent._aedt_version, isaedtowned=True,
                            oproject=self._parent.oproject)
        else:
            self._mttime = 0
        self.messenger.add_info_message("EDB Loaded")

        self.layers = Layers(self._parent,self, roughnessunits="um")
        self.messenger.add_info_message("Layers Loaded")
        self._primitives = Primitives3DLayout(self._parent, self)
        self.messenger.add_info_message("Primitives Loaded")
        self.layers.refresh_all_layers()

        pass

    @property
    def edb(self):
        """ """
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
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def oeditor(self):
        """ """
        return self._parent.odesign.SetActiveEditor("Layout")

    @aedt_exception_handler
    def fit_all(self):
        """ """
        self.oeditor.ZoomToFit()

    @property
    def model_units(self):
        """ """
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
        """ """
        if self._primitivesDes != self._parent.project_name + self._parent.design_name:
            self._primitives = Primitives3DLayout(self._parent, self)
            self._primitivesDes = self._parent.project_name + self._parent.design_name
        return self._primitives

    @property
    def obounding_box(self):
        """ """
        return self.oeditor.GetModelBoundingBox()

    @aedt_exception_handler
    def import_cadence_brd(self, brd_filename, edb_path=None, edb_name=None):
        """

        Parameters
        ----------
        brd_filename :
            BRD Full File name
        edb_path :
            Path where EDB shall be created. if no path is provided, project dir will be used (Default value = None)
        edb_name :
            name of EDB. If no name is provided, brd name will be used (Default value = None)

        Returns
        -------

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
        """

        Parameters
        ----------
        ipc_filename :
            IPC Full File name
        edb_path :
            Path where EDB shall be created. if no path is provided, project dir will be used (Default value = None)
        edb_name :
            name of EDB. If no name is provided, brd name will be used (Default value = None)

        Returns
        -------

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
        """Subtract objects from names

        Parameters
        ----------
        blank :
            name of geometry from which subtract
        tool :
            name of geometry that will be subtracted. it can be a list

        Returns
        -------

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
        """Unite objects from names

        Parameters
        ----------
        objectlists :
            list of objects to unite

        Returns
        -------

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
            self.messenger.add_error_message("Input list must contain at least 2 elements")
            return False

    @aedt_exception_handler
    def intersect(self, objectlists):
        """Intersect objects from names

        Parameters
        ----------
        objectlists :
            list of objects to unite

        Returns
        -------

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
            self.messenger.add_error_message("Input list must contain at least 2 elements")
            return False