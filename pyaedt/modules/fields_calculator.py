# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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
import os

import pyaedt
from pyaedt.generic.general_methods import generate_unique_project_name
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import read_toml


class FieldsCalculator:
    def __init__(self, app):
        self.expression_catalog = read_toml(os.path.join(pyaedt.__path__[0], "misc", "expression_catalog.toml"))
        self.__app = app
        self.design_type = app.design_type
        self.ofieldsreporter = app.ofieldsreporter

    @property
    def expression_names(self):
        """List of available expressions.

        Returns
        -------
        list
        """
        return list(self.expression_catalog.keys())

    @pyaedt_function_handler()
    def add_expression(self, calculation, assignment, name=None):
        """Add named expression.

        Parameters
        ----------
        calculation :
            Calculation type.
        assignment : int or :class:`pyaedt.modeler.cad.object3d.Object3d` or
         :class:`pyaedt.modeler.cad.FacePrimitive
            Name of the object to add the named expression from.
        name : str, optional
            Name of the named expression. The default is ``None``.

        Returns
        -------
        str, bool
            Named expression when successful, ``False`` when failed.
        """
        if assignment is not None:
            assignment = self.__app.modeler.convert_to_selections(assignment, return_list=True)[0]

        if calculation not in self.expression_names:
            self.__app.logger.error("Calculation is not available.")
            return False

        expression_info = copy.deepcopy(self.expression_catalog[calculation])

        if not name:
            name = expression_info["name"]

        expression_info["name"] = name

        if self.is_expression_defined(expression_info["name"]):
            self.__app.logger.debug("Named expression already exists.")
            return expression_info["name"]

        # Check design type
        design_type = self.__app.design_type
        if design_type not in expression_info["design_type"]:
            self.__app.logger.error("Design type is not compatible.")
            return False
        design_type_index = expression_info["design_type"].index(design_type)

        # Check assignment type
        if assignment and isinstance(assignment, str) and assignment not in self.__app.modeler.object_names:
            self.__app.logger.error("Assignment type is not correct.")
            return False

        # Check assignment type
        if assignment and isinstance(assignment, str):
            assignment_type = self.__app.modeler.objects_by_name[assignment].object_type
            if assignment_type not in expression_info["assignment_type"]:
                self.__app.logger.error("Wrong assignment type.")
                return False
        elif assignment and isinstance(assignment, int):
            if "Face" not in expression_info["assignment_type"]:
                self.__app.logger.error("Wrong assignment type.")
                return False
            else:
                assignment = "Face" + str(assignment)

        # Check constants
        if "constants" in expression_info:
            constants = expression_info["constants"]
            if constants:
                for k, v in constants.items():
                    self.__app.variable_manager.set_variable(k, v, postprocessing=True)

        # Check for dependent expressions
        if expression_info["dependent_expressions"]:
            for expression in expression_info["dependent_expressions"]:
                expression_name = self.add_expression(calculation=expression, assignment=None)
                expression_info["operations"] = [
                    operation.replace(expression, expression_name) for operation in expression_info["operations"]
                ]

        if assignment is not None:
            expression_info["assignment"] = assignment

        expression_info["operations"] = [
            operation.replace("assignment", expression_info["assignment"])
            for operation in expression_info["operations"]
        ]

        # Create clc file
        file_name = self.create_expression_file(expression_info["name"], expression_info["operations"])

        # Import clc
        self.ofieldsreporter.LoadNamedExpressions(
            os.path.abspath(file_name), expression_info["fields_type"][design_type_index], [name]
        )

        return expression_info["name"]

    @pyaedt_function_handler()
    def create_expression_file(self, name, operations):
        """Create a calculator expression file.

        Parameters
        ----------
        name : str
            Name of the expression.
        operations : list
            List of operations in the calculator.

        Returns
        -------
        str, bool
            Path of the calculator expression file when successful, ``False`` when failed.
        """
        file_name = generate_unique_project_name(
            root_name=self.__app.toolkit_directory,
            folder_name=self.__app.design_name,
            project_name=name,
            project_format="clc",
        )
        try:
            with open_file(file_name, "w") as file:
                file.write("$begin 'Named_Expression'\n")
                file.write(f"	Name('{name}')\n")
                for operation in operations:
                    file.write(f"	{operation}\n")
                file.write("$end 'Named_Expression'\n")
        except Exception:  # pragma: no cover
            return False
        return os.path.abspath(file_name)

    @pyaedt_function_handler()
    def expression_plot(self, calculation, assignment, names, setup=None):
        """Add a named expression.

        Parameters
        ----------
        calculation : str
            Calculation type.
        assignment : list
            List of assignments to apply the expression to. If the expression is not general, assignment is not needed.
        names : list
            Name of the expressions to plot.
        setup : str
            Analysis setup.

        Returns
        -------
        list
            List of created reports.
        """
        if assignment is not None:
            assignment = self.__app.modeler.convert_to_selections(assignment, return_list=True)

        for name in names:
            if not self.is_expression_defined(name):
                self.__app.logger.error("Named expression not available.")
                return False

        if calculation not in self.expression_names:
            self.__app.logger.error("Calculation is not available.")
            return False

        if not setup:
            setup = self.__app.existing_analysis_sweeps[0]

        expression_info = self.expression_catalog[calculation]
        fields_type = expression_info["fields_type"]
        primary_sweep = expression_info["primary_sweep"]

        reports = []

        for report_type in expression_info["report"]:  # pragma: no cover
            if report_type in ["Data Table", "Rectangular Plot"]:
                assignment_report = assignment
                primary_sweep_report = primary_sweep
                if self.is_general_expression(calculation):
                    # General expression to calculate the field over the polyline distance
                    primary_sweep_report = "Distance"
                else:
                    # Non-general expression does not need assignment
                    assignment_report = [None]

                if None in assignment_report or (
                    not self.__has_integer(assignment_report) and self.__has_lines(assignment_report)
                ):
                    for assign in assignment_report:
                        if "CG Fields" in fields_type and self.design_type == "Q3D Extractor":
                            report = self.__app.post.reports_by_category.cg_fields(names, setup, polyline=assign)
                        elif "DC R/L Fields" in fields_type and self.design_type == "Q3D Extractor":
                            report = self.__app.post.reports_by_category.dc_fields(names, setup, polyline=assign)
                        else:
                            report = self.__app.post.reports_by_category.fields(names, setup, polyline=assign)
                        report.report_type = report_type
                        report.primary_sweep = primary_sweep_report
                        report.create()
                        reports.append(report)
            elif report_type in ["Field_3D"]:
                intrinsic = {}
                if self.design_type == "Q3D Extractor":
                    intrinsic = {"Freq": self.__app.setups[0].props["AdaptiveFreq"]}
                for assign in assignment:
                    if isinstance(assign, int) or assign in self.__app.modeler.sheet_names:
                        report = self.__app.post.create_fieldplot_surface(
                            quantity=names[0], assignment=assign, field_type=fields_type, intrinsics=intrinsic
                        )
                        reports.append(report)
                    else:
                        if assign not in self.__app.modeler.point_names and assign not in self.__app.modeler.line_names:
                            report = self.__app.post.create_fieldplot_volume(
                                quantity=names[0], assignment=assign, field_type=fields_type, intrinsics=intrinsic
                            )
                            reports.append(report)
        return reports

    @pyaedt_function_handler()
    def delete_expression(self, name=None):
        """Delete a named expression.

        Parameters
        ----------
        name : str, optional
            Name of the named expression. The default is ``None``, in which case all named expressions are deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.ofieldsreporter.ClearAllNamedExpr()
            return True
        if self.is_expression_defined(name):
            self.ofieldsreporter.DeleteNamedExpr(name)
        return True

    @pyaedt_function_handler()
    def is_expression_defined(self, name):
        """Check if a named expression exists.

        Parameters
        ----------
        name : str,
            Named expression.

        Returns
        -------
        bool
            ``True`` when exists.
        """
        is_defined = self.ofieldsreporter.DoesNamedExpressionExists(name)
        if is_defined == 1:
            return True
        return False

    @pyaedt_function_handler()
    def is_general_expression(self, name):
        """Check if a named expression is general.

        Parameters
        ----------
        name : str,
            Named expression.

        Returns
        -------
        bool
            ``True`` if the named expression is general.
        """
        if name not in self.expression_names:
            self.__app.logger.error("Named expression not available.")
            return False
        is_general = True
        for operation in self.expression_catalog[name]["operations"]:
            if "assignment" in operation:
                is_general = False
                break
        return is_general

    @pyaedt_function_handler()
    def load_expression_file(self, input_file):
        """Load expressions from a TOML file.

        Parameters
        ----------
        input_file : str
            Full path to the file.

        Returns
        -------
        dict
            Dictionary of available expressions.
        """
        if not os.path.isfile(input_file):
            self.__app.logger.error("File does not exist.")
            return False

        new_expression_catalog = read_toml(input_file)

        if new_expression_catalog:
            self.expression_catalog.update(new_expression_catalog)

        return self.expression_catalog

    @staticmethod
    def __has_integer(lst):  # pragma: no cover
        """Check if a list has integers."""
        for item in lst:
            if isinstance(item, int):
                return True
        return False

    def __has_lines(self, lst):  # pragma: no cover
        """Check if a list has lines."""
        for item in lst:
            if item not in self.__app.modeler.line_names:
                return False
        return True
