# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.aedt_constants import DesignType
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class DesignSolution(PyAedtBase):
    def __init__(self, odesign, design_type, aedt_version):
        self._odesign = odesign
        self._aedt_version = aedt_version
        self.model_name = design_type.model_name
        self._solution_options = copy.deepcopy(design_type.solution_types)
        if not self._solution_options:
            raise ValueError("Design type is not valid.")
        # deepcopy doesn't work on remote
        self._design_type = design_type
        if design_type == DesignType.HFSS and aedt_version >= "2021.2":
            self._solution_options["Modal"]["name"] = "HFSS Modal Network"
            self._solution_options["Terminal"]["name"] = "HFSS Terminal Network"
        self._solution_type = None

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._design_type in [
            DesignType.CIRCUIT,
            DesignType.TWINBUILDER,
            DesignType.HFSS3DLAYOUT,
            DesignType.EMIT,
            DesignType.Q3D,
        ]:
            if not self._solution_type:
                self._solution_type = self._design_type.solution_default
        elif self._odesign:
            try:
                self._solution_type = self._odesign.GetSolutionType()
            except Exception:
                self._solution_type = self._design_type.solution_default
        elif self._solution_type is None:
            self._solution_type = self._design_type.solution_default
        return self._solution_type

    @solution_type.setter
    def solution_type(self, value):
        if value is None:
            if self._design_type in [
                DesignType.CIRCUIT,
                DesignType.TWINBUILDER,
                DesignType.HFSS3DLAYOUT,
                DesignType.EMIT,
                DesignType.Q3D,
            ]:
                self._solution_type = self._design_type.default_solution
            elif self._odesign:
                try:
                    self._solution_type = self._odesign.GetSolutionType()
                except Exception:
                    self._solution_type = self._design_type.default_solution
            else:
                self._solution_type = self._design_type.default_solution
        elif value and value in self._solution_options:
            self._solution_type = value
            if self._solution_options[value]["name"]:
                if self._solution_options[value]["options"]:
                    self._odesign.SetSolutionType(
                        self._solution_options[value]["name"], self._solution_options[value]["options"]
                    )
                else:
                    try:
                        self._odesign.SetSolutionType(self._solution_options[value]["name"])
                    except Exception:
                        self._odesign.SetSolutionType(self._solution_options[value]["name"], "")

    @property
    def report_type(self):
        """Return the default report type of the selected solution if present."""
        return self._solution_options[self.solution_type]["report_type"]

    @property
    def default_setup(self):
        """Return the default setup id of the selected solution if present."""
        return self._solution_options[self.solution_type]["default_setup"]

    @property
    def default_adaptive(self):
        """Return the default adaptive name of the selected solution if present."""
        return self._solution_options[self.solution_type]["default_adaptive"]

    @property
    def solution_types(self):
        """Return the list of all available solutions."""
        return list(self._solution_options.keys())

    @property
    def design_types(self):
        """Return the list of all available designs."""
        return [str(getattr(DesignType, i)) for i in dir(DesignType) if not i.startswith("_")]

    @property
    def intrinsics(self):
        """Get list of intrinsics for that specified setup."""
        if "intrinsics" in self._solution_options[self.solution_type]:
            return self._solution_options[self.solution_type]["intrinsics"]
        return []


class HFSSDesignSolution(DesignSolution, PyAedtBase):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._composite = False
        self._hybrid = False

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._odesign:
            try:
                self._solution_type = self._odesign.GetSolutionType()
                if "Modal" in self._solution_type:
                    self._solution_type = "Modal"
                elif "Terminal" in self._solution_type:
                    self._solution_type = "Terminal"
            except Exception:
                self._solution_type = self._design_type.default_solution
        elif self._solution_type is None:
            self._solution_type = self._design_type.default_solution
        return self._solution_type

    @solution_type.setter
    def solution_type(self, value):
        if self._aedt_version < "2021.2":
            if not value:
                self._solution_type = "DrivenModal"
                self._odesign.SetSolutionType(self._solution_type)
            elif "Modal" in value:
                self._solution_type = "DrivenModal"
                self._odesign.SetSolutionType(self._solution_type)
            elif "Terminal" in value:
                self._solution_type = "DrivenTerminal"
                self._odesign.SetSolutionType(self._solution_type)
            else:
                try:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"])
                except Exception:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"], "")
        elif value is None:
            if self._odesign:
                try:
                    self._solution_type = self._odesign.GetSolutionType()
                    if "Modal" in self._solution_type:
                        self._solution_type = "Modal"
                    elif "Terminal" in self._solution_type:
                        self._solution_type = "Terminal"
                except Exception:
                    self._solution_type = self._design_type.default_solution
            else:
                self._solution_type = self._design_type.default_solution
        elif value and value in self._solution_options and self._solution_options[value]["name"]:
            if value == "Transient" or value == "Transient Network":
                value = "Transient Network"
                self._solution_type = "Transient Network"
            elif value == "Transient Composite":
                value = "Transient Composite"
                self._solution_type = "Transient Composite"
            elif "Modal" in value:
                value = "Modal"
                self._solution_type = "Modal"
            elif "Terminal" in value:
                value = "Terminal"
                self._solution_type = "Terminal"
            else:
                self._solution_type = value
            if self._solution_options[value]["options"]:
                self._odesign.SetSolutionType(
                    self._solution_options[value]["name"], self._solution_options[value]["options"]
                )
            else:
                try:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"])
                except Exception:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"], "")

    @property
    def hybrid(self):
        """HFSS hybrid mode for the active solution."""
        if self._aedt_version < "2021.2":
            return False
        if self.solution_type is not None:
            self._hybrid = "Hybrid" in self._odesign.GetSolutionType()
        return self._hybrid

    @hybrid.setter
    def hybrid(self, value):
        if self._aedt_version < "2021.2":
            return
        if value and "Hybrid" not in self._solution_options[self.solution_type]["name"]:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("HFSS", "HFSS Hybrid")
        else:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("HFSS Hybrid", "HFSS")
        self._hybrid = value
        self.solution_type = self.solution_type

    @property
    def composite(self):
        """HFSS composite mode for the active solution."""
        if self._aedt_version < "2021.2":
            return False
        if self._composite is None and self.solution_type is not None:
            self._composite = "Composite" in self._odesign.GetSolutionType()
        return self._composite

    @composite.setter
    def composite(self, val):
        if self._aedt_version < "2021.2":
            return
        if val:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("Network", "Composite")
        else:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("Composite", "Network")
        self._composite = val
        self.solution_type = self.solution_type

    @pyaedt_function_handler()
    def set_auto_open(self, enable=True, opening_type="Radiation"):
        """Set HFSS auto open type.

        Parameters
        ----------
        enable : bool, optional
            Whether to enable auto open. The default is ``True``.
        opening_type : str, optional
            Boundary type to use with auto open. The default is `"Radiation"`.

        Returns
        -------
        bool
        """
        if self._aedt_version < "2021.2":
            return False
        options = ["NAME:Options", "EnableAutoOpen:=", enable]
        if enable:
            options.append("BoundaryType:=")
            options.append(opening_type)
        self._solution_options[self.solution_type]["options"] = options
        self.solution_type = self.solution_type
        return True


class Maxwell2DDesignSolution(DesignSolution, PyAedtBase):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._geometry_mode = "XY"

    @property
    def xy_plane(self):
        """Get/Set Maxwell 2d plane between `"XY"` and `"about Z"`."""
        return self._geometry_mode == "XY"

    @xy_plane.setter
    def xy_plane(self, value=True):
        if value:
            self._geometry_mode = "XY"
        else:
            self._geometry_mode = "about Z"
        self._solution_options[self.solution_type]["options"] = self._geometry_mode
        self.solution_type = self.solution_type

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._odesign and "GetSolutionType":
            try:
                self._solution_type = self._odesign.GetSolutionType()
            except Exception:
                self._solution_type = self._design_type.default_solution
        return self._solution_type

    @solution_type.setter
    def solution_type(self, value):
        if value is None:
            if self._odesign and "GetSolutionType" in dir(self._odesign):
                self._solution_type = self._odesign.GetSolutionType()
                if "Modal" in self._solution_type:
                    self._solution_type = "Modal"
                elif "Terminal" in self._solution_type:
                    self._solution_type = "Terminal"
            return
        elif value[-1:] == "Z":
            self._solution_type = value[:-1]
            self._solution_options[self._solution_type]["options"] = "about Z"
            self._geometry_mode = "about Z"
        elif value[-2:] == "XY":
            self._solution_type = value[:-2]
            self._solution_options[self._solution_type]["options"] = "XY"
            self._geometry_mode = "XY"
        else:
            self._solution_type = value
        if self._solution_type in self._solution_options and self._solution_options[self._solution_type]["name"]:
            try:
                if self._solution_options[self._solution_type]["options"]:
                    opts = self._solution_options[self._solution_type]["options"]
                else:
                    opts = ""
                self._odesign.SetSolutionType(self._solution_options[self._solution_type]["name"], opts)
            except Exception:
                logger.error("Failed to set solution type.")


class IcepakDesignSolution(DesignSolution, PyAedtBase):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._problem_type = "TemperatureAndFlow"

    @property
    def problem_type(self):
        """Get/Set the problem type of the icepak Design.

        It can be any of`"TemperatureAndFlow"`, `"TemperatureOnly"`,`"FlowOnly"`.
        """
        if self._odesign:
            self._problem_type = self._odesign.GetProblemType()
        return self._problem_type

    @problem_type.setter
    def problem_type(self, value="TemperatureAndFlow"):
        if value == "TemperatureAndFlow":
            self._problem_type = value
            self._solution_options[self.solution_type]["options"] = self._problem_type
            if self.solution_type == "SteadyState":
                self._solution_options[self.solution_type]["default_setup"] = 11
            else:
                self._solution_options[self.solution_type]["default_setup"] = 36
        elif value == "TemperatureOnly":
            self._problem_type = value
            self._solution_options[self.solution_type]["options"] = self._problem_type
            if self.solution_type == "SteadyState":
                self._solution_options[self.solution_type]["default_setup"] = 12
            else:
                self._solution_options[self.solution_type]["default_setup"] = 37
        elif value == "FlowOnly":
            self._problem_type = value
            self._solution_options[self.solution_type]["options"] = self._problem_type
            if self.solution_type == "SteadyState":
                self._solution_options[self.solution_type]["default_setup"] = 13
            else:
                self._solution_options[self.solution_type]["default_setup"] = 38
        else:
            raise AttributeError("Wrong input. Expected values are TemperatureAndFlow, TemperatureOnly and FlowOnly.")
        self.solution_type = self.solution_type

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._odesign:
            try:
                self._solution_type = self._odesign.GetSolutionType()
            except Exception:
                self._solution_type = self._design_type.default_solution
        return self._solution_type

    @solution_type.setter
    def solution_type(self, solution_type):
        if solution_type:
            if "SteadyState" in solution_type:
                self._solution_type = "SteadyState"
            else:
                self._solution_type = "Transient"
            if "TemperatureAndFlow" in solution_type:
                self._problem_type = "TemperatureAndFlow"
            elif "TemperatureOnly" in solution_type:
                self._problem_type = "TemperatureOnly"
            elif "FlowOnly" in solution_type:
                self._problem_type = "FlowOnly"
            if self._solution_options[self._solution_type]["name"]:
                options = [
                    "NAME:SolutionTypeOption",
                    "SolutionTypeOption:=",
                    self._solution_type,
                    "ProblemOption:=",
                    self._problem_type,
                ]
                try:
                    self._odesign.SetSolutionType(options)
                except Exception:
                    logger.error("Failed to set solution type.")


class RmXprtDesignSolution(DesignSolution, PyAedtBase):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)

    @property
    def solution_type(self):
        """Get/Set the Machine Type of the active Design."""
        if self._solution_type is None and "GetMachineType" in dir(self._odesign):
            self._solution_type = self._odesign.GetMachineType()
        return self._solution_type

    @solution_type.setter
    def solution_type(self, solution_type):
        if solution_type:
            try:
                self._odesign.SetDesignFlow(self._design_type.NAME, solution_type)
                self._solution_type = solution_type
            except Exception:
                logger.error("Failed to set design flow.")

    @property
    def design_type(self):
        """Get/Set the Machine Design Type."""
        return self._design_type

    @design_type.setter
    def design_type(self, value):
        if value:
            self._design_type = value
            self.solution_type = self._solution_type
