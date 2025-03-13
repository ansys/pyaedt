# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path

import ansys.aedt.core
import ansys.aedt.core.workflows.hfss3dlayout
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
from pyedb import Edb

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
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    master = tkinter.Tk()
    master.title(extension_description)

    # Detect if user closes the UI
    master.flag = False

    # Load the logo for the main window
    icon_path = Path(ansys.aedt.core.workflows.__path__[0]) / "images" / "large" / "logo.png"
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

    label = ttk.Label(master, text="Export IPC2581:", style="PyAEDT.TLabel")
    label.grid(row=0, column=0, pady=10, padx=10)

    ipc_check = tkinter.IntVar()
    check = ttk.Checkbutton(master, width=0, variable=ipc_check, style="PyAEDT.TCheckbutton")
    check.grid(row=0, column=1, pady=10, padx=5)
    ipc_check.set(1)

    label2 = ttk.Label(master, text="Export Configuration file:", style="PyAEDT.TLabel")
    label2.grid(row=1, column=0, pady=10, padx=10)

    configuration_check = tkinter.IntVar()
    check2 = ttk.Checkbutton(master, width=0, variable=configuration_check, style="PyAEDT.TCheckbutton")
    check2.grid(row=1, column=1, pady=10, padx=5)
    configuration_check.set(1)

    label3 = ttk.Label(master, text="Export BOM file:", style="PyAEDT.TLabel")
    label3.grid(row=2, column=0, pady=10, padx=10)

    bom_check = tkinter.IntVar()
    check3 = ttk.Checkbutton(master, width=0, variable=bom_check, style="PyAEDT.TCheckbutton")
    check3.grid(row=2, column=1, pady=10, padx=5)
    bom_check.set(1)

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
        change_theme_button.config(text="\u263D")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=3, column=1, pady=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263D", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        master.ipc_ui = True if ipc_check.get() == 1 else False
        master.confg_ui = True if configuration_check.get() == 1 else False
        master.bom_ui = True if bom_check.get() == 1 else False
        master.destroy()

    b = ttk.Button(master, text="Export", width=30, command=callback, style="PyAEDT.TButton")
    b.grid(row=3, column=0, pady=10, padx=10)

    tkinter.mainloop()

    ipc_ui = getattr(master, "ipc_ui", extension_arguments["export_ipc"])
    confg_ui = getattr(master, "confg_ui", extension_arguments["export_configuration"])
    bom_ui = getattr(master, "bom_ui", extension_arguments["export_bom"])
    output_dict = {}
    if master.flag:
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
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    aedb_path = Path(active_project.GetPath()) / f"{active_project.GetName()}.aedb"
    edb = Edb(str(aedb_path), active_design.GetName().split(";")[1], edbversion=version)
    if ipc:
        ipc_file = aedb_path.with_name(aedb_path.stem + "_ipc2581.xml")
        edb.export_to_ipc2581(ipc_file)
    if bom:
        bom_file = aedb_path.with_name(aedb_path.stem + "_bom.csv")
        edb.workflow.export_bill_of_materials(bom_file)
    if config:
        config_file = aedb_path.with_name(aedb_path.stem + "_config.json")
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
    else:
        main(args)
