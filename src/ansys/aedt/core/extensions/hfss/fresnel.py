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

from collections import defaultdict
from dataclasses import dataclass
import tkinter
from tkinter import ttk

from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.numbers_utils import Quantity

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"choice": "", "velocity": 1.4, "acceleration": 0.0, "delay": 0.0}
EXTENSION_TITLE = "Fresnel Coefficients"


@dataclass
class MoveItExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    choice: str = EXTENSION_DEFAULT_ARGUMENTS["choice"]
    velocity: float = EXTENSION_DEFAULT_ARGUMENTS["velocity"]
    acceleration: float = EXTENSION_DEFAULT_ARGUMENTS["acceleration"]
    delay: float = EXTENSION_DEFAULT_ARGUMENTS["delay"]


# Default width and height for the extension window
WIDTH = 650
HEIGHT = 750

# Maximum dimensions for the extension window
MAX_WIDTH = 800
MAX_HEIGHT = 850

# Minimum dimensions for the extension window
MIN_WIDTH = 600
MIN_HEIGHT = 750


class FresnelExtension(ExtensionHFSSCommon):
    """Extension for move it in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=4,
            toggle_column=0,
        )

        # Attributes
        self.fresnel_type = tkinter.StringVar(value="isotropic")
        self.setups = self.aedt_application.design_setups
        if not self.setups:
            self.setups = {"No Setup": None}

        self.setup_names = list(self.setups.keys())

        self.active_setup = None
        self.sweep = None
        self.floquet_ports = None

        # Layout
        self.root.columnconfigure(0, weight=1)

        fresnel_frame = ttk.LabelFrame(self.root, text="Fresnel Coefficients Mode", style="PyAEDT.TLabelframe")
        fresnel_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Anisotropic and isotropic (legacy) workflows
        ttk.Radiobutton(
            fresnel_frame,
            text="Isotropic (legacy) - scan over elevation only",
            value="isotropic",
            style="PyAEDT.TRadiobutton",
            variable=self.fresnel_type,
            command=self.on_fresnel_type_changed,
        ).grid(row=0, column=0, sticky="w")

        ttk.Radiobutton(
            fresnel_frame,
            text="Anisotropic - scan over elevation and azimuth",
            value="anisotropic",
            style="PyAEDT.TRadiobutton",
            variable=self.fresnel_type,
            command=self.on_fresnel_type_changed,
        ).grid(row=1, column=0, sticky="w")

        # Advanced and automated workflows
        tabs = ttk.Notebook(self.root, style="PyAEDT.TNotebook")
        self._widgets["tabs"] = tabs

        self._widgets["tabs"].grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self._widgets["auto_tab"] = ttk.Frame(self._widgets["tabs"], style="PyAEDT.TFrame")
        self._widgets["advanced_tab"] = ttk.Frame(self._widgets["tabs"], style="PyAEDT.TFrame")

        self._widgets["tabs"].add(self._widgets["auto_tab"], text="Automated Workflow")
        self._widgets["tabs"].add(self._widgets["advanced_tab"], text="Advanced Workflow")

        # Angle resolution
        self._widgets["elevation_resolution"] = tkinter.DoubleVar(value=7.5)
        self._widgets["azimuth_resolution"] = tkinter.DoubleVar(value=10.0)
        self._widgets["elevation_max"] = tkinter.DoubleVar(value=15.0)

        self.elevation_resolution_slider_values = [10.0, 7.5, 5.0]
        self.azimuth_resolution_slider_values = [15.0, 10.0, 7.5]

        self.elevation_resolution_values = [
            22.5,
            18.0,
            15.0,
            11.25,
            10.0,
            9.0,
            7.5,
            6.0,
            5.0,
            3.75,
            2.5,
            2.0,
            1.5,
            1.25,
            1.0,
        ]
        self.azimuth_resolution_values = self.elevation_resolution_values

        # self.build_automated_tab(auto_tab)
        self.build_advanced_tab()

        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.maxsize(MAX_WIDTH, MAX_HEIGHT)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")

    def on_fresnel_type_changed(self):
        selected = self.fresnel_type.get()
        selected_tab = self._widgets["tabs"].index(self._widgets["tabs"].select())
        if selected == "isotropic" and selected_tab == 1:
            self._widgets["azimuth_slider"].grid_remove()
            self._widgets["azimuth_spin"].grid_remove()
            self._widgets["azimuth_label"].grid_remove()
        elif selected == "anisotropic" and selected_tab == 1:
            self._widgets["azimuth_slider"].grid()
            self._widgets["azimuth_spin"].grid()
            self._widgets["azimuth_label"].grid()

    def build_advanced_tab(self):
        # Setup
        label = ttk.Label(self._widgets["advanced_tab"], text="Simulation setup", style="PyAEDT.TLabel")
        label.grid(row=0, column=0, padx=15, pady=10)

        self._widgets["setup_combo"] = ttk.Combobox(
            self._widgets["advanced_tab"], width=30, style="PyAEDT.TCombobox", name="simulation_setup", state="readonly"
        )
        self._widgets["setup_combo"].grid(row=0, column=1, padx=15, pady=10)

        self._widgets["setup_combo"]["values"] = self.setup_names
        self._widgets["setup_combo"].current(0)
        self.active_setup = self.setups[self.setup_names[0]]

        # Sweep
        self._widgets["frequency_sweep_frame"] = ttk.LabelFrame(
            self._widgets["advanced_tab"], text="Frequency sweep", padding=10, style="PyAEDT.TLabelframe"
        )
        self._widgets["frequency_sweep_frame"].grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        ttk.Label(self._widgets["frequency_sweep_frame"], text="Start", style="PyAEDT.TLabel").grid(
            row=0, column=1, padx=10
        )
        ttk.Label(self._widgets["frequency_sweep_frame"], text="Stop", style="PyAEDT.TLabel").grid(
            row=0, column=2, padx=10
        )
        ttk.Label(self._widgets["frequency_sweep_frame"], text="Step", style="PyAEDT.TLabel").grid(
            row=0, column=3, padx=10
        )
        ttk.Label(self._widgets["frequency_sweep_frame"], text="Frequency Units", style="PyAEDT.TLabel").grid(
            row=0, column=4, padx=10
        )

        initial_freq = "1.0"
        if hasattr(self.active_setup, "properties") and "Solution Freq" in self.active_setup.properties:
            freq_mesh = Quantity(self.active_setup.properties["Solution Freq"])
            initial_freq = str(freq_mesh.value)

        self._widgets["start_frequency"] = tkinter.Text(self._widgets["frequency_sweep_frame"], width=10, height=1)
        self._widgets["start_frequency"].insert(tkinter.END, initial_freq)
        self._widgets["start_frequency"].grid(row=1, column=1, padx=10)
        self._widgets["start_frequency"].configure(
            background=self.theme.light["label_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        self._widgets["stop_frequency"] = tkinter.Text(self._widgets["frequency_sweep_frame"], width=10, height=1)
        self._widgets["stop_frequency"].insert(tkinter.END, initial_freq)
        self._widgets["stop_frequency"].grid(row=1, column=2, padx=10)
        self._widgets["stop_frequency"].configure(
            background=self.theme.light["label_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        self._widgets["step_frequency"] = tkinter.Text(self._widgets["frequency_sweep_frame"], width=10, height=1)
        self._widgets["step_frequency"].insert(tkinter.END, "0.1")
        self._widgets["step_frequency"].grid(row=1, column=3, padx=10)
        self._widgets["step_frequency"].configure(
            background=self.theme.light["label_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        self._widgets["frequency_units_combo"] = ttk.Combobox(
            self._widgets["frequency_sweep_frame"], width=15, style="PyAEDT.TCombobox", state="readonly"
        )
        self._widgets["frequency_units_combo"].grid(row=1, column=4, padx=10)
        self._widgets["frequency_units_combo"]["values"] = ["GHz", "MHz", "kHz", "Hz"]
        self._widgets["frequency_units_combo"].current(0)

        # Angular resolution
        self._widgets["angular_resolution_frame"] = ttk.LabelFrame(
            self._widgets["advanced_tab"], text="Angular resolution", padding=10, style="PyAEDT.TLabelframe"
        )
        self._widgets["angular_resolution_frame"].grid(row=2, column=0, padx=15, pady=10, columnspan=2)

        # Slider positions
        for i, val in enumerate(["Coarse", "Regular", "Fine"]):
            ttk.Label(self._widgets["angular_resolution_frame"], text=val, style="PyAEDT.TLabel").grid(
                row=0, column=1 + i, padx=15
            )

        # Elevation slider
        ttk.Label(self._widgets["angular_resolution_frame"], text="Theta:", style="PyAEDT.TLabel").grid(
            row=1, column=0, padx=15, pady=10
        )

        self._widgets["elevation_slider"] = ttk.Scale(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=2,
            orient="horizontal",
            command=self.elevation_slider_changed,
            length=200,
        )
        self._widgets["elevation_slider"].grid(row=1, column=1, columnspan=3)

        self._widgets["elevation_spin"] = ttk.Spinbox(
            self._widgets["angular_resolution_frame"],
            values=[str(v) for v in self.elevation_resolution_values],
            textvariable=self._widgets["elevation_resolution"],
            width=6,
            command=self.elevation_spin_changed,
            state="readonly",
            font=self.theme.default_font,
            style="PyAEDT.TSpinbox",
        )
        self._widgets["elevation_spin"].grid(row=1, column=4, padx=15)
        self._widgets["elevation_slider"].set(1)

        # Azimuth slider
        self._widgets["azimuth_label"] = ttk.Label(
            self._widgets["angular_resolution_frame"], text="Phi:", style="PyAEDT.TLabel"
        )
        self._widgets["azimuth_label"].grid(row=2, column=0, padx=15, pady=10)

        self._widgets["azimuth_slider"] = ttk.Scale(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=2,
            orient="horizontal",
            command=self.azimuth_slider_changed,
            length=200,
        )
        self._widgets["azimuth_slider"].grid(row=2, column=1, columnspan=3)

        self._widgets["azimuth_spin"] = ttk.Spinbox(
            self._widgets["angular_resolution_frame"],
            values=[str(v) for v in self.azimuth_resolution_values],
            textvariable=self._widgets["azimuth_resolution"],
            width=6,
            state="readonly",
            font=self.theme.default_font,
            style="PyAEDT.TSpinbox",
        )
        self._widgets["azimuth_spin"].grid(row=2, column=4, padx=15)
        self._widgets["azimuth_slider"].set(1)

        # Disabled by default in Isotropic mode
        self._widgets["azimuth_slider"].grid_remove()
        self._widgets["azimuth_spin"].grid_remove()
        self._widgets["azimuth_label"].grid_remove()

        # Separator
        separator = ttk.Separator(self._widgets["angular_resolution_frame"], orient="horizontal")
        separator.grid(row=3, column=0, columnspan=5, sticky="ew", padx=15, pady=10)

        # Elevation max
        ttk.Label(self._widgets["angular_resolution_frame"], text="Theta MAX:", style="PyAEDT.TLabel").grid(
            row=4, column=0, padx=15, pady=10
        )

        self._widgets["elevation_max_slider"] = ttk.Scale(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=90,
            orient="horizontal",
            variable=self._widgets["elevation_max"],
            command=self.snap_elevation_max_slider,
            length=200,
        )
        self._widgets["elevation_max_slider"].grid(row=4, column=1, columnspan=3)

        self._widgets["elevation_max_spin"] = ttk.Spinbox(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=90,
            increment=1,
            textvariable=self._widgets["elevation_max"],
            width=6,
            command=self.snap_elevation_max_spin,
            font=self.theme.default_font,
        )
        self._widgets["elevation_max_spin"].grid(row=4, column=4)

        self._widgets["apply_validate_button"] = ttk.Button(
            self._widgets["advanced_tab"],
            text="Apply and Validate",
            width=40,
            command=lambda: self.apply_validate(),
            style="PyAEDT.TButton",
        )
        self._widgets["apply_validate_button"].grid(row=4, column=0, padx=15, pady=10, columnspan=2)

        # Validation menu
        self._widgets["validation_frame"] = ttk.LabelFrame(
            self._widgets["advanced_tab"], text="Validation", padding=10, style="PyAEDT.TLabelframe"
        )
        self._widgets["validation_frame"].grid(row=5, column=0, padx=10, pady=10, columnspan=2)

        ttk.Label(self._widgets["validation_frame"], text="Floquet ports: ", style="PyAEDT.TLabel").grid(
            row=0, column=1, padx=10
        )
        self._widgets["floquet_ports_label"] = ttk.Label(self._widgets["validation_frame"], style="PyAEDT.TLabel")
        self._widgets["floquet_ports_label"].grid(row=0, column=2, padx=10)
        self._widgets["floquet_ports_label"]["text"] = "N/A"

        ttk.Label(self._widgets["validation_frame"], text="Frequency points: ", style="PyAEDT.TLabel").grid(
            row=1, column=1, padx=10
        )
        self._widgets["frequency_points_label"] = ttk.Label(self._widgets["validation_frame"], style="PyAEDT.TLabel")
        self._widgets["frequency_points_label"].grid(row=1, column=2, padx=10)
        self._widgets["frequency_points_label"]["text"] = "N/A"

        ttk.Label(self._widgets["validation_frame"], text="Spatial directions: ", style="PyAEDT.TLabel").grid(
            row=2, column=1, padx=10
        )
        self._widgets["spatial_points_label"] = ttk.Label(self._widgets["validation_frame"], style="PyAEDT.TLabel")
        self._widgets["spatial_points_label"].grid(row=2, column=2, padx=10)
        self._widgets["spatial_points_label"]["text"] = "N/A"

        ttk.Label(self._widgets["validation_frame"], text="Design validation: ", style="PyAEDT.TLabel").grid(
            row=3, column=1, padx=10
        )
        self._widgets["design_validation_label"] = ttk.Label(self._widgets["validation_frame"], style="PyAEDT.TLabel")
        self._widgets["design_validation_label"].grid(row=3, column=2, padx=10)
        self._widgets["design_validation_label"]["text"] = "N/A"

    def elevation_slider_changed(self, pos):
        index = int(float(pos))
        new_val = self.elevation_resolution_slider_values[index]
        self._widgets["elevation_resolution"].set(new_val)
        self._widgets["elevation_spin"].set(new_val)
        self.update_elevation_max_constraints()

    def elevation_spin_changed(self):
        self.update_elevation_max_constraints()

    def azimuth_slider_changed(self, pos):
        index = int(float(pos))
        new_val = self.azimuth_resolution_slider_values[index]
        self._widgets["azimuth_resolution"].set(new_val)
        self._widgets["azimuth_spin"].set(new_val)

    def update_elevation_max_constraints(self):
        theta_val = self._widgets["elevation_resolution"].get()
        if theta_val <= 0 or theta_val > 90:
            return

        max_step = int(90 / theta_val)
        last_value = round(max_step * theta_val, 2)

        if last_value > 90:
            last_value = 90 - theta_val
        elif last_value < 90 and abs(90 - last_value) < 1e-6:
            last_value = 90.0

        if "elevation_max_slider" in self._widgets:
            self._widgets["elevation_max_slider"].config(
                from_=theta_val,
                to=last_value,
            )
        if "elevation_max_spin" in self._widgets:
            self._widgets["elevation_max_spin"].config(from_=theta_val, to=last_value, increment=theta_val)

        current_val = self._widgets["elevation_max"].get()
        snapped = round(current_val / theta_val) * theta_val
        if snapped > last_value:
            snapped = last_value
        self._widgets["elevation_max"].set(round(snapped, 2))

    def snap_elevation_max_slider(self, val):
        theta_step = float(self._widgets["elevation_resolution"].get())
        val = float(val)
        snapped = round(val / theta_step) * theta_step
        if snapped > 90:
            snapped = 90 - theta_step
        # self._widgets["elevation_max_slider"].set(round(snapped, 2))
        self._widgets["elevation_max_spin"].set(round(snapped, 2))

    def snap_elevation_max_spin(self):
        self.snap_elevation_max_slider(self._widgets["elevation_max_slider"].get())

    def apply_validate(self):
        self._widgets["frequency_points_label"].config(text="N/A")
        self._widgets["floquet_ports_label"].config(text="N/A")

        simulation_setup = self._widgets["setup_combo"].get()

        if simulation_setup == "No Setup":
            self.aedt_application.logger.error("No setup selected.")
            return

        # Create sweep
        self.active_setup = self.aedt_application.design_setups[simulation_setup]

        start_frequency = float(self._widgets["start_frequency"].get("1.0", tkinter.END).strip())
        stop_frequency = float(self._widgets["stop_frequency"].get("1.0", tkinter.END).strip())
        step_frequency = float(self._widgets["step_frequency"].get("1.0", tkinter.END).strip())
        frequency_units = self._widgets["frequency_units_combo"].get()

        if start_frequency > stop_frequency:
            self.aedt_application.logger.error("Start frequency must be less than stop frequency.")
            self._widgets["frequency_points_label"].config(text="❌")
            return

        for sweep_name, available_sweep in self.active_setup.children.items():
            available_sweep.properties["Enabled"] = False

        self.sweep = self.active_setup.add_sweep(type="Discrete")

        self.sweep.props["Type"] = "Discrete"
        self.sweep.props["SaveFields"] = True

        if start_frequency == stop_frequency:
            self.sweep.props["RangeType"] = "SinglePoints"
        else:
            self.sweep.props["RangeType"] = "LinearStep"

        self.sweep.props["RangeStart"] = f"{start_frequency}{frequency_units}"
        self.sweep.props["RangeEnd"] = f"{stop_frequency}{frequency_units}"
        self.sweep.props["RangeStep"] = f"{step_frequency}{frequency_units}"
        self.sweep.update()

        # Check number of ports and each port should have 2 modes

        self._get_floquet_ports()
        if self.floquet_ports is None:
            self._widgets["floquet_ports_label"]["text"] = "❌"
            return
        self._widgets["floquet_ports_label"]["text"] = f"{len(self.floquet_ports)} Floquet port defined" + " ✅"

        # Show frequency points

        frequency_points = int((stop_frequency - start_frequency) / step_frequency) + 1
        self._widgets["frequency_points_label"]["text"] = str(frequency_points) + " ✅"

        # Show spatial directions

        theta_resolution = float(self._widgets["elevation_resolution"].get())
        phi_resolution = float(self._widgets["azimuth_resolution"].get())
        phi_max = 360.0
        if self.fresnel_type.get() == "isotropic":
            phi_resolution = 1.0
            phi_max = 1.0
        theta_max = float(self._widgets["elevation_max"].get())

        theta_steps = int(theta_max / theta_resolution)
        phi_steps = int(phi_max / phi_resolution)

        total_combinations = theta_steps * phi_steps
        self._widgets["spatial_points_label"]["text"] = str(total_combinations) + " ✅"

        # Check validations

        validation = self.aedt_application.validate_simple()
        if validation == 1:
            self._widgets["design_validation_label"]["text"] = "Passed ✅"
        else:
            self._widgets["design_validation_label"].config(text="Failed ❌")
            return

        # Check if lattice pair

        # Assign variable to lattice pair

        # Create optimetrics

        pass

    def _get_floquet_ports(self):
        self.floquet_ports = None
        port_mode_list = self.aedt_application.excitation_names

        ports = defaultdict(set)

        for item in port_mode_list:
            if ":" in item:
                port_name, mode = item.split(":")
                ports[port_name].add(int(mode))

        port_names = list(ports.keys())

        for port, modes in ports.items():
            if len(modes) < 2:
                self.aedt_application.logger.error(f"{port} has less than 2 modes.")
                return
            elif len(modes) > 2:
                self.aedt_application.logger.error(f"{port} has more than 2 modes.")
                return

        if len(ports) <= 2:
            self.floquet_ports = port_names
            return port_names
        self.aedt_application.logger.error("More than 2 Floquet ports defined.")
        return


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = FresnelExtension(withdraw=False)

        tkinter.mainloop()

        # if extension.data is not None:
        #     main(extension.data)

    else:
        data = MoveItExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        # main(data)
