from tkinter import ttk

def create_padstack_defs_ui(tab_frame, app_instance):
    # Configure tab_frame to make it resizable
    tab_frame.grid_rowconfigure(3, weight=1)  # Set table area row weight to 1
    tab_frame.grid_columnconfigure(0, weight=1)  # Set column weight to 1

    # File selection area
    title_frame = ttk.Frame(tab_frame, style="PyAEDT.TFrame")
    title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

    ttk.Label(title_frame, style="PyAEDT.TLabel", text="Title").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(title_frame).grid(row=0, column=1, sticky='w', padx=5, pady=5)

    ttk.Label(title_frame, style="PyAEDT.TLabel", text="AEDT Version").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(title_frame).grid(row=1, column=1, sticky='w', padx=5, pady=5)

    ttk.Label(title_frame, style="PyAEDT.TLabel", text="Output Dir").grid(row=2, column=0, sticky='w', padx=5, pady=5)
    output_dir_entry = ttk.Entry(title_frame, width=50)
    output_dir_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
    
    # Configure column weight for title_frame to make Entry expandable
    title_frame.grid_columnconfigure(1, weight=1)