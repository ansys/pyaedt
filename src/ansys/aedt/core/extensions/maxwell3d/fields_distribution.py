# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from dataclasses import field
import json
import math
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Any
from typing import Protocol
from typing import cast

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
"""Port used by the extension."""
VERSION = get_aedt_version()
"""AEDT version used by the extension."""
AEDT_PROCESS_ID = get_process_id()
"""AEDT process identifier."""
IS_STUDENT = is_student()
"""Flag indicating whether the student version is used."""

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "points_file": "",
    "export_file": "",
    "export_option": "Ohmic loss",
    "objects_list": [],
    "solution_option": "",
    "field_type": "Fields",
    "time": "",
    "start_time": "0s",
}
"""Default arguments for the extension."""
EXTENSION_TITLE = "Fields Distribution"
"""Title displayed for the extension."""
LISTBOX_HEIGHT = 6
"""Number of visible rows in the quantity and objects lists."""
LABEL_WIDTH = 14
"""Width of the field labels, used to align the entries across sections."""
TEXT_WIDTH = 40
"""Width, in characters, of the file path text boxes."""
TEXT_MAX_LINES = 4
"""Maximum number of lines displayed by the file path text boxes."""


class MaxwellFieldsAppLike(Protocol):
    design_type: str
    solution_type: str
    _aedt_version: str
    modeler: Any
    post: Any
    existing_analysis_sweeps: list[str]
    setups: list[Any]


@dataclass
class FieldsDistributionExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    >>> data = FieldsDistributionExtensionData(
    ...     export_file="field_output.csv",
    ...     export_option="Ohmic loss",
    ...     solution_option="Setup1 : LastAdaptive",
    ... )

    """

    points_file: str = EXTENSION_DEFAULT_ARGUMENTS["points_file"]
    """File path for points."""
    export_file: str = EXTENSION_DEFAULT_ARGUMENTS["export_file"]
    """File path for export."""
    export_option: str = EXTENSION_DEFAULT_ARGUMENTS["export_option"]
    """Value for export option."""
    objects_list: list[str] | None = field(default_factory=list)
    """Value for objects list."""
    solution_option: str = EXTENSION_DEFAULT_ARGUMENTS["solution_option"]
    """Value for solution option."""
    field_type: str = EXTENSION_DEFAULT_ARGUMENTS["field_type"]
    """Field type as in AEDT Fields Calculator. Options are ``"Fields"`` and ``"Time Averaged Fields"``."""
    time: str = EXTENSION_DEFAULT_ARGUMENTS["time"]
    """Time, with units, to export transient fields at. For time averaged fields, it is the stop time."""
    start_time: str = EXTENSION_DEFAULT_ARGUMENTS["start_time"]
    """Start time, with units, of the averaging range. Used only for time averaged fields."""

    def __post_init__(self) -> None:
        if self.objects_list is None:
            self.objects_list = []


class FieldsDistributionExtension(ExtensionCommon):
    """Extension for fields distribution in Maxwell.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtension
    >>> extension = FieldsDistributionExtension(withdraw=True)

    """

    def __init__(self, withdraw: bool = False) -> None:
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=3,
            toggle_column=1,
        )

        # Add private attributes and initialize them through __load_aedt_info
        self.__is_transient = False
        self.__time_averaged_available = False
        self.__named_expressions = []
        self.__objects_list = []
        self.__solution_options = []
        self.__load_aedt_info()

        # Tkinter widgets will be stored in self._widgets

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()
        # Re-apply the theme so the widgets created above (listboxes, text boxes) are themed too
        self.apply_theme(self.theme_color)

    @property
    def fields_data(self) -> FieldsDistributionExtensionData:
        return cast(FieldsDistributionExtensionData, self.data)

    @property
    def maxwell_app(self) -> MaxwellFieldsAppLike:
        return cast(MaxwellFieldsAppLike, self.aedt_application)

    def __get_design_type(self) -> str:
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

    def check_design_type(self) -> None:
        """Check if the active design is a Maxwell design.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtension
        >>> extension = FieldsDistributionExtension(withdraw=True)
        >>> extension.check_design_type()

        """
        if self.aedt_application.design_type not in ["Maxwell 2D", "Maxwell 3D"]:
            self.release_desktop()
            raise AEDTRuntimeError("Active design is not Maxwell 2D or 3D.")

    def __load_aedt_info(self) -> None:
        """Load Maxwell design info."""
        self.__is_transient = "Transient" in str(self.maxwell_app.solution_type)
        # Fields Calculator expressions split by field type are available from AEDT 2026.1
        self.__time_averaged_available = self.__is_transient and self.maxwell_app._aedt_version >= "2026.1"
        # Get named expressions for field quantities
        # make it backward compatible by implementing a check on AEDT version
        if self.maxwell_app._aedt_version < "2026.1":
            point = self.maxwell_app.modeler.create_point([0, 0, 0])
            self.__named_expressions = self.maxwell_app.post.available_report_quantities(
                report_category="Fields", context=point.name, quantities_category="Calculator Expressions"
            )
            # Load vector fields from JSON
            json_path = Path(__file__).resolve().parent / "vector_fields.json"
            with open(json_path, "r") as f:
                vector_fields = json.load(f)
            self.__named_expressions.extend(vector_fields[self.maxwell_app.design_type])
            point.delete()
        elif self.__time_averaged_available:
            self.__named_expressions = list(
                self.maxwell_app.post.fields_calculator.get_expressions(field_type="Fields")
            )
        else:
            self.__named_expressions = self.maxwell_app.post.fields_calculator.get_expressions()

        # Get objects list
        self.__objects_list = list(self.maxwell_app.modeler.objects_by_name.keys())
        if not self.__objects_list:
            self.release_desktop()
            raise AEDTRuntimeError("No objects are defined in this design.")

        # Get solution options
        self.__solution_options = self.maxwell_app.existing_analysis_sweeps
        if not self.__solution_options:
            self.release_desktop()
            raise AEDTRuntimeError("No solved analysis sweeps found.")

    def _text_size(self, path: str, entry: tkinter.Text) -> None:
        """Adjust the text widget height so that the whole path is visible."""
        height = min(TEXT_MAX_LINES, max(1, math.ceil(len(path) / TEXT_WIDTH)))
        entry.configure(height=height)
        entry.delete("1.0", tkinter.END)
        entry.insert(tkinter.END, path)

    def _populate_listbox(
        self, frame: tkinter.Frame, listbox: tkinter.Listbox, listbox_height: int, items_list: list[str]
    ) -> None:
        """Populate listbox with items and add scrollbar if needed."""
        listbox.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        if len(items_list) > 6:
            scroll_bar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL, command=listbox.yview)
            scroll_bar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
            listbox.config(yscrollcommand=scroll_bar.set, height=listbox_height)
        for item in items_list:
            listbox.insert(tkinter.END, item)

    def _toggle_time_averaged(self) -> None:
        """Update quantities and time entries when the time averaged option changes."""
        time_averaged_var = cast(tkinter.BooleanVar, self._widgets["time_averaged_var"])
        export_options_lb = cast(tkinter.Listbox, self._widgets["export_options_lb"])
        start_time_label = cast(ttk.Label, self._widgets["start_time_label"])
        start_time_entry = cast(ttk.Entry, self._widgets["start_time_entry"])
        time_label = cast(ttk.Label, self._widgets["time_label"])

        field_type = "Time Averaged Fields" if time_averaged_var.get() else "Fields"
        expressions = list(self.maxwell_app.post.fields_calculator.get_expressions(field_type=field_type))
        export_options_lb.delete(0, tkinter.END)
        for item in expressions:
            export_options_lb.insert(tkinter.END, item)

        if time_averaged_var.get():
            start_time_label.grid()
            start_time_entry.grid()
            time_label.configure(text="Stop time:")
        else:
            start_time_label.grid_remove()
            start_time_entry.grid_remove()
            time_label.configure(text="Time:")

    def _get_time_settings(self) -> tuple[str, str, str] | None:
        """Get field type, time, and start time from the UI.

        Returns
        -------
        tuple or None
            Field type, time, and start time. ``None`` if the input is not valid.
        """
        if not self.__is_transient:
            return "Fields", "", EXTENSION_DEFAULT_ARGUMENTS["start_time"]
        time = cast(ttk.Entry, self._widgets["time_entry"]).get().strip()
        start_time = EXTENSION_DEFAULT_ARGUMENTS["start_time"]
        field_type = "Fields"
        time_averaged_var = cast(tkinter.BooleanVar | None, self._widgets.get("time_averaged_var"))
        if time_averaged_var is not None and time_averaged_var.get():
            field_type = "Time Averaged Fields"
            start_time = cast(ttk.Entry, self._widgets["start_time_entry"]).get().strip()
            if not time or not start_time:
                messagebox.showerror("Error", "Please specify the start and stop times for time averaged fields.")
                return None
        return field_type, time, start_time

    def add_extension_content(self) -> None:
        """Add custom content to the extension UI.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtension
        >>> extension = FieldsDistributionExtension(withdraw=True)
        >>> extension.add_extension_content()

        """
        self.root.columnconfigure(0, weight=1)

        # Quantity and objects selection, side by side
        selection_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        selection_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew")
        selection_frame.columnconfigure(0, weight=1, uniform="selection")
        selection_frame.columnconfigure(1, weight=1, uniform="selection")
        self._widgets["selection_frame"] = selection_frame

        export_options_frame = ttk.LabelFrame(selection_frame, text="Quantity", style="PyAEDT.TLabelframe")
        export_options_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        self._widgets["export_options_frame"] = export_options_frame

        export_options_lb = tkinter.Listbox(
            export_options_frame,
            selectmode=tkinter.SINGLE,
            height=LISTBOX_HEIGHT,
            exportselection=False,
            activestyle="none",
        )
        self._widgets["export_options_lb"] = export_options_lb
        self._populate_listbox(export_options_frame, export_options_lb, LISTBOX_HEIGHT, self.__named_expressions)

        objects_list_frame = ttk.LabelFrame(selection_frame, text="Objects", style="PyAEDT.TLabelframe")
        objects_list_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        self._widgets["objects_list_frame"] = objects_list_frame

        objects_list_lb = tkinter.Listbox(
            objects_list_frame,
            selectmode=tkinter.MULTIPLE,
            height=LISTBOX_HEIGHT,
            exportselection=False,
            activestyle="none",
        )
        self._widgets["objects_list_lb"] = objects_list_lb
        self._populate_listbox(objects_list_frame, objects_list_lb, LISTBOX_HEIGHT, self.__objects_list)

        # Solution and transient settings
        solution_frame = ttk.LabelFrame(self.root, text="Solution", style="PyAEDT.TLabelframe")
        solution_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        solution_frame.columnconfigure(1, weight=1)
        self._widgets["solution_frame"] = solution_frame

        solution_label = ttk.Label(solution_frame, text="Setup:", width=LABEL_WIDTH, style="PyAEDT.TLabel")
        solution_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._widgets["solution_label"] = solution_label

        solution_dropdown_var = tkinter.StringVar(solution_frame, value=self.__solution_options[0])
        self._widgets["solution_dropdown_var"] = solution_dropdown_var
        solution_dropdown = ttk.Combobox(
            solution_frame,
            textvariable=solution_dropdown_var,
            values=self.__solution_options,
            state="readonly",
            style="PyAEDT.TCombobox",
        )
        solution_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self._widgets["solution_dropdown"] = solution_dropdown

        if self.__is_transient:
            transient_frame = ttk.Frame(solution_frame, style="PyAEDT.TFrame")
            transient_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            self._widgets["transient_frame"] = transient_frame

            if self.__time_averaged_available:
                time_averaged_var = tkinter.BooleanVar(transient_frame, value=False)
                self._widgets["time_averaged_var"] = time_averaged_var
                time_averaged_check = ttk.Checkbutton(
                    transient_frame,
                    text="Time averaged fields",
                    variable=time_averaged_var,
                    command=self._toggle_time_averaged,
                    style="PyAEDT.TCheckbutton",
                )
                time_averaged_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
                self._widgets["time_averaged_check"] = time_averaged_check

                start_time_label = ttk.Label(
                    transient_frame, text="Start time:", width=LABEL_WIDTH, style="PyAEDT.TLabel"
                )
                start_time_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
                self._widgets["start_time_label"] = start_time_label
                start_time_entry = ttk.Entry(transient_frame, width=20, style="PyAEDT.TEntry")
                start_time_entry.insert(0, EXTENSION_DEFAULT_ARGUMENTS["start_time"])
                start_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
                self._widgets["start_time_entry"] = start_time_entry
                start_time_label.grid_remove()
                start_time_entry.grid_remove()

            time_label = ttk.Label(transient_frame, text="Time:", width=LABEL_WIDTH, style="PyAEDT.TLabel")
            time_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self._widgets["time_label"] = time_label
            time_entry = ttk.Entry(transient_frame, width=20, style="PyAEDT.TEntry")
            time_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self._widgets["time_entry"] = time_entry

        # Input and output files
        files_frame = ttk.LabelFrame(self.root, text="Files", style="PyAEDT.TLabelframe")
        files_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        files_frame.columnconfigure(1, weight=1)
        self._widgets["files_frame"] = files_frame

        sample_points_label = ttk.Label(files_frame, text="Sample points:", width=LABEL_WIDTH, style="PyAEDT.TLabel")
        sample_points_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._widgets["sample_points_label"] = sample_points_label

        sample_points_entry = tkinter.Text(files_frame, height=1, width=TEXT_WIDTH, wrap=tkinter.CHAR)
        sample_points_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self._widgets["sample_points_entry"] = sample_points_entry

        # Points file button
        def browse_points_file() -> None:
            sample_points_entry = cast(tkinter.Text | None, self._widgets.get("sample_points_entry"))
            if sample_points_entry is None:
                raise RuntimeError("Fields Distribution widgets are not initialized.")
            filename = filedialog.askopenfilename(
                initialdir="/",
                title="Select Points File",
                filetypes=[("Points file", "*.pts")],
            )
            if filename:
                self._text_size(filename, sample_points_entry)

        export_points_button = ttk.Button(
            files_frame, text="...", command=browse_points_file, width=10, style="PyAEDT.TButton"
        )
        export_points_button.grid(row=0, column=2, padx=5, pady=5)
        self._widgets["export_points_button"] = export_points_button

        export_file_label = ttk.Label(files_frame, text="Output file:", width=LABEL_WIDTH, style="PyAEDT.TLabel")
        export_file_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self._widgets["export_file_label"] = export_file_label

        export_file_entry = tkinter.Text(files_frame, width=TEXT_WIDTH, height=1, wrap=tkinter.CHAR)
        export_file_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self._widgets["export_file_entry"] = export_file_entry

        # Save as button
        def save_as_files() -> None:
            export_file_entry = cast(tkinter.Text | None, self._widgets.get("export_file_entry"))
            if export_file_entry is None:
                raise RuntimeError("Fields Distribution widgets are not initialized.")
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
                self._text_size(filename, export_file_entry)

        save_as_button = ttk.Button(
            files_frame, text="Save as...", command=save_as_files, width=10, style="PyAEDT.TButton"
        )
        save_as_button.grid(row=1, column=2, padx=5, pady=5)
        self._widgets["save_as_button"] = save_as_button

        # Action buttons, next to the theme toggle button
        buttons_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self._widgets["buttons_frame"] = buttons_frame

        def callback_export() -> None:
            sample_points_entry = cast(tkinter.Text | None, self._widgets.get("sample_points_entry"))
            export_file_entry = cast(tkinter.Text | None, self._widgets.get("export_file_entry"))
            export_options_lb = cast(tkinter.Listbox | None, self._widgets.get("export_options_lb"))
            objects_list_lb = cast(tkinter.Listbox | None, self._widgets.get("objects_list_lb"))
            solution_dropdown_var = cast(tkinter.StringVar | None, self._widgets.get("solution_dropdown_var"))
            if (
                sample_points_entry is None
                or export_file_entry is None
                or export_options_lb is None
                or objects_list_lb is None
                or solution_dropdown_var is None
            ):
                raise RuntimeError("Fields Distribution widgets are not initialized.")
            points_file = sample_points_entry.get("1.0", tkinter.END).strip()
            export_file = export_file_entry.get("1.0", tkinter.END).strip()
            selected_export = export_options_lb.curselection()
            if not selected_export:
                messagebox.showerror("Error", "Please select an export option.")
                return
            export_option = cast(str, export_options_lb.get(selected_export[0]))
            selected_objects = objects_list_lb.curselection()
            objects_list = [cast(str, objects_list_lb.get(i)) for i in selected_objects]
            solution_option = solution_dropdown_var.get()
            time_settings = self._get_time_settings()
            if time_settings is None:
                return
            field_type, time, start_time = time_settings

            fields_data = FieldsDistributionExtensionData(
                points_file=points_file,
                export_file=export_file,
                export_option=export_option,
                objects_list=objects_list,
                solution_option=solution_option,
                field_type=field_type,
                time=time,
                start_time=start_time,
            )
            self.data = fields_data
            self.root.destroy()

        export_button = ttk.Button(
            buttons_frame, text="Export", command=callback_export, width=12, style="PyAEDT.TButton"
        )
        export_button.pack(side="left")
        self._widgets["export_button"] = export_button


def main(data: FieldsDistributionExtensionData) -> bool:
    """Main function to run the fields distribution extension.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    >>> from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main
    >>> data = FieldsDistributionExtensionData(
    ...     export_file="field_output.csv",
    ...     export_option="Ohmic loss",
    ...     solution_option="Setup1 : LastAdaptive",
    ... )
    >>> main(data)

    """
    if not data.export_file:
        raise AEDTRuntimeError("No export file specified.")
    if data.field_type == "Time Averaged Fields" and not data.time:
        raise AEDTRuntimeError("No stop time specified for time averaged fields.")

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

    aedtapp = cast(MaxwellFieldsAppLike, get_pyaedt_app(project_name, design_name))

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
        list_name = f"ObjectList{len(aedtapp.modeler.user_lists) + 1}"
        if VERSION < "2026.1":
            selection = aedtapp.modeler.create_object_list(assignment=objects_list, name=list_name)
        else:
            selection = aedtapp.modeler.create_named_selection(name=list_name, assignment=objects_list)
        assignment = selection.name
    else:
        assignment = objects_list[0]

    setup_name = solution_option.split(":")[0].strip()
    # setup.is_solved is not reliable for transient designs: the export raises if fields are not available.
    is_transient = "Transient" in str(aedtapp.solution_type)
    is_solved = is_transient or [s.is_solved for s in aedtapp.setups if s.name == setup_name][0]
    if not is_solved:
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        raise AEDTRuntimeError("The setup is not solved. Please solve the setup before exporting the field data.")

    field_path = str(Path(export_file).with_suffix(".fld"))

    if data.time:
        if not points_file:
            aedtapp.post.export_transient_field_file(
                quantity=export_option,
                time=data.time,
                solution=solution_option,
                output_file=field_path,
                assignment=assignment,
                objects_type="Surf",
                field_type=data.field_type,
                start_time=data.start_time,
            )
        else:
            aedtapp.post.export_transient_field_file_on_points(
                quantity=export_option,
                time=data.time,
                sample_points=points_file,
                solution=solution_option,
                output_file=field_path,
                field_type=data.field_type,
                start_time=data.start_time,
            )
    elif not points_file:
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

    output_file = Path(export_file)
    match output_file.suffix:
        case ".csv":
            write_csv(str(output_file), csv_data)
        case ".tab":
            write_csv(str(output_file), csv_data, delimiter="\t")
        case ".npy":
            array = np.array(csv_data)
            np.save(output_file, array)
        case _:
            raise AEDTRuntimeError(f"{output_file.suffix} is not supported.")

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
            main(extension.fields_data)

    else:
        data = FieldsDistributionExtensionData()
        for key, value in args.items():
            if hasattr(data, key):
                setattr(data, key, value)
        main(data)
