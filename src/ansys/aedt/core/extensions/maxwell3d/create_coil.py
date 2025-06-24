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
from ansys.aedt.core.generic.numbers import Quantity
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.coil import Coil

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_TITLE = "Create coil"
EXTENSION_DEFAULT_ARGUMENTS = {
    "coil_type": "vertical",
    "name": "coil",
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


@dataclass
class CoilExtensionData(ExtensionCommonData):
    """Data class containing parameters to create coils."""

    coil_type: str = EXTENSION_DEFAULT_ARGUMENTS["coil_type"]
    name: str = EXTENSION_DEFAULT_ARGUMENTS["name"]
    # Full superset of possible parameters
    centre_x: str = EXTENSION_DEFAULT_ARGUMENTS["centre_x"]
    centre_y: str = EXTENSION_DEFAULT_ARGUMENTS["centre_y"]
    centre_z: str = EXTENSION_DEFAULT_ARGUMENTS["centre_z"]
    turns: str = EXTENSION_DEFAULT_ARGUMENTS["turns"]
    inner_width: str = EXTENSION_DEFAULT_ARGUMENTS["inner_width"]
    inner_length: str = EXTENSION_DEFAULT_ARGUMENTS["inner_length"]
    wire_radius: str = EXTENSION_DEFAULT_ARGUMENTS["wire_radius"]
    inner_distance: str = EXTENSION_DEFAULT_ARGUMENTS["inner_distance"]
    direction: str = EXTENSION_DEFAULT_ARGUMENTS["direction"]
    pitch: str = EXTENSION_DEFAULT_ARGUMENTS["pitch"]
    arc_segmentation: str = EXTENSION_DEFAULT_ARGUMENTS["arc_segmentation"]
    section_segmentation: str = EXTENSION_DEFAULT_ARGUMENTS["section_segmentation"]
    distance: str = EXTENSION_DEFAULT_ARGUMENTS["distance"]
    looping_position: str = EXTENSION_DEFAULT_ARGUMENTS["looping_position"]


class CoilExtension(ExtensionCommon):
    """Extension to create coils in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=18,
            toggle_column=2,
        )
        # Initialize the Coil class
        self.coil = Coil(self.aedt_application)
        # Tkinter widgets
        self.check = None
        self.name_text = None
        self.x_pos_text = None
        self.y_pos_text = None
        self.turns_text = None
        self.inner_width_text = None
        self.inner_length_text = None
        self.wire_radius_text = None
        self.inner_distance_text = None
        self.arc_segmentation_text = None
        self.section_segmentation_text = None
        self.looping_position_text = None
        self.distance_text = None
        self.z_pos_text = None
        self.direction_text = None
        self.pitch_text = None
        # add custom content
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        self.root.geometry("850x750")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        def on_checkbox_toggle():
            if is_vertical.get() == 0:
                # unchecked
                # Flat coil
                self.looping_position_text.config(state=tk.NORMAL)
                self.distance_text.config(state=tk.NORMAL)
                self.z_pos_text.config(state=tk.DISABLED)
                self.direction_text.config(state=tk.DISABLED)
                self.pitch_text.config(state=tk.DISABLED)
            else:
                # checked
                # Vertical coil
                self.looping_position_text.config(state=tk.DISABLED)
                self.distance_text.config(state=tk.DISABLED)
                self.z_pos_text.config(state=tk.NORMAL)
                self.direction_text.config(state=tk.NORMAL)
                self.pitch_text.config(state=tk.NORMAL)

        is_vertical_label = ttk.Label(self.root, text="Vertical Coil", style="PyAEDT.TLabel", width=20)
        is_vertical_label.grid(row=0, column=0, pady=5, padx=5)
        is_vertical = tk.IntVar(self.root, name="is_vertical")
        self.check = ttk.Checkbutton(
            self.root, variable=is_vertical, style="PyAEDT.TCheckbutton", name="is_vertical", command=on_checkbox_toggle
        )
        self.check.grid(row=0, column=1, pady=5, padx=5)
        is_vertical_description = tk.Text(self.root, width=40, height=2, name="is_vertical_description", wrap=tk.WORD)
        is_vertical_description.insert("1.0", "If checkbox is selected, the coil is vertical, otherwise flat.")
        is_vertical_description.grid(row=0, column=2, pady=1, padx=5)
        is_vertical_description.config(state=tk.DISABLED)

        name = ttk.Label(self.root, text="Coil name:", style="PyAEDT.TLabel", width=20)
        name.grid(row=1, column=0, pady=5, padx=5)
        self.name_text = tk.Text(self.root, width=20, height=1, name="coil_name")
        self.name_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.name_text.grid(row=1, column=1, pady=5, padx=5)
        name_description = tk.Text(self.root, width=40, height=1, name="name_description", wrap=tk.WORD)
        name_description.insert("1.0", "Coil name")
        name_description.grid(row=1, column=2, pady=5, padx=5)
        name_description.config(state=tk.DISABLED)

        centre_x = ttk.Label(self.root, text="x position:", style="PyAEDT.TLabel", width=20)
        centre_x.grid(row=2, column=0, pady=5)
        self.x_pos_text = tk.Text(self.root, width=20, height=1, name="centre_x")
        self.x_pos_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.x_pos_text.grid(row=2, column=1, pady=5, padx=5)
        x_pos_description = tk.Text(self.root, width=40, height=1, name="x_pos_description", wrap=tk.WORD)
        x_pos_description.insert("1.0", "x position of coil center point")
        x_pos_description.grid(row=2, column=2, pady=5, padx=5)
        x_pos_description.config(state=tk.DISABLED)

        centre_y = ttk.Label(self.root, text="y position:", style="PyAEDT.TLabel", width=20)
        centre_y.grid(row=3, column=0, pady=5)
        self.y_pos_text = tk.Text(self.root, width=20, height=1, name="centre_y")
        self.y_pos_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.y_pos_text.grid(row=3, column=1, pady=5, padx=5)
        y_pos_description = tk.Text(self.root, width=40, height=1, name="y_pos_description", wrap=tk.WORD)
        y_pos_description.insert("1.0", "y position of coil center point")
        y_pos_description.grid(row=3, column=2, pady=5, padx=5)
        y_pos_description.config(state=tk.DISABLED)

        turns = ttk.Label(self.root, text="Number of turns:", style="PyAEDT.TLabel", width=20)
        turns.grid(row=4, column=0, pady=5)
        self.turns_text = tk.Text(self.root, width=20, height=1, name="turns")
        self.turns_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.turns_text.grid(row=4, column=1, pady=5, padx=5)
        turns_description = tk.Text(self.root, width=40, height=1, name="turns_description", wrap=tk.WORD)
        turns_description.insert("1.0", "Number of turns")
        turns_description.grid(row=4, column=2, pady=5, padx=5)
        turns_description.config(state=tk.DISABLED)

        inner_width = ttk.Label(self.root, text="Inner width:", style="PyAEDT.TLabel", width=20)
        inner_width.grid(row=5, column=0, pady=5)
        self.inner_width_text = tk.Text(self.root, width=20, height=1, name="inner_width")
        self.inner_width_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.inner_width_text.grid(row=5, column=1, pady=5, padx=5)
        inner_width_description = tk.Text(self.root, width=40, height=2, name="inner_width_description", wrap=tk.WORD)
        inner_width_description.insert("1.0", "Inner width of the coil (length along X axis)")
        inner_width_description.grid(row=5, column=2, pady=5, padx=5)
        inner_width_description.config(state=tk.DISABLED)

        inner_length = ttk.Label(self.root, text="Inner length:", style="PyAEDT.TLabel", width=20)
        inner_length.grid(row=6, column=0, pady=5)
        self.inner_length_text = tk.Text(self.root, width=20, height=1, name="inner_length")
        self.inner_length_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.inner_length_text.grid(row=6, column=1, pady=5, padx=5)
        inner_length_description = tk.Text(self.root, width=40, height=2, name="inner_length_description", wrap=tk.WORD)
        inner_length_description.insert("1.0", "Inner length of the coil (length along Y axis)")
        inner_length_description.grid(row=6, column=2, pady=5, padx=5)
        inner_length_description.config(state=tk.DISABLED)

        wire_radius = ttk.Label(self.root, text="Wire radius:", style="PyAEDT.TLabel", width=20)
        wire_radius.grid(row=7, column=0, pady=5)
        self.wire_radius_text = tk.Text(self.root, width=20, height=1, name="wire_radius")
        self.wire_radius_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.wire_radius_text.grid(row=7, column=1, pady=5, padx=5)
        wire_radius_description = tk.Text(self.root, width=40, height=2, name="wire_radius_description", wrap=tk.WORD)
        wire_radius_description.insert("1.0", "Width of the wire (length along Y axis)")
        wire_radius_description.grid(row=7, column=2, pady=5, padx=5)
        wire_radius_description.config(state=tk.DISABLED)

        inner_distance = ttk.Label(self.root, text="Inner distance:", style="PyAEDT.TLabel", width=20)
        inner_distance.grid(row=8, column=0, pady=5)
        self.inner_distance_text = tk.Text(self.root, width=20, height=1, name="inner_distance")
        self.inner_distance_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.inner_distance_text.grid(row=8, column=1, pady=5, padx=5)
        inner_distance_description = tk.Text(
            self.root, width=40, height=2, name="inner_distance_description", wrap=tk.WORD
        )
        inner_distance_description.insert(
            "1.0", "Distance between the coil and the inner rectangle (length along X or Y axis)"
        )
        inner_distance_description.grid(row=8, column=2, pady=5, padx=5)
        inner_distance_description.config(state=tk.DISABLED)

        arc_segmentation = ttk.Label(self.root, text="Arc segmentation:", style="PyAEDT.TLabel", width=20)
        arc_segmentation.grid(row=9, column=0, pady=5)
        self.arc_segmentation_text = tk.Text(self.root, width=20, height=1, name="arc_segmentation")
        self.arc_segmentation_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.arc_segmentation_text.grid(row=9, column=1, pady=5, padx=5)
        arc_segmentation_description = tk.Text(
            self.root, width=40, height=2, name="arc_segmentation_description", wrap=tk.WORD
        )
        arc_segmentation_description.insert("1.0", "number of segments into which to divide the coil corners")
        arc_segmentation_description.grid(row=9, column=2, pady=5, padx=5)
        arc_segmentation_description.config(state=tk.DISABLED)

        section_segmentation = ttk.Label(self.root, text="Section segmentation:", style="PyAEDT.TLabel", width=20)
        section_segmentation.grid(row=10, column=0, pady=5)
        self.section_segmentation_text = tk.Text(self.root, width=20, height=1, name="section_segmentation")
        self.section_segmentation_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.section_segmentation_text.grid(row=10, column=1, pady=5, padx=5)
        section_segmentation_description = tk.Text(
            self.root, width=40, height=2, name="section_segmentation_description", wrap=tk.WORD
        )
        section_segmentation_description.insert("1.0", "number of segments into which to divide the coil section")
        section_segmentation_description.grid(row=10, column=2, pady=5, padx=5)
        section_segmentation_description.config(state=tk.DISABLED)

        flat_specific_section = ttk.Label(self.root, text="Flat specific parameters:", style="PyAEDT.TLabel", width=20)
        flat_specific_section.grid(row=11, column=1, pady=5, padx=5)

        looping_position = ttk.Label(self.root, text="Looping position:", style="PyAEDT.TLabel", width=20)
        looping_position.grid(row=12, column=0, pady=5)
        self.looping_position_text = tk.Text(self.root, width=20, height=1, name="looping_position")
        self.looping_position_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.looping_position_text.grid(row=12, column=1, pady=5, padx=5)
        looping_position_description = tk.Text(
            self.root, width=40, height=1, name="looping_position_description", wrap=tk.WORD
        )
        looping_position_description.insert("1.0", "Position of the loop, from 0.5 to 1")
        looping_position_description.grid(row=12, column=2, pady=5, padx=5)
        looping_position_description.config(state=tk.DISABLED)

        distance = ttk.Label(self.root, text="Distance:", style="PyAEDT.TLabel", width=20)
        distance.grid(row=13, column=0, pady=5)
        self.distance_text = tk.Text(self.root, width=20, height=1, name="distance")
        self.distance_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.distance_text.grid(row=13, column=1, pady=5, padx=5)
        distance_description = tk.Text(self.root, width=40, height=1, name="distance_description", wrap=tk.WORD)
        distance_description.insert("1.0", "Distance between turns")
        distance_description.grid(row=13, column=2, pady=5, padx=5)
        distance_description.config(state=tk.DISABLED)

        vertical_specific_section = ttk.Label(
            self.root, text="Vertical specific parameters:", style="PyAEDT.TLabel", width=25
        )
        vertical_specific_section.grid(row=14, column=1, pady=5, padx=5)

        centre_z = ttk.Label(self.root, text="z position:", style="PyAEDT.TLabel", width=20)
        centre_z.grid(row=15, column=0, pady=5)
        self.z_pos_text = tk.Text(self.root, width=20, height=1, name="centre_z", state=tk.DISABLED)
        self.z_pos_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.z_pos_text.grid(row=15, column=1, pady=5, padx=5)
        z_pos_description = tk.Text(self.root, width=40, height=1, name="z_pos_description", wrap=tk.WORD)
        z_pos_description.insert("1.0", "z position of coil center point")
        z_pos_description.grid(row=15, column=2, pady=5, padx=5)
        z_pos_description.config(state=tk.DISABLED)

        direction = ttk.Label(self.root, text="Direction:", style="PyAEDT.TLabel", width=20)
        direction.grid(row=16, column=0, pady=5)
        self.direction_text = tk.Text(self.root, width=20, height=1, name="direction", state=tk.DISABLED)
        self.direction_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.direction_text.grid(row=16, column=1, pady=5, padx=5)
        direction_description = tk.Text(self.root, width=40, height=2, name="direction_description", wrap=tk.WORD)
        direction_description.insert("1.0", "Direction of the coil (left side 1 or right -1)")
        direction_description.grid(row=16, column=2, pady=5, padx=5)
        direction_description.config(state=tk.DISABLED)

        pitch = ttk.Label(self.root, text="Pitch:", style="PyAEDT.TLabel", width=20)
        pitch.grid(row=17, column=0, pady=5)
        self.pitch_text = tk.Text(self.root, width=20, height=1, name="pitch", state=tk.DISABLED)
        self.pitch_text.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.pitch_text.grid(row=17, column=1, pady=5, padx=5)
        pitch_description = tk.Text(self.root, width=40, height=2, name="pitch_description", wrap=tk.WORD)
        pitch_description.insert("1.0", "Pitch of the coil (deviation along Z axis per turn)")
        pitch_description.grid(row=17, column=2, pady=5, padx=5)
        pitch_description.config(state=tk.DISABLED)

        def callback(extension: CoilExtension):
            data = CoilExtensionData(
                coil_type="vertical" if self.check.state() == 1 else "flat",
                name=self.name_text.get("1.0", tk.END).strip(),
                centre_x=self.x_pos_text.get("1.0", tk.END).strip(),
                centre_y=self.y_pos_text.get("1.0", tk.END).strip(),
                centre_z=self.z_pos_text.get("1.0", tk.END).strip(),
                turns=self.turns_text.get("1.0", tk.END).strip(),
                inner_width=self.inner_width_text.get("1.0", tk.END).strip(),
                inner_length=self.inner_length_text.get("1.0", tk.END).strip(),
                wire_radius=self.wire_radius_text.get("1.0", tk.END).strip(),
                inner_distance=self.inner_distance_text.get("1.0", tk.END).strip(),
                direction=self.direction_text.get("1.0", tk.END).strip(),
                pitch=self.pitch_text.get("1.0", tk.END).strip(),
                arc_segmentation=self.arc_segmentation_text.get("1.0", tk.END).strip(),
                section_segmentation=self.section_segmentation_text.get("1.0", tk.END).strip(),
                looping_position=self.looping_position_text.get("1.0", tk.END).strip(),
                distance=self.distance_text.get("1.0", tk.END).strip(),
            )
            try:
                self.coil.validate_coil_arguments(asdict(data), coil_type=data.coil_type)
            except ValueError as e:
                raise AEDTRuntimeError(str(e))
            extension.data = data
            self.root.destroy()

        create_coil = ttk.Button(
            self.root,
            text="Create",
            width=20,
            style="PyAEDT.TButton",
            name="create_coil",
            command=lambda: callback(self),
        )
        create_coil.grid(row=18, column=1, pady=5, padx=10)


def main(data: CoilExtensionData):
    """Main function to create coils in AEDT."""
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
        raise AEDTRuntimeError("This extension can only be used with Maxwell 3D designs.")

    coil = Coil(aedtapp, name=data.name, coil_type=data.coil_type, coil_parameters=asdict(data))

    data_dict = asdict(data)

    # Create polyline shape for coil
    polyline = coil.create_vertical_path() if data.coil_type == "vertical" else coil.create_flat_path()

    centre_x = Quantity(data_dict["centre_x"]).value
    centre_y = Quantity(data_dict["centre_y"]).value
    inner_y = Quantity(data_dict["inner_length"]).value

    if data.coil_type == "vertical":
        centre_z = Quantity(data_dict["centre_z"]).value
        inner_distance = Quantity(data_dict["inner_distance"]).value
        pitch = Quantity(data_dict["pitch"]).value
        turns = int(data_dict["turns"])
        start_point = [
            centre_x,
            centre_y - 0.5 * inner_y - inner_distance,
            centre_z + pitch * turns * 0.5,
        ]
    else:
        inner_x = Quantity(data_dict["inner_width"]).value
        start_position = Quantity(data_dict["looping_position"]).value
        start_point = [
            centre_x + 0.25 * inner_x,
            centre_y - (start_position - 0.5) * inner_y,
            0,
        ]
    # Create coil profile
    coil.create_sweep_profile(start_point, polyline)

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

        main(extension.data)
    else:
        data = CoilExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
