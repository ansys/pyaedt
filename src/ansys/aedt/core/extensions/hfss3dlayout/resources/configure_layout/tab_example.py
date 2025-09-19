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

import json
from pathlib import Path
import tempfile
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.template import SERDES_CONFIG


def create_tab_example(tab_frame, master):
    ttk.Button(
        tab_frame,
        name="load_example_board",
        text="Load Example Board",
        command=lambda: call_back_load_example_board(master),
        style="PyAEDT.TButton",
        width=30,
    ).pack(expand=True, padx=5, pady=5, side="left", anchor="nw")

    ttk.Button(
        tab_frame,
        name="export_example_config",
        text="Export Example Config",
        command=call_back_export_template,
        style="PyAEDT.TButton",
        width=30,
    ).pack(expand=True, padx=5, pady=5, side="right", anchor="ne")


def call_back_load_example_board(master, test_folder=None):
    temp_dir = tempfile.TemporaryDirectory(suffix=".ansys", dir=test_folder).name
    Path(temp_dir).mkdir()
    example_edb = download_file(source="edb/ANSYS_SVP_V1_1.aedb", local_path=temp_dir)
    master.load_edb_into_hfss3dlayout(example_edb)


def call_back_export_template():
    file = filedialog.asksaveasfilename(
        initialfile="serdes_config.json", defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if not file:  # pragma: no cover
        return
    file = Path(file)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(SERDES_CONFIG, f, indent=2)
    messagebox.showinfo("Message", "Template file exported successfully.")
