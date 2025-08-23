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
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk

import toml

from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.extensions.project.resources.via_design.src.backend import ViaDesignBackend
from ansys.aedt.core.extensions.project.resources.via_design.src.data_classes import ConfigModel
from ansys.aedt.core.extensions.project.resources.via_design.src.example_tab import create_example_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.general_settings_tab import create_general_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.help_tab import create_help_tab_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.padstack_defs_tab import create_padstack_defs_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.pin_map_settings_tab import create_pin_map_settings_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.project_settings_tab import create_project_settings_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.simulation_settings_tab import (
    create_simulation_settings_ui,
)
from ansys.aedt.core.extensions.project.resources.via_design.src.stackup_settings_tab import create_stackup_settings_ui
from ansys.aedt.core.extensions.project.resources.via_design.src.stackup_settings_tab import update_stackup_tree
from ansys.aedt.core.extensions.project.resources.via_design.src.technology_settings_tab import (
    create_technology_settings_ui,
)
from ansys.aedt.core.extensions.project.resources.via_design.src.template import CFG_PACKAGE_DIFF
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.internal.errors import AEDTRuntimeError

IS_TEST = True if "PYTEST_CURRENT_TEST" in os.environ else False

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_DEFAULT_ARGUMENTS = {"file_path": ""}
EXTENSION_TITLE = "Via design"
EXTENSION_NB_ROW = 2
EXTENSION_NB_COLUMN = 3

EXTENSION_RESOURCES_PATH = Path(__file__).parent / "resources" / "via_design"
DEFAULT_CFG = EXTENSION_RESOURCES_PATH / "package_diff.toml"


class ViaDesignExtension(ExtensionProjectCommon):
    """Extension for advanced fields calculator in AEDT."""

    EXTENSION_RESOURCES_PATH = Path(__file__).parent / "resources" / "via_design"

    def __init__(self, path_config=None, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            title=EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=None,
            toggle_column=None,
        )
        self.__create_design_path = None
        self.config_model = ConfigModel(**CFG_PACKAGE_DIFF)

        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Configure root window row and column weights to make it resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        menubar = tkinter.Menu(self.root, name="menubar")
        # === File Menu ===
        file_menu = tkinter.Menu(menubar, tearoff=0, name="load_menu")
        file_menu.add_command(
            label="Load",
            command=self.load_config,
        )
        file_menu.add_command(
            label="Save",
            command=self.save_config,
        )
        menubar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menubar)

        self.root.geometry("1920x1080")

        self.notebook = ttk.Notebook(self.root, style="PyAEDT.TNotebook")
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        example_ui_frame = ttk.Frame(self.notebook, style="PyAEDT.TFrame")

        self.general_tab_frame = ttk.Frame(self.notebook, style="PyAEDT.TFrame")
        self.stackup_tab_frame = ttk.Frame(self.notebook, style="PyAEDT.TFrame")
        self.padstack_defs_frame = ttk.Frame(self.notebook, style="PyAEDT.TFrame")

        self.pin_map_tab_frame = ttk.Frame(self.notebook)
        self.technology_tab_frame = ttk.Frame(self.notebook)
        self.simulation_tab_frame = ttk.Frame(self.notebook)
        self.project_tab_frame = ttk.Frame(self.notebook)
        self.help_tab_frame = ttk.Frame(self.notebook)

        self.notebook.add(example_ui_frame, text="Configuration examples")
        self.notebook.add(self.general_tab_frame, text="General Setttings")
        self.notebook.add(self.stackup_tab_frame, text="Stackup Settings")
        self.notebook.add(self.padstack_defs_frame, text="PadStack Settings")
        self.notebook.add(self.pin_map_tab_frame, text="Pin Map Settings")
        self.notebook.add(self.technology_tab_frame, text="Technology Settings")
        self.notebook.add(self.simulation_tab_frame, text="Simulation Settings")
        self.notebook.add(self.project_tab_frame, text="Project Settings")
        self.notebook.add(self.help_tab_frame, text="Help")

        create_example_ui(example_ui_frame, self, EXTENSION_NB_COLUMN)
        create_general_ui(self.general_tab_frame, self)
        create_stackup_settings_ui(self.stackup_tab_frame, self)
        create_padstack_defs_ui(self.padstack_defs_frame, self)
        create_pin_map_settings_ui(self.pin_map_tab_frame, self)
        create_technology_settings_ui(self.technology_tab_frame, self)
        create_simulation_settings_ui(self.simulation_tab_frame, self)
        create_project_settings_ui(self.project_tab_frame, self)
        create_help_tab_ui(self.help_tab_frame, self)

    def load_config(self):
        create_design_path = filedialog.askopenfilename(
            title="Select configuration",
            filetypes=(("json", "*.json"),),
            defaultextension=".toml",
        )
        if not create_design_path:
            return

        create_design_path = Path(create_design_path)
        if not create_design_path.is_file():
            raise AEDTRuntimeError(f"Selected file does not exist or is not a file: {self.__create_design_path}")
        else:
            try:
                with open(create_design_path, "r") as f:
                    data = json.load(f)

                self.config_model = ConfigModel(**data)
                # Update all UI components after loading new configuration
                # Update Stackup
                update_stackup_tree(self)

                self.refresh_general_ui_after_config_load()
                self.refresh_padstack_ui_after_config_load()

                messagebox.showinfo(
                    "Configuration Loaded", f"Configuration successfully loaded from:\n{create_design_path}"
                )

            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration:\n{str(e)}")
            # todo update GUI
            # Update Stackup
            update_stackup_tree(self)

    def save_config(self):
        file_path = filedialog.asksaveasfilename(
            title="Select configuration",
            filetypes=(("toml", "*.toml"),),
            defaultextension=".toml",
        )
        if not file_path:
            return

        data = self.config_model.model_dump()

        # todo Refactor to use tomlkit
        with open(file_path, "w") as f:
            toml.dump(data, f)

    def update_config_model(self):
        """Update self.config_model from UI."""
        # todo
        pass

    def create_design(self):
        """Create via design in AEDT"""
        self.update_config_model()

        dict_config = self.config_model.model_dump()

        edb_path = self.create_design_batch(dict_config)
        hfss_3d = Hfss3dLayout(
            project=edb_path,
            version=VERSION,
            port=PORT,
            aedt_process_id=AEDT_PROCESS_ID,
            student_version=IS_STUDENT,
        )
        if "PYTEST_CURRENT_TEST" in os.environ:
            hfss_3d.close_project()
        else:
            hfss_3d.release_desktop(close_projects=False, close_desktop=False)
        return True

    @staticmethod
    def create_design_batch(config: dict):
        technologies = config.pop("technologies")

        for param_name, param_value in config["signals"].items():
            tech_name = param_value["technology"]
            config["signals"][param_name]["stacked_vias"] = technologies[tech_name]["stacked_via"]

        for param_name, param_value in config["differential_signals"].items():
            tech_name = param_value["technology"]
            config["differential_signals"][param_name]["stacked_vias"] = technologies[tech_name]["stacked_via"]

        backend = ViaDesignBackend(config)
        edb_path = backend.create_edb()
        settings.logger.info(f"New Via design is saved to {edb_path}.")
        return edb_path

    @property
    def create_design_path(self):
        return self.__create_design_path

    @property
    def export_examples(self):
        return self.__export_examples


def batch(file_path):
    file_path = Path(file_path)
    data = toml.load(file_path) if file_path.suffix == ".toml" else json.loads(file_path.read_text(encoding="utf-8"))
    cfg = ConfigModel(**data)
    app = ViaDesignExtension(withdraw=True)
    return app.create_design_batch(cfg.model_dump())


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = ViaDesignExtension(withdraw=False)
        tkinter.mainloop()
    else:
        batch(args["file_path"])
