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

from ansys.aedt.core.generic.file_utils import read_toml


class PyAEDTBot(tk.Tk):
    def __init__(self):
        super().__init__()
        icon_name = "bot.png"
        script_root = Path(__file__)
        self.script_dir = script_root.parent
        icon_path = self.script_dir / icon_name

        self.config_path = os.environ.get("PyAEDT_BOT_CONFIG", None)
        if self.config_path is None:
            self.config_path = self.script_dir / "config.toml"
        else:
            self.config_path = Path(self.config_path)

        self.extensions_dir = self.script_dir.parent

        self.overrideredirect(True)
        self.geometry("+100+100")
        self.configure(bg="white")
        self.attributes("-topmost", True)

        self.wm_attributes("-transparentcolor", "white")

        self._offset_x = 0
        self._offset_y = 0

        self.icon_image = tk.PhotoImage(file=icon_path)
        self.icon_label = tk.Label(self, image=self.icon_image, bg="white", bd=0)
        self.icon_label.pack()

        self.icon_label.bind("<Button-1>", self.start_move)
        self.icon_label.bind("<B1-Motion>", self.move_icon)

        self.menu = Menu(self, tearoff=0)
        self.load_menu()
        self.icon_label.bind("<Button-3>", self.show_menu)

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def move_icon(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def load_menu(self):
        if not self.config_path.is_file():  # pragma: no cover
            raise FileNotFoundError(f"{self.config_path} not found.")

        config = read_toml(self.config_path)

        for extension_type, extensions in config.items():
            submenu = Menu(self.menu, tearoff=0)
            for key, extension_data in extensions.items():
                nombre = extension_data.get("name", key)
                script = extension_data.get("script", None)
                if not script:
                    continue
                script_path = Path(script)
                if not script_path.is_file():
                    script_path = self.extensions_dir / script_path

                submenu.add_command(label=nombre, command=lambda s=script_path: self.launch_extension(s))
            self.menu.add_cascade(label=extension_type, menu=submenu)

        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.destroy)

    @staticmethod
    def launch_extension(script_path):
        if not script_path.is_file():
            raise FileNotFoundError(f"{script_path} not found.")
        subprocess.Popen([sys.executable, str(script_path)], shell=True)


if __name__ == "__main__":
    app = PyAEDTBot()
    app.mainloop()
