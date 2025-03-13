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

import os
from pathlib import Path
import shutil
from tkinter import messagebox

import ansys.aedt.core
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import generate_unique_name
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
extension_arguments = {
    "aedb_path": "",
    "design_name": "",
    "new_aedb_path": "",
    "nets_filter": [],
    "start_layer": "",
    "stop_layer": "",
    "contour_list": [],
    "test_mode": False,
}
extension_description = "Via clustering utility"


def frontend():  # pragma: no cover
    frontend_dict = {}
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )
    active_project = app.active_project()
    active_project_path = active_project.GetPath()
    active_project_name = active_project.GetName()
    frontend_dict["design_name"] = active_project_name
    aedb_path = Path(active_project_path) / (active_project_name + ".aedb")
    frontend_dict["aedb_path"] = os.path.join(active_project_path, active_project_name + ".aedb")
    active_design_name = app.active_design().GetName().split(";")[1]
    app.release_desktop(False, False)
    edb = Edb(aedb_path, active_design_name, edbversion=version)
    layers = list(edb.stackup.signal_layers.keys())
    edb.close()

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

    def callback_start_layer(event):
        frontend_dict["start_layer"] = start_layer_var.get()

    def callback_stop_layer(event):
        frontend_dict["stop_layer"] = stop_layer_var.get()

    project_name = tkinter.Entry(master, width=40)
    project_name.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    project_name.insert(tkinter.END, generate_unique_name(active_project_name, n=2))
    project_name.grid(row=1, column=0, pady=10, padx=0)

    label_start_layer = ttk.Label(master, text="Start layer", style="PyAEDT.TLabel")
    label_start_layer.grid(row=0, column=2, pady=10)

    start_layer_var = tkinter.StringVar()
    start_layer_var.set(layers[0])
    frontend_dict["start_layer"] = layers[0]
    start_layer_cbox = ttk.Combobox(master, height=20, width=30, textvariable=start_layer_var)
    start_layer_cbox["values"] = layers
    start_layer_cbox.grid(row=1, column=2, pady=5)
    start_layer_cbox.bind("<<ComboboxSelected>>", callback_start_layer)

    label_stop_layer = ttk.Label(master, text="Stop layer", style="PyAEDT.TLabel")
    label_stop_layer.grid(row=0, column=3, pady=10)

    stop_layer_var = tkinter.StringVar()
    stop_layer_var.set(layers[-1])
    frontend_dict["stop_layer"] = layers[-1]
    stop_layer_cbox = ttk.Combobox(master, height=20, width=30, textvariable=stop_layer_var)
    stop_layer_cbox["values"] = layers
    stop_layer_cbox.grid(row=1, column=3, pady=5)
    stop_layer_cbox.bind("<<ComboboxSelected>>", callback_stop_layer)

    def add_drawing_layer():
        hfss = Hfss3dLayout(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )
        layer = hfss.modeler.stackup.add_layer("via_merging")
        layer.usp = True
        hfss.release_desktop(close_desktop=False, close_projects=False)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        project_name.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        project_name.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    def callback():
        """Method called when button for merging padstack instances is clicked."""
        master.flag = True
        hfss = Hfss3dLayout(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )
        hfss.save_project()
        primitives = hfss.modeler.objects_by_layer(layer="via_merging")
        if not primitives:
            messagebox.showwarning(message="No primitives found on layer defined for merging padstack instances.")
            hfss.release_desktop(close_desktop=False, close_projects=False)
        else:
            frontend_dict["contour_list"] = []
            for primitive in primitives:
                prim = hfss.modeler.geometries[primitive]
                if prim.prim_type == "poly" or prim.prim_type == "rect":
                    pts = [pt for pt in [_pt.position for _pt in prim.points]]
                    frontend_dict["contour_list"].append(pts)
                else:
                    hfss.logger.warning(
                        f"Unsupported primitive {prim.name}, only polygon and rectangles are supported."
                    )
        frontend_dict["new_aedb_path"] = os.path.join(active_project_path, project_name.get() + ".aedb")
        master.destroy()

    button_add_layer = ttk.Button(master, text="Add layer", width=40, command=add_drawing_layer, style="PyAEDT.TButton")
    button_add_layer.grid(row=3, column=0, pady=10, padx=10)

    button_merge_pdstacks = ttk.Button(
        master, text="Merge padstack instances", width=40, command=callback, style="PyAEDT.TButton"
    )
    button_merge_pdstacks.grid(row=4, column=0, pady=10, padx=10)

    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=5, column=3, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=10, text="\u263D", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    tkinter.mainloop()
    return frontend_dict


def main(extension_arguments):
    test_mode = extension_arguments.get("test_mode", False)
    start_layer = extension_arguments.get("start_layer", False)
    stop_layer = extension_arguments.get("stop_layer", False)
    design_name = extension_arguments.get("design_name", "")
    # nets_filter = extension_arguments.get("nets_filter", "")
    contour_list = extension_arguments.get("contour_list", [])
    aedb_path = extension_arguments.get("aedb_path", "")
    new_aedb_path = extension_arguments.get("new_aedb_path", "")
    shutil.copytree(aedb_path, new_aedb_path)
    edb = Edb(new_aedb_path, design_name, edbversion=version)
    edb.padstacks.merge_via(contour_boxes=contour_list, net_filter=None, start_layer=start_layer, stop_layer=stop_layer)
    for prim in edb.modeler.primitives_by_layer["via_merging"]:
        prim.delete()
    edb.save()
    edb.close_edb()
    h3d = Hfss3dLayout(new_aedb_path)
    h3d.logger.info("Project generated correctly.")
    if not test_mode:
        h3d.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)
    import pyedb

    if pyedb.__version__ < "0.35.0":
        raise Exception("PyEDB 0.35.0 or recent needs to run this extension.")
    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:  # pragma no cover
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value
            main(args)
    else:  # pragma no cover
        main(args)
