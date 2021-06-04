"""
Setup Library Class
----------------


**Description**


This class contains all the functionalities to create and edit a setup. It is based on templates in order to allow to create and modify setup properties easily


================

"""
from __future__ import absolute_import

from collections import OrderedDict
import os.path

from ..generic.general_methods import aedt_exception_handler, generate_unique_name

from .SetupTemplates import SweepHFSS, SweepQ3D, SetupKeys
from ..application.DataHandlers import tuple2dict, dict2arg


class Setup(object):
    """This Class defines the functions to initialize, create and update a Setup in Electronic Desktop"""

    @property
    def parent(self):
        """ """
        return self._parent

    @parent.setter
    def parent(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        self._parent = value
        pass

    @property
    def omodule(self):
        """ """
        return self._parent.oanalysis

    def __repr__(self):
        return "SetupName " + self.name + " with " + str(len(self.sweeps)) + " Sweeps"

    def __init__(self, parent, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        """
        :param parent: AEDT Module for Analysis Setup
        :param setupname: Setup Name
        :param solutiontype: Setup Type of Application.SolutionType
        :param isnewsetup: Boolean. True if is a new setup to be created from template. False to access existing Setup
        """
        self._parent = None
        self.parent = parent
        self.setuptype = solutiontype
        self.name = setupname
        self.props = {}
        self.sweeps = []
        if isnewsetup:
            setup_template = SetupKeys.SetupTemplates[solutiontype]
            for t in setup_template:
                tuple2dict(t, self.props)
        else:
            try:
                setups_data = self.parent.design_properties["AnalysisSetup"]["SolveSetups"]
                if setupname in setups_data:
                    setup_data = setups_data[setupname]
                    if "Sweeps" in setup_data and self.setuptype not in [0,7]:   #0 and 7 represent setup HFSSDrivenAuto
                        if self.setuptype <= 4:
                            app = setup_data["Sweeps"]
                            app.pop('NextUniqueID', None)
                            app.pop('MoveBackForward', None)
                            app.pop('MoveBackwards', None)
                            for el in app:
                                if type(app[el]) is OrderedDict:
                                    self.sweeps.append(SweepHFSS(self.omodule, setupname, el, props=app[el]))

                        else:
                            app = setup_data["Sweeps"]
                            for el in app:
                                if type(app[el]) is OrderedDict:
                                    self.sweeps.append(SweepQ3D(self.omodule, setupname, el, props=app[el]))
                        setup_data.pop('Sweeps', None)
                    self.props = OrderedDict(setup_data)
            except:
                self.props = OrderedDict()


    @aedt_exception_handler
    def check_dict(self, listin, name, out):
        """

        Parameters
        ----------
        listin :
            
        name :
            
        out :
            

        Returns
        -------

        """
        arg = ["Name:" + name.replace("__", " ")]
        for a in listin:
            if type(a) is tuple:
                if type(a[1]) is list and type(a[1][0]) is tuple:
                    arg = self.check_dict(a[1], a[0], arg)
                else:
                    arg.append(a[0].replace("__", " ") + ":=")
                    arg.append(a[1])
            else:
                arg.append(a)
        out.append(arg)
        return out

    @aedt_exception_handler
    def create(self):
        """Insert a new Setup based on Class settings into the AEDT Application
        
        :return: the argument list

        Parameters
        ----------

        Returns
        -------

        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.InsertSetup(soltype, arg)
        return arg

    @aedt_exception_handler
    def update(self, update_dictionary=None):
        """update the setup based on the class argument or to the updated dictionary passed as arcument

        Parameters
        ----------
        update_dictionary :
            optional dictionary of settings to apply (Default value = None)

        Returns
        -------
        type
            bool

        """
        if update_dictionary:
            for el in update_dictionary:
                self.props[el]=update_dictionary[el]
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def _expression_cache(self, expression_list, report_type_list,intrinsics_list, isconvergence_list,
                          isrelativeconvergence, conv_criteria):
        """

        Parameters
        ----------
        expression_list :
            
        report_type_list :
            
        intrinsics_list :
            
        isconvergence_list :
            
        isrelativeconvergence :
            
        conv_criteria :
            

        Returns
        -------

        """
        if isrelativeconvergence:
            userelative = 1
        else:
            userelative = 0

        list_data = ["NAME:ExpressionCache"]
        if type(expression_list) is list:
            i=0
            while i < len(expression_list):
                expression=expression_list[i]
                name = expression.replace("(", "_") + "1"
                name = name.replace(")", "_")
                name = name.replace(" ", "_")
                if type(report_type_list) is list:
                    report_type = report_type_list[i]
                else:
                    report_type = report_type_list
                if type(isconvergence_list) is list:
                    isconvergence = isconvergence_list[i]
                else:
                    isconvergence = isconvergence_list
                if type(intrinsics_list) is list:
                    intrinsics = intrinsics_list[i]
                else:
                    intrinsics = intrinsics_list
                list_data.append([
                    "NAME:CacheItem",
                    "Title:=", name,
                    "Expression:=", expression,
                    "Intrinsics:=", intrinsics,
                    "IsConvergence:=", isconvergence,
                    "UseRelativeConvergence:=", 1,
                    "MaxConvergenceDelta:=", 1,
                    "MaxConvergeValue:=", "0.01",
                    "ReportType:=", report_type,
                    [
                        "NAME:ExpressionContext"
                    ]
                ])
                i+=1

        else:
            name = expression_list.replace("(", "") + "1"
            name = name.replace(")", "")
            name = name.replace(" ", "")
            name = name.replace(",", "_")
            list_data.append([
                "NAME:CacheItem",
                "Title:=", name,
                "Expression:=", expression_list,
                "Intrinsics:=", intrinsics_list,
                "IsConvergence:=", isconvergence_list,
                "UseRelativeConvergence:=", userelative,
                "MaxConvergenceDelta:=", conv_criteria,
                "MaxConvergeValue:=", str(conv_criteria),
                "ReportType:=", report_type_list,
                [
                    "NAME:ExpressionContext"
                ]
            ])

        return list_data

    @aedt_exception_handler
    def enable_expression_cache(self, expressions, report_type="Fields", intrinsics='', isconvergence=True,
                                isrelativeconvergence=True, conv_criteria=1):
        """Enable Setup Expression Cache

        Parameters
        ----------
        conv_criteria :
            param isrelativeconvergence: (Default value = 1)
        expressions :
            Formula to be added to the expression cache. It can be a list or a string
        report_type :
            Report type of expression cache (eg. Fields). It can be a list or a string (same length of expression_list) (Default value = "Fields")
        isconvergence :
            Boolean if expression is in convergence criteria. It can be a list or a string (same length of expression_list) (Default value = True)
        intrinsics :
            List of Intrinsics of expression (if any). It can be a list or a string (same length of expression_list) (Default value = '')
        isrelativeconvergence :
             (Default value = True)

        Returns
        -------
        type
            none

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        expression_cache = self._expression_cache(expressions, report_type, intrinsics, isconvergence,
                                                  isrelativeconvergence, conv_criteria)
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def add_derivatives(self, derivative_list):
        """Add Derivatives to setup

        Parameters
        ----------
        derivative_list :
            derivative list

        Returns
        -------
        type
            Bool

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        arg.append("VariablesForDerivatives:=")
        arg.append(derivative_list)
        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def enable(self, setup_name=None):
        """Enable specific Setup

        Parameters
        ----------
        setup_name :
            optional setup name (Default value = None)

        Returns
        -------
        type
            none

        """
        if not setup_name:
            self.omodule.EditSetup(self.name,
                                   [
                                       "NAME:" + self.name,
                                       "IsEnabled:="		, True])
        else:
            self.omodule.EditSetup(setup_name,
                                   [
                                       "NAME:" + setup_name,
                                       "IsEnabled:="		, True])
        return True

    @aedt_exception_handler
    def disable(self, setup_name=None):
        """Disable specific Setup

        Parameters
        ----------
        setup_name :
            optional setup name (Default value = None)

        Returns
        -------
        type
            none

        """
        if not setup_name:
            self.omodule.EditSetup(self.name,
                                   [
                                       "NAME:" + self.name,
                                       "IsEnabled:="		, False])

        else:
            self.omodule.EditSetup(setup_name,
                                   [
                                       "NAME:" + setup_name,
                                       "IsEnabled:="		, False])
        return True

    @aedt_exception_handler
    def add_sweep(self, sweepname=None, sweeptype= "Interpolating"):
        """Add a Sweep to the Project

        Parameters
        ----------
        sweepname :
            str Sweep Name (Default value = None)
        sweeptype :
            sweep type (Default value = "Interpolating")

        Returns
        -------
        type
            sweep object

        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        if self.setuptype <= 4:
            sweep_n = SweepHFSS(self.omodule, self.name, sweepname, sweeptype)
        else:
            sweep_n = SweepQ3D(self.omodule, self.name, sweepname, sweeptype)
        sweep_n.create()
        self.sweeps.append(sweep_n)
        return sweep_n

    @aedt_exception_handler
    def add_mesh_link(self, design_name, solution_name, parameters_dict, project_name="This Project*"):
        """Add Mesh Link to another design. Design can be in the same project (default) or external project

        Parameters
        ----------
        project_name :
            name of project "This Project*" by default
        design_name :
            str name of the design
        solution_name :
            str, name of solution in the format "setupname : solutionname". Optionally use appname.nominal_adaptive to get nominal adaptive or appname.nominal_sweep
        parameters_dict :
            dictionary of parameters. Optionally use appname.available_variations.nominal_w_values_dict property to get nominal values

        Returns
        -------
        type
            Bool

        """
        meshlinks = self.props["MeshLink"]
        meshlinks["ImportMesh"] = True
        meshlinks["Project"] = project_name
        meshlinks["Product"] = "ElectronicsDesktop"
        meshlinks["Design"] = design_name
        meshlinks["Soln"] = solution_name
        meshlinks["Params"] = OrderedDict({})
        for el in parameters_dict:
            if el in list(self._parent.available_variations.nominal_w_values_dict.keys()):
                meshlinks["Params"][el] = el
            else:
                meshlinks["Params"][el] = parameters_dict[el]
        meshlinks["ForceSourceToSolve"] = True
        meshlinks["PreservePartnerSoln"] = True
        meshlinks["PathRelativeTo"] = "TargetProject"
        meshlinks["ApplyMeshOp"] = True
        self.update()
        return True

class SetupCircuit(object):
    """This Class defines the functions to initialize, create and update a Setup in Electronic Desktop

    Parameters
    ----------
    design :
        AEDT oDesign module
    setupmodule :
        AEDT Module for Analysis Setup
    setupname :
        Setup Name
    solutiontype :
        Setup Type of Application.SolutionType
    isnewsetup :
        Boolean. True if is a new setup to be created from template. False to access existing Setup

    Returns
    -------

    """
    @property
    def name(self):
        """ """
        return self._Name

    @name.setter
    def name(self, name):
        """

        Parameters
        ----------
        name :
            

        Returns
        -------

        """
        self._Name = name
        self.props["Name"] = name

    @property
    def parent(self):
        """ """
        return self._parent

    @parent.setter
    def parent(self, name):
        """

        Parameters
        ----------
        name :
            

        Returns
        -------

        """
        self._parent = name

    @property
    def odesign(self):
        """ """
        return self._parent.odesign

    @property
    def omodule(self):
        """ """
        return self._parent.oanalysis

    def __init__(self, parent,  solutiontype, setupname="MySetupAuto", isnewsetup=True):
        self._parent = None
        self.parent = parent
        self.setuptype = solutiontype
        self._Name = "LinearFrequency"
        self.props = {}
        if isnewsetup:
            setup_template = SetupKeys.SetupTemplates[solutiontype]
            for t in setup_template:
                tuple2dict(t, self.props)
        else:
            try:
                setups_data = self.parent.design_properties["SimSetups"]["SimSetup"]
                if type(setups_data) is not list:
                    setups_data=[setups_data]
                for setup in setups_data:
                    if setupname == setup["Name"]:
                        setup_data = setup
                        setup_data.pop('Sweeps', None)
                        self.props = setup_data
            except:
                self.props = {}
        self.name = setupname

    @aedt_exception_handler
    def check_dict(self, listin, name, out):
        """

        Parameters
        ----------
        listin :
            
        name :
            
        out :
            

        Returns
        -------

        """
        arg = ["Name:" + name.replace("__", " ")]
        for a in listin:
            if type(a) is tuple:
                if type(a[1]) is list and type(a[1][0]) is tuple:
                    arg = self.check_dict(a[1], a[0], arg)
                else:
                    arg.append(a[0].replace("__", " ") + ":=")
                    arg.append(a[1])
            else:
                arg =name.replace("__", " ")+ ":="
                out.append(arg)
                arg = None
                out.append(listin)
                break
        if arg:
            out.append(arg)
        return out

    @aedt_exception_handler
    def create(self):
        """Insert a new Setup based on Class settings into the AEDT Application
        
        :return: the argument list

        Parameters
        ----------

        Returns
        -------

        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:SimSetup"]
        dict2arg(self.props, arg)
        self._setup(soltype, arg)
        return arg

    @aedt_exception_handler
    def _setup(self, soltype, arg, newsetup=True):
        """

        Parameters
        ----------
        soltype :
            
        arg :
            
        newsetup :
             (Default value = True)

        Returns
        -------

        """
        if newsetup:
            if soltype == "NexximLNA":
                self.omodule.AddLinearNetworkAnalysis(arg)
            elif soltype == "NexximDC":
                self.omodule.AddDCAnalysis(arg)
            elif soltype == "NexximTransient":
                self.omodule.AddTransient(arg)
            else:
                print("Not Implemented Yet")
        else:
            if soltype == "NexximLNA":
                self.omodule.EditLinearNetworkAnalysis(self.name, arg)
            elif soltype == "NexximDC":
                self.omodule.EditDCAnalysis(self.name, arg)
            elif soltype == "NexximTransient":
                self.omodule.EditTransient(self.name, arg)
            else:
                print("Not Implemented Yet")
        return True

    @aedt_exception_handler
    def update(self, update_dictionary=None):
        """update the setup based on the class argument or to the updated dictionary passed as arcument

        Parameters
        ----------
        update_dictionary :
            optional dictionary of settings to apply (Default value = None)

        Returns
        -------
        type
            bool

        """
        if update_dictionary:
            for el in update_dictionary:
                self.props[el]=update_dictionary[el]
        arg = ["NAME:SimSetup"]
        soltype = SetupKeys.SetupNames[self.setuptype]
        dict2arg(self.props, arg)
        self._setup(soltype, arg, False)
        return True

    @aedt_exception_handler
    def _expression_cache(self, expression_list, report_type_list, intrinsics_list, isconvergence_list,
                          isrelativeconvergence, conv_criteria):
        """

        Parameters
        ----------
        expression_list :
            
        report_type_list :
            
        intrinsics_list :
            
        isconvergence_list :
            
        isrelativeconvergence :
            
        conv_criteria :
            

        Returns
        -------

        """

        if isrelativeconvergence:
            userelative = 1
        else:
            userelative = 0

        list_data = ["NAME:ExpressionCache"]
        if type(expression_list) is list:
            i=0
            while i < len(expression_list):
                expression=expression_list[i]
                name = expression.replace("(", "_") + "1"
                name = name.replace(")", "_")
                name = name.replace(" ", "_")
                if type(report_type_list) is list:
                    report_type = report_type_list[i]
                else:
                    report_type = report_type_list
                if type(isconvergence_list) is list:
                    isconvergence = isconvergence_list[i]
                else:
                    isconvergence = isconvergence_list
                if type(intrinsics_list) is list:
                    intrinsics = intrinsics_list[i]
                else:
                    intrinsics = intrinsics_list
                list_data.append([
                    "NAME:CacheItem",
                    "Title:=", name,
                    "Expression:=", expression,
                    "Intrinsics:=", intrinsics,
                    "IsConvergence:=", isconvergence,
                    "UseRelativeConvergence:=", 1,
                    "MaxConvergenceDelta:=", 1,
                    "MaxConvergeValue:=", "0.01",
                    "ReportType:=", report_type,
                    [
                        "NAME:ExpressionContext"
                    ]
                ])
                i+=1

        else:
            name = expression_list.replace("(", "") + "1"
            name = name.replace(")", "")
            name = name.replace(" ", "")
            name = name.replace(",", "_")
            list_data.append([
                "NAME:CacheItem",
                "Title:=", name,
                "Expression:=", expression_list,
                "Intrinsics:=", intrinsics_list,
                "IsConvergence:=", isconvergence_list,
                "UseRelativeConvergence:=", userelative,
                "MaxConvergenceDelta:=", conv_criteria,
                "MaxConvergeValue:=", str(conv_criteria),
                "ReportType:=", report_type_list,
                [
                    "NAME:ExpressionContext"
                ]
            ])

        return list_data

    @aedt_exception_handler
    def enable_expression_cache(self, expressions, report_type="Fields", intrinsics='', isconvergence=True,
                                isrelativeconvergence=True, conv_criteria=1):
        """

        Parameters
        ----------
        conv_criteria :
            param isrelativeconvergence: (Default value = 1)
        expressions :
            Formula to be added to the expression cache. It can be a list or a string
        report_type :
            Report type of expression cache (eg. Fields). It can be a list or a string (same length of expression_list) (Default value = "Fields")
        isconvergence :
            Boolean if expression is in convergence criteria. It can be a list or a string (same length of expression_list) (Default value = True)
        intrinsics :
            List of Intrinsics of expression (if any). It can be a list or a string (same length of expression_list) (Default value = '')
        isrelativeconvergence :
             (Default value = True)

        Returns
        -------
        type
            none

        """
        arg = ["Name:SimSetup"]
        dict2arg(self.props, arg)
        expression_cache = self._expression_cache(expressions, report_type, intrinsics, isconvergence,
                                                  isrelativeconvergence, conv_criteria)
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def add_derivatives(self, derivative_list):
        """Add Derivatives to Setup

        Parameters
        ----------
        derivative_list :
            derivative lists

        Returns
        -------
        type
            Bool

        """
        arg = ["Name:SimSetup"]
        dict2arg(self.props, arg)
        arg.append("VariablesForDerivatives:=")
        arg.append(derivative_list)
        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def enable(self, setup_name=None):
        """Enable specific Setup

        Parameters
        ----------
        setup_name :
            optional setup name (Default value = None)

        Returns
        -------
        type
            none

        """
        if not setup_name:
            self.odesign.EnableSolutionSetup(self.name, True)
        else:
            self.odesign.EnableSolutionSetup(setup_name, True)
        return True

    @aedt_exception_handler
    def disable(self, setup_name=None):
        """Disable specific Setup

        Parameters
        ----------
        setup_name :
            optional setup name (Default value = None)

        Returns
        -------
        type
            none

        """
        if not setup_name:
            self.odesign.EnableSolutionSetup(self.name, False)
        else:
            self.odesign.EnableSolutionSetup(setup_name, False)
        return True


class Setup3DLayout(object):
    """This Class defines the functions to initialize, create and update a Setup in Electronic Desktop

    Parameters
    ----------
    setupmodule :
        AEDT Module for Analysis Setup
    setupname :
        Setup Name
    solutiontype :
        Setup Type of Application.SolutionType
    isnewsetup :
        Boolean. True if is a new setup to be created from template. False to access existing Setup

    Returns
    -------

    """

    @property
    def omodule(self):
        """ """
        return self.parent.oanalysis

    def __init__(self, parent, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        self.parent = parent
        self._solutiontype = solutiontype
        self.name = setupname
        self.props = OrderedDict()
        self.sweeps = []
        if isnewsetup:
            setup_template = SetupKeys.SetupTemplates[self._solutiontype]
            for t in setup_template:
                tuple2dict(t, self.props)
        else:
            try:
                setups_data = self.parent.design_properties["Setup"]["Data"]
                if setupname in setups_data:
                    setup_data = setups_data[setupname]
                    if "Data" in setup_data:   #0 and 7 represent setup HFSSDrivenAuto
                        app = setup_data["Data"]
                        for el in app:
                            if type(app[el]) is OrderedDict:
                                self.sweeps.append(SweepHFSS(self.omodule, setupname, el, props=app[el]))

                    self.props = OrderedDict(setup_data)
            except:
                self.props = OrderedDict()
            #
            # setup_data = self.omodule.GetSetupData(setupname)
            # dict_data = OrderedDict()
            # _arg2dict(setup_data, dict_data)
            # self.props = dict_data[setupname]

    @property
    def setup_type(self):
        """:return: setup type"""
        if 'SolveSetupType' in self.props:
            return self.props['SolveSetupType']
        else:
            return None

    @aedt_exception_handler
    def create(self):
        """Insert a new Setup based on Class settings into the AEDT Application
        
        :return: the argument list

        Parameters
        ----------

        Returns
        -------

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.Add(arg)
        return True

    @aedt_exception_handler
    def update(self):
        """update the setup based on the class argument or to the updated dictionary passed as arcument

        Parameters
        ----------
        update_dictionary :
            optional dictionary of settings to apply

        Returns
        -------
        type
            Bool

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.Edit(self.name, arg)
        return True

    @aedt_exception_handler
    def enable(self):
        """Enable specific Setup

        Parameters
        ----------
        setup_name :
            optional setup name

        Returns
        -------
        type
            Bool

        """
        self.props['Properties']['Enable'] = "true"
        self.update()
        return True

    @aedt_exception_handler
    def disable(self):
        """Disable specific Setup

        Parameters
        ----------
        setup_name :
            optional setup name

        Returns
        -------
        type
            Bool

        """
        self.props['Properties']['Enable'] = "false"
        self.update()
        return True

    @aedt_exception_handler
    def export_to_hfss(self, file_fullname):
        """Export Project to

        Parameters
        ----------
        file_fullname :
            fullname of desgintation

        Returns
        -------
        type
            Bool

        """

        file_fullname = os.path.normpath(file_fullname)
        if not os.path.isdir(os.path.dirname(file_fullname)):
            return False
        file_fullname = os.path.splitext(file_fullname)[0] + '.aedt'
        self.omodule.ExportToHfss(self.name, file_fullname)
        return True


    @aedt_exception_handler
    def add_sweep(self, sweepname=None, sweeptype="Interpolating"):
        """Add Frequency Sweep

        Parameters
        ----------
        sweepname :
            str sweep name (Default value = None)
        sweeptype :
            str sweep type (Default value = "Interpolating")

        Returns
        -------
        type
            sweep object

        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        sweep_n = SweepHFSS(self.omodule, self.name, sweepname, sweeptype)
        self.sweeps.append(sweep_n)
        return sweep_n