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
import os
from unittest.mock import patch

import pytest
import tkinter as tk
from tkinter import ttk

from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import EXTENSION_TITLE, add_table_to_tab
from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import IcepakModelReviewer
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import Table
from tests import TESTS_UNIT_PATH
from ansys.aedt.core.icepak import Icepak
from pathlib import Path

AEDT_FILENAME = "Graphics_Card"
CONFIG_FILE = "Modified_Data.json"
TEST_SUBFOLDER = "T45"
AEDT_FILE_PATH = Path(__file__).parent / "example_models" / TEST_SUBFOLDER / (AEDT_FILENAME + ".aedt")



def config_file_load():
    config_file = os.path.join(TESTS_UNIT_PATH, "extensions", "graphics_card.json")
    with open(config_file, "r") as file:
        data = json.load(file)
    return data


def mapping_load():
    mapping_file = os.path.join(TESTS_UNIT_PATH, "extensions", "mapping.json")
    with open(mapping_file, "r") as file:
        data = json.load(file)
    return data



@pytest.fixture
def patched_loader():
    with patch.object(IcepakModelReviewer, "get_project_data", side_effect=config_file_load) as mock_loader:
        yield mock_loader


@pytest.fixture
def patched_object_id():
    with patch.object(IcepakModelReviewer, "object_id_mapping", side_effect=mapping_load) as mock_loader:
        yield mock_loader


@pytest.fixture
def patched_import_data_to_project():
    with patch.object(IcepakModelReviewer, "import_data_to_project", return_value=None) as mock_loader:
        yield mock_loader


theme = ExtensionTheme()


def add_icon_to_cells(data, read_only): return data


def flatten_list(data): return data


# --- Pytest Fixture ---
@pytest.fixture
def table_app():
    root = tk.Tk()
    root.geometry("800x500")  # Set a size so it's visible
    #root.withdraw()
    # --- 1. MOCK DATA ---
    headings = ["Name", "Type", "Objects"]
    type_list = ["text", "combo", "multiple_text"]
    selection_dict = {
        "Type": ["Solid", "Fluid"],
        "Objects": ["CPU", "DDR", "RAM"]
    }
    row_data = [["BC1", "Solid", ["CPU"]]]
    read_only_cols = [[]]

    # --- 2. CORRECT LAYOUT ---
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)  # Must pack the notebook!

    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Mock Tab")  # Must add the frame to the notebook!

    table_data = (headings, type_list, selection_dict, row_data, read_only_cols)
    table = add_table_to_tab(tab, table_data)

    # --- 3. PROCESS EVENTS WITHOUT BLOCKING ---
    root.update_idletasks()
    root.update()
    #root.mainloop()
    # We do NOT use root.mainloop() here because it blocks pytest.
    # root.update() is enough to render the window for the test.

    yield root, table

    root.destroy()
# --- Main Test Case ---
def test_ui_edit_workflow(table_app):
    root, table = table_app
    tree = table.tree
    row_id = tree.get_children()[0]
    tree.see(row_id)
    # ==========================================================
    # 1. TESTING THE 'TEXT' COLUMN (#2)
    # ==========================================================
    # Locate cell, simulate click, and type text
    x, y, w, h = tree.bbox(row_id, "#2")
    event = tk.Event()
    event.x, event.y = x + 200, y + 20
    table.edit_cell(event)

    # Find the Entry widget that was dynamically created
    entry = next(c for c in tree.winfo_children() if isinstance(c, tk.Entry))
    entry.delete(0, tk.END)
    entry.insert(0, "BC2")
    tree.update()
    entry.event_generate("<Return>")  # Simulate pressing Enter to save
    assert tree.set(row_id, "#2") == "BC2"

    # ==========================================================
    # 2. TESTING THE 'COMBO' COLUMN (#3)
    # ==========================================================
    # Locate cell, simulate click, and select from dropdown
    x, y, w, h = tree.bbox(row_id, "#3")
    event.x, event.y = x + 200, y + 20
    table.edit_cell(event)

    # Find the Combobox widget that was dynamically created
    combo = next(c for c in tree.winfo_children() if isinstance(c, ttk.Combobox))
    combo.set("Fluid")
    combo.event_generate("<<ComboboxSelected>>")  # Trigger selection event
    tree.update()
    assert tree.set(row_id, "#3") == "Fluid"

    # ==========================================================
    # 3. TESTING THE 'MULTIPLE_TEXT' COLUMN (#4)
    # ==========================================================
    x, y, w, h = tree.bbox(row_id, "#4")
    event.x, event.y = x + 200, y + 20  # Adjust to hit the cell

    def handle_toplevel():
        # 1. Find the Toplevel window
        # We look for a Toplevel that is a child of the table
        top = next(c for c in table.winfo_children() if isinstance(c, tk.Toplevel))

        # 2. Find the Listbox inside that Toplevel
        listbox = next(c for c in top.winfo_children() if isinstance(c, tk.Listbox))

        # 3. Select specific indices (e.g., first and second items)
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(0)
        listbox.selection_set(1)

        # 4. Find and click the 'OK' button
        ok_btn = next(c for c in top.winfo_children() if isinstance(c, ttk.Button))
        ok_btn.invoke()

    # Schedule the handler to run once the mainloop starts waiting for the window
    table.after(100, handle_toplevel)

    # This call will block due to self.wait_window(top),
    # but the after() scheduled above will execute.
    table.edit_cell(event)
    tree.update()
    # Verify the result (comma-separated string)
    # Note: Ensure these expected values match your multi_select_options
    # expected_val = f"{table.multi_select_options[table.headers[3]][0]}, {table.multi_select_options[table.headers[3]][1]}"
    assert tree.set(row_id, "#4") == "CPU, DDR"



def test_icepak_model_reviewer(mock_icepak_app):
    """Test instantiation of the IcepakModelReviewer."""
    extension = IcepakModelReviewer(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_icepak_model_reviewer_load_project(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    assert boundary_table.tree is not None
    assert len(boundary_table.tree.get_children()) == 3


def test_icepak_model_reviewer_table_values(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1, row2, row3 = boundary_table.tree.get_children()[:3]
    assert boundary_table.tree.column(5)["id"] == "Value 1"
    assert boundary_table.tree.item(row1)["values"][5] == "4W"
    assert boundary_table.tree.item(row1)["values"][3] == "CPU,KB,HEAT_SINK"
    assert boundary_table.tree.item(row2)["values"][5] == "5w_per_m3"
    assert boundary_table.tree.item(row2)["values"][3] == "MEMORY1,MEMORY1_1"
    assert boundary_table.tree.item(row3)["values"][5] == "1W"
    materials_table = extension.root.materials_tab.winfo_children()[0]
    assert len(materials_table.tree.get_children()) == 4
    row1, row2, row3, row4 = materials_table.tree.get_children()[:4]
    assert materials_table.tree.item(row1)["values"][1] == "Al-Extruded🔒"
    assert materials_table.tree.item(row1)["values"][2] == "Solid🔒"
    assert materials_table.tree.item(row1)["values"][3] == 152
    assert materials_table.tree.item(row1)["values"][4] == 2000
    assert materials_table.tree.item(row2)["values"][4] == "1.1614"
    assert materials_table.tree.item(row3)["values"][5] == 2
    assert materials_table.tree.item(row4)["values"][6] == 0
    model_table = extension.root.models_tab.winfo_children()[0]
    assert len(model_table.tree.get_children()) == 11
    row1, row2, row3 = model_table.tree.get_children()[:3]
    assert model_table.tree.item(row1)["values"][2] == "air"
    assert model_table.tree.item(row2)["values"][3] == "Soft Rubber-Gray-surface"
    assert model_table.tree.item(row3)["values"][4] == "True"
    assert model_table.tree.item(row3)["values"][5] == "Model"


def test_table_icon_handling_after_load(mock_icepak_app, patched_loader):
    """Verify that all read-only cells in the table have the 🔒 icon appended."""
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()

    for tab_name in ["boundary_tab", "materials_tab", "models_tab"]:
        table = getattr(extension.root, tab_name).winfo_children()[0]
        tree = table.tree
        rows = tree.get_children()
        # For every row, check each read-only column
        for row_index, row_id in enumerate(rows):
            values = tree.item(row_id)["values"]
            readonly_cols = table.read_only_data[row_index]

            for col_index, value in enumerate(values):  # 1-based index for consistency
                val_str = str(value)
                if col_index in readonly_cols:
                    assert val_str.endswith("🔒")
                else:
                    assert not val_str.endswith("🔒")


def test_table_headers_and_types_consistency(mock_icepak_app, patched_loader):
    """
    Verify:
    - each table has consistent header/type pairing
    - 'multiple_text' columns contain comma-separated values
    """
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()

    for tab_name in ["boundary_tab", "materials_tab", "models_tab"]:
        table = getattr(extension.root, tab_name).winfo_children()[0]
        headers = table.headers
        types = table.types
        tree = table.tree

        # --- 1Check header/type consistency ---
        assert len(headers) == len(types), f"{tab_name} headers/types mismatch"

        # --- multiple_text columns should have comma-separated values ---
        multi_text_indices = [i for i, t in enumerate(types) if t == "multiple_text"]
        if multi_text_indices:
            found_multi = False
            for row_id in tree.get_children():
                values = tree.item(row_id)["values"]
                for idx in multi_text_indices:
                    if idx < len(values) and "," in str(values[idx]):
                        found_multi = True
                        break
                if found_multi:
                    break
            assert found_multi


def test_table_reload_does_not_duplicate(mock_icepak_app, patched_loader):
    """Ensure multiple loads don't duplicate table entries."""
    extension = IcepakModelReviewer(withdraw=True)

    extension.load_button.invoke()
    first_load_rows = len(extension.root.boundary_tab.winfo_children()[0].tree.get_children())

    # Invoke load again
    extension.load_button.invoke()
    second_load_rows = len(extension.root.boundary_tab.winfo_children()[0].tree.get_children())

    assert first_load_rows == second_load_rows


def test_icepak_model_reviewer_table_modification(
    mock_icepak_app, patched_loader, patched_import_data_to_project, patched_object_id
):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    boundary_table.tree.set(row1, column="Value 1", value="2W")
    boundary_table.tree.set(row1, column="Selected Objects", value="CPU,KB")
    boundary_table.tree.set(row2, column="Value 1", value="2w_per_m3")
    boundary_table.tree.set(row3, column="Value 1", value="1.5W")
    extension.update_button.invoke()
    assert extension.combined_data["boundaries"]["CPU"]["Total Power"] == "2W"
    assert extension.combined_data["boundaries"]["CPU"]["Objects"] == [422, 150]
    assert extension.combined_data["boundaries"]["Memory"]["Power Density"] == "2w_per_m3"
    assert extension.combined_data["boundaries"]["Source1"]["Total Power"] == "1.5W"
    material_table = extension.root.materials_tab.winfo_children()[0]
    row1 = material_table.tree.get_children()[0]
    row2 = material_table.tree.get_children()[1]
    row3 = material_table.tree.get_children()[2]
    material_table.tree.set(row1, column="Thermal Conductivity", value="150")
    material_table.tree.set(row2, column="Mass Density", value="1.2")
    material_table.tree.set(row3, column="Specific Heat", value="4")
    extension.update_button.invoke()
    assert extension.combined_data["materials"]["Al-Extruded"]["thermal_conductivity"] == "150"
    assert extension.combined_data["materials"]["air"]["mass_density"] == "1.2"
    assert extension.combined_data["materials"]["PCB_Material"]["specific_heat"] == "4"
    model_table = extension.root.models_tab.winfo_children()[0]
    row1 = model_table.tree.get_children()[1]
    row2 = model_table.tree.get_children()[2]
    model_table.tree.set(row1, column="Modeling", value="Non-Model")
    model_table.tree.set(row2, column="Bulk Material", value="Al-Extruded")
    extension.update_button.invoke()
    assert extension.combined_data["objects"]["MEMORY1"]["Material"] == "Al-Extruded"
    assert extension.combined_data["objects"]["SERIAL_PORT"]["Model"] == "False"


def test_icepak_table_modification(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()

    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]

    # 1. TEST PROGRAMMATIC MODIFICATION
    # Simulates changing 'Value 1' (Col 5) to '10W'
    boundary_table.update_cell_value(row1, 5, "10W")
    assert boundary_table.tree.item(row1)["values"][5] == "10W"

    # 2. TEST BULK EDITING (UI Logic Coverage)
    row2 = boundary_table.tree.get_children()[2]
    row3 = boundary_table.tree.get_children()[2]
    boundary_table.toggle_row(row1)  # Select row 1
    boundary_table.toggle_row(row2) # Select row 2
    boundary_table.toggle_row(row2) # Unselect row 2
    boundary_table.toggle_row(row3)  # Select row 3

    # Modifying row1 should now also modify row2
    boundary_table.update_cell_value(row1, 5, "99W")
    assert boundary_table.tree.item(row3)["values"][5] == "99W"

