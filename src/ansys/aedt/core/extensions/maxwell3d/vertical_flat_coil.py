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

from dataclasses import asdict
from dataclasses import dataclass
import os
import tkinter as tk
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.coil import Coil

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_TITLE = "Create vertical or flat coil"
EXTENSION_DEFAULT_ARGUMENTS = {
    "is_vertical": False,
    "centre_x": "0mm",
    "centre_y": "0mm",
    "centre_z": "0mm",
    "turns": "4",
    "inner_width": "12mm",
    "inner_length": "6mm",
    "wire_radius": "1mm",
    "inner_distance": "2mm",
    "direction": "1",
    "pitch": "3mm",
    "arc_segmentation": "4",
    "section_segmentation": "8",
    "distance": "5mm",
    "looping_position": "0.5",
}

result = None


@dataclass
class CoilExtensionData(ExtensionCommonData):
    """Data class containing parameters to create vertical or flat coils."""

    is_vertical: bool = True
    centre_x: str = "0mm"
    centre_y: str = "0mm"
    centre_z: str = "0mm"
    turns: str = "5"
    inner_width: str = "12mm"
    inner_length: str = "6mm"
    wire_radius: str = "1mm"
    inner_distance: str = "2mm"
    direction: str = "1"
    pitch: str = "3mm"
    arc_segmentation: str = "1"
    section_segmentation: str = "1"
    distance: str = "5mm"
    looping_position: str = "0.5"


class CoilExtension(ExtensionCommon):
    """Extension to create vertical or flat coils in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=16,
            toggle_column=2,
        )
        # private attributes

        # add custom content
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        is_vertical_label = ttk.Label(self.root, text="Vertical Coil", style="PyAEDT.TLabel")
        is_vertical_label.grid(row=0, column=0, pady=10)
        is_vertical = tk.IntVar(self.root, name="is_vertical")
        check = ttk.Checkbutton(self.root, variable=is_vertical, style="PyAEDT.TCheckbutton", name="is_vertical")
        check.grid(row=0, column=1, pady=10, padx=5)
        is_vertical_description = tk.Text(self.root, width=40, height=2, name="is_vertical_description", wrap=tk.WORD)
        is_vertical_description.insert("1.0", "If checkbox is selected, the coil is vertical, otherwise flat.")
        is_vertical_description.grid(row=0, column=2, pady=10, padx=5)
        is_vertical_description.config(state=tk.DISABLED)

        centre_x = ttk.Label(self.root, text="x position:", style="PyAEDT.TLabel")
        centre_x.grid(row=1, column=0, pady=10)
        x_pos_text = tk.Text(self.root, width=40, height=1, name="centre_x")
        x_pos_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        x_pos_text.grid(row=1, column=1, pady=10, padx=5)
        x_pos_description = tk.Text(self.root, width=40, height=1, name="x_pos_description", wrap=tk.WORD)
        x_pos_description.insert("1.0", "x position of coil center point")
        x_pos_description.grid(row=1, column=2, pady=10, padx=5)
        x_pos_description.config(state=tk.DISABLED)

        centre_y = ttk.Label(self.root, text="y position:", style="PyAEDT.TLabel")
        centre_y.grid(row=2, column=0, pady=10)
        y_pos_text = tk.Text(self.root, width=40, height=1, name="centre_y")
        y_pos_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        y_pos_text.grid(row=2, column=1, pady=10, padx=5)
        y_pos_description = tk.Text(self.root, width=40, height=1, name="y_pos_description", wrap=tk.WORD)
        y_pos_description.insert("1.0", "y position of coil center point")
        y_pos_description.grid(row=2, column=2, pady=10, padx=5)
        y_pos_description.config(state=tk.DISABLED)

        centre_z = ttk.Label(self.root, text="z position:", style="PyAEDT.TLabel")
        centre_z.grid(row=3, column=0, pady=10)
        z_pos_text = tk.Text(self.root, width=40, height=1, name="centre_z")
        z_pos_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        z_pos_text.grid(row=3, column=1, pady=10, padx=5)
        z_pos_description = tk.Text(self.root, width=40, height=1, name="z_pos_description", wrap=tk.WORD)
        z_pos_description.insert("1.0", "z position of coil center point")
        z_pos_description.grid(row=3, column=2, pady=10, padx=5)
        z_pos_description.config(state=tk.DISABLED)

        turns = ttk.Label(self.root, text="Number of turns:", style="PyAEDT.TLabel")
        turns.grid(row=4, column=0, pady=10)
        turns_text = tk.Text(self.root, width=40, height=1, name="turns")
        turns_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        turns_text.grid(row=4, column=1, pady=10, padx=5)
        turns_description = tk.Text(self.root, width=40, height=1, name="turns_description", wrap=tk.WORD)
        turns_description.insert("1.0", "Number of turns")
        turns_description.grid(row=4, column=2, pady=10, padx=5)
        turns_description.config(state=tk.DISABLED)

        inner_width = ttk.Label(self.root, text="Inner width:", style="PyAEDT.TLabel")
        inner_width.grid(row=5, column=0, pady=10)
        inner_width_text = tk.Text(self.root, width=40, height=1, name="inner_width")
        inner_width_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        inner_width_text.grid(row=5, column=1, pady=10, padx=5)
        inner_width_description = tk.Text(self.root, width=40, height=2, name="inner_width_description", wrap=tk.WORD)
        inner_width_description.insert("1.0", "Inner width of the coil (length along X axis)")
        inner_width_description.grid(row=5, column=2, pady=10, padx=5)
        inner_width_description.config(state=tk.DISABLED)

        inner_length = ttk.Label(self.root, text="Inner length:", style="PyAEDT.TLabel")
        inner_length.grid(row=6, column=0, pady=10)
        inner_length_text = tk.Text(self.root, width=40, height=1, name="inner_length")
        inner_length_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        inner_length_text.grid(row=6, column=1, pady=10, padx=5)
        inner_length_description = tk.Text(self.root, width=40, height=2, name="inner_length_description", wrap=tk.WORD)
        inner_length_description.insert("1.0", "Inner length of the coil (length along Y axis)")
        inner_length_description.grid(row=6, column=2, pady=10, padx=5)
        inner_length_description.config(state=tk.DISABLED)

        wire_radius = ttk.Label(self.root, text="Wire radius:", style="PyAEDT.TLabel")
        wire_radius.grid(row=7, column=0, pady=10)
        wire_radius_text = tk.Text(self.root, width=40, height=1, name="wire_radius")
        wire_radius_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        wire_radius_text.grid(row=7, column=1, pady=10, padx=5)
        wire_radius_description = tk.Text(self.root, width=40, height=2, name="wire_radius_description", wrap=tk.WORD)
        wire_radius_description.insert("1.0", "Width of the wire (length along Y axis)")
        wire_radius_description.grid(row=7, column=2, pady=10, padx=5)
        wire_radius_description.config(state=tk.DISABLED)

        inner_distance = ttk.Label(self.root, text="Inner distance:", style="PyAEDT.TLabel")
        inner_distance.grid(row=8, column=0, pady=10)
        inner_distance_text = tk.Text(self.root, width=40, height=1, name="inner_distance")
        inner_distance_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        inner_distance_text.grid(row=8, column=1, pady=10, padx=5)
        inner_distance_description = tk.Text(
            self.root, width=40, height=2, name="inner_distance_description", wrap=tk.WORD
        )
        inner_distance_description.insert(
            "1.0", "Distance between the coil and the inner rectangle (length along X or Y axis)"
        )
        inner_distance_description.grid(row=8, column=2, pady=10, padx=5)
        inner_distance_description.config(state=tk.DISABLED)

        direction = ttk.Label(self.root, text="Direction:", style="PyAEDT.TLabel")
        direction.grid(row=9, column=0, pady=10)
        direction_text = tk.Text(self.root, width=40, height=1, name="direction")
        direction_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        direction_text.grid(row=9, column=1, pady=10, padx=5)
        direction_description = tk.Text(self.root, width=40, height=2, name="direction_description", wrap=tk.WORD)
        direction_description.insert("1.0", "Direction of the coil (left side 1 or right -1)")
        direction_description.grid(row=9, column=2, pady=10, padx=5)
        direction_description.config(state=tk.DISABLED)

        pitch = ttk.Label(self.root, text="Pitch:", style="PyAEDT.TLabel")
        pitch.grid(row=10, column=0, pady=10)
        pitch_text = tk.Text(self.root, width=40, height=1, name="pitch")
        pitch_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        pitch_text.grid(row=10, column=1, pady=10, padx=5)
        pitch_description = tk.Text(self.root, width=40, height=2, name="pitch_description", wrap=tk.WORD)
        pitch_description.insert("1.0", "Pitch of the coil (deviation along Z axis per turn)")
        pitch_description.grid(row=10, column=2, pady=10, padx=5)
        pitch_description.config(state=tk.DISABLED)

        arc_segmentation = ttk.Label(self.root, text="Arc segmentation:", style="PyAEDT.TLabel")
        arc_segmentation.grid(row=11, column=0, pady=10)
        arc_segmentation_text = tk.Text(self.root, width=40, height=1, name="arc_segmentation")
        arc_segmentation_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        arc_segmentation_text.grid(row=11, column=1, pady=10, padx=5)
        arc_segmentation_description = tk.Text(
            self.root, width=40, height=2, name="arc_segmentation_description", wrap=tk.WORD
        )
        arc_segmentation_description.insert("1.0", "number of segments into which to divide the coil corners")
        arc_segmentation_description.grid(row=11, column=2, pady=10, padx=5)
        arc_segmentation_description.config(state=tk.DISABLED)

        section_segmentation = ttk.Label(self.root, text="Section segmentation:", style="PyAEDT.TLabel")
        section_segmentation.grid(row=12, column=0, pady=10)
        section_segmentation_text = tk.Text(self.root, width=40, height=1, name="section_segmentation")
        section_segmentation_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        section_segmentation_text.grid(row=12, column=1, pady=10, padx=5)
        section_segmentation_description = tk.Text(
            self.root, width=40, height=2, name="section_segmentation_description", wrap=tk.WORD
        )
        section_segmentation_description.insert("1.0", "number of segments into which to divide the coil section")
        section_segmentation_description.grid(row=12, column=2, pady=10, padx=5)
        section_segmentation_description.config(state=tk.DISABLED)

        looping_position = ttk.Label(self.root, text="Looping position:", style="PyAEDT.TLabel")
        looping_position.grid(row=13, column=0, pady=10)
        looping_position_text = tk.Text(self.root, width=40, height=1, name="looping_position")
        looping_position_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        looping_position_text.grid(row=13, column=1, pady=10, padx=5)
        looping_position_description = tk.Text(
            self.root, width=40, height=1, name="looping_position_description", wrap=tk.WORD
        )
        looping_position_description.insert("1.0", "Position of the loop, from 0.5 to 1")
        looping_position_description.grid(row=13, column=2, pady=10, padx=5)
        looping_position_description.config(state=tk.DISABLED)

        distance = ttk.Label(self.root, text="Distance:", style="PyAEDT.TLabel")
        distance.grid(row=14, column=0, pady=10)
        distance_text = tk.Text(self.root, width=40, height=1, name="distance")
        distance_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        distance_text.grid(row=14, column=1, pady=10, padx=5)
        distance_description = tk.Text(self.root, width=40, height=1, name="distance_description", wrap=tk.WORD)
        distance_description.insert("1.0", "Distance between turns")
        distance_description.grid(row=14, column=2, pady=10, padx=5)
        distance_description.config(state=tk.DISABLED)

        if is_vertical.get():
            looping_position_text.config(state=tk.DISABLED, fg="gray", bg="#f0f0f0")
            distance_text.config(state=tk.DISABLED, fg="gray", bg="#f0f0f0")

        def callback(extension: CoilExtension):
            data = CoilExtensionData(
                is_vertical=True if is_vertical.get() == 1 else False,
                centre_x=x_pos_text.get("1.0", tk.END).strip(),
                centre_y=y_pos_text.get("1.0", tk.END).strip(),
                centre_z=z_pos_text.get("1.0", tk.END).strip(),
                turns=turns_text.get("1.0", tk.END).strip(),
                inner_width=inner_width_text.get("1.0", tk.END).strip(),
                inner_length=inner_length_text.get("1.0", tk.END).strip(),
                wire_radius=wire_radius_text.get("1.0", tk.END).strip(),
                inner_distance=inner_distance_text.get("1.0", tk.END).strip(),
                direction=direction_text.get("1.0", tk.END).strip(),
                pitch=pitch_text.get("1.0", tk.END).strip(),
                arc_segmentation=arc_segmentation_text.get("1.0", tk.END).strip(),
                section_segmentation=section_segmentation_text.get("1.0", tk.END).strip(),
                looping_position=looping_position_text.get("1.0", tk.END).strip(),
                distance=distance_text.get("1.0", tk.END).strip(),
            )
            extension.data = data
            self.root.destroy()

        create_coil = ttk.Button(
            self.root,
            text="Create",
            width=40,
            style="PyAEDT.TButton",
            name="create_coil",
            command=lambda: callback(self),
        )
        create_coil.grid(row=16, column=1, pady=10, padx=10)


def main(data: CoilExtensionData):
    """Main function to create vertical or flat coils in AEDT."""
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

    aedtapp = get_pyaedt_app(project_name, design_name)
    if aedtapp.design_type != "Maxwell 3D":
        raise ValueError("This extension can only be used with Maxwell 3D designs.")

    coil = Coil(
        aedtapp,
        name="TOBEADDINUI",
        is_vertical=data.is_vertical,
        centre_x=data.centre_x,
        centre_y=data.centre_y,
        centre_z=data.centre_z,
        turns=data.turns,
        inner_width=data.inner_width,
        inner_length=data.inner_length,
        wire_radius=data.wire_radius,
        inner_distance=data.inner_distance,
        direction=data.direction,
        pitch=data.pitch,
        arc_segmentation=data.arc_segmentation,
        section_segmentation=data.section_segmentation,
        looping_position=data.looping_position,
        distance=data.distance,
    )

    data_dict = asdict(data)
    polyline = (
        coil.create_vertical_path(aedtapp, data_dict) if data.is_vertical else coil.create_flat_path(aedtapp, data_dict)
    )
    coil.create_sweep_profile(aedtapp, [data_dict["centre_x"], data_dict["centre_y"], data_dict["centre_z"]], polyline)

    if "PYTEST_CURRENT_TEST" not in os.environ:
        extension.desktop.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
    default_args = False
    parameters = {}
    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = CoilExtension(withdraw=False)

        tk.mainloop()

        if [d for d in extension.data.__dataclass_fields__ if d == ""]:
            raise ValueError("Not enough entries provided to create the coil. Please fill in all entries.")

        main(extension.data)
    else:
        data = CoilExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
