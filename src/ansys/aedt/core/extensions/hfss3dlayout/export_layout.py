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
from tkinter import ttk

from pyedb import Edb

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "export_ipc": True,
    "export_configuration": True,
    "export_bom": True,
}
EXTENSION_TITLE = "Layout Exporter"


@dataclass
class ExportLayoutExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    export_ipc: bool = EXTENSION_DEFAULT_ARGUMENTS["export_ipc"]
    export_configuration: bool = EXTENSION_DEFAULT_ARGUMENTS["export_configuration"]
    export_bom: bool = EXTENSION_DEFAULT_ARGUMENTS["export_bom"]


class ExportLayoutExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for exporting layout data in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=3,
            toggle_column=1,
        )

        # Tkinter widgets
        self.ipc_check = None
        self.configuration_check = None
        self.bom_check = None

        # Trigger manually since add_extension_content requires it
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Export IPC2581 option
        label = ttk.Label(
            self.root,
            text="Export IPC2581:",
            width=30,
            style="PyAEDT.TLabel",
        )
        label.grid(row=0, column=0, padx=15, pady=10)

        self.ipc_check = tkinter.IntVar()
        check = ttk.Checkbutton(
            self.root,
            width=0,
            variable=self.ipc_check,
            style="PyAEDT.TCheckbutton",
        )
        check.grid(row=0, column=1, padx=15, pady=10)
        self.ipc_check.set(1)

        # Export Configuration file option
        label2 = ttk.Label(
            self.root,
            text="Export Configuration file:",
            width=30,
            style="PyAEDT.TLabel",
        )
        label2.grid(row=1, column=0, padx=15, pady=10)

        self.configuration_check = tkinter.IntVar()
        check2 = ttk.Checkbutton(
            self.root,
            width=0,
            variable=self.configuration_check,
            style="PyAEDT.TCheckbutton",
        )
        check2.grid(row=1, column=1, padx=15, pady=10)
        self.configuration_check.set(1)

        # Export BOM file option
        label3 = ttk.Label(
            self.root,
            text="Export BOM file:",
            width=30,
            style="PyAEDT.TLabel",
        )
        label3.grid(row=2, column=0, padx=15, pady=10)

        self.bom_check = tkinter.IntVar()
        check3 = ttk.Checkbutton(
            self.root,
            width=0,
            variable=self.bom_check,
            style="PyAEDT.TCheckbutton",
        )
        check3.grid(row=2, column=1, padx=15, pady=10)
        self.bom_check.set(1)

        def callback(extension: ExportLayoutExtension):
            data = ExportLayoutExtensionData()
            data.export_ipc = extension.ipc_check.get() == 1
            data.export_configuration = extension.configuration_check.get() == 1
            data.export_bom = extension.bom_check.get() == 1
            extension.data = data
            extension.root.destroy()

        ok_button = ttk.Button(
            self.root,
            text="Export",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="export",
        )
        ok_button.grid(row=3, column=0, padx=15, pady=10)


def main(data: ExportLayoutExtensionData):
    """Main function to run the export layout extension."""
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    project_path = Path(active_project.GetPath())
    project_name = active_project.GetName()
    aedb_path = project_path / f"{project_name}.aedb"
    design_name = active_design.GetName().split(";")[1]
    edb = Edb(str(aedb_path), design_name, edbversion=VERSION)

    try:
        if data.export_ipc:
            ipc_file = aedb_path.with_name(aedb_path.stem + "_ipc2581.xml")
            edb.export_to_ipc2581(ipc_path=str(ipc_file))

        if data.export_bom:
            bom_file = aedb_path.with_name(aedb_path.stem + "_bom.csv")
            edb.workflow.export_bill_of_materials(bom_file)

        if data.export_configuration:
            config_file = aedb_path.with_name(aedb_path.stem + "_config.json")
            edb.configuration.export(config_file)
    finally:
        # Ensure EDB is properly closed
        edb.close_edb()

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.logger.info("Project generated correctly.")
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExportLayoutExtension = ExportLayoutExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = ExportLayoutExtensionData()
        for key, value in args.items():
            if hasattr(data, key):
                setattr(data, key, value)
        main(data)
