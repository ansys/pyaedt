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
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

from pathlib import Path

class Pin:
    def __init__(self, name=None, layer=None, x=None, y=None, diameter=None, via_type="Through"):
        self.name = name
        self.layer = layer
        self.x = x
        self.y = y
        self.diameter = diameter
        self.via_type = via_type
    
    def to_dict(self):
        return {
            "name": self.name,
            "layer": self.layer,
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "via_type": self.via_type
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            layer=data.get("layer"),
            x=data.get("x"),
            y=data.get("y"),
            diameter=data.get("diameter"),
            via_type=data.get("via_type", "Through")
        )

# Note: Removed global pin_map_data variable - now using config_model directly


def create_pin_map_settings_ui(tab_frame, app_instance):
    style = ttk.Style()
    style.configure("PyAEDT.Treeview", rowheight=25)
    style.map("PyAEDT.Treeview",
              foreground=[('selected', '#000000')],
              background=[('selected', '#CCE4F7')])

    # UI variables have been created during tab initialization, no need to check here

    # Pin Map
    params_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    params_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(5, 0))

    ttk.Label(params_frame, text="Pitch X", style="PyAEDT.TLabel").grid(row=0, column=0)
    app_instance.pinmap_ui_vars.pitch_x_entry = ttk.Entry(params_frame, width=15)
    app_instance.pinmap_ui_vars.pitch_x_entry.insert(0, "1000um")
    app_instance.pinmap_ui_vars.pitch_x_entry.grid(row=0, column=1)
    
    ttk.Label(params_frame, text="Pitch Y", style="PyAEDT.TLabel").grid(row=0, column=2, padx=5)
    app_instance.pinmap_ui_vars.pitch_y_entry = ttk.Entry(params_frame, width=15)
    app_instance.pinmap_ui_vars.pitch_y_entry.insert(0, "1000um")
    app_instance.pinmap_ui_vars.pitch_y_entry.grid(row=0, column=3)
    
    ttk.Label(params_frame, text="Num of Single Nets", style="PyAEDT.TLabel").grid(row=0, column=4, padx=5)
    app_instance.pinmap_ui_vars.single_nets_combo = ttk.Combobox(params_frame, width=5, values=list(range(6)))
    app_instance.pinmap_ui_vars.single_nets_combo.grid(row=0, column=5)
    app_instance.pinmap_ui_vars.single_nets_combo.set("4")
    
    ttk.Label(params_frame, text="Num of Diff Pairs", style="PyAEDT.TLabel").grid(row=0, column=6, padx=5)
    app_instance.pinmap_ui_vars.diff_pairs_combo = ttk.Combobox(params_frame, width=5, values=list(range(6)))
    app_instance.pinmap_ui_vars.diff_pairs_combo.grid(row=0, column=7)
    app_instance.pinmap_ui_vars.diff_pairs_combo.set("2")
    
    ttk.Label(params_frame, text="Num of Rows", style="PyAEDT.TLabel").grid(row=0, column=8, padx=5)
    app_instance.pinmap_ui_vars.rows_combo = ttk.Combobox(params_frame, width=5, values=list(range(1, 11)), state="normal")
    app_instance.pinmap_ui_vars.rows_combo.grid(row=0, column=9)
    app_instance.pinmap_ui_vars.rows_combo.set("3")
    
    ttk.Label(params_frame, text="Num of Column", style="PyAEDT.TLabel").grid(row=0, column=10, padx=5)
    app_instance.pinmap_ui_vars.columns_combo = ttk.Combobox(params_frame, width=5, values=list(range(1, 11)), state="normal")
    app_instance.pinmap_ui_vars.columns_combo.grid(row=0, column=11)
    app_instance.pinmap_ui_vars.columns_combo.set("3")
    
    ttk.Button(params_frame, text="Generate", command=lambda: generate_pin_map(app_instance), style="PyAEDT.TButton").grid(row=0, column=12, padx=20)


    # Pin Map table
    table_frame = ttk.LabelFrame(tab_frame, style="PyAEDT.TLabelframe")
    table_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
    tab_frame.grid_rowconfigure(2, weight=1)
    tab_frame.grid_columnconfigure(0, weight=1)
    
    # Create table container
    table_container = ttk.Frame(table_frame, style="PyAEDT.TFrame")
    table_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Create scrollbar
    canvas = tk.Canvas(table_container, bg='white')
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="PyAEDT.TFrame")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create table header
    header_frame = ttk.Frame(scrollable_frame, style="PyAEDT.TFrame")
    header_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
    
    # Store reference to table header frame
    app_instance.pinmap_ui_vars.header_frame = header_frame
    
    # Initialize table header
    create_table_headers(app_instance)
    
    # Container for storing table data
    app_instance.pinmap_ui_vars.pin_grid_frame = ttk.Frame(scrollable_frame, style="PyAEDT.TFrame")
    app_instance.pinmap_ui_vars.pin_grid_frame.grid(row=1, column=0, sticky='ew', padx=2, pady=2)

    # Bottom button
    button_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=4, column=0, sticky='ew', pady=5)
    
    # Configure button_frame to make it resizable
    button_frame.grid_columnconfigure(3, weight=1)  # Last column takes remaining space
    
    ttk.Button(button_frame, text="Reset", command=lambda: reset_pin_map(app_instance), style="PyAEDT.TButton").grid(row=0, column=0, padx=5, sticky='e')

    # Initialize table data
    update_pin_tree(app_instance)
    

# Create table headers based on column count
def create_table_headers(app_instance, num_columns=None):
    # Clear existing headers
    for widget in app_instance.pinmap_ui_vars.header_frame.winfo_children():
        widget.destroy()
    
    # If num_columns is not provided, get it from combo box
    if num_columns is None:
        try:
            num_columns = int(app_instance.pinmap_ui_vars.columns_combo.get())
        except (ValueError, AttributeError):
            num_columns = 3  # Default to 3 columns
    
    # Generate column names: Index + A, B, C, ...
    columns = ['Index']
    for i in range(num_columns):
        columns.append(chr(ord('A') + i))
    
    # Create header labels
    for i, col in enumerate(columns):
        width = 6 if col == 'Index' else 10
        label = ttk.Label(app_instance.pinmap_ui_vars.header_frame, text=col, style="PyAEDT.TLabel", width=width, anchor='center')
        label.grid(row=0, column=i, padx=1, pady=1, sticky='ew')
        if col != 'Index':
            app_instance.pinmap_ui_vars.header_frame.grid_columnconfigure(i, weight=1)

# Update table display
def update_pin_tree(app_instance, use_config_data=True):
    # Clear existing widgets and data
    for widget_row in app_instance.pinmap_ui_vars.pin_grid_widgets:
        for widget in widget_row:
            widget.destroy()
    app_instance.pinmap_ui_vars.pin_grid_widgets.clear()
    app_instance.pinmap_ui_vars.pin_grid_data.clear()
    
    # Get number of columns from the combo box
    try:
        num_columns = int(app_instance.pinmap_ui_vars.columns_combo.get())
    except (ValueError, AttributeError):
        num_columns = 3  # Default to 3 columns
    
    # Get number of rows from the combo box
    try:
        num_rows = int(app_instance.pinmap_ui_vars.rows_combo.get())
    except (ValueError, AttributeError):
        num_rows = 3  # Default to 3 rows
    
    # Dynamically generate dropdown options
    pin_options = ["VSS", "VDD", "GND"]  # Basic options
    
    # Extract generated pin names from config_model
    if hasattr(app_instance, 'config_model') and app_instance.config_model.placement.pin_map:
        # Get pin names from config model if available
        pass  # Pin options are already set above
    
    # If config_model.placement.pin_map exists, also add options from it
    config_pin_map = None
    if use_config_data:
        try:
            if (hasattr(app_instance, 'config_model') and 
                hasattr(app_instance.config_model, 'placement') and 
                hasattr(app_instance.config_model.placement, 'pin_map')):
                config_pin_map = app_instance.config_model.placement.pin_map
                if config_pin_map:
                    # Extract all unique pin names from configuration data
                    for row in config_pin_map:
                        for pin_name in row:
                            if pin_name not in pin_options:
                                pin_options.append(pin_name)
        except AttributeError:
            pass
    
    # Remove duplicates and maintain order
    pin_options = list(dict.fromkeys(pin_options))
    
    # Use configuration data's row and column count only during initialization
    if use_config_data and config_pin_map:
        num_rows = len(config_pin_map)
        num_columns = len(config_pin_map[0]) if config_pin_map else num_columns
        # Update combo box values to reflect actual data
        app_instance.pinmap_ui_vars.rows_combo.set(str(num_rows))
        app_instance.pinmap_ui_vars.columns_combo.set(str(num_columns))
    
    # Update table header using determined column count
    create_table_headers(app_instance, num_columns)
    
    # Create data for specified number of rows
    for row_idx in range(num_rows):
        # Create row data
        if config_pin_map and row_idx < len(config_pin_map):
            # Use configuration data
            row_data = config_pin_map[row_idx][:num_columns]  # Ensure not exceeding column count
            # If configuration data has insufficient columns, fill with default values
            while len(row_data) < num_columns:
                row_data.append("VSS")
        else:
            # Use default data
            row_data = ["VSS"] * num_columns
        
        app_instance.pinmap_ui_vars.pin_grid_data.append(row_data)
        
        # Create row widgets
        row_widgets = []
        
        # Index column (label)
        index_label = ttk.Label(app_instance.pinmap_ui_vars.pin_grid_frame, text=str(row_idx + 1), 
                               style="PyAEDT.TLabel", width=6, anchor='center')
        index_label.grid(row=row_idx, column=0, padx=1, pady=1, sticky='ew')
        row_widgets.append(index_label)
        
        # Dynamic columns (dropdowns)
        for col_idx in range(num_columns):
            combo = ttk.Combobox(app_instance.pinmap_ui_vars.pin_grid_frame, values=pin_options, 
                               width=8, style="PyAEDT.TCombobox", state="readonly")
            # Set actual value
            combo.set(row_data[col_idx])
            combo.grid(row=row_idx, column=col_idx + 1, padx=1, pady=1, sticky='ew')
            
            # Bind value change event
            def on_combo_change(event, r=row_idx, c=col_idx):
                app_instance.pinmap_ui_vars.pin_grid_data[r][c] = event.widget.get()
            combo.bind('<<ComboboxSelected>>', on_combo_change)
            
            row_widgets.append(combo)
            # Set column weight
            app_instance.pinmap_ui_vars.pin_grid_frame.grid_columnconfigure(col_idx + 1, weight=1)
        
        app_instance.pinmap_ui_vars.pin_grid_widgets.append(row_widgets)


def save_pin_map_to_config(app_instance):
    """Save current table area data as 2D array to config_model.placement.pin_map"""
    try:
        if hasattr(app_instance, 'config_model'):
            # Ensure config_model has placement attribute
            if not hasattr(app_instance.config_model, 'placement'):
                # This should not happen if ConfigModel is properly initialized
                # Warning: config_model.placement not found
                return
            
            # Ensure placement has pin_map attribute
            if not hasattr(app_instance.config_model.placement, 'pin_map'):
                app_instance.config_model.placement.pin_map = []
            
            # Save current table's pin_grid_data as 2D array
            app_instance.config_model.placement.pin_map = [row[:] for row in app_instance.pinmap_ui_vars.pin_grid_data]  # Deep copy
    except Exception as e:
        # Error saving pin map to config
        pass


# Generate pin map based on parameters
def generate_pin_map(app_instance):
    try:
        # Get parameter values
        pitch_x = app_instance.pinmap_ui_vars.pitch_x_entry.get()
        pitch_y = app_instance.pinmap_ui_vars.pitch_y_entry.get()
        num_rows = int(app_instance.pinmap_ui_vars.rows_combo.get())
        num_cols = int(app_instance.pinmap_ui_vars.columns_combo.get())
        num_single_nets = int(app_instance.pinmap_ui_vars.single_nets_combo.get())
        num_diff_pairs = int(app_instance.pinmap_ui_vars.diff_pairs_combo.get())
        # arrangement_type = app_instance.arrangement_var.get()
        
        # Generate net names
        net_names = []
        
        # Add single nets
        for i in range(num_single_nets):
            net_names.append(f"SIG_{i+1}")
        
        # Add differential pairs
        for i in range(num_diff_pairs):
            net_names.append(f"SIG_{i+1}_P")
            net_names.append(f"SIG_{i+1}_N")
        
        # Update config model with new parameters
        app_instance.config_model.placement.pitch_x = float(pitch_x.replace('um', '')) if pitch_x else 1.0
        app_instance.config_model.placement.pitch_y = float(pitch_y.replace('um', '')) if pitch_y else 1.0
        app_instance.config_model.placement.num_single_nets = num_single_nets
        app_instance.config_model.placement.num_diff_pairs = num_diff_pairs
        
        # Clear existing data
        app_instance.pinmap_ui_vars.pin_grid_data.clear()
        
        # Generate pin data based on parameters
        net_index = 0
        for row in range(num_rows):
            row_data = []
            for col in range(num_cols):
                if net_index < len(net_names):
                    row_data.append(net_names[net_index])
                    net_index += 1
                else:
                    row_data.append("VSS")
            app_instance.pinmap_ui_vars.pin_grid_data.append(row_data)
        
        # Update table display (don't use config data, use user-set row/column count)
        update_pin_tree(app_instance, use_config_data=False)
        
        # After Generate completion, save current table data to config_model
        save_pin_map_to_config(app_instance)
        
        messagebox.showinfo("Success", f"Generated {num_rows * num_cols} pins")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate pin map: {str(e)}")


def reset_pin_map(app_instance):
    """Reset the pin map configuration to default values from config_model.
    
    Args:
        app_instance: The main application instance containing pin map data
    """
    confirmation_msg = "Are you sure you want to reset the pin map? All changes will be lost."
    if messagebox.askyesno("Confirmation", confirmation_msg):
        # Read default values from config_model.pin_map and update table
        update_pin_tree(app_instance, use_config_data=True)
