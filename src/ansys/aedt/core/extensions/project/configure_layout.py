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

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Union
import webbrowser

from pyedb import Edb
import toml

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.generic.file_utils import read_toml
from ansys.aedt.core.generic.file_utils import write_configuration_file
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

EXTENSION_TITLE = "Configure Layout"
GRID_PARAMS = {"padx": 10, "pady": 10}

INTRO_LINK = "https://aedt.docs.pyansys.com/version/dev/User_guide/pyaedt_extensions_doc/project/configure_layout.html"
GUIDE_LINK = "https://examples.aedt.docs.pyansys.com/version/dev/examples/00_edb/use_configuration/index.html"


def get_active_edb():
    desktop = ansys.aedt.core.Desktop(
        new_desktop_session=False,
        specified_version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    active_project = desktop.active_project()
    if active_project:
        project_name = active_project.GetName()
        project_dir = active_project.GetPath()
        aedb_directory = Path(project_dir) / (project_name + ".aedb")
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            desktop.release_desktop(False, False)
    else:  # pragma: no cover
        if "PYTEST_CURRENT_TEST" not in os.environ:
            desktop.release_desktop(False, False)
        raise AEDTRuntimeError("No active design")
    return aedb_directory


class CfgConfigureLayout:
    class LayoutValidation:
        def __init__(self, data):
            self.illegal_rlc_values = data.get("illegal_rlc_values", False)

    def __init__(self, file_path: Union[Path, str]):
        self._file_path = Path(file_path)
        data = read_toml(self._file_path)
        self.title = data["title"]
        self.version = data["version"]
        self.layout_file = Path(data["layout_file"])
        self.rlc_to_ports = data.get("rlc_to_ports", [])
        self.edb_config = data["edb_config"]

        self.layout_validation = self.LayoutValidation(data.get("layout_validation", {}))

        supplementary_json = data.get("supplementary_json", "")
        if supplementary_json != "":
            Path(supplementary_json)
            self.supplementary_json = str(self._file_path.with_name(Path(supplementary_json).name))
        else:  # pragma: no cover
            self.supplementary_json = ""
        self.check()

    def check(self):
        if self.layout_file.suffix == ".aedt":  # pragma: no cover
            self.layout_file = self.layout_file.with_suffix(".aedb")

        if not bool(self.layout_file.drive):
            self.layout_file = self._file_path.parent / self.layout_file

    def get_edb_config_dict(self, edb: Edb):
        edb_config = dict(self.edb_config)

        # RLC
        cfg_components = []
        cfg_ports = []
        for i in self.rlc_to_ports:
            comp = edb.components[i]
            layer = comp.placement_layer
            p1, p2 = list(comp.pins.values())
            cfg_port = {
                "name": f"port_{comp.name}",
                "type": "circuit",
                "positive_terminal": {"coordinates": {"layer": layer, "point": p1.position, "net": p1.net_name}},
                "negative_terminal": {"coordinates": {"layer": layer, "point": p2.position, "net": p2.net_name}},
            }
            cfg_ports.append(cfg_port)

            cfg_comp = {
                "enabled": False,
                "reference_designator": comp.name,
            }
            cfg_components.append(cfg_comp)
        if "ports" in edb_config:
            edb_config["ports"].extend(cfg_ports)
        else:  # pragma: no cover
            edb_config["ports"] = cfg_ports

        if "components" in edb_config:
            edb_config["components"].extend(cfg_components)
        else:  # pragma: no cover
            edb_config["components"] = cfg_components

        return edb_config


@dataclass
class ExtensionDataLoad:
    active_design = True
    overwrite = False


@dataclass
class ExportOptions:
    general = False
    stackup = True
    package_definitions = False
    setups = True
    sources = True
    ports = True
    nets = False
    pin_groups = True
    operations = True
    components = False
    boundaries = False
    s_parameters = False
    padstacks = False


@dataclass
class ExtensionDataExport:
    working_directory = ""
    src_aedb = ""


class TabLoadConfig:
    class TKVars:
        def __init__(self):
            self.load_active_design = tkinter.BooleanVar()
            self.load_overwrite = tkinter.BooleanVar()
            self.init()

        def init(self):
            self.load_active_design.set(ExtensionDataLoad.active_design)
            self.load_overwrite.set(ExtensionDataLoad.overwrite)

    def __init__(self, master_ui):
        self.master_ui = master_ui
        self.tk_vars = self.TKVars()
        self.new_aedb = ""

    def create_ui(self, master):
        row = 0
        b = ttk.Button(
            master,
            name="load_config_file",
            text="Load Config file",
            command=self.call_back_load,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=row, column=0, **GRID_PARAMS)

        row = row + 1
        b = ttk.Button(
            master,
            name="generate_template",
            text="Generate Template",
            command=self.call_back_export_template,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=row, column=0, **GRID_PARAMS)

        row = row + 1
        r = ttk.Checkbutton(
            master,
            name="active_design",
            text="Active Design",
            variable=self.tk_vars.load_active_design,
            style="PyAEDT.TCheckbutton",
        )
        r.grid(row=row, column=0, sticky="w")

        row = row + 1
        r = ttk.Checkbutton(
            master,
            name="overwrite",
            text="Overwrite Design",
            variable=self.tk_vars.load_overwrite,
            style="PyAEDT.TCheckbutton",
        )
        r.grid(row=row, column=0, sticky="w")

    def call_back_load(self):
        file_path = filedialog.askopenfilename(
            title="Select Configuration",
            filetypes=(("toml", "*.toml"),),
            defaultextension=".toml",
        )

        if not file_path:  # pragma: no cover
            return

        config = CfgConfigureLayout(file_path)

        config.version = VERSION

        if self.tk_vars.load_active_design.get():
            aedb = get_active_edb()
            config.layout_file = aedb

        working_directory = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        working_directory.mkdir()

        new_aedb = ConfigureLayoutBackend.load_config(
            config=config, working_directory=working_directory, overwrite=self.tk_vars.load_overwrite.get()
        )
        self.new_aedb = new_aedb

        if self.tk_vars.load_overwrite.get():
            desktop = ansys.aedt.core.Desktop(
                new_desktop=False,
                version=VERSION,
                port=PORT,
                aedt_process_id=AEDT_PROCESS_ID,
                student_version=IS_STUDENT,
            )
            desktop.odesktop.DeleteProject(Path(new_aedb).stem)
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                desktop.release_desktop(False, False)

        app = ansys.aedt.core.Hfss3dLayout(
            project=str(new_aedb),
            version=VERSION,
            port=PORT,
            aedt_process_id=AEDT_PROCESS_ID,
            student_version=IS_STUDENT,
        )

        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        return True

    @staticmethod
    def call_back_export_template():
        write_dir = filedialog.askdirectory(title="Save to")
        if not write_dir:  # pragma: no cover
            return
        working_directory = Path(write_dir)

        _, msg = ConfigureLayoutBackend.export_template_config(working_directory)
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            messagebox.showinfo("Message", msg)


class TabExportConfigFromDesign:
    def __init__(self, master_ui):
        self.master_ui = master_ui

        self.export_options = {}
        for i, j in ExportOptions.__dict__.items():
            if i.startswith("_"):
                continue
            self.export_options[i] = tkinter.BooleanVar()
            self.export_options[i].set(j)

    def create_ui(self, master):
        frame0 = ttk.Frame(master, name="frame0", style="PyAEDT.TFrame")
        frame0.grid(row=0, column=0, **GRID_PARAMS)

        b = ttk.Button(
            frame0,
            name="export_config",
            text="Export Config File From Active Design",
            command=self.export_config_from_design,
            style="PyAEDT.TButton",
            width=30,
        )
        b.grid(row=0, column=0, **GRID_PARAMS)

        frame1 = ttk.Frame(master, name="frame1", style="PyAEDT.TFrame")
        frame1.grid(row=1, column=0, **GRID_PARAMS)
        row = 0
        col = 0
        for i, j in self.export_options.items():
            r = ttk.Checkbutton(
                frame1,
                name=i,
                text=i,
                variable=j,
                style="PyAEDT.TCheckbutton",
            )
            r.i = i
            r.j = j
            r.grid(row=row, column=col, sticky="w")
            if col == 1:
                row = row + 1
                col = 0
            else:
                col += 1

    def export_config_from_design(self):
        export_directory = filedialog.askdirectory(title="Save to")
        if export_directory:
            export_directory = Path(export_directory)
        else:  # pragma: no cover
            return False

        for i, j in self.export_options.items():
            setattr(ExportOptions, i, j.get())

        ExtensionDataExport.src_aedb = get_active_edb()
        ExtensionDataExport.working_directory = export_directory
        if ConfigureLayoutBackend.export_config_from_design():
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                messagebox.showinfo("Message", "Done")
            return True
        else:  # pragma: no cover
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                messagebox.showinfo("Message", "Failed")


class ConfigureLayoutExtension(ExtensionCommon):
    def __init__(self, withdraw: bool = False):
        self.tabs = {}
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_extension_content(self):
        menubar = tkinter.Menu(self.root)
        # === File Menu ===
        help_menu = tkinter.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Introduction",
            command=lambda: webbrowser.open(INTRO_LINK),
        )
        help_menu.add_command(
            label="User Guide",
            command=lambda: webbrowser.open(GUIDE_LINK),
        )

        # Add File menu to menubar
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook", width=400)

        tab_name = "Load"
        tab = ttk.Frame(nb, name=tab_name.lower(), style="PyAEDT.TFrame")
        nb.add(tab, text=tab_name)
        sub_ui = TabLoadConfig(self)
        sub_ui.create_ui(tab)
        self.tabs[tab_name] = sub_ui

        tab_name = "Export"
        tab = ttk.Frame(nb, name=tab_name.lower(), style="PyAEDT.TFrame")
        nb.add(tab, text=tab_name)
        sub_ui = TabExportConfigFromDesign(self)
        sub_ui.create_ui(tab)
        self.tabs[tab_name] = sub_ui

        nb.grid(row=0, column=0, sticky="e", **GRID_PARAMS)


class ConfigureLayoutBackend:
    @staticmethod
    def load_config(config, working_directory, overwrite):
        app = Edb(edbpath=str(config.layout_file), edbversion=config.version)

        if config.layout_validation.illegal_rlc_values:
            app.layout_validation.illegal_rlc_values(fix=True)

        cfg = config.get_edb_config_dict(app)

        if config.supplementary_json != "":
            app.configuration.load(config.supplementary_json)
        app.configuration.load(cfg)

        app.configuration.run()

        if overwrite:
            app.save()
            new_aedb = app.edbpath
        else:
            new_aedb = str(Path(working_directory) / Path(app.edbpath).name)
            app.save_as(new_aedb)
        app.close()
        settings.logger.info(f"New Edb is saved to {new_aedb}")
        return str(new_aedb)

    @staticmethod
    def export_template_config(working_directory):
        export_directory = Path(working_directory)
        msg = []

        # Read examples serdes
        example_master_config = Path(__file__).parent / "resources" / "configure_layout" / "example_serdes.toml"
        content = read_toml(example_master_config)
        content["version"] = VERSION

        # Not download in tests
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            example_edb = download_file(source="edb/ANSYS_SVP_V1_1.aedb", local_path=export_directory)
        else:
            example_edb = export_directory / "ANSYS_SVP_V1_1.aedb"
        content["layout_file"] = str(example_edb)

        if bool(example_edb):
            msg.append(f"Example Edb is downloaded to {example_edb}")
        else:  # pragma: no cover
            msg.append("Failed to download example board.")

        example_config = Path(__file__).parent / "resources" / "configure_layout" / "example_serdes_supplementary.json"
        example_config_content = read_json(example_config)
        example_path = working_directory / "example_serdes_supplementary.json"
        write_configuration_file(example_config_content, example_path)
        msg.append(f"Example configure file is copied to {export_directory / example_config.name}")

        content["supplementary_json"] = str(example_path)

        write_configuration_file(content, export_directory / "example_serdes.toml")
        msg.append(f"Example master configure file is copied to {export_directory / example_master_config.name}")
        return True, "\n\n".join(msg)

    @staticmethod
    def export_config_from_design():
        src_aedb = Path(ExtensionDataExport.src_aedb)
        working_directory = Path(ExtensionDataExport.working_directory)

        app: Edb = Edb(edbpath=str(src_aedb), edbversion=VERSION)
        config_dict = app.configuration.get_data_from_db(**ExportOptions.__dict__)
        app.close_edb()

        toml_name = src_aedb.with_suffix(".toml").name
        json_name = src_aedb.with_suffix(".json").name
        config_master = {
            "title": src_aedb.stem,
            "version": VERSION,
            "layout_file": str(src_aedb),
            "supplementary_json": json_name,
            "rlc_to_ports": [],
            "edb_config": {"ports": [], "setups": []},
        }
        with open(working_directory / toml_name, "w", encoding="utf-8") as f:
            toml.dump(config_master, f)

        with open(working_directory / json_name, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True


def main(
    working_directory: Union[Path, str],
    config_file: Union[Path, str],
) -> str:
    """
    working_directory: str, Path
        Directory in which the result files are saved to.
    config_file: str, Path
        Master configure file in toml format.
    """

    config = CfgConfigureLayout(config_file)
    return ConfigureLayoutBackend.load_config(config, working_directory, False)


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_TITLE)

    if not args["is_batch"]:
        temp = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        temp.mkdir()
        extension: ExtensionCommon = ConfigureLayoutExtension(withdraw=False)
        extension.working_directory = temp
        tkinter.mainloop()
    else:
        main(args["working_directory"], args["config_file"])
