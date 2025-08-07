# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

from ansys.aedt.core import Circuit
from ansys.aedt.core import Desktop
from ansys.aedt.core.extensions.misc import ExtensionCircuitCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

# Retrieve environment info
PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments and title
EXTENSION_DEFAULT_ARGUMENTS = {"file_extension": ""}
EXTENSION_TITLE = "Import schematic to Circuit"


@dataclass
class ImportSchematicData(ExtensionCommonData):
    """Data class for import schematic extension."""

    file_extension: str = EXTENSION_DEFAULT_ARGUMENTS["file_extension"]


class ImportSchematicExtension(ExtensionCircuitCommon):
    """Extension for importing schematic into Circuit."""

    def __init__(self, withdraw: bool = False):
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=1,
            toggle_column=2,
        )
        self._text_widget = None
        self.add_extension_content()

    def add_extension_content(self):
        """Add UI elements for file selection and import action."""
        label = ttk.Label(
            self.root,
            text="Browse file:",
            style="PyAEDT.TLabel",
        )
        label.grid(row=0, column=0, padx=15, pady=10)

        self._text_widget = tkinter.Text(
            self.root,
            width=40,
            height=1,
        )
        self._text_widget.grid(row=0, column=1, padx=5, pady=10)

        def browse_file():
            current = self._text_widget.get(
                "1.0",
                tkinter.END,
            ).strip()
            initial = Path(current).parent if current else Path.home()
            filename = filedialog.askopenfilename(
                initialdir=initial,
                title="Select schematic file",
                filetypes=(
                    ("LTSPice file", "*.asc"),
                    ("Spice file", "*.cir *.sp"),
                    ("Qcv file", "*.qcv"),
                ),
            )
            if filename:
                self._text_widget.delete("1.0", tkinter.END)
                self._text_widget.insert(tkinter.END, filename)

        browse_button = ttk.Button(
            self.root,
            text="...",
            width=10,
            command=browse_file,
            style="PyAEDT.TButton",
        )
        browse_button.grid(row=0, column=2, padx=10, pady=10)

        def callback():
            file_extension = self._text_widget.get(
                "1.0",
                tkinter.END,
            ).strip()
            if not Path(file_extension).exists():
                raise ValueError("File does not exist.")
            self.data = ImportSchematicData(file_extension=file_extension)
            self.root.destroy()

        import_button = ttk.Button(
            self.root,
            text="Import",
            width=40,
            command=callback,
            style="PyAEDT.TButton",
        )
        import_button.grid(row=1, column=1, padx=10, pady=10)


def main(data: ImportSchematicData) -> bool:
    """Execute schematic import based on provided data."""
    file_extension = Path(data.file_extension)
    app = Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    cir = Circuit(design=file_extension.stem)

    if file_extension.suffix == ".asc":
        cir.create_schematic_from_asc_file(str(file_extension))
    elif file_extension.suffix in {".sp", ".cir"}:
        cir.create_schematic_from_netlist(str(file_extension))
    elif file_extension.suffix == ".qcv":
        cir.create_schematic_from_mentor_netlist(str(file_extension))

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
    if not args.get("is_batch", False):
        extension = ImportSchematicExtension(withdraw=False)
        tkinter.mainloop()
        if extension.data:
            main(extension.data)
    else:
        data = ImportSchematicData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
