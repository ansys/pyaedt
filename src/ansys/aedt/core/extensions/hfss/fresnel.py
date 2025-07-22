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
HEIGHT = 550

# Maximum dimensions for the extension window
MAX_WIDTH = 800
MAX_HEIGHT = 750

# Minimum dimensions for the extension window
MIN_WIDTH = 600
MIN_HEIGHT = 550


class FresnelExtension(ExtensionHFSSCommon):
    """Extension for move it in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=3,
            toggle_column=0,
        )

        # Attributes
        self.fresnel_type = tkinter.StringVar(value="isotropic")
        self.setups = self.aedt_application.setup_sweeps_names
        if not self.setups:
            self.setups = {"No Setup": {"Sweeps": ["No Sweep"]}}

        self.setup_names = list(self.setups.keys())

        self.active_setup = None
        self.active_sweep = None

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
        ).grid(row=0, column=0, sticky="w")

        ttk.Radiobutton(
            fresnel_frame,
            text="Anisotropic - scan over elevation and azimuth",
            value="anisotropic",
            style="PyAEDT.TRadiobutton",
            variable=self.fresnel_type,
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
        self.azimuth_resolution_slider_values = [15, 10.0, 7.5]

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
        # Get sweeps in setup
        if not self.active_setup["Sweeps"]:
            self.active_sweep = "LastAdaptive"
            sweeps = ["LastAdaptive"]
        else:
            sweeps = self.active_setup["Sweeps"]

        self._widgets["setup_combo"].bind("<<ComboboxSelected>>", self.on_setup_changed)

        # Sweep
        label = ttk.Label(self._widgets["advanced_tab"], text="Frequency sweep", style="PyAEDT.TLabel")
        label.grid(row=1, column=0, padx=15, pady=10)

        self._widgets["sweep_combo"] = ttk.Combobox(
            self._widgets["advanced_tab"], width=30, style="PyAEDT.TCombobox", name="simulation_sweep", state="readonly"
        )
        self._widgets["sweep_combo"].grid(row=1, column=1, padx=15, pady=10)
        self._widgets["sweep_combo"]["values"] = sweeps
        self._widgets["sweep_combo"].current(0)

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
        ttk.Label(self._widgets["angular_resolution_frame"], text="Elevation:", style="PyAEDT.TLabel").grid(
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
        )
        self._widgets["elevation_spin"].grid(row=1, column=4, padx=15)
        self._widgets["elevation_slider"].set(1)

        # Azimuth slider
        ttk.Label(self._widgets["angular_resolution_frame"], text="Azimuth:", style="PyAEDT.TLabel").grid(
            row=2, column=0, padx=15, pady=10
        )

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
        )
        self._widgets["azimuth_spin"].grid(row=2, column=4, padx=15)
        self._widgets["azimuth_slider"].set(1)

        # Elevation max
        ttk.Label(self._widgets["angular_resolution_frame"], text="Elevation MAX:", style="PyAEDT.TLabel").grid(
            row=3, column=0, padx=15, pady=10
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
        self._widgets["elevation_max_slider"].grid(row=3, column=1, columnspan=3)

        self._widgets["elevation_max_spin"] = ttk.Spinbox(
            self._widgets["angular_resolution_frame"],
            from_=0,
            to=90,
            increment=1,
            textvariable=self._widgets["elevation_max"],
            width=6,
            command=self.snap_elevation_max_spin,
        )
        self._widgets["elevation_max_spin"].grid(row=3, column=4)

    def on_setup_changed(self, event):
        selected_setup = self._widgets["setup_combo"].get()
        self.active_setup = self.setups[selected_setup]

        if not self.active_setup["Sweeps"]:
            sweeps = ["LastAdaptive"]
        else:
            sweeps = self.active_setup["Sweeps"]

        self._widgets["sweep_combo"]["values"] = sweeps
        self._widgets["sweep_combo"].current(0)

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
