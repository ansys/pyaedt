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

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import PIL.Image
import PIL.ImageTk

import ansys.aedt.core
from ansys.aedt.core import Circuit
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import generate_unique_name

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()


class ConfigureCircuitFrontend(tk.Tk):  # pragma: no cover
    app_options = ["Active Design", "Circuit"]
    _execute = {
        "active_load": [],
        "aedt_load": [],
        "active_export": [],
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
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )

    def __init__(self):
        super().__init__()

        self.geometry("310x300")
        self.title("Circuit Configuration")

        self.status = tk.StringVar(value="")
        self.selected_app_option = tk.StringVar(value="Active Design")
        self.selected_project_file_path = ""
        self.selected_project_file = tk.StringVar(value="")
        self.selected_cfg_file_folder = tk.StringVar(value="")

        # Load the logo for the main window
        icon_path = os.path.join(os.path.dirname(ansys.aedt.core.extensions.__file__), "images", "large", "logo.png")
        im = PIL.Image.open(icon_path)
        photo = PIL.ImageTk.PhotoImage(im)

        # Set the icon for the main window
        self.iconphoto(True, photo)

        # Configure style for ttk buttons
        style = ttk.Style()
        style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

        # Main window
        self.create_main_window()

    def create_main_window(self):
        col_width = [50, 20, 30]

        # Section 1
        # self.label_version = ttk.Label(self, text=f"AEDT {version}")
        # self.label_version.grid(row=0, column=0)
        # label = ttk.Label(self, textvariable=self.status)
        # label.grid(row=0, column=1)

        # Section 2
        s2_start_row = 1
        for index, option in enumerate(self.app_options):
            ttk.Radiobutton(self, text=option, value=option, variable=self.selected_app_option).grid(
                row=index + s2_start_row, column=0, sticky=tk.W
            )

        # Section 3
        s3_start_row = 4
        button_select_project_file = ttk.Button(
            self, text="Select project file", width=col_width[0], command=self.call_select_project
        )
        button_select_project_file.grid(row=s3_start_row, column=0)

        # Spacing for project display in the UI.
        label_project_file = tk.Label(self, width=col_width[2], height=1, textvariable=self.selected_project_file)
        label_project_file.grid(row=s3_start_row + 1, column=0)

        # Apply cfg
        button = ttk.Button(
            self, text="Select and Apply Configuration", width=col_width[0], command=self.call_apply_cfg_file
        )
        button.grid(row=s3_start_row + 3, column=0)

        # Export cfg
        button = ttk.Button(self, text="Export Configuration", width=col_width[0], command=self.call_export_cfg)
        button.grid(row=s3_start_row + 4, column=0)

    def call_select_project(self):
        if self.selected_app_option.get() == "Circuit":
            file_path = filedialog.askopenfilename(
                initialdir="/", title="Select File", filetypes=[("Electronics Desktop", "*.aedt")]
            )
        else:
            file_path = None

        if not file_path:
            return
        else:
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

        if self.selected_app_option.get() == "Circuit":
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
                if self.selected_app_option.get() == "Circuit":
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

        if self.selected_app_option.get() == "Circuit":
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
        ConfigureCircuitBackend(self._execute)
        self._execute = {
            "active_load": [],
            "aedt_load": [],
            "active_export": [],
            "aedt_export": [],
        }

    def execute_load(self):
        self.execute()
        self.desktop.release_desktop(False, False)
        messagebox.showinfo("Information", "Done!")

    def execute_export(self, file_path):
        ConfigureCircuitBackend(self._execute)
        self._execute = {
            "active_load": [],
            "aedt_load": [],
            "active_export": [],
            "aedt_export": [],
        }
        messagebox.showinfo("Information", f"Configuration file saved to {file_path}.")


class ConfigureCircuitBackend:
    def __init__(self, args, is_test=False):
        self.is_test = is_test

        if len(args["aedt_load"]):
            for i in args["aedt_load"]:
                self.execute_load_cfg_aedt(**i)

        if len(args["active_load"]):
            for i in args["active_load"]:
                self.execute_load_cfg_aedt(**i)

        if len(args["aedt_export"]):
            for i in args["aedt_export"]:
                self.execute_export_cfg_aedt(**i)

        if len(args["active_export"]):
            for i in args["active_export"]:
                self.execute_export_cfg_aedt(**i)

    def execute_load_cfg_aedt(self, project_file, file_cfg_path, file_save_path):
        fcir = Path(project_file).with_suffix(".aedt")
        cir = Circuit(str(fcir), version=version)
        cir.configurations.import_config(file_cfg_path)
        cir.save_project(str(Path(file_save_path).with_suffix(".aedt")))
        cir.release_desktop(close_projects=False, close_desktop=False)
        if not self.is_test:
            h3d = Circuit(str(Path(file_save_path).with_suffix(".aedt")))
            h3d.save_project()

    @staticmethod
    def execute_export_cfg_aedt(project_file, file_path_save):
        fcir = Path(project_file).with_suffix(".aedt")
        cir = Circuit(str(fcir), version=version)
        cir.configurations.export_config(file_path_save)
        cir.release_desktop(close_projects=False, close_desktop=False)


def main(is_test=False, execute=""):
    if is_test:
        ConfigureCircuitBackend(execute, is_test)
    else:  # pragma: no cover
        app = ConfigureCircuitFrontend()
        app.mainloop()


if __name__ == "__main__":
    # Open UI
    main()
