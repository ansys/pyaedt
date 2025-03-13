# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

import argparse
import os
import sys

from ansys.aedt.core.generic.aedt_versions import aedt_versions


def get_process_id():
    """Get process ID from environment variable."""
    aedt_process_id = None
    if os.getenv("PYAEDT_SCRIPT_PROCESS_ID", None):  # pragma: no cover
        aedt_process_id = int(os.getenv("PYAEDT_SCRIPT_PROCESS_ID"))
    return aedt_process_id


def get_port():
    """Get gRPC port from environment variable."""
    port = 0
    if "PYAEDT_SCRIPT_PORT" in os.environ:
        port = int(os.environ["PYAEDT_SCRIPT_PORT"])
    return port


def get_aedt_version():
    """Get AEDT release from environment variable."""
    version = aedt_versions.current_version
    if "PYAEDT_SCRIPT_VERSION" in os.environ:
        version = os.environ["PYAEDT_SCRIPT_VERSION"]
    return version


def is_student():
    """Get if AEDT student is opened from environment variable."""
    student_version = False
    if "PYAEDT_STUDENT_VERSION" in os.environ:  # pragma: no cover
        student_version = False if os.environ["PYAEDT_STUDENT_VERSION"] == "False" else True
    return student_version


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
