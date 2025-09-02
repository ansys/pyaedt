"""Stackup Settings Tab Module for Via Design Extension.

This module provides the user interface and functionality for managing
PCB stackup configurations in the Via Design extension.
"""

import json
from pathlib import Path
import ansys.aedt.core
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage

import json
import os
import tkinter as tk
from tkinter import filedialog  # If you need to add functionality to the browse button
from tkinter import messagebox
from tkinter import ttk

from PIL import Image
from PIL import ImageTk


def create_stackup_settings_ui(tab_frame, app_instance):
    """Create the stackup settings user interface.
    
    Args:
        tab_frame: The parent frame for the stackup settings tab
        app_instance: The main application instance
    """
    # UI variables have been created during tab initialization, no need to check here
    # Configure tab_frame to make it resizable
    tab_frame.grid_rowconfigure(3, weight=1)  # Table area row weight
    tab_frame.grid_columnconfigure(0, weight=1)  # Column weight
    
    # Configure Treeview style for better appearance
    style = ttk.Style()
    style.configure("PyAEDT.Treeview", rowheight=25)
    style.map("PyAEDT.Treeview",
              foreground=[('selected', '#000000')],
              background=[('selected', '#CCE4F7')])
     
    # File selection area (currently unused but reserved for future features)
    file_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    file_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

    # Layer count selection and generate button
    layer_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    layer_frame.grid(row=2, column=0, sticky='ew')
    
    # Layer count selection controls
    ttk.Label(layer_frame, text="Number Of Metal Layers", style="PyAEDT.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    app_instance.stackup_ui_vars.layer_count = ttk.Combobox(layer_frame, width=5, values=list(range(2, 21)), style="PyAEDT.TCombobox")
    app_instance.stackup_ui_vars.layer_count.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    app_instance.stackup_ui_vars.layer_count.set(4)  # Default to 4-layer PCB
    
    generate_button = ttk.Button(layer_frame, text="Generate", command=lambda: generate_stackup(app_instance), style="PyAEDT.TButton")
    generate_button.grid(row=0, column=2, padx=20, pady=5, sticky='w')
    
    # Configure column weights for proper layout
    layer_frame.grid_columnconfigure(3, weight=1)

    # Main content area with table and image
    table_image_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    table_image_frame.grid(row=3, column=0, sticky='nsew', pady=(5, 0))
    
    # Configure layout: 75% table, 25% image
    table_image_frame.grid_rowconfigure(0, weight=1)
    table_image_frame.grid_columnconfigure(0, weight=3)  # Table area
    table_image_frame.grid_columnconfigure(1, weight=1)  # Image area

    # Table container frame
    table_frame = ttk.Frame(table_image_frame, style="PyAEDT.TFrame")
    table_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
    
    # Configure table frame layout
    table_frame.grid_rowconfigure(1, weight=1)  # Table row expands
    table_frame.grid_columnconfigure(0, weight=1)  # Column expands
    
    # Table control buttons area
    table_buttons_frame = ttk.Frame(table_frame, style="PyAEDT.TFrame")
    table_buttons_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))

    # Select all checkbox for bulk operations
    app_instance.stackup_ui_vars.select_all_var = tk.BooleanVar()
    select_all_check = ttk.Checkbutton(table_buttons_frame, text="Select All", variable=app_instance.stackup_ui_vars.select_all_var, 
                                      command=lambda: toggle_all_selections(app_instance), style="PyAEDT.TCheckbutton")
    select_all_check.grid(row=0, column=0, padx=5, sticky='w')
    
    # Layer management buttons
    add_layer_button = ttk.Button(table_buttons_frame, text="Add Layer", command=lambda: add_layer(app_instance), style="PyAEDT.TButton")
    add_layer_button.grid(row=0, column=1, padx=5, sticky='w')
    
    delete_layer_button = ttk.Button(table_buttons_frame, text="Delete Layer", command=lambda: delete_layer(app_instance), style="PyAEDT.TButton")
    delete_layer_button.grid(row=0, column=2, padx=5, sticky='w')
    
    edit_layer_button = ttk.Button(table_buttons_frame, text="Edit Layer", command=lambda: edit_layer(app_instance), style="PyAEDT.TButton")
    edit_layer_button.grid(row=0, column=3, padx=5, sticky='w')
    
    # Layer reordering buttons
    move_up_button = ttk.Button(table_buttons_frame, text="Move Up", command=lambda: move_layer_up(app_instance), style="PyAEDT.TButton")
    move_up_button.grid(row=0, column=4, padx=5, sticky='w')
    
    move_down_button = ttk.Button(table_buttons_frame, text="Move Down", command=lambda: move_layer_down(app_instance), style="PyAEDT.TButton")
    move_down_button.grid(row=0, column=5, padx=5, sticky='w')
    
    # Configure button frame layout
    table_buttons_frame.grid_columnconfigure(5, weight=1)
    
    # Create stackup table with columns
    columns = ('Select', 'Index', 'Name', 'Type', 'Material', 'Dielectric Fill', 'Thickness')
    app_instance.stackup_ui_vars.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='extended', style="PyAEDT.Treeview")
    
    # Configure checkbox column for layer selection
    app_instance.stackup_ui_vars.tree.column('Select', width=80, stretch=True, anchor='center')
    app_instance.stackup_ui_vars.tree.heading('Select', text='Select')
    
    # Configure index column
    app_instance.stackup_ui_vars.tree.column('Index', width=50, stretch=True)
    app_instance.stackup_ui_vars.tree.heading('Index', text='#')

    
    # Add keyboard shortcuts for selection
    def handle_selection_shortcut(event):
        if event.state & 4:  # Ctrl key
            if event.keysym == 'a':  # Ctrl+A
                app_instance.stackup_ui_vars.tree.selection_set(app_instance.stackup_ui_vars.tree.get_children())
                return 'break'
    
    app_instance.stackup_ui_vars.tree.bind('<Control-a>', handle_selection_shortcut)
    
    # Add Shift+Click support for range selection
    app_instance.stackup_ui_vars.last_selected = None
    
    def handle_shift_click(event):
        if event.state & 1:  # Shift key
            item = app_instance.stackup_ui_vars.tree.identify_row(event.y)
            if item and app_instance.stackup_ui_vars.last_selected:
                items = app_instance.stackup_ui_vars.tree.get_children()
                try:
                    start_idx = items.index(app_instance.stackup_ui_vars.last_selected)
                    end_idx = items.index(item)
                    if start_idx > end_idx:
                        start_idx, end_idx = end_idx, start_idx
                    for i in range(start_idx, end_idx + 1):
                        app_instance.stackup_ui_vars.tree.selection_add(items[i])
                except ValueError:
                    pass
                return 'break'
        app_instance.stackup_ui_vars.last_selected = app_instance.stackup_ui_vars.tree.identify_row(event.y)
    
    app_instance.stackup_ui_vars.tree.bind('<ButtonRelease-1>', handle_shift_click)
    
    # Initialize selection states for toggle buttons
    app_instance.stackup_ui_vars.metal_selected = False
    app_instance.stackup_ui_vars.dielectric_selected = False
    
    # Add layer type selection buttons with fixed width to prevent layout shifts
    app_instance.stackup_ui_vars.select_metal_button = ttk.Button(table_buttons_frame, text="Select Metal", width=15,
                                   command=lambda: toggle_select_by_type(app_instance, 'signal'), style="PyAEDT.TButton")
    app_instance.stackup_ui_vars.select_metal_button.grid(row=0, column=6, padx=5, sticky='w')
    
    app_instance.stackup_ui_vars.select_dielectric_button = ttk.Button(table_buttons_frame, text="Select Dielectric", width=15,
                                         command=lambda: toggle_select_by_type(app_instance, 'dielectric'), style="PyAEDT.TButton")
    app_instance.stackup_ui_vars.select_dielectric_button.grid(row=0, column=7, padx=5, sticky='w')
    
    # Add batch edit button
    batch_edit_button = ttk.Button(table_buttons_frame, text="Batch Edit", 
                                 command=lambda: batch_edit_layers(app_instance), style="PyAEDT.TButton")
    batch_edit_button.grid(row=0, column=8, padx=5, sticky='w')

    # Configure remaining columns with auto-sizing
    for col in columns:
        if col not in ['Select', 'Index']:  # Skip already configured columns
            app_instance.stackup_ui_vars.tree.heading(col, text=col)
            if col == 'Name':
                width = 150
            elif col == 'Type':
                width = 120
            elif col == 'Material':
                width = 140
            elif col == 'Dielectric Fill':
                width = 140
            elif col == 'Thickness':
                width = 120
            else:
                width = 100
            app_instance.stackup_ui_vars.tree.column(col, width=width, stretch=True)
    
    # Initialize checkbox widgets dictionary
    app_instance.stackup_ui_vars.checkbox_widgets = {}

    # Add vertical scrollbar for table
    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=app_instance.stackup_ui_vars.tree.yview, style="PyAEDT.Vertical.TScrollbar")
    app_instance.stackup_ui_vars.tree.configure(yscrollcommand=scrollbar.set)
    
    # Position table and scrollbar
    app_instance.stackup_ui_vars.tree.grid(row=1, column=0, sticky='nsew')
    scrollbar.grid(row=1, column=1, sticky='ns')
    
    # Add right-click menu
    context_menu = tk.Menu(app_instance.stackup_ui_vars.tree, tearoff=0)
    context_menu.add_command(label="Add Layer", command=lambda: add_layer(app_instance))
    context_menu.add_command(label="Edit Layer", command=lambda: edit_layer(app_instance))
    context_menu.add_command(label="Delete Layer", command=lambda: delete_layer(app_instance))
    context_menu.add_separator()
    context_menu.add_command(label="Move Up", command=lambda: move_layer_up(app_instance))
    context_menu.add_command(label="Move Down", command=lambda: move_layer_down(app_instance))

    def show_context_menu(event):
        item = app_instance.stackup_ui_vars.tree.identify_row(event.y)
        if item:
            app_instance.stackup_ui_vars.tree.selection_set(item)
            context_menu.post(event.x_root, event.y_root)

    app_instance.stackup_ui_vars.tree.bind("<Button-3>", show_context_menu)
    
    # Event handling for single click and double click
    click_timer = None
    
    def on_single_click(event):
        nonlocal click_timer
        if click_timer:
            app_instance.root.after_cancel(click_timer)
        
        # Delay single click handling to distinguish from double click
        click_timer = app_instance.root.after(200, lambda: handle_single_click(event))
    
    def on_double_click(event):
        nonlocal click_timer
        # Cancel single click timer if double click occurs
        if click_timer:
            app_instance.root.after_cancel(click_timer)
            click_timer = None
        
        # Handle double click - edit layer
        edit_layer(app_instance)
    
    def handle_single_click(event):
        region = app_instance.stackup_ui_vars.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = app_instance.stackup_ui_vars.tree.identify_column(event.x)
            if column == '#1':  # Select column (checkbox column)
                item = app_instance.stackup_ui_vars.tree.identify_row(event.y)
                if item:
                    # Toggle checkbox state
                    current_state = app_instance.stackup_ui_vars.checkbox_states.get(item, False)
                    new_state = not current_state
                    app_instance.stackup_ui_vars.checkbox_states[item] = new_state
                    
                    # Update checkbox symbol
                    values = list(app_instance.stackup_ui_vars.tree.item(item, 'values'))
                    values[0] = "☑" if new_state else "☐"
                    app_instance.stackup_ui_vars.tree.item(item, values=values)
                    
                    # Update selection
                    if new_state:
                        app_instance.stackup_ui_vars.tree.selection_add(item)
                    else:
                        app_instance.stackup_ui_vars.tree.selection_remove(item)
                    
                    # Update select all checkbox state
                    update_select_all_state(app_instance)
    
    # Bind events
    app_instance.stackup_ui_vars.tree.bind('<Button-1>', on_single_click)
    app_instance.stackup_ui_vars.tree.bind('<Double-1>', on_double_click)

    # Stackup visualization area
    image_frame = ttk.Frame(table_image_frame, style="PyAEDT.TFrame")
    image_frame.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
    
    # Configure image frame for resizing
    image_frame.grid_rowconfigure(0, weight=1)
    image_frame.grid_columnconfigure(0, weight=1)

    try:
        current_script_directory = Path(__file__).parent
        stackup_demo_image_path = current_script_directory / "stackup_demo.png"
        stackup_demo_image = Image.open(stackup_demo_image_path)
        app_instance.stackup_ui_vars.diagram_image = ImageTk.PhotoImage(stackup_demo_image)
        stackup_image_label = ttk.Label(image_frame, image=app_instance.stackup_ui_vars.diagram_image, style="PyAEDT.TLabel")
        stackup_image_label.grid(row=0, column=0, sticky='nsew')
    except FileNotFoundError:
        image_not_found_label = ttk.Label(image_frame, text="Image not found\n(stackup_demo.png)", style="PyAEDT.TLabel")
        image_not_found_label.grid(row=0, column=0, sticky='nsew')
    except Exception as image_loading_error:
        image_error_label = ttk.Label(image_frame, text=f"Error loading image:\n{str(image_loading_error)}", style="PyAEDT.TLabel")
        image_error_label.grid(row=0, column=0, sticky='nsew')

    # Bottom button
    button_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=4, column=0, sticky="ew", pady=5)

    # Configure button_frame to make it resizable
    button_frame.grid_columnconfigure(3, weight=1)  # Last column takes remaining space
    
    ttk.Button(button_frame, text="Reset", command=lambda: reset_stackup(app_instance), style="PyAEDT.TButton").grid(row=0, column=0, padx=5, sticky='e')
    
    # Initialize default layers
    generate_default_stackup(app_instance)


def generate_default_stackup(app_instance):
    """Initialize default 4-layer PCB stackup structure.
    
    Args:
        app_instance: The main application instance
    """
    if app_instance.config_model.stackup:
        return update_stackup_tree(app_instance)
    
    # Clear existing stackup in config_model
    app_instance.config_model.stackup = []
    
    # Build standard 4-layer PCB stackup using config_model methods
    app_instance.config_model.add_layer_at_bottom(name="PCB_L1", type="signal", material="copper", fill_material="fr4", thickness="22um")
    app_instance.config_model.add_layer_at_bottom(name="PCB_DE1", type="dielectric", material="fr4", fill_material="", thickness="30um")
    app_instance.config_model.add_layer_at_bottom(
        name="PCB_L2", type="signal", material="copper", fill_material="fr4", thickness="15um"
    )
    app_instance.config_model.add_layer_at_bottom(name="PCB_DE2", type="dielectric", material="fr4", fill_material="", thickness="30um")
    app_instance.config_model.add_layer_at_bottom(
        name="PCB_L3", type="signal", material="copper", fill_material="fr4", thickness="15um"
    )
    app_instance.config_model.add_layer_at_bottom(name="PCB_DE3", type="dielectric", material="fr4", fill_material="", thickness="30um")
    app_instance.config_model.add_layer_at_bottom(
        name="PCB_L4", type="signal", material="copper", fill_material="fr4", thickness="15um"
    )

    update_stackup_tree(app_instance)

def generate_stackup(app_instance):
    """Generate PCB stackup structure based on selected layer count.
    
    Args:
        app_instance: The main application instance containing UI elements
    """
    try:
        layer_count = int(app_instance.stackup_ui_vars.layer_count.get())
        if layer_count < 1:
            messagebox.showerror("Error", "Layer count must be at least 1")
            return

        # Clear existing stackup in config_model
        app_instance.config_model.stackup = []
        
        # Add top metal layer using config_model
        app_instance.config_model.add_layer_at_bottom(
            name="PCB_L1",
            type="signal",
            material="copper",
            fill_material="fr4",
            thickness="50um"
        )
        
        # Add remaining layers using config_model methods
        for i in range(1, layer_count):
            # Add dielectric layer
            app_instance.config_model.add_layer_at_bottom(
                name=f"PCB_DE{i}",
                type="dielectric",
                material="fr4",
                fill_material="",
                thickness="100um" if i % 2 == 1 else "125um"
            )

            # Add metal layer
            layer_thickness = "50um" if i == layer_count - 1 else "17um"
            app_instance.config_model.add_layer_at_bottom(
                name=f"PCB_L{i + 1}", type="signal", material="copper", fill_material="fr4", thickness=layer_thickness
            )

        update_stackup_tree(app_instance)
        messagebox.showinfo("Success", f"Generated {layer_count}-layer PCB structure")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid layer count")

def update_select_all_state(app_instance):
    """Update the select all checkbox state based on individual layer selections.
    
    Args:
        app_instance: The main application instance
    """
    if not hasattr(app_instance, 'stackup_ui_vars') or not hasattr(app_instance.stackup_ui_vars, 'checkbox_states'):
        return
    
    all_items = app_instance.stackup_ui_vars.tree.get_children()
    if not all_items:
        app_instance.stackup_ui_vars.select_all_var.set(False)
        return
    
    checked_count = sum(1 for item in all_items if app_instance.stackup_ui_vars.checkbox_states.get(item, False))
    
    if checked_count == len(all_items):
        app_instance.stackup_ui_vars.select_all_var.set(True)
    else:
        app_instance.stackup_ui_vars.select_all_var.set(False)

def toggle_all_selections(app_instance):
    """Toggle selection state for all layers in the stackup table.
    
    Args:
        app_instance: The main application instance
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    if not hasattr(app_instance.stackup_ui_vars, 'checkbox_states'):
        app_instance.stackup_ui_vars.checkbox_states = {}
    
    select_all = app_instance.stackup_ui_vars.select_all_var.get()
    
    # Reset other button states when Select All is activated
    if select_all:
        app_instance.stackup_ui_vars.metal_selected = False
        app_instance.stackup_ui_vars.dielectric_selected = False
        app_instance.stackup_ui_vars.select_metal_button.config(text="Select Metal")
        app_instance.stackup_ui_vars.select_dielectric_button.config(text="Select Dielectric")
    
    for item in app_instance.stackup_ui_vars.tree.get_children():
        # Update checkbox state
        app_instance.stackup_ui_vars.checkbox_states[item] = select_all
        
        # Update checkbox symbol
        values = list(app_instance.stackup_ui_vars.tree.item(item, 'values'))
        values[0] = "☑" if select_all else "☐"
        app_instance.stackup_ui_vars.tree.item(item, values=values)
        
        # Update selection
        if select_all:
            app_instance.stackup_ui_vars.tree.selection_add(item)
        else:
            app_instance.stackup_ui_vars.tree.selection_remove(item)

def toggle_select_by_type(app_instance, layer_type):
    """Toggle selection of layers by type (signal/dielectric) with button state management.
    
    Args:
        app_instance: The main application instance
        layer_type: Type of layers to select ('signal' or 'dielectric')
    """
    if not hasattr(app_instance.stackup_ui_vars, 'checkbox_states'):
        app_instance.stackup_ui_vars.checkbox_states = {}
    
    # Determine current state and target state
    if layer_type == 'signal':
        current_selected = app_instance.stackup_ui_vars.metal_selected
        app_instance.stackup_ui_vars.metal_selected = not current_selected
        target_state = app_instance.stackup_ui_vars.metal_selected
        button = app_instance.stackup_ui_vars.select_metal_button
        button_text = "Deselect Metal" if target_state else "Select Metal"
        
        # Reset other button states when this button is activated
        if target_state:
            app_instance.stackup_ui_vars.dielectric_selected = False
            app_instance.stackup_ui_vars.select_dielectric_button.config(text="Select Dielectric")
            app_instance.stackup_ui_vars.select_all_var.set(False)
    else:  # dielectric
        current_selected = app_instance.stackup_ui_vars.dielectric_selected
        app_instance.stackup_ui_vars.dielectric_selected = not current_selected
        target_state = app_instance.stackup_ui_vars.dielectric_selected
        button = app_instance.stackup_ui_vars.select_dielectric_button
        button_text = "Deselect Dielectric" if target_state else "Select Dielectric"
        
        # Reset other button states when this button is activated
        if target_state:
            app_instance.stackup_ui_vars.metal_selected = False
            app_instance.stackup_ui_vars.select_metal_button.config(text="Select Metal")
            app_instance.stackup_ui_vars.select_all_var.set(False)
    
    # Update button text
    button.config(text=button_text)
    
    # If activating this button, first clear all selections
    if target_state:
        # Clear all current selections
        for item in app_instance.stackup_ui_vars.tree.get_children():
            app_instance.stackup_ui_vars.checkbox_states[item] = False
            values = list(app_instance.stackup_ui_vars.tree.item(item)['values'])
            values[0] = "☐"
            app_instance.stackup_ui_vars.tree.item(item, values=values)
            app_instance.stackup_ui_vars.tree.selection_remove(item)
    
    # Update selections for the target layer type
    for item in app_instance.stackup_ui_vars.tree.get_children():
        values = app_instance.stackup_ui_vars.tree.item(item)['values']
        # Check if this item matches the layer type (Select=0, Index=1, Name=2, Type=3)
        if len(values) > 3 and values[3] == layer_type:
            # Update checkbox state
            app_instance.stackup_ui_vars.checkbox_states[item] = target_state
            # Update display
            new_values = list(values)
            new_values[0] = "☑" if target_state else "☐"
            app_instance.stackup_ui_vars.tree.item(item, values=new_values)
            # Update selection
            if target_state:
                app_instance.stackup_ui_vars.tree.selection_add(item)
            else:
                app_instance.stackup_ui_vars.tree.selection_remove(item)
    
    # Update select all checkbox state
    update_select_all_state(app_instance)

def select_by_type(app_instance, layer_type):
    """Select layers by type - legacy function for compatibility.
    
    Args:
        app_instance: The main application instance
        layer_type: Type of layers to select
    """
    if not hasattr(app_instance.stackup_ui_vars, 'checkbox_states'):
        app_instance.stackup_ui_vars.checkbox_states = {}
    if not hasattr(app_instance.stackup_ui_vars, 'checkbox_widgets'):
        app_instance.stackup_ui_vars.checkbox_widgets = {}
    
    # Clear all selections and checkboxes first
    app_instance.stackup_ui_vars.tree.selection_clear()
    
    for item in app_instance.stackup_ui_vars.tree.get_children():
        values = app_instance.stackup_ui_vars.tree.item(item)['values']
        # Check if this item matches the layer type (Select=0, Index=1, Name=2, Type=3)
        if len(values) > 3 and values[3] == layer_type:
            # Select this item
            app_instance.stackup_ui_vars.tree.selection_add(item)
            # Update checkbox state
            app_instance.stackup_ui_vars.checkbox_states[item] = True
            # Update checkbox symbol
            updated_values = list(values)
            updated_values[0] = "☑"
            app_instance.stackup_ui_vars.tree.item(item, values=updated_values)
        else:
            # Uncheck this item
            app_instance.stackup_ui_vars.checkbox_states[item] = False
            # Update checkbox symbol
            updated_values = list(values)
            updated_values[0] = "☐"
            app_instance.stackup_ui_vars.tree.item(item, values=updated_values)
    
    # Update select all checkbox state
    update_select_all_state(app_instance)

def batch_edit_layers(app_instance):
    """Open batch edit dialog for selected layers.
    
    Args:
        app_instance: The main application instance
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    selected_items = app_instance.stackup_ui_vars.tree.selection()
    if not selected_items:
        messagebox.showinfo("Information", "Please select layers to edit")
        return
    
    # Create edit window
    edit_window = tk.Toplevel()
    edit_window.title("Batch Edit Layers")
    edit_window.geometry("400x400")
    edit_window.resizable(False, False)
    edit_window.grab_set()  # Modal window

    # Apply PyAEDT style to the window content
    main_frame = ttk.Frame(edit_window, style="PyAEDT.TFrame")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create form
    ttk.Label(main_frame, text="Material:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    material_combo = ttk.Combobox(main_frame, width=28, values=["copper", "aluminum", "gold", ""], style="PyAEDT.TCombobox")
    material_combo.grid(row=0, column=1, padx=10, pady=5)
    
    ttk.Label(main_frame, text="Dielectric Fill:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    dielectric_combo = ttk.Combobox(main_frame, width=28, values=["", "fr4", "air", "polyimide"], style="PyAEDT.TCombobox")
    dielectric_combo.grid(row=1, column=1, padx=10, pady=5)
    
    ttk.Label(main_frame, text="Thickness:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    thickness_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    thickness_entry.grid(row=2, column=1, padx=10, pady=5)
    
    # Create buttons
    button_frame = ttk.Frame(main_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)
    
    def save_changes():
        for item in selected_items:
            idx = app_instance.stackup_ui_vars.tree.index(item)
            layer = app_instance.config_model.stackup[idx]
            
            if material_combo.get():
                layer.material = material_combo.get()
            if dielectric_combo.get():
                layer.fill_material = dielectric_combo.get()
            if thickness_entry.get():
                layer.thickness = thickness_entry.get()
        
        update_stackup_tree(app_instance)
        edit_window.destroy()
    
    ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, style="PyAEDT.TButton").pack(side="right", padx=5)
    ttk.Button(button_frame, text="Save", command=save_changes, style="PyAEDT.TButton").pack(side="right", padx=5)

def update_stackup_tree(app_instance):
    """Refresh the stackup table display with current layer data.
    
    Args:
        app_instance: The main application instance containing UI elements
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    # Clear existing table entries
    for item in app_instance.stackup_ui_vars.tree.get_children():
        app_instance.stackup_ui_vars.tree.delete(item)
    
    # Initialize checkbox states dictionary
    if not hasattr(app_instance.stackup_ui_vars, 'checkbox_states'):
        app_instance.stackup_ui_vars.checkbox_states = {}
    
    # Reset selection button states to default
    if hasattr(app_instance.stackup_ui_vars, 'metal_selected'):
        app_instance.stackup_ui_vars.metal_selected = False
        app_instance.stackup_ui_vars.select_metal_button.config(text="Select Metal")
    if hasattr(app_instance.stackup_ui_vars, 'dielectric_selected'):
        app_instance.stackup_ui_vars.dielectric_selected = False
        app_instance.stackup_ui_vars.select_dielectric_button.config(text="Select Dielectric")
    
    # Populate table with current stackup layer data from config_model
    for layer_index, stackup_layer in enumerate(app_instance.config_model.stackup, 1):
        tree_item_id = app_instance.stackup_ui_vars.tree.insert("", "end", values=(
            "☐",  # Unchecked checkbox symbol
            str(layer_index),  # Layer index
            stackup_layer.name if stackup_layer.name else "",
            stackup_layer.type if stackup_layer.type else "",
            stackup_layer.material if stackup_layer.material else "",
            stackup_layer.fill_material if stackup_layer.fill_material else "",
            stackup_layer.thickness if stackup_layer.thickness else ""
        ))
        
        # Initialize checkbox state as unchecked
        app_instance.stackup_ui_vars.checkbox_states[tree_item_id] = False
    


def add_layer(app_instance):
    """Open dialog window to add a new layer to the stackup configuration.
    
    Args:
        app_instance: The main application instance containing stackup data
    """
    # Create modal dialog window
    add_layer_dialog = tk.Toplevel()
    add_layer_dialog.title("Add Layer")
    add_layer_dialog.geometry("400x400")
    add_layer_dialog.resizable(False, False)
    add_layer_dialog.grab_set()  # Make window modal
    
    # Create main container frame with PyAEDT styling
    dialog_main_frame = ttk.Frame(add_layer_dialog, style="PyAEDT.TFrame")
    dialog_main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create form
    ttk.Label(dialog_main_frame, text="Layer Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    layer_name_entry = ttk.Entry(dialog_main_frame, width=30, style="PyAEDT.TEntry")
    layer_name_entry.grid(row=0, column=1, padx=10, pady=5)
    layer_name_entry.insert(0, f"PKG_L{len(app_instance.config_model.stackup) + 1}")
    
    ttk.Label(dialog_main_frame, text="Layer Type:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    layer_type_combobox = ttk.Combobox(dialog_main_frame, width=28, values=["signal", "dielectric", "plane"], style="PyAEDT.TCombobox")
    layer_type_combobox.grid(row=1, column=1, padx=10, pady=5)
    layer_type_combobox.set("signal")
    
    ttk.Label(dialog_main_frame, text="Material:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    layer_material_combobox = ttk.Combobox(dialog_main_frame, width=28, values=["copper", "aluminum", "gold", ""], style="PyAEDT.TCombobox")
    layer_material_combobox.grid(row=2, column=1, padx=10, pady=5)
    layer_material_combobox.set("copper")
    
    ttk.Label(dialog_main_frame, text="Dielectric Fill:", style="PyAEDT.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    dielectric_fill_combobox = ttk.Combobox(dialog_main_frame, width=28, values=["", "fr4", "air", "polyimide"], style="PyAEDT.TCombobox")
    dielectric_fill_combobox.grid(row=3, column=1, padx=10, pady=5)
    dielectric_fill_combobox.set("")
    
    ttk.Label(dialog_main_frame, text="Thickness:", style="PyAEDT.TLabel").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    layer_thickness_entry = ttk.Entry(dialog_main_frame, width=30, style="PyAEDT.TEntry")
    layer_thickness_entry.grid(row=4, column=1, padx=10, pady=5)
    layer_thickness_entry.insert(0, "15um")
    
    # Create buttons
    dialog_button_frame = ttk.Frame(dialog_main_frame, style="PyAEDT.TFrame")
    dialog_button_frame.grid(row=9, column=0, columnspan=2, pady=10)
    
    # Define save_layer function inside add_layer to access local variables
    def save_new_layer():
        # Create a new layer with form data

        # Add to layers list
        app_instance.config_model.add_layer_at_bottom(
            name=layer_name_entry.get(),
            type=layer_type_combobox.get(),
            material=layer_material_combobox.get(),
            fill_material=dielectric_fill_combobox.get(),
            thickness=layer_thickness_entry.get(),
        )

        # Update table
        update_stackup_tree(app_instance)

        # Close window
        add_layer_dialog.destroy()
    
    ttk.Button(dialog_button_frame, text="Save", command=save_new_layer, style="PyAEDT.TButton").pack(side="left", padx=10)
    ttk.Button(dialog_button_frame, text="Cancel", command=add_layer_dialog.destroy, style="PyAEDT.TButton").pack(side="left", padx=10)

def edit_layer(app_instance):
    """Open dialog window to edit properties of the selected layer.
    
    Args:
        app_instance: The main application instance containing stackup data
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    selection = app_instance.stackup_ui_vars.tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    # Get selected layer data
    selected_layer_index = app_instance.stackup_ui_vars.tree.index(selection[0])
    selected_layer = app_instance.config_model.stackup[selected_layer_index]
    
    # Create modal edit dialog
    edit_layer_dialog = tk.Toplevel()
    edit_layer_dialog.title("Edit Layer")
    edit_layer_dialog.geometry("400x400")
    edit_layer_dialog.resizable(False, False)
    edit_layer_dialog.grab_set()  # Make window modal
    
    # Apply PyAEDT style to the window content
    edit_dialog_main_frame = ttk.Frame(edit_layer_dialog, style="PyAEDT.TFrame")
    edit_dialog_main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create form
    ttk.Label(edit_dialog_main_frame, text="Layer Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    edit_layer_name_entry = ttk.Entry(edit_dialog_main_frame, width=30, style="PyAEDT.TEntry")
    edit_layer_name_entry.grid(row=0, column=1, padx=10, pady=5)
    edit_layer_name_entry.insert(0, selected_layer.name)
    
    ttk.Label(edit_dialog_main_frame, text="Layer Type:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    edit_layer_type_combobox = ttk.Combobox(edit_dialog_main_frame, width=28, values=["signal", "dielectric", "plane"], style="PyAEDT.TCombobox")
    edit_layer_type_combobox.grid(row=1, column=1, padx=10, pady=5)
    edit_layer_type_combobox.set(selected_layer.type)
    
    ttk.Label(edit_dialog_main_frame, text="Material:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    edit_layer_material_combobox = ttk.Combobox(edit_dialog_main_frame, width=28, values=["copper", "aluminum", "gold", ""], style="PyAEDT.TCombobox")
    edit_layer_material_combobox.grid(row=2, column=1, padx=10, pady=5)
    edit_layer_material_combobox.set(selected_layer.material)
    
    ttk.Label(edit_dialog_main_frame, text="Dielectric Fill:", style="PyAEDT.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    edit_dielectric_fill_combobox = ttk.Combobox(edit_dialog_main_frame, width=28, values=["", "fr4", "air", "polyimide"], style="PyAEDT.TCombobox")
    edit_dielectric_fill_combobox.grid(row=3, column=1, padx=10, pady=5)
    edit_dielectric_fill_combobox.set(selected_layer.fill_material if selected_layer.fill_material else "")
    
    ttk.Label(edit_dialog_main_frame, text="Thickness:", style="PyAEDT.TLabel").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    edit_layer_thickness_entry = ttk.Entry(edit_dialog_main_frame, width=30, style="PyAEDT.TEntry")
    edit_layer_thickness_entry.grid(row=4, column=1, padx=10, pady=5)
    edit_layer_thickness_entry.insert(0, selected_layer.thickness)

    
    # Create buttons
    edit_dialog_button_frame = ttk.Frame(edit_dialog_main_frame, style="PyAEDT.TFrame")
    edit_dialog_button_frame.grid(row=9, column=0, columnspan=2, pady=10)
    
    # Define save_edited_layer function inside edit_layer to access local variables
    def save_edited_layer():
        # Update the layer with form data
        selected_layer.name = edit_layer_name_entry.get()
        selected_layer.type = edit_layer_type_combobox.get()
        selected_layer.material = edit_layer_material_combobox.get()
        selected_layer.fill_material = edit_dielectric_fill_combobox.get()
        selected_layer.thickness = edit_layer_thickness_entry.get()
        # selected_layer.etch = etch_entry.get()
        # selected_layer.rough = rough_entry.get()
        # selected_layer.solver = solver_entry.get()
        # selected_layer.transparency = int(transparency_entry.get() if transparency_entry.get() else 60)
        
        # Update table
        update_stackup_tree(app_instance)

        # Close window
        edit_layer_dialog.destroy()
    
    ttk.Button(edit_dialog_button_frame, text="Save", command=save_edited_layer, style="PyAEDT.TButton").pack(side="left", padx=10)
    ttk.Button(edit_dialog_button_frame, text="Cancel", command=edit_layer_dialog.destroy, style="PyAEDT.TButton").pack(side="left", padx=10)

def delete_layer(app_instance):
    """Delete the selected layer from the stackup configuration.
    
    Args:
        app_instance: The main application instance containing stackup data
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    selection = app_instance.stackup_ui_vars.tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    # Get selected layer index and confirm deletion
    selected_layer_index = app_instance.stackup_ui_vars.tree.index(selection[0])
    selected_layer_name = app_instance.config_model.stackup[selected_layer_index].name
    if messagebox.askyesno("Confirmation", f"Are you sure you want to delete layer '{selected_layer_name}'?"):
        del app_instance.config_model.stackup[selected_layer_index]
        update_stackup_tree(app_instance)

def move_layer_up(app_instance):
    """Move the selected layer up one position in the stackup order.
    
    Args:
        app_instance: The main application instance containing stackup data
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    selection = app_instance.stackup_ui_vars.tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    current_layer_index = app_instance.stackup_ui_vars.tree.index(selection[0])
    if current_layer_index > 0:
        # Swap current layer with the one above it
        stackup_layers = app_instance.config_model.stackup
        stackup_layers[current_layer_index], stackup_layers[current_layer_index-1] = stackup_layers[current_layer_index-1], stackup_layers[current_layer_index]
        update_stackup_tree(app_instance)
        
        # Maintain selection on the moved layer
        tree_items = app_instance.stackup_ui_vars.tree.get_children()
        app_instance.stackup_ui_vars.tree.selection_set(tree_items[current_layer_index-1])

def move_layer_down(app_instance):
    """Move the selected layer down one position in the stackup order.
    
    Args:
        app_instance: The main application instance containing stackup data
    """
    if not hasattr(app_instance, 'stackup_ui_vars'):
        return
        
    selection = app_instance.stackup_ui_vars.tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    current_layer_index = app_instance.stackup_ui_vars.tree.index(selection[0])
    if current_layer_index < len(app_instance.config_model.stackup) - 1:
        # Swap current layer with the one below it
        stackup_layers = app_instance.config_model.stackup
        stackup_layers[current_layer_index], stackup_layers[current_layer_index+1] = stackup_layers[current_layer_index+1], stackup_layers[current_layer_index]
        update_stackup_tree(app_instance)
        
        # Maintain selection on the moved layer
        tree_items = app_instance.stackup_ui_vars.tree.get_children()
        app_instance.stackup_ui_vars.tree.selection_set(tree_items[current_layer_index+1])

def reset_stackup(app_instance):
    """Reset the stackup configuration to default 4-layer PCB structure.
    
    Args:
        app_instance: The main application instance containing stackup data
    """
    confirmation_msg = "Are you sure you want to reset the stackup? All changes will be lost."
    if messagebox.askyesno("Confirmation", confirmation_msg):
        # Clear config_model stackup before generating default
        app_instance.config_model.stackup = []
        generate_default_stackup(app_instance)
