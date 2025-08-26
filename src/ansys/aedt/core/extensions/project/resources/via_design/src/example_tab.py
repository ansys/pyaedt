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
from functools import partial
from pathlib import Path
from tkinter import filedialog
from tkinter import ttk

import PIL

from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import SUN


@dataclass
class ExportExampleData:
    """"""

    picture_path: Path
    toml_file_path: Path


def create_example_ui(frame, app_instance, EXTENSION_NB_COLUMN):
    def save_example(toml_file_path: Path):
        file_path = filedialog.asksaveasfilename(
            initialfile=toml_file_path.name,
            defaultextension=".toml",
            filetypes=[("TOML File", "*.toml"), ("All Files", "*.*")],
            title="Save example as",
        )
        if file_path:
            with open(toml_file_path, "r", encoding="utf-8") as file:
                config_string = file.read()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(config_string)

    export_exmaples = [
        ExportExampleData(
            app_instance.EXTENSION_RESOURCES_PATH / "via_design_rf.png",
            app_instance.EXTENSION_RESOURCES_PATH / "pcb_rf.toml",
        ),
        ExportExampleData(
            app_instance.EXTENSION_RESOURCES_PATH / "via_design_pcb_diff.png",
            app_instance.EXTENSION_RESOURCES_PATH / "pcb_diff.toml",
        ),
        ExportExampleData(
            app_instance.EXTENSION_RESOURCES_PATH / "via_design_pkg_diff.png",
            app_instance.EXTENSION_RESOURCES_PATH / "package_diff.toml",
        ),
    ]

    row = 0
    column = 0
    for example in export_exmaples:
        img = PIL.Image.open(example.picture_path)
        img = img.resize((100, 100))
        photo = PIL.ImageTk.PhotoImage(img, master=frame)

        example_name = example.toml_file_path.stem
        button = ttk.Button(
            frame,
            command=partial(save_example, example.toml_file_path),
            style="PyAEDT.TButton",
            image=photo,
            width=20,
            name=f"button_{example_name}",
        )
        # NOTE: Setting button.image ensures that a reference to the photo is kept and that
        # the picture is correctly rendered in the tkinter window
        button.image = photo
        button.grid(row=row, column=column, **DEFAULT_PADDING)

        if column > EXTENSION_NB_COLUMN:
            row += 1
            column = 0
        else:
            column += 1

    lower_frame = ttk.Frame(app_instance.root, style="PyAEDT.TFrame")
    lower_frame.grid(row=2, column=0, columnspan=EXTENSION_NB_COLUMN)

    create_design_button = ttk.Button(
        lower_frame,
        text="Create Design",
        command=app_instance.create_design,
        style="PyAEDT.TButton",
        width=20,
        name="button_create_design",
    )
    create_design_button.grid(row=0, column=0, sticky="w", **DEFAULT_PADDING)
    change_theme_button = ttk.Button(
        lower_frame,
        width=20,
        text=SUN,
        command=app_instance.toggle_theme,
        style="PyAEDT.TButton",
        name="theme_toggle_button",
    )
    change_theme_button.grid(row=0, column=1)
