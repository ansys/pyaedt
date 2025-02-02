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

# Extension template to help get started

from pathlib import Path

import ansys.aedt.core
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk
from ansys.aedt.core.workflows.misc import ExtensionTheme

# Extension batch arguments
extension_arguments = {"Selections": 0, "anti pad diameter": "1mm"}
extension_description = "Layout Design Toolkit"
VERSION = "0.1.0"

default_config = {
    "selections": [],
    "diameter": "1mm"
}


class frontend():

    @property
    def active_design(self):
        desktop = ansys.aedt.core.Desktop(
            new_desktop=False,
            specified_version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )
        project = desktop.active_project()
        design = project.GetActiveDesign()

        if design.GetDesignType() in ["HFSS 3D Layout Design"]:
            return desktop, design

    def __init__(self):
        # Load initial configuration
        self.config_dict = default_config.copy()

        # Create UI
        self.master = tk.Tk()
        master = self.master

        master.geometry()

        master.title(extension_description)

        # Detect if user close the UI
        master.flag = False

        # Load the logo for the main window
        icon_path = Path(ansys.aedt.core.workflows.__path__[0]) / "images" / "large" / "logo.png"
        im = PIL.Image.open(icon_path)
        photo = PIL.ImageTk.PhotoImage(im)

        # Set the icon for the main window
        master.iconphoto(True, photo)

        # Configure style for ttk buttons
        self.style = ttk.Style()
        self.theme = ExtensionTheme()

        self.theme.apply_light_theme(self.style)
        master.theme = "light"

        # Set background color of the window (optional)
        master.configure(bg=self.theme.light["widget_bg"])

        # Selection entry
        row = 0
        selections_label = ttk.Label(master, text="Vias", width=20, style="PyAEDT.TLabel")
        selections_label.grid(row=row, column=0, padx=15, pady=10)
        self.selections_entry = tk.Text(master, width=40, height=1)
        self.selections_entry.grid(row=row, column=1, pady=15, padx=10)
        self.selections_entry.configure(bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"],
                                   font=self.theme.default_font)
        selections_button = ttk.Button(master, text="Get Selections", command=self.get_selections, width=20,
                                       style="PyAEDT.TButton")
        selections_button.grid(row=row, column=2, pady=15, padx=10)

        # Diameter
        diameter_label = ttk.Label(master, text="Anti pad Diameter", width=20, style="PyAEDT.TLabel")
        diameter_label.grid(row=1, column=0, padx=15, pady=10)
        self.diameter_entry = tk.Text(master, width=40, height=1)
        self.diameter_entry.insert("1.0", default_config["diameter"])
        self.diameter_entry.grid(row=1, column=1, pady=15, padx=10)
        self.diameter_entry.configure(bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"],
                                 font=self.theme.default_font)

        # Create buttons to create sphere and change theme color
        create_button = ttk.Button(master, text="Create", command=self.callback, style="PyAEDT.TButton")
        self.change_theme_button = ttk.Button(master, text="\u263D", width=2, command=self.toggle_theme,
                                         style="PyAEDT.TButton")

        create_button.grid(row=6, column=0, padx=15, pady=10)
        self.change_theme_button.grid(row=6, column=2, pady=10)

        tk.mainloop()

    def get_selections(self):
        desktop, h3d = self.active_design
        selected = h3d.GetEditor("Layout").GetSelections()
        if len(selected) == 2:
            self.config_dict["selections"] = selected
            text = ", ".join(selected)
        else:
            self.config_dict["selections"] = []
            text = "Please select two vias"
        self.selections_entry.replace("1.0", tk.END, text)
        desktop.release_desktop(False, False)

    def toggle_theme(self):
        master = self.master
        if master.theme == "light":
            self.set_dark_theme()
            master.theme = "dark"
        else:
            self.set_light_theme()
            master.theme = "light"

    def set_light_theme(self):
        theme = self.theme
        master = self.master
        style = self.style

        master.configure(bg=theme.light["widget_bg"])
        self.selections_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        self.diameter_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        self.change_theme_button.config(text="\u263D")

    def set_dark_theme(self):
        theme = self.theme
        master = self.master
        style = self.style

        master.configure(bg=theme.dark["widget_bg"])
        self.selections_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        self.diameter_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        self.change_theme_button.config(text="\u2600")

    def callback(self):
        print(self.config_dict)
        pass


class AddAntipad():
    IS_OK = False

    def __init__(self, config):
        self.via_1_name, self.via_2_name = config["selections"]

    def create_differential_antipad(self, diameter, racetrack=True):
        via_p = self.instances_by_name[self.via_1_name]
        via_n = self.instances_by_name[self.via_2_name]
        path = [via_p.position, via_n.position]

        prims = {}
        for i in self._pedb.layout.primitives:
            if i.primitive_type in ["rectangle", "polygon"]:
                for pos in path:
                    if i.polygon_data.point_in_polygon(pos[0], pos[1]):
                        if i.layer_name not in prims:
                            prims[i.layer_name] = [i]
                        else:
                            prims[i.layer_name].append(i)
                        break

        if racetrack:
            for l in via_p.layer_range_names:
                for obj in prims.get(l, []):
                    prim = self._pedb.modeler.create_trace(path, layer_name=l, width=diameter, net_name=via_p.net_name)
                    obj.add_void(prim)


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
    file_path = extension_args.get("file_path", extension_arguments["file_path"])

    # Your script
    if file_path:
        aedtapp.load_project(file_path, set_active=True)
    else:
        aedtapp.modeler.create_sphere([origin_x, origin_y, origin_z], radius)

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":
    args = get_arguments(extension_arguments, extension_description)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        app = frontend()
