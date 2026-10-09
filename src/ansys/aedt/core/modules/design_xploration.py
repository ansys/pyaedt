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

from typing import TYPE_CHECKING
from typing import Any

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SolutionsHfss
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as SetupProps
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode

if TYPE_CHECKING:
    pass


class OptimetricsSetup(BinaryTreeNode, PyAedtBase):
    """Optimetrics setup object.

    Parameters
    ----------
    app : class:`ansys.aedt.core.modules.design_xploration.Parametrics`
    or class:`ansys.aedt.core.modules.design_xploration.Optimizations`
        PyAEDT optimetrics instance.
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
        self._optimetrics = app
        self._app: Any = self._optimetrics._app
        self.ooptimetrics = self._app.ooptimetrics
        self._legacy_props = {}
        self._name = name
        self._is_new_setup = False

        # Optimetrics setup type
        self._setup_type = None
        # if setup_type:
        #     self._setup_type = setup_type
        #
        #     inputd = copy.deepcopy(props)
        #
        #     if self.setup_type == "OptiParametric":
        #         self._legacy_props = inputd or copy.deepcopy(defaultparametricSetup)
        #
        #         if not inputd and self._app.design_type == "Icepak":
        #             self._legacy_props["ProdOptiSetupDataV2"] = {
        #                 "SaveFields": False,
        #                 "FastOptimetrics": False,
        #                 "SolveWithCopiedMeshOnly": True,
        #             }
        #     elif self.setup_type == "OptiDesignExplorer":
        #         self._legacy_props = inputd or copy.deepcopy(defaultdxSetup)
        #     elif self.setup_type == "OptiOptimization":
        #         self._legacy_props = inputd or copy.deepcopy(defaultoptiSetup)
        #     elif self.setup_type == "OptiSensitivity":
        #         self._legacy_props = inputd or copy.deepcopy(defaultsensitivitySetup)
        #     elif self.setup_type == "OptiStatistical":
        #         self._legacy_props = inputd or copy.deepcopy(defaultstatisticalSetup)
        #     elif self.setup_type == "OptiDXDOE":
        #         self._legacy_props = inputd or copy.deepcopy(defaultdoeSetup)
        #     elif self.setup_type == "optiSLang":
        #         self._legacy_props = inputd or copy.deepcopy(defaultdxSetup)
        #
        #     if inputd:
        #         self._legacy_props.pop("ID", None)
        #         self._legacy_props.pop("NextUniqueID", None)
        #         self._legacy_props.pop("MoveBackwards", None)
        #         self._legacy_props.pop("GoalSetupVersion", None)
        #         self._legacy_props.pop("Version", None)
        #         self._legacy_props.pop("SetupType", None)
        #         if inputd.get("Sim. Setups"):
        #             setups = inputd["Sim. Setups"]
        #             for el in setups:
        #                 try:
        #                     if isinstance(self._app.design_properties["SolutionManager"]["ID Map"]["Setup"], list):
        #                         for setup in self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]:
        #                             if setup["I"] == el:
        #                                 setups[setups.index(el)] = setup["N"]
        #                                 break
        #                     else:
        #                         if self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]["I"] == el:
        #                             setups[setups.index(el)] = self._app.design_properties["SolutionManager"]
        #                             ["ID Map"][
        #                                 "Setup"
        #                             ]["N"]
        #                             break
        #
        #                 except (TypeError, KeyError):
        #                     pass
        #
        #         if inputd.get("Goals", None) and self.name in self.omodule.GetChildNames():
        #             if self._app._is_object_oriented_enabled():
        #                 oparams = self._app.get_oo_object(self.omodule, self.name).GetCalculationInfo()
        #                 oparam = [i for i in oparams[0]]
        #                 idx = None
        #                 if oparam[0] in oparam[1:]:
        #                     idx = oparam[1:].index(oparam[0]) + 1
        #                 if idx:
        #                     oparam = [["NAME:Goal"] + oparam[k : idx + k] for k in range(0, len(oparam), idx)]
        #                 else:
        #                     oparam = [["NAME:Goal"] + oparam]
        #
        #                 self._legacy_props["Goals"]["Goal"] = []
        #                 for param in oparam:
        #                     arg1 = {}
        #                     _arg2dict(param, arg1)
        #                     self._get_setup_props(arg1)
        #                     self._legacy_props["Goals"]["Goal"].append(SetupProps(self, arg1["Goal"]))
        #
        #         if inputd.get("Variables"):  # pragma: no cover
        #             for var in inputd.get("Variables"):
        #                 output_list = []
        #                 props = self._legacy_props["Variables"][var]
        #                 for prop in props:
        #                     parts = prop.split("=")
        #                     value = (
        #                         True
        #                         if parts[1].lower() == "true"
        #                         else False
        #                         if parts[1].lower() == "false"
        #                         else parts[1].strip("'")
        #                     )
        #                     output_list.extend([parts[0] + ":=", value])
        #                 self._legacy_props["Variables"][var] = output_list

        # GetObjData is available for some objects in 2026R1
        self._has_getobject = _has_get_obj_data(self._child_object)

    @property
    def _child_object(self) -> object | None:
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
        """Name of the optimetrics setup.

        Returns
        -------
        str
           Name of the mesh operation.

        """
        if self._child_object:
            self._name = self._child_object.Name
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        if new_name in self._optimetrics.setup_names:
            raise ValueError(f"Name {new_name} already assigned in the design.")
        if self._child_object:
            self._child_object.Name = str(new_name)
            object.__setattr__(self, "_name", new_name)
            object.__setattr__(self, "_tree_node_initialized", False)
            object.__setattr__(self, "_props", None)
            object.__setattr__(self, "_children_loaded", False)
        if not self._has_getobject:
            # If object does not have GetObjData, PyAEDT needs to save the project
            self._app.save_project()

    @property
    def props(self) -> SetupProps:
        """Properties of the optimetrics setup."""
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
        """Retrieve type.

        Returns
        -------
        str
            Type of the optimetrics setup.

        """
        if not self._setup_type:
            app_type = None
            child_object = self._child_object
            if "GetObjType" in dir(child_object):
                app_type = child_object.GetObjType()
            else:
                name = self.name
                for st in self._app.ooptimetrics.GetChildTypes():
                    if name in self._app.ooptimetrics.GetChildNames(st):
                        app_type = st
                        break
            self._setup_type = app_type
        return self._setup_type

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

        self.ooptimetrics.EditSetup(self.name, arg)

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
        self.ooptimetrics.InsertSetup(self.setup_type, arg)
        return self

    @pyaedt_function_handler()
    def delete(self) -> bool:
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
        self.ooptimetrics.DeleteSetups([self.name])
        return True

    @pyaedt_function_handler()
    def add_variation(
        self,
        sweep_variable: str,
        start_point: float | int,
        end_point: float | int | None = None,
        step: float | int = 100,
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
        if self.setup_type != "OptiParametric":
            raise AEDTRuntimeError("Setup must be a parametric setup.")
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
        sweepdefinition = {"Variable": sweep_variable, "Data": sweep_range, "OffsetF1": False, "Synchronize": 0}
        if self._legacy_props["Sweeps"]["SweepDefinition"] is None:
            self._legacy_props["Sweeps"]["SweepDefinition"] = sweepdefinition
        elif type(self.props["Sweeps"]["SweepDefinition"]) is not list:
            self._legacy_props["Sweeps"]["SweepDefinition"] = [self._legacy_props["Sweeps"]["SweepDefinition"]]
            self._append_sweepdefinition(sweepdefinition)
        else:
            self._append_sweepdefinition(sweepdefinition)

        return self.update()

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
        expressions,
        condition,
        goal_weight,
        goal_value,
        setup_sweep_name=None,
        domain: str = "Sweep",
        intrinsics=None,
        report_category=None,
        context=None,
        subdesign_id: int | None = None,
        polyline_points: int = 0,
        is_goal: bool = False,
    ):
        did = 3
        if domain != "Sweep":
            did = 1
        sweep_definition = {"ReportType": report_category}
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        sweep_definition["Solution"] = setup_sweep_name
        ctxt = {}

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
            goal_value = {
                "GoalValueType": "Independent",
                "Format": "Real/Imag",
                "bG": ["v:=", f"[{goal_value};]"],
            }
            goal_value = SetupProps(self, goal_value)
            sweep_definition["GoalValue"] = goal_value
            sweep_definition["Weight"] = f"[{goal_weight};]"
        return sweep_definition


class Parametrics(PyAedtBase):
    """Optimetrics parametric main class.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> app.optimetrics.parametrics

    """

    def __init__(self, app: Optimetrics) -> None:
        app.logger.reset_timer()
        self.optimetrics: Optimetrics = app
        self._app: Any = self.optimetrics._app
        self._child_object = self.optimetrics._child_object
        self.logger = self.optimetrics.logger

        self.__setups = SetupDict()
        self.__setup_names = []

        app.logger.info_timer("Parametrics class has been initialized!")

    @pyaedt_function_handler()
    def __getitem__(self, name) -> OptimetricsSetup | None:
        """Get the object ``OptimetricsSetup`` for a given setup name.

        Parameters
        ----------
        name : str
            Optimetrics setup operation name.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimetricsSetup`
            Returns ``None`` if the part ID or the object name is not found.

        """
        return self.optimetrics[name]

    @property
    def setup_names(self) -> list[str]:
        """Return the available optimetrics parametric setup names.

        Returns
        -------
        list
            List of setup names.

        """
        optimetrics_child_object = self._child_object

        if not optimetrics_child_object:
            return []

        for name in self.optimetrics.setup_names:
            app_type = None
            if name in self.__setup_names:
                # This saves time to avoid multiple call to the AEDT API
                continue
            child_object = self._app.get_oo_object(optimetrics_child_object, name)
            if "GetObjType" in dir(child_object):
                app_type = child_object.GetObjType()
            else:
                for st in self._app.ooptimetrics.GetChildTypes():
                    if name in self._app.ooptimetrics.GetChildNames(st):
                        app_type = st
                        break
            if app_type == "OptiParametric":
                self.__setup_names.append(name)

        return self.__setup_names

    @property
    def setups(self) -> SetupDict:
        """Parametric setups.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Optimetrics setup object.

        """
        for setup_name in self.setup_names:
            if setup_name not in self.__setups:
                # ADD COMMENT
                self.__setups[setup_name] = OptimetricsSetup(app=self, name=setup_name, props={})
        return self.__setups


class Optimizations(PyAedtBase):
    """Optimetrics optimization main class.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> app.optimizations

    """

    def __init__(self, app: Optimetrics) -> None:
        app.logger.reset_timer()
        self.optimetrics: Optimetrics = app
        self._app: Any = self.optimetrics._app
        self._child_object = self.optimetrics._child_object
        self.logger = self.optimetrics.logger

        self.__setups = SetupDict()
        self.__setup_names = []

        app.logger.info_timer("Optimizations class has been initialized!")

    @pyaedt_function_handler()
    def __getitem__(self, name) -> OptimetricsSetup | None:
        """Get the object ``OptimetricsSetup`` for a given setup name.

        Parameters
        ----------
        name : str
            Optimetrics setup operation name.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimetricsSetup`
            Returns ``None`` if the part ID or the object name is not found.

        """
        return self.optimetrics[name]

    @property
    def setup_names(self) -> list[str]:
        """Return the available optimetrics optimization setup names.

        Returns
        -------
        list
            List of setup names.

        """
        optimetrics_child_object = self._child_object

        if not optimetrics_child_object:
            return []

        for name in self.optimetrics.setup_names:
            app_type = None
            if name in self.__setup_names:
                # This saves time to avoid multiple call to the AEDT API
                continue
            child_object = self._app.get_oo_object(optimetrics_child_object, name)
            if "GetObjType" in dir(child_object):
                app_type = child_object.GetObjType()
            else:
                for st in self._app.ooptimetrics.GetChildTypes():
                    if name in self._app.ooptimetrics.GetChildNames(st):
                        app_type = st
                        break
            if app_type != "OptiParametric":
                self.__setup_names.append(name)

        return self.__setup_names

    @property
    def setups(self) -> SetupDict:
        """Parametric setups.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Optimetrics setup object.

        """
        for setup_name in self.setup_names:
            if setup_name not in self.__setups:
                # ADD COMMENT
                self.__setups[setup_name] = OptimetricsSetup(app=self, name=setup_name, props={})
        return self.__setups


class Optimetrics(PyAedtBase):
    """Optimetrics main class.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> app = Hfss()
    >>> app.optimetrics

    """

    def __init__(self, app) -> None:
        app.logger.reset_timer()
        self._app: Any = app
        self.ooptimetrics = self._app.ooptimetrics
        self.logger = self._app.logger

        # ADD COMMENT HERE
        self._parametrics = None
        self._optimizations = None

        self.__setups = SetupDict()
        self.__setups_by_type = SetupDict()

        app.logger.info_timer("Optimetrics class has been initialized!")

        if not settings.lazy_load:
            self._parametrics = self.parametrics
            self._optimizations = self.optimizations

    @pyaedt_function_handler()
    def __getitem__(self, name) -> OptimetricsSetup | None:
        """Get the object ``OptimetricsSetup`` for a given setup name.

        Parameters
        ----------
        name : str
            Optimetrics setup operation name.

        Returns
        -------
        :class:`ansys.aedt.core.modules.design_xploration.OptimetricsSetup`
            Returns ``None`` if the part ID or the object name is not found.

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

        """
        child_object = None
        design_childs = self._app.get_oo_name(self._app.odesign)

        if "Optimetrics" in design_childs:
            child_object = self._app.get_oo_object(self._app.odesign, "Optimetrics")
        return child_object

    @property
    def parametrics(self) -> Parametrics:
        """"""
        if self._parametrics is None:
            self._parametrics = Parametrics(self)
        return self._parametrics

    @property
    def optimizations(self) -> Parametrics:
        """"""
        if self._optimizations is None:
            self._optimizations = Parametrics(self)
        return self._optimizations

    @property
    def setup_names(self) -> list[str]:
        """Return all the available optimetrics setup names.

        Returns
        -------
        list
            List of setup names.

        """
        if self._app._is_object_oriented_enabled():
            return list(self._app.get_oo_name(self._app.odesign, "Optimetrics"))
        return []

    @property
    def setups(self) -> SetupDict | None:
        """Return the available setups.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Optimetrics setup object.

        """
        for setup_name, setup in self.parametrics.setups.items():
            if setup_name not in self.__setups:
                self.__setups[setup_name] = OptimetricsSetup(app=setup, name=setup_name, props={})

        for setup_name, setup in self.optimizations.setups.items():
            if setup_name not in self.__setups:
                self.__setups[setup_name] = OptimetricsSetup(app=setup, name=setup_name, props={})

        return self.__setups

    @pyaedt_function_handler()
    def add_parametric(
        self,
        variable: str,
        start_point: float,
        end_point: float | None = None,
        step: float | int = 100,
        variation_type: str = "LinearCount",
        solution: str | None = None,
        name: str | None = None,
        **kwargs,
    ) -> OptimetricsSetup:
        """Add parametric setup.
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
        **kwargs : optional
            Additional keyword arguments to pass when creating the setup.

        Returns
        -------
         :class:`ansys.aedt.core.modules.design_xploration.OptimetricsSetup`
            Optimetrics setup object.

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

        setup = OptimetricsSetup(app=self, name=name, props={}, setup_type="OptiParametric")

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
