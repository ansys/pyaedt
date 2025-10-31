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
import json
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import numpy as np

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
from ansys.aedt.core.generic.file_utils import write_csv
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "points_file": "",
    "export_file": "",
    "export_option": "Ohmic loss",
    "objects_list": [],
    "solution_option": "",
}
EXTENSION_TITLE = "Fields Distribution"


@dataclass
class FieldsDistributionExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    points_file: str = EXTENSION_DEFAULT_ARGUMENTS["points_file"]
    export_file: str = EXTENSION_DEFAULT_ARGUMENTS["export_file"]
    export_option: str = EXTENSION_DEFAULT_ARGUMENTS["export_option"]
    objects_list: list = None
    solution_option: str = EXTENSION_DEFAULT_ARGUMENTS["solution_option"]

    def __post_init__(self):
        if self.objects_list is None:
            self.objects_list = EXTENSION_DEFAULT_ARGUMENTS["objects_list"].copy()


class FieldsDistributionExtension(ExtensionCommon):
    """Extension for fields distribution in Maxwell."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=6,
            toggle_column=1,
        )

        # Add private attributes and initialize them through __load_aedt_info
        self.__named_expressions = []
        self.__objects_list = []
        self.__solution_options = []
        self.__load_aedt_info()

        # Tkinter widgets will be stored in self._widgets

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

    def __get_design_type(self):
        """Get the design type of the active design."""
        try:
            app = ansys.aedt.core.Desktop(
                new_desktop=False,
                version=VERSION,
                port=PORT,
                aedt_process_id=AEDT_PROCESS_ID,
                student_version=IS_STUDENT,
            )
            active_design = app.active_design()
            design_type = active_design.GetDesignType()
            app.release_desktop(False, False)
            return design_type
        except Exception:
            return "Maxwell 3D"  # Default fallback

    def check_design_type(self):
        """Check if the active design is a Maxwell design."""
        if self.aedt_application.design_type not in ["Maxwell 2D", "Maxwell 3D"]:
            self.release_desktop()
            raise AEDTRuntimeError("Active design is not Maxwell 2D or 3D.")

    def __load_aedt_info(self):
        """Load Maxwell design info."""
        # Get named expressions for field quantities
        point = self.aedt_application.modeler.create_point([0, 0, 0])
        self.__named_expressions = self.aedt_application.post.available_report_quantities(
            report_category="Fields", context=point.name, quantities_category="Calculator Expressions"
        )

        # Load vector fields from JSON
        json_path = Path(__file__).resolve().parent / "vector_fields.json"
        with open(json_path, "r") as f:
            vector_fields = json.load(f)
        self.__named_expressions.extend(vector_fields[self.aedt_application.design_type])
        point.delete()

        # Get objects list
        self.__objects_list = list(self.aedt_application.modeler.objects_by_name.keys())
        if not self.__objects_list:
            self.release_desktop()
            raise AEDTRuntimeError("No objects are defined in this design.")

        # Get solution options
        self.__solution_options = self.aedt_application.existing_analysis_sweeps
        if not self.__solution_options:
            self.release_desktop()
            raise AEDTRuntimeError("No solved analysis sweeps found.")

    def _text_size(self, path, entry):
        """Adjust text widget size based on content."""
        text_length = len(path)
        height = 1
        if text_length > 50:
            height += 1
        entry.configure(height=height, width=max(40, text_length // 2))
        entry.delete("1.0", tkinter.END)
        entry.insert(tkinter.END, path)

    def _populate_listbox(self, frame, listbox, listbox_height, items_list):
        """Populate listbox with items and add scrollbar if needed."""
        listbox.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        if len(items_list) > 6:
            scroll_bar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL, command=listbox.yview)
            scroll_bar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
            listbox.config(yscrollcommand=scroll_bar.set, height=listbox_height)
        for item in items_list:
            listbox.insert(tkinter.END, item)

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Export options
        export_options_frame = tkinter.Frame(self.root, width=20)
        export_options_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        self._widgets["export_options_frame"] = export_options_frame

        export_options_label = ttk.Label(
            export_options_frame,
            text="Export options:",
            width=15,
            style="PyAEDT.TLabel",
            justify=tkinter.CENTER,
            anchor="w",
        )
        self._widgets["export_options_label"] = export_options_label
        export_options_label.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        listbox_height = min(len(self.__named_expressions), 6)
        export_options_lb = tkinter.Listbox(
            export_options_frame,
            selectmode=tkinter.SINGLE,
            height=listbox_height,
            justify=tkinter.CENTER,
            exportselection=False,
        )
        self._widgets["export_options_lb"] = export_options_lb
        self._populate_listbox(export_options_frame, export_options_lb, listbox_height, self.__named_expressions)

        # Objects list
        objects_list_frame = tkinter.Frame(self.root, width=20)
        objects_list_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        self._widgets["objects_list_frame"] = objects_list_frame

        objects_list_label = ttk.Label(
            objects_list_frame,
            text="Objects list:",
            width=15,
            style="PyAEDT.TLabel",
            justify=tkinter.CENTER,
            anchor="w",
        )
        self._widgets["objects_list_label"] = objects_list_label
        objects_list_label.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        objects_listbox_height = min(len(self.__objects_list), 6)
        objects_list_lb = tkinter.Listbox(
            objects_list_frame,
            selectmode=tkinter.MULTIPLE,
            justify=tkinter.CENTER,
            exportselection=False,
            height=objects_listbox_height,
        )
        self._widgets["objects_list_lb"] = objects_list_lb
        self._populate_listbox(objects_list_frame, objects_list_lb, objects_listbox_height, self.__objects_list)

        # Solution
        solution_frame = tkinter.Frame(self.root, width=20)
        solution_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        self._widgets["solution_frame"] = solution_frame

        solution_label = ttk.Label(
            solution_frame, text="Solution:", style="PyAEDT.TLabel", justify=tkinter.CENTER, anchor="w"
        )
        self._widgets["solution_label"] = solution_label
        solution_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

        solution_dropdown_var = tkinter.StringVar(solution_frame)
        solution_dropdown_var.set(self.__solution_options[0])
        self._widgets["solution_dropdown_var"] = solution_dropdown_var
        solution_dropdown = tkinter.OptionMenu(solution_frame, solution_dropdown_var, *self.__solution_options)
        solution_dropdown.config(bg="white", fg="black")
        solution_dropdown.pack(pady=20)
        self._widgets["solution_dropdown"] = solution_dropdown

        # Sample points file
        sample_points_frame = tkinter.Frame(self.root, width=20)
        sample_points_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        self._widgets["sample_points_frame"] = sample_points_frame

        sample_points_label = ttk.Label(
            sample_points_frame,
            text="Sample points file:",
            width=15,
            style="PyAEDT.TLabel",
            justify=tkinter.CENTER,
            anchor="w",
        )
        self._widgets["sample_points_label"] = sample_points_label
        sample_points_label.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        sample_points_entry = tkinter.Text(sample_points_frame, height=1, width=40, wrap=tkinter.WORD)
        sample_points_entry.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self._widgets["sample_points_entry"] = sample_points_entry

        # Points file button
        def show_points_popup():
            popup = tkinter.Toplevel(self.root)
            popup.title("Select an Option")

            tkinter.Label(popup, text="Choose an option:").pack(pady=10)

            option_var = tkinter.StringVar(value="Option 1")

            tkinter.Radiobutton(popup, text="Generate mesh grid", variable=option_var, value="Option 1").pack(
                anchor=tkinter.W
            )
            number_points_label = tkinter.Label(popup, text="Number of Points:")
            number_points_label.pack(anchor=tkinter.W, pady=5, padx=20)
            points_entry = tkinter.Text(popup, wrap=tkinter.WORD, width=20, height=1)
            points_entry.pack(pady=5, padx=20)
            tkinter.Radiobutton(popup, text="Import .pts file", variable=option_var, value="Option 2").pack(
                anchor=tkinter.W
            )

            def submit():
                if option_var.get() == "Option 1":
                    from ansys.aedt.core.extensions.common.points_cloud import PointsCloudExtensionData
                    from ansys.aedt.core.extensions.common.points_cloud import main as points_main

                    selected_objects = self._widgets["objects_list_lb"].curselection()
                    objects_list = [self._widgets["objects_list_lb"].get(i) for i in selected_objects]
                    points = points_entry.get("1.0", tkinter.END).strip()
                    try:
                        data = PointsCloudExtensionData(choice=objects_list, points=int(points))
                        pts_path = points_main(data)
                        self._text_size(pts_path, self._widgets["sample_points_entry"])
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to generate points: {str(e)}")
                else:
                    filename = filedialog.askopenfilename(
                        initialdir="/",
                        title="Select Points File",
                        filetypes=(("Points file", ".pts"), ("all files", "*.*")),
                    )
                    if filename:
                        self._text_size(filename, self._widgets["sample_points_entry"])
                popup.destroy()

            tkinter.Button(popup, text="OK", command=submit).pack(pady=10)

        export_points_button = ttk.Button(
            sample_points_frame, text="...", command=show_points_popup, width=10, style="PyAEDT.TButton"
        )
        export_points_button.pack(side=tkinter.RIGHT, padx=10)
        self._widgets["export_points_button"] = export_points_button

        # Export file
        export_file_frame = tkinter.Frame(self.root, width=20)
        export_file_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
        self._widgets["export_file_frame"] = export_file_frame

        export_file_label = ttk.Label(
            export_file_frame,
            text="Output file location:",
            width=20,
            style="PyAEDT.TLabel",
            justify=tkinter.CENTER,
            anchor="w",
        )
        self._widgets["export_file_label"] = export_file_label
        export_file_label.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        export_file_entry = tkinter.Text(export_file_frame, width=40, height=1, wrap=tkinter.WORD)
        export_file_entry.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self._widgets["export_file_entry"] = export_file_entry

        # Save as button
        def save_as_files():
            filename = filedialog.asksaveasfilename(
                initialdir="/",
                defaultextension="*.tab",
                filetypes=[
                    ("tab data file", "*.tab"),
                    ("csv data file", "*.csv"),
                    ("Numpy array", "*.npy"),
                ],
            )
            if filename:
                self._text_size(filename, self._widgets["export_file_entry"])

        save_as_button = ttk.Button(
            export_file_frame, text="Save as...", command=save_as_files, width=10, style="PyAEDT.TButton"
        )
        save_as_button.pack(side=tkinter.RIGHT, padx=10)
        self._widgets["save_as_button"] = save_as_button

        # Buttons frame
        buttons_frame = tkinter.Frame(self.root, width=20)
        buttons_frame.grid(row=5, column=0, pady=10, padx=15, sticky="ew")
        self._widgets["buttons_frame"] = buttons_frame

        def callback_export():
            points_file = self._widgets["sample_points_entry"].get("1.0", tkinter.END).strip()
            export_file = self._widgets["export_file_entry"].get("1.0", tkinter.END).strip()
            selected_export = self._widgets["export_options_lb"].curselection()
            if not selected_export:
                messagebox.showerror("Error", "Please select an export option.")
                return
            export_option = self._widgets["export_options_lb"].get(selected_export[0])
            selected_objects = self._widgets["objects_list_lb"].curselection()
            objects_list = [self._widgets["objects_list_lb"].get(i) for i in selected_objects]
            solution_option = self._widgets["solution_dropdown_var"].get()

            fields_data = FieldsDistributionExtensionData(
                points_file=points_file,
                export_file=export_file,
                export_option=export_option,
                objects_list=objects_list,
                solution_option=solution_option,
            )
            self.data = fields_data
            self.root.destroy()

        def callback_preview():
            selected_export = self._widgets["export_options_lb"].curselection()
            if not selected_export:
                messagebox.showerror("Error", "Please select an export option.")
                return
            export_option = self._widgets["export_options_lb"].get(selected_export[0])
            selected_objects = self._widgets["objects_list_lb"].curselection()
            objects_list = [self._widgets["objects_list_lb"].get(i) for i in selected_objects]
            solution_option = self._widgets["solution_dropdown_var"].get()

            try:
                plot = self.aedt_application.post.plot_field(
                    quantity=export_option,
                    assignment=objects_list,
                    plot_type="Surface",
                    setup=solution_option,
                    plot_cad_objs=False,
                    keep_plot_after_generation=False,
                    show_grid=False,
                )
                if not plot.fields:
                    setup_name = solution_option.split(":")[0].strip()
                    messagebox.showerror("Error", f"{setup_name} is not solved.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create preview: {str(e)}")

        export_button = ttk.Button(
            buttons_frame, text="Export", command=callback_export, width=10, style="PyAEDT.TButton"
        )
        preview_button = ttk.Button(
            buttons_frame, text="Preview plot", command=callback_preview, width=10, style="PyAEDT.TButton"
        )
        export_button.pack(side="left", expand=True, padx=5)
        preview_button.pack(side="left", expand=True, padx=5)
        self._widgets["export_button"] = export_button
        self._widgets["preview_button"] = preview_button


def main(data: FieldsDistributionExtensionData):
    """Main function to run the fields distribution extension."""
    if not data.export_file:
        raise AEDTRuntimeError("No export file specified.")

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

    if aedtapp.design_type not in ["Maxwell 2D", "Maxwell 3D"]:
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        raise AEDTRuntimeError("Active design is not Maxwell 2D or 3D.")

    points_file = data.points_file if data.points_file else None
    export_file = data.export_file
    export_option = data.export_option
    objects_list = data.objects_list
    solution_option = data.solution_option

    if not objects_list:
        assignment = "AllObjects"
    elif isinstance(objects_list, list) and len(objects_list) > 1:
        if len(aedtapp.modeler.user_lists) == 0:
            objects_list = aedtapp.modeler.create_object_list(objects_list, "ObjectList1")
        else:
            objects_list = aedtapp.modeler.create_object_list(
                objects_list, f"ObjectList{len(aedtapp.modeler.user_lists) + 1}"
            )
        assignment = objects_list.name
    else:
        assignment = objects_list[0]

    setup_name = solution_option.split(":")[0].strip()
    is_solved = [s.is_solved for s in aedtapp.setups if s.name == setup_name][0]
    if not is_solved:
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        raise AEDTRuntimeError("The setup is not solved. Please solve the setup before exporting the field data.")

    field_path = str(Path(export_file).with_suffix(".fld"))

    if not points_file:
        aedtapp.post.export_field_file(
            quantity=export_option,
            solution=solution_option,
            output_file=field_path,
            sample_points_file=points_file,
            assignment=assignment,
            objects_type="Surf",
        )
    else:
        aedtapp.post.export_field_file(
            quantity=export_option,
            solution=solution_option,
            output_file=field_path,
            sample_points_file=points_file,
        )

    with open(field_path, "r") as file:
        lines_to_skip = 2
        if points_file:
            lines_to_skip = 1
        for _ in range(lines_to_skip):
            file.readline()

        csv_data = []
        for line in file:
            tmp = line.strip().split(" ")
            tmp = [element.replace("\t\t", "") for element in tmp]
            if len(tmp) > 1:
                csv_data.append(tmp)

    if Path(export_file).suffix == ".csv" or Path(export_file).suffix == ".tab":
        output_file = Path(export_file).with_suffix(Path(export_file).suffix)
        write_csv(output_file, csv_data)
    elif Path(export_file).suffix == ".npy":
        output_file = Path(export_file).with_suffix(".npy")
        array = np.array(csv_data)
        np.save(output_file, array)

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = FieldsDistributionExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = FieldsDistributionExtensionData()
        for key, value in args.items():
            if hasattr(data, key):
                setattr(data, key, value)
        main(data)
