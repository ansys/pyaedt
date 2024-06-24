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

from pyedb import Edb

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
extension_arguments = {"export_ipc": True, "export_configuration": True, "export_bom": True}
extension_description = "Layout Exporter"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("700x450")

    master.title("Layout exporter")

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
    label = tkinter.Label(master, textvariable=var)
    var.set("Export IPC2581:")
    label.grid(row=0, column=0, pady=10)
    ipc_check = tkinter.IntVar()
    check = tkinter.Checkbutton(master, width=30, variable=ipc_check)
    check.grid(row=0, column=1, pady=10, padx=5)
    ipc_check.set(1)

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2)
    var2.set("Export Configuration file:")
    label2.grid(row=1, column=0, pady=10)
    configuration_check = tkinter.IntVar()
    check2 = tkinter.Checkbutton(master, width=30, variable=configuration_check)
    check2.grid(row=1, column=1, pady=10, padx=5)
    configuration_check.set(1)

    var3 = tkinter.StringVar()
    label3 = tkinter.Label(master, textvariable=var3)
    var3.set("Export BOM file:")
    label3.grid(row=2, column=0, pady=10)
    bom_check = tkinter.IntVar()
    check3 = tkinter.Checkbutton(master, width=30, variable=bom_check)
    check3.grid(row=2, column=1, pady=10, padx=5)
    bom_check.set(1)

    def callback():
        master.ipc_ui = True if ipc_check.get() == 1 else False
        master.confg_ui = True if configuration_check.get() == 1 else False
        master.bom_ui = True if bom_check.get() == 1 else False
        master.destroy()

    b = tkinter.Button(master, text="Export", width=40, command=callback)
    b.grid(row=3, column=1, pady=10)

    tkinter.mainloop()

    ipc_ui = getattr(master, "ipc_ui", extension_arguments["export_ipc"])
    confg_ui = getattr(master, "confg_ui", extension_arguments["export_configuration"])
    bom_ui = getattr(master, "bom_ui", extension_arguments["export_bom"])

    output_dict = {
        "export_ipc": ipc_ui,
        "export_configuration": confg_ui,
        "export_bom": bom_ui,
    }
    return output_dict


def main(extension_args):
    ipc = extension_args["export_ipc"]
    bom = extension_args["export_bom"]
    config = extension_args["export_configuration"]
    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    aedb_path = os.path.join(active_project.GetPath(), active_project.GetName() + ".aedb")
    edb = Edb(aedb_path, active_design.GetName().split(";")[1], edbversion=version)
    if ipc:
        ipc_file = aedb_path[:-5] + "_ipc2581.xml"
        edb.export_to_ipc2581(ipc_file)
    if bom:
        bom_file = aedb_path[:-5] + "_bom.csv"
        edb.components.export_bom(bom_file)
    if config:
        config_file = aedb_path[:-5] + "_config.json"
        edb.configuration.export(config_file)

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
