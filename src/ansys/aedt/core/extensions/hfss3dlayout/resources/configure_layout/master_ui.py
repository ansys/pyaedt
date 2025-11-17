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

import os
from pathlib import Path
import tempfile
import tkinter
from tkinter import ttk
from typing import Union
import webbrowser

from pyedb import Edb

import ansys.aedt.core
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.data_class import AedtInfo
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.data_class import ExportOptions
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_example import create_tab_example
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_main import create_tab_main
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError

INTRO_LINK = "https://aedt.docs.pyansys.com/version/dev/User_guide/pyaedt_extensions_doc/project/configure_layout.html"
GUIDE_LINK = "https://examples.aedt.docs.pyansys.com/version/dev/examples/edb/use_configuration/index.html"


def create_new_edb_name(name):
    suffix = name.split("_")[-1]
    is_int = True
    try:
        suffix_ = int(suffix)
    except ValueError:
        is_int = False
        suffix_ = 0
    new_name = f"{name.rstrip(suffix)}{suffix_ + 1}" if is_int else f"{name}_{suffix_ + 1}"
    return new_name


class ConfigureLayoutExtension(ExtensionHFSS3DLayoutCommon):
    EXTENSION_TITLE = "Configure Layout"
    GRID_PARAMS = {"padx": 15, "pady": 10, "sticky": "nsew"}

    tab_frame_main = None
    tab_frame_export = None
    tab_frame_example = None

    var_active_design = None
    var_load_overwrite = None
    var_selected_design = None

    __selected_design = ""

    @property
    def selected_edb(self):
        if self.var_active_design.get() == 0:
            return self.get_active_edb()
        else:
            return self.__selected_design

    @selected_edb.setter
    def selected_edb(self, value: Union[str, Path]):
        self.__selected_design = value

    def __init__(self, withdraw: bool = False):
        self.aedt_info = AedtInfo(
            port=get_port(), version=get_aedt_version(), aedt_process_id=get_process_id(), student_version=is_student()
        )
        self.export_options = ExportOptions()
        self.export_option_vars = {}

        super().__init__(
            self.EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_toggle_theme_button(self, parent, toggle_row, toggle_column):
        return

    def add_toggle_theme_button_(self, parent):
        """Create a button to toggle between light and dark themes."""
        button_frame = ttk.Frame(
            parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2, name="theme_button_frame"
        )
        button_frame.pack(fill="both", expand=False, **{"padx": 5, "pady": 5})
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
        change_theme_button.pack(anchor="e", **{"padx": 15, "pady": 10})
        self._widgets["change_theme_button"] = change_theme_button

    def add_extension_content(self):
        self.var_active_design = tkinter.IntVar()
        self.var_load_overwrite = tkinter.BooleanVar()
        self.var_active_design.set(0)
        self.var_load_overwrite.set(False)
        self.var_selected_design = tkinter.StringVar()

        self.root.geometry("700x600")
        # self.root.grid_rowconfigure(0, weight=1)
        # self.root.grid_columnconfigure(0, weight=1)

        menubar = tkinter.Menu(self.root)
        # === File Menu ===
        help_menu = tkinter.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Introduction",
            command=lambda: webbrowser.open(INTRO_LINK),
        )
        help_menu.add_command(
            label="User Guide",
            command=lambda: webbrowser.open(GUIDE_LINK),
        )

        # Add File menu to menubar
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook")

        self.tab_frame_main = ttk.Frame(nb, name="main", style="PyAEDT.TFrame")
        self.tab_frame_example = ttk.Frame(nb, name="example", style="PyAEDT.TFrame")

        nb.add(self.tab_frame_main, text="Main")
        # nb.add(self.tab_frame_export, text="Export")
        nb.add(self.tab_frame_example, text="Example")
        # nb.grid(row=0, column=0, **self.GRID_PARAMS)
        nb.pack(fill="both", expand=True)

        create_tab_main(self.tab_frame_main, self)
        create_tab_example(self.tab_frame_example, self)

        self.add_toggle_theme_button_(self.root)

    def apply_config_to_edb(self, config_path, test_folder=None):
        settings.logger.info("Applying configuration to EDB")
        selected_edb = self.selected_edb
        settings.logger.info(f"target EDB: {selected_edb}")
        app = Edb(edbpath=str(selected_edb), edbversion=self.aedt_info.version)

        temp_dir = Path(tempfile.TemporaryDirectory(suffix=".ansys").name, dir=test_folder)
        temp_dir.mkdir()

        new_name = create_new_edb_name(Path(app.edbpath).stem) + ".aedb"
        app.save_as(str(temp_dir / new_name))
        app.configuration.load(config_path)
        app.configuration.run()
        app.save()
        app.close()
        return app.edbpath

    def export_config_from_edb(self):
        app = Edb(edbpath=str(self.selected_edb), edbversion=self.aedt_info.version)
        data = app.configuration.get_data_from_db(**self.export_options.model_dump())
        app.close()
        return data

    def load_edb_into_hfss3dlayout(self, edb_path: Union[str, Path]):
        app = ansys.aedt.core.Hfss3dLayout(project=str(edb_path), **self.aedt_info.model_dump())
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        else:
            app.close_project(save=False)
        return app

    def get_active_edb(self):
        desktop = ansys.aedt.core.Desktop(new_desktop=False, **self.aedt_info.model_dump())
        active_project = desktop.active_project()
        if active_project:
            project_name = active_project.GetName()
            project_dir = active_project.GetPath()
            aedb_directory = Path(project_dir) / (project_name + ".aedb")
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                desktop.release_desktop(False, False)
        else:  # pragma: no cover
            if "PYTEST_CURRENT_TEST" not in os.environ:
                desktop.release_desktop(False, False)
            raise AEDTRuntimeError("No active design")
        return str(aedb_directory)
