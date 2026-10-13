# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SolutionsHfss
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.generic.general_methods import deprecated_property
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as SetupProps
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.optimetrics_templates import defaultdoeSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultdxSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultoptiSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultparametricSetup
from ansys.aedt.core.modules.optimetrics_templates import defaultsensitivitySetup
from ansys.aedt.core.modules.optimetrics_templates import defaultstatisticalSetup

if TYPE_CHECKING:
    from ansys.aedt.core.application.analysis import Analysis


class OptimetricsSetup(BinaryTreeNode, PyAedtBase):
    """Optimetrics setup object.

    Parameters
    ----------
    app : class:`ansys.aedt.core.modules.design_xploration.Parametrics`
    or class:`ansys.aedt.core.modules.design_xploration.Optimizations`
        PyAEDT Optimetrics instance.
    name : str, optional
        Optimetrics setup name.
    props : dict, optional
        Setup properties.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> setup_names = app.optimetrics.setup_names
    >>> app.optimetrics.setups[setup_names[0]]

    """

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __init__(self, app: Parametrics | Optimizations, name: str, props: dict) -> None:
        self._parent: Parametrics | Optimizations = app
        self._app: Any = self._parent._app
        self._legacy_props = {}
        self._name = name

        # If no props is provided, it means the setup already exist.
        if props:
            self._legacy_props = props
            if props == defaultparametricSetup:
                self.__setup_type = "OptiParametric"
            elif props == defaultoptiSetup:
                self.__setup_type = "OptiOptimization"
            elif props == defaultstatisticalSetup:
                self.__setup_type = "OptiStatistical"
            elif props == defaultsensitivitySetup:
                self.__setup_type = "OptiSensitivity"
            elif props == defaultdoeSetup:
                self.__setup_type = "OptiDXDOE"
            elif "is_optislang" in props:
                # OptiSLang and Design Explorer share the same properties, PyAEDT adds a temporal key.
                if props["is_optislang"]:
                    self.__setup_type = "optiSLang"
                else:
                    self.__setup_type = "OptiDesignExplorer"
                del props["is_optislang"]

        else:
            self.__setup_type = self._parent.setups_by_type.get(self._name)

        # GetObjData is available for some objects in 2026R1
        self._has_getobject = _has_get_obj_data(self._child_object)

    @property
    def _child_object(self) -> Any | None:
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or None

        """
        child_object = None
        design_childs = self._app.get_oo_name(self._app.odesign)

        if "Optimetrics" in design_childs:
            cc = self._app.get_oo_object(self._app.odesign, "Optimetrics")
            cc_names = self._app.get_oo_name(cc)
            if self._name in cc_names:
                child_object = self._app.get_oo_object(cc, self._name)
        return child_object

    @property
    def name(self) -> str:
        """Name of the Optimetrics setup.

        Returns
        -------
        str
           Name of the mesh operation.

        """
        child_object = self._child_object
        if child_object is not None:
            self._name = child_object.Name
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        if new_name in self._app.optimetrics.setup_names:
            raise ValueError(f"Name {new_name} already assigned in the design.")
        child_object = self._child_object
        if child_object is not None:
            child_object.Name = str(new_name)
            object.__setattr__(self, "_name", new_name)
            object.__setattr__(self, "_tree_node_initialized", False)
            object.__setattr__(self, "_props", None)
            object.__setattr__(self, "_children_loaded", False)
        if not self._has_getobject:
            # If object does not have GetObjData, PyAEDT needs to save the project
            self._app.save_project()

    @property
    def props(self) -> SetupProps:
        """Properties of the Optimetrics setup."""
        if self._legacy_props and not self._has_getobject:
            return SetupProps(self, self._legacy_props)

        if self._has_getobject:
            setup_data = _get_obj_data(self._child_object)

            for prop_name, prop_value in setup_data.items():
                self._legacy_props[prop_name] = prop_value
        else:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                if self.name in setups_data:
                    self._legacy_props = SetupProps(self, setups_data[self._name])

            except Exception:
                self._legacy_props = {}
                self._app.logger.debug(
                    "An error occurred while creating an instance of OptimizationSetups."
                )  # pragma: no cover

        return SetupProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        # Merge with existing props to support partial updates
        current_props = dict(self.props) if self._legacy_props else {}
        current_props.update(value)

        props = SetupProps(self, current_props)

        self.update(props)

    @property
    def setup_type(self) -> str | None:
        """Setup type.

        Returns
        -------
        str
            Type of the Optimetrics setup.

        """
        return self.__setup_type

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the setup.

        Parameters
        ----------
        props : dict, optional
            New properties to update. The  default is ``None``, in which case it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup

        """
        if props is None:
            props = dict(self.props)

        if self.setup_type == "OptiParametric" and "Sweep Operations" in props and len(props["Sweep Operations"]) == 3:
            props[8] = ["NAME:Sweep Operations"]
            for variation in props["Sweep Operations"].get("add", []):
                props[8].append("add:=")
                props[8].append(variation)

        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)

        self._app.ooptimetrics.EditSetup(self.name, arg)

        self._legacy_props = dict(props)
        return True

    @pyaedt_function_handler()
    def create(self) -> OptimetricsSetup:
        """Create a setup.

        References
        ----------
        >>> oModule.InsertSetup

        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self._app.ooptimetrics.InsertSetup(self.setup_type, arg)
        return self

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete a defined Optimetrics Setup.

        Parameters
        ----------
        name : str
            Name of Optimetrics setup to delete.

        Returns
        -------
        bool
            `True` if setup is deleted. `False` if it failed.


        """
        self._app.ooptimetrics.DeleteSetups([self.name])
        return True

    @pyaedt_function_handler()
    def add_calculation(
        self,
        calculation,
        ranges=None,
        variables=None,
        solution: str | None = None,
        context=None,
        subdesign_id: int | None = None,
        polyline_points: int = 1001,
        report_type=None,
        is_goal: bool = False,
        condition: str = "<=",
        goal_value: int = 1,
        goal_weight: int = 1,
    ):
        if not solution:
            solution = self._app.nominal_sweep
        setupname = solution.split(" ")[0]
        if setupname not in self._legacy_props["Sim. Setups"]:
            self._legacy_props["Sim. Setups"].append(setupname)
        domain = "Time"
        maxwell_solutions = SolutionsMaxwell3D
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
        if self.setup_type in ["OptiDesignExplorer", "OptiDXDOE"] and is_goal:
            optigoalname = "CostFunctionGoals"
        else:
            optigoalname = "Goals"
        if "Goal" in self.props[optigoalname]:
            if type(self.props[optigoalname]["Goal"]) is not list:
                self._legacy_props[optigoalname]["Goal"] = [
                    self.props[optigoalname]["Goal"],
                    SetupProps(self, sweepdefinition),
                ]
            else:
                self.props[optigoalname]["Goal"].append(sweepdefinition)
        else:
            self._legacy_props[optigoalname] = {}
            self._legacy_props[optigoalname]["Goal"] = sweepdefinition
        return self.update()

    @pyaedt_function_handler()
    def _activate_variable(self, variable_name):
        if self.setup_type in ["OptiDesignExplorer", "OptiDXDOE", "OptiOptimization", "optiSLang"]:
            self._app.activate_variable_optimization(variable_name)
        elif self.setup_type == "OptiParametric":
            self._app.activate_variable_tuning(variable_name)
        elif self.setup_type == "OptiSensitivity":
            self._app.activate_variable_sensitivity(variable_name)
        elif self.setup_type == "OptiStatistical":
            self._app.activate_variable_statistical(variable_name)

    @pyaedt_function_handler()
    def _get_context(
        self,
        expressions: str,
        condition: str,
        goal_weight: int,
        goal_value: int,
        setup_sweep_name: str | None = None,
        domain: str = "Sweep",
        intrinsics: dict | None = None,
        report_category: str | None = None,
        context: str | None = None,
        subdesign_id: int | None = None,
        polyline_points: int = 0,
        is_goal: bool = False,
    ) -> dict[str, Any] | bool:
        did = 3
        if domain != "Sweep":
            did = 1
        sweep_definition: dict[str, Any] = {"ReportType": report_category}
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        sweep_definition["Solution"] = setup_sweep_name
        ctxt: dict[str, Any] = {}

        if self._app.solution_type in ["TR", "AC", "DC", "TwinbuilderTR", "TwinbuilderAC", "TwinbuilderDC"]:
            ctxt["SimValueContext"] = [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]
            if self._app.solution_type == "TwinbuilderTR":
                setup_sweep_name = "TR"
            elif self._app.solution_type == "TwinbuilderAC":
                setup_sweep_name = "AC"
            elif self._app.solution_type == "TwinbuilderDC":
                setup_sweep_name = "DC"
            else:
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
            goal_value_props = {
                "GoalValueType": "Independent",
                "Format": "Real/Imag",
                "bG": ["v:=", f"[{goal_value};]"],
            }
            sweep_definition["GoalValue"] = SetupProps(self, goal_value_props)
            sweep_definition["Weight"] = f"[{goal_weight};]"
        return sweep_definition

    @pyaedt_function_handler()
    def _activate_variable(self, variable_name):
        if self.setup_type in ["OptiDesignExplorer", "OptiDXDOE", "OptiOptimization", "optiSLang"]:
            self._app.activate_variable_optimization(variable_name)
        elif self.setup_type == "OptiParametric":
            self._app.activate_variable_tuning(variable_name)
        elif self.setup_type == "OptiSensitivity":
            self._app.activate_variable_sensitivity(variable_name)
        elif self.setup_type == "OptiStatistical":
            self._app.activate_variable_statistical(variable_name)


class ParametricSetup(OptimetricsSetup):
    """Parametric setup object with parametric-specific operations."""

    @pyaedt_function_handler()
    def add_variation(
        self,
        sweep_variable: str,
        start_point: float | int | str,
        end_point: float | int | str | None = None,
        step: float | int | str = 100,
        units: str | None = None,
        variation_type: str = "LinearCount",
    ) -> bool:
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
            raise AEDTRuntimeError(f"Variable {sweep_variable} does not exist.")

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

        sweepdefinition = {"Variable": sweep_variable, "Data": sweep_range, "OffsetF1": False, "Synchronize": 0}
        if self._legacy_props["Sweeps"]["SweepDefinition"] is None:
            self._legacy_props["Sweeps"]["SweepDefinition"] = sweepdefinition
        elif type(self.props["Sweeps"]["SweepDefinition"]) is not list:
            self._legacy_props["Sweeps"]["SweepDefinition"] = [self._legacy_props["Sweeps"]["SweepDefinition"]]
            self._legacy_props["Sweeps"]["SweepDefinition"].append(sweepdefinition)
        else:
            for count, sweep_def in enumerate(self.props["Sweeps"]["SweepDefinition"]):
                sweep_def_copy = dict(sweep_def)
                if sweepdefinition["Variable"] == sweep_def_copy["Variable"]:
                    sweep_def_copy["Data"] += " " + sweepdefinition["Data"]
                    self._legacy_props["Sweeps"]["SweepDefinition"][count] = sweep_def_copy
                    break
        return self.update()

    @pyaedt_function_handler()
    def export_to_csv(self, output_file: str) -> bool:
        """Export the current setup to csv.

        Parameters
        ----------
        output_file : str
            Full Path to the csv file.

        Returns
        -------
        bool
            `True` if the export is correctly executed.

        """
        if self.setup_type != "OptiParametric":
            raise AEDTRuntimeError("Setup must be a parametric setup.")

        self._app.ooptimetrics.ExportParametricSetupTable(self.name, output_file)
        return True

    @pyaedt_function_handler()
    def sync_variables(self, variables: list, sync_n: int = 1) -> bool:
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

        Examples
        --------
        >>> from ansys.aedt.core.modules.design_xploration import ParametricSetup
        >>> obj = ParametricSetup()
        >>> obj.sync_variables(variables=["Box1"])

        """
        if self.setup_type != "OptiParametric":
            raise AEDTRuntimeError("Setup must be a parametric setup.")

        if type(self.props["Sweeps"]["SweepDefinition"]) is not list:
            raise AEDTRuntimeError("Not enough variables are defined in the parametric setup")

        existing_variables = [s["Variable"] for s in self.props["Sweeps"]["SweepDefinition"]]
        undo_vals = {}
        for v in variables:
            if v not in existing_variables:
                raise AEDTRuntimeError(f"Variable {v} is not defined in the parametric setup.")

        for v in variables:
            for count, sweep_def in enumerate(self._legacy_props["Sweeps"]["SweepDefinition"]):
                sweep_def_copy = dict(sweep_def)
                if v == sweep_def_copy["Variable"]:
                    undo_vals[v] = sweep_def_copy["Synchronize"]
                    sweep_def_copy["Synchronize"] = sync_n
                self._legacy_props["Sweeps"]["SweepDefinition"][count] = sweep_def_copy
        try:
            self.update()
        except Exception:  # pragma: no cover
            # If it fails to sync (due to e.g. different number of variations), reverts to original values.
            for v in variables:
                for count, sweep_def in self.props["Sweeps"]["SweepDefinition"].items():
                    sweep_def_copy = dict(sweep_def)
                    if v == sweep_def_copy["Variable"]:
                        sweep_def_copy["Synchronize"] = undo_vals[v]
                    self._legacy_props["Sweeps"]["SweepDefinition"][count] = sweep_def_copy
            self._app.logger.error("Failed to sync the Parametric setup.")
            return False
        return True


class OptimizationSetup(OptimetricsSetup):
    """Parametric setup object with parametric-specific operations."""

    @pyaedt_function_handler()
    def add_variation(
        self,
        variable_name: str,
        min_value: float,
        max_value: float,
        starting_point: float | None = None,
        min_step: float | None = None,
        max_step: float | None = None,
        use_manufacturable: bool = False,
        levels: list | None = None,
    ) -> bool:
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
            raise AEDTRuntimeError(f"Variable {variable_name} does not exist.")

        self._activate_variable(variable_name)

        if not min_step:
            min_step = (max_value - min_value) / 100
        min_step = self._app.value_with_units(min_step, self._app.variable_manager[variable_name].units)

        if not max_step:
            max_step = (max_value - min_value) / 10
        if levels is None:
            levels_with_units = f"[{min_value}: {max_value}] mm"
        else:
            levels_with_units = f"{levels} {self._app.variable_manager[variable_name].units}"
        max_step = self._app.value_with_units(max_step, self._app.variable_manager[variable_name].units)
        min_value_wuints = self._app.value_with_units(min_value, self._app.variable_manager[variable_name].units)
        max_value_wuints = self._app.value_with_units(max_value, self._app.variable_manager[variable_name].units)

        if self.setup_type == "OptiDXDOE":
            self._app.variable_manager.variables[variable_name].optimization_max_value = max_value_wuints
            self._app.variable_manager.variables[variable_name].optimization_min_value = min_value_wuints

            return True
        elif self.setup_type in ["optiSLang", "OptiDesignExplorer"]:
            self._app.variable_manager.variables[variable_name].optimization_max_value = max_value_wuints
            self._app.variable_manager.variables[variable_name].optimization_min_value = min_value_wuints
            input_variables = self._legacy_props["Sweeps"]["SweepDefinition"]
            cont = 0
            variable_included = False
            for var in input_variables:
                if var["Variable"] == variable_name:
                    self._legacy_props["Sweeps"]["SweepDefinition"][cont]["Data"] = (
                        self._app.variable_manager.variables[variable_name].evaluated_value
                    )
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
        elif self.setup_type == "OptiParametric":
            self._app.activate_variable_tuning(variable_name)
        elif self.setup_type == "OptiSensitivity":
            self._app.activate_variable_sensitivity(variable_name)
        elif self.setup_type == "OptiStatistical":
            self._app.activate_variable_statistical(variable_name)
        else:
            manufacturable_value = "true" if use_manufacturable else "false"
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
                manufacturable_value,
            ]
            if self._app.desktop_class.aedt_version_id > "2023.2":
                arg.extend(["Level:=", levels_with_units])
            if not self.props.get("Variables", None):
                self._legacy_props["Variables"] = {}
            self.props["Variables"][variable_name] = arg
            if not self._legacy_props.get("StartingPoint", None):
                self._legacy_props["StartingPoint"] = {}
            if not starting_point:
                starting_point = self._app.variable_manager[variable_name].numeric_value
                if starting_point < min_value or starting_point > max_value:
                    starting_point = (max_value + min_value) / 2

            self._legacy_props["StartingPoint"][variable_name] = self._app.value_with_units(
                starting_point, self._app.variable_manager[variable_name].units
            )

        return self.update()

    @pyaedt_function_handler()
    def add_goal(
        self,
        calculation: str,
        ranges: dict,
        variables: dict | None = None,
        solution: str | None = None,
        context: str | None = None,
        subdesign_id: int | None = None,
        polyline_points: int = 1001,
        report_type: str | None = None,
        condition: str = "<=",
        goal_value: int = 1,
        goal_weight: int = 1,
    ) -> bool:
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
        return self.add_calculation(
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


class Parametrics(PyAedtBase):
    """Manager for parametric setups in an Optimetrics design.

    Access this manager through :attr:`Optimetrics.parametrics` or ``app.parametrics``. Use it to
    create and retrieve parametric setups, inspect available setup names,
    import or export setup data, and delete setups. Each setup is represented
    by a :class:`ParametricSetup`.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> parametrics = app.optimetrics.parametrics
    >>> same_parametrics = app.parametrics
    >>> setup = parametrics.add("width", 1, 5, step=5)
    >>> setup.add_variation("height", 1, 3, step=3)

    """

    def __init__(self, app: Optimetrics) -> None:
        """Initialize the parametric setup manager for an Optimetrics instance."""
        app.logger.reset_timer()
        self.optimetrics: Optimetrics = app
        self._app: Any = self.optimetrics._app
        self._child_object = self.optimetrics._child_object
        self.logger = self.optimetrics.logger

        # Available parametric setups
        self.__setups = SetupDict()
        self.__setup_names = []
        self.__setups_by_type = SetupDict()

        app.logger.info_timer("Parametrics class has been initialized!")

    @pyaedt_function_handler()
    def __getitem__(self, name) -> ParametricSetup | None:
        """Get the parametric setup for a given setup name.

        Parameters
        ----------
        name : str
            Optimetrics setup name.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.ParametricSetup`
            Returns ``None`` if the part ID or the object name is not found.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> parametric = app.optimetrics.add_parametric("width", 1, 5, step=5)
        >>> same_parametric = app.parametrics[parametric.name]

        """
        setup = self.optimetrics[name]
        if isinstance(setup, ParametricSetup):
            return setup
        return None

    @property
    def setup_names(self) -> list[str]:
        """Return the names of available parametric setups.

        Returns
        -------
        list[str]
            Names of setups whose Optimetrics type is ``"OptiParametric"``.
            Returns an empty list if the design has no Optimetrics object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.setup_names

        """
        setup_types = self.optimetrics._get_setup_types()
        self.__setup_names = [name for name, setup_type in setup_types.items() if setup_type == "OptiParametric"]
        self.__setups = SetupDict((name, setup) for name, setup in self.__setups.items() if name in self.__setup_names)
        self.__setups_by_type = SetupDict(
            (name, setup_type) for name, setup_type in setup_types.items() if setup_type == "OptiParametric"
        )
        return self.__setup_names

    @property
    def setups(self) -> SetupDict:
        """Get the available parametric setups, indexed by name.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of setup names to :class:`ParametricSetup` objects. Setup
            objects are created when first accessed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.setups

        """
        for setup_name in self.setup_names:
            if setup_name not in self.__setups:
                self.__setups[setup_name] = ParametricSetup(app=self, name=setup_name, props={})
        return self.__setups

    @property
    def setups_by_type(self) -> SetupDict:
        """Get the discovered setup names and their Optimetrics types.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of parametric setup names to their AEDT setup type, usually
            ``"OptiParametric"``.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.setups_by_type

        """
        return self.__setups_by_type

    @property
    @deprecated_property("Use setups instead.")
    def design_setups(self) -> SetupDict:
        """Return parametric setups ordered by name.

        Deprecated. Use :attr:`setups` instead.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of setup names to :class:`ParametricSetup` objects.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.design_setups

        """
        return self.setups

    @pyaedt_function_handler()
    def add(
        self,
        variable: str,
        start_point: float | int | str,
        end_point: float | int | str | None = None,
        step: float | int | str = 100,
        variation_type: str = "LinearCount",
        solution: str | None = None,
        name: str | None = None,
        **kwargs,
    ) -> ParametricSetup:
        """Create a parametric setup with an initial variable sweep.

        Parameters
        ----------
        variable : str
            Existing design variable to sweep.
        start_point : float, int, or str
            Starting value, or the value for a ``"SingleValue"`` sweep. Strings
            can include units or an AEDT expression.
        end_point : float, int, or str, optional
            Ending value. Not required for a ``"SingleValue"`` sweep. Strings
            can include units or an AEDT expression.
        step : float, int, or str, optional
            Number of points for count-based sweeps or the step size for
            ``"LinearStep"``. Defaults to ``100``. A string can include units
            or an AEDT expression.
        variation_type : str, optional
            Sweep definition type. Supported values are ``"LinearCount"``,
            ``"LinearStep"``, ``"DecadeCount"``, ``"OctaveCount"``,
            ``"ExponentialCount"``, and ``"SingleValue"``.
        solution : str, optional
            Solution setup and sweep to associate with the parametric setup.
            Defaults to the design's nominal sweep.
        name : str, optional
            Name for the setup. A unique name is generated if omitted.
        **kwargs : optional
            Additional properties to set on the new setup before creating it.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.ParametricSetup`
            The created setup, configured with the initial variable sweep.

        Raises
        ------
        AEDTRuntimeError
            If the variable does not exist, no solution setup is available, or
            the initial variation cannot be added.

        References
        ----------
        >>> oModule.InsertSetup
        >>> oModule.EditSetup

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> setup = app.parametrics.add(
        ...     variable="width", start_point=1, end_point=5, step=5, variation_type="LinearCount"
        ... )
        >>> setup.add_variation("height", 1, 3, step=3)

        """
        if variable not in self._app.variable_manager.variables:
            raise AEDTRuntimeError(f"Variable {variable} not found.")

        if not solution and not self._app.nominal_sweep:
            raise AEDTRuntimeError("At least one setup is needed.")

        if not solution:
            solution = self._app.nominal_sweep

        setupname = solution.split(" ")[0]
        if not name:
            name = generate_unique_name("Parametric")
        elif name in self.setup_names:
            raise AEDTRuntimeError(f"Name {name} already exists.")

        props = defaultparametricSetup

        setup = ParametricSetup(app=self, name=name, props=props)

        setup._legacy_props["Sim. Setups"] = [setupname]
        setup._legacy_props["Sweeps"] = {"SweepDefinition": None}

        for arg_name, arg_value in kwargs.items():
            setup._legacy_props[arg_name] = arg_value

        setup.create()

        unit = self._app.variable_manager[variable].units

        is_added = setup.add_variation(variable, start_point, end_point, step, unit, variation_type)

        if not is_added:
            raise AEDTRuntimeError("Variation could not be added.")

        return setup

    @pyaedt_function_handler()
    def delete(self, name: str) -> bool:
        """Delete a parametric setup by name.

        Parameters
        ----------
        name : str
            Name of the setup to delete.

        Returns
        -------
        bool
            ``True`` if the setup was found and deleted, otherwise ``False``.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.delete("ParametricSetup1")

        """
        for setup_name, setup in self.setups.items():
            if setup_name == name:
                setup.delete()
                return True
        return False

    @pyaedt_function_handler()
    def export_to_csv(self, output_file: str, name: str) -> bool:
        """Export a parametric setup's variation table to a CSV file.

        Parameters
        ----------
        output_file : str
            Destination file path.
        name : str
            Name of the parametric setup to export.

        Returns
        -------
        bool
            ``True`` if the export succeeds.

        Raises
        ------
        AEDTRuntimeError
            If ``name`` does not identify an available parametric setup.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.export_to_csv(r"C:/temp/variations.csv", "ParametricSetup1")

        """
        if name not in self.setup_names:
            raise AEDTRuntimeError(f"{name} not found in parametric setup names.")
        return self.setups[name].export_to_csv(output_file)

    @pyaedt_function_handler()
    def add_from_file(self, input_file: str, name: str | None = None) -> ParametricSetup:
        """Import a parametric setup from a CSV or TXT file.

        Parameters
        ----------
        input_file : str
            Path to the input file. The file must use a format supported by
            AEDT's Optimetrics parametric setup importer.
        name : str, optional
            Name to assign to the imported setup. A unique name is generated
            if omitted.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.ParametricSetup`
            Object representing the imported setup.

        Raises
        ------
        ValueError
            If ``input_file`` does not have a ``.csv`` or ``.txt`` extension.

        References
        ----------
        >>> oModule.ImportSetup

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.parametrics.add_from_file(input_file="example.txt")

        """
        if not name:
            name = generate_unique_name("Parametric")
        elif name in self.setup_names:
            raise AEDTRuntimeError(f"Name {name} already exists.")

        setup = ParametricSetup(app=self, name=name, props={})

        setup._legacy_props["Sim. Setups"] = [setup_defined.name for setup_defined in self._app.setups]

        file_path = Path(input_file)
        if file_path.suffix not in [".csv", ".txt"]:
            raise ValueError("Input file must be a CSV or TXT file.")

        csvfile = open_file(input_file, "r")
        if csvfile is None:
            raise FileNotFoundError(f"Parametric setup file {input_file} was not found.")
        with csvfile:
            csvreader = csv.DictReader(csvfile)
            first_data_line = next(csvreader)
            fieldnames = csvreader.fieldnames or []
            sweep_definition = [
                {
                    "Variable": var_name,
                    "Data": first_data_line[var_name],
                    "OffsetF1": False,
                    "Synchronize": 0,
                }
                for var_name in fieldnames
                if var_name != "*"
            ]
            setup._legacy_props["Sweeps"] = {"SweepDefinition": sweep_definition}

            table = [[line[var_name] for var_name in fieldnames if var_name != "*"] for line in csvreader]
            if table:
                setup._legacy_props["Sweep Operations"] = {"add": table}

        args = ["NAME:" + name, input_file]
        self._app.ooptimetrics.ImportSetup("OptiParametric", args)

        return setup


class Optimizations(PyAedtBase):
    """Manager for optimization-related Optimetrics setups.

    Access this manager through :attr:`Optimetrics.optimizations` or
    ``app.optimizations``. Use it to create and retrieve optimization, DOE,
    Design Explorer, sensitivity, statistical, and optiSLang setups. Each
    setup is represented by an :class:`OptimizationSetup`.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> optimizations = app.optimetrics.optimizations
    >>> setup = optimizations.add(calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"})

    """

    def __init__(self, app: Optimetrics) -> None:
        """Initialize the optimization manager for an Optimetrics instance."""
        app.logger.reset_timer()
        self.optimetrics: Optimetrics = app
        self._app: Any = self.optimetrics._app
        self._child_object = self.optimetrics._child_object
        self.logger = self.optimetrics.logger

        self.__setups = SetupDict()
        self.__setup_names = []
        self.__setups_by_type = SetupDict()

        app.logger.info_timer("Optimizations class has been initialized!")

    @pyaedt_function_handler()
    def __getitem__(self, name) -> OptimizationSetup | None:
        """Get an optimization-related setup by name.

        Parameters
        ----------
        name : str
            Name of the setup to retrieve.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimizationSetup`
            The matching setup, or ``None`` if the name is not found among
            optimization-related setups.

        Examples
        --------
        >>> setup = app.optimetrics.optimizations["Optimization1"]

        """
        setup = self.optimetrics[name]
        if isinstance(setup, OptimizationSetup):
            return setup
        return None

    @property
    def setup_names(self) -> list[str]:
        """Return names of available non-parametric Optimetrics setups.

        Returns
        -------
        list[str]
            Names of setups whose type is not ``"OptiParametric"``. This can
            include optimization, DOE, Design Explorer, sensitivity,
            statistical, and optiSLang setups. Returns an empty list if no
            Optimetrics object is available.

        Examples
        --------
        >>> app.optimetrics.optimizations.setup_names

        """
        setup_types = self.optimetrics._get_setup_types()
        self.__setup_names = [name for name, setup_type in setup_types.items() if setup_type != "OptiParametric"]
        self.__setups = SetupDict((name, setup) for name, setup in self.__setups.items() if name in self.__setup_names)
        self.__setups_by_type = SetupDict(
            (name, setup_type) for name, setup_type in setup_types.items() if setup_type != "OptiParametric"
        )
        return self.__setup_names

    @property
    def setups(self) -> SetupDict:
        """Get available optimization-related setups, indexed by name.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of setup names to :class:`OptimizationSetup` objects.
            Setup objects are created when first accessed.

        Examples
        --------
        >>> app.optimetrics.optimizations.setups

        """
        for setup_name in self.setup_names:
            if setup_name not in self.__setups:
                self.__setups[setup_name] = OptimizationSetup(app=self, name=setup_name, props={})
        return self.__setups

    @property
    def setups_by_type(self) -> SetupDict:
        """Get the discovered setup names and their Optimetrics types.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of non-parametric setup names to their AEDT setup type.
        """
        return self.__setups_by_type

    @pyaedt_function_handler()
    def add(
        self,
        calculation: str | None = None,
        ranges: dict | None = None,
        variables: list | None = None,
        optimization_type: str = "Optimization",
        condition: str = "<=",
        goal_value: int = 1,
        goal_weight: int = 1,
        solution: str | None = None,
        name: str | None = None,
        context: str | None = None,
        subdesign_id: int | None = None,
        polyline_points: int = 1001,
        report_type: str | None = None,
        **kwargs,
    ) -> OptimizationSetup:
        """Create an optimization-related setup and optionally add a goal.

        Parameters
        ----------
        calculation : str, optional
            Expression to evaluate as a goal. If provided, a goal is added
            using ``condition``, ``goal_value``, and ``goal_weight``.
        ranges : dict, optional
            Intrinsic ranges for the calculation, such as ``"Freq"``,
            ``"Time"``, ``"Theta"``, or ``"Distance"``. Values can be a
            discrete-value list, a string of discrete values, or a
            ``(start, stop)`` tuple.
        variables : list, optional
            Design variables to include in the setup. For Design Explorer and
            optiSLang, omitted variables default to all design variables or
            all variables, respectively.
        optimization_type : str, optional
            Setup type: ``"Optimization"``, ``"DXDOE"``,
            ``"DesignExplorer"``, ``"Sensitivity"``, ``"Statistical"``, or
            ``"optiSLang"``.
        condition : str, optional
            Comparison condition for the goal, for example ``"<="``.
            Defaults to ``"<="``.
        goal_value : int, optional
            Target value for the goal. Defaults to ``1``.
        goal_weight : int, optional
            Weight assigned to the goal. Defaults to ``1``.
        solution : str, optional
            Solution setup and sweep used to evaluate the calculation.
            Defaults to the design's nominal sweep.
        name : str, optional
            Name for the setup. A unique name is generated if omitted.
        context : str, optional
            Calculation context, such as a far-field sphere, matrix, or
            polyline.
        subdesign_id : int, optional
            Subdesign ID for Circuit and HFSS 3D Layout designs.
        polyline_points : int, optional
            Number of points to use for a polyline context. Defaults to
            ``1001``.
        report_type : str, optional
            Override the automatically selected calculation report type.
        **kwargs : optional
            Additional properties to set on the new setup.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimetricsSetup`
            The created setup, ready for further configuration.

        Raises
        ------
        AEDTRuntimeError
            If neither ``solution`` nor a nominal sweep is available.
        ValueError
            If ``optimization_type`` is not supported.

        References
        ----------
        ``oModule.InsertSetup``.

        Examples
        --------
        >>> setup = app.optimetrics.optimizations.add(
        ...     calculation="dB(S(1,1))",
        ...     ranges={"Freq": "2.5GHz"},
        ...     optimization_type="Optimization",
        ... )

        """
        if not solution and not self._app.nominal_sweep:
            raise AEDTRuntimeError("At least one setup is needed.")

        if optimization_type not in [
            "optiSLang",
            "Optimization",
            "DXDOE",
            "DesignExplorer",
            "Sensitivity",
            "Statistical",
        ]:
            raise ValueError("Unsupported optimization type.")

        if not solution:
            solution = self._app.nominal_sweep

        setupname = solution.split(" ")[0]
        if not name:
            name = generate_unique_name(optimization_type)
        elif name in self.setup_names:
            raise AEDTRuntimeError(f"Name {name} already exists.")

        if optimization_type != "optiSLang":
            optimization_type = "Opti" + optimization_type

        props = defaultoptiSetup

        if optimization_type == "OptiStatistical":
            props = defaultstatisticalSetup
        elif optimization_type == "OptiSensitivity":
            props = defaultsensitivitySetup
        elif optimization_type == "OptiDXDOE":
            props = defaultdoeSetup
        elif optimization_type == "OptiDesignExplorer":
            props = defaultdxSetup
            props["is_optislang"] = False
        elif optimization_type == "optiSLang":
            props = defaultdxSetup
            props["is_optislang"] = True

        setup = OptimizationSetup(self, name, props=props)

        setup._legacy_props["Sim. Setups"] = [setupname]

        for arg_name, arg_value in kwargs.items():
            setup._legacy_props[arg_name] = arg_value

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
            setup._legacy_props["Goals"]["Goal"] = sweepdefinition

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
            setup._legacy_props["CostFunctionGoals"]["Goal"] = sweepdefinition

        if optimization_type in ["optiSLang", "OptiDesignExplorer"]:
            setup._legacy_props["Sweeps"]["SweepDefinition"] = []
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
                    setup._legacy_props["Sweeps"]["SweepDefinition"].append(arg)
            else:
                for var, data in dx_variables.items():
                    arg = {"Variable": var, "Data": data, "OffsetF1": False, "Synchronize": 0}
                    setup._legacy_props["Sweeps"]["SweepDefinition"].append(arg)

        setup.create()

        return setup

    @pyaedt_function_handler()
    def delete(self, name: str) -> bool:
        """Delete an optimization setup by name.

        Parameters
        ----------
        name : str
            Name of the setup to delete.

        Returns
        -------
        bool
            ``True`` if the setup was found and deleted, otherwise ``False``.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimizations.delete("OptimizationSetup1")

        """
        for setup_name, setup in self.setups.items():
            if setup_name == name:
                setup.delete()
                return True
        return False


class Optimetrics(PyAedtBase):
    """Main entry point for working with Optimetrics.

    Access this class through ``app.optimetrics``. It provides a unified view of
    Optimetrics setups and routes parametric and optimization operations to their
    respective managers. Use :attr:`parametrics` or :attr:`optimizations` when
    you need the manager-specific setup collections and methods.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> app.optimetrics
    >>> parametric = app.optimetrics.add_parametric("width", 1, 5, step=5)
    >>> optimization = app.optimetrics.add_optimization()

    """

    def __init__(self, app: Analysis) -> None:
        app.logger.reset_timer()
        self._app: Any = app
        self.logger = self._app.logger

        # Lazy load parametric and optimization objects
        self._parametrics = None
        self._optimizations = None

        # Available Optimetrics setups
        self.__setups = SetupDict()
        self.__setups_by_type = SetupDict()

        app.logger.info_timer("Optimetrics class has been initialized!")

        if not settings.lazy_load:
            self._parametrics = self.parametrics
            self._optimizations = self.optimizations

    @pyaedt_function_handler()
    def __getitem__(self, name) -> OptimizationSetup | ParametricSetup | None:
        """Get the object for a given setup name.

        Parameters
        ----------
        name : str
            Optimetrics setup name.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimizationSetup`, or
        :class:`ansys.aedt.core.modules.design_xploration.ParametricSetup`
            Returns ``None`` if the part ID or the object name is not found.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> parametric = app.optimetrics.add_parametric("width", 1, 5, step=5)
        >>> same_parametric = app.optimetrics[parametric.name]

        """
        if name in self.setup_names:
            return self.setups[name]
        return None

    @property
    def _child_object(self) -> object | None:
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or None

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics._child_object.GetChildNames()

        """
        child_object = None
        design_childs = self._app.get_oo_name(self._app.odesign)

        if "Optimetrics" in design_childs:
            child_object = self._app.get_oo_object(self._app.odesign, "Optimetrics")
        return child_object

    @property
    def parametrics(self) -> Parametrics:
        """Access the manager for parametric setups.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.Parametrics`
            Manager for creating and managing parametric setups.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics.parametrics

        """
        if self._parametrics is None:
            self._parametrics = Parametrics(self)
        return self._parametrics

    @property
    def optimizations(self) -> Optimizations:
        """Access the manager for optimization setups.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.Optimizations`
            Manager for creating and managing optimization, DOE, sensitivity,
            statistical, Design Explorer, and optiSLang setups.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics.optimizations

        """
        if self._optimizations is None:
            self._optimizations = Optimizations(self)
        return self._optimizations

    @property
    def setup_names(self) -> list[str]:
        """Return all the available Optimetrics setup names.

        Returns
        -------
        list
            List of setup names.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics.setup_names

        """
        if self._app._is_object_oriented_enabled():
            return list(self._app.get_oo_name(self._app.odesign, "Optimetrics"))
        return []

    @property
    def setups(self) -> SetupDict:
        """Return the available setups.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Optimetrics setup object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics.setups

        """
        for setup_name, setup in self.parametrics.setups.items():
            if setup_name not in self.__setups:
                self.__setups[setup_name] = setup

        for setup_name, setup in self.optimizations.setups.items():
            if setup_name not in self.__setups:
                self.__setups[setup_name] = setup

        active_names = set(self.setup_names)
        for setup_name in list(self.__setups):
            if setup_name not in active_names:
                del self.__setups[setup_name]

        return self.__setups

    @pyaedt_function_handler()
    def add_parametric(
        self,
        variable: str,
        start_point: float | int | str,
        end_point: float | int | str | None = None,
        step: float | int | str = 100,
        variation_type: str = "LinearCount",
        solution: str | None = None,
        name: str | None = None,
        **kwargs,
    ) -> ParametricSetup:
        """Create a parametric setup and add its initial variable variation.

        This is the convenience entry point for adding a parametric setup from
        ``app.optimetrics``. Additional variations and setup properties can be
        added through the returned :class:`ParametricSetup`.

        Parameters
        ----------
        variable : str
            Design variable to sweep. It must already exist in the design.
        start_point : float, int, or str
            Start value of the variation, or the single value when
            ``variation_type="SingleValue"``. Strings may include units or a
            valid AEDT expression.
        end_point : float, int, or str, optional
            End value of the variation. Not needed for a single-value variation.
        step : float, int, or str
            Step size or number of points, depending on ``variation_type``.
            Defaults to ``100`` for ``"LinearCount"``. A string can specify a
            unit-bearing value or valid AEDT expression, for example ``"0.1mm"``
            for ``"LinearStep"``.
        variation_type : str, optional
            Variation method. Supported values are ``"LinearCount"``,
            ``"LinearStep"``, ``"DecadeCount"``, ``"OctaveCount"``,
            ``"ExponentialCount"``, and ``"SingleValue"``.
        solution : str, optional
            Solution setup and sweep to associate with the parametric setup.
            Defaults to the design's nominal sweep.
        name : str, optional
            Name for the parametric setup. A unique name is generated if omitted.
        **kwargs : optional
            Additional setup properties forwarded to the new setup.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.ParametricSetup`
            The created parametric setup, with the initial variation configured.

        References
        ----------
        >>> oModule.InsertSetup
        >>> oModule.EditSetup

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics.add_parametric("width", 1, 5, step=5)

        """
        return self.parametrics.add(
            variable=variable,
            start_point=start_point,
            end_point=end_point,
            step=step,
            variation_type=variation_type,
            solution=solution,
            name=name,
            **kwargs,
        )

    @pyaedt_function_handler()
    def add_optimization(
        self,
        calculation: str | None = None,
        ranges: dict | None = None,
        variables: list | None = None,
        optimization_type: str = "Optimization",
        condition: str = "<=",
        goal_value: int = 1,
        goal_weight: int = 1,
        solution: str | None = None,
        name: str | None = None,
        context: str | None = None,
        subdesign_id: int | None = None,
        polyline_points: int = 1001,
        report_type: str | None = None,
        **kwargs,
    ) -> OptimetricsSetup:
        """Create an optimization setup through the main Optimetrics entry point.

        This method forwards setup creation to the optimization manager and
        returns the created setup. Use the returned object to add or edit
        variables, goals, and other setup properties.

        Parameters
        ----------
        calculation : str, optional
            Expression to evaluate as an optimization goal. When provided,
            a goal is created using ``condition``, ``goal_value``, and
            ``goal_weight``.
        ranges : dict, optional
            Intrinsic ranges for the calculation, such as ``"Freq"`` or
            ``"Time"``. A value can be a single value, a sequence of discrete
            values, or a ``(start, stop)`` tuple.
        variables : list, optional
            Design variables to include. If omitted, the setup manager's
            defaults for the selected optimization type are used.
        optimization_type : str, optional
            Type of setup to create: ``"Optimization"``, ``"DXDOE"``,
            ``"DesignExplorer"``, ``"Sensitivity"``, ``"Statistical"``, or
            ``"optiSLang"``.
        condition : str, optional
            Comparison condition for the goal, for example ``"<="``. The
            default is ``"<="``.
        goal_value : int, optional
            Target value for the goal. The default is ``1``.
        goal_weight : int, optional
            Weight assigned to the goal. The default is ``1``.
        solution : str, optional
            Solution setup and sweep used to evaluate the calculation.
            Defaults to the design's nominal sweep.
        name : str, optional
            Name for the setup. A unique name is generated if omitted.
        context : str, optional
            Calculation context, such as a far-field sphere, matrix, or
            polyline.
        subdesign_id : int, optional
            Subdesign ID for Circuit and HFSS 3D Layout designs.
        polyline_points : int, optional
            Number of points used for a polyline context. The default is
            ``1001``.
        report_type : str, optional
            Override the automatically selected calculation report type.
        **kwargs : optional
            Additional setup properties forwarded to the optimization manager.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimetricsSetup`
            The created optimization setup, ready for further configuration.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> setup = app.optimetrics.add_optimization(
        ...     calculation="dB(S(1,1))",
        ...     ranges={"Freq": "2.5GHz"},
        ...     optimization_type="Optimization",
        ... )
        """
        return self.optimizations.add(
            calculation=calculation,
            ranges=ranges,
            variables=variables,
            optimization_type=optimization_type,
            condition=condition,
            goal_value=goal_value,
            goal_weight=goal_weight,
            solution=solution,
            name=name,
            context=context,
            subdesign_id=subdesign_id,
            polyline_points=polyline_points,
            report_type=report_type,
            **kwargs,
        )

    @pyaedt_function_handler()
    def delete_setup(self, name: str) -> bool:
        """Delete an Optimetrics setup by name.

        Parameters
        ----------
        name : str
            Name of the setup to delete.

        Returns
        -------
        bool
            ``True`` if the setup was found and deleted, otherwise ``False``.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.optimetrics.delete_setup("OptimizationSetup1")

        """
        if not self.setups:
            return False

        for setup_name, setup in self.setups.items():
            if setup_name == name:
                setup.delete()
                return True
        return False

    @pyaedt_function_handler()
    def _get_setup_types(self) -> dict[str, str | None]:
        """Return AEDT setup types for the currently available Optimetrics setups."""
        setup_names = self.setup_names
        optimetrics_child_object = self._child_object
        if not setup_names or not optimetrics_child_object:
            return {}

        setup_types = {}
        legacy_setup_types = None
        for name in setup_names:
            child_object = self._app.get_oo_object(optimetrics_child_object, name)
            if "GetObjType" in dir(child_object):
                setup_type = child_object.GetObjType()
            else:
                if legacy_setup_types is None:
                    legacy_setup_types = {}
                    for setup_type in self._app.ooptimetrics.GetChildTypes():
                        for child_name in self._app.ooptimetrics.GetChildNames(setup_type):
                            legacy_setup_types[child_name] = setup_type
                setup_type = legacy_setup_types.get(name)
            setup_types[name] = setup_type

        return setup_types
