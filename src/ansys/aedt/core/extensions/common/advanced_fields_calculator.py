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

from dataclasses import dataclass
from dataclasses import field
import os
from pathlib import Path
import tkinter
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

EXTENSION_DEFAULT_ARGUMENTS = {"setup": "", "calculation": "", "assignments": []}
EXTENSION_TITLE = "Advanced fields calculator"


@dataclass
class AdvancedFieldsCalculatorExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    setup: str = ""
    calculation: str = ""
    assignments: list = field(default_factory=lambda: [])


class AdvancedFieldsCalculatorExtension(ExtensionProjectCommon):
    """Extension for advanced fields calculator in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=2,
            toggle_column=1,
        )
        # Add private attributes and initialize them through __load_expression_files
        self.__setups = None
        self.__available_descriptions = None
        self.__load_expression_files()
        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

    def check_design_type(self):
        """Check if the design type is HFSS, Icepak, HFSS 3D, Maxwell 3D, Q3D, Maxwell 2D, Q2D, Mechanical"""
        if self.aedt_application.design_type not in [
            "HFSS",
            "Icepak",
            "HFSS 3D",
            "Maxwell 3D",
            "Q3D",
            "Maxwell 2D",
            "Q2D",
            "Mechanical",
        ]:
            self.release_desktop()
            raise AEDTRuntimeError(
                "This extension only works with HFSS, Icepak, "
                "HFSS 3D, Maxwell 3D, Q3D, Maxwell 2D, Q2D, or Mechanical designs."
            )

    def __load_expression_files(self):
        """Load expression files from the current directory and personal library."""
        # Load new expressions from current directory
        current_directory = Path.cwd()
        toml_files = list(current_directory.glob("*.toml"))
        for toml_file in toml_files:
            # Skip the pyproject.toml file to avoid warning messages
            if toml_file.name != "pyproject.toml":
                self.desktop.logger.debug("Loading expression file: %s", toml_file)
                self.aedt_application.post.fields_calculator.load_expression_file(toml_file)

        # Load new expressions from Personal Lib directory
        personal_lib_directory = Path(self.aedt_application.personallib)
        toml_files = list(personal_lib_directory.glob("*.toml"))
        for toml_file in toml_files:
            self.desktop.logger.debug("Loading expression file: %s", toml_file)
            self.aedt_application.post.fields_calculator.load_expression_file(toml_file)

        setups = self.aedt_application.existing_analysis_sweeps
        if not setups:
            self.release_desktop()
            raise AEDTRuntimeError("No setups defined. Please define at least one setup in the project.")
        self.__setups = setups

        # Available fields calculator expressions
        available_expressions = self.aedt_application.post.fields_calculator.expression_catalog
        available_descriptions = {}
        for expression, expression_info in available_expressions.items():
            if "design_type" in expression_info and self.aedt_application.design_type in expression_info["design_type"]:
                if (
                    "Transient" in self.aedt_application.solution_type
                    and "Transient" in expression_info["solution_type"]
                ):
                    available_descriptions[expression] = expression_info["description"]
                elif (
                    "Transient" not in self.aedt_application.solution_type
                    and "Transient" not in expression_info["solution_type"]
                ):
                    available_descriptions[expression] = expression_info["description"]
        self.__available_descriptions = available_descriptions

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        label = ttk.Label(self.root, text="Solved setup:", style="PyAEDT.TLabel")
        label.grid(row=0, column=0, padx=15, pady=10)

        combo_setup = ttk.Combobox(self.root, width=30, style="PyAEDT.TCombobox", name="combo_setup")
        combo_setup["values"] = self.__setups
        combo_setup.current(0)
        combo_setup.grid(row=0, column=1, padx=15, pady=10)
        combo_setup.focus_set()

        label = ttk.Label(self.root, text="Calculation:", style="PyAEDT.TLabel")
        label.grid(row=1, column=0, padx=15, pady=10)

        combo_calculation = ttk.Combobox(self.root, width=30, style="PyAEDT.TCombobox", name="combo_calculation")
        combo_calculation["values"] = list(self.__available_descriptions.values())
        combo_calculation.current(0)
        combo_calculation.grid(row=1, column=1, padx=15, pady=10)
        combo_calculation.focus_set()

        def callback(extension: AdvancedFieldsCalculatorExtension):
            assignments = extension.aedt_application.modeler.convert_to_selections(
                extension.aedt_application.modeler.selections, True
            )
            calculation_label = combo_calculation.get()
            calculation = next(
                (key for key, value in extension.available_descriptions.items() if value == calculation_label),
                calculation_label,
            )
            data = AdvancedFieldsCalculatorExtensionData(
                setup=combo_setup.get(), calculation=calculation, assignments=assignments
            )
            extension.data = data
            self.root.destroy()

        ok_button = ttk.Button(
            self.root, text="Ok", width=20, command=lambda: callback(self), style="PyAEDT.TButton", name="ok_button"
        )
        ok_button.grid(row=2, column=0, padx=15, pady=10)

    @property
    def available_descriptions(self):
        """Get available descriptions for fields calculator expressions."""
        return self.__available_descriptions


def main(data: AdvancedFieldsCalculatorExtensionData):
    """Main function to run the advanced fields calculator extension."""
    if not data.calculation:
        raise AEDTRuntimeError("No calculation provided to the extension.")
    if not data.setup:
        raise AEDTRuntimeError("No setup provided to the extension.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    if active_design.GetDesignType() == "HFSS 3D Layout Design":  # pragma: no cover
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()

    aedt_app = get_pyaedt_app(project_name, design_name)

    assignments = []
    for assignment in data.assignments:
        if assignment not in aedt_app.modeler.object_names and "Face" in assignment:
            assignments.append(aedt_app.modeler.get_face_by_id(int(assignment[4:])))
        else:
            assignments.append(assignment)

    names = []
    if not aedt_app.post.fields_calculator.is_general_expression(data.calculation):
        for assignment in assignments:
            assignment_str = assignment
            if isinstance(assignment_str, FacePrimitive):  # pragma: no cover
                assignment_str = str(assignment.id)
            elif not isinstance(assignment_str, str):  # pragma: no cover
                assignment_str = generate_unique_name(data.calculation)
            name = aedt_app.post.fields_calculator.add_expression(
                data.calculation, assignment, data.calculation + "_" + assignment_str
            )
            if name:
                names.append(name)
            else:
                raise AEDTRuntimeError(f"Failed to add expression for assignment {assignment_str}.")
    else:
        names.append(aedt_app.post.fields_calculator.add_expression(data.calculation, None))

    if not aedt_app.post.fields_calculator.is_general_expression(data.calculation):
        _ = aedt_app.post.fields_calculator.expression_plot(data.calculation, None, names, data.setup)
    else:
        _ = aedt_app.post.fields_calculator.expression_plot(data.calculation, assignments, names, data.setup)

    if "PYTEST_CURRENT_TEST" not in os.environ:
        extension.desktop.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = AdvancedFieldsCalculatorExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)
    else:
        data = AdvancedFieldsCalculatorExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
