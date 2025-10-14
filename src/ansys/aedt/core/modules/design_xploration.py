# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import copy
import csv
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SolutionsHfss
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.data_handlers import _arg2dict
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import PropsManager
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modules.optimetrics_templates import defaultdoeSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultdxSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultoptiSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultparametricSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultsensitivitySetup
from ansys.aedt.core.modules.optimetrics_templates import defaultstatisticalSetup
from ansys.aedt.core.modules.solve_sweeps import SetupProps


class CommonOptimetrics(PropsManager, PyAedtBase):
    """Creates and sets up optimizations.

    Parameters
    ----------
    p_app : :class:`ansys.aedt.core.application.analysis.Analysis`
        PyAEDT analysis instance.
    name : str
        Optimetrics setup name.
    dictinputs : dict
        Input setup parameters.
    optimtype : str
        Type of the optimization. Available options are: ``"OptiParametric"``, ``"OptiDesignExplorer"`,
        ``"OptiOptimization"``, ``"OptiSensitivity"``, ``"OptiStatistical"``, ``"OptiDXDOE"``, and ``"optiSLang"``.
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
            if not inputd and self._app.design_type == "Icepak":
                self.props["ProdOptiSetupDataV2"] = {
                    "SaveFields": False,
                    "FastOptimetrics": False,
                    "SolveWithCopiedMeshOnly": True,
                }
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
        if optimtype == "optiSLang":
            self.props = SetupProps(self, inputd or copy.deepcopy(defaultdxSetup))
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
                    try:
                        if isinstance(self._app.design_properties["SolutionManager"]["ID Map"]["Setup"], list):
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
                    except (TypeError, KeyError):
                        pass

            if inputd.get("Goals", None) and self.name in self.omodule.GetChildNames():
                if self._app._is_object_oriented_enabled():
                    oparams = self.omodule.GetChildObject(self.name).GetCalculationInfo()
                    oparam = [i for i in oparams[0]]
                    idx = None
                    if oparam[0] in oparam[1:]:
                        idx = oparam[1:].index(oparam[0]) + 1
                    if idx:
                        oparam = [["NAME:Goal"] + oparam[k : idx + k] for k in range(0, len(oparam), idx)]
                    else:
                        oparam = [["NAME:Goal"] + oparam]

                    self.props["Goals"]["Goal"] = []
                    for param in oparam:
                        arg1 = {}
                        _arg2dict(param, arg1)
                        self._get_setup_props(arg1)
                        self.props["Goals"]["Goal"].append(SetupProps(self, arg1["Goal"]))

            if inputd.get("Variables"):  # pragma: no cover
                for var in inputd.get("Variables"):
                    output_list = []
                    props = self.props["Variables"][var]
                    for prop in props:
                        parts = prop.split("=")
                        value = (
                            True
                            if parts[1].lower() == "true"
                            else False
                            if parts[1].lower() == "false"
                            else parts[1].strip("'")
                        )
                        output_list.extend([parts[0] + ":=", value])
                    self.props["Variables"][var] = output_list

        self.auto_update = True

    def _get_setup_props(self, arg1: Dict[str, Any]) -> None:
        for k, v in arg1.items():
            if isinstance(v, dict):
                arg1[k] = SetupProps(self, v)
                self._get_setup_props(v)
            elif isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, dict):
                        v[idx] = SetupProps(self, item)

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
        is_goal=False,
    ):
        did = 3
        if domain != "Sweep":
            did = 1
        sweep_definition = {"ReportType": report_category}
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        sweep_definition["Solution"] = setup_sweep_name
        ctxt = {}

        if self._app.solution_type in ["TR", "AC", "DC"]:
            ctxt["SimValueContext"] = [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]
            setup_sweep_name = self._app.solution_type
            sweep_definition["Solution"] = setup_sweep_name

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
            ctxt = {"Domain": domain}
        sweep_definition["SimValueContext"] = ctxt
        sweep_definition["Calculation"] = expressions
        sweep_definition["Name"] = expressions
        sweep_definition["Ranges"] = {}
        if context and context in self._app.modeler.line_names and intrinsics and "Distance" not in intrinsics:
            sweep_definition["Ranges"]["Range"] = ("Var:=", "Distance", "Type:=", "a")
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
                r = {}
                if not k:
                    r = {"Var": v, "Type": "a"}
                elif isinstance(k, tuple):
                    r = {"Var": v, "Type": "rd", "Start": k[0], "Stop": k[1], "DiscreteValues": ""}
                elif isinstance(k, (list, str)):
                    r = {"Var": v, "Type": "d", "DiscreteValues": ",".join(k) if isinstance(k, list) else k}
                r = SetupProps(self, r)
                if not sweep_definition["Ranges"]:
                    sweep_definition["Ranges"]["Range"] = [r]
                elif isinstance(sweep_definition["Ranges"]["Range"], list):
                    sweep_definition["Ranges"]["Range"].append(r)
                else:
                    sweep_definition["Ranges"]["Range"] = [sweep_definition["Ranges"]["Range"]]
                    sweep_definition["Ranges"]["Range"].append(r)
        if is_goal:
            sweep_definition["Condition"] = condition
            goal_value = {
                "GoalValueType": "Independent",
                "Format": "Real/Imag",
                "bG": ["v:=", f"[{goal_value};]"],
            }
            goal_value = SetupProps(self, goal_value)
            sweep_definition["GoalValue"] = goal_value
            sweep_definition["Weight"] = f"[{goal_weight};]"
        return sweep_definition

    @pyaedt_function_handler()
    def update(self, update_dictionary: Optional[Dict[str, Any]] = None) -> bool:
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

        if self.soltype == "OptiParametric" and len(arg[8]) == 3:
            arg[8] = ["NAME:Sweep Operations"]
            for variation in self.props["Sweep Operations"].get("add", []):
                arg[8].append("add:=")
                arg[8].append(variation)

        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def create(self) -> bool:
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
    def add_calculation(
        self,
        calculation,
        ranges=None,
        variables=None,
        solution=None,
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        report_type=None,
    ):
        """Add a calculation to the setup.

        Parameters
        ----------
        calculation : str, optional
            Name of the calculation.
        ranges : dict, optional
            Dictionary of ranges with respective values.
            Values can be: `None` for all values, a List of Discrete Values, a tuple of start and stop range.
            It includes intrinsics like "Freq", "Time", "Theta", "Distance".
            The default is ``None``, to be used e.g. in "Eigenmode" design type.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        context : str, optional
            Calculation contexts. It can be a sphere, a matrix or a polyline.
        subdesign_id : int, optional
            Subdesign id for Circuit and HFSS 3D Layout objects.
        polyline_points : int, optional
            Number of points for Polyline context.
        report_type : str, optional
            Override the auto computation of Calculation Type.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup
        """
        return self._add_calculation(
            calculation,
            ranges,
            variables,
            solution,
            context,
            subdesign_id,
            polyline_points,
            report_type,
            is_goal=False,
        )

    @pyaedt_function_handler()
    def _add_calculation(
        self,
        calculation,
        ranges=None,
        variables=None,
        solution=None,
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        report_type=None,
        is_goal=False,
        condition="<=",
        goal_value=1,
        goal_weight=1,
    ):
        self.auto_update = False
        if not solution:
            solution = self._app.nominal_sweep
        setupname = solution.split(" ")[0]
        if setupname not in self.props["Sim. Setups"]:
            self.props["Sim. Setups"].append(setupname)
        domain = "Time"
        aedt_version = settings.aedt_version
        maxwell_solutions = SolutionsMaxwell3D.versioned(aedt_version)
        if (ranges and ("Freq" in ranges or "Phase" in ranges or "Theta" in ranges)) or self._app.solution_type in [
            maxwell_solutions.Magnetostatic,
            maxwell_solutions.ElectroStatic,
            maxwell_solutions.EddyCurrent,
            maxwell_solutions.ACMagnetic,
            maxwell_solutions.DCConduction,
            SolutionsHfss.EigenMode,
        ]:
            domain = "Sweep"
        if not report_type:
            report_type = self._app.design_solutions.report_type
            if context and context in self._app.modeler.sheet_names:
                report_type = "Fields"
            elif self._app.solution_type in ["Q3D Extractor", "2D Extractor"]:
                report_type = "Matrix"
            elif context:
                try:
                    for f in self._app.field_setups:
                        if context == f.name:
                            report_type = "Far Fields"
                except Exception:
                    self._app.logger.debug(
                        "An error occurred when handling `report_type` while adding calculation."
                    )  # pragma: no cover
        sweepdefinition = self._get_context(
            calculation,
            condition,
            goal_weight,
            goal_value,
            solution,
            domain,
            ranges,
            report_type,
            context,
            subdesign_id,
            polyline_points,
            is_goal,
        )
        dx_variables = {}
        if variables:
            for el in list(variables):
                try:
                    dx_variables[el] = self._app[el]
                except Exception:
                    self._app.logger.debug("An error occurred while adding calculation.")  # pragma: no cover
        for v in list(dx_variables.keys()):
            self._activate_variable(v)
        if self.soltype in ["OptiDesignExplorer", "OptiDXDOE"] and is_goal:
            optigoalname = "CostFunctionGoals"
        else:
            optigoalname = "Goals"
        if "Goal" in self.props[optigoalname]:
            if type(self.props[optigoalname]["Goal"]) is not list:
                self.props[optigoalname]["Goal"] = [self.props[optigoalname]["Goal"], SetupProps(self, sweepdefinition)]
            else:
                self.props[optigoalname]["Goal"].append(sweepdefinition)
        else:
            self.props[optigoalname] = {}
            self.props[optigoalname]["Goal"] = sweepdefinition
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def _activate_variable(self, variable_name):
        if self.soltype in ["OptiDesignExplorer", "OptiDXDOE", "OptiOptimization", "optiSLang"]:
            self._app.activate_variable_optimization(variable_name)
        elif self.soltype == "OptiParametric":
            self._app.activate_variable_tuning(variable_name)
        elif self.soltype == "OptiSensitivity":
            self._app.activate_variable_sensitivity(variable_name)
        elif self.soltype == "OptiStatistical":
            self._app.activate_variable_statistical(variable_name)

    @pyaedt_function_handler(num_cores="cores", num_tasks="tasks", num_gpu="gpus")
    def analyze(
        self,
        cores: int = 1,
        tasks: int = 1,
        gpus: int = 0,
        acf_file: str = None,
        use_auto_settings: bool = True,
        solve_in_batch: bool = False,
        machine: str = "localhost",
        run_in_thread: bool = False,
        revert_to_initial_mesh: bool = False,
        blocking: bool = True,
    ) -> bool:
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
        return self._app.analyze(
            setup=self.name,
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


class SetupOpti(CommonOptimetrics, PyAedtBase):
    """Sets up an optimization in Opimetrics."""

    def __init__(self, app, name, dictinputs=None, optim_type="OptiDesignExplorer"):
        CommonOptimetrics.__init__(self, app, name, dictinputs=dictinputs, optimtype=optim_type)

    @pyaedt_function_handler()
    def delete(self):
        """Delete a defined Optimetrics Setup.

        Parameters
        ----------
        name : str
            Name of optimetrics setup to delete.

        Returns
        -------
        bool
            `True` if setup is deleted. `False` if it failed.
        """
        self.omodule.DeleteSetups([self.name])
        self._app.optimizations.setups.remove(self)
        return True

    @pyaedt_function_handler()
    def add_goal(
        self,
        calculation,
        ranges,
        variables=None,
        solution=None,
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        report_type=None,
        condition="<=",
        goal_value=1,
        goal_weight=1,
    ):
        """Add a goal to the setup.

        Parameters
        ----------
        calculation : str, optional
            Name of the calculation.
        ranges : dict
            Dictionary of ranges with respective values.
            Values can be: `None` for all values, a List of Discrete Values, a tuple of start and stop range.
            It includes intrinsics like "Freq", "Time", "Theta", "Distance".
        variables : list, optional
            List of variables to include in the optimization.
        condition : string, optional
            The default is ``"<="``.
        goal_value : optional
            Value for the goal. The default is ``1``.
        goal_weight : optional
            Value for the goal weight. The default is ``1``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        context : str, optional
            Calculation contexts. It can be a sphere, a matrix or a polyline.
        subdesign_id : int, optional
            Subdesign id for Circuit and HFSS 3D Layout objects.
        polyline_points : int, optional
            Number of points for Polyline context.
        report_type : str, optional
            Override the auto computation of Calculation Type.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup
        """
        return self._add_calculation(
            calculation,
            ranges,
            variables,
            solution,
            context,
            subdesign_id,
            polyline_points,
            report_type,
            True,
            condition,
            goal_value,
            goal_weight,
        )

    @pyaedt_function_handler()
    def add_variation(
        self,
        variable_name,
        min_value,
        max_value,
        starting_point=None,
        min_step=None,
        max_step=None,
        use_manufacturable=False,
        levels=None,
    ):
        """Add a new variable as input for the optimization and defines its ranges.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        min_value : float
            Minimum Optimization Value for variable_name.
        max_value : float
            Maximum Optimization Value for variable_name.
        starting_point : float, optional
            Starting point for optimization. If None, default will be used.
        min_step : float
            Minimum Step Size for optimization. If None, 1/100 of the range will be used.
        max_step : float
            Maximum Step Size for optimization. If None, 1/10 of the range will be used.
        use_manufacturable : bool
            Either if to use or not the manufacturable values. Default is False.
        levels : list, optional
            List of available manufacturer levels.

        Returns
        -------
        bool
        """
        if variable_name not in self._app.variable_manager.variables:
            self._app.logger.error(f"Variable {variable_name} does not exists.")
            return False
        self.auto_update = False
        self._activate_variable(variable_name)

        if not min_step:
            min_step = (max_value - min_value) / 100
        min_step = self._app.value_with_units(min_step, self._app.variable_manager[variable_name].units)

        if not max_step:
            max_step = (max_value - min_value) / 10
        if levels is None:
            levels = f"[{min_value}: {max_value}] mm"
        else:
            levels = f"{levels} {self._app.variable_manager[variable_name].units}"
        max_step = self._app.value_with_units(max_step, self._app.variable_manager[variable_name].units)
        min_value_wuints = self._app.value_with_units(min_value, self._app.variable_manager[variable_name].units)
        max_value_wuints = self._app.value_with_units(max_value, self._app.variable_manager[variable_name].units)

        if self.soltype in "OptiDXDOE":
            self._app.variable_manager.variables[variable_name].optimization_max_value = max_value_wuints
            self._app.variable_manager.variables[variable_name].optimization_min_value = min_value_wuints
            self.auto_update = True
            return True
        elif self.soltype in ["optiSLang", "OptiDesignExplorer"]:
            self._app.variable_manager.variables[variable_name].optimization_max_value = max_value_wuints
            self._app.variable_manager.variables[variable_name].optimization_min_value = min_value_wuints
            input_variables = self.props["Sweeps"]["SweepDefinition"]
            cont = 0
            variable_included = False
            for var in input_variables:
                if var["Variable"] == variable_name:
                    self.props["Sweeps"]["SweepDefinition"][cont]["Data"] = self._app.variable_manager.variables[
                        variable_name
                    ].evaluated_value
                    variable_included = True
                    break
                cont += 1
            if not variable_included:
                sweepdefinition = {}
                sweepdefinition["Variable"] = variable_name
                sweepdefinition["Data"] = self._app.variable_manager.variables[variable_name].evaluated_value
                sweepdefinition["OffsetF1"] = False
                sweepdefinition["Synchronize"] = 0
                self.props["Sweeps"]["SweepDefinition"].append(sweepdefinition)
        elif self.soltype == "OptiParametric":
            self._app.activate_variable_tuning(variable_name)
        elif self.soltype == "OptiSensitivity":
            self._app.activate_variable_sensitivity(variable_name)
        elif self.soltype == "OptiStatistical":
            self._app.activate_variable_statistical(variable_name)
        else:
            use_manufacturable = "true" if use_manufacturable else "false"
            arg = [
                "i:=",
                True,
                "int:=",
                False,
                "Min:=",
                min_value_wuints,
                "Max:=",
                max_value_wuints,
                "MinStep:=",
                min_step,
                "MaxStep:=",
                max_step,
                "MinFocus:=",
                min_value_wuints,
                "MaxFocus:=",
                max_value_wuints,
                "UseManufacturableValues:=",
                use_manufacturable,
            ]
            if self._app.aedt_version_id > "2023.2":
                arg.extend(["Level:=", levels])
            if not self.props.get("Variables", None):
                self.props["Variables"] = {}
            self.props["Variables"][variable_name] = arg
            if not self.props.get("StartingPoint", None):
                self.props["StartingPoint"] = {}
            if not starting_point:
                starting_point = self._app.variable_manager[variable_name].numeric_value
                if starting_point < min_value or starting_point > max_value:
                    starting_point = (max_value + min_value) / 2

            self.props["StartingPoint"][variable_name] = self._app.value_with_units(
                starting_point, self._app.variable_manager[variable_name].units
            )
        self.auto_update = True
        self.update()
        return True


class SetupParam(CommonOptimetrics, PyAedtBase):
    """Sets up a parametric analysis in Optimetrics."""

    def __init__(self, p_app, name, dictinputs=None, optim_type="OptiParametric"):
        CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype=optim_type)
        pass

    @pyaedt_function_handler()
    def delete(self):
        """Delete a defined Optimetrics Setup.

        Returns
        -------
        bool
            ``True`` if setup is deleted. ``False`` if it failed.
        """
        self.omodule.DeleteSetups([self.name])
        self._app.parametrics.setups.remove(self)
        return True

    @pyaedt_function_handler(sweep_var="sweep_variable", unit="units")
    def add_variation(
        self, sweep_variable, start_point, end_point=None, step=100, units=None, variation_type="LinearCount"
    ):
        """Add a variation to an existing parametric setup.

        Parameters
        ----------
        sweep_variable : str
            Name of the variable.
        start_point : float or int
            Variation Start Point.
        end_point : float or int, optional
            Variation End Point. This parameter is optional if a Single Value is defined.
        step : float or int, optional
            Variation Step or Count depending on variation_type. Default is `100`.
        units : str, optional
            Variation units. Default is `None`.
        variation_type : str, optional
            Variation Type. Admitted values are `"SingleValue", `"LinearCount"`, `"LinearStep"`,
            `"DecadeCount"`, `"OctaveCount"`, `"ExponentialCount"`.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup
        """
        if sweep_variable not in self._app.variable_manager.variables:
            self._app.logger.error(f"Variable {sweep_variable} does not exists.")
            return False
        sweep_range = ""
        if not units:
            units = self._app.variable_manager[sweep_variable].units
        start_point = self._app.value_with_units(start_point, units)
        if variation_type != "SingleValue":
            end_point = self._app.value_with_units(end_point, units)
        if variation_type == "LinearCount":
            sweep_range = f"LINC {start_point} {end_point} {step}"
        elif variation_type == "LinearStep":
            sweep_range = f"LIN {start_point} {end_point} {self._app.value_with_units(step, units)}"
        elif variation_type == "DecadeCount":
            sweep_range = f"DEC {start_point} {end_point} {step}"
        elif variation_type == "OctaveCount":
            sweep_range = f"OCT {start_point} {end_point} {step}"
        elif variation_type == "ExponentialCount":
            sweep_range = f"ESTP {start_point} {end_point} {step}"
        elif variation_type == "SingleValue":
            sweep_range = f"{start_point}"
        if not sweep_range:
            return False
        self._activate_variable(sweep_variable)
        sweepdefinition = {}
        sweepdefinition["Variable"] = sweep_variable
        sweepdefinition["Data"] = sweep_range
        sweepdefinition["OffsetF1"] = False
        sweepdefinition["Synchronize"] = 0
        if self.props["Sweeps"]["SweepDefinition"] is None:
            self.props["Sweeps"]["SweepDefinition"] = sweepdefinition
        elif type(self.props["Sweeps"]["SweepDefinition"]) is not list:
            self.props["Sweeps"]["SweepDefinition"] = [self.props["Sweeps"]["SweepDefinition"]]
            self._append_sweepdefinition(sweepdefinition)
        else:
            self._append_sweepdefinition(sweepdefinition)

        return self.update()

    @pyaedt_function_handler()
    def _append_sweepdefinition(self, sweepdefinition):
        for sweep_def in self.props["Sweeps"]["SweepDefinition"]:
            if sweepdefinition["Variable"] == sweep_def["Variable"]:
                sweep_def["Data"] += " " + sweepdefinition["Data"]
                return True
        self.props["Sweeps"]["SweepDefinition"].append(sweepdefinition)
        return True

    @pyaedt_function_handler()
    def sync_variables(self, variables, sync_n=1):
        """Sync variable variations in an existing parametric setup.
        Setting the sync number to `0` will effectively unsync the variables.

        Parameters
        ----------
        variables : list
            List of variables to sync.
        sync_n : int, optional
            Sync number. Sweep variables with the same Sync number will be synchronizad.
            Default is `1`.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup
        """
        if type(self.props["Sweeps"]["SweepDefinition"]) is not list:
            self._app.logger.error("Not enough variables are defined in the Parametric setup")
            return False
        existing_variables = [s["Variable"] for s in self.props["Sweeps"]["SweepDefinition"]]
        undo_vals = {}
        for v in variables:
            if v not in existing_variables:
                self._app.logger.error(f"Variable {v} is not defined in the Parametric setup")
                return False
        legacy_update = self.auto_update
        self.auto_update = False
        for v in variables:
            for sweep_def in self.props["Sweeps"]["SweepDefinition"]:
                if v == sweep_def["Variable"]:
                    undo_vals[v] = sweep_def["Synchronize"]
                    sweep_def["Synchronize"] = sync_n
        try:
            self.update()
        except Exception:  # pragma: no cover
            # If it fails to sync (due to e.g. different number of variations), reverts to original values.
            for v in variables:
                for sweep_def in self.props["Sweeps"]["SweepDefinition"]:
                    if v == sweep_def["Variable"]:
                        sweep_def["Synchronize"] = undo_vals[v]
            self._app.logger.error("Failed to sync the Parametric setup.")
            self.auto_update = legacy_update
            return False
        self.auto_update = legacy_update
        return True

    @pyaedt_function_handler(filename="output_file")
    def export_to_csv(self, output_file):
        """Export the current Parametric Setup to csv.

        Parameters
        ----------
        output_file : str
            Full Path to the csv file.

        Returns
        -------
        bool
            `True` if the export is correctly executed.
        """
        self.omodule.ExportParametricSetupTable(self.name, output_file)
        return True


class ParametricSetups(PyAedtBase):
    """Sets up Parametrics analyses. It includes Parametrics, Sensitivity and Statistical Analysis.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
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
                    if isinstance(setups_data[data], dict) and setups_data[data]["SetupType"] == "OptiParametric":
                        self.setups.append(SetupParam(p_app, data, setups_data[data], setups_data[data]["SetupType"]))
            except Exception:
                self._app.logger.debug(
                    "An error occurred while creating an instance of ParametricSetups."
                )  # pragma: no cover

    @property
    def design_setups(self):
        """All design setups ordered by name.

        Returns
        -------
        dict[str, :class:`ansys.aedt.core.modules.solve_setup.Setup`]
        """
        return {i.name.split(":")[0].strip(): i for i in self.setups}

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

    @pyaedt_function_handler(sweep_var="variable", parametricname="name")
    def add(
        self,
        variable,
        start_point,
        end_point=None,
        step=100,
        variation_type="LinearCount",
        solution=None,
        name=None,
    ):
        """Add a basic sensitivity analysis.
        You can customize all options after the analysis is added.

        Parameters
        ----------
        variable : str
            Name of the variable.
        start_point : float, int or str
            Variation Start Point if a variation is defined or Single Value.
        end_point : float or int, optional
            Variation End Point. This parameter is optional if a Single Value is defined.
        step : float, int, or str
            Variation Step or Count depending on variation_type. The default is ``100``
            for the "LinearCount" variation_type. If a string is passed as an argument, it
            must be a valid expression in the given context. For example, "0.1mm" may be passed
            for a step size when the variation_type is "LinearStep".
        variation_type : str, optional
            Variation Type. Permitted values are `"LinearCount"`, `"LinearStep"`, `"LogScale"`, `"SingleValue"`.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        name : str, optional
            Name of the sensitivity analysis. The default is ``None``, in which case
            a default name is assigned.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.SetupParam`
            Optimization Object.

        References
        ----------
        >>> oModule.InsertSetup
        """
        if variable not in self._app.variable_manager.variables:
            self._app.logger.error(f"Variable {variable} not found.")
            return False
        if not solution and not self._app.nominal_sweep:
            self._app.logger.error("At least one setup is needed.")
            return False
        if not solution:
            solution = self._app.nominal_sweep
        setupname = solution.split(" ")[0]
        if not name:
            name = generate_unique_name("Parametric")
        setup = SetupParam(self._app, name, optim_type="OptiParametric")
        setup.auto_update = False

        setup.props["Sim. Setups"] = [setupname]
        setup.props["Sweeps"] = {"SweepDefinition": None}
        setup.create()
        unit = self._app.variable_manager[variable].units
        setup.add_variation(variable, start_point, end_point, step, unit, variation_type)
        setup.auto_update = True
        self.setups.append(setup)
        return setup

    @pyaedt_function_handler(setup_name="name")
    def delete(self, name):
        """Delete a defined Parametric Setup.

        Parameters
        ----------
        name : str
            Name of parametric setup to delete.

        Returns
        -------
        bool
            ``True`` if setup is deleted. ``False`` if it failed.
        """
        for el in self.setups:
            if el.name == name:
                el.delete()
                return True
        return False

    @pyaedt_function_handler(filename="input_file", parametricname="name")
    def add_from_file(self, input_file, name=None):
        """Add a Parametric setup from either a csv or txt file.

        Parameters
        ----------
        input_file : str
            ``.csv`` or ``.txt`` file path.
        name : str, option
            Name of parametric setup.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.SetupParam`
            Optimization Object.

        References
        ----------
        >>> oModule.ImportSetup
        """
        if not name:
            name = generate_unique_name("Parametric")
        setup = SetupParam(self._app, name, optim_type="OptiParametric")
        setup.auto_update = False
        setup.props["Sim. Setups"] = [setup_defined.name for setup_defined in self._app.setups]

        file_path = Path(input_file)
        if file_path.suffix not in [".csv", ".txt"]:
            raise ValueError("Input file must be a CSV or TXT file.")

        with open_file(input_file, "r") as csvfile:
            csvreader = csv.DictReader(csvfile)
            first_data_line = next(csvreader)
            sweep_definition = [
                {
                    "Variable": var_name,
                    "Data": first_data_line[var_name],
                    "OffsetF1": False,
                    "Synchronize": 0,
                }
                for var_name in csvreader.fieldnames
                if var_name != "*"
            ]
            setup.props["Sweeps"] = {"SweepDefinition": sweep_definition}

            table = [[line[var_name] for var_name in csvreader.fieldnames if var_name != "*"] for line in csvreader]
            if table:
                setup.props["Sweep Operations"] = {"add": table}

        args = ["NAME:" + name, input_file]
        self.optimodule.ImportSetup("OptiParametric", args)

        self.setups.append(setup)
        return setup


class OptimizationSetups(PyAedtBase):
    """Sets up optimizations. It includes Optimization, DOE and DesignXplorer Analysis.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> optimization_setup = app.optimizations
    """

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if isinstance(setups_data[data], dict) and setups_data[data]["SetupType"] in [
                        "OptiOptimization",
                        "OptiDXDOE",
                        "OptiDesignExplorer",
                        "OptiSLang",
                        "optiSLang",
                        "OptiSensitivity",
                        "OptiStatistical",
                    ]:
                        self.setups.append(SetupOpti(p_app, data, setups_data[data], setups_data[data]["SetupType"]))
            except Exception:
                self._app.logger.debug(
                    "An error occurred while creating an instance of OptimizationSetups."
                )  # pragma: no cover

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def design_setups(self):
        """All design setups ordered by name.

        Returns
        -------
        dict[str, :class:`ansys.aedt.core.modules.solve_setup.Setup`]
        """
        return {i.name.split(":")[0].strip(): i for i in self.setups}

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    @pyaedt_function_handler(setup_name="name")
    def delete(self, name):
        """Delete a defined Optimetrics Setup.

        Parameters
        ----------
        name : str
            Name of optimetrics setup to delete.

        Returns
        -------
        bool
            ``True`` if setup is deleted. ``False`` if it failed.
        """
        for el in self.setups:
            if el.name == name:
                el.delete()
                return True
        return False

    @pyaedt_function_handler(optim_type="optimization_type", parametricname="name")
    def add(
        self,
        calculation=None,
        ranges=None,
        variables=None,
        optimization_type="Optimization",
        condition="<=",
        goal_value=1,
        goal_weight=1,
        solution=None,
        name=None,
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        report_type=None,
    ):
        """Add a basic optimization analysis.
        You can customize all options after the analysis is added.

        Parameters
        ----------
        calculation : str, optional
            Name of the calculation.
        ranges : dict, optional
            Dictionary of ranges with respective values.
            Values can be: a list of discrete values, a dict with tuple args of start and stop range.
            It includes intrinsics like "Freq", "Time", "Theta", "Distance".
        variables : list, optional
            List of variables to include in the optimization. By default all variables are included.
        optimization_type : strm optional
            Optimization Type.
            Possible values are `"Optimization"`, `"DXDOE"`,`"DesignExplorer"`,`"Sensitivity"`,`"Statistical"`
            and `"optiSLang"`.
        condition : string, optional
            The default is ``"<="``.
        goal_value : optional
            Value for the goal. The default is ``1``.
        goal_weight : optional
            Value for the goal weight. The default is ``1``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        name : str, optional
            Name of the analysis. The default is ``None``, in which case a
            default name is assigned.
        context : str, optional
            Calculation contexts. It can be a sphere, a matrix or a polyline.
        subdesign_id : int, optional
            Subdesign id for Circuit and HFSS 3D Layout objects.
        polyline_points : int, optional
            Number of points for Polyline context.
        report_type : str, optional
            Override the auto computation of Calculation Type.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.SetupOpti`
            Optimization object.

        References
        ----------
        >>> oModule.InsertSetup
        """
        if not solution and not self._app.nominal_sweep:
            self._app.logger.error("At least one setup is needed.")
            return False
        if not solution:
            solution = self._app.nominal_sweep
        setupname = solution.split(" ")[0]
        if not name:
            name = generate_unique_name(optimization_type)
        if optimization_type != "optiSLang":
            optimization_type = "Opti" + optimization_type
        setup = SetupOpti(self._app, name, optim_type=optimization_type)
        setup.auto_update = False
        setup.props["Sim. Setups"] = [setupname]
        if calculation:
            domain = "Time"
            if not ranges:
                ranges = {}
            if "Freq" in ranges or "Phase" in ranges or "Theta" in ranges:
                domain = "Sweep"
            if not report_type:
                report_type = self._app.design_solutions.report_type
                if context and context in self._app.modeler.sheet_names:
                    report_type = "Fields"
                elif self._app.solution_type in ["Q3D Extractor", "2D Extractor"]:
                    report_type = "Matrix"
                elif context:
                    try:
                        for f in self._app.field_setups:
                            if context == f.name:
                                report_type = "Far Fields"
                    except Exception:
                        self._app.logger.debug(
                            "An error occurred when handling `report_type` while adding a basic optimization analysis."
                        )  # pragma: no cover
            sweepdefinition = setup._get_context(
                calculation,
                condition,
                goal_weight,
                goal_value,
                solution,
                domain,
                ranges,
                report_type,
                context,
                subdesign_id,
                polyline_points,
                is_goal=True,
            )
            setup.props["Goals"]["Goal"] = sweepdefinition

        dx_variables = {}
        if variables:
            for el in variables:
                try:
                    dx_variables[el] = self._app[el]
                except Exception:
                    self._app.logger.debug(
                        "An error occurred while adding a basic optimization analysis."
                    )  # pragma: no cover
        for v in list(dx_variables.keys()):
            if optimization_type in ["OptiOptimization", "OptiDXDOE", "OptiDesignExplorer", "optiSLang"]:
                self._app.activate_variable_optimization(v)
            elif optimization_type == "OptiSensitivity":
                self._app.activate_variable_sensitivity(v)
            elif optimization_type == "OptiStatistical":
                self._app.activate_variable_statistical(v)
        if optimization_type == "OptiDXDOE" and calculation:
            setup.props["CostFunctionGoals"]["Goal"] = sweepdefinition

        if optimization_type in ["optiSLang", "OptiDesignExplorer"]:
            setup.props["Sweeps"]["SweepDefinition"] = []
            if not dx_variables:
                if optimization_type == "optiSLang":
                    dx_variables = self._app.variable_manager.design_variables
                else:
                    dx_variables = self._app.variable_manager.variables
                for variable in dx_variables.keys():
                    self._app.activate_variable_optimization(variable)
                for var in dx_variables:
                    arg = {
                        "Variable": var,
                        "Data": dx_variables[var].evaluated_value,
                        "OffsetF1": False,
                        "Synchronize": 0,
                    }
                    setup.props["Sweeps"]["SweepDefinition"].append(arg)
            else:
                for var, data in dx_variables.items():
                    arg = {"Variable": var, "Data": data, "OffsetF1": False, "Synchronize": 0}
                    setup.props["Sweeps"]["SweepDefinition"].append(arg)
        setup.create()

        setup.auto_update = True
        self.setups.append(setup)
        return setup
