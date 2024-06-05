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

import os.path

import pyaedt
from pyaedt import get_pyaedt_app
import pyaedt.workflows
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_arguments
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"setup": "", "calculation": "", "assignment": []}
extension_description = "Simplified use of Fields Calculator"


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    # Get ports
    app = pyaedt.Desktop(
        new_desktop_session=False,
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

    # Available fields calculator expressions
    available_expressions = aedtapp.post.fields_calculator.available_expressions
    available_descriptions = {}
    for expression in available_expressions:
        available_descriptions[expression] = aedtapp.post.fields_calculator.expression_catalog[expression][
            "description"
        ]

    available_setups = aedtapp.existing_analysis_sweeps

    if not available_setups:
        app.logger.error("No setups defined.")
        aedtapp.release_desktop(False, False)
        output_dict = {"setup": "", "calculation": "", "assignment": []}
        return output_dict

    # Create UI
    master = tkinter.Tk()

    master.geometry("700x150")

    master.title("Advanced fields calculator")

    # Load the logo for the main window
    icon_path = os.path.join(pyaedt.workflows.__path__[0], "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 8))

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Solved setup:")
    label.grid(row=0, column=0, pady=10, padx=15)
    combo_setup = ttk.Combobox(master, width=30)
    combo_setup["values"] = available_setups
    combo_setup.current(0)
    combo_setup.grid(row=0, column=1, pady=10, padx=10)
    combo_setup.focus_set()

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Calculations:")
    label.grid(row=1, column=0, pady=10, padx=15)
    combo_calculation = ttk.Combobox(master, width=30)
    combo_calculation["values"] = list(available_descriptions.values())
    combo_calculation.current(0)
    combo_calculation.grid(row=1, column=1, pady=10, padx=10)
    combo_calculation.focus_set()

    def callback():
        master.setup = combo_setup.get()
        master.calculation = combo_calculation.get()
        master.destroy()

    b = tkinter.Button(master, text="Ok", width=40, command=callback)
    b.grid(row=2, column=1, pady=10)

    tkinter.mainloop()

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

    assignment = aedtapp.modeler.selections

    app.release_desktop(False, False)

    output_dict = {"setup": setup, "calculation": calculation, "assignment": assignment}

    return output_dict


def main(extension_args):
    setup = extension_args["setup"]
    calculation = extension_args["calculation"]
    assignment = extension_args["assignment"]

    app = pyaedt.Desktop(
        new_desktop_session=False,
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

    names = []
    for element in assignment:
        name = aedtapp.post.fields_calculator.add_expression(calculation, element, name=calculation + "_" + element)
        if name:
            names.append(name)

    expression_info = aedtapp.post.fields_calculator.expression_catalog[calculation]
    design_type_index = expression_info["design_type"].index(aedtapp.design_type)
    if names:
        for report_type in expression_info["report"]:
            if expression_info["fields_type"][design_type_index] == "CG Fields":
                report = aedtapp.post.reports_by_category.cg_fields(names, setup)
            else:
                report = aedtapp.post.reports_by_category.fields(names, setup)
            report.report_type = report_type
            report.create()

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
