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
from tkinter import font
from tkinter import ttk
from typing import Union

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
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
EXTENSION_NB_COLUMN = 3


@dataclass
class PointsCloudExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    choice: Union[str, list[str]] = EXTENSION_DEFAULT_ARGUMENTS["choice"]
    points: int = EXTENSION_DEFAULT_ARGUMENTS["points"]
    output_file: str = EXTENSION_DEFAULT_ARGUMENTS["output_file"]


class PointsCloudExtension(ExtensionProjectCommon):
    """Extension for point cloud generator in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )
        # Add private attributes and initialize them through __load_aedt_info
        self.__aedt_solids = None
        self.__aedt_sheets = None
        self.__load_aedt_info()

        # Trigger manually since add_extension_content requires loading info from current project first
        self.add_extension_content()

    def check_design_type(self):
        """Check if the design type is HFSS, Icepak, HFSS 3D, Maxwell 3D, Maxwell 2D, Q3D, Mechanical"""
        if self.aedt_application.design_type not in [
            "HFSS",
            "Icepak",
            "HFSS 3D",
            "Maxwell 3D",
            "Maxwell 2D",
            "Q3D",
            "Mechanical",
        ]:
            self.release_desktop()
            raise AEDTRuntimeError(
                "This extension only works with HFSS, Icepak, HFSS 3D, "
                "Maxwell 3D, Maxwell 2D, Q3D, or Mechanical designs."
            )

    def __load_aedt_info(self):
        """Load info."""
        solids = self.aedt_application.modeler.get_objects_in_group("Solids")
        sheets = self.aedt_application.modeler.get_objects_in_group("Sheets")

        if not solids and not sheets:
            self.release_desktop()
            raise AEDTRuntimeError("No solids or sheets are defined in this design.")
        self.__aedt_solids = solids
        self.__aedt_sheets = sheets

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Upper frame of the extension GUI with widgets receiving user inputs
        input_frame = ttk.Frame(self.root, style="PyAEDT.TFrame", name="input_frame")
        input_frame.grid(row=0, column=0, columnspan=EXTENSION_NB_COLUMN)

        # Points entry - Defined first for geometry management of the tkinter.Listbox above it in GUI
        points_label = ttk.Label(input_frame, width=20, text="Number of Points:", style="PyAEDT.TLabel")
        points_label.grid(row=1, column=0, **DEFAULT_PADDING)
        points_entry = tkinter.Text(input_frame, width=30, height=1)
        points_entry.insert(tkinter.END, "1000")
        points_entry.grid(row=1, column=1, **DEFAULT_PADDING)
        points_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self._widgets["points_entry"] = points_entry

        # Listbox for objects and surfaces
        objects_label = ttk.Label(input_frame, width=20, text="Select Object or Surface:", style="PyAEDT.TLabel")
        objects_label.grid(row=0, column=0, **DEFAULT_PADDING)
        # List all objects and surfaces available
        entries = []
        if self.__aedt_solids:
            entries.append("--- Objects ---")
            entries.extend(self.__aedt_solids)
        if self.__aedt_sheets:
            entries.append("--- Surfaces ---")
            entries.extend(self.__aedt_sheets)
        # Create the ListBox inside a sub-frame to solve conflict between .grid and .pack methods in GUI
        objects_list_frame = tkinter.Frame(input_frame, width=20)
        objects_list_frame.grid(row=0, column=1, **DEFAULT_PADDING, sticky="ew")
        listbox_height = min(len(entries), 6)
        objects_list = tkinter.Listbox(
            objects_list_frame,
            selectmode=tkinter.MULTIPLE,
            justify=tkinter.CENTER,
            exportselection=False,
            height=listbox_height,
        )
        # Populate the Listbox
        objects_list.insert(tkinter.END, *entries)
        objects_list.configure(
            background=self.theme.light["widget_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        # Add vertical scrollbar if more than 6 elements are to be displayed
        if len(entries) > 6:
            scroll_bar = tkinter.Scrollbar(objects_list_frame, orient=tkinter.VERTICAL, command=objects_list.yview)
            objects_list.config(yscrollcommand=scroll_bar.set)
            scroll_bar.configure(background=self.theme.light["widget_bg"])
            scroll_bar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
            # Measure width of listbox with vertical scrollbar
            self.root.update()
            pix_width_listbox = points_entry.winfo_width() - scroll_bar.winfo_width()
        else:
            # Measure width of listbox without vertical scrollbar
            self.root.update()
            pix_width_listbox = points_entry.winfo_width()
        # Measure width of listbox entries to determine if horizontal scrollbar is needed and add it if required
        listbox_font = font.Font(font=objects_list.cget("font"))
        entries_pix_width = [listbox_font.measure(entry) for entry in entries]
        if max(entries_pix_width) >= pix_width_listbox:
            horiz_scroll_bar = tkinter.Scrollbar(
                objects_list_frame, orient=tkinter.HORIZONTAL, command=objects_list.xview
            )
            objects_list.config(xscrollcommand=horiz_scroll_bar.set)
            horiz_scroll_bar.configure(background=self.theme.light["widget_bg"])
            horiz_scroll_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        # Finally insert listbox - has to be done after both scrollbars
        objects_list.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self._widgets["objects_list"] = objects_list

        # Output file entry
        output_file_label = ttk.Label(input_frame, width=20, text="Output File:", style="PyAEDT.TLabel")
        output_file_label.grid(row=2, column=0, **DEFAULT_PADDING)
        output_file_entry = tkinter.Text(input_frame, width=30, height=1, wrap=tkinter.WORD)
        output_file_entry.grid(row=2, column=1, **DEFAULT_PADDING)
        output_file_entry.configure(
            bg=self.theme.light["pane_bg"],
            foreground=self.theme.light["text"],
            font=self.theme.default_font,
            state="disabled",
        )
        self._widgets["output_file_entry"] = output_file_entry

        def browse_output_location():
            """Define output file."""
            self._widgets["output_file_entry"].config(state="normal")
            # Clear content if an output file is already provided
            if self._widgets["output_file_entry"].get("1.0", tkinter.END).strip():
                self._widgets["output_file_entry"].delete("1.0", tkinter.END)

            filename = filedialog.asksaveasfilename(
                initialdir="/",
                title="Select output file",
                defaultextension=".pts",
                filetypes=(("Points file", ".pts"), ("all files", "*.*")),
            )
            self._widgets["output_file_entry"].insert(tkinter.END, filename)
            self._widgets["output_file_entry"].config(state="disabled")

        # Output file button
        output_file_button = ttk.Button(
            input_frame,
            text="Save as...",
            command=browse_output_location,
            style="PyAEDT.TButton",
            name="browse_output",
        )
        output_file_button.grid(row=2, column=2, **DEFAULT_PADDING)

        @graphics_required
        def preview():
            """Generate and visualize the point cloud."""
            import pyvista as pv

            selected_objects, num_points, _ = self.check_and_format_extension_data()
            try:
                # Generate point cloud
                point_cloud = generate_point_cloud(self.aedt_application, selected_objects, num_points)

                # Visualize the point cloud
                plotter = pv.Plotter()
                for file, actor in point_cloud.values():
                    plotter.add_mesh(actor, color="white", point_size=5, render_points_as_spheres=True)
                    Path.unlink(file)  # Delete .pts file
                plotter.show()

            except Exception as e:  # pragma: no cover
                self.release_desktop()
                raise AEDTRuntimeError(str(e))

        # Lower frame of the extension GUI with 3 buttons
        buttons_frame = ttk.Frame(self.root, style="PyAEDT.TFrame", name="buttons_frame")
        buttons_frame.grid(row=1, column=0, columnspan=EXTENSION_NB_COLUMN)

        # Preview button
        preview_button = ttk.Button(
            buttons_frame, text="Preview", command=preview, style="PyAEDT.TButton", name="preview"
        )
        preview_button.grid(row=0, column=0, **DEFAULT_PADDING)

        def callback(extension: PointsCloudExtension):
            """Collect extension data."""
            selected_objects, num_points, output_file = self.check_and_format_extension_data()

            extension.data = PointsCloudExtensionData(
                choice=selected_objects,
                points=num_points,
                output_file=output_file,
            )
            self.root.destroy()

        # Generate button
        generate_button = ttk.Button(
            buttons_frame,
            text="Generate",
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        generate_button.grid(row=0, column=1, **DEFAULT_PADDING)

        # Toggle theme button
        self.add_toggle_theme_button(buttons_frame, 0, 2)

    def check_and_format_extension_data(self):
        """Perform checks and formatting on extension input data."""
        selected_objects = [self._widgets["objects_list"].get(i) for i in self._widgets["objects_list"].curselection()]
        if not selected_objects or any(
            element in selected_objects for element in ["--- Objects ---", "--- Surfaces ---", ""]
        ):
            self.release_desktop()
            raise AEDTRuntimeError("Please select a valid object or surface.")

        points = self._widgets["points_entry"].get("1.0", tkinter.END).strip()
        num_points = int(points)
        if num_points <= 0:
            self.release_desktop()
            raise AEDTRuntimeError("Number of points must be greater than zero.")

        output_file = self._widgets["output_file_entry"].get("1.0", tkinter.END).strip()
        if not Path(output_file).parent.exists():
            self.release_desktop()
            raise AEDTRuntimeError("Path to the specified output file does not exist.")

        return selected_objects, num_points, output_file


def main(data: PointsCloudExtensionData):
    """Main function to run the point cloud generator extension."""
    # Check validity of data
    if not data.choice:
        raise AEDTRuntimeError("No assignment provided to the extension.")
    if not isinstance(data.choice, list):
        data.choice = [data.choice]

    if not isinstance(data.points, int) or data.points <= 0:
        raise AEDTRuntimeError("Number of points must be provided as an integer value and be greater than zero.")

    if not Path(data.output_file).parent.exists():
        raise AEDTRuntimeError("Path to the specified output file does not exist.")

    # Get pyaedt application
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

    # Check that assignment provided to the extension matches existing object/surface
    valid_assignments = []
    if aedtapp.modeler.get_objects_in_group("Solids"):
        valid_assignments.extend(aedtapp.modeler.get_objects_in_group("Solids"))
    if aedtapp.modeler.get_objects_in_group("Sheets"):
        valid_assignments.extend(aedtapp.modeler.get_objects_in_group("Sheets"))
    if not valid_assignments:
        raise AEDTRuntimeError("No solids or sheets are defined in this design.")
    if not all(item in valid_assignments for item in data.choice):
        raise AEDTRuntimeError("Provided assignment does not match existing object in design.")

    assignment = data.choice
    points = data.points
    output_file = data.output_file

    try:
        # Generate point cloud
        point_cloud = generate_point_cloud(aedtapp, assignment, points, output_file)
    except Exception as e:  # pragma: no cover
        app.release_desktop(False, False)
        raise AEDTRuntimeError(str(e))

    if aedtapp.design_type == "HFSS":
        for input_file, _ in point_cloud.values():
            _ = aedtapp.insert_near_field_points(input_file=input_file)

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)

    return str(point_cloud[list(point_cloud.keys())[0]][0])


def generate_point_cloud(aedtapp, selected_objects, num_points, output_file=None):
    """Generate point cloud from selected objects"""
    # Export the mesh (export_model_obj expects a file name with the .obj extension passed as a str)
    if not output_file or Path(output_file).is_dir():
        file_name = "_".join(selected_objects) + ".obj"
        export_path = Path(aedtapp.working_directory) if not output_file else Path(output_file)
        output_file = export_path / file_name
    else:
        output_file = Path(output_file).with_suffix(".obj")

    export_model = aedtapp.post.export_model_obj(assignment=selected_objects, export_path=str(output_file))

    if not export_model or not Path(export_model[0][0]).is_file():  # pragma: no cover
        raise Exception("Object could not be exported.")

    # Generate the point cloud
    geometry_file = export_model[0][0]  # The str path to the .obj file generated by the export_model_obj() method
    model_plotter = ModelPlotter()
    model_plotter.add_object(geometry_file)
    point_cloud = model_plotter.point_cloud(points=num_points)  # Generates the .pts file

    # Delete .mtl and .obj files generated by the export_model_obj() method
    Path.unlink(output_file)
    Path.unlink(output_file.with_suffix(".mtl"))

    return point_cloud


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
