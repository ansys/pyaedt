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
extension_arguments = {"setup": "", "sweep": ""}
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

    solved_analysis = setups_with_solved_fields(aedtapp)

    if not solved_analysis:
        app.logger.error("No field solved solutions.")
        aedtapp.release_desktop(False, False)
        output_dict = {"setup": "", "sweep": ""}
        return output_dict
    else:
        solved_analysis_list = [f"{setup} : {sweep}" for setup, sweep in solved_analysis]

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
    combo_setup["values"] = solved_analysis_list
    combo_setup.current(0)
    combo_setup.grid(row=0, column=1, pady=10, padx=10)
    combo_setup.focus_set()

    def callback():
        master.setup = combo_setup.get()
        master.destroy()

    b = tkinter.Button(master, text="Ok", width=40, command=callback)
    b.grid(row=2, column=1, pady=10)

    app.release_desktop(False, False)

    def update_page(event=None):
        combo_setup = toolkits_combo.get()

    combo_setup.bind("<<ComboboxSelected>>", update_page)

    update_page()

    tkinter.mainloop()

    setup_ui = getattr(master, "setup", extension_arguments["setup"])
    if getattr(master, "setup"):
        setup, sweep = setup_ui.split(" : ")
    else:
        setup = extension_arguments["setup"]
        sweep = extension_arguments["sweep"]

    output_dict = {"setup": setup, "sweep": sweep}

    return output_dict


# def setups_with_solved_fields(aedt_app):
#     solved_analysis_sweeps = []
#     for setup in aedt_app.setups:
#         if setup.has_fields or setup.has_fields is None and setup.is_solved:
#             solved_analysis_sweeps.append([setup.name, "LastAdaptive"])
#         if setup.sweeps:
#             for sweep in setup.sweeps:
#                 has_fields = getattr(sweep, "has_fields", None)
#                 if has_fields is None or has_fields and sweep.is_solved:
#                     # Has fields only available for HFSS
#                     solved_analysis_sweeps.append([setup.name, sweep.name])
#
#     return solved_analysis_sweeps


def main(extension_args):
    setup = extension_args["setup"]
    sweep = extension_args["sweep"]

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

    solved_setups = setups_with_solved_fields(aedtapp)
    solved_analysis_list = [f"{setup} : {sweep}" for setup, sweep in solved_setups]
    analysis_name = ""
    if not setup or not sweep:
        app.logger.error("Not valid setup or sweep.")
    else:
        analysis_name = setup + " : " + sweep
    if analysis_name not in solved_analysis_list:
        app.logger.error("Not valid setup or sweep.")

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
