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

from dataclasses import dataclass
import os
import tkinter
from tkinter import ttk

import PIL.Image
import PIL.ImageTk

from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions import EXTENSIONS_PATH
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

EXTENSION_TITLE = "Extension Manager"
AEDT_APPLICATIONS = [
    "Project",
    "HFSS",
    "Maxwell3D",
    "Icepak",
    "Q3D",
    "Maxwell2D",
    "Q2D",
    "HFSS3DLayout",
    "Mechanical",
    "Circuit",
    "EMIT",
    "TwinBuilder",
]
WIDTH = 600
HEIGHT = 250


class ExtensionManager(ExtensionCommon):
    """Extension for move it in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=4,
            toggle_column=1,
        )

        # Tkinter widgets
        self.right_panel = None
        self.programs = None
        self.default_label = None
        self.images = []

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

        self.root.minsize(WIDTH, HEIGHT)

    def add_extension_content(self):
        """Add custom content to the extension UI."""

        # Main container (horizontal layout)
        container = ttk.Frame(self.root, style="PyAEDT.TFrame")
        container.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Left panel (Programs)
        left_panel = ttk.Frame(container, width=250, style="PyAEDT.TFrame")
        left_panel.grid(row=0, column=0, sticky="ns")

        # Right panel (Extensions)
        self.right_panel = ttk.Frame(container, style="PyAEDT.TFrame")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Program list
        self.programs = {
            "Project": ["Custom", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran"],
            "HFSS": ["Custom", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran"],
            "Maxwell": ["Custom", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran", "Import Nastran"],
        }

        for i, name in enumerate(self.programs):
            btn = ttk.Button(left_panel, text=name, command=lambda n=name: self.load_extensions(n),
                             style="PyAEDT.TButton")
            btn.grid(row=i, column=0, sticky="ew", padx=5, pady=2)

        # Placeholder content
        self.default_label = ttk.Label(self.right_panel, text="Select a category",
                                       style="PyAEDT.TLabel",
                                       font=("Arial", 12, "bold"))
        self.default_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

    def load_extensions(self, category: str):
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        canvas = tkinter.Canvas(self.right_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="PyAEDT.TFrame")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        header = ttk.Label(scroll_frame, text=f"{category} Extensions", style="PyAEDT.TLabel",
                           font=("Arial", 12, "bold"))
        header.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 10))

        self.style.configure("PyAEDT.TFrame", relief="raised", borderwidth=1)

        options = self.programs.get(category, [])
        for index, option in enumerate(options):
            row = (index // 3) + 1
            col = index % 3

            card = ttk.Frame(scroll_frame, style="PyAEDT.TFrame", padding=10)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            if option.lower() == "custom":
                icon = ttk.Label(card, text="🧩", style="PyAEDT.TLabel", font=("Segoe UI Emoji", 18))
                icon.pack(pady=(0, 5))
            else:
                try:
                    image_path = EXTENSIONS_PATH / "project" / "images" / "large" / "cloud.png"
                    img = PIL.Image.open(str(image_path)).resize((48, 48), PIL.Image.LANCZOS)
                    photo = PIL.ImageTk.PhotoImage(img)
                    self.images.append(photo)
                    icon = ttk.Label(card, image=photo, background="#ffffff")
                    icon.pack(pady=(0, 5))
                except Exception as e:
                    icon = ttk.Label(card, text="❓", style="PyAEDT.TLabel", font=("Segoe UI Emoji", 18))
                    icon.pack(pady=(0, 5))

            # Texto
            label = ttk.Label(card, text=option, style="PyAEDT.TLabel", anchor="center")
            label.pack()

            # Click handler para toda la tarjeta
            card.bind("<Button-1>", lambda e, opt=option: print(f"Clicked: {opt}"))
            icon.bind("<Button-1>", lambda e, opt=option: print(f"Clicked: {opt}"))
            label.bind("<Button-1>", lambda e, opt=option: print(f"Clicked: {opt}"))

        # Expande columnas
        for col in range(3):
            scroll_frame.grid_columnconfigure(col, weight=1)


if __name__ == "__main__":  # pragma: no cover
    # Open UI
    extension: ExtensionCommon = ExtensionManager(withdraw=False)

    tkinter.mainloop()
