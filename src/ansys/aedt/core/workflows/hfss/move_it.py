# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
import numpy as np
from scipy.interpolate import CubicSpline

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"choice": "", "velocity": 1.4, "acceleration": 0.0, "delay": 0.0}
extension_description = "Move It"


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

    hfss.modeler.model_units = "meter"
    hfss.modeler.set_working_coordinate_system(name="Global")

    aedt_lines = hfss.modeler.get_objects_in_group("Lines")

    if not aedt_lines:  # pragma: no cover
        msg = "No lines are defined in this design."
        messagebox.showerror("Error", msg)
        app.logger.error(msg)
        hfss.release_desktop(False, False)
        output_dict = {}
        return output_dict

    # Dropdown label
    label = ttk.Label(master, text="Select line:", width=20, style="PyAEDT.TLabel")
    label.grid(row=0, column=0, pady=10)

    # Dropdown menu for objects and surfaces
    combo = ttk.Combobox(master, width=40, style="PyAEDT.TCombobox", state="readonly")

    combo["values"] = aedt_lines

    combo.current(0)
    combo.grid(row=0, column=1, pady=10, padx=10)
    combo.focus_set()

    # Velocity entry
    velocity_label = ttk.Label(master, text="Velocity along path (m / s):", width=20, style="PyAEDT.TLabel")
    velocity_label.grid(row=1, column=0, padx=15, pady=10)
    velocity_entry = tkinter.Text(master, width=30, height=1)
    velocity_entry.insert(tkinter.END, "1.4")
    velocity_entry.grid(row=1, column=1, pady=15, padx=10)
    velocity_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Acceleration entry
    acceleration_label = ttk.Label(master, text="Acceleration along path (m /s ^ 2):", width=20, style="PyAEDT.TLabel")
    acceleration_label.grid(row=2, column=0, padx=15, pady=10)
    acceleration_entry = tkinter.Text(master, width=30, height=1)
    acceleration_entry.insert(tkinter.END, "0.0")
    acceleration_entry.grid(row=2, column=1, pady=15, padx=10)
    acceleration_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # Velocity entry
    delay_label = ttk.Label(master, text="Time delay (s):", width=20, style="PyAEDT.TLabel")
    delay_label.grid(row=3, column=0, padx=15, pady=10)
    delay_entry = tkinter.Text(master, width=30, height=1)
    delay_entry.insert(tkinter.END, "0.0")
    delay_entry.grid(row=3, column=1, pady=15, padx=10)
    delay_entry.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        velocity_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        acceleration_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        delay_entry.configure(
            background=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263d")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        velocity_entry.configure(
            background=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        acceleration_entry.configure(
            background=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        delay_entry.configure(background=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=4, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263d", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        selected_item = combo.get()

        velocity_val = velocity_entry.get("1.0", tkinter.END).strip()
        velocity_val = float(velocity_val)
        if velocity_val < 0:
            master.flag = False
            messagebox.showerror("Error", "Velocity must be greater than zero.")

        acceleration_val = acceleration_entry.get("1.0", tkinter.END).strip()
        acceleration_val = float(acceleration_val)
        if acceleration_val < 0:
            master.flag = False
            messagebox.showerror("Error", "Acceleration must be greater than zero.")

        delay_val = delay_entry.get("1.0", tkinter.END).strip()
        delay_val = float(delay_val)
        if delay_val < 0:
            master.flag = False
            messagebox.showerror("Error", "Delay must be greater than zero.")

        master.assignment = selected_item
        master.velocity = velocity_val
        master.delay = delay_val
        master.acceleration = acceleration_val

        master.destroy()

    b3 = ttk.Button(master, text="Generate", width=40, command=callback, style="PyAEDT.TButton")
    b3.grid(row=4, column=1, pady=10, padx=10)

    tkinter.mainloop()

    assignment = getattr(master, "assignment", extension_arguments["choice"])
    velocity = getattr(master, "velocity", extension_arguments["velocity"])
    acceleration = getattr(master, "acceleration", extension_arguments["acceleration"])
    delay = getattr(master, "delay", extension_arguments["delay"])

    hfss.release_desktop(False, False)
    output_dict = {}
    if master.flag:
        output_dict = {"choice": assignment, "velocity": velocity, "acceleration": acceleration, "delay": delay}
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

    hfss = get_pyaedt_app(project_name, design_name)

    if hfss.design_type != "HFSS":  # pragma: no cover
        app.logger.error("Active design is not HFSS.")
        if not extension_args["is_test"]:
            app.release_desktop(False, False)
        return False

    assignment = extension_args.get("choice", extension_arguments["choice"])
    velocity = extension_args.get("velocity", extension_arguments["velocity"])
    acceleration = extension_args.get("acceleration", extension_arguments["acceleration"])
    delay = extension_args.get("delay", extension_arguments["delay"])

    hfss.modeler.purge_history(assignment)
    hfss.modeler.generate_object_history(assignment)

    discrete_points = 101

    pts = hfss.modeler[assignment].points
    x_vals, y_vals, z_vals = np.array(pts).T

    num_input_pts = len(pts)
    n_input = np.linspace(1, num_input_pts, num_input_pts)
    n_output = np.linspace(1, num_input_pts, discrete_points)

    cs_x = CubicSpline(n_input, x_vals, bc_type="natural")
    cs_y = CubicSpline(n_input, y_vals, bc_type="natural")
    cs_z = CubicSpline(n_input, z_vals, bc_type="natural")

    x_out = cs_x(n_output)
    y_out = cs_y(n_output)
    z_out = cs_z(n_output)

    index_pos = range(1, len(n_output) + 1)

    # Crear nombres de datasets
    dataset_x_name = f"ds_{assignment}_xpos"
    dataset_y_name = f"ds_{assignment}_ypos"
    dataset_z_name = f"ds_{assignment}_zpos"

    if dataset_x_name in hfss.design_datasets:  # pragma: no cover
        hfss.design_datasets[dataset_x_name].x = index_pos
        hfss.design_datasets[dataset_x_name].y = x_out
        hfss.design_datasets[dataset_x_name].update()
    else:
        hfss.create_dataset1d_design(name=dataset_x_name, x=index_pos, y=x_out, x_unit="", y_unit="", sort=True)

    if dataset_y_name in hfss.design_datasets:  # pragma: no cover
        hfss.design_datasets[dataset_y_name].x = index_pos
        hfss.design_datasets[dataset_y_name].y = y_out
        hfss.design_datasets[dataset_y_name].update()
    else:
        hfss.create_dataset1d_design(name=dataset_y_name, x=index_pos, y=y_out, x_unit="", y_unit="", sort=True)

    if dataset_z_name in hfss.design_datasets:  # pragma: no cover
        hfss.design_datasets[dataset_z_name].x = index_pos
        hfss.design_datasets[dataset_z_name].y = z_out
        hfss.design_datasets[dataset_z_name].update()
    else:
        hfss.create_dataset1d_design(name=dataset_z_name, x=index_pos, y=z_out, x_unit="", y_unit="", sort=True)

    # Create index variable
    index_var_name = "index_pos_" + assignment

    hfss.variable_manager.set_variable(
        index_var_name, expression=1, description="variable used for position of CS", hidden=True
    )

    # Create coordinate system
    cs_name = assignment + "_CS"
    units = hfss.modeler.model_units

    origin_x = f"pwl({dataset_x_name}, {index_var_name})*1{units}"
    origin_y = f"pwl({dataset_y_name}, {index_var_name})*1{units}"
    origin_z = f"pwl({dataset_z_name}, {index_var_name})*1{units}"

    x_axis_vec = (
        f"pwl({dataset_x_name}, {index_var_name} + 1)*1{units} - pwl({dataset_x_name}, {index_var_name})*1{units}"
    )
    y_axis_vec = (
        f"pwl({dataset_y_name}, {index_var_name} + 1)*1{units} - pwl({dataset_y_name}, {index_var_name})*1{units}"
    )
    z_axis_vec = (
        f"pwl({dataset_z_name}, {index_var_name} + 1)*1{units} - pwl({dataset_z_name}, {index_var_name})*1{units}"
    )

    cs = [i for i in hfss.modeler.coordinate_systems if i.name == cs_name]

    if cs:  # pragma: no cover
        cs = cs[0]
        cs.props["OriginX"] = origin_x
        cs.props["OriginY"] = origin_y
        cs.props["OriginZ"] = origin_z
        cs.props["XAxisXvec"] = x_axis_vec
        cs.props["XAxisYvec"] = y_axis_vec
        cs.props["XAxisZvec"] = z_axis_vec
        cs.props["XAxisXvec"] = x_axis_vec
        cs.props["XAxisYvec"] = y_axis_vec
        cs.props["XAxisZvec"] = z_axis_vec
        cs.props["YAxisXvec"] = "0mm"
        cs.props["YAxisYvec"] = "0mm"
        cs.props["YAxisZvec"] = "1mm"
        res = cs.update()
        if not res:
            raise AEDTRuntimeError("Failed to update the coordinate system.")

    else:
        cs = hfss.modeler.create_coordinate_system(
            name=cs_name,
            origin=[origin_x, origin_y, origin_z],
            x_pointing=[x_axis_vec, y_axis_vec, z_axis_vec],
            y_pointing=["0mm", "0mm", "1mm"],
        )

    cs_name_rotated = cs.name + "_rotated"

    cs_rotated = [i for i in hfss.modeler.coordinate_systems if i.name == cs_name_rotated]

    if cs_rotated:  # pragma: no cover
        cs_rotated = cs_rotated[0]
        cs_rotated.props["YAxisXvec"] = "0"
        cs_rotated.props["YAxisYvec"] = "0"
        cs_rotated.props["YAxisZvec"] = "-1"
        cs_rotated.props["Reference CS"] = cs.name
        res = cs_rotated.update()
        if not res:
            raise AEDTRuntimeError("Failed to update the coordinate system.")
    else:
        _ = hfss.modeler.create_coordinate_system(name=cs_name_rotated, reference_cs=cs.name, y_pointing=[0, 0, -1])

    # Add total distance dataset
    total_distance_ds_name = "ds_" + assignment + "_total_dist"

    # Calculate the differences between consecutive points
    dx = np.diff(x_out)
    dy = np.diff(y_out)
    dz = np.diff(z_out)

    # Compute the Euclidean distances
    distances = np.sqrt(dx**2 + dy**2 + dz**2)

    # Compute the cumulative distance
    cumulative_dist = np.concatenate(([0], np.cumsum(distances)))

    if total_distance_ds_name in hfss.design_datasets:  # pragma: no cover
        hfss.design_datasets[dataset_z_name].x = cumulative_dist
        hfss.design_datasets[dataset_z_name].y = index_pos
        hfss.design_datasets[dataset_z_name].update()
    else:
        hfss.create_dataset1d_design(
            name=total_distance_ds_name, x=cumulative_dist, y=index_pos, x_unit="", y_unit="", sort=True
        )

    # Add variables
    time_var_name = "time_var"
    time_delay_name = "time_delay_" + assignment
    velocity_var_name = "velocity_" + assignment
    acceleration_var_name = "acceleration_" + assignment

    condition1 = "0"
    condition2 = (
        velocity_var_name
        + "*("
        + time_var_name
        + "-"
        + time_delay_name
        + ")+0.5*"
        + acceleration_var_name
        + "*("
        + time_var_name
        + "-"
        + time_delay_name
        + ")^2"
    )
    where_am_i = "if(" + time_var_name + "<" + time_delay_name + "," + condition1 + "," + condition2 + ")"
    index_at_time = "pwl(" + total_distance_ds_name + "," + where_am_i + ")"

    hfss.variable_manager.set_variable(time_var_name, expression="0s", description="system time", hidden=False)

    # Separator
    hfss.variable_manager.set_variable(assignment)

    hfss.variable_manager.set_variable(
        time_delay_name, expression=f"{delay}s", description="Delay before object starts moving", hidden=False
    )

    hfss.variable_manager.set_variable(
        velocity_var_name, expression=f"{velocity}m_per_sec", description="Variable used velocity", hidden=False
    )

    hfss.variable_manager.set_variable(
        acceleration_var_name,
        expression=f"{acceleration}",
        description="Variable used acceleration, units are m/s^2",
        hidden=False,
    )

    hfss[index_var_name] = index_at_time

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
