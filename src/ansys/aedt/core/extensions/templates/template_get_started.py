# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

from dataclasses import asdict
from dataclasses import dataclass
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

EXTENSION_DEFAULT_ARGUMENTS = {"origin_x": 0, "origin_y": 0, "origin_z": 0, "radius": 1, "file_path": ""}
EXTENSION_TITLE = "Extension template"

result = None


@dataclass
class ExtensionData:
    """Data class containing user input."""

    origin_x: float = 0.0
    origin_y: float = 0.0
    origin_z: float = 0.0
    radius: float = 1
    file_path: str = ""


class TemplateExtension(ExtensionProjectCommon):
    """Extension template to help get started."""

    def __init__(self, withdraw: bool = False):
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=6,
            toggle_column=2,
        )

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Origin x entry
        origin_x_label = ttk.Label(self.root, text="Origin X:", width=20, style="PyAEDT.TLabel")
        origin_x_label.grid(row=0, column=0, padx=15, pady=10)
        origin_x_entry = tkinter.Text(self.root, width=40, height=1)
        origin_x_entry.grid(row=0, column=1, pady=15, padx=10)
        origin_x_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Origin y entry
        origin_y_label = ttk.Label(self.root, text="Origin Y:", width=20, style="PyAEDT.TLabel")
        origin_y_label.grid(row=1, column=0, padx=15, pady=10)
        origin_y_entry = tkinter.Text(self.root, width=40, height=1)
        origin_y_entry.grid(row=1, column=1, pady=15, padx=10)
        origin_y_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Origin z entry
        origin_z_label = ttk.Label(self.root, text="Origin Y:", width=20, style="PyAEDT.TLabel")
        origin_z_label.grid(row=2, column=0, padx=15, pady=10)
        origin_z_entry = tkinter.Text(self.root, width=40, height=1)
        origin_z_entry.grid(row=2, column=1, pady=15, padx=10)
        origin_z_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Radius entry
        radius_label = ttk.Label(self.root, text="Radius:", width=20, style="PyAEDT.TLabel")
        radius_label.grid(row=3, column=0, padx=15, pady=10)
        radius_entry = tkinter.Text(self.root, width=40, height=1)
        radius_entry.grid(row=3, column=1, pady=15, padx=10)
        radius_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Browse file entry
        browse_file_label = ttk.Label(self.root, text="Browse File:", width=20, style="PyAEDT.TLabel")
        browse_file_label.grid(row=4, column=0, pady=10)
        browse_file_entry = tkinter.Text(self.root, width=40, height=1)
        browse_file_entry.grid(row=4, column=1, pady=15, padx=10)
        browse_file_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Project name info
        project_name_label = ttk.Label(self.root, text="Project Name:", width=20, style="PyAEDT.TLabel")
        project_name_label.grid(row=5, column=0, pady=10)
        project_name_entry = tkinter.Text(self.root, width=40, height=1)
        project_name_entry.insert(tkinter.INSERT, self.active_project_name)
        project_name_entry.grid(row=5, column=1, pady=15, padx=10)
        project_name_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        def callback():
            global result
            result = ExtensionData(
                origin_x=float(origin_x_entry.get("1.0", tkinter.END).strip() or 0.0),
                origin_y=float(origin_y_entry.get("1.0", tkinter.END).strip() or 0.0),
                origin_z=float(origin_z_entry.get("1.0", tkinter.END).strip() or 0.0),
                radius=float(radius_entry.get("1.0", tkinter.END).strip() or 1.0),
                file_path=browse_file_entry.get("1.0", tkinter.END).strip(),
            )
            self.root.destroy()

        def browse_files():
            global result
            filename = filedialog.askopenfilename(
                initialdir="/",
                title="Select an Electronics File",
                filetypes=(("AEDT", ".aedt"), ("all files", "*.*")),
            )
            browse_file_entry.insert(tkinter.END, filename)
            result = ExtensionData(file_path=browse_file_entry.get("1.0", tkinter.END).strip())

            self.root.destroy()

        # Create button to browse an AEDT file
        browse_button = ttk.Button(
            self.root, text="...", command=browse_files, width=10, style="PyAEDT.TButton", name="browse_button"
        )
        browse_button.grid(row=4, column=2, pady=10, padx=15)

        # Create button to generate sphere
        create_button = ttk.Button(
            self.root, text="Create Sphere", command=callback, style="PyAEDT.TButton", name="create_button"
        )
        create_button.grid(row=6, column=0, padx=15, pady=10)


def main(extension_args):
    origin_x = extension_args.get("origin_x", EXTENSION_DEFAULT_ARGUMENTS["origin_x"])
    origin_y = extension_args.get("origin_y", EXTENSION_DEFAULT_ARGUMENTS["origin_y"])
    origin_z = extension_args.get("origin_z", EXTENSION_DEFAULT_ARGUMENTS["origin_z"])
    radius = extension_args.get("radius", EXTENSION_DEFAULT_ARGUMENTS["radius"])
    file_path = Path(extension_args.get("file_path", EXTENSION_DEFAULT_ARGUMENTS["file_path"]))

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    active_project = app.active_project()
    active_design = app.active_design()

    if active_project is None:
        raise AEDTRuntimeError(
            "No active project found. Please open or create a project before running this extension."
        )

    project_name = active_project.GetName()
    if active_design.GetDesignType() == "HFSS 3D Layout Design":
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()
    aedtapp = get_pyaedt_app(project_name, design_name)

    if file_path.is_file():
        app.logger.info("Loading project...")
        aedtapp.load_project(str(file_path), set_active=True)
        app.logger.info("Project loaded.")
    else:
        app.logger.info("Creating sphere...")
        aedtapp.modeler.create_sphere([origin_x, origin_y, origin_z], radius)
        app.logger.info(f"Sphere created with origin ({origin_x}, {origin_y}, {origin_z}) and radius {radius}.")

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        extension: ExtensionProjectCommon = TemplateExtension(withdraw=False)

        tkinter.mainloop()

        if result:
            args.update(asdict(result))
            main(args)
    else:
        main(args)
