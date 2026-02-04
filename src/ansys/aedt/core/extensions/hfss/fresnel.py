# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import tkinter
from tkinter import ttk
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

import numpy as np

from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.numbers_utils import Quantity

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

EXTENSION_TITLE = "Fresnel Coefficients"

# Default width and height for the extension window
WIDTH = 650
HEIGHT = 850

# Maximum dimensions for the extension window
MAX_WIDTH = 800
MAX_HEIGHT = 950

# Minimum dimensions for the extension window
MIN_WIDTH = 600
MIN_HEIGHT = 750


class FresnelExtension(ExtensionHFSSCommon):
    """Extension to generate Fresnel coefficients in AEDT."""

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
        self.setup_sweep_names = []

        if not self.setups:
            self.setups = {"No Setup": None}
            self.setup_sweep_names = ["No Setup : No Sweep"]
            self.setup_names = ["No Setup"]
        else:
            self.setup_names = list(self.setups.keys())
            for setup_name, setup in self.setups.items():
                self.setup_sweep_names.append(f"{setup_name} : LastAdaptive")
                if setup.children:
                    sweeps = list(setup.children.keys())
                    for sweep in sweeps:
                        self.setup_sweep_names.append(f"{setup_name} : {sweep}")

        self.active_setup = None
        self.sweep = None
        self.active_setup_sweep = None
        self.floquet_ports = None
        self.active_parametric = None
        self.start_frequency = None
        self.stop_frequency = None
        self.step_frequency = None
        self.frequency_units = None

        # Layout
        self.root.columnconfigure(0, weight=1)

        fresnel_frame = ttk.LabelFrame(self.root, text="Fresnel Coefficients Mode", style="PyAEDT.TLabelframe")
        fresnel_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        state = "normal"
        if self.desktop.aedt_version_id < "2026.2":
            # Anisotropic not available before 2026R2
            state = "disabled"

        # Anisotropic and isotropic workflows
        isotropic_button = ttk.Radiobutton(
            fresnel_frame,
            text="Isotropic - scan over elevation only",
            value="isotropic",
            style="PyAEDT.TRadiobutton",
            variable=self.fresnel_type,
            command=self.on_fresnel_type_changed,
            state=state,
        )
        isotropic_button.grid(row=0, column=0, sticky="w")
        self._widgets["anisotropic_button"] = isotropic_button

        anisotropic_button = ttk.Radiobutton(
            fresnel_frame,
            text="Anisotropic - scan over elevation and azimuth (in progress)",
            value="anisotropic",
            style="PyAEDT.TRadiobutton",
            variable=self.fresnel_type,
            command=self.on_fresnel_type_changed,
            state=state,
        )
        anisotropic_button.grid(row=1, column=0, sticky="w")
        self._widgets["isotropic_button"] = anisotropic_button

        # Extraction, advanced and automated workflows
        tabs = ttk.Notebook(self.root, style="PyAEDT.TNotebook")
        self._widgets["tabs"] = tabs

        self._widgets["tabs"].grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self._widgets["extraction_tab"] = ttk.Frame(self._widgets["tabs"], style="PyAEDT.TFrame")
        # self._widgets["auto_tab"] = ttk.Frame(self._widgets["tabs"], style="PyAEDT.TFrame")
        self._widgets["advanced_tab"] = ttk.Frame(self._widgets["tabs"], style="PyAEDT.TFrame")
        self._widgets["settings_tab"] = ttk.Frame(self._widgets["tabs"], style="PyAEDT.TFrame")

        self._widgets["tabs"].add(self._widgets["extraction_tab"], text="Extraction")

        # self._widgets["tabs"].add(self._widgets["auto_tab"], text="Automated")
        # Disable Automated workflow until it is not implemented
        # self._widgets["tabs"].tab(self._widgets["auto_tab"], state="disabled")

        self._widgets["tabs"].add(self._widgets["advanced_tab"], text="Advanced")
        self._widgets["tabs"].add(self._widgets["settings_tab"], text="Simulation Settings")

        # Select the "Advanced Workflow" tab by default
        self._widgets["tabs"].select(self._widgets["extraction_tab"])

        # Angle resolution
        self._widgets["elevation_resolution"] = tkinter.DoubleVar(value=7.5)
        self._widgets["azimuth_resolution"] = tkinter.DoubleVar(value=10.0)
        self._widgets["theta_scan_max"] = tkinter.DoubleVar(value=15.0)

        self.elevation_resolution_slider_values = [10.0, 7.5, 5.0]
        self.azimuth_resolution_slider_values = [15.0, 10.0, 7.5]

        self.elevation_resolution_values = [
            1.0,
            1.25,
            1.5,
            2.0,
            2.5,
            3.75,
            5.0,
            6.0,
            7.5,
            9.0,
            10.0,
            11.25,
            15.0,
            18.0,
            22.5,
            30.0,
        ]
        self.azimuth_resolution_values = self.elevation_resolution_values

        # self.build_automated_tab(auto_tab)
        self.build_advanced_tab()
        self.build_extraction_tab()
        self.build_settings_tab()

        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.maxsize(MAX_WIDTH, MAX_HEIGHT)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")

    def on_fresnel_type_changed(self):
        selected = self.fresnel_type.get()
        # selected_tab = self._widgets["tabs"].index(self._widgets["tabs"].select())
        if selected == "isotropic":
            self._widgets["azimuth_slider"].grid_remove()
            self._widgets["azimuth_spin"].grid_remove()
            self._widgets["azimuth_label"].grid_remove()
        elif selected == "anisotropic":
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

        self._widgets["theta_scan_max_slider"] = ttk.Scale(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=90,
            orient="horizontal",
            variable=self._widgets["theta_scan_max"],
            command=self.snap_theta_scan_max_slider,
            length=200,
        )
        self._widgets["theta_scan_max_slider"].grid(row=4, column=1, columnspan=3)

        self._widgets["theta_scan_max_spin"] = ttk.Spinbox(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=90,
            increment=1,
            textvariable=self._widgets["theta_scan_max"],
            width=6,
            command=self.snap_theta_scan_max_spin,
            font=self.theme.default_font,
            style="PyAEDT.TSpinbox",
        )
        self._widgets["theta_scan_max_spin"].grid(row=4, column=4)

        # Apply and Validate button
        self._widgets["apply_validate_button"] = ttk.Button(
            self._widgets["advanced_tab"],
            text="Apply and Validate",
            width=40,
            command=lambda: self.apply_validate(),
            style="PyAEDT.TButton",
        )  # nosec
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

        # Start button
        self._widgets["start_button"] = ttk.Button(
            self._widgets["advanced_tab"],
            text="Start",
            width=40,
            command=lambda: self.start_extraction(),
            style="PyAEDT.TButton",
        )  # nosec
        self._widgets["start_button"].grid(row=6, column=0, padx=15, pady=10, columnspan=2)
        self._widgets["start_button"].grid_remove()

    def build_extraction_tab(self):
        # Setup
        label = ttk.Label(self._widgets["extraction_tab"], text="Simulation setup", style="PyAEDT.TLabel")
        label.grid(row=0, column=0, padx=15, pady=10)

        self._widgets["setup_sweep_combo"] = ttk.Combobox(
            self._widgets["extraction_tab"],
            width=30,
            style="PyAEDT.TCombobox",
            name="simulation_setup",
            state="readonly",
        )
        self._widgets["setup_sweep_combo"].grid(row=0, column=1, padx=15, pady=10)

        self._widgets["setup_sweep_combo"]["values"] = self.setup_sweep_names
        self._widgets["setup_sweep_combo"].current(0)

        self.active_setup = self.setups[self.setup_sweep_names[0].split(" : ")[0]]

        # Validate button
        self._widgets["validate_button"] = ttk.Button(
            self._widgets["extraction_tab"],
            text="Validate",
            width=40,
            command=lambda: self.validate(),
            style="PyAEDT.TButton",
        )  # nosec
        self._widgets["validate_button"].grid(row=1, column=0, padx=15, pady=10, columnspan=2)

        # Validation menu
        self._widgets["validation_frame_extraction"] = ttk.LabelFrame(
            self._widgets["extraction_tab"], text="Validation", padding=10, style="PyAEDT.TLabelframe"
        )
        self._widgets["validation_frame_extraction"].grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        ttk.Label(self._widgets["validation_frame_extraction"], text="Floquet ports: ", style="PyAEDT.TLabel").grid(
            row=0, column=1, padx=10
        )
        self._widgets["floquet_ports_label_extraction"] = ttk.Label(
            self._widgets["validation_frame_extraction"], style="PyAEDT.TLabel"
        )
        self._widgets["floquet_ports_label_extraction"].grid(row=0, column=2, padx=10)
        self._widgets["floquet_ports_label_extraction"]["text"] = "N/A"

        ttk.Label(
            self._widgets["validation_frame_extraction"], text="Spatial directions: ", style="PyAEDT.TLabel"
        ).grid(row=2, column=1, padx=10)
        self._widgets["spatial_points_label_extraction"] = ttk.Label(
            self._widgets["validation_frame_extraction"], style="PyAEDT.TLabel"
        )
        self._widgets["spatial_points_label_extraction"].grid(row=2, column=2, padx=10)
        self._widgets["spatial_points_label_extraction"]["text"] = "N/A"

        ttk.Label(self._widgets["validation_frame_extraction"], text="Design validation: ", style="PyAEDT.TLabel").grid(
            row=3, column=1, padx=10
        )
        self._widgets["design_validation_label_extraction"] = ttk.Label(
            self._widgets["validation_frame_extraction"], style="PyAEDT.TLabel"
        )
        self._widgets["design_validation_label_extraction"].grid(row=3, column=2, padx=10)
        self._widgets["design_validation_label_extraction"]["text"] = "N/A"

        # Start button
        self._widgets["start_button_extraction"] = ttk.Button(
            self._widgets["extraction_tab"],
            text="Start",
            width=40,
            command=lambda: self.get_coefficients(),
            style="PyAEDT.TButton",
        )  # nosec
        self._widgets["start_button_extraction"].grid(row=4, column=0, padx=15, pady=10, columnspan=2)
        self._widgets["start_button_extraction"].grid_remove()

    def build_settings_tab(self):
        # Simulation menu
        self._widgets["hpc_frame"] = ttk.LabelFrame(
            self._widgets["settings_tab"], text="HPC options", padding=10, style="PyAEDT.TLabelframe"
        )
        self._widgets["hpc_frame"].grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        ttk.Label(self._widgets["hpc_frame"], text="Cores: ", style="PyAEDT.TLabel").grid(row=0, column=1, padx=10)
        self._widgets["core_number"] = tkinter.Text(self._widgets["hpc_frame"], width=20, height=1)
        self._widgets["core_number"].insert(tkinter.END, "4")
        self._widgets["core_number"].grid(row=0, column=2, padx=10)
        self._widgets["core_number"].configure(
            background=self.theme.light["label_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        ttk.Label(self._widgets["hpc_frame"], text="Tasks: ", style="PyAEDT.TLabel").grid(row=1, column=1, padx=10)
        self._widgets["tasks_number"] = tkinter.Text(self._widgets["hpc_frame"], width=20, height=1)
        self._widgets["tasks_number"].insert(tkinter.END, "1")
        self._widgets["tasks_number"].grid(row=1, column=2, padx=10)
        self._widgets["tasks_number"].configure(
            background=self.theme.light["label_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Simulation menu
        self._widgets["optimetrics_frame"] = ttk.LabelFrame(
            self._widgets["settings_tab"], text="Optimetrics options", padding=10, style="PyAEDT.TLabelframe"
        )
        self._widgets["optimetrics_frame"].grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="ew")

        self._widgets["keep_mesh"] = tkinter.BooleanVar()
        self._widgets["keep_mesh_checkbox"] = ttk.Checkbutton(
            self._widgets["optimetrics_frame"],
            text="Same mesh for all variations",
            variable=self._widgets["keep_mesh"],
            style="PyAEDT.TCheckbutton",
        )
        self._widgets["keep_mesh_checkbox"].grid(row=0, column=1, columnspan=2, padx=10, sticky="w")
        self._widgets["keep_mesh"].set(True)

    def elevation_slider_changed(self, pos):
        index = int(float(pos))
        new_val = self.elevation_resolution_slider_values[index]
        self._widgets["elevation_resolution"].set(new_val)
        self._widgets["elevation_spin"].set(new_val)
        self.update_theta_scan_max_constraints()

    def elevation_spin_changed(self):
        self.update_theta_scan_max_constraints()

    def azimuth_slider_changed(self, pos):
        index = int(float(pos))
        new_val = self.azimuth_resolution_slider_values[index]
        self._widgets["azimuth_resolution"].set(new_val)
        self._widgets["azimuth_spin"].set(new_val)

    def update_theta_scan_max_constraints(self):
        theta_val = self._widgets["elevation_resolution"].get()
        if theta_val <= 0 or theta_val > 90:
            return

        max_step = int(90 / theta_val)
        last_value = round(max_step * theta_val, 2)

        if last_value > 90:  # pragma: no cover
            last_value = 90 - theta_val
        elif last_value < 90 and abs(90 - last_value) < 1e-6:
            last_value = 90.0

        if "theta_scan_max_slider" in self._widgets:
            self._widgets["theta_scan_max_slider"].config(
                from_=theta_val,
                to=last_value,
            )
        if "theta_scan_max_spin" in self._widgets:
            self._widgets["theta_scan_max_spin"].config(from_=theta_val, to=last_value, increment=theta_val)

        current_val = self._widgets["theta_scan_max"].get()
        snapped = round(current_val / theta_val) * theta_val
        if snapped > last_value:
            snapped = last_value
        self._widgets["theta_scan_max"].set(round(snapped, 2))

    def snap_theta_scan_max_slider(self, val):
        theta_step = float(self._widgets["elevation_resolution"].get())
        val = float(val)
        snapped = round(val / theta_step) * theta_step
        if snapped > 90:
            snapped = 90 - theta_step
        self._widgets["theta_scan_max_spin"].set(round(snapped, 2))

    def snap_theta_scan_max_spin(self):
        self.snap_theta_scan_max_slider(self._widgets["theta_scan_max_slider"].get())

    def apply_validate(self):
        # Init
        self._widgets["frequency_points_label"].config(text="N/A")
        self._widgets["floquet_ports_label"].config(text="N/A")
        self._widgets["design_validation_label"].config(text="N/A")
        self._widgets["spatial_points_label"].config(text="N/A")
        self._widgets["start_button"].grid_remove()

        simulation_setup = self._widgets["setup_combo"].get()

        if simulation_setup == "No Setup":
            self.aedt_application.logger.add_error_message("No setup selected.")
            return False

        # Create sweep
        self.active_setup = self.aedt_application.design_setups[simulation_setup]

        self.start_frequency = float(self._widgets["start_frequency"].get("1.0", tkinter.END).strip())
        self.stop_frequency = float(self._widgets["stop_frequency"].get("1.0", tkinter.END).strip())
        self.step_frequency = float(self._widgets["step_frequency"].get("1.0", tkinter.END).strip())
        self.frequency_units = self._widgets["frequency_units_combo"].get()

        if self.start_frequency > self.stop_frequency:
            self.aedt_application.logger.add_error_message("Start frequency must be less than stop frequency.")
            self._widgets["frequency_points_label"].config(text="❌")
            return False

        for _, available_sweep in self.active_setup.children.items():
            available_sweep.properties["Enabled"] = False

        self.sweep = self.active_setup.add_sweep(type="Interpolating")

        self.sweep.props["Type"] = "Interpolating"
        self.sweep.props["SaveFields"] = False

        if self.start_frequency == self.stop_frequency:
            self.sweep.props["Type"] = "Discrete"
            self.sweep.props["RangeType"] = "SinglePoints"
        else:
            self.sweep.props["RangeType"] = "LinearStep"

        self.sweep.props["RangeStart"] = f"{self.start_frequency}{self.frequency_units}"
        self.sweep.props["RangeEnd"] = f"{self.stop_frequency}{self.frequency_units}"
        self.sweep.props["RangeStep"] = f"{self.step_frequency}{self.frequency_units}"
        self.sweep.update()

        # Check number of ports and each port should have 2 modes
        self.floquet_ports = self.aedt_application.get_fresnel_floquet_ports()
        if self.floquet_ports is None:
            self._widgets["floquet_ports_label"]["text"] = "❌"
            return False
        self._widgets["floquet_ports_label"]["text"] = f"{len(self.floquet_ports)} Floquet port defined" + " ✅"

        # Show frequency points

        frequency_points = int((self.stop_frequency - self.start_frequency) / self.step_frequency) + 1
        self._widgets["frequency_points_label"]["text"] = str(frequency_points) + " ✅"

        # Show spatial directions

        theta_resolution = float(self._widgets["elevation_resolution"].get())
        phi_resolution = float(self._widgets["azimuth_resolution"].get())
        phi_max = 360.0 - phi_resolution
        is_isotropic = self.fresnel_type.get() == "isotropic"
        if is_isotropic:
            phi_resolution = 1.0
            phi_max = 0
        theta_max = float(self._widgets["theta_scan_max"].get())

        theta_steps = int(theta_max / theta_resolution) + 1
        phi_steps = int(phi_max / phi_resolution) + 1

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
        bounds = self.aedt_application.boundaries_by_type
        if "Lattice Pair" not in bounds:
            self.aedt_application.logger.add_error_message("No lattice pair found.")
            self._widgets["design_validation_label"].config(text="Failed ❌")
            return

        # Assign variable to lattice pair
        self.aedt_application["scan_P"] = "0deg"
        self.aedt_application["scan_T"] = "0deg"

        for lattice_pair in bounds["Lattice Pair"]:
            lattice_pair.properties["Theta"] = "scan_T"
            lattice_pair.properties["Phi"] = "scan_P"

        # Create optimetrics
        for available_sweep in self.aedt_application.parametrics.setups:
            available_sweep.props["IsEnabled"] = False
            available_sweep.update()

        self.active_parametric = self.aedt_application.parametrics.add(
            "scan_T", 0.0, theta_max, theta_resolution, variation_type="LinearStep", solution=self.active_setup.name
        )

        if not is_isotropic:
            self.active_parametric.add_variation("scan_P", 0.0, phi_max, phi_resolution, variation_type="LinearStep")

        # Save mesh and equivalent meshes
        self.active_parametric.props["ProdOptiSetupDataV2"]["CopyMesh"] = self._widgets["keep_mesh"].get()
        self.active_parametric.props["ProdOptiSetupDataV2"]["SaveFields"] = False

        # Create output variables
        self.active_setup_sweep = self.active_setup.name + " : " + self.sweep.name
        self.aedt_application.create_fresnel_variables(self.active_setup_sweep)

        self.aedt_application.save_project()

        self._widgets["start_button"].grid()

        return True

    def validate(self, active_setup=None):
        # Init
        self._widgets["floquet_ports_label_extraction"].config(text="N/A")
        self._widgets["spatial_points_label_extraction"].config(text="N/A")
        self._widgets["design_validation_label_extraction"].config(text="N/A")
        self._widgets["start_button_extraction"].grid_remove()

        if active_setup is None:
            simulation_setup = self._widgets["setup_sweep_combo"].get()
            if simulation_setup is None:
                simulation_setup = self.active_setup_sweep
        else:
            simulation_setup = active_setup

        setup_name = simulation_setup.split(" : ")[0]
        sweep_name = simulation_setup.split(" : ")[1]

        if setup_name.lower() == "no setup":
            self.aedt_application.logger.add_error_message("No setup selected.")
            self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
            return False

        self.active_setup = self.setups[setup_name]

        self.active_setup_sweep = simulation_setup

        active_sweep = None
        if sweep_name != "LastAdaptive":
            # Setup has only one frequency sweep
            sweeps = self.active_setup.sweeps
            for sweep in set(sweeps):
                if sweep.name == sweep_name:
                    active_sweep = sweep
                    break

            if active_sweep is None:
                self.aedt_application.logger.add_error_message(f"{sweep_name} not found.")
                self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
                return False

            # Frequency sweep has linearly frequency samples
            sweep_type = active_sweep.props.get("RangeType", None)

            if sweep_type not in ["LinearStep", "LinearCount", "SinglePoints"]:
                self.aedt_application.logger.add_error_message(
                    f"{active_sweep.name} does not have linearly frequency samples."
                )
                self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
                return False

        # We can not get the frequency points with the AEDT API

        # Floquet and modes

        # Check number of ports and each port should have 2 modes
        self.floquet_ports = self.aedt_application.get_fresnel_floquet_ports()
        if self.floquet_ports is None:
            self._widgets["floquet_ports_label_extraction"]["text"] = "❌"
            return False
        self._widgets["floquet_ports_label_extraction"]["text"] = (
            f"{len(self.floquet_ports)} Floquet port defined" + " ✅"
        )

        # Parametric setup is driven by the variables defining the scan direction

        bounds = self.aedt_application.boundaries_by_type
        if "Lattice Pair" not in bounds:
            self.aedt_application.logger.add_error_message("No lattice pair found.")
            self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
            return False

        lattice_pair = bounds["Lattice Pair"]

        theta_scan_variable = lattice_pair[0].properties["Theta"]
        phi_scan_variable = lattice_pair[0].properties["Phi"]
        is_isotropic = self.fresnel_type.get() == "isotropic"

        report_quantities = self.aedt_application.post.available_report_quantities()

        variations = self.aedt_application.available_variations.all
        variations["Freq"] = "All"

        data = self.aedt_application.post.get_solution_data_per_variation(
            "Modal Solution Data", self.active_setup_sweep, ["Domain:=", "Sweep"], variations, report_quantities[0]
        )

        parametric_data = self.extract_parametric_fresnel(
            data.variations, theta_key=theta_scan_variable, phi_key=phi_scan_variable
        )

        if is_isotropic:
            if parametric_data["has_phi"]:
                if parametric_data["phi"][0] != 0.0:
                    self.aedt_application.logger.add_error_message("Phi sweep must contain 0.0deg.")
                    self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
                    return False
                phi_0 = parametric_data["phi"][0]
                theta_resolution = parametric_data["theta_resolution_by_phi"][phi_0]
                phi_resolution = 1.0
                phi_max = 0
                theta_max = parametric_data["theta_by_phi"][phi_0][-1]
            else:
                theta_resolution = parametric_data["theta_resolution"]
                phi_resolution = 1.0
                phi_max = 0
                theta_max = parametric_data["theta"][-1]
        else:
            if not parametric_data["has_phi"]:
                self.aedt_application.logger.add_error_message("Scan phi is not defined.")
                self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
                return False
            phi_0 = parametric_data["phi"][0]
            theta_resolution = parametric_data["theta_resolution_by_phi"][phi_0]
            theta_max = parametric_data["theta_by_phi"][phi_0][-1]
            phi_resolution = parametric_data["phi"][1] - parametric_data["phi"][0]
            phi_max = 360.0 - phi_resolution

        # Show spatial directions

        theta_steps = int(theta_max / theta_resolution) + 1
        phi_steps = int(phi_max / phi_resolution) + 1

        total_combinations = theta_steps * phi_steps
        self._widgets["spatial_points_label_extraction"]["text"] = str(total_combinations) + " ✅"

        # Check validations

        validation = self.aedt_application.validate_simple()
        if validation == 1:
            self._widgets["design_validation_label_extraction"]["text"] = "Passed ✅"
        else:
            self._widgets["design_validation_label_extraction"].config(text="Failed ❌")
            return False

        self._widgets["start_button_extraction"].grid()

        return True

    def start_extraction(self):
        cores = int(self._widgets["core_number"].get("1.0", tkinter.END).strip())
        tasks = int(self._widgets["tasks_number"].get("1.0", tkinter.END).strip())
        active_parametric = self.active_parametric.name

        # Solve
        self.aedt_application.analyze_setup(cores=cores, num_variations_to_distribute=tasks, name=active_parametric)

        self.aedt_application.save_project()

        is_valid = self.validate(self.active_setup_sweep)

        if is_valid:
            self.get_coefficients()

    def get_coefficients(self):
        _ = self.aedt_application.get_fresnel_coefficients(
            setup_sweep=self.active_setup_sweep,
            theta_name="scan_T",
            phi_name="scan_P",
        )
        self.release_desktop()

        self.root.destroy()

    @staticmethod
    def validate_even_and_divides_90(
        values: Sequence[float],
        float_precision: float = 1e-5,
        min_step_possible: float = 0.01,
    ) -> Tuple[bool, Optional[float], List[float]]:
        """
        Validate and extract an evenly-spaced theta sequence in [0, 90] that divides 90.

        It sorts and filters values to [0, 90]. Requires that 0.0 is present. It searches for a step size `step` such
        that a sequence starting at 0deg is (approximately) on a uniform grid, and that 90° is a multiple of `step`.
        Returns validity, the detected `step` (if valid), and the filtered list
        of input values that fall on the detected grid (up to 90°).

        Parameters
        ----------
        values : Sequence[float]
            Input angles (degrees), possibly unsorted and with out-of-range values.
        float_precision : float, optional
            Tolerance used for “close to integer multiple” checks.
        min_step_possible : float, optional
            Minimum step allowed during the step search.

        Returns
        -------
        is_valid : bool
            True if an evenly-spaced sequence is detected and 90° is divisible by the step.
        step : float or None
            Detected step (degrees) if valid, otherwise None.
        filtered_list : list of float
            Values from the input that lie in [0, 90] and align with the detected grid.
            If not valid, returns just the input values filtered to [0, 90] (sorted).
        """
        # Sort & filter to [0, 90]
        th_input = np.sort(np.asarray(values, dtype=float))
        th_090 = th_input[(th_input >= 0.0) & (th_input <= 90.0)]

        # Must start at exactly 0.0 (as in your final code)
        if th_090.size == 0 or th_090[0] != 0.0:
            return False, None, th_090.tolist()

        # Need at least two points to reason about spacing
        if th_090.size < 2:
            return False, None, th_090.tolist()

        # Step search setup
        # non-zero points relative to 0
        delta_0 = th_090[1:]
        # consecutive differences
        delta_opt = th_090[1:] - th_090[:-1]
        min_step_check = max(delta_opt.min(), min_step_possible)

        n_max = int(np.ceil(90.0 / min_step_check) + 1)
        step = 90.0 / n_max
        number_of_steps = n_max

        search_flag = True

        # Search loop (vectorized point selection per candidate step)
        while (n_max > 1) and search_flag:
            n_max -= 1
            step_check = 90.0 / n_max
            # Distances normalized by candidate step
            delta_rel = delta_0 / step_check

            # Points close to integer grid (within tolerance)
            k = np.rint(delta_rel)
            close_mask = np.abs(delta_rel - k) < float_precision
            k_sel = k[close_mask]

            if k_sel.size > 0:
                # Require first integer index < 2 and successive increments < 2
                # (equivalent to “exactly one step apart” with tolerance logic)
                diffs = np.diff(k_sel)
                if (k_sel[0] < 2) and np.all(diffs < 2):
                    step = step_check
                    number_of_steps = int(k_sel.size)
                    search_flag = False

        # If nothing worked, return not valid
        if search_flag:
            return False, None, th_090.tolist()

        # Build theoretical sequence and filter inputs that match it
        th_syn = np.arange(0, number_of_steps + 1, dtype=float) * step

        # Compute ratios for all values in [0,90], check closeness to nearest int
        in_range_mask = (th_input >= 0.0) & (th_input <= 90.0)
        cand = th_input[in_range_mask]
        ratios = np.divide(cand, step, out=np.zeros_like(cand), where=step != 0)
        nearest = np.rint(ratios)
        on_grid_mask = np.abs(ratios - nearest) < float_precision

        # Keep at most number_of_steps + 1 values, in order
        idx = np.flatnonzero(on_grid_mask)
        if idx.size > (number_of_steps + 1):
            idx = idx[: number_of_steps + 1]
        th_res = cand[idx].tolist()

        # Final validation
        divides_90 = abs((90.0 / step) - np.rint(90.0 / step)) < float_precision
        same_len = len(th_res) == th_syn.size
        close_seq = same_len and np.allclose(np.asarray(th_res, float), th_syn, atol=float_precision)

        is_valid = bool(divides_90 and close_seq)
        return is_valid, (float(step) if is_valid else None), th_res

    def extract_parametric_fresnel(self, rows, theta_key="scan_T", phi_key="scan_P"):
        if not rows:
            return {"has_phi": False, "theta": [], "phi": [], "theta_by_phi": {}}

        # Check if phi is defined
        has_phi = any(phi_key in r for r in rows)

        if not has_phi:
            # Only theta
            thetas = [r[theta_key] for r in rows if theta_key in r]
            thetas = sorted(set(thetas))
            valid, step, thetas = self.validate_even_and_divides_90(thetas)
            return {
                "has_phi": False,
                "theta": thetas,
                "theta_resolution": step,
                "theta_valid": valid,
                "phi": [],
                "theta_by_phi": {},
            }

        # phi groups
        theta_by_phi = {}
        for r in rows:
            if theta_key not in r or phi_key not in r:
                continue
            phi = r[phi_key]
            theta = r[theta_key]
            theta_by_phi.setdefault(phi, []).append(theta)

        # Order list
        for phi, lst in theta_by_phi.items():
            theta_by_phi[phi] = sorted(set(lst))

        # Sweep phi
        phi_values = sorted(theta_by_phi.keys())

        # Phi validations
        theta_resolution_by_phi = {}
        theta_valid_by_phi = {}
        for phi, lst in theta_by_phi.items():
            valid, step, _ = self.validate_even_and_divides_90(lst)
            theta_resolution_by_phi[phi] = step
            theta_valid_by_phi[phi] = valid

        return {
            "has_phi": True,
            "phi": phi_values,
            "theta_by_phi": theta_by_phi,
            "theta_resolution_by_phi": theta_resolution_by_phi,
            "theta_valid_by_phi": theta_valid_by_phi,
        }


if __name__ == "__main__":  # pragma: no cover
    # Open UI
    extension: ExtensionCommon = FresnelExtension(withdraw=False)

    tkinter.mainloop()
