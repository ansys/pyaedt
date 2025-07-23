import os
import json
from pathlib import Path
import ansys.aedt.core
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog  # If you need to add functionality to the browse button

from ansys.aedt.core.extensions.misc import ExtensionCommon


class StackupLayer:
    def __init__(self, name="", layer_type="signal", material="copper", dielectric_fill="fr4", thickness="15um", etch="", rough="", solver="", transparency=60):
        self.name = name
        self.layer_type = layer_type
        self.material = material
        self.dielectric_fill = dielectric_fill
        self.thickness = thickness
        self.etch = etch
        self.rough = rough
        self.solver = solver
        self.transparency = transparency

    def to_dict(self):
        return {
            "name": self.name,
            "layer_type": self.layer_type,
            "material": self.material,
            "dielectric_fill": self.dielectric_fill,
            "thickness": self.thickness,
            "etch": self.etch,
            "rough": self.rough,
            "solver": self.solver,
            "transparency": self.transparency
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            layer_type=data.get("layer_type", "signal"),
            material=data.get("material", "copper"),
            dielectric_fill=data.get("dielectric_fill", "fr4"),
            thickness=data.get("thickness", "15um"),
            etch=data.get("etch", ""),
            rough=data.get("rough", ""),
            solver=data.get("solver", ""),
            transparency=data.get("transparency", 60)
        )


def create_stackup_settings_ui(tab_frame, app_instance):
    app_instance.stackup_layers = []  # List to store layer information
    
    # Configure tab_frame to make it resizable
    tab_frame.grid_rowconfigure(3, weight=1)  # Set table area row weight to 1
    tab_frame.grid_columnconfigure(0, weight=1)  # Set column weight to 1
    
    # File selection area
    file_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    file_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

    ttk.Label(file_frame, style="PyAEDT.TLabel", text="Material Model File").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(file_frame).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    ttk.Button(file_frame, text="Browse", style="PyAEDT.TButton").grid(row=0, column=2, padx=2, pady=5)

    ttk.Label(file_frame, text="Stackup Settings File", style="PyAEDT.TLabel").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(file_frame, style="PyAEDT.TEntry").grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    ttk.Button(file_frame, text="Browse", style="PyAEDT.TButton").grid(row=1, column=2, padx=2, pady=5)
    ttk.Button(file_frame, text="Import", style="PyAEDT.TButton").grid(row=1, column=3, padx=5, pady=5)
    file_frame.grid_columnconfigure(1, weight=1)

    # Parameter settings area
    params_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    params_frame.grid(row=1, column=0, sticky='ew')

    # First row of parameters
    ttk.Label(params_frame, text="PP Thickness(um)", style="PyAEDT.TLabel").grid(row=0, column=0, padx=(5, 5), pady=5, sticky='w')
    ttk.Entry(params_frame, width=15, style="PyAEDT.TEntry").grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="PP Material", style="PyAEDT.TLabel").grid(row=0, column=2, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12, style="PyAEDT.TCombobox").grid(row=0, column=3, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Core Thickness(um)", style="PyAEDT.TLabel").grid(row=0, column=4, padx=5, pady=5, sticky='w')
    ttk.Entry(params_frame, width=15, style="PyAEDT.TEntry").grid(row=0, column=5, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Core Material", style="PyAEDT.TLabel").grid(row=0, column=6, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12, style="PyAEDT.TCombobox").grid(row=0, column=7, sticky='ew', padx=5, pady=5)

    # Second row of parameters
    ttk.Label(params_frame, text="Metal Thickness(um)", style="PyAEDT.TLabel").grid(row=1, column=0, padx=(5, 5), pady=5, sticky='w')
    ttk.Entry(params_frame, width=15, style="PyAEDT.TEntry").grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Metal Material", style="PyAEDT.TLabel").grid(row=1, column=2, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12, style="PyAEDT.TCombobox").grid(row=1, column=3, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Soldermask Thickness(um)", style="PyAEDT.TLabel").grid(row=1, column=4, padx=5, pady=5, sticky='w')
    ttk.Entry(params_frame, width=15, style="PyAEDT.TEntry").grid(row=1, column=5, sticky='ew', padx=5, pady=5)
    ttk.Label(params_frame, text="Soldermask Material", style="PyAEDT.TLabel").grid(row=1, column=6, padx=5, pady=5, sticky='w')
    ttk.Combobox(params_frame, width=12, style="PyAEDT.TCombobox").grid(row=1, column=7, sticky='ew', padx=5, pady=5)

    # Set weights for all columns to make them adaptable to width
    for i in range(8):
        params_frame.grid_columnconfigure(i, weight=1)

    # Layer count selection and generate button
    layer_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    layer_frame.grid(row=2, column=0, sticky='ew')
    
    # Use grid instead of pack for layout
    ttk.Label(layer_frame, text="Number Of Metal Layers", style="PyAEDT.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    app_instance.layer_count = ttk.Combobox(layer_frame, width=5, values=[2, 4, 6, 8, 10, 12, 14, 16], style="PyAEDT.TCombobox")
    app_instance.layer_count.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    app_instance.layer_count.set(4)  # Default value
    
    generate_button = ttk.Button(layer_frame, text="Generate", command=lambda: generate_stackup(app_instance), style="PyAEDT.TButton")
    generate_button.grid(row=0, column=2, padx=20, pady=5, sticky='w')
    
    # Set column weights for layer_frame
    layer_frame.grid_columnconfigure(3, weight=1)  # Last column takes remaining space

    # Table area
    # Create a horizontal layout Frame to hold the table and image
    table_image_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    table_image_frame.grid(row=3, column=0, sticky='nsew', pady=(5, 0))
    
    # Configure table_image_frame to make it resizable
    table_image_frame.grid_rowconfigure(0, weight=1)
    table_image_frame.grid_columnconfigure(0, weight=3)  # Table area takes 75%
    table_image_frame.grid_columnconfigure(1, weight=1)  # Image area takes 25%

    # Table area - takes 75% of width
    table_frame = ttk.Frame(table_image_frame, style="PyAEDT.TFrame")
    table_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
    
    # Configure table_frame to make it resizable
    table_frame.grid_rowconfigure(1, weight=1)  # Table row
    table_frame.grid_columnconfigure(0, weight=1)  # Column
    
    # Button area above the table
    table_buttons_frame = ttk.Frame(table_frame, style="PyAEDT.TFrame")
    table_buttons_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
    
    # Use grid layout for buttons
    add_layer_button = ttk.Button(table_buttons_frame, text="Add Layer", command=lambda: add_layer(app_instance), style="PyAEDT.TButton")
    add_layer_button.grid(row=0, column=0, padx=5, sticky='w')
    
    delete_layer_button = ttk.Button(table_buttons_frame, text="Delete Layer", command=lambda: delete_layer(app_instance), style="PyAEDT.TButton")
    delete_layer_button.grid(row=0, column=1, padx=5, sticky='w')
    
    edit_layer_button = ttk.Button(table_buttons_frame, text="Edit Layer", command=lambda: edit_layer(app_instance), style="PyAEDT.TButton")
    edit_layer_button.grid(row=0, column=2, padx=5, sticky='w')
    
    move_up_button = ttk.Button(table_buttons_frame, text="Move Up", command=lambda: move_layer_up(app_instance), style="PyAEDT.TButton")
    move_up_button.grid(row=0, column=3, padx=5, sticky='w')
    
    move_down_button = ttk.Button(table_buttons_frame, text="Move Down", command=lambda: move_layer_down(app_instance), style="PyAEDT.TButton")
    move_down_button.grid(row=0, column=4, padx=5, sticky='w')
    
    # Set the last column to take remaining space
    table_buttons_frame.grid_columnconfigure(5, weight=1)
    
    # Create table
    columns = ('Name', 'Type', 'Material', 'Dielectric Fill', 'Thickness', 'Etch', 'Rough', 'Solver', 'Transparency')
    app_instance.stackup_tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse', style="PyAEDT.Treeview")

    # Set column headers
    for col in columns:
        app_instance.stackup_tree.heading(col, text=col)
        width = 100 if col != 'Name' else 120
        app_instance.stackup_tree.column(col, width=width)

    app_instance.stackup_tree.grid(row=1, column=0, sticky='nsew')
    
    # Add right-click menu
    context_menu = tk.Menu(app_instance.stackup_tree, tearoff=0)
    context_menu.add_command(label="Add Layer", command=lambda: add_layer(app_instance))
    context_menu.add_command(label="Edit Layer", command=lambda: edit_layer(app_instance))
    context_menu.add_command(label="Delete Layer", command=lambda: delete_layer(app_instance))
    context_menu.add_separator()
    context_menu.add_command(label="Move Up", command=lambda: move_layer_up(app_instance))
    context_menu.add_command(label="Move Down", command=lambda: move_layer_down(app_instance))
    
    def show_context_menu(event):
        item = app_instance.stackup_tree.identify_row(event.y)
        if item:
            app_instance.stackup_tree.selection_set(item)
            context_menu.post(event.x_root, event.y_root)
    
    app_instance.stackup_tree.bind("<Button-3>", show_context_menu)
    
    # Double-click to edit
    app_instance.stackup_tree.bind("<Double-1>", lambda event: edit_layer(app_instance))

    # Image area - takes 25% of width
    image_frame = ttk.Frame(table_image_frame, style="PyAEDT.TFrame")
    image_frame.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
    
    # Configure image_frame to make it resizable
    image_frame.grid_rowconfigure(0, weight=1)
    image_frame.grid_columnconfigure(0, weight=1)
    
    try:
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "stackup_demo.png")  # Assuming the image name is stackup_diagram.png
        image = Image.open(image_path)
        app_instance.diagram_image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(image_frame, image=app_instance.diagram_image, style="PyAEDT.TLabel")
        image_label.grid(row=0, column=0, sticky='nsew')
    except FileNotFoundError:
        error_label = ttk.Label(image_frame, text="Image not found\n(stackup_diagram.png)", style="PyAEDT.TLabel")
        error_label.grid(row=0, column=0, sticky='nsew')
    except Exception as e:
        error_label = ttk.Label(image_frame, text=f"Error loading image:\n{str(e)}", style="PyAEDT.TLabel")
        error_label.grid(row=0, column=0, sticky='nsew')

    # Bottom buttons
    button_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=4, column=0, sticky='ew', pady=5)
    
    # Configure button_frame to make it resizable
    button_frame.grid_columnconfigure(3, weight=1)  # Last column takes remaining space
    
    ttk.Button(button_frame, text="Reset", command=lambda: reset_stackup(app_instance), style="PyAEDT.TButton").grid(row=0, column=0, padx=5, sticky='e')
    ttk.Button(button_frame, text="Apply", command=lambda: apply_stackup(app_instance), style="PyAEDT.TButton").grid(row=0, column=1, padx=5, sticky='e')
    ttk.Button(button_frame, text="Export", command=lambda: export_stackup(app_instance), style="PyAEDT.TButton").grid(row=0, column=2, padx=5, sticky='e')
    ttk.Button(button_frame, text="Import", command=lambda: import_stackup(app_instance), style="PyAEDT.TButton").grid(row=0, column=3, padx=5, sticky='e')
    
    # Initialize default layers
    generate_default_stackup(app_instance)


# Generate default stackup structure
def generate_default_stackup(app_instance):
    app_instance.stackup_layers = []
    # Add default 4-layer PCB structure
    app_instance.stackup_layers.append(StackupLayer(name="PCB_L1", layer_type="signal", material="copper", dielectric_fill="fr4", thickness="22um"))
    app_instance.stackup_layers.append(StackupLayer(name="PCB_DE1", layer_type="dielectric", material="", dielectric_fill="fr4", thickness="30um"))
    app_instance.stackup_layers.append(StackupLayer(name="PCB_L2", layer_type="signal", material="copper", dielectric_fill="fr4", thickness="15um"))
    app_instance.stackup_layers.append(StackupLayer(name="PCB_DE2", layer_type="dielectric", material="", dielectric_fill="fr4", thickness="30um"))
    app_instance.stackup_layers.append(StackupLayer(name="PCB_L3", layer_type="signal", material="copper", dielectric_fill="fr4", thickness="15um"))
    app_instance.stackup_layers.append(StackupLayer(name="PCB_DE3", layer_type="dielectric", material="", dielectric_fill="fr4", thickness="30um"))
    app_instance.stackup_layers.append(StackupLayer(name="PCB_L4", layer_type="signal", material="copper", dielectric_fill="fr4", thickness="15um"))
    
    update_stackup_tree(app_instance)

# Generate stackup structure based on layer count
def generate_stackup(app_instance):
    try:
        layer_count = int(app_instance.layer_count.get())
        if layer_count < 1:
            messagebox.showerror("Error", "Layer count must be at least 1")
            return
            
        app_instance.stackup_layers = []
        
        # 1. Add top metal layer (PCB_L1)
        app_instance.stackup_layers.append(StackupLayer(
            name="PCB_L1", 
            layer_type="signal", 
            material="copper", 
            dielectric_fill="fr4", 
            thickness="50um"  # 顶层较厚
        ))
        
        # 2. # Add middle layers
        for i in range(1, layer_count):
            # Add dielectric layer
            app_instance.stackup_layers.append(StackupLayer(
                name=f"PCB_DE{i}", 
                layer_type="dielectric", 
                material="fr4", 
                dielectric_fill="", 
                thickness="100um" if i % 2 == 1 else "125um"  # 交替厚度
            ))
            
            # Add metal layer
            layer_thickness = "50um" if i == layer_count - 1 else "17um"
            app_instance.stackup_layers.append(StackupLayer(
                name=f"PCB_L{i+1}", 
                layer_type="signal", 
                material="copper", 
                dielectric_fill="fr4", 
                thickness=layer_thickness
            ))
        
        update_stackup_tree(app_instance)
        messagebox.showinfo("Success", f"Generated {layer_count}-layer PCB structure")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid layer count")

# Update table display
def update_stackup_tree(app_instance):
    # Clear table
    for item in app_instance.stackup_tree.get_children():
        app_instance.stackup_tree.delete(item)
    
    # Add layers to table
    for layer in app_instance.stackup_layers:
        app_instance.stackup_tree.insert("", "end", values=(
            layer.name,
            layer.layer_type,
            layer.material,
            layer.dielectric_fill,
            layer.thickness,
            layer.etch,
            layer.rough,
            layer.solver,
            layer.transparency
        ))

# Add new layer
def add_layer(app_instance):
    # Create edit window
    edit_window = tk.Toplevel()
    edit_window.title("Add Layer")
    edit_window.geometry("400x400")
    edit_window.resizable(False, False)
    edit_window.grab_set()  # Modal window
    
    # Apply PyAEDT style to the window content
    main_frame = ttk.Frame(edit_window, style="PyAEDT.TFrame")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create form
    ttk.Label(main_frame, text="Layer Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    name_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    name_entry.insert(0, f"PKG_L{len(app_instance.stackup_layers) + 1}")
    
    ttk.Label(main_frame, text="Layer Type:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    layer_type_combo = ttk.Combobox(main_frame, width=28, values=["signal", "dielectric", "plane"], style="PyAEDT.TCombobox")
    layer_type_combo.grid(row=1, column=1, padx=10, pady=5)
    layer_type_combo.set("signal")
    
    ttk.Label(main_frame, text="Material:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    material_combo = ttk.Combobox(main_frame, width=28, values=["copper", "aluminum", "gold", ""], style="PyAEDT.TCombobox")
    material_combo.grid(row=2, column=1, padx=10, pady=5)
    material_combo.set("copper")
    
    ttk.Label(main_frame, text="Dielectric Fill:", style="PyAEDT.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    dielectric_combo = ttk.Combobox(main_frame, width=28, values=["fr4", "air", "polyimide"], style="PyAEDT.TCombobox")
    dielectric_combo.grid(row=3, column=1, padx=10, pady=5)
    dielectric_combo.set("fr4")
    
    ttk.Label(main_frame, text="Thickness:", style="PyAEDT.TLabel").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    thickness_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    thickness_entry.grid(row=4, column=1, padx=10, pady=5)
    thickness_entry.insert(0, "15um")
    
    ttk.Label(main_frame, text="Etch:", style="PyAEDT.TLabel").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    etch_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    etch_entry.grid(row=5, column=1, padx=10, pady=5)
    
    ttk.Label(main_frame, text="Roughness:", style="PyAEDT.TLabel").grid(row=6, column=0, sticky="w", padx=10, pady=5)
    rough_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    rough_entry.grid(row=6, column=1, padx=10, pady=5)
    
    ttk.Label(main_frame, text="Solver:", style="PyAEDT.TLabel").grid(row=7, column=0, sticky="w", padx=10, pady=5)
    solver_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    solver_entry.grid(row=7, column=1, padx=10, pady=5)
    
    ttk.Label(main_frame, text="Transparency:", style="PyAEDT.TLabel").grid(row=8, column=0, sticky="w", padx=10, pady=5)
    transparency_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    transparency_entry.grid(row=8, column=1, padx=10, pady=5)
    transparency_entry.insert(0, "60")
    
    # Create buttons
    button_frame = ttk.Frame(main_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=9, column=0, columnspan=2, pady=10)
    
    # Define save_layer function inside add_layer to access local variables
    def save_layer():
        # Create a new layer with form data
        new_layer = StackupLayer(
            name=name_entry.get(),
            layer_type=layer_type_combo.get(),
            material=material_combo.get(),
            dielectric_fill=dielectric_combo.get(),
            thickness=thickness_entry.get(),
            etch=etch_entry.get(),
            rough=rough_entry.get(),
            solver=solver_entry.get(),
            transparency=int(transparency_entry.get() if transparency_entry.get() else 60)
        )
        
        # Add to layers list
        app_instance.stackup_layers.append(new_layer)
        
        # Update table
        update_stackup_tree(app_instance)
        
        # Close window
        edit_window.destroy()
    
    ttk.Button(button_frame, text="Save", command=save_layer, style="PyAEDT.TButton").pack(side="left", padx=10)
    ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, style="PyAEDT.TButton").pack(side="left", padx=10)

# Edit selected layer
def edit_layer(app_instance):
    selection = app_instance.stackup_tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    idx = app_instance.stackup_tree.index(selection[0])
    layer = app_instance.stackup_layers[idx]
    
    # Create edit window
    edit_window = tk.Toplevel()
    edit_window.title("Edit Layer")
    edit_window.geometry("400x400")
    edit_window.resizable(False, False)
    edit_window.grab_set()  # Modal window
    
    # Apply PyAEDT style to the window content
    main_frame = ttk.Frame(edit_window, style="PyAEDT.TFrame")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create form
    ttk.Label(main_frame, text="Layer Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    name_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    name_entry.insert(0, layer.name)
    
    ttk.Label(main_frame, text="Layer Type:", style="PyAEDT.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    layer_type_combo = ttk.Combobox(main_frame, width=28, values=["signal", "dielectric", "plane"], style="PyAEDT.TCombobox")
    layer_type_combo.grid(row=1, column=1, padx=10, pady=5)
    layer_type_combo.set(layer.layer_type)
    
    ttk.Label(main_frame, text="Material:", style="PyAEDT.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    material_combo = ttk.Combobox(main_frame, width=28, values=["copper", "aluminum", "gold", ""], style="PyAEDT.TCombobox")
    material_combo.grid(row=2, column=1, padx=10, pady=5)
    material_combo.set(layer.material)
    
    ttk.Label(main_frame, text="Dielectric Fill:", style="PyAEDT.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    dielectric_combo = ttk.Combobox(main_frame, width=28, values=["fr4", "air", "polyimide"], style="PyAEDT.TCombobox")
    dielectric_combo.grid(row=3, column=1, padx=10, pady=5)
    dielectric_combo.set(layer.dielectric_fill)
    
    ttk.Label(main_frame, text="Thickness:", style="PyAEDT.TLabel").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    thickness_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    thickness_entry.grid(row=4, column=1, padx=10, pady=5)
    thickness_entry.insert(0, layer.thickness)
    
    ttk.Label(main_frame, text="Etch:", style="PyAEDT.TLabel").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    etch_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    etch_entry.grid(row=5, column=1, padx=10, pady=5)
    etch_entry.insert(0, layer.etch)
    
    ttk.Label(main_frame, text="Roughness:", style="PyAEDT.TLabel").grid(row=6, column=0, sticky="w", padx=10, pady=5)
    rough_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    rough_entry.grid(row=6, column=1, padx=10, pady=5)
    rough_entry.insert(0, layer.rough)
    
    ttk.Label(main_frame, text="Solver:", style="PyAEDT.TLabel").grid(row=7, column=0, sticky="w", padx=10, pady=5)
    solver_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    solver_entry.grid(row=7, column=1, padx=10, pady=5)
    solver_entry.insert(0, layer.solver)
    
    ttk.Label(main_frame, text="Transparency:", style="PyAEDT.TLabel").grid(row=8, column=0, sticky="w", padx=10, pady=5)
    transparency_entry = ttk.Entry(main_frame, width=30, style="PyAEDT.TEntry")
    transparency_entry.grid(row=8, column=1, padx=10, pady=5)
    transparency_entry.insert(0, str(layer.transparency))
    
    # Create buttons
    button_frame = ttk.Frame(main_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=9, column=0, columnspan=2, pady=10)
    
    # Define save_layer function inside edit_layer to access local variables
    def save_layer():
        # Update the layer with form data
        layer.name = name_entry.get()
        layer.layer_type = layer_type_combo.get()
        layer.material = material_combo.get()
        layer.dielectric_fill = dielectric_combo.get()
        layer.thickness = thickness_entry.get()
        layer.etch = etch_entry.get()
        layer.rough = rough_entry.get()
        layer.solver = solver_entry.get()
        layer.transparency = int(transparency_entry.get() if transparency_entry.get() else 60)
        
        # Update table
        update_stackup_tree(app_instance)
        
        # Close window
        edit_window.destroy()
    
    ttk.Button(button_frame, text="Save", command=save_layer, style="PyAEDT.TButton").pack(side="left", padx=10)
    ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, style="PyAEDT.TButton").pack(side="left", padx=10)

# Delete selected layer
def delete_layer(app_instance):
    selection = app_instance.stackup_tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    idx = app_instance.stackup_tree.index(selection[0])
    if messagebox.askyesno("Confirmation", f"Are you sure you want to delete layer '{app_instance.stackup_layers[idx].name}'?"):
        del app_instance.stackup_layers[idx]
        update_stackup_tree(app_instance)

# Move selected layer up
def move_layer_up(app_instance):
    selection = app_instance.stackup_tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    idx = app_instance.stackup_tree.index(selection[0])
    if idx > 0:
        app_instance.stackup_layers[idx], app_instance.stackup_layers[idx-1] = app_instance.stackup_layers[idx-1], app_instance.stackup_layers[idx]
        update_stackup_tree(app_instance)
        # Reselect the moved item
        items = app_instance.stackup_tree.get_children()
        app_instance.stackup_tree.selection_set(items[idx-1])

# Move selected layer down
def move_layer_down(app_instance):
    selection = app_instance.stackup_tree.selection()
    if not selection:
        messagebox.showinfo("Information", "Please select a layer first")
        return
    
    idx = app_instance.stackup_tree.index(selection[0])
    if idx < len(app_instance.stackup_layers) - 1:
        app_instance.stackup_layers[idx], app_instance.stackup_layers[idx+1] = app_instance.stackup_layers[idx+1], app_instance.stackup_layers[idx]
        update_stackup_tree(app_instance)
        # Reselect the moved item
        items = app_instance.stackup_tree.get_children()
        app_instance.stackup_tree.selection_set(items[idx+1])

# Reset stackup structure
def reset_stackup(app_instance):
    if messagebox.askyesno("Confirmation", "Are you sure you want to reset the stackup? All changes will be lost."):
        generate_default_stackup(app_instance)

# Apply stackup structure
def apply_stackup(app_instance):
    # Here you would add code to apply the stackup to the actual project
    messagebox.showinfo("Success", "Stackup applied successfully")

# Export stackup to JSON file
def export_stackup(app_instance):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Export Stackup"
    )
    
    if file_path:
        try:
            data = [layer.to_dict() for layer in app_instance.stackup_layers]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"Stackup exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

# Import stackup from JSON file
def import_stackup(app_instance):
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Import Stackup"
    )
    
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            app_instance.stackup_layers = [StackupLayer.from_dict(layer_data) for layer_data in data]
            update_stackup_tree(app_instance)
            messagebox.showinfo("Success", f"Stackup imported from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")