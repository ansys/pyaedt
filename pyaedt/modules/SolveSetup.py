"""
This module contains these classes: `Setup`, `Setup3DLayout`, and `SetupCircuit`.

This module provides all functionalities for creating and editing setups in AEDT.
It is based on templates to allow for easy creation and modification of setup properties.

"""
from __future__ import absolute_import  # noreorder

import logging
import os.path
import time
import warnings
from collections import OrderedDict
from random import randrange

from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.general_methods import PropsManager
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.SetupTemplates import SetupKeys
from pyaedt.modules.SolveSweeps import SetupProps
from pyaedt.modules.SolveSweeps import SweepHFSS
from pyaedt.modules.SolveSweeps import SweepHFSS3DLayout
from pyaedt.modules.SolveSweeps import SweepMatrix
from pyaedt.modules.SolveSweeps import identify_setup


class CommonSetup(PropsManager, object):
    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        self.auto_update = False
        self._app = None
        self.p_app = app
        if solutiontype is None:
            self.setuptype = self.p_app.design_solutions.default_setup
        elif isinstance(solutiontype, int):
            self.setuptype = solutiontype
        elif solutiontype in SetupKeys.SetupNames:
            self.setuptype = SetupKeys.SetupNames.index(solutiontype)
        else:
            self.setuptype = self.p_app.design_solutions._solution_options[solutiontype]["default_setup"]
        self._setupname = setupname
        self.props = {}
        self.sweeps = []
        self._init_props(isnewsetup)
        self.auto_update = True

    @property
    def default_intrinsics(self):
        """Retrieve default intrinsic for actual setup.

        Returns
        -------
        dict
            Dictionary which keys are typically Freq, Phase or Time."""
        intr = {}
        for i in self._app.design_solutions.intrinsics:
            if i == "Freq" and "Frequency" in self.props:
                intr[i] = self.props["Frequency"]
            elif i == "Phase":
                intr[i] = "0deg"
            elif i == "Time":
                intr[i] = "0s"
        return intr

    def __repr__(self):
        return "SetupName " + self.name + " with " + str(len(self.sweeps)) + " Sweeps"

    @pyaedt_function_handler()
    def analyze(
        self,
        num_cores=None,
        num_tasks=None,
        num_gpu=None,
        acf_file=None,
        use_auto_settings=True,
        solve_in_batch=False,
        machine="localhost",
        run_in_thread=False,
        revert_to_initial_mesh=False,
    ):
        """Solve the active design.

        Parameters
        ----------
        num_cores : int, optional
            Number of simulation cores.
        num_tasks : int, optional
            Number of simulation tasks.
        num_gpu : int, optional
            Number of simulation graphic processing units to use.
        acf_file : str, optional
            Full path to the custom ACF file.
        use_auto_settings : bool, optional
            Set ``True`` to use automatic settings for HPC. The option is only considered for setups
            that support automatic settings.
        solve_in_batch : bool, optional
            Whether to solve the project in batch or not.
            If ``True`` the project will be saved, closed, solved and repened.
        machine : str, optional
            Name of the machine if remote.  The default is ``"localhost"``.
        run_in_thread : bool, optional
            Whether to submit the batch command as a thread. The default is
            ``False``.
        revert_to_initial_mesh : bool, optional
            Whether to revert to initial mesh before solving or not. Default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.Analyze
        """
        self._app.analyze(
            setup_name=self.name,
            num_cores=num_cores,
            num_tasks=num_tasks,
            num_gpu=num_gpu,
            acf_file=acf_file,
            use_auto_settings=use_auto_settings,
            solve_in_batch=solve_in_batch,
            machine=machine,
            run_in_thread=run_in_thread,
            revert_to_initial_mesh=revert_to_initial_mesh,
        )

    @pyaedt_function_handler()
    def _init_props(self, isnewsetup=False):
        if isnewsetup:
            setup_template = SetupKeys.get_setup_templates()[self.setuptype]
            self.props = SetupProps(self, setup_template)
        else:
            try:
                setups_data = self.p_app.design_properties["AnalysisSetup"]["SolveSetups"]
                if self.name in setups_data:
                    setup_data = setups_data[self.name]
                    if "Sweeps" in setup_data and self.setuptype not in [
                        0,
                        7,
                    ]:  # 0 and 7 represent setup HFSSDrivenAuto
                        if self.setuptype <= 4:
                            app = setup_data["Sweeps"]
                            app.pop("NextUniqueID", None)
                            app.pop("MoveBackForward", None)
                            app.pop("MoveBackwards", None)
                            for el in app:
                                if isinstance(app[el], (OrderedDict, dict)):
                                    self.sweeps.append(SweepHFSS(self, el, props=app[el]))

                        else:
                            app = setup_data["Sweeps"]
                            for el in app:
                                if isinstance(app[el], (OrderedDict, dict)):
                                    self.sweeps.append(SweepMatrix(self, el, props=app[el]))
                        setup_data.pop("Sweeps", None)
                    self.props = SetupProps(self, OrderedDict(setup_data))
            except:
                self.props = SetupProps(self, OrderedDict())

    @property
    def is_solved(self):
        """Verify if solutions are available for given setup.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        if self.p_app.design_solutions.default_adaptive:
            expressions = [
                i
                for i in self.p_app.post.available_report_quantities(
                    solution="{} : {}".format(self.name, self.p_app.design_solutions.default_adaptive)
                )
            ]
            sol = self.p_app.post.reports_by_category.standard(
                setup_name="{} : {}".format(self.name, self.p_app.design_solutions.default_adaptive),
                expressions=expressions[0],
            )
        else:
            expressions = [i for i in self.p_app.post.available_report_quantities(solution=self.name)]
            sol = self.p_app.post.reports_by_category.standard(setup_name=self.name, expressions=expressions[0])
        if identify_setup(self.props):
            sol.domain = "Time"
        return True if sol.get_solution_data() else False

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @p_app.setter
    def p_app(self, value):
        self._app = value

    @property
    def omodule(self):
        """Analysis module."""
        return self._app.oanalysis

    @property
    def name(self):
        """Name."""
        return self._setupname

    @name.setter
    def name(self, name):
        self._setupname = name
        self.props["Name"] = name


class Setup(CommonSetup):
    """Initializes, creates, and updates a 3D setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        CommonSetup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def create(self):
        """Add a new setup based on class settings in AEDT.

        Returns
        -------
        dict
            Dictionary of arguments.

        References
        ----------

        >>> oModule.InsertSetup
        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.InsertSetup(soltype, arg)
        return arg

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditSetup
        """
        legacy_update = self.auto_update
        self.auto_update = False
        if update_dictionary:
            for el in update_dictionary:
                self.props[el] = update_dictionary[el]
        self.auto_update = legacy_update
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete actual Setup.

        Returns
        -------
        bool
            ``True`` if setup is deleted. ``False`` if it failed.
        """

        self.omodule.DeleteSetups([self.name])
        self._app.setups.remove(self)
        return True

    @pyaedt_function_handler()
    def _expression_cache(
        self,
        expression_list,
        report_type_list,
        intrinsics_list,
        isconvergence_list,
        isrelativeconvergence,
        conv_criteria,
    ):
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
        if isinstance(expression_list, list):
            i = 0
            while i < len(expression_list):
                expression = expression_list[i]
                name = expression.replace("(", "_") + "1"
                name = name.replace(")", "_")
                name = name.replace(" ", "_")
                name = name.replace(".", "_")
                name = name.replace("/", "_")
                name = name.replace("*", "_")
                name = name.replace("+", "_")
                name = name.replace("-", "_")
                if isinstance(report_type_list, list):
                    report_type = report_type_list[i]
                else:
                    report_type = report_type_list
                if isinstance(isconvergence_list, list):
                    isconvergence = isconvergence_list[i]
                else:
                    isconvergence = isconvergence_list
                if type(intrinsics_list) is list:
                    intrinsics = intrinsics_list[i]
                else:
                    intrinsics = intrinsics_list
                list_data.append(
                    [
                        "NAME:CacheItem",
                        "Title:=",
                        name,
                        "Expression:=",
                        expression,
                        "Intrinsics:=",
                        intrinsics,
                        "IsConvergence:=",
                        isconvergence,
                        "UseRelativeConvergence:=",
                        userelative,
                        "MaxConvergenceDelta:=",
                        conv_criteria,
                        "MaxConvergeValue:=",
                        str(conv_criteria),
                        "ReportType:=",
                        report_type,
                        ["NAME:ExpressionContext"],
                    ]
                )
                i += 1

        else:
            name = expression_list.replace("(", "") + "1"
            name = name.replace(")", "")
            name = name.replace(" ", "")
            name = name.replace(",", "_")
            list_data.append(
                [
                    "NAME:CacheItem",
                    "Title:=",
                    name,
                    "Expression:=",
                    expression_list,
                    "Intrinsics:=",
                    intrinsics_list,
                    "IsConvergence:=",
                    isconvergence_list,
                    "UseRelativeConvergence:=",
                    userelative,
                    "MaxConvergenceDelta:=",
                    conv_criteria,
                    "MaxConvergeValue:=",
                    str(conv_criteria),
                    "ReportType:=",
                    report_type_list,
                    ["NAME:ExpressionContext"],
                ]
            )

        return list_data

    @pyaedt_function_handler()
    def enable_expression_cache(
        self,
        expressions,
        report_type="Fields",
        intrinsics="",
        isconvergence=True,
        isrelativeconvergence=True,
        conv_criteria=1,
    ):
        """Enable an expression cache.

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
        isconvergence : bool or str or list, optional
            Whether the expression is in the convergence criteria. The default is ``True``.
            If a list of expressions is supplied, a corresponding list of Boolean values must be
            supplied.
        isrelativeconvergence : bool, optional
            The default is ``True``.
        conv_criteria :
            The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        expression_cache = self._expression_cache(
            expressions, report_type, intrinsics, isconvergence, isrelativeconvergence, conv_criteria
        )
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name

        self.omodule.EditSetup(setup_name, ["NAME:" + setup_name, "IsEnabled:=", True])
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name

        self.omodule.EditSetup(setup_name, ["NAME:" + setup_name, "IsEnabled:", False])
        return True

    @pyaedt_function_handler()
    def add_mesh_link(
        self,
        design_name,
        solution_name=None,
        parameters_dict=None,
        project_name="This Project*",
        force_source_to_solve=True,
        preserve_partner_solution=True,
        apply_mesh_operations=True,
        adapt_port=True,
    ):
        """Add a mesh link to another design.

        Parameters
        ----------
        design_name : str
            Name of the design.
        solution_name : str, optional
            Name of the solution in the format ``"setupname : solutionname"``.
            If ``None`` the default value is ``setupname : LastAdaptive``.
        parameters_dict : dict, optional
            Dictionary of the parameters.
            If ``None`` the default value is `appname.available_variations.nominal_w_values_dict`.
        project_name : str, optional
            Name of the project with the design. The default is ``"This Project*"``.
            However, you can supply the full path and name to another project.
        force_source_to_solve : bool, optional
            Default value is ``True``.
        preserve_partner_solution : bool, optional
            Default value is ``True``.
        apply_mesh_operations : bool, optional
            Apply mesh operations in target design on the imported mesh.
            Default value is ``True``.
        adapt_port : bool, optional
            Perform port adapt/seeding in target solve setup.
            Default value is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        auto_update = self.auto_update
        try:
            self.auto_update = False
            meshlinks = self.props["MeshLink"]
            # design type
            if self.p_app.design_type == "Mechanical":
                design_type = "ElectronicsDesktop"
            elif self.p_app.design_type == "Maxwell 2D" or self.p_app.design_type == "Maxwell 3D":
                design_type = "Maxwell"
            else:
                design_type = self.p_app.design_type
            meshlinks["Product"] = design_type
            # design name
            if not design_name or design_name is None:
                raise ValueError("Provide design name to add mesh link to.")
            elif design_name not in self.p_app.design_list:
                raise ValueError("Design does not exist in current project.")
            else:
                meshlinks["Design"] = design_name
            # project name
            if project_name != "This Project*":
                if os.path.exists(project_name):
                    meshlinks["Project"] = project_name
                    meshlinks["PathRelativeTo"] = "SourceProduct"
                else:
                    raise ValueError("Project file path provided does not exist.")
            else:
                meshlinks["Project"] = project_name
                meshlinks["PathRelativeTo"] = "TargetProject"
            # if self.p_app.solution_type == "SBR+":
            meshlinks["ImportMesh"] = True
            # solution name
            if solution_name is None:
                meshlinks["Soln"] = "{} : LastAdaptive".format(
                    self.p_app.oproject.GetDesign(design_name).GetChildObject("Analysis").GetChildNames()[0]
                )
            elif (
                solution_name.split()[0]
                in self.p_app.oproject.GetDesign(design_name).GetChildObject("Analysis").GetChildNames()
            ):
                meshlinks["Soln"] = "{} : LastAdaptive".format(solution_name.split()[0])
            else:
                raise ValueError("Setup does not exist in current design.")
            # parameters
            meshlinks["Params"] = OrderedDict({})
            if parameters_dict is None:
                parameters_dict = self.p_app.available_variations.nominal_w_values_dict
                for el in parameters_dict:
                    meshlinks["Params"][el] = el
            else:
                for el in parameters_dict:
                    if el in list(self._app.available_variations.nominal_w_values_dict.keys()):
                        meshlinks["Params"][el] = el
                    else:
                        meshlinks["Params"][el] = parameters_dict[el]
            meshlinks["ForceSourceToSolve"] = force_source_to_solve
            meshlinks["PreservePartnerSoln"] = preserve_partner_solution
            meshlinks["ApplyMeshOp"] = apply_mesh_operations
            if self.p_app.design_type != "Maxwell 2D" or self.p_app.design_type != "Maxwell 3D":
                meshlinks["AdaptPort"] = adapt_port
            self.update()
            self.auto_update = auto_update
            return True
        except:
            self.auto_update = auto_update
            return False


class SetupCircuit(CommonSetup):
    """Initializes, creates, and updates a circuit setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`
        Inherited app object.
    solutiontype : str, int
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
      Whether to create the setup from a template. The default is ``True.``
      If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        CommonSetup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def _init_props(self, isnewsetup=False):
        props = {}
        if isnewsetup:
            setup_template = SetupKeys.get_setup_templates()[self.setuptype]
            self.props = SetupProps(self, setup_template)
        else:
            self.props = SetupProps(self, OrderedDict())
            try:
                setups_data = self.p_app.design_properties["SimSetups"]["SimSetup"]
                if type(setups_data) is not list:
                    setups_data = [setups_data]
                for setup in setups_data:
                    if self.name == setup["Name"]:
                        setup_data = setup
                        setup_data.pop("Sweeps", None)
                        self.props = SetupProps(self, setup_data)
            except:
                self.props = SetupProps(self, OrderedDict())
        self.props["Name"] = self.name

    @property
    def _odesign(self):
        """Design."""
        return self._app._odesign

    @pyaedt_function_handler()
    def create(self):
        """Add a new setup based on class settings in AEDT.

        Returns
        -------
        dict
            Dictionary of the arguments.

        References
        ----------

        >>> oModule.AddLinearNetworkAnalysis
        >>> oModule.AddDCAnalysis
        >>> oModule.AddTransient
        >>> oModule.AddQuickEyeAnalysis
        >>> oModule.AddVerifEyeAnalysis
        >>> oModule.AddAMIAnalysis
        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:SimSetup"]
        _dict2arg(self.props, arg)
        self._setup(soltype, arg)
        return arg

    @pyaedt_function_handler()
    def _setup(self, soltype, arg, newsetup=True):
        if newsetup:
            if soltype == "NexximLNA":
                self.omodule.AddLinearNetworkAnalysis(arg)
            elif soltype == "NexximDC":
                self.omodule.AddDCAnalysis(arg)
            elif soltype == "NexximTransient":
                self.omodule.AddTransient(arg)
            elif soltype == "NexximQuickEye":
                self.omodule.AddQuickEyeAnalysis(arg)
            elif soltype == "NexximVerifEye":
                self.omodule.AddVerifEyeAnalysis(arg)
            elif soltype == "NexximAMI":
                self.omodule.AddAMIAnalysis(arg)
            else:
                warnings.warn("Solution Not Implemented Yet")
        else:
            if soltype == "NexximLNA":
                self.omodule.EditLinearNetworkAnalysis(self.name, arg)
            elif soltype == "NexximDC":
                self.omodule.EditDCAnalysis(self.name, arg)
            elif soltype == "NexximTransient":
                self.omodule.EditTransient(self.name, arg)
            elif soltype == "NexximQuickEye":
                self.omodule.EditQuickEyeAnalysis(self.name, arg)
            elif soltype == "NexximVerifEye":
                self.omodule.EditVerifEyeAnalysis(self.name, arg)
            elif soltype == "NexximAMI":
                self.omodule.EditAMIAnalysis(self.name, arg)

            else:
                raise NotImplementedError("Solution type '{}' is not implemented yet".format(soltype))
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        legacy_update = self.auto_update
        self.auto_update = False
        if update_dictionary:
            for el in update_dictionary:
                self.props[el] = update_dictionary[el]
        arg = ["NAME:SimSetup"]
        soltype = SetupKeys.SetupNames[self.setuptype]
        _dict2arg(self.props, arg)
        self._setup(soltype, arg, False)
        self.auto_update = legacy_update
        return True

    @pyaedt_function_handler()
    def add_sweep_points(self, sweep_variable="Freq", sweep_points=1, units="GHz", override_existing_sweep=True):
        """Add a linear count sweep to existing Circuit Setup.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        sweep_points : float or str or list, optional
            Sweep points to apply linear sweep. It can be a list or single points.
             Points can be float or str. If ``str`` then no units will be applied.
        end_point float or str, optional
            End Point of Linear Count sweep. If ``str`` then no units will be applied.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point
        override_existing_sweep : bool, optional
            Define if existing sweep on the same variable has to be overridden or kept and added to this new sweep.

        Returns
        -------
        bool
            ``True`` is succeeded.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        if isinstance(sweep_points, (int, float)):
            sweep_points = [sweep_points]
        sweeps = []
        for el in sweep_points:
            if isinstance(el, (int, float)):
                sweeps.append(str(el) + units)
            else:
                sweeps.append(el)
        lin_data = " ".join(sweeps)
        return self._add_sweep(sweep_variable, lin_data, override_existing_sweep)

    @pyaedt_function_handler()
    def add_sweep_count(
        self,
        sweep_variable="Freq",
        start_point=1,
        end_point=100,
        count=100,
        units="GHz",
        count_type="Linear",
        override_existing_sweep=True,
    ):
        """Add a step sweep to existing Circuit Setup. It can be ``"Linear"``, ``"Decade"`` or ``"Octave"``.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        start_point : float or str, optional
            Start Point of Linear Count sweep. If ``str`` then no units will be applied.
        end_point : float or str, optional
            End Point of Linear Count sweep. If ``str`` then no units will be applied.
        count :  int, optional
            Number of points. Default is ``100``.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point.
        count_type : str, optional
            Count Type. Default is ``"Linear"``. It can be also ``"Decade"`` or ``"Octave"``.
        override_existing_sweep : bool, optional
            Define if existing sweep on the same variable has to be overridden or kept and added to this new sweep.

        Returns
        -------
        bool
            ``True`` is succeeded.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        if isinstance(start_point, (int, float)):
            start_point = str(start_point) + units
        if isinstance(end_point, (int, float)):
            end_point = str(end_point) + units
        lin_in = "LINC"
        if count_type.lower() == "decade":
            lin_in = "DEC"
        elif count_type.lower() == "octave":
            lin_in = "OCT"
        lin_data = "{} {} {} {}".format(lin_in, start_point, end_point, count)
        return self._add_sweep(sweep_variable, lin_data, override_existing_sweep)

    @pyaedt_function_handler()
    def add_sweep_step(
        self,
        sweep_variable="Freq",
        start_point=1,
        end_point=100,
        step_size=1,
        units="GHz",
        override_existing_sweep=True,
    ):
        """Add a linear count sweep to existing Circuit Setup.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        start_point : float or str, optional
            Start Point of Linear Count sweep. If ``str`` then no units will be applied.
        end_point : float or str, optional
            End Point of Linear Count sweep. If ``str`` then no units will be applied.
        step_size :  float or str, optional
            Step Size of sweep. If ``str`` then no units will be applied.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point
        override_existing_sweep : bool, optional
            Define if existing sweep on the same variable has to be overridden or kept and added to this new sweep.

        Returns
        -------
        bool
            ``True`` is succeeded.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        if isinstance(start_point, (int, float)):
            start_point = str(start_point) + units
        if isinstance(end_point, (int, float)):
            end_point = str(end_point) + units
        if isinstance(step_size, (int, float)):
            step_size = str(step_size) + units
        linc_data = "LIN {} {} {}".format(start_point, end_point, step_size)
        return self._add_sweep(sweep_variable, linc_data, override_existing_sweep)

    @pyaedt_function_handler()
    def _add_sweep(self, sweep_variable, equation, override_existing_sweep):
        if isinstance(self.props["SweepDefinition"], list):
            for sw in self.props["SweepDefinition"]:
                if sw["Variable"] == sweep_variable:
                    if override_existing_sweep:
                        sw["Data"] = equation
                    else:
                        sw["Data"] += " " + equation
                    return self.update()
        elif self.props["SweepDefinition"]["Variable"] == sweep_variable:
            if override_existing_sweep:
                self.props["SweepDefinition"]["Data"] = equation
            else:
                self.props["SweepDefinition"]["Data"] += " " + equation
            return self.update()
        if isinstance(self.props["SweepDefinition"], (OrderedDict, dict)):
            self.props["SweepDefinition"] = [self.props["SweepDefinition"]]
        prop = OrderedDict({"Variable": sweep_variable, "Data": equation, "OffsetF1": False, "Synchronize": 0})
        self.props["SweepDefinition"].append(prop)
        return self.update()

    @pyaedt_function_handler()
    def _expression_cache(
        self,
        expression_list,
        report_type_list,
        intrinsics_list,
        isconvergence_list,
        isrelativeconvergence,
        conv_criteria,
    ):
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
        if isinstance(expression_list, list):
            i = 0
            while i < len(expression_list):
                expression = expression_list[i]
                name = expression.replace("(", "_") + "1"
                name = name.replace(")", "_")
                name = name.replace(" ", "_")
                if isinstance(report_type_list, list):
                    report_type = report_type_list[i]
                else:
                    report_type = report_type_list
                if isinstance(isconvergence_list, list):
                    isconvergence = isconvergence_list[i]
                else:
                    isconvergence = isconvergence_list
                if isinstance(intrinsics_list, list):
                    intrinsics = intrinsics_list[i]
                else:
                    intrinsics = intrinsics_list
                list_data.append(
                    [
                        "NAME:CacheItem",
                        "Title:=",
                        name,
                        "Expression:=",
                        expression,
                        "Intrinsics:=",
                        intrinsics,
                        "IsConvergence:=",
                        isconvergence,
                        "UseRelativeConvergence:=",
                        1,
                        "MaxConvergenceDelta:=",
                        1,
                        "MaxConvergeValue:=",
                        "0.01",
                        "ReportType:=",
                        report_type,
                        ["NAME:ExpressionContext"],
                    ]
                )
                i += 1

        else:
            name = expression_list.replace("(", "") + "1"
            name = name.replace(")", "")
            name = name.replace(" ", "")
            name = name.replace(",", "_")
            list_data.append(
                [
                    "NAME:CacheItem",
                    "Title:=",
                    name,
                    "Expression:=",
                    expression_list,
                    "Intrinsics:=",
                    intrinsics_list,
                    "IsConvergence:=",
                    isconvergence_list,
                    "UseRelativeConvergence:=",
                    userelative,
                    "MaxConvergenceDelta:=",
                    conv_criteria,
                    "MaxConvergeValue:=",
                    str(conv_criteria),
                    "ReportType:=",
                    report_type_list,
                    ["NAME:ExpressionContext"],
                ]
            )

        return list_data

    @pyaedt_function_handler()
    def enable_expression_cache(
        self,
        expressions,
        report_type="Fields",
        intrinsics="",
        isconvergence=True,
        isrelativeconvergence=True,
        conv_criteria=1,
    ):
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

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["Name:SimSetup"]
        _dict2arg(self.props, arg)
        expression_cache = self._expression_cache(
            expressions, report_type, intrinsics, isconvergence, isrelativeconvergence, conv_criteria
        )
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name
        self._odesign.EnableSolutionSetup(setup_name, True)
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name
        self._odesign.EnableSolutionSetup(setup_name, False)
        return True


class Setup3DLayout(CommonSetup):
    """Initializes, creates, and updates a 3D Layout setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3DLayout.FieldAnalysis3DLayout`
        Inherited app object.
    solutiontype : int or str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True.``
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        CommonSetup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def _init_props(self, isnewsetup=False):
        if isnewsetup:
            setup_template = SetupKeys.get_setup_templates()[self.setuptype]
            self.props = SetupProps(self, setup_template)
        else:
            try:
                setups_data = self._app.design_properties["Setup"]["Data"]
                if self.name in setups_data:
                    setup_data = setups_data[self.name]
                    if "Data" in setup_data:  # 0 and 7 represent setup HFSSDrivenAuto
                        app = setup_data["Data"]
                        for el in app:
                            if isinstance(app[el], (OrderedDict, dict)):
                                self.sweeps.append(SweepHFSS3DLayout(self, el, props=app[el]))

                    self.props = SetupProps(self, OrderedDict(setup_data))
            except:
                self.props = SetupProps(self, OrderedDict())

    @property
    def is_solved(self):
        """Verify if solutions are available for a given setup.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        if self.props.get("SolveSetupType", "HFSS") == "HFSS":
            sol = self._app.post.reports_by_category.standard(setup_name="{} : Last Adaptive".format(self.name))
        elif self.props.get("SolveSetupType", "HFSS") == "SIwave":
            sol = self._app.post.reports_by_category.standard(
                setup_name="{} : {}".format(self.name, self.sweeps[0].name)
            )
        else:
            sol = self._app.post.reports_by_category.standard(setup_name=self.name)
        if identify_setup(self.props):
            sol.domain = "Time"
        return True if sol.get_solution_data() else False

    @property
    def solver_type(self):
        """Setup type.

        Returns
        -------
        type
            Setup type.
        """

        if "SolveSetupType" in self.props:
            return self.props["SolveSetupType"]
        else:
            return None

    @pyaedt_function_handler()
    def create(self):
        """Add a new setup based on class settings in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Add
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.Add(arg)
        return True

    @pyaedt_function_handler()
    def update(self, update_dictionary=None):
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary of settings to apply.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Edit
        """
        if update_dictionary:
            for el in update_dictionary:
                self.props._setitem_without_update(el, update_dictionary[el])
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.Edit(self.name, arg)
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.Edit
        """
        self.props["Properties"]["Enable"] = "true"
        self.update()
        return True

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.Edit
        """
        self.props["Properties"]["Enable"] = "false"
        self.update()
        return True

    @pyaedt_function_handler()
    def export_to_hfss(self, file_fullname, keep_net_name=False):
        """Export the HFSS 3DLayout design to HFSS 3D design.

        Parameters
        ----------
        file_fullname : str
            Full path and file name for exporting the project.

        keep_net_name : bool
            Keep net name in 3D export when ``True`` or by default when ``False``. Default value is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportToHfss
        """

        file_fullname = file_fullname
        if not os.path.isdir(os.path.dirname(file_fullname)):
            return False
        file_fullname = os.path.splitext(file_fullname)[0] + ".aedt"
        self.omodule.ExportToHfss(self.name, file_fullname)
        timeout = 20
        time.sleep(2)
        while timeout > 0:
            timeout -= 1
            if os.path.exists(file_fullname):
                timeout = 0
            time.sleep(1)
        if keep_net_name:
            from pyaedt import Hfss

            primitives_3d_pts_per_nets = self._get_primitives_points_per_net()
            via_per_nets = self._get_via_position_per_net()
            layers_elevation = {
                lay.name: lay.lower_elevation + lay.thickness / 2
                for lay in list(self.p_app.modeler.edb.stackup.signal_layers.values())
            }
            hfss = Hfss(projectname=file_fullname)
            units = hfss.modeler.model_units
            aedt_units = AEDT_UNITS["Length"][units]
            self._convert_edb_to_aedt_units(input_dict=primitives_3d_pts_per_nets, output_unit=aedt_units)
            self._convert_edb_to_aedt_units(input_dict=via_per_nets, output_unit=aedt_units)
            self._convert_edb_layer_elevation_to_aedt_units(input_dict=layers_elevation, output_units=aedt_units)
            metal_object = [
                obj.name
                for obj in hfss.modeler.solid_objects
                if not obj.material_name in hfss.modeler.materials.dielectrics
            ]
            for net, primitives in primitives_3d_pts_per_nets.items():
                obj_dict = {}
                for position in primitives_3d_pts_per_nets[net]:
                    hfss_objs = [p for p in hfss.modeler.get_bodynames_from_position(position) if p in metal_object]
                    if hfss_objs:
                        for p in hfss.modeler.get_bodynames_from_position(position, None, False):
                            if p in metal_object:
                                obj_ind = hfss.modeler.object_id_dict[p]
                                if obj_ind not in obj_dict:
                                    obj_dict[obj_ind] = hfss.modeler.objects[obj_ind]
                if net in via_per_nets:
                    for via_pos in via_per_nets[net]:
                        for p in hfss.modeler.get_bodynames_from_position(via_pos, None, False):
                            if p in metal_object:
                                obj_ind = hfss.modeler.object_id_dict[p]
                                if obj_ind not in obj_dict:
                                    obj_dict[obj_ind] = hfss.modeler.objects[obj_ind]
                            for lay_el in list(layers_elevation.values()):
                                pad_pos = via_pos[:2]
                                pad_pos.append(lay_el)
                                pad_objs = hfss.modeler.get_bodynames_from_position(pad_pos, None, False)
                                for pad_obj in pad_objs:
                                    if pad_obj in metal_object:
                                        pad_ind = hfss.modeler.object_id_dict[pad_obj]
                                        if pad_ind not in obj_dict:
                                            obj_dict[pad_ind] = hfss.modeler.objects[pad_ind]
                obj_list = list(obj_dict.values())
                if len(obj_list) == 1:
                    obj_list[0].name = net
                    obj_list[0].color = [randrange(255), randrange(255), randrange(255)]
                elif len(obj_list) > 1:
                    united_object = hfss.modeler.unite(obj_list, purge=True)
                    obj_ind = hfss.modeler.object_id_dict[united_object]
                    hfss.modeler.objects[obj_ind].name = net
                    hfss.modeler.objects[obj_ind].color = [randrange(255), randrange(255), randrange(255)]
            hfss.close_project(save_project=True)
        return True

    @pyaedt_function_handler()
    def _get_primitives_points_per_net(self):
        edb = self.p_app.modeler.edb
        net_primitives = edb.core_primitives.primitives_by_net
        primitive_dict = {}
        for net, primitives in net_primitives.items():
            primitive_dict[net] = []
            if primitives:
                for prim in primitives:
                    layer = edb.stackup.signal_layers[prim.layer_name]
                    z = layer.lower_elevation + layer.thickness / 2
                    for arc in prim.arcs:
                        pt = self._get_polygon_centroid(arc.points)
                        pt.append(z)
                        primitive_dict[net].append(pt)
        return primitive_dict

    @pyaedt_function_handler()
    def _get_polygon_centroid(self, arcs=None):
        if arcs:
            k = len(arcs[0])
            x = sum(arcs[0]) / k
            y = sum(arcs[1]) / k
            return [x, y]

    @pyaedt_function_handler()
    def _convert_edb_to_aedt_units(self, input_dict=None, output_unit=0.001):
        if input_dict:
            for k, v in input_dict.items():
                new_pts = []
                for pt in v:
                    new_pts.append([round(coord / output_unit, 5) for coord in pt])
                input_dict[k] = new_pts

    @pyaedt_function_handler()
    def _get_via_position_per_net(self):
        via_dict = {}
        via_list = list(self.p_app.modeler.edb.core_padstack.padstack_instances.values())
        if via_list:
            for net in list(self.p_app.modeler.edb.core_nets.nets.keys()):
                vias = [via for via in via_list if via.net_name == net and via.start_layer != via.stop_layer]
                if vias:
                    via_dict[net] = []
                    for via in vias:
                        via_pos = via.position
                        z1 = self.p_app.modeler.edb.stackup.signal_layers[via.start_layer].lower_elevation
                        z2 = self.p_app.modeler.edb.stackup.signal_layers[via.stop_layer].upper_elevation
                        z = (z2 + z1) / 2
                        via_pos.append(z)
                        via_dict[net].append(via_pos)
        return via_dict

    @pyaedt_function_handler()
    def _convert_edb_layer_elevation_to_aedt_units(self, input_dict=None, output_units=0.001):
        if input_dict:
            for k, v in input_dict.items():
                input_dict[k] = round(v / output_units, 5)

    @pyaedt_function_handler()
    def export_to_q3d(self, file_fullname):
        """Export the HFSS 3DLayout design to Q3D design.

        Parameters
        ----------
        file_fullname : str
            Full path and file name for exporting the project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportToQ3d
        """

        if not os.path.isdir(os.path.dirname(file_fullname)):
            return False
        file_fullname = os.path.splitext(file_fullname)[0] + ".aedt"
        self.omodule.ExportToQ3d(self.name, file_fullname)
        timeout = 20
        while timeout > 0:
            timeout -= 1
            if os.path.exists(file_fullname):
                timeout = 0
            time.sleep(2)
        return True

    @pyaedt_function_handler()
    def add_sweep(self, sweepname=None, sweeptype="Interpolating"):
        """Add a frequency sweep.

        Parameters
        ----------
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. Options are ``"Interpolating"`` and ``"Discrete"``.
            The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS3DLayout`
            Sweep object.

        References
        ----------

        >>> oModule.AddSweep
        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        sweep_n = SweepHFSS3DLayout(self, sweepname, sweeptype)
        if sweep_n.create():
            self.sweeps.append(sweep_n)
            return sweep_n
        return False

    def import_from_json(self, file_path):
        """Import setup properties from a json file.

        Parameters
        ----------
        file_path : str
            File path of the json file.
        """
        self.props._import_properties_from_json(file_path)
        if self.props["AdaptiveSettings"]["AdaptType"] == "kBroadband":
            BroadbandFrequencyDataList = self.props["AdaptiveSettings"]["BroadbandFrequencyDataList"]
            max_delta = BroadbandFrequencyDataList["AdaptiveFrequencyData"][0]["MaxDelta"]
            max_passes = BroadbandFrequencyDataList["AdaptiveFrequencyData"][0]["MaxPasses"]

            SingleFrequencyDataList = self.props["AdaptiveSettings"]["SingleFrequencyDataList"]
            SingleFrequencyDataList["AdaptiveFrequencyData"]["MaxDelta"] = max_delta
            SingleFrequencyDataList = self.props["AdaptiveSettings"]["SingleFrequencyDataList"]
            SingleFrequencyDataList["AdaptiveFrequencyData"]["MaxPasses"] = max_passes
        return True

    def export_to_json(self, file_path, overwrite=False):
        """Export all setup properties into a json file.

        Parameters
        ----------
        file_path : str
            File path of the json file.
        overwrite : bool
            Whether to overwrite the file if it already exists.
        """
        if os.path.isdir(file_path):  # pragma no cover
            if not overwrite:  # pragma no cover
                raise logging.error("File {} already exists. Configure file is not exported".format(file_path))
        return self.props._export_properties_to_json(file_path)


class SetupHFSS(Setup, object):
    """Initializes, creates, and updates an HFSS setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        Setup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def get_derivative_variables(self):
        """Return Derivative Enabled variables.

        Returns
        -------
        List
        """
        try:
            return list(self._app.oanalysis.GetDerivativeVariables(self.name))
        except AttributeError:
            return []

    @pyaedt_function_handler()
    def add_derivatives(self, derivative_list):
        """Add derivatives to the setup.

        Parameters
        ----------
        derivative_list : str or List
            Derivative variable names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not isinstance(derivative_list, list):
            derivative_list = [derivative_list]
        self.auto_update = False
        self.props["VariablesForDerivatives"] = derivative_list + self.get_derivative_variables()
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def create_frequency_sweep(
        self,
        unit,
        freqstart,
        freqstop,
        num_of_freq_points=None,
        sweepname=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
        interpolation_tol=0.5,
        interpolation_max_solutions=250,
    ):
        """Create a sweep with the specified number of points.

        Parameters
        ----------
        unit : str
            Frequency Units.
        freqstart : float
            Starting frequency of the sweep, such as ``1``.
        freqstop : float
            Stopping frequency of the sweep.
        num_of_freq_points : int
            Number of frequency points in the range. The default is ``401`` for
            a sweep type of ``"Interpolating"`` or ``"Fast"``. The default is ``5`` for a sweep
            type of ``"Discrete"``.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
            and ``"Discrete"``. The default is ``"Discrete"``.
        interpolation_tol : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the interpolation process.
            The default is ``250``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------

        Create a setup named ``"LinearCountSetup"`` and use it in a linear count sweep
        named ``"LinearCountSweep"``.

        >>> setup = hfss.create_setup("LinearCountSetup")
        >>> linear_count_sweep = hfss.create_linear_count_sweep(setupname="LinearCountSetup",
        ...                                                     sweepname="LinearCountSweep",
        ...                                                     unit="MHz", freqstart=1.1e3,
        ...                                                     freqstop=1200.1, num_of_freq_points=1658)
        >>> type(linear_count_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """

        # Set default values for num_of_freq_points if a value was not passed. Also,
        # check that sweep_type is valid.
        if sweep_type in ["Interpolating", "Fast"]:
            if num_of_freq_points == None:
                num_of_freq_points = 401
        elif sweep_type == "Discrete":
            if num_of_freq_points == None:
                num_of_freq_points = 5
        else:
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if sweepname in [sweep.name for sweep in self.sweeps]:
            oldname = sweepname
            sweepname = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname)
        sweepdata = self.add_sweep(sweepname, sweep_type)
        if not sweepdata:
            return False
        sweepdata.props["RangeType"] = "LinearCount"
        sweepdata.props["RangeStart"] = str(freqstart) + unit
        sweepdata.props["RangeEnd"] = str(freqstop) + unit
        sweepdata.props["RangeCount"] = num_of_freq_points
        sweepdata.props["Type"] = sweep_type
        if sweep_type == "Interpolating":
            sweepdata.props["InterpTolerance"] = interpolation_tol
            sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
            sweepdata.props["InterpMinSolns"] = 0
            sweepdata.props["InterpMinSubranges"] = 1
        sweepdata.props["SaveFields"] = save_fields
        sweepdata.props["SaveRadFields"] = save_rad_fields
        sweepdata.update()
        self._app.logger.info("Linear count sweep {} has been correctly created".format(sweepname))
        return sweepdata

    @pyaedt_function_handler()
    def create_linear_step_sweep(
        self,
        setupname,
        unit,
        freqstart,
        freqstop,
        step_size,
        sweepname=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
    ):
        """Create a Sweep with a specified frequency step.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        step_size : float
            Frequency size of the step.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.
        sweep_type : str, optional
            Whether to create a ``"Discrete"``,``"Interpolating"`` or ``"Fast"`` sweep.
            The default is ``"Discrete"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------

        Create a setup named ``"LinearStepSetup"`` and use it in a linear step sweep
        named ``"LinearStepSweep"``.

        >>> setup = hfss.create_setup("LinearStepSetup")
        >>> linear_step_sweep = hfss.create_linear_step_sweep(setupname="LinearStepSetup",
        ...                                                   sweepname="LinearStepSweep",
        ...                                                   unit="MHz", freqstart=1.1e3,
        ...                                                   freqstop=1200.1, step_size=153.8)
        >>> type(linear_step_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to either 'Discrete', 'Interpolating', or 'Fast'")
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self._app.setup_names:
            return False
        for s in self._app.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self._app.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, sweep_type)
                if not sweepdata:
                    return False
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeStep"] = str(step_size) + unit
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = sweep_type
                if sweep_type == "Interpolating":
                    sweepdata.props["InterpTolerance"] = 0.5
                    sweepdata.props["InterpMaxSolns"] = 250
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1
                sweepdata.update()
                self._app.logger.info("Linear step sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False

    @pyaedt_function_handler()
    def create_single_point_sweep(
        self,
        setupname,
        unit,
        freq,
        sweepname=None,
        save_single_field=True,
        save_fields=False,
        save_rad_fields=False,
    ):
        """Create a Sweep with a single frequency point.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        freq : float, list
            Frequency of the single point or list of frequencies to create distinct single points.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_single_field : bool, list, optional
            Whether to save the fields of the single point. The default is ``True``.
            If a list is specified, the length must be the same as freq length.
        save_fields : bool, optional
            Whether to save the fields for all points and subranges defined in the sweep. The default is ``False``.
        save_rad_fields : bool, optional
            Whether to save only the radiating fields. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------

        Create a setup named ``"LinearStepSetup"`` and use it in a single point sweep
        named ``"SinglePointSweep"``.

        >>> setup = hfss.create_setup("LinearStepSetup")
        >>> single_point_sweep = hfss.create_single_point_sweep(setupname="LinearStepSetup",
        ...                                                   sweepname="SinglePointSweep",
        ...                                                   unit="MHz", freq=1.1e3)
        >>> type(single_point_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweepname is None:
            sweepname = generate_unique_name("SinglePoint")

        if isinstance(save_single_field, list):
            if not isinstance(freq, list) or len(save_single_field) != len(freq):
                raise AttributeError("The length of save_single_field must be the same as freq length.")

        add_subranges = False
        if isinstance(freq, list):
            if not freq:
                raise AttributeError("Frequency list is empty! Specify at least one frequency point.")
            freq0 = freq.pop(0)
            if freq:
                add_subranges = True
        else:
            freq0 = freq

        if isinstance(save_single_field, list):
            save0 = save_single_field.pop(0)
        else:
            save0 = save_single_field
            if add_subranges:
                save_single_field = [save0] * len(freq)

        if setupname not in self._app.setup_names:
            return False
        for s in self._app.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self._app.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeType"] = "SinglePoints"
                sweepdata.props["RangeStart"] = str(freq0) + unit
                sweepdata.props["RangeEnd"] = str(freq0) + unit
                sweepdata.props["SaveSingleField"] = save0
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["SMatrixOnlySolveMode"] = "Auto"
                if add_subranges:
                    for f, s in zip(freq, save_single_field):
                        sweepdata.add_subrange(rangetype="SinglePoints", start=f, unit=unit, save_single_fields=s)
                sweepdata.update()
                self._app.logger.info("Single point sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False

    @pyaedt_function_handler()
    def add_sweep(self, sweepname=None, sweeptype="Interpolating"):
        """Add a sweep to the project.

        Parameters
        ----------
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or :class:`pyaedt.modules.SolveSweeps.SweepMatrix`
            Sweep object.

        References
        ----------

        >>> oModule.InsertFrequencySweep
        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        if self.setuptype == 7:
            self._app.logger.warning("This method only applies to HFSS and Q3D. Use add_eddy_current_sweep method.")
            return False
        if self.setuptype <= 4:
            sweep_n = SweepHFSS(self, sweepname=sweepname, sweeptype=sweeptype)
        elif self.setuptype in [14, 30, 31]:
            sweep_n = SweepMatrix(self, sweepname=sweepname, sweeptype=sweeptype)
        else:
            self._app.logger.warning("This method only applies to HFSS, Q2D and Q3D.")
            return False
        sweep_n.create()
        self.sweeps.append(sweep_n)
        return sweep_n

    @pyaedt_function_handler()
    def enable_adaptive_setup_single(self, freq=None, max_passes=None, max_delta_s=None):
        """Enable HFSS single frequency setup.

        Parameters
        ----------
        freq : float, str, optional
            Frequency at which to set the adaptive convergence.
            The default is ``None`` which will not update the value in setup.
            You can enter a float value in (GHz) or a string.
        max_passes : int, optional
            Maximum number of adaptive passes. The default is ``None`` which will not update the value in setup.
        max_delta_s : float, optional
            Delta S convergence criteria. The default is ``None`` which will not update the value in setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "Single"
        if isinstance(freq, (int, float)):
            freq = "{}GHz".format(freq)
        if freq:
            self.props["Frequency"] = freq
        if max_passes:
            self.props["MaximumPasses"] = max_passes
        if max_delta_s:
            self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_broadband(self, low_frequency, high_frquency, max_passes=6, max_delta_s=0.02):
        """Enable HFSS broadband setup.

        Parameters
        ----------
        low_frequency : float, str
            Lower Frequency at which set the adaptive convergence.
            It can be float (GHz) or str.
        high_frquency : float, str
            Lower Frequency at which set the adaptive convergence. It can be float (GHz) or str.
        max_passes : int, optional
            Maximum number of adaptive passes. The default is ``6``.
        max_delta_s : float, optional
            Delta S Convergence criteria. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "BroadBand"
        for el in list(self.props["MultipleAdaptiveFreqsSetup"].keys()):
            del self.props["MultipleAdaptiveFreqsSetup"][el]
        if isinstance(low_frequency, (int, float)):
            low_frequency = "{}GHz".format(low_frequency)
        if isinstance(high_frquency, (int, float)):
            high_frquency = "{}GHz".format(high_frquency)
        self.props["MultipleAdaptiveFreqsSetup"]["Low"] = low_frequency
        self.props["MultipleAdaptiveFreqsSetup"]["High"] = high_frquency
        self.props["MaximumPasses"] = max_passes
        self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_multifrequency(self, frequencies, max_delta_s=0.02):
        """Enable HFSS multi-frequency setup.

        Parameters
        ----------
        frequencies : list
            Frequency at which to set the adaptive convergence. You can enter list entries
            as float values in GHz or as strings.
        max_delta_s : list, float
            Delta S convergence criteria. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "MultiFrequency"
        for el in list(self.props["MultipleAdaptiveFreqsSetup"].keys()):
            del self.props["MultipleAdaptiveFreqsSetup"][el]
        i = 0
        for f in frequencies:
            if isinstance(max_delta_s, float):
                if isinstance(f, (int, float)):
                    f = "{}GHz".format(f)
                self.props["MultipleAdaptiveFreqsSetup"][f] = [max_delta_s]
            else:
                if isinstance(f, (int, float)):
                    f = "{}GHz".format(f)
                try:
                    self.props["MultipleAdaptiveFreqsSetup"][f] = [max_delta_s[i]]
                except IndexError:
                    self.props["MultipleAdaptiveFreqsSetup"][f] = [0.02]
            i += 1
        self.auto_update = True
        return self.update()


class SetupHFSSAuto(Setup, object):
    """Initializes, creates, and updates an HFSS SBR+ or  HFSS Auto setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        Setup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def get_derivative_variables(self):
        """Return Derivative Enabled variables.

        Returns
        -------
        List
        """
        try:
            return list(self._app.oanalysis.GetDerivativeVariables(self.name))
        except AttributeError:
            return []

    @pyaedt_function_handler()
    def add_derivatives(self, derivative_list):
        """Add derivatives to the setup.

        Parameters
        ----------
        derivative_list : str or List
            Derivative variable names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not isinstance(derivative_list, list):
            derivative_list = [derivative_list]
        self.auto_update = False
        self.props["VariablesForDerivatives"] = derivative_list + self.get_derivative_variables()
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def add_subrange(self, rangetype, start, end=None, count=None, unit="GHz", clear=False):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count : int or float
            Frequency count or frequency step.
        unit : str, optional
            Frequency Units.
        clear : bool, optional
            Either if the subrange has to be appended to existing ones or replace them.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if clear:
            self.props["Sweeps"]["Sweep"]["RangeType"] = rangetype
            self.props["Sweeps"]["Sweep"]["RangeStart"] = str(start) + unit
            if rangetype == "LinearCount":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeCount"] = count
            elif rangetype == "LinearStep":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeStep"] = str(count) + unit
            elif rangetype == "LogScale":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeSamples"] = count
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
            return self.update()
        sweep_range = {"RangeType": rangetype, "RangeStart": str(start) + unit}
        if rangetype == "LinearCount":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = count
        elif rangetype == "LinearStep":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeStep"] = str(count) + unit
        elif rangetype == "LogScale":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = self.props["RangeCount"]
            sweep_range["RangeSamples"] = count
        if not self.props["Sweeps"]["Sweep"].get("SweepRanges") or not self.props["Sweeps"]["Sweep"]["SweepRanges"].get(
            "Subrange"
        ):
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
        self.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"].append(sweep_range)
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_single(self, freq=None, max_passes=None, max_delta_s=None):
        """Enable HFSS single frequency setup.

        Parameters
        ----------
        freq : float, str, optional
            Frequency at which to set the adaptive convergence.
            The default is ``None`` which will not update the value in setup.
            You can enter a float value in (GHz) or a string.
        max_passes : int, optional
            Maximum number of adaptive passes. The default is ``None`` which will not update the value in setup.
        max_delta_s : float, optional
            Delta S convergence criteria. The default is ``None`` which will not update the value in setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "Single"
        if isinstance(freq, (int, float)):
            freq = "{}GHz".format(freq)
        if freq:
            self.props["Frequency"] = freq
        if max_passes:
            self.props["MaximumPasses"] = max_passes
        if max_delta_s:
            self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_broadband(self, low_frequency, high_frquency, max_passes=6, max_delta_s=0.02):
        """Enable HFSS broadband setup.

        Parameters
        ----------
        low_frequency : float, str
            Lower Frequency at which set the adaptive convergence.
            It can be float (GHz) or str.
        high_frquency : float, str
            Lower Frequency at which set the adaptive convergence. It can be float (GHz) or str.
        max_passes : int, optional
            Maximum number of adaptive passes. The default is ``6``.
        max_delta_s : float, optional
            Delta S Convergence criteria. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "BroadBand"
        for el in list(self.props["MultipleAdaptiveFreqsSetup"].keys()):
            del self.props["MultipleAdaptiveFreqsSetup"][el]
        if isinstance(low_frequency, (int, float)):
            low_frequency = "{}GHz".format(low_frequency)
        if isinstance(high_frquency, (int, float)):
            high_frquency = "{}GHz".format(high_frquency)
        self.props["MultipleAdaptiveFreqsSetup"]["Low"] = low_frequency
        self.props["MultipleAdaptiveFreqsSetup"]["High"] = high_frquency
        self.props["MaximumPasses"] = max_passes
        self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_multifrequency(self, frequencies, max_delta_s=0.02):
        """Enable HFSS multi-frequency setup.

        Parameters
        ----------
        frequencies : list
            Frequency at which to set the adaptive convergence. You can enter list entries
            as float values in GHz or as strings.
        max_delta_s : list, float
            Delta S convergence criteria. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "MultiFrequency"
        for el in list(self.props["MultipleAdaptiveFreqsSetup"].keys()):
            del self.props["MultipleAdaptiveFreqsSetup"][el]
        i = 0
        for f in frequencies:
            if isinstance(max_delta_s, float):
                if isinstance(f, (int, float)):
                    f = "{}GHz".format(f)
                self.props["MultipleAdaptiveFreqsSetup"][f] = [max_delta_s]
            else:
                if isinstance(f, (int, float)):
                    f = "{}GHz".format(f)
                try:
                    self.props["MultipleAdaptiveFreqsSetup"][f] = [max_delta_s[i]]
                except IndexError:
                    self.props["MultipleAdaptiveFreqsSetup"][f] = [0.02]
            i += 1
        self.auto_update = True
        return self.update()


class SetupSBR(Setup, object):
    """Initializes, creates, and updates an HFSS SBR+ or  HFSS Auto setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        Setup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def add_subrange(self, rangetype, start, end=None, count=None, unit="GHz", clear=False):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count : int or float
            Frequency count or frequency step.
        unit : str, optional
            Frequency Units.
        clear : bool, optional
            Either if the subrange has to be appended to existing ones or replace them.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if clear:
            self.props["Sweeps"]["Sweep"]["RangeType"] = rangetype
            self.props["Sweeps"]["Sweep"]["RangeStart"] = str(start) + unit
            if rangetype == "LinearCount":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeCount"] = count
            elif rangetype == "LinearStep":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeStep"] = str(count) + unit
            elif rangetype == "LogScale":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeSamples"] = count
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
            return self.update()
        sweep_range = {"RangeType": rangetype, "RangeStart": str(start) + unit}
        if rangetype == "LinearCount":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = count
        elif rangetype == "LinearStep":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeStep"] = str(count) + unit
        elif rangetype == "LogScale":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = self.props["RangeCount"]
            sweep_range["RangeSamples"] = count
        if not self.props["Sweeps"]["Sweep"].get("SweepRanges") or not self.props["Sweeps"]["Sweep"]["SweepRanges"].get(
            "Subrange"
        ):
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
        self.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"].append(sweep_range)
        return self.update()


class SetupMaxwell(Setup, object):
    """Initializes, creates, and updates an HFSS setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        Setup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def add_eddy_current_sweep(self, range_type="LinearStep", start=0.1, end=100, count=0.1, units="Hz", clear=True):
        """Create a Maxwell Eddy Current Sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, ``"LogScale"`` and ``"SinglePoints"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. Required for ``rangetype="LinearCount"|"LinearStep"|"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. Required for ``rangetype="LinearCount"|"LinearStep"|"LogScale"``.
        units : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"Hz"``.

        clear : boolean, optional
            If set to ``True``, all other subranges will be suppressed except the current one under creation.
            Default value is ``False``.

        Returns
        -------
        bool
        """

        if self.setuptype != 7:
            self._app.logger.warning("This method only applies to Maxwell Eddy Current Solution.")
            return False
        legacy_update = self.auto_update
        self.auto_update = False
        props = OrderedDict()
        props["RangeType"] = range_type
        props["RangeStart"] = "{}{}".format(start, units)
        if range_type == "LinearStep":
            props["RangeEnd"] = "{}{}".format(end, units)
            props["RangeStep"] = "{}{}".format(count, units)
        elif range_type == "LinearCount":
            props["RangeEnd"] = "{}{}".format(end, units)
            props["RangeCount"] = count
        elif range_type == "LogScale":
            props["RangeEnd"] = "{}{}".format(end, units)
            props["RangeSamples"] = count
        elif range_type == "SinglePoints":
            props["RangeEnd"] = "{}{}".format(start, units)
        if clear:
            self.props["SweepRanges"]["Subrange"] = props
        elif isinstance(self.props["SweepRanges"]["Subrange"], list):
            self.props["SweepRanges"]["Subrange"].append(props)
        else:
            self.props["SweepRanges"]["Subrange"] = [self.props["SweepRanges"]["Subrange"], props]
        self.update()
        self.auto_update = legacy_update
        return True
