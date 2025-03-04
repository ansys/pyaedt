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
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
import numpy as np

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"points_file": "", "export_file": "", "export_option": "Ohmic loss", "objects_list": []}
extension_description = "Export of transformer loss distribution"


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
    active_design = app.active_design()
    active_project_name = active_project.GetName()
    active_design_name = active_design.GetName()
    design_type = active_design.GetDesignType()
    if design_type == "Maxwell 2D":
        maxwell = ansys.aedt.core.Maxwell2d(active_project_name, active_design_name)
    elif design_type == "Maxwell 3D":
        maxwell = ansys.aedt.core.Maxwell3d(active_project_name, active_design_name)

    # Create UI
    master = tk.Tk()

    # Configure the grid to expand with the window
    master.grid_rowconfigure(0, weight=1)
    master.grid_columnconfigure(0, weight=1)
    master.grid_columnconfigure(1, weight=1)
    master.grid_columnconfigure(2, weight=1)

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

    # Export options
    frame = tk.Frame(master, width=20)
    frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
    export_options_list = ["Ohmic loss", "AC Force Density"]
    export_options_label = ttk.Label(
        frame, text="Export options:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    export_options_label.pack(side=tk.TOP, fill=tk.BOTH)
    export_options_lb = tk.Listbox(
        frame, selectmode=tk.SINGLE, height=2, width=15, justify=tk.CENTER, exportselection=False
    )
    export_options_lb.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
    for opt in export_options_list:
        export_options_lb.insert(tk.END, opt)
    export_options_lb.config(selectmode=tk.SINGLE)

    # Objects list
    frame = tk.Frame(master, width=20)
    frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
    objects_list = maxwell.modeler.objects_by_name
    objects_list_label = ttk.Label(
        frame, text="Objects list:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    objects_list_label.pack(side=tk.TOP, fill=tk.BOTH)
    scroll_bar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    objects_list_lb = tk.Listbox(
        frame, selectmode=tk.MULTIPLE, yscrollcommand=scroll_bar.set, justify=tk.CENTER, exportselection=False
    )
    objects_list_lb.pack(expand=True, fill=tk.BOTH, side=tk.RIGHT)
    for obj in objects_list:
        objects_list_lb.insert(tk.END, obj)
    objects_list_lb.config(height=6)
    scroll_bar.config(command=objects_list_lb.yview)

    # Sample points file
    sample_points_frame = tk.Frame(master, width=20)
    sample_points_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
    sample_points_label = ttk.Label(
        sample_points_frame, text="Sample points file:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    sample_points_label.pack(side=tk.TOP, fill=tk.BOTH)
    sample_points_entry = tk.Text(sample_points_frame, height=1, width=40)
    sample_points_entry.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
    sample_points_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Export file
    export_file_frame = tk.Frame(master, width=20)
    export_file_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
    export_file_label = ttk.Label(
        export_file_frame, text="Output file location:", width=20, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    export_file_label.pack(side=tk.TOP, fill=tk.BOTH)
    export_file_entry = tk.Text(export_file_frame, width=40, height=1)
    export_file_entry.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
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
        sample_points_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        # change_theme_button.config(text="\u263D")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        export_options_lb.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        objects_list_lb.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        scroll_bar.configure(bg=theme.dark["pane_bg"])
        export_file_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        sample_points_entry.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        # change_theme_button.config(text="\u2600")

    def callback():
        master.points_file = sample_points_entry.get("1.0", tk.END).strip()
        master.export_file = export_file_entry.get("1.0", tk.END).strip()
        selected_export = export_options_lb.curselection()
        master.export_option = [export_options_lb.get(i) for i in selected_export]
        selected_objects = objects_list_lb.curselection()
        master.objects_list = [objects_list_lb.get(i) for i in selected_objects]
        master.destroy()

    def browse_files():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Electronics File",
            filetypes=(("Points file", ".pts"), ("all files", "*.*")),
        )
        sample_points_entry.insert(tk.END, filename)
        master.file_path = sample_points_entry.get("1.0", tk.END).strip()
        master.destroy()

    # Export points file button
    export_points_button = ttk.Button(
        sample_points_frame, text="...", command=browse_files, width=10, style="PyAEDT.TButton"
    )
    export_points_button.pack(side=tk.RIGHT, padx=10)

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
    save_as_button = ttk.Button(
        export_file_frame, text="Save as...", command=save_as_files, width=10, style="PyAEDT.TButton"
    )
    save_as_button.pack(side=tk.RIGHT, padx=10)

    # Create button to export fields data
    export_button = ttk.Button(master, text="Export", command=callback, width=10, style="PyAEDT.TButton")
    export_button.grid(row=6, column=0, pady=10, padx=15)

    # Create buttons to create sphere and change theme color
    change_theme_button = ttk.Button(master, text="\u263D", width=2, command=toggle_theme, style="PyAEDT.TButton")
    change_theme_button.grid(row=6, column=1, pady=10)

    # Get objects list selection
    tk.mainloop()

    points_file = getattr(master, "points_file", extension_arguments["points_file"])
    export_file = getattr(master, "export_file", extension_arguments["export_file"])
    export_option = getattr(master, "export_option", extension_arguments["export_option"])
    objects_list = getattr(master, "objects_list", extension_arguments["objects_list"])

    output_dict = {
        "points_file": points_file,
        "export_file": export_file,
        "export_option": export_option,
        "objects_list": objects_list,
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
    design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    points_file = extension_args.get("points_file", extension_arguments["points_file"])
    export_file = extension_args.get("export_file", extension_arguments["export_file"])
    export_option = extension_args.get("export_option", extension_arguments["export_option"])
    objects_list = extension_args.get("objects_list", extension_arguments["objects_list"])

    # Your workflow
    if not points_file:
        points_file = None
    elif not objects_list:
        assignment = "AllObjects"
    elif isinstance(objects_list, list) and len(objects_list) > 1:
        if len(aedtapp.modeler.user_lists) == 0:
            objects_list = aedtapp.modeler.create_object_list(objects_list, "ObjectList1")
        else:
            objects_list = aedtapp.modeler.create_object_list(
                objects_list, f"ObjectList{len(aedtapp.modeler.user_lists)+1}"
            )
        assignment = objects_list.name

    if export_option == "Ohmic loss":
        quantity = "Ohmic-Loss"
        file_header = "x,y,z,field"
    else:
        quantity = "SurfaceAcForceDensity"
        file_header = "r", "phi", "z", "fr_real", "fr_imag", "fphi_real", "fphi_imag", "fz_real", "fz_imag"

    aedtapp.post.export_field_file(
        quantity=quantity, output_file=export_file, sample_points_file=points_file, assignment=assignment
    )

    # Populate PyVista object
    plotter = ansys.aedt.core.visualization.plot.pyvista.ModelPlotter()
    plotter.add_field_from_file(export_file)
    plotter.populate_pyvista_object()

    file_name = Path(export_file).stem
    file_path = str(Path(export_file).parent)

    field_coordinates = np.column_stack((np.array(plotter.pv.mesh.points), np.array(plotter.pv.mesh.active_scalars)))

    if Path(export_file).suffix == ".npy":
        np.save(Path(file_path).joinpath(f"{file_name}.npy"), field_coordinates)
    elif Path(export_file).suffix == ".csv":
        np.savetxt(
            Path(file_path).joinpath(f"{file_name}.csv"),
            field_coordinates,
            delimiter=",",
            header=file_header,
            comments="",
        )
    elif Path(export_file).suffix == ".tab":
        np.savetxt(
            Path(file_path).joinpath(f"{file_name}.tab"),
            field_coordinates,
            delimiter=",",
            header=file_header,
            comments="",
        )

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
    else:
        main(args)
