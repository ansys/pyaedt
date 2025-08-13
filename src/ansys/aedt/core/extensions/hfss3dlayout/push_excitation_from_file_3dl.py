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
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"choice": "", "file_path": ""}
EXTENSION_TITLE = "Push Excitation From File - 3D Layout"


@dataclass
class PushExcitation3DLayoutExtensionData(ExtensionCommonData):
    """Data class for Push Excitation 3D Layout extension."""

    choice: str = ""
    file_path: str = ""


class PushExcitation3DLayoutExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for push excitation from file in HFSS 3D Layout."""

    def __init__(self, withdraw: bool = False):
        """Initialize the extension."""
        # Initialize the common extension class
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=3,
            toggle_column=1,
        )

        # Initialize data
        self.data = PushExcitation3DLayoutExtensionData()

        self.__load_aedt_info()
        self.add_extension_content()

        if not withdraw:
            self.root.mainloop()

    def __load_aedt_info(self):
        """Load AEDT information and validate the design."""
        if not self.aedt_application:
            raise AEDTRuntimeError("No active AEDT design found.")

        if self.aedt_application.design_type != "HFSS 3D Layout Design":
            raise AEDTRuntimeError("This extension only works with HFSS 3D Layout designs.")

        # Get excitation names
        excitation_names = self.aedt_application.excitation_names
        if not excitation_names:
            raise AEDTRuntimeError("No excitations found in the design.")

        self.excitation_names = excitation_names

    def add_extension_content(self):
        """Add content to the extension UI."""
        # Port selection
        self.port_label = ttk.Label(self.root, text="Choose a port:", style="PyAEDT.TLabel")
        self.port_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        self.port_combo = ttk.Combobox(self.root, width=30, style="PyAEDT.TCombobox")
        self.port_combo["values"] = self.excitation_names
        if self.excitation_names:
            self.port_combo.current(0)
        self.port_combo.grid(row=0, column=1, pady=10, padx=5, sticky="ew")

        # File path selection
        self.file_label = ttk.Label(self.root, text="Browse file:", style="PyAEDT.TLabel")
        self.file_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.file_entry = tkinter.Text(self.root, width=50, height=1)
        self.file_entry.grid(row=1, column=1, pady=10, padx=5, sticky="ew")

        self.file_browse_button = ttk.Button(
            self.root,
            text="...",
            width=10,
            command=self.browse_files,
            style="PyAEDT.TButton",
        )
        self.file_browse_button.grid(row=1, column=2, pady=10, padx=10)

        # Generate button
        def callback(extension: PushExcitation3DLayoutExtension):
            choice = extension.port_combo.get()
            file_path_text = extension.file_entry.get("1.0", tkinter.END).strip()

            if not choice:
                extension.release_desktop()
                raise AEDTRuntimeError("Please select a port.")

            if not file_path_text or not Path(file_path_text).is_file():
                extension.release_desktop()
                raise AEDTRuntimeError("Please select a valid file.")

            push_excitation_data = PushExcitation3DLayoutExtensionData(choice=choice, file_path=file_path_text)
            extension.data = push_excitation_data
            self.root.destroy()

        self.generate_button = ttk.Button(
            self.root,
            text="Push Excitation",
            width=40,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        self.generate_button.grid(row=2, column=1, pady=20)

        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)

    def browse_files(self):
        """Open file dialog to browse for excitation files."""
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Transient File",
            filetypes=(
                ("Transient curve", "*.csv*"),
                ("all files", "*.*"),
            ),
        )
        if filename:
            self.file_entry.delete("1.0", tkinter.END)
            self.file_entry.insert(tkinter.END, filename)


def main(data: PushExcitation3DLayoutExtensionData):
    """Main function to run the push excitation extension."""
    if not data.choice:
        raise AEDTRuntimeError("No excitation selected.")

    if not data.file_path:
        raise AEDTRuntimeError("No file path provided.")

    file_path = Path(data.file_path)
    if not file_path.is_file():
        raise AEDTRuntimeError("File does not exist.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    if not active_project:
        raise AEDTRuntimeError("No active project found.")

    if not active_design:
        raise AEDTRuntimeError("No active design found.")

    project_name = active_project.GetName()

    if active_design.GetDesignType() not in ["HFSS 3D Layout Design"]:
        raise AEDTRuntimeError("This extension only works with HFSS 3D Layout designs.")

    design_name = active_design.GetName().split(";")[1]

    hfss_3dl = get_pyaedt_app(project_name, design_name)

    if hfss_3dl.design_type != "HFSS 3D Layout Design":
        raise AEDTRuntimeError("This extension only works with HFSS 3D Layout designs.")

    # Push excitation from file
    hfss_3dl.edit_source_from_file(
        source=data.choice,
        input_file=str(file_path),
        is_time_domain=True,
    )
    hfss_3dl.logger.info("Excitation assigned correctly.")

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)

    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = PushExcitation3DLayoutExtension(withdraw=False)
        if extension.data.choice and extension.data.file_path:
            main(extension.data)
    else:
        data = PushExcitation3DLayoutExtensionData(**args)
        main(data)
