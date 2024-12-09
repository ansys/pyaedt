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

# Extension template to help get started

import os

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"origin_x": 0, "origin_y": 0, "origin_z": 0, "radius": 1}
extension_description = "Extension template - Create sphere"


def frontend():
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    # Create UI
    master = tkinter.Tk()

    master.geometry()

    master.title("Create sphere")

    # Load the logo for the main window
    icon_path = os.path.join(ansys.aedt.core.workflows.__path__[0], "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 8))

    # Origin x entry
    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Origin X:")
    label.grid(row=0, column=0, padx=15, pady=10)
    origin_x = ttk.Entry(master)
    origin_x.grid(row=0, column=1, padx=15, pady=10)

    # Origin y entry
    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Origin Y:")
    label.grid(row=1, column=0, padx=15, pady=10)
    origin_x = ttk.Entry(master)
    origin_x.grid(row=1, column=1, padx=15, pady=10)

    # Origin z entry
    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Origin Z:")
    label.grid(row=2, column=0, padx=15, pady=10)
    origin_x = ttk.Entry(master)
    origin_x.grid(row=2, column=1, padx=15, pady=10)

    # Radius entry
    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Radius:")
    label.grid(row=3, column=0, padx=15, pady=10)
    origin_x = ttk.Entry(master)
    origin_x.grid(row=3, column=1, padx=15, pady=10)

    def callback():
        master.destroy()

    # Add "Create" button
    b = ttk.Button(master, text="Create", width=20, command=callback, style="PyAEDT.TButton")
    b.grid(row=4, column=1, pady=15)

    tkinter.mainloop()

    origin_x = getattr(master, "origin_x", extension_arguments["origin_x"])
    origin_y = getattr(master, "origin_y", extension_arguments["origin_y"])
    origin_z = getattr(master, "origin_z", extension_arguments["origin_z"])
    radius = getattr(master, "radius", extension_arguments["radius"])

    output_dict = {"origin_x": origin_x, "origin_y": origin_y, "origin_z": origin_z, "radius": radius}

    return output_dict


def main(extension_args):
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
    if active_design.GetDesignType() == "HFSS 3D Layout Design":
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    origin_x = extension_args.get("origin_x", extension_arguments["origin_x"])
    origin_y = extension_args.get("origin_y", extension_arguments["origin_y"])
    origin_z = extension_args.get("origin_z", extension_arguments["origin_z"])
    radius = extension_args.get("radius", extension_arguments["radius"])

    # Your PyAEDT script
    aedtapp.modeler.create_sphere([origin_x, origin_y, origin_z], radius)

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":
    args = get_arguments(extension_arguments, extension_description)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value

    main(args)
