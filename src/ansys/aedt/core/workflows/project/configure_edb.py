# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

import PIL.Image
import PIL.ImageTk
import ansys.aedt.core
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import generate_unique_name
import ansys.aedt.core.workflows.hfss3dlayout
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
from pyedb import Edb
from pyedb import Siwave

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()


class ConfigureEdbFrontend(tk.Tk):  # pragma: no cover
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
        project_name = self.desktop.active_project().GetName()
        project_dir = self.desktop.active_project().GetPath()
        project_file = os.path.join(project_dir, project_name + ".aedt")
        return [project_dir, project_file]

    def __init__(self, desktop):
        super().__init__()
        self.desktop = desktop

        self.geometry("500x300")
        self.title("EDB Configuration 2.0")

        self.status = tk.StringVar(value="")
        self.selected_app_option = tk.StringVar(value="Active Design")
        self.selected_project_file_path = ""
        self.selected_project_file = tk.StringVar(value="")
        self.selected_cfg_file_folder = tk.StringVar(value="")

        # Load the logo for the main window
        icon_path = os.path.join(os.path.dirname(ansys.aedt.core.workflows.__file__), "images", "large", "logo.png")
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
        col_width = [30, 20, 30]

        # Section 1
        self.label_version = ttk.Label(self, text=f"AEDT {version}")
        self.label_version.grid(row=0, column=0)
        label = ttk.Label(self, textvariable=self.status)
        label.grid(row=0, column=1)

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

        # Siwave
        label_project_file = tk.Label(self, width=col_width[2], height=1, textvariable=self.selected_project_file)
        label_project_file.grid(row=s3_start_row, column=2)

        # Apply cfg
        button = ttk.Button(self, text="Apply Configuration", width=col_width[0], command=self.call_apply_cfg_file)
        button.grid(row=s3_start_row + 2, column=0)

        button = ttk.Button(
            self, text="Apply Configuration Batch", width=col_width[0], command=self.call_select_cfg_folder
        )
        button.grid(row=s3_start_row + 3, column=0)

        # Export cfg
        button = ttk.Button(self, text="Export Configuration", width=col_width[0], command=self.call_export_cfg)
        button.grid(row=s3_start_row + 4, column=0)

    def call_select_project(self):
        if self.selected_app_option.get() == "HFSS 3D Layout":
            file_path = filedialog.askopenfilename(
                initialdir="/",
                title="Select File",
                filetypes=(("Electronics Desktop", "*.aedt"),),
            )
        elif self.selected_app_option.get() == "SIwave":
            file_path = filedialog.askopenfilename(
                initialdir="/",
                title="Select File",
                filetypes=(("SIwave project", "*.siw"),),
            )
        else:
            file_path = None

        if not file_path:
            return
        else:
            self.selected_project_file_path = file_path
            self.selected_project_file.set(Path(file_path).parts[-1])

    def call_apply_cfg_file(self):
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
            # self.execute_load_cfg_active(file_cfg_path)
        self.execute()

    def call_select_cfg_folder(self):
        init_dir = Path(self.selected_project_file_path).parent if self.selected_project_file_path else "/"
        file_dir = filedialog.askdirectory(initialdir=init_dir, title="Select a Folder")
        if not file_dir:
            return

        if self.selected_app_option.get() == "Active Design":
            data = self.get_active_project_info()
            if data:
                project_dir, project_file = data
            else:
                return
        else:
            file_save_dir = filedialog.askdirectory(
                initialdir=init_dir,
                title="Save new projects to",
            )
            project_file = self.selected_project_file_path

        for i in os.listdir(file_dir):
            if i.endswith(".json") or i.endswith(".toml"):
                file_cfg_path = os.path.join(file_dir, i)
                if self.selected_app_option.get() == "SIwave":
                    file_save_path = os.path.join(
                        Path(file_save_dir), Path(project_file).stem + "_" + Path(i).stem + ".siw"
                    )
                    self._execute["siwave_load"].append(
                        {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
                    )
                elif self.selected_app_option.get() == "HFSS 3D Layout":
                    file_save_path = os.path.join(
                        Path(file_save_dir), Path(project_file).stem + "_" + Path(i).stem + ".aedt"
                    )
                    self._execute["aedt_load"].append(
                        {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
                    )
                else:

                    file_save_path = os.path.join(
                        project_dir, Path(project_file).stem + "_" + generate_unique_name(Path(i).stem) + ".aedt"
                    )
                    self._execute["active_load"].append(
                        {"project_file": project_file, "file_cfg_path": file_cfg_path, "file_save_path": file_save_path}
                    )
        self.execute()

    def call_select_cfg_file(self, tk_label):
        init_dir = Path(self.selected_project_file_path).parent if self.selected_project_file_path else "/"
        file_path = filedialog.askopenfilename(
            initialdir=init_dir,
            title="Select Configuration File",
            filetypes=(("json file", "*.json"), ("toml", "*.toml")),
            defaultextension=".json",
        )

        if not file_path:
            return
        self.selected_cfg_file_folder.set(file_path)
        tk_label.config(text=Path(file_path).parts[-1])

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
        else:
            data = self.get_active_project_info()
            if data:
                _, project_file = data
                self._execute["active_export"].append({"project_file": project_file, "file_path_save": file_path_save})
            else:
                return
        self.execute()

    def execute(self):
        ConfigureEdbBackend(self._execute)
        self._execute = {
            "active_load": [],
            "siwave_load": [],
            "aedt_load": [],
            "active_export": [],
            "siwave_export": [],
            "aedt_export": [],
        }
        messagebox.showinfo("Information", "Configuration Done!")


class ConfigureEdbBackend:
    def __init__(self, args):
        if len(args["siwave_load"]):  # pragma: no cover
            for i in args["siwave_load"]:
                self.execute_load_cfg_siw(**i)

        if len(args["aedt_load"]):
            for i in args["aedt_load"]:
                self.execute_load_cfg_aedt(**i)

        if len(args["active_load"]):
            for i in args["active_load"]:
                self.execute_load_cfg_aedt(**i)

        if len(args["siwave_export"]):  # pragma: no cover
            for i in args["siwave_export"]:
                self.execute_export_cfg_siw(**i)

        if len(args["aedt_export"]):
            for i in args["aedt_export"]:
                self.execute_export_cfg_aedt(**i)

        if len(args["active_export"]):
            for i in args["active_export"]:
                self.execute_export_cfg_aedt(**i)

    @staticmethod
    def execute_load_cfg_siw(project_file, file_cfg_path, file_save_path):  # pragma: no cover
        """Load configuration file."""
        fdir = Path(file_save_path).parent
        fname = Path(file_save_path).stem
        siw = Siwave(specified_version=version)
        siw.open_project(str(project_file))
        siw.load_configuration(file_cfg_path)
        siw.save_project(fdir, fname)
        siw.quit_application()

    @staticmethod
    def execute_load_cfg_aedt(project_file, file_cfg_path, file_save_path):
        fedb = Path(project_file).with_suffix(".aedb")
        edbapp = Edb(str(fedb), edbversion=version)
        edbapp.configuration.load(file_cfg_path)
        edbapp.configuration.run()
        edbapp.save_as(str(Path(file_save_path).with_suffix(".aedb")))
        edbapp.close()

        h3d = Hfss3dLayout(str(Path(file_save_path).with_suffix(".aedb")))
        h3d.save_project()

    @staticmethod
    def execute_load_cfg_active(project_file, file_cfg_path, file_save_path):
        fedb = Path(project_file).with_suffix(".aedb")

        edbapp = Edb(fedb, edbversion=version)
        edbapp.configuration.load(config_file=file_cfg_path)
        edbapp.configuration.run()
        edbapp.save_as(str(Path(file_save_path).with_suffix(".aedb")))
        edbapp.close()
        h3d = Hfss3dLayout(str(Path(file_save_path).with_suffix(".aedb")))
        h3d.save_project()

    @staticmethod
    def execute_export_cfg_siw(project_file, file_path_save):  # pragma: no cover
        siw = Siwave(specified_version=version)
        siw.open_project(str(project_file))
        siw.export_configuration(file_path_save)
        siw.quit_application()

    @staticmethod
    def execute_export_cfg_aedt(project_file, file_path_save):
        fedb = Path(project_file).with_suffix(".aedb")
        edbapp = Edb(str(fedb), edbversion=version)
        edbapp.configuration.export(file_path_save)
        edbapp.close()


def main(is_test=False, execute=""):
    if is_test:
        ConfigureEdbBackend(execute)
    else:  # pragma: no cover
        desktop = ansys.aedt.core.Desktop(
            new_desktop_session=False,
            specified_version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )
        app = ConfigureEdbFrontend(desktop)
        app.mainloop()
        desktop.release_desktop(False, False)


if __name__ == "__main__":
    # Open UI
    main()
