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
import os
import warnings

from jsonschema import exceptions
from jsonschema import validate

import ansys.aedt.core
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import generate_unique_project_name
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.file_utils import read_configuration_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class FieldsCalculator(PyAedtBase):
    """Provides the Advanced fields calculator methods.

    Provide methods to add, load and delete named expressions on top of the
    already existing ones in AEDT Fields calculator.

    Parameters
    ----------
    app :
        Inherited parent object.

    Examples
    --------
    Custom expressions can be added as dictionary on-the-fly:

    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
    >>> my_expression = {
    ...     "name": "test",
    ...     "description": "Voltage drop along a line",
    ...     "design_type": ["HFSS", "Q3D Extractor"],
    ...     "fields_type": ["Fields", "CG Fields"],
    ...     "solution_type": "",
    ...     "primary_sweep": "Freq",
    ...     "assignment": "",
    ...     "assignment_type": ["Line"],
    ...     "operations": [
    ...         "Fundamental_Quantity('E')",
    ...         "Operation('Real')",
    ...         "Operation('Tangent')",
    ...         "Operation('Dot')",
    ...         "EnterLine('assignment')",
    ...         "Operation('LineValue')",
    ...         "Operation('Integrate')",
    ...         "Operation('CmplxR')",
    ...     ],
    ...     "report": ["Data Table", "Rectangular Plot"],
    ... }
    >>> expr_name = hfss.post.fields_calculator.add_expression(my_expression, "Polyline1")
    >>> hfss.desktop_class.release_desktop(False, False)

    or they can be added from the ``expression_catalog.toml``:

    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
    >>> expr_name = hfss.post.fields_calculator.add_expression("voltage_line", "Polyline1")
    >>> hfss.desktop_class.release_desktop(False, False)

    """

    def __init__(self, app):
        self.expression_catalog = read_configuration_file(
            os.path.join(
                ansys.aedt.core.__path__[0],
                "visualization",
                "post",
                "fields_calculator_files",
                "expression_catalog.toml",
            )
        )
        self.expression_schema = read_configuration_file(
            os.path.join(
                ansys.aedt.core.__path__[0],
                "visualization",
                "post",
                "fields_calculator_files",
                "fields_calculator.schema.json",
            )
        )
        self.__app = app
        self.design_type = app.design_type
        self.ofieldsreporter = app.ofieldsreporter

    @property
    def expression_names(self):
        """List of available expressions.

        Returns
        -------
        list
            List of available expressions in the catalog.
        """
        return list(self.expression_catalog.keys())

    @pyaedt_function_handler()
    def add_expression(self, calculation, assignment, name=None):
        """Add named expression.

        Parameters
        ----------
        calculation : str, dict
            Calculation type.
            If provided as a string, it has to be a name defined in the expression_catalog.toml.
            If provided as a dict, it has to contain all the necessary arguments to define an expression.
            For reference look at the expression_catalog.toml.
        assignment : int or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d` or
         :class:`ansys.aedt.core.modeler.cad.FacePrimitive
            Name of the object to add the named expression from.
        name : str, optional
            Name of the named expression. The default is ``None``.

        Returns
        -------
        str, bool
            Named expression when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        >>> my_expression = {
        ...     "name": "test",
        ...     "description": "Voltage drop along a line",
        ...     "design_type": ["HFSS", "Q3D Extractor"],
        ...     "fields_type": ["Fields", "CG Fields"],
        ...     "solution_type": "",
        ...     "primary_sweep": "Freq",
        ...     "assignment": "",
        ...     "assignment_type": ["Line"],
        ...     "operations": [
        ...         "Fundamental_Quantity('E')",
        ...         "Operation('Real')",
        ...         "Operation('Tangent')",
        ...         "Operation('Dot')",
        ...         "EnterLine('assignment')",
        ...         "Operation('LineValue')",
        ...         "Operation('Integrate')",
        ...         "Operation('CmplxR')",
        ...     ],
        ...     "report": ["Data Table", "Rectangular Plot"],
        ... }
        >>> expr_name = hfss.post.fields_calculator.add_expression(my_expression, "Polyline1")
        >>> hfss.desktop_class.release_desktop(False, False)
        """
        if assignment is not None:
            assignment = self.__app.modeler.convert_to_selections(assignment, return_list=True)[0]

        if calculation not in self.expression_names:
            if isinstance(calculation, dict):
                expression_info = self.validate_expression(calculation)
                if not expression_info:
                    return False
            else:
                self.__app.logger.error("Calculation does not exist in expressions catalog.")
                return False
        else:
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
        if self.__app.design_type not in ["HFSS 3D Layout Design", "HFSS 3D Layout"]:
            if (
                assignment and isinstance(assignment, str) and assignment not in self.__app.modeler.object_names
            ):  # pragma no cover
                self.__app.logger.error("Assignment type is not correct.")
                return False

            # Check assignment type
            if assignment and isinstance(assignment, str):  # pragma no cover
                assignment_type = self.__app.modeler.objects_by_name[assignment].object_type
                if assignment_type not in expression_info["assignment_type"]:
                    self.__app.logger.error("Wrong assignment type.")
                    return False
            elif assignment and isinstance(assignment, int):  # pragma no cover
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
                    self.__app.variable_manager.set_variable(k, v, is_post_processing=True)

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
        """Create plots defined in the expression catalog.

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

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        >>> expr_name = hfss.post.fields_calculator.add_expression("voltage_line", "Polyline1")
        >>> reports = hfss.post.fields_calculator.expression_plot("voltage_line", "Polyline1", [name])
        >>> hfss.desktop_class.release_desktop(False, False)
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

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        >>> expr_name = hfss.post.fields_calculator.add_expression("voltage_line", "Polyline1")
        >>> hfss.post.fields_calculator.delete_expression(expr_name)
        >>> hfss.desktop_class.release_desktop(False, False)
        """
        if not name:
            self.ofieldsreporter.ClearAllNamedExpr()
            return True
        if self.is_expression_defined(name):
            self.ofieldsreporter.CalcStack("clear")
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
            ``True`` when it exists, ``False`` otherwise.
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
            ``True`` if the named expression is general, ``False`` otherwise.
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
        """Load expressions from an external TOML file.

        Parameters
        ----------
        input_file : str
            Full path to the file.

        Returns
        -------
        dict
            Dictionary of available expressions.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> my_toml = os.path.join("my_path_to_toml", "my_toml.toml")
        >>> new_catalog = hfss.post.fields_calculator.load_expression_file(my_toml)
        >>> hfss.desktop_class.release_desktop(False, False)
        """
        if not os.path.isfile(input_file):
            self.__app.logger.error("File does not exist.")
            return False

        new_expression_catalog = read_configuration_file(input_file)

        if new_expression_catalog:
            for _, new_expression_props in new_expression_catalog.items():
                new_expression = self.validate_expression(new_expression_props)
                if new_expression:
                    self.expression_catalog.update(new_expression)

        return self.expression_catalog

    @pyaedt_function_handler()
    def validate_expression(self, expression):
        """Validate expression file against the schema.

        The default schema can be found in ``pyaedt/misc/fields_calculator.schema.json``.

        Parameters
        ----------
        expression : dict
            Expression defined as a dictionary.

        Returns
        -------
        dict or bool
            Expression if the input expression is valid, ``False`` otherwise.
        """
        if not isinstance(expression, dict):
            self.__app.logger.error("Incorrect data type.")
            return False

        try:
            validate(instance=expression, schema=self.expression_schema)
            for prop_name, sub_schema in self.expression_schema["properties"].items():
                if "default" in sub_schema and prop_name not in expression:
                    expression[prop_name] = sub_schema["default"]
            return expression
        except exceptions.ValidationError as e:
            self.__app.logger.warning("Configuration is invalid.")
            self.__app.logger.warning("Validation error:" + e.message)
            return False

    @pyaedt_function_handler()
    def calculator_write(self, expression, output_file, setup=None, intrinsics=None):
        """Save the content of the stack register for future reuse in a later Field Calculator session.

        Parameters
        ----------
        expression : str
            Expression name.
            The expression must exist already in the named expressions list in AEDT Fields Calculator.
        output_file : str
            File path to save the stack entry to.
            File extension must be either ``.fld`` or ``.reg``.
        setup : str
            Solution name.
            If not provided the nominal adaptive solution is taken.
        intrinsics : dict
            Intrinsics variables provided as a dictionary.
            Key is the variable name and value is the variable value.
            These are typically: frequency, time and phase.
            If it is a dictionary, keys depend on the solution type and can be expressed as:
            - ``"Freq"``.
            - ``"Time"``.
            - ``"Phase"``.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        >>> expr_name = hfss.post.fields_calculator.add_expression("voltage_line", "Polyline1")
        >>> file_path = os.path.join(hfss.working_directory, "my_expr.fld")
        >>> hfss.post.fields_calculator.calculator_write("voltage_line", file_path, hfss.nominal_adaptive)
        >>> hfss.desktop_class.release_desktop(False, False)
        """
        warnings.warn("Use :func:`write` method instead.", DeprecationWarning)
        return self.write(expression, output_file, setup=setup, intrinsics=intrinsics)  # pragma: no cover

    @pyaedt_function_handler()
    def write(self, expression, output_file, setup=None, intrinsics=None):
        """Save the content of the stack register for future reuse in a later Field Calculator session.

        Parameters
        ----------
        expression : str
            Expression name.
            The expression must exist already in the named expressions list in AEDT Fields Calculator.
        output_file : str
            File path to save the stack entry to.
            File extension must be either ``.fld`` or ``.reg``.
        setup : str
            Solution name.
            If not provided the nominal adaptive solution is taken.
        intrinsics : dict
            Intrinsics variables provided as a dictionary.
            Key is the variable name and value is the variable value.
            These are typically: frequency, time and phase.
            If it is a dictionary, keys depend on the solution type and can be expressed as:
            - ``"Freq"``.
            - ``"Time"``.
            - ``"Phase"``.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> poly = hfss.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        >>> expr_name = hfss.post.fields_calculator.add_expression("voltage_line", "Polyline1")
        >>> file_path = os.path.join(hfss.working_directory, "my_expr.fld")
        >>> hfss.post.fields_calculator.write("voltage_line", file_path, hfss.nominal_adaptive)
        >>> hfss.desktop_class.release_desktop(False, False)
        """
        if not self.is_expression_defined(expression):
            self.__app.logger.error("Expression does not exist in current stack.")
            return False
        if os.path.splitext(output_file)[1] not in [".fld", ".reg"]:
            self.__app.logger.error("Invalid file extension. Accepted extensions are '.fld' and '.reg'.")
            return False
        if not setup:
            setup = self.__app.nominal_adaptive
        setup_name = setup.split(":")[0].strip(" ")
        if setup_name not in self.__app.setup_names:
            self.__app.logger.error("Invalid setup name.")
            return False
        self.ofieldsreporter.CalcStack("clear")
        self.ofieldsreporter.CopyNamedExprToStack(expression)
        args = []
        for k, v in self.__app.variable_manager.design_variables.items():
            args.append(f"{k}:=")
            args.append(v.expression)
        intrinsics = self.__app.post._check_intrinsics(intrinsics)
        for k, v in intrinsics.items():
            if k == "Time" and self.__app.solution_type == "SteadyState":
                continue
            args.append(f"{k}:=")
            args.append(v)
        self.ofieldsreporter.CalculatorWrite(output_file, ["Solution:=", setup], args)
        self.ofieldsreporter.CalcStack("clear")
        return True

    @pyaedt_function_handler()
    def evaluate(self, expression, setup=None, intrinsics=None):
        """Evaluate an expression and return the value.

        Parameters
        ----------
        expression : str
            Expression name.
            The expression must exist already in the named expressions list in AEDT Fields Calculator.
        setup : str
            Solution name.
            If not provided the nominal adaptive solution is taken.
        intrinsics : dict
            Intrinsics variables provided as a dictionary.
            Key is the variable name and value is the variable value.
            These are typically: frequency, time and phase.
            If it is a dictionary, keys depend on the solution type and can be expressed as:
            - ``"Freq"``.
            - ``"Time"``.
            - ``"Phase"``.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.

        Returns
        -------
        float
            Value computed.
        """
        out_file = os.path.join(self.__app.working_directory, generate_unique_name("expression") + ".fld")
        self.write(expression, setup=setup, intrinsics=intrinsics, output_file=out_file)
        value = None
        if os.path.exists(out_file):
            with open_file(out_file, "r") as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                value = lines[-1]
            try:
                os.remove(out_file)
            except OSError:
                pass
        return value

    @pyaedt_function_handler()
    def export(
        self,
        quantity,
        solution=None,
        variations=None,
        output_file=None,
        intrinsics=None,
        phase=None,
        sample_points=None,
        export_with_sample_points=True,
        reference_coordinate_system="Global",
        export_in_si_system=True,
        export_field_in_reference=True,
        grid_type=None,
        grid_center=None,
        grid_start=None,
        grid_stop=None,
        grid_step=None,
        is_vector=False,
        assignment="AllObjects",
        objects_type="Vol",
    ):
        """Export the field quantity at the top of the register to a file, mapping it to a grid of points.

        Two options are available for defining the grid points on which to export:
        -   Input grid points from file : Maps the field quantity to a customized grid of points.
                                          Before using this command, you must create a file containing the points
                                          and units.
        -   Calculate grid points : Maps the field quantity to a three-dimensional Cartesian grid.
                                    You specify the dimensions and spacing of the grid in the x, y, and z directions,
                                    with units. The initial units are taken from the model.
                                    Other grid options are: Cylindrical, in which case rho, phi and z directions must be
                                    specified, or Spherical, in which case r, theta and phi directions must be
                                    specified.

        If you want to adopt the first option you must provide either the file containing the grid of points
        or a list of sample points in ``sample_points``. In the latter case, a new file is created
        in the working directory called "temp_points.pts" that will be automatically written with the data points
        provided and consequently imported.
        If you want to adopt the second option you must provide the grid type (Cartesian, Cylindrical or Spherical).
        If ``grid_center``, ``grid_start`` or ``grid_stop`` are not provided the default values are used.

        Parameters
        ----------
        quantity : str
            Name of the quantity to export.
        solution : str, optional
            Name of the solution in the format ``"solution : sweep"``. The default is ``None``.
        variations : dict, optional
            Dictionary of all variation variables with their values.
            The default is ``None``.
        output_file : str, optional
            Full path and name to save the file to.
            The default is ``None``, in which case the file is exported
            to the working directory.
        assignment : str, optional
            List of objects to export. The default is ``"AllObjects"``.
        objects_type : str, optional
            Type of objects to export. The default is ``"Vol"``.
            Options are ``"Surf"`` for surface and ``"Vol"`` for
            volume.
        intrinsics : dict, str, optional
            Intrinsic variables required to compute the field before the export.
            These are typically: frequency, time and phase.
            It can be provided either as a dictionary or as a string.
            If it is a dictionary, keys depend on the solution type and can be expressed in lower or camel case as:
            - ``"Freq"`` or ``"Frequency"``
            - ``"Time"``
            - ``"Phase"``
            If it is a string, it can either be ``"Freq"`` or ``"Time"`` depending on the solution type.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.
        phase : str, optional
            Field phase. The default is ``None``.
            This argument is deprecated. Please use ``intrinsics`` and provide the phase as a dictionary key instead.
        sample_points : str, list
            Name of the file with sample points or list of the sample points.
        export_with_sample_points : bool, optional
            Whether to include the sample points in the file to export.
            The default is ``True``.
        reference_coordinate_system : str, optional
            Reference coordinate system in the file to export.
            The default is ``"Global"``.
        export_in_si_system : bool, optional
            Whether the provided sample points are defined in the SI system or model units.
            The default is ``True``.
        export_field_in_reference : bool, optional
            Whether to export the field in reference coordinate system.
            The default is ``True``.
        grid_type : str
            Type of the grid to export. The options are:
            - ``Cartesian``
            - ``Cylindrical``
            - ``Spherical``
        grid_center : list, optional
            The ``[x, y, z]`` coordinates for the center of the grid.
            The default is ``[0, 0, 0]``. This parameter is disabled if ``gridtype=
            "Cartesian"``.
        grid_start : list, optional
            The ``[x, y, z]`` coordinates for the starting point of the grid.
            The default is ``[0, 0, 0]``.
        grid_stop : list, optional
            The ``[x, y, z]`` coordinates for the stopping point of the grid.
            The default is ``[0, 0, 0]``.
        grid_step : list, optional
            The ``[x, y, z]`` coordinates for the step size of the grid.
            The default is ``[0, 0, 0]``.
        is_vector : bool, optional
            Whether the quantity is a vector. The  default is ``False``.

        Returns
        -------
        bool or str
            The path to the exported field file when successful, ``False`` when failed.
        """
        if sample_points:
            if isinstance(sample_points, str):
                sample_points_file = sample_points
                sample_points = None
            elif isinstance(sample_points, list):
                sample_points_file = None
                sample_points = sample_points
            else:
                self.__app.logger.error("``sample_points`` can only be either a string or a list.")
                return False
            output_file = self.__app.post.export_field_file(
                quantity=quantity,
                solution=solution,
                variations=variations,
                output_file=output_file,
                assignment=assignment,
                objects_type=objects_type,
                intrinsics=intrinsics,
                phase=phase,
                sample_points_file=sample_points_file,
                sample_points=sample_points,
                export_with_sample_points=export_with_sample_points,
                reference_coordinate_system=reference_coordinate_system,
                export_in_si_system=export_in_si_system,
                export_field_in_reference=export_field_in_reference,
            )
        elif grid_type:
            if grid_type not in ["Cartesian", "Cylindrical", "Spherical"]:
                self.__app.logger.error("Invalid grid type.")
                return False
            output_file = self.__app.post.export_field_file_on_grid(
                quantity=quantity,
                solution=solution,
                variations=variations,
                file_name=output_file,
                grid_type=grid_type,
                grid_center=grid_center,
                grid_start=grid_start,
                grid_stop=grid_stop,
                grid_step=grid_step,
                is_vector=is_vector,
                intrinsics=intrinsics,
                phase=phase,
                export_with_sample_points=export_with_sample_points,
                reference_coordinate_system=reference_coordinate_system,
                export_in_si_system=export_in_si_system,
                export_field_in_reference=export_field_in_reference,
            )
        else:
            self.__app.logger.error(
                "You have to provide one of the three following inputs: a path to a file containing the grid of points,"
                " a sample list of points or the grid type with a three dimensional grid."
            )
            return False

        if os.path.exists(output_file):
            return output_file
        return False

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
