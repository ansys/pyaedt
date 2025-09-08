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

    # Signal and Differential Signal Configuration Section
    signal_frame = ttk.LabelFrame(tab_frame, text="Signal Configuration", style="PyAEDT.TLabelframe")
    signal_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    tab_frame.grid_columnconfigure(0, weight=1)
    
    # Create notebook for signals and differential signals
    signal_notebook = ttk.Notebook(signal_frame, style="PyAEDT.TNotebook")
    signal_notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    signal_frame.grid_rowconfigure(0, weight=1)
    signal_frame.grid_columnconfigure(0, weight=1)
    
    # Signals tab
    signals_tab = ttk.Frame(signal_notebook, style="PyAEDT.TFrame")
    signal_notebook.add(signals_tab, text="Signals")
    
    # Differential Signals tab
    diff_signals_tab = ttk.Frame(signal_notebook, style="PyAEDT.TFrame")
    signal_notebook.add(diff_signals_tab, text="Differential Signals")
    
    # Create signals UI
    create_signals_ui(signals_tab, app_instance)
    
    # Create differential signals UI
    create_diff_signals_ui(diff_signals_tab, app_instance)

    # Pin Map
    params_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    params_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(5, 0))

    ttk.Label(params_frame, text="Pitch", style="PyAEDT.TLabel").grid(row=0, column=0)
    app_instance.pinmap_ui_vars.pitch_entry = ttk.Entry(params_frame, width=15)
    app_instance.pinmap_ui_vars.pitch_entry.insert(0, "1000um")
    app_instance.pinmap_ui_vars.pitch_entry.grid(row=0, column=1)
    
    # ttk.Label(params_frame, text="Pitch Y", style="PyAEDT.TLabel").grid(row=0, column=2, padx=5)
    # app_instance.pinmap_ui_vars.pitch_y_entry = ttk.Entry(params_frame, width=15)
    # app_instance.pinmap_ui_vars.pitch_y_entry.insert(0, "1000um")
    # app_instance.pinmap_ui_vars.pitch_y_entry.grid(row=0, column=3)
    
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
    
    # Only add generated signal names when not using config data (i.e., after Generate is clicked)
    if not use_config_data:
        try:
            num_single_nets = int(app_instance.pinmap_ui_vars.single_nets_combo.get())
            num_diff_pairs = int(app_instance.pinmap_ui_vars.diff_pairs_combo.get())
            
            # Add single nets to options (independent indexing)
            for i in range(num_single_nets):
                signal_name = f"SIG_{i+1}"
                if signal_name not in pin_options:
                    pin_options.append(signal_name)
            
            # Add differential pairs to options (independent indexing)
            for i in range(num_diff_pairs):
                p_signal = f"SIG_{i+1}_P"
                n_signal = f"SIG_{i+1}_N"
                if p_signal not in pin_options:
                    pin_options.append(p_signal)
                if n_signal not in pin_options:
                    pin_options.append(n_signal)
        except (ValueError, AttributeError):
            pass
    
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
        pitch = app_instance.pinmap_ui_vars.pitch_entry.get()
        num_rows = int(app_instance.pinmap_ui_vars.rows_combo.get())
        num_cols = int(app_instance.pinmap_ui_vars.columns_combo.get())
        num_single_nets = int(app_instance.pinmap_ui_vars.single_nets_combo.get())
        num_diff_pairs = int(app_instance.pinmap_ui_vars.diff_pairs_combo.get())
        
        # Generate net names
        net_names = []
        
        # Add single nets
        for i in range(num_single_nets):
            net_names.append(f"SIG_{i+1}")
        
        # Add differential pairs (independent indexing)
        for i in range(num_diff_pairs):
            net_names.append(f"SIG_{i+1}_P")
            net_names.append(f"SIG_{i+1}_N")
        
        # Update config model with new parameters
        app_instance.config_model.placement.pitch = pitch
        
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


def create_signals_ui(parent_frame, app_instance):
    """Create UI for signal configuration based on config_model.signals"""
    # Configure parent frame layout
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Signal control buttons area
    signal_buttons_frame = ttk.Frame(parent_frame, style="PyAEDT.TFrame")
    signal_buttons_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5, 0))
    
    # Select all checkbox for bulk operations
    if not hasattr(app_instance, 'signal_ui_vars'):
        app_instance.signal_ui_vars = type('SignalUIVars', (), {})()
    
    app_instance.signal_ui_vars.select_all_var = tk.BooleanVar()
    select_all_check = ttk.Checkbutton(signal_buttons_frame, text="Select All", 
                                      variable=app_instance.signal_ui_vars.select_all_var,
                                      command=lambda: toggle_all_signal_selections(app_instance), 
                                      style="PyAEDT.TCheckbutton")
    select_all_check.grid(row=0, column=0, padx=5, sticky='w')
    
    # Signal management buttons
    add_signal_button = ttk.Button(signal_buttons_frame, text="Add Signal", 
                                  command=lambda: add_signal(app_instance), style="PyAEDT.TButton")
    add_signal_button.grid(row=0, column=1, padx=5, sticky='w')
    
    edit_signal_button = ttk.Button(signal_buttons_frame, text="Edit Signal", 
                                   command=lambda: edit_signal(app_instance), style="PyAEDT.TButton")
    edit_signal_button.grid(row=0, column=2, padx=5, sticky='w')
    
    delete_signal_button = ttk.Button(signal_buttons_frame, text="Delete Signal", 
                                     command=lambda: delete_signal(app_instance), style="PyAEDT.TButton")
    delete_signal_button.grid(row=0, column=3, padx=5, sticky='w')
    
    # Configure button frame layout
    signal_buttons_frame.grid_columnconfigure(4, weight=1)
    
    # Create signals table with columns
    columns = ('Select', 'Signal Name', 'Technology', 'Fanout Traces')
    app_instance.signal_ui_vars.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', 
                                                   selectmode='extended', style="PyAEDT.Treeview")
    
    # Configure checkbox column for signal selection
    app_instance.signal_ui_vars.tree.column('Select', width=80, stretch=False, anchor='center')
    app_instance.signal_ui_vars.tree.heading('Select', text='Select')
    
    # Configure other columns
    app_instance.signal_ui_vars.tree.column('Signal Name', width=150, stretch=True)
    app_instance.signal_ui_vars.tree.heading('Signal Name', text='Signal Name')
    
    app_instance.signal_ui_vars.tree.column('Technology', width=120, stretch=True)
    app_instance.signal_ui_vars.tree.heading('Technology', text='Technology')
    
    app_instance.signal_ui_vars.tree.column('Fanout Traces', width=120, stretch=True)
    app_instance.signal_ui_vars.tree.heading('Fanout Traces', text='Fanout Traces')
    
    # Initialize checkbox states dictionary
    app_instance.signal_ui_vars.checkbox_states = {}
    
    # Add vertical scrollbar for table
    signal_scrollbar = ttk.Scrollbar(parent_frame, orient='vertical', 
                                   command=app_instance.signal_ui_vars.tree.yview, 
                                   style="PyAEDT.Vertical.TScrollbar")
    app_instance.signal_ui_vars.tree.configure(yscrollcommand=signal_scrollbar.set)
    
    # Position table and scrollbar
    app_instance.signal_ui_vars.tree.grid(row=1, column=0, sticky='nsew', padx=(5, 0), pady=5)
    signal_scrollbar.grid(row=1, column=1, sticky='ns', pady=5)
    
    # Add event handling for checkbox clicks
    def handle_signal_click(event):
        region = app_instance.signal_ui_vars.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = app_instance.signal_ui_vars.tree.identify_column(event.x)
            if column == '#1':  # Select column (checkbox column)
                item = app_instance.signal_ui_vars.tree.identify_row(event.y)
                if item:
                    # Toggle checkbox state
                    current_state = app_instance.signal_ui_vars.checkbox_states.get(item, False)
                    new_state = not current_state
                    app_instance.signal_ui_vars.checkbox_states[item] = new_state
                    
                    # Update checkbox symbol
                    values = list(app_instance.signal_ui_vars.tree.item(item, 'values'))
                    values[0] = "☑" if new_state else "☐"
                    app_instance.signal_ui_vars.tree.item(item, values=values)
                    
                    # Update selection
                    if new_state:
                        app_instance.signal_ui_vars.tree.selection_add(item)
                    else:
                        app_instance.signal_ui_vars.tree.selection_remove(item)
    
    app_instance.signal_ui_vars.tree.bind('<Button-1>', handle_signal_click)
    
    # Add double-click to edit
    app_instance.signal_ui_vars.tree.bind('<Double-1>', lambda e: edit_signal(app_instance))
    
    # Update signals table with data
    update_signals_tree(app_instance)


def create_diff_signals_ui(parent_frame, app_instance):
    """Create UI for differential signal configuration based on config_model.differential_signals"""
    # Configure parent frame layout
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Differential signal control buttons area
    diff_signal_buttons_frame = ttk.Frame(parent_frame, style="PyAEDT.TFrame")
    diff_signal_buttons_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5, 0))
    
    # Select all checkbox for bulk operations
    if not hasattr(app_instance, 'diff_signal_ui_vars'):
        app_instance.diff_signal_ui_vars = type('DiffSignalUIVars', (), {})()
    
    app_instance.diff_signal_ui_vars.select_all_var = tk.BooleanVar()
    select_all_check = ttk.Checkbutton(diff_signal_buttons_frame, text="Select All", 
                                      variable=app_instance.diff_signal_ui_vars.select_all_var,
                                      command=lambda: toggle_all_diff_signal_selections(app_instance), 
                                      style="PyAEDT.TCheckbutton")
    select_all_check.grid(row=0, column=0, padx=5, sticky='w')
    
    # Differential signal management buttons
    add_diff_signal_button = ttk.Button(diff_signal_buttons_frame, text="Add Diff Signal", 
                                       command=lambda: add_diff_signal(app_instance), style="PyAEDT.TButton")
    add_diff_signal_button.grid(row=0, column=1, padx=5, sticky='w')
    
    edit_diff_signal_button = ttk.Button(diff_signal_buttons_frame, text="Edit Diff Signal", 
                                        command=lambda: edit_diff_signal(app_instance), style="PyAEDT.TButton")
    edit_diff_signal_button.grid(row=0, column=2, padx=5, sticky='w')
    
    delete_diff_signal_button = ttk.Button(diff_signal_buttons_frame, text="Delete Diff Signal", 
                                          command=lambda: delete_diff_signal(app_instance), style="PyAEDT.TButton")
    delete_diff_signal_button.grid(row=0, column=3, padx=5, sticky='w')
    
    # Configure button frame layout
    diff_signal_buttons_frame.grid_columnconfigure(4, weight=1)
    
    # Create differential signals table with columns
    columns = ('Select', 'Diff Signal Name', 'P/N Signals', 'Technology', 'Fanout Traces')
    app_instance.diff_signal_ui_vars.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', 
                                                        selectmode='extended', style="PyAEDT.Treeview")
    
    # Configure checkbox column for differential signal selection
    app_instance.diff_signal_ui_vars.tree.column('Select', width=80, stretch=False, anchor='center')
    app_instance.diff_signal_ui_vars.tree.heading('Select', text='Select')
    
    # Configure other columns
    app_instance.diff_signal_ui_vars.tree.column('Diff Signal Name', width=150, stretch=True)
    app_instance.diff_signal_ui_vars.tree.heading('Diff Signal Name', text='Diff Signal Name')
    
    app_instance.diff_signal_ui_vars.tree.column('P/N Signals', width=180, stretch=True)
    app_instance.diff_signal_ui_vars.tree.heading('P/N Signals', text='P/N Signals')
    
    app_instance.diff_signal_ui_vars.tree.column('Technology', width=120, stretch=True)
    app_instance.diff_signal_ui_vars.tree.heading('Technology', text='Technology')
    
    app_instance.diff_signal_ui_vars.tree.column('Fanout Traces', width=120, stretch=True)
    app_instance.diff_signal_ui_vars.tree.heading('Fanout Traces', text='Fanout Traces')
    
    # Initialize checkbox states dictionary
    app_instance.diff_signal_ui_vars.checkbox_states = {}
    
    # Add vertical scrollbar for table
    diff_signal_scrollbar = ttk.Scrollbar(parent_frame, orient='vertical', 
                                        command=app_instance.diff_signal_ui_vars.tree.yview, 
                                        style="PyAEDT.Vertical.TScrollbar")
    app_instance.diff_signal_ui_vars.tree.configure(yscrollcommand=diff_signal_scrollbar.set)
    
    # Position table and scrollbar
    app_instance.diff_signal_ui_vars.tree.grid(row=1, column=0, sticky='nsew', padx=(5, 0), pady=5)
    diff_signal_scrollbar.grid(row=1, column=1, sticky='ns', pady=5)
    
    # Add event handling for checkbox clicks
    def handle_diff_signal_click(event):
        region = app_instance.diff_signal_ui_vars.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = app_instance.diff_signal_ui_vars.tree.identify_column(event.x)
            if column == '#1':  # Select column (checkbox column)
                item = app_instance.diff_signal_ui_vars.tree.identify_row(event.y)
                if item:
                    # Toggle checkbox state
                    current_state = app_instance.diff_signal_ui_vars.checkbox_states.get(item, False)
                    new_state = not current_state
                    app_instance.diff_signal_ui_vars.checkbox_states[item] = new_state
                    
                    # Update checkbox symbol
                    values = list(app_instance.diff_signal_ui_vars.tree.item(item, 'values'))
                    values[0] = "☑" if new_state else "☐"
                    app_instance.diff_signal_ui_vars.tree.item(item, values=values)
                    
                    # Update selection
                    if new_state:
                        app_instance.diff_signal_ui_vars.tree.selection_add(item)
                    else:
                        app_instance.diff_signal_ui_vars.tree.selection_remove(item)
    
    app_instance.diff_signal_ui_vars.tree.bind('<Button-1>', handle_diff_signal_click)
    
    # Add double-click to edit
    app_instance.diff_signal_ui_vars.tree.bind('<Double-1>', lambda e: edit_diff_signal(app_instance))
    
    # Update differential signals table with data
    update_diff_signals_tree(app_instance)


def update_signals_tree(app_instance):
    """Update signals tree with current data from config_model"""
    if not hasattr(app_instance, 'signal_ui_vars') or not hasattr(app_instance.signal_ui_vars, 'tree'):
        return
    
    # Clear existing items
    for item in app_instance.signal_ui_vars.tree.get_children():
        app_instance.signal_ui_vars.tree.delete(item)
    
    # Clear checkbox states
    app_instance.signal_ui_vars.checkbox_states = {}
    
    # Add signals from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'signals'):
        for signal_name, signal_data in app_instance.config_model.signals.items():
            # Get signal properties
            technology = getattr(signal_data, 'technology', 'N/A')
            fanout_traces = getattr(signal_data, 'fanout_trace', [])
            trace_count = len(fanout_traces) if fanout_traces else 0
            
            # Insert item with checkbox unchecked by default
            item_id = app_instance.signal_ui_vars.tree.insert('', 'end', values=(
                "☐",  # Checkbox unchecked
                signal_name,
                technology,
                f"{trace_count} traces"
            ))
            
            # Initialize checkbox state
            app_instance.signal_ui_vars.checkbox_states[item_id] = False


def toggle_all_signal_selections(app_instance):
    """Toggle all signal selections based on select all checkbox"""
    if not hasattr(app_instance, 'signal_ui_vars') or not hasattr(app_instance.signal_ui_vars, 'tree'):
        return
    
    select_all = app_instance.signal_ui_vars.select_all_var.get()
    
    # Update all items
    for item in app_instance.signal_ui_vars.tree.get_children():
        app_instance.signal_ui_vars.checkbox_states[item] = select_all
        values = list(app_instance.signal_ui_vars.tree.item(item, 'values'))
        values[0] = "☑" if select_all else "☐"
        app_instance.signal_ui_vars.tree.item(item, values=values)
        
        if select_all:
            app_instance.signal_ui_vars.tree.selection_add(item)
        else:
            app_instance.signal_ui_vars.tree.selection_remove(item)


def add_signal(app_instance):
    """Add new signal"""
    # Create a simple dialog to get signal name and technology
    dialog = tk.Toplevel()
    dialog.title("Add Signal")
    dialog.geometry("400x300")
    dialog.resizable(False, False)
    dialog.transient(app_instance.root if hasattr(app_instance, 'root') else None)
    dialog.grab_set()
    
    # Apply PyAEDT style to the window content
    add_dialog_main_frame = ttk.Frame(dialog, style="PyAEDT.TFrame")
    add_dialog_main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Signal name
    ttk.Label(add_dialog_main_frame, text="Signal Name:", style="PyAEDT.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    name_var = tk.StringVar()
    ttk.Entry(add_dialog_main_frame, textvariable=name_var, width=30, style="PyAEDT.TEntry").grid(row=0, column=1, padx=10, pady=5)
    
    # Technology selection
    ttk.Label(add_dialog_main_frame, text="Technology:", style="PyAEDT.TLabel").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    tech_var = tk.StringVar()
    tech_combo = ttk.Combobox(add_dialog_main_frame, textvariable=tech_var, width=27, style="PyAEDT.TCombobox")
    
    # Get available technologies from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'technologies'):
        tech_combo['values'] = list(app_instance.config_model.technologies.keys())
    tech_combo.grid(row=1, column=1, padx=10, pady=5)
    
    def save_signal():
        signal_name = name_var.get().strip()
        technology = tech_var.get().strip()
        
        if not signal_name:
            tk.messagebox.showerror("Error", "Signal name is required")
            return
        
        if not technology:
            tk.messagebox.showerror("Error", "Technology is required")
            return
        
        # Check if signal already exists
        if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'signals'):
            if signal_name in app_instance.config_model.signals:
                tk.messagebox.showerror("Error", f"Signal '{signal_name}' already exists")
                return
        
        # Add signal using ConfigModel method
        try:
            signal_data = {
                'technology': technology,
                'fanout_trace': []
            }
            app_instance.config_model.add_signal(signal_name, signal_data)
            
            # Update the UI
            update_signals_tree(app_instance)
            
            dialog.destroy()
            tk.messagebox.showinfo("Success", f"Signal '{signal_name}' added successfully")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to add signal: {str(e)}")
    
    def cancel():
        dialog.destroy()
    
    # Buttons
    button_frame = ttk.Frame(add_dialog_main_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=2, column=0, columnspan=2, pady=20)
    
    ttk.Button(button_frame, text="Save", command=save_signal, style="PyAEDT.TButton").grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Cancel", command=cancel, style="PyAEDT.TButton").grid(row=0, column=1, padx=5)


def edit_signal(app_instance):
    """Edit selected signal"""
    if not hasattr(app_instance, 'signal_ui_vars') or not hasattr(app_instance.signal_ui_vars, 'tree'):
        return
    
    selected_items = app_instance.signal_ui_vars.tree.selection()
    if not selected_items:
        tk.messagebox.showwarning("Warning", "No signal selected for editing")
        return
    
    if len(selected_items) > 1:
        tk.messagebox.showwarning("Warning", "Please select only one signal for editing")
        return
    
    # Get signal name from selected item
    item = selected_items[0]
    values = app_instance.signal_ui_vars.tree.item(item, 'values')
    signal_name = values[1]  # Signal name is in column 1
    
    # Get current signal data
    if not hasattr(app_instance, 'config_model') or signal_name not in app_instance.config_model.signals:
        tk.messagebox.showerror("Error", f"Signal '{signal_name}' not found")
        return
    
    signal_data = app_instance.config_model.signals[signal_name]
    
    # Create edit dialog
    dialog = tk.Toplevel()
    dialog.title(f"Edit Signal: {signal_name}")
    dialog.geometry("400x300")
    dialog.resizable(False, False)
    dialog.grab_set()

    # Apply PyAEDT style to the window content
    edit_dialog_main_frame = ttk.Frame(dialog, style="PyAEDT.TFrame")
    edit_dialog_main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Signal name (read-only)
    ttk.Label(edit_dialog_main_frame, text="Signal Name:", style="PyAEDT.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    ttk.Label(edit_dialog_main_frame, text=signal_name, font=('TkDefaultFont', 9, 'bold'), style="PyAEDT.TLabel").grid(row=0, column=1, padx=10, pady=5, sticky='w')
    
    # Technology selection
    ttk.Label(edit_dialog_main_frame, text="Technology:", style="PyAEDT.TLabel").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    tech_var = tk.StringVar(value=getattr(signal_data, 'technology', ''))
    tech_combo = ttk.Combobox(edit_dialog_main_frame, textvariable=tech_var, width=27, style="PyAEDT.TCombobox")
    
    # Get available technologies from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'technologies'):
        tech_combo['values'] = list(app_instance.config_model.technologies.keys())
    tech_combo.grid(row=1, column=1, padx=10, pady=5)
    
    def save_changes():
        technology = tech_var.get().strip()
        
        if not technology:
            tk.messagebox.showerror("Error", "Technology is required")
            return
        
        try:
            # Update signal technology
            signal_data.technology = technology
            
            # Update the UI
            update_signals_tree(app_instance)
            
            dialog.destroy()
            tk.messagebox.showinfo("Success", f"Signal '{signal_name}' updated successfully")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to update signal: {str(e)}")
    
    def cancel():
        dialog.destroy()
    
    # Buttons
    button_frame = ttk.Frame(edit_dialog_main_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=2, column=0, columnspan=2, pady=20)
    
    ttk.Button(button_frame, text="Save", command=save_changes, style="PyAEDT.TButton").grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Cancel", command=cancel, style="PyAEDT.TButton").grid(row=0, column=1, padx=5)


def delete_signal(app_instance):
    """Delete selected signals"""
    if not hasattr(app_instance, 'signal_ui_vars') or not hasattr(app_instance.signal_ui_vars, 'tree'):
        return
    
    selected_items = app_instance.signal_ui_vars.tree.selection()
    if not selected_items:
        tk.messagebox.showwarning("Warning", "No signals selected for deletion")
        return
    
    # Get signal names from selected items
    signal_names = []
    for item in selected_items:
        values = app_instance.signal_ui_vars.tree.item(item, 'values')
        signal_names.append(values[1])  # Signal name is in column 1
    
    # Confirm deletion
    if len(signal_names) == 1:
        message = f"Are you sure you want to delete signal '{signal_names[0]}'?"
    else:
        message = f"Are you sure you want to delete {len(signal_names)} signals?"
    
    if not tk.messagebox.askyesno("Confirm Deletion", message):
        return
    
    # Delete signals using ConfigModel method
    try:
        deleted_count = 0
        for signal_name in signal_names:
            if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'signals'):
                if signal_name in app_instance.config_model.signals:
                    app_instance.config_model.delete_signal(signal_name)
                    deleted_count += 1
        
        # Update the UI
        update_signals_tree(app_instance)
        
        if deleted_count > 0:
            tk.messagebox.showinfo("Success", f"{deleted_count} signal(s) deleted successfully")
        else:
            tk.messagebox.showwarning("Warning", "No signals were deleted")
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to delete signals: {str(e)}")


def toggle_all_diff_signal_selections(app_instance):
    """Toggle all differential signal selections based on select all checkbox"""
    if not hasattr(app_instance, 'diff_signal_ui_vars') or not hasattr(app_instance.diff_signal_ui_vars, 'tree'):
        return
    
    select_all = app_instance.diff_signal_ui_vars.select_all_var.get()
    
    # Update all items
    for item in app_instance.diff_signal_ui_vars.tree.get_children():
        app_instance.diff_signal_ui_vars.checkbox_states[item] = select_all
        values = list(app_instance.diff_signal_ui_vars.tree.item(item, 'values'))
        values[0] = "☑" if select_all else "☐"
        app_instance.diff_signal_ui_vars.tree.item(item, values=values)
        
        if select_all:
            app_instance.diff_signal_ui_vars.tree.selection_add(item)
        else:
            app_instance.diff_signal_ui_vars.tree.selection_remove(item)


def add_diff_signal(app_instance):
    """Add new differential signal"""
    # Create a dialog to get differential signal information
    dialog = tk.Toplevel()
    dialog.title("Add Differential Signal")
    dialog.geometry("600x700")
    dialog.transient(app_instance.root if hasattr(app_instance, 'root') else None)
    dialog.grab_set()
    
    # Create a scrollable frame
    canvas = tk.Canvas(dialog)
    scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview, style="PyAEDT.Vertical.TScrollbar")
    scrollable_frame = ttk.Frame(canvas, style="PyAEDT.TFrame")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Differential signal name
    ttk.Label(scrollable_frame, text="Diff Signal Name:", style="PyAEDT.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    name_var = tk.StringVar()
    ttk.Entry(scrollable_frame, textvariable=name_var, width=30, style="PyAEDT.TEntry").grid(row=0, column=1, padx=10, pady=5)
    
    # P/N Signals
    ttk.Label(scrollable_frame, text="P Signal:", style="PyAEDT.TLabel").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    p_signal_var = tk.StringVar()
    p_signal_combo = ttk.Combobox(scrollable_frame, textvariable=p_signal_var, width=27, style="PyAEDT.TCombobox")
    
    ttk.Label(scrollable_frame, text="N Signal:", style="PyAEDT.TLabel").grid(row=2, column=0, padx=10, pady=5, sticky='w')
    n_signal_var = tk.StringVar()
    n_signal_combo = ttk.Combobox(scrollable_frame, textvariable=n_signal_var, width=27, style="PyAEDT.TCombobox")
    
    # Get available signals from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'signals'):
        signal_names = list(app_instance.config_model.signals.keys())
        p_signal_combo['values'] = signal_names
        n_signal_combo['values'] = signal_names
    
    p_signal_combo.grid(row=1, column=1, padx=10, pady=5)
    n_signal_combo.grid(row=2, column=1, padx=10, pady=5)
    
    # Technology selection
    ttk.Label(scrollable_frame, text="Technology:", style="PyAEDT.TLabel").grid(row=3, column=0, padx=10, pady=5, sticky='w')
    tech_var = tk.StringVar()
    tech_combo = ttk.Combobox(scrollable_frame, textvariable=tech_var, width=27, style="PyAEDT.TCombobox")
    
    # Get available technologies from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'technologies'):
        tech_combo['values'] = list(app_instance.config_model.technologies.keys())
    tech_combo.grid(row=3, column=1, padx=10, pady=5)
    
    # Fanout Trace Configuration Section
    ttk.Separator(scrollable_frame, orient='horizontal', style="PyAEDT.TSeparator").grid(row=4, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
    ttk.Label(scrollable_frame, text="Fanout Trace Configuration:", font=('TkDefaultFont', 9, 'bold'), style="PyAEDT.TLabel").grid(row=5, column=0, columnspan=2, padx=10, pady=5)
    
    # Via Index
    ttk.Label(scrollable_frame, text="Via Index:", style="PyAEDT.TLabel").grid(row=6, column=0, padx=10, pady=5, sticky='w')
    via_index_var = tk.StringVar(value="0")
    ttk.Entry(scrollable_frame, textvariable=via_index_var, width=30, style="PyAEDT.TEntry").grid(row=6, column=1, padx=10, pady=5)
    
    # Layer
    ttk.Label(scrollable_frame, text="Layer:", style="PyAEDT.TLabel").grid(row=7, column=0, padx=10, pady=5, sticky='w')
    layer_var = tk.StringVar()
    ttk.Entry(scrollable_frame, textvariable=layer_var, width=30, style="PyAEDT.TEntry").grid(row=7, column=1, padx=10, pady=5)
    
    # Width
    ttk.Label(scrollable_frame, text="Width:", style="PyAEDT.TLabel").grid(row=8, column=0, padx=10, pady=5, sticky='w')
    width_var = tk.StringVar()
    ttk.Entry(scrollable_frame, textvariable=width_var, width=30, style="PyAEDT.TEntry").grid(row=8, column=1, padx=10, pady=5)
    
    # Separation (specific to differential signals)
    ttk.Label(scrollable_frame, text="Separation:", style="PyAEDT.TLabel").grid(row=9, column=0, padx=10, pady=5, sticky='w')
    separation_var = tk.StringVar()
    ttk.Entry(scrollable_frame, textvariable=separation_var, width=30, style="PyAEDT.TEntry").grid(row=9, column=1, padx=10, pady=5)
    
    # Clearance
    ttk.Label(scrollable_frame, text="Clearance:", style="PyAEDT.TLabel").grid(row=10, column=0, padx=10, pady=5, sticky='w')
    clearance_var = tk.StringVar()
    ttk.Entry(scrollable_frame, textvariable=clearance_var, width=30, style="PyAEDT.TEntry").grid(row=10, column=1, padx=10, pady=5)
    
    # Incremental Path DY (specific to differential signals)
    ttk.Label(scrollable_frame, text="Incremental Path DY:", style="PyAEDT.TLabel").grid(row=11, column=0, padx=10, pady=5, sticky='w')
    incremental_path_dy_var = tk.StringVar()
    ttk.Entry(scrollable_frame, textvariable=incremental_path_dy_var, width=30, style="PyAEDT.TEntry").grid(row=11, column=1, padx=10, pady=5)
    
    # End Cap Style
    ttk.Label(scrollable_frame, text="End Cap Style:", style="PyAEDT.TLabel").grid(row=12, column=0, padx=10, pady=5, sticky='w')
    end_cap_style_var = tk.StringVar(value="round")
    end_cap_combo = ttk.Combobox(scrollable_frame, textvariable=end_cap_style_var, values=["round", "square", "flat"], width=27, style="PyAEDT.TCombobox")
    end_cap_combo.grid(row=12, column=1, padx=10, pady=5)
    
    # Flip DX
    ttk.Label(scrollable_frame, text="Flip DX:", style="PyAEDT.TLabel").grid(row=13, column=0, padx=10, pady=5, sticky='w')
    flip_dx_var = tk.BooleanVar()
    ttk.Checkbutton(scrollable_frame, variable=flip_dx_var, style="PyAEDT.TCheckbutton").grid(row=13, column=1, padx=10, pady=5, sticky='w')
    
    # Flip DY
    ttk.Label(scrollable_frame, text="Flip DY:", style="PyAEDT.TLabel").grid(row=14, column=0, padx=10, pady=5, sticky='w')
    flip_dy_var = tk.BooleanVar()
    ttk.Checkbutton(scrollable_frame, variable=flip_dy_var, style="PyAEDT.TCheckbutton").grid(row=14, column=1, padx=10, pady=5, sticky='w')
    
    # Port Configuration
    ttk.Separator(scrollable_frame, orient='horizontal', style="PyAEDT.TSeparator").grid(row=15, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
    ttk.Label(scrollable_frame, text="Port Configuration:", font=('TkDefaultFont', 9, 'bold'), style="PyAEDT.TLabel").grid(row=16, column=0, columnspan=2, padx=10, pady=5)
    
    # Horizontal Extent Factor
    ttk.Label(scrollable_frame, text="Horizontal Extent Factor:", style="PyAEDT.TLabel").grid(row=17, column=0, padx=10, pady=5, sticky='w')
    h_extent_var = tk.StringVar(value="5")
    ttk.Entry(scrollable_frame, textvariable=h_extent_var, width=30, style="PyAEDT.TEntry").grid(row=17, column=1, padx=10, pady=5)
    
    # Vertical Extent Factor
    ttk.Label(scrollable_frame, text="Vertical Extent Factor:", style="PyAEDT.TLabel").grid(row=18, column=0, padx=10, pady=5, sticky='w')
    v_extent_var = tk.StringVar(value="5")
    ttk.Entry(scrollable_frame, textvariable=v_extent_var, width=30, style="PyAEDT.TEntry").grid(row=18, column=1, padx=10, pady=5)
    
    def save_diff_signal():
        diff_signal_name = name_var.get().strip()
        p_signal = p_signal_var.get().strip()
        n_signal = n_signal_var.get().strip()
        technology = tech_var.get().strip()
        
        if not diff_signal_name:
            tk.messagebox.showerror("Error", "Differential signal name is required")
            return
        
        if not p_signal or not n_signal:
            tk.messagebox.showerror("Error", "Both P and N signals are required")
            return
        
        if p_signal == n_signal:
            tk.messagebox.showerror("Error", "P and N signals must be different")
            return
        
        if not technology:
            tk.messagebox.showerror("Error", "Technology is required")
            return
        
        # Check if differential signal already exists
        if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'differential_signals'):
            if diff_signal_name in app_instance.config_model.differential_signals:
                tk.messagebox.showerror("Error", f"Differential signal '{diff_signal_name}' already exists")
                return
        
        # Add differential signal using ConfigModel method
        try:
            # Create fanout trace data if any fields are filled
            fanout_trace_list = []
            if (via_index_var.get().strip() or layer_var.get().strip() or width_var.get().strip() or 
                separation_var.get().strip() or clearance_var.get().strip()):
                
                # Parse incremental_path_dy as a list
                incremental_path_dy_list = []
                if incremental_path_dy_var.get().strip():
                    try:
                        # Split by comma and strip whitespace
                        incremental_path_dy_list = [x.strip() for x in incremental_path_dy_var.get().split(',') if x.strip()]
                    except:
                        incremental_path_dy_list = [incremental_path_dy_var.get().strip()]
                
                fanout_trace_data = {
                    'via_index': int(via_index_var.get()) if via_index_var.get().strip().isdigit() else 0,
                    'layer': layer_var.get().strip(),
                    'width': width_var.get().strip(),
                    'separation': separation_var.get().strip(),
                    'clearance': clearance_var.get().strip(),
                    'incremental_path_dy': incremental_path_dy_list,
                    'end_cap_style': end_cap_style_var.get(),
                    'flip_dx': flip_dx_var.get(),
                    'flip_dy': flip_dy_var.get(),
                    'port': {
                        'horizontal_extent_factor': int(h_extent_var.get()) if h_extent_var.get().strip().isdigit() else 5,
                        'vertical_extent_factor': int(v_extent_var.get()) if v_extent_var.get().strip().isdigit() else 5
                    }
                }
                fanout_trace_list.append(fanout_trace_data)
            
            diff_signal_data = {
                'signals': [p_signal, n_signal],
                'technology': technology,
                'fanout_trace': fanout_trace_list
            }
            app_instance.config_model.add_differential_signal(diff_signal_name, diff_signal_data)
            
            # Update the UI
            update_diff_signals_tree(app_instance)
            
            dialog.destroy()
            tk.messagebox.showinfo("Success", f"Differential signal '{diff_signal_name}' added successfully")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to add differential signal: {str(e)}")
    
    def cancel():
        dialog.destroy()
    
    # Buttons
    button_frame = ttk.Frame(scrollable_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=19, column=0, columnspan=2, pady=20)
    
    ttk.Button(button_frame, text="Save", command=save_diff_signal, style="PyAEDT.TButton").grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Cancel", command=cancel, style="PyAEDT.TButton").grid(row=0, column=1, padx=5)


def edit_diff_signal(app_instance):
    """Edit selected differential signal"""
    if not hasattr(app_instance, 'diff_signal_ui_vars') or not hasattr(app_instance.diff_signal_ui_vars, 'tree'):
        return
    
    selected_items = app_instance.diff_signal_ui_vars.tree.selection()
    if not selected_items:
        tk.messagebox.showwarning("Warning", "No differential signal selected for editing")
        return
    
    if len(selected_items) > 1:
        tk.messagebox.showwarning("Warning", "Please select only one differential signal for editing")
        return
    
    # Get differential signal name from selected item
    item = selected_items[0]
    values = app_instance.diff_signal_ui_vars.tree.item(item, 'values')
    diff_signal_name = values[1]  # Diff signal name is in column 1
    
    # Get current differential signal data
    if not hasattr(app_instance, 'config_model') or diff_signal_name not in app_instance.config_model.differential_signals:
        tk.messagebox.showerror("Error", f"Differential signal '{diff_signal_name}' not found")
        return
    
    diff_signal_data = app_instance.config_model.differential_signals[diff_signal_name]
    
    # Create edit dialog
    dialog = tk.Toplevel()
    dialog.title(f"Edit Differential Signal: {diff_signal_name}")
    dialog.geometry("600x700")
    dialog.transient(app_instance.root if hasattr(app_instance, 'root') else None)
    dialog.grab_set()
    
    # Create a scrollable frame
    canvas = tk.Canvas(dialog)
    scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview, style="PyAEDT.Vertical.TScrollbar")
    scrollable_frame = ttk.Frame(canvas, style="PyAEDT.TFrame")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Differential signal name (read-only)
    ttk.Label(scrollable_frame, text="Diff Signal Name:", style="PyAEDT.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    ttk.Label(scrollable_frame, text=diff_signal_name, font=('TkDefaultFont', 9, 'bold'), style="PyAEDT.TLabel").grid(row=0, column=1, padx=10, pady=5, sticky='w')
    
    # P/N Signals
    current_signals = getattr(diff_signal_data, 'signals', [])
    p_signal_current = current_signals[0] if len(current_signals) > 0 else ''
    n_signal_current = current_signals[1] if len(current_signals) > 1 else ''
    
    ttk.Label(scrollable_frame, text="P Signal:", style="PyAEDT.TLabel").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    p_signal_var = tk.StringVar(value=p_signal_current)
    p_signal_combo = ttk.Combobox(scrollable_frame, textvariable=p_signal_var, width=27, style="PyAEDT.TCombobox")
    
    ttk.Label(scrollable_frame, text="N Signal:", style="PyAEDT.TLabel").grid(row=2, column=0, padx=10, pady=5, sticky='w')
    n_signal_var = tk.StringVar(value=n_signal_current)
    n_signal_combo = ttk.Combobox(scrollable_frame, textvariable=n_signal_var, width=27, style="PyAEDT.TCombobox")
    
    # Get available signals from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'signals'):
        signal_names = list(app_instance.config_model.signals.keys())
        p_signal_combo['values'] = signal_names
        n_signal_combo['values'] = signal_names
    
    p_signal_combo.grid(row=1, column=1, padx=10, pady=5)
    n_signal_combo.grid(row=2, column=1, padx=10, pady=5)
    
    # Technology selection
    ttk.Label(scrollable_frame, text="Technology:", style="PyAEDT.TLabel").grid(row=3, column=0, padx=10, pady=5, sticky='w')
    tech_var = tk.StringVar(value=getattr(diff_signal_data, 'technology', ''))
    tech_combo = ttk.Combobox(scrollable_frame, textvariable=tech_var, width=27, style="PyAEDT.TCombobox")
    
    # Get available technologies from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'technologies'):
        tech_combo['values'] = list(app_instance.config_model.technologies.keys())
    tech_combo.grid(row=3, column=1, padx=10, pady=5)
    
    # Get existing fanout trace data
    current_fanout_traces = getattr(diff_signal_data, 'fanout_trace', [])
    current_fanout_trace = current_fanout_traces[0] if current_fanout_traces else None
    
    # Fanout Trace Configuration Section
    ttk.Separator(scrollable_frame, orient='horizontal', style="PyAEDT.TSeparator").grid(row=4, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
    ttk.Label(scrollable_frame, text="Fanout Trace Configuration:", font=('TkDefaultFont', 9, 'bold'), style="PyAEDT.TLabel").grid(row=5, column=0, columnspan=2, padx=10, pady=5)
    
    # Via Index
    ttk.Label(scrollable_frame, text="Via Index:", style="PyAEDT.TLabel").grid(row=6, column=0, padx=10, pady=5, sticky='w')
    via_index_var = tk.StringVar(value=str(getattr(current_fanout_trace, 'via_index', 0)) if current_fanout_trace else '0')
    ttk.Entry(scrollable_frame, textvariable=via_index_var, width=30, style="PyAEDT.TEntry").grid(row=6, column=1, padx=10, pady=5)
    
    # Layer
    ttk.Label(scrollable_frame, text="Layer:", style="PyAEDT.TLabel").grid(row=7, column=0, padx=10, pady=5, sticky='w')
    layer_var = tk.StringVar(value=getattr(current_fanout_trace, 'layer', '') if current_fanout_trace else '')
    ttk.Entry(scrollable_frame, textvariable=layer_var, width=30, style="PyAEDT.TEntry").grid(row=7, column=1, padx=10, pady=5)
    
    # Width
    ttk.Label(scrollable_frame, text="Width:", style="PyAEDT.TLabel").grid(row=8, column=0, padx=10, pady=5, sticky='w')
    width_var = tk.StringVar(value=getattr(current_fanout_trace, 'width', '') if current_fanout_trace else '')
    ttk.Entry(scrollable_frame, textvariable=width_var, width=30, style="PyAEDT.TEntry").grid(row=8, column=1, padx=10, pady=5)
    
    # Separation (specific to differential signals)
    ttk.Label(scrollable_frame, text="Separation:", style="PyAEDT.TLabel").grid(row=9, column=0, padx=10, pady=5, sticky='w')
    separation_var = tk.StringVar(value=getattr(current_fanout_trace, 'separation', '') if current_fanout_trace else '')
    ttk.Entry(scrollable_frame, textvariable=separation_var, width=30, style="PyAEDT.TEntry").grid(row=9, column=1, padx=10, pady=5)
    
    # Clearance
    ttk.Label(scrollable_frame, text="Clearance:", style="PyAEDT.TLabel").grid(row=10, column=0, padx=10, pady=5, sticky='w')
    clearance_var = tk.StringVar(value=getattr(current_fanout_trace, 'clearance', '') if current_fanout_trace else '')
    ttk.Entry(scrollable_frame, textvariable=clearance_var, width=30, style="PyAEDT.TEntry").grid(row=10, column=1, padx=10, pady=5)
    
    # Incremental Path DY (specific to differential signals)
    ttk.Label(scrollable_frame, text="Incremental Path DY:", style="PyAEDT.TLabel").grid(row=11, column=0, padx=10, pady=5, sticky='w')
    incremental_path_dy_current = getattr(current_fanout_trace, 'incremental_path_dy', []) if current_fanout_trace else []
    incremental_path_dy_str = ', '.join(incremental_path_dy_current) if isinstance(incremental_path_dy_current, list) else str(incremental_path_dy_current)
    incremental_path_dy_var = tk.StringVar(value=incremental_path_dy_str)
    ttk.Entry(scrollable_frame, textvariable=incremental_path_dy_var, width=30, style="PyAEDT.TEntry").grid(row=11, column=1, padx=10, pady=5)
    
    # End Cap Style
    ttk.Label(scrollable_frame, text="End Cap Style:", style="PyAEDT.TLabel").grid(row=12, column=0, padx=10, pady=5, sticky='w')
    end_cap_style_var = tk.StringVar(value=getattr(current_fanout_trace, 'end_cap_style', 'round') if current_fanout_trace else 'round')
    end_cap_combo = ttk.Combobox(scrollable_frame, textvariable=end_cap_style_var, values=["round", "square", "flat"], width=27, style="PyAEDT.TCombobox")
    end_cap_combo.grid(row=12, column=1, padx=10, pady=5)
    
    # Flip DX
    ttk.Label(scrollable_frame, text="Flip DX:", style="PyAEDT.TLabel").grid(row=13, column=0, padx=10, pady=5, sticky='w')
    flip_dx_var = tk.BooleanVar(value=getattr(current_fanout_trace, 'flip_dx', False) if current_fanout_trace else False)
    ttk.Checkbutton(scrollable_frame, variable=flip_dx_var, style="PyAEDT.TCheckbutton").grid(row=13, column=1, padx=10, pady=5, sticky='w')
    
    # Flip DY
    ttk.Label(scrollable_frame, text="Flip DY:", style="PyAEDT.TLabel").grid(row=14, column=0, padx=10, pady=5, sticky='w')
    flip_dy_var = tk.BooleanVar(value=getattr(current_fanout_trace, 'flip_dy', False) if current_fanout_trace else False)
    ttk.Checkbutton(scrollable_frame, variable=flip_dy_var, style="PyAEDT.TCheckbutton").grid(row=14, column=1, padx=10, pady=5, sticky='w')
    
    # Port Configuration
    ttk.Separator(scrollable_frame, orient='horizontal', style="PyAEDT.TSeparator").grid(row=15, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
    ttk.Label(scrollable_frame, text="Port Configuration:", font=('TkDefaultFont', 9, 'bold'), style="PyAEDT.TLabel").grid(row=16, column=0, columnspan=2, padx=10, pady=5)
    
    current_port = getattr(current_fanout_trace, 'port', None) if current_fanout_trace else None
    
    # Horizontal Extent Factor
    ttk.Label(scrollable_frame, text="Horizontal Extent Factor:", style="PyAEDT.TLabel").grid(row=17, column=0, padx=10, pady=5, sticky='w')
    h_extent_value = 5  # default value
    if current_port:
        if hasattr(current_port, 'horizontal_extent_factor'):
            h_extent_value = current_port.horizontal_extent_factor
        elif isinstance(current_port, dict):
            h_extent_value = current_port.get('horizontal_extent_factor', 5)
    h_extent_var = tk.StringVar(value=str(h_extent_value))
    ttk.Entry(scrollable_frame, textvariable=h_extent_var, width=30, style="PyAEDT.TEntry").grid(row=17, column=1, padx=10, pady=5)
    
    # Vertical Extent Factor
    ttk.Label(scrollable_frame, text="Vertical Extent Factor:", style="PyAEDT.TLabel").grid(row=18, column=0, padx=10, pady=5, sticky='w')
    v_extent_value = 5  # default value
    if current_port:
        if hasattr(current_port, 'vertical_extent_factor'):
            v_extent_value = current_port.vertical_extent_factor
        elif isinstance(current_port, dict):
            v_extent_value = current_port.get('vertical_extent_factor', 5)
    v_extent_var = tk.StringVar(value=str(v_extent_value))
    ttk.Entry(scrollable_frame, textvariable=v_extent_var, width=30, style="PyAEDT.TEntry").grid(row=18, column=1, padx=10, pady=5)
    
    def save_changes():
        p_signal = p_signal_var.get().strip()
        n_signal = n_signal_var.get().strip()
        technology = tech_var.get().strip()
        
        if not p_signal or not n_signal:
            tk.messagebox.showerror("Error", "Both P and N signals are required")
            return
        
        if p_signal == n_signal:
            tk.messagebox.showerror("Error", "P and N signals must be different")
            return
        
        if not technology:
            tk.messagebox.showerror("Error", "Technology is required")
            return
        
        try:
            # Update differential signal data
            diff_signal_data.signals = [p_signal, n_signal]
            diff_signal_data.technology = technology
            
            # Update fanout trace data if any fields are filled
            fanout_trace_list = []
            if (via_index_var.get().strip() or layer_var.get().strip() or width_var.get().strip() or 
                separation_var.get().strip() or clearance_var.get().strip()):
                
                # Parse incremental_path_dy as a list
                incremental_path_dy_list = []
                if incremental_path_dy_var.get().strip():
                    try:
                        # Split by comma and strip whitespace
                        incremental_path_dy_list = [x.strip() for x in incremental_path_dy_var.get().split(',') if x.strip()]
                    except:
                        incremental_path_dy_list = [incremental_path_dy_var.get().strip()]
                
                fanout_trace_data = {
                    'via_index': int(via_index_var.get()) if via_index_var.get().strip().isdigit() else 0,
                    'layer': layer_var.get().strip(),
                    'width': width_var.get().strip(),
                    'separation': separation_var.get().strip(),
                    'clearance': clearance_var.get().strip(),
                    'incremental_path_dy': incremental_path_dy_list,
                    'end_cap_style': end_cap_style_var.get(),
                    'flip_dx': flip_dx_var.get(),
                    'flip_dy': flip_dy_var.get(),
                    'port': {
                        'horizontal_extent_factor': int(h_extent_var.get()) if h_extent_var.get().strip().isdigit() else 5,
                        'vertical_extent_factor': int(v_extent_var.get()) if v_extent_var.get().strip().isdigit() else 5
                    }
                }
                fanout_trace_list.append(fanout_trace_data)
            
            diff_signal_data.fanout_trace = fanout_trace_list
            
            # Update the UI
            update_diff_signals_tree(app_instance)
            
            dialog.destroy()
            tk.messagebox.showinfo("Success", f"Differential signal '{diff_signal_name}' updated successfully")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to update differential signal: {str(e)}")
    
    def cancel():
        dialog.destroy()
    
    # Buttons
    button_frame = ttk.Frame(scrollable_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=19, column=0, columnspan=2, pady=20)
    
    ttk.Button(button_frame, text="Save", command=save_changes, style="PyAEDT.TButton").grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Cancel", command=cancel, style="PyAEDT.TButton").grid(row=0, column=1, padx=5)


def delete_diff_signal(app_instance):
    """Delete selected differential signals"""
    if not hasattr(app_instance, 'diff_signal_ui_vars') or not hasattr(app_instance.diff_signal_ui_vars, 'tree'):
        return
    
    selected_items = app_instance.diff_signal_ui_vars.tree.selection()
    if not selected_items:
        tk.messagebox.showwarning("Warning", "No differential signals selected for deletion")
        return
    
    # Get differential signal names from selected items
    diff_signal_names = []
    for item in selected_items:
        values = app_instance.diff_signal_ui_vars.tree.item(item, 'values')
        diff_signal_names.append(values[1])  # Diff signal name is in column 1
    
    # Confirm deletion
    if len(diff_signal_names) == 1:
        message = f"Are you sure you want to delete differential signal '{diff_signal_names[0]}'?"
    else:
        message = f"Are you sure you want to delete {len(diff_signal_names)} differential signals?"
    
    if not tk.messagebox.askyesno("Confirm Deletion", message):
        return
    
    # Delete differential signals using ConfigModel method
    try:
        deleted_count = 0
        for diff_signal_name in diff_signal_names:
            if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'differential_signals'):
                if diff_signal_name in app_instance.config_model.differential_signals:
                    app_instance.config_model.delete_differential_signal(diff_signal_name)
                    deleted_count += 1
        
        # Update the UI
        update_diff_signals_tree(app_instance)
        
        if deleted_count > 0:
            tk.messagebox.showinfo("Success", f"{deleted_count} differential signal(s) deleted successfully")
        else:
            tk.messagebox.showwarning("Warning", "No differential signals were deleted")
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to delete differential signals: {str(e)}")


def update_diff_signals_tree(app_instance):
    """Update differential signals tree with current data from config_model"""
    if not hasattr(app_instance, 'diff_signal_ui_vars') or not hasattr(app_instance.diff_signal_ui_vars, 'tree'):
        return
    
    # Clear existing items
    for item in app_instance.diff_signal_ui_vars.tree.get_children():
        app_instance.diff_signal_ui_vars.tree.delete(item)
    
    # Clear checkbox states
    app_instance.diff_signal_ui_vars.checkbox_states = {}
    
    # Add differential signals from config_model
    if hasattr(app_instance, 'config_model') and hasattr(app_instance.config_model, 'differential_signals'):
        for diff_signal_name, diff_signal_data in app_instance.config_model.differential_signals.items():
            # Get differential signal properties
            signals = getattr(diff_signal_data, 'signals', [])
            signals_text = ', '.join(signals) if signals else 'N/A'
            technology = getattr(diff_signal_data, 'technology', 'N/A')
            fanout_traces = getattr(diff_signal_data, 'fanout_trace', [])
            trace_count = len(fanout_traces) if fanout_traces else 0
            
            # Insert item with checkbox unchecked by default
            item_id = app_instance.diff_signal_ui_vars.tree.insert('', 'end', values=(
                "☐",  # Checkbox unchecked
                diff_signal_name,
                signals_text,
                technology,
                f"{trace_count} traces"
            ))
            
            # Initialize checkbox state
            app_instance.diff_signal_ui_vars.checkbox_states[item_id] = False
