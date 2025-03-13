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

    # Origin x entry
    origin_x_label = ttk.Label(master, text="Origin X:", width=20, style="PyAEDT.TLabel")
    origin_x_label.grid(row=0, column=0, padx=15, pady=10)
    origin_x_entry = tk.Text(master, width=40, height=1)
    origin_x_entry.grid(row=0, column=1, pady=15, padx=10)
    origin_x_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Origin y entry
    origin_y_label = ttk.Label(master, text="Origin Y:", width=20, style="PyAEDT.TLabel")
    origin_y_label.grid(row=1, column=0, padx=15, pady=10)
    origin_y_entry = tk.Text(master, width=40, height=1)
    origin_y_entry.grid(row=1, column=1, pady=15, padx=10)
    origin_y_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Origin z entry
    origin_z_label = ttk.Label(master, text="Origin Y:", width=20, style="PyAEDT.TLabel")
    origin_z_label.grid(row=2, column=0, padx=15, pady=10)
    origin_z_entry = tk.Text(master, width=40, height=1)
    origin_z_entry.grid(row=2, column=1, pady=15, padx=10)
    origin_z_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Radius entry
    radius_label = ttk.Label(master, text="Radius:", width=20, style="PyAEDT.TLabel")
    radius_label.grid(row=3, column=0, padx=15, pady=10)
    radius_entry = tk.Text(master, width=40, height=1)
    radius_entry.grid(row=3, column=1, pady=15, padx=10)
    radius_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Browse file entry
    browse_file_label = ttk.Label(master, text="Browse File:", width=20, style="PyAEDT.TLabel")
    browse_file_label.grid(row=4, column=0, pady=10)
    browse_file_entry = tk.Text(master, width=40, height=1)
    browse_file_entry.grid(row=4, column=1, pady=15, padx=10)
    browse_file_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Project name info
    project_name_label = ttk.Label(master, text="Project Name:", width=20, style="PyAEDT.TLabel")
    project_name_label.grid(row=5, column=0, pady=10)
    project_name_entry = tk.Text(master, width=40, height=1)
    project_name_entry.insert(tk.INSERT, active_project_name)
    project_name_entry.grid(row=5, column=1, pady=15, padx=10)
    project_name_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        origin_x_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        origin_y_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        origin_z_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        radius_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        browse_file_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        project_name_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        origin_x_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        origin_y_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        origin_z_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        radius_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        browse_file_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        project_name_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")

    def callback():
        master.origin_x = origin_x_entry.get("1.0", tk.END).strip()
        master.origin_y = origin_y_entry.get("1.0", tk.END).strip()
        master.origin_z = origin_z_entry.get("1.0", tk.END).strip()
        master.radius = radius_entry.get("1.0", tk.END).strip()
        master.destroy()

    def browse_files():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Electronics File",
            filetypes=(("AEDT", ".aedt"), ("all files", "*.*")),
        )
        browse_file_entry.insert(tk.END, filename)
        master.file_path = browse_file_entry.get("1.0", tk.END).strip()
        master.destroy()

    # Create button to browse an AEDT file
    browse_button = ttk.Button(master, text="...", command=browse_files, width=10, style="PyAEDT.TButton")
    browse_button.grid(row=4, column=2, pady=10, padx=15)

    # Create buttons to create sphere and change theme color
    create_button = ttk.Button(master, text="Create Sphere", command=callback, style="PyAEDT.TButton")
    change_theme_button = ttk.Button(master, text="\u263D", width=2, command=toggle_theme, style="PyAEDT.TButton")
    create_button.grid(row=6, column=0, padx=15, pady=10)
    change_theme_button.grid(row=6, column=2, pady=10)

    tk.mainloop()

    origin_x = getattr(master, "origin_x", extension_arguments["origin_x"])
    origin_y = getattr(master, "origin_y", extension_arguments["origin_y"])
    origin_z = getattr(master, "origin_z", extension_arguments["origin_z"])
    radius = getattr(master, "radius", extension_arguments["radius"])
    file_path = getattr(master, "file_path", extension_arguments["file_path"])

    output_dict = {
        "origin_x": origin_x,
        "origin_y": origin_y,
        "origin_z": origin_z,
        "radius": radius,
        "file_path": file_path,
    }

    app.release_desktop(False, False)

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
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value

    main(args)
