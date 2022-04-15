"""
This module contains these classes: ``Design`` and ``DesignCache``.

This module provides all functionalities for basic project information and objects.
These classes are inherited in the main tool class.

"""

from __future__ import absolute_import  # noreorder

import gc
import json
import os
import random
import re
import shutil
import string
import sys
import time
import warnings
from collections import OrderedDict

from pyaedt.application.design_solutions import DesignSolution
from pyaedt.application.design_solutions import HFSSDesignSolution
from pyaedt.application.design_solutions import IcepakDesignSolution
from pyaedt.application.design_solutions import Maxwell2DDesignSolution
from pyaedt.application.design_solutions import model_names
from pyaedt.application.design_solutions import RmXprtDesignSolution
from pyaedt.application.design_solutions import solutions_defaults
from pyaedt.application.Variables import DataSet
from pyaedt.application.Variables import VariableManager
from pyaedt.desktop import Desktop
from pyaedt.desktop import exception_to_desktop
from pyaedt.desktop import get_version_env_variable
from pyaedt.desktop import release_desktop
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.constants import unit_system
from pyaedt.generic.DataHandlers import variation_string_to_dict
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import write_csv
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
from pyaedt.modules.Boundary import BoundaryObject

if sys.version_info.major > 2:
    import base64


def list_difference(list1, list2):
    return list(set(list1) - set(list2))


class DesignCache(object):
    """Analyzes the differences in the state of a design between two points in time.

    The contents of the design tracked in the message manager currently are:

        * global-level messages
        * project-level messages
        * design-level messages

    Parameters
    ----------
    parent : str
        Name of the parent object.

    """

    def __init__(self, app):
        self._app = app
        self._allow_errors_local = []
        self._allow_errors_global = []
        self.clear()
        self._snapshot = self.design_snapshot()

    @property
    def allowed_error_messages(self):
        """Add this error message to the ignored error messages."""
        return self._allow_errors_global + self._allow_errors_local

    def ignore_error_message_local(self, msg):
        """Add this error message to the ignored local error messages."""
        self._allow_errors_local.append("[error] {}".format(msg))

    def ignore_error_message_global(self, msg):
        """Add this error message to the ignored global error messages."""
        self._allow_errors_global.append("[error] {}".format(msg))

    @property
    def no_change(self):
        """Check if the design snapshot is unchanged since the last update.

        Returns
        --------
        bool
            ``True`` if the design snapshot is unchanged since the last
            update, ``False`` otherwise.
        """
        return self._no_change

    @property
    def delta_global_messages(self):
        """Check for any new or missing global-level messages since the last update.

        Returns
        -------
        list of str
            List of any new or missing global-level messages since the last update.
        """
        return self._delta_global_messages

    @property
    def delta_project_messages(self):
        """Check for any new or missing project-level messages since the last update.

        Returns
        -------
        list of str
            List of any new or missing project-level messages since the last update.
        """
        return self._delta_global_messages

    @property
    def delta_design_messages(self):
        """Check for any new or missing design-level messages since the last update.

        Returns
        -------
        list of str
            List of any new or missing design-level messages since the last update.
        """
        return self._delta_design_messages

    @property
    def delta_error_messages(self):
        """Check for any new or missing error messages since the last update.

        Returns
        -------
        list of str
            List of any new or missing error messages since the last update.
        """
        return self._new_error_messages

    @property
    def no_new_messages(self):
        """Check for any new messages that have appeared since the last update or since the message manager was cleared.

        Returns
        -------
        bool
            ``True`` if new messages have appeared since the last
            update or since the message manager was cleared, ``False``
            otherwise.
        """
        return not bool(self._delta_messages)

    @property
    def no_new_errors(self):
        """Check for any new error messages that have appeared since the last uodate.

        Returns
        -------
        bool
            ``True`` if new error messages have appeared since the
            last update, ``False`` otherwise.
        """
        return not bool(self._new_error_messages)

    @property
    def no_new_warnings(self):
        """Check for any new warning messages that have appeared since the last uodate.

        Returns
        -------
        bool
            ``True`` if new error messages have appeared since the
            last update, ``False`` otherwise.
        """
        return not bool(self._new_warning_messages)

    @property
    def no_change(self):
        """Check if cache elements are unchanged since the last update.

        Returns
        -------
        bool
            ``True`` if the cache elements are unchanged since the last update,
            ``Fasle`` otherwise.
        """
        return self.no_new_messages

    def design_snapshot(self):
        """Retrieve the design snapshot.

        Returns
        -------
        type
            Snapshot object.
        """
        snapshot = {
            "Solids:": self._app.modeler.solid_names,
            "Lines:": self._app.modeler.line_names,
            "Sheets": self._app.modeler.sheet_names,
            "DesignName": self._app.design_name,
        }
        return snapshot

    def clear(self):
        """Clear cached values."""
        self._messages_global_level = []
        self._messages_project_level = []
        self._messages_design_level = []

    def update(self):
        """Update the current state.

        Retrieve the current state values from the design and perform
        a delta calculation with the cached values. Then replace the
        cached values with the current values.

        .. note::
           The update is done automatically when the property
           ``"no_change"`` is accessed.
        """

        messages = self._app._logger.messages

        # Check whether the design snapshot has changed since the last update
        new_snapshot = self.design_snapshot()
        if new_snapshot == self._snapshot:
            self._no_change = True
        else:
            self._no_change = False

        self._snapshot = new_snapshot

        self._delta_global_messages = list_difference(messages.global_level, self._messages_global_level)
        self._delta_project_messages = list_difference(messages.project_level, self._messages_project_level)
        self._delta_design_messages = list_difference(messages.design_level, self._messages_design_level)
        self._delta_messages_unfiltered = (
            self._delta_global_messages + self._delta_project_messages + self._delta_design_messages
        )

        # filter out allowed messages
        self._delta_messages = []
        for msg in self._delta_messages_unfiltered:
            mask = False
            allowed_errors = self._allow_errors_local + self._allow_errors_global
            for allowed in allowed_errors:
                if msg.find(allowed) == 0:
                    mask = True
                    break
            if not mask:
                self._delta_messages.append(msg)

        self._new_error_messages = [msg for msg in self._delta_messages if msg.find("[error]") == 0]
        self._new_warning_messages = [msg for msg in self._delta_messages if msg.find("[warning]") == 0]

        self._messages_global_level = messages.global_level
        self._messages_project_level = messages.project_level
        self._messages_design_level = messages.design_level

        self._allow_errors_local = []

        return self


class Design(object):
    """Contains all functions and objects connected to the active project and design.

    This class is inherited in the caller application and is accessible through it (for
    example, ``hfss.method_name``.

    Parameters
    ----------
    design_type : str
        Type of the design.
    project_name : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    design_name : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT launches in graphical mode.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default
        is ``False``.

    """

    def __str__(self):
        pyaedt_details = "      pyaedt API\n"
        pyaedt_details += "pyaedt running AEDT Version {} \n".format(self._aedt_version)
        pyaedt_details += "Running {} tool in AEDT\n".format(self.design_type)
        pyaedt_details += "Solution Type: {} \n".format(self.solution_type)
        pyaedt_details += "Project Name: {} Design Name {} \n".format(self.project_name, self.design_name)
        pyaedt_details += 'Project Path: "{}" \n'.format(self.project_path)
        return pyaedt_details

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            exception_to_desktop(ex_value, ex_traceback)
        if self.release_on_exit:
            self.release_desktop(self.close_on_exit, self.close_on_exit)

    def __enter__(self):
        pass

    @pyaedt_function_handler()
    def __getitem__(self, variable_name):
        return self.variable_manager[variable_name].string_value

    @pyaedt_function_handler()
    def __setitem__(self, variable_name, variable_value):
        self.variable_manager[variable_name] = variable_value
        return True

    def __init__(
        self,
        design_type,
        project_name=None,
        design_name=None,
        solution_type=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=False,
        close_on_exit=False,
        student_version=False,
    ):
        self._init_variables()
        # Get Desktop from global Desktop Environment
        self._project_dictionary = OrderedDict()
        self.boundaries = []
        self.project_datasets = {}
        self.design_datasets = {}
        main_module = sys.modules["__main__"]
        self.close_on_exit = close_on_exit

        if "pyaedt_initialized" not in dir(main_module):
            desktop = Desktop(specified_version, non_graphical, new_desktop_session, close_on_exit, student_version)
            self._logger = desktop.logger
            self.release_on_exit = True
        else:
            self._logger = main_module.aedt_logger
            self.release_on_exit = False

        self.student_version = main_module.student_version
        self._mttime = None
        self._design_type = design_type
        self._desktop = main_module.oDesktop
        self._desktop_install_dir = main_module.sDesktopinstallDirectory
        self._aedt_version = self._desktop.GetVersion()[0:6]
        self._odesign = None
        self._oproject = None
        self._design_type = design_type

        if design_type == "HFSS":
            self.design_solutions = HFSSDesignSolution(None, design_type, self._aedt_version)
        elif design_type == "Icepak":
            self.design_solutions = IcepakDesignSolution(None, design_type, self._aedt_version)
        elif design_type == "Maxwell 2D":
            self.design_solutions = Maxwell2DDesignSolution(None, design_type, self._aedt_version)
        elif design_type == "RMxprtSolution" or design_type == "ModelCreation":
            self.design_solutions = RmXprtDesignSolution(None, design_type, self._aedt_version)
        else:
            self.design_solutions = DesignSolution(None, design_type, self._aedt_version)
        self.design_solutions._solution_type = solution_type
        self.oproject = project_name
        self.odesign = design_name
        self.design_solutions._odesign = self.odesign
        if solution_type:
            self.design_solutions.solution_type = solution_type
        self._oimport_export = self._desktop.GetTool("ImportExport")
        self._variable_manager = VariableManager(self)
        self.project_datasets = self._get_project_datasets()
        self.design_datasets = self._get_design_datasets()
        _mtime = self.project_time_stamp

    @property
    def odesktop(self):
        """AEDT instance containing all projects and designs.

        Examples
        --------
        Get the COM object representing the desktop.

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.odesktop
        <class 'win32com.client.CDispatch'>
        """
        return self._desktop

    @property
    def oimport_export(self):
        """Import/Export Manager Module.

        References
        ----------

        >>> oDesktop.GetTool("ImportExport")"""
        return self._oimport_export

    @property
    def odefinition_manager(self):
        """Definition Manager Module.

        References
        ----------

        >>> oDefinitionManager = oProject.GetDefinitionManager()
        """
        return self.oproject.GetDefinitionManager()

    @property
    def omaterial_manager(self):
        """Material Manager Module.

        References
        ----------

        >>> oMaterialManager = oDefinitionManager.GetManager("Material")
        """
        return self.odefinition_manager.GetManager("Material")

    @pyaedt_function_handler()
    def __delitem__(self, key):
        """Implement destructor with array name or index."""
        del self._variable_manager[key]

    def _init_variables(self):
        self._oboundary = None
        self._oimport_export = None
        self._ooptimetrics = None
        self._ooutput_variable = None
        self._oanalysis = None
        self._modeler = None
        self._post = None
        self._materials = None
        self._variable_manager = None
        self.parametrics = None
        self.optimizations = None
        self.native_components = None
        self._mesh = None

    @property
    def logger(self):
        """Logger for the design.

        Returns
        -------
        :class:`pyaedt.aedt_logger.AedtLogger`
        """
        return self._logger

    # TODO Project properties are set at the beginning
    # but after they are never updated along the different project steps.

    @property
    def project_properies(self):
        """Project properties.

        Returns
        -------
        dict
            Dictionary of the project properties.
        """
        start = time.time()
        if not self._project_dictionary and os.path.exists(self.project_file):
            self._project_dictionary = load_entire_aedt_file(self.project_file)
            self._logger.info("aedt file load time {}".format(time.time() - start))
        return self._project_dictionary

    @property
    def design_properties(self, design_name=None):
        """Design properties.

        Parameters
        ----------
        design_name : str, optional
            Name of the design to select. The default is ``None``, in
            which case an attempt is made to get an active design. If no
            designs are present, an empty design is created.

        Returns
        -------
        dict
           Dictionary of the design properties.

        """
        if not design_name:
            design_name = self.design_name
        try:
            if model_names[self._design_type] in self.project_properies["AnsoftProject"]:
                designs = self.project_properies["AnsoftProject"][model_names[self._design_type]]
                if isinstance(designs, list):
                    for design in designs:
                        if design["Name"] == design_name:
                            return design
                else:
                    if designs["Name"] == design_name:
                        return designs
        except:
            return OrderedDict()

    @property
    def aedt_version_id(self):
        """AEDT version.

        Returns
        -------
        str
            Version of AEDT.

        References
        ----------

        >>> oDesktop.GetVersion()
        """
        version = self.odesktop.GetVersion()
        return get_version_env_variable(version)

    @property
    def design_name(self):
        """Design name.

        Returns
        -------
        str
            Name of the parent AEDT design.

        References
        ----------

        >>> oDesign.GetName
        >>> oDesign.RenameDesignInstance

        Examples
        --------
        Set the design name.

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.design_name = 'new_design'
        """
        if not self.odesign:
            return None
        name = self.odesign.GetName()
        if ";" in name:
            return name.split(";")[1]
        else:
            return name

    @design_name.setter
    @pyaedt_function_handler()
    def design_name(self, new_name):
        if ";" in new_name:
            new_name = new_name.split(";")[1]

        self.odesign.RenameDesignInstance(self.design_name, new_name)
        timeout = 5.0
        timestep = 0.1
        while new_name not in [i.GetName() for i in list(self._oproject.GetDesigns())]:
            time.sleep(timestep)
            timeout -= timestep
            assert timeout >= 0

    @property
    def design_list(self):
        """Design list.

        Returns
        -------
        list
            List of the designs.

        References
        ----------

        >>> oProject.GetTopDesignList()
        """
        deslist = list(self.oproject.GetTopDesignList())
        updateddeslist = []
        for el in deslist:
            m = re.search(r"[^;]+$", el)
            updateddeslist.append(m.group(0))
        return updateddeslist

    @property
    def design_type(self):
        """Design type.

        Options are ``"Circuit Design"``, ``"Emit"``, ``"HFSS"``,
        ``"HFSS 3D Layout Design"``, ``"Icepak"``, ``"Maxwell 2D"``,
        ``"Maxwell 3D"``, ``"Maxwell Circuit"``, ``"Mechanical"``, ``"ModelCreation"``,
        ``"Q2D Extractor"``, ``"Q3D Extractor"``, ``"RMxprtSolution"``,
        and ``"Twin Builder"``.

        Returns
        -------
        str
            Type of the design. See above for a list of possible return values.

        """
        return self._design_type

    @property
    def project_name(self):
        """Project name.

        Returns
        -------
        str
            Name of the project.

        References
        ----------

        >>> oProject.GetName
        """
        if self._oproject:
            try:
                return self._oproject.GetName()
            except:
                return None
        else:
            return None

    @property
    def project_list(self):
        """Project list.

        Returns
        -------
        list
            List of projects.

        References
        ----------

        >>> oDesktop.GetProjectList
        """
        return list(self.odesktop.GetProjectList())

    @property
    def project_path(self):
        """Project path.

        Returns
        -------
        str
            Path to the project.

        References
        ----------

        >>> oProject.GetPath
        """
        return os.path.normpath(self.oproject.GetPath())

    @property
    def project_time_stamp(self):
        """Return Project time stamp."""
        if os.path.exists(self.project_file):
            self._mttime = os.path.getmtime(self.project_file)
        else:
            self._mttime = 0
        return self._mttime

    @property
    def project_timestamp_changed(self):
        """Return a bool if time stamp changed or not."""
        old_time = self._mttime
        return old_time != self.project_time_stamp

    @property
    def project_file(self):
        """Project name and path.

        Returns
        -------
        str
            Full absolute name and path for the project.

        """
        return os.path.join(self.project_path, self.project_name + ".aedt")

    @property
    def lock_file(self):
        """Lock file.

        Returns
        -------
        str
            Full absolute name and path for the project's lock file.

        """
        return os.path.join(self.project_path, self.project_name + ".aedt.lock")

    @property
    def results_directory(self):
        """Results directory.

        Returns
        -------
        str
            Full absolute path for the ``aedtresults`` directory.

        """
        return os.path.join(self.project_path, self.project_name + ".aedtresults")

    @property
    def solution_type(self):
        """Solution type.

        Returns
        -------
        str
            Type of the solution.

        References
        ----------

        >>> oDesign.GetSolutionType
        >>> oDesign.SetSolutionType
        """
        return self.design_solutions.solution_type

    @solution_type.setter
    @pyaedt_function_handler()
    def solution_type(self, soltype):
        self.design_solutions.solution_type = soltype

    @property
    def valid_design(self):
        """Valid design.

        Returns
        -------
        bool
            ``True`` when the project and design exists, ``False`` otherwise.

        """
        if self._oproject and self._odesign:
            return True
        else:
            return False

    @property
    def personallib(self):
        """PersonalLib directory.

        Returns
        -------
        str
            Full absolute path for the ``PersonalLib`` directory.

        References
        ----------

        >>> oDesktop.GetPersonalLibDirectory
        """
        return os.path.normpath(self.odesktop.GetPersonalLibDirectory())

    @property
    def userlib(self):
        """UserLib directory.

        Returns
        -------
        str
            Full absolute path for the ``UserLib`` directory.

        References
        ----------

        >>> oDesktop.GetUserLibDirectory
        """
        return os.path.normpath(self.odesktop.GetUserLibDirectory())

    @property
    def syslib(self):
        """SysLib directory.

        Returns
        -------
        str
            Full absolute path for the ``SysLib`` directory.

        References
        ----------

        >>> oDesktop.GetLibraryDirectory
        """
        return os.path.normpath(self.odesktop.GetLibraryDirectory())

    @property
    def src_dir(self):
        """Source directory for Python.

        Returns
        -------
        str
            Full absolute path for the ``python`` directory.

        """
        return os.path.dirname(os.path.realpath(__file__))

    @property
    def pyaedt_dir(self):
        """PyAEDT directory.

        Returns
        -------
        str
           Full absolute path for the ``pyaedt`` directory.

        """
        return os.path.realpath(os.path.join(self.src_dir, ".."))

    @property
    def library_list(self):
        """Library list.

        Returns
        -------
        list
            List of libraries: ``[syslib, userlib, personallib]``.

        """
        return [self.syslib, self.userlib, self.personallib]

    @property
    def temp_directory(self):
        """Path to the temporary directory.

        Returns
        -------
        str
            Full absolute path for the ``temp`` directory.

        """
        return os.path.normpath(self.odesktop.GetTempDirectory())

    @property
    def toolkit_directory(self):
        """Path to the toolkit directory.


        Returns
        -------
        str
            Full absolute path for the ``pyaedt`` directory for this project.
            If this directory does not exist, it is created.
        """

        toolkit_directory = os.path.join(self.project_path, self.project_name + ".pyaedt")
        if not os.path.isdir(toolkit_directory):
            os.mkdir(toolkit_directory)
        return toolkit_directory

    @property
    def working_directory(self):
        """Path to the working directory.

        Returns
        -------
        str
             Full absolute path for the project's working directory.
             If this directory does not exist, it is created.

        """
        working_directory = os.path.join(self.toolkit_directory, self.design_name)
        if not os.path.isdir(working_directory):
            os.mkdir(working_directory)
        return working_directory

    @property
    def default_solution_type(self):
        """Default solution type.

        Returns
        -------
        str
           Default for the solution type.

        """
        return solutions_defaults[self._design_type]

    @property
    def odesign(self):
        """Design.

        Returns
        -------
        type
            Design object.

        References
        ----------

        >>> oProject.SetActiveDesign
        >>> oProject.InsertDesign
        """
        return self._odesign

    @odesign.setter
    @pyaedt_function_handler()
    def odesign(self, des_name):
        warning_msg = None
        activedes = des_name
        if des_name:
            if self._assert_consistent_design_type(des_name) == des_name:
                self._insert_design(self._design_type, design_name=des_name)
        else:
            if self.design_list:
                self._odesign = self._oproject.GetDesign(self.design_list[0])
                if not self._check_design_consistency():
                    count_consistent_designs = 0
                    for des in self.design_list:
                        self._odesign = self._oproject.SetActiveDesign(des)
                        if self._check_design_consistency():
                            count_consistent_designs += 1
                            activedes = des
                    if count_consistent_designs != 1:
                        warning_msg = "No consistent unique design is present. Inserting a new design."
                    else:
                        self._odesign = self.oproject.SetActiveDesign(activedes)
                        self.logger.info("Active Design set to {}".format(activedes))
                else:
                    self._odesign = self._oproject.SetActiveDesign(self.design_list[0])
                    self.logger.info("Active design is set to {}".format(self.design_list[0]))
            else:
                warning_msg = "No design is present. Inserting a new design."

            if warning_msg:
                self.logger.info(warning_msg)
                self._insert_design(self._design_type)
        self.boundaries = self._get_boundaries_data()

    @property
    def oproject(self):
        """Project property.

        Returns
        -------
            Project object

        References
        ----------

        >>> oDesktop.GetActiveProject
        >>> oDesktop.SetActiveProject
        >>> oDesktop.NewProject
        """
        return self._oproject

    @oproject.setter
    @pyaedt_function_handler()
    def oproject(self, proj_name=None):
        if not proj_name:
            self._oproject = self.odesktop.GetActiveProject()
            if self._oproject:
                self.logger.info(
                    "No project is defined. Project {} exists and has been read.".format(self._oproject.GetName())
                )
        else:
            if proj_name in self.odesktop.GetProjectList():
                self._oproject = self.odesktop.SetActiveProject(proj_name)
            elif os.path.exists(proj_name):
                if ".aedtz" in proj_name:
                    name = self._generate_unique_project_name()

                    path = os.path.dirname(proj_name)
                    self.odesktop.RestoreProjectArchive(proj_name, os.path.join(path, name), True, True)
                    time.sleep(0.5)
                    proj = self.odesktop.GetActiveProject()
                    self.logger.info("Archive {} has been restored to project {}".format(proj_name, proj.GetName()))
                elif ".def" in proj_name or proj_name[-5:] == ".aedb":
                    oTool = self.odesktop.GetTool("ImportExport")
                    if ".def" in proj_name:
                        oTool.ImportEDB(proj_name)
                    else:
                        oTool.ImportEDB(os.path.join(proj_name, "edb.def"))
                    proj = self.odesktop.GetActiveProject()
                    proj.Save()
                    self.logger.info("EDB folder %s has been imported to project %s", proj_name, proj.GetName())
                else:
                    assert not os.path.exists(
                        proj_name + ".lock"
                    ), "Project is locked. Close or remove the lock before proceeding."
                    proj = self.odesktop.OpenProject(proj_name)
                    self.logger.info("Project %s has been opened.", proj.GetName())
                    time.sleep(0.5)
                self._oproject = proj
            else:
                self._oproject = self.odesktop.NewProject()
                if ".aedt" in proj_name:
                    self._oproject.Rename(proj_name, True)
                else:
                    self._oproject.Rename(os.path.join(self.project_path, proj_name + ".aedt"), True)
                self.logger.info("Project %s has been created.", self._oproject.GetName())
        if not self._oproject:
            self._oproject = self.odesktop.NewProject()
            self.logger.info("Project %s has been created.", self._oproject.GetName())

    @property
    def desktop_install_dir(self):
        """AEDT installation directory.

        Returns
        -------
        str
            AEDT installation directory.

        """
        return self._desktop_install_dir

    @pyaedt_function_handler()
    def get_oo_name(self, aedt_object, object_name):
        """Return the Object Oriented AEDT Properties names.

        Parameters
        ----------
        aedt_object : object
            AEDT Object on which search for property. It can be any oProperty (ex. oDesign).
        object_name : str
            Path to the object list. Example `"DesginName\Boundaries"`.

        Returns
        -------
        list
            Values returned by method if any.
        """
        try:
            return aedt_object.GetChildObject(object_name).GetChildNames()
        except:
            return False

    @pyaedt_function_handler()
    def get_oo_object(self, aedt_object, object_name):
        """Return the Object Oriented AEDT Object.

        Parameters
        ----------
        aedt_object : object
            AEDT Object on which search for property. It can be any oProperty (ex. oDesign).
        object_name : str
            Path to the object list. Example `"DesginName\Boundaries"`.

        Returns
        -------
        object
            Aedt Object if Any.
        """
        try:
            return aedt_object.GetChildObject(object_name)
        except:
            return False

    @pyaedt_function_handler()
    def get_oo_properties(self, aedt_object, object_name):
        """Return the Object Oriented AEDT Object Properties.

        Parameters
        ----------
        aedt_object : object
            AEDT Object on which search for property. It can be any oProperty (ex. oDesign).
        object_name : str
            Path to the object list. Example `"DesginName\Boundaries"`.

        Returns
        -------
        list
            Values returned by method if any.
        """
        try:
            return aedt_object.GetChildObject(object_name).GetPropNames()
        except:
            return False

    @pyaedt_function_handler()
    def get_oo_property_value(self, aedt_object, object_name, prop_name):
        """Return the Object Oriented AEDT Object Properties.

        Parameters
        ----------
        aedt_object : object
            AEDT Object on which search for property. It can be any oProperty (ex. oDesign).
        object_name : str
            Path to the object list. Example `"DesginName\Boundaries"`.

        Returns
        -------
        list
            Values returned by method if any.
        """
        try:
            return aedt_object.GetChildObject(object_name).GetPropValue(prop_name)
        except:
            return False

    @pyaedt_function_handler()
    def export_profile(self, setup_name, variation_string="", file_path=None):
        """Export a solution profile to a PROF file.

        Parameters
        ----------
        setup_name : str
            Setup name. For example, ``'Setup1'``.
        variation_string : str
            Variation string with values. For example, ``'radius=3mm'``.
        file_path : str, optional
            Full path to the PROF file. The default is ``None``, in which case
            the working directory is used.


        Returns
        -------
        str
            File path if created.

        References
        ----------

        >>> oDesign.ExportProfile
        """

        if not file_path:
            file_path = os.path.join(self.working_directory, generate_unique_name("Profile") + ".prop")
        if not variation_string:
            val_str = []
            for el, val in self.available_variations.nominal_w_values_dict.items():
                val_str.append("{}={}".format(el, val))
            variation_string = ",".join(val_str)
        if self.design_type == "2D Extractor":
            for setup in self.setups:
                if setup.name == setup_name:
                    if "CGDataBlock" in setup.props:
                        file_path = os.path.splitext(file_path)[0] + "CG" + os.path.splitext(file_path)[1]
                        self.odesign.ExportProfile(setup_name, variation_string, "CG", file_path, True)
                        self.logger.info("Exported Profile to file {}".format(file_path))
                    if "RLDataBlock" in setup.props:
                        file_path = os.path.splitext(file_path)[0] + "RL" + os.path.splitext(file_path)[1]
                        self.odesign.ExportProfile(setup_name, variation_string, "RL", file_path, True)
                        self.logger.info("Exported Profile to file {}".format(file_path))
                    break
        elif self.design_type == "Q3D Extractor":
            for setup in self.setups:
                if setup.name == setup_name:
                    if "Cap" in setup.props:
                        file_path = os.path.splitext(file_path)[0] + "CG" + os.path.splitext(file_path)[1]
                        self.odesign.ExportProfile(setup_name, variation_string, "CG", file_path, True)
                        self.logger.info("Exported Profile to file {}".format(file_path))
                    if "AC" in setup.props:
                        file_path = os.path.splitext(file_path)[0] + "ACRL" + os.path.splitext(file_path)[1]
                        self.odesign.ExportProfile(setup_name, variation_string, "AC RL", file_path, True)
                        self.logger.info("Exported Profile to file {}".format(file_path))
                    if "DC" in setup.props:
                        file_path = os.path.splitext(file_path)[0] + "DC" + os.path.splitext(file_path)[1]
                        self.odesign.ExportProfile(setup_name, variation_string, "DC RL", file_path, True)
                        self.logger.info("Exported Profile to file {}".format(file_path))

                    break
        else:
            try:
                self.odesign.ExportProfile(setup_name, variation_string, file_path)
            except:
                self.odesign.ExportProfile(setup_name, variation_string, file_path, True)
            self.logger.info("Exported Profile to file {}".format(file_path))
        return file_path

    @pyaedt_function_handler()
    def add_info_message(self, message_text, message_type=None):
        """Add a type 0 "Info" message to either the global, active project, or active design
        level of the message manager tree.

        Also add an "Info" message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the info message.
        message_type : str, optional
            Level to add the "Info" message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the "Info" message gets added to the ``"Design"``
            level.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.logger.info("Global info message")
        >>> hfss.logger.project.info("Project info message")
        >>> hfss.logger.design.info("Design info message")

        """
        warnings.warn(
            "`add_info_message` is deprecated. Use `logger.design_logger.info` instead.",
            DeprecationWarning,
        )
        if message_type.lower() == "project":
            self.logger.project.info(message_text)
        elif message_type.lower() == "design":
            self.logger.design.info(message_text)
        else:
            self.logger.info(message_text)
        return True

    @pyaedt_function_handler()
    def add_warning_message(self, message_text, message_type=None):
        """Add a type 0 "Warning" message to either the global, active project, or active design
        level of the message manager tree.

        Also add an "Warning" message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the "Warning" message.
        message_type : str, optional
            Level to add the "Warning" message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the "Warning" message gets added to the ``"Design"``
            level.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.logger.warning("Global warning message", "Global")
        >>> hfss.logger.project.warning("Project warning message", "Project")
        >>> hfss.logger.design.warning("Design warning message")

        """
        warnings.warn(
            "`add_warning_message` is deprecated. Use `logger.design_logger.warning` instead.",
            DeprecationWarning,
        )

        if message_type.lower() == "project":
            self.logger.project.warning(message_text)
        elif message_type.lower() == "design":
            self.logger.design.warning(message_text)
        else:
            self.logger.warning(message_text)
        return True

    @pyaedt_function_handler()
    def add_error_message(self, message_text, message_type=None):
        """Add a type 0 "Error" message to either the global, active project, or active design
        level of the message mmanager tree.

        Also add an "Error" message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the "Error" message.
        message_type : str, optional
            Level to add the "Error" message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the "Error" message gets added to the ``"Design"``
            level.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.logger.error("Global error message", "Global")
        >>> hfss.logger.project.error("Project error message", "Project")
        >>> hfss.logger.design.error("Design error message")

        """
        warnings.warn(
            "`add_error_message` is deprecated. Use `logger.design_logger.error` instead.",
            DeprecationWarning,
        )

        if message_type.lower() == "project":
            self.logger.project.error(message_text)
        elif message_type.lower() == "design":
            self.logger.design.error(message_text)
        else:
            self.logger.error(message_text)
        return True

    @property
    def variable_manager(self):
        """Variable manager for creating and managing project design and postprocessing variables.

        Returns
        -------
        pyaedt.application.Variables.VariableManager

        """
        return self._variable_manager

    @pyaedt_function_handler()
    def _arg_with_units(self, value, units=None):
        """Dimension argument.

        Parameters
        ----------
        value :

        sUnits : optional
             The default is ``None``.

        Returns
        -------
        str
            String concatenating the value and unit.

        """
        if units is None:
            units = self.modeler.model_units
        if type(value) is str:
            try:
                float(value)
                val = "{0}{1}".format(value, units)
            except:
                val = value
        else:
            val = "{0}{1}".format(value, units)
        return val

    @pyaedt_function_handler()
    def set_license_type(self, license_type="Pool"):
        """Change the license type between ``"Pack"`` and ``"Pool"``.

        Parameters
        ----------
        license_type : str, optional
            Type of license type, which can be either ``"Pack"`` or ``"Pool"``.

        Returns
        -------
        bool
            ``True``.

            .. note::
               Because of an API limitation, the command returns ``True`` even when the key is wrong.

        References
        ----------

        >>> oDesktop.SetRegistryString
        """
        try:
            self.odesktop.SetRegistryString("Desktop/Settings/ProjectOptions/HPCLicenseType", license_type)
            return True
        except:
            return False

    @pyaedt_function_handler()
    def set_registry_key(self, key_full_name, key_value):
        """Change a specific registry key to a new value.

        Parameters
        ----------
        key_full_name : str
            Full name of the AEDT registry key.
        key_value : str, int
            Value for the AEDT registry key.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.SetRegistryString
        >>> oDesktop.SetRegistryInt
        """
        if isinstance(key_value, str):
            try:
                self.odesktop.SetRegistryString(key_full_name, key_value)
                self.logger.info("Key %s correctly changed.", key_full_name)
                return True
            except:
                self.logger.warning("Error setting up Key %s.", key_full_name)
                return False
        elif isinstance(key_value, int):
            try:
                self.odesktop.SetRegistryInt(key_full_name, key_value)
                self.logger.info("Key %s correctly changed.", key_full_name)
                return True
            except:
                self.logger.warning("Error setting up Key %s.", key_full_name)
                return False
        else:
            self.logger.warning("Key value must be an integer or string.")
            return False

    @pyaedt_function_handler()
    def get_registry_key_string(self, key_full_name):
        """Get the value for the AEDT registry key if one exists.

        Parameters
        ----------
        key_full_name : str
            Full name of the AEDT registry key.

        Returns
        -------
        str
          Value for the AEDT registry key, otherwise ``''``.

        References
        ----------

        >>> oDesktop.GetRegistryString
        """
        return self.odesktop.GetRegistryString(key_full_name)

    @pyaedt_function_handler()
    def get_registry_key_int(self, key_full_name):
        """Get the value for the AEDT registry key if one exists.

        Parameters
        ----------
        key_full_name : str
            Full name of the AEDT registry key.

        Returns
        -------
        str
            Value for the AEDT registry key, otherwise ``0``.

        References
        ----------

        >>> oDesktop.GetRegistryInt
        """
        return self.odesktop.GetRegistryInt(key_full_name)

    @pyaedt_function_handler()
    def check_beta_option_enabled(self, beta_option_name):
        """Check if a beta option is enabled.

        Parameters
        ----------
        beta_option_name : str
            Name of the beta option to check. For example, ``'SF43060_HFSS_PI'``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.GetRegistryString
        """
        limit = 100
        i = 0
        while limit > 0:
            a = self.get_registry_key_string("Desktop/Settings/ProjectOptions/EnabledBetaOptions/Item{}".format(i))
            if a and a == beta_option_name:
                return True
            elif a:
                limit -= 1
            else:
                limit = 0
        return False

    @pyaedt_function_handler()
    def _is_object_oriented_enabled(self):
        if self._aedt_version >= "2022.1":
            return True
        elif self.check_beta_option_enabled("SF159726_SCRIPTOBJECT"):
            return True
        else:
            try:
                self.oproject.GetChildObject("Variables")
                return True
            except:
                return False

    @pyaedt_function_handler()
    def set_active_dso_config_name(self, product_name="HFSS", config_name="Local"):
        """Change a specific registry key to a new value.

        Parameters
        ----------
        product_name : str, optional
            Name of the tool to apply the active configuration to. The default is ``"HFSS"``.
        config_name : str, optional
            Name of the configuration to apply. The default is ``"Local"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.SetRegistryString
        """
        try:
            self.set_registry_key("Desktop/ActiveDSOConfigurations/{}".format(product_name), config_name)
            self.logger.info("Configuration Changed correctly to %s for %s.", config_name, product_name)
            return True
        except:
            self.logger.warning("Error Setting Up Configuration %s for %s.", config_name, product_name)
            return False

    @pyaedt_function_handler()
    def set_registry_from_file(self, registry_file, make_active=True):
        """Apply desktop registry settings from an ACT file.

        One way to get an ACF file is to export a configuration from the AEDT UI and then edit and reuse it.

        Parameters
        ----------
        registry_file : str
            Full path to the ACF file.
        make_active : bool, optional
            Whether to set the imported configuration as active. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.SetRegistryFromFile
        """
        try:
            self.odesktop.SetRegistryFromFile(registry_file)
            if make_active:
                with open(registry_file, "r") as f:
                    for line in f:
                        stripped_line = line.strip()
                        if "ConfigName" in stripped_line:
                            config_name = stripped_line.split("=")
                        elif "DesignType" in stripped_line:
                            design_type = stripped_line.split("=")
                            break
                    if design_type and config_name:
                        self.set_active_dso_config_name(design_type[1], config_name[1])
            return True
        except:
            return False

    @pyaedt_function_handler()
    def _optimetrics_variable_args(
        self,
        arg,
        optimetrics_type,
        variable_name,
        min_val=None,
        max_val=None,
        tolerance=None,
        probability=None,
        mean=None,
        enable=True,
    ):
        """Optimetrics variable arguments.

        Parameters
        ----------
        arg :

        optimetrics_type :

        variable_name : str
            Name of the variable.
        min_val : optional
            Minimum value for the variable. The default is ``None``.
        max_val :  optional
            Maximum value for the variable. The default is ``None``.
        tolerance : optional
            The default is ``None``.
        probability : optional
            The default is ``None``.
        mean : optional
            The default is ``None``.
        enable : bool, optional
            The default is ``True``.

        Returns
        -------

        """
        if "$" in variable_name:
            tab = "NAME:ProjectVariableTab"
            propserver = "ProjectVariables"
        else:
            tab = "NAME:LocalVariableTab"
            propserver = "LocalVariables"
        arg2 = ["NAME:" + optimetrics_type, "Included:=", enable]
        if min_val:
            arg2.append("Min:=")
            arg2.append(min_val)
        if max_val:
            arg2.append("Max:=")
            arg2.append(max_val)
        if tolerance:
            arg2.append("Tol:=")
            arg2.append(tolerance)
        if probability:
            arg2.append("Prob:=")
            arg2.append(probability)
        if mean:
            arg2.append("Mean:=")
            arg2.append(mean)
        arg3 = [tab, ["NAME:PropServers", propserver], ["NAME:ChangedProps", ["NAME:" + variable_name, arg2]]]
        arg.append(arg3)

    @pyaedt_function_handler()
    def activate_variable_statistical(
        self, variable_name, min_val=None, max_val=None, tolerance=None, probability=None, mean=None
    ):
        """Activate statitistical analysis for a variable and optionally set up ranges.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_val : optional
            Minimum value for the variable. The default is ``None``.
        max_val : optional
            Maximum value for the variable. The default is ``None``.
        tolerance : optional
            Tolerance value for the variable. The default is ``None``.
        probability : optional
            Probability value for the variable. The default is ``None``.
        mean :
            Mean value for the variable. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(
            arg, "Statistical", variable_name, min_val, max_val, tolerance, probability, mean
        )
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def activate_variable_optimization(self, variable_name, min_val=None, max_val=None):
        """Activate optimization analysis for a variable and optionally set up ranges.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_val : optional
            Minimum value for the variable. The default is ``None``.
        max_val : optional
            Maximum value for the variable. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Optimization", variable_name, min_val, max_val)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def activate_variable_sensitivity(self, variable_name, min_val=None, max_val=None):
        """Activate sensitivity analysis for a variable and optionally set up ranges.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_val : optional
            Minimum value for the variable. The default is ``None``.
        max_val : optional
            Maximum value for the variable. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Sensitivity", variable_name, min_val, max_val)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def activate_variable_tuning(self, variable_name, min_val=None, max_val=None):
        """Activate tuning analysis for a variable and optionally set up ranges.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_val : optional
            Minimum value for the variable. The default is ``None``.
        max_val : optional
            Maximum value for the variable. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Tuning", variable_name, min_val, max_val)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def deactivate_variable_statistical(self, variable_name):
        """Deactivate the statistical analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Statistical", variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def deactivate_variable_optimization(self, variable_name):
        """Deactivate the optimization analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Optimization", variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def deactivate_variable_sensitivity(self, variable_name):
        """Deactivate the sensitivity analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Sensitivity", variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def deactivate_variable_tuning(self, variable_name):
        """Deactivate the tuning analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Tuning", variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def _get_boundaries_data(self):
        """Retrieve boundary data.

        Returns
        -------
        [:class:`pyaedt.modules.Boundary.BoundaryObject`]
        """
        boundaries = []
        if self.design_properties and "BoundarySetup" in self.design_properties:
            for ds in self.design_properties["BoundarySetup"]["Boundaries"]:
                try:
                    if isinstance(self.design_properties["BoundarySetup"]["Boundaries"][ds], (OrderedDict, dict)):
                        boundaries.append(
                            BoundaryObject(
                                self,
                                ds,
                                self.design_properties["BoundarySetup"]["Boundaries"][ds],
                                self.design_properties["BoundarySetup"]["Boundaries"][ds]["BoundType"],
                            )
                        )
                except:
                    pass
        return boundaries

    @pyaedt_function_handler()
    def _get_ds_data(self, name, datas):
        """

        Parameters
        ----------
        name :

        datas :


        Returns
        -------

        """
        units = datas["DimUnits"]
        numcol = len(units)
        x = []
        y = []
        z = None
        v = None
        if numcol > 2:
            z = []
            v = []
        if "Coordinate" in datas:
            for el in datas["Coordinate"]:
                x.append(el["CoordPoint"][0])
                y.append(el["CoordPoint"][1])
                if numcol > 2:
                    z.append(el["CoordPoint"][2])
                    v.append(el["CoordPoint"][3])
        else:
            new_list = [datas["Points"][i : i + numcol] for i in range(0, len(datas["Points"]), numcol)]
            for el in new_list:
                x.append(el[0])
                y.append(el[1])
                if numcol > 2:
                    z.append(el[2])
                    v.append(el[3])
        if numcol == 2:
            return DataSet(self, name, x, y, z, v, units[0], units[1])
        else:
            return DataSet(self, name, x, y, z, v, units[0], units[1], units[2], units[3])

    @pyaedt_function_handler()
    def _get_project_datasets(self):
        """ """
        datasets = {}
        try:
            for ds in self.project_properies["AnsoftProject"]["ProjectDatasets"]["DatasetDefinitions"]:
                datas = self.project_properies["AnsoftProject"]["ProjectDatasets"]["DatasetDefinitions"][ds][
                    "Coordinates"
                ]
                datasets[ds] = self._get_ds_data(ds, datas)
        except:
            pass
        return datasets

    @pyaedt_function_handler()
    def _get_design_datasets(self):
        """ """
        datasets = {}
        try:
            for ds in self.design_properties["ModelSetup"]["DesignDatasets"]["DatasetDefinitions"]:
                datas = self.project_properies["ModelSetup"]["DesignDatasets"]["DatasetDefinitions"][ds]["Coordinates"]
                datasets[ds] = self._get_ds_data(ds, datas)
        except:
            pass
        return datasets

    @pyaedt_function_handler()
    def close_desktop(self):
        """Close AEDT and release it.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        release_desktop()
        return True

    @pyaedt_function_handler()
    def autosave_disable(self):
        """Disable autosave in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.EnableAutoSave
        """
        self.odesktop.EnableAutoSave(False)
        return True

    @pyaedt_function_handler()
    def autosave_enable(self):
        """Enable autosave in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.EnableAutoSave
        """
        self.odesktop.EnableAutoSave(True)
        return True

    @pyaedt_function_handler()
    def release_desktop(self, close_projects=True, close_desktop=True):
        """Release AEDT.

        Parameters
        ----------
        close_projects : bool, optional
            Whether to close all projects. The default is ``True``.
        close_desktop : bool, optional
            Whether to close AEDT after releasing it. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        release_desktop(close_projects, close_desktop)
        props = [a for a in dir(self) if not a.startswith("__")]
        for a in props:
            self.__dict__.pop(a, None)
        gc.collect()
        return True

    @pyaedt_function_handler()
    def generate_temp_project_directory(self, subdir_name):
        """Generate a unique directory string to save a project to.

        This method creates a directory for storage of a project in the ``temp`` directory
        of the AEDT installation because this location is guaranteed to exist. If the ``name``
        parameter is defined, a subdirectory is added within the ``temp`` directory and a
        hash suffix is added to ensure that this directory is empty and has a unique name.

        Parameters
        ----------
        subdir_name : str
            Base name of the subdirectory to create in the ``temp`` directory.

        Returns
        -------
        str
            Base name of the created subdirectory.

        Examples
        --------
        >>> m3d = Maxwell3d()
        >>> proj_directory = m3d.generate_temp_project_directory("Example")

        """
        base_path = self.temp_directory

        if not isinstance(subdir_name, str):
            self.logger.error("Input argument 'subdir' must be a string")
            return False
        dir_name = generate_unique_name(subdir_name)
        project_dir = os.path.join(base_path, dir_name)
        try:
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
            return project_dir
        except OSError:
            return False

    @pyaedt_function_handler()
    def load_project(self, project_file, design_name=None, close_active_proj=False):
        """Open an AEDT project based on a project and optional design.

        Parameters
        ----------
        project_file : str
            Full path and name for the project.
        design_name : str, optional
            Design name. The default is ``None``.
        close_active_proj : bool, optional
            Whether to close the active project. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.OpenProject
        """

        if close_active_proj and self.oproject:
            self._close_edb()
            self.close_project(self.project_name)
        proj = self.odesktop.OpenProject(project_file)
        if proj:
            self.__init__(projectname=proj.GetName(), designname=design_name)
            return True
        else:
            return False

    @pyaedt_function_handler()
    def _close_edb(self):
        if self.design_type == "HFSS 3D Layout Design":  # pragma: no cover
            if self.modeler and self.modeler.edb:
                self.modeler.edb.close_edb()

    @pyaedt_function_handler()
    def create_dataset1d_design(self, dsname, xlist, ylist, xunit="", yunit=""):
        """Create a design dataset.

        Parameters
        ----------
        dsname : str
            Name of the dataset (without a prefix for a project dataset).
        xlist : list
            List of X-axis values for the dataset.
        ylist : list
            List of Y-axis values for the dataset.
        xunit : str, optional
            Units for the X axis. The default is ``""``.
        yunit : str, optional
            Units for the Y axis. The default is ``""``.

        Returns
        -------
        :class:`pyaedt.application.Variables.DataSet`

        References
        ----------

        >>> oProject.AddDataset
        >>> oDesign.AddDataset
        """
        return self.create_dataset(dsname, xlist, ylist, is_project_dataset=False, xunit=xunit, yunit=yunit)

    @pyaedt_function_handler()
    def create_dataset1d_project(self, dsname, xlist, ylist, xunit="", yunit=""):
        """Create a project dataset.

        Parameters
        ----------
        dsname : str
            Name of dataset (without a prefix for a project dataset).
        xlist : list
            List of X-axis values for the dataset.
        ylist : list
            List of Y-axis values for the dataset.
        xunit : str, optional
            Units for the X axis. The default is ``""``.
        yunit : str, optional
            Units for the Y axis. The default is ``""``.

        Returns
        -------
        :class:`pyaedt.application.Variables.DataSet`
            Dataset object when the dataset is created, ``False`` otherwise.

        References
        ----------

        >>> oProject.AddDataset
        >>> oDesign.AddDataset
        """
        return self.create_dataset(dsname, xlist, ylist, is_project_dataset=True, xunit=xunit, yunit=yunit)

    @pyaedt_function_handler()
    def create_dataset3d(self, dsname, xlist, ylist, zlist=None, vlist=None, xunit="", yunit="", zunit="", vunit=""):
        """Create a 3D dataset.

        Parameters
        ----------
        dsname : str
            Name of the dataset (without a prefix for a project dataset).
        xlist : list
            List of X-axis values for the dataset.
        ylist : list
            List of Y-axis values for the dataset.
        zylist : list, optional
            List of Z-axis values for a 3D dataset only. The default is ``None``.
        vylist : list, optional
            List of V-axis values for a 3D dataset only. The default is ``None``.
        xunit : str, optional
            Units for the X axis. The default is ``""``.
        yunit : str, optional
            Units for the Y axis. The default is ``""``.
        zunit : str, optional
            Units for the Z axis for a 3D dataset only. The default is ``""``.
        vunit : str, optional
            Units for the V axis for a 3D dataset only. The default is ``""``.

        Returns
        -------
        :class:`pyaedt.application.Variables.DataSet`
            Dataset object when the dataset is created, ``False`` otherwise.

        References
        ----------

        >>> oDesign.AddDataset
        """
        return self.create_dataset(
            dsname=dsname,
            xlist=xlist,
            ylist=ylist,
            zlist=zlist,
            vlist=vlist,
            xunit=xunit,
            yunit=yunit,
            zunit=zunit,
            vunit=vunit,
        )

    @pyaedt_function_handler()
    def create_dataset(
        self,
        dsname,
        xlist,
        ylist,
        zlist=None,
        vlist=None,
        is_project_dataset=True,
        xunit="",
        yunit="",
        zunit="",
        vunit="",
    ):
        """Create a dataset.

        Parameters
        ----------
        dsname : str
            Name of the dataset (without a prefix for a project dataset).
        xlist : list
            List of X-axis values for the dataset.
        ylist : list
            List of Y-axis values for the dataset.
        zlist : list, optional
            List of Z-axis values for a 3D dataset only. The default is ``None``.
        vlist : list, optional
            List of V-axis values for a 3D dataset only. The default is ``None``.
        is_project_dataset : bool, optional
            Whether it is a project data set. The default is ``True``.
        xunit : str, optional
            Units for the X axis. The default is ``""``.
        yunit : str, optional
            Units for the Y axis. The default is ``""``.
        zunit : str, optional
            Units for the Z axis for a 3D dataset only. The default is ``""``.
        vunit : str, optional
            Units for the V axis for a 3D dataset only. The default is ``""``.

        Returns
        -------
        :class:`pyaedt.application.Variables.DataSet`
            Dataset object when the dataset is created, ``False`` otherwise.

        References
        ----------

        >>> oProject.AddDataset
        >>> oDesign.AddDataset
        """
        if not self.dataset_exists(dsname, is_project_dataset):
            if is_project_dataset:
                dsname = "$" + dsname
            ds = DataSet(self, dsname, xlist, ylist, zlist, vlist, xunit, yunit, zunit, vunit)
        else:
            self.logger.warning("Dataset %s already exists", dsname)
            return False
        ds.create()
        if is_project_dataset:
            self.project_datasets[dsname] = ds
        else:
            self.design_datasets[dsname] = ds
        self.logger.info("Dataset %s created successfully.", dsname)
        return ds

    @pyaedt_function_handler()
    def dataset_exists(self, name, is_project_dataset=True):
        """Check if a dataset exists.

        Parameters
        ----------
        name :str
            Name of the dataset (without a prefix for a project dataset).
        is_project_dataset : bool, optional
            Whether it is a project data set. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if is_project_dataset and "$" + name in self.project_datasets:
            self.logger.info("Dataset %s$ exists.", name)
            return True
            # self.oproject.ExportDataSet("$"+name, os.path.join(self.temp_directory, "ds.tab"))
        elif not is_project_dataset and name in self.design_datasets:
            self.logger.info("Dataset %s exists.", name)
            return True
            # self.odesign.ExportDataSet(name, os.path.join(self.temp_directory, "ds.tab"))
        self.logger.info("Dataset %s doesn't exist.", name)
        return False

    @pyaedt_function_handler()
    def change_automatically_use_causal_materials(self, lossy_dielectric=True):
        """Enable or disable the automatic use of causal materials for lossy dielectrics.

        Parameters
        ----------
        lossy_dielectric : bool, optional
            Whether to enable causal materials.
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        if lossy_dielectric:
            self.logger.info("Enabling Automatic use of causal materials")
        else:
            self.logger.info("Disabling Automatic use of causal materials")
        self.odesign.SetDesignSettings(["NAME:Design Settings Data", "Calculate Lossy Dielectrics:=", lossy_dielectric])
        return True

    @pyaedt_function_handler()
    def change_material_override(self, material_override=True):
        """Enable or disable the material override in the project.

        Parameters
        ----------
        material_override : bool, optional
            Whether to enable the material override.
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        if material_override:
            self.logger.info("Enabling Material Override")
        else:
            self.logger.info("Disabling Material Override")
        self.odesign.SetDesignSettings(["NAME:Design Settings Data", "Allow Material Override:=", material_override])
        return True

    @pyaedt_function_handler()
    def change_validation_settings(
        self, entity_check_level="Strict", ignore_unclassified=False, skip_intersections=False
    ):
        """Update the validation design settings.

        Parameters
        ----------
        entity_check_level : str, optional
            Entity check level. The default is ``"Strict"``.
        ignore_unclassified : bool, optional
            Whether to ignore unclassified elements. The default is ``False``.
        skip_intersections : bool, optional
            Whether to skip intersections. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        self.logger.info("Changing the validation design settings")
        self.odesign.SetDesignSettings(
            ["NAME:Design Settings Data"],
            [
                "NAME:Model Validation Settings",
                "EntityCheckLevel:=",
                entity_check_level,
                "IgnoreUnclassifiedObjects:=",
                ignore_unclassified,
                "SkipIntersectionChecks:=",
                skip_intersections,
            ],
        )
        return True

    @pyaedt_function_handler()
    def clean_proj_folder(self, directory=None, name=None):
        """Delete a project folder.

        Parameters
        ----------
        directory : str, optionl
            Name of the directory. The default is ``None``, in which case the active project is
            deleted from the ``aedtresults`` directory.
        name : str, optional
            Name of the project. The default is ``None``, in which case the data for the
            active project is deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if not name:
            name = self.project_name
        if not directory:
            directory = self.results_directory
        self.logger.info("Cleanup folder %s from project %s", directory, name)
        if os.path.exists(directory):
            shutil.rmtree(directory, True)
            if not os.path.exists(directory):
                os.mkdir(directory)
        self.logger.info("Project Directory cleaned")
        return True

    @pyaedt_function_handler()
    def copy_project(self, path, dest):
        """Copy the project to another destination.

        .. note::
           This method saves the project before copying it.

        Parameters
        ----------
        path : str
            Path to save a copy of the project to.
        dest :
            Name to give the project in the new destination.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.SaveAs
        """
        self.logger.info("Copy AEDT Project ")
        self.oproject.Save()
        self.oproject.SaveAs(os.path.join(path, dest + ".aedt"), True)
        return True

    @pyaedt_function_handler()
    def create_new_project(self, proj_name):
        """Create a project within AEDT.

        Parameters
        ----------
        proj_name :
            Name of the project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.NewProject
        """
        self.logger.info("Creating new Project ")
        prj = self.odesktop.NewProject(proj_name)
        prj_name = prj.GetName()
        self.oproject = prj_name
        self.odesign = None
        return True

    @pyaedt_function_handler()
    def close_project(self, name=None, saveproject=True):
        """Close an AEDT project.

        Parameters
        ----------
        name : str, optional
            Name of the project. The default is ``None``, in which case the
            active project is closed.
        saveproject : bool, optional
            Whether to save the project before closing it. The default is
            ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.CloseProject
        """
        legacy_name = self.project_name
        if name and name not in self.project_list:
            self.logger.warning("Project not found. ", name)
            return False
        if not name:
            name = self.project_name
        self.logger.info("Closing the AEDT Project {}".format(name))
        oproj = self.odesktop.SetActiveProject(name)
        proj_path = oproj.GetPath()
        if saveproject:
            oproj.Save()
        self.odesktop.CloseProject(name)
        if name == legacy_name:
            if not is_ironpython:
                self._init_variables()
            self._oproject = None
            self._odesign = None
        else:
            self.odesktop.SetActiveProject(legacy_name)
        i = 0
        timeout = 10
        while True:
            if not os.path.exists(os.path.join(proj_path, name + ".aedt.lock")):
                self.logger.info("Project {} closed correctly".format(name))
                break
            elif i > timeout:
                self.logger.warning("Lock File still exists.")
                break
            else:
                i += 0.2
                time.sleep(0.2)
        return True

    @pyaedt_function_handler()
    def delete_design(self, name=None, fallback_design=None):
        """Delete a design from the current project.

        .. warning::
           This method does not work from the toolkit.

        Parameters
        ----------
        name : str, optional
            Name of the design. The default is ``None``, in which case
            the active design is deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.DeleteDesign
        """
        if not name:
            name = self.design_name
        self.oproject.DeleteDesign(name)
        if name != self.design_name:
            return True
        if fallback_design and (
            fallback_design in [x for i in list(self._oproject.GetDesigns()) for x in (i.GetName(), i.GetName()[2:])]
        ):
            try:
                self.set_active_design(fallback_design)
            except:
                if os.name != "posix":
                    self._init_variables()
                self._odesign = None
                return False
        else:
            if os.name != "posix":
                self._init_variables()
            self._odesign = None
        return True

    @pyaedt_function_handler()
    def delete_separator(self, separator_name):
        """Delete a separator from either the active project or a design.

        Parameters
        ----------
        separator_name : str
            Name of the separator.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.ChangeProperty
        >>> oDesign.ChangeProperty
        """
        return self._variable_manager.delete_separator(separator_name)

    @pyaedt_function_handler()
    def delete_variable(self, sVarName):
        """Delete a variable.

        Parameters
        ----------
        sVarName :
            Name of the variable.

        References
        ----------

        >>> oProject.ChangeProperty
        >>> oDesign.ChangeProperty
        """
        return self.variable_manager.delete_variable(sVarName)

    @pyaedt_function_handler()
    def insert_design(self, design_name=None):
        """Add a design of a specified type.

        The default design type is taken from the derived application class.

        Parameters
        ----------
        design_name : str, optional
            Name of the design. The default is ``None``, in which case the
            default design name is ``<Design-Type>Design<_index>``. If the
            given or default design name is in use, then an underscore and
            index is added to ensure that the design name is unique.
            The inserted object is assigned to the ``Design`` object.

        Returns
        -------
        str
            Name of the design.

        References
        ----------

        >>> oProject.InsertDesign
        """
        self._close_edb()
        if self.project_name:
            self.__init__(projectname=self.project_name, designname=design_name)
        else:
            self.__init__(projectname=generate_unique_name("Project"), designname=design_name)

    def _insert_design(self, design_type, design_name=None, solution_type=None):
        assert design_type in self.design_solutions.design_types, "Invalid design type for insert: {}".format(
            design_type
        )
        # self.save_project() ## Commented because it saves a Projectxxx.aedt when launched on an empty Desktop
        unique_design_name = self._generate_unique_design_name(design_name)

        if design_type == "RMxprtSolution":
            new_design = self._oproject.InsertDesign("RMxprt", unique_design_name, "Inner-Rotor Induction Machine", "")
        elif design_type == "ModelCreation":
            new_design = self._oproject.InsertDesign(
                "RMxprt", unique_design_name, "Model Creation Inner-Rotor Induction Machine", ""
            )
        else:
            if design_type == "HFSS" and self._aedt_version < "2021.2":
                new_design = self._oproject.InsertDesign(design_type, unique_design_name, "DrivenModal", "")
            else:
                new_design = self._oproject.InsertDesign(
                    design_type, unique_design_name, self.default_solution_type, ""
                )
        self.logger.info("Added design '%s' of type %s.", unique_design_name, design_type)
        name = new_design.GetName()
        if ";" in name:
            self.odesign = name.split(";")[1]
        else:
            self.odesign = name
        return name

    @pyaedt_function_handler()
    def _generate_unique_design_name(self, design_name):
        """Generate an unique design name.

        Parameters
        ----------
        design_name : str
            Name of the design.


        Returns
        -------
        str
            Name of the design.

        """
        design_index = 0
        suffix = ""
        if not design_name:
            char_set = string.ascii_uppercase + string.digits
            uName = "".join(random.sample(char_set, 3))
            design_name = self._design_type + "_" + uName
        while design_name in self.design_list:
            if design_index:
                design_name = design_name[0 : -len(suffix)]
            design_index += 1
            suffix = "_" + str(design_index)
            design_name += suffix
        return design_name

    @pyaedt_function_handler()
    def _generate_unique_project_name(self):
        """Generate an unique project name.

        Returns
        --------
        str
            Unique project name in the form ``"Project_<unique_name>.aedt".

        """
        char_set = string.ascii_uppercase + string.digits
        uName = "".join(random.sample(char_set, 3))
        proj_name = "Project_" + uName + ".aedt"
        return proj_name

    @pyaedt_function_handler()
    def rename_design(self, new_name):
        """Rename the active design.

        Parameters
        ----------
        new_name : str
            New name of the design.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.RenameDesignInstance
        """
        self._odesign.RenameDesignInstance(self.design_name, new_name)
        self.odesign = new_name
        return True

    @pyaedt_function_handler()
    def copy_design_from(self, project_fullname, design_name):
        """Copy a design from a project into the active design.

        Parameters
        ----------
        project_fullname : str
            Full path and name for the project containing the design to copy.
            The active design is maintained.
        design_name : str
            Name of the design to copy into the active design. If a design with this
            name is already present in the destination project, AEDT automatically
            changes the name.

        Returns
        -------
        str
           Name of the copied design name when successful or ``None`` when failed.
           Failure is generally a result of the name specified for ``design_name``
           not existing in the project specified for ``project_fullname``.

        References
        ----------

        >>> oProject.CopyDesign
        >>> oProject.Paste
        """
        self.save_project()
        active_design = self.design_name
        # open the origin project
        if os.path.exists(project_fullname):
            proj_from = self.odesktop.OpenProject(project_fullname)
            proj_from_name = proj_from.GetName()
        else:
            return None
        # check if the requested design exists in the origin project
        if design_name not in [x for i in list(proj_from.GetDesigns()) for x in (i.GetName(), i.GetName()[2:])]:
            return None
        # copy the source design
        proj_from.CopyDesign(design_name)
        # paste in the destination project and get the name
        self._oproject.Paste()
        new_designname = self._oproject.GetActiveDesign().GetName()
        if self._oproject.GetActiveDesign().GetDesignType() == "HFSS 3D Layout Design":
            new_designname = new_designname[2:]  # name is returned as '2;EMDesign3'
        # close the source project
        self.odesktop.CloseProject(proj_from_name)
        # reset the active design (very important)
        self.save_project()
        self._close_edb()
        self.__init__(self.project_name, new_designname)
        self._oproject.SetActiveDesign(active_design)

        # return the pasted design name
        return new_designname

    @pyaedt_function_handler()
    def duplicate_design(self, label):
        """Copy a design to a new name.

        The new name consists of the original
        design name plus a suffix of ``MMode`` and a running index
        as necessary to allow for multiple calls.

        Parameters
        ----------
        label : str
            Name of the design to copy.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.CopyDesign
        >>> oProject.Paste
        """

        active_design = self.design_name
        design_list = self.design_list
        self._oproject.CopyDesign(active_design)
        self._oproject.Paste()
        newname = label
        ind = 1
        while newname in self.design_list:
            newname = label + "_" + str(ind)
            ind += 1
        actual_name = [i for i in self.design_list if i not in design_list]
        self.odesign = actual_name
        self.design_name = newname
        self._close_edb()
        self.__init__(self.project_name, self.design_name)

        return True

    @pyaedt_function_handler()
    def export_design_preview_to_jpg(self, filename):
        """Export design preview image to a JPG file.

        Parameters
        ----------
        filename : str
            Full path and name for the JPG file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        design_info = self.project_properies["ProjectPreview"]["DesignInfo"]
        if not isinstance(design_info, dict):
            # there are multiple designs, find the right one
            # is self.design_name guaranteed to be there?
            design_info = [design for design in design_info if design["DesignName"] == self.design_name][0]
        image_data_str = design_info["Image64"]
        with open(filename, "wb") as f:
            if sys.version_info.major == 2:
                bytestring = bytes(image_data_str).decode("base64")
            else:
                bytestring = base64.decodebytes(image_data_str.encode("ascii"))
            f.write(bytestring)
        return True

    @pyaedt_function_handler()
    def export_variables_to_csv(self, filename, export_project=True, export_design=True):
        """Export design properties, project variables, or both to a CSV file.

        Parameters
        ----------
        filename : str
            Full path and name for the CSV file.
        export_project : bool, optional
            Whether to export project variables. The default is ``True``.
        export_design : bool, optional
            Whether to export design properties. The default is ``True``.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.GetProperties
        >>> oDesign.GetProperties
        >>> oProject.GetVariableValue
        >>> oDesign.GetVariableValue
        """
        varnames = []
        desnames = []
        if export_project:
            varnames = self.oproject.GetProperties("ProjectVariableTab", "ProjectVariables")
        if export_design:
            desnames = self.odesign.GetProperties("LocalVariableTab", "LocalVariables")
        list_full = [["Name", "Value"]]
        for el in varnames:
            value = self.oproject.GetVariableValue(el)
            list_full.append([el, value])
        for el in desnames:
            value = self.odesign.GetVariableValue(el)
            list_full.append([el, value])
        return write_csv(filename, list_full)

    @pyaedt_function_handler()
    def read_design_data(self):
        """Read back the design data as a dictionary.

        Returns
        -------
        dict
            Dictionary of the design data.

        """
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, "r") as fps:
            design_data = json.load(fps)
        return design_data

    @pyaedt_function_handler()
    def save_project(self, project_file=None, overwrite=True, refresh_obj_ids_after_save=False):
        """Save the project and add a message.

        Parameters
        ----------
        project_file : str, optional
            Full path and project name. The default is ````None``.
        overwrite : bool, optional
            Whether to overwrite the existing project. The default is ``True``.
        refresh_obj_ids_after_save : bool, optional
            Whether to refresh object IDs after saving the project.
            The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.Save
        >>> oProject.SaveAs
        """
        msg_text = "Saving {0} Project".format(self.project_name)
        self.logger.info(msg_text)
        if project_file and not os.path.exists(os.path.dirname(project_file)):
            os.makedirs(os.path.dirname(project_file))
        elif project_file:
            self.oproject.SaveAs(project_file, overwrite)
        else:
            self.oproject.Save()
        if refresh_obj_ids_after_save:
            self.modeler.refresh_all_ids()
            self.modeler._refresh_all_ids_from_aedt_file()
        return True

    @pyaedt_function_handler()
    def archive_project(
        self,
        project_file=None,
        include_external_files=True,
        include_results_file=True,
        additional_file_lists=[],
        notes="",
    ):
        """Archive the AEDT project and add a message.

        Parameters
        ----------
        project_file : str, optional
            Full path and project name. The default is ``None``.
        include_external_files : bool, optional
            Whether to include external files in the archive. The default is ``True``.
        include_results_file : bool, optional
            Whether to include simulation results files in the archive. The default is ``True``.
        additional_file_lists : list, optional
            List of additional files to add to the archive. The default is ``[]``.
        notes : str, optional
            Simulation notes to add to the archive. The default is ``""``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oProject.Save
        >>> oProject.SaveProjectArchive
        """
        msg_text = "Saving {0} Project".format(self.project_name)
        self.logger.info(msg_text)
        if not project_file:
            project_file = os.path.join(self.project_path, self.project_name + ".aedtz")
        self.oproject.Save()
        self.oproject.SaveProjectArchive(
            project_file, include_external_files, include_results_file, additional_file_lists, notes
        )

        return True

    @pyaedt_function_handler()
    def delete_project(self, project_name):
        """Delete a project.

        Parameters
        ----------
        project_name : str
            Name of the project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.DeleteProject
        """
        assert self.project_name != project_name, "You cannot delete the active project."
        self.odesktop.DeleteProject(project_name)
        return True

    @pyaedt_function_handler()
    def set_active_design(self, name):
        """Change the active design to another design.

        Parameters
        ----------
        name :
            Name of the design to make active.

        References
        ----------

        >>> oProject.SetActiveDesign
        """
        self.oproject.SetActiveDesign(name)
        self.odesign = name
        self._close_edb()
        self.__init__(self.project_name, self.design_name)
        return True

    @pyaedt_function_handler()
    def validate_simple(self, logfile=None):
        """Validate a design.

        Parameters
        ----------
        logfile : str, optional
            Name of the log file to save validation information to.
            The default is ``None``.

        Returns
        -------
        int
            ``1`` when successful, ``0`` when failed.

        References
        ----------

        >>> oDesign.ValidateDesign
        """
        if logfile:
            return self._odesign.ValidateDesign(logfile)
        else:
            return self._odesign.ValidateDesign()

    @pyaedt_function_handler()
    def get_evaluated_value(self, variable_name, variation=None, units=None):
        """Retrieve the evaluated value of a design property or project variable in SI units if no unit is provided.

        Parameters
        ----------
        variable_name : str
            Name of the design property or project variable.
        variation : float, optional
            Variation value for the evaluation. The default is ``None``,
            in which case the nominal variation is used.
        units : str, optional
            Name of the unit to use for rescaling. The default is ``None``,
            in which case SI units are applied by default.

        Returns
        -------
        float
            Evaluated value of the design property or project variable in SI units.

        References
        ----------

        >>> oDesign.GetNominalVariation
        >>> oDesign.GetVariationVariableValue

        Examples
        --------

        >>> M3D = Maxwell3d()
        >>> M3D["p1"] = "10mm"
        >>> M3D["p2"] = "20mm"
        >>> M3D["p3"] = "P1 * p2"
        >>> eval_p3 = M3D.get_evaluated_value("p3")
        """
        if not variation:
            variation_string = self._odesign.GetNominalVariation()
        else:
            variation_string = self.design_variation(variation_string=variation)
        try:
            si_value = self._odesign.GetVariationVariableValue(variation_string, variable_name)
        except:
            si_value = self._odesign.GetVariableValue(variable_name)
        if units:
            scale = AEDT_UNITS[unit_system(units)][units]
            if isinstance(scale, tuple):
                return scale[0](si_value, True)
            else:
                return si_value / scale
        return si_value

    @pyaedt_function_handler()
    def evaluate_expression(self, expression_string):
        """Evaluate a valid string expression and return the numerical value in SI units.

        Parameters
        ----------
        expression_string : str
            A valid string expression for a design property or project variable.
            For example, ``"34mm*sqrt(2)"`` or ``"$G1*p2/34"``.

        Returns
        -------
        float
            Evaluated value for the string expression.

        """
        # Set the value of an internal reserved design variable to the specified string
        if expression_string in self._variable_manager.variables:
            return self._variable_manager.variables[expression_string]
        else:
            try:
                self._variable_manager.set_variable(
                    "pyaedt_evaluator",
                    expression=expression_string,
                    readonly=True,
                    hidden=True,
                    description="Internal_Evaluator",
                )
            except:
                raise ("Invalid string expression {}".expression_string)

            # Extract the numeric value of the expression (in SI units!)
            return self._variable_manager.variables["pyaedt_evaluator"].value

    @pyaedt_function_handler()
    def design_variation(self, variation_string=None):
        """Generate a string to specify a desired variation.

        This method converts an input string defining a desired solution variation into a valid
        string taking into account all existing design properties and project variables, including
        dependent (non-sweep) properties.

        This is needed because the standard method COM function ``GetVariationVariableValue``
        does not work for obtaining values of dependent (non-sweep) variables.
        Using the object-oriented scripting model, which is a beta feature, could make this redundant in
        future releases.

        Parameters
        ----------
        variation_string : str, optional
            Variation string. For example, ``"p1=1mm"`` or ``"p2=3mm"``.

        Returns
        -------
        str
            String specifying the desired variation.

        References
        ----------

        >>> oDesign.GetNominalVariation
        """
        nominal = self._odesign.GetNominalVariation()
        if variation_string:
            # decompose the nominal variation into a dictionary of name[value]
            nominal_dict = variation_string_to_dict(nominal)

            # decompose the desired variation into a dictionary of name[value]
            var_dict = variation_string_to_dict(variation_string)

            # set the values of the desired variation in the active design
            for key, value in var_dict.items():
                self[key] = value

            # get the desired variation values
            nominal = self._odesign.GetNominalVariation()

            # Reset the nominal values in the active design
            for key in var_dict:
                self[key] = nominal_dict[key]

        return nominal

    @pyaedt_function_handler()
    def _assert_consistent_design_type(self, des_name):
        if des_name in self.design_list:
            self._odesign = self._oproject.SetActiveDesign(des_name)
            dtype = self._odesign.GetDesignType()
            if dtype != "RMxprt":
                assert dtype == self._design_type, "Error: Specified design is not of type {}.".format(
                    self._design_type
                )
            else:
                assert ("RMxprtSolution" == self._design_type) or (
                    "ModelCreation" == self._design_type
                ), "Error: Specified design is not of type {}.".format(self._design_type)
            return True
        else:
            return des_name

    @pyaedt_function_handler()
    def _check_solution_consistency(self):
        """Check solution consistency."""
        if self.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design", "EMIT", "Q3D Extractor"]:
            return True
        if self.design_solutions and self.design_solutions._solution_type:
            return self.design_solutions._solution_type in self._odesign.GetSolutionType()
        else:
            return True

    @pyaedt_function_handler()
    def _check_design_consistency(self):
        """ """
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == self._design_type:
            consistent = self._check_solution_consistency()
        return consistent
