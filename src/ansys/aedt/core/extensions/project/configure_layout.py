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
import os
from pathlib import Path
import tempfile
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Union
import webbrowser

from pydantic import BaseModel
from pyedb import Edb
import toml

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.extensions.project.resources.configure_layout.src.data_class import CfgConfigureLayout


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


class ExtensionDataLoad(BaseModel):
    active_design: bool = True
    overwrite: bool = False


class ExportOptions(BaseModel):
    general: bool = False
    variables: bool = True
    stackup: bool = True
    package_definitions: bool = False
    setups: bool = True
    sources: bool = True
    ports: bool = True
    nets: bool = False
    pin_groups: bool = True
    operations: bool = True
    components: bool = False
    boundaries: bool = False
    s_parameters: bool = False
    padstacks: bool = False


class ExtensionDataExport(BaseModel):
    working_directory: str = ""
    src_aedb: str = ""


class ExtensionData(BaseModel):
    load: ExtensionDataLoad = ExtensionDataLoad()
    export: ExtensionDataExport = ExtensionDataExport()
    export_options: ExportOptions = ExportOptions()


class TabLoadConfig:
    class TKVars:
        def __init__(self, master):
            self.master = master
            self.load_active_design = tkinter.BooleanVar()
            self.load_overwrite = tkinter.BooleanVar()
            self.init()

        def init(self):
            self.load_active_design.set(self.master.master.extension_data.load.active_design)
            self.load_overwrite.set(self.master.master.extension_data.load.overwrite)

    def __init__(self, master):
        self.master = master
        self.tk_vars = self.TKVars(self)

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
        radio1 = ttk.Radiobutton(
            master,
            text="Active Design",
            value=True,
            variable=self.tk_vars.load_active_design,
            style="PyAEDT.TRadiobutton",
            name="active_design",
        )
        radio1.grid(row=row, column=0, sticky="w")
        row = row + 1
        radio2 = ttk.Radiobutton(
            master,
            text="Configure File Specified Design",
            value=False,
            variable=self.tk_vars.load_active_design,
            name="specified_design",
            style="PyAEDT.TRadiobutton",
        )
        radio2.grid(row=row, column=0, sticky="w")

        row = row + 1
        r = ttk.Checkbutton(
            master,
            name="overwrite_design",
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

        config = CfgConfigureLayout.from_file(file_path)

        if self.tk_vars.load_active_design.get():
            aedb = get_active_edb()
            config.layout_file = aedb

        working_directory = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        working_directory.mkdir()


        # Apply settings to Edb
        app = Edb(edbpath=str(config.layout_file), edbversion=config.version)
        if config.layout_validation.illegal_rlc_values:
            app.layout_validation.illegal_rlc_values(fix=True)

        cfg = config.get_edb_config_dict(app)

        if config.supplementary_json != "":
            app.configuration.load(config.supplementary_json)
        app.configuration.load(cfg)

        app.configuration.run()

        if self.tk_vars.load_overwrite.get():
            app.save()
            new_aedb = app.edbpath
            # Delete .aedt if it exists
            if Path(new_aedb).with_suffix(".aedt").exists():
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
        else:
            new_aedb = str(Path(working_directory) / Path(app.edbpath).name)
            app.save_as(new_aedb)
        app.close()
        settings.logger.info(f"New Edb is saved to {new_aedb}")

        # Open new Edb in AEDT
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

        msg = []
        example_master_config = Path(__file__).parent / "resources" / "configure_layout" / "example_serdes.toml"
        example_slave_config = (
            Path(__file__).parent / "resources" / "configure_layout" / "example_serdes_supplementary.json"
        )
        export_directory = Path(working_directory)
        with open(example_master_config, "r", encoding="utf-8") as file:
            content = file.read()

        example_edb = download_file(source="edb/ANSYS_SVP_V1_1.aedb", local_path=working_directory)

        if bool(example_edb):
            msg.append(f"Example Edb is downloaded to {example_edb}")
        else:  # pragma: no cover
            msg.append("Failed to download example board.")

        with open(export_directory / example_master_config.name, "w", encoding="utf-8") as f:
            f.write(content)
            msg.append(f"Example master configure file is copied to {export_directory / example_master_config.name}")

        with open(example_slave_config, "r", encoding="utf-8") as file:
            content = file.read()
        with open(export_directory / example_slave_config.name, "w", encoding="utf-8") as f:
            f.write(content)
            msg.append(f"Example slave configure file is copied to {export_directory / example_slave_config.name}")

        msg_ = "\n\n".join(msg)

        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            messagebox.showinfo("Message", msg_)


class TabExportConfigFromDesign:
    def __init__(self, master):
        self.master = master

        self.export_options = {}
        for i, j in self.master.extension_data.export_options.model_dump().items():
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
        def _export_config_from_design(src_aedb, working_directory, export_options):
            app: Edb = Edb(edbpath=str(src_aedb), edbversion=VERSION)
            config_dict = app.configuration.get_data_from_db(**export_options)
            app.close()

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

        export_directory = filedialog.askdirectory(title="Save to")
        if export_directory:
            export_directory = Path(export_directory)
        else:  # pragma: no cover
            return False

        for i, j in self.export_options.items():
            setattr(self.master.extension_data.export_options, i, j.get())

        self.master.extension_data.export.src_aedb = get_active_edb()
        self.master.extension_data.export.working_directory = export_directory
        if _export_config_from_design(
            self.master.extension_data.export.src_aedb,
            self.master.extension_data.export.working_directory,
            self.master.extension_data.export_options.model_dump(),
        ):
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                messagebox.showinfo("Message", "Done")
            return True
        else:  # pragma: no cover
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                messagebox.showinfo("Message", "Failed")


class ConfigureLayoutExtension(ExtensionProjectCommon):
    def __init__(self, withdraw: bool = False):
        self.extension_data = ExtensionData()
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


def main(
    working_directory: Union[Path, str],
    config_file: Union[Path, str],
    layout_file: Union[Path, str],
) -> str:
    """
    working_directory: str, Path
        Directory in which the result files are saved to.
    config_file: str, Path
        Master configure file in toml format.
    layout_file: str, Path
        Layout database. supports aedt and aedb, odb++, brd.
    """

    config = CfgConfigureLayout(config_file)
    config.layout_file = layout_file
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
        main(args["working_directory"], args["config_file"], args["layout_file"])
