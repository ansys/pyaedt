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
from pathlib import Path
import sys
import subprocess
import tkinter
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
import webbrowser

import PIL.Image
import PIL.ImageTk

from ansys.aedt.core.extensions import EXTENSIONS_PATH
from ansys.aedt.core.extensions.customize_automation_tab import available_toolkits
from ansys.aedt.core.extensions.customize_automation_tab import add_script_to_menu
from ansys.aedt.core.extensions.customize_automation_tab import remove_script_from_menu
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

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
WIDTH = 850
HEIGHT = 550


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

        self.python_interpreter = Path(sys.executable)
        self.toolkits = None
        self.add_to_aedt_var = tkinter.BooleanVar(value=True)

        # Tkinter widgets
        self.right_panel = None
        self.programs = None
        self.default_label = None
        self.images = []

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

        self.root.minsize(WIDTH, HEIGHT)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")

    def add_extension_content(self):
        """Add custom content to the extension."""

        # Main container (horizontal layout)
        container = ttk.Frame(self.root, style="PyAEDT.TFrame")
        container.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Left panel (Programs)
        left_panel = ttk.Frame(container, width=250, style="PyAEDT.TFrame")
        left_panel.grid(row=0, column=0, sticky="ns")

        # Right panel (Extensions)
        self.right_panel = ttk.Frame(container, style="PyAEDT.TFrame", relief="solid")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Load programs and extensions dynamically
        self.toolkits = available_toolkits()
        self.programs = AEDT_APPLICATIONS

        for i, name in enumerate(AEDT_APPLICATIONS):
            btn = ttk.Button(left_panel, text=name, command=lambda n=name: self.load_extensions(n),
                             style="PyAEDT.TButton")
            btn.grid(row=i, column=0, sticky="ew", padx=5, pady=2)

        # Placeholder content
        self.default_label = ttk.Label(self.right_panel, text="Select application",
                                       style="PyAEDT.TLabel",
                                       font=("Arial", 12, "bold"))
        self.default_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

    def load_extensions(self, category: str):
        """Load application extensions."""
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        canvas = tkinter.Canvas(self.right_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical",
                                  command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="PyAEDT.TFrame", relief="solid")

        # Apply theme to canvas
        self.apply_canvas_theme(canvas)

        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)

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

        # Checkbox to add to AEDT
        add_checkbox = ttk.Checkbutton(
            scroll_frame,
            text="Add to AEDT",
            variable=self.add_to_aedt_var,
            style="PyAEDT.TCheckbutton"
        )
        add_checkbox.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10), columnspan=3)

        extensions = list(self.toolkits.get(category, {}).keys())
        options = {}
        if extensions:
            options["Custom"] = "Custom"
            for extension_name in extensions:
                options[extension_name] = self.toolkits[category][extension_name].get("name", extension_name)

        else:
            options["Custom"] = "Custom"
        for index, option in enumerate(options):
            row = (index // 3) + 2
            col = index % 3

            card = ttk.Frame(scroll_frame, style="PyAEDT.TFrame", relief="solid")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            if option.lower() == "custom":
                icon = ttk.Label(card, text="🧩", style="PyAEDT.TLabel",
                                 font=("Segoe UI Emoji", 25))
                icon.pack(padx=10, pady=10)
            else:
                try:
                    # Try to find the icon for this specific extension
                    extension_info = self.toolkits[category][option]
                    if extension_info.get("icon"):
                        icon_path = (EXTENSIONS_PATH / category.lower() /
                                     extension_info["icon"])
                    else:
                        icon_path = (EXTENSIONS_PATH / "images" /
                                     "large" / "pyansys.png")

                    # Load image and preserve transparency
                    img = PIL.Image.open(str(icon_path))
                    img = img.resize((48, 48), PIL.Image.LANCZOS)

                    # Get current theme colors for background
                    theme_colors = (self.theme.light if self.root.theme == "light"
                                    else self.theme.dark)

                    # Create a background with theme color for transparency
                    if img.mode == 'RGBA' or 'transparency' in img.info:
                        # Create background with theme color
                        bg_color = theme_colors["widget_bg"]
                        # Convert hex to RGB
                        bg_rgb = tuple(int(bg_color[i:i + 2], 16) for i in (1, 3, 5))
                        background = PIL.Image.new('RGBA', img.size, bg_rgb + (255,))
                        # Composite the image with background
                        img = PIL.Image.alpha_composite(background, img.convert('RGBA'))
                        img = img.convert('RGB')

                    photo = PIL.ImageTk.PhotoImage(img)
                    self.images.append(photo)
                    icon = ttk.Label(card, image=photo)
                    icon.pack(padx=10, pady=10)
                except Exception:
                    icon = ttk.Label(card, text="❓", style="PyAEDT.TLabel",
                                     font=("Segoe UI Emoji", 18))
                    icon.pack(padx=10, pady=10)

            # Text
            label = ttk.Label(card, text=options[option], style="PyAEDT.TLabel", anchor="center")
            label.pack(padx=10, pady=10)

            # Click handler for launching extensions
            card.bind("<Button-1>", lambda e, cat=category, opt=option:
            self.launch_extension(cat, opt))
            icon.bind("<Button-1>", lambda e, cat=category, opt=option:
            self.launch_extension(cat, opt))
            label.bind("<Button-1>", lambda e, cat=category, opt=option:
            self.launch_extension(cat, opt))

            def on_right_click(event, cat=category, opt=option):
                self.confirm_uninstall(cat, opt)

            card.bind("<Button-3>", on_right_click)
            icon.bind("<Button-3>", on_right_click)
            label.bind("<Button-3>", on_right_click)

        # Expand columns
        for col in range(3):
            scroll_frame.grid_columnconfigure(col, weight=1)

    def launch_extension(self, category: str, option: str):
        """Launch extension."""
        if option.lower() == "custom":
            script_file, option = self.handle_custom_extension()
            icon = EXTENSIONS_PATH / "images" / "large" / "pyansys.png"
        else:
            if self.toolkits[category][option].get("script", None):
                script_file = EXTENSIONS_PATH / category.lower() / self.toolkits[category][option]["script"]
                icon = EXTENSIONS_PATH / category.lower() / self.toolkits[category][option]["icon"]
            elif self.toolkits[category][option].get("url", None):
                url = self.toolkits[category][option]["url"]
                try:
                    webbrowser.open(str(url))
                except Exception as e:  # pragma: no cover
                    desktop.logger.error("Error launching browser for %s: %s", name, str(e))
                    desktop.logger.error(
                        f"There was an error launching a browser. Please open the following link: {url}.")
                return
            else:  # pragma: no cover
                messagebox.showinfo("Error", "Wrong extension.")
                return

        if getattr(self, "add_to_aedt_var", tkinter.BooleanVar(value=True)).get():
            # Install the custom extension
            add_script_to_menu(
                name=option,
                script_file=str(script_file),
                product=category.lower(),
                executable_interpreter=sys.executable,
                personal_lib=self.desktop.personallib,
                aedt_version=self.desktop.aedt_version_id,
                copy_to_personal_lib=False,
                icon_file=str(icon)
            )

            self.desktop.logger.info(f"Extension {option} added successfully.")

            # Refresh toolkit UI
            if hasattr(self.desktop, 'odesktop'):
                self.desktop.odesktop.RefreshToolkitUI()

        self.desktop.logger.info(f"Launching {str(script_file)}")
        self.desktop.logger.info(f"Using interpreter: {str(self.python_interpreter)}")
        if not script_file.is_file():
            logger.error(f"{script_file} not found.")
            raise FileNotFoundError(f"{script_file} not found.")
        subprocess.Popen([self.python_interpreter, str(script_file)], shell=True)
        self.desktop.logger.info(f"Finished launching {script_file}.")

    def handle_custom_extension(self):
        """Handle custom extension installation."""
        # Ask for script file
        script_file = filedialog.askopenfilename(
            title="Select Extension Script",
            filetypes=[
                ("Python files", "*.py"),
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ]
        )

        if not script_file:
            script_file = EXTENSIONS_PATH / "templates" / "template_get_started.py"
        else:
            script_file = Path(script_file)

        extension_name = "Custom Extension"

        if getattr(self, "add_to_aedt_var", tkinter.BooleanVar(value=True)).get():
            # Ask for extension name
            extension_name = simpledialog.askstring(
                "Extension Name",
                "Enter a name for this extension:"
            )

            if not extension_name:
                extension_name = "Custom Extension"

        return script_file, extension_name

    def apply_canvas_theme(self, canvas):
        """Apply theme to a specific canvas widget."""
        theme_colors = (self.theme.light if self.root.theme == "light"
                        else self.theme.dark)
        canvas.configure(
            background=theme_colors["pane_bg"],
            highlightbackground=theme_colors["tab_border"],
            highlightcolor=theme_colors["tab_border"],
        )

    def toggle_theme(self):
        """Toggle between light and dark themes and update all canvases."""
        super().toggle_theme()

        # Update all canvas elements in the UI
        for widget in self._ExtensionCommon__find_all_widgets(self.root, tkinter.Canvas):
            self.apply_canvas_theme(widget)

    def confirm_uninstall(self, category, option):
        if option.lower() == "custom":
            # Ask for extension name
            option = simpledialog.askstring(
                "Extension Name",
                "Extension name to uninstall:"
            )

            if not option:
                messagebox.showinfo("Information", "Wrong extension name.")
                return

        answer = messagebox.askyesno(
            "Uninstall extension",
            f"Do you want to uninstall '{option}' in {category}?"
        )

        if answer:
            try:
                remove_script_from_menu(desktop_object=self.desktop, name=option, product=category)
                # Refresh toolkit UI
                if hasattr(self.desktop, 'odesktop'):
                    self.desktop.odesktop.RefreshToolkitUI()
            except Exception:
                messagebox.showerror("Error", f"Extension could not be uninstalled")


if __name__ == "__main__":  # pragma: no cover
    # Open UI
    extension: ExtensionCommon = ExtensionManager(withdraw=False)

    tkinter.mainloop()
