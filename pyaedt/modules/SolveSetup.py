"""
This module contains these classes: `Setup`, `Setup3DLayout`, and `SetupCircuit`.

This module provides all functionalities for creating and editing setups in AEDT.
It is based on templates to allow for easy creation and modification of setup properties.

"""

from __future__ import absolute_import  # noreorder

from collections import OrderedDict
import os.path
from random import randrange
import re
import time
import warnings

from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import PropsManager
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.modules.SetupTemplates import SetupKeys
from pyaedt.modules.SolveSweeps import SetupProps
from pyaedt.modules.SolveSweeps import SweepHFSS
from pyaedt.modules.SolveSweeps import SweepHFSS3DLayout
from pyaedt.modules.SolveSweeps import SweepMatrix
from pyaedt.modules.SolveSweeps import identify_setup


class CommonSetup(PropsManager, object):
    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        self.auto_update = False
        self._app = None
        self.p_app = app
        if solution_type is None:
            self.setuptype = self.p_app.design_solutions.default_setup
        elif isinstance(solution_type, int):
            self.setuptype = solution_type
        elif solution_type in SetupKeys.SetupNames:
            self.setuptype = SetupKeys.SetupNames.index(solution_type)
        else:
            self.setuptype = self.p_app.design_solutions._solution_options[solution_type]["default_setup"]
        self._name = name
        self.props = {}
        self.sweeps = []
        self._init_props(is_new_setup)
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

    @pyaedt_function_handler(num_cores="cores", num_tasks="tasks", num_gpu="gpus")
    def analyze(
        self,
        cores=1,
        tasks=1,
        gpus=0,
        acf_file=None,
        use_auto_settings=True,
        solve_in_batch=False,
        machine="localhost",
        run_in_thread=False,
        revert_to_initial_mesh=False,
        blocking=True,
    ):
        """Solve the active design.

        Parameters
        ----------
        cores : int, optional
            Number of simulation cores. The default is ``1``.
        tasks : int, optional
            Number of simulation tasks. The default is ``1``.
        gpus : int, optional
            Number of simulation graphic processing units to use. The default is ``0``.
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
        blocking : bool, optional
            Whether to block script while analysis is completed or not. It works from AEDT 2023 R2.
            Default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.Analyze
        """
        self._app.analyze(
            name=self.name,
            cores=cores,
            tasks=tasks,
            gpus=gpus,
            acf_file=acf_file,
            use_auto_settings=use_auto_settings,
            solve_in_batch=solve_in_batch,
            machine=machine,
            run_in_thread=run_in_thread,
            revert_to_initial_mesh=revert_to_initial_mesh,
            blocking=blocking,
        )

    @pyaedt_function_handler()
    def _init_props(self, is_new_setup=False):
        if is_new_setup:
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
            except Exception:
                self.props = SetupProps(self, OrderedDict())

    @property
    def is_solved(self):
        """Verify if solutions are available for given setup.

        Returns
        -------
        bool
            ``True`` if solutions are available, ``False`` otherwise.
        """
        if self.p_app.design_solutions.default_adaptive:
            expressions = [
                i
                for i in self.p_app.post.available_report_quantities(
                    solution="{} : {}".format(self.name, self.p_app.design_solutions.default_adaptive)
                )
            ]
            sol = self.p_app.post.reports_by_category.standard(
                expressions=expressions[0],
                setup="{} : {}".format(self.name, self.p_app.design_solutions.default_adaptive),
            )
        else:
            expressions = [i for i in self.p_app.post.available_report_quantities(solution=self.name)]
            sol = self.p_app.post.reports_by_category.standard(expressions=expressions[0], setup=self.name)
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
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.props["Name"] = name

    @pyaedt_function_handler(sweep_name="sweep")
    def get_solution_data(
        self,
        expressions=None,
        domain=None,
        variations=None,
        primary_sweep_variable=None,
        report_category=None,
        context=None,
        polyline_points=1001,
        math_formula=None,
        sweep=None,
    ):
        """Get a simulation result from a solved setup and cast it in a ``SolutionData`` object.
        Data to be retrieved from Electronics Desktop are any simulation results available in that
        specific simulation context.
        Most of the argument have some defaults which works for most of the ``Standard`` report quantities.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. Example is value ``"dB(S(1,1))"`` or a list of values.
            Default is `None` which will return all traces.
        domain : str, optional
            Plot Domain. Options are "Sweep" for frequency domain related results and "Time" for transient related data.
        variations : dict, optional
            Dictionary of all families including the primary sweep.
            The default is ``None`` which will use the nominal variations of the setup.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"None"`` which, depending on the context,
            will internally assign the primary sweep to:
            1. ``Freq`` for frequency domain results,
            2. ``Time`` for transient results,
            3. ``Theta`` for radiation patterns,
            4. ``distance`` for field plot over a polyline.
        report_category : str, optional
            Category of the Report to be created. If `None` default data Report will be used.
            The Report Category can be one of the types available for creating a report depend on the simulation setup.
            For example for a Far Field Plot in HFSS the UI shows the report category as "Create Far Fields Report".
            The report category will be in this case "Far Fields".
            Depending on the setup different categories are available.
            If `None` default category will be used (the first item in the Results drop down menu in AEDT).
            To get the list of available categories user can use method ``available_report_types``.
        context : str, dict, optional
            This is the context of the report.
            The default is ``None``. It can be:
            1. `None`
            2. Infinite Sphere name for Far Fields Plot.
            3. Dictionary. If dictionary is passed, key is the report property name and value is property value.
        polyline_points : int, optional
            Number of points on which to create the report for plots on polylines.
            This parameter is valid for ``Fields`` plot only.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        sweep : str, optional
            Name of the sweep adaptive setup to get solutions from. the default is ``LastAdaptive``.

        Returns
        -------
        :class:`pyaedt.modules.solutions.SolutionData`
            Solution Data object.

        References
        ----------

        >>> oModule.GetSolutionDataPerVariation

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> aedtapp.post.create_report("dB(S(1,1))")

        >>> variations = aedtapp.available_variations.nominal_w_values_dict
        >>> variations["Theta"] = ["All"]
        >>> variations["Phi"] = ["All"]
        >>> variations["Freq"] = ["30GHz"]
        >>> data1 = aedtapp.post.get_solution_data("GainTotal", aedtapp.nominal_adaptive,
        ...                                        variations=variations, primary_sweep_variable="Phi",
        ...                                        report_category="Far Fields", context="3D")

        >>> data2 =aedtapp.post.get_solution_data("S(1,1)",aedtapp.nominal_sweep,variations=variations)
        >>> data2.plot()

        >>> from pyaedt import Maxwell2d
        >>> maxwell_2d = Maxwell2d()
        >>> data3 = maxwell_2d.post.get_solution_data("InputCurrent(PHA)",domain="Time",primary_sweep_variable="Time")
        >>> data3.plot("InputCurrent(PHA)")

        >>> from pyaedt import Circuit
        >>> circuit = Circuit()
        >>> context = {"algorithm": "FFT", "max_frequency": "100MHz", "time_stop": "2.5us", "time_start": "0ps"}
        >>> spectralPlotData = circuit.post.get_solution_data(expressions="V(Vprobe1)", domain="Spectral",
        ...                                                   primary_sweep_variable="Spectrum", context=context)
        """
        if sweep:
            setup_sweep_name = [
                i for i in self._app.existing_analysis_sweeps if self.name == i.split(" : ")[0] and sweep in i
            ]
        else:
            setup_sweep_name = [i for i in self._app.existing_analysis_sweeps if self.name == i.split(" : ")[0]]
        if setup_sweep_name:
            return self._app.post.get_solution_data(
                expressions=expressions,
                domain=domain,
                variations=variations,
                primary_sweep_variable=primary_sweep_variable,
                report_category=report_category,
                context=context,
                polyline_points=polyline_points,
                math_formula=math_formula,
                setup_sweep_name=sweep,
            )
        return None

    @pyaedt_function_handler(sweep_name="sweep", plotname="name")
    def create_report(
        self,
        expressions=None,
        domain="Sweep",
        variations=None,
        primary_sweep_variable=None,
        secondary_sweep_variable=None,
        report_category=None,
        plot_type="Rectangular Plot",
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        name=None,
        sweep=None,
    ):
        """Create a report in AEDT. It can be a 2D plot, 3D plot, polar plot, or data table.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. Example is value = ``"dB(S(1,1))"``.
        domain : str, optional
            Plot Domain. Options are "Sweep", "Time", "DCIR".
        variations : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}``.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"Freq"``.
        secondary_sweep_variable : str, optional
            Name of the secondary sweep variable in 3D Plots.
        report_category : str, optional
            Category of the Report to be created. If `None` default data Report will be used.
            The Report Category can be one of the types available for creating a report depend on the simulation setup.
            For example for a Far Field Plot in HFSS the UI shows the report category as "Create Far Fields Report".
            The report category will be in this case "Far Fields".
            Depending on the setup different categories are available.
            If `None` default category will be used (the first item in the Results drop down menu in AEDT).
        plot_type : str, optional
            The format of Data Visualization. Default is ``Rectangular Plot``.
        context : str, optional
            The default is ``None``. It can be `None`, `"Differential Pairs"`,`"RL"`,
            `"Sources"`, `"Vias"`,`"Bondwires"`, `"Probes"` for Hfss3dLayout or
            Reduce Matrix Name for Q2d/Q3d solution or Infinite Sphere name for Far Fields Plot.
        name : str, optional
            Name of the plot. The default is ``None``.
        polyline_points : int, optional,
            Number of points for creating the report for plots on polylines.
        subdesign_id : int, optional
            Specify a subdesign ID to export a Touchstone file of this subdesign to.
            This parameter is valid only for a circuit.
            The default value is ``None``.
        context : str, optional
        sweep : str, optional
            Name of the sweep adaptive setup to get solutions from. The default is ``LastAdaptive``.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`
            ``True`` when successful, ``False`` when failed.


        References
        ----------

        >>> oModule.CreateReport

        Examples
        --------
        >>> from pyaedt import Circuit
        >>> aedtapp = Circuit()
        >>> aedtapp.post.create_report("dB(S(1,1))")

        >>> variations = aedtapp.available_variations.nominal_w_values_dict
        >>> aedtapp.post.setups[0].create_report("dB(S(1,1))",variations=variations,primary_sweep_variable="Freq")

        >>> aedtapp.post.create_report("S(1,1)",variations=variations,plot_type="Smith Chart")
        """
        if sweep:
            setup_sweep_name = [
                i for i in self._app.existing_analysis_sweeps if self.name == i.split(" : ")[0] and sweep in i
            ]
        else:
            setup_sweep_name = [i for i in self._app.existing_analysis_sweeps if self.name == i.split(" : ")[0]]
        if setup_sweep_name:
            return self._app.post.create_report(
                expressions=expressions,
                domain=domain,
                variations=variations,
                primary_sweep_variable=primary_sweep_variable,
                secondary_sweep_variable=secondary_sweep_variable,
                report_category=report_category,
                plot_type=plot_type,
                context=context,
                polyline_points=polyline_points,
            )
        return None


class Setup(CommonSetup):
    """Initializes, creates, and updates a 3D setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis.Analysis`
        Inherited app object.
    solution_type : int, str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        CommonSetup.__init__(self, app, solution_type, name, is_new_setup)

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

    @pyaedt_function_handler(update_dictionary="properties")
    def update(self, properties=None):
        """Update the setup based on either the class argument or a dictionary.

        Parameters
        ----------
        properties : optional
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
        if properties:
            for el in properties:
                self.props[el] = properties[el]
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

        self._app.delete_setup(self.name)
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
                name = name.replace(":", "_")
                name = name.replace(",", "_")
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
        use_cache_for_pass=True,
        use_cache_for_freq=True,
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
        use_cache_for_pass : bool, optional
            Use cache for pass.
            Default value is ``True``.
        use_cache_for_freq : bool, optional
            Use cache for frequency.
            Default value is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["NAME:" + self.name]
        self.props["UseCacheFor"] = []
        if use_cache_for_pass:
            self.props["UseCacheFor"].append("Pass")
        if use_cache_for_freq:
            self.props["UseCacheFor"].append("Freq")
        _dict2arg(self.props, arg)
        expression_cache = self._expression_cache(
            expressions, report_type, intrinsics, isconvergence, isrelativeconvergence, conv_criteria
        )
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler(setup_name="name")
    def enable(self, name=None):
        """Enable a setup.

        Parameters
        ----------
        name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not name:
            name = self.name

        self.omodule.EditSetup(name, ["NAME:" + name, "IsEnabled:=", True])
        return True

    @pyaedt_function_handler(setup_name="name")
    def disable(self, name=None):
        """Disable a setup.

        Parameters
        ----------
        name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not name:
            name = self.name

        self.omodule.EditSetup(name, ["NAME:" + name, "IsEnabled:", False])
        return True

    @pyaedt_function_handler(
        design_name="design", solution_name="solution", parameters_dict="parameters", project_name="project"
    )
    def add_mesh_link(
        self,
        design,
        solution=None,
        parameters=None,
        project="This Project*",
        force_source_to_solve=True,
        preserve_partner_solution=True,
        apply_mesh_operations=True,
        adapt_port=True,
    ):
        """Add a mesh link to another design.

        Parameters
        ----------
        design : str
            Name of the design.
        solution : str, optional
            Name of the solution in the format ``"setup_name : solution_name"``.
            If ``None``, the default value is ``setup_name : LastAdaptive``.
        parameters : dict, optional
            Dictionary of the parameters.
            If ``None``, the default is `appname.available_variations.nominal_w_values_dict`.
        project : str, optional
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
            if not design or design is None:
                raise ValueError("Provide design name to add mesh link to.")
            elif design not in self.p_app.design_list:
                raise ValueError("Design does not exist in current project.")
            else:
                meshlinks["Design"] = design
            # project name
            if project != "This Project*":
                if os.path.exists(project):
                    meshlinks["Project"] = project
                    meshlinks["PathRelativeTo"] = "SourceProduct"
                else:
                    raise ValueError("Project file path provided does not exist.")
            else:
                meshlinks["Project"] = project
                meshlinks["PathRelativeTo"] = "TargetProject"
            # if self.p_app.solution_type == "SBR+":
            meshlinks["ImportMesh"] = True
            # solution name
            if solution is None:
                meshlinks["Soln"] = "{} : LastAdaptive".format(
                    self.p_app.oproject.GetDesign(design).GetChildObject("Analysis").GetChildNames()[0]
                )
            elif (
                solution.split()[0] in self.p_app.oproject.GetDesign(design).GetChildObject("Analysis").GetChildNames()
            ):
                meshlinks["Soln"] = "{} : LastAdaptive".format(solution.split()[0])
            else:
                raise ValueError("Setup does not exist in current design.")
            # parameters
            meshlinks["Params"] = OrderedDict({})
            if parameters is None:
                parameters = self.p_app.available_variations.nominal_w_values_dict
                for el in parameters:
                    meshlinks["Params"][el] = el
            else:
                for el in parameters:
                    if el in list(self._app.available_variations.nominal_w_values_dict.keys()):
                        meshlinks["Params"][el] = el
                    else:
                        meshlinks["Params"][el] = parameters[el]
            meshlinks["ForceSourceToSolve"] = force_source_to_solve
            meshlinks["PreservePartnerSoln"] = preserve_partner_solution
            meshlinks["ApplyMeshOp"] = apply_mesh_operations
            if self.p_app.design_type != "Maxwell 2D" or self.p_app.design_type != "Maxwell 3D":
                meshlinks["AdaptPort"] = adapt_port
            self.update()
            self.auto_update = auto_update
            return True
        except Exception:
            self.auto_update = auto_update
            return False

    @pyaedt_function_handler(
        design_name="design", solution_name="solution", parameters_dict="parameters", project_name="project"
    )
    def start_continue_from_previous_setup(
        self,
        design,
        solution,
        map_variables_by_name=True,
        parameters=None,
        project="This Project*",
        force_source_to_solve=True,
        preserve_partner_solution=True,
    ):
        """Start or continue from a previously solved setup.

        Parameters
        ----------
        design : str
            Name of the design.
        solution : str, optional
            Name of the solution in the format ``"setup_name : solution_name"``.
            For example, ``"Setup1 : Transient", "MySetup : LastAdaptive"``.
        map_variables_by_name : bool, optional
            Whether variables are mapped by name from the source design. The default is
            ``True``.
        parameters : dict, optional
            Dictionary of the parameters. This parameter is not considered if
            ``map_variables_by_name=True``. If ``None``, the default is
            ``appname.available_variations.nominal_w_values_dict``.
        project : str, optional
            Name of the project with the design. The default is ``"This Project*"``.
            However, you can supply the full path and name to another project.
        force_source_to_solve : bool, optional
            The default is ``True``.
        preserve_partner_solution : bool, optional
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup

        Examples
        --------
        >>> m2d = pyaedt.Maxwell2d()
        >>> setup = m2d.get_setup("Setup1")
        >>> setup.start_continue_from_previous_setup(design="IM",solution="Setup1 : Transient")

        """

        auto_update = self.auto_update
        try:
            self.auto_update = False

            # parameters
            params = OrderedDict({})
            if map_variables_by_name:
                parameters = self.p_app.available_variations.nominal_w_values_dict
                for k, v in parameters.items():
                    params[k] = k
            elif parameters is None:
                parameters = self.p_app.available_variations.nominal_w_values_dict
                for k, v in parameters.items():
                    params[k] = v
            else:
                for k, v in parameters.items():
                    if k in list(self._app.available_variations.nominal_w_values_dict.keys()):
                        params[k] = v
                    else:
                        params[k] = parameters[v]

            prev_solution = OrderedDict({})

            # project name
            if project != "This Project*":
                if os.path.exists(project):
                    prev_solution["Project"] = project
                    self.props["PathRelativeTo"] = "SourceProduct"
                else:
                    raise ValueError("Project file path provided does not exist.")
            else:
                prev_solution["Project"] = project
                self.props["PathRelativeTo"] = "TargetProject"

            # design name
            if not design or design is None:
                raise ValueError("Provide design name to add mesh link to.")
            elif design not in self.p_app.design_list:
                raise ValueError("Design does not exist in current project.")
            else:
                prev_solution["Design"] = design

            # solution name
            if solution:
                prev_solution["Soln"] = solution
            else:
                raise ValueError("Provide a valid solution name.")

            self.props["PrevSoln"] = prev_solution

            self.props["PrevSoln"]["Params"] = params
            self.props["ForceSourceToSolve"] = force_source_to_solve
            self.props["PreservePartnerSoln"] = preserve_partner_solution

            self.props["IsGeneralTransient"] = True
            if self.props["IsHalfPeriodicTransient"]:
                raise UserWarning(
                    "Half periodic TDM disabled because it is not "
                    "supported with start/continue from a previously solved setup."
                )

            self.update()
            self.auto_update = auto_update
            return True
        except Exception:
            self.auto_update = auto_update
            return False


class SetupCircuit(CommonSetup):
    """Manages a circuit setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`
        Inherited app object.
    solution_type : str, int
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
      Whether to create the setup from a template. The default is ``True.``
      If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        CommonSetup.__init__(self, app, solution_type, name, is_new_setup)

    @pyaedt_function_handler(isnewsetup="is_new_setup")
    def _init_props(self, is_new_setup=False):
        props = {}
        if is_new_setup:
            setup_template = SetupKeys.get_setup_templates()[self.setuptype]
            self.props = SetupProps(self, setup_template)
        else:
            self.props = SetupProps(self, OrderedDict())
            try:
                setups_data = self.p_app.design_properties["SimSetups"]["SimSetup"]
                if not isinstance(setups_data, list):
                    setups_data = [setups_data]
                for setup in setups_data:
                    if self.name == setup["Name"]:
                        setup_data = setup
                        setup_data.pop("Sweeps", None)
                        self.props = SetupProps(self, setup_data)
            except Exception:
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

    @pyaedt_function_handler(update_dictionary="properties")
    def update(self, properties=None):
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        properties : dict, optional
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
        if properties:
            for el in properties:
                self.props[el] = properties[el]
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

    @pyaedt_function_handler(start_point="start", end_point="stop")
    def add_sweep_count(
        self,
        sweep_variable="Freq",
        start=1,
        stop=100,
        count=100,
        units="GHz",
        count_type="Linear",
        override_existing_sweep=True,
    ):
        """Add a step sweep to existing Circuit Setup. It can be ``"Linear"``, ``"Decade"`` or ``"Octave"``.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable that the sweep belongs to. The default is ``"Freq``.
        start : float or str, optional
            Start point of the linear count sweep. The default is ``1``.
            If a string ``str`` is specified, no units are applied.
        stop : float or str, optional
            End point of the linear count sweep. The default is ``100``.
            If a string is specified, no units are applied.
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
        if isinstance(start, (int, float)):
            start = str(start) + units
        if isinstance(stop, (int, float)):
            stop = str(stop) + units
        lin_in = "LINC"
        if count_type.lower() == "decade":
            lin_in = "DEC"
        elif count_type.lower() == "octave":
            lin_in = "OCT"
        lin_data = "{} {} {} {}".format(lin_in, start, stop, count)
        return self._add_sweep(sweep_variable, lin_data, override_existing_sweep)

    @pyaedt_function_handler(start_point="start", end_point="stop")
    def add_sweep_step(
        self,
        sweep_variable="Freq",
        start=1,
        stop=100,
        step_size=1,
        units="GHz",
        override_existing_sweep=True,
    ):
        """Add a linear count sweep to existing Circuit Setup.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        start : float or str, optional
            Start point of the linear count sweep. The default is ``1``.
            If a string ``str`` is specified, no units are applied.
        stop : float or str, optional
            End point of the linear count sweep. The default is ``100``.
            If a string is specified, no units are applied.
        step_size :  float or str, optional
            Step size of the sweep. The default is ``1``.
            If a string is specified, no units are applied.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point.
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
        if isinstance(start, (int, float)):
            start = str(start) + units
        if isinstance(stop, (int, float)):
            stop = str(stop) + units
        if isinstance(step_size, (int, float)):
            step_size = str(step_size) + units
        linc_data = "LIN {} {} {}".format(start, stop, step_size)
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

    @pyaedt_function_handler(setup_name="name")
    def enable(self, name=None):
        """Enable a setup.

        Parameters
        ----------
        name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not name:
            name = self.name
        self._odesign.EnableSolutionSetup(name, True)
        return True

    @pyaedt_function_handler(setup_name="name")
    def disable(self, name=None):
        """Disable a setup.

        Parameters
        ----------
        name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not name:
            name = self.name
        self._odesign.EnableSolutionSetup(name, False)
        return True

    @pyaedt_function_handler()
    def get_solution_data(
        self,
        expressions=None,
        domain=None,
        variations=None,
        primary_sweep_variable=None,
        report_category=None,
        context=None,
        polyline_points=1001,
        math_formula=None,
        sweep=None,
    ):
        """Get a simulation result from a solved setup and cast it in a ``SolutionData`` object.
        Data to be retrieved from Electronics Desktop are any simulation results available in that
        specific simulation context.
        Most of the argument have some defaults which works for most of the ``Standard`` report quantities.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. Example is value ``"dB(S(1,1))"`` or a list of values.
            Default is `None` which will return all traces.
        domain : str, optional
            Plot Domain. Options are "Sweep" for frequency domain related results and "Time" for transient related data.
        variations : dict, optional
            Dictionary of all families including the primary sweep.
            The default is ``None`` which will use the nominal variations of the setup.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"None"`` which, depending on the context,
            will internally assign the primary sweep to:
            1. ``Freq`` for frequency domain results,
            2. ``Time`` for transient results,
            3. ``Theta`` for radiation patterns,
            4. ``distance`` for field plot over a polyline.
        report_category : str, optional
            Category of the Report to be created. If `None` default data Report will be used.
            The Report Category can be one of the types available for creating a report depend on the simulation setup.
            For example for a Far Field Plot in HFSS the UI shows the report category as "Create Far Fields Report".
            The report category will be in this case "Far Fields".
            Depending on the setup different categories are available.
            If `None` default category will be used (the first item in the Results drop down menu in AEDT).
            To get the list of available categories user can use method ``available_report_types``.
        context : str, dict, optional
            This is the context of the report.
            The default is ``None``. It can be:
            1. `None`
            2. ``"Differential Pairs"``
            3. Reduce Matrix Name for Q2d/Q3d solution
            4. Infinite Sphere name for Far Fields Plot.
            5. Dictionary. If dictionary is passed, key is the report property name and value is property value.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        polyline_points : int, optional
            Number of points on which to create the report for plots on polylines.
            This parameter is valid for ``Fields`` plot only.
        sweep : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.


        Returns
        -------
        :class:`pyaedt.modules.solutions.SolutionData`
            Solution Data object.

        References
        ----------

        >>> oModule.GetSolutionDataPerVariation
        """
        return self._app.post.get_solution_data(
            expressions=expressions,
            domain=domain,
            variations=variations,
            primary_sweep_variable=primary_sweep_variable,
            report_category=report_category,
            context=context,
            polyline_points=polyline_points,
            math_formula=math_formula,
            sweep=sweep,
        )

    @pyaedt_function_handler()
    def create_report(
        self,
        expressions=None,
        domain="Sweep",
        variations=None,
        primary_sweep_variable=None,
        secondary_sweep_variable=None,
        report_category=None,
        plot_type="Rectangular Plot",
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        name=None,
    ):
        """Create a report in AEDT. It can be a 2D plot, 3D plot, polar plots or data tables.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. Example is value = ``"dB(S(1,1))"``.
        domain : str, optional
            Plot Domain. Options are "Sweep", "Time", "DCIR".
        variations : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}``.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"Freq"``.
        secondary_sweep_variable : str, optional
            Name of the secondary sweep variable in 3D Plots.
        report_category : str, optional
            Category of the Report to be created. If `None` default data Report will be used.
            The Report Category can be one of the types available for creating a report depend on the simulation setup.
            For example for a Far Field Plot in HFSS the UI shows the report category as "Create Far Fields Report".
            The report category will be in this case "Far Fields".
            Depending on the setup different categories are available.
            If `None` default category will be used (the first item in the Results drop down menu in AEDT).
        plot_type : str, optional
            The format of Data Visualization. Default is ``Rectangular Plot``.
        context : str, optional
            The default is ``None``. It can be `None`, `"Differential Pairs"`,`"RL"`,
            `"Sources"`, `"Vias"`,`"Bondwires"`, `"Probes"` for Hfss3dLayout or
            Reduce Matrix Name for Q2d/Q3d solution or Infinite Sphere name for Far Fields Plot.
        name : str, optional
            Name of the plot. The default is ``None``.
        polyline_points : int, optional,
            Number of points for creating the report for plots on polylines.
        subdesign_id : int, optional
            Specify a subdesign ID to export a Touchstone file of this subdesign. Valid for Circuit Only.
            The default value is ``None``.
        context : str, optional

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`
            ``True`` when successful, ``False`` when failed.


        References
        ----------

        >>> oModule.CreateReport
        """
        return self._app.post.create_report(
            expressions=expressions,
            domain=domain,
            variations=variations,
            primary_sweep_variable=primary_sweep_variable,
            secondary_sweep_variable=secondary_sweep_variable,
            report_category=report_category,
            plot_type=plot_type,
            context=context,
            subdesign_id=subdesign_id,
            polyline_points=polyline_points,
        )


class Setup3DLayout(CommonSetup):
    """Initializes, creates, and updates a 3D Layout setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3DLayout.FieldAnalysis3DLayout`
        Inherited app object.
    solution_type : int or str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True.``
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        CommonSetup.__init__(self, app, solution_type, name, is_new_setup)

    @pyaedt_function_handler(isnewsetup="is_new_setup")
    def _init_props(self, is_new_setup=False):
        if is_new_setup:
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
            except Exception:
                self.props = SetupProps(self, OrderedDict())
                settings.logger.error("Unable to set props.")

    @property
    def is_solved(self):
        """Verify if solutions are available for a given setup.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        if self.props.get("SolveSetupType", "HFSS") == "HFSS":
            combined_name = "{} : Last Adaptive".format(self.name)
            expressions = [i for i in self.p_app.post.available_report_quantities(solution=combined_name)]
            sol = self._app.post.reports_by_category.standard(expressions=expressions[0], setup=combined_name)
        elif self.props.get("SolveSetupType", "HFSS") == "SIwave":
            combined_name = "{} : {}".format(self.name, self.sweeps[0].name)
            expressions = [i for i in self.p_app.post.available_report_quantities(solution=combined_name)]
            sol = self._app.post.reports_by_category.standard(expressions=expressions[0], setup=combined_name)
        elif self.props.get("SolveSetupType", "HFSS") == "SIwaveDCIR":
            expressions = self.p_app.post.available_report_quantities(solution=self.name, is_siwave_dc=True)
            sol = self._app.post.reports_by_category.standard(expressions=expressions[0], setup=self.name)
        else:
            expressions = [i for i in self.p_app.post.available_report_quantities(solution=self.name)]

            sol = self._app.post.reports_by_category.standard(expressions=expressions[0], setup=self.name)
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

    @pyaedt_function_handler(update_dictionary="properties")
    def update(self, properties=None):
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        properties : dict, optional
            Dictionary of settings to apply.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Edit
        """
        if properties:
            for el in properties:
                self.props._setitem_without_update(el, properties[el])
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

    @pyaedt_function_handler(file_fullname="output_file")
    def export_to_hfss(self, output_file, keep_net_name=False):
        """Export the HFSS 3D Layout design to an HFSS 3D design.

        This method is not supported with IronPython.

        Parameters
        ----------
        output_file : str
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

        output_file = output_file
        if not os.path.isdir(os.path.dirname(output_file)):
            return False
        output_file = os.path.splitext(output_file)[0] + ".aedt"
        info_messages = list(self.p_app.odesktop.GetMessages(self.p_app.project_name, self.p_app.design_name, 0))
        error_messages = list(self.p_app.odesktop.GetMessages(self.p_app.project_name, self.p_app.design_name, 2))
        self.omodule.ExportToHfss(self.name, output_file)
        succeeded = self._check_export_log(info_messages, error_messages, output_file)
        if succeeded and keep_net_name:
            if not is_ironpython:
                from pyaedt import Hfss

                self._get_net_names(Hfss, output_file)
            else:
                self.p_app.logger.error("Exporting layout while keeping net name is not supported with IronPython")
        return succeeded

    @pyaedt_function_handler()
    def _get_net_names(self, app, file_fullname):
        primitives_3d_pts_per_nets = self._get_primitives_points_per_net()
        self.p_app.logger.info("Processing vias...")
        via_per_nets = self._get_via_position_per_net()
        self.p_app.logger.info("Vias processing completed.")
        layers_elevation = {
            lay.name: lay.lower_elevation + lay.thickness / 2
            for lay in list(self.p_app.modeler.edb.stackup.signal_layers.values())
        }
        aedtapp = app(projectname=file_fullname)
        units = aedtapp.modeler.model_units
        aedt_units = AEDT_UNITS["Length"][units]
        self._convert_edb_to_aedt_units(input_dict=primitives_3d_pts_per_nets, output_unit=aedt_units)
        self._convert_edb_to_aedt_units(input_dict=via_per_nets, output_unit=aedt_units)
        self._convert_edb_layer_elevation_to_aedt_units(input_dict=layers_elevation, output_units=aedt_units)
        metal_object = [
            obj.name
            for obj in aedtapp.modeler.solid_objects
            if not obj.material_name in aedtapp.modeler.materials.dielectrics
        ]
        for net, positions in primitives_3d_pts_per_nets.items():
            object_names = []
            for position in positions:
                aedtapp_objs = [p for p in aedtapp.modeler.get_bodynames_from_position(position) if p in metal_object]
                object_names.extend(aedtapp_objs)
            if net in via_per_nets:
                for via_pos in via_per_nets[net]:
                    object_names.extend(
                        [
                            p
                            for p in aedtapp.modeler.get_bodynames_from_position(via_pos, None, False)
                            if p in metal_object
                        ]
                    )

                    for lay_el in list(layers_elevation.values()):
                        pad_pos = via_pos[:2]
                        pad_pos.append(lay_el)
                        object_names.extend(
                            [
                                p
                                for p in aedtapp.modeler.get_bodynames_from_position(pad_pos, None, False)
                                if p in metal_object
                            ]
                        )

            net = net.replace(".", "_")
            net = net.replace("-", "m")
            net = net.replace("+", "p")
            net_name = re.sub("[^a-zA-Z0-9 .\n]", "_", net)
            self.p_app.logger.info("Renaming primitives for net {}...".format(net_name))
            object_names = list(set(object_names))
            if len(object_names) == 1:

                object_p = aedtapp.modeler[object_names[0]]
                object_p.name = net_name
                object_p.color = [randrange(255), randrange(255), randrange(255)]  # nosec
            elif len(object_names) > 1:
                united_object = aedtapp.modeler.unite(object_names, purge=True)
                obj_ind = aedtapp.modeler.objects[united_object].id
                if obj_ind:
                    aedtapp.modeler.objects[obj_ind].name = net_name
                    aedtapp.modeler.objects[obj_ind].color = [randrange(255), randrange(255), randrange(255)]  # nosec

        if aedtapp.design_type == "Q3D Extractor":
            aedtapp.auto_identify_nets()
        aedtapp.close_project(save_project=True)

    @pyaedt_function_handler()
    def _get_primitives_points_per_net(self):
        edb = self.p_app.modeler.edb
        if not edb:
            return
        net_primitives = edb.modeler.primitives_by_net
        primitive_dict = {}
        layers_elevation = {
            lay.name: lay.lower_elevation + lay.thickness / 2
            for lay in list(self.p_app.modeler.edb.stackup.signal_layers.values())
        }
        for net, primitives in net_primitives.items():
            primitive_dict[net] = []
            self.p_app.logger.info("Processing net {}...".format(net))
            for prim in primitives:

                if prim.layer_name not in layers_elevation:
                    continue
                z = layers_elevation[prim.layer_name]
                if "EdbPath" in str(prim):
                    points = list(prim.center_line.Points)
                    pt = [points[0].X.ToDouble(), points[0].Y.ToDouble()]
                    pt.append(z)
                    next_p = int(len(points) / 4)
                    pt = [points[next_p].X.ToDouble(), points[next_p].Y.ToDouble()]
                    pt.append(z)
                    primitive_dict[net].append(pt)

                elif "EdbPolygon" in str(prim):
                    pdata_orig = prim.polygon_data.edb_api
                    pdata = self.p_app.modeler.edb._edb.Geometry.PolygonData.CreateFromArcs(
                        pdata_orig.GetArcData(), True
                    )

                    pdata.Scale(0.99, pdata.GetBoundingCircleCenter())
                    points = [[], []]
                    for point in list(pdata.Points):
                        points[0].append(point.X.ToDouble())
                        points[1].append(point.Y.ToDouble())
                    # points = prim.points()
                    pt = [points[0][0], points[1][0]]
                    pt.append(z)
                    primitive_dict[net].append(pt)
                    next_p = int(len(points[0]) / 4)
                    pt = [points[0][next_p], points[1][next_p]]
                    pt.append(z)
                    primitive_dict[net].append(pt)
                    next_p = int(len(points[0]) / 2)
                    pt = [points[0][next_p], points[1][next_p]]
                    pt.append(z)
                    primitive_dict[net].append(pt)

                else:
                    n = 0
                    while n < 1000:
                        n += 10
                        pt = self._get_point_inside_primitive(prim, n)
                        if pt:
                            pt.append(z)
                            primitive_dict[net].append(pt)
                            break
        self.p_app.logger.info("Net processing completed.")
        return primitive_dict

    @pyaedt_function_handler()
    def _get_point_inside_primitive(self, primitive, n):
        from pyaedt.modeler.geometry_operators import GeometryOperators

        if not is_ironpython:
            import numpy as np
        else:
            return False
        bbox = primitive.bbox
        primitive_x_points = []
        primitive_y_points = []
        for arc in primitive.arcs:
            if len(arc.points) == 2:
                primitive_x_points += arc.points[0]
                primitive_y_points += arc.points[1]
        dx = (bbox[2] - bbox[0]) / n
        dy = (bbox[3] - bbox[1]) / n
        xcoords = [i for i in np.arange(bbox[0], bbox[2], dx)]
        ycoords = [i for i in np.arange(bbox[1], bbox[3], dy)]
        for x in xcoords:
            for y in ycoords:
                if GeometryOperators.point_in_polygon([x, y], [primitive_x_points, primitive_y_points]) == 1:
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
        if not self.p_app.modeler.edb:
            return
        via_list = list(self.p_app.modeler.edb.padstacks.instances.values())
        if via_list:
            for net in list(self.p_app.modeler.edb.nets.nets.keys()):
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
    def _check_export_log(self, info_messages, error_messages, file_fullname):
        run = True
        succeeded = False
        while run:
            info_messages_n = list(self.p_app.odesktop.GetMessages(self.p_app.project_name, self.p_app.design_name, 0))
            error_messages_n = list(self.p_app.odesktop.GetMessages(self.p_app.project_name, self.p_app.design_name, 2))
            infos = [i for i in info_messages_n if i not in info_messages]
            if infos:
                for info in infos:
                    if "Export complete" in info:
                        succeeded = True
                    self.p_app.logger.info(info)
                info_messages.extend(info_messages_n)
                if succeeded:
                    break
            elif os.path.exists(file_fullname):
                succeeded = True
                break
            infos_errors = [i for i in error_messages_n if i not in error_messages]
            if infos_errors:
                for message in infos_errors:
                    self.p_app.logger.error(message)
                break
            time.sleep(2)
        return succeeded

    @pyaedt_function_handler(file_fullname="output_file")
    def export_to_q3d(self, output_file, keep_net_name=False):
        """Export the HFSS 3D Layout design to a Q3D design.

        Parameters
        ----------
        output_file : str
            Full path and file name for exporting the project.
        keep_net_name : bool
            Whether to keep the net name in the 3D export, The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        keep_net_name : bool
            Keep net name in 3D export when ``True`` or by default when ``False``. Default value is ``False``.

        References
        ----------

        >>> oModule.ExportToQ3d
        """

        if not os.path.isdir(os.path.dirname(output_file)):
            return False
        output_file = os.path.splitext(output_file)[0] + ".aedt"
        if os.path.exists(output_file):
            os.unlink(output_file)
        info_messages = list(self.p_app.odesktop.GetMessages(self.p_app.project_name, self.p_app.design_name, 0))
        error_messages = list(self.p_app.odesktop.GetMessages(self.p_app.project_name, self.p_app.design_name, 2))
        self.omodule.ExportToQ3d(self.name, output_file)
        succeeded = self._check_export_log(info_messages, error_messages, output_file)
        if succeeded and keep_net_name:
            if not is_ironpython:
                from pyaedt import Q3d

                self._get_net_names(Q3d, output_file)
            else:
                self.p_app.logger.error("Exporting layout while keeping net name is not supported with IronPython.")
        return succeeded

    @pyaedt_function_handler(sweepname="name", sweeptype="sweep_type")
    def add_sweep(self, name=None, sweep_type="Interpolating"):
        """Add a frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``,
            ``"Interpolating"``, and ``"Discrete"``.
            The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS3DLayout`
            Sweep object.

        References
        ----------

        >>> oModule.AddSweep
        """
        if not name:
            name = generate_unique_name("Sweep")
        sweep_n = SweepHFSS3DLayout(self, name, sweep_type)
        if sweep_n.create():
            self.sweeps.append(sweep_n)
            return sweep_n
        return False

    @pyaedt_function_handler(sweepname="name")
    def get_sweep(self, name=None):
        """Return frequency sweep object of a given sweep.

        Parameters
        ----------
        name : str, optional
            Name of the sweep. The default is ``None``, in which case
            the first sweep is used.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS3DLayout`

        Examples
        --------
        >>> h3d = Hfss3dLayout()
        >>> setup = h3d.get_setup('Pyaedt_setup')
        >>> sweep = setup.get_sweep('Sweep1')
        >>> sweep.add_subrange("LinearCount",0,10,1,"Hz")
        >>> sweep.add_subrange("LogScale",10,1E8,100,"Hz")
        """
        if name:
            for sweep in self.sweeps:
                if name == sweep.name:
                    return sweep
        else:
            if self.sweeps:
                return self.sweeps[0]
        return False

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
    def export_to_json(self, file_path, overwrite=False):
        """Export all setup properties into a json file.

        Parameters
        ----------
        file_path : str
            File path of the json file.
        overwrite : bool, optional
            Whether to overwrite the file if it already exists.
        """
        if os.path.isfile(file_path):  # pragma no cover
            if not overwrite:  # pragma no cover
                settings.logger.error("File {} already exists. Configure file is not exported".format(file_path))
                return False
        return self.props._export_properties_to_json(file_path, overwrite=overwrite)


class SetupHFSS(Setup, object):
    """Initializes, creates, and updates an HFSS setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis.Analysis`
        Inherited app object.
    solution_type : int, str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        Setup.__init__(self, app, solution_type, name, is_new_setup)

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

    @pyaedt_function_handler(freqstart="start_frequency", freqstop="stop_frequency", sweepname="name")
    def create_frequency_sweep(
        self,
        unit=None,
        start_frequency=1.0,
        stop_frequency=10.0,
        num_of_freq_points=None,
        name=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
        interpolation_tol=0.5,
        interpolation_max_solutions=250,
    ):
        """Create a sweep with the specified number of points.

        Parameters
        ----------
        unit : str, optional
            Unit of the frequency.. The default is ``None``, in which case the default desktop units are used.
        start_frequency : float, str, optional
            Starting frequency of the sweep. The default is ``1.0``.
            If a unit is passed with number, such as ``"1MHz"``, the unit is ignored.
        stop_frequency : float, str, optional
            Stopping frequency of the sweep. The default is ``10.0``.
            If a unit is passed with number, such as ``"1MHz"`, the unit is ignored.
        num_of_freq_points : int
            Number of frequency points in the range. The default is ``401`` for
            a sweep type of ``"Interpolating"`` or ``"Fast"``. The default is ``5`` for a sweep
            type of ``"Discrete"``.
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
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
        >>> linear_count_sweep = setup.create_linear_count_sweep(,,
        >>> type(linear_count_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """

        # Set default values for num_of_freq_points if a value was not passed. Also,
        # check that sweep_type is valid.
        if sweep_type in ["Interpolating", "Fast"]:
            num_of_freq_points = num_of_freq_points or 401
        elif sweep_type == "Discrete":
            num_of_freq_points = num_of_freq_points or 5
        else:  # pragma: no cover
            raise ValueError("Invalid `sweep_type`. It has to be 'Discrete', 'Interpolating', or 'Fast'")

        if name is None:
            name = generate_unique_name("Sweep")

        if name in [sweep.name for sweep in self.sweeps]:
            oldname = name
            name = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, name)
        sweepdata = self.add_sweep(name, sweep_type)
        if not sweepdata:
            return False
        sweepdata.props["RangeType"] = "LinearCount"
        sweepdata.props["RangeStart"] = self.p_app.value_with_units(start_frequency, unit, "Frequency")
        sweepdata.props["RangeEnd"] = self.p_app.value_with_units(stop_frequency, unit, "Frequency")

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
        self._app.logger.info("Linear count sweep {} has been correctly created".format(name))
        return sweepdata

    @pyaedt_function_handler(freqstart="start_frequency", freqstop="stop_frequency", sweepname="name")
    def create_linear_step_sweep(
        self,
        unit="GHz",
        start_frequency=0.1,
        stop_frequency=2.0,
        step_size=0.05,
        name=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
    ):
        """Create a Sweep with a specified frequency step.

        Parameters
        ----------
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        start_frequency : float, optional
            Starting frequency of the sweep. The default is ``0.1``.
        stop_frequency : float, optional
            Stopping frequency of the sweep. The default is ``2.0``.
        step_size : float, optional
            Frequency size of the step. The default is ``0.05``.
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
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
        >>> linear_step_sweep = setup.create_linear_step_sweep(name="LinearStepSweep",
        ...                                                   unit="MHz", start_frequency=1.1e3,
        ...                                                   stop_frequency=1200.1, step_size=153.8)
        >>> type(linear_step_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to either 'Discrete', 'Interpolating', or 'Fast'")
        if name is None:
            name = generate_unique_name("Sweep")

        if name in [sweep.name for sweep in self.sweeps]:
            oldname = name
            name = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, name)
        sweepdata = self.add_sweep(name, sweep_type)
        if not sweepdata:
            return False
        sweepdata.props["RangeType"] = "LinearStep"
        sweepdata.props["RangeStart"] = str(start_frequency) + unit
        sweepdata.props["RangeEnd"] = str(stop_frequency) + unit
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
        self._app.logger.info("Linear step sweep {} has been correctly created".format(name))
        return sweepdata

    @pyaedt_function_handler(sweepname="name")
    def create_single_point_sweep(
        self,
        unit="GHz",
        freq=1,
        name=None,
        save_single_field=True,
        save_fields=False,
        save_rad_fields=False,
    ):
        """Create a Sweep with a single frequency point.

        Parameters
        ----------
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        freq : float, list
            Frequency of the single point or list of frequencies to create distinct single points.
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        save_single_field : bool, list, optional
            Whether to save the fields of the single point. The default is ``True``.
            If a list is specified, the length must be the same as the frequency length.
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
        >>> single_point_sweep = setup.create_single_point_sweep(name="SinglePointSweep", unit="MHz", freq=1.1e3)
        >>> type(single_point_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if name is None:
            name = generate_unique_name("SinglePoint")

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

        if name in [sweep.name for sweep in self.sweeps]:
            oldname = name
            name = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, name)
        sweepdata = self.add_sweep(name, "Discrete")
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
        self._app.logger.info("Single point sweep {} has been correctly created".format(name))
        return sweepdata

    @pyaedt_function_handler(sweepname="name", sweeptype="sweep_type")
    def add_sweep(self, name=None, sweep_type="Interpolating"):
        """Add a sweep to the project.

        Parameters
        ----------
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        sweep_type : str, optional
            Type of the sweep. The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or :class:`pyaedt.modules.SolveSweeps.SweepMatrix`
            Sweep object.

        References
        ----------

        >>> oModule.InsertFrequencySweep
        """
        if not name:
            name = generate_unique_name("Sweep")
        if self.setuptype == 7:
            self._app.logger.warning("This method only applies to HFSS and Q3D. Use add_eddy_current_sweep method.")
            return False
        if self.setuptype <= 4:
            sweep_n = SweepHFSS(self, name=name, sweep_type=sweep_type)
        elif self.setuptype in [14, 30, 31]:
            sweep_n = SweepMatrix(self, name=name, sweep_type=sweep_type)
        else:
            self._app.logger.warning("This method only applies to HFSS, Q2D, and Q3D.")
            return False
        sweep_n.create()
        self.sweeps.append(sweep_n)
        return sweep_n

    @pyaedt_function_handler(sweepname="name")
    def get_sweep(self, name=None):
        """Return frequency sweep object of a given sweep.

        Parameters
        ----------
        name : str, optional
            Name of the sweep. The default is ``None``, in which case the
            first sweep is used.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or :class:`pyaedt.modules.SolveSweeps.SweepMatrix`

        Examples
        --------
        >>> hfss = Hfss()
        >>> setup = hfss.get_setup('Pyaedt_setup')
        >>> sweep = setup.get_sweep('Sweep1')
        >>> sweep.add_subrange("LinearCount",0,10,1,"Hz")
        >>> sweep.add_subrange("LogScale",10,1E8,100,"Hz")
        """
        if name:
            for sweep in self.sweeps:
                if name == sweep.name:
                    return sweep
        else:
            if self.sweeps:
                return self.sweeps[0]
        return False

    @pyaedt_function_handler()
    def get_sweep_names(self):
        """Get the names of all sweeps in a given analysis setup.

        Returns
        -------
        list of str
            List of names of all sweeps for the setup.

        References
        ----------

        >>> oModules.GetSweeps

        Examples
        --------
        >>> import pyaedt
        >>> hfss = pyaedt.Hfss()
        >>> setup = hfss.get_setup('Pyaedt_setup')
        >>> sweeps = setup.get_sweep_names()
        """
        return self.omodule.GetSweeps(self.name)

    @pyaedt_function_handler(sweepname="name")
    def delete_sweep(self, name):
        """Delete a sweep.

        Parameters
        ----------
        name : str
            Name of the sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteSweep

        Examples
        --------
        Create a frequency sweep and then delete it.

        >>> import pyaedt
        >>> hfss = pyaedt.Hfss()
        >>> setup1 = hfss.create_setup(name='Setup1')
        >>> setup1.create_frequency_sweep(
            "GHz", 24, 24.25, 26, "Sweep1", sweep_type="Fast",
        )
        >>> setup1.delete_sweep("Sweep1")
        """
        if name in self.get_sweep_names():
            self.sweeps = [sweep for sweep in self.sweeps if sweep.name != name]
            self.omodule.DeleteSweep(self.name, name)
            return True
        return False

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
        # props["MultipleAdaptiveFreqsSetup"] could potentially be nonexistent.
        # A known case is the setup automatically created by setting auto-open region.
        if "MultipleAdaptiveFreqsSetup" not in self.props:  # pragma no cover
            self.props["MultipleAdaptiveFreqsSetup"] = {}
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
    app : :class:`pyaedt.application.Analysis.Analysis`
        Inherited app object.
    solution_type : int, str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        Setup.__init__(self, app, solution_type, name, is_new_setup)

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

    @pyaedt_function_handler(rangetype="range_type")
    def add_subrange(self, range_type, start, end=None, count=None, unit="GHz", clear=False):
        """Add a subrange to the sweep.

        Parameters
        ----------
        range_type : str
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
            self.props["Sweeps"]["Sweep"]["RangeType"] = range_type
            self.props["Sweeps"]["Sweep"]["RangeStart"] = str(start) + unit
            if range_type == "LinearCount":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeCount"] = count
            elif range_type == "LinearStep":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeStep"] = str(count) + unit
            elif range_type == "LogScale":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeSamples"] = count
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
            return self.update()
        sweep_range = {"RangeType": range_type, "RangeStart": str(start) + unit}
        if range_type == "LinearCount":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = count
        elif range_type == "LinearStep":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeStep"] = str(count) + unit
        elif range_type == "LogScale":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = self.props["RangeCount"]
            sweep_range["RangeSamples"] = count
        if not self.props["Sweeps"]["Sweep"].get("SweepRanges") or not self.props["Sweeps"]["Sweep"]["SweepRanges"].get(
            "Subrange"
        ):
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
        self.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"].append(sweep_range)
        return self.update()

    @pyaedt_function_handler(freq="frequency")
    def enable_adaptive_setup_single(self, frequency=None, max_passes=None, max_delta_s=None):
        """Enable HFSS single frequency setup.

        Parameters
        ----------
        frequency : float, str, optional
            Frequency to set the adaptive convergence at.
            The default is ``None``, in which case the value in the setup is
            not updated. You can specify a float value (GHz) or a string.
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
        if isinstance(frequency, (int, float)):
            frequency = "{}GHz".format(frequency)
        if frequency:
            self.props["Frequency"] = frequency
        if max_passes:
            self.props["MaximumPasses"] = max_passes
        if max_delta_s:
            self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler(high_frquency="high_frequency")
    def enable_adaptive_setup_broadband(self, low_frequency, high_frequency, max_passes=6, max_delta_s=0.02):
        """Enable HFSS broadband setup.

        Parameters
        ----------
        low_frequency : float, str
            Lower frequency to set the adaptive convergence at.
            You can specify a float value (GHz) or a string.
        high_frequency : float, str
            Lower frequency to set the adaptive convergence at. You can
            specify a float value (GHz) or a string.
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
        if isinstance(high_frequency, (int, float)):
            high_frequency = "{}GHz".format(high_frequency)
        self.props["MultipleAdaptiveFreqsSetup"]["Low"] = low_frequency
        self.props["MultipleAdaptiveFreqsSetup"]["High"] = high_frequency
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
    app : :class:`pyaedt.application.Analysis.Analysis`
        Inherited app object.
    solution_type : int, str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        Setup.__init__(self, app, solution_type, name, is_new_setup)

    @pyaedt_function_handler(rangetype="range_type")
    def add_subrange(self, range_type, start, end=None, count=None, unit="GHz", clear=False):
        """Add a subrange to the sweep.

        Parameters
        ----------
        range_type : str
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
            self.props["Sweeps"]["Sweep"]["RangeType"] = range_type
            self.props["Sweeps"]["Sweep"]["RangeStart"] = str(start) + unit
            if range_type == "LinearCount":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeCount"] = count
            elif range_type == "LinearStep":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeStep"] = str(count) + unit
            elif range_type == "LogScale":
                self.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end) + unit
                self.props["Sweeps"]["Sweep"]["RangeSamples"] = count
            self.props["Sweeps"]["Sweep"]["SweepRanges"] = {"Subrange": []}
            return self.update()
        sweep_range = {"RangeType": range_type, "RangeStart": str(start) + unit}
        if range_type == "LinearCount":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = count
        elif range_type == "LinearStep":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeStep"] = str(count) + unit
        elif range_type == "LogScale":
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
    app : :class:`pyaedt.application.Analysis.Analysis`
        Inherited app object.
    solution_type : int, str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        Setup.__init__(self, app, solution_type, name, is_new_setup)

    @pyaedt_function_handler()
    def add_eddy_current_sweep(
        self, range_type="LinearStep", start=0.1, end=100, count=0.1, units="Hz", clear=True, save_all_fields=True
    ):
        """Create a Maxwell Eddy Current Sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, ``"LogScale"`` and ``"SinglePoints"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. Required for ``range_type="LinearCount"|"LinearStep"|"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. Required for ``range_type="LinearCount"|"LinearStep"|"LogScale"``.
        units : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"Hz"``.
        clear : bool, optional
            If set to ``True``, all other subranges will be suppressed except the current one under creation.
            Default value is ``False``.
        save_all_fields : bool, optional
            Save fields at all frequency points to save fields for the entire set of sweep ranges.
            Default is ``True``.


        Returns
        -------
        bool
            ``True`` if successful, ``False`` if it fails.
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
        self.props["SaveAllFields"] = save_all_fields
        self.update()
        self.auto_update = legacy_update
        return True

    @pyaedt_function_handler()
    def enable_control_program(self, control_program_path, control_program_args=" ", call_after_last_step=False):
        """Enable control program option is solution setup.
        Provide externally created executable files, or Python (*.py) scripts that are called after each time step,
        and allow you to control the source input, circuit elements, mechanical quantities, time step,
        and stopping criteria, based on the updated solutions.

        Parameters
        ----------
        control_program_path : str
            File path of control program.
        control_program_args : str, optional
            Arguments to pass to control program.
            Default value is ``" "``.
        call_after_last_step : bool, optional
            If ``True`` the control program is called after the simulation is completed.
            Default value is ``False``.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if it fails.

        Notes
        -----
        By default a control program script will be called by the pre-installed Python interpreter:
        ``<install_path>\\Win64\\commonfiles\\CPython\\37\\winx64\\Release\\python\\python.exe``.
        However, the user can specify a custom Python interpreter to be used by setting following environment variable:
        ``EM_CTRL_PROG_PYTHON_PATH=<path_to\\python.exe>``

        References
        ----------
        >>> oModule.EditSetup
        """
        if self.p_app.solution_type not in ["Transient", "TransientXY", "TransientZ"]:
            self._app.logger.error("Control Program is only available in Maxwell 2D and 3D Transient solutions.")
            return False

        if not os.path.exists(control_program_path):
            self._app.logger.error("Control Program file does not exist.")
            return False

        if not isinstance(control_program_args, str):
            self._app.logger.error("Control Program arguments have to be a string.")
            return False

        self.auto_update = False
        self.props["UseControlProgram"] = True
        self.props["ControlProgramName"] = control_program_path
        self.props["ControlProgramArg"] = control_program_args
        self.props["CallCtrlProgAfterLastStep"] = call_after_last_step
        self.auto_update = True
        self.update()

        return True


class SetupQ3D(Setup, object):
    """Initializes, creates, and updates an Q3D setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solution_type : int, str
        Type of the setup.
    name : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    is_new_setup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solution_type, name="MySetupAuto", is_new_setup=True):
        Setup.__init__(self, app, solution_type, name, is_new_setup)
        self._dc_enabled = True
        self._ac_rl_enbled = True
        self._capacitance_enabled = True

    @pyaedt_function_handler(freqstart="start_frequency", freqstop="stop_frequency", sweepname="name")
    def create_frequency_sweep(
        self,
        unit=None,
        start_frequency=0.0,
        stop_frequency=20.0,
        num_of_freq_points=None,
        name=None,
        save_fields=True,
        sweep_type="Discrete",
        interpolation_tol=0.5,
        interpolation_max_solutions=250,
    ):
        """Create a sweep with the specified number of points.

        Parameters
        ----------
        unit : str, optional
            Frequency units. The default is ``None``, in which case the default desktop units are used.
        start_frequency : float, str, optional
            Starting frequency of the sweep. The default is ``0.0``.
            If a unit is passed with the number, such as``"1MHz"``, the unit is ignored.
        stop_frequency : float, str, optional
            Stopping frequency of the sweep. The default is ``20.0``.
            If a unit is passed with the number, such as ``"1MHz"``, the unit is ignored.
        num_of_freq_points : int
            Number of frequency points in the range. The default is ``401`` for
            a sweep type of ``"Interpolating"`` or ``"Fast"``. The default is ``5`` for a sweep
            type of ``"Discrete"``.
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
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
        :class:`pyaedt.modules.SolveSweeps.SweepQ3D` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------
        >>> oModule.InsertFrequencySweep

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> q3d = Q3d()
        >>> setup = q3d.create_setup("LinearCountSetup")
        >>> sweep = setup.create_frequency_sweep(unit="GHz", start_frequency=0.5,
        ...                                     stop_frequency=1.5, name="Sweep1")
        >>> q3d.release_desktop(True, True)
        """
        if sweep_type in ["Interpolating", "Fast"]:
            num_of_freq_points = num_of_freq_points or 401
        elif sweep_type == "Discrete":
            num_of_freq_points = num_of_freq_points or 5
        else:
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")

        if name is None:
            name = generate_unique_name("Sweep")

        if name in [sweep.name for sweep in self.sweeps]:
            oldname = name
            name = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, name)
        sweepdata = self.add_sweep(name, sweep_type)
        if not sweepdata:
            return False
        sweepdata.props["RangeType"] = "LinearCount"
        sweepdata.props["RangeStart"] = self.p_app.value_with_units(start_frequency, unit, "Frequency")
        sweepdata.props["RangeEnd"] = self.p_app.value_with_units(stop_frequency, unit, "Frequency")
        sweepdata.props["RangeCount"] = num_of_freq_points
        sweepdata.props["Type"] = sweep_type
        if sweep_type == "Interpolating":
            sweepdata.props["InterpTolerance"] = interpolation_tol
            sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
            sweepdata.props["InterpMinSolns"] = 0
            sweepdata.props["InterpMinSubranges"] = 1
        sweepdata.props["SaveFields"] = save_fields if sweep_type == "Discrete" else False
        sweepdata.props["SaveRadFields"] = False
        sweepdata.update()
        self._app.logger.info("Linear count sweep {} has been correctly created".format(name))
        return sweepdata

    @pyaedt_function_handler(freqstart="start_frequency", freqstop="stop_frequency", sweepname="name")
    def create_linear_step_sweep(
        self,
        unit="GHz",
        start_frequency=0.0,
        stop_frequency=2.0,
        step_size=0.05,
        name=None,
        save_fields=True,
        sweep_type="Discrete",
    ):
        """Create a sweep with a specified frequency step.

        Parameters
        ----------
        unit : str, optional
            Unit of the frequency. The default is ``"GHz"``.
        start_frequency : float, optional
            Starting frequency of the sweep. The default is ``0.0``.
        stop_frequency : float, optional
            Stopping frequency of the sweep. The default is ``2.0``.
        step_size : float, optional
            Frequency size of the step. The default is ``0.05``.
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        sweep_type : str, optional
            Whether to create a ``"Discrete"`` or``"Interpolating"``  sweep.
            The default is ``"Discrete"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepQ3D` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------
        Create a setup named ``"LinearStepSetup"`` and use it in a linear step sweep
        named ``"LinearStepSweep"``.
        >>> from pyaedt import Q3d
        >>> q3d = Q3d()
        >>> setup = q3d.create_setup("LinearStepSetup")
        >>> linear_step_sweep = setup.create_linear_step_sweep(name="LinearStepSweep",
        ...                                                   unit="MHz", start_frequency=1.1e3,
        ...                                                   stop_frequency=1200.1, step_size=153.8)
        >>> type(linear_step_sweep)
        >>> q3d.release_desktop(True, True)
        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")
        if name is None:
            name = generate_unique_name("Sweep")

        if name in [sweep.name for sweep in self.sweeps]:
            oldname = name
            name = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, name)
        sweepdata = self.add_sweep(name, sweep_type)
        if not sweepdata:
            return False
        sweepdata.props["RangeType"] = "LinearStep"
        sweepdata.props["RangeStart"] = str(start_frequency) + unit
        sweepdata.props["RangeEnd"] = str(stop_frequency) + unit
        sweepdata.props["RangeStep"] = str(step_size) + unit
        sweepdata.props["SaveFields"] = save_fields if sweep_type == "Discrete" else False
        sweepdata.props["SaveRadFields"] = False
        sweepdata.props["ExtrapToDC"] = False
        sweepdata.props["Type"] = sweep_type
        if sweep_type == "Interpolating":
            sweepdata.props["InterpTolerance"] = 0.5
            sweepdata.props["InterpMaxSolns"] = 250
            sweepdata.props["InterpMinSolns"] = 0
            sweepdata.props["InterpMinSubranges"] = 1
        sweepdata.update()
        self._app.logger.info("Linear step sweep {} has been correctly created".format(name))
        return sweepdata

    @pyaedt_function_handler(sweepname="name")
    def create_single_point_sweep(
        self,
        unit="GHz",
        freq=1.0,
        name=None,
        save_single_field=True,
        save_fields=False,
    ):
        """Create a sweep with a single frequency point.

        Parameters
        ----------
        unit : str, optional
            Unit of the frequency. The default is ``"GHz"``.
        freq : float, list, optional
            One or more frequencies for creating distinct single points.
            The default is ``1.0``.
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        save_single_field : bool, list, optional
            Whether to save the fields of the single point. The default is ``True``.
            If a list is specified, the length must be the same as the
            frequency length.
        save_fields : bool, optional
            Whether to save the fields for all points and subranges defined in the sweep. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepQ3D` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------
        >>> oModule.InsertFrequencySweep

        Examples
        --------
        Create a setup named ``"SinglePointSetup"`` and use it in a single point sweep
        named ``"SinglePointSweep"``.
        >>> from pyaedt import Q3d
        >>> q3d = Q3d()
        >>> setup = q3d.create_setup("SinglePointSetup")
        >>> single_point_sweep = setup.create_single_point_sweep(
        ...                                                   name="SinglePointSweep",
        ...                                                   unit="MHz", freq=1.1e3)
        >>> type(single_point_sweep)
        >>> q3d.release_desktop(True, True)
        """
        if name is None:
            name = generate_unique_name("SinglePoint")

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

        if name in [sweep.name for sweep in self.sweeps]:
            oldname = name
            name = generate_unique_name(oldname)
            self._app.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, name)
        sweepdata = self.add_sweep(name, "Discrete")
        sweepdata.props["RangeType"] = "SinglePoints"
        sweepdata.props["RangeStart"] = str(freq0) + unit
        sweepdata.props["RangeEnd"] = str(freq0) + unit
        sweepdata.props["SaveSingleField"] = save0
        sweepdata.props["SaveFields"] = save_fields
        sweepdata.props["SaveRadFields"] = False
        sweepdata.props["SMatrixOnlySolveMode"] = "Auto"
        if add_subranges:
            for f, s in zip(freq, save_single_field):
                sweepdata.add_subrange(rangetype="SinglePoints", start=f, unit=unit, save_single_fields=s)
        sweepdata.update()
        self._app.logger.info("Single point sweep {} has been correctly created".format(name))
        return sweepdata

    @pyaedt_function_handler(sweepname="name", sweeptype="sweep_type")
    def add_sweep(self, name=None, sweep_type="Interpolating"):
        """Add a sweep to the project.

        Parameters
        ----------
        name : str, optional
            Name of the sweep. The default is ``None``, in which
            case a name is automatically assigned.
        sweep_type : str, optional
            Type of the sweep. The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepHFSS` or :class:`pyaedt.modules.SolveSweeps.SweepMatrix`
            Sweep object.

        References
        ----------

        >>> oModule.InsertFrequencySweep
        """
        if not name:
            name = generate_unique_name("Sweep")
        if self.setuptype == 7:
            self._app.logger.warning("This method only applies to HFSS and Q3D. Use add_eddy_current_sweep method.")
            return False
        if self.setuptype <= 4:
            sweep_n = SweepHFSS(self, name=name, sweep_type=sweep_type)
        elif self.setuptype in [14, 30, 31]:
            sweep_n = SweepMatrix(self, name=name, sweep_type=sweep_type)
        else:
            self._app.logger.warning("This method only applies to HFSS, Q2D, and Q3D.")
            return False
        sweep_n.create()
        self.sweeps.append(sweep_n)
        for setup in self.p_app.setups:
            if self.name == setup.name:
                setup.sweeps.append(sweep_n)
                break
        return sweep_n

    @pyaedt_function_handler(sweepname="name")
    def get_sweep(self, name=None):
        """Get the frequency sweep object of a given sweep.

        Parameters
        ----------
        name : str, optional
            Name of the sweep. The default is ``None``, in which case the
            first sweep is used.

        Returns
        -------
        :class:`pyaedt.modules.SolveSweeps.SweepQ3D` or :class:`pyaedt.modules.SolveSweeps.SweepMatrix`

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> q3d = Q3d()
        >>> setup = q3d.create_setup()
        >>> sweep = setup.create_frequency_sweep(name="Sweep1")
        >>> sweep.add_subrange("LinearCount",0,10,1,"Hz")
        >>> sweep.add_subrange("LogScale",10,1E8,100,"Hz")
        >>> sweep = setup.get_sweep("Sweep1")
        >>> q3d.release_desktop(True, True)
        """
        if name:
            for sweep in self.sweeps:
                if name == sweep.name:
                    return sweep
        else:
            if self.sweeps:
                return self.sweeps[0]
        return False

    @property
    def ac_rl_enabled(self):
        """Get/Set the AC RL solution in active Q3D setup.

        Returns
        -------
        bool
        """
        return self._ac_rl_enbled

    @ac_rl_enabled.setter
    def ac_rl_enabled(self, value):
        if value or (self._dc_enabled or self._capacitance_enabled):
            self._ac_rl_enbled = value
            self.update()

    @property
    def capacitance_enabled(self):
        """Get/Set the Capacitance solution in active Q3D setup.

        Returns
        -------
        bool
        """
        return self._capacitance_enabled

    @capacitance_enabled.setter
    def capacitance_enabled(self, value):
        if value or (self._dc_enabled or self._ac_rl_enbled):
            self._capacitance_enabled = value
            self.update()

    @property
    def dc_enabled(self):
        """Get/Set the DC solution in active Q3D setup.

        Returns
        -------
        bool
        """
        return self._dc_enabled

    @dc_enabled.setter
    def dc_enabled(self, value):
        if value or (self._ac_rl_enbled or self._capacitance_enabled):
            self._dc_enabled = value
            self.update()

    @property
    def dc_resistance_only(self):
        """Get/Set the DC Resistance Only or Resistance/Inductance calculatio in active Q3D setup.

        Returns
        -------
        bool
        """
        try:
            return self.props["DC"]["SolveResOnly"]
        except KeyError:
            return False

    @dc_resistance_only.setter
    def dc_resistance_only(self, value):
        if self.dc_enabled:
            self.props["DC"]["SolveResOnly"] = value

    @pyaedt_function_handler()
    def update(self, properties=None):
        """Update the setup based on either the class argument or a dictionary.

        Parameters
        ----------
        properties : optional
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
        if properties:
            for el in properties:
                self.props[el] = properties[el]
        self.auto_update = legacy_update
        arg = ["NAME:" + self.name]
        props1 = {i: v for i, v in self.props.items()}
        if not self.capacitance_enabled:
            del props1["Cap"]
        if not self.ac_rl_enabled:
            del props1["AC"]
        if not self.dc_enabled:
            del props1["DC"]
        _dict2arg(props1, arg)

        self.omodule.EditSetup(self.name, arg)
        return True
