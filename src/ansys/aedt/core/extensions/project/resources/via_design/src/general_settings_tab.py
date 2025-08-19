from tkinter import filedialog, ttk, END
import os

class GeneralSettingsUI:
    """General settings UI manager - single responsibility principle"""
    
    def __init__(self, tab_frame, app_instance):
        self.tab_frame = tab_frame
        self.app = app_instance
        self.widgets = {}
        
        self._setup_layout()
        self._create_widgets()
        self._bind_events()
        self._load_initial_data()
    
    def _setup_layout(self):
        """Configure basic layout - separation of concerns"""
        self.tab_frame.grid_rowconfigure(0, weight=1)
        self.tab_frame.grid_columnconfigure(0, weight=1)
        
        self.main_frame = ttk.Frame(self.tab_frame, style="PyAEDT.TFrame")
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def _create_widgets(self):
        """Create all UI components - clear structure"""
        self._create_title_field()
        self._create_version_field()
        self._create_output_dir_field()
    
    def _create_title_field(self):
        """Create title input field - unified pattern"""
        row = 0
        self.widgets['title'] = self._create_entry_field(
            self.main_frame, row, "Title", 
            update_callback=self._update_title
        )
    
    def _create_version_field(self):
        """Create AEDT version input field - unified pattern"""
        row = 1
        self.widgets['version'] = self._create_entry_field(
            self.main_frame, row, "AEDT Version", 
            update_callback=self._update_version
        )
    
    def _create_output_dir_field(self):
        """Create output directory field with browse button - unified pattern"""
        row = 2
        self.widgets['output_dir'] = self._create_entry_field(
            self.main_frame, row, "Output Dir", 
            update_callback=self._update_output_dir,
            width=50
        )
        
        # Add browse button
        browse_button = ttk.Button(
            self.main_frame, 
            style="PyAEDT.TButton", 
            text="Browse...", 
            command=self._browse_output_dir
        )
        browse_button.grid(row=row, column=2, sticky='w', padx=5, pady=5)
    
    def _create_entry_field(self, parent, row, label_text, update_callback, width=None):
        """Create entry field with label - unified pattern"""
        # Create label
        ttk.Label(
            parent, 
            style="PyAEDT.TLabel", 
            text=label_text
        ).grid(row=row, column=0, sticky='w', padx=5, pady=5)
        
        # Create entry widget
        entry_kwargs = {}
        if width:
            entry_kwargs['width'] = width
            
        entry_widget = ttk.Entry(parent, **entry_kwargs)
        entry_widget.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        return entry_widget
    
    def _bind_events(self):
        """Bind events - clear event management"""
        # Bind title field events
        self.widgets['title'].bind('<KeyRelease>', self._update_title)
        self.widgets['title'].bind('<FocusOut>', self._update_title)
        
        # Bind version field events
        self.widgets['version'].bind('<KeyRelease>', self._update_version)
        self.widgets['version'].bind('<FocusOut>', self._update_version)
        
        # Bind output directory field events
        self.widgets['output_dir'].bind('<KeyRelease>', self._update_output_dir)
        self.widgets['output_dir'].bind('<FocusOut>', self._update_output_dir)
    
    def _load_initial_data(self):
        """Load initial data from config_model - simplified data loading"""
        if not self._has_valid_config():
            return
        
        # Load title
        title_value = getattr(self.app.config_model, 'title', '') or ''
        self._set_widget_value(self.widgets['title'], title_value)
        
        # Load version and output_dir from general config
        if self._has_valid_general_config():
            version_value = getattr(self.app.config_model.general, 'version', '') or ''
            output_dir_value = getattr(self.app.config_model.general, 'output_dir', '') or ''
            
            self._set_widget_value(self.widgets['version'], version_value)
            self._set_widget_value(self.widgets['output_dir'], output_dir_value)
    
    # Unified widget operation methods
    def _set_widget_value(self, widget, value):
        """Set widget value - unified operation"""
        widget.delete(0, END)
        widget.insert(0, value)
    
    def _get_widget_value(self, widget):
        """Get widget value - unified operation"""
        return widget.get()
    
    # Data validation methods - eliminate complex edge case handling
    def _has_valid_config(self):
        """Check if config_model is valid - simple validation"""
        return (hasattr(self.app, 'config_model') and 
                self.app.config_model is not None)
    
    def _has_valid_general_config(self):
        """Check if general config is valid - simple validation"""
        return (self._has_valid_config() and 
                hasattr(self.app.config_model, 'general') and 
                self.app.config_model.general is not None)
    
    # Event handlers - simplified update logic
    def _update_title(self, event=None):
        """Update title in config_model - simplified update"""
        if not self._has_valid_config():
            return
        
        new_value = self._get_widget_value(self.widgets['title'])
        self.app.config_model.title = new_value
    
    def _update_version(self, event=None):
        """Update version in config_model - simplified update"""
        if not self._has_valid_general_config():
            return
        
        new_value = self._get_widget_value(self.widgets['version'])
        self.app.config_model.general.version = new_value
    
    def _update_output_dir(self, event=None, new_path=None):
        """Update output directory in config_model - simplified update"""
        if not self._has_valid_general_config():
            return
        
        if new_path is not None:
            # Direct path update (from browse dialog)
            self.app.config_model.general.output_dir = new_path
        else:
            # Update from widget value
            new_value = self._get_widget_value(self.widgets['output_dir'])
            self.app.config_model.general.output_dir = new_value
    
    def _browse_output_dir(self):
        """Browse for output directory - simplified directory selection"""
        selected_directory = filedialog.askdirectory()
        if not selected_directory:
            return
        
        # Validate directory exists
        if not os.path.isdir(selected_directory):
            return
        
        # Get absolute path and update UI and config
        absolute_path = os.path.abspath(selected_directory)
        self._set_widget_value(self.widgets['output_dir'], absolute_path)
        self._update_output_dir(new_path=absolute_path)
    
    def _refresh_ui_after_config_load(self):
        """Refresh UI after config load - complete data reload"""
        self._load_initial_data()


def create_general_ui(tab_frame, app_instance):
    """Create general settings UI - factory function for backward compatibility"""
    ui = GeneralSettingsUI(tab_frame, app_instance)

    app_instance.refresh_general_ui_after_config_load = ui._refresh_ui_after_config_load
    return ui

