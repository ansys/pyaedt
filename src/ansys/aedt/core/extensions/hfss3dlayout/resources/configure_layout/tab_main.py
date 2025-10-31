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
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


def create_tab_main(tab_frame, master):
    frame0 = ttk.Frame(tab_frame, name="frame0", style="PyAEDT.TFrame", borderwidth=1, relief="raised")
    # frame0.grid(row=0, column=0, **master.GRID_PARAMS)
    frame0.pack(fill="both", expand=True, padx=5, pady=5)
    frame1 = ttk.Frame(tab_frame, name="frame1", style="PyAEDT.TFrame", borderwidth=1, relief="raised")
    # frame1.grid(row=1, column=0, **master.GRID_PARAMS)
    frame1.pack(fill="both", expand=True, padx=5, pady=5)

    create_sub_frame0(frame0, master)
    create_sub_frame1(frame1, master)


def create_sub_frame0(parent, master):
    """Import frame."""
    row = 0
    ttk.Radiobutton(
        parent,
        text="Active Design",
        value=0,
        variable=master.var_active_design,
        style="PyAEDT.TRadiobutton",
        name="active_design",
    ).grid(row=row, column=0, **master.GRID_PARAMS)

    row = row + 1
    ttk.Radiobutton(
        parent,
        text="Specify Design",
        value=1,
        variable=master.var_active_design,
        name="specified_design",
        style="PyAEDT.TRadiobutton",
    ).grid(row=row, column=0, **master.GRID_PARAMS)

    ttk.Entry(
        parent,
        name="specified_design_name",
        state="readonly",
        width=50,
    ).grid(row=row, column=1, **master.GRID_PARAMS)
    ttk.Button(
        parent,
        text="Select",
        name="select_design",
        command=lambda: callback_select_design(master),
    ).grid(row=row, column=2, **master.GRID_PARAMS)
    # ttk.Checkbutton(
    #     tab_frame,
    #     name="overwrite_design",
    #     text="Overwrite Design",
    #     variable=master.var_load_overwrite,
    #     style="PyAEDT.TCheckbutton",
    # ).grid(row=row, column=0, sticky="w")


def create_sub_frame1(parent, master):
    """Export frame"""
    row = 0

    ttk.Button(
        parent,
        name="load_config",
        text="Load Config",
        command=lambda: callback_apply(master),
        style="PyAEDT.TButton",
    ).grid(row=row, column=0, **master.GRID_PARAMS)

    row = row + 1
    ttk.Button(
        parent,
        name="export_config",
        text="Export Config",
        command=lambda: callback_export(master),
        style="PyAEDT.TButton",
    ).grid(row=row, column=0, **master.GRID_PARAMS)

    row = row + 1
    options = master.export_options.model_dump()

    # Initialize checkbox variables if not already created
    if not master.export_option_vars:
        for name in options:
            master.export_option_vars[name] = tk.BooleanVar(master=master.root, value=options[name])

    for idx, name in enumerate(options):
        col = idx % 2
        chk = ttk.Checkbutton(
            parent, name=name, text=name, variable=master.export_option_vars[name], style="PyAEDT.TCheckbutton"
        )
        chk.grid(row=row, column=col, padx=5, pady=2, sticky="w")
        row = row if col == 0 else row + 1


def callback_select_design(master):
    """Select design to apply configuration."""
    design_path = filedialog.askopenfilename(
        title="Select Design",
        filetypes=(("All files", "*.*"), ("Brd", "*.brd"), ("ODB++", "*.tgz"), ("Edb", "*.def")),
    )
    if not design_path:  # pragma: no cover
        return
    else:
        if design_path.endswith(".def"):
            design_name = Path(design_path).parent.name
        else:
            design_name = Path(design_path).name
        entry = master.root.nametowidget(".notebook.main.frame0.specified_design_name")
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, design_name)
        entry.config(state="disabled")
        master.selected_edb = design_path


def callback_apply(master):
    file_path = filedialog.askopenfilename(
        title="Select Configuration",
        filetypes=(("json", "*.json"), ("toml", "*.toml"), ("All files", "*.*")),
        defaultextension=".json",
    )

    if not file_path:  # pragma: no cover
        return False

    edbpath = master.apply_config_to_edb(file_path)
    master.load_edb_into_hfss3dlayout(edbpath)
    return True


def callback_export(master):
    file_path = filedialog.asksaveasfilename(
        title="Select Configuration",
        filetypes=(("json", "*.json"), ("toml", "*.toml"), ("All files", "*.*")),
        defaultextension=".json",
    )
    if not file_path:  # pragma: no cover
        return False

    update_options(master)
    config_dict = master.export_config_from_edb()
    with open(file_path, "w") as f:
        json.dump(config_dict, f, indent=4)
    messagebox.showinfo("Information", f"Saved to {file_path}")
    return file_path


def update_options(master):
    """Update export options based on the selected checkboxes."""
    for name, var in master.export_option_vars.items():
        setattr(master.export_options, name, var.get())
