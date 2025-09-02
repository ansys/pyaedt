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
from tkinter import ttk, messagebox, simpledialog
import types

from PIL import Image
from PIL import ImageTk


def create_technology_settings_ui(tab_frame, app_instance):
    """Create technology settings UI with resizable left-middle-right layout for managing technologies and stacked vias"""
    
    # UI variables have been created during tab initialization, no need to check here
    
    # Create main PanedWindow for resizable panels
    main_paned = ttk.PanedWindow(tab_frame, orient=tk.HORIZONTAL)
    main_paned.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Left panel for technology types
    left_panel = ttk.LabelFrame(main_paned, text="Technology Types", style="PyAEDT.TLabelframe")
    main_paned.add(left_panel, weight=1)
    
    # Middle panel for stacked via array
    middle_panel = ttk.LabelFrame(main_paned, text="Stacked Via Array", style="PyAEDT.TLabelframe")
    main_paned.add(middle_panel, weight=1)
    
    # Right panel for via details
    right_panel = ttk.LabelFrame(main_paned, text="Via Details", style="PyAEDT.TLabelframe")
    main_paned.add(right_panel, weight=2)
    
    # Create panel contents
    create_left_panel(left_panel, app_instance)
    create_middle_panel(middle_panel, app_instance)
    create_right_panel(right_panel, app_instance)
    
    # Load initial data
    load_technology_data(app_instance)
    
    return main_paned


def create_left_panel(parent, app_instance):
    """Create the left panel with technology types list"""
    
    # Technology types listbox with scrollbar
    list_frame = ttk.Frame(parent, style="PyAEDT.TFrame")
    list_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Listbox for technology types
    app_instance.technology_ui_vars.type_listbox = tk.Listbox(list_frame, height=15)
    app_instance.technology_ui_vars.type_listbox.pack(side="left", fill="both", expand=True)
    
    # Scrollbar for listbox
    type_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                   command=app_instance.technology_ui_vars.type_listbox.yview)
    type_scrollbar.pack(side="right", fill="y")
    app_instance.technology_ui_vars.type_listbox.configure(yscrollcommand=type_scrollbar.set)
    
    # Bind selection event
    app_instance.technology_ui_vars.type_listbox.bind('<<ListboxSelect>>', 
                                                        lambda e: on_type_select(app_instance))
    
    # Buttons frame
    buttons_frame = ttk.Frame(parent, style="PyAEDT.TFrame")
    buttons_frame.pack(fill="x", padx=5, pady=5)
    
    # Add/Remove technology buttons
    ttk.Button(buttons_frame, text="Add Type", 
               command=lambda: add_technology_type(app_instance), 
               style="PyAEDT.TButton").pack(side="top", fill="x", pady=(0, 2))
    
    ttk.Button(buttons_frame, text="Remove Type", 
               command=lambda: remove_technology_type(app_instance), 
               style="PyAEDT.TButton").pack(side="top", fill="x")


def create_middle_panel(parent, app_instance):
    """Create the middle panel with stacked via array"""
    
    # Current technology label
    app_instance.technology_ui_vars.current_type_label = ttk.Label(parent, 
                                                                    text="Select a technology type", 
                                                                    style="PyAEDT.TLabel", 
                                                                    font=('TkDefaultFont', 9, 'bold'))
    app_instance.technology_ui_vars.current_type_label.pack(pady=(5, 10))
    
    # Stacked via array listbox with scrollbar
    array_frame = ttk.Frame(parent, style="PyAEDT.TFrame")
    array_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Listbox for stacked via array
    app_instance.technology_ui_vars.via_listbox = tk.Listbox(array_frame, height=12)
    app_instance.technology_ui_vars.via_listbox.pack(side="left", fill="both", expand=True)
    
    # Scrollbar for via listbox
    via_scrollbar = ttk.Scrollbar(array_frame, orient="vertical", 
                                  command=app_instance.technology_ui_vars.via_listbox.yview)
    via_scrollbar.pack(side="right", fill="y")
    app_instance.technology_ui_vars.via_listbox.configure(yscrollcommand=via_scrollbar.set)
    
    # Bind selection event
    app_instance.technology_ui_vars.via_listbox.bind('<<ListboxSelect>>', 
                                                       lambda e: on_via_select(app_instance))
    
    # Buttons for via management
    via_buttons_frame = ttk.Frame(parent, style="PyAEDT.TFrame")
    via_buttons_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Button(via_buttons_frame, text="Add Via", 
               command=lambda: add_stacked_via(app_instance), 
               style="PyAEDT.TButton").pack(side="top", fill="x", pady=(0, 2))
    
    ttk.Button(via_buttons_frame, text="Remove Via", 
               command=lambda: remove_stacked_via(app_instance), 
               style="PyAEDT.TButton").pack(side="top", fill="x", pady=(0, 2))
    
    # Note: Move Up/Down buttons removed as vias are unordered


def create_right_panel(parent, app_instance):
    """Create the right panel with via details editing"""
    
    # Current via label
    app_instance.technology_ui_vars.current_via_label = ttk.Label(parent, 
                                                                   text="Select a stacked via", 
                                                                   style="PyAEDT.TLabel", 
                                                                   font=('TkDefaultFont', 9, 'bold'))
    app_instance.technology_ui_vars.current_via_label.pack(pady=(5, 10))
    
    # Create scrollable frame for via details
    canvas = tk.Canvas(parent, bg='white')
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="PyAEDT.TFrame")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scrollbar.pack(side="right", fill="y", pady=5)
    
    # Store references
    app_instance.technology_ui_vars.details_canvas = canvas
    app_instance.technology_ui_vars.details_frame = scrollable_frame
    
    # Initialize empty details form
    create_empty_details_form(scrollable_frame, app_instance)


def create_empty_details_form(parent, app_instance):
    """Create empty form when no via is selected"""
    # Clear existing widgets
    for widget in parent.winfo_children():
        widget.destroy()
    
    empty_label = ttk.Label(parent, text="No via selected", style="PyAEDT.TLabel")
    empty_label.grid(row=0, column=0, pady=50, padx=20)
    parent.grid_columnconfigure(0, weight=1)


def create_via_details_form(parent, app_instance, via_data, via_index):
    """Create detailed form for editing via parameters"""
    
    # Clear existing widgets
    for widget in parent.winfo_children():
        widget.destroy()
    
    # Create form fields
    row = 0
    
    # Padstack Definition
    ttk.Label(parent, text="Padstack Definition:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    padstack_var = tk.StringVar(value=via_data.get('padstack_def', ''))
    padstack_combo = ttk.Combobox(parent, textvariable=padstack_var, 
                                  values=["MICRO_VIA", "CORE_VIA", "BGA"], 
                                  style="PyAEDT.TCombobox")
    padstack_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    row += 1
    
    # Start Layer
    ttk.Label(parent, text="Start Layer:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    start_layer_var = tk.StringVar(value=via_data.get('start_layer', ''))
    start_layer_entry = ttk.Entry(parent, textvariable=start_layer_var)
    start_layer_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    row += 1
    
    # Stop Layer
    ttk.Label(parent, text="Stop Layer:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    stop_layer_var = tk.StringVar(value=via_data.get('stop_layer', ''))
    stop_layer_entry = ttk.Entry(parent, textvariable=stop_layer_var)
    stop_layer_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    row += 1
    
    # DX
    ttk.Label(parent, text="DX:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    dx_var = tk.StringVar(value=str(via_data.get('dx', '0')))
    dx_entry = ttk.Entry(parent, textvariable=dx_var)
    dx_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    row += 1
    
    # DY
    ttk.Label(parent, text="DY:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    dy_var = tk.StringVar(value=str(via_data.get('dy', '0')))
    dy_entry = ttk.Entry(parent, textvariable=dy_var)
    dy_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    row += 1
    
    # Anti-pad Diameter
    ttk.Label(parent, text="Anti-pad Diameter:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    antipad_var = tk.StringVar(value=via_data.get('anti_pad_diameter', ''))
    antipad_entry = ttk.Entry(parent, textvariable=antipad_var)
    antipad_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    row += 1
    
    # Boolean options
    flip_dx_var = tk.BooleanVar(value=via_data.get('flip_dx', False))
    flip_dx_check = ttk.Checkbutton(parent, text="Flip DX", variable=flip_dx_var, style="PyAEDT.TCheckbutton")
    flip_dx_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    row += 1
    
    flip_dy_var = tk.BooleanVar(value=via_data.get('flip_dy', False))
    flip_dy_check = ttk.Checkbutton(parent, text="Flip DY", variable=flip_dy_var, style="PyAEDT.TCheckbutton")
    flip_dy_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    row += 1
    
    solder_ball_var = tk.BooleanVar(value=via_data.get('with_solder_ball', False))
    solder_ball_check = ttk.Checkbutton(parent, text="With Solder Ball", variable=solder_ball_var, style="PyAEDT.TCheckbutton")
    solder_ball_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    row += 1
    
    # Connection Trace - can be False or dict with width/clearance
    connection_trace_data = via_data.get('connection_trace', False)
    connection_trace_enabled = isinstance(connection_trace_data, dict)
    
    connection_trace_var = tk.BooleanVar(value=connection_trace_enabled)
    connection_trace_check = ttk.Checkbutton(parent, text="Connection Trace", variable=connection_trace_var, 
                                           style="PyAEDT.TCheckbutton",
                                           command=lambda: toggle_connection_trace_fields(app_instance, connection_trace_var.get()))
    connection_trace_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    row += 1
    
    # Connection Trace details frame
    connection_trace_frame = ttk.Frame(parent, style="PyAEDT.TFrame")
    connection_trace_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
    row += 1
    
    # Width field
    ttk.Label(connection_trace_frame, text="Width:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    width_var = tk.StringVar(value=connection_trace_data.get('width', '0.3mm') if isinstance(connection_trace_data, dict) else '0.3mm')
    width_entry = ttk.Entry(connection_trace_frame, textvariable=width_var, width=15)
    width_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    # Clearance field
    ttk.Label(connection_trace_frame, text="Clearance:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    clearance_var = tk.StringVar(value=connection_trace_data.get('clearance', '0.15mm') if isinstance(connection_trace_data, dict) else '0.15mm')
    clearance_entry = ttk.Entry(connection_trace_frame, textvariable=clearance_var, width=15)
    clearance_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    # Initially show/hide connection trace fields based on checkbox state
    if not connection_trace_enabled:
        connection_trace_frame.grid_remove()
    
    # Store references for toggling visibility
    app_instance.technology_ui_vars.connection_trace_frame = connection_trace_frame
    app_instance.technology_ui_vars.connection_trace_width_var = width_var
    app_instance.technology_ui_vars.connection_trace_clearance_var = clearance_var
    
    backdrill_var = tk.BooleanVar(value=via_data.get('backdrill_parameters', False))
    backdrill_check = ttk.Checkbutton(parent, text="Backdrill Parameters", variable=backdrill_var, style="PyAEDT.TCheckbutton")
    backdrill_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    row += 1
    
    # Stitching Vias - can be False or dict with start_angle/step_angle/number_of_vias/distance
    stitching_vias_data = via_data.get('stitching_vias', False)
    stitching_vias_enabled = isinstance(stitching_vias_data, dict)
    
    stitching_var = tk.BooleanVar(value=stitching_vias_enabled)
    stitching_check = ttk.Checkbutton(parent, text="Stitching Vias", variable=stitching_var, 
                                     style="PyAEDT.TCheckbutton",
                                     command=lambda: toggle_stitching_vias_fields(app_instance, stitching_var.get()))
    stitching_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    row += 1
    
    # Stitching Vias details frame
    stitching_vias_frame = ttk.Frame(parent, style="PyAEDT.TFrame")
    stitching_vias_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
    row += 1
    
    # Start Angle field
    ttk.Label(stitching_vias_frame, text="Start Angle:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    start_angle_var = tk.StringVar(value=str(stitching_vias_data.get('start_angle', 90)) if isinstance(stitching_vias_data, dict) else '90')
    start_angle_entry = ttk.Entry(stitching_vias_frame, textvariable=start_angle_var, width=15)
    start_angle_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    # Step Angle field
    ttk.Label(stitching_vias_frame, text="Step Angle:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    step_angle_var = tk.StringVar(value=str(stitching_vias_data.get('step_angle', 45)) if isinstance(stitching_vias_data, dict) else '45')
    step_angle_entry = ttk.Entry(stitching_vias_frame, textvariable=step_angle_var, width=15)
    step_angle_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    # Number of Vias field
    ttk.Label(stitching_vias_frame, text="Number of Vias:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=2)
    number_of_vias_var = tk.StringVar(value=str(stitching_vias_data.get('number_of_vias', 5)) if isinstance(stitching_vias_data, dict) else '5')
    number_of_vias_entry = ttk.Entry(stitching_vias_frame, textvariable=number_of_vias_var, width=15)
    number_of_vias_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
    
    # Distance field
    ttk.Label(stitching_vias_frame, text="Distance:", style="PyAEDT.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=2)
    distance_var = tk.StringVar(value=stitching_vias_data.get('distance', '0.125mm') if isinstance(stitching_vias_data, dict) else '0.125mm')
    distance_entry = ttk.Entry(stitching_vias_frame, textvariable=distance_var, width=15)
    distance_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
    
    # Initially show/hide stitching vias fields based on checkbox state
    if not stitching_vias_enabled:
        stitching_vias_frame.grid_remove()
    
    # Store references for toggling visibility
    app_instance.technology_ui_vars.stitching_vias_frame = stitching_vias_frame
    app_instance.technology_ui_vars.stitching_start_angle_var = start_angle_var
    app_instance.technology_ui_vars.stitching_step_angle_var = step_angle_var
    app_instance.technology_ui_vars.stitching_number_of_vias_var = number_of_vias_var
    app_instance.technology_ui_vars.stitching_distance_var = distance_var
    
    # Configure column weights
    parent.grid_columnconfigure(1, weight=1)
    
    # Store variables for later access
    app_instance.technology_ui_vars.current_via_vars = {
        'padstack_def': padstack_var,
        'start_layer': start_layer_var,
        'stop_layer': stop_layer_var,
        'dx': dx_var,
        'dy': dy_var,
        'anti_pad_diameter': antipad_var,
        'flip_dx': flip_dx_var,
        'flip_dy': flip_dy_var,
        'with_solder_ball': solder_ball_var,
        'connection_trace': connection_trace_var,
        'connection_trace_width': width_var,
        'connection_trace_clearance': clearance_var,
        'backdrill_parameters': backdrill_var,
        'stitching_vias': stitching_var,
        'stitching_start_angle': start_angle_var,
        'stitching_step_angle': step_angle_var,
        'stitching_number_of_vias': number_of_vias_var,
        'stitching_distance': distance_var,
        'via_index': via_index
    }
    
    # Bind auto-save events to all input controls
    def auto_save(*args):
        save_via_changes(app_instance)
    
    # Bind events for automatic saving
    padstack_var.trace('w', auto_save)
    start_layer_var.trace('w', auto_save)
    stop_layer_var.trace('w', auto_save)
    dx_var.trace('w', auto_save)
    dy_var.trace('w', auto_save)
    antipad_var.trace('w', auto_save)
    flip_dx_var.trace('w', auto_save)
    flip_dy_var.trace('w', auto_save)
    solder_ball_var.trace('w', auto_save)
    connection_trace_var.trace('w', auto_save)
    width_var.trace('w', auto_save)
    clearance_var.trace('w', auto_save)
    backdrill_var.trace('w', auto_save)
    stitching_var.trace('w', auto_save)
    start_angle_var.trace('w', auto_save)
    step_angle_var.trace('w', auto_save)
    number_of_vias_var.trace('w', auto_save)
    distance_var.trace('w', auto_save)
    
    # Save button
    save_button = ttk.Button(parent, text="Save Changes", 
                            command=lambda: save_via_changes(app_instance), 
                            style="PyAEDT.TButton")
    save_button.grid(row=row, column=0, columnspan=2, pady=10)


def toggle_connection_trace_fields(app_instance, enabled):
    """Toggle visibility of connection trace detail fields"""
    if hasattr(app_instance.technology_ui_vars, 'connection_trace_frame'):
        if enabled:
            app_instance.technology_ui_vars.connection_trace_frame.grid()
        else:
            app_instance.technology_ui_vars.connection_trace_frame.grid_remove()


def toggle_stitching_vias_fields(app_instance, enabled):
    """Toggle visibility of stitching vias detail fields"""
    if hasattr(app_instance.technology_ui_vars, 'stitching_vias_frame'):
        if enabled:
            app_instance.technology_ui_vars.stitching_vias_frame.grid()
        else:
            app_instance.technology_ui_vars.stitching_vias_frame.grid_remove()


def load_technology_data(app_instance):
    """Load technology data from config model or use demo data."""
    try:
        if hasattr(app_instance, 'config_model') and app_instance.config_model:
            technologies = app_instance.config_model.technologies
            # Convert Technology objects to dictionary format
            tech_data = {}
            if isinstance(technologies, dict):
                for tech_name, tech_obj in technologies.items():
                    if hasattr(tech_obj, 'stacked_via'):
                        # Convert Technology object to dict
                        tech_data[tech_name] = {
                            "stacked_via": []
                        }
                        # Convert ViaDefinition objects to dict
                        for via in tech_obj.stacked_via:
                            if hasattr(via, '__dict__'):
                                via_dict = via.__dict__.copy()
                                # Handle ConnectionTrace object conversion
                                if 'connection_trace' in via_dict and hasattr(via_dict['connection_trace'], '__dict__'):
                                    via_dict['connection_trace'] = via_dict['connection_trace'].__dict__
                                # Handle StitchingVias object conversion
                                if 'stitching_vias' in via_dict and hasattr(via_dict['stitching_vias'], '__dict__'):
                                    via_dict['stitching_vias'] = via_dict['stitching_vias'].__dict__
                                tech_data[tech_name]["stacked_via"].append(via_dict)
                            else:
                                tech_data[tech_name]["stacked_via"].append(via)
                    else:
                        tech_data[tech_name] = tech_obj
            else:
                tech_data = technologies
                
            app_instance.technology_ui_vars.data = tech_data
        else:
            # Use demo data if config model is not available
            demo_data = {
                "TYPE_1": {
                    "stacked_via": [
                        {
                            "padstack_def": "MICRO_VIA",
                            "start_layer": "L1",
                            "stop_layer": "L2",
                            "dx": 0,
                            "dy": 0,
                            "flip_dx": False,
                            "flip_dy": False,
                            "anti_pad_diameter": "0.5mm",
                            "connection_trace": False,
                            "with_solder_ball": False,
                            "backdrill_parameters": False,
                            "stitching_vias": False
                        }
                    ]
                },
                "TYPE_2": {
                    "stacked_via": []
                }
            }
            app_instance.technology_ui_vars.data = demo_data
    except Exception as e:
        # Error loading technology data, using fallback
        # Fallback to demo data
        demo_data = {
            "TYPE_1": {
                "stacked_via": [
                    {
                        "padstack_def": "MICRO_VIA",
                        "start_layer": "L1",
                        "stop_layer": "L2",
                        "dx": 0,
                        "dy": 0,
                        "flip_dx": False,
                        "flip_dy": False,
                        "anti_pad_diameter": "0.5mm",
                        "connection_trace": False,
                        "with_solder_ball": False,
                        "backdrill_parameters": False,
                        "stitching_vias": False
                    }
                ]
            },
            "TYPE_2": {
                "stacked_via": []
            }
        }
        app_instance.technology_ui_vars.data = demo_data
    
    # Populate technology types listbox
    refresh_type_list(app_instance)


def refresh_type_list(app_instance):
    """Refresh the technology types listbox"""
    app_instance.technology_ui_vars.type_listbox.delete(0, tk.END)
    for tech_type in app_instance.technology_ui_vars.data.keys():
        app_instance.technology_ui_vars.type_listbox.insert(tk.END, tech_type)


def refresh_via_list(app_instance):
    """Refresh the stacked via array listbox"""
    app_instance.technology_ui_vars.via_listbox.delete(0, tk.END)
    
    if app_instance.technology_ui_vars.selected_type:
        tech_type = app_instance.technology_ui_vars.selected_type
        if tech_type in app_instance.technology_ui_vars.data:
            stacked_vias = app_instance.technology_ui_vars.data[tech_type].get('stacked_via', [])
            for i, via_data in enumerate(stacked_vias):
                padstack = via_data.get('padstack_def', 'Unknown')
                start_layer = via_data.get('start_layer', '')
                stop_layer = via_data.get('stop_layer', '')
                display_text = f"Via {i+1}: {padstack} ({start_layer}-{stop_layer})"
                app_instance.technology_ui_vars.via_listbox.insert(tk.END, display_text)


def on_type_select(app_instance):
    """Handle technology type selection"""
    selection = app_instance.technology_ui_vars.type_listbox.curselection()
    if selection:
        tech_type = app_instance.technology_ui_vars.type_listbox.get(selection[0])
        app_instance.technology_ui_vars.selected_type = tech_type
        app_instance.technology_ui_vars.selected_via_index = None
        
        # Update middle panel
        app_instance.technology_ui_vars.current_type_label.config(text=f"Technology: {tech_type}")
        refresh_via_list(app_instance)
        
        # Clear right panel
        create_empty_details_form(app_instance.technology_ui_vars.details_frame, app_instance)
        app_instance.technology_ui_vars.current_via_label.config(text="Select a stacked via")


def on_via_select(app_instance):
    """Handle stacked via selection"""
    selection = app_instance.technology_ui_vars.via_listbox.curselection()
    if selection and app_instance.technology_ui_vars.selected_type:
        via_index = selection[0]
        app_instance.technology_ui_vars.selected_via_index = via_index
        
        tech_type = app_instance.technology_ui_vars.selected_type
        stacked_vias = app_instance.technology_ui_vars.data[tech_type].get('stacked_via', [])
        
        if via_index < len(stacked_vias):
            via_data = stacked_vias[via_index]
            
            # Update right panel
            app_instance.technology_ui_vars.current_via_label.config(text=f"Via {via_index + 1} Details")
            create_via_details_form(app_instance.technology_ui_vars.details_frame, app_instance, via_data, via_index)


def add_technology_type(app_instance):
    """Add a new technology type"""
    tech_name = simpledialog.askstring("Add Technology Type", "Enter technology type name:")
    if tech_name and tech_name not in app_instance.technology_ui_vars.data:
        app_instance.technology_ui_vars.data[tech_name] = {"stacked_via": []}
        refresh_type_list(app_instance)
        save_to_config_model(app_instance)


def remove_technology_type(app_instance):
    """Remove selected technology type"""
    selection = app_instance.technology_ui_vars.type_listbox.curselection()
    if selection:
        tech_type = app_instance.technology_ui_vars.type_listbox.get(selection[0])
        if messagebox.askyesno("Confirm", f"Remove technology type '{tech_type}'?"):
            del app_instance.technology_ui_vars.data[tech_type]
            refresh_type_list(app_instance)
            
            # Clear selections and panels
            app_instance.technology_ui_vars.selected_type = None
            app_instance.technology_ui_vars.selected_via_index = None
            app_instance.technology_ui_vars.current_type_label.config(text="Select a technology type")
            app_instance.technology_ui_vars.current_via_label.config(text="Select a stacked via")
            app_instance.technology_ui_vars.via_listbox.delete(0, tk.END)
            create_empty_details_form(app_instance.technology_ui_vars.details_frame, app_instance)
            
            save_to_config_model(app_instance)


def add_stacked_via(app_instance):
    """Add a new stacked via to current technology"""
    if not app_instance.technology_ui_vars.selected_type:
        messagebox.showwarning("Warning", "Please select a technology type first.")
        return
    
    tech_type = app_instance.technology_ui_vars.selected_type
    new_via = {
        "padstack_def": "MICRO_VIA",
        "start_layer": "",
        "stop_layer": "",
        "dx": 0,
        "dy": 0,
        "flip_dx": False,
        "flip_dy": False,
        "anti_pad_diameter": "0.5mm",
        "connection_trace": False,
        "with_solder_ball": False,
        "backdrill_parameters": False,
        "stitching_vias": False
    }
    
    app_instance.technology_ui_vars.data[tech_type]['stacked_via'].append(new_via)
    refresh_via_list(app_instance)
    save_to_config_model(app_instance)


def remove_stacked_via(app_instance):
    """Remove selected stacked via"""
    if not app_instance.technology_ui_vars.selected_type:
        return
    
    selection = app_instance.technology_ui_vars.via_listbox.curselection()
    if selection:
        via_index = selection[0]
        tech_type = app_instance.technology_ui_vars.selected_type
        stacked_vias = app_instance.technology_ui_vars.data[tech_type]['stacked_via']
        
        if via_index < len(stacked_vias):
            if messagebox.askyesno("Confirm", f"Remove Via {via_index + 1}?"):
                stacked_vias.pop(via_index)
                refresh_via_list(app_instance)
                
                # Clear right panel if this via was selected
                if app_instance.technology_ui_vars.selected_via_index == via_index:
                    app_instance.technology_ui_vars.selected_via_index = None
                    app_instance.technology_ui_vars.current_via_label.config(text="Select a stacked via")
                    create_empty_details_form(app_instance.technology_ui_vars.details_frame, app_instance)
                
                save_to_config_model(app_instance)


# Move functions removed - vias are unordered


def save_via_changes(app_instance):
    """Save changes from the via details form"""
    if not hasattr(app_instance.technology_ui_vars, 'current_via_vars'):
        return
    
    vars_dict = app_instance.technology_ui_vars.current_via_vars
    via_index = vars_dict['via_index']
    tech_type = app_instance.technology_ui_vars.selected_type
    
    if tech_type and via_index is not None:
        stacked_vias = app_instance.technology_ui_vars.data[tech_type]['stacked_via']
        if via_index < len(stacked_vias):
            # Update via data from form
            via_data = stacked_vias[via_index]
            via_data.update({
                'padstack_def': vars_dict['padstack_def'].get(),
                'start_layer': vars_dict['start_layer'].get(),
                'stop_layer': vars_dict['stop_layer'].get(),
                'dx': vars_dict['dx'].get(),
                'dy': vars_dict['dy'].get(),
                'anti_pad_diameter': vars_dict['anti_pad_diameter'].get(),
                'flip_dx': vars_dict['flip_dx'].get(),
                'flip_dy': vars_dict['flip_dy'].get(),
                'with_solder_ball': vars_dict['with_solder_ball'].get(),
                'connection_trace': {
                    'width': vars_dict['connection_trace_width'].get(),
                    'clearance': vars_dict['connection_trace_clearance'].get()
                } if vars_dict['connection_trace'].get() else False,
                'backdrill_parameters': vars_dict['backdrill_parameters'].get(),
                'stitching_vias': {
                    'start_angle': int(vars_dict['stitching_start_angle'].get()) if vars_dict['stitching_start_angle'].get().isdigit() else 90,
                    'step_angle': int(vars_dict['stitching_step_angle'].get()) if vars_dict['stitching_step_angle'].get().isdigit() else 45,
                    'number_of_vias': int(vars_dict['stitching_number_of_vias'].get()) if vars_dict['stitching_number_of_vias'].get().isdigit() else 5,
                    'distance': vars_dict['stitching_distance'].get()
                } if vars_dict['stitching_vias'].get() else False
            })
            
            # Refresh via list to show updated info
            refresh_via_list(app_instance)
            app_instance.technology_ui_vars.via_listbox.selection_set(via_index)
            
            save_to_config_model(app_instance)

def save_to_config_model(app_instance):
    """Save technology data back to config model"""
    try:
        if hasattr(app_instance, 'config_model'):
            # Import the data classes for object conversion
            from ansys.aedt.core.extensions.project.resources.via_design.src.data_classes import (
                Technology, ViaDefinition, ConnectionTrace, StitchingVias
            )
            
            # Convert dictionary data back to proper objects
            tech_objects = {}
            for tech_name, tech_data in app_instance.technology_ui_vars.data.items():
                via_objects = []
                for via_dict in tech_data.get('stacked_via', []):
                    # Convert connection_trace dict back to ConnectionTrace object or keep as bool
                    connection_trace = via_dict.get('connection_trace', False)
                    if isinstance(connection_trace, dict):
                        connection_trace = ConnectionTrace(**connection_trace)
                    
                    # Convert stitching_vias dict back to StitchingVias object or keep as bool
                    stitching_vias = via_dict.get('stitching_vias', False)
                    if isinstance(stitching_vias, dict):
                        stitching_vias = StitchingVias(**stitching_vias)
                    
                    # Create ViaDefinition object with converted nested objects
                    via_dict_copy = via_dict.copy()
                    via_dict_copy['connection_trace'] = connection_trace
                    via_dict_copy['stitching_vias'] = stitching_vias
                    
                    via_objects.append(ViaDefinition(**via_dict_copy))
                
                tech_objects[tech_name] = Technology(stacked_via=via_objects)
            
            app_instance.config_model.technologies = tech_objects
    except Exception as e:
        # Error saving to config model
        pass
