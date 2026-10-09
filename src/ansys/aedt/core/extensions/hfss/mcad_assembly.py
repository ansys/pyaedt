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

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import Any

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly as MCADAssemblyBackend  # noqa: F401
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import run

PORT = get_port()
"""Port used by the extension."""
VERSION = get_aedt_version()
"""AEDT version used by the extension."""
AEDT_PROCESS_ID = get_process_id()
"""AEDT process identifier."""
IS_STUDENT = is_student()
"""Flag indicating whether the student version is used."""

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"config_file_path": ""}
"""Default arguments for the extension."""
EXTENSION_TITLE = "MCAD Assembly"
"""Title displayed for the extension."""


@dataclass
class MCADAssemblyExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data.

    Examples
    --------

    """

    config_file_path: str = EXTENSION_DEFAULT_ARGUMENTS["config_file_path"]


class MCADAssemblyExtension(ExtensionHFSSCommon):
    """Provide MCAD assembly frontend."""

    """Title displayed for the extension."""
    GRID_PARAMS = {"padx": 15, "pady": 10, "sticky": "nsew"}
    """Grid params."""
    PACK_PARAMS = {"padx": 15, "pady": 10}
    """Pack params."""

    tab_frame_main = None
    """Value for tab frame main."""

    local_path: Path | str = ""
    """Path to local."""
    config_data: dict = dict()
    """Value for config data."""
    config_file_path: str = ""

    def __init__(self, withdraw: bool = False) -> None:

        super().__init__(
            EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=1,
        )

    def add_extension_content(self) -> None:
        """Add custom content to the extension UI.

        Examples
        --------

        """
        self.root.geometry("700x600")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook")
        self.tab_frame_main = ttk.Frame(nb, name="main", style="PyAEDT.TFrame")

        nb.add(self.tab_frame_main, text="Main")

        nb.grid(row=0, column=0, columnspan=2, sticky="nsew")

        create_tab_main(self.tab_frame_main, self)

        ttk.Button(
            self.root,
            width=10,
            text="Run",
            command=self.create_assembly,
            style="PyAEDT.TButton",
            name="run",
        ).grid(row=2, column=0, sticky="w", padx=15, pady=10)

    def create_assembly(self):
        self.data = MCADAssemblyExtensionData(
            config_file_path=self.config_file_path,
        )
        self.root.destroy()


# create main tab
def create_tab_main(tab_frame: tkinter.Widget, master: MCADAssemblyExtension) -> None:
    """Create tab main."""
    tree = ttk.Treeview(tab_frame, name="tree")
    tree.pack(
        expand=True,
        fill="both",
        padx=master.PACK_PARAMS["padx"],
        pady=master.PACK_PARAMS["pady"],
    )

    ttk.Button(
        tab_frame,
        # width=10,
        text="Load Configure File",
        command=lambda: load_dict(tree, master),
        style="PyAEDT.TButton",
        name="load",
    ).pack(anchor="w", padx=master.PACK_PARAMS["padx"], pady=master.PACK_PARAMS["pady"])


def load_dict(tree: ttk.Treeview, master: MCADAssemblyExtension) -> None:
    """Load dict."""
    file_path = filedialog.askopenfilename(
        title="Select Design",
        filetypes=(("JSON", "*.json"), ("All files", "*.*")),
    )
    if not file_path:  # pragma: no cover
        return
    else:
        master.config_file_path = file_path
        with open(file_path, "r") as f:
            data = json.load(f)
            local_path = Path(file_path)
            master.local_path = local_path.parent
            master.config_data = data
    tree.delete(*tree.get_children())  # clear everything

    for key in ["coordinate_system", "component_models", "layout_component_models"]:
        temp = tree.insert("", "end", text=key, open=False)
        for key, value in master.config_data.get(key, {}).items():
            text = f"{key}: {value}"
            tree.insert(temp, "end", text=text, open=False)

    node3 = tree.insert("", "end", text=str("assembly"), open=False)

    temp = master.config_data.get("assembly", {})
    if not temp:
        temp = master.config_data.get("sub_components", {})
    insert_items(tree, node3, temp)


def insert_items(tree: ttk.Treeview, parent: str, dictionary: dict | list | str | int | float | None) -> None:
    """Insert items."""
    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            node = tree.insert(parent, "end", text=str(key), open=False)
            insert_items(tree, node, value)
    elif isinstance(dictionary, list):
        for idx, item in enumerate(dictionary):
            node = tree.insert(parent, "end", text=f"[{idx}]", open=False)
            insert_items(tree, node, item)
    else:
        tree.insert(parent, "end", text=str(dictionary))


def main(data: MCADAssemblyExtensionData) -> bool:
    if not data.config_file_path:
        raise AEDTRuntimeError("No assignment provided to the extension.")

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

    hfss: Any = get_pyaedt_app(project_name, design_name)

    if hfss.design_type != "HFSS":
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        raise AEDTRuntimeError("Active design is not HFSS.")

    config_file_path = data.config_file_path
    json_text = Path(config_file_path).read_text()

    data = MCADAssembly.model_validate_json(json_text)
    run(data, model_dir=str(Path(config_file_path).parent), hfss=hfss)


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    if not args["is_batch"]:
        extension = MCADAssemblyExtension(withdraw=False)
        tkinter.mainloop()

        if isinstance(extension.data, MCADAssemblyExtensionData):
            main(extension.data)
