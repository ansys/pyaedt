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
from pathlib import Path
import tkinter as tk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student


@dataclass
class ExtensionData:
    is_vertical: bool = True
    x_pos: str = ""
    y_pos: str = ""
    z_pos: str = ""
    turns: int = 4
    inner_width: str = ""
    inner_length: str = ""
    wire_radius: str = ""
    inner_distance: str = ""
    direction: int = 1
    pitch: str = ""
    arc_segmentation: int = 4
    section_segmentation: int = 8
    dist: str = ""
    looping_position: float = 0.5
    height_return: str = "2mm"


PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_TITLE = "Create vertical or flat coil"
EXTENSION_DEFAULT_ARGUMENTS = {
    "is_vertical": True,
    "x_pos": "0mm",
    "y_pos": "0mm",
    "z_pos": "0mm",
    "turns": 4,
    "inner_width": "12mm",
    "inner_length": "6mm",
    "wire_radius": "1mm",
    "inner_distance": "2mm",
    "direction": 1,
    "pitch": "3mm",
    "arc_segmentation": 4,
    "section_segmentation": 8,
    "dist": "5mm",
    "looping_position": 0.5,
    "height_return": "2mm",
}

result = None


def _text_size(theme, path, entry):  # pragma: no cover
    # Calculate the length of the text
    text_length = len(path)

    height = 1
    # Adjust font size based on text length
    if text_length > 50:
        height += 1

    # Adjust the width and the height of the Text widget based on text length
    entry.configure(height=height, width=max(40, text_length // 2), font=theme.default_font)

    entry.insert(tk.END, path)


def create_ui(withdraw=False):
    from tkinter import ttk

    from ansys.aedt.core.extensions.misc import create_default_ui

    root, theme, style = create_default_ui(EXTENSION_TITLE, withdraw=withdraw)

    is_vertical_label = ttk.Label(root, text="Vertical Coil", style="PyAEDT.TLabel")
    is_vertical_label.grid(row=0, column=0, pady=10)
    is_vertical = tk.IntVar(root, name="is_vertical")
    check = ttk.Checkbutton(root, variable=is_vertical, style="PyAEDT.TCheckbutton", name="is_vertical")
    check.grid(row=0, column=1, pady=10, padx=5)

    x_pos = ttk.Label(root, text="x position:", style="PyAEDT.TLabel")
    x_pos.grid(row=1, column=0, pady=10)
    x_pos_text = tk.Text(root, width=40, height=1, name="x_pos")
    x_pos_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    x_pos_text.grid(row=1, column=1, pady=10, padx=5)
    x_pos_description = tk.Text(root, width=40, height=1, name="x_pos_description", wrap=tk.WORD)
    x_pos_description.insert("1.0", "x position of coil center point")
    x_pos_description.grid(row=1, column=2, pady=10, padx=5)
    x_pos_description.config(state=tk.DISABLED)

    y_pos = ttk.Label(root, text="y position:", style="PyAEDT.TLabel")
    y_pos.grid(row=2, column=0, pady=10)
    y_pos_text = tk.Text(root, width=40, height=1, name="y_pos")
    y_pos_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    y_pos_text.grid(row=2, column=1, pady=10, padx=5)
    y_pos_description = tk.Text(root, width=40, height=1, name="y_pos_description", wrap=tk.WORD)
    y_pos_description.insert("1.0", "y position of coil center point")
    y_pos_description.grid(row=2, column=2, pady=10, padx=5)
    y_pos_description.config(state=tk.DISABLED)

    z_pos = ttk.Label(root, text="z position:", style="PyAEDT.TLabel")
    z_pos.grid(row=3, column=0, pady=10)
    z_pos_text = tk.Text(root, width=40, height=1, name="z_pos")
    z_pos_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    z_pos_text.grid(row=3, column=1, pady=10, padx=5)
    z_pos_description = tk.Text(root, width=40, height=1, name="z_pos_description", wrap=tk.WORD)
    z_pos_description.insert("1.0", "z position of coil center point")
    z_pos_description.grid(row=3, column=2, pady=10, padx=5)
    z_pos_description.config(state=tk.DISABLED)

    turns = ttk.Label(root, text="Number of turns:", style="PyAEDT.TLabel")
    turns.grid(row=4, column=0, pady=10)
    turns_text = tk.Text(root, width=40, height=1, name="turns")
    turns_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    turns_text.grid(row=4, column=1, pady=10, padx=5)
    turns_description = tk.Text(root, width=40, height=1, name="turns_description", wrap=tk.WORD)
    turns_description.insert("1.0", "Number of turns")
    turns_description.grid(row=4, column=2, pady=10, padx=5)
    turns_description.config(state=tk.DISABLED)

    inner_width = ttk.Label(root, text="Inner width:", style="PyAEDT.TLabel")
    inner_width.grid(row=5, column=0, pady=10)
    inner_width_text = tk.Text(root, width=40, height=1, name="inner_width")
    inner_width_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    inner_width_text.grid(row=5, column=1, pady=10, padx=5)
    inner_width_description = tk.Text(root, width=40, height=2, name="inner_width_description", wrap=tk.WORD)
    inner_width_description.insert("1.0", "Inner width of the coil (length along X axis)")
    inner_width_description.grid(row=5, column=2, pady=10, padx=5)
    inner_width_description.config(state=tk.DISABLED)

    inner_length = ttk.Label(root, text="Inner length:", style="PyAEDT.TLabel")
    inner_length.grid(row=6, column=0, pady=10)
    inner_length_text = tk.Text(root, width=40, height=1, name="inner_length")
    inner_length_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    inner_length_text.grid(row=6, column=1, pady=10, padx=5)
    inner_length_description = tk.Text(root, width=40, height=2, name="inner_length_description", wrap=tk.WORD)
    inner_length_description.insert("1.0", "Inner length of the coil (length along Y axis)")
    inner_length_description.grid(row=6, column=2, pady=10, padx=5)
    inner_length_description.config(state=tk.DISABLED)

    wire_radius = ttk.Label(root, text="Wire radius:", style="PyAEDT.TLabel")
    wire_radius.grid(row=7, column=0, pady=10)
    wire_radius_text = tk.Text(root, width=40, height=1, name="wire_radius")
    wire_radius_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    wire_radius_text.grid(row=7, column=1, pady=10, padx=5)
    wire_radius_description = tk.Text(root, width=40, height=2, name="wire_radius_description", wrap=tk.WORD)
    wire_radius_description.insert("1.0", "Width of the wire (length along Y axis)")
    wire_radius_description.grid(row=7, column=2, pady=10, padx=5)
    wire_radius_description.config(state=tk.DISABLED)

    inner_distance = ttk.Label(root, text="Inner distance:", style="PyAEDT.TLabel")
    inner_distance.grid(row=8, column=0, pady=10)
    inner_distance_text = tk.Text(root, width=40, height=1, name="inner_distance")
    inner_distance_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    inner_distance_text.grid(row=8, column=1, pady=10, padx=5)
    inner_distance_description = tk.Text(root, width=40, height=2, name="inner_distance_description", wrap=tk.WORD)
    inner_distance_description.insert(
        "1.0", "Distance between the coil and the inner rectangle (length along X or Y axis)"
    )
    inner_distance_description.grid(row=8, column=2, pady=10, padx=5)
    inner_distance_description.config(state=tk.DISABLED)

    direction = ttk.Label(root, text="Direction:", style="PyAEDT.TLabel")
    direction.grid(row=9, column=0, pady=10)
    direction_text = tk.Text(root, width=40, height=1, name="direction")
    direction_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    direction_text.grid(row=9, column=1, pady=10, padx=5)
    direction_description = tk.Text(root, width=40, height=1, name="direction_description", wrap=tk.WORD)
    direction_description.insert("1.0", "Direction of the coil (left side 1 or right -1)")
    direction_description.grid(row=9, column=2, pady=10, padx=5)
    direction_description.config(state=tk.DISABLED)

    pitch = ttk.Label(root, text="Pitch:", style="PyAEDT.TLabel")
    pitch.grid(row=10, column=0, pady=10)
    pitch_text = tk.Text(root, width=40, height=1, name="pitch")
    pitch_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    pitch_text.grid(row=10, column=1, pady=10, padx=5)
    pitch_description = tk.Text(root, width=40, height=1, name="pitch_description", wrap=tk.WORD)
    pitch_description.insert("1.0", "Pitch of the coil (deviation along Z axis per turn)")
    pitch_description.grid(row=10, column=2, pady=10, padx=5)
    pitch_description.config(state=tk.DISABLED)

    arc_segmentation = ttk.Label(root, text="Arc segmentation:", style="PyAEDT.TLabel")
    arc_segmentation.grid(row=11, column=0, pady=10)
    arc_segmentation_text = tk.Text(root, width=40, height=1, name="arc_segmentation")
    arc_segmentation_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    arc_segmentation_text.grid(row=11, column=1, pady=10, padx=5)
    arc_segmentation_description = tk.Text(root, width=40, height=1, name="arc_segmentation_description", wrap=tk.WORD)
    arc_segmentation_description.insert("1.0", "number of segments into which to divide the coil corners")
    arc_segmentation_description.grid(row=11, column=2, pady=10, padx=5)
    arc_segmentation_description.config(state=tk.DISABLED)

    section_segmentation = ttk.Label(root, text="Section segmentation:", style="PyAEDT.TLabel")
    section_segmentation.grid(row=12, column=0, pady=10)
    section_segmentation_text = tk.Text(root, width=40, height=1, name="section_segmentation")
    section_segmentation_text.configure(
        bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font
    )
    section_segmentation_text.grid(row=12, column=1, pady=10, padx=5)
    section_segmentation_description = tk.Text(
        root, width=40, height=1, name="section_segmentation_description", wrap=tk.WORD
    )
    section_segmentation_description.insert("1.0", "number of segments into which to divide the coil section")
    section_segmentation_description.grid(row=12, column=2, pady=10, padx=5)
    section_segmentation_description.config(state=tk.DISABLED)

    looping_position = ttk.Label(root, text="Looping position:", style="PyAEDT.TLabel")
    looping_position.grid(row=13, column=0, pady=10)
    looping_position_text = tk.Text(root, width=40, height=1, name="looping_position")
    looping_position_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    looping_position_text.grid(row=13, column=1, pady=10, padx=5)
    looping_position_description = tk.Text(root, width=40, height=1, name="looping_position_description", wrap=tk.WORD)
    looping_position_description.insert("1.0", "Position of the loop, from 0.5 to 1")
    looping_position_description.grid(row=13, column=2, pady=10, padx=5)
    looping_position_description.config(state=tk.DISABLED)

    distance = ttk.Label(root, text="Distance:", style="PyAEDT.TLabel")
    distance.grid(row=14, column=0, pady=10)
    distance_text = tk.Text(root, width=40, height=1, name="distance")
    distance_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    distance_text.grid(row=14, column=1, pady=10, padx=5)
    distance_description = tk.Text(root, width=40, height=1, name="distance_description", wrap=tk.WORD)
    distance_description.insert("1.0", "Position of the loop, from 0.5 to 1")
    distance_description.grid(row=14, column=2, pady=10, padx=5)
    distance_description.config(state=tk.DISABLED)

    height_return = ttk.Label(root, text="Height return:", style="PyAEDT.TLabel")
    height_return.grid(row=15, column=0, pady=10)
    height_return_text = tk.Text(root, width=40, height=1, name="height_return")
    height_return_text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    height_return_text.grid(row=15, column=1, pady=10, padx=5)
    height_return_description = tk.Text(root, width=40, height=1, name="height_return_description", wrap=tk.WORD)
    height_return_description.insert("1.0", "Distance btw Coil and return (length along Z axis)")
    height_return_description.grid(row=15, column=2, pady=10, padx=5)
    height_return_description.config(state=tk.DISABLED)

    if is_vertical.get():
        looping_position_text.config(state=tk.DISABLED, fg="gray", bg="#f0f0f0")
        distance_text.config(state=tk.DISABLED, fg="gray", bg="#f0f0f0")
        height_return_text.config(state=tk.DISABLED, fg="gray", bg="#f0f0f0")

    def toggle_theme():
        if root.theme == "light":
            set_dark_theme()
            root.theme = "dark"
        else:
            set_light_theme()
            root.theme = "light"

    def set_light_theme():
        root.configure(bg=theme.light["widget_bg"])
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263d")  # Sun icon for light theme
        for widget in root.winfo_children():
            if isinstance(widget, tk.Text):
                widget.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def set_dark_theme():
        root.configure(bg=theme.dark["widget_bg"])
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme
        for widget in root.winfo_children():
            if isinstance(widget, tk.Text):
                widget.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)

    button_frame = ttk.Frame(root, style="PyAEDT.TFrame", relief=tk.SUNKEN, borderwidth=2, name="theme_button_frame")
    button_frame.grid(row=16, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263d", command=toggle_theme, style="PyAEDT.TButton", name="theme_toggle_button"
    )
    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        global result
        result = ExtensionData(
            is_vertical=True if is_vertical.get() == 1 else False,
            x_pos=x_pos_text.get("1.0", tk.END).strip(),
            y_pos=y_pos_text.get("1.0", tk.END).strip(),
            z_pos=z_pos_text.get("1.0", tk.END).strip(),
            turns=int(turns_text.get("1.0", tk.END).strip()),
            inner_width=inner_width_text.get("1.0", tk.END).strip(),
            inner_length=inner_length_text.get("1.0", tk.END).strip(),
            wire_radius=wire_radius_text.get("1.0", tk.END).strip(),
            inner_distance=inner_distance_text.get("1.0", tk.END).strip(),
            direction=int(direction_text.get("1.0", tk.END).strip()),
            pitch=pitch_text.get("1.0", tk.END).strip(),
            arc_segmentation=int(arc_segmentation_text.get("1.0", tk.END).strip()),
            section_segmentation=int(section_segmentation_text.get("1.0", tk.END).strip()),
            looping_position=float(looping_position_text.get("1.0", tk.END).strip()),
            dist=distance_text.get("1.0", tk.END).strip(),
            height_return=height_return_text.get("1.0", tk.END).strip(),
        )
        root.destroy()

    create_coil = ttk.Button(
        root, text="Create", width=40, style="PyAEDT.TButton", name="create_coil", command=callback
    )
    create_coil.grid(row=16, column=1, pady=10, padx=10)

    return root


def main(extension_args):
    is_vertical = Path(extension_args["is_vertical"])

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

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        root = create_ui()

        tk.mainloop()

        if result:
            args.update(asdict(result))
            main(args)
    else:
        main(args)
