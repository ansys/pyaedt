# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import tkinter as tk
from tkinter import ttk

from ansys.aedt.core import Desktop
from ansys.aedt.core import Icepak
from ansys.aedt.core.extensions.icepak.model_reviewer.backend import export_config_file
from ansys.aedt.core.extensions.icepak.model_reviewer.backend import get_object_id_mapping
from ansys.aedt.core.extensions.icepak.model_reviewer.backend import import_config_file
from ansys.aedt.core.extensions.icepak.model_reviewer.configuration_data_processing import (
    compare_and_update_boundary_data,
)
from ansys.aedt.core.extensions.icepak.model_reviewer.configuration_data_processing import (
    compare_and_update_material_data,
)
from ansys.aedt.core.extensions.icepak.model_reviewer.configuration_data_processing import compare_and_update_model_data
from ansys.aedt.core.extensions.icepak.model_reviewer.configuration_data_processing import extract_boundary_data
from ansys.aedt.core.extensions.icepak.model_reviewer.configuration_data_processing import extract_material_data
from ansys.aedt.core.extensions.icepak.model_reviewer.configuration_data_processing import extract_model_data
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
theme = ExtensionTheme()
EXTENSION_TITLE = "Icepak Model Reviewer"


def flatten_list(mixed_list):
    flat_list = []
    for row in mixed_list:
        result = []
        for item in row:
            if isinstance(item, list):
                result.append(",".join(str(sub) for sub in item))
            else:
                result.append(str(item))
        flat_list.append(result)
    return flat_list


def expand_list(flat_list):
    mixed_list = []
    for row in flat_list:
        result = []
        for item in row:
            if isinstance(item, str) and "," in item:
                parts = [s.strip() for s in item.split(",")]
                result.append(parts)
            else:
                result.append(str(item))
        mixed_list.append(result)
    return mixed_list


def add_icon_to_cells(data, icon_indices, icon="🔒"):
    """
    Adds an icon to specified cells in the data.

    Parameters
    ----------
    - data: list of list of strings (table rows)
    - icon_indices: list of list of ints, where each inner list contains read only column indices
    - icon: string icon to prepend (default '🔒')

    Returns
    -------
    - new_data: deep copy of data with icons added
    """
    from copy import deepcopy

    new_data = deepcopy(data)

    for row_idx, cols in enumerate(icon_indices):
        for col_idx in cols:
            cell = new_data[row_idx][col_idx - 1]
            if isinstance(cell, str):
                new_data[row_idx][col_idx - 1] = f"{cell}{icon}"
            elif isinstance(cell, list):
                cell[-1] += icon
                new_data[row_idx][col_idx - 1] = cell
    return new_data


def remove_icon_from_cells(data, icon="🔒"):
    """
    Removes the icon from all cells that start with it.

    Parameters
    ----------
    - data: list of list of strings
    - icon: the icon to remove (default '🔒')

    Returns
    -------
    - new_data: deep copy of data with icons removed
    """
    from copy import deepcopy

    new_data = deepcopy(data)

    for i, row in enumerate(new_data):
        for j, cell in enumerate(row):
            if isinstance(cell, str):
                if cell.endswith(f"{icon}"):  # cells can also be list in case of multiple selection
                    new_data[i][j] = cell[: -(len(icon))]
            if isinstance(cell, list):
                if cell[-1].endswith(icon):
                    cell[-1] = cell[-1][: -(len(icon))]
    return new_data


def add_table_to_tab(tab, table_data):
    for child in tab.winfo_children():
        child.destroy()
    headings, type_list, selection_dict, row_data, read_only_cols = table_data
    table = Table(tab, headings, type_list, read_only_cols)
    table.pack(fill=tk.BOTH, expand=True)
    for column_name, options in selection_dict.items():
        table.set_multi_select_options(column_name, options)
    row_data_with_icon = add_icon_to_cells(flatten_list(row_data), read_only_cols)
    for row in row_data_with_icon:
        table.add_row(row)
    return table


class Table(ttk.Frame):
    def __init__(self, parent, headers, types, read_only_data):
        super().__init__(parent, style="PyAEDT.TFrame")
        self.headers = ["✔"] + headers
        self.types = ["checkbox"] + types
        self.read_only_data = [set(r) for r in read_only_data]
        self.tree = ttk.Treeview(
            self, columns=self.headers, show="headings", selectmode="browse", style="PyAEDT.Treeview"
        )
        for i, header in enumerate(self.headers):
            self.tree.heading(header, text=header)
            self.tree.column(header, width=50 if i == 0 else 140, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-1>", self.edit_cell)

        self.rows_data = []
        self.multi_select_options = {}
        self.selected_rows = set()

    def set_multi_select_options(self, header, options):
        self.multi_select_options[header] = options

    def add_row(self, row_data):
        if len(row_data) != len(self.headers) - 1:
            raise ValueError("Row data must match the number of non-checkbox columns")

        full_data = ["⬜"] + row_data
        self.rows_data.append(full_data)
        self.tree.insert("", "end", values=full_data)

    def toggle_row(self, row_id):
        if row_id in self.selected_rows:
            self.selected_rows.remove(row_id)
            self.tree.set(row_id, 0, "⬜")
        else:
            self.selected_rows.add(row_id)
            self.tree.set(row_id, 0, "✅")

    def get_modified_data(self):
        return [self.tree.item(row)["values"][1:] for row in self.tree.get_children()]

    def update_cell_value(self, row_id, col, new_value):
        """Modified data update logic decoupled from UI events."""
        # Determine which rows to update (bulk edit if selected)
        if row_id in self.selected_rows:
            targets = self.selected_rows
        else:
            targets = {row_id}
        for rid in targets:
            idx = self.tree.index(rid)
            # Check read-only constraint
            if col not in self.read_only_data[idx]:
                self.tree.set(rid, col, new_value)
                # Update the underlying data list
                self.rows_data[idx][col] = new_value

    def edit_cell(self, event):

        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col = int(self.tree.identify_column(event.x)[1:]) - 1
        item_index = self.tree.index(row_id)

        if col == 0:
            self.toggle_row(row_id)
            return

        if col in self.read_only_data[item_index]:
            return

        bbox = self.tree.bbox(row_id, f"#{col + 1}")
        if not bbox:
            return

        x, y, width, height = bbox
        abs_x = self.tree.winfo_rootx() + x
        abs_y = self.tree.winfo_rooty() + y

        item = self.tree.item(row_id)
        value = item["values"][col]
        type_ = self.types[col]

        def apply_to_selected(new_value):
            self.update_cell_value(row_id, col, new_value)

        if type_ == "text":
            entry = tk.Entry(self.tree)
            entry.insert(0, value)
            entry.place(x=x, y=y, width=width, height=height)
            entry.focus_set()

            def on_return(event):
                new_value = entry.get()
                apply_to_selected(new_value)
                entry.destroy()

            entry.bind("<Return>", on_return)
            entry.bind("<FocusOut>", lambda e: entry.destroy())

        elif type_ == "combo":
            options = self.multi_select_options.get(self.headers[col], [])
            combo = ttk.Combobox(
                self.tree, values=options, state="readonly", style="PyAEDT.TCombobox", font=theme.default_font
            )
            combo.place(x=x, y=y, width=width, height=height)
            combo.set(value)

            def on_select(event=None):
                new_value = combo.get()
                apply_to_selected(new_value)
                combo.destroy()

            combo.bind("<<ComboboxSelected>>", on_select)
            combo.bind("<FocusOut>", lambda e: combo.destroy())
            combo.focus_set()

        elif type_ == "multiple_text":
            options = self.multi_select_options.get(self.headers[col], [])
            top = tk.Toplevel(self)
            top.title("Select Multiple")
            top.geometry(f"200x300+{abs_x}+{abs_y}")

            listbox = tk.Listbox(top, selectmode="multiple", font=theme.default_font)
            for opt in options:
                listbox.insert(tk.END, opt)
            listbox.pack(fill="both", expand=True)

            current_vals = [val.strip() for val in value.split(",")]
            for idx, opt in enumerate(options):
                if opt in current_vals:
                    listbox.selection_set(idx)

            def confirm():
                selected = [options[i] for i in listbox.curselection()]
                value_str = ", ".join(selected)
                apply_to_selected(value_str)
                top.destroy()

            ttk.Button(top, text="OK", command=confirm).pack()
            top.transient(self)
            top.grab_set()
            self.wait_window(top)


class IcepakModelReviewer(ExtensionCommon):
    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )

        self.differences = None
        self.combined_data = None
        self.add_extension_content()

    def add_extension_content(self):
        # --- Top Button Panel ---
        button_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        notebook = ttk.Notebook(self.root, style="TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)
        self.root.boundary_tab = ttk.Frame(notebook, style="PyAEDT.TFrame")
        notebook.add(self.root.boundary_tab, text="Boundary")
        self.root.materials_tab = ttk.Frame(notebook, style="PyAEDT.TFrame")
        notebook.add(self.root.materials_tab, text="Material")
        self.root.models_tab = ttk.Frame(notebook, style="PyAEDT.TFrame")
        notebook.add(self.root.models_tab, text="Models")
        self.load_button = ttk.Button(
            button_frame, text="Load Project", command=self.load_project, style="PyAEDT.TButton"
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.update_button = ttk.Button(
            button_frame, text="Update Project", command=self.update_project, style="PyAEDT.TButton"
        )
        self.update_button.pack(side=tk.LEFT, padx=5)
        lower_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        lower_frame.pack(fill=tk.X, padx=10, pady=5)
        self.add_toggle_theme_button(lower_frame, 0, 0)

    def check_design_type(self):
        """Check if the active design is an Icepak design."""
        if self.aedt_application.design_type != "Icepak":
            raise AEDTRuntimeError("This extension can only be used with Icepak designs.")

    def get_project_data(self):
        desktop = Desktop(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student(),
        )
        ipk = Icepak()
        data = export_config_file(ipk)
        ipk.logger.info("Loading project details into Table")
        if "PYTEST_CURRENT_TEST" not in os.environ:
            desktop.release_desktop(close_projects=False, close_on_exit=False)
        return data

    def import_data_to_project(self, combined_data, differences):
        desktop = Desktop(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student(),
        )
        ipk = Icepak()
        ipk.logger.info("Updating the project based on modified table data")
        ipk.logger.info("Following modifications are made in the table")
        ipk.logger.info(differences)
        import_config_file(ipk, combined_data)
        if "PYTEST_CURRENT_TEST" not in os.environ:
            desktop.release_desktop(False, False)

    def object_id_mapping(self):
        desktop = Desktop(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student(),
        )
        ipk = Icepak()
        mapping = get_object_id_mapping(ipk)
        if "PYTEST_CURRENT_TEST" not in os.environ:
            desktop.release_desktop(False, False)
        return mapping

    def load_project(self):
        data = self.get_project_data()
        self.root.json_data = data

        # --- Tabbed Interface ---
        table_data = extract_boundary_data(data)
        self.root.bc_table = add_table_to_tab(self.root.boundary_tab, table_data)
        table_data = extract_material_data(data)
        self.root.mat_table = add_table_to_tab(self.root.materials_tab, table_data)
        table_data = extract_model_data(data)
        self.root.model_table = add_table_to_tab(self.root.models_tab, table_data)

    def update_project(self):
        obj_mapping = self.object_id_mapping()
        bc_data = self.root.bc_table.get_modified_data()
        bc_data = expand_list(remove_icon_from_cells(bc_data))
        bc_differences, new_bc_data = compare_and_update_boundary_data(self.root.json_data, bc_data, obj_mapping)
        mat_data = self.root.mat_table.get_modified_data()
        mat_data = expand_list(remove_icon_from_cells(mat_data))
        mat_differences, new_mat_data = compare_and_update_material_data(self.root.json_data, mat_data)
        model_data = self.root.model_table.get_modified_data()
        model_data = expand_list(remove_icon_from_cells(model_data))
        model_differences, new_model_data = compare_and_update_model_data(self.root.json_data, model_data)
        self.combined_data = {**new_model_data, **new_mat_data, **new_bc_data}
        self.differences = bc_differences + mat_differences + model_differences
        self.import_data_to_project(self.combined_data, self.differences)


if __name__ == "__main__":
    extension = IcepakModelReviewer(withdraw=False)
    tk.mainloop()
