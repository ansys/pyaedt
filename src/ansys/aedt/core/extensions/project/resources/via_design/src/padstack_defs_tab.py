from tkinter import ttk
import tkinter as tk
from tkinter import messagebox, simpledialog
from ansys.aedt.core.extensions.project.resources.via_design.src.data_classes import PadstackDef, SolderBallParameters

HOLE_RANGE_OPTIONS = ['upper_pad_to_lower_pad', 'through', 'begin_on_upper_pad', 'end_on_lower_pad']
SOLDER_BALL_PLACEMENT_OPTIONS = ["above_padstack", "below_padstack"]
SOLDER_BALL_SHAPE = ["cylinder", "spheroid"]


class PadstackDefsUI:
    """Padstack definitions UI manager - single responsibility"""
    
    def __init__(self, tab_frame, app_instance):
        self.tab_frame = tab_frame
        self.app = app_instance
        self.property_widgets = {}
        self.solder_widgets = {}
        self.solder_ball_var = tk.BooleanVar()
        
        self._setup_layout()
        self._create_widgets()
        self._bind_events()
        self._refresh_ui()
    
    def _setup_layout(self):
        """Configure basic layout - separation of concerns"""
        self.tab_frame.grid_rowconfigure(0, weight=1)
        self.tab_frame.grid_columnconfigure(0, weight=1)
        
        self.main_frame = ttk.Frame(self.tab_frame, style="PyAEDT.TFrame")
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=0)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def _create_widgets(self):
        """Create all UI components - clear structure"""
        self._create_left_panel()
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create left panel - padstack type selection"""
        self.left_frame = ttk.LabelFrame(self.main_frame, text="Padstack Types", style="PyAEDT.TLabelframe")
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=0)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Listbox
        self.padstack_listbox = tk.Listbox(
            self.left_frame, 
            selectmode=tk.SINGLE, 
            height=10, 
            width=15,
            exportselection=False
        )
        self.padstack_listbox.grid(row=0, column=0, sticky='nsew', padx=5, pady=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(self.left_frame, style="PyAEDT.TFrame")
        button_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        self.add_button = ttk.Button(button_frame, text="Add", style="PyAEDT.TButton")
        self.add_button.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        
        self.delete_button = ttk.Button(button_frame, text="Delete", style="PyAEDT.TButton")
        self.delete_button.grid(row=0, column=1, sticky='ew', padx=(2, 0))
    
    def _create_right_panel(self):
        """Create right panel - property editing"""
        self.right_frame = ttk.LabelFrame(self.main_frame, text="Padstack Properties", style="PyAEDT.TLabelframe")
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=0)
        self.right_frame.grid_columnconfigure(1, weight=1)
        
        self._create_property_fields()
        self._create_solder_section()
        self._create_save_button()
    
    def _create_property_fields(self):
        """Create property fields - unified creation pattern"""
        row = 0
        
        # Read-only fields
        self.property_widgets['name'] = self._create_readonly_field(self.right_frame, row, "Name")
        row += 1
        self.property_widgets['shape'] = self._create_readonly_field(self.right_frame, row, "Shape")
        row += 1
        
        # Editable fields
        self.property_widgets['pad_diameter'] = self._create_entry_field(self.right_frame, row, "Pad Diameter")
        row += 1
        self.property_widgets['hole_diameter'] = self._create_entry_field(self.right_frame, row, "Hole Diameter")
        row += 1
        self.property_widgets['hole_range'] = self._create_combo_field(self.right_frame, row, "Hole Range", HOLE_RANGE_OPTIONS)
        
        self.current_row = row + 1
    
    def _create_solder_section(self):
        """Create solder ball parameters section"""
        # Checkbox
        checkbox_frame = ttk.Frame(self.right_frame, style="PyAEDT.TFrame")
        checkbox_frame.grid(row=self.current_row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        solder_checkbox = ttk.Checkbutton(
            checkbox_frame, 
            text="Enable Solder Ball", 
            variable=self.solder_ball_var,
            command=self._toggle_solder_parameters,
            style="PyAEDT.TCheckbutton"
        )
        solder_checkbox.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.current_row += 1
        
        # Solder ball parameters frame
        self.solder_frame = ttk.LabelFrame(self.right_frame, text="Solder Ball Parameters", style="PyAEDT.TLabelframe")
        self.solder_frame.grid(row=self.current_row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        self.solder_frame.grid_columnconfigure(1, weight=1)
        self.solder_frame.grid_remove()
        
        # Solder ball parameter fields
        solder_row = 0
        self.solder_widgets['shape'] = self._create_combo_field(self.solder_frame, solder_row, "Shape", SOLDER_BALL_SHAPE)
        solder_row += 1
        self.solder_widgets['diameter'] = self._create_entry_field(self.solder_frame, solder_row, "Diameter")
        solder_row += 1
        self.solder_widgets['mid_diameter'] = self._create_entry_field(self.solder_frame, solder_row, "Mid Diameter")
        solder_row += 1
        self.solder_widgets['placement'] = self._create_combo_field(self.solder_frame, solder_row, "Placement", SOLDER_BALL_PLACEMENT_OPTIONS)
        solder_row += 1
        self.solder_widgets['material'] = self._create_entry_field(self.solder_frame, solder_row, "Material")
        
        self.current_row += 1
    
    def _create_save_button(self):
        """Create save button"""
        save_frame = ttk.Frame(self.right_frame, style="PyAEDT.TFrame")
        save_frame.grid(row=self.current_row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        self.save_button = ttk.Button(
            save_frame, 
            text="Save Changes", 
            command=self._save_changes,
            style="PyAEDT.TButton"
        )
        self.save_button.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    
    # Unified widget creation methods - eliminate code duplication
    def _create_readonly_field(self, parent, row, label_text):
        """Create read-only field - unified pattern"""
        ttk.Label(parent, text=f"{label_text}:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        widget = ttk.Label(parent, text="", style="PyAEDT.TLabel")
        widget.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        return widget
    
    def _create_entry_field(self, parent, row, label_text):
        """Create entry field - unified pattern"""
        ttk.Label(parent, text=f"{label_text}:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        widget = ttk.Entry(parent, width=20)
        widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        return widget
    
    def _create_combo_field(self, parent, row, label_text, options):
        """Create combobox field - unified pattern"""
        ttk.Label(parent, text=f"{label_text}:", style="PyAEDT.TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        widget = ttk.Combobox(parent, values=options, state="readonly", width=20)
        widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        if options:
            widget.set(options[0])
        return widget
    
    def _bind_events(self):
        """Bind events - clear event management"""
        self.add_button.configure(command=self._add_padstack)
        self.delete_button.configure(command=self._delete_padstack)
        self.padstack_listbox.bind('<<ListboxSelect>>', self._on_selection_change)
    
    # Data operation methods - simple and direct
    def _get_padstack_by_name(self, name):
        """Get padstack by name - simple and direct"""
        for item in self.app.config_model.padstack_defs:
            if item.name == name:
                return item
        return None
    
    def _get_padstack_names(self):
        """Get all padstack names"""
        return [item.name for item in self.app.config_model.padstack_defs]
    
    def _get_selected_padstack(self):
        """Get currently selected padstack - unified selection logic"""
        selection = self.padstack_listbox.curselection()
        if not selection:
            return None
        return self.padstack_listbox.get(selection[0])
    
    # UI update methods - eliminate complex edge case handling
    def _refresh_listbox(self):
        """Refresh listbox - simple and direct"""
        self.padstack_listbox.delete(0, tk.END)
        for name in self._get_padstack_names():
            self.padstack_listbox.insert(tk.END, name)
    
    def _refresh_ui(self):
        """Refresh entire UI - simplified state management"""
        current_selection = self._get_selected_padstack()
        self._refresh_listbox()
        self._restore_selection(current_selection)
        self._update_properties()
    
    def _restore_selection(self, target_name):
        """Restore selection - eliminate complex edge cases"""
        if not target_name:
            self._select_first_item()
            return
        
        names = self._get_padstack_names()
        if target_name in names:
            index = names.index(target_name)
            self._select_item(index)
        else:
            self._select_first_item()
    
    def _select_item(self, index):
        """Select specified item - unified selection operation"""
        if 0 <= index < self.padstack_listbox.size():
            self.padstack_listbox.selection_set(index)
            self.padstack_listbox.see(index)
    
    def _select_first_item(self):
        """Select first item - simple default behavior"""
        if self.padstack_listbox.size() > 0:
            self._select_item(0)
    
    # Widget operation methods - unified operation patterns
    def _clear_widget(self, widget, widget_type):
        """Clear widget - unified clear operation"""
        if widget_type == 'entry':
            widget.delete(0, tk.END)
        elif widget_type == 'combo':
            widget.set('')
        elif widget_type == 'label':
            widget.configure(text='')
    
    def _set_widget_value(self, widget, value, widget_type):
        """Set widget value - unified set operation"""
        if widget_type == 'entry':
            widget.delete(0, tk.END)
            widget.insert(0, value)
        elif widget_type == 'combo':
            widget.set(value)
        elif widget_type == 'label':
            widget.configure(text=value)
    
    # Event handling methods
    def _on_selection_change(self, event=None):
        """Handle selection change"""
        self._update_properties()
    
    def _update_properties(self):
        """Update property display - simplified update logic"""
        selected_name = self._get_selected_padstack()
        if not selected_name:
            self._clear_all_properties()
            return
        
        data = self._get_padstack_by_name(selected_name)
        if not data:
            return
        
        # Update basic properties
        self._set_widget_value(self.property_widgets['name'], data.name, 'label')
        self._set_widget_value(self.property_widgets['shape'], data.shape, 'label')
        self._set_widget_value(self.property_widgets['pad_diameter'], data.pad_diameter, 'entry')
        self._set_widget_value(self.property_widgets['hole_diameter'], data.hole_diameter, 'entry')
        self._set_widget_value(self.property_widgets['hole_range'], data.hole_range, 'combo')
        
        # Update solder ball parameters
        self.solder_ball_var.set(bool(data.solder_ball_parameters))
        self._toggle_solder_parameters()
    
    def _clear_all_properties(self):
        """Clear all properties - unified clear operation"""
        for key, widget in self.property_widgets.items():
            widget_type = 'label' if key in ['name', 'shape'] else ('combo' if key == 'hole_range' else 'entry')
            self._clear_widget(widget, widget_type)
        
        for key, widget in self.solder_widgets.items():
            widget_type = 'combo' if key in ['shape', 'placement'] else 'entry'
            self._clear_widget(widget, widget_type)
        
        self.solder_ball_var.set(False)
        self.solder_frame.grid_remove()
    
    def _toggle_solder_parameters(self):
        """Toggle solder parameter display - simplified toggle logic"""
        if self.solder_ball_var.get():
            self.solder_frame.grid()
            self._load_solder_data()
        else:
            self.solder_frame.grid_remove()
            self._clear_solder_widgets()
    
    def _load_solder_data(self):
        """Load solder ball data"""
        selected_name = self._get_selected_padstack()
        if not selected_name:
            return
        
        data = self._get_padstack_by_name(selected_name)
        if not data:
            return
        
        if not data.solder_ball_parameters:
            data.solder_ball_parameters = self._create_default_solder_params()
        
        solder_data = data.solder_ball_parameters
        self._set_widget_value(self.solder_widgets['shape'], solder_data.shape, 'combo')
        self._set_widget_value(self.solder_widgets['diameter'], solder_data.diameter, 'entry')
        self._set_widget_value(self.solder_widgets['mid_diameter'], solder_data.mid_diameter, 'entry')
        self._set_widget_value(self.solder_widgets['placement'], solder_data.placement, 'combo')
        self._set_widget_value(self.solder_widgets['material'], solder_data.material, 'entry')
    
    def _clear_solder_widgets(self):
        """Clear solder ball widgets"""
        for key, widget in self.solder_widgets.items():
            widget_type = 'combo' if key in ['shape', 'placement'] else 'entry'
            self._clear_widget(widget, widget_type)
    
    def _create_default_solder_params(self):
        """Create default solder ball parameters"""
        return SolderBallParameters(
            shape=SOLDER_BALL_SHAPE[0],
            diameter="0.4mm",
            mid_diameter="0.4mm",
            placement=SOLDER_BALL_PLACEMENT_OPTIONS[0],
            material="solder"
        )
    
    # Business operation methods
    def _add_padstack(self):
        """Add new padstack type"""
        new_name = simpledialog.askstring("Add Padstack Type", "Enter new padstack type name:")
        if not new_name or not new_name.strip():
            return
        
        new_name = new_name.strip().upper()
        
        if self._get_padstack_by_name(new_name):
            messagebox.showerror("Error", f"Padstack type '{new_name}' already exists!")
            return
        
        new_padstack = PadstackDef(
            name=new_name,
            shape="circle",
            pad_diameter="0.25mm",
            hole_diameter="0.1mm",
            hole_range=HOLE_RANGE_OPTIONS[0]
        )
        
        self.app.config_model.padstack_defs.append(new_padstack)
        self._refresh_ui()
        
        # Select newly created item
        names = self._get_padstack_names()
        if new_name in names:
            index = names.index(new_name)
            self._select_item(index)
        
        messagebox.showinfo("Success", f"Padstack type '{new_name}' created successfully!")
    
    def _delete_padstack(self):
        """Delete selected padstack type"""
        selected_name = self._get_selected_padstack()
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a padstack type to delete!")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete padstack type '{selected_name}'?"):
            return
        
        padstack_item = self._get_padstack_by_name(selected_name)
        if padstack_item:
            self.app.config_model.padstack_defs.remove(padstack_item)
        
        self._refresh_ui()
        messagebox.showinfo("Success", f"Padstack type '{selected_name}' deleted successfully!")
    
    def _save_changes(self):
        """Save changes - simplified save logic"""
        selected_name = self._get_selected_padstack()
        if not selected_name:
            messagebox.showwarning("Warning", "Please select a padstack type to save!")
            return
        
        data = self._get_padstack_by_name(selected_name)
        if not data:
            messagebox.showerror("Error", "Selected padstack type not found!")
            return
        
        try:
            self._update_padstack_data(data)
            messagebox.showinfo("Success", "Changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
    
    def _update_padstack_data(self, data):
        """Update padstack data"""
        # Update basic properties
        data.pad_diameter = self.property_widgets['pad_diameter'].get()
        data.hole_diameter = self.property_widgets['hole_diameter'].get()
        data.hole_range = self.property_widgets['hole_range'].get()
        
        # Update solder ball parameters
        if self.solder_ball_var.get():
            if not data.solder_ball_parameters:
                data.solder_ball_parameters = self._create_default_solder_params()
            
            solder_data = data.solder_ball_parameters
            solder_data.shape = self.solder_widgets['shape'].get()
            solder_data.diameter = self.solder_widgets['diameter'].get()
            solder_data.mid_diameter = self.solder_widgets['mid_diameter'].get()
            solder_data.placement = self.solder_widgets['placement'].get()
            solder_data.material = self.solder_widgets['material'].get()
        else:
            data.solder_ball_parameters = None

    def _refresh_ui_after_config_load(self):
        """Refresh UI after config load - complete data reload without selection dependency"""
        # Clear all existing UI state
        self._clear_all_properties()
        
        # Rebuild listbox from new config_model data
        self._rebuild_listbox_from_config()
        
        # Select first item if available, otherwise clear properties
        self._select_first_available_item()
        
        # Update properties for first available item (not dependent on selection state)
        self._update_properties_after_config_load()
    
    def _update_properties_after_config_load(self):
        """Update properties after config load - independent of selection state"""
        # Get first available padstack directly from config_model
        first_padstack = self._get_first_available_padstack()
        if not first_padstack:
            # No padstack data available, keep properties cleared
            return
        
        # Update properties directly from data object
        self._populate_properties_from_data(first_padstack)
    
    def _get_first_available_padstack(self):
        """Get first available padstack from config_model - no UI dependency"""
        if not (hasattr(self.app, 'config_model') and 
                hasattr(self.app.config_model, 'padstack_defs')):
            return None
        
        padstack_defs = self.app.config_model.padstack_defs
        if padstack_defs and len(padstack_defs) > 0:
            return padstack_defs[0]
        return None
    
    def _populate_properties_from_data(self, padstack_data):
        """Populate properties directly from data object - pure data operation"""
        if not padstack_data:
            return
        
        # Update basic properties directly from data
        self._set_widget_value(self.property_widgets['name'], padstack_data.name, 'label')
        self._set_widget_value(self.property_widgets['shape'], padstack_data.shape, 'label')
        self._set_widget_value(self.property_widgets['pad_diameter'], padstack_data.pad_diameter, 'entry')
        self._set_widget_value(self.property_widgets['hole_diameter'], padstack_data.hole_diameter, 'entry')
        self._set_widget_value(self.property_widgets['hole_range'], padstack_data.hole_range, 'combo')
        
        # Update solder ball parameters directly from data
        has_solder_ball = bool(padstack_data.solder_ball_parameters)
        self.solder_ball_var.set(has_solder_ball)
        
        if has_solder_ball:
            self._populate_solder_ball_properties(padstack_data.solder_ball_parameters)
            if hasattr(self, 'solder_frame'):
                self.solder_frame.grid()
        else:
            if hasattr(self, 'solder_frame'):
                self.solder_frame.grid_remove()
    
    def _populate_solder_ball_properties(self, solder_data):
        """Populate solder ball properties from data - direct data mapping"""
        if not solder_data:
            return
        
        # Populate solder ball widgets directly from data
        self._set_widget_value(self.solder_widgets['shape'], solder_data.shape, 'combo')
        self._set_widget_value(self.solder_widgets['diameter'], solder_data.diameter, 'entry')
        self._set_widget_value(self.solder_widgets['mid_diameter'], solder_data.mid_diameter, 'entry')
        self._set_widget_value(self.solder_widgets['placement'], solder_data.placement, 'combo')
        self._set_widget_value(self.solder_widgets['material'], solder_data.material, 'entry')
    
    def _rebuild_listbox_from_config(self):
        """Rebuild listbox completely from config_model - no dependency on current state"""
        # Clear existing listbox content
        self.padstack_listbox.delete(0, tk.END)
        
        # Validate config_model exists and has padstack_defs
        if not (hasattr(self.app, 'config_model') and 
                hasattr(self.app.config_model, 'padstack_defs')):
            return
        
        # Populate with fresh data from new config_model
        padstack_defs = self.app.config_model.padstack_defs
        if padstack_defs:
            for padstack_def in padstack_defs:
                self.padstack_listbox.insert(tk.END, padstack_def.name)
    
    def _select_first_available_item(self):
        """Select first item if listbox has content - safe selection without assumptions"""
        if self.padstack_listbox.size() > 0:
            self.padstack_listbox.selection_set(0)
            self.padstack_listbox.see(0)
        # If no items, properties will be cleared by _update_properties


def create_padstack_defs_ui(tab_frame, app_instance):
    """Factory function - maintain backward compatibility"""
    ui = PadstackDefsUI(tab_frame, app_instance)
    # Maintain original global refresh interface
    app_instance.refresh_padstack_ui_after_config_load = ui._refresh_ui_after_config_load
    return ui