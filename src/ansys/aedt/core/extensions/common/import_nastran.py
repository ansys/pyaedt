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
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.syslib.nastran_import import nastran_to_stl

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "file_path": "",
    "lightweight": False,
    "decimate": 0.0,
    "planar": True,
    "remove_multiple_connections": False,
}
EXTENSION_TITLE = "Import Nastran"


@dataclass
class ImportNastranExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    file_path: str = EXTENSION_DEFAULT_ARGUMENTS["file_path"]
    lightweight: bool = EXTENSION_DEFAULT_ARGUMENTS["lightweight"]
    decimate: float = EXTENSION_DEFAULT_ARGUMENTS["decimate"]
    planar: bool = EXTENSION_DEFAULT_ARGUMENTS["planar"]
    remove_multiple_connections: bool = EXTENSION_DEFAULT_ARGUMENTS["remove_multiple_connections"]


class ImportNastranExtension(ExtensionProjectCommon):
    """Extension for importing Nastran or STL files in AEDT."""

    def __init__(self, withdraw: bool = False):
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=5,
            toggle_column=2,
        )

        # Initialize UI variables
        self.__file_path_text = None
        self.__decimation_text = None
        self.__lightweight_var = None
        self.__planar_var = None
        self.__remove_multiple_connections_var = None

        # Add extension content
        self.add_extension_content()

    def check_design_type(self):
        """Check if the design type is HFSS, Icepak, HFSS 3D, Maxwell 3D, Q3D, Mechanical"""
        if self.aedt_application.design_type not in ["HFSS", "Icepak", "HFSS 3D", "Maxwell 3D", "Q3D", "Mechanical"]:
            self.release_desktop()
            raise AEDTRuntimeError(
                "This extension only works with HFSS, Icepak, HFSS 3D, Maxwell 3D, Q3D, or Mechanical designs."
            )

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # File path selection
        ttk.Label(self.root, text="Browse file:", style="PyAEDT.TLabel").grid(row=0, column=0, padx=15, pady=10)

        self.__file_path_text = tkinter.Text(self.root, width=40, height=1, name="file_path_text")
        self.__file_path_text.grid(row=0, column=1, pady=10, padx=5)

        ttk.Button(
            self.root,
            text="...",
            width=10,
            command=self.__browse_files,
            style="PyAEDT.TButton",
            name="browse_button",
        ).grid(row=0, column=2, pady=10)

        # Decimation factor
        ttk.Label(
            self.root,
            text="Decimation factor (0-0.9):",
            style="PyAEDT.TLabel",
        ).grid(row=1, column=0, padx=15, pady=10)

        self.__decimation_text = tkinter.Text(self.root, width=20, height=1, name="decimation_text")
        self.__decimation_text.insert(tkinter.END, "0.0")
        self.__decimation_text.grid(row=1, column=1, pady=10, padx=5)

        # Lightweight import option
        ttk.Label(
            self.root,
            text="Import as lightweight:",
            style="PyAEDT.TLabel",
        ).grid(row=2, column=0, padx=15, pady=10)

        self.__lightweight_var = tkinter.IntVar(self.root, name="var_lightweight")
        ttk.Checkbutton(
            self.root,
            variable=self.__lightweight_var,
            style="PyAEDT.TCheckbutton",
            name="check_lightweight",
        ).grid(row=2, column=1, pady=10, padx=5)

        # Planar merge option
        ttk.Label(
            self.root,
            text="Enable planar merge:",
            style="PyAEDT.TLabel",
        ).grid(row=3, column=0, padx=15, pady=10)

        self.__planar_var = tkinter.IntVar(self.root, value=1, name="var_planar")
        ttk.Checkbutton(
            self.root,
            variable=self.__planar_var,
            style="PyAEDT.TCheckbutton",
            name="check_planar_merge",
        ).grid(row=3, column=1, pady=10, padx=5)

        # Remove multiple connections option
        ttk.Label(
            self.root,
            text="Remove multiple connections:",
            style="PyAEDT.TLabel",
        ).grid(row=4, column=0, padx=15, pady=10)

        self.__remove_multiple_connections_var = tkinter.IntVar(self.root, name="var_remove_multiple_connections")
        ttk.Checkbutton(
            self.root,
            variable=self.__remove_multiple_connections_var,
            style="PyAEDT.TCheckbutton",
            name="check_remove_multiple_connections",
        ).grid(row=4, column=1, pady=10, padx=5)

        # Preview button
        ttk.Button(
            self.root,
            text="Preview",
            width=40,
            command=self.__preview,
            style="PyAEDT.TButton",
            name="preview_button",
        ).grid(row=5, column=0, pady=10, padx=10)

        # Import button
        ttk.Button(
            self.root,
            text="Import",
            width=40,
            command=self.__import_callback,
            style="PyAEDT.TButton",
            name="import_button",
        ).grid(row=5, column=1, pady=10, padx=10)

    def __browse_files(self):
        """Open the file dialog to select Nastran or STL file."""
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Nastran or STL File",
            filetypes=(
                ("Nastran", "*.nas"),
                ("STL", "*.stl"),
                ("all files", "*.*"),
            ),
        )
        if filename:
            self.__file_path_text.delete("1.0", tkinter.END)
            self.__file_path_text.insert(tkinter.END, filename)

    def __preview(self):
        """Preview the geometry file."""
        file_path_ui = self.__file_path_text.get("1.0", tkinter.END).strip()

        if not file_path_ui:
            raise ValueError("Please select a valid file.")

        if not Path(file_path_ui).is_file():
            raise FileNotFoundError(f"File ({file_path_ui}) not found")

        decimate_ui = float(self.__decimation_text.get("1.0", tkinter.END).strip())

        if file_path_ui.endswith(".nas"):
            nastran_to_stl(file_path_ui, decimation=decimate_ui, preview=True)
        else:
            from ansys.aedt.core.visualization.advanced.misc import simplify_and_preview_stl

            simplify_and_preview_stl(file_path_ui, decimation=decimate_ui, preview=True)

    def __import_callback(self):
        """Callback for import button."""
        file_path = self.__file_path_text.get("1.0", tkinter.END).strip()
        lightweight_val = self.__lightweight_var.get() == 1
        planar_val = self.__planar_var.get() == 1
        remove_multiple_connections_val = self.__remove_multiple_connections_var.get() == 1

        # Validation
        if not file_path:
            raise ValueError("Please select a file path.")

        if not Path(file_path).is_file():
            raise FileNotFoundError(f"File ({file_path}) not found")

        decimate_val = float(self.__decimation_text.get("1.0", tkinter.END).strip())

        if decimate_val < 0 or decimate_val >= 1:
            raise ValueError("Decimation factor must be between 0 and 0.9")

        # Create data object and close UI
        self.data = ImportNastranExtensionData(
            file_path=file_path,
            decimate=decimate_val,
            lightweight=lightweight_val,
            planar=planar_val,
            remove_multiple_connections=remove_multiple_connections_val,
        )
        self.root.destroy()


def main(data: ImportNastranExtensionData):
    """Main function to run the import nastran extension."""
    # Input validation
    if not data.file_path:
        raise AEDTRuntimeError("No file path provided.")

    if data.decimate < 0 or data.decimate >= 1:
        raise AEDTRuntimeError("Decimation factor must be between 0 and 0.9")

    file_path = Path(data.file_path)
    if not file_path.is_file():
        raise AEDTRuntimeError(f"File ({data.file_path}) not found")

    # Connect to AEDT
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    if not active_project:
        raise AEDTRuntimeError("No active project found.")

    active_design = app.active_design()
    if not active_design:
        raise AEDTRuntimeError("No active design found.")

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    # Import geometry based on file type
    if file_path.suffix == ".nas":
        aedtapp.modeler.import_nastran(
            str(file_path),
            import_as_light_weight=data.lightweight,
            decimation=data.decimate,
            enable_planar_merge=str(data.planar),
            remove_multiple_connections=data.remove_multiple_connections,
        )
    else:
        from ansys.aedt.core.visualization.advanced.misc import simplify_and_preview_stl

        outfile = simplify_and_preview_stl(str(file_path), decimation=data.decimate)
        aedtapp.modeler.import_3d_cad(
            outfile,
            healing=False,
            create_lightweigth_part=data.lightweight,
            merge_planar_faces=data.planar,
        )

    app.logger.info("Geometry imported correctly.")

    # Clean up
    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = ImportNastranExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = ImportNastranExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
