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

# from ansys.aedt.core.generic.design_types import get_pyaedt_app
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
extension_arguments = {"origin_x": 0, "origin_y": 0, "origin_z": 0, "radius": 1, "file_path": ""}
extension_description = "Extension template"


def frontend():
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.ttk as ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    # app = ansys.aedt.core.Desktop(
    #     new_desktop=False,
    #     specified_version=version,
    #     port=port,
    #     aedt_process_id=aedt_process_id,
    #     student_version=is_student,
    # )
    #
    # active_project = app.active_project()
    #
    # if not active_project:
    #     active_project_name = "No active project"
    # else:
    #     active_project_name = active_project.GetName()
    #     active_design_name = app.active_design().GetName()
    #     maxwell = ansys.aedt.core.Maxwell3d(active_project_name, active_design_name)
    # Create UI
    master = tk.Tk()

    # Configure the grid to expand with the window
    master.grid_rowconfigure(0, weight=1)
    master.grid_columnconfigure(0, weight=1)

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
    project_name_entry.insert(tk.INSERT, "active_project_name")
    project_name_entry.grid(row=0, column=1, pady=15, padx=10)
    project_name_entry.configure(
        bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font, state=tk.DISABLED
    )

    # Design name info
    design_name_label = ttk.Label(master, text="Design Name:", width=20, style="PyAEDT.TLabel")
    design_name_label.grid(row=1, column=0, pady=10)
    design_name_entry = tk.Text(master, width=40, height=1)
    design_name_entry.insert(tk.INSERT, "active_design_name")
    design_name_entry.grid(row=1, column=1, pady=15, padx=10)
    design_name_entry.configure(
        bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font, state=tk.DISABLED
    )

    # Export options
    frame = tk.Frame(master)
    frame.grid(row=2, column=0, pady=10, padx=10)
    export_options_list = ["Ohmic loss", "Force"]
    export_options_label = ttk.Label(
        frame, text="Export options:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor=tk.CENTER
    )
    export_options_label.pack(side=tk.TOP, fill=tk.BOTH)
    export_options_lb = tk.Listbox(frame, selectmode=tk.SINGLE, height=2, width=15, justify=tk.CENTER)
    export_options_lb.pack(expand=True, fill=tk.BOTH)
    for opt in export_options_list:
        export_options_lb.insert(tk.END, opt)

    # Objects list
    frame = tk.Frame(master)
    frame.grid(row=2, column=1, pady=10, padx=10)
    objects_list = ["Object1", "Object2", "Object3", "Object1", "Object2", "Object3", "Object1", "Object2", "Object3"]
    objects_list_label = ttk.Label(
        frame, text="Objects list:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor=tk.CENTER
    )
    objects_list_label.pack(side=tk.TOP, fill=tk.BOTH)
    scroll_bar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    objects_list_lb = tk.Listbox(frame, selectmode=tk.MULTIPLE, yscrollcommand=scroll_bar.set, justify=tk.CENTER)
    objects_list_lb.pack(expand=True, fill=tk.BOTH)
    for obj in objects_list:
        objects_list_lb.insert(tk.END, obj)
    objects_list_lb.config(height=6, width=30)
    scroll_bar.config(command=objects_list_lb.yview)

    # Sample points file
    sample_points_label = ttk.Label(master, text="Sample points file:", width=20, style="PyAEDT.TLabel")
    sample_points_label.grid(row=3, column=0, pady=10)
    sample_points_entry = tk.Text(master, width=40, height=1)
    sample_points_entry.grid(row=3, column=1, pady=15, padx=10)
    sample_points_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Export file
    export_file_label = ttk.Label(master, text="Output file location:", width=20, style="PyAEDT.TLabel")
    export_file_label.grid(row=4, column=0, pady=10)
    export_file_entry = tk.Text(master, width=40, height=1)
    export_file_entry.grid(row=4, column=1, pady=15, padx=10)
    export_file_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        project_name_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        design_name_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        export_options_lb.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        objects_list_lb.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        scroll_bar.configure(background=theme.light["pane_bg"])
        export_file_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        # change_theme_button.config(text="\u263D")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        project_name_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        design_name_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        export_options_lb.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        objects_list_lb.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        scroll_bar.configure(bg=theme.dark["pane_bg"])
        export_file_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        project_name_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        # change_theme_button.config(text="\u2600")

    def callback():
        # master.origin_x = origin_x_entry.get("1.0", tk.END).strip()
        # master.origin_y = origin_y_entry.get("1.0", tk.END).strip()
        # master.origin_z = origin_z_entry.get("1.0", tk.END).strip()
        # master.radius = radius_entry.get("1.0", tk.END).strip()
        master.destroy()

    def browse_files():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Electronics File",
            filetypes=(("Points file", ".pst"), ("all files", "*.*")),
        )
        sample_points_entry.insert(tk.END, filename)
        master.file_path = sample_points_entry.get("1.0", tk.END).strip()
        master.destroy()

    # Export points file button
    export_points_button = ttk.Button(master, text="...", command=browse_files, width=10, style="PyAEDT.TButton")
    export_points_button.grid(row=3, column=2, pady=10, padx=15)

    def save_as_files():
        filename = filedialog.asksaveasfilename(
            initialdir="/",
            defaultextension=".tab",
            filetypes=[
                ("tab data file", ".tab"),
                ("csv data file", ".csv"),
                # ("MATLAB", ".mat"),
                ("Numpy array", ".npy"),
            ],
        )
        export_file_entry.insert(tk.END, filename)
        master.file_path = export_file_entry.get("1.0", tk.END).strip()
        # master.destroy()

    # Create button to select output file location
    save_as_button = ttk.Button(master, text="Save as...", command=save_as_files, width=10, style="PyAEDT.TButton")
    save_as_button.grid(row=4, column=2, pady=10, padx=15)

    # Create button to export fields data
    # In command put the workflow to export the data
    export_button = ttk.Button(master, text="Export", width=10, style="PyAEDT.TButton")
    export_button.grid(row=5, column=1, pady=10, padx=15)

    # Configure logging
    text_area = tk.Text(master, wrap=tk.WORD, width=40, height=2)
    text_area.grid(row=6, column=1, pady=10, sticky="nsew")
    text_area.config(state=tk.DISABLED)
    if sample_points_entry.get("1.0", tk.END).strip() == "":
        text_area.insert(
            tk.INSERT, "If a points file is not selected the export fields will be performed on mesh nodes."
        )
    text_area.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Create buttons to create sphere and change theme color
    change_theme_button = ttk.Button(master, text="\u263D", width=2, command=toggle_theme, style="PyAEDT.TButton")
    change_theme_button.grid(row=7, column=2, pady=10)

    # Get objects list selection
    # selected_objects = variable.get()

    tk.mainloop()

    # app.release_desktop(False, False)

    return {}


def main(extension_args):
    # app = ansys.aedt.core.Desktop(
    #     new_desktop=False,
    #     version=version,
    #     port=port,
    #     aedt_process_id=aedt_process_id,
    #     student_version=is_student,
    # )
    #
    # active_project = app.active_project()
    # active_design = app.active_design()
    #
    # project_name = active_project.GetName()
    # if active_design.GetDesignType() == "HFSS 3D Layout Design":
    #     design_name = active_design.GetDesignName()
    # else:
    #     design_name = active_design.GetName()
    #
    # aedtapp = get_pyaedt_app(project_name, design_name)

    # origin_x = extension_args.get("origin_x", extension_arguments["origin_x"])
    # origin_y = extension_args.get("origin_y", extension_arguments["origin_y"])
    # origin_z = extension_args.get("origin_z", extension_arguments["origin_z"])
    # radius = extension_args.get("radius", extension_arguments["radius"])
    # file_path = extension_args.get("file_path", extension_arguments["file_path"])

    # Your script
    # if file_path:
    #     #     aedtapp.load_project(file_path, set_active=True)
    #     # else:
    #     #     aedtapp.modeler.create_sphere([origin_x, origin_y, origin_z], radius)

    if not extension_args["is_test"]:  # pragma: no cover
        # app.release_desktop(False, False)
        pass
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
