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
from tkinter import messagebox

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.visualization.plot.pyvista import ModelPlotter
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
import pyvista as pv

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"choice": "", "points": 1000}
extension_description = "Point cloud generator"


def frontend():  # pragma: no cover
    import tkinter
    import tkinter.ttk as ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()

    if not active_project:  # pragma: no cover
        app.logger.error("No active project.")

    active_design = app.active_design()

    if not active_design:  # pragma: no cover
        app.logger.error("No active design.")

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    hfss = get_pyaedt_app(project_name, design_name)

    if hfss.design_type != "HFSS":  # pragma: no cover
        app.logger.error("Active design is not HFSS.")
        hfss.release_desktop(False, False)
        output_dict = {"choice": "", "file_path": ""}
        return output_dict

    # Create UI
    master = tkinter.Tk()

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

    hfss.modeler.model_units = "mm"
    hfss.modeler.set_working_coordinate_system(name="Global")

    aedt_solids = hfss.modeler.get_objects_in_group("Solids")
    aedt_sheets = hfss.modeler.get_objects_in_group("Sheets")

    if not aedt_solids and aedt_sheets:
        msg = "No solids or sheets are defined in this design."
        messagebox.showerror("Error", msg)
        app.logger.error(msg)
        hfss.release_desktop(False, False)
        output_dict = {}
        return output_dict

    # Dropdown label
    label = ttk.Label(master, text="Select Object or Surface:", width=20, style="PyAEDT.TLabel")
    label.grid(row=0, column=0, pady=10)

    # Dropdown menu for objects and surfaces
    combo = ttk.Combobox(master, width=30, style="PyAEDT.TCombobox", state="readonly")

    values = ["--- Objects ---"]
    if aedt_solids:
        values.extend(aedt_solids)

    values.append("--- Surfaces ---")
    if aedt_sheets:
        values.extend(aedt_sheets)
    combo["values"] = values

    combo.current(1)
    combo.grid(row=0, column=1, pady=10, padx=5)
    combo.focus_set()

    # Points entry
    points_label = ttk.Label(master, text="Number of Points:", width=20, style="PyAEDT.TLabel")
    points_label.grid(row=1, column=0, padx=15, pady=10)
    points_entry = tkinter.Text(master, width=40, height=1)
    points_entry.insert(tkinter.END, "1000")
    points_entry.grid(row=1, column=1, pady=15, padx=10)
    points_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        points_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        points_entry.configure(background=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=3, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263D", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        selected_item = combo.get()
        if selected_item in ["--- Objects ---", "--- Surfaces ---", ""]:
            messagebox.showerror("Error", "Please select a valid object or surface.")
            master.flag = False

        points = points_entry.get("1.0", tkinter.END).strip()
        num_points = int(points)
        if num_points <= 0:
            master.flag = False
            messagebox.showerror("Error", "Number of points must be greater than zero.")

        master.assignment = selected_item
        master.points = points

        master.destroy()

    def preview():
        try:
            selected_item = combo.get()
            if selected_item in ["--- Objects ---", "--- Surfaces ---", ""]:
                messagebox.showerror("Error", "Please select a valid object or surface.")
                return None
            points = points_entry.get("1.0", tkinter.END).strip()
            num_points = int(points)
            if num_points <= 0:
                messagebox.showerror("Error", "Number of points must be greater than zero.")
                return None

            # Export the mesh and generate point cloud
            output_file = hfss.post.export_model_obj(assignment=selected_item)

            if not output_file or not Path(output_file[0][0]).is_file():
                messagebox.showerror("Error", "Object could not be exported.")
                hfss.release_desktop(False, False)
                output_dict = {"choice": "", "file_path": ""}
                return output_dict

            goemetry_file = output_file[0][0]

            # Generate and visualize the point cloud
            model_plotter = ModelPlotter()
            model_plotter.add_object(goemetry_file)
            point_cloud = model_plotter.point_cloud(points=num_points)

            plotter = pv.Plotter()
            for _, actor in point_cloud.values():
                plotter.add_mesh(actor, color="white", point_size=5, render_points_as_spheres=True)
            plotter.show()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            hfss.release_desktop(False, False)
            output_dict = {}
            return output_dict

    b2 = ttk.Button(master, text="Preview", width=40, command=preview, style="PyAEDT.TButton")
    b2.grid(row=3, column=0, pady=10, padx=10)

    b3 = ttk.Button(master, text="Generate", width=40, command=callback, style="PyAEDT.TButton")
    b3.grid(row=3, column=1, pady=10, padx=10)

    tkinter.mainloop()

    assignment = getattr(master, "assignment", extension_arguments["choice"])
    points = getattr(master, "points", extension_arguments["points"])

    hfss.release_desktop(False, False)
    output_dict = {}
    if master.flag:
        output_dict = {"choice": assignment, "points": points}
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

    hfss = get_pyaedt_app(project_name, design_name)

    if hfss.design_type != "HFSS":  # pragma: no cover
        app.logger.error("Active design is not HFSS.")
        if not extension_args["is_test"]:
            app.release_desktop(False, False)
        return False

    assignment = extension_args.get("choice", extension_arguments["choice"])
    points = extension_args.get("points", extension_arguments["points"])

    # Export the mesh and generate point cloud
    output_file = hfss.post.export_model_obj(assignment=assignment)

    goemetry_file = output_file[0][0]

    # Generate and visualize the point cloud
    model_plotter = ModelPlotter()
    model_plotter.add_object(goemetry_file)
    point_values = model_plotter.point_cloud(points=int(points))

    for input_file, _ in point_values.values():
        _ = hfss.insert_near_field_points(input_file=input_file)

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
