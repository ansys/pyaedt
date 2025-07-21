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
WIDTH = 800
HEIGHT = 450

# Maximum dimensions for the extension window
MAX_WIDTH = 800
MAX_HEIGHT = 550

# Minimum dimensions for the extension window
MIN_WIDTH = 600
MIN_HEIGHT = 400


class FresnelExtension(ExtensionHFSSCommon):
    """Extension for move it in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=2,
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

        fresnel_frame = ttk.LabelFrame(self.root, text="Fresnel Coefficients type", style="PyAEDT.TLabelframe")
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

        # self.build_automated_tab(auto_tab)
        self.build_advanced_tab()

        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.maxsize(MAX_WIDTH, MAX_HEIGHT)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")

    def build_advanced_tab(self):
        label = ttk.Label(self._widgets["advanced_tab"], text="Simulation setup", width=30, style="PyAEDT.TLabel")
        label.grid(row=0, column=0, padx=15, pady=10)

        self._widgets["setup_combo"] = ttk.Combobox(
            self._widgets["advanced_tab"], width=30, style="PyAEDT.TCombobox", name="simulation_setup", state="readonly"
        )
        self._widgets["setup_combo"].grid(row=0, column=1, padx=15, pady=10)

        self._widgets["setup_combo"]["values"] = self.setup_names
        self._widgets["setup_combo"].current(0)
        self.active_setup = self.setups[self.setup_names[0]]

        if not self.active_setup["Sweeps"]:
            self.active_sweep = "LastAdaptive"
            sweeps = ["LastAdaptive"]
        else:
            sweeps = self.active_setup["Sweeps"]

        self._widgets["setup_combo"].bind("<<ComboboxSelected>>", self.on_setup_changed)

        label = ttk.Label(self._widgets["advanced_tab"], text="Frequency Sweep", width=30, style="PyAEDT.TLabel")
        label.grid(row=1, column=0, padx=15, pady=10)

        self._widgets["sweep_combo"] = ttk.Combobox(
            self._widgets["advanced_tab"], width=30, style="PyAEDT.TCombobox", name="simulation_sweep", state="readonly"
        )
        self._widgets["sweep_combo"].grid(row=1, column=1, padx=15, pady=10)
        self._widgets["sweep_combo"]["values"] = sweeps
        self._widgets["sweep_combo"].current(0)

    def on_setup_changed(self, event):
        selected_setup = self._widgets["setup_combo"].get()
        self.active_setup = self.setups[selected_setup]

        if not self.active_setup["Sweeps"]:
            sweeps = ["LastAdaptive"]
        else:
            sweeps = self.active_setup["Sweeps"]

        self._widgets["sweep_combo"]["values"] = sweeps
        self._widgets["sweep_combo"].current(0)


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
