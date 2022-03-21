import copy
from collections import OrderedDict

from pyaedt.generic.DataHandlers import _arg2dict
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.OptimetricsTemplates import defaultdoeSetup
from pyaedt.modules.OptimetricsTemplates import defaultdxSetup
from pyaedt.modules.OptimetricsTemplates import defaultoptiSetup
from pyaedt.modules.OptimetricsTemplates import defaultparametricSetup
from pyaedt.modules.OptimetricsTemplates import defaultsensitivitySetup
from pyaedt.modules.OptimetricsTemplates import defaultstatisticalSetup
from pyaedt.modules.SetupTemplates import SetupProps


class CommonOptimetrics(object):
    """Creates and sets up optimizations.

    Parameters
    ----------
    p_app :

    name :

    dictinputs

    optimtype : str
        Type of the optimization.

    """

    def __init__(self, p_app, name, dictinputs, optimtype):
        self.auto_update = False
        self._app = p_app
        self.omodule = self._app.ooptimetrics
        self.name = name
        self.soltype = optimtype

        inputd = copy.deepcopy(dictinputs)

        if optimtype == "OptiParametric":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultparametricSetup))
        if optimtype == "OptiDesignExplorer":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultdxSetup))
        if optimtype == "OptiOptimization":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultoptiSetup))
        if optimtype == "OptiSensitivity":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultsensitivitySetup))
        if optimtype == "OptiStatistical":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultstatisticalSetup))
        if optimtype == "OptiDXDOE":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultdoeSetup))

        if inputd:
            self.props.pop("ID", None)
            self.props.pop("NextUniqueID", None)
            self.props.pop("MoveBackwards", None)
            self.props.pop("GoalSetupVersion", None)
            self.props.pop("Version", None)
            self.props.pop("SetupType", None)
            if inputd.get("Sim. Setups"):
                setups = inputd["Sim. Setups"]
                for el in setups:
                    if type(self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]) is list:
                        for setup in self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]:
                            if setup["I"] == el:
                                setups[setups.index(el)] = setup["I"]
                                break
                    else:
                        if self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]["I"] == el:
                            setups[setups.index(el)] = self._app.design_properties["SolutionManager"]["ID Map"][
                                "Setup"
                            ]["N"]
                            break
            if inputd.get("Goals", None):
                if self._app._is_object_oriented_enabled():
                    oparams = self.omodule.GetChildObject(self.name).GetCalculationInfo()
                    oparam = [i for i in oparams[0]]
                    calculation = ["NAME:Goal"]
                    calculation.extend(oparam)
                    arg1 = OrderedDict()
                    _arg2dict(calculation, arg1)
                    self.props["Goals"] = arg1
        self.auto_update = True

    @pyaedt_function_handler()
    def _get_context(
        self,
        expressions,
        condition,
        goal_weight,
        goal_value,
        setup_sweep_name=None,
        domain="Sweep",
        intrinsics=None,
        report_category=None,
        context=None,
        subdesign_id=None,
        polyline_points=0,
    ):
        did = 3
        var_type = "d"
        if domain != "Sweep":
            did = 1
            var_type = "a"
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = report_category
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        sweepdefinition["Solution"] = setup_sweep_name
        ctxt = OrderedDict({})

        if self._app.solution_type in ["TR", "AC", "DC"]:
            ctxt["SimValueContext"] = [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]
            setup_sweep_name = self._app.solution_type
            sweepdefinition["Solution"] = setup_sweep_name

        elif self._app.solution_type in ["HFSS3DLayout"]:
            if context == "Differential Pairs":
                ctxt["SimValueContext"] = [
                    did,
                    0,
                    2,
                    0,
                    False,
                    False,
                    -1,
                    1,
                    0,
                    1,
                    1,
                    "",
                    0,
                    0,
                    "EnsDiffPairKey",
                    False,
                    "1",
                    "IDIID",
                    False,
                    "1",
                ]
            else:
                ctxt["SimValueContext"] = [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]

        elif self._app.solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt["SimValueContext"] = [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]
            if subdesign_id:
                ctxt_temp = ["NUMLEVELS", False, "1", "SUBDESIGNID", False, str(subdesign_id)]
                ctxt["SimValueContext"].extend(ctxt_temp)
            if context == "Differential Pairs":
                ctxt_temp = ["USE_DIFF_PAIRS", False, "1"]
                ctxt["SimValueContext"].extend(ctxt_temp)
        elif context == "Differential Pairs":
            ctxt["SimValueContext"] = ["Diff:=", "Differential Pairs", "Domain:=", domain]
        elif self._app.solution_type in ["Q3D Extractor", "2D Extractor"]:
            if not context:
                ctxt["Context"] = "Original"
            else:
                ctxt["Context"] = context
        elif context:
            ctxt["Context"] = context
            if context in self._app.modeler.line_names:
                ctxt["PointCount"] = polyline_points
        else:
            ctxt = OrderedDict({"Domain": domain})

        sweepdefinition["SimValueContext"] = ctxt

        sweepdefinition["Calculation"] = expressions
        sweepdefinition["Name"] = expressions
        sweepdefinition["Ranges"] = OrderedDict({})
        if context in self._app.modeler.line_names and intrinsics and "Distance" not in intrinsics:
            sweepdefinition["Ranges"]["Range"] = ("Var:=", "Distance", "Type:=", "a")
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
            if not setup_sweep_name:
                self._app.logger.error("Sweep not Available.")
                return False
        elif setup_sweep_name not in self._app.existing_analysis_sweeps:
            self._app.logger.error("Sweep not Available.")
            return False

        if intrinsics:
            for v, k in intrinsics.items():
                r = ["Var:=", v, "Type:=", var_type]
                if var_type == "d" and k:
                    r.append("DiscreteValues:=")
                    if isinstance(k, list):
                        r.append(",".join(k))
                    else:
                        r.append(k)

                if not sweepdefinition["Ranges"]:
                    sweepdefinition["Ranges"]["Range"] = {"Range": tuple(r)}
                elif isinstance(sweepdefinition["Ranges"]["Range"], list):
                    sweepdefinition["Ranges"]["Range"].append(tuple(r))
                else:
                    sweepdefinition["Ranges"]["Range"] = [sweepdefinition["Ranges"]["Range"]]
                    sweepdefinition["Ranges"]["Range"].append(tuple(r))

        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]}
        )
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)
        return sweepdefinition

    @pyaedt_function_handler()
    def update(self, update_dictionary=None):
        """Update the setup based on stored properties.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary to use. The  default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if update_dictionary:
            for el in update_dictionary:
                self.props._setitem_without_update(el, update_dictionary[el])

        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def create(self):
        """Create a setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.InsertSetup
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.InsertSetup(self.soltype, arg)
        return True

    @pyaedt_function_handler()
    def _add_calculation(
        self,
        reporttype,
        solution=None,
        domain="Sweep",
        calculation="",
        calculation_type="d",
        calculation_value="",
        calculation_name=None,
    ):
        """Add a calculation to the setup.

        Parameters
        ----------
        reporttype : str
            Type of report.
        solution : str, optional
            Type of the solution. The default is ``None``.
        domain : str, optional
             Type of the domain. The default is ``"Sweep"``.
        calculation : str, optional
             The default is ``""``.
        calculation_type : str, optional
             Type of the calculaton. The default is ``"d"``.
        calculation_value : str, optional
             The default is ``""``.
        calculation_name : str, optional
             Name of the the calculation. The default is ``None``.

        Returns
        -------

        """
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep

        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        if calculation_name:
            sweepdefinition["Name"] = calculation_name
        else:
            sweepdefinition["Name"] = generate_unique_name(calculation)
        if domain == "Sweep":
            var = "Freq"
        else:
            var = "Time"
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", var, "Type:=", calculation_type, "DiscreteValues:=", calculation_value]}
        )
        if "Goal" in self.props["Goals"]:
            if type(self.props["Goals"]["Goal"]) is not list:
                self.props["Goals"]["Goal"] = [self.props["Goals"]["Goal"], sweepdefinition]
            else:
                self.props["Goals"]["Goal"].append(sweepdefinition)
        else:
            self.props["Goals"]["Goal"] = sweepdefinition

        return self.update()

    @pyaedt_function_handler()
    def _add_goal(
        self,
        optigoalname,
        reporttype,
        solution=None,
        domain="Sweep",
        calculation="",
        calculation_type="discrete",
        calc_val1="",
        calc_val2="",
        condition="==",
        goal_value=1,
        goal_weight=1,
        goal_name=None,
    ):
        """Add an optimization goal to the setup.

        Parameters
        ----------
        optigoalname : str
            Name of the optimization goal.
        reporttype : str, optional
            Type of the report.
        solution : str, optional
            Type of the solution. The default is ``None``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"''.
        calculation : str, optional
            Name of the calculation. The default is ``""``.
        calculation_type : str, optional
            Type of the calculation. The default is ``"discrete"``.
        calc_val1 : str, optional
            First value for the calculation. The default is ``""``.
        calc_val2 : str, optional
            Second value for the calculation. The default is ``""``.
        condition : str, optional
            The condition for the calculation. The default is ``"=="``.
        goal_value : optional
            Value for the optimization goal. The default is ``1``.
        goal_weight : optional
            Weight for the optimzation goal. The default is ``1``.
        goal_name : str, optional
            Name of the goal. The default is ``None``.

        Returns
        -------

        """
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep
        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        if goal_name:
            sweepdefinition["Name"] = goal_name
        else:
            sweepdefinition["Name"] = generate_unique_name(calculation)
        if domain == "Sweep":
            var = "Freq"
        else:
            var = "Time"
        if calculation_type == "discrete":
            if type(calc_val1) is list:
                dr = ",".join(calc_val1)
            else:
                dr = calc_val1
            sweepdefinition["Ranges"] = OrderedDict({"Range": ["Var:=", var, "Type:=", "d", "DiscreteValues:=", dr]})
        else:
            sweepdefinition["Ranges"] = OrderedDict(
                {
                    "Range": [
                        "Var:=",
                        var,
                        "Type:=",
                        calculation_type,
                        "Start:=",
                        calc_val1,
                        "Stop:=",
                        calc_val2,
                        "DiscreteValues:=",
                        "",
                    ]
                }
            )
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]}
        )
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)
        if "Goal" in self.props[optigoalname]:
            if type(self.props[optigoalname]["Goal"]) is not list:
                self.props[optigoalname]["Goal"] = [self.props[optigoalname]["Goal"], sweepdefinition]
            else:
                self.props[optigoalname]["Goal"].append(sweepdefinition)
        else:
            self.props[optigoalname]["Goal"] = sweepdefinition
        return self.update()


class SetupOpti(CommonOptimetrics, object):
    """Sets up a DesignXplorer optimization in optiSLang.

    Parameters
    ----------
    app :
    name :
    dictinputs :
        The default is ``None``.
    optimtype : str, optional
        Type of the optimization. The default is ``"OptiDesignExplorer"``.

    """

    def __init__(self, app, name, dictinputs=None, optim_type="OptiDesignExplorer"):
        CommonOptimetrics.__init__(self, app, name, dictinputs=dictinputs, optimtype=optim_type)

    @pyaedt_function_handler()
    def add_calculation(
        self,
        calculation="",
        calculation_value="",
        reporttype="Modal Solution Data",
        solution=None,
        domain="Sweep",
        calculation_name=None,
    ):
        """Add a calculation to the setup.

        Parameters
        ----------
        calculation : str, optional
            Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
        calculation_value : str, optional
            Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        calculation_name : str, optional
             Name of the calculation. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        return self._add_calculation(
            reporttype=reporttype,
            solution=solution,
            domain=domain,
            calculation_type="d",
            calculation=calculation,
            calculation_value=calculation_value,
            calculation_name=calculation_name,
        )

    @pyaedt_function_handler()
    def add_goal(
        self,
        calculation="",
        calculation_value="",
        calculation_type="discrete",
        calculation_stop="",
        reporttype="Modal Solution Data",
        solution=None,
        domain="Sweep",
        goal_name=None,
        goal_value=1,
        goal_weight=1,
        condition="==",
    ):
        """Add a goal to the setup.

        Parameters
        ----------
        calculation : str, optional
            Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
        calculation_value : str, optional
            Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
            If ``calculation_type="discrete"``, the value is discrete or is a list. If the
            value is a range, it is the starting value.
        calculation_type : str, optional
            Type of the calculation. Options are ``"discrete"`` or ``"range"``.
            The default is ``"discrete"``.
        calculation_stop : str, optional
            Stopping value for the calculation if ``calculation_type="range"``.
            The default is ``""``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        goal_name : str, optional
             Name of the goal. The default is ``None``.
        goal_value : optional
             Value for the goal. The default is ``1``.
        goal_weight : optional
             Value for the goal weight. The default is ``1``.
        condition : string, optional
             The default is ``"=="``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        return self._add_goal(
            optigoalname="CostFunctionGoals",
            reporttype=reporttype,
            solution=solution,
            domain=domain,
            calculation_type=calculation_type,
            calculation=calculation,
            calc_val1=calculation_value,
            calc_val2=calculation_stop,
            goal_name=goal_name,
            goal_weight=goal_weight,
            goal_value=goal_value,
            condition=condition,
        )


class SetupParam(CommonOptimetrics, object):

    """Sets up a parametric analysis in optiSLang.

    Parameters
    ----------
    p_app : str
        Inherited AEDT object.

    name :

    dictinputs : optional
        The default is ``None``.
    otimtype : str, optional
        Type of the optimization. The default is ``"OptiParametric"``.

    """

    def __init__(self, p_app, name, dictinputs=None, optim_type="OptiParametric"):
        CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype=optim_type)
        pass

    @pyaedt_function_handler()
    def add_variation(self, sweep_var, datarange):
        """Add a variation to an existing parametric setup.

        Parameters
        ----------
        sweep_var : str
            Name of the variable.
        datarange :
            Range of the data.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if type(self.props["Sweeps"]["SweepDefinition"]) is not list:
            self.props["Sweeps"]["SweepDefinition"] = [self.props["Sweeps"]["SweepDefinition"]]
        sweepdefinition = OrderedDict()
        sweepdefinition["Variable"] = sweep_var
        sweepdefinition["Data"] = datarange
        sweepdefinition["OffsetF1"] = False
        sweepdefinition["Synchronize"] = 0
        self.props["Sweeps"]["SweepDefinition"].append(sweepdefinition)
        self.update()
        return True

    @pyaedt_function_handler()
    def add_calculation(
        self,
        calculation="",
        calculation_value="",
        reporttype="Modal Solution Data",
        solution=None,
        domain="Sweep",
        calculation_name=None,
    ):
        """Add a calculation to the parametric setup.

        Parameters
        ----------
        calculation : str, optional
            Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
        calculation_value : str, optional
            Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        calculation_name : str, optional
            Name of the calculation. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        return self._add_calculation(
            reporttype=reporttype,
            solution=solution,
            domain=domain,
            calculation_type="d",
            calculation=calculation,
            calculation_value=calculation_value,
            calculation_name=calculation_name,
        )


class ParametricSetups(object):
    """Sets up Parametrics analyses. It includes Parametrics, Sensitivity and Statistical Analysis.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> sensitivity_setups = app.parametrics
    """

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if (
                        isinstance(setups_data[data], (OrderedDict, dict))
                        and setups_data[data]["SetupType"] == "OptiParametric"
                    ):
                        self.setups.append(SetupParam(p_app, data, setups_data[data], setups_data[data]["SetupType"]))
            except:
                pass

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    @pyaedt_function_handler()
    def add(
        self,
        sweeps,
        solution=None,
        parametricname=None,
    ):
        """Add a basic sensitivity analysis.

        You can customize all options after the analysis is added.

        Parameters
        ----------
        sweeps : dict
            Variables with values.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        parametricname : str, optional
            Name of the sensitivity analysis. The default is ``None``, in which case
            a default name is assigned.

        Returns
        -------
        :class:`Sensitivity`

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not solution:
            solution = self._app.nominal_sweep
        setupname = [solution.split(" ")[0]]
        if not parametricname:
            parametricname = generate_unique_name("Parametric")
        setup = SetupParam(self._app, parametricname, optim_type="OptiParametric")
        setup.auto_update = False

        setup.props["Sim. Setups"] = setupname
        setup.props["Sweeps"] = OrderedDict({"SweepDefinition": None})
        for v, k in sweeps.items():
            sd = OrderedDict({"Variable": v, "Data": k, "OffsetF1": False, "Synchronize": 0})
            if not setup.props["Sweeps"]["SweepDefinition"]:
                setup.props["Sweeps"]["SweepDefinition"] = sd
            elif isinstance(setup.props["Sweeps"]["SweepDefinition"], list):
                setup.props["Sweeps"]["SweepDefinition"].append(sd)
            else:
                setup.props["Sweeps"]["SweepDefinition"] = [setup.props["Sweeps"]["SweepDefinition"]]
                setup.props["Sweeps"]["SweepDefinition"].append(sd)
        setup.create()
        setup.auto_update = True
        self.setups.append(setup)
        return setup


class OptimizationSetups(object):
    """Sets up optimizations. It includes Optimization, DOE and DesignXplorer Analysis.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> optimization_setup = app.optimizations
    """

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if isinstance(setups_data[data], (OrderedDict, dict)) and setups_data[data]["SetupType"] in [
                        "OptiOptimization",
                        "OptiDXDOE",
                        "OptiDesignExplorer",
                        "OptiSensitivity" "OptiStatistical",
                    ]:
                        self.setups.append(SetupOpti(p_app, data, setups_data[data], setups_data[data]["SetupType"]))
            except:
                pass

    @pyaedt_function_handler()
    def add(
        self,
        calculation,
        intrinsics,
        optim_type="Optimization",
        reporttype="Modal Solution Data",
        domain="Sweep",
        condition="<=",
        goal_value=1,
        goal_weight=1,
        solution=None,
        parametricname=None,
        context=None,
        subdesign_id=None,
        polyline_points=1001,
    ):
        """Add a basic optimization analysis.

        You can customize all options after the analysis is added.

        Parameters
        ----------
        calculation : str, optional
            Name of the calculation.
        calculation_value : str, optional
            Variation value, such as ``"1GHz"``.
        calculation_type : str, optional
            Type of the calculation. The default is ``"Freq"``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        condition : string, optional
            The default is ``"<="``.
        goal_value : optional
            Value for the goal. The default is ``1``.
        goal_weight : optional
            Value for the goal weight. The default is ``1``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        parametricname : str, optional
            Name of the analysis. The default is ``None``, in which case a
            default name is assigned.

        Returns
        -------
        type
            Optimization object.

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not solution:
            solution = self._app.nominal_sweep
        setupname = [solution.split(" ")[0]]
        if not parametricname:
            parametricname = generate_unique_name(optim_type)
        setup = SetupOpti(self._app, parametricname, optim_type="Opti" + optim_type)
        setup.auto_update = False
        sweepdefinition = setup._get_context(
            calculation,
            condition,
            goal_weight,
            goal_value,
            solution,
            domain,
            intrinsics,
            reporttype,
            context,
            subdesign_id,
            polyline_points,
        )
        setup.props["Sim. Setups"] = setupname
        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        setup.auto_update = True
        self.setups.append(setup)
        return setup
