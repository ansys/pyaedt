from collections import OrderedDict
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..application.DataHandlers import dict2arg, arg2dict
import copy

defaultparametricSetup = OrderedDict({"IsEnabled": True, "ProdOptiSetupDataV2":
            OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
                                                "StartingPoint": OrderedDict(), "Sim. Setups": [],
                                                "Sweeps": OrderedDict({"SweepDefinition":
                                                                           OrderedDict({"Variable": "",
                                                                                        "Data": "",
                                                                                        "OffsetF1": False,
                                                                                        "Synchronize": 0})}),
                                                "Sweep Operations": OrderedDict(),
                                                "Goals": OrderedDict()})


defaultdxSetup = OrderedDict({"IsEnabled": True, "ProdOptiSetupDataV2":
            OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
                                                "StartingPoint": OrderedDict(), "Sim. Setups": [],
                                                "Sweeps": OrderedDict({"SweepDefinition":
                                                                           OrderedDict({"Variable": "",
                                                                                        "Data": "",
                                                                                        "OffsetF1": False,
                                                                                        "Synchronize": 0})}),
                              "Sweep Operations": OrderedDict(), "CostFunctionName": "Cost", "CostFuncNormType": "L2",
                               "CostFunctionGoals": OrderedDict(),"EmbeddedParamSetup": -1, "Goals": OrderedDict()})

defaultoptiSetup = OrderedDict({"IsEnabled": True, "ProdOptiSetupDataV2":
    OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
                                "StartingPoint": OrderedDict(), "Optimizer": "Quasi Newton",
                                "AnalysisStopOptions": OrderedDict({"StopForNumIteration": True,
                                                                    "StopForElapsTime": False,
                                                                    "StopForSlowImprovement": False,
                                                                    "StopForGrdTolerance": False,
                                                                    "MaxNumIteration": 1000,
                                                                    "MaxSolTimeInSec": 3600,
                                                                    "RelGradientTolerance": 0,
                                                                    "MinNumIteration": 10
                                                                    }),
                                "CostFuncNormType": "L2", "PriorPSetup": "", "PreSolvePSetup": True,
                                "Variables": OrderedDict(), "LCS": OrderedDict(), "Goals": OrderedDict(),
                                "Acceptable_Cost": 0, "Noise": 0.0001, "UpdateDesign": False, "UpdateIteration": 5,
                                "KeepReportAxis": True, "UpdateDesignWhenDone": True})

defaultsensitivitySetup = OrderedDict({"IsEnabled": True, "ProdOptiSetupDataV2":
    OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
                                       "StartingPoint": OrderedDict(), "MaxIterations": 10,
                                       "PriorPSetup": "", "PreSolvePSetup": True, "Variables": OrderedDict(),
                                       "LCS": OrderedDict(), "Goals": OrderedDict(), "Primary Goal": 0,
                                       "PrimaryError": 0.0001, "Perform Worst Case Analysis": False})

defaultstatisticalSetup = OrderedDict({"IsEnabled": True, "ProdOptiSetupDataV2":
    OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
                                       "StartingPoint": OrderedDict(), "MaxIterations": 50,
                                       "SeedValue": 0, "PriorPSetup": "", "Variables": OrderedDict(),
                                       "Goals": OrderedDict()})

defaultdoeSetup = OrderedDict({"IsEnabled": True, "ProdOptiSetupDataV2":
            OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
                                                "StartingPoint": OrderedDict(), "Sim. Setups": [],
                                                "CostFunctionName": "Cost",
                               "CostFuncNormType": "L2", "CostFunctionGoals": OrderedDict(), "Variables": OrderedDict(),
                               "Goals": OrderedDict(),
                               "DesignExprData": OrderedDict({"Type": "kOSF", "CCDDeignType": "kFaceCentered",
                                                              "CCDTemplateType": "kStandard",
                                                              "LHSSampleType": "kCCDSample",
                                                              "RamdomSeed": 0, "NumofSamples": 10,
                                                              "OSFDeignType": "kOSFD_MAXIMINDIST",
                                                              "MaxCydes": 10}),
                               "RespSurfaceSetupData": OrderedDict({"Type": "kGenAggr", "RefineType": "kManual"}),
                               "ResponsePoints": OrderedDict({"NumOfStrs": 0}),
                               "ManualRefinePoints": OrderedDict({"NumOfStrs": 0}),
                               "CustomVerifyPoints": OrderedDict({"NumOfStrs": 0}), "Tolerances": []})


class CommonOptimetrics(object):
    """Common Optimetrics Methods Class"""
    @property
    def omodule(self):
        """ """
        return self._parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent, name, dictinputs, optimtype):
        self._parent = parent
        self.name = name
        self.soltype = optimtype

        inputd = copy.deepcopy(dictinputs)


        if optimtype == "OptiParametric":
            self.props = inputd or defaultparametricSetup
        if optimtype == "OptiDesignExplorer":
            self.props = inputd or defaultdxSetup
        if optimtype == "OptiOptimization":
            self.props = inputd or defaultoptiSetup
        if optimtype == "OptiSensitivity":
            self.props = inputd or defaultsensitivitySetup
        if optimtype == "OptiStatistical":
            self.props = inputd or defaultstatisticalSetup
        if optimtype == "OptiDXDOE":
            self.props = inputd or defaultdoeSetup

        if inputd:
            self.props.pop('ID', None)
            self.props.pop('NextUniqueID', None)
            self.props.pop('MoveBackwards', None)
            self.props.pop('GoalSetupVersion', None)
            self.props.pop('Version', None)
            self.props.pop('SetupType', None)
            if inputd.get("Sim. Setups"):
                setups = inputd["Sim. Setups"]
                for el in setups:
                    if type(self._parent.design_properties["SolutionManager"]['ID Map']['Setup']) is list:
                        for setup in self._parent.design_properties["SolutionManager"]['ID Map']['Setup']:
                            if setup['I'] == el:
                                setups[setups.index(el)]= setup['I']
                                break
                    else:
                        if self._parent.design_properties["SolutionManager"]['ID Map']['Setup']['I'] == el:
                            setups[setups.index(el)] = self._parent.design_properties["SolutionManager"]['ID Map']['Setup']['N']
                            break
            if inputd.get("Goals", None):
                oparams = self.omodule.GetChildObject(self.name).GetCalculationInfo()
                oparam = [i for i in oparams[0]]
                calculation = ["NAME:Goal"]
                calculation.extend(oparam)
                arg1 = OrderedDict()
                arg2dict(calculation, arg1)
                self.props['Goals'] = arg1

    @aedt_exception_handler
    def update(self, update_dictionary=None):
        """update a Setup based on stored properties. a dictionary can be provided as argument

        Parameters
        ----------
        update_dictionary :
            optional dictionary argument (Default value = None)

        Returns
        -------
        type
            Bool

        """
        if update_dictionary:
            for el in update_dictionary:
                self.props[el]=update_dictionary[el]

        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @aedt_exception_handler
    def create(self):
        """update a Setup based on stored properties.
        
        :return: Bool

        Parameters
        ----------

        Returns
        -------

        """
        arg = ["NAME:" + self.name]
        dict2arg(self.props, arg)
        self.omodule.InsertSetup(self.soltype, arg)
        return True

    @aedt_exception_handler
    def _add_calculation(self, reporttype, solution=None, domain="Sweep", calculation="", calculation_type="d",
                         calculation_value="", calculation_name=None):
        """

        Parameters
        ----------
        reporttype :
            
        solution :
             (Default value = None)
        domain :
             (Default value = "Sweep")
        calculation :
             (Default value = "")
        calculation_type :
             (Default value = "d")
        calculation_value :
             (Default value = "")
        calculation_name :
             (Default value = None)

        Returns
        -------

        """
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._parent.nominal_sweep

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
            var ="Time"
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", var, "Type:=", calculation_type, "DiscreteValues:=", calculation_value]})
        if "Goal" in self.props["Goals"]:
            if type(self.props["Goals"]["Goal"]) is not list:
                self.props["Goals"]["Goal"] = [self.props["Goals"]["Goal"], sweepdefinition]
            else:
                self.props["Goals"]["Goal"].append(sweepdefinition)
        else:
            self.props["Goals"]["Goal"] = sweepdefinition

        return self.update()

    @aedt_exception_handler
    def _add_goal(self, optigoalname,reporttype, solution=None, domain="Sweep", calculation="", calculation_type="discrete",
                  calc_val1="", calc_val2="", condition="==", goal_value=1, goal_weight=1, goal_name=None):
        """

        Parameters
        ----------
        optigoalname :
            
        reporttype :
            
        solution :
             (Default value = None)
        domain :
             (Default value = "Sweep")
        calculation :
             (Default value = "")
        calculation_type :
             (Default value = "discrete")
        calc_val1 :
             (Default value = "")
        calc_val2 :
             (Default value = "")
        condition :
             (Default value = "==")
        goal_value :
             (Default value = 1)
        goal_weight :
             (Default value = 1)
        goal_name :
             (Default value = None)

        Returns
        -------

        """
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._parent.nominal_sweep
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
            var ="Time"
        if calculation_type =="discrete":
            if type(calc_val1) is list:
                dr = ",".join(calc_val1)
            else:
                dr = calc_val1
            sweepdefinition["Ranges"] = OrderedDict(
                {"Range": ["Var:=", var, "Type:=", "d", "DiscreteValues:=", dr]})
        else:
            sweepdefinition["Ranges"] = OrderedDict({"Range": ["Var:=", var, "Type:=", calculation_type,
                                                               "Start:=", calc_val1, "Stop:=", calc_val2,
                                                               "DiscreteValues:=", ""]})
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]})
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)
        if "Goal" in self.props[optigoalname]:
            if type(self.props[optigoalname]["Goal"]) is not list:
                self.props[optigoalname]["Goal"] = [self.props[optigoalname]["Goal"], sweepdefinition]
            else:
                self.props[optigoalname]["Goal"].append(sweepdefinition)
        else:
            self.props[optigoalname]["Goal"] = sweepdefinition
        return self.update()


class DXSetups(object):
    """Design XPlorer Setups Class"""

    class Setup(CommonOptimetrics, object):
        """Setup Class"""
        def __init__(self, parent, name, dictinputs=None):
            CommonOptimetrics.__init__(self, parent, name, dictinputs=dictinputs, optimtype="OptiDesignExplorer")
            pass

        @aedt_exception_handler
        def add_calculation(self, calculation="", calculation_value="", reporttype="Modal Solution Data", solution=None, domain="Sweep",  calculation_name=None):
            """Add Calculation to DX Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_value :
                calculation value. eg. if sweep "1GHz) (Default value = "")
            calculation_name :
                 (Default value = None)

            Returns
            -------
            type
                bool

            """
            return self._add_calculation(reporttype=reporttype, solution=solution, domain=domain, calculation_type="d",
                                         calculation=calculation, calculation_value=calculation_value, calculation_name=calculation_name)

        @aedt_exception_handler
        def add_goal(self, calculation="", calculation_value="", calculation_type="discrete", calculation_stop="",
                     reporttype="Modal Solution Data", solution=None, domain="Sweep", goal_name=None, goal_value=1, goal_weight=1, condition="=="):
            """Add Goald to DX Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_type :
                discrete or range (Default value = "discrete")
            calculation_value :
                calculation value. eg. if sweep "1GHz). if discrete, it is discrete value or list, if range, it is start value (Default value = "")
            calculation_stop :
                calculation value. eg. if sweep "1GHz). if range it is the stop value (Default value = "")
            goal_name :
                 (Default value = None)
            goal_value :
                 (Default value = 1)
            goal_weight :
                 (Default value = 1)
            condition :
                 (Default value = "==")

            Returns
            -------
            type
                bool

            """
            return self._add_goal(optigoalname="CostFunctionGoals", reporttype=reporttype, solution=solution,
                                  domain=domain, calculation_type=calculation_type, calculation=calculation,
                                  calc_val1=calculation_value, calc_val2=calculation_stop, goal_name=goal_name,
                                  goal_weight=goal_weight, goal_value=goal_value, condition=condition)
    @property
    def parent(self):
        """ """
        return self._parent
    @property
    def optimodule(self):
        """ """
        return self.parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent):
        self._parent = parent
        self.setups = []
        if self._parent.design_properties:
            try:
                setups_data = self._parent.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if type(setups_data[data]) is OrderedDict and setups_data[data]['SetupType'] == "OptiDesignExplorer":
                        self.setups.append(self.Setup(parent, data, setups_data[data]))
            except:
                pass

    @aedt_exception_handler
    def add_dx_setup(self,variables_to_include, defaults_var_values=None, setupname=None, parametricname=None):
        """Add a DesignXplorer Basic Setup. User can customize all DX Options after the creation

        Parameters
        ----------
        variables_to_include :
            list of variables to include in DesignXplorer
        defaults_var_values :
            list of default variable values
        setupname :
            Optional Setup name. if none, the default analysis setup will be used
        parametricname :
            optional Parametric Name (Default value = None)

        Returns
        -------
        type
            Optimetrics Object Class

        """
        if not setupname:
            setupname = [self._parent.analysis_setup]
        elif type(setupname) is not list:
            setupname = [setupname]
        if not parametricname:
            parametricname = generate_unique_name("DesignXplorer")
        setup = self.Setup(self._parent, parametricname)
        setup.props["Sim. Setups"] = setupname
        setup.props['Sweeps'] = []
        if not defaults_var_values:
            for v in variables_to_include:
                sweepdefinition = OrderedDict()
                sweepdefinition["Variable"] = v
                if "$" in v:
                    sweepdefinition["Data"] = self._parent.oproject.GetVariableValue(v)
                else:
                    sweepdefinition["Data"] = self._parent.odesign.GetVariableValue(v)
                sweepdefinition["OffsetF1"] = False
                sweepdefinition["Synchronize"] = 0
        else:
            for v,vv in zip(variables_to_include, defaults_var_values):
                sweepdefinition = OrderedDict()
                sweepdefinition["Variable"] = v
                sweepdefinition["Data"] = vv
                sweepdefinition["OffsetF1"] = False
                sweepdefinition["Synchronize"] = 0
                setup.props['Sweeps'].append(sweepdefinition)
                setup.props["StartingPoint"][v] = vv
        setup.create()
        self.setups.append(setup)
        return setup


class ParametericsSetups(object):
    """Parametric Setup Class"""
    class Setup(CommonOptimetrics, object):
        """Setup Class"""
        def __init__(self, parent, name, dictinputs=None):
            CommonOptimetrics.__init__(self, parent, name, dictinputs=dictinputs, optimtype="OptiParametric")
            pass

        @aedt_exception_handler
        def add_variation(self, sweep_var, datarange):
            """Add a Variation to an existing Parametric Setup

            Parameters
            ----------
            sweep_var :
                Variable name
            datarange :
                Data Range

            Returns
            -------
            type
                Bool

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

        @aedt_exception_handler
        def add_calculation(self, calculation="", calculation_value="", reporttype="Modal Solution Data", solution=None,
                            domain="Sweep", calculation_name=None):
            """Add Calculation to Parametric Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_value :
                calculation value. eg. if sweep "1GHz) (Default value = "")
            calculation_name :
                 (Default value = None)

            Returns
            -------
            type
                bool

            """
            return self._add_calculation(reporttype=reporttype, solution=solution, domain=domain, calculation_type="d",
                                         calculation=calculation, calculation_value=calculation_value, calculation_name=calculation_name)



    @property
    def parent(self):
        """ """
        return self._parent

    @property
    def optimodule(self):
        """ """
        return self.parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent):
        self._parent = parent
        self.setups = []
        if self._parent.design_properties:
            try:
                setups_data = self._parent.design_properties["Optimetrics"]["OptimetricsSetups"]

                for data in setups_data:
                    if type(setups_data[data]) is OrderedDict and setups_data[data]['SetupType'] == "OptiParametric":
                        self.setups.append(self.Setup(parent, data, setups_data[data]))
            except:
                pass

    @aedt_exception_handler
    def add_parametric_setup(self, sweep_var, datarange, setupname=None, parametricname=None):
        """Add a Parametric Basic Setup. User can customize all Options after the creation

        Parameters
        ----------
        sweep_var :
            Variable name
        datarange :
            Data Range
        setupname :
            Optional Setup name. if none, the default analysis setup will be used
        parametricname :
            optional Parametric Name (Default value = None)

        Returns
        -------
        type
            Optimetrics Object Class

        """
        if not setupname:
            setupname = [self._parent.analysis_setup]
        elif type(setupname) is not list:
            setupname = [setupname]
        if not parametricname:
            parametricname = generate_unique_name("Parametric")
        setup = self.Setup(self._parent, parametricname)
        setup.props["Sim. Setups"] = setupname
        sweepdefinition = OrderedDict()
        sweepdefinition["Variable"] = sweep_var
        sweepdefinition["Data"] = datarange
        sweepdefinition["OffsetF1"] = False
        sweepdefinition["Synchronize"] = 0
        setup.props["Sweeps"]["SweepDefinition"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class SensitivitySetups(object):
    """Sensitivity Class"""
    class Setup(CommonOptimetrics, object):
        """Setup Class"""
        def __init__(self, parent, name, dictinputs=None):
            CommonOptimetrics.__init__(self, parent, name, dictinputs=dictinputs, optimtype="OptiSensitivity")
            pass

        @aedt_exception_handler
        def add_calculation(self, calculation="", calculation_value="", reporttype="Modal Solution Data", solution=None,
                            domain="Sweep", calculation_name=None):
            """Add Calculation to Sensitivity Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_value :
                calculation value. eg. if sweep "1GHz) (Default value = "")
            calculation_name :
                 (Default value = None)

            Returns
            -------
            type
                bool

            """
            return self._add_calculation(reporttype=reporttype, solution=solution, domain=domain, calculation_type="d",
                                         calculation=calculation, calculation_value=calculation_value, calculation_name=calculation_name)

    @property
    def parent(self):
        """ """
        return self._parent
    @property
    def optimodule(self):
        """ """
        return self.parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent):
        self._parent = parent
        self.setups = []
        if self._parent.design_properties:
            try:
                setups_data = self._parent.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if type(setups_data[data]) is OrderedDict and setups_data[data]['SetupType'] == "OptiSensitivity":
                        self.setups.append(self.Setup(parent, data, setups_data[data]))
            except:
                pass

    @aedt_exception_handler
    def add_sensitivity(self, calculation, calculation_value, calculation_type="Freq",
                        reporttype="Modal Solution Data", domain="Sweep", solution=None, parametricname=None):
        """Add a Sensitivity Basic Setup. User can customize all Options after the creation

        Parameters
        ----------
        calculation :
            name of the Calculation
        calculation_value :
            Variation Value (eg. "1GHz")
        calculation_type :
            Variation type. Default Freq
        reporttype :
            Report Type. Default "Modal Solution Data"
        domain :
            Default "Sweep"
        solution :
            Solution name. If nothing, nominal sweep will be used (Default value = None)
        parametricname :
            Name of the sensititivy analsysis. if nothing, a default name will be given

        Returns
        -------
        type
            Sensitivity object

        """
        if not parametricname:
            parametricname = generate_unique_name("Sensitivity")
        setup = self.Setup(self._parent, parametricname)
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._parent.nominal_sweep
        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        sweepdefinition["Name"] = calculation
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", calculation_type, "Type:=", "d", "DiscreteValues:=", calculation_value]})
        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class StatisticalSetups(object):
    """Statistical Class"""
    class Setup(CommonOptimetrics, object):
        """Setup Class"""
        def __init__(self, parent, name, dictinputs=None):
            CommonOptimetrics.__init__(self, parent, name, dictinputs=dictinputs, optimtype="OptiStatistical")
            pass

        @aedt_exception_handler
        def add_calculation(self, calculation="", calculation_value="", reporttype="Modal Solution Data", solution=None, domain="Sweep",  calculation_name=None):
            """Add Calculation to Statistical Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_value :
                calculation value. eg. if sweep "1GHz) (Default value = "")
            calculation_name :
                 (Default value = None)

            Returns
            -------
            type
                bool

            """
            return self._add_calculation(reporttype=reporttype, solution=solution, domain=domain, calculation_type="d",
                                         calculation=calculation, calculation_value=calculation_value, calculation_name=calculation_name)

    @property
    def parent(self):
        """ """
        return self._parent
    @property
    def optimodule(self):
        """ """
        return self.parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent):
        self._parent = parent
        self.setups = []
        if self._parent.design_properties:
            try:
                setups_data = self._parent.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if type(setups_data[data]) is OrderedDict and setups_data[data]['SetupType'] == "OptiStatistical":
                        self.setups.append(self.Setup(parent, data, setups_data[data]))
            except:
                pass

    @aedt_exception_handler
    def add_statistical(self, calculation_name, calc_variation_value, calculation_type="Freq",
                        reporttype="Modal Solution Data", domain="Sweep", solution=None, parametricname=None):
        """Add a Sensitivity Basic Setup. User can customize all Options after the creation

        Parameters
        ----------
        calculation_name :
            name of the Calculation
        calc_variation_value :
            Variation Value (eg. "1GHz")
        calculation_type :
            Variation type. Default Freq
        reporttype :
            Report Type. Default "Modal Solution Data"
        domain :
            Default "Sweep"
        solution :
            Solution name. If nothing, nominal sweep will be used (Default value = None)
        parametricname :
            Name of the sensititivy analsysis. if nothing, a default name will be given

        Returns
        -------
        type
            Statistical object

        """
        if not parametricname:
            parametricname = generate_unique_name("Statistical")
        setup = self.Setup(self._parent, parametricname)
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._parent.nominal_sweep

        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation_name
        sweepdefinition["Name"] = calculation_name
        sweepdefinition["Ranges"] = OrderedDict({"Range": ["Var:=", calculation_type,	"Type:=", "d", "DiscreteValues:=", calc_variation_value]})
        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class DOESetups(object):
    """DOE Class"""
    class Setup(CommonOptimetrics, object):
        """Setup Class"""
        def __init__(self, parent, name, dictinputs=None):
            CommonOptimetrics.__init__(self, parent, name, dictinputs=dictinputs, optimtype="OptiDXDOE")
            pass
        @aedt_exception_handler
        def add_calculation(self, calculation="", calculation_value="", reporttype="Modal Solution Data", solution=None,
                            domain="Sweep", calculation_name=None):
            """Add Calculation to DOE Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_value :
                calculation value. eg. if sweep "1GHz) (Default value = "")
            calculation_name :
                 (Default value = None)

            Returns
            -------
            type
                bool

            """
            return self._add_calculation(reporttype=reporttype, solution=solution, domain=domain, calculation_type="d",
                                         calculation=calculation, calculation_value=calculation_value, calculation_name=calculation_name)

        @aedt_exception_handler
        def add_goal(self, calculation="", calculation_value="", calculation_type="discrete",
                     calculation_stop="", reporttype="Modal Solution Data", solution=None, domain="Sweep", goal_name=None, goal_value=1, goal_weight=1, condition="=="):
            """Add Goald to DOE Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_type :
                discrete or range (Default value = "discrete")
            calculation_value :
                calculation value. eg. if sweep "1GHz). if discrete, it is discrete value or list, if range, it is start value (Default value = "")
            calculation_stop :
                calculation value. eg. if sweep "1GHz). if range it is the stop value (Default value = "")
            goal_name :
                 (Default value = None)
            goal_value :
                 (Default value = 1)
            goal_weight :
                 (Default value = 1)
            condition :
                 (Default value = "==")

            Returns
            -------
            type
                bool

            """
            return self._add_goal(optigoalname="CostFunctionGoals", reporttype=reporttype, solution=solution,
                                  domain=domain, calculation_type=calculation_type, calculation=calculation,
                                  calc_val1=calculation_value, calc_val2=calculation_stop, goal_name=goal_name,
                                  goal_weight=goal_weight,
                                  goal_value=goal_value, condition=condition)

    @property
    def parent(self):
        """ """
        return self._parent
    @property
    def optimodule(self):
        """ """
        return self.parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent):
        self._parent = parent
        self.setups = []
        if self._parent.design_properties:
            try:
                setups_data = self._parent.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if type(setups_data[data]) is OrderedDict and setups_data[data]['SetupType'] == "OptiDXDOE":
                        self.setups.append(self.Setup(parent, data, setups_data[data]))
            except:
                pass

    @aedt_exception_handler
    def add_doe(self, calculation, calculation_value, calculation_type="Freq", reporttype="Modal Solution Data",
                domain="Sweep", condition="<=", goal_value=1, goal_weight=1, solution=None, parametricname=None):
        """Add a DOE Basic Setup. User can customize all Options after the creation

        Parameters
        ----------
        calculation :
            name of the Calculation
        calculation_value :
            Variation Value (eg. "1GHz")
        calculation_type :
            Variation type. Default Freq
        reporttype :
            Report Type. Default "Modal Solution Data"
        domain :
            Default "Sweep"
        condition :
            goal condition. Default "<="
        goal_value :
            goal value to meet condition. Default 1
        goal_weight :
            goal weight. Default 1
        solution :
            Solution name. If nothing, nominal sweep will be used (Default value = None)
        parametricname :
            Name of the sensititivy analsysis. if nothing, a default name will be given

        Returns
        -------
        type
            DOE object

        """
        if not solution:
            solution = self._parent.nominal_sweep
        setupname = [solution.split(" ")[0]]
        if not parametricname:
            parametricname = generate_unique_name("DesignOfExp")
        setup = self.Setup(self._parent, parametricname)
        setup.props["Sim. Setups"] = setupname
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype

        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        sweepdefinition["Name"] = calculation
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", calculation_type, "Type:=", "d", "DiscreteValues:=", calculation_value]})
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]})
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)
        setup.props["CostFunctionGoals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class OptimizationSetups(object):
    """Optimization Class"""
    class Setup(CommonOptimetrics, object):
        """Setup Class"""
        def __init__(self, parent, name, dictinputs=None):
            CommonOptimetrics.__init__(self, parent, name, dictinputs=dictinputs, optimtype="OptiOptimization")
            pass

        @aedt_exception_handler
        def add_goal(self, calculation="", calculation_value="", calculation_type="discrete", calculation_stop="",
                     reporttype="Modal Solution Data", solution=None, domain="Sweep", goal_name=None, goal_value=1,
                     goal_weight=1, condition="=="):
            """Add Calculation to Optimetrics Setup

            Parameters
            ----------
            reporttype :
                Name of the Report to take the Calculation (Default value = "Modal Solution Data")
            solution :
                solution type. if none, default solution will be taken
            domain :
                domain type. if none sweep will be taken (Default value = "Sweep")
            calculation :
                calculation value eg. dB(S(1,1,)) (Default value = "")
            calculation_type :
                discrete or range (Default value = "discrete")
            calculation_value :
                calculation value. eg. if sweep "1GHz). if discrete, it is discrete value or list, if range, it is start value (Default value = "")
            calculation_stop :
                calculation value. eg. if sweep "1GHz). if range it is the stop value (Default value = "")
            goal_value :
                goal Value. Default 1
            goal_weight :
                Goal Weight. Default 1
            condition :
                Condition. Default "=="
            goal_name :
                 (Default value = None)

            Returns
            -------
            type
                bool

            """
            return self._add_goal(optigoalname="Goals", reporttype=reporttype, solution=solution, domain=domain,
                                  calculation_type=calculation_type, calculation=calculation,
                                  calc_val1=calculation_value, calc_val2=calculation_stop, goal_name=goal_name, goal_value=goal_value, goal_weight=goal_weight, condition=condition)

    @property
    def parent(self):
        """ """
        return self._parent
    @property
    def optimodule(self):
        """ """
        return self.parent.odesign.GetModule("Optimetrics")

    def __init__(self, parent):
        self._parent = parent
        self.setups = []
        if self._parent.design_properties:
            try:
                setups_data = self._parent.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if type(setups_data[data]) is OrderedDict and setups_data[data]['SetupType'] == "OptiOptimization":
                        self.setups.append(self.Setup(parent, data, setups_data[data]))
            except:
                pass



    @aedt_exception_handler
    def add_optimization(self, calculation, calculation_value, calculation_type="Freq",
                         reporttype="Modal Solution Data", domain="Sweep", condition="<=", goal_value=1, goal_weight=1,
                         solution=None, parametricname=None):
        """Add a Optimization Basic Setup. User can customize all Options after the creation

        Parameters
        ----------
        calculation :
            name of the Calculation
        calculation_value :
            Variation Value (eg. "1GHz")
        calculation_type :
            Variation type. Default Freq
        reporttype :
            Report Type. Default "Modal Solution Data"
        domain :
            Default "Sweep"
        condition :
            goal condition. Default "<="
        goal_value :
            goal value to meet condition. Default 1
        goal_weight :
            goal weight. Default 1
        solution :
            Solution name. If nothing, nominal sweep will be used (Default value = None)
        parametricname :
            Name of the sensititivy analsysis. if nothing, a default name will be given

        Returns
        -------
        type
            Optimization object

        """
        if not parametricname:
            parametricname = generate_unique_name("Optimization")
        setup = self.Setup(self._parent, parametricname)
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._parent.nominal_sweep
        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        sweepdefinition["Name"] = calculation
        sweepdefinition["Ranges"] = OrderedDict({"Range": ["Var:=", calculation_type,	"Type:=", "d", "DiscreteValues:=", calculation_value]})
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]})
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)

        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup
