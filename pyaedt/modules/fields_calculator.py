# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
        self.ofieldsreporter = app.ofieldsreporter

    @property
    def available_expressions(self):
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
        calculation : str
            Calculation to add.
        assignment : str
            Name of the object from which to add the named expression.
        name : str, optional
            Name of the named expression. The default is ``None``.

        Returns
        -------
        str, bool
            Named expression when successful, ``False`` when failed.
        """
        if calculation not in self.available_expressions:
            self.__app.logger.error("Calculation is not available.")
            return False

        expression_info = copy.deepcopy(self.expression_catalog[calculation])

        if not name:
            name = expression_info["name"]

        expression_info["name"] = name

        if self.is_expression_defined(expression_info["name"]):
            self.__app.logger.warning("Named expression already exists.")
            return expression_info["name"]

        # Check design type
        design_type = self.__app.design_type
        if design_type not in expression_info["design_type"]:
            self.__app.logger.error("Design type is not compatible.")
            return False
        design_type_index = expression_info["design_type"].index(design_type)

        # Check assignment type
        if assignment not in self.__app.modeler.object_names:
            self.__app.logger.error("Assignment type is not correct.")
            return False

        # Check assignment type
        assignment_type = self.__app.modeler.objects_by_name[assignment].object_type
        if assignment_type not in expression_info["assignment_type"]:
            self.__app.logger.error("Wrong assignment type.")
            return False

        expression_info["assignment"] = assignment

        expression_info["operations"] = [
            operation.replace("assignment", expression_info["assignment"])
            for operation in expression_info["operations"]
        ]

        # Create clc
        file_name = self.create_expression_file(expression_info["name"], expression_info["operations"])

        # Import CLC
        self.ofieldsreporter.LoadNamedExpressions(
            os.path.abspath(file_name), expression_info["fields_type"][design_type_index], [name]
        )

        return expression_info["name"]

    @pyaedt_function_handler()
    def create_expression_file(self, name, operations):
        """Create calculator expression file.

        Parameters
        ----------
        name : str
            Name of the expression.
        expression : str
            Expression to add.
        operations : list
            List of operations in the calculator.

        Returns
        -------
        str, bool
            Path of the calculator expression file when successful, ``False`` when failed.
        """
        file_name = generate_unique_project_name(
            rootname=self.__app.toolkit_directory,
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
    def delete_expression(self, name=None):
        """Delete named expression.

        Parameters
        ----------
        name : str, optional
            Name of the named expression. The default is ``None`` in which case all named expressions are deleted.

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
        """Check if expression exists.

        Parameters
        ----------
        name : str,
            Named expression.

        Returns
        -------
        bool
            ``True`` when exists.
        """
        return self.ofieldsreporter.DoesNamedExpressionExists(name)
