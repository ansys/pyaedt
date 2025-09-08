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
from tkinter import ttk, messagebox


def create_simulation_settings_ui(tab_frame, app_instance):
    """Create simulation settings UI based on config_model.setups[0]"""
    style = ttk.Style()
    style.configure("PyAEDT.Treeview", rowheight=25)
    style.map("PyAEDT.Treeview",
              foreground=[('selected', '#000000')],
              background=[('selected', '#CCE4F7')])
    
    # Main container with scrollable content
    main_canvas = tk.Canvas(tab_frame, bg='white')
    main_scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=main_canvas.yview)
    scrollable_main_frame = ttk.Frame(main_canvas, style="PyAEDT.TFrame")
    
    scrollable_main_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_main_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    
    main_canvas.pack(side="left", fill="both", expand=True)
    main_scrollbar.pack(side="right", fill="y")
    
    # Setup Configuration Section
    setup_frame = ttk.LabelFrame(scrollable_main_frame, text="Setup Configuration", style="PyAEDT.TLabelframe")
    setup_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
    scrollable_main_frame.grid_columnconfigure(0, weight=1)
    
    # Get setup data from config_model
    setup_data = {}
    if (hasattr(app_instance, 'config_model') and 
        hasattr(app_instance.config_model, 'setups') and 
        len(app_instance.config_model.setups) > 0):
        setup_data = app_instance.config_model.setups[0]
    
    # Setup basic parameters
    create_setup_basic_params(setup_frame, app_instance, setup_data)
    
    # Frequency Sweep Section
    freq_sweep_frame = ttk.LabelFrame(scrollable_main_frame, text="Frequency Sweep", style="PyAEDT.TLabelframe")
    freq_sweep_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
    
    # Create frequency sweep UI
    create_freq_sweep_ui(freq_sweep_frame, app_instance, setup_data)
    
    # Buttons
    button_frame = ttk.Frame(scrollable_main_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
    
    ttk.Button(button_frame, text="Apply Settings", 
               command=lambda: apply_simulation_settings(app_instance), 
               style="PyAEDT.TButton").grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Reset to Default", 
               command=lambda: reset_simulation_settings(app_instance), 
               style="PyAEDT.TButton").grid(row=0, column=1, padx=5)


def create_setup_basic_params(parent_frame, app_instance, setup_data):
    """Create basic setup parameters UI"""
    # Setup Name
    ttk.Label(parent_frame, text="Setup Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    app_instance.sim_setup_name = ttk.Entry(parent_frame, width=20)
    app_instance.sim_setup_name.insert(0, getattr(setup_data, 'name', 'hfss_setup_1'))
    app_instance.sim_setup_name.grid(row=0, column=1, sticky='w', padx=5, pady=2)
    
    # Setup Type
    ttk.Label(parent_frame, text="Setup Type:", style="PyAEDT.TLabel").grid(row=0, column=2, sticky='w', padx=5, pady=2)
    app_instance.sim_setup_type = ttk.Combobox(parent_frame, width=15, values=['hfss', 'q3d', 'maxwell'], state="readonly")
    app_instance.sim_setup_type.set(getattr(setup_data, 'type', 'hfss'))
    app_instance.sim_setup_type.grid(row=0, column=3, sticky='w', padx=5, pady=2)
    
    # Adaptive Frequency
    ttk.Label(parent_frame, text="Adaptive Frequency:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    app_instance.sim_f_adapt = ttk.Entry(parent_frame, width=20)
    app_instance.sim_f_adapt.insert(0, getattr(setup_data, 'f_adapt', '5GHz'))
    app_instance.sim_f_adapt.grid(row=1, column=1, sticky='w', padx=5, pady=2)
    
    # Max Number of Passes
    ttk.Label(parent_frame, text="Max Passes:", style="PyAEDT.TLabel").grid(row=1, column=2, sticky='w', padx=5, pady=2)
    app_instance.sim_max_passes = ttk.Entry(parent_frame, width=15)
    app_instance.sim_max_passes.insert(0, str(getattr(setup_data, 'max_num_passes', 10)))
    app_instance.sim_max_passes.grid(row=1, column=3, sticky='w', padx=5, pady=2)
    
    # Max Delta S
    ttk.Label(parent_frame, text="Max Delta S:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    app_instance.sim_max_delta_s = ttk.Entry(parent_frame, width=20)
    app_instance.sim_max_delta_s.insert(0, str(getattr(setup_data, 'max_mag_delta_s', 0.02)))
    app_instance.sim_max_delta_s.grid(row=2, column=1, sticky='w', padx=5, pady=2)


def create_freq_sweep_ui(parent_frame, app_instance, setup_data):
    """Create frequency sweep configuration UI"""
    # Create notebook for different sweep types
    sweep_notebook = ttk.Notebook(parent_frame, style="PyAEDT.TNotebook")
    sweep_notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    parent_frame.grid_rowconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Get frequency sweep data
    freq_sweeps = getattr(setup_data, 'freq_sweep', [])
    
    # Initialize sweep data storage
    if not hasattr(app_instance, 'freq_sweep_data'):
        app_instance.freq_sweep_data = []
    
    # Create tabs for each frequency sweep
    for i, sweep_data in enumerate(freq_sweeps):
        sweep_tab = ttk.Frame(sweep_notebook, style="PyAEDT.TFrame")
        sweep_name = sweep_data.get('name', f'sweep{i+1}')
        sweep_notebook.add(sweep_tab, text=sweep_name)
        
        create_single_sweep_ui(sweep_tab, app_instance, sweep_data, i)
    
    # Add button to create new sweep
    if len(freq_sweeps) == 0:
        # Create default sweep tab if no sweeps exist
        default_sweep_tab = ttk.Frame(sweep_notebook, style="PyAEDT.TFrame")
        sweep_notebook.add(default_sweep_tab, text="sweep1")
        default_sweep_data = {
            'name': 'sweep1',
            'type': 'interpolation',
            'frequencies': ['LIN 0.05GHz 0.2GHz 0.01GHz']
        }
        create_single_sweep_ui(default_sweep_tab, app_instance, default_sweep_data, 0)


def create_single_sweep_ui(parent_frame, app_instance, sweep_data, sweep_index):
    """Create UI for a single frequency sweep"""
    # Sweep Name
    ttk.Label(parent_frame, text="Sweep Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    sweep_name_entry = ttk.Entry(parent_frame, width=20)
    sweep_name_entry.insert(0, sweep_data.get('name', f'sweep{sweep_index+1}'))
    sweep_name_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
    
    # Sweep Type
    ttk.Label(parent_frame, text="Sweep Type:", style="PyAEDT.TLabel").grid(row=0, column=2, sticky='w', padx=5, pady=2)
    sweep_type_combo = ttk.Combobox(parent_frame, width=15, 
                                   values=['interpolation', 'discrete', 'fast'], state="readonly")
    sweep_type_combo.set(sweep_data.get('type', 'interpolation'))
    sweep_type_combo.grid(row=0, column=3, sticky='w', padx=5, pady=2)
    
    # Frequencies section
    freq_frame = ttk.LabelFrame(parent_frame, text="Frequencies", style="PyAEDT.TLabelframe")
    freq_frame.grid(row=1, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Create scrollable text widget for frequencies
    freq_text_frame = ttk.Frame(freq_frame, style="PyAEDT.TFrame")
    freq_text_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    freq_frame.grid_rowconfigure(0, weight=1)
    freq_frame.grid_columnconfigure(0, weight=1)
    
    freq_text = tk.Text(freq_text_frame, height=6, width=60)
    freq_scrollbar = ttk.Scrollbar(freq_text_frame, orient="vertical", command=freq_text.yview)
    freq_text.configure(yscrollcommand=freq_scrollbar.set)
    
    # Insert frequency data
    frequencies = sweep_data.get('frequencies', [])
    freq_text.insert('1.0', '\n'.join(frequencies))
    
    freq_text.pack(side="left", fill="both", expand=True)
    freq_scrollbar.pack(side="right", fill="y")
    
    # Store references for later access
    if not hasattr(app_instance, 'freq_sweep_widgets'):
        app_instance.freq_sweep_widgets = []
    
    app_instance.freq_sweep_widgets.append({
        'name': sweep_name_entry,
        'type': sweep_type_combo,
        'frequencies': freq_text
    })


def apply_simulation_settings(app_instance):
    """Apply simulation settings to config_model"""
    try:
        if not hasattr(app_instance, 'config_model'):
            messagebox.showerror("Error", "Config model not found")
            return
        
        # Ensure setups list exists
        if not hasattr(app_instance.config_model, 'setups'):
            app_instance.config_model.setups = []
        
        # Create or update first setup
        if len(app_instance.config_model.setups) == 0:
            app_instance.config_model.setups.append({})
        
        setup = app_instance.config_model.setups[0]
        
        # Update basic parameters
        setup['name'] = app_instance.sim_setup_name.get()
        setup['type'] = app_instance.sim_setup_type.get()
        setup['f_adapt'] = app_instance.sim_f_adapt.get()
        setup['max_num_passes'] = int(app_instance.sim_max_passes.get())
        setup['max_mag_delta_s'] = float(app_instance.sim_max_delta_s.get())
        
        # Update frequency sweeps
        freq_sweeps = []
        if hasattr(app_instance, 'freq_sweep_widgets'):
            for widget_set in app_instance.freq_sweep_widgets:
                sweep = {
                    'name': widget_set['name'].get(),
                    'type': widget_set['type'].get(),
                    'frequencies': widget_set['frequencies'].get('1.0', 'end-1c').split('\n')
                }
                # Remove empty frequency lines
                sweep['frequencies'] = [f.strip() for f in sweep['frequencies'] if f.strip()]
                freq_sweeps.append(sweep)
        
        setup['freq_sweep'] = freq_sweeps
        
        messagebox.showinfo("Success", "Simulation settings applied successfully")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")


def reset_simulation_settings(app_instance):
    """Reset simulation settings to default values"""
    confirmation_msg = "Are you sure you want to reset simulation settings? All changes will be lost."
    if messagebox.askyesno("Confirmation", confirmation_msg):
        # Reset to default values
        app_instance.sim_setup_name.delete(0, 'end')
        app_instance.sim_setup_name.insert(0, 'hfss_setup_1')
        
        app_instance.sim_setup_type.set('hfss')
        
        app_instance.sim_f_adapt.delete(0, 'end')
        app_instance.sim_f_adapt.insert(0, '5GHz')
        
        app_instance.sim_max_passes.delete(0, 'end')
        app_instance.sim_max_passes.insert(0, '10')
        
        app_instance.sim_max_delta_s.delete(0, 'end')
        app_instance.sim_max_delta_s.insert(0, '0.02')
        
        # Reset frequency sweep widgets
        if hasattr(app_instance, 'freq_sweep_widgets'):
            for widget_set in app_instance.freq_sweep_widgets:
                widget_set['name'].delete(0, 'end')
                widget_set['name'].insert(0, 'sweep1')
                widget_set['type'].set('interpolation')
                widget_set['frequencies'].delete('1.0', 'end')
                widget_set['frequencies'].insert('1.0', 'LIN 0.05GHz 0.2GHz 0.01GHz')
        
        messagebox.showinfo("Success", "Simulation settings reset to default values")
