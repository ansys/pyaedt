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
import json
# Extension template to help get started

from dataclasses import asdict
from dataclasses import dataclass
import os
from pathlib import Path
import tkinter
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import Union

import toml
import tomli
import tempfile

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from pyedb import Edb

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

GRID_PARAMS = {"padx": 10, "pady": 10}
EXTENSION_TITLE = "Extension template"


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


@dataclass
class ExtensionData:
    """Data class containing user input."""

    example_master_config: Path = Path(
        __file__).parent / "resources" / "configure_layout" / "example_serdes.toml"
    example_slave_config: Path = Path(
        __file__).parent / "resources" / "configure_layout" / "example_serdes_supplementary.json"

    control_ini: Path = Path(__file__).parent / "resources" / "configure_layout" / "control.ini"


class TabBase:
    icon_path = Path()

    def __init__(self, master_ui):
        self.master_ui = master_ui

        self.open_in_3d_layout = tkinter.BooleanVar()

        self.open_in_3d_layout.set(True)

    def create_ui(self, master):
        pass


class TabApplyConfig(TabBase):
    def create_ui(self, master):
        row = 0
        b = ttk.Button(
            master,
            text="Apply Config file",
            command=self.apply_config_file,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=row, column=0, **GRID_PARAMS)

        row = row + 1
        b = ttk.Button(
            master,
            text="Export Example Config file",
            command=self.export_example_cfg,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=row, column=0, **GRID_PARAMS)

    @staticmethod
    def apply_config_file():
        file_path = filedialog.askopenfilename(
            title="Select Configuration",
            filetypes=(("toml", "*.toml"),),
            defaultextension=".toml",
        )
        if not file_path:
            return

        file_path = Path(file_path)
        cfg = CfgConfigureLayout(file_path=file_path)
        cfg.version = VERSION

        new_aedb = ConfigureLayoutBackend.apply_config(config=cfg)

        app = ansys.aedt.core.Hfss3dLayout(
            project=str(new_aedb),
            version=VERSION,
            port=PORT,
            aedt_process_id=AEDT_PROCESS_ID,
            student_version=IS_STUDENT,
        )

        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        return True

    @staticmethod
    def export_example_cfg(export_directory=""):
        if export_directory == "":
            write_dir = filedialog.askdirectory(title="Save to")
            if write_dir:
                write_dir = Path(write_dir)
            else:
                return
        else:
            write_dir = Path(export_directory)
        if ConfigureLayoutBackend.export_example_config(write_dir, result.example_master_config,
                                                        result.example_slave_config):
            messagebox.showinfo("Message", "Done")
        else:
            raise


class TabExportConfigFromDesign(TabBase):
    def __init__(self, master):
        super().__init__(master)

    def create_ui(self, master):
        row = 0
        b = ttk.Button(
            master,
            text="Export",
            command=self.export_config_from_design,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=row, column=0, **GRID_PARAMS)

        row = row + 1
        b = ttk.Button(
            master,
            text="Export Control File",
            command=self.export_control_file,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=row, column=0, **GRID_PARAMS)

    @staticmethod
    def export_config_from_design(ini="", export_directory=""):
        if ini == "":
            export_ini = filedialog.askopenfilename(
                title="Select",
                filetypes=(("ini", "*.ini"),),
                defaultextension=".ini",
            )
            if export_ini:
                export_ini = Path(export_ini)
            else:
                return
        else:
            export_ini = Path(ini)

        if export_directory == "":
            export_directory = filedialog.askdirectory(title="Save to")
            if export_directory:
                export_directory = Path(export_directory)
            else:
                return
        else:
            export_directory = Path(export_directory)

        with open(export_ini, "rb") as file:
            control = tomli.load(file)

        if ConfigureLayoutBackend.export_config(control, export_directory):
            messagebox.showinfo("Message", "Done")
        else:
            raise

    @staticmethod
    def export_control_file(save_as=""):
        if save_as == "":
            file_path = filedialog.asksaveasfilename(
                initialfile="export_config.ini",
                title="Select Configuration",
                filetypes=(("ini", "*.ini"),),
                defaultextension=".ini",
            )
            if file_path:
                file_path = Path(file_path)
            else:
                return
        else:
            file_path = Path(save_as)

        file_path = Path(file_path)
        if ConfigureLayoutBackend.export_control(file_path, result.control_ini):
            messagebox.showinfo("Message", "Done")
        else:
            raise


class ConfigureLayout(ExtensionCommon):

    def __init__(self, withdraw: bool = False):
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_extension_content(self):
        nb = ttk.Notebook(self.root, style="PyAEDT.TNotebook", width=400)

        tabs = {
            "Load": TabApplyConfig,
            "Export": TabExportConfigFromDesign,
        }
        for tab_name, tab_class in tabs.items():
            tab = ttk.Frame(nb, style="PyAEDT.TFrame")
            nb.add(tab, text=tab_name)
            sub_ui = tab_class(self)
            sub_ui.create_ui(tab)
        nb.grid(row=0, column=0, sticky="e", **GRID_PARAMS)


class ConfigureLayoutBackend:
    def __init__(self):
        pass

    @staticmethod
    def apply_config(config: Union[CfgConfigureLayout, str, Path]):
        if isinstance(config, CfgConfigureLayout):
            config = config
        else:
            config = CfgConfigureLayout(config)

        app = Edb(edbpath=str(config.layout_file), edbversion=config.version)

        cfg = config.get_edb_config_dict(app)
        file_json = config.output_dir / "edb_config.json"
        with open(file_json, "w") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)

        if config.supplementary_json != "":
            app.configuration.load(config.supplementary_json)
        app.configuration.load(cfg)

        app.configuration.run()

        new_aedb = Path(config.output_dir) / Path(app.edbpath).name
        app.save_edb_as(str(new_aedb))
        app.close()
        return new_aedb

    @staticmethod
    def export_example_config(export_directory, example_master_config, example_slave_config):
        export_directory = Path(export_directory)
        with open(example_master_config, "r", encoding="utf-8") as file:
            content = file.read()
        with open(export_directory / example_master_config.name, "w", encoding="utf-8") as f:
            f.write(content)

        with open(example_slave_config, "r", encoding="utf-8") as file:
            content = file.read()
        with open(export_directory / example_slave_config.name, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    @staticmethod
    def export_config(control, export_directory):
        export_directory = Path(export_directory)

        layout_file = Path(control["layout_file"])
        if not layout_file.exists() or str(layout_file) == "":
            raise
        elif layout_file.suffix == ".aedt":
            layout_aedb = layout_file.with_suffix(".aedb")
        else:
            layout_aedb = layout_file

        app: Edb = Edb(edbpath=str(layout_aedb), edbversion=VERSION)
        config_dict = app.configuration.get_data_from_db(**control["Export"])
        app.close_edb()

        toml_name = layout_file.with_suffix(".toml").name
        json_name = layout_file.with_suffix(".json").name
        config_master = {
            "title": layout_file.stem,
            "version": VERSION,
            "layout_file": str(layout_file),
            "output_dir": "TEMP",
            "supplementary_json": json_name,
            "rlc_to_ports": [],
            "edb_config": {
                "ports": [],
                "setups": []
            }
        }
        with open(export_directory / toml_name, "w", encoding="utf-8") as f:
            toml.dump(config_master, f)

        with open(export_directory / json_name, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True

    @staticmethod
    def export_control(export_as, control_ini):
        with open(control_ini, "r", encoding="utf-8") as file:
            config_string = file.read()
        with open(export_as, "w", encoding="utf-8") as f:
            f.write(config_string)
        return True


def main(
        export_example_layout_config=False,
        load_config=False,
        export_control=False,
        export_config_from_design=False,
        export_directory="",
        master_config_file="",
        export_control_file_as="",
        control_file="",
):
    extension_data = ExtensionData()

    if export_example_layout_config:
        if export_directory == "" or not Path(export_directory).exists():
            raise
        else:
            ConfigureLayoutBackend.export_example_config(export_directory, extension_data.example_master_config,
                                                         extension_data.example_slave_config)

    if export_control:
        if export_directory == "" or not Path(export_directory).exists():
            raise
        elif export_control_file_as == "" or not Path(export_control_file_as).exists():
            raise
        else:
            ConfigureLayoutBackend.export_control(export_control_file_as, export_directory)

    if load_config:
        if master_config_file == "" or not Path(master_config_file).exists():
            raise
        else:
            ConfigureLayoutBackend.apply_config(master_config_file)

    if export_config_from_design:
        if export_directory == "" or not Path(export_directory).exists():
            raise
        elif control_file == "" or not Path(control_file).exists():
            raise
        else:
            ConfigureLayoutBackend.export_config(control_file, export_directory)


if __name__ == "__main__":
    args = get_arguments()
    result = ExtensionData()

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        extension: ExtensionCommon = ConfigureLayout(withdraw=False)

        tkinter.mainloop()

    else:
        main(**args)
