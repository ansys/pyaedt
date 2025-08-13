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
import tkinter
from tkinter import ttk

import ansys.aedt.core
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
EXTENSION_DEFAULT_ARGUMENTS = {"choice": "Export to HFSS"}
EXTENSION_TITLE = "Export to 3D"

SUFFIXES = {"Export to HFSS": "HFSS", "Export to Q3D": "Q3D", "Export to Maxwell 3D": "M3D", "Export to Icepak": "IPK"}


@dataclass
class ExportTo3DExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    choice: str = EXTENSION_DEFAULT_ARGUMENTS["choice"]


class ExportTo3DExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for exporting to 3D in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with title and theme
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=1,
            toggle_column=1,
        )
        # Add private attributes and initialize them through load info
        self.__load_aedt_info()

        # Tkinter widgets
        self.combo_choice = None

        # Trigger manually since add_extension_content requires info
        self.add_extension_content()

    def __load_aedt_info(self):
        """Load info."""
        design_type = self.aedt_application.design_type
        if design_type != "HFSS 3D Layout Design":
            self.release_desktop()
            msg = "HFSS 3D Layout project is needed."
            raise AEDTRuntimeError(msg)

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        label = ttk.Label(self.root, text="Choose an option:", width=30, style="PyAEDT.TLabel")
        label.grid(row=0, column=0, columnspan=2, padx=15, pady=10)

        # Dropdown menu for export choices
        self.combo_choice = ttk.Combobox(
            self.root, width=40, style="PyAEDT.TCombobox", name="combo_choice", state="readonly"
        )
        export_options = ("Export to HFSS", "Export to Q3D", "Export to Maxwell 3D", "Export to Icepak")
        self.combo_choice["values"] = export_options
        self.combo_choice.current(0)
        self.combo_choice.grid(row=0, column=1, columnspan=2, padx=15, pady=10)
        self.combo_choice.focus_set()

        def callback(extension: ExportTo3DExtension):
            choice = extension.combo_choice.get()

            export_data = ExportTo3DExtensionData(choice=choice)
            extension.data = export_data
            self.root.destroy()

        ok_button = ttk.Button(
            self.root,
            text="Export",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="export",
        )
        ok_button.grid(row=1, column=0, padx=15, pady=10)


def main(data: ExportTo3DExtensionData):
    """Main function to run the export to 3D extension."""
    if not data.choice:
        raise AEDTRuntimeError("No choice provided to the extension.")

    choice = data.choice

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

    if active_design.GetDesignType() in ["HFSS 3D Layout Design"]:
        design_name = active_design.GetName().split(";")[1]
    else:  # pragma: no cover
        app.logger.debug("HFSS 3D Layout project is needed.")
        app.release_desktop(False, False)
        raise AEDTRuntimeError("HFSS 3D Layout project is needed.")

    h3d = ansys.aedt.core.Hfss3dLayout(project=project_name, design=design_name)
    setup = h3d.create_setup()
    suffix = SUFFIXES[choice]

    if choice == "Export to Q3D":
        project_file = h3d.project_file[:-5] + f"_{suffix}.aedt"
        setup.export_to_q3d(project_file, keep_net_name=True)
    else:
        project_file = h3d.project_file[:-5] + f"_{suffix}.aedt"
        setup.export_to_hfss(project_file, keep_net_name=True)

    h3d.delete_setup(setup.name)

    h3d.save_project()

    if choice == "Export to Q3D":
        project_file = h3d.project_file[:-5] + f"_{suffix}.aedt"
        _ = ansys.aedt.core.Q3d(project=project_file)
    else:
        project_file = h3d.project_file[:-5] + f"_{suffix}.aedt"
        aedtapp = ansys.aedt.core.Hfss(project=project_file)
        aedtapp2 = None
        if choice == "Export to Maxwell 3D":
            aedtapp2 = ansys.aedt.core.Maxwell3d(project=aedtapp.project_name)
        elif choice == "Export to Icepak":
            aedtapp2 = ansys.aedt.core.Icepak(project=aedtapp.project_name)
        if aedtapp2:
            aedtapp2.copy_solid_bodies_from(aedtapp, no_vacuum=False, no_pec=False, include_sheets=True)
            aedtapp2.delete_design(aedtapp.design_name)
            aedtapp2.save_project()

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.logger.info("Project generated correctly.")
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionHFSS3DLayoutCommon = ExportTo3DExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = ExportTo3DExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
