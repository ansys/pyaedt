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
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"origin_x": 0, "origin_y": 0, "origin_z": 0, "radius": 1, "file_path": ""}
extension_description = "Extension template"


def frontend():
    import tkinter as tk
    import tkinter.ttk as ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        specified_version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()

    if not active_project:
        active_project_name = "No active project"
    else:
        active_project_name = active_project.GetName()
        active_design_name = app.active_design(active_project_name)
        maxwell = ansys.aedt.core.Maxwell3D(active_project_name, active_design_name)

    # Create UI
    master = tk.Tk()

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
    style = ttk.Style()
    theme = ExtensionTheme()

    theme.apply_light_theme(style)
    master.theme = "light"

    # Set background color of the window (optional)
    master.configure(bg=theme.light["widget_bg"])

    # Project name info
    project_name_label = ttk.Label(master, text="Project Name:", width=20, style="PyAEDT.TLabel")
    project_name_label.grid(row=0, column=0, pady=10)
    project_name_entry = tk.Text(master, width=40, height=1)
    project_name_entry.insert(tk.INSERT, active_project_name)
    project_name_entry.grid(row=0, column=1, pady=15, padx=10)
    project_name_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Design name info
    design_name_label = ttk.Label(master, text="Design Name:", width=20, style="PyAEDT.TLabel")
    design_name_label.grid(row=1, column=0, pady=10)
    design_name_entry = tk.Text(master, width=40, height=1)
    design_name_entry.insert(tk.INSERT, active_project_name)
    design_name_entry.grid(row=1, column=1, pady=15, padx=10)
    design_name_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Objects list
    objects_list = maxwell.modeler.objects
    objects_list_label = ttk.Label(master, text="Objects list:", width=20, style="PyAEDT.TLabel")
    objects_list_label.grid(row=2, column=0, pady=10)
    objects_list_lb = tk.Listbox(master, selectmode=tk.MULTIPLE, height=len(objects_list), width=50)
    for obj in objects_list:
        objects_list_lb.insert(tk.END, obj)
        objects_list_lb.pack()
    objects_list_lb.grid(row=2, column=1, pady=15, padx=10)

    # Formats list
    formats_list = [".tab", ".csv", ".mat"]
    formats_list_label = ttk.Label(master, text="Available output formats:", width=20, style="PyAEDT.TLabel")
    formats_list_label.grid(row=3, column=0, pady=10)
    formats_list_lb = tk.Listbox(master, selectmode=tk.MULTIPLE, height=len(formats_list), width=50)
    for format in formats_list:
        formats_list_lb.insert(tk.END, format)
        formats_list_lb.pack()
    formats_list_lb.grid(row=3, column=1, pady=15, padx=10)

    # Browse output file entry
    browse_file_label = ttk.Label(master, text="Output file location:", width=20, style="PyAEDT.TLabel")
    browse_file_label.grid(row=4, column=0, pady=10)
    browse_file_entry = tk.Text(master, width=40, height=1)
    browse_file_entry.grid(row=4, column=1, pady=15, padx=10)
    browse_file_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        # origin_x_entry.configure(
        #     background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        # )
        # origin_y_entry.configure(
        #     background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        # )
        # origin_z_entry.configure(
        #     background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        # )
        # radius_entry.configure(
        #     background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        # )
        # browse_file_entry.configure(
        #     background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        # )
        project_name_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        # change_theme_button.config(text="\u263D")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        # origin_x_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        # origin_y_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        # origin_z_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        # radius_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        # browse_file_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        project_name_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        # change_theme_button.config(text="\u2600")
