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

import os.path

import pyaedt
from pyaedt import Hfss
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
extension_arguments = {"file_path": "", "choice": ""}
extension_description = "Push excitation from file"


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    # Get ports
    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    hfss = Hfss(project_name, design_name)

    port_selection = hfss.excitations

    if not port_selection:
        app.logger.error("No ports found.")
        hfss.release_desktop(False, False)
        output_dict = {"choice": "", "file_path": ""}
        return output_dict

    # Create UI
    master = tkinter.Tk()

    master.geometry("700x150")

    master.title("Assign push excitation to port from transient data")

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
    var.set("Choose a port:")
    label.grid(row=0, column=0, pady=10)
    combo = ttk.Combobox(master, width=30)
    combo["values"] = port_selection
    combo.current(0)
    combo.grid(row=0, column=1, pady=10, padx=5)
    combo.focus_set()
    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2)
    var2.set("Browse file:")
    label2.grid(row=1, column=0, pady=10)
    text = tkinter.Text(master, width=50, height=1)
    text.grid(row=1, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Transient File",
            filetypes=(("Transient curve", "*.csv*"), ("all files", "*.*")),
        )
        text.insert(tkinter.END, filename)

    b1 = tkinter.Button(master, text="...", width=10, command=browseFiles)
    b1.grid(row=3, column=0)
    b1.grid(row=1, column=2, pady=10)

    def callback():
        master.choice_ui = combo.get()
        master.file_path_ui = text.get("1.0", tkinter.END).strip()
        master.destroy()

    b = tkinter.Button(master, text="Ok", width=40, command=callback)
    b.grid(row=2, column=1, pady=10)

    tkinter.mainloop()

    file_path_ui = getattr(master, "file_path_ui", extension_arguments["file_path"])
    choice_ui = getattr(master, "choice_ui", extension_arguments["choice"])

    if not file_path_ui or not os.path.isfile(file_path_ui):
        app.logger.error("File does not exist.")

    if not choice_ui:
        app.logger.error("Excitation not found.")

    hfss.release_desktop(False, False)

    output_dict = {"choice": choice_ui, "file_path": file_path_ui}

    return output_dict


def main(extension_args):
    choice = extension_args["choice"]
    file_path = extension_args["file_path"]

    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    hfss = Hfss(project_name, design_name)

    if not os.path.isfile(file_path):  # pragma: no cover
        app.logger.error("File does not exist.")
    elif choice:
        hfss.edit_source_from_file(choice, file_path, is_time_domain=True)
        app.logger.info("Excitation assigned correctly.")
    else:
        app.logger.error("Failed to select a port.")

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
