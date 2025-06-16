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

# Extension template to help get started

from copy import deepcopy as copy
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk
from pyedb.extensions.via_design_backend import ViaDesignBackend
import toml

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()


class ViaDesignFrontend:  # pragma: no cover
    IS_TEST = False

    class TabBase:
        icon_path = Path()
        fpath_config = ""

        def __init__(self, master_ui):
            self.master_ui = master_ui

            resource_dir = Path(__file__).parent / "resources" / "via_design"
            self.examples = [
                {"pic": resource_dir / "via_design_rf.png", "fpath": resource_dir / "pcb_rf.toml",
                 "callback": self.callback_rf},
                {"pic": resource_dir / "via_design_pcb_diff.png", "fpath": resource_dir / "pcb_diff.toml",
                 "callback": self.callback_pcb},
                {"pic": resource_dir / "via_design_pkg_diff.png", "fpath": resource_dir / "package_diff.toml",
                 "callback": self.callback_pkg},
            ]

        def create_ui(self, master):
            grid_params = {"padx": 15, "pady": 10}

            row = 0
            col = 0
            for i in self.examples:
                pic = i["pic"]
                callback = i["callback"]

                img = PIL.Image.open(pic)
                img = img.resize((100, 100))
                photo = PIL.ImageTk.PhotoImage(img)

                b = ttk.Button(
                    master,
                    command=callback,
                    style="PyAEDT.TButton",
                    image=photo,
                    width=20,
                )
                b.image = photo
                b.grid(row=row, column=col, **grid_params)
                if col == 4:
                    row = row + 1
                    col = 0
                else:
                    col += 1

        def callback_rf(self):
            self.callback_export_example_cfg(self.examples[0]["fpath"])

        def callback_pcb(self):
            self.callback_export_example_cfg(self.examples[1]["fpath"])

        def callback_pkg(self):
            self.callback_export_example_cfg(self.examples[2]["fpath"])

        @staticmethod
        def callback_export_example_cfg(src_file_path):
            file_path = filedialog.asksaveasfilename(
                initialfile=src_file_path.name,
                defaultextension=".toml", filetypes=[("TOML File", "*.toml"), ("All Files", "*.*")], title="Save As"
            )
            if file_path:
                with open(src_file_path, "r", encoding="utf-8") as file:
                    config_string = file.read()

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(config_string)

    def __init__(self):
        self.master = None
        # Load initial configuration

    def launch(self):
        # Create UI
        self.master = tk.Tk()
        master = self.master
        master.geometry()
        master.title("Via Design Beta")

        # Detect if user close the UI
        master.flag = False

        # Load the logo for the main window
        icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo.png"
        im = PIL.Image.open(icon_path)
        photo = PIL.ImageTk.PhotoImage(im)

        # Set the icon for the main window
        master.iconphoto(True, photo)

        # Configure style for ttk buttons
        self.style = ttk.Style()
        self.theme = ExtensionTheme()

        self.theme.apply_light_theme(self.style)
        master.theme = "light"

        # Set background color of the window (optional)
        master.configure(bg=self.theme.light["widget_bg"])
        # Create buttons to create sphere and change theme color

        # Main panel
        main_frame = ttk.PanedWindow(master, orient=tk.VERTICAL, style="TPanedwindow")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Upper panel
        nb = ttk.Notebook(master, style="PyAEDT.TNotebook")

        # Tab 1
        tab = ttk.Frame(nb, style="PyAEDT.TFrame")
        nb.add(tab, text="Examples")
        sub_ui = self.TabBase(self)
        sub_ui.create_ui(tab)

        main_frame.add(nb, weight=1)

        # Lower panel
        lower_frame = ttk.Frame(master, style="PyAEDT.TFrame")
        main_frame.add(lower_frame, weight=3)

        grid_params = {"padx": 15, "pady": 10}

        row = 0
        b = ttk.Button(lower_frame, text="Create Design", command=self.callback, style="PyAEDT.TButton", width=30)
        b.grid(row=row, column=0, **grid_params, sticky="w")

        self.change_theme_button = ttk.Button(
            lower_frame, text="\u263d", width=2, command=self.toggle_theme, style="PyAEDT.TButton"
        )
        self.change_theme_button.grid(row=row, column=1, **grid_params, sticky="e")

        self.set_dark_theme()
        self.master.mainloop()

    def callback(self, file_path=None, output_dir=""):
        # Get cfg files
        if file_path is None:
            file_path_toml = filedialog.askopenfilename(
                # initialdir=init_dir,
                title="Select Configuration",
                filetypes=(("toml", "*.toml"),),
                defaultextension=".toml",
            )
        else:
            file_path_toml = file_path

        if not file_path_toml:
            return
        else:
            config_toml = dict(toml.load(file_path_toml))
            config = copy(config_toml)
            stacked_vias = config.pop("stacked_vias")

            for name, s in config["signals"].items():
                stacked_vias_name = s["stacked_vias"]
                config["signals"][name]["stacked_vias"] = stacked_vias[stacked_vias_name]

            for name, s in config["differential_signals"].items():
                stacked_vias_name = s["stacked_vias"]
                config["differential_signals"][name]["stacked_vias"] = stacked_vias[stacked_vias_name]

            if self.IS_TEST:
                config["general"]["output_dir"] = output_dir

            backend = ViaDesignBackend(config)
            h3d = ansys.aedt.core.Hfss3dLayout(
                project=backend.app.edbpath,
                version=version,
                port=port,
                aedt_process_id=aedt_process_id,
                student_version=is_student,
            )

            if self.IS_TEST:
                return True
            else:
                return h3d.release_desktop(close_projects=False, close_desktop=False)

    def toggle_theme(self):
        master = self.master
        if master.theme == "light":
            self.set_dark_theme()
            master.theme = "dark"
        else:
            self.set_light_theme()
            master.theme = "light"

    def set_light_theme(self):
        self.master.configure(bg=self.theme.light["widget_bg"])
        self.theme.apply_light_theme(self.style)
        self.change_theme_button.config(text="\u263d")

    def set_dark_theme(self):
        self.master.configure(bg=self.theme.dark["widget_bg"])
        self.theme.apply_dark_theme(self.style)
        self.change_theme_button.config(text="\u2600")


def main(is_test=False, **kwargs):  # pragma: no cover
    ViaDesignFrontend.IS_TEST = True if is_test else False
    app = ViaDesignFrontend()
    if is_test:
        app.callback(file_path=kwargs["file_path"], output_dir=kwargs["output_dir"])
    else:
        app.launch()


if __name__ == "__main__":  # pragma: no cover
    main()
