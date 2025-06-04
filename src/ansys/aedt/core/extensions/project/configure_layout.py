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
import json
# Extension template to help get started

import tempfile
from copy import deepcopy as copy
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk

import toml

import ansys.aedt.core
from pyedb import Edb
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()


class FrontendBase:
    IS_TEST = False

    class TabBase:
        GRID_PARAMS = {"padx": 15, "pady": 10}

        icon_path = Path()
        fpath_config = ""

        def __init__(self, master_ui):
            self.master_ui = master_ui

            self.open_in_3d_layout = tk.BooleanVar()

            self.open_in_3d_layout.set(True)

        def create_ui(self, master):
            pass

    def __init__(self, tabs: dict):
        # Load initial configuration

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

        for tab_name, tab_class in tabs.items():

            tab = ttk.Frame(nb, style="PyAEDT.TFrame")
            nb.add(tab, text=tab_name)
            sub_ui = tab_class(self)
            sub_ui.create_ui(tab)

        main_frame.add(nb, weight=1)

        # Lower panel
        lower_frame = ttk.Frame(master, style="PyAEDT.TFrame")
        main_frame.add(lower_frame, weight=3)

        grid_params = {"padx": 15, "pady": 10}

        row = 0

        """b = ttk.Button(lower_frame, text="Create Design", command=self.callback, style="PyAEDT.TButton", width=30)
        b.grid(row=row, column=0, **grid_params, sticky="w")"""

        self.change_theme_button = ttk.Button(
            lower_frame, text="\u263d", width=2, command=self.toggle_theme, style="PyAEDT.TButton"
        )
        self.change_theme_button.grid(row=row, column=1, **grid_params, sticky="e")

        self.toggle_theme()

    def launch(self):
        self.master.mainloop()

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

    def callback(self, **kwargs):
        return kwargs


class ConfigureLayoutFrontend(FrontendBase):  # pragma: no cover

    class TabLoad(FrontendBase.TabBase):
        fpath_config = Path(__file__).parent / "resources" / "via_design" / "package_diff.toml"

        def create_ui(self, master):

            row = 0
            b = ttk.Button(
                master,
                text="Apply Config file",
                command=self.apply_config_file,
                style="PyAEDT.TButton",
                width=30,
            )
            b.grid(row=row, column=0, **self.GRID_PARAMS)

            row = row + 1
            b = ttk.Button(
                master,
                text="Export Example Config file",
                command=self.call_back_export_example_cfg,
                style="PyAEDT.TButton",
                width=30,
            )
            b.grid(row=row, column=0, **self.GRID_PARAMS)

        def apply_config_file(self, file_path=None):
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
                config = toml.load(file_path_toml)
                backend = ConfigureLayoutBackend(design_config=config)
                backend.launch_h3d()
                if self.IS_TEST:
                    return True
                else:
                    return h3d.release_desktop(close_projects=False, close_desktop=False)

        def call_back_export_example_cfg(self):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".toml", filetypes=[("TOML File", "*.toml"), ("All Files", "*.*")], title="Save As"
            )
            if file_path:
                with open(self.fpath_config, "r", encoding="utf-8") as file:
                    config_string = file.read()

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(config_string)

    class TabExport(FrontendBase.TabBase):
        fpath_config = Path(__file__).parent / "resources" / "via_design" / "pcb_diff.toml"

    def __init__(self):
        tabs = {
            "Load": self.TabLoad,
            "Export": self.TabExport,
        }
        super().__init__(tabs)


class ConfigureLayoutBackend:
    _OUTPUT_DIR = None

    @property
    def layout_file(self):
        layout_file = Path(self.config["layout_file"])
        if self.config.get("demo"):
            layout_file = Path(__file__).parent.parent / "project_data" / layout_file

        if layout_file.exists():
            return layout_file
        else:
            raise

    @property
    def output_dir(self):
        if self._OUTPUT_DIR is None:
            output_dir = self.config["output_dir"]
            if output_dir == "":
                self._OUTPUT_DIR = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
            else:
                self._OUTPUT_DIR = Path(output_dir)
        return self._OUTPUT_DIR

    def __init__(self, design_config, json_config=None):
        config = toml.load(design_config)
        self.config = config
        self.version = config["version"]

        self.app = Edb(edbpath=self.layout_file, edbversion=self.version)

        cfg = self.parser()
        self.app.configuration.load(cfg)
        self.app.configuration.run()

        if json_config is not None:
            self.app.configuration.load(json_config, append=False)
            self.app.configuration.run()

        new_edb_dir = self.output_dir / Path(self.app.edbpath).name
        self.app.save_edb_as(str(new_edb_dir))
        self.app.close()

        self.cfg = cfg

    def dump_config_file(self, file_format="json"):
        if file_format == "json":
            file_json = self.output_dir / "config.json"
            with open(file_json, "w") as f:
                json.dump(self.cfg, f, indent=4, ensure_ascii=False)
        elif file_format == "toml":
            file_toml = self.output_dir / "config.toml"
            with open(file_toml, "w") as f:
                toml.dump(self.cfg, f)

    def parser(self):
        edb_config = copy(self.config["EDB_Config"])

        # RLC
        cfg_components = []
        cfg_ports = []
        for i in self.config.get("rlc_to_ports", []):
            comp = self.app.components[i]
            p1, p2 = list(comp.pins.values())
            cfg_port = {
                "name": f"port_{comp.name}",
                "type": "circuit",
                "positive_terminal": {"padstack": p1.aedt_name},
                "negative_terminal": {"padstack": p2.aedt_name},
            }
            cfg_ports.append(cfg_port)

            cfg_comp = {
                "enabled": False,
                "reference_designator": comp.name,
            }
            cfg_components.append(cfg_comp)
        if "ports" in edb_config:
            edb_config["ports"].extend(cfg_ports)
        else:
            edb_config["ports"] = cfg_ports
        if "components" in edb_config:
            edb_config["components"].extend(cfg_components)
        else:
            edb_config["components"] = cfg_components

        return edb_config

    def launch_h3d(self, is_test=False):
        h3d = ansys.aedt.core.Hfss3dLayout(project=self.app.edbpath, version=self.version)
        h3d.release_desktop(False, False)


def main(is_test=False, **kwargs):  # pragma: no cover
    ConfigureLayoutFrontend.IS_TEST = True if is_test else False
    app = ConfigureLayoutFrontend()
    if is_test:
        app.callback(file_path=kwargs["file_path"], output_dir=kwargs["output_dir"])
    else:
        app.launch()


if __name__ == "__main__":  # pragma: no cover
    main()
