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

"""Miscellaneous Methods for PyAEDT workflows."""

from __future__ import annotations

from abc import abstractmethod
import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys
import tkinter
from tkinter import ttk
from tkinter.messagebox import showerror
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

import PIL.Image
import PIL.ImageTk

from ansys.aedt.core import Desktop
import ansys.aedt.core.extensions
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.errors import AEDTRuntimeError

NO_ACTIVE_PROJECT = "No active project"
MOON = "\u2600"
SUN = "\u263d"
DEFAULT_PADDING = {"padx": 15, "pady": 10}


def get_process_id():
    """Get process ID from environment variable."""
    value = os.getenv("PYAEDT_SCRIPT_PROCESS_ID")
    return int(value) if value is not None else None


def get_port():
    """Get gRPC port from environment variable."""
    res = int(os.getenv("PYAEDT_SCRIPT_PORT", 0))
    return res


def get_aedt_version():
    """Get AEDT release from environment variable."""
    res = os.getenv("PYAEDT_SCRIPT_VERSION", aedt_versions.current_version)
    return res


def is_student():
    """Get if AEDT student is opened from environment variable."""
    res = os.getenv("PYAEDT_STUDENT_VERSION", "False") != "False"
    return res


@dataclass
class ExtensionCommonData:
    """Data class containing user input and computed data."""


class ExtensionCommon:
    def __init__(
        self,
        title: str,
        theme_color: str = "light",
        withdraw: bool = False,
        add_custom_content: bool = True,
    ):
        """Create and initialize a themed Tkinter UI window.

        This function creates a Tkinter root window, applies a theme, sets the
        application icon, and configures error handling behavior. It also allows for
        optional withdrawal of the window, i.e. keeping it hidden.

        Parameters:
        ----------
        title : str
            The title of the main window.
        theme_color: str, optional
            The theme color to apply to the UI. Options are "light" or "dark". Default is "light".
        withdraw : bool, optional
            If True, the main window is hidden. Default is ``False``.
        add_custom_content : bool, optional
            If True, the method `add_extension_content` is called to add custom content to the UI.
        """
        if theme_color not in ["light", "dark"]:
            raise ValueError(f"Invalid theme color: {theme_color}. Use 'light' or 'dark'.")

        self.root = self.__init_root(title, withdraw)
        self.style: ttk.Style = ttk.Style()
        self.theme: ExtensionTheme = ExtensionTheme()
        self.__desktop = None
        self.__aedt_application = None
        self.__data: Optional[ExtensionCommonData] = None

        self.__apply_theme(theme_color)

        # Top bar frame
        top_frame = ttk.Frame(self.root, style="PyAEDT.TFrame", name="top_frame")
        top_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=0)
        # Icon placeholder (left)
        icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo_pyaedt.png"
        im = PIL.Image.open(icon_path)
        box_size = (150, 40)
        # Create a transparent box
        box = PIL.Image.new("RGBA", box_size, (255, 255, 255, 0))
        # Resize image to fit within box, preserving aspect ratio
        im.thumbnail(box_size, PIL.Image.LANCZOS)
        # Center the image
        x = (box_size[0] - im.width) // 2
        y = (box_size[1] - im.height) // 2
        box.paste(im, (x, y), im if im.mode == "RGBA" else None)
        photo = PIL.ImageTk.PhotoImage(box, master=self.root)
        self.icon_placeholder = ttk.Label(top_frame, image=photo, style="PyAEDT.TLabel", name="icon_placeholder")
        self.icon_placeholder.image = photo  # Keep a reference to avoid garbage collection
        self.icon_placeholder.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        # Theme toggle button (right)
        self.change_theme_button = ttk.Button(
            top_frame,
            width=4,
            text=SUN if theme_color == "light" else MOON,
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        self.change_theme_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        # Separator between top bar and main content
        sep = ttk.Separator(self.root, orient="horizontal")
        sep.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 10))

        # Main content frame for extension content
        self.content_frame = ttk.Frame(self.root, style="PyAEDT.TFrame", name="content_frame")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        if add_custom_content:
            self.add_extension_content()

        self.root.protocol("WM_DELETE_WINDOW", self.__on_close)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.root.theme == "light":
            self.__apply_theme("dark")
        elif self.root.theme == "dark":
            self.__apply_theme("light")
        else:
            raise ValueError(f"Unknown theme: {self.root.theme}. Use 'light' or 'dark'.")

    def __init_root(self, title: str, withdraw: bool) -> tkinter.Tk:
        """Initialize the Tkinter root window with error handling and icon."""

        def report_callback_exception(self, exc, val, tb):
            """Custom exception showing an error message."""
            showerror("Error", message=f"{val} \n {tb}")

        def report_callback_exception_withdraw(self, exc, val, tb):
            """Custom exception that raises the error without showing a message box."""
            raise val

        if withdraw:
            tkinter.Tk.report_callback_exception = report_callback_exception_withdraw
        else:
            tkinter.Tk.report_callback_exception = report_callback_exception

        root = tkinter.Tk()
        root.title(title)
        if withdraw:
            root.withdraw()

        # Load and set the logo for the main window
        if not withdraw:
            icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo.png"
            im = PIL.Image.open(icon_path)
            photo = PIL.ImageTk.PhotoImage(im, master=root)
            root.iconphoto(True, photo)

        return root

    def __apply_theme(self, theme_color: str):
        button_text = None
        self.theme.apply_theme(self.style, self.root, theme_color)
        if theme_color == "light":
            button_text = SUN
        else:
            button_text = MOON
        try:
            self.change_theme_button.config(text=button_text)
        except Exception:
            pass

    def __find_all_widgets(
        self, widget: tkinter.Widget, widget_classes: Union[Type[tkinter.Widget], Tuple[Type[tkinter.Widget], ...]]
    ) -> List[tkinter.Widget]:
        """Return a list of all widgets of given type(s) in the widget hierarchy."""
        res = []
        if isinstance(widget, widget_classes):
            res.append(widget)
        for child in widget.winfo_children():
            res.extend(self.__find_all_widgets(child, widget_classes))
        return res

    def __on_close(self):
        self.release_desktop()
        self.root.destroy()

    @property
    def browse_button(self) -> tkinter.Widget:
        """Return the browse button."""
        res = self.root.nametowidget("browse_button")
        return res

    @property
    def desktop(self) -> Desktop:
        """Return the AEDT Desktop instance."""
        if self.__desktop is None:
            self.__desktop = Desktop(
                new_desktop=False,
                version=get_aedt_version(),
                port=get_port(),
                aedt_process_id=get_process_id(),
                student_version=is_student(),
            )
        return self.__desktop

    @property
    def aedt_application(self):
        """Return the active AEDT application instance."""
        if self.__aedt_application is None:
            active_project = self.desktop.active_project()
            active_design = self.desktop.active_design()
            if active_project is None:
                raise AEDTRuntimeError(
                    "No active project found. Please open or create a project before running this extension."
                )

            project_name = active_project.GetName()
            if active_design.GetDesignType() == "HFSS 3D Layout Design":
                design_name = active_design.GetDesignName()
            else:
                design_name = active_design.GetName()

            self.__aedt_application = get_pyaedt_app(project_name, design_name)
        return self.__aedt_application

    def release_desktop(self):
        """Release AEDT desktop instance."""
        if self.__desktop is not None and "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            self.desktop.release_desktop(False, False)
        return True

    @property
    def data(self) -> Optional[ExtensionCommonData]:
        return self.__data

    @data.setter
    def data(self, value: ExtensionCommonData):
        if not isinstance(value, ExtensionCommonData):
            raise TypeError(f"Expected ExtensionCommonData, got {type(value)}")
        self.__data = value

    @property
    def active_project_name(self) -> str:
        """Return the name of the active project."""
        res = NO_ACTIVE_PROJECT
        active_project = self.desktop.active_project()
        if active_project:
            res = active_project.GetName()
        return res

    @abstractmethod
    def add_extension_content(self):
        """Add content to the extension UI.

        This method should be implemented by subclasses to add specific content
        to the extension UI.
        """
        raise NotImplementedError("Subclasses must implement this method.")


def create_default_ui(title, withdraw=False):
    import tkinter
    from tkinter import ttk
    from tkinter.messagebox import showerror

    import PIL.Image
    import PIL.ImageTk

    import ansys.aedt.core.extensions
    from ansys.aedt.core.extensions.misc import ExtensionTheme

    def report_callback_exception(self, exc, val, tb):
        showerror("Error", message=str(val))

    def report_callback_exception_withdraw(self, exc, val, tb):
        raise val

    if withdraw:
        tkinter.Tk.report_callback_exception = report_callback_exception_withdraw
    else:
        tkinter.Tk.report_callback_exception = report_callback_exception

    root = tkinter.Tk()

    if withdraw:
        root.withdraw()
    root.title(title)

    if not withdraw:
        # Load the logo for the main window
        icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo.png"
        im = PIL.Image.open(icon_path)
        photo = PIL.ImageTk.PhotoImage(im, master=root)

        # Set the icon for the main window
        root.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    theme = ExtensionTheme()

    # Apply light theme initially
    theme.apply_light_theme(style)
    root.theme = "light"

    return root, theme, style


def get_arguments(args=None, description=""):  # pragma: no cover
    """Get extension arguments."""
    output_args = {"is_batch": False, "is_test": False}

    if len(sys.argv) != 1:  # pragma: no cover
        try:
            parsed_args = __parse_arguments(args, description)
            output_args["is_batch"] = True
            for k, v in parsed_args.__dict__.items():
                if v is not None:
                    output_args[k] = __string_to_bool(v)
        except SystemExit as e:
            print(f"Argument parsing failed: {e}")
            raise
    return output_args


class ExtensionTheme:  # pragma: no cover
    def __init__(self):
        # Set default font
        self.default_font = ("Arial", 12)

    def apply_theme(self, style, root, theme_color: str):
        """Apply the specified theme, sourcing the tcl file if needed."""
        from pathlib import Path

        import ansys.aedt.core.extensions

        available_themes = style.theme_names()
        theme_file = "light-theme" if theme_color == "light" else "dark-theme"
        if theme_file not in available_themes:
            root.tk.call(
                "source",
                str(Path(ansys.aedt.core.extensions.__path__[0]) / "theme" / f"{theme_file}.tcl"),
            )
        bg_color = "#313131" if theme_color == "dark" else "#ffffff"
        root.configure(bg=bg_color)
        style.theme_use(theme_file)
        root.theme = theme_color

    def apply_light_theme(self, style):
        """Apply light theme."""
        style.theme_use("light-theme")

    def apply_dark_theme(self, style):
        """Apply dark theme."""
        style.theme_use("dark-theme")


def __string_to_bool(v):  # pragma: no cover
    """Change string to bool."""
    if isinstance(v, str) and v.lower() in ("true", "1"):
        v = True
    elif isinstance(v, str) and v.lower() in ("false", "0"):
        v = False
    return v


def __parse_arguments(args=None, description=""):  # pragma: no cover
    """Parse arguments."""
    parser = argparse.ArgumentParser(description=description)
    if args:
        for arg in args:
            parser.add_argument(f"--{arg}", default=args[arg])
    parsed_args = parser.parse_args()
    return parsed_args
