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
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.plot.pyvista import ModelPlotter

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"choice": "", "points": 1000, "output_file": ""}
EXTENSION_TITLE = "Point cloud generator"


@dataclass
class PointsCloudExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    choice: str = EXTENSION_DEFAULT_ARGUMENTS["choice"]
    points: int = EXTENSION_DEFAULT_ARGUMENTS["points"]
    output_file: str = EXTENSION_DEFAULT_ARGUMENTS["output_file"]


class PointsCloudExtension(ExtensionCommon):
    """Extension for point cloud generator in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=3,  # TODO: Adapt position of theme button
            toggle_column=2,
        )
        # Add private attributes and initialize them through load_aedt_info
        self._aedt_solids = None
        self._aedt_sheets = None
        self.load_aedt_info()

        # Tkinter widgets
        self.objects_list_lb = None
        self.scroll_bar = None
        self.points_entry = None
        self.output_file_entry = None

        # Trigger manually since add_extension_content requires loading info from current project first
        self.add_extension_content()

    def load_aedt_info(self):
        """Load info."""
        aedt_solids = self.aedt_application.modeler.get_objects_in_group("Solids")
        aedt_sheets = self.aedt_application.modeler.get_objects_in_group("Sheets")

        if not aedt_solids and not aedt_sheets:
            self.release_desktop(False, False)
            raise AEDTRuntimeError("No solids or sheets are defined in this design.")
        self._aedt_solids = aedt_solids
        self._aedt_sheets = aedt_sheets

    def add_extension_content(self):
        """Add custom content to the extension UI."""

        # Dropdown menu for objects and surfaces
        objects_surface_label = ttk.Label(self.root, text="Select Object or Surface:", width=20, style="PyAEDT.TLabel")
        objects_surface_label.grid(row=0, column=0, pady=10)
        # List all objects and surfaces available
        entries = []
        if self._aedt_solids:
            entries.append("--- Objects ---")
            entries.extend(self._aedt_solids)
        if self._aedt_sheets:
            entries.append("--- Surfaces ---")
            entries.extend(self._aedt_sheets)
        # Determine the height of the ListBox
        listbox_height = min(len(entries), 6)
        objects_list_frame = tkinter.Frame(self.root, width=20)
        objects_list_frame.grid(row=0, column=1, pady=10, padx=10, sticky="ew")
        self.objects_list_lb = tkinter.Listbox(
            objects_list_frame,
            selectmode=tkinter.MULTIPLE,
            justify=tkinter.CENTER,
            exportselection=False,
            height=listbox_height,
        )
        self.objects_list_lb.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        # Add scrollbar if more than 6 elements are to be displayed
        if len(entries) > 6:
            self.scroll_bar = tkinter.Scrollbar(
                objects_list_frame, orient=tkinter.VERTICAL, command=self.objects_list_lb.yview
            )
            self.scroll_bar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
            self.objects_list_lb.config(yscrollcommand=self.scroll_bar.set, height=listbox_height)
            self.scroll_bar.configure(background=self.theme.light["widget_bg"])
        # Populate the listbox
        for obj in entries:
            self.objects_list_lb.insert(tkinter.END, obj)
        self.objects_list_lb.configure(
            background=self.theme.light["widget_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Points entry
        points_label = ttk.Label(self.root, text="Number of Points:", width=20, style="PyAEDT.TLabel")
        points_label.grid(row=1, column=0, padx=15, pady=10)
        self.points_entry = tkinter.Text(self.root, width=40, height=1)
        self.points_entry.insert(tkinter.END, "1000")
        self.points_entry.grid(row=1, column=1, pady=15, padx=10)
        self.points_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Output file entry
        output_file_label = ttk.Label(self.root, text="Output File:", width=20, style="PyAEDT.TLabel")
        output_file_label.grid(row=2, column=0, padx=15, pady=10)
        self.output_file_entry = tkinter.Text(self.root, width=40, height=1, wrap=tkinter.WORD)
        self.output_file_entry.grid(row=2, column=1, pady=15, padx=10)
        self.output_file_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        def browse_output_location(extension: PointsCloudExtension):
            filename = filedialog.asksaveasfilename(
                initialdir="/",
                title="Select output folder",
                defaultextension=".pts",
                filetypes=(("Points file", ".pts"), ("all files", "*.*")),
            )
            self.output_file_entry.insert(tkinter.END, filename)
            extension.data = PointsCloudExtensionData(
                output_file=self.output_file_entry.get("1.0", tkinter.END).strip()
            )

        # Output file button
        output_file_button = ttk.Button(
            self.root,
            text="Save as...",
            width=20,
            command=lambda: browse_output_location(self),
            style="PyAEDT.TButton",
            name="browse_output",
        )
        output_file_button.grid(row=2, column=2, padx=0)

        @graphics_required
        def preview():
            import pyvista as pv

            try:
                selected_objects = [self.objects_list_lb.get(i) for i in self.objects_list_lb.curselection()]
                if not selected_objects or any(
                    element in selected_objects for element in ["--- Objects ---", "--- Surfaces ---", ""]
                ):
                    self.release_desktop(False, False)
                    raise AEDTRuntimeError("Please select a valid object or surface.")
                points = self.points_entry.get("1.0", tkinter.END).strip()
                num_points = int(points)
                if num_points <= 0:
                    raise AEDTRuntimeError("Number of points must be greater than zero.")

                # Export the mesh and generate point cloud
                output_file = self.aedt_application.post.export_model_obj(assignment=selected_objects)

                if not output_file or not Path(output_file[0][0]).is_file():
                    AEDTRuntimeError("Object could not be exported.")
                    self.release_desktop(False, False)

                geometry_file = output_file[0][0]

                # Generate and visualize the point cloud
                model_plotter = ModelPlotter()
                model_plotter.add_object(geometry_file)
                point_cloud = model_plotter.point_cloud(points=num_points)

                plotter = pv.Plotter()
                for _, actor in point_cloud.values():
                    plotter.add_mesh(actor, color="white", point_size=5, render_points_as_spheres=True)
                plotter.show()

            except Exception as e:
                AEDTRuntimeError(str(e))
                self.release_desktop(False, False)

        # Preview button
        preview_button = ttk.Button(
            self.root, text="Preview", width=40, command=preview, style="PyAEDT.TButton", name="preview"
        )
        preview_button.grid(row=3, column=0, pady=10, padx=10)

        def callback(extension: PointsCloudExtension):
            selected_objects = self.objects_list_lb.curselection()
            if not selected_objects or any(
                element in selected_objects for element in ["--- Objects ---", "--- Surfaces ---", ""]
            ):
                AEDTRuntimeError("Please select a valid object or surface.")
                self.release_desktop(False, False)

            points = self.points_entry.get("1.0", tkinter.END).strip()
            num_points = int(points)
            if num_points <= 0:
                AEDTRuntimeError("Number of points must be greater than zero.")
                self.release_desktop(False, False)

            extension.data = PointsCloudExtensionData(
                choice=[self.objects_list_lb.get(i) for i in selected_objects],
                points=points,
                output_file=self.output_file_entry.get("1.0", tkinter.END).strip(),
            )
            self.root.destroy()

        # Generate button
        generate_button = ttk.Button(
            self.root,
            text="Generate",
            width=40,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        generate_button.grid(row=3, column=1, pady=10, padx=10)


def main(data: PointsCloudExtensionData):
    """Main function to run the point cloud generator extension."""
    app = ansys.aedt.core.Desktop(
        new_desktop=False, version=VERSION, port=PORT, aedt_process_id=AEDT_PROCESS_ID, student_version=IS_STUDENT
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    if active_design.GetDesignType() == "HFSS 3D Layout Design":
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    assignment = data.choice
    points = data.points
    output_file = data.output_file

    # Export the mesh and generate point cloud
    output_file = aedtapp.post.export_model_obj(assignment=assignment, export_path=Path(output_file).parent)

    geometry_file = output_file[0][0]

    # Generate and visualize the point cloud
    model_plotter = ModelPlotter()
    model_plotter.add_object(geometry_file)
    point_values = model_plotter.point_cloud(points=int(points))

    if aedtapp.design_type == "HFSS":
        for input_file, _ in point_values.values():
            _ = aedtapp.insert_near_field_points(input_file=input_file)

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return str(point_values[list(point_values.keys())[0]][0])


if __name__ == "__main__":
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        extension: ExtensionCommon = PointsCloudExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = PointsCloudExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
