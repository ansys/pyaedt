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

import logging
from pathlib import Path
import shutil
import subprocess  # nosec
import sys
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import webbrowser
import threading

import PIL.Image
import PIL.ImageTk

from ansys.aedt.core.extensions import EXTENSIONS_PATH
from ansys.aedt.core.extensions.customize_automation_tab import add_script_to_menu
from ansys.aedt.core.extensions.customize_automation_tab import available_toolkits
from ansys.aedt.core.extensions.customize_automation_tab import get_custom_extension_image
from ansys.aedt.core.extensions.customize_automation_tab import get_custom_extension_script
from ansys.aedt.core.extensions.customize_automation_tab import get_custom_extensions_from_tabconfig
from ansys.aedt.core.extensions.customize_automation_tab import is_extension_in_panel
from ansys.aedt.core.extensions.customize_automation_tab import remove_script_from_menu
from ansys.aedt.core.extensions.customize_automation_tab import AEDT_APPLICATIONS
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon, ToolTip, check_for_pyaedt_update
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()


EXTENSION_TITLE = "Extension Manager"

# Default width and height for the extension window
WIDTH = 900
HEIGHT = 450

# Maximum dimensions for the extension window
MAX_WIDTH = 900
MAX_HEIGHT = 550

# Minimum dimensions for the extension window
MIN_WIDTH = 600
MIN_HEIGHT = 400

AEDT_EXTENSION_APPLICATIONS = [
    "Common",
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


class ExtensionManager(ExtensionProjectCommon):
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
        self.active_process = None
        self.active_extension = None

        self.python_interpreter = Path(sys.executable)
        self.toolkits = None
        self.add_to_aedt_var = tkinter.BooleanVar(value=True)
        self.current_category = (
            "Common"  # Default to Project application
        )

        # Tkinter widgets
        self.right_panel = None
        self.images = []

        # Log variables
        self.full_log_buffer = []  # store tuples (text, tag)
        self.logs_window = None
        self.logs_text_widget = None
        self._log_stream_threads = []

        # Trigger manually since add_extension_content requires loading expression files first
        self.add_extension_content()

        # Add logger
        self.add_logger(self.root, row=4, column=0)

        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.maxsize(MAX_WIDTH, MAX_HEIGHT)
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.update()

        # After UI initialization schedule the non-blocking update check
        try:
            self.check_for_pyaedt_update_on_startup()
        except Exception:  # don't let update checker break the UI
            logging.getLogger("Global").debug("Failed to start pyaedt update checker", exc_info=True)

    def add_extension_content(self):
        """Add custom content to the extension."""
        # Main container (horizontal layout)
        container = ttk.Frame(self.root, style="PyAEDT.TFrame")
        container.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Left panel (Programs) with scrolling
        left_panel = ttk.Frame(
            container, width=250, style="PyAEDT.TFrame"
        )
        left_panel.grid(row=0, column=0, sticky="nsew")

        # Create scrollable left panel
        left_canvas = tkinter.Canvas(
            left_panel, highlightthickness=0, width=135
        )
        left_scrollbar = ttk.Scrollbar(
            left_panel, orient="vertical", command=left_canvas.yview
        )
        left_scroll_frame = ttk.Frame(
            left_canvas, style="PyAEDT.TFrame"
        )

        # Apply theme to left canvas
        self.apply_canvas_theme(left_canvas)

        # Configure scrolling for left panel
        def _on_left_mousewheel(event):  # pragma: no cover
            if _left_content_overflows():
                left_canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )

        def _left_content_overflows():  # pragma: no cover
            left_canvas.update_idletasks()
            bbox = left_canvas.bbox("all")
            if bbox is None:
                return False
            content_height = bbox[3] - bbox[1]
            canvas_height = left_canvas.winfo_height()
            return content_height > canvas_height

        def _bind_left_mousewheel(event):  # pragma: no cover
            left_canvas.bind_all("<MouseWheel>", _on_left_mousewheel)

        def _unbind_left_mousewheel(event):  # pragma: no cover
            left_canvas.unbind_all("<MouseWheel>")

        def _configure_left_scroll_region(e):  # pragma: no cover
            left_canvas.configure(
                scrollregion=left_canvas.bbox("all")
            )
            # Show/hide scrollbar based on content overflows
            if _left_content_overflows():
                left_scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                left_scrollbar.grid_remove()

        left_canvas.bind("<Enter>", _bind_left_mousewheel)
        left_canvas.bind("<Leave>", _unbind_left_mousewheel)
        left_scroll_frame.bind(
            "<Configure>", _configure_left_scroll_region
        )
        left_canvas.create_window(
            (0, 0), window=left_scroll_frame, anchor="nw"
        )
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.grid(row=0, column=0, sticky="nsew")
        # Initially hide scrollbar - it will show if needed after content is added

        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Right panel (Extensions)
        self.right_panel = ttk.Frame(
            container, style="PyAEDT.TFrame", relief="solid"
        )
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Load programs and extensions dynamically
        self.toolkits = available_toolkits()

        for i, name in enumerate(AEDT_EXTENSION_APPLICATIONS):
            btn = ttk.Button(
                left_scroll_frame,
                text=name,
                command=lambda n=name: self.load_extensions(n),
                style="PyAEDT.TButton",
            )
            btn.grid(row=i, column=0, sticky="ew", padx=5, pady=2)

        # Configure button column to expand
        left_scroll_frame.grid_columnconfigure(0, weight=1)

        # Load the current category (default to Project if none set)
        if self.current_category:
            self.load_extensions(self.current_category)

    def load_extensions(self, category: str):
        """Load application extensions."""
        # Track the current category for UI refresh
        mapped_category = AEDT_APPLICATIONS.get(str(category).lower())

        if mapped_category:
            self.current_category = mapped_category
        elif category in AEDT_APPLICATIONS.values():
            self.current_category = category
        else:
            matched = next(
                (
                    v
                    for v in AEDT_APPLICATIONS.values()
                    if v.lower() == str(category).lower()
                ),
                None,
            )
            self.current_category = matched or category

        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        canvas = tkinter.Canvas(
            self.right_panel, highlightthickness=0
        )
        v_scrollbar = ttk.Scrollbar(
            self.right_panel, orient="vertical", command=canvas.yview
        )
        h_scrollbar = ttk.Scrollbar(
            self.right_panel,
            orient="horizontal",
            command=canvas.xview,
        )
        scroll_frame = ttk.Frame(
            canvas, style="PyAEDT.TFrame", relief="solid"
        )

        # Apply theme to canvas
        self.apply_canvas_theme(canvas)

        # Add mouse wheel scrolling only when content overflows
        def _on_mousewheel(event):  # pragma: no cover
            # Only scroll if content overflows the canvas
            if _content_overflows_vertically():
                canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )

        def _on_shift_mousewheel(event):  # pragma: no cover
            # Horizontal scrolling with Shift+MouseWheel
            if _content_overflows_horizontally():
                canvas.xview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )

        def _content_overflows_vertically():  # pragma: no cover
            # Check if scroll region height > canvas height
            canvas.update_idletasks()  # Ensure layout is updated
            bbox = canvas.bbox("all")
            if bbox is None:
                return False
            content_height = bbox[3] - bbox[1]  # bottom - top
            canvas_height = canvas.winfo_height()
            return content_height > canvas_height

        def _content_overflows_horizontally():  # pragma: no cover
            # Check if scroll region width > canvas width
            canvas.update_idletasks()  # Ensure layout is updated
            bbox = canvas.bbox("all")
            if bbox is None:
                return False
            content_width = bbox[2] - bbox[0]  # right - left
            canvas_width = canvas.winfo_width()
            return content_width > canvas_width

        def _bind_mousewheel(event):  # pragma: no cover
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all(
                "<Shift-MouseWheel>", _on_shift_mousewheel
            )

        def _unbind_mousewheel(event):  # pragma: no cover
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Shift-MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        def _configure_scroll_region(e):  # pragma: no cover
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
        canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
        )

        canvas.grid(row=0, column=0, sticky="nsew")
        # Scrollbars shown/hidden dynamically based on overflow

        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        # For horizontal scrollbar
        self.right_panel.grid_rowconfigure(1, weight=0)

        header = ttk.Label(
            scroll_frame,
            text=f"{category} Extensions",
            style="PyAEDT.TLabel",
            font=("Arial", 12, "bold"),
        )
        header.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=10,
            pady=(10, 10),
        )

        # Load extensions from TOML
        extensions = list(self.toolkits.get(self.current_category, {}).keys())
        options = {}
        toml_names = set()
        if extensions:
            options["Custom"] = "Custom"
            for extension_name in extensions:
                options[extension_name] = self.toolkits[self.current_category][extension_name].get("name",
                                                                                                   extension_name)
                toml_names.add(self.toolkits[self.current_category][extension_name].get("name", extension_name))
        else:
            options["Custom"] = "Custom"

        # Load custom extensions from XML if available
        toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
        xml_dir = toolkit_dir / self.current_category
        tabconfig_path = xml_dir / "TabConfig.xml"
        logger = logging.getLogger("Global")
        if xml_dir.is_dir() and tabconfig_path.is_file():
            get_custom_extensions_from_tabconfig(
                tabconfig_path, toml_names, options, logger=logger
            )

        for index, option in enumerate(options):
            row = (index // 3) + 1
            col = index % 3

            # Create main card container
            card = ttk.Frame(
                scroll_frame, style="PyAEDT.TFrame", relief="solid"
            )
            card.grid(
                row=row, column=col, padx=10, pady=10, sticky="nsew"
            )

            # Create icon container with relative positioning -
            # make it wider to accommodate pin
            icon_container = ttk.Frame(card, style="PyAEDT.TFrame")
            icon_container.pack(padx=10, pady=10)

            # Create a sub-frame for just the main icon,
            # positioned to the left
            main_icon_frame = ttk.Frame(
                icon_container, style="PyAEDT.TFrame"
            )
            main_icon_frame.pack(side="left")

            # Check if extension has URL for clickable functionality
            has_url = False
            if option.lower() == "custom":
                # Custom option always has a URL (documentation link)
                has_url = True
            else:
                extension_info = self.toolkits.get(self.current_category, {}).get(
                    option, {}
                )
                has_url = extension_info.get("url", None) is not None

            # If this is a custom extension from XML, use image and script fields
            if (
                option not in self.toolkits.get(self.current_category, {}) and
                option != "Custom"
            ):
                # Find the button element again to get image and script
                try: # pragma: no cover
                    toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
                    xml_dir = toolkit_dir / self.current_category
                    tabconfig_path = xml_dir / "TabConfig.xml"
                    logger = logging.getLogger("Global")
                    image_path = get_custom_extension_image(tabconfig_path, option, logger=logger)
                    if image_path:
                        image_path_full = (xml_dir / image_path).resolve()
                    else:
                        image_path_full = ""
                except Exception: # pragma: no cover
                    image_path_full = ""
                if image_path_full and Path(image_path_full).is_file(): # pragma: no cover
                    try:
                        img = PIL.Image.open(str(image_path_full))
                        photo = self.create_theme_background_image(img, (48, 48))
                        self.images.append(photo)
                        icon = ttk.Label(main_icon_frame, image=photo)
                        icon.pack()
                    except Exception:
                        icon = ttk.Label(
                            main_icon_frame,
                            text="🧩",
                            style="PyAEDT.TLabel",
                            font=("Segoe UI Emoji", 25),
                        )
                        icon.pack()
                else:
                    icon = ttk.Label(
                        main_icon_frame,
                        text="🧩",
                        style="PyAEDT.TLabel",
                        font=("Segoe UI Emoji", 25),
                    )
                    icon.pack()
            elif option.lower() == "custom":
                icon = ttk.Label(
                    main_icon_frame,
                    text="🧩",
                    style="PyAEDT.TLabel",
                    font=("Segoe UI Emoji", 25),
                )
                icon.pack()
            else:
                try:
                    # Try to find the icon for this specific extension
                    extension_info = self.toolkits[self.current_category][option]
                    if extension_info.get("icon"):
                        icon_path = (
                            EXTENSIONS_PATH
                            / category.lower()
                            / extension_info["icon"]
                        )
                    else:
                        icon_path = (
                            EXTENSIONS_PATH
                            / "images"
                            / "large"
                            / "pyansys.png"
                        )

                    # Load image and preserve transparency
                    img = PIL.Image.open(str(icon_path))

                    # Use the extracted method for theme background
                    # handling
                    photo = self.create_theme_background_image(
                        img, (48, 48)
                    )
                    self.images.append(photo)
                    icon = ttk.Label(main_icon_frame, image=photo)
                    icon.pack()
                except Exception:
                    icon = ttk.Label(
                        main_icon_frame,
                        text="❓",
                        style="PyAEDT.TLabel",
                        font=("Segoe UI Emoji", 18),
                    )
                    icon.pack()

            # Make icon clickable if it has a URL
            if has_url:
                icon.configure(cursor="hand2")

                def create_click_handler(cat, opt):
                    return lambda e: self.launch_web_url(cat, opt)

                icon.bind(
                    "<Button-1>",
                    create_click_handler(self.current_category, option),
                )
                # Add tooltip for clickable icons
                ToolTip(icon, "Click to open documentation")

            # Display name: for custom extensions, strip 'custom_' prefix
            display_name = options[option]
            label = ttk.Label(
                card,
                text=display_name,
                style="PyAEDT.TLabel",
                anchor="center",
            )
            label.pack(padx=10, pady=(10, 5))
            # Determine if this is an extension (has script) or toolkit (does not have script)
            is_extension = False
            is_toolkit = False
            if (option.lower() != "custom" and
                option in self.toolkits.get(category, {})):
                extension_info = self.toolkits[category][option]
                is_extension = (
                    extension_info.get("script", None) is not None
                )
                is_toolkit = not is_extension
            # For custom extensions from XML, treat as extension (show Launch button)
            if (option not in self.toolkits.get(category, {}) and
                option != "Custom"):
                is_extension = True
                is_toolkit = False

            # Add pin icon overlay only for actual extensions
            # (not custom or toolkits)
            if is_extension:
                # Create overlay frame positioned to the right of
                # the main icon
                overlay_frame = tkinter.Frame(
                    icon_container, highlightthickness=0
                )
                overlay_frame.pack(
                    side="right", anchor="ne", padx=(5, 0)
                )

                pin_icon = self.create_pin_icon(
                    overlay_frame, category, option
                )
                pin_icon.pack()
            # Show appropriate buttons based on type
            if (option.lower() == "custom" or
                (option not in self.toolkits.get(category, {}) and
                 option != "Custom")):
                # Custom extensions get a shortcut button for pinning
                button_frame = ttk.Frame(card, style="PyAEDT.TFrame")
                button_frame.pack(padx=10, pady=(0, 10), fill="x")

                custom_btn = ttk.Button(
                    button_frame,
                    text="Launch",
                    style="PyAEDT.ActionLaunch.TButton",
                    command=lambda cat=category,
                    opt=option: self.launch_extension(cat, opt),
                )
                custom_btn.pack(expand=True, fill="x")
            elif is_toolkit:
                # For toolkits, show only "Open Web" button
                button_frame = ttk.Frame(card, style="PyAEDT.TFrame")
                button_frame.pack(padx=10, pady=(0, 10), fill="x")

                web_btn = ttk.Button(
                    button_frame,
                    text="Open Web",
                    style="PyAEDT.ActionWeb.TButton",
                    command=lambda cat=category,
                    opt=option: self.launch_web_url(cat, opt),
                )
                web_btn.pack(expand=True, fill="x")
            elif is_extension:
                # For extensions, show only "Launch" button (pin handles pin/unpin)
                button_frame = ttk.Frame(card, style="PyAEDT.TFrame")
                button_frame.pack(padx=10, pady=(0, 10), fill="x")

                launch_btn = ttk.Button(
                    button_frame,
                    text="Launch",
                    style="PyAEDT.ActionLaunch.TButton",
                    command=lambda cat=category,
                    opt=option: self.launch_extension(cat, opt),
                )
                launch_btn.pack(expand=True, fill="x")

        # Expand columns
        for col in range(3):
            scroll_frame.grid_columnconfigure(col, weight=1)

    def launch_extension(self, category: str, option: str):
        """Launch extension without pinning it to AEDT top bar."""
        if self.active_process and self.active_process.poll() is None:
            self.log_message(f"{self.active_extension} is already running.")
            return
        self.active_process = None
        self.active_extension = None
        category = category.lower()
        is_custom = option.lower() == "custom"
        script_file = None
        script_field = None
        option_label = option
        logger = logging.getLogger("Global")
        if option not in self.toolkits.get(self.current_category, {}) and option != "Custom": # pragma: no cover
            toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
            xml_dir = toolkit_dir / self.current_category
            tabconfig_path = xml_dir / "TabConfig.xml"
            if xml_dir.is_dir() and tabconfig_path.is_file():
                script_field = get_custom_extension_script(tabconfig_path, option, logger=logger)
                if script_field:
                    script_file = (xml_dir / script_field).resolve()
                else:
                    script_file = None
                option_label = option
            if not script_file:
                messagebox.showinfo("Error", f"Script {script_field} for custom extension "
                                             f"'{option}' not found.")
                return
        elif is_custom:
            script_file, display_name = self.handle_custom_extension()
            if script_file is None:
                self.desktop.logger.info("Exited custom extension setup.")
                return
            option_label = display_name
        else:
            # PyAEDT built-in extensions
            option_label = option
            category_toolkits = self.toolkits.get(self.current_category, {})
            if category_toolkits.get(option, {}).get("script", None):
                script_file = (
                    EXTENSIONS_PATH
                    / category
                    / self.toolkits[self.current_category][option]["script"]
                )
            else:
                messagebox.showinfo("Error", "Wrong extension.")
                return
        icon = EXTENSIONS_PATH / "images" / "large" / "pyansys.png"
        if is_custom and script_field is None:
            try:
                add_script_to_menu(
                    name=option_label,
                    script_file=str(script_file),
                    product=category,
                    executable_interpreter=sys.executable,
                    personal_lib=self.desktop.personallib,
                    aedt_version=self.desktop.aedt_version_id,
                    copy_to_personal_lib=True,
                    icon_file=str(icon),
                    is_custom=True,
                )
            except Exception as e:
                self.desktop.logger.error(
                    "Failed to install custom extension %s: %s",
                    option_label,
                    e,
                )
                messagebox.showerror("Error", f"Failed to pin custom extension: {e}")
                return

            # Refresh the custom extensions
            self.load_extensions(category)
            self.desktop.logger.info(
                "Extension %s pinned successfully. If the extension is not visible, create a new AEDT session or create a new project.",
                option_label,
            )

            # if hasattr(self.desktop, "odesktop"):
            #     self.desktop.odesktop.RefreshToolkitUI()
        msg1 = f"{option} launched."

        self.desktop.logger.info(msg1)
        self.desktop.logger.info(f"Using interpreter: {str(self.python_interpreter)}")
        self.log_message(msg1)

        if not script_file:
            msg = f"{script_file} not found."
            self.desktop.logger.error(msg)
            self.log_message(msg)
            raise FileNotFoundError(f"{script_file} not found.")
        if not script_file.suffix == ".py":
            script_file = script_file.with_suffix(".py")
        self.active_extension = option
        self.active_process = subprocess.Popen([
            self.python_interpreter, str(script_file)
        ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # nosec

        # Start streaming logs
        self._start_log_stream_threads()

    def _start_log_stream_threads(self):
        """Start background threads to capture stdout and stderr."""
        import threading
        if not self.active_process:
            return
        def reader(stream, tag):
            for line in iter(stream.readline, ''):
                self._append_full_log(line.rstrip('\n'), tag)
            stream.close()
        for thr in self._log_stream_threads:
            if thr.is_alive():
                return  # already running
        self._log_stream_threads = []
        t_out = threading.Thread(
            target=reader, args=(self.active_process.stdout, 'stdout'), daemon=True
        )
        t_err = threading.Thread(
            target=reader, args=(self.active_process.stderr, 'stderr'), daemon=True
        )
        t_out.start()
        t_err.start()
        self._log_stream_threads.extend([t_out, t_err])
        # Schedule periodic UI refresh
        self.root.after(500, self._periodic_log_refresh)

    def _append_full_log(self, text, tag):
        self.full_log_buffer.append((text, tag))
        # Keep size bounded (optional)
        if len(self.full_log_buffer) > 10000:
            self.full_log_buffer = self.full_log_buffer[-8000:]

    def _periodic_log_refresh(self): # pragma: no cover
        # If detached window open update it
        if self.logs_window and self.logs_text_widget:
            try:
                self._update_logs_text_widget()
            except Exception:
                messagebox.showerror(
                    "Error", "Logs window error. Closing it."
                )
        # Reschedule if process still running
        if self.active_process and self.active_process.poll() is None:
            self.root.after(500, self._periodic_log_refresh)

    def _update_logs_text_widget(self):
        widget = self.logs_text_widget
        if not widget:
            return
        # Save current view to auto-scroll only if at bottom
        at_end = False
        if widget.index('end-1c') == widget.index('insert'):
            at_end = True
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        for line, tag in self.full_log_buffer:
            if tag == 'stderr':
                widget.insert('end', line + '\n', 'stderr')
            else:
                widget.insert('end', line + '\n')
        widget.configure(state='disabled')
        if at_end:
            widget.see('end')

    def _close_logs_window(self):  # pragma: no cover
        """Close and cleanup the detached logs window."""
        if self.logs_window:
            try:
                self.logs_window.destroy()
            except Exception:
                messagebox.showerror(
                    "Error", "Failed to close logs window."
                )
            finally:
                # Clear reference so future checks see it's closed
                self.logs_window = None
        self.logs_text_widget = None

    def open_all_logs_window(self):  # override base
        # Toggle behavior: if already open, close it on button click
        if self.logs_window and tkinter.Toplevel.winfo_exists(
            self.logs_window
        ):
            try:
                self._close_logs_window()
                return
            except Exception:  # pragma: no cover
                messagebox.showerror(
                    "Error", "Failed to close existing logs window."
                )
                return
        self.logs_window = tkinter.Toplevel(self.root)
        self.logs_window.title('Extension Logs')
        self.logs_window.geometry('700x400')
        self.logs_window.protocol(
            'WM_DELETE_WINDOW', self._close_logs_window
        )

        # Top-right buttons frame
        top_btn_frame = ttk.Frame(self.logs_window, style='PyAEDT.TFrame')
        top_btn_frame.pack(fill='x', padx=5, pady=(5, 0))

        # Place buttons on the right side of the top bar
        export_btn = ttk.Button(
            top_btn_frame,
            text='Export',
            style='PyAEDT.TButton',
            command=self._export_logs,
            width=10,
        )
        export_btn.pack(side='right', padx=(5, 0))

        clear_btn = ttk.Button(
            top_btn_frame,
            text='Clear',
            style='PyAEDT.TButton',
            command=self._clear_logs,
            width=10,
        )
        clear_btn.pack(side='right')

        # Text area + scrollbars container (below top buttons)
        text_frame = ttk.Frame(self.logs_window, style='PyAEDT.TFrame')
        text_frame.pack(fill='both', expand=True, padx=5, pady=(5, 5))

        # Vertical and horizontal scrollbars
        v_scroll = ttk.Scrollbar(text_frame, orient='vertical')
        h_scroll = ttk.Scrollbar(text_frame, orient='horizontal')

        txt = tkinter.Text(
            text_frame, wrap='none',
            xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set
        )
        # Attach scroll commands
        v_scroll.config(command=txt.yview)
        h_scroll.config(command=txt.xview)

        # Layout: vertical scrollbar on right, horizontal at bottom
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        txt.pack(side='left', fill='both', expand=True)

        # Apply theme colors
        theme_colors = (
            self.theme.light if self.root.theme == 'light'
            else self.theme.dark
        )
        txt.configure(
            background=theme_colors['pane_bg'],
            foreground=theme_colors['text'],
            font=self.theme.default_font,
        )
        txt.tag_config('stderr', foreground='red')
        self.logs_text_widget = txt
        self._update_logs_text_widget()

    def _clear_logs(self):
        """Clear full log buffer and update window."""
        self.full_log_buffer.clear()
        if self.logs_text_widget:
            try:
                self.logs_text_widget.configure(state='normal')
                self.logs_text_widget.delete('1.0', 'end')
                self.logs_text_widget.configure(state='disabled')
            except Exception:  # pragma: no cover
                messagebox.showerror(
                    "Error", "Failed to clear logs window."
                )

    def _export_logs(self):
        """Export logs to a text file."""
        if not self.full_log_buffer:
            messagebox.showinfo(
                'Export Logs', 'No logs to export.'
            )
            return
        file_path = filedialog.asksaveasfilename(
            title='Save Logs',
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')],
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line, tag in self.full_log_buffer:
                    if tag == 'stderr':
                        f.write('[ERR] ' + line + '\n')
                    else:
                        f.write(line + '\n')
            messagebox.showinfo(
                'Export Logs', f'Logs saved to\n{file_path}'
            )
        except Exception as e:
            messagebox.showerror(
                'Export Logs', f'Failed to save logs: {e}'
            )

    def pin_extension(self, category: str, option: str):
        """Pin extension to AEDT to bar."""
        if option.lower() == "custom":
            script_file, option = self.handle_custom_extension()
            icon = (
                EXTENSIONS_PATH / "images" / "large" / "pyansys.png"
            )
            # If the user selected a script, copy it into personal lib Toolkits/<product>/<option>/Lib
            if not script_file:
                self.desktop.logger.info("No script selected for custom extension. Aborting pin.")
                return
            try:
                add_script_to_menu(
                    name=option,
                    script_file=str(script_file),
                    product=category,
                    executable_interpreter=sys.executable,
                    personal_lib=self.desktop.personallib,
                    aedt_version=self.desktop.aedt_version_id,
                    copy_to_personal_lib=True,
                    icon_file=str(icon),
                    is_custom=True,
                )
                msg = (f"Extension {option} pinned successfully.\n"
                       f"If the extension is not visible create a new AEDT session or create a new project.")
                self.desktop.logger.info(msg)
                self.log_message(msg)
            except Exception as e:
                self.desktop.logger.error(f"Failed to pin custom extension {option}: {e}")
                messagebox.showerror("Error", f"Failed to pin custom extension: {e}")
                return
        else:
            if self.toolkits[self.current_category][option].get("script", None):
                script_file = (
                    EXTENSIONS_PATH
                    / category.lower()
                    / self.toolkits[self.current_category][option]["script"]
                )
                icon = (
                    EXTENSIONS_PATH
                    / category.lower()
                    / self.toolkits[self.current_category][option]["icon"]
                )
                # Pin the extension
                add_script_to_menu(
                    name=option,
                    script_file=str(script_file),
                    product=category,
                    executable_interpreter=sys.executable,
                    personal_lib=self.desktop.personallib,
                    aedt_version=self.desktop.aedt_version_id,
                    copy_to_personal_lib=False,
                    icon_file=str(icon),
                )
                msg = (f"Extension {option} pinned successfully.\n"
                       f"If the extension is not visible create a new AEDT session or create a new project.")
                self.desktop.logger.info(msg)
                self.log_message(msg)
                # # Refresh toolkit UI
                # if hasattr(self.desktop, "odesktop"):
                #     self.desktop.odesktop.CloseAllWindows()
                #     self.desktop.odesktop.RefreshToolkitUI()
            else:  # pragma: no cover
                messagebox.showinfo("Error", "Wrong extension.")
                return

        # Refresh the extension manager UI to show the unpin button
        self.load_extensions(category)

    def handle_custom_extension(self):
        """Handle custom extension pin to the top bar."""
        # Prompt user for script file and extension name
        result = {"script_file": None, "display_name": None}
        # Create a single dialog window for all inputs
        dialog = tkinter.Toplevel(self.root)
        dialog.title("Custom Extension Setup")
        dialog.resizable(False, False)

        # Script file selection
        ttk.Label(dialog, text="Select Extension Script:").pack(
            padx=10, pady=(10, 2), anchor="w"
        )
        script_var = tkinter.StringVar()
        script_entry = ttk.Entry(
            dialog, textvariable=script_var, width=60
        )
        script_entry.pack(padx=10, pady=2, fill="x")

        def browse_script(): # pragma: no cover
            file_path = filedialog.askopenfilename(
                title="Select Python script",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
            )
            if file_path:
                script_var.set(file_path)

        browse_btn = ttk.Button(
            dialog, text="Browse...", command=browse_script
        )
        browse_btn.pack(padx=10, pady=2, anchor="e")

        # Extension name input
        ttk.Label(dialog, text="Extension Name:").pack(
            padx=10, pady=(10, 2), anchor="w"
        )
        name_var = tkinter.StringVar(value="Custom Extension")
        name_entry = ttk.Entry(
            dialog, textvariable=name_var, width=60
        )
        name_entry.pack(padx=10, pady=2, fill="x")

        # Buttons frame (OK / Cancel)
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(padx=10, pady=10, fill="x")

        def on_ok():
            script = script_var.get().strip()
            name = name_var.get().strip()

            # Basic validation
            if not script:
                script = (
                    EXTENSIONS_PATH
                    / "templates"
                    / "template_get_started.py"
                )
            script_path = Path(script)
            if not name: # pragma: no cover
                messagebox.showerror("Error", "Please enter an extension name.")
                return

            # Prevent using reserved option name
            if name.lower() == "custom" or name.lower() == "custom_extension":  # pragma: no cover
                messagebox.showerror(
                    "Error",
                    "The names 'custom' and 'custom_extension' are reserved. Please choose a different name.",
                )
                return

            # Check for conflicts in existing toolkits / program extension folder
            product = self.current_category
            toolkit_dir = Path(self.desktop.personallib) / "Toolkits"

            existing_keys = {k.lower() for k in self.toolkits.get(product, {}).keys()}
            if name.lower() in existing_keys:  # pragma: no cover
                messagebox.showerror(
                    "Error",
                    f"An extension named '{name}' already exists in {product}. Please choose a different name.",
                )
                return

            if is_extension_in_panel(str(toolkit_dir), product, name):  # pragma: no cover
                messagebox.showerror(
                    "Error",
                    f"An extension named '{name}' already exists in {product}. Please choose a different name.",
                )
                return

            result["script_file"] = script_path.resolve()
            result["display_name"] = name
            dialog.destroy()

        def on_cancel():
            result["script_file"] = None
            result["display_name"] = None
            dialog.destroy()

        ok_btn = ttk.Button(btn_frame, text="OK", command=on_ok)
        ok_btn.pack(side="right", padx=(5, 0))
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=on_cancel)
        cancel_btn.pack(side="right")

        dialog.grab_set()
        self.root.wait_window(dialog)

        if result["script_file"]:
            return result["script_file"], result["display_name"]
        return None, None

    def create_theme_background_image(self, img, target_size=None):
        """Create a background image with theme color for transparency.

        Parameters
        ----------
        img : PIL.Image
            The image to process.
        target_size : tuple, optional
            Target size to resize the image to (width, height).

        Returns
        -------
        PIL.ImageTk.PhotoImage
            The processed image ready for tkinter.
        """
        # Resize if target size is specified
        if target_size:
            img = img.resize(target_size, PIL.Image.LANCZOS)

        # Get current theme colors for background
        theme_colors = (
            self.theme.light
            if self.root.theme == "light"
            else self.theme.dark
        )

        # Create a background with theme color for transparency
        if img.mode == "RGBA" or "transparency" in img.info:
            # Create background with theme color
            bg_color = theme_colors["widget_bg"]
            # Convert hex to RGB
            bg_rgb = tuple(
                int(bg_color[i : i + 2], 16) for i in (1, 3, 5)
            )
            # Make background fully transparent
            background = PIL.Image.new(
                "RGBA", img.size, bg_rgb + (0,)
            )
            # Blend with original image
            img = PIL.Image.alpha_composite(
                background, img.convert("RGBA")
            )

        return PIL.ImageTk.PhotoImage(img, master=self.root)

    def create_pin_icon(
        self, parent, category: str, option: str, size=(20, 20)
    ):
        """Create a pin icon based on extension installation status.

        Parameters
        ----------
        parent : tkinter widget
            Parent widget to place the pin icon on.
        category : str
            The category/product name.
        option : str
            The extension name.
        size : tuple
            Size of the pin icon (width, height).

        Returns
        -------
        ttk.Label
            The pin icon label widget.
        """
        is_pinned = self.check_extension_pinned(category, option)

        if is_pinned:
            pin_path = (
                EXTENSIONS_PATH
                / "installer"
                / "images"
                / "large"
                / "pin.png"
            )
            tooltip_text = "Click to unpin extension"
        else:
            pin_path = (
                EXTENSIONS_PATH
                / "installer"
                / "images"
                / "large"
                / "unpin.png"
            )
            tooltip_text = "Click to pin extension"

        # Load pin image
        pin_img = PIL.Image.open(str(pin_path))

        # Use the extracted method for theme background handling
        pin_photo = self.create_theme_background_image(
            pin_img, target_size=size
        )
        self.images.append(pin_photo)

        pin_label = ttk.Label(
            parent,
            image=pin_photo,
            style="PyAEDT.TLabel",
            cursor="hand2",
        )

        # Add tooltip
        ToolTip(pin_label, tooltip_text)

        # Bind click event
        pin_label.bind(
            "<Button-1>",
            lambda e: self.on_pin_click(category, option),
        )
        return pin_label

    def on_pin_click(self, category: str, option: str):
        """Handle pin icon click events.

        Parameters
        ----------
        category : str
            The category/product name.
        option : str
            The extension name.
        """
        is_pinned = self.check_extension_pinned(category, option)

        if is_pinned:
            self.confirm_unpin(category, option)
        else:
            self.pin_extension(category, option)

    def apply_canvas_theme(self, canvas):
        """Apply theme to a specific canvas widget."""
        theme_colors = (
            self.theme.light
            if self.root.theme == "light"
            else self.theme.dark
        )
        canvas.configure(
            background=theme_colors["pane_bg"],
            highlightbackground=theme_colors["tab_border"],
            highlightcolor=theme_colors["tab_border"],
        )

    def toggle_theme(self):
        """Toggle between light and dark themes and refresh UI."""
        super().toggle_theme()

        # Clear the images cache to force recreation with new theme
        self.images.clear()

        # Update all canvas elements in the UI
        for widget in self._ExtensionCommon__find_all_widgets(
            self.root, tkinter.Canvas
        ):
            self.apply_canvas_theme(widget)

        # Recreate the extension content with new theme-appropriate
        # images
        self.add_extension_content()

    def confirm_unpin(self, category, option):
        # If custom extension, label starts with 'custom_'
        is_custom = option.startswith("custom_")
        if option.lower() == "custom": # pragma: no cover
            option = simpledialog.askstring(
                "Extension Name", "Extension name to unpin:",
            )
            if not option:
                messagebox.showinfo(
                    "Information", "Wrong extension name."
                )
                return
            is_custom = option.startswith("custom_")
        product = category
        toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
        if not is_extension_in_panel(
            str(toolkit_dir), product, option
        ):
            messagebox.showinfo(
                "Information",
                f"'{option}' extension is already unpined "
                f"or does not exist in {category}.",
            )
            return
        answer = messagebox.askyesno(
            "Unpin extension",
            f"Do you want to unpin '{option}' in {category}?",
        )
        if answer:
            try:
                remove_script_from_menu(
                    desktop_object=self.desktop,
                    name=option,
                    product=category,
                )
                # If custom, delete its files
                if is_custom:
                    custom_dir = (
                        Path(self.desktop.personallib)
                        / "Toolkits" / category / option
                    )
                    shutil.rmtree(custom_dir, ignore_errors=True)

                # if hasattr(self.desktop, "odesktop"):
                #     Bug in AEDT does not allow to refresh the UI correctly
                #     self.desktop.odesktop.RefreshToolkitUI()
                self.log_message(f"{option} extension removed successfully.")
                if self.current_category:
                    self.load_extensions(category)
            except Exception: # pragma: no cover
                messagebox.showerror(
                    "Error", "Extension could not be removed."
                )

    def check_extension_pinned(self, category: str, option: str):
        """Check if an extension is pined in AEDT.

        Parameters
        ----------
        category : str
            The category/product name.
        option : str
            The extension name.

        Returns
        -------
        bool
            True if the extension is pinned, False otherwise.
        """
        if option.lower() == "custom": # pragma: no cover
            return False  # Custom extensions are not tracked

        try:
            product = category.lower()
            toolkit_dir = Path(self.desktop.personallib) / "Toolkits"
            return is_extension_in_panel(
                str(toolkit_dir), product, option
            )
        except Exception: # pragma: no cover
            return False

    def launch_web_url(self, category: str, option: str):
        """Launch web URL for an extension or toolkit."""
        try:
            if option.lower() == "custom":
                # For custom option, open PyAEDT documentation
                url = "https://aedt.docs.pyansys.com/version/stable/User_guide/extensions.html"
                webbrowser.open(str(url))
                msg = "Opened template documentation."
                self.desktop.logger.info(msg)
                self.log_message(msg)
                return True
            else:
                extension_info = self.toolkits[category][option]
                url = extension_info.get("url", None)
                if url:
                    webbrowser.open(str(url))
                    msg = f"Opened {option} documentation."
                    self.desktop.logger.info(msg)
                    self.log_message(msg)
                    return True
                else:
                    messagebox.showinfo(
                        "Error", "No URL found for this extension."
                    )
                    return False
        except Exception as e: # pragma: no cover
            msg = "Could not open web URL."
            self.log_message(msg)
            self.desktop.logger.error(f"Error opening web URL: {e}")
            messagebox.showerror("Error", msg)
            return False

    def check_for_pyaedt_update_on_startup(self):
        """Spawn a background thread to check PyPI for a newer PyAEDT release.
        """
        def worker(): # pragma: no cover
            log = logging.getLogger("Global")
            try:
                latest, declined_file = check_for_pyaedt_update(self.desktop.personallib)
                if not latest:
                    log.debug("PyAEDT update check: no prompt required or latest unavailable.")
                    return
                try:
                    self.root.after(
                        0,
                        lambda: self.show_pyaedt_update_popup(latest, declined_file)
                    )
                except Exception:
                    log.debug("PyAEDT update check: failed to schedule popup.", exc_info=True)
            except Exception:
                log.debug("PyAEDT update check: worker failed.", exc_info=True)

        threading.Thread(target=worker, daemon=True).start()

    def show_pyaedt_update_popup(self, latest_version: str, declined_file_path: Path): # pragma: no cover
        """Display a modal dialog offering Decline or Remind later and instruct user to open Version Manager."""
        try:
            dlg = tkinter.Toplevel(self.root)
            dlg.title("PyAEDT Update")
            dlg.resizable(False, False)

            # Center dialog
            try:
                self.root.update_idletasks()
                width, height = 500, 120
                x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
                y = self.root.winfo_rooty() + (self.root.winfo_height() - height) // 2
                dlg.geometry(f"{width}x{height}+{x}+{y}")
            except Exception:
                logging.getLogger("Global").debug("Failed to center update popup", exc_info=True)

            # Create frame for label and changelog button
            label_frame = ttk.Frame(dlg, style="PyAEDT.TFrame")
            label_frame.pack(
                padx=20, pady=(20, 10), expand=True, fill="both"
            )

            ttk.Label(
                label_frame,
                text=(
                    f"A new version of PyAEDT is available: "
                    f"{latest_version}\n"
                    "To update PyAEDT, please open the "
                    "Version Manager."
                ),
                style="PyAEDT.TLabel",
                anchor="center",
                justify="center",
            ).pack(side="left", expand=True, fill="both")

            def open_changelog():
                try:
                    url = ("https://aedt.docs.pyansys.com/version/stable/"
                           "changelog.html")
                    webbrowser.open(str(url))
                    logging.getLogger("Global").info(
                        "Opened PyAEDT changelog."
                    )
                except Exception:
                    logging.getLogger("Global").debug(
                        "Failed to open changelog", exc_info=True
                    )

            changelog_btn = ttk.Button(
                label_frame,
                text="?",
                command=open_changelog,
                style="PyAEDT.TButton",
                width=3
            )
            changelog_btn.pack(side="right", padx=(5, 0))
            ToolTip(changelog_btn, "View changelog")

            btn_frame = ttk.Frame(dlg, style="PyAEDT.TFrame")
            btn_frame.pack(padx=10, pady=(0, 10), fill="x")

            def decline():
                try:
                    from ansys.aedt.core.extensions.misc import (
                        decline_pyaedt_update,
                    )

                    decline_pyaedt_update(
                        declined_file_path, latest_version
                    )
                except Exception:
                    logging.getLogger("Global").debug(
                        "PyAEDT update popup: failed to record "
                        "declined version.",
                        exc_info=True,
                    )
                dlg.destroy()

            def remind():
                dlg.destroy()

            ttk.Button(
                btn_frame, text="Decline", command=decline,
                style="PyAEDT.TButton"
            ).pack(side="left", expand=True, fill="x", padx=5)
            ttk.Button(
                btn_frame, text="Remind later", command=remind,
                style="PyAEDT.TButton"
            ).pack(side="left", expand=True, fill="x", padx=5)

            dlg.transient(self.root)
            dlg.grab_set()
            self.root.wait_window(dlg)
        except Exception:
            logging.getLogger("Global").debug(
                "PyAEDT update popup: failed to display.",
                exc_info=True
            )


if __name__ == "__main__":  # pragma: no cover
    # Open UI
    extension: ExtensionProjectCommon = ExtensionManager(
        withdraw=False
    )

    tkinter.mainloop()
