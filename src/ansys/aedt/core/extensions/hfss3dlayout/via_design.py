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
from functools import partial
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
import tkinter.ttk as ttk
from typing import List
from typing import Optional

import PIL.Image
import PIL.ImageTk
from pyedb.extensions.via_design_backend import ViaDesignBackend
import toml

from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import SUN
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_DEFAULT_ARGUMENTS = {"file_path": ""}
EXTENSION_TITLE = "Via design"
EXTENSION_RESOURCES_PATH = Path(__file__).parent / "resources" / "via_design"
EXTENSION_NB_ROW = 2
EXTENSION_NB_COLUMN = 3


@dataclass
class ExportExampleData:
    """"""

    picture_path: Path
    toml_file_path: Path


EXPORT_EXAMPLES = [
    ExportExampleData(EXTENSION_RESOURCES_PATH / "via_design_rf.png", EXTENSION_RESOURCES_PATH / "pcb_rf.toml"),
    ExportExampleData(EXTENSION_RESOURCES_PATH / "via_design_pcb_diff.png", EXTENSION_RESOURCES_PATH / "pcb_diff.toml"),
    ExportExampleData(
        EXTENSION_RESOURCES_PATH / "via_design_pkg_diff.png", EXTENSION_RESOURCES_PATH / "package_diff.toml"
    ),
]


class ViaDesignExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for advanced fields calculator in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )
        self.__create_design_path = None
        self.__export_examples: List[ExportExampleData] = EXPORT_EXAMPLES
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""

        def save_example(toml_file_path: Path):
            file_path = filedialog.asksaveasfilename(
                initialfile=toml_file_path.name,
                defaultextension=".toml",
                filetypes=[("TOML File", "*.toml"), ("All Files", "*.*")],
                title="Save example as",
            )
            if file_path:
                with open(toml_file_path, "r", encoding="utf-8") as file:
                    config_string = file.read()

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(config_string)

        notebook = ttk.Notebook(self.root, style="PyAEDT.TNotebook")
        notebook.grid(row=0, column=0, padx=10, pady=10)
        frame = ttk.Frame(notebook, style="PyAEDT.TFrame")
        notebook.add(frame, text="Configuration examples")

        row = 0
        column = 0
        for example in self.__export_examples:
            img = PIL.Image.open(example.picture_path)
            img = img.resize((100, 100))
            photo = PIL.ImageTk.PhotoImage(img, master=frame)

            example_name = example.toml_file_path.stem
            button = ttk.Button(
                frame,
                command=partial(save_example, example.toml_file_path),
                style="PyAEDT.TButton",
                image=photo,
                width=20,
                name=f"button_{example_name}",
            )
            # NOTE: Setting button.image ensures that a reference to the photo is kept and that
            # the picture is correctly rendered in the tkinter window
            button.image = photo
            button.grid(row=row, column=column, **DEFAULT_PADDING)

            if column > EXTENSION_NB_COLUMN:
                row += 1
                column = 0
            else:
                column += 1

        lower_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        lower_frame.grid(row=2, column=0, columnspan=EXTENSION_NB_COLUMN)

        create_design_button = ttk.Button(
            lower_frame,
            text="Create Design",
            command=self.create_design,
            style="PyAEDT.TButton",
            width=20,
            name="button_create_design",
        )
        create_design_button.grid(row=0, column=0, sticky="w", **DEFAULT_PADDING)
        change_theme_button = ttk.Button(
            lower_frame,
            width=20,
            text=SUN,
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        change_theme_button.grid(row=0, column=1)

    def create_design(self, create_design_path: Optional[Path] = None):
        """Create via design in AEDT"""
        if create_design_path is None:
            create_design_path = filedialog.askopenfilename(
                title="Select configuration",
                filetypes=(("toml", "*.toml"),),
                defaultextension=".toml",
            )
            if not create_design_path:
                return

        self.__create_design_path = Path(create_design_path)
        if not self.__create_design_path.is_file():
            raise AEDTRuntimeError(f"Selected file does not exist or is not a file: {self.__create_design_path}")

        dict_config = toml.load(self.__create_design_path)
        stacked_vias = dict_config.pop("stacked_vias")

        for param_name, param_value in dict_config["signals"].items():
            stacked_vias_name = param_value["stacked_vias"]
            dict_config["signals"][param_name]["stacked_vias"] = stacked_vias[stacked_vias_name]

        for param_name, param_value in dict_config["differential_signals"].items():
            stacked_vias_name = param_value["stacked_vias"]
            dict_config["differential_signals"][param_name]["stacked_vias"] = stacked_vias[stacked_vias_name]

        backend = ViaDesignBackend(dict_config)
        hfss_3d = Hfss3dLayout(
            project=backend.app.edbpath,
            version=VERSION,
            port=PORT,
            aedt_process_id=AEDT_PROCESS_ID,
            student_version=IS_STUDENT,
        )

        if "PYTEST_CURRENT_TEST" not in os.environ:
            hfss_3d.desktop_class.release_desktop(False, False)
        return True

    @property
    def create_design_path(self):
        return self.__create_design_path

    @property
    def export_examples(self):
        return self.__export_examples


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = ViaDesignExtension(withdraw=False)

        tkinter.mainloop()
    else:
        extension = ViaDesignExtension(withdraw=True)
        extension.create_design(args["file_path"])
