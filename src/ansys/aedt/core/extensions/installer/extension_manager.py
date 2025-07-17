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

from pathlib import Path
import sys
import subprocess  # nosec
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
from ansys.aedt.core.extensions.customize_automation_tab import is_extension_in_panel
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

# Default width and height for the extension window
WIDTH = 810
HEIGHT = 450

# Maximum dimensions for the extension window
MAX_WIDTH = 810
MAX_HEIGHT = 550

# Minimum dimensions for the extension window
MIN_WIDTH = 600
MIN_HEIGHT = 400


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
        self.current_category = None  # Track current category for UI refresh

        # Tkinter widgets
        self.right_panel = None
        self.programs = None
        self.default_label = None
        self.images = []

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.maxsize(MAX_WIDTH, MAX_HEIGHT)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")

    def add_extension_content(self):
        """Add custom content to the extension."""

        # Main container (horizontal layout)
        container = ttk.Frame(self.root, style="PyAEDT.TFrame")
        container.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Left panel (Programs) with scrolling
        left_panel = ttk.Frame(container, width=250, style="PyAEDT.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew")

        # Create scrollable left panel
        left_canvas = tkinter.Canvas(left_panel, highlightthickness=0, width=135)
        left_scrollbar = ttk.Scrollbar(left_panel, orient="vertical",
                                       command=left_canvas.yview)
        left_scroll_frame = ttk.Frame(left_canvas,
                                      style="PyAEDT.TFrame")

        # Apply theme to left canvas
        self.apply_canvas_theme(left_canvas)

        # Configure scrolling for left panel
        def _on_left_mousewheel(event):
            if _left_content_overflows():
                left_canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                         "units")

        def _left_content_overflows():
            left_canvas.update_idletasks()
            bbox = left_canvas.bbox("all")
            if bbox is None:
                return False
            content_height = bbox[3] - bbox[1]
            canvas_height = left_canvas.winfo_height()
            return content_height > canvas_height

        def _bind_left_mousewheel(event):
            left_canvas.bind_all("<MouseWheel>", _on_left_mousewheel)

        def _unbind_left_mousewheel(event):
            left_canvas.unbind_all("<MouseWheel>")

        def _configure_left_scroll_region(e):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            # Show/hide scrollbar based on content overflow
            if _left_content_overflows():
                left_scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                left_scrollbar.grid_remove()

        left_canvas.bind('<Enter>', _bind_left_mousewheel)
        left_canvas.bind('<Leave>', _unbind_left_mousewheel)
        left_scroll_frame.bind("<Configure>",
                               _configure_left_scroll_region)
        left_canvas.create_window((0, 0), window=left_scroll_frame,
                                  anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.grid(row=0, column=0, sticky="nsew")
        # Initially hide scrollbar - it will show if needed after content is added

        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Right panel (Extensions)
        self.right_panel = ttk.Frame(container, style="PyAEDT.TFrame",
                                     relief="solid")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Load programs and extensions dynamically
        self.toolkits = available_toolkits()
        self.programs = AEDT_APPLICATIONS

        for i, name in enumerate(AEDT_APPLICATIONS):
            btn = ttk.Button(left_scroll_frame, text=name,
                             command=lambda n=name: self.load_extensions(n),
                             style="PyAEDT.TButton")
            btn.grid(row=i, column=0, sticky="ew", padx=5, pady=2)

        # Configure button column to expand
        left_scroll_frame.grid_columnconfigure(0, weight=1)

        # Placeholder content
        self.default_label = ttk.Label(self.right_panel, text="Select application",
                                       style="PyAEDT.TLabel",
                                       font=("Arial", 12, "bold"))
        self.default_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

    def load_extensions(self, category: str):
        """Load application extensions."""
        # Track the current category for UI refresh
        self.current_category = category
        
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        canvas = tkinter.Canvas(self.right_panel, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical",
                                    command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.right_panel, orient="horizontal",
                                    command=canvas.xview)
        scroll_frame = ttk.Frame(canvas, style="PyAEDT.TFrame",
                                 relief="solid")

        # Apply theme to canvas
        self.apply_canvas_theme(canvas)

        # Add mouse wheel scrolling only when content overflows
        def _on_mousewheel(event):
            # Only scroll if content overflows the canvas
            if _content_overflows_vertically():
                canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                    "units")

        def _on_shift_mousewheel(event):
            # Horizontal scrolling with Shift+MouseWheel
            if _content_overflows_horizontally():
                canvas.xview_scroll(int(-1 * (event.delta / 120)),
                                    "units")

        def _content_overflows_vertically():
            # Check if scroll region height > canvas height
            canvas.update_idletasks()  # Ensure layout is updated
            bbox = canvas.bbox("all")
            if bbox is None:
                return False
            content_height = bbox[3] - bbox[1]  # bottom - top
            canvas_height = canvas.winfo_height()
            return content_height > canvas_height

        def _content_overflows_horizontally():
            # Check if scroll region width > canvas width
            canvas.update_idletasks()  # Ensure layout is updated
            bbox = canvas.bbox("all")
            if bbox is None:
                return False
            content_width = bbox[2] - bbox[0]  # right - left
            canvas_width = canvas.winfo_width()
            return content_width > canvas_width

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Shift-MouseWheel>",
                            _on_shift_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Shift-MouseWheel>")

        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)

        def _configure_scroll_region(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Show/hide scrollbars based on content overflow
            if _content_overflows_vertically():
                v_scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                v_scrollbar.grid_remove()

            if _content_overflows_horizontally():
                h_scrollbar.grid(row=1, column=0, sticky="ew")
            else:
                h_scrollbar.grid_remove()

        scroll_frame.bind("<Configure>", _configure_scroll_region)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set,
                         xscrollcommand=h_scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        # Scrollbars shown/hidden dynamically based on overflow

        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        # For horizontal scrollbar
        self.right_panel.grid_rowconfigure(1, weight=0)

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

            # Create main card container
            card = ttk.Frame(scroll_frame, style="PyAEDT.TFrame", relief="solid")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Create icon container with relative positioning
            icon_container = ttk.Frame(card, style="PyAEDT.TFrame")
            icon_container.pack(padx=10, pady=10)

            if option.lower() == "custom":
                icon = ttk.Label(icon_container, text="🧩", style="PyAEDT.TLabel",
                                 font=("Segoe UI Emoji", 25))
                icon.pack()
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
                    icon = ttk.Label(icon_container, image=photo)
                    icon.pack()
                except Exception:
                    icon = ttk.Label(icon_container, text="❓", style="PyAEDT.TLabel",
                                     font=("Segoe UI Emoji", 18))
                    icon.pack()

            # Check if extension is installed and add overlay if it is
            is_installed = self.check_extension_installed(category, option)
            uninstall_overlay = None
            if is_installed:
                # Create uninstall overlay button
                uninstall_overlay = ttk.Label(icon_container, text="✖", 
                                            style="PyAEDT.TLabel",
                                            font=("Arial", 12, "bold"),
                                            foreground="red",
                                            background="white",
                                            relief="raised",
                                            padding=2)
                uninstall_overlay.place(relx=1.0, rely=0.0, anchor="ne")
                
                # Bind uninstall click handler to overlay
                uninstall_overlay.bind("<Button-1>", lambda e, cat=category, opt=option:
                                     self.confirm_uninstall(cat, opt))

            # Text
            label = ttk.Label(card, text=options[option], style="PyAEDT.TLabel", anchor="center")
            label.pack(padx=10, pady=10)

            # Click handler for launching extensions (only bind to main elements, not overlay)
            card.bind("<Button-1>", lambda e, cat=category, opt=option:
            self.launch_extension(cat, opt))
            icon.bind("<Button-1>", lambda e, cat=category, opt=option:
            self.launch_extension(cat, opt))
            label.bind("<Button-1>", lambda e, cat=category, opt=option:
            self.launch_extension(cat, opt))

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
                except Exception:  # pragma: no cover
                    self.desktop.logger.error(
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
            
            # Refresh the extension manager UI to show the uninstall button
            self.load_extensions(category)

        self.desktop.logger.info(f"Launching {str(script_file)}")
        self.desktop.logger.info(f"Using interpreter: {str(self.python_interpreter)}")
        if not script_file.is_file():
            self.desktop.logger.error(f"{script_file} not found.")
            raise FileNotFoundError(f"{script_file} not found.")
        subprocess.Popen([self.python_interpreter, str(script_file)], shell=True)  # nosec
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

        # Check if extension is already uninstalled
        product = category
        toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
        if not is_extension_in_panel(str(toolkit_dir / product), option):
            messagebox.showinfo(
            "Information", 
            f"'{option}' extension is already uninstalled or does not exist in {category}."
            )
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
                
                # Refresh the extension manager UI to hide the uninstall button
                if self.current_category:
                    self.load_extensions(self.current_category)
            except Exception:
                messagebox.showerror("Error", "Extension could not be uninstalled")

    def check_extension_installed(self, category: str, option: str):
        """Check if an extension is installed in AEDT.
        
        Parameters
        ----------
        category : str
            The category/product name.
        option : str
            The extension name.
            
        Returns
        -------
        bool
            True if the extension is installed, False otherwise.
        """
        if option.lower() == "custom":
            return False  # Custom extensions are not tracked
        
        try:
            product = category
            toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
            return is_extension_in_panel(
                str(toolkit_dir / product),
                option
            )
        except Exception:
            return False


if __name__ == "__main__":  # pragma: no cover
    # Open UI
    extension: ExtensionCommon = ExtensionManager(withdraw=False)

    tkinter.mainloop()
