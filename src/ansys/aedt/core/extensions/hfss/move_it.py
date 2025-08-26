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

from dataclasses import dataclass
import os
import tkinter
from tkinter import ttk

import numpy as np
from scipy.interpolate import CubicSpline

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"choice": "", "velocity": 1.4, "acceleration": 0.0, "delay": 0.0}
EXTENSION_TITLE = "Move It"


@dataclass
class MoveItExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    choice: str = EXTENSION_DEFAULT_ARGUMENTS["choice"]
    velocity: float = EXTENSION_DEFAULT_ARGUMENTS["velocity"]
    acceleration: float = EXTENSION_DEFAULT_ARGUMENTS["acceleration"]
    delay: float = EXTENSION_DEFAULT_ARGUMENTS["delay"]


class MoveItExtension(ExtensionHFSSCommon):
    """Extension for move it in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=4,
            toggle_column=1,
        )
        # Add private attributes and initialize them through __load_aedt_info
        self.__assignments = None
        self.__load_aedt_info()

        # Tkinter widgets
        self.combo_line = None
        self.delay_entry = None
        self.acceleration_entry = None
        self.velocity_entry = None

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

    def __load_aedt_info(self):
        """Load info."""
        aedt_lines = self.aedt_application.modeler.get_objects_in_group("Lines")
        if not aedt_lines:
            self.release_desktop()
            raise AEDTRuntimeError("No lines are defined in this design.")
        self.__assignments = aedt_lines

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        label = ttk.Label(self.root, text="Select line:", width=30, style="PyAEDT.TLabel")
        label.grid(row=0, column=0, padx=15, pady=10)

        # Dropdown menu for lines
        self.combo_line = ttk.Combobox(
            self.root, width=30, style="PyAEDT.TCombobox", name="combo_line", state="readonly"
        )
        self.combo_line["values"] = self.__assignments
        self.combo_line.current(0)
        self.combo_line.grid(row=0, column=1, padx=15, pady=10)
        self.combo_line.focus_set()

        # Velocity entry
        velocity_label = ttk.Label(self.root, text="Velocity along path (m / s):", width=30, style="PyAEDT.TLabel")
        velocity_label.grid(row=1, column=0, padx=15, pady=10)
        self.velocity_entry = tkinter.Text(self.root, width=30, height=1)
        self.velocity_entry.insert(tkinter.END, "1.4")
        self.velocity_entry.grid(row=1, column=1, pady=15, padx=10)

        # Acceleration entry
        acceleration_label = ttk.Label(
            self.root, text="Acceleration along path (m /s ^ 2):", width=30, style="PyAEDT.TLabel"
        )
        acceleration_label.grid(row=2, column=0, padx=15, pady=10)
        self.acceleration_entry = tkinter.Text(self.root, width=30, height=1)
        self.acceleration_entry.insert(tkinter.END, "0.0")
        self.acceleration_entry.grid(row=2, column=1, pady=15, padx=10)

        # Delay entry
        delay_label = ttk.Label(self.root, text="Time delay (s):", width=30, style="PyAEDT.TLabel")
        delay_label.grid(row=3, column=0, padx=15, pady=10)
        self.delay_entry = tkinter.Text(self.root, width=30, height=1)
        self.delay_entry.insert(tkinter.END, "0.0")
        self.delay_entry.grid(row=3, column=1, pady=15, padx=10)

        def callback(extension: MoveItExtension):
            choice = extension.combo_line.get()
            velocity_val = extension.velocity_entry.get("1.0", tkinter.END).strip()
            velocity_val = float(velocity_val)
            if velocity_val < 0:
                extension.release_desktop()
                raise AEDTRuntimeError("Velocity must be greater than zero.")

            acceleration_val = extension.acceleration_entry.get("1.0", tkinter.END).strip()
            acceleration_val = float(acceleration_val)
            if acceleration_val < 0:
                extension.release_desktop()
                raise AEDTRuntimeError("Acceleration must be greater than zero.")

            delay_val = extension.delay_entry.get("1.0", tkinter.END).strip()
            delay_val = float(delay_val)
            if delay_val < 0:
                extension.release_desktop()
                raise AEDTRuntimeError("Delay must be greater than zero.")

            move_it_data = MoveItExtensionData(
                choice=choice, velocity=velocity_val, acceleration=acceleration_val, delay=delay_val
            )
            extension.data = move_it_data
            self.root.destroy()

        ok_button = ttk.Button(
            self.root,
            text="Generate",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        ok_button.grid(row=4, column=0, padx=15, pady=10)


def main(data: MoveItExtensionData):
    """Main function to run the move it extension."""
    if not data.choice:
        raise AEDTRuntimeError("No assignment provided to the extension.")

    if data.velocity < 0:
        raise AEDTRuntimeError("Velocity must be greater than zero.")

    if data.acceleration < 0:
        raise AEDTRuntimeError("Acceleration must be greater than zero.")

    if data.delay < 0:
        raise AEDTRuntimeError("Delay must be greater than zero.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    hfss = get_pyaedt_app(project_name, design_name)

    if hfss.design_type != "HFSS":
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        raise AEDTRuntimeError("Active design is not HFSS.")

    assignment = data.choice
    velocity = data.velocity
    acceleration = data.acceleration
    delay = data.delay

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

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = MoveItExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = MoveItExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
