"""
Design Module
-------------

Description
===========
This class contains all the basic Project information and
objects. since it is hinerithed in the Main Tool class it will be a
simple call from it

Examples
--------

>>> hfss = HFSS()

Return the oProject object

>>> hfss.oproject


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
from collections import OrderedDict
from .MessageManager import AEDTMessageManager
from .Variables import VariableManager, DataSet
from ..desktop import exception_to_desktop, Desktop, force_close_desktop, release_desktop, get_version_env_variable
from ..generic.LoadAEDTFile import load_entire_aedt_file
from ..generic.general_methods import aedt_exception_handler
from ..modules.Boundary import BoundaryObject

try:
    import webbrowser
except ImportError:
    warnings.warn("webbrowser not supported")

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
    ]
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

#TODO: refactor this to Generic ?
def _variation_string_to_dict(variation_string):
    """Helper function to convert a list of "="-separated strings into a dictionary

    Returns
    -------
    dict
    """
    var_data = variation_string.split()
    variation_dict = {}
    for var in var_data:
        pos_eq = var.find("=")
        var_name = var[0:pos_eq]
        var_value = var[pos_eq+1:].replace('\'', '')
        variation_dict[var_name] = var_value
    return variation_dict

class Design(object):
    """Class Design. Contains all functions and objects connected to the active Project and Design"""
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
        assert variable_name in self.variable_manager.variables, "Variable {0} dies not exist !".format(variable_name)
        return self.variable_manager[variable_name].string_value

    @aedt_exception_handler
    def __setitem__(self, variable_name, variable_value):
        self.variable_manager[variable_name] = variable_value
        return True

    def __init__(self, design_type, project_name=None, design_name=None, solution_type=None):
        # Get Desktop from global Desktop Environment
        self._project_dictionary = OrderedDict()
        self.boundaries = OrderedDict()
        self.project_datasets = {}
        self.design_datasets = {}
        main_module = sys.modules['__main__']
        if "pyaedt_initialized" not in dir(main_module):
            Desktop()
        self._project_dictionary = {}
        self._mttime = None
        self._desktop = main_module.oDesktop
        self._aedt_version = main_module.AEDTVersion
        self._desktop_install_dir = main_module.sDesktopinstallDirectory
        self._messenger = AEDTMessageManager(self)

        assert design_type in design_solutions, "Invalid design type specified: {}".format(design_type)
        self._design_type = design_type
        if solution_type:
            assert solution_type in design_solutions[design_type], \
                "Invalid solution type {0} for design type {1}".format(solution_type, design_type)
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
        """ """
        if os.path.exists(self.project_file):
            _mttime = os.path.getmtime(self.project_file)
            if _mttime != self._mttime:
                self._project_dictionary = load_entire_aedt_file(self.project_file)
                self._mttime = _mttime
        return self._project_dictionary

    @property
    def design_properties(self, design_name=None):
        """

        Parameters
        ----------
        design_name :
             (Default value = None)

        Returns
        -------

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
        """Property
        
        :return: AEDT Version

        Parameters
        ----------

        Returns
        -------

        """
        version = self.odesktop.GetVersion()
        return get_version_env_variable(version)

    @property
    def design_name(self):
        """Name of the parent AEDT Design.

        Returns
        -------
        str
            Name of the parent AEDT Design.

        Examples
        --------
        Set the design name.

        >>> hfss = HFSS()
        >>> hfss.design_name = 'new_design'

        """
        name = self.odesign.GetName()
        if ";" in name:
            return name.split(";")[1]
        else:
            return name

    @design_name.setter
    def design_name(self, new_name):
        if ";" in new_name:
            new_name = new_name.split(";")[1]
        # src_dir = self.working_directory
        old_name = self.design_name
        self.odesign.RenameDesignInstance(old_name, new_name)

    @property
    def design_list(self):
        """List of available designs

        Returns
        -------

        """
        deslist = list(self.oproject.GetTopDesignList())
        updateddeslist = []
        for el in deslist:
            m = re.search(r'[^;]+$', el)
            updateddeslist.append(m.group(0))
        return updateddeslist

    @property
    def design_type(self):
        """Property
        
        :return: Design Type

        Parameters
        ----------

        Returns
        -------

        """
        return self._odesign.GetDesignType()

    @property
    def project_name(self):
        """Property
        
        :return: Project Name

        Parameters
        ----------

        Returns
        -------

        """
        return self._oproject.GetName()

    @property
    def project_list(self):
        """Property
        
        :return: List of available Projects

        Parameters
        ----------

        Returns
        -------

        """
        return list(self._desktop.GetProjectList())

    @property
    def project_path(self):
        """Property
        
        :return: Project Path

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.normpath(self._oproject.GetPath())

    @property
    def project_file(self):
        """Property
        
        :return: Full absolute Project name and path

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.join(self.project_path, self.project_name + '.aedt')

    @property
    def lock_file(self):
        """Property
        
        :return: Full absolute Project lock file

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.join(self.project_path, self.project_name + '.aedt.lock')

    @property
    def results_directory(self):
        """Property
        
        :return: Full absolute path of the aedtresults directory

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.join(self.project_path, self.project_name + '.aedtresults')

    @property
    def solution_type(self):
        """Property
        
        :return: Solution Type

        Parameters
        ----------

        Returns
        -------

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
        """Property
        
        :return: True if oproject and odesign exists

        Parameters
        ----------

        Returns
        -------

        """
        return self._oproject and self._odesign

    @property
    def personallib(self):
        """Property
        
        :return: Full absolute path of the PersonalLib directory

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.normpath(self._desktop.GetPersonalLibDirectory())

    @property
    def userlib(self):
        """Property
        
        :return: Full absolute path of the UserLib directory

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.normpath(self._desktop.GetUserLibDirectory())

    @property
    def syslib(self):
        """Property
        
        :return: Full absolute path of the SysLib directory

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.normpath(self._desktop.GetLibraryDirectory())

    @property
    def src_dir(self):
        """Property
        
        :return: Full absolute path of the python directory

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.dirname(os.path.realpath(__file__))

    @property
    def pyaedt_dir(self):
        """Property
        
        :return: Full absolute path of the pyaedt Root Parent

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.realpath(os.path.join(self.src_dir, '..'))

    @property
    def library_list(self):
        """Property
        
        :return: list of [syslub, userlib, personallib]

        Parameters
        ----------

        Returns
        -------

        """
        return [self.syslib, self.userlib, self.personallib]

    @property
    def temp_directory(self):
        """Property
        
        :return: Full absolute path of the TEMP directory

        Parameters
        ----------

        Returns
        -------

        """
        return os.path.normpath(self._desktop.GetTempDirectory())

    @property
    def toolkit_directory(self):
        """Property
        
        :return: Full absolute path of the toolkit directory for this project - creates it if does not exist

        Parameters
        ----------

        Returns
        -------

        """
        toolkit_directory = os.path.join(self.project_path, self.project_name + '.toolkit')
        if not os.path.isdir(toolkit_directory):
            os.mkdir(toolkit_directory)
        return toolkit_directory

    @property
    def working_directory(self):
        """Property
        
        :return: Full absolute path of the working directory for this project - creates it if does not exist

        Parameters
        ----------

        Returns
        -------

        """
        working_directory = os.path.join(self.toolkit_directory, self.design_name)
        if not os.path.isdir(working_directory):
            os.mkdir(working_directory)
        return working_directory

    @property
    def default_solution_type(self):
        """Property
        
        :return: Default solution type for the current application running

        Parameters
        ----------

        Returns
        -------

        """
        return design_solutions[self._design_type][0]

    @property
    def odesign(self):
        """Property
        
        :return: oDesign object

        Parameters
        ----------

        Returns
        -------

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
                self.insert_design(self._design_type, design_name=des_name, solution_type=self._solution_type)
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
                self._messenger.add_warning_message(warning_msg, level='Project')
                self.insert_design(self._design_type, solution_type=self._solution_type)
        self.boundaries = self._get_boundaries_data()

    @property
    def oboundary(self):
        """Property
        
        :return: BoundarySetup Module object

        Parameters
        ----------

        Returns
        -------

        """
        return self._odesign.GetModule("BoundarySetup")

    @property
    def omodelsetup(self):
        """Property
        
        :return: ModelSetup Module object

        Parameters
        ----------

        Returns
        -------

        """
        return self._odesign.GetModule("ModelSetup")


    @property
    def oimportexport(self):
        """Property
        
        :return: ImportExport Module object

        Parameters
        ----------

        Returns
        -------

        """
        return self.odesktop.GetTool("ImportExport")

    @property
    def oproject(self):
        """Property
        
        :return: oProject object

        Parameters
        ----------

        Returns
        -------

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
                        proj_name + ".lock"), "Project Is Locked. Close or remove the lock before proceeding"
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
        """Property
        
        :return: AnalysisSetup Module object

        Parameters
        ----------

        Returns
        -------

        """
        return self.odesign.GetModule("AnalysisSetup")

    @property
    def odesktop(self):
        """Property
        
        :return: oDesktop Module object

        Parameters
        ----------

        Returns
        -------

        """
        return self._desktop

    @property
    def desktop_install_dir(self):
        """Property
        
        :return: AEDT Install Dir

        Parameters
        ----------

        Returns
        -------

        """
        return self._desktop_install_dir

    @property
    def messenger(self):
        """Property
        
        :return: Messenger object that can be used for logging on log file and on AEDT Message Windows

        Parameters
        ----------

        Returns
        -------

        """
        return self._messenger

    @property
    def variable_manager(self):
        """Property
        
        :return: Variable maanager that can be used to create and manage Project, Design and PostProcessing Variables

        Parameters
        ----------

        Returns
        -------

        """
        return self._variable_manager

    @aedt_exception_handler
    def _optimetrics_variable_args(self, arg, optimetrics_type, variable_name, min_val=None, max_val=None, tolerance=None, probability=None, mean=None, enable=True):
        """

        Parameters
        ----------
        arg :
            
        optimetrics_type :
            
        variable_name :
            
        min_val :
             (Default value = None)
        max_val :
             (Default value = None)
        tolerance :
             (Default value = None)
        probability :
             (Default value = None)
        mean :
             (Default value = None)
        enable :
             (Default value = True)

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
        """Activate Statitistical Analysis for variable selected. Optionally setup ranges

        Parameters
        ----------
        variable_name :
            name of the variable
        min_val :
            Minimum value for variable. Optional (Default value = None)
        max_val :
            Maximum value for variable. Optional (Default value = None)
        tolerance :
            Tolerance value for variable. Optional (Default value = None)
        probability :
            Probability value for variable. Optional (Default value = None)
        mean :
            Mean value for variable. Optional (Default value = None)

        Returns
        -------
        type
            Bool

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
        """Activate Optimization Analysis for variable selected. Optionally setup ranges

        Parameters
        ----------
        variable_name :
            name of the variable
        min_val :
            Minimum value for variable. Optional (Default value = None)
        max_val :
            Maximum value for variable. Optional (Default value = None)

        Returns
        -------
        type
            Bool

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
        """Activate Sensitivity Analysis for variable selected. Optionally setup ranges

        Parameters
        ----------
        variable_name :
            name of the variable
        min_val :
            Minimum value for variable. Optional (Default value = None)
        max_val :
            Maximum value for variable. Optional (Default value = None)

        Returns
        -------
        type
            Bool

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
        """Activate Tuning Analysis for variable selected. Optionally setup ranges

        Parameters
        ----------
        variable_name :
            name of the variable
        min_val :
            Minimum value for variable. Optional (Default value = None)
        max_val :
            Maximum value for variable. Optional (Default value = None)

        Returns
        -------
        type
            Bool

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
        """Deactivate Statistical Analysis for variable selected.

        Parameters
        ----------
        variable_name :
            name of the variable

        Returns
        -------
        type
            Bool

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
        """Deactivate Optimization Analysis for variable selected.

        Parameters
        ----------
        variable_name :
            name of the variable

        Returns
        -------
        type
            Bool

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
        """Deactivate Sensitivity Analysis for variable selected.

        Parameters
        ----------
        variable_name :
            name of the variable

        Returns
        -------
        type
            Bool

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
        """Deactivate Tuning Analysis for variable selected.

        Parameters
        ----------
        variable_name :
            name of the variable

        Returns
        -------
        type
            Bool

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
        """ """
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
        """:return: Close the Desktop and release the tool"""
        force_close_desktop()
        return True

    @aedt_exception_handler
    def release_desktop(self):
        """:return: Release the desktop by keeping it open"""
        release_desktop()
        return True


    @aedt_exception_handler
    def load_project(self, project_file, design_name=None, close_active_proj=False):
        """Open aedt project based on project file. Design is optional

        Parameters
        ----------
        project_file :
            full path project file name
        design_name :
            optional design name (Default value = None)
        close_active_proj :
            bool (Default value = False)

        Returns
        -------
        type
            bool

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
            return True
        else:
            return False

    @aedt_exception_handler
    def create_dataset1d_design(self, dsname, xlist, ylist, xunit="", yunit=""):
        """Create a Design dataset

        Parameters
        ----------
        dsname :
            name of dataset (without prefix for project datasets)
        xlist :
            list of x values of dataset
        ylist :
            list of y values of dataset
        xunit :
            optional x unit (Default value = "")
        yunit :
            optional y unit (Default value = "")

        Returns
        -------
        type
            Dataset object if dataset is created. False if not

        """
        return self.create_dataset(dsname, xlist,ylist, is_project_dataset=False, xunit=xunit, yunit=yunit)

    @aedt_exception_handler
    def create_dataset1d_project(self, dsname, xlist, ylist, xunit="", yunit=""):
        """Create a Project dataset

        Parameters
        ----------
        dsname :
            name of dataset (without prefix for project datasets)
        xlist :
            list of x values of dataset
        ylist :
            list of y values of dataset
        xunit :
            optional x unit (Default value = "")
        yunit :
            optional y unit (Default value = "")

        Returns
        -------
        type
            Dataset object if dataset is created. False if not

        """
        return self.create_dataset(dsname, xlist,ylist, is_project_dataset=True, xunit=xunit, yunit=yunit)

    @aedt_exception_handler
    def create_dataset3d(self, dsname, xlist, ylist, zlist=None, vlist=None, xunit="", yunit="",
                       zunit="", vunit=""):
        """Create a Dataset

        Parameters
        ----------
        dsname :
            name of dataset (without prefix for project datasets)
        xlist :
            list of x values of dataset
        ylist :
            list of y values of dataset
        zlist :
            list of z values of dataset (for 3D Datasets only) (Default value = None)
        vlist :
            list of v values of dataset (for 3D Datasets only) (Default value = None)
        xunit :
            optional x unit (Default value = "")
        yunit :
            optional y unit (Default value = "")
        zunit :
            optional z unit (for 3D Datasets only) (Default value = "")
        vunit :
            optional v unit (for 3D Datasets only) (Default value = "")

        Returns
        -------
        type
            Dataset object if dataset is created. False if not

        """
        return self.create_dataset(dsname=dsname, xlist=xlist, ylist=ylist, zlist=zlist, vlist=vlist, xunit=xunit,
                                   yunit=yunit, zunit=zunit, vunit=vunit)

    @aedt_exception_handler
    def create_dataset(self, dsname, xlist, ylist, zlist=None, vlist=None, is_project_dataset=True, xunit="", yunit="",
                       zunit="", vunit=""):
        """Create a Dataset

        Parameters
        ----------
        dsname :
            name of dataset (without prefix for project datasets)
        xlist :
            list of x values of dataset
        ylist :
            list of y values of dataset
        zlist :
            list of z values of dataset (for 3D Datasets only) (Default value = None)
        vlist :
            list of v values of dataset (for 3D Datasets only) (Default value = None)
        is_project_dataset :
            bool True if is a project dataset, False if it is a design dataset (Default value = True)
        xunit :
            optional x unit (Default value = "")
        yunit :
            optional y unit (Default value = "")
        zunit :
            optional z unit (for 3D Datasets only) (Default value = "")
        vunit :
            optional v unit (for 3D Datasets only) (Default value = "")

        Returns
        -------
        type
            Dataset object if dataset is created. False if not

        """
        if not self.dataset_exists(dsname, is_project_dataset):
            if is_project_dataset:
                dsname = "$" + dsname
            ds = DataSet(self, dsname, xlist, ylist, zlist, vlist, xunit, yunit, zunit, vunit)
        else:
            self.messenger.add_warning_message("Dataset {} already exists".format(dsname))
            return False
        ds.create()
        if is_project_dataset:
            self.project_datasets[dsname] = ds
        else:
            self.design_datasets[dsname] = ds
        return ds

    @aedt_exception_handler
    def dataset_exists(self, name, is_project_dataset=True):
        """Check if a dataset exists

        Parameters
        ----------
        name :
            Name of dataset to check  (without prefix for project datasets)
        is_project_dataset :
            bool (Default value = True)

        Returns
        -------
        type
            True if dataset exists

        """
        if is_project_dataset and "$"+name in self.project_datasets:
            self.messenger.add_info_message("DATASET {} exists.".format("$"+name))
            return True
            #self.oproject.ExportDataSet("$"+name, os.path.join(self.temp_directory, "ds.tab"))
        elif not is_project_dataset and name in self.design_datasets:
            self.messenger.add_info_message("DATASET {} exists.".format(name))
            return True
            #self.odesign.ExportDataSet(name, os.path.join(self.temp_directory, "ds.tab"))
        self.messenger.add_info_message("DATASET {} doesn't exists.".format(name))
        return False


    @aedt_exception_handler
    def change_automatically_use_causal_materials(self, lossy_dielectric=True):
        """Enable or disable the automatic use of causal material for lossy dielectrics

        Parameters
        ----------
        lossy_dielectric : bool
            enable or disable causal materials (Default value = True)

        Returns
        -------

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
        """Enable the material override in the given Project

        Parameters
        ----------
        ___________ :
            
        material_override :
            bool (Default value = True)
        enable :
            or disable material override

        Returns
        -------
        type
            _______
            bool

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
        """change the validation design settings

        Parameters
        ----------
        entity_check_level : str
            Entity Level, default "Strict"
        ignore_unclassified : bool
            Ignore unclassified elements (Default value = False)
        skip_intersections : bool
            Skip Intersections (Default value = False)

        Returns
        -------
        
            bool

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
        """Delete all project name related folder

        Parameters
        ----------
        directory :
            project directory (Default value = None)
        name :
            project name (Default value = None)

        Returns
        -------

        """
        if not name:
            name=self.project_name
        if not directory:
            directory = os.path.join(self.project_path, self.project_name + ".aedtresults")
        self._messenger.add_info_message("Cleanup folder from " + name + " project files")
        if os.path.exists(directory):
            shutil.rmtree(directory, True)
            os.mkdir(directory)
        self._messenger.add_info_message("Project Directory cleaned")
        return True

    @aedt_exception_handler
    def copy_project(self, path, dest):
        """Copy the given project to another destination
        Save the project before copying it

        Parameters
        ----------
        path :
            destination project path
        dest :
            name of the project

        Returns
        -------

        """
        self._messenger.add_info_message("Copy AEDT Project ")
        self.oproject.Save()
        self.oproject.SaveAs(os.path.join(path, dest + ".aedt"), True)
        return True

    @aedt_exception_handler
    def create_new_project(self, proj_name):
        """Create a new project within the desktop

        Parameters
        ----------
        proj_name :
            name of the new project

        Returns
        -------

        """
        self._messenger.add_info_message("Creating new Project ")
        prj = self._desktop.NewProject(proj_name)
        prj_name = prj.GetName()
        self.oproject = prj_name
        self.odesign = None
        return True

    @aedt_exception_handler
    def close_project(self, name=None, saveproject=True):
        """Close the specified project and release the Desktop

        Parameters
        ----------
        name :
            name of the project (if none take active provect) (Default value = None)
        saveproject : bool
            Save Project before close (Default value = True)

        Returns
        -------

        """
        msg_txt = ""
        if name:
            assert name in self.project_list, "Invalid project name {}".format(name)
            msg_txt = "specified "+ name
        else:
            name = self.project_name
            msg_txt = "active "+ self.project_name
        self._messenger.add_info_message("Closing the {} AEDT Project".format(msg_txt))
        if name != self.project_name:
            oproj = self.odesktop.SetActiveProject(name)
        else:
            oproj = self.oproject
        if saveproject:
            oproj.Save()

        lock_file = str(self.lock_file)
        self.odesktop.CloseProject(name)
        if name == self.project_name:
            assert not os.path.exists(lock_file), 'AEDT project did not close properly'
        return True

    @aedt_exception_handler
    def delete_design(self, name):
        """Delete name Design from the current project (will not work from toolkit)

        Parameters
        ----------
        name :
            

        Returns
        -------
        bool
            succeed status

        """

        self.oproject.DeleteDesign(name)
        return True


    @aedt_exception_handler
    def delete_separator(self, separator_name):
        """Deletes a separator from either the active project or design

        Parameters
        ----------
        separator_name :
            

        Returns
        -------
        bool
            True if the separator exists and can be deleted, False otherwise

        """
        obj = [(self._odesign, "Local"),
               (self.oproject, "Project")]

        for object in obj:
            desktop_object = object[0]
            var_type = object[1]
            try:
                desktop_object.ChangeProperty(["NAME:AllTabs",
                                               ["NAME:{0}VariableTab".format(var_type),
                                                ["NAME:PropServers",
                                                 "{0}Variables".format(var_type)],
                                                ["NAME:DeletedProps",
                                                 separator_name]]])
                return True
            except:
                pass
        return False

    @aedt_exception_handler
    def delete_variable(self, sVarName):
        """Delete a Variable

        Parameters
        ----------
        sVarName :
            name of variable to delete

        Returns
        -------
        type
            none

        """
        if sVarName[0] == "$":
            var_type = "Project"
            desktop_object = self.oproject
        else:
            var_type = "Local"
            desktop_object = self._odesign

        var_list = desktop_object.GetVariables()
        lower_case_vars = [var_name.lower() for var_name in var_list]

        if sVarName.lower() in lower_case_vars:
            desktop_object.ChangeProperty(["NAME:AllTabs",
                                           ["NAME:{0}VariableTab".format(var_type),
                                            ["NAME:PropServers",
                                             "{0}Variables".format(var_type)],
                                            ["NAME:DeletedProps",
                                             sVarName]]])
            return True
        return False

    @aedt_exception_handler
    def insert_design(self, design_type, design_name=None, solution_type=None):
        """Inserts a design of the specified design type. Default design type is taked from the derived application \
        class. If no design-name is given, the default design name is <Design-Type>Design<_index>. If the given or \
        default design name is in use, then an underscore + index is added            to ensure that the design name\
        is unique. The inserted object is assigned to self._odesign

        Parameters
        ----------
        design_type :
            Type of design to insert (eg. HFSS)
        design_name :
            optional design name (Default value = None)
        solution_type :
            optional solution_type. it can be a SolutionType object (Default value = None)

        Returns
        -------

        """
        assert design_type in design_solutions, "Invalid design type for insert: {}".format(design_type)
        # self.save_project() ## Commented because it saves a Projectxxx.aedt when launched on an empty Desktop
        unique_design_name = self._generate_unique_design_name(design_name)
        if solution_type:
            assert solution_type in design_solutions[self._design_type], \
                "Invalid solution type {0} for design type {1}".format(solution_type, self._design_type)
        else:
            solution_type = self.default_solution_type
        if design_type == "RMxprtSolution":
            new_design = self._oproject.InsertDesign("RMxprt", unique_design_name, "Inner-Rotor Induction Machine", "")
        elif design_type == "ModelCreation":
            new_design = self._oproject.InsertDesign("RMxprt", unique_design_name, "Model Creation Inner-Rotor Induction Machine", "")
        else:
            new_design = self._oproject.InsertDesign(design_type, unique_design_name, solution_type, "")
        self._messenger.add_info_message("Added design '{0}' of type {1}".format(unique_design_name, design_type),
                                         level='Project')
        name = new_design.GetName()
        if ";" in name:
            self.odesign = name.split(";")[1]
        else:
            self.odesign = name
        return name

    @aedt_exception_handler
    def _generate_unique_design_name(self, design_name):
        """

        Parameters
        ----------
        design_name :
            

        Returns
        -------

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
        """ """
        char_set = string.ascii_uppercase + string.digits
        uName = ''.join(random.sample(char_set, 3))
        proj_name = "Project_" + uName+ ".aedt"
        return proj_name

    @aedt_exception_handler
    def rename_design(self, new_name):
        """Rename the active Design

        Parameters
        ----------
        new_name :
            new name of the design

        Returns
        -------

        """
        self._odesign.RenameDesignInstance(self.design_name, new_name)
        self.odesign = new_name
        return True

    @aedt_exception_handler
    def copy_design_from(self, project_fullname, design_name):
        """Copy the design with name design_name from the project project_fullname  into the active design\
        If a design with the same name is already present in the destination project, the name is\
         automatically changed (this is done by AEDT). The name is returned by the function.\
        The active design is maintained.

        Parameters
        ----------
        project_fullname :
            copmlete full name (with path) of the project containing the design to be copied
        design_name :
            design name to be copied into the active design

        Returns
        -------
        type
            the copied design name or None if not copied (e.g. design_name does not exists in project_fullname)

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
        # return the pasted design name
        return new_designname

    @aedt_exception_handler
    def duplicate_design(self, label):
        """Copy the selected design with a new name consisting of the original design name, plus
            a defined extension MMode, plus a running index as necessary to allow for multiple calls

        Parameters
        ----------
        label :
            

        Returns
        -------

        """

        self.save_project()
        active_design = self.design_name
        self._oproject.CopyDesign(active_design)
        self._oproject.Paste()
        newname = label
        ind = 1
        while newname in self.design_list:
            newname = label + '_' + str(ind)
            ind += 1
        oDesign = self._oproject.GetActiveDesign()
        oDesign.RenameDesignInstance(oDesign.GetName(), newname)
        self.odesign = newname
        assert os.path.exists(self.working_directory)
        return True

    @aedt_exception_handler
    def export_variables_to_csv(self, filename, export_project=True, export_design=True):
        """Export Project and design variables variables to filename

        Parameters
        ----------
        filename :
            full path to csv file to export data
        export_design :
            True (Export Design Variables) | False (Default value = True)
        export_project :
            True (Export Project Variables) | False (Default value = True)

        Returns
        -------
        type
            True

        """
        """
            
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
        """Reads back the design data as a dictionary"""
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, 'r') as fps:
            design_data = json.load(fps)
        return design_data

    @aedt_exception_handler
    def save_project(self, project_file=None, overwrite=True, refresh_obj_ids_after_save=False):
        """Save the AEDT Project and add a message.

        Parameters
        ----------
        project_file : str, optional
            Full Project path. Default ``None``.
        overwrite : bool, optional
            Overwrite existing project.  Default ``True``.
        refresh_obj_ids_after_save : bool
            Refresh object IDs after save.  Default ``False``.

        Returns
        -------
        bool
            Always returns ``True``

        """
        msg_text = "Saving {0} Project".format(self.project_name)
        self._messenger.add_info_message(msg_text, level='Global')
        if project_file:
            self.oproject.SaveAs(project_file, overwrite)
        else:
            self.oproject.Save()
        if refresh_obj_ids_after_save:
            self.modeler.primitives.refresh_all_ids_from_aedt_file()
        return True

    @aedt_exception_handler
    def delete_project(self, project_name):
        """Delete the named project.

        Parameters
        ----------
        project_name : str
            Name of the project to delete

        Returns
        -------
        bool
            Always returns ``True``.

        """
        assert self.project_name != project_name, "Cannot delete active design"
        self._desktop.DeleteProject(project_name)
        return True

    @aedt_exception_handler
    def set_active_design(self, name):
        """Change active Design to another design

        Parameters
        ----------
        name :
            design name to make active

        Returns
        -------
        type
            nothing

        """
        self.oproject.SetActiveDesign(name)
        self.odesign = name
        return True

    @aedt_exception_handler
    def update_registry_from_file(self, filename):
        """Update HPC options from an af from an acf configuration file.

        Parameters
        ----------
        filename :
            full path to the filename (can be an acf or a txt)

        Returns
        -------
        type
            nothing

        """
        self._desktop.SetRegistryFromFile(r'%s' % os.path.abspath(filename))
        return True

    @aedt_exception_handler
    def validate_simple(self, logfile=None):
        """Validate Design. Return 0 if validation failed or 1 if passed

        Parameters
        ----------
        logfile :
            Optional, save validation to logfile (Default value = None)

        Returns
        -------

        """
        if logfile:
            return self._odesign.ValidateDesign(logfile)
        else:
            return self._odesign.ValidateDesign()


    @aedt_exception_handler
    def get_evaluated_value(self, variable_name, variation=None):
        """
        Returns the floating-point evaluated value of a given variable
        (design property or project variable) in SI-units

        Optionally a variation string of the form

        Parameters
        ----------
        variable_name : str, default=None
        Name of the project- or design variable to be evaluated
        variation : str, default=None
        Variation string for the evaluation. If not specified then use the nominal variation

        >>> M3D = Maxwell3D()
        >>> M3D["p1"] = "10mm"
        >>> M3D["p2"] = "20mm"
        >>> M3D["p3"] = "P1 * p2"
        >>> eval_p3 = M3D.get_evaluated_value("p3")

        Returns
        -------
        float

        """
        if not variation:
            variation_string = self._odesign.GetNominalVariation()
        else:
            variation_string = self.design_variation(variation_string=variation)

        si_value = self._odesign.GetVariationVariableValue(variation_string, variable_name)

        return si_value

    @aedt_exception_handler
    def evaluate_expression(self, expression_string):
        """ Evaluate an arbitrary valid string expression and return the numerical value in SI units

        Parameters
        ----------
        expression_string : str
        A valid design property/project variable string, i.e "34mm*sqrt(2)", "$G1*p2/34"

        Returns
        -------
        float

        """
        # Set the value of an internal reserved design variable to the specified string
        if expression_string in self._variable_manager.variables:
            return self._variable_manager.variables[expression_string]
        else:
            try:
                self._variable_manager.set_variable("pyaedt_evaluator", expression=expression_string, prop_type="VariableProp",
                                                    readonly=True, hidden=True, description="Internal_Evaluator")
            except:
                raise("Invalid string expression {}".expression_string)

            # Extract the numeric value of the expression (in SI units!)
            return self._variable_manager.variables["pyaedt_evaluator"].value

    @aedt_exception_handler
    def design_variation(self, variation_string=None):
        """Generate a string to specify a desired variation

        Converts a user input string defining a desired solution variation, e.g. "p1=1mm p2=3mm" into a valid
        string taking into account all existing design properties and project variables including non-sweep
        dependent properties.

        This is actually needed because the standard GetVariationVariableValue does not work for obtaining
        values of dependent (non-sweep variables). Presumably using the new beta feature object-oriented
        scripting model this could be made redundant in future releases.

        Parameters
        ----------
        variation_string : str
        Variation string of the form "p1=1mm p2=3mm"

            Parameters
            ----------
            variation_string

            Returns
            -------

        """
        nominal = self._odesign.GetNominalVariation()
        if variation_string:
            # decompose the nominal variation into a dictionary of name[value]
            nominal_dict = _variation_string_to_dict(nominal)

            # decompose the desired variation into a dictionary of name[value]
            var_dict = _variation_string_to_dict(variation_string)

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
        """

        Parameters
        ----------
        des_name :
            

        Returns
        -------

        """
        if des_name in self.design_list:
            self._odesign = self._oproject.SetActiveDesign(des_name)
            dtype = self._odesign.GetDesignType()
            if dtype != "RMxprt":
                assert dtype == self._design_type, \
                    "Error: Specified design is not of type {}".format(self._design_type)
            else:
                assert ("RMxprtSolution" == self._design_type) or ("ModelCreation" == self._design_type), \
                    "Error: Specified design is not of type {}".format(self._design_type)
            return True
        else:
            return des_name

    @aedt_exception_handler
    def _check_solution_consistency(self):
        """ """
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
