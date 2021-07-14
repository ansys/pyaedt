"""
This module contains these classes: `Setup`, `Setup3DLayout`, and `SetupCircuit`.

This module provides all functionalities for creating and editing setups in AEDT.
It is based on templates to allow for easy creation and modification of setup properties.

"""
from __future__ import absolute_import

from collections import OrderedDict
import os.path

from ..generic.general_methods import aedt_exception_handler, generate_unique_name

from .SetupTemplates import SweepHFSS, SweepQ3D, SetupKeys, SweepHFSS3DLayout
from ..application.DataHandlers import tuple2dict, dict2arg


class Setup(object):
    """Setup class.
    
    This class provides the functionalities needed to initialize, create, and update a 3D setup.
    
    Parameters
    ----------
    parent: str
        AEDT module for analysis setup.
    solutiontype: 
        Type of the setup.
    setupname: str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup: bool, optional
        Whether to create the new setup from a template. The default is ``True.``
        If ``False``, access is to the existing setup.
     
    """

    @property
    def parent(self):
        """Parent."""
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def omodule(self):
        """Analysis module."""
        return self._parent.oanalysis

    def __repr__(self):
        return "SetupName " + self.name + " with " + str(len(self.sweeps)) + " Sweeps"

    def __init__(self, parent, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        
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
    def create(self):
        """Add a new setup based on class settings in AEDT.
              
        Returns
        -------
        dict
            Dictionary of arguments.

        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.InsertSetup(soltype, arg)
        return arg

    @aedt_exception_handler
    def update(self, update_dictionary=None):
        """Update the setup based on either the class argument or a dictionary.

        Parameters
        ----------
        update_dictionary : optional
            Dictionary to use to update the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if update_dictionary:
            for el in update_dictionary:
                self.props[el]=update_dictionary[el]
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def _expression_cache(self, expression_list, report_type_list, intrinsics_list, isconvergence_list,
                          isrelativeconvergence, conv_criteria):
        """Retrieve data from the expression setup cache.

        Parameters
        ----------
        expressions_list : list
            List of formulas to retrieve. 
        report_type_list : list
            List of report types for the expressions. 
        intrinsics_list : list
            List of intrinsic expressions for the expressions. 
        isconvergence_list : list
            List of Boolean values indicating whether the expressions are in 
            the convergence criteria.
        isrelativeconvergence : bool
            
        conv_criteria:
        
        Returns
        -------
        list
            List of the data.

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
        """Enable a setup expression cache.

        Parameters
        ----------
        expressions : str or list
            One or more formulas to add to the expression cache. 
        report_type : str or list, optional
            Type of the report for the expression. The default is ``Fields``. If a list of expressions
            is supplied, supply a corresponding list of report types.
        intrinsics : str or list, optional
            Intrinsic functions for the expressions. The default is ``""``. If a list of expressions
            is supplied, a corresponding list of intrinsic functions must be supplied.
        isconvergence, bool, str, or list, optional
            Whether the expression is in the convergence criteria. The default is ``True``.
            If a list of expressions is supplied, a corresponding list of Boolean values must be
            supplied.
        isrelativeconvergence : bool, optional
            The default is ``True``.
                
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Add derivatives to the setup.

        Parameters
        ----------
        derivative_list : list
            List of derivatives.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        arg.append("VariablesForDerivatives:=")
        arg.append(derivative_list)
        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def enable(self, setup_name=None):
        """Enable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        if not setup_name:
            setup_name = self.name

        self.omodule.EditSetup(
            setup_name,
            [
                "NAME:" + setup_name,
                "IsEnabled:=", True
            ]
        )
        return True

    @aedt_exception_handler
    def disable(self, setup_name=None):
        """Disable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        if not setup_name:
            setup_name = self.name

        self.omodule.EditSetup(
            setup_name,
            [
                "NAME:" + setup_name,
                "IsEnabled:", False
            ]
        )
        return True

    @aedt_exception_handler
    def add_sweep(self, sweepname=None, sweeptype= "Interpolating"):
        """Add a sweep to the project.

        Parameters
        ----------
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. The default is ``"Interpolating"``.

        Returns
        -------
        type
            Sweep object.

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
        """Add a mesh link to another design. 

        Parameters
        ----------
        design_name : str, 
            Name of the design.
        solution_name : str
            Name of the solution in the format ``"setupname : solutionname"``.
            Optionally use ``appname.nominal_adaptive`` to get the
            nominal adaptive or ``appname.nominal_sweep`` to get the
            nominal sweep.
        parameters_dict : dict
            Dictionary of the parameters. Optionally use the
            ``appname.available_variations.nominal_w_values_dict``
            property to get the nominal values.
        project_name : str, optional
            Name of the project with the design. The default is ``"This Project"``. 
            However, you can supply the full path and name to another project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
    """SetupCircuit class.
    
    This class provides the functionalities needed to initialize, create, and update a circuit setup.
    
    Parameters
    ----------
    parent: str
        AEDT module for analysis setup.
    solutiontype: 
        Type of the setup.
    setupname: str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup: bool, optional
      Whether to create the new setup from a template. The default is ``True.``
      If ``False``, access is to the existing setup.     

    """
    @property
    def name(self):
        """Name."""
        return self._Name

    @name.setter
    def name(self, name):
        self._Name = name
        self.props["Name"] = name

    @property
    def parent(self):
        """Parent."""
        return self._parent

    @parent.setter
    def parent(self, name):
        self._parent = name

    @property
    def odesign(self):
        """Design."""
        return self._parent.odesign

    @property
    def omodule(self):
        """Analysis module.

        Parameters
        ----------
        parent: str
            AEDT module for analysis setup.
        solutiontype:
            Type of the setup.
        setupname: str, optional
            Name of the setup. The default is ``"MySetupAuto"``.
        isnewsetup: bool, optional
          Whether to create the new setup from a template. The default is ``True.``
          If ``False``, access is to the existing setup.

        Returns
        -------
        str
            Name of the setup.

        """
        return self._parent.oanalysis

    def __init__(self, parent, solutiontype, setupname="MySetupAuto", isnewsetup=True):
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
    def create(self):
        """Add a new setup based on class settings in AEDT.
        
        Returns
        -------
        dict
            Dictionary of the arguments.

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
        soltype : str
            Type of the solution.
            
        arg :
            
        newsetup : bool, optional
            Whether this is a new setup. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary of settings to apply. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Retrieve data from the expression setup cache.

        Parameters
        ----------
        expressions_list : list
            List of formulas to retrieve. 
        report_type_list : list
            List of report types for the expressions. 
        intrinsics_list : list
            List of intrinsic functions for the expressions.
        isconvergence_list : list
            List of Boolean values indicating whether the expressions are in 
            the convergence criteria.
        isrelativeconvergence : 
            
        conv_criteria:
        
        Returns
        -------
        list
            List of the data.
        
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
        """Enable a setup expression cache.

        Parameters
        ----------
        expressions : str or list
            One or more formulas to add to the expression cache. 
        report_type : str or list, optional
            Type of the report for the expression. The default is ``"Fields"``. If a list of expressions
            is supplied, a corresponding list of report types must be supplied.
        intrinsics : str or list, optional
            Intrinsic functions for the expressions. The default is ``""``. If a list of expressions
            is supplied, a corresponding list of intrinsic expressesions must be supplied.
        isconvergence : bool, str, or list, optional
            Whether the expression is in the convergence criteria. The  default is ``True``.  
            If a list of expressions is supplied, a corresponding list of Boolean values must be
            supplied.
        isrelativeconvergence : bool, optional
            The default is ``True``.
        conv_criteria
            The default is ``1``.
                
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Add derivatives to the setup.

        Parameters
        ----------
        derivative_list : list
            List of derivatives.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["Name:SimSetup"]
        dict2arg(self.props, arg)
        arg.append("VariablesForDerivatives:=")
        arg.append(derivative_list)
        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def enable(self, setup_name=None):
        """Enable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        if not setup_name:
            setup_name = self.name
        self.odesign.EnableSolutionSetup(setup_name, True)
        return True

    @aedt_exception_handler
    def disable(self, setup_name=None):
        """Disable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        if not setup_name:
            setup_name = self.name
        self.odesign.EnableSolutionSetup(setup_name, False)
        return True


class Setup3DLayout(object):
    """Setup3DLayout class.
    
    This class provides the functionalities needed to initialize, create, and update a 3D Layout setup.
    
    Parameters
    ----------
    parent: str
        AEDT module for analysis setup.
    solutiontype: 
        Type of the setup.
    setupname: str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup: bool, optional
        Whether to create the new setup from a template. The default is ``True.``
        If ``False``, access is to the existing setup.
    
    """

    @property
    def omodule(self):
        """Analysis module.

        Parameters
        ----------
        parent: str
           AEDT module for analysis setup.
        solutiontype:
            Type of the setup.
        setupname: str, optional
            Name of the setup. The default is ``"MySetupAuto"``.
        isnewsetup: bool, optional
            Whether to create the new setup from a template. The default is ``True.``
            If ``False``, access is to the existing setup.

        Returns
        -------
        type
            Analysis module.

        """
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
                                self.sweeps.append(SweepHFSS3DLayout(self.omodule, setupname, el, props=app[el]))

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
        """Setup type.
        
        Returns
        -------
        type
            Setup type.
        """
        
        if 'SolveSetupType' in self.props:
            return self.props['SolveSetupType']
        else:
            return None

    @aedt_exception_handler
    def create(self):
        """Add a new setup based on class settings in AEDT.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.Add(arg)
        return True

    @aedt_exception_handler
    def update(self):
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary of settings to apply.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.Edit(self.name, arg)
        return True

    @aedt_exception_handler
    def enable(self):
        """Enable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.props['Properties']['Enable'] = "true"
        self.update()
        return True

    @aedt_exception_handler
    def disable(self):
        """Disable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.props['Properties']['Enable'] = "false"
        self.update()
        return True

    @aedt_exception_handler
    def export_to_hfss(self, file_fullname):
        """Export the project to a file.

        Parameters
        ----------
        file_fullname : str
            Full path and name to export the project to.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        file_fullname = os.path.normpath(file_fullname)
        if not os.path.isdir(os.path.dirname(file_fullname)):
            return False
        file_fullname = os.path.splitext(file_fullname)[0] + '.aedt'
        self.omodule.ExportToHfss(self.name, file_fullname)
        return True


    @aedt_exception_handler
    def add_sweep(self, sweepname=None, sweeptype="Interpolating"):
        """Add a frequency sweep.

        Parameters
        ----------
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. The default is ``"Interpolating"``.

        Returns
        -------
        SweeHFSS3DLayout
            Sweep object.

        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        sweep_n = SweepHFSS3DLayout(self.omodule, self.name, sweepname, sweeptype)
        if sweep_n.create():
            self.sweeps.append(sweep_n)
            return sweep_n
        return False
