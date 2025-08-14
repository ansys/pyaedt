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
from dataclasses import field
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import List

import ansys.aedt.core
from ansys.aedt.core import Circuit
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import ExtensionCircuitCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
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
EXTENSION_DEFAULT_ARGUMENTS = {"file_path": [], "output_dir": ""}
EXTENSION_TITLE = "Circuit Configuration"
EXTENSION_NB_COLUMN = 2
FILE_PATH_ERROR_MSG = "Select an existing file before importing."
DESIGN_TYPE_ERROR_MSG = "A Circuit design is needed for this extension."


@dataclass
class CircuitConfigurationData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    file_path: List[str] = field(default_factory=list)
    output_dir: str = EXTENSION_DEFAULT_ARGUMENTS["output_dir"]


class CircuitConfigurationExtension(ExtensionCircuitCommon):
    """Circuit configuration extension."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )
        self.data: CircuitConfigurationData = CircuitConfigurationData()

        self.add_extension_content()

    def browse_file(self):
        file_path = filedialog.askopenfilenames(
            initialdir="/",
            title="Select file",
            filetypes=(("json file", "*.json"), ("toml", "*.toml")),
        )
        if file_path == "":
            return
        for file in file_path:
            self.data.file_path.append(Path(file))
        self.root.destroy()

    def output_dir(self):
        output = filedialog.askdirectory(
            initialdir="/",
            title="Save new projects to",
        )
        if output == "":
            return

        self.data.output_dir = Path(output)

        self.root.destroy()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        upper_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        upper_frame.grid(row=0, column=0, columnspan=EXTENSION_NB_COLUMN)

        import_button = ttk.Button(
            upper_frame,
            text="Selected and apply configuration",
            command=lambda: self.browse_file(),
            style="PyAEDT.TButton",
        )
        import_button.grid(row=0, column=0, **DEFAULT_PADDING)
        self._widgets["import_button"] = import_button

        lower_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        lower_frame.grid(row=1, column=0, columnspan=EXTENSION_NB_COLUMN)

        export_button = ttk.Button(
            lower_frame, text="Export configuration", command=lambda: self.output_dir(), style="PyAEDT.TButton"
        )
        export_button.grid(row=0, column=0, **DEFAULT_PADDING)
        self._widgets["export_button"] = export_button
        self.add_toggle_theme_button(lower_frame, 0, 1)


def main(data: CircuitConfigurationData):
    """Main function to execute circuit configuration extension."""
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

    if active_design.GetDesignType() == "Circuit Design":
        design_name = active_design.GetName()
        if ";" in design_name:
            design_name = design_name.split(";")[1]
    else:  # pragma: no cover
        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        raise AEDTRuntimeError(DESIGN_TYPE_ERROR_MSG)

    cir = Circuit(project_name, design_name)

    if data.file_path:
        for file in data.file_path:
            cir.configurations.import_config(file)
            cir.save_project()

    elif data.output_dir:
        config_file = Path(data.output_dir) / "circuit_configuration.json"
        cir.configurations.export_config(str(config_file))
    else:
        raise AEDTRuntimeError("No file path or output directory provided.")

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCircuitCommon = CircuitConfigurationExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data.file_path or extension.data.output_dir:
            main(extension.data)

    else:
        data = CircuitConfigurationData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
