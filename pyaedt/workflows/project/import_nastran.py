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
from pyaedt import get_pyaedt_app
from pyaedt.modules.solutions import nastran_to_stl
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
extension_arguments = {"decimate": 0.0, "lightweight": False, "planar": True, "file_path": ""}
extension_description = "Import Nastran or STL file"


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("750x250")

    master.title("Import Nastran or STL file")

    # Load the logo for the main window
    icon_path = os.path.join(pyaedt.workflows.__path__[0], "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 8))

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2)
    var2.set("Browse file:")
    label2.grid(row=0, column=0, pady=10)
    text = tkinter.Text(master, width=40, height=1)
    text.grid(row=0, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Nastran or stl File",
            filetypes=(("Nastran", "*.nas"), ("STL", "*.stl"), ("all files", "*.*")),
        )
        text.insert(tkinter.END, filename)

    b1 = tkinter.Button(master, text="...", width=10, command=browseFiles)
    b1.grid(row=0, column=2, pady=10)

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Decimation factor (0-0.9). It may affect results:")
    label.grid(row=1, column=0, pady=10)
    check = tkinter.Text(master, width=20, height=1)
    check.insert(tkinter.END, "0.0")
    check.grid(row=1, column=1, pady=10, padx=5)

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Import as lightweight (only HFSS):")
    label.grid(row=2, column=0, pady=10)
    light = tkinter.IntVar()
    check2 = tkinter.Checkbutton(master, width=30, variable=light)
    check2.grid(row=2, column=1, pady=10, padx=5)

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Enable planar merge:")
    label.grid(row=3, column=0, pady=10)
    planar = tkinter.IntVar(value=1)
    check3 = tkinter.Checkbutton(master, width=30, variable=planar)
    check3.grid(row=3, column=1, pady=10, padx=5)

    def callback():
        master.decimate_ui = float(check.get("1.0", tkinter.END).strip())
        master.lightweight_ui = True if light.get() == 1 else False
        master.planar_ui = True if planar.get() == 1 else False
        master.file_path_ui = text.get("1.0", tkinter.END).strip()
        master.destroy()

    def preview():
        master.decimate_ui = float(check.get("1.0", tkinter.END).strip())
        master.lightweight_ui = True if light.get() == 1 else False
        master.planar_ui = True if planar.get() == 1 else False
        master.file_path_ui = text.get("1.0", tkinter.END).strip()

        if master.file_path_ui.endswith(".nas"):
            nastran_to_stl(input_file=master.file_path_ui, decimation=master.decimate_ui, preview=True)
        else:
            from pyaedt.modules.solutions import simplify_stl

            simplify_stl(master.file_path_ui, decimation=master.decimate_ui, preview=True)

    b2 = tkinter.Button(master, text="Preview", width=40, command=preview)
    b2.grid(row=5, column=0, pady=10, padx=10)

    b3 = tkinter.Button(master, text="Ok", width=40, command=callback)
    b3.grid(row=5, column=1, pady=10, padx=10)

    tkinter.mainloop()

    decimate_ui = getattr(master, "decimate_ui", extension_arguments["decimate"])
    lightweight_ui = getattr(master, "lightweight_ui", extension_arguments["lightweight"])
    planar_ui = getattr(master, "planar_ui", extension_arguments["planar"])
    file_path_ui = getattr(master, "file_path_ui", extension_arguments["file_path"])

    output_dict = {
        "decimate": decimate_ui,
        "lightweight": lightweight_ui,
        "planar": planar_ui,
        "file_path": file_path_ui,
    }
    return output_dict


def main(extension_args):
    file_path = extension_args["file_path"]
    lightweight = extension_args["lightweight"]
    decimate = extension_args["decimate"]
    planar = extension_args["planar"]

    if os.path.exists(file_path):
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

        aedtapp = get_pyaedt_app(project_name, design_name)

        if file_path.endswith(".nas"):
            aedtapp.modeler.import_nastran(
                file_path, import_as_light_weight=lightweight, decimation=decimate, enable_planar_merge=str(planar)
            )
        else:
            from pyaedt.modules.solutions import simplify_stl

            outfile = simplify_stl(file_path, decimation=decimate)
            aedtapp.modeler.import_3d_cad(
                outfile, healing=False, create_lightweigth_part=lightweight, merge_planar_faces=planar
            )
        app.logger.info("Geometry imported correctly.")
    else:
        app = pyaedt.Desktop(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )
        app.logger.debug("Wrong file selected. Select a .nas or .stl file")

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
