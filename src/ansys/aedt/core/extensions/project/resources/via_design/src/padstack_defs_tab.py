from tkinter import ttk
import tkinter as tk

def create_padstack_defs_ui(tab_frame, app_instance):
    # Configure tab_frame to make it resizable
    tab_frame.grid_rowconfigure(0, weight=1)  # Set main content area row weight to 1
    tab_frame.grid_columnconfigure(0, weight=1)  # Set column weight to 1

    # Main content frame with left and right panels
    main_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=0)  # Fixed width for left panel
    main_frame.grid_columnconfigure(1, weight=1)  # Expandable right panel

    # Left panel - Padstack type selection
    left_frame = ttk.LabelFrame(main_frame, text="Padstack Types", style="PyAEDT.TLabelframe")
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=0)
    left_frame.grid_rowconfigure(0, weight=1)  # Listbox takes most space
    left_frame.grid_rowconfigure(1, weight=0)  # Button frame fixed height
    left_frame.grid_columnconfigure(0, weight=1)

    # Listbox for padstack types
    padstack_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=10, width=15)
    padstack_listbox.grid(row=0, column=0, sticky='nsew', padx=5, pady=(5, 0))
    
    # Button frame for add/delete operations
    button_frame = ttk.Frame(left_frame, style="PyAEDT.TFrame")
    button_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    
    # Add and Delete buttons
    add_button = ttk.Button(button_frame, text="Add", style="PyAEDT.TButton")
    add_button.grid(row=0, column=0, sticky='ew', padx=(0, 2))
    
    delete_button = ttk.Button(button_frame, text="Delete", style="PyAEDT.TButton")
    delete_button.grid(row=0, column=1, sticky='ew', padx=(2, 0))

    # Right panel - Padstack properties
    right_frame = ttk.LabelFrame(main_frame, text="Padstack Properties", style="PyAEDT.TLabelframe")
    right_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=0)
    right_frame.grid_columnconfigure(1, weight=1)

    # Padstack data
    padstack_data = [
        {
            "name": "CORE_VIA",
            "shape": "Circle",
            "pad_diameter": "0.25mm",
            "hole_diameter": "0.1mm",
            "hole_range": "From upper to lower pad"
        },
        {
            "name": "MICRO_VIA",
            "shape": "Circle",
            "pad_diameter": "0.1mm",
            "hole_diameter": "0.05mm",
            "hole_range": "From upper to lower pad"
        },
        {
            "name": "BGA",
            "shape": "Circle",
            "pad_diameter": "0.5mm",
            "hole_diameter": "0.4mm",
            "hole_range": "From upper to lower pad",
            "solder_ball_parameters": {
                "shape": "Spheroid",
                "diameter": "0.4mm",
                "mid_diameter": "0.5mm",
                "placement": "Above padstack",
                "material": "solder"
            }
        }
    ]

    # Helper function to find padstack data by name
    def find_padstack_by_name(name):
        """Find padstack data by name in the list"""
        for item in padstack_data:
            if item['name'] == name:
                return item
        return None
    
    def get_padstack_names():
        """Get list of all padstack names"""
        return [item['name'] for item in padstack_data]
    
    # Add padstack types to listbox
    for ptype in get_padstack_names():
        padstack_listbox.insert(tk.END, ptype)
    
    # Property display widgets
    property_widgets = {}
    
    def create_property_row(parent, row, label_text, value="", readonly=False, options=None):
        ttk.Label(parent, text=label_text + ":", style="PyAEDT.TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        if readonly:
            # Create a label for readonly fields
            widget = ttk.Label(parent, text=value, style="PyAEDT.TLabel", relief="sunken", background="white")
            widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        elif options:
            # Create a combobox for dropdown fields
            widget = ttk.Combobox(parent, values=options, state="readonly", width=20)
            widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
            if value in options:
                widget.set(value)
            elif options:
                widget.set(options[0])  # Set default to first option
        else:
            # Create an entry for editable fields
            widget = ttk.Entry(parent, width=20)
            widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
            widget.insert(0, value)
        return widget

    # Create property input fields
    row = 0
    # Create Name field as pure text display
    ttk.Label(right_frame, text="Name:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    property_widgets['name'] = ttk.Label(right_frame, text="", style="PyAEDT.TLabel")
    property_widgets['name'].grid(row=row, column=1, sticky='w', padx=5, pady=2)
    row += 1
    shape_options = ["Circle", "Square", "Rectangle"]
    property_widgets['shape'] = create_property_row(right_frame, row, "Shape", options=shape_options)
    row += 1
    property_widgets['pad_diameter'] = create_property_row(right_frame, row, "Pad Diameter")
    row += 1
    property_widgets['hole_diameter'] = create_property_row(right_frame, row, "Hole Diameter")
    row += 1
    hole_range_options = ["Through all layout layers", "Begin at upper pad", "End at lower pad", "From upper to lower pad"]
    property_widgets['hole_range'] = create_property_row(right_frame, row, "Hole Range", options=hole_range_options)
    row += 1

    # Solder ball parameters checkbox
    solder_checkbox_frame = ttk.Frame(right_frame, style="PyAEDT.TFrame")
    solder_checkbox_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    
    solder_ball_var = tk.BooleanVar()
    solder_checkbox = ttk.Checkbutton(
        solder_checkbox_frame, 
        text="Enable Solder Ball", 
        variable=solder_ball_var,
        style="PyAEDT.TCheckbutton"
    )
    solder_checkbox.grid(row=0, column=0, sticky='w', padx=5, pady=2)
    row += 1

    # Solder ball parameters section (initially hidden)
    solder_frame = ttk.LabelFrame(right_frame, text="Solder Ball Parameters", style="PyAEDT.TLabelframe")
    solder_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
    solder_frame.grid_columnconfigure(1, weight=1)
    solder_frame.grid_remove()  # Initially hide the solder frame
    
    solder_widgets = {}
    solder_row = 0
    solder_shape_options = ["Cylinder", "Spheroid"]
    solder_widgets['shape'] = create_property_row(solder_frame, solder_row, "Shape", options=solder_shape_options)
    solder_row += 1
    solder_widgets['diameter'] = create_property_row(solder_frame, solder_row, "Diameter")
    solder_row += 1
    solder_widgets['mid_diameter'] = create_property_row(solder_frame, solder_row, "Mid Diameter")
    solder_row += 1
    placement_options = ["Above padstack", "Below padstack"]
    solder_widgets['placement'] = create_property_row(solder_frame, solder_row, "Placement", options=placement_options)
    solder_row += 1
    solder_widgets['material'] = create_property_row(solder_frame, solder_row, "Material")
    
    # Save button at the bottom
    save_button_frame = ttk.Frame(right_frame, style="PyAEDT.TFrame")
    save_button_frame.grid(row=row+1, column=0, columnspan=2, sticky='ew', padx=5, pady=15)
    save_button_frame.grid_columnconfigure(0, weight=1)
    
    save_button = ttk.Button(save_button_frame, text="Save Changes", style="PyAEDT.TButton")
    save_button.grid(row=0, column=0, sticky='ew')

    def toggle_solder_parameters():
        """Toggle solder ball parameters visibility based on checkbox"""
        if solder_ball_var.get():
            solder_frame.grid()
            # Load current solder ball data if available
            selection = padstack_listbox.curselection()
            if selection:
                selected_type = padstack_listbox.get(selection[0])
                data = find_padstack_by_name(selected_type)
                if data and 'solder_ball_parameters' in data:
                    solder_data = data['solder_ball_parameters']
                    # Set solder shape value for combobox
                    solder_widgets['shape'].set(solder_data['shape'])
                    
                    solder_widgets['diameter'].delete(0, tk.END)
                    solder_widgets['diameter'].insert(0, solder_data['diameter'])
                    
                    solder_widgets['mid_diameter'].delete(0, tk.END)
                    solder_widgets['mid_diameter'].insert(0, solder_data['mid_diameter'])
                    
                    # Set placement value for combobox
                    solder_widgets['placement'].set(solder_data['placement'])
                    
                    solder_widgets['material'].delete(0, tk.END)
                    solder_widgets['material'].insert(0, solder_data['material'])
        else:
            solder_frame.grid_remove()
            # Clear solder ball parameters
            for key, widget in solder_widgets.items():
                if key in ['placement', 'shape']:
                    widget.set('')  # Clear combobox
                else:
                    widget.delete(0, tk.END)  # Clear entry
    
    # Bind checkbox command
    solder_checkbox.configure(command=toggle_solder_parameters)
    
    def save_changes():
        """Save changes to the selected padstack type"""
        from tkinter import messagebox
        
        selection = padstack_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a padstack type to save!")
            return
        
        selected_type = padstack_listbox.get(selection[0])
        data = find_padstack_by_name(selected_type)
        if not data:
            messagebox.showerror("Error", "Selected padstack type not found!")
            return
        
        try:
            # Update basic properties from widgets
            data['shape'] = property_widgets['shape'].get()
            data['pad_diameter'] = property_widgets['pad_diameter'].get()
            data['hole_diameter'] = property_widgets['hole_diameter'].get()
            data['hole_range'] = property_widgets['hole_range'].get()
            
            # Update solder ball parameters if enabled
            if solder_ball_var.get():
                if 'solder_ball_parameters' not in data:
                    data['solder_ball_parameters'] = {}
                
                data['solder_ball_parameters']['shape'] = solder_widgets['shape'].get()
                data['solder_ball_parameters']['diameter'] = solder_widgets['diameter'].get()
                data['solder_ball_parameters']['mid_diameter'] = solder_widgets['mid_diameter'].get()
                data['solder_ball_parameters']['placement'] = solder_widgets['placement'].get()
                data['solder_ball_parameters']['material'] = solder_widgets['material'].get()
            else:
                # Remove solder ball parameters if disabled
                if 'solder_ball_parameters' in data:
                    del data['solder_ball_parameters']
            
            # Print debug information to verify data is saved
            print(f"DEBUG: Saved data for {selected_type}:")
            print(f"  Shape: {data['shape']}")
            print(f"  Pad Diameter: {data['pad_diameter']}")
            print(f"  Hole Diameter: {data['hole_diameter']}")
            print(f"  Hole Range: {data['hole_range']}")
            if 'solder_ball_parameters' in data:
                print(f"  Solder Ball Parameters: {data['solder_ball_parameters']}")
            
            messagebox.showinfo("Success", f"Changes to '{selected_type}' saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

    def update_properties(event=None):
        """Update property fields based on selected padstack type"""
        selection = padstack_listbox.curselection()
        if selection:
            # Get the selected type name directly from listbox instead of using index
            selected_type = padstack_listbox.get(selection[0])
            data = find_padstack_by_name(selected_type)
            if not data:
                return
            
            # Print debug information to verify data is loaded
            print(f"DEBUG: Loading data for {selected_type}:")
            print(f"  Shape: {data['shape']}")
            print(f"  Pad Diameter: {data['pad_diameter']}")
            print(f"  Hole Diameter: {data['hole_diameter']}")
            print(f"  Hole Range: {data['hole_range']}")
            if 'solder_ball_parameters' in data:
                print(f"  Solder Ball Parameters: {data['solder_ball_parameters']}")
            
            # Update basic properties
            # Update name (readonly label)
            property_widgets['name'].configure(text=data['name'])
            
            # Set shape value for combobox
            property_widgets['shape'].set(data['shape'])
            
            property_widgets['pad_diameter'].delete(0, tk.END)
            property_widgets['pad_diameter'].insert(0, data['pad_diameter'])
            
            property_widgets['hole_diameter'].delete(0, tk.END)
            property_widgets['hole_diameter'].insert(0, data['hole_diameter'])
            
            # Set hole_range value for combobox
            property_widgets['hole_range'].set(data['hole_range'])
            
            # Update checkbox state based on whether solder ball parameters exist
            if 'solder_ball_parameters' in data:
                solder_ball_var.set(True)
            else:
                solder_ball_var.set(False)
            
            # Update solder parameters visibility
            toggle_solder_parameters()

    def add_padstack_type():
        """Add a new padstack type"""
        from tkinter import simpledialog, messagebox
        
        # Get new padstack name from user
        new_name = simpledialog.askstring("Add Padstack Type", "Enter new padstack type name:")
        if new_name and new_name.strip():
            new_name = new_name.strip().upper()
            
            # Check if name already exists
            if find_padstack_by_name(new_name):
                messagebox.showerror("Error", f"Padstack type '{new_name}' already exists!")
                return
            
            # Add new padstack type with default values
            new_padstack = {
                "name": new_name,
                "shape": "Circle",
                "pad_diameter": "0.25mm",
                "hole_diameter": "0.1mm",
                "hole_range": "From upper to lower pad"
            }
            padstack_data.append(new_padstack)
            
            # Add to listbox
            padstack_listbox.insert(tk.END, new_name)
            
            # Select the new item
            padstack_listbox.selection_clear(0, tk.END)
            padstack_listbox.selection_set(tk.END)
            padstack_listbox.see(tk.END)
            
            # Update properties display
            update_properties()
            
            messagebox.showinfo("Success", f"Padstack type '{new_name}' created successfully!")
    
    def delete_padstack_type():
        """Delete selected padstack type"""
        from tkinter import messagebox
        
        selection = padstack_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a padstack type to delete!")
            return
        
        selected_index = selection[0]
        selected_type = padstack_listbox.get(selected_index)
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete padstack type '{selected_type}'?")
        if result:
            # Remove from data
            padstack_item = find_padstack_by_name(selected_type)
            if padstack_item:
                padstack_data.remove(padstack_item)
            
            # Remove from listbox
            padstack_listbox.delete(selected_index)
            
            # Select next item or clear if no items left
            if padstack_listbox.size() > 0:
                if selected_index < padstack_listbox.size():
                    padstack_listbox.selection_set(selected_index)
                else:
                    padstack_listbox.selection_set(padstack_listbox.size() - 1)
                update_properties()
            else:
                # Clear all property fields if no items left
                property_widgets['name'].configure(text="")
                for key, widget in property_widgets.items():
                    if key != 'name':  # Skip name field as it's readonly
                        if key in ['shape', 'hole_range']:
                            widget.set('')  # Clear combobox
                        else:
                            widget.delete(0, tk.END)  # Clear entry
                for key, widget in solder_widgets.items():
                    if key in ['placement', 'shape']:
                        widget.set('')  # Clear combobox
                    else:
                        widget.delete(0, tk.END)  # Clear entry
                solder_ball_var.set(False)
                solder_frame.grid_remove()
            
            messagebox.showinfo("Success", f"Padstack type '{selected_type}' deleted successfully!")
    
    # Bind button commands
    add_button.configure(command=add_padstack_type)
    delete_button.configure(command=delete_padstack_type)
    save_button.configure(command=save_changes)
    
    # Bind selection event
    padstack_listbox.bind('<<ListboxSelect>>', update_properties)
    
    # Select first item by default
    if padstack_listbox.size() > 0:
        padstack_listbox.selection_set(0)
        update_properties()