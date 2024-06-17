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

import os

import pyaedt
import pyaedt.workflows.hfss3dlayout
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
extension_arguments = {"choice": "Export to HFSS"}
extension_description = "Export layout to 3D Modeler"

suffixes = {"Export to HFSS": "HFSS", "Export to Q3D": "Q3D", "Export to Maxwell 3D": "M3D", "Export to Icepak": "IPK"}


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("400x150")

    master.title("Export to 3D")

    # Load the logo for the main window
    icon_path = os.path.join(os.path.dirname(pyaedt.workflows.__file__), "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var, relief=tkinter.RAISED)
    var.set("Choose an option:")
    label.pack(pady=10)
    combo = ttk.Combobox(master, width=40)  # Set the width of the combobox
    combo["values"] = ("Export to HFSS", "Export to Q3D", "Export to Maxwell 3D", "Export to Icepak")
    combo.current(0)
    combo.pack(pady=10)

    combo.focus_set()

    def callback():
        master.choice_ui = combo.get()
        master.destroy()

    b = tkinter.Button(master, text="Export", width=40, command=callback)
    b.pack(pady=10)

    tkinter.mainloop()

    choice_ui = getattr(master, "choice_ui", extension_arguments["choice"])

    output_dict = {
        "choice": choice_ui,
    }
    return output_dict


def main(extension_args):
    choice = extension_args["choice"]

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

    if active_design.GetDesignType() in ["HFSS 3D Layout Design"]:
        design_name = active_design.GetName().split(";")[1]
    else:  # pragma: no cover
        app.logger.debug("Hfss 3D Layout project is needed.")
        app.release_desktop(False, False)
        raise Exception("Hfss 3D Layout project is needed.")

    h3d = pyaedt.Hfss3dLayout(project=project_name, design=design_name)
    setup = h3d.create_setup()
    suffix = suffixes[choice]

    if choice == "Export to Q3D":
        setup.export_to_q3d(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
    else:
        setup.export_to_hfss(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)

    h3d.delete_setup(setup.name)

    h3d.save_project()

    if choice == "Export to Q3D":
        _ = pyaedt.Q3d(project=h3d.project_file[:-5] + f"_{suffix}.aedt")
    else:
        aedtapp = pyaedt.Hfss(project=h3d.project_file[:-5] + f"_{suffix}.aedt")
        aedtapp2 = None
        if choice == "Export to Maxwell 3D":
            aedtapp2 = pyaedt.Maxwell3d(project=aedtapp.project_name)
        elif choice == "Export to Icepak":
            aedtapp2 = pyaedt.Icepak(project=aedtapp.project_name)
        if aedtapp2:
            aedtapp2.copy_solid_bodies_from(aedtapp, no_vacuum=False, no_pec=False, include_sheets=True)
            aedtapp2.delete_design(aedtapp.design_name)
            aedtapp2.save_project()

    if not extension_args["is_test"]:  # pragma: no cover
        app.logger.info("Project generated correctly.")
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
