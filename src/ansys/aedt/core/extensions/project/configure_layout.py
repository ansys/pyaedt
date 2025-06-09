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
from pyedb import Edb

from ansys.aedt.core.extensions.project.configure_edb import ConfigureEdbBackend as LegacyBackend
from ansys.aedt.core.generic.file_utils import generate_unique_name


PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

GRID_PARAMS = {"padx": 10, "pady": 10}
EXTENSION_TITLE = "Extension template"

EXPORT_DIR = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
EXPORT_DIR.mkdir()


class CfgConfigureLayout:  # pragma: no cover
    def __init__(self, file_path: Union[Path, str]):
        with open(file_path, "rb") as f:
            data = tomli.load(f)
        self.title = data["title"]
        self.version = data["version"]
        self.layout_file = Path(data["layout_file"])
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
class ExtensionData:  # pragma: no cover
    """Data class containing user input."""

    example_master_config: Path = Path(
        __file__).parent / "resources" / "configure_layout" / "example_serdes.toml"
    example_slave_config: Path = Path(
        __file__).parent / "resources" / "configure_layout" / "example_serdes_supplementary.json"

    control_ini: Path = Path(__file__).parent / "resources" / "configure_layout" / "control.ini"


class TabApplyConfig:  # pragma: no cover
    def __init__(self, master_ui):
        self.master_ui = master_ui
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

        new_aedb = ConfigureLayoutBackend.apply_config(config=cfg, export_directory=EXPORT_DIR)

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


class TabExportConfigFromDesign:  # pragma: no cover
    def __init__(self, master_ui):
        self.master_ui = master_ui

    def create_ui(self, master):
        row = 0
        b = ttk.Button(
            master,
            text="Export Config File",
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


class TabLegacy:  # pragma: no cover
    app_options = ["Active Design", "HFSS 3D Layout", "SIwave"]
    _execute = {
        "active_load": [],
        "siwave_load": [],
        "aedt_load": [],
        "active_export": [],
        "siwave_export": [],
        "aedt_export": [],
    }

    def get_active_project_info(self):
        desktop = self.desktop
        active_project = desktop.active_project()
        if active_project:
            project_name = active_project.GetName()
            project_dir = active_project.GetPath()
            project_file = os.path.join(project_dir, project_name + ".aedt")
            desktop.release_desktop(False, False)
            return project_file
        else:
            desktop.release_desktop(False, False)
            return

    @property
    def desktop(self):
        return ansys.aedt.core.Desktop(
            new_desktop_session=False,
            specified_version=VERSION,
            port=PORT,
            aedt_process_id=AEDT_PROCESS_ID,
            student_version=IS_STUDENT,
        )

    def __init__(self, master_ui):
        self.master_ui = master_ui

        self.status = tkinter.StringVar(value="")
        self.selected_app_option = tkinter.StringVar(value="Active Design")
        self.selected_project_file_path = ""
        self.selected_project_file = tkinter.StringVar(value="")
        self.selected_cfg_file_folder = tkinter.StringVar(value="")

    def create_ui(self, master):

        # Section 1
        # self.label_version = ttk.Label(self, text=f"AEDT {version}")
        # self.label_version.grid(row=0, column=0)
        # label = ttk.Label(self, textvariable=self.status)
        # label.grid(row=0, column=1)

        # Section 2
        s2_start_row = 1
        for index, option in enumerate(self.app_options):
            ttk.Radiobutton(master, text=option, value=option, variable=self.selected_app_option).grid(
                row=index + s2_start_row, column=0, sticky=tkinter.W
            )

        # Section 3
        s3_start_row = 4
        button_select_project_file = ttk.Button(
            master, text="Select project file", width=30, command=self.call_select_project,
            style="PyAEDT.TButton",
        )
        button_select_project_file.grid(row=s3_start_row, column=0)

        # SIwave
        label_project_file = tkinter.Label(master, width=30, height=1, textvariable=self.selected_project_file)
        label_project_file.grid(row=s3_start_row + 1, column=0)

        # Apply cfg
        button = ttk.Button(
            master, text="Select and Apply Configuration", width=30, command=self.call_apply_cfg_file,
            style="PyAEDT.TButton",
        )
        button.grid(row=s3_start_row + 3, column=0)

        # Export cfg
        button = ttk.Button(master, text="Export Configuration", width=30, command=self.call_export_cfg,
                            style="PyAEDT.TButton",)
        button.grid(row=s3_start_row + 4, column=0)

    def call_select_project(self):
        if self.selected_app_option.get() == "HFSS 3D Layout":
            file_path = filedialog.askopenfilename(
                initialdir="/",
                title="Select File",
                filetypes=(("Electronics Desktop", "*.aedt"), ("Electronics Database", "*.def")),
            )
        elif self.selected_app_option.get() == "SIwave":
            file_path = filedialog.askopenfilename(
                initialdir="/",
                title="Select File",
                filetypes=(("SIwave project", "*.siw"), ("Electronics Database", "*.def")),
            )
        else:
            file_path = None

        if not file_path:
            return
        else:
            if file_path.endswith(".def"):
                file_path = Path(file_path).parent
            self.selected_project_file_path = file_path
            self.selected_project_file.set(Path(file_path).parts[-1])

    def _call_apply_cfg_file(self):
        if not self.selected_app_option.get() == "Active Design":
            if not self.selected_project_file_path:
                return

        init_dir = Path(self.selected_project_file_path).parent if self.selected_project_file_path else "/"
        file_cfg_path = filedialog.askopenfilename(
            initialdir=init_dir,
            title="Select Configuration File",
            filetypes=(("json file", "*.json"), ("toml", "*.toml")),
            defaultextension=".json",
        )

        if not file_cfg_path:
            return

        if self.selected_app_option.get() == "SIwave":
            project_file = self.selected_project_file_path
            file_save_path = filedialog.asksaveasfilename(
                initialdir=init_dir,
                title="Save new project as",
                filetypes=[("SIwave", "*.siw")],
                defaultextension=".siw",
            )
            if not file_save_path:
                return
            self._execute["siwave_load"].append(
                {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
            )
            # self.execute_load_cfg_siw(project_file, file_cfg_path, file_save_path)
        elif self.selected_app_option.get() == "HFSS 3D Layout":
            project_file = self.selected_project_file_path
            file_save_path = filedialog.asksaveasfilename(
                initialdir=init_dir,
                title="Save new project as",
                filetypes=[("Electronics Desktop", "*.aedt")],
                defaultextension=".aedt",
            )
            self._execute["aedt_load"].append(
                {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
            )
            # self.execute_load_cfg_aedt(project_file, file_cfg_path, file_save_path)
        else:
            data = self.get_active_project_info()
            if data:
                project_dir, project_file = data
            else:
                return
            file_save_path = os.path.join(
                project_dir, Path(project_file).stem + "_" + generate_unique_name(Path(file_cfg_path).stem) + ".aedt"
            )
            self._execute["active_load"].append(
                {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
            )
        self.execute()

    def call_select_cfg_folder(self):
        pass

    def call_apply_cfg_file(self):
        init_dir = Path(self.selected_project_file_path).parent if self.selected_project_file_path else "/"
        # Get original project file path
        if self.selected_app_option.get() == "Active Design":
            project_file = self.get_active_project_info()
            if not project_file:
                return
        else:
            project_file = self.selected_project_file_path

        # Get cfg files
        cfg_files = filedialog.askopenfilenames(
            initialdir=init_dir,
            title="Select Configuration",
            filetypes=(("json file", "*.json"), ("toml", "*.toml")),
            defaultextension=".json",
        )
        if not cfg_files:
            return

        file_save_dir = filedialog.askdirectory(
            initialdir=init_dir,
            title="Save new projects to",
        )

        for file_cfg_path in cfg_files:
            fname = Path(project_file).stem + "_" + generate_unique_name(Path(file_cfg_path).stem)
            if file_cfg_path.endswith(".json") or file_cfg_path.endswith(".toml"):
                if self.selected_app_option.get() == "SIwave":
                    file_save_path = os.path.join(Path(file_save_dir), fname + ".siw")
                    self._execute["siwave_load"].append(
                        {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
                    )
                elif self.selected_app_option.get() == "HFSS 3D Layout":
                    file_save_path = os.path.join(Path(file_save_dir), fname + ".aedt")
                    self._execute["aedt_load"].append(
                        {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
                    )
                else:
                    file_save_path = os.path.join(file_save_dir, fname + ".aedt")
                    self._execute["active_load"].append(
                        {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
                    )
        self.execute_load()

    def call_export_cfg(self):
        """Export configuration file."""
        init_dir = Path(self.selected_project_file_path).parent
        file_path_save = filedialog.asksaveasfilename(
            initialdir=init_dir,
            title="Select Configuration File",
            filetypes=(("json file", "*.json"), ("toml", "*.toml")),
            defaultextension=".json",
        )
        if not file_path_save:
            return

        if self.selected_app_option.get() == "SIwave":
            self._execute["siwave_export"].append(
                {"project_file": self.selected_project_file_path, "file_path_save": file_path_save}
            )
        elif self.selected_app_option.get() == "HFSS 3D Layout":
            self._execute["aedt_export"].append(
                {"project_file": self.selected_project_file_path, "file_path_save": file_path_save}
            )
        elif self.selected_app_option.get() == "Active Design":
            data = self.get_active_project_info()
            if data:
                project_file = data
                self._execute["active_export"].append({"project_file": project_file, "file_path_save": file_path_save})
            else:
                return

        self.execute_export(file_path_save)

    def execute(self):
        LegacyBackend(self._execute)
        self._execute = {
            "active_load": [],
            "siwave_load": [],
            "aedt_load": [],
            "active_export": [],
            "siwave_export": [],
            "aedt_export": [],
        }

    def execute_load(self):
        if self.selected_app_option.get() == "Active Design":
            desktop = self.desktop
            self.execute()
            desktop.release_desktop(False, False)
        else:
            self.execute()
        messagebox.showinfo("Information", "Done!")

    def execute_export(self, file_path):
        LegacyBackend(self._execute)
        self._execute = {
            "active_load": [],
            "siwave_load": [],
            "aedt_load": [],
            "active_export": [],
            "siwave_export": [],
            "aedt_export": [],
        }
        messagebox.showinfo("Information", f"Configuration file saved to {file_path}.")


class ConfigureLayout(ExtensionCommon):  # pragma: no cover

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
            "Legacy": TabLegacy
        }
        for tab_name, tab_class in tabs.items():
            tab = ttk.Frame(nb, style="PyAEDT.TFrame")
            nb.add(tab, text=tab_name)
            sub_ui = tab_class(self)
            sub_ui.create_ui(tab)
        nb.grid(row=0, column=0, sticky="e", **GRID_PARAMS)


class ConfigureLayoutBackend:  # pragma: no cover
    def __init__(self):
        pass

    @staticmethod
    def apply_config(config: Union[CfgConfigureLayout, str, Path], export_directory: Union[Path, str]):
        if isinstance(config, CfgConfigureLayout):
            config = config
        else:
            config = CfgConfigureLayout(config)

        app = Edb(edbpath=str(config.layout_file), edbversion=config.version)

        cfg = config.get_edb_config_dict(app)

        if config.supplementary_json != "":
            app.configuration.load(config.supplementary_json)
        app.configuration.load(cfg)

        app.configuration.run()

        new_aedb = Path(export_directory) / Path(app.edbpath).name
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
        control = control if isinstance(control, dict) else toml.load(control)
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
        ConfigureLayoutBackend.export_control(export_control_file_as, extension_data.control_ini)

    if load_config:
        if master_config_file == "" or not Path(master_config_file).exists():
            raise
        else:
            ConfigureLayoutBackend.apply_config(master_config_file, export_directory)

    if export_config_from_design:
        if export_directory == "" or not Path(export_directory).exists():
            raise
        elif control_file == "" or not Path(control_file).exists():
            raise
        else:
            ConfigureLayoutBackend.export_config(control_file, export_directory)


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments()
    result = ExtensionData()

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        extension: ExtensionCommon = ConfigureLayout(withdraw=False)

        tkinter.mainloop()

    else:
        main(**args)
