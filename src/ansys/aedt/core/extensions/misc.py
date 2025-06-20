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
        toggle_row: Optional[int] = None,
        toggle_column: Optional[int] = None,
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
        toggle_row : int, optional
            The row index where the toggle button will be placed.
        toggle_column : int, optional
            The column index where the toggle button will be placed.
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
        if toggle_row is not None and toggle_column is not None:
            self.add_toggle_theme_button(toggle_row=toggle_row, toggle_column=toggle_column)
        if add_custom_content:
            self.add_extension_content()

        self.root.protocol("WM_DELETE_WINDOW", self.__on_close)

    def add_toggle_theme_button(self, toggle_row, toggle_column):
        """Create a button to toggle between light and dark themes."""
        button_frame = ttk.Frame(
            self.root, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2, name="theme_button_frame"
        )
        button_frame.grid(row=toggle_row, column=toggle_column, sticky="e", padx=10, pady=10)
        change_theme_button = ttk.Button(
            button_frame,
            width=20,
            text=SUN,
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        change_theme_button.grid(row=0, column=0)

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
        """Apply a theme to the UI."""
        theme_colors_dict = self.theme.light if theme_color == "light" else self.theme.dark
        self.root.configure(background=theme_colors_dict["widget_bg"])
        for widget in self.__find_all_widgets(self.root, tkinter.Text):
            widget.configure(
                background=theme_colors_dict["pane_bg"],
                foreground=theme_colors_dict["text"],
                font=self.theme.default_font,
            )

        button_text = None
        if theme_color == "light":
            self.theme.apply_light_theme(self.style)
            self.root.theme = "light"
            button_text = SUN
        else:
            self.theme.apply_dark_theme(self.style)
            self.root.theme = "dark"
            button_text = MOON

        try:
            self.change_theme_button.config(text=button_text)
        except KeyError:
            # Handle the case where the button is not yet created
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
    def change_theme_button(self) -> tkinter.Widget:
        """Return the theme toggle button."""
        res = self.root.nametowidget("theme_button_frame.theme_toggle_button")
        return res

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
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
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

    # Set background color of the window (optional)
    root.configure(bg=theme.light["widget_bg"])

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
        # Define light and dark theme colors
        self.light = {
            "widget_bg": "#FFFFFF",
            "text": "#000000",
            "button_bg": "#E6E6E6",
            "button_hover_bg": "#D9D9D9",
            "button_active_bg": "#B8B8B8",
            "tab_bg_inactive": "#F0F0F0",
            "tab_bg_active": "#FFFFFF",
            "tab_border": "#D9D9D9",
            "label_bg": "#FFFFFF",
            "label_fg": "#000000",
            "labelframe_bg": "#FFFFFF",
            "labelframe_fg": "#000000",
            "labelframe_title_bg": "#FFFFFF",  # Background for title (text)
            "labelframe_title_fg": "#000000",  # Text color for title
            "radiobutton_bg": "#FFFFFF",  # Background for Radiobutton
            "radiobutton_fg": "#000000",  # Text color for Radiobutton
            "radiobutton_selected": "#E0E0E0",  # Color when selected
            "radiobutton_unselected": "#FFFFFF",  # Color when unselected
            "pane_bg": "#F0F0F0",  # Background for PanedWindow
            "sash_color": "#C0C0C0",  # Color for sash (separator) in PanedWindow
            "combobox_bg": "#FFFFFF",  # Matches widget_bg
            "combobox_arrow_bg": "#E6E6E6",  # Matches button_bg
            "combobox_arrow_fg": "#000000",  # Matches text
            "combobox_readonly_bg": "#F0F0F0",  # Matches tab_bg_inactive
            "checkbutton_bg": "#FFFFFF",  # Matches widget_bg
            "checkbutton_fg": "#000000",  # Matches text
            "checkbutton_indicator_bg": "#D9D9D9",  # Matches button_hover_bg
            "checkbutton_active_bg": "#B8B8B8",  # Matches button_active_bg
        }

        self.dark = {
            "widget_bg": "#313335",
            "text": "#FFFFFF",
            "button_bg": "#FFFFFF",
            "button_hover_bg": "#606060",
            "button_active_bg": "#808080",
            "tab_bg_inactive": "#313335",
            "tab_bg_active": "#2B2B2B",
            "tab_border": "#3E4042",
            "label_bg": "#313335",  # Background for labels
            "label_fg": "#FFFFFF",  # Text color for labels
            "labelframe_bg": "#313335",  # Background for LabelFrame
            "labelframe_fg": "#FFFFFF",  # Text color for LabelFrame
            "labelframe_title_bg": "#313335",  # Dark background for title (text)
            "labelframe_title_fg": "#FFFFFF",  # Dark text color for title
            "radiobutton_bg": "#2E2E2E",  # Background for Radiobutton
            "radiobutton_fg": "#FFFFFF",  # Text color for Radiobutton
            "radiobutton_selected": "#45494A",  # Color when selected
            "radiobutton_unselected": "#313335",  # Color when unselected
            "pane_bg": "#2E2E2E",  # Background for PanedWindow
            "combobox_bg": "#313335",  # Matches widget_bg
            "combobox_arrow_bg": "#606060",  # Matches button_hover_bg
            "combobox_arrow_fg": "#FFFFFF",  # Matches text
            "combobox_readonly_bg": "#2E2E2E",  # Matches pane_bg
            "checkbutton_bg": "#313335",  # Matches widget_bg
            "checkbutton_fg": "#FFFFFF",  # Matches text
            "checkbutton_indicator_bg": "#2E2E2E",  # Matches pane_bg
            "checkbutton_active_bg": "#45494A",  # Matches radiobutton_selected
        }

        # Set default font
        self.default_font = ("Arial", 12)

    def apply_light_theme(self, style):
        """Apply light theme."""
        self._apply_theme(style, self.light)

    def apply_dark_theme(self, style):
        """Apply dark theme."""
        self._apply_theme(style, self.dark)

    def _apply_theme(self, style, colors):
        # Apply the colors and font to the style
        style.theme_use("clam")

        style.configure("TPanedwindow", background=colors["pane_bg"])

        style.configure(
            "PyAEDT.TButton", background=colors["button_bg"], foreground=colors["text"], font=self.default_font
        )

        # Apply the color for hover and active states
        style.map(
            "PyAEDT.TButton",
            background=[("active", colors["button_active_bg"]), ("!active", colors["button_hover_bg"])],
            foreground=[("active", colors["text"]), ("!active", colors["text"])],
        )

        # Apply the color for hover and active states

        # Apply the colors and font to the style for Frames and Containers
        style.configure("PyAEDT.TFrame", background=colors["widget_bg"], font=self.default_font)

        # Apply the colors and font to the style for Tabs
        style.configure(
            "TNotebook", background=colors["tab_bg_inactive"], bordercolor=colors["tab_border"], font=self.default_font
        )
        style.configure(
            "TNotebook.Tab", background=colors["tab_bg_inactive"], foreground=colors["text"], font=self.default_font
        )
        style.map("TNotebook.Tab", background=[("selected", colors["tab_bg_active"])])

        # Apply the colors and font to the style for Labels
        style.configure(
            "PyAEDT.TLabel", background=colors["label_bg"], foreground=colors["label_fg"], font=self.default_font
        )

        # Apply the colors and font to the style for LabelFrames
        style.configure(
            "PyAEDT.TLabelframe",
            background=colors["labelframe_bg"],
            foreground=colors["labelframe_fg"],
            font=self.default_font,
        )
        style.configure(
            "PyAEDT.TLabelframe.Label",  # Specific style for the title text (label)
            background=colors["labelframe_title_bg"],
            foreground=colors["labelframe_title_fg"],
            font=self.default_font,
        )

        # Apply the colors and font to the style for Radiobuttons
        style.configure(
            "PyAEDT.TRadiobutton",
            background=colors["radiobutton_bg"],
            foreground=colors["radiobutton_fg"],
            font=self.default_font,
        )

        style.map(
            "TRadiobutton",
            background=[("selected", colors["radiobutton_selected"]), ("!selected", colors["radiobutton_unselected"])],
        )

        # Apply the colors and font to the style for Combobox
        style.configure(
            "PyAEDT.TCombobox",
            fieldbackground=colors["combobox_bg"],
            background=colors["combobox_arrow_bg"],
            foreground=colors["text"],
            font=self.default_font,
            arrowcolor=colors["combobox_arrow_fg"],
        )
        style.map(
            "PyAEDT.TCombobox",
            fieldbackground=[("readonly", colors["combobox_readonly_bg"])],
            foreground=[("readonly", colors["text"])],
        )

        # Style for Checkbutton
        style.configure(
            "PyAEDT.TCheckbutton",
            background=colors["checkbutton_bg"],
            foreground=colors["checkbutton_fg"],
            font=self.default_font,
            indicatorcolor=colors["checkbutton_indicator_bg"],
            focuscolor=colors["checkbutton_active_bg"],  # For focus/active state
        )
        style.map(
            "PyAEDT.TCheckbutton",
            background=[("active", colors["checkbutton_active_bg"])],
            indicatorcolor=[("selected", colors["checkbutton_indicator_bg"])],
        )


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
