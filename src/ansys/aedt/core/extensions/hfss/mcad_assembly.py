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

import json
from pathlib import Path
import tempfile
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import Any
from typing import cast

from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly as MCADAssemblyBackend  # noqa: F401
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import run


class MCADAssemblyFrontend(ExtensionHFSSCommon):
    """Provide MCAD assembly frontend."""

    EXTENSION_TITLE = "MCAD Assembly"
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

    def __init__(self, withdraw: bool = False) -> None:

        super().__init__(
            self.EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_toggle_theme_button(self, parent: tkinter.Misc, toggle_row: int, toggle_column: int) -> None:
        """Create a button to toggle between light and dark themes.

        Examples
        --------
        >>> import tkinter
        >>> from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
        >>> frontend = MCADAssemblyFrontend(withdraw=True)
        >>> frame = tkinter.Frame(frontend.root)
        >>> frontend.add_toggle_theme_button(frame)

        """
        button_frame = ttk.Frame(
            parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2, name="theme_button_frame"
        )
        button_frame.pack(fill="both", expand=False, padx=5, pady=5)

        ttk.Button(
            button_frame,
            width=10,
            text="Run",
            command=lambda: run(self.config_data, model_dir=self.local_path),
            style="PyAEDT.TButton",
            name="run",
        ).pack(anchor="w", side="left", padx=15, pady=10)

        self._widgets["button_frame"] = button_frame

        change_theme_button = ttk.Button(
            button_frame,
            width=10,
            text="\u263d",
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        # change_theme_button.grid(row=0, column=0, **{"padx": 15, "pady": 10})
        change_theme_button.pack(anchor="e", side="right", padx=15, pady=10)
        self._widgets["change_theme_button"] = change_theme_button

    def add_extension_content(self) -> None:
        """Add custom content to the extension UI.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
        >>> extension = MCADAssemblyFrontend(withdraw=True)
        >>> extension.add_extension_content()

        """
        self.root.geometry("700x600")

        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook")
        self.tab_frame_main = ttk.Frame(nb, name="main", style="PyAEDT.TFrame")

        nb.add(self.tab_frame_main, text="Main")

        nb.pack(fill="both", expand=True)

        create_tab_main(self.tab_frame_main, self)


# create main tab
def create_tab_main(tab_frame: tkinter.Widget, master: MCADAssemblyFrontend) -> None:
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


def load_dict(tree: ttk.Treeview, master: MCADAssemblyFrontend) -> None:
    """Load dict."""
    file_path = filedialog.askopenfilename(
        title="Select Design",
        filetypes=(("JSON", "*.json"), ("All files", "*.*")),
    )
    if not file_path:  # pragma: no cover
        return
    else:
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


# end of create_tab_main function

# End of frontend


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments()

    if not args["is_batch"]:
        temp = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        temp.mkdir()
        extension: ExtensionCommon = MCADAssemblyFrontend(withdraw=False)
        cast(Any, extension).working_directory = temp
        tkinter.mainloop()
