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
import tkinter
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core.extensions.hfss.src_mcad_assembly.backend import MCADAssemblyBackend
from ansys.aedt.core.extensions.hfss.src_mcad_assembly.data_classes import AedtInfo
from ansys.aedt.core.extensions.hfss.src_mcad_assembly.tab_main import create_tab_main
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student


class MCADAssemblyFrontend(ExtensionProjectCommon):
    EXTENSION_TITLE = "MCAD Assembly"
    GRID_PARAMS = {"padx": 15, "pady": 10, "sticky": "nsew"}
    PACK_PARAMS = {"padx": 15, "pady": 10}

    tab_frame_main = None

    config_data: dict = dict()

    def __init__(self, withdraw: bool = False):
        self.aedt_info = AedtInfo(
            port=get_port(), version=get_aedt_version(), aedt_process_id=get_process_id(), student_version=is_student()
        )

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

        ttk.Button(
            button_frame,
            width=10,
            text="Run",
            command=lambda: self.run(self.config_data),
            style="PyAEDT.TButton",
            name="run",
        ).pack(anchor="w", side="left", **{"padx": 15, "pady": 10})

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
        change_theme_button.pack(anchor="e", side="right", **{"padx": 15, "pady": 10})
        self._widgets["change_theme_button"] = change_theme_button

    def add_extension_content(self):
        self.root.geometry("700x600")

        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook")
        self.tab_frame_main = ttk.Frame(nb, name="main", style="PyAEDT.TFrame")

        nb.add(self.tab_frame_main, text="Main")

        nb.pack(fill="both", expand=True)

        create_tab_main(self.tab_frame_main, self)
        self.add_toggle_theme_button_(self.root)

    def run(self, config_data):
        hfss = ansys.aedt.core.Hfss(**self.aedt_info.model_dump())
        app = MCADAssemblyBackend.load(data=config_data)
        app.run(hfss)
        del app

        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            hfss.release_desktop(False, False)
        else:
            hfss.close_project(save=False)
        return
