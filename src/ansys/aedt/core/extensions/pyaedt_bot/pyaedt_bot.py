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

import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import Menu

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.file_utils import read_toml


def get_base_dir():
    """Determine the base directory for resources depending on whether running as PyInstaller executable or as a
    script."""
    if getattr(sys, "frozen", False):
        # Running from PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running from source
        return Path(__file__).resolve().parent


def get_extensions_dir():
    """Determine the location of the extension directory."""
    if getattr(sys, "frozen", False):
        # In PyInstaller, use relative path based on known structure inside dist/
        return Path(sys._MEIPASS).parents[1] / "pyaedt_bot" / "_internal" / "ansys" / "aedt" / "core" / "extensions"
    else:
        # In development, go up to project root
        return Path(__file__).resolve().parents[6] / "src" / "ansys" / "aedt" / "core" / "extensions"


VENV_DIR_PREFIX = ".pyaedt_env"


class PyAEDTBot(tk.Tk):
    def __init__(self):
        super().__init__()

        self.base_dir = get_base_dir()
        self.extensions_dir = get_extensions_dir()

        # Load icon for the bot
        icon_path = self.base_dir / "assets" / "bot.png"
        self.icon_image = tk.PhotoImage(file=icon_path)

        # Load config file from environment or default
        self.config_path = os.environ.get("PyAEDT_BOT_CONFIG")
        if self.config_path is None or not Path(self.config_path).is_file():
            self.config_path = self.base_dir / "assets" / "config.toml"
        else:
            self.config_path = Path(self.config_path)

        if self.config_path.is_file():
            self.config = read_toml(self.config_path)
        else:
            raise FileNotFoundError(f"{self.config_path} not found.")

        default_interpreter = Path(os.environ["APPDATA"]) / VENV_DIR_PREFIX / "3_10" / "Scripts" / "python.exe"

        self.python_interpreter = Path(sys.executable)

        if "python.exe" not in str(self.python_interpreter):
            self.python_interpreter = default_interpreter

        local_interpreter = self.config.get("interpreter", None)
        if local_interpreter:
            self.python_interpreter = Path(local_interpreter)

        # Window setup
        self.overrideredirect(True)
        self.geometry("+100+100")
        self.configure(bg="white")
        self.attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "white")

        self._offset_x = 0
        self._offset_y = 0

        # Display icon as draggable bot
        self.icon_label = tk.Label(self, image=self.icon_image, bg="white", bd=0)
        self.icon_label.pack()
        self.icon_label.bind("<Button-1>", self.start_move)
        self.icon_label.bind("<B1-Motion>", self.move_icon)

        # Right-click context menu
        self.menu = Menu(self, tearoff=0)
        self.load_menu()
        self.icon_label.bind("<Button-3>", self.show_menu)

    def start_move(self, event):
        """Start moving the window."""
        self._offset_x = event.x
        self._offset_y = event.y

    def move_icon(self, event):
        """Move the icon according to mouse motion."""
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        """Display the context menu on right click."""
        self.menu.tk_popup(event.x_root, event.y_root)

    def load_menu(self):
        """Load the context menu from the TOML configuration."""

        for extension_type, extensions in self.config.items():
            if isinstance(extensions, dict):
                submenu = Menu(self.menu, tearoff=0)
                for key, extension_data in extensions.items():
                    name = extension_data.get("name", key)
                    script = extension_data.get("script")
                    if not script:
                        continue

                    script_path = Path(script)
                    if not script_path.is_file():
                        script_path = self.extensions_dir / script_path

                    submenu.add_command(label=name, command=lambda s=script_path: self.launch_extension(s))
                self.menu.add_cascade(label=extension_type, menu=submenu)

        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.destroy)

    def launch_extension(self, script_path):
        """Launch an extension script using the Python interpreter."""
        logger.info(f"Launching {script_path}")
        logger.info(f"Using interpreter: {self.python_interpreter}")
        if not script_path.is_file():
            logger.error(f"{script_path} not found.")
            raise FileNotFoundError(f"{script_path} not found.")
        subprocess.Popen([self.python_interpreter, str(script_path)], shell=True)


if __name__ == "__main__":
    app = PyAEDTBot()
    app.mainloop()
