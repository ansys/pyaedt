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
import time
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core.edb import Edb
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "working_path": "",
    "source_path": "",
    "mounting_side": "top",
    "import_edb": True,
}
EXTENSION_TITLE = "Arbitrary wave port creator"


@dataclass
class ArbitraryWavePortExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    working_path: str = EXTENSION_DEFAULT_ARGUMENTS["working_path"]
    source_path: str = EXTENSION_DEFAULT_ARGUMENTS["source_path"]
    mounting_side: str = EXTENSION_DEFAULT_ARGUMENTS["mounting_side"]
    import_edb: bool = EXTENSION_DEFAULT_ARGUMENTS["import_edb"]


class ArbitraryWavePortExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for generating arbitrary wave ports in HFSS 3D Layout."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=4,
            toggle_column=2,
        )

        # Initialize data
        self.data = ArbitraryWavePortExtensionData()

        # Tkinter widgets
        self.work_dir_entry = None
        self.source_file_entry = None
        self.mounting_side_combo = None
        self.import_edb_variable = None

        # Trigger manually since add_extension_content
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Working directory
        work_dir_label = ttk.Label(self.root, text="Working directory:", width=20, style="PyAEDT.TLabel")
        work_dir_label.grid(row=0, column=0, padx=15, pady=10)

        self.work_dir_entry = tkinter.Text(self.root, width=40, height=1)
        self.work_dir_entry.grid(row=0, column=1, padx=15, pady=10)

        work_dir_button = ttk.Button(
            self.root,
            text="Browse",
            command=self.__browse_work_dir,
            style="PyAEDT.TButton",
        )
        work_dir_button.grid(row=0, column=2, padx=5, pady=10)

        # Source layout
        source_label = ttk.Label(self.root, text="Source layout:", width=20, style="PyAEDT.TLabel")
        source_label.grid(row=1, column=0, padx=15, pady=10)

        self.source_file_entry = tkinter.Text(self.root, width=40, height=1)
        self.source_file_entry.grid(row=1, column=1, padx=15, pady=10)

        source_button = ttk.Button(
            self.root,
            text="Browse",
            command=self.__browse_source_file,
            style="PyAEDT.TButton",
        )
        source_button.grid(row=1, column=2, padx=5, pady=10)

        # Mounting side
        mounting_label = ttk.Label(self.root, text="Mounting side:", width=20, style="PyAEDT.TLabel")
        mounting_label.grid(row=2, column=0, padx=15, pady=10)

        self.mounting_side_combo = ttk.Combobox(
            self.root,
            width=15,
            style="PyAEDT.TCombobox",
            name="mounting_side_combo",
            state="readonly",
        )
        self.mounting_side_combo["values"] = ("top", "bottom")
        self.mounting_side_combo.current(0)
        self.mounting_side_combo.grid(row=2, column=1, padx=15, pady=10, sticky="w")

        # Import EDB checkbox
        self.import_edb_variable = tkinter.BooleanVar()
        self.import_edb_variable.set(True)
        import_edb_check = ttk.Checkbutton(
            self.root,
            text="Import EDB",
            variable=self.import_edb_variable,
            style="PyAEDT.TCheckbutton",
        )
        import_edb_check.grid(row=3, column=0, padx=15, pady=10, sticky="w")

        def callback(extension: ArbitraryWavePortExtension):
            extension.data.working_path = extension.work_dir_entry.get("1.0", tkinter.END).strip()
            extension.data.source_path = extension.source_file_entry.get("1.0", tkinter.END).strip()
            extension.data.mounting_side = extension.mounting_side_combo.get()
            extension.data.import_edb = extension.import_edb_variable.get()
            extension.root.destroy()

        ok_button = ttk.Button(
            self.root,
            text="Generate",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        ok_button.grid(row=4, column=0, padx=15, pady=10)

    def __browse_work_dir(self):
        """Browse for working directory."""
        work_dir_path = filedialog.askdirectory()
        if work_dir_path:
            self.work_dir_entry.delete("1.0", tkinter.END)
            self.work_dir_entry.insert(tkinter.END, work_dir_path)

    def __browse_source_file(self):
        """Browse for source file."""
        if not self.import_edb_variable.get():
            file_type = (
                ("odb++", "*.tgz"),
                ("cadence pcb", "*.brd"),
                ("cadence package", "*.mcm"),
                ("", "*.zip"),
            )
            source_path = filedialog.askopenfilename(filetypes=file_type, title="Please select the source design")
        else:
            source_path = filedialog.askdirectory(title="Import aedb folder")

        if source_path:
            self.source_file_entry.delete("1.0", tkinter.END)
            self.source_file_entry.insert(tkinter.END, source_path)


def main(data: ArbitraryWavePortExtensionData):
    """Main function to run the arbitrary wave port extension."""
    # Validate input data
    if not data.working_path:
        raise AEDTRuntimeError("No working path provided")
    if not data.source_path:
        raise AEDTRuntimeError("No source path provided")

    working_dir = Path(data.working_path)
    edb_file = Path(data.source_path)
    mounting_side_variable = data.mounting_side

    edb_project = working_dir / "arbitrary_wave_port.aedb"
    out_3d_project = working_dir / "output_3d.aedt"
    component_3d_file = working_dir / "wave_port.a3dcomp"

    if working_dir.exists():
        if len(list(working_dir.iterdir())) > 0:
            if "PYTEST_CURRENT_TEST" not in os.environ:
                res = messagebox.askyesno(
                    title="Warning",
                    message="The selected working directory is not empty, "
                    "the entire content will be deleted. "
                    "Are you sure to continue ?",
                )
                if res == "no":
                    return False

    edb = Edb(edbpath=rf"{edb_file}", edbversion=VERSION)
    if not edb.create_model_for_arbitrary_wave_ports(
        temp_directory=str(working_dir),
        mounting_side=mounting_side_variable,
        output_edb=str(edb_project),
    ):
        if "PYTEST_CURRENT_TEST" not in os.environ:
            messagebox.showerror(
                "EDB model failure",
                "Failed to create EDB model, please make sure you "
                "selected the correct mounting side. The selected side must "
                "must contain explicit voids with pad-stack instances inside.",
            )
        raise AEDTRuntimeError("Failed to create EDB model.")
    edb.close()
    time.sleep(1)

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    hfss3d = Hfss3dLayout(project=str(edb_project), version=VERSION)
    setup = hfss3d.create_setup("wave_ports")
    setup.export_to_hfss(file_fullname=str(out_3d_project), keep_net_name=True)
    time.sleep(1)
    hfss3d.close_project()

    hfss = Hfss(
        projectname=str(out_3d_project),
        specified_version=VERSION,
        new_desktop_session=False,
    )
    hfss.solution_type = "Terminal"

    # Deleting dielectric objects
    for solid_obj in [
        obj for obj in hfss.modeler.solid_objects if obj.material_name in hfss.modeler.materials.dielectrics
    ]:
        solid_obj.delete()

    # creating ports
    for sheet in hfss.modeler.sheet_objects:
        hfss.wave_port(assignment=sheet.id, reference="GND", terminals_rename=False)

    # create 3D component
    hfss.save_project(file_name=str(out_3d_project))
    hfss.modeler.create_3dcomponent(input_file=str(component_3d_file))
    hfss.logger.info(
        f"3D component with arbitrary wave ports has been generated. "
        f"You can import the file located in working directory {working_dir}"
    )
    hfss.close_project()

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = ArbitraryWavePortExtension()
        tkinter.mainloop()
        if extension.data:
            for output_name, output_value in extension.data.__dict__.items():
                if output_name in EXTENSION_DEFAULT_ARGUMENTS:
                    args[output_name] = output_value
            main(extension.data)
    else:
        data = ArbitraryWavePortExtensionData(**args)
        main(data)
