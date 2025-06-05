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
from typing import Union
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk

import tomli

import ansys.aedt.core
from pyedb import Edb
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student


class FrontendBase:

    port = 0
    version = ""
    aedt_process_id = 0
    student_version = False

    class TabBase:
        GRID_PARAMS = {"padx": 15, "pady": 10}

        icon_path = Path()

        def __init__(self, master_ui):
            self.master_ui = master_ui

            self.open_in_3d_layout = tk.BooleanVar()

            self.open_in_3d_layout.set(True)

        def create_ui(self, master):
            pass

    def __init__(self, tabs: dict, title, is_test=False):
        self.title = title
        self.master = None
        if is_test is False:
            self.create_ui(tabs)

    def create_ui(self, tabs: dict):
        # Create UI
        self.master = tk.Tk()
        master = self.master
        master.geometry()
        master.title(self.title)

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
        self.port = get_port()
        self.version = get_aedt_version()
        self.aedt_process_id = get_process_id()
        self.student_version = is_student()
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


class CfgConfigureLayout:
    def __init__(self, file_path: Union[Path, str]):
        with open(file_path, "rb") as f:
            data = tomli.load(f)
        self.title = data["title"]
        self.version = data["version"]
        self.layout_file = Path(data["layout_file"])
        self.output_dir = Path(data["output_dir"])
        self.rlc_to_ports = data.get("rlc_to_ports", [])
        self.edb_config = data["edb_config"]

        supplementary_json = data.get("supplementary_json", "")
        if supplementary_json != "":
            self.supplementary_json = str(file_path.with_name(supplementary_json))
        else:
            self.supplementary_json = ""
        self.check()

    def check(self):
        if not self.layout_file.exists() or str(self.layout_file) == "":
            raise
        elif self.layout_file.suffix == ".aedt":
            self.layout_file = self.layout_file.with_suffix(".aedb")

        if str(self.output_dir) == "TEMP":
            self.output_dir = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
            self.output_dir.mkdir()
        elif not self.output_dir.exists():
            raise

    def get_edb_config_dict(self, edb: Edb):
        edb_config = dict(self.edb_config)

        # RLC
        cfg_components = []
        cfg_ports = []
        for i in self.rlc_to_ports:
            comp = edb.components[i]
            p1, p2 = list(comp.pins.keys())
            cfg_port = {
                "name": f"port_{comp.name}",
                "type": "circuit",
                "reference_designator": comp.name,
                "positive_terminal": {"pin": p1},
                "negative_terminal": {"pin": p2},
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


class ConfigureLayoutFrontend(FrontendBase):  # pragma: no cover

    class TabLoad(FrontendBase.TabBase):

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
                    title="Select Configuration",
                    filetypes=(("toml", "*.toml"),),
                    defaultextension=".toml",
                )
            else:
                file_path_toml = file_path

            if not file_path_toml:
                return
            else:
                file_path_toml = Path(file_path_toml)
                cfg = CfgConfigureLayout(file_path=file_path_toml)
                cfg.version = self.master_ui.version

                backend = ConfigureLayoutBackend(config=cfg)

                h3d = self.launch_h3d(backend.new_aedb)

                return h3d.release_desktop(close_projects=False, close_desktop=False)

        @staticmethod
        def call_back_export_example_cfg():

            write_dir = filedialog.askdirectory(
                title="Save to"
            )
            write_dir = Path(write_dir)

            if write_dir:
                example_dir = Path(__file__).parent / "resources" / "configure_layout"
                for fname in ["example_serdes.toml", "example_serdes_supplementary.json"]:
                    with open(example_dir / fname, "r", encoding="utf-8") as file:
                        config_string = file.read()

                    with open(write_dir / fname, "w", encoding="utf-8") as f:
                        f.write(config_string)

        def launch_h3d(self, fpath_aedb):
            h3d = ansys.aedt.core.Hfss3dLayout(project=str(fpath_aedb),
                                               version=self.master_ui.version,
                                               port=self.master_ui.port,
                                               aedt_process_id=self.master_ui.aedt_process_id,
                                               student_version=self.master_ui.student_version,
                                               )
            return h3d

    class TabExport(FrontendBase.TabBase):

        def __init__(self, master):
            super().__init__(master)

        def create_ui(self, master):
            row = 0
            b = ttk.Button(
                master,
                text="Export",
                command=self.export,
                style="PyAEDT.TButton",
                width=30,
            )
            b.grid(row=row, column=0, **self.GRID_PARAMS)

            row = row + 1
            b = ttk.Button(
                master,
                text="Export Template",
                command=self.call_back_export_template,
                style="PyAEDT.TButton",
                width=30,
            )
            b.grid(row=row, column=0, **self.GRID_PARAMS)

        def export(self, file_path_input=None, file_path_output=None):
            if file_path_input is None:
                file_path_input = filedialog.askopenfilename(
                    title="Select",
                    filetypes=(("toml", "*.toml"),),
                    defaultextension=".toml",
                )
            if file_path_input:
                file_path_input = Path(file_path_input)
            else:
                return

            if file_path_output is None:
                file_path_output = filedialog.asksaveasfilename(
                    initialfile="config.json",
                    title="Save",
                    filetypes=(("json", "*.json"),),
                    defaultextension=".json",
                )
                if file_path_output:
                    file_path_output = Path(file_path_output)
                else:
                    return

                with open(file_path_input, "rb") as f:
                    data = tomli.load(f)
                layout_file = Path(data.pop("layout_file"))
                if not layout_file.exists() or str(layout_file) == "":
                    raise
                elif layout_file.suffix == ".aedt":
                    layout_file = layout_file.with_suffix(".aedb")

                app = Edb(edbpath=str(layout_file), edbversion=self.master_ui.version)
                config_dict = app.configuration.get_data_from_db(
                    **data
                )
                with open(file_path_output, "w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=4)
                messagebox.showinfo("Message", "Done")

        @staticmethod
        def call_back_export_template(file_path=None):
            if file_path is None:
                file_path = filedialog.asksaveasfilename(
                    initialfile="export_template.toml",
                    title="Select Configuration",
                    filetypes=(("toml", "*.toml"),),
                    defaultextension=".toml",
                )
            if file_path:
                file_path = Path(file_path)
            else:
                return

            template_file = Path(__file__).parent / "resources" / "configure_layout" / "export_template.toml"
            with open(template_file, "r", encoding="utf-8") as file:
                config_string = file.read()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(config_string)

    def __init__(self, is_test=False):
        tabs = {
            "Load": self.TabLoad,
            "Export": self.TabExport,
        }
        super().__init__(tabs, "Configure Layout", is_test)


class ConfigureLayoutBackend:
    def __init__(self, config: Union[CfgConfigureLayout, str, Path]):
        if isinstance(config, CfgConfigureLayout):
            self.config = config
        else:
            self.config = CfgConfigureLayout(config)

        self.app = Edb(edbpath=str(self.config.layout_file), edbversion=self.config.version)

        cfg = self.config.get_edb_config_dict(self.app)
        file_json = self.config.output_dir / "edb_config.json"
        with open(file_json, "w") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)

        if self.config.supplementary_json != "":
            self.app.configuration.load(self.config.supplementary_json)
        self.app.configuration.load(cfg)

        self.app.configuration.run()

        self.new_aedb = Path(self.config.output_dir) / Path(self.app.edbpath).name
        self.app.save_edb_as(str(self.new_aedb))
        self.app.close()


def main(is_test=False):  # pragma: no cover
    if is_test:
        config = Path(__file__).parent / "resources" / "configure_layout" / "example_serdes.toml"
        backend = ConfigureLayoutBackend(config)
        return backend.new_aedb
    else:
        app = ConfigureLayoutFrontend()
        app.launch()


if __name__ == "__main__":  # pragma: no cover
    main()
