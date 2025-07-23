from dataclasses import dataclass

from numpy import version

from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import SUN
from pathlib import Path
from tkinter import filedialog, ttk, END
from functools import partial
import PIL

def create_general_ui(tab_frame, app_instance, EXTENSION_NB_COLUMN):

    title_frame = ttk.LabelFrame(tab_frame)
    title_frame.pack(fill='x', padx=5, pady=5)
    title_frame.columnconfigure(1, weight=1)

    title_label = ttk.Label(title_frame, text="Title:")
    title_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
    title_entry = ttk.Entry(title_frame, width=20)
    title_entry.insert(0, "PCB RF Via")
    title_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)

    version_label = ttk.Label(title_frame, text="AEDT Version:")
    version_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
    version_entry = ttk.Entry(title_frame, width=20)
    version_entry.insert(0, "2025R2")
    version_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)

    # 输出目录选择 - 替换原有版本输入框
    output_dir_label = ttk.Label(title_frame, text="Output Dir:")
    output_dir_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)

    output_dir_entry = ttk.Entry(title_frame, width=10)
    output_dir_entry.grid(row=2, column=1, sticky='w', padx=2, pady=2)

    def browse_output_dir():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            output_dir_entry.delete(0, END)
            output_dir_entry.insert(0, folder_selected)
    
    browse_btn = ttk.Button(title_frame, text="Browse...", command=browse_output_dir)
    browse_btn.grid(row=2, column=2, sticky='w', padx=2, pady=2)

    outline_extent_label = ttk.Label(title_frame, text="Outline Extent:")
    outline_extent_label.grid(row=3, column=0, sticky='w', padx=5, pady=2)
    outline_extent_entry = ttk.Entry(title_frame, width=20)
    outline_extent_entry.insert(0, "10mm")
    outline_extent_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)

    pitch_label = ttk.Label(title_frame, text="Pitch:")
    pitch_label.grid(row=4, column=0, sticky='w', padx=5, pady=2)
    pitch_entry = ttk.Entry(title_frame, width=20)
    pitch_entry.insert(0, "10mm")
    pitch_entry.grid(row=3, column=1, sticky='w', padx=5, pady=2)


