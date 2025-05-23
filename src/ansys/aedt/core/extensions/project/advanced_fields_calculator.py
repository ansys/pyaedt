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

from pathlib import Path

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"setup": "", "calculation": "", "assignment": []}
extension_description = "Advanced fields calculator"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    from ansys.aedt.core.extensions.misc import ExtensionTheme

    # Get ports
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        specified_version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    if active_design.GetDesignType() == "HFSS 3D Layout Design":
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    # Load new expressions from file
    current_directory = Path.cwd()
    toml_files = list(current_directory.glob("*.toml"))
    for toml_file in toml_files:
        aedtapp.post.fields_calculator.load_expression_file(toml_file)

    # Personal Lib directory
    personal_lib_directory = Path(aedtapp.personallib)
    toml_files = list(personal_lib_directory.glob("*.toml"))
    for toml_file in toml_files:
        aedtapp.post.fields_calculator.load_expression_file(toml_file)

    # Available fields calculator expressions
    available_expressions = aedtapp.post.fields_calculator.expression_catalog
    available_descriptions = {}
    for expression, expression_info in available_expressions.items():
        if "design_type" in expression_info and aedtapp.design_type in expression_info["design_type"]:
            if "Transient" in aedtapp.solution_type and "Transient" in expression_info["solution_type"]:
                available_descriptions[expression] = expression_info["description"]
            elif "Transient" not in aedtapp.solution_type and "Transient" not in expression_info["solution_type"]:
                available_descriptions[expression] = expression_info["description"]

    available_setups = aedtapp.existing_analysis_sweeps

    if not available_setups:
        app.logger.error("No setups defined.")
        aedtapp.release_desktop(False, False)
        output_dict = {"setup": "", "calculation": "", "assignment": []}
        return output_dict

    # Create UI
    master = tkinter.Tk()
    master.title(extension_description)

    # Detect if user closes the UI
    master.flag = False

    # Load the logo for the main window
    icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo.png"
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    theme = ExtensionTheme()

    # Apply light theme initially
    theme.apply_light_theme(style)
    master.theme = "light"

    # Set background color of the window (optional)
    master.configure(bg=theme.light["widget_bg"])

    label = ttk.Label(master, text="Solved setup:", style="PyAEDT.TLabel")
    label.grid(row=0, column=0, pady=10, padx=15)

    combo_setup = ttk.Combobox(master, width=30, style="PyAEDT.TCombobox")
    combo_setup["values"] = available_setups
    combo_setup.current(0)
    combo_setup.grid(row=0, column=1, pady=10, padx=10)
    combo_setup.focus_set()

    label = ttk.Label(master, text="Calculations:", style="PyAEDT.TLabel")
    label.grid(row=1, column=0, pady=10, padx=15)

    combo_calculation = ttk.Combobox(master, width=30, style="PyAEDT.TCombobox")
    combo_calculation["values"] = list(available_descriptions.values())
    combo_calculation.current(0)
    combo_calculation.grid(row=1, column=1, pady=10, padx=10)
    combo_calculation.focus_set()

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263d")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=2, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263d", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        master.setup = combo_setup.get()
        master.calculation = combo_calculation.get()
        master.destroy()

    b = ttk.Button(master, text="Ok", width=40, command=callback, style="PyAEDT.TButton")
    b.grid(row=2, column=1, pady=10)

    tkinter.mainloop()

    output_dict = {}

    if master.flag:
        setup_ui = getattr(master, "setup", extension_arguments["setup"])
        if getattr(master, "setup"):
            setup = setup_ui
        else:
            setup = extension_arguments["setup"]

        calculation_ui = getattr(master, "calculation", extension_arguments["calculation"])
        calculation = extension_arguments["setup"]

        if getattr(master, "setup"):
            calculation_description = calculation_ui
            for k, v in available_descriptions.items():
                if calculation_description == v:
                    calculation = k
                    break

        assignments = aedtapp.modeler.convert_to_selections(aedtapp.modeler.selections, True)
        output_dict = {"setup": setup, "calculation": calculation, "assignment": assignments}

    app.release_desktop(False, False)

    return output_dict


def main(extension_args):
    setup = extension_args["setup"]
    calculation = extension_args["calculation"]
    assignment_selection = extension_args["assignment"]

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    if active_design.GetDesignType() == "HFSS 3D Layout Design":  # pragma: no cover
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    if not calculation:
        aedtapp.logger.warning("No calculation selected.")
        if not extension_args["is_test"]:  # pragma: no cover
            app.release_desktop(False, False)
        return False

    assignments = []
    for assignment in assignment_selection:
        if assignment not in aedtapp.modeler.object_names and "Face" in assignment:
            assignments.append(aedtapp.modeler.get_face_by_id(int(assignment[4:])))
        else:
            assignments.append(assignment)

    # Load new expressions from file
    # Current directory
    # Load new expressions from file
    current_directory = Path.cwd()
    toml_files = list(current_directory.glob("*.toml"))
    for toml_file in toml_files:
        aedtapp.post.fields_calculator.load_expression_file(toml_file)

    # Personal Lib directory
    personal_lib_directory = Path(aedtapp.personallib)
    toml_files = list(personal_lib_directory.glob("*.toml"))
    for toml_file in toml_files:  # pragma: no cover
        aedtapp.post.fields_calculator.load_expression_file(toml_file)

    names = []

    if not aedtapp.post.fields_calculator.is_general_expression(calculation):
        for assignment in assignments:
            assignment_str = assignment
            if isinstance(assignment_str, FacePrimitive):  # pragma: no cover
                assignment_str = str(assignment.id)
            elif not isinstance(assignment_str, str):  # pragma: no cover
                assignment_str = generate_unique_name(calculation)
            name = aedtapp.post.fields_calculator.add_expression(
                calculation, assignment, calculation + "_" + assignment_str
            )
            if name:
                names.append(name)
            else:
                aedtapp.logger.error("Wrong assignment.")
                if not extension_args["is_test"]:  # pragma: no cover
                    app.release_desktop(False, False)
                return False
    else:
        names.append(aedtapp.post.fields_calculator.add_expression(calculation, None))

    if not aedtapp.post.fields_calculator.is_general_expression(calculation):
        _ = aedtapp.post.fields_calculator.expression_plot(calculation, None, names, setup)
    else:
        _ = aedtapp.post.fields_calculator.expression_plot(calculation, assignments, names, setup)

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value
            main(args)
    else:
        main(args)
