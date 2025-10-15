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
import logging
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
import requests

from ansys.aedt.core import Desktop
from ansys.aedt.core.base import PyAedtBase
import ansys.aedt.core.extensions
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.generic.general_methods import active_sessions
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.errors import AEDTRuntimeError

NO_ACTIVE_PROJECT = "No active project"
NO_ACTIVE_DESIGN = "No active design"
MOON = "\u2600"
SUN = "\u263d"
DEFAULT_PADDING = {"padx": 15, "pady": 10}
DEFAULT_WIDTH = 10
DEFAULT_FOREGROUND: str = "white"
DEFAULT_FOREGROUND_DARK: str = "black"
DEFAULT_BD: int = 1
DEFAULT_BORDERWIDTH: int = 1


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


def get_latest_version(package_name, timeout=3):
    """Return latest version string from PyPI or 'Unknown' on failure."""
    UNKNOWN_VERSION = "Unknown"
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return data.get("info", {}).get("version", UNKNOWN_VERSION)
        return UNKNOWN_VERSION
    except Exception:
        return UNKNOWN_VERSION


def check_for_pyaedt_update(personallib: str) -> Tuple[Optional[str], Optional[Path]]:
    """Check PyPI for a newer PyAEDT release and whether the user should be prompted.

    Returns
    -------
    tuple[str | None, pathlib.Path | None]
        (latest_version, declined_file_path) if the UI should prompt the user,
        otherwise (None, None).
    """

    def compare_versions(local: str, remote: str) -> bool:
        """Return True if local < remote (very loose numeric comparison)."""

        def to_tuple(v: str):
            out = []
            # Remove dev/rc suffixes and split by dots
            version_clean = v.split("dev")[0].split("rc")[0]
            for token in version_clean.split("."):
                try:
                    out.append(int(token))
                except Exception:  # pragma: no cover
                    break
            return tuple(out)

        try:
            return to_tuple(local) < to_tuple(remote)
        except Exception:  # pragma: no cover
            return False

    def read_version_file(file_path: Path) -> Tuple[Optional[str], bool]:
        """Read version file and return (last_known_version, show_updates).

        File format:
        Line 1: last known version
        Line 2: show_updates preference ("true" or "false")
        """
        if not file_path.is_file():
            return None, True  # First start - don't show popup

        try:
            content = file_path.read_text(encoding="utf-8").strip()
            lines = content.split("\n")
            if len(lines) >= 2:
                last_version = lines[0].strip()
                show_updates = lines[1].strip().lower() == "true"
                return last_version, show_updates
            elif len(lines) == 1:
                # Legacy format - only version, assume user wants updates
                return lines[0].strip(), True
            else:  # pragma: no cover
                return None, True
        except Exception:  # pragma: no cover
            return None, True

    def write_version_file(file_path: Path, version: str, show_updates: bool):
        """Write version and preference to file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = f"{version}\n{str(show_updates).lower()}"
            file_path.write_text(content, encoding="utf-8")
        except Exception:  # pragma: no cover
            log.debug("PyAEDT update check: failed to write version file.", exc_info=True)

    log = logging.getLogger("Global")

    # Get current PyAEDT version
    try:
        from ansys.aedt.core import __version__ as current_version
    except ImportError:  # pragma: no cover
        log.debug("PyAEDT update check: could not import version.")
        return None, None

    latest = get_latest_version("pyaedt")
    if not latest or latest == "Unknown":
        log.debug("PyAEDT update check: latest version unavailable.")
        return None, None

    # Resolve user toolkit directory
    try:
        toolkit_dir = Path(personallib) / "Toolkits"
    except Exception:  # pragma: no cover
        log.debug("PyAEDT update check: personal lib path not found.", exc_info=True)
        return None, None

    version_file = toolkit_dir / ".pyaedt_version"
    last_known_version, show_updates = read_version_file(version_file)

    # If this is first start (no file exists), record the latest known release
    # (not the installed version) so we won't prompt until a newer release appears.
    if last_known_version is None:
        write_version_file(version_file, latest, False)
        log.debug("PyAEDT update check: first start, recording latest release.")
        return None, None

    # If the user already has the latest version installed, never show the popup.
    if current_version == latest:  # pragma: no cover
        if last_known_version != latest:
            write_version_file(version_file, latest, False)
        return None, None

    # Check if there's a newer version available compared to installed package
    has_newer_version = compare_versions(current_version, latest)

    if not has_newer_version:
        if last_known_version != latest:
            write_version_file(version_file, latest, show_updates)
        return None, None
    version_changed = compare_versions(last_known_version, latest)
    prompt_user = show_updates or version_changed

    if not prompt_user:
        return None, None

    return latest, version_file


@dataclass
class ExtensionCommonData(PyAedtBase):
    """Data class containing user input and computed data."""


class ExtensionCommon(PyAedtBase):
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

        Parameters
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
        self.root.protocol("WM_DELETE_WINDOW", self.__on_close)
        self.style: ttk.Style = ttk.Style()
        self.theme: ExtensionTheme = ExtensionTheme()
        self._widgets = {}
        self.__desktop = None
        self.__aedt_application = None
        self.__data: Optional[ExtensionCommonData] = None
        self._widgets["log_widget"] = None
        self._widgets["button_frame"] = None

        self.__apply_theme(theme_color)
        if toggle_row is not None and toggle_column is not None:
            self.add_toggle_theme_button(self.root, toggle_row, toggle_column)
        if add_custom_content:
            self.add_extension_content()

        self.check_design_type()

    def add_toggle_theme_button(self, parent, toggle_row, toggle_column):
        """Create a button to toggle between light and dark themes."""
        button_frame = ttk.Frame(
            parent,
            style="PyAEDT.TFrame",
            relief=tkinter.SUNKEN,
            borderwidth=2,
            name="theme_button_frame",
        )
        button_frame.grid(
            row=toggle_row,
            column=toggle_column,
            sticky="e",
            **DEFAULT_PADDING,
        )
        self._widgets["button_frame"] = button_frame

        change_theme_button = ttk.Button(
            button_frame,
            width=DEFAULT_WIDTH,
            text=SUN,
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        change_theme_button.grid(row=0, column=0)
        self._widgets["change_theme_button"] = change_theme_button

    def add_logger(self, parent, row, column):
        logger_frame = ttk.Frame(parent, style="PyAEDT.TFrame", name="logger_frame")
        logger_frame.grid(row=row, column=column, sticky="ew", **DEFAULT_PADDING)
        self._widgets["logger_frame"] = logger_frame

        # Configure grid so text expands and button stays to the right
        logger_frame.grid_columnconfigure(0, weight=1)

        log_text = tkinter.Text(
            self._widgets["logger_frame"],
            height=2,
            width=80,
            name="log_text_widget",
        )
        log_text.configure(
            bg=self.theme.light["pane_bg"],
            foreground=self.theme.light["text"],
            font=self.theme.default_font,
        )
        log_text.grid(
            row=0,
            column=0,
            padx=(10, 5),
            pady=5,
            sticky="nsew",
        )
        log_text.configure(state="disabled")  # Make it read-only
        self._widgets["log_text_widget"] = log_text

        # Add "Show logs" button
        all_logs_btn = ttk.Button(
            logger_frame,
            text="Show logs",
            style="PyAEDT.TButton",
            command=self.open_all_logs_window,
            width=12,
            name="all_logs_button",
        )
        all_logs_btn.grid(
            row=0,
            column=1,
            padx=(5, 10),
            pady=5,
            sticky="e",
        )
        self._widgets["all_logs_button"] = all_logs_btn

        self.log_message("Welcome to the PyAEDT Extension Manager!")

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.root.theme == "light":
            self.__apply_theme("dark")
        elif self.root.theme == "dark":
            self.__apply_theme("light")
        else:  # pragma: no cover
            raise ValueError(f"Unknown theme: {self.root.theme}. Use 'light' or 'dark'.")

    def log_message(self, message: str):
        """Append a message to the log text box."""
        if self._widgets["log_text_widget"]:
            widget = self._widgets["log_text_widget"]
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("end", message + "\n")
            widget.configure(state="disabled")

    def __init_root(self, title: str, withdraw: bool) -> tkinter.Tk:
        """Init Tk root window with error handling and icon."""

        def report_callback_exception(self, exc, val, tb):
            """Custom exception showing an error message."""
            if not val:
                val = "An error occurred when using the extension."
            showerror("Error", message=f"{val}")

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
        for widget in self.__find_all_widgets(
            self.root,
            (tkinter.Text, tkinter.Listbox, tkinter.Scrollbar),
        ):
            if isinstance(widget, tkinter.Text):
                widget.configure(
                    background=theme_colors_dict["pane_bg"],
                    foreground=theme_colors_dict["text"],
                    font=self.theme.default_font,
                )
            elif isinstance(widget, tkinter.Listbox):
                widget.configure(
                    background=theme_colors_dict["widget_bg"],
                    foreground=theme_colors_dict["text"],
                    font=self.theme.default_font,
                )
            elif isinstance(widget, tkinter.Canvas):
                widget.configure(
                    background=theme_colors_dict["pane_bg"],
                    highlightbackground=theme_colors_dict["tab_border"],
                    highlightcolor=theme_colors_dict["tab_border"],
                )
            else:
                if "background" in widget.keys():
                    widget.configure(background=self.theme.light["widget_bg"])

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
        self,
        widget: tkinter.Widget,
        widget_classes: Union[Type[tkinter.Widget], Tuple[Type[tkinter.Widget], ...]],
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
            # Extensions for now should only work in graphical sessions and with an existing AEDT session
            version = get_aedt_version()
            aedt_active_sessions = active_sessions(
                version=version,
                student_version=False,
                non_graphical=False,
            )
            student_active_sessions = active_sessions(
                version=version,
                student_version=True,
                non_graphical=False,
            )

            if not aedt_active_sessions and not student_active_sessions:
                raise AEDTRuntimeError(f"AEDT {version} session not found. Launch AEDT and try again.")

            self.__desktop = Desktop(
                new_desktop=False,
                version=version,
                port=get_port(),
                aedt_process_id=get_process_id(),
                student_version=is_student(),
                close_on_exit=False,
            )
        return self.__desktop

    @property
    def aedt_application(self):
        """Return the active AEDT application instance."""
        if self.__aedt_application is None:
            active_project_name = self.active_project_name
            if active_project_name == NO_ACTIVE_PROJECT:
                self.release_desktop()
                raise AEDTRuntimeError(
                    "No active project found. Please open or create a project before running this extension."
                )
            active_design_name = self.active_design_name
            if active_design_name == NO_ACTIVE_DESIGN:
                self.release_desktop()
                raise AEDTRuntimeError(
                    "No active design found. Please open or create a design before running this extension."
                )
            self.__aedt_application = get_pyaedt_app(active_project_name, active_design_name)
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

    @property
    def active_design_name(self) -> str:
        """Return the name of the active design."""
        design_list = self.desktop.design_list(self.active_project_name)
        active_design = None
        if design_list:
            active_design = self.desktop.active_design()
        if not active_design:
            return NO_ACTIVE_DESIGN
        match active_design.GetDesignType():
            case "HFSS 3D Layout Design":
                res = active_design.GetDesignName()
            case "Circuit Design":
                res = active_design.GetName().split(";")[1]
            case "Twin Builder":
                res = active_design.GetName().split(";")[1]
            case _:
                res = active_design.GetName()
        return res

    @abstractmethod
    def add_extension_content(self):
        """Add content to the extension UI.

        This method should be implemented by subclasses to add specific content
        to the extension UI.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def check_design_type(self):
        """Check the design type.

        This method should be implemented by subclasses to add specific content
        to the extension UI.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class ExtensionIcepakCommon(ExtensionCommon):
    """Common methods for Icepak extensions."""

    def check_design_type(self):
        """Check if the active design is an Icepak design."""
        if self.aedt_application.design_type != "Icepak":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with Icepak designs.")


class ExtensionHFSSCommon(ExtensionCommon):
    """Common methods for HFSS extensions."""

    def check_design_type(self):
        """Check if the active design is an HFSS design."""
        if self.aedt_application.design_type != "HFSS":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with HFSS designs.")


class ExtensionHFSS3DLayoutCommon(ExtensionCommon):
    """Common methods for HFSS 3D Layout extensions."""

    def check_design_type(self):
        """Check if the active design is an HFSS 3D Layout design."""
        if self.aedt_application.design_type != "HFSS 3D Layout Design":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with HFSS 3D Layout designs.")


class ExtensionMaxwell2DCommon(ExtensionCommon):
    """Common methods for Maxwell 2D extensions."""

    def check_design_type(self):
        """Check if the active design is a Maxwell 2D design."""
        if self.aedt_application.design_type != "Maxwell 2D":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with Maxwell 2D designs.")


class ExtensionMaxwell3DCommon(ExtensionCommon):
    """Common methods for Maxwell 3D extensions."""

    def check_design_type(self):
        """Check if the active design is a Maxwell 3D design."""
        if self.aedt_application.design_type != "Maxwell 3D":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with Maxwell 3D designs.")


class ExtensionCircuitCommon(ExtensionCommon):
    """Common methods for Circuit extensions."""

    def check_design_type(self):
        """Check if the active design is an Circuit design."""
        if self.aedt_application.design_type != "Circuit Design":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with Circuit designs.")


class ExtensionTwinBuilderCommon(ExtensionCommon):
    """Common methods for TwinBuilder extensions."""

    def check_design_type(self):
        """Check if the active design is a TwinBuilder design."""
        if self.aedt_application.design_type != "Twin Builder":
            self.release_desktop()
            raise AEDTRuntimeError("This extension can only be used with Twin Builder designs.")


class ExtensionProjectCommon(ExtensionCommon):
    """Common methods for project-level extensions."""

    def check_design_type(self):
        """Check the active design type.

        Not required for extension at project level.
        """
        pass


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


class ExtensionTheme(PyAedtBase):  # pragma: no cover
    def __init__(self):
        # Define light and dark theme colors
        self.light = {
            "widget_bg": "#FFFFFF",
            "text": "#000000",
            "button_bg": "#E6E6E6",
            "button_hover_bg": "#D9D9D9",
            "button_active_bg": "#B8B8B8",
            "button_border": "#B0B0B0",
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
            "button_bg": "#45494A",
            "button_hover_bg": "#5A5E5F",
            "button_active_bg": "#6A6E6F",
            "button_border": "#918E8E",
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
            "PyAEDT.TButton",
            background=colors["button_bg"],
            foreground=colors["text"],
            bd=DEFAULT_BD,
            borderwidth=DEFAULT_BORDERWIDTH,
            relief="solid",
            focuscolor="none",
            highlightthickness=0,
            font=self.default_font,
            anchor="center",
            padding=(8, 4),
        )

        # Apply the color for hover and active states
        style.map(
            "PyAEDT.TButton",
            background=[
                ("active", colors["button_active_bg"]),
                ("!active", colors["button_hover_bg"]),
            ],
            foreground=[
                ("active", colors["text"]),
                ("!active", colors["text"]),
            ],
            bordercolor=[
                ("active", colors["button_border"]),
                ("!active", colors["button_border"]),
            ],
        )

        # Apply the color for hover and active states

        # Apply the colors and font to the style for Frames
        style.configure(
            "PyAEDT.TFrame",
            background=colors["widget_bg"],
            borderwidth=0,
            relief="flat",
            font=self.default_font,
        )

        # Apply the colors and font to the style for Tabs
        style.configure(
            "TNotebook",
            background=colors["tab_bg_inactive"],
            bordercolor=colors["tab_border"],
            font=self.default_font,
        )
        style.configure(
            "TNotebook.Tab",
            background=colors["tab_bg_inactive"],
            foreground=colors["text"],
            font=self.default_font,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", colors["tab_bg_active"])],
        )

        # Apply the colors and font to the style for Labels
        style.configure(
            "PyAEDT.TLabel",
            background=colors["label_bg"],
            foreground=colors["label_fg"],
            font=self.default_font,
        )

        # Apply the colors and font to the style for LabelFrames
        style.configure(
            "PyAEDT.TLabelframe",
            background=colors["labelframe_bg"],
            foreground=colors["labelframe_fg"],
            font=self.default_font,
        )
        style.configure(
            "PyAEDT.TLabelframe.Label",  # Style for title text
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
            background=[
                ("selected", colors["radiobutton_selected"]),
                ("!selected", colors["radiobutton_unselected"]),
            ],
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
        action_button_font = ("Arial", 10)

        # Success button style (green for adding the shortcut)
        style.configure(
            "PyAEDT.Success.TButton",
            background="#28a745",  # Green
            foreground=DEFAULT_FOREGROUND,
            bd=DEFAULT_BD,
            borderwidth=DEFAULT_BORDERWIDTH,
            relief="solid",
            focuscolor="none",
            highlightthickness=0,
            font=action_button_font,
            anchor="center",
            padding=(8, 4),
        )
        style.map(
            "PyAEDT.Success.TButton",
            background=[
                ("active", "#218838"),
                ("!active", "#28a745"),
            ],
            foreground=[("active", "white"), ("!active", "white")],
        )

        # Danger button style (red for removing the shortcut)
        style.configure(
            "PyAEDT.Danger.TButton",
            background="#dc3545",  # Red
            foreground=DEFAULT_FOREGROUND,
            bd=DEFAULT_BD,
            borderwidth=DEFAULT_BORDERWIDTH,
            relief="solid",
            focuscolor="none",
            highlightthickness=0,
            font=action_button_font,
            anchor="center",
            padding=(8, 4),
        )
        style.map(
            "PyAEDT.Danger.TButton",
            background=[
                ("active", "#c82333"),
                ("!active", "#dc3545"),
            ],
            foreground=[("active", "white"), ("!active", "white")],
        )

        # Web button style
        style.configure(
            "PyAEDT.ActionWeb.TButton",
            bd=DEFAULT_BD,
            borderwidth=DEFAULT_BORDERWIDTH,
            relief="solid",
            focuscolor="none",
            highlightthickness=0,
            font=action_button_font,
            anchor="center",
            padding=(8, 4),
        )

        # Launch button style (ANSYS dark yellow)
        style.configure(
            "PyAEDT.ActionLaunch.TButton",
            background="#F3C767",  # ANSYS dark yellow
            foreground=DEFAULT_FOREGROUND_DARK,
            bd=DEFAULT_BD,
            borderwidth=DEFAULT_BORDERWIDTH,
            relief="solid",
            focuscolor="none",
            highlightthickness=0,
            font=action_button_font,
            anchor="center",
            padding=(8, 4),
        )
        style.map(
            "PyAEDT.ActionLaunch.TButton",
            background=[
                (
                    "active",
                    "#E6A600",
                ),  # Slightly darker yellow for active
                ("!active", "#F3C767"),
            ],
            foreground=[("active", "black"), ("!active", "black")],
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


class ToolTip:
    """Create a tooltip for a given widget."""

    def __init__(self, widget, text="Widget info"):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None

    def enter(self, event=None):
        """Show tooltip on mouse enter."""
        self.show_tooltip()

    def leave(self, event=None):
        """Hide tooltip on mouse leave."""
        self.hide_tooltip()

    def show_tooltip(self):  # pragma: no cover
        """Display tooltip."""
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tkinter.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tkinter.Label(
            tw,
            text=self.text,
            justify=tkinter.LEFT,
            background="#ffffe0",
            relief=tkinter.SOLID,
            borderwidth=1,
            font=("Arial", 9, "normal"),
        )
        label.pack(ipadx=1)

    def hide_tooltip(self):  # pragma: no cover
        """Hide tooltip."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def decline_pyaedt_update(declined_file_path: Path, latest_version: str):
    """Record that the user declined the update notification."""
    try:
        declined_file_path.parent.mkdir(parents=True, exist_ok=True)
        if latest_version is None:
            return
        content = f"{latest_version}\nfalse"
        declined_file_path.write_text(content, encoding="utf-8")
    except Exception:  # pragma: no cover
        logging.getLogger("Global").debug("Failed to write declined update file", exc_info=True)
