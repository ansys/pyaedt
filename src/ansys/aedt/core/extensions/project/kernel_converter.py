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
import logging
import os
import os.path
import tkinter
from tkinter import filedialog
from tkinter import ttk

from ansys.aedt.core import Desktop
from ansys.aedt.core import Hfss
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Q3d
from ansys.aedt.core.application.design_solutions import solutions_types
from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.internal.filesystem import search_files

settings.use_grpc_api = True
settings.use_multi_desktop = True

on_ci = os.getenv("ON_CI", "false")

if on_ci.lower() == "true":
    settings.use_multi_desktop = False

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "password": "",
    "application": "HFSS",
    "solution": "Modal",
    "file_path": "",
}
EXTENSION_TITLE = "Kernel Converter"


@dataclass
class KernelConverterExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    password: str = EXTENSION_DEFAULT_ARGUMENTS["password"]
    application: str = EXTENSION_DEFAULT_ARGUMENTS["application"]
    solution: str = EXTENSION_DEFAULT_ARGUMENTS["solution"]
    file_path: str = EXTENSION_DEFAULT_ARGUMENTS["file_path"]


class KernelConverterExtension(ExtensionProjectCommon):
    """Extension for kernel converter in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=4,
            toggle_column=2,
        )

        # Tkinter widgets
        self.file_path_entry = None
        self.password_entry = None
        self.application_combo = None
        self.solution_combo = None

        # Add extension content
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # File path selection
        file_label = ttk.Label(
            self.root,
            text="Browse file or folder:",
            width=40,
            style="PyAEDT.TLabel",
        )
        file_label.grid(row=0, column=0, **DEFAULT_PADDING)

        file_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        file_frame.grid(row=0, column=1, sticky="ew", **DEFAULT_PADDING)

        self.file_path_entry = tkinter.Text(file_frame, width=30, height=1)
        self.file_path_entry.grid(row=0, column=0, padx=(0, 5))
        self.file_path_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        browse_button = ttk.Button(
            file_frame,
            text="...",
            width=5,
            command=self._browse_files,
            style="PyAEDT.TButton",
        )
        browse_button.grid(row=0, column=1)

        # Password entry
        password_label = ttk.Label(
            self.root,
            text="Password (Encrypted 3D Component Only):",
            width=40,
            style="PyAEDT.TLabel",
        )
        password_label.grid(row=1, column=0, **DEFAULT_PADDING)
        self.password_entry = tkinter.Entry(self.root, width=30, show="*")
        self.password_entry.grid(row=1, column=1, **DEFAULT_PADDING)

        # Application selection
        application_label = ttk.Label(
            self.root,
            text="Application (3D Component Only):",
            width=40,
            style="PyAEDT.TLabel",
        )
        application_label.grid(row=2, column=0, **DEFAULT_PADDING)
        self.application_combo = ttk.Combobox(
            self.root,
            width=30,
            style="PyAEDT.TCombobox",
            state="readonly",
        )
        self.application_combo["values"] = (
            "HFSS",
            "Q3D Extractor",
            "Maxwell 3D",
            "Icepak",
        )
        self.application_combo.current(0)
        self.application_combo.bind("<<ComboboxSelected>>", self._update_solutions)
        self.application_combo.grid(row=2, column=1, **DEFAULT_PADDING)

        # Solution selection
        solution_label = ttk.Label(
            self.root,
            text="Solution (3D Component Only):",
            width=40,
            style="PyAEDT.TLabel",
        )
        solution_label.grid(row=3, column=0, **DEFAULT_PADDING)
        self.solution_combo = ttk.Combobox(
            self.root,
            width=40,
            style="PyAEDT.TCombobox",
            state="readonly",
        )
        self.solution_combo["values"] = tuple(solutions_types["HFSS"].keys())
        self.solution_combo.current(0)
        self.solution_combo.grid(row=3, column=1, **DEFAULT_PADDING)

        def callback(extension: KernelConverterExtension):
            """Callback function for the convert button."""
            file_path = extension.file_path_entry.get("1.0", tkinter.END).strip()
            password = extension.password_entry.get()
            application = extension.application_combo.get()
            solution = extension.solution_combo.get()

            data = KernelConverterExtensionData(
                file_path=file_path,
                password=password,
                application=application,
                solution=solution,
            )
            extension.data = data
            extension.root.destroy()

        # Convert button
        convert_button = ttk.Button(
            self.root,
            text="Convert",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="convert",
        )
        convert_button.grid(row=4, column=0, **DEFAULT_PADDING)

    def _browse_files(self):
        """Browse for files or folders."""
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Electronics File",
            filetypes=(
                ("AEDT", ".aedt *.a3dcomp"),
                ("all files", "*.*"),
            ),
        )
        if filename:
            self.file_path_entry.delete("1.0", tkinter.END)
            self.file_path_entry.insert(tkinter.END, filename)

    def _update_solutions(self, event=None):
        """Update solution options based on selected application."""
        app_name = self.application_combo.get()
        if app_name in solutions_types:
            self.solution_combo["values"] = tuple(solutions_types[app_name].keys())
            self.solution_combo.current(0)


def _check_missing(input_object, output_object, file_path):
    """Check for missing objects after conversion."""
    from ansys.aedt.core.generic.file_utils import read_csv
    from ansys.aedt.core.generic.file_utils import write_csv

    if output_object.design_type not in [
        "HFSS",
        "Icepak",
        "Q3d",
        "2D Extractor",
        "Maxwell 3D",
        "Maxwell 2D",
        "Mechanical",
    ]:
        return

    object_list = input_object.modeler.object_names[::]
    new_object_list = output_object.modeler.object_names[::]
    un_classified_objects = output_object.modeler.unclassified_names[::]
    unclassified = [i for i in object_list if i not in new_object_list and i in un_classified_objects]
    disappeared = [i for i in object_list if i not in new_object_list and i not in un_classified_objects]
    list_of_suppressed = [["Design", "Object", "Operation"]]

    for obj_name in unclassified:
        if obj_name in output_object.modeler.object_names:
            continue
        hist = output_object.modeler[obj_name].history()
        for el_name, el in list(hist.children.items())[::-1]:
            if "Suppress Command" in el.props:
                el.props["Suppress Command"] = True
                list_of_suppressed.append([output_object.design_name, obj_name, el_name])
            if obj_name in output_object.modeler.object_names:
                break

    for obj_name in disappeared:
        input_object.export_3d_model(
            file_name=obj_name,
            file_format=".x_t",
            file_path=input_object.working_directory,
            assignment_to_export=[obj_name],
        )
        output_object.modeler.import_3d_cad(os.path.join(input_object.working_directory, obj_name + ".x_t"))
        list_of_suppressed.append([output_object.design_name, obj_name, "History"])

    if file_path.split(".")[1] == "a3dcomp":
        output_csv = os.path.join(file_path[:-8], "Import_Errors.csv")[::-1].replace("\\", "_", 1)[::-1]
    else:
        output_csv = os.path.join(file_path[:-5], "Import_Errors.csv")[::-1].replace("\\", "_", 1)[::-1]

    if os.path.exists(output_csv):
        data_read = read_csv(output_csv)
        list_of_suppressed = data_read + list_of_suppressed[1:]

    write_csv(output_csv, list_of_suppressed)
    print(f"Errors saved in {output_csv}")
    return output_csv, True


def _convert_3d_component(extension_args, output_desktop, input_desktop):
    """Convert 3D component files."""
    file_path = extension_args.file_path
    password = extension_args.password
    solution = extension_args.solution
    application = extension_args.application

    output_path = file_path[:-8] + f"_{VERSION}.a3dcomp"

    if os.path.exists(output_path):
        output_path = file_path[:-8] + generate_unique_name("_version", n=2) + ".a3dcomp"

    app = Hfss
    if application == "Icepak":
        app = Icepak
    elif application == "Maxwell 3D":
        app = Maxwell3d
    elif application == "Q3D Extractor":
        app = Q3d

    app1 = app(aedt_process_id=input_desktop.aedt_process_id, solution_type=solution)
    cmp = app1.modeler.insert_3d_component(file_path, password=password)
    app_comp = cmp.edit_definition(password=password)
    design_name = app_comp.design_name
    app_comp.oproject.CopyDesign(design_name)
    project_name2 = generate_unique_name("Proj_convert")
    output_app = app(
        aedt_process_id=output_desktop.aedt_process_id,
        solution_type=solution,
        project=project_name2,
    )

    output_app.oproject.Paste()
    output_app = get_pyaedt_app(desktop=output_desktop, project_name=project_name2, design_name=design_name)
    _check_missing(app_comp, output_app, file_path)
    output_app.modeler.create_3dcomponent(
        output_path,
        is_encrypted=True if password else False,
        allow_edit=True if password else False,
        edit_password=password,
        password_type="InternalPassword" if password else "UserSuppliedPassword",
        hide_contents=False,
    )
    try:
        output_desktop.DeleteProject(project_name2)
        print("Project successfully deleted")
    except Exception:  # pragma: no cover
        print("Error project was not closed")
    print(f"3D Component {output_path} has been created.")


def _convert_aedt(extension_args, output_desktop, input_desktop):
    """Convert AEDT project files."""
    file_path = extension_args.file_path

    file_path = str(file_path)
    a3d_component_path = str(file_path)
    output_path = a3d_component_path[:-5] + f"_{VERSION}.aedt"

    if os.path.exists(output_path):
        output_path = a3d_component_path[:-5] + generate_unique_name(f"_{VERSION}", n=2) + ".aedt"

    input_desktop.load_project(file_path)
    project_name = os.path.splitext(os.path.split(file_path)[-1])[0]
    oproject2 = output_desktop.odesktop.NewProject(output_path)
    project_name2 = os.path.splitext(os.path.split(output_path)[-1])[0]

    for design in input_desktop.design_list():
        app1 = get_pyaedt_app(desktop=input_desktop, project_name=project_name, design_name=design)
        app1.oproject.CopyDesign(app1.design_name)
        oproject2.Paste()
        output_app = get_pyaedt_app(desktop=output_desktop, project_name=project_name2, design_name=design)
        _check_missing(app1, output_app, file_path)
        output_app.save_project()
    input_desktop.odesktop.CloseProject(os.path.splitext(os.path.split(file_path)[-1])[0])


def main(data: KernelConverterExtensionData):  # pragma: no cover
    """Main function to run the kernel converter extension."""
    if not data.file_path:
        raise AEDTRuntimeError("No file path provided to the extension.")

    logger = logging.getLogger("Global")

    if os.path.isdir(data.file_path):
        files_path = search_files(data.file_path, "*.a3dcomp")
        files_path += search_files(data.file_path, "*.aedt")
    else:
        files_path = [data.file_path]

    # Remove the clipboard isolation env variable if present
    env_var_name = "ANS_USE_ISOLATED_CLIPBOARD"
    saved_env_var = None
    if env_var_name in os.environ:
        saved_env_var = os.environ[env_var_name]
        del os.environ[env_var_name]

    output_desktop = Desktop(
        new_desktop=True,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    input_desktop = Desktop(new_desktop=True, version=222, non_graphical=True)

    for file in files_path:
        try:
            data.file_path = file
            if data.file_path.endswith("a3dcomp"):
                _convert_3d_component(data, output_desktop, input_desktop)
            else:
                _convert_aedt(data, output_desktop, input_desktop)
        except Exception:
            logger.error(f"Failed to convert {file}")

    input_desktop.release_desktop()
    output_desktop.release_desktop(False, False)

    # Reset the clipboard isolation env variable if it was present
    if saved_env_var is not None:
        os.environ[env_var_name] = saved_env_var

    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: KernelConverterExtension = KernelConverterExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = KernelConverterExtensionData()
        for key, value in args.items():
            if hasattr(data, key):
                setattr(data, key, value)
        main(data)
