"""
This module contains these classes: `Design` and `DesignCache`.

It contains all basic project information and objects. 
Because this module is inherited in the Main Tool class, 
it will be a simple call from it.

"""
from __future__ import absolute_import

import warnings
import os
import re
import csv
import shutil
import sys
import json
import string
import random
import time
import logging
from collections import OrderedDict
from .MessageManager import AEDTMessageManager
from .Variables import VariableManager, DataSet
from ..desktop import exception_to_desktop, Desktop, force_close_desktop, release_desktop, get_version_env_variable
from ..generic.LoadAEDTFile import load_entire_aedt_file
from ..generic.general_methods import aedt_exception_handler
from ..generic.list_handling import variation_string_to_dict
from ..modules.Boundary import BoundaryObject
from ..generic.general_methods import generate_unique_name


design_solutions = {
    "Maxwell 2D": [
        "MagnetostaticXY",
        "MagnetostaticZ",
        "EddyCurrentXY",
        "EddyCurrentZ",
        "TransientXY",
        "TransientZ",
        "ElectrostaticXY",
        "ElectrostaticZ",
        "ElectricTransientXY",
        "ElectricTransientZ",
        "ElectroDCConductionXY",
        "ElectroDCConductionZ"
    ],
    "Maxwell 3D": [
        "Magnetostatic",
        "EddyCurrent",
        "Transient",
        "Electrostatic",
        "DCConduction",
        "ElectroDCConduction",
        "ElectricTransient"
    ],
    "Twin Builder": [
        "TR",
        "AC",
        "DC"
    ],
    "Circuit Design": [
        "NexximLNA"
    ],
    "2D Extractor": [
        "Open",
        "Closed"
    ],
    "Q3D Extractor": [
        "Q3D Extractor"
    ],
    "HFSS": [
        "DrivenModal",
        "DrivenTerminal",
        "Transient Network",
        "Eigenmode",
        "Characteristic Mode",
        "SBR+"
    ],
    "Icepak": [
        "SteadyTemperatureAndFlow",
        "SteadyTemperatureOnly",
        "SteadyFlowOnly",
        "TransientTemperatureAndFlow",
        "TransientTemperatureOnly",
        "TransientFlowOnly"

    ],
    "RMxprtSolution": [
        "IRIM", "ORIM", "SRIM", "WRIM", "DFIG", "AFIM", "HM", "RFSM", "RASM", "RSM", "ISM", "APSM", "IBDM", "ABDM",
        "TPIM", "SPIM", "TPSM", "BLDC", "ASSM", "PMDC", "SRM", "LSSM", "UNIM", "DCM", "CPSM", "NSSM"
    ],
    "ModelCreation": [
        "IRIM", "ORIM", "SRIM", "WRIM", "DFIG", "AFIM", "HM", "RFSM", "RASM", "RSM", "ISM", "APSM", "IBDM", "ABDM",
    ],
    "HFSS 3D Layout Design": [
        ""
    ],
    "Mechanical": [
        "Thermal",
        "Modal",
        "Structural"
    ],
    "EMIT": ["EMIT"]
}

solutions_settings = {
    "DrivenModal": "DrivenModal",
    "DrivenTerminal": "DrivenTerminal",
    "EigenMode": "EigenMode",
    "Transient Network": "Transient Network",
    "SBR+": "SBR+",
    "Transient": "Transient",
    "Magnetostatic": "Magnetostatic",
    "EddyCurrent": "EddyCurrent",
    "Electrostatic": "Electrostatic",
    "ElectroDCConduction": "ElectroDCConduction",
    "ElectricTransient": "ElectricTransient",
    "Matrix": "Matrix",
    "SteadyTemperatureAndFlow": [
        "NAME:SolutionTypeOption",
        "SolutionTypeOption:=",
        "SteadyState",
        "ProblemOption:=",
        "SteadyTemperatureAndFlow"
    ],
    "SteadyTemperatureOnly": [
        "NAME:SolutionTypeOption",
        "SolutionTypeOption:=",
        "SteadyState",
        "ProblemOption:=",
        "SteadyTemperatureOnly"
    ],
    "SteadyFlowOnly": [
        "NAME:SolutionTypeOption",
        "SolutionTypeOption:=",
        "SteadyState",
        "ProblemOption:=",
        "SteadyFlowOnly"
    ],
    "TransientTemperatureAndFlow": [
        "NAME:SolutionTypeOption",
        "SolutionTypeOption:=",
        "Transient",
        "ProblemOption:=",
        "SteadyTemperatureAndFlow"
    ],
    "TransientTemperatureOnly": [
        "NAME:SolutionTypeOption",
        "SolutionTypeOption:=",
        "Transient",
        "ProblemOption:=",
        "SteadyTemperatureOnly"
    ],
    "TransientFlowOnly": [
        "NAME:SolutionTypeOption",
        "SolutionTypeOption:=",
        "Transient",
        "ProblemOption:=",
        "SteadyFlowOnly"
    ],
    "NexximLNA": "NexximLNA",
    "NexximDC": "NexximDC",
    "NexximTransient": "NexximTransient",
    "NexximQuickEye": "NexximQuickEye",
    "NexximVerifEye": "NexximVerifEye",
    "NexximAMI": "NexximAMI",
    "NexximOscillatorRSF": "NexximOscillatorRSF",
    "NexximOscillator1T": "NexximOscillator1T",
    "NexximOscillatorNT": "NexximOscillatorNT",
    "NexximHarmonicBalance1T": "NexximHarmonicBalance1T",
    "NexximHarmonicBalanceNT": "NexximHarmonicBalanceNT",
    "NexximSystem": "NexximSystem",
    "NexximTVNoise": "NexximTVNoise",
    "HSPICE": "HSPICE",
    "TR": "TR",
    "Open": "Open",
    "Closed": "Closed",
    "TransientXY": ["Transient", "XY"], "TransientZ": ["Transient", "about Z"],
    "MagnetostaticXY": ["Magnetostatic", "XY"], "MagnetostaticZ": ["Magnetostatic", "about Z"],
    "EddyCurrentXY": ["EddyCurrent", "XY"], "EddyCurrentZ": ["EddyCurrent", "about Z"],
    "ElectrostaticXY": ["Electrostatic", "XY"], "ElectrostaticZ": ["Electrostatic", "about Z"],
    "ElectroDCConductionXY": ["ElectroDCConduction", "XY"], "ElectroDCConductionZ": ["ElectroDCConduction", "about Z"],
    "ElectricTransientXY": ["ElectricTransient", "XY"], "ElectricTransientZ": ["ElectricTransient", "about Z"],
    "Modal": "Modal", "Thermal": "Thermal","Structural" : "Structural",
    "IRIM" : "IRIM", "ORIM": "ORIM", "SRIM": "SRIM", "WRIM" : "WRIM", "DFIG" : "DFIG", "AFIM": "AFIM", "HM" : "HM",
    "RFSM" :"RFSM", "RASM": "RASM", "RSM" : "RSM", "ISM" : "ISM", "APSM" : "APSM", "IBDM" : "IBDM", "ABDM" : "ABDM",
    "TPIM" : "TPIM", "SPIM" : "SPIM", "TPSM" : "TPSM", "BLDC" : "BLDC", "ASSM" : "ASSM", "PMDC" : "PMDC", "SRM" : "SRM",
    "LSSM" : "LSSM", "UNIM" : "UNIM", "DCM" : "DCM", "CPSM" : "CPSM", "NSSM" :"NSSM"
}

model_names = {
    "Maxwell 2D": "Maxwell2DModel",
    "Maxwell 3D": "Maxwell3DModel",
    "Twin Builder": "SimplorerCircuit",
    "Circuit Design": "NexximCircuit",
    "2D Extractor": "2DExtractorModel",
    "Q3D Extractor": "Q3DModel",
    "HFSS": "HFSSModel",
    "Mechanical": "MechanicalModel",
    "Icepak": "IcepakModel",
    "RMxprtSolution": "RMxprtDesign",
    "ModelCreation": "RMxprtDesign",
    "HFSS 3D Layout Design": "PlanarEMCircuit",
    "EMIT Design": "EMIT Design",
}


def list_difference(list1, list2):
    return list(set(list1) - set(list2))

class DesignCache(object):
    """DesignCache class.
    
    The cache object analyzes the differences in the state of a design between two points in time.

    The contents of the design tracked in the Message Manager currently are:

        * global-level messages
        * project-level messages
        * design-level messages
    
    Parameters
    ----------
    parent: str
        Name of the parent object.
        
    """
    def __init__(self, parent):
        self._parent = parent
        self._allow_errors_local = []
        self._allow_errors_global = []
        self.clear()
        self._snapshot = self.design_snapshot()

    @property
    def allowed_error_messages(self):
        return self._allow_errors_global + self._allow_errors_local

    def ignore_error_message_local(self, msg):
        self._allow_errors_local.append("[error] {}".format(msg))

    def ignore_error_message_global(self, msg):
        self._allow_errors_global.append("[error] {}".format(msg))

    @property
    def no_change(self):
        """Whether the design snapshot is unchanged since the last update.
        
        Returns
        --------
        bool
            ``True`` when the design snapshot is unchanged since the last update; ``False`` otherwise.
        """
        return self._no_change

    @property
    def delta_global_messages(self):
        """List of any new or missing global-level messages since the last update.
        
        Returns
        -------
        list
            List of any new or missing global-level messages since the last update.
        """
        return self._delta_global_messages

    @property
    def delta_project_messages(self):
        """List of any new or missing project-level messages since the last update.
        
        Returns
        -------
        list
            List of any new or missing project-level messages since the last update.
        """
        return self._delta_global_messages

    @property
    def delta_design_messages(self):
        """List of any new or missing design-level messages since the last update.
        
        Returns
        -------
        list
            List of any new or missing design-level messages since the last update.
        """
        return self._delta_design_messages

    @property
    def delta_error_messages(self):
        """List of any new or missing error messages since the last update.
        
        Returns
        -------
        list
            List of any new or missing error messages since the last update.
        """
        return self._new_error_messages

    @property
    def no_new_messages(self):
        """Whether new messages have appeared since the last update or since the Message Manager was cleared.
        
        Returns
        -------
        bool
            ``True`` if new messages have appeared since the last update or since the Message Manager was
            cleared; ``False`` otherwise.
        """
        return not bool(self._delta_messages)

    @property
    def no_new_errors(self):
        """Whether any new error messages have appeared since the last uodate.
        
        Returns
        -------
        bool
            ``True`` if new error messages have appeared since the last update; ``False`` otherwise.
        """
        return not bool(self._new_error_messages)

    @property
    def no_new_warnings(self):
        """Whether any new warning messages have appeared since the last uodate.
        Returns
        -------
        bool
            ``True`` if new error messages have appeared since the last update; ``False`` otherwise.
        """
        return not bool(self._new_warning_messages)

    @property
    def no_change(self):
        """Whether cache elements are unchanged since the last update.
        
        Returns
        -------
        bool
            ``True`` if the cache elements are unchanged since the last update.
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
            "Solids:":  self._parent.modeler.primitives.solid_names,
            "Lines:":  self._parent.modeler.primitives.line_names,
            "Sheets": self._parent.modeler.primitives.sheet_names,
            "DesignName" : self._parent.design_name
        }
        return snapshot

    def clear(self):
        """Clear the cached values."""
        self._messages_global_level = []
        self._messages_project_level = []
        self._messages_design_level = []

    def update(self):
        """Retrieve the current state values from the design and perform a delta calculation with the cached values.
        Then replace the cached values with the current values. 
        
        .. note::
           The update is done automatically when the property
           ``'no_change'`` is accessed.
        """
        
        messages = self._parent._messenger.messages

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
        self._delta_messages_unfiltered = self._delta_global_messages + self._delta_project_messages + self._delta_design_messages

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
    """Design class. 
    
    This class contains all functions and objects connected to the active project and design.
    
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
    specified_version: str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default 
        is ``False``, in which case AEDT launches in the graphical mode.  
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    release_on_exit : bool, optional
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
        pyaedt_details += "Project Name: {}    Design Name{} \n".format(self.project_name, self.design_name)
        pyaedt_details += "Project Path: \"{}\" \n".format(self.project_path)
        return pyaedt_details

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    def __enter__(self):
        pass

    @aedt_exception_handler
    def __getitem__(self, variable_name):
        return self.variable_manager[variable_name].string_value

    @aedt_exception_handler
    def __setitem__(self, variable_name, variable_value):
        self.variable_manager[variable_name] = variable_value
        return True

    def __init__(self, design_type, project_name=None, design_name=None, solution_type=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        # Get Desktop from global Desktop Environment
        self._project_dictionary = OrderedDict()
        self.boundaries = OrderedDict()
        self.project_datasets = {}
        self.design_datasets = {}
        main_module = sys.modules['__main__']
        if "pyaedt_initialized" not in dir(main_module):
            Desktop(specified_version, NG, AlwaysNew, release_on_exit, student_version)
        self._project_dictionary = {}
        self._mttime = None
        self._desktop = main_module.oDesktop
        self._aedt_version = main_module.AEDTVersion
        self._desktop_install_dir = main_module.sDesktopinstallDirectory
        self._messenger = AEDTMessageManager(self)
        self.logger = logging.getLogger(__name__)

        assert design_type in design_solutions, "Invalid design type is specified: {}.".format(design_type)
        self._design_type = design_type
        if solution_type:
            assert solution_type in design_solutions[design_type], \
                "Invalid solution type {0} exists for design type {1}.".format(solution_type, design_type)
        self._solution_type = solution_type
        self._odesign = None
        self._oproject = None
        self._design_type = design_type
        self.oproject = project_name
        self.odesign = design_name
        self._variable_manager = VariableManager(self)
        self.solution_type = self._solution_type
        self.project_datasets = self._get_project_datasets()
        self.design_datasets = self._get_design_datasets()

    @property
    def project_properies(self):
        """Project properties."""
        if os.path.exists(self.project_file):
            _mttime = os.path.getmtime(self.project_file)
            if _mttime != self._mttime:
                self._project_dictionary = load_entire_aedt_file(self.project_file)
                self._mttime = _mttime
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
           Dictionary of design properties.

        """
        if not design_name:
            design_name = self.design_name
        try:
            if model_names[self._design_type] in self.project_properies['AnsoftProject']:
                designs = self.project_properies['AnsoftProject'][model_names[self._design_type]]
                if type(designs) is list:
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

        """
        version = self.odesktop.GetVersion()
        return get_version_env_variable(version)

    @property
    def design_name(self):
        """Name of the parent AEDT design.

        Returns
        -------
        str
            Name of the parent AEDT design.

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
    def design_name(self, new_name):
        """
        Property

        :return: Change the name of the parent AEDT Design
        """

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
        """List of designs.

        Returns
        -------
        list
            List of the designs.

        """
        deslist = list(self.oproject.GetTopDesignList())
        updateddeslist = []
        for el in deslist:
            m = re.search(r'[^;]+$', el)
            updateddeslist.append(m.group(0))
        return updateddeslist

    @property
    def design_type(self):
        """Design type.

        Parameters
        ----------
        type
            Type of the design.

        Returns
        -------

        """
        #return self._odesign.GetDesignType()
        return self. _design_type


    @property
    def project_name(self):
        """Project name.

        Returns
        -------
        str
            Name of the project.

        """
        if self._oproject:
            return self._oproject.GetName()
        else:
            return None

    @property
    def project_list(self):
        """Project list.     
        
        Returns
        -------
        list
            List of projects.

        """
        return list(self._desktop.GetProjectList())

    @property
    def project_path(self):
        """Project path.

        Returns
        -------
        str
            Path to the project file.

        """
        return os.path.normpath(self._oproject.GetPath())

    @property
    def project_file(self):
        """Project file.

        Returns
        -------
        str
            Full absolute name and path for the project file.

        """
        return os.path.join(self.project_path, self.project_name + '.aedt')

    @property
    def lock_file(self):
        """Lock file.
      
        Returns
        -------
        str
            Full absolute name and path for the project lock file.
        
        """
        return os.path.join(self.project_path, self.project_name + '.aedt.lock')

    @property
    def results_directory(self):
        """Property
       
        Returns
        -------
        str
            Full absolute path for the ``aedtresults`` directory.
  
        """
        return os.path.join(self.project_path, self.project_name + '.aedtresults')

    @property
    def solution_type(self):
        """Solutiion type.

        Returns
        -------
        str
            Type of the solution.

        """
        try:
            return self._odesign.GetSolutionType()
        except:
            if self.design_type == "Q3D Extractor":
                return "Matrix"
            elif self.design_type == "HFSS 3D Layout Design":
                return "HFSS3DLayout"
            else:
                return None

    @solution_type.setter
    def solution_type(self, soltype):
        """

        Parameters
        ----------
        soltype :
            SolutionType object

        Returns
        -------

        """

        if soltype:
            sol = solutions_settings[soltype]
            try:
                if self.design_type == "Maxwell 2D":
                    self.odesign.SetSolutionType(sol[0],sol[1])
                else:
                    self.odesign.SetSolutionType(sol)
            except:
                pass



    @property
    def valid_design(self):
        """Valid design.
       
        Returns
        -------
        bool
            ``True`` when project and design exists, ``False`` otherwise.

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

        """
        return os.path.normpath(self._desktop.GetPersonalLibDirectory())

    @property
    def userlib(self):
        """UserLib directory.

        Returns
        -------
        str
            Full absolute path for the ``UserLib`` directory.

        """
        return os.path.normpath(self._desktop.GetUserLibDirectory())

    @property
    def syslib(self):
        """SysLib directory

        Returns
        -------
        str
            Full absolute path for the ``SysLib`` directory.

        """
        return os.path.normpath(self._desktop.GetLibraryDirectory())

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
        return os.path.realpath(os.path.join(self.src_dir, '..'))

    @property
    def library_list(self):
        """Library list.

        Returns
        -------
        list
            List of libraries: ``[syslib, userlib, personallib]``

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
        return os.path.normpath(self._desktop.GetTempDirectory())

    @property
    def toolkit_directory(self):
        """Path to the toolkit directory.

        Returns
        -------
        str
            Full absolute path for the ``toolkit`` directory for this project. 
            If this directory does not exist, it is created.

        """
        toolkit_directory = os.path.join(self.project_path, self.project_name + '.toolkit')
        if not os.path.isdir(toolkit_directory):
            os.mkdir(toolkit_directory)
        return toolkit_directory

    @property
    def working_directory(self):
        """Path to the working directory.

        Returns
        -------
         str
             Full absolute path for the working directory for this project. 
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
        return design_solutions[self._design_type][0]

    @property
    def odesign(self):
        """Design object.

        Returns
        -------
        type
            Design object.

        """
        return self._odesign

    @odesign.setter
    def odesign(self, des_name):
        """

        Parameters
        ----------
        des_name :


        Returns
        -------

        """
        warning_msg = None
        activedes = des_name
        if des_name:
            if self._assert_consistent_design_type(des_name) == des_name:
                self._insert_design(self._design_type, design_name=des_name, solution_type=self._solution_type)
        else:
            # self._odesign = self._oproject.GetActiveDesign()
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
                        warning_msg = "No consistent unique design present - inserting a new design"
                    else:
                        self._odesign = self.oproject.SetActiveDesign(activedes)
            else:
                warning_msg = "No design present - inserting a new design"

            if warning_msg:
                self.logger.debug(warning_msg)
                self._insert_design(self._design_type, solution_type=self._solution_type)
        self.boundaries = self._get_boundaries_data()

    @property
    def oboundary(self):
        """BoundarySetup module object.

        Returns
        -------
        type
            BoundarySetup module object.

        """
        return self._odesign.GetModule("BoundarySetup")

    @property
    def omodelsetup(self):
        """ModelSetup module object.

        Returns
        -------
        type
            ModelSetup module object.
            
        """
        return self._odesign.GetModule("ModelSetup")


    @property
    def oimportexport(self):
        """ImportExport module object.

        Returns
        -------
        type
            ImportExport module object.

        """
        return self.odesktop.GetTool("ImportExport")

    @property
    def oproject(self):
        """Property object.

        Returns
        -------
        type
            Project object

        """
        return self._oproject

    @oproject.setter
    def oproject(self, proj_name=None):
        """

        Parameters
        ----------
        proj_name :
             (Default value = None)

        Returns
        -------

        """
        if not proj_name:
            self._oproject = self._desktop.GetActiveProject()
        else:
            if os.path.exists(proj_name):
                if ".aedtz" in proj_name:
                    name = self._generate_unique_project_name()

                    path = os.path.dirname(proj_name)
                    self._desktop.RestoreProjectArchive(proj_name, os.path.join(path, name), True, True)
                    time.sleep(0.5)
                    proj = self._desktop.GetActiveProject()
                elif ".def" in proj_name:
                    oTool = self._desktop.GetTool("ImportExport")
                    oTool.ImportEDB(proj_name)
                    proj = self._desktop.GetActiveProject()
                    proj.Save()
                else:
                    assert not os.path.exists(
                        proj_name + ".lock"), "Project is locked. Close or remove the lock before proceeding."
                    proj = self._desktop.OpenProject(proj_name)
                    time.sleep(0.5)
                self._oproject = proj
            elif proj_name in self._desktop.GetProjectList():
                self._oproject = self._desktop.SetActiveProject(proj_name)
            else:
                self._oproject = self._desktop.NewProject()
                self._oproject.Rename(os.path.join(self.project_path, proj_name+".aedt"), True)

        if not self._oproject:
            self._oproject = self._desktop.NewProject()

    @property
    def oanalysis_setup(self):
        """AnalysisSetup module object.

        Returns
        -------
        type
            AnalysisSetup module object.

        """
        return self.odesign.GetModule("AnalysisSetup")

    @property
    def odesktop(self):
        """Desktop module object.

        Returns
        -------
        type
            Desktop module object.

        """
        return self._desktop

    @property
    def desktop_install_dir(self):
        """Desktop installation directory.

        Returns
        -------
        str
            AEDT installation directory.

        """
        return self._desktop_install_dir


    @aedt_exception_handler
    def add_info_message(self, message_text, message_type=None):
        """Add a type 0 "Info" message to the active design level of the Message Manager tree.

                Also add an info message to the logger if the handler is present.

                Parameters
                ----------
                message_text : str
                    Text to display as the info message.
                message_type : str, optional
                    Level to add the info message to. Options are ``"Global"``,
                    ``"Project"``, and ``"Design"``. The default is ``None``,
                    in which case the info message gets added to the ``"Design"``
                    level.

                Returns
                -------
                bool
                    ``True`` if succeeded.

                Examples
                --------
                >>> from pyaedt import Hfss
                >>> hfss = Hfss()
                >>> hfss.add_info_message("Global info message", "Global")
                >>> hfss.add_info_message("Project info message", "Project")
                >>> hfss.add_info_message("Design info message")

                """
        self._messenger.add_info_message(message_text, message_type)
        return True

    @aedt_exception_handler
    def add_warning_message(self, message_text, message_type=None):
        """Add a type 0 "Warning" message to the active design level of the Message Manager tree.

                Also add an info message to the logger if the handler is present.

                Parameters
                ----------
                message_text : str
                    Text to display as the warning message.
                message_type : str, optional
                    Level to add the warning message to. Options are ``"Global"``,
                    ``"Project"``, and ``"Design"``. The default is ``None``,
                    in which case the warning message gets added to the ``"Design"``
                    level.

                Returns
                -------
                bool
                    ``True`` if succeeded.

                Examples
                --------
                >>> from pyaedt import Hfss
                >>> hfss = Hfss()
                >>> hfss.add_warning_message("Global warning message", "Global")
                >>> hfss.add_warning_message("Project warning message", "Project")
                >>> hfss.add_warning_message("Design warning message")

                """
        self._messenger.add_warning_message(message_text, message_type)
        return True

    @aedt_exception_handler
    def add_error_message(self, message_text, message_type=None):
        """Add a type 0 "Error" message to the active design level of the Message Manager tree.

                Also add an error message to the logger if the handler is present.

                Parameters
                ----------
                message_text : str
                    Text to display as the error message.
                message_type : str, optional
                    Level to add the error message to. Options are ``"Global"``,
                    ``"Project"``, and ``"Design"``. The default is ``None``,
                    in which case the error message gets added to the ``"Design"``
                    level.

                Returns
                -------
                bool
                    ``True`` if succeeded.

                Examples
                --------
                >>> from pyaedt import Hfss
                >>> hfss = Hfss()
                >>> hfss.add_error_message("Global error message", "Global")
                >>> hfss.add_error_message("Project error message", "Project")
                >>> hfss.add_error_message("Design error message")

                """
        self._messenger.add_error_message(message_text, message_type)
        return True

    @property
    def variable_manager(self):
        """Variable manager.
        
        This object is used to create and manage project design and postprocessing variables.

        Returns
        -------
        VariableManager
            Variable manager object.
            
        """
        return self._variable_manager

    @aedt_exception_handler
    def _optimetrics_variable_args(self, arg, optimetrics_type, variable_name, min_val=None, max_val=None, tolerance=None, probability=None, mean=None, enable=True):
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
        arg2 = ["NAME:"+optimetrics_type, "Included:=", enable]
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

    @aedt_exception_handler
    def activate_variable_statistical(self, variable_name, min_val=None, max_val=None, tolerance=None, probability=None, mean=None):
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

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Statistical", variable_name, min_val, max_val, tolerance, probability, mean)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def activate_variable_optimization(self, variable_name, min_val=None, max_val=None):
        """Activate optimization analysis for a variable and optionally set up ranges.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_val : str, optional
            Minimum value for the variable. The default is ``None``.
        max_val : str, optional
            Maximum value for the variable. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Optimization",variable_name, min_val, max_val)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
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

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Sensitivity",variable_name, min_val, max_val)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def activate_variable_tuning(self, variable_name, min_val=None, max_val=None):
        """Activate tuning analysis for a variable and optionally set up ranges.
        
        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_val : str, optional
            Minimum value for the variable. The default is ``None``.
        max_val : str, optional
            Maximum value for the variable. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Tuning",variable_name, min_val, max_val)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def deactivate_variable_statistical(self, variable_name):
        """Deactivate statistical analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Statistical",variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def deactivate_variable_optimization(self, variable_name):
        """Deactivate optimization analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Optimization", variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def deactivate_variable_sensitivity(self, variable_name):
        """Deactivate sensitivity analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Sensitivity",variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def deactivate_variable_tuning(self, variable_name):
        """Deactivate tuning analysis for a variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:AllTabs"]
        self._optimetrics_variable_args(arg, "Tuning",variable_name, enable=False)
        if "$" in variable_name:
            self.oproject.ChangeProperty(arg)
        else:
            self.odesign.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def _get_boundaries_data(self):
        """Retrieve data for boundaries."""
        boundaries = []
        if self.design_properties and 'BoundarySetup' in self.design_properties:
            for ds in self.design_properties['BoundarySetup']["Boundaries"]:
                try:
                    if type(self.design_properties['BoundarySetup']["Boundaries"][ds]) is OrderedDict:
                        boundaries.append(BoundaryObject(self, ds,
                                                        self.design_properties['BoundarySetup']["Boundaries"][ds],
                                                        self.design_properties['BoundarySetup']["Boundaries"][ds][
                                                            'BoundType']))
                except:
                    pass
        return boundaries


    @aedt_exception_handler
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
        if 'Coordinate' in datas:
            for el in datas['Coordinate']:
                x.append(el['CoordPoint'][0])
                y.append(el['CoordPoint'][1])
                if numcol > 2:
                    z.append(el['CoordPoint'][2])
                    v.append(el['CoordPoint'][3])
        else:
            new_list = [datas['Points'][i:i + numcol] for i in range(0, len(datas['Points']), numcol)]
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

    @aedt_exception_handler
    def _get_project_datasets(self):
        """ """
        datasets = {}
        try:
            for ds in self.project_properies['AnsoftProject']['ProjectDatasets']['DatasetDefinitions']:
                datas = self.project_properies['AnsoftProject']['ProjectDatasets']['DatasetDefinitions'][ds]['Coordinates']
                datasets[ds] = self._get_ds_data(ds, datas)
        except:
            pass
        return datasets


    @aedt_exception_handler
    def _get_design_datasets(self):
        """ """
        datasets = {}
        try:
            for ds in self.design_properties['ModelSetup']['DesignDatasets']['DatasetDefinitions']:
                datas = self.project_properies['ModelSetup']['DesignDatasets']['DatasetDefinitions'][ds]['Coordinates']
                datasets[ds] = self._get_ds_data(ds, datas)
        except:
            pass
        return datasets

    @aedt_exception_handler
    def close_desktop(self):
        """Close the desktop and release AEDT.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        force_close_desktop()
        return True

    @aedt_exception_handler
    def release_desktop(self, close_projects=True, close_desktop=True):
        """Release the desktop.

        Parameters
        ----------
        close_projects: bool, optional
            Whether to close all projects. The default is ``True``.
        close_desktop: bool, optional
            Whether to close the desktop after releasing it. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        release_desktop(close_projects, close_desktop)
        return True

    @aedt_exception_handler
    def generate_temp_project_directory(self, subdir_name):
        """Generate a unique directory string to save a project to.

        This method creates a directory for storage of a project in the ``temp`` directory 
        of the AED installation because this location is guaranteed to exist. If the '`name`' 
        parameter is defined, a subdirectory is added within the ``temp`` directory and a 
        hash suffix is added to ensure that this directory is empty and has a unique name.

        Parameters
        ----------
        subdir_name : str
            Base name of the subdirectory to create in the ``temp`` directory.

        Returns
        -------
        str
            Base name of the subdirectory created.

        Examples
        --------
        >>> m3d = Maxwell3d()
        >>> proj_directory = m3d.generate_temp_project_directory("Example")

        """
        base_path = self.temp_directory

        if not isinstance(subdir_name, str):
            self._messenger.add_error_message("Input argument 'subdir' must be a string")
            return False
        dir_name = generate_unique_name(subdir_name)
        project_dir = os.path.join(base_path, dir_name)
        try:
            if not os.path.exists(project_dir): os.makedirs(project_dir)
            return project_dir
        except OSError:
            return False


    @aedt_exception_handler
    def load_project(self, project_file, design_name=None, close_active_proj=False):
        """Open an AEDT project based on a project file and an optional design.

        Parameters
        ----------
        project_file : str
            Full path and name for the project file.
        design_name : str, optional
            Design name. The default is ``None``.
        close_active_proj : bool, optional
            Whether to close the active project. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if close_active_proj:
            self._desktop.CloseProject(self.project_name)
        proj = self._desktop.OpenProject(project_file)
        time.sleep(0.5)
        self._odesign = None
        self._oproject = None
        self.oproject = proj.GetName()
        time.sleep(0.5)
        self.odesign = design_name
        time.sleep(0.5)
        if proj:
            self.__init__(projectname=proj.GetName(), designname=design_name)
            return True
        else:
            return False

    @aedt_exception_handler
    def create_dataset1d_design(self, dsname, xlist, ylist, xunit="", yunit=""):
        """Create a design dataset.

        Parameters
        ----------
        dsname : str
            Name of the dataset (without a prefix for a project dataset).
        xlist : list
            List of X values for the dataset.
        ylist : list
            List of y values for the dataset.
        xunit : str, optional
            Units for the X axis. The default is ``""``.
        yunit : str, optional
            Units for the Y axis. The default is ``""``.

        Returns
        -------
        type
            Dataset object when the dataset is created; ``False`` otherwise.

        """
        return self.create_dataset(dsname, xlist,ylist, is_project_dataset=False, xunit=xunit, yunit=yunit)

    @aedt_exception_handler
    def create_dataset1d_project(self, dsname, xlist, ylist, xunit="", yunit=""):
        """Create a project dataset.

        Parameters
        ----------
        dsname : str
            Name of dataset (without a prefix for a project dataset).
        xlist : list
            List of X values for the dataset.
        ylist : list
            List of Y values for the dataset.
        xunit : str, optional
            Units for the X axis. The default is ``""``.
        yunit : str, optional
            Units for the Y axis. The default is ``""``.

        Returns
        -------
        type
            Dataset object when the dataset is created; ``False`` otherwise.

        """
        return self.create_dataset(dsname, xlist,ylist, is_project_dataset=True, xunit=xunit, yunit=yunit)

    @aedt_exception_handler
    def create_dataset3d(self, dsname, xlist, ylist, zlist=None, vlist=None, xunit="", yunit="",
                       zunit="", vunit=""):
        """Create a 3D dataset.

        Parameters
        ----------
        dsname : str
            Name of the dataset (without prefix for a project dataset).
        xlist : list
            List of X values for the dataset.
        ylist : list
            List of Y values for the dataset.
        zylist : list, optional
            List of Z values for a 3D dataset only. The default is ``None``.
        vylist : list, optional
            List of V values for a 3D dataset only. The default is ``None``.
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
        type
            Dataset object when the dataset is created; ``False`` otherwise.

        """
        return self.create_dataset(dsname=dsname, xlist=xlist, ylist=ylist, zlist=zlist, vlist=vlist, xunit=xunit,
                                   yunit=yunit, zunit=zunit, vunit=vunit)

    @aedt_exception_handler
    def create_dataset(self, dsname, xlist, ylist, zlist=None, vlist=None, is_project_dataset=True, xunit="", yunit="",
                       zunit="", vunit=""):
        """Create a dataset.

        Parameters
        ----------
        dsname : str
            Name of the dataset (without prefix for a project dataset).
        xlist : list
            List of X values for the dataset.
        ylist : list
            List of Y values for the dataset.
        zylist : list, optional
            List of Z values for a 3D dataset only. The default is ``None``.
        vylist : list, optional
            List of V values for a 3D dataset only. The default is ``None``.
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
        type
            Dataset object when the dataset is created; ``False`` otherwise.

        """
        if not self.dataset_exists(dsname, is_project_dataset):
            if is_project_dataset:
                dsname = "$" + dsname
            ds = DataSet(self, dsname, xlist, ylist, zlist, vlist, xunit, yunit, zunit, vunit)
        else:
            self._messenger.add_warning_message("Dataset {} already exists".format(dsname))
            return False
        ds.create()
        if is_project_dataset:
            self.project_datasets[dsname] = ds
        else:
            self.design_datasets[dsname] = ds
        return ds

    @aedt_exception_handler
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
        if is_project_dataset and "$"+name in self.project_datasets:
            self._messenger.add_info_message("DATASET {} exists.".format("$"+name))
            return True
            #self.oproject.ExportDataSet("$"+name, os.path.join(self.temp_directory, "ds.tab"))
        elif not is_project_dataset and name in self.design_datasets:
            self._messenger.add_info_message("DATASET {} exists.".format(name))
            return True
            #self.odesign.ExportDataSet(name, os.path.join(self.temp_directory, "ds.tab"))
        self._messenger.add_info_message("DATASET {} doesn't exists.".format(name))
        return False


    @aedt_exception_handler
    def change_automatically_use_causal_materials(self, lossy_dielectric=True):
        """Enable the automatic use of causal material for lossy dielectrics.

        Parameters
        ----------
        lossy_dielectric : bool, optional
            Whether to enable causal materials. 
            The default is ``True``.

        Returns
        -------
        bool    
            ``True`` when successful, ``False`` when failed.

        """
        if lossy_dielectric:
            self._messenger.add_info_message("Enabling Automatic use of causal materials")
        else:
            self._messenger.add_info_message("Disabling Automatic use of causal materials")
        self.odesign.SetDesignSettings(
            ["NAME:Design Settings Data", "Calculate Lossy Dielectrics:=", lossy_dielectric])
        return True

    @aedt_exception_handler
    def change_material_override(self, material_override=True):
        """Enable the material override in the project.

        Parameters
        ----------
        material_override : bool, optional
            Whether to enable the material override. 
            The default is ``True``.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if material_override:
            self._messenger.add_info_message("Enabling Material Override")
        else:
            self._messenger.add_info_message("Disabling Material Override")
        self.odesign.SetDesignSettings(
            ["NAME:Design Settings Data", "Allow Material Override:=", material_override])
        return True

    @aedt_exception_handler
    def change_validation_settings(self, entity_check_level="Strict", ignore_unclassified=False,
                                   skip_intersections=False):
        """Update the validation design settings.

        Parameters
        ----------
        entity_check_level : str, optional
            Entity Level. The default is ``"Strict"``.
        ignore_unclassified : bool, optional
            Whether to ignore unclassified elements. The default is ``False``.
        skip_intersections : bool, optional
            Whether to skip intersections. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        self._messenger.add_info_message("Changing the validation design settings")
        self.odesign.SetDesignSettings(["NAME:Design Settings Data"],
                                       ["NAME:Model Validation Settings",
                                        "EntityCheckLevel:=", entity_check_level,
                                        "IgnoreUnclassifiedObjects:=", ignore_unclassified,
                                        "SkipIntersectionChecks:=", skip_intersections])
        return True

    @aedt_exception_handler
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
            name=self.project_name
        if not directory:
            directory = self.results_directory
        self._messenger.add_info_message("Cleanup folder {} from project {}".format(directory, name))
        if os.path.exists(directory):
            shutil.rmtree(directory, True)
            if not os.path.exists(directory):
                os.mkdir(directory)
        self._messenger.add_info_message("Project Directory cleaned")
        return True

    @aedt_exception_handler
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

        """
        self._messenger.add_info_message("Copy AEDT Project ")
        self.oproject.Save()
        self.oproject.SaveAs(os.path.join(path, dest + ".aedt"), True)
        return True

    @aedt_exception_handler
    def create_new_project(self, proj_name):
        """Create a project within the desktop.

        Parameters
        ----------
        proj_name :
            Name of the project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        self._messenger.add_info_message("Creating new Project ")
        prj = self._desktop.NewProject(proj_name)
        prj_name = prj.GetName()
        self.oproject = prj_name
        self.odesign = None
        return True

    @aedt_exception_handler
    def close_project(self, name=None, saveproject=True):
        """Close a project.

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

        """
        msg_txt = ""
        if name:
            assert name in self.project_list, "Invalid project name {}.".format(name)
            msg_txt = "specified "+ name
        else:
            name = self.project_name
            msg_txt = "active "+ self.project_name
        self._messenger.add_info_message("Closing the {} AEDT Project".format(msg_txt), level="Global")
        if name != self.project_name:
            oproj = self.odesktop.SetActiveProject(name)
        else:
            oproj = self.oproject
        if saveproject:
            oproj.Save()
        self.odesktop.CloseProject(name)

        return True

    @aedt_exception_handler
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
            
        """
        if not name:
            name = self.design_name
        self.oproject.DeleteDesign(name)
        try:
            if fallback_design:
                new_designname = fallback_design
            else:
                if not self._oproject.GetActiveDesign():
                    new_designname = None
                    self.odesign = None
                else:
                    new_designname = self._oproject.GetActiveDesign().GetName()
            self.set_active_design(new_designname)
        except:
            pass

        return True


    @aedt_exception_handler
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

        """
        return self._variable_manager.delete_separator(separator_name)

    @aedt_exception_handler
    def delete_variable(self, sVarName):
        """Delete a variable.

        Parameters
        ----------
        sVarName :
            Name of the variable.
       
        """
        return  self.variable_manager.delete_variable(sVarName)

    @aedt_exception_handler
    def insert_design(self, design_name=None):
        """Insert a design of a specified design type. 
        
        The default design type is taked from the derived application class. 
       
        Parameters
        ----------
        design_name : str, optional
            Name of the design. The default is ``None``, in which case, the 
            default design name is ``<Design-Type>Design<_index>``. If the 
            given or default design name is in use, then an underscore and 
            index is added to ensure that the design name is unique. 
            The inserted object is assigned to the Design object.

        Returns
        -------
        str
            Name of the design.

        """
        if self.design_type == "Circuit Design" or self.design_type == "HFSS 3D Layout Design":
            self.modeler.edb.close_edb()
        self.__init__(projectname=self.project_name, designname=design_name)

    def _insert_design(self, design_type, design_name=None, solution_type=None):
        assert design_type in design_solutions, "Invalid design type for insert: {}".format(design_type)
        # self.save_project() ## Commented because it saves a Projectxxx.aedt when launched on an empty Desktop
        unique_design_name = self._generate_unique_design_name(design_name)
        if solution_type:
            assert solution_type in design_solutions[self._design_type], \
                "Solution type {0} is invalid for design type {1}.".format(solution_type, self._design_type)
        else:
            solution_type = self.default_solution_type
        if design_type == "RMxprtSolution":
            new_design = self._oproject.InsertDesign("RMxprt", unique_design_name, "Inner-Rotor Induction Machine", "")
        elif design_type == "ModelCreation":
            new_design = self._oproject.InsertDesign("RMxprt", unique_design_name, "Model Creation Inner-Rotor Induction Machine", "")
        else:
            new_design = self._oproject.InsertDesign(design_type, unique_design_name, solution_type, "")
        self._messenger.add_info_message("Added design '{0}' of type {1}.".format(unique_design_name, design_type),
                                         level='Project')
        name = new_design.GetName()
        if ";" in name:
            self.odesign = name.split(";")[1]
        else:
            self.odesign = name
        return name

    @aedt_exception_handler
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
            uName = ''.join(random.sample(char_set, 3))
            design_name = self._design_type + "_" + uName
        while design_name in self.design_list:
            if design_index:
                design_name = design_name[0:-len(suffix)]
            design_index += 1
            suffix = "_" + str(design_index)
            design_name += suffix
        return design_name

    @aedt_exception_handler
    def _generate_unique_project_name(self):
        """Generate an unique project name.

        Returns
        --------
        str
            Unique project name in the form ``"Project_<unique_name>.aedt".
        
        """
        char_set = string.ascii_uppercase + string.digits
        uName = ''.join(random.sample(char_set, 3))
        proj_name = "Project_" + uName+ ".aedt"
        return proj_name

    @aedt_exception_handler
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

        """
        self._odesign.RenameDesignInstance(self.design_name, new_name)
        self.odesign = new_name
        return True

    @aedt_exception_handler
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

        """
        self.save_project()
        active_design = self.design_name
        # open the origin project
        if os.path.exists(project_fullname):
            proj_from = self._desktop.OpenProject(project_fullname)
            proj_from_name = proj_from.GetName()
        else:
            return None
        # check if the requested design exists in the origin project
        if design_name not in [i.GetName() for i in list(proj_from.GetDesigns())]:
            return None
        # copy the source design
        proj_from.CopyDesign(design_name)
        # paste in the destination project and get the name
        self._oproject.Paste()
        new_designname = self._oproject.GetActiveDesign().GetName()
        if self._oproject.GetActiveDesign().GetDesignType() == 'HFSS 3D Layout Design':
            new_designname = new_designname[2:]  # name is returned as '2;EMDesign3'
        # close the source project
        self._desktop.CloseProject(proj_from_name)
        # reset the active design (very important)
        self._oproject.SetActiveDesign(active_design)
        self.save_project()
        self.__init__(self.project_name, new_designname)

        # return the pasted design name
        return new_designname

    @aedt_exception_handler
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
      
        """

        active_design = self.design_name
        design_list = self.design_list
        self._oproject.CopyDesign(active_design)
        self._oproject.Paste()
        newname = label
        ind = 1
        while newname in self.design_list:
            newname = label + '_' + str(ind)
            ind += 1
        actual_name = [i for i in self.design_list if i not in design_list]
        self.odesign = actual_name
        self.design_name = newname
        self.__init__(self.project_name, self.design_name)

        return True

    @aedt_exception_handler
    def export_variables_to_csv(self, filename, export_project=True, export_design=True):
        """Export a project and design variables to a CSV file.

        Parameters
        ----------
        filename : str
            Full path and name for the CSV file.
        export_project : bool, optional
            Whether to export project variables. The default is ``True``.
        export_design : bool, optional
            Whether to export design variables. The default is ``True``.
        

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        varnames = []
        desnames = []
        if export_project:
            varnames = self.oproject.GetProperties("ProjectVariableTab", "ProjectVariables")
        if export_design:
            desnames = self.odesign.GetProperties("LocalVariableTab", "LocalVariables")
        with open(filename, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Name', 'Value'])
            for el in varnames:
                value = self.oproject.GetVariableValue(el)
                filewriter.writerow([el, value])
            for el in desnames:
                value = self.odesign.GetVariableValue(el)
                filewriter.writerow([el, value])
        return True

    @aedt_exception_handler
    def read_design_data(self):
        """Read back the design data as a dictionary.
        
        Returns
        -------
        dict
            Dictionary of the design data.
        
        """
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, 'r') as fps:
            design_data = json.load(fps)
        return design_data

    @aedt_exception_handler
    def save_project(self, project_file=None, overwrite=True, refresh_obj_ids_after_save=False):
        """Save the AEDT project and add a message.

        Parameters
        ----------
        project_file : str, optional
            Full path and project file name. The default is ````None``.
        overwrite : bool, optional
            Whether to overwrite the existing project. The default is ``True``.
        refresh_obj_ids_after_save : bool, optional
            Whether to refresh object IDs after saving the project.  
            The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        msg_text = "Saving {0} Project".format(self.project_name)
        self._messenger.add_info_message(msg_text, level='Global')
        if project_file:
            self.oproject.SaveAs(project_file, overwrite)
        else:
            self.oproject.Save()
        if refresh_obj_ids_after_save:
            self.modeler.primitives._refresh_all_ids_from_aedt_file()
        return True

    @aedt_exception_handler
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

        """
        assert self.project_name != project_name, "You cannot delete the active design."
        self._desktop.DeleteProject(project_name)
        return True

    @aedt_exception_handler
    def set_active_design(self, name):
        """Change the active design to another design.

        Parameters
        ----------
        name :
            Name of the design to make active.
        
        """
        self.oproject.SetActiveDesign(name)
        self.odesign = name
        self.__init__(self.project_name, self.design_name)
        return True

    @aedt_exception_handler
    def update_registry_from_file(self, filename):
        """Update HPC options from a configuration file.

        Parameters
        ----------
        filename : str
            Full path and name of the configuration, which can be an ACF or TXT file.
        
        """
        self._desktop.SetRegistryFromFile(r'%s' % os.path.abspath(filename))
        return True

    @aedt_exception_handler
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
            ``0`` if validation failed or ``1`` if passed.

        """
        if logfile:
            return self._odesign.ValidateDesign(logfile)
        else:
            return self._odesign.ValidateDesign()


    @aedt_exception_handler
    def get_evaluated_value(self, variable_name, variation=None):
        """Return the evaluated value of a design property or project variable in SI units.
        

        Parameters
        ----------
        variable_name : str 
            Name of the project or design variable to evaluate.
        variation : str, optional
            Variation string for the evaluation. The default is ``None``,
            in which case the nominal variation is used.
            
        Examples
        --------

        >>> M3D = Maxwell3D()
        >>> M3D["p1"] = "10mm"
        >>> M3D["p2"] = "20mm"
        >>> M3D["p3"] = "P1 * p2"
        >>> eval_p3 = M3D.get_evaluated_value("p3")

        Returns
        -------
        float
            Evaluated value of the design property or project variable in SI units.

        """
        if not variation:
            variation_string = self._odesign.GetNominalVariation()
        else:
            variation_string = self.design_variation(variation_string=variation)

        si_value = self._odesign.GetVariationVariableValue(variation_string, variable_name)

        return si_value

    @aedt_exception_handler
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
                self._variable_manager.set_variable("pyaedt_evaluator", expression=expression_string,
                                                    readonly=True, hidden=True, description="Internal_Evaluator")
            except:
                raise("Invalid string expression {}".expression_string)

            # Extract the numeric value of the expression (in SI units!)
            return self._variable_manager.variables["pyaedt_evaluator"].value

    @aedt_exception_handler
    def design_variation(self, variation_string=None):
        """Generate a string to specify a desired variation.

        This method converts a user input string defining a desired solution variation into a valid
        string taking into account all existing design properties and project variables, including 
        dependent (non-sweep) properties.

        This is needed because the standard function `GetVariationVariableValue` does not work for obtaining
        values of dependent (non-sweep variables). Using the new beta feature object-oriented
        scripting model could make this redundant in future releases.

        Parameters
        ----------
        variation_string : str, optional
            Variation string. For example, ``"p1=1mm" or ``"p2=3mm"``.

        Returns
        -------
        str
            String specifying the desired variation.

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

    @aedt_exception_handler
    def _assert_consistent_design_type(self, des_name):
        """Assert consistent design type.

        Parameters
        ----------
        des_name : str
            Name of the design.


        Returns
        -------

        """
        if des_name in self.design_list:
            self._odesign = self._oproject.SetActiveDesign(des_name)
            dtype = self._odesign.GetDesignType()
            if dtype != "RMxprt":
                assert dtype == self._design_type, \
                    "Error: Specified design is not of type {}.".format(self._design_type)
            else:
                assert ("RMxprtSolution" == self._design_type) or ("ModelCreation" == self._design_type), \
                    "Error: Specified design is not of type {}.".format(self._design_type)
            return True
        else:
            return des_name

    @aedt_exception_handler
    def _check_solution_consistency(self):
        """Check solution consistency. """
        if self._solution_type:
            return self._odesign.GetSolutionType() in self._solution_type
        else:
            return True

    @aedt_exception_handler
    def _check_design_consistency(self):
        """ """
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == self._design_type:
            consistent = self._check_solution_consistency()
        return consistent
