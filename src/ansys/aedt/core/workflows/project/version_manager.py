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

VERSION = "0.3.0"

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import webbrowser
import xml.etree.ElementTree as ET
import zipfile

import ansys.aedt.core as pyaedt
from ansys.aedt.core.workflows.customize_automation_tab import add_script_to_menu
from ansys.aedt.core.workflows.customize_automation_tab import available_toolkits
from ansys.aedt.core.workflows.misc import ExtensionTheme
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
import pyedb
import requests

DISCLAIMER = (
    "This script will download and install certain third-party software and/or "
    "open-source software (collectively, 'Third-Party Software'). Such Third-Party "
    "Software is subject to separate terms and conditions and not the terms of your "
    "Ansys software license agreement. Ansys does not warrant or support such "
    "Third-Party Software.\n"
    "Do you want to proceed ?"
)


def is_git_installed():
    try:
        # Run the command `git --version`
        result = subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the command ran successfully
        if result.returncode == 0:
            print(f"Git is installed: {result.stdout.strip()}")
            return True
        else:
            print("Git is not installed.")
            return False
    except FileNotFoundError:
        print("Git is not installed.")
        return False


def get_latest_version(package_name):
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if response.status_code == 200:
        data = response.json()
        return data["info"]["version"]
    else:
        return "Unknown"


class VersionManager:
    TITLE = "Version Manager {}".format(VERSION)
    USER_GUIDE = "https://github.com/"
    UI_WIDTH = 800
    UI_HEIGHT = 500

    @property
    def venv_path(self):
        return sys.prefix

    @property
    def python_exe(self):
        return os.path.join(self.venv_path, "Scripts", "python.exe")

    @property
    def python_version(self):
        temp = platform.python_version().split(".")[0:2]
        return ".".join(temp)

    @property
    def pyaedt_version(self):
        return pyaedt.version

    @property
    def pyedb_version(self):
        return pyedb.version

    def __init__(self, ui, desktop, aedt_version, personal_lib):
        self.desktop = desktop
        self.aedt_version = aedt_version
        self.personal_lib = personal_lib

        self.style = ttk.Style()

        # Define the custom style for TLabel (ttk.Label)
        self.style.configure(
            "PyAEDT",
            font=("Helvetica", 14, "bold"),  # Font style: Helvetica, size 14, bold
            foreground="darkblue",  # Text color
            background="lightyellow",  # Background color
            padding=(10, 5),  # Padding inside the label
            anchor="w",
        )
        self.theme = ExtensionTheme()

        self.theme.apply_light_theme(self.style)
        ui.theme = "light"

        self.venv_information = tk.StringVar()
        self.pyaedt_info = tk.StringVar()
        self.pyedb_info = tk.StringVar()
        self.venv_information.set("Venv Information")

        self.pyaedt_branch_name = tk.StringVar()
        self.pyaedt_branch_name.set("main")
        self.pyedb_branch_name = tk.StringVar()
        self.pyedb_branch_name.set("main")

        self.ini_file_path = os.path.join(os.path.dirname(__file__), "settings.ini")

        self.root = ui
        self.root.title(self.TITLE)
        self.root.geometry(f"{self.UI_WIDTH}x{self.UI_HEIGHT}")

        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL, style="TPanedwindow")
        main_frame.pack(fill=tk.BOTH, expand=True)
        notebook = ttk.Notebook(self.root, style="TNotebook")
        main_frame.add(notebook, weight=3)
        # notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_basic = ttk.Frame(notebook)
        tab_advanced = ttk.Frame(notebook)
        tab_extensions = ttk.Frame(notebook)

        notebook.add(tab_basic, text="Basic")
        notebook.add(tab_advanced, text="Advanced")
        # notebook.add(tab_extensions, text="Extensions")

        self.create_file_menu()
        self.create_button_frame(self.root)
        self.create_ui_basic(tab_basic)
        self.create_ui_advanced(tab_advanced)
        self.create_ui_extensions(tab_extensions)

        self.clicked_refresh()

    def create_file_menu(self):
        menu_bar = tk.Menu(root)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        #help_menu.add_command(label="User Guide", command=lambda: webbrowser.open(self.USER_GUIDE))
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def create_ui_basic(self, parent):
        def create_ui_wheelhouse(frame):
            buttons = [
                ["Update from wheelhouse", self.update_from_wheelhouse],
                ["Update extensions", self.update_extensions],
            ]
            for text, cmd in buttons:
                button = tk.Button(frame, text=text, width=40, height=2, command=cmd)
                button.pack(side="left", padx=10, pady=10)

        def create_ui_pyaedt(frame):
            label = ttk.Label(frame, textvariable=self.pyaedt_info, width=30, style="TLabel")
            label.pack(side="left")

            buttons = [
                ["Update", self.update_pyaedt],
            ]
            for text, cmd in buttons:
                button = tk.Button(frame, text=text, width=20, height=2, command=cmd)
                button.pack(side="left", padx=10, pady=10)

        def create_ui_pyedb(frame):
            label = ttk.Label(frame, textvariable=self.pyedb_info, width=30, style="TLabel")
            label.pack(side="left")

            buttons = [
                ["Update", self.update_pyedb],
            ]
            for text, cmd in buttons:
                button = tk.Button(frame, text=text, width=20, height=2, command=cmd)
                button.pack(side="left", padx=10, pady=10)

        def create_ui_info(frame):
            label = ttk.Label(frame, textvariable=self.venv_information, style="TLabel")
            label.pack(anchor="w")

        frame0 = tk.Frame(parent)
        frame1 = tk.Frame(parent)
        frame2 = tk.Frame(parent)
        frame3 = tk.Frame(parent)

        frame0.pack(padx=5, pady=5)
        frame1.pack(padx=5, pady=5)
        frame2.pack(side="top", padx=5, pady=5)
        frame3.pack(side="top", padx=20, pady=20, fill="x")

        create_ui_pyaedt(frame0)
        create_ui_pyedb(frame1)
        create_ui_wheelhouse(frame2)
        create_ui_info(frame3)

    def create_ui_advanced(self, parent):
        def create_ui_pyaedt(frame):
            label = ttk.Label(frame, text="PyAEDT", width=10, style="TLabel")
            label.pack(side="left")

            buttons = [
                ["Get Branch", self.get_pyaedt_branch],
            ]
            for text, cmd in buttons:
                button = tk.Button(frame, text=text, width=20, height=2, command=cmd)
                button.pack(side="left", padx=10, pady=10)
            entry = tk.Entry(frame, width=30, textvariable=self.pyaedt_branch_name)
            entry.pack(side="left")

        def create_ui_pyedb(frame):
            label = ttk.Label(frame, text="PyEDB", width=10, style="TLabel")
            label.pack(side="left")

            buttons = [
                ["Get Branch", self.get_pyedb_branch],
            ]
            for text, cmd in buttons:
                button = tk.Button(frame, text=text, width=20, height=2, command=cmd)
                button.pack(side="left", padx=10, pady=10)
            entry = tk.Entry(frame, width=30, textvariable=self.pyedb_branch_name)
            entry.pack(side="left")

        def create_ui_pyaedt_buttons(frame):
            buttons = [["Reset PyAEDT Buttons", self.reset_pyaedt_buttons_in_aedt]]
            for text, cmd in buttons:
                button = tk.Button(frame, text=text, width=40, height=2, command=cmd)
                button.pack(side="left", padx=10, pady=10)

        frame0 = tk.Frame(parent)
        frame1 = tk.Frame(parent)
        frame2 = tk.Frame(parent)

        frame0.pack(padx=5, pady=5)
        frame1.pack(padx=5, pady=5)
        frame2.pack(padx=5, pady=5)

        create_ui_pyaedt(frame0)
        create_ui_pyedb(frame1)
        create_ui_pyaedt_buttons(frame2)

    def create_ui_extensions(self, parent):
        frame = tk.Frame(parent)
        frame.pack(padx=5, pady=5)

        buttons = [
            ["Update Configure Layout", self.update_extensions],
        ]
        for text, cmd in buttons:
            button = tk.Button(frame, text=text, width=20, height=2, command=cmd)
            button.pack(side="left", padx=10, pady=10)

    def create_button_frame(self, parent):
        def set_light_theme():
            self.root.configure(bg=self.theme.light["widget_bg"])
            self.theme.apply_light_theme(self.style)
            change_theme_button.config(text="\u263D")

        def set_dark_theme():
            self.root.configure(bg=self.theme.dark["widget_bg"])
            self.theme.apply_dark_theme(self.style)
            change_theme_button.config(text="\u2600")

        def toggle_theme():
            if self.root.theme == "light":
                set_dark_theme()
                self.root.theme = "dark"
            else:
                set_light_theme()
                self.root.theme = "light"

        button_frame = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tk.SUNKEN, borderwidth=2)
        button_frame.pack(fill=tk.X, pady=0)
        change_theme_button = ttk.Button(button_frame, text="\u263D", command=toggle_theme, style="PyAEDT.TButton")
        change_theme_button.pack(side=tk.RIGHT, padx=5, pady=40)

    def update_extensions(self):
        response = messagebox.askquestion("Confirm Action", "Are you sure you want to proceed?")
        if response == "yes":
            toolkits_path = Path(self.personal_lib, "Toolkits")
            temp = []
            for product in toolkits_path.iterdir():
                if not product.is_dir():
                    continue
                xml_file = product / "TabConfig.xml"
                if xml_file.exists():
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    panel_label = "Panel_PyAEDT_Extensions"
                    for panel in root.findall("panel"):
                        if panel.get("label") == panel_label:
                            for button in panel.findall("button"):
                                name = button.get("label")
                                temp.append([product, name])

            atk = available_toolkits()
            msg = ["Below extensions are updated.", ""]
            for product, name in temp:
                product_name = product.stem
                if product_name not in atk:
                    continue
                for i, j in atk[product_name].items():
                    extension_dir = product / name
                    if j["name"] == name:
                        shutil.rmtree(extension_dir, ignore_errors=True)

                        workflow_dir = Path(pyaedt.workflows.__file__).parent

                        add_script_to_menu(
                            name=name,
                            script_file=str(workflow_dir / product_name.lower() / j["script"]),
                            icon_file=str(workflow_dir / product_name.lower() / j["icon"]),
                            product=product_name,
                            template_file=j.get("template", "run_pyaedt_toolkit_script"),
                            copy_to_personal_lib=True,
                            executable_interpreter=self.python_exe,
                            personal_lib=self.personal_lib,
                            aedt_version=self.aedt_version,
                        )
                        msg.append(f"{product_name} {name}")
            messagebox.showinfo("Message", "\n".join(msg))

    def update_pyaedt(self):
        response = messagebox.askquestion("Disclaimer", DISCLAIMER)

        if response == "yes":
            url = f"https://pypi.org/pypi/pyaedt/json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                released_version = data["info"]["version"]
            else:
                released_version = 0

            if self.pyaedt_version > released_version:
                subprocess.run([self.python_exe, "-m", "pip", "install", f"pyaedt=={released_version}"], check=True)
            else:
                subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "pyaedt"], check=True)

            self.clicked_refresh(need_restart=True)

    def get_pyaedt_branch(self):
        if not is_git_installed():
            messagebox.showinfo("Git is not installed")
            return

        response = messagebox.askquestion("Disclaimer", DISCLAIMER)

        if response == "yes":
            branch_name = self.pyaedt_branch_name.get()
            subprocess.run(
                [
                    self.python_exe,
                    "-m",
                    "pip",
                    "install",
                    # "--force-reinstall",
                    f"git+https://github.com/ansys/pyaedt.git@{branch_name}",
                ],
                check=True,
            )
            self.clicked_refresh(need_restart=True)

    def get_pyedb_branch(self):
        if not is_git_installed():
            messagebox.showinfo("Git is not installed")
            return

        response = messagebox.askquestion("Disclaimer", DISCLAIMER)

        if response == "yes":
            branch_name = self.pyedb_branch_name.get()
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", f"git+https://github.com/ansys/pyedb.git@{branch_name}"],
                check=True,
            )
            self.clicked_refresh(need_restart=True)

    def update_pyedb(self):
        response = messagebox.askquestion("Disclaimer", DISCLAIMER)
        if response == "yes":
            url = f"https://pypi.org/pypi/pyedb/json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                released_version = data["info"]["version"]
            else:
                released_version = 0

            if self.pyedb_version > released_version:
                subprocess.run([self.python_exe, "-m", "pip", "install", f"pyedb=={released_version}"], check=True)
            else:
                subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "pyedb"], check=True)

            self.clicked_refresh(need_restart=True)

    def update_from_wheelhouse(self):
        file_selected = filedialog.askopenfilename(title="Select Wheelhouse")

        if file_selected:
            fpath = Path(file_selected)
            file_name = fpath.stem
            _, wh_pyaedt_version, wh_pkg_type, _, _, _, wh_python_version = file_name.split("-")

            msg = []
            correct_wheelhouse = file_name
            # Check Python version
            if not wh_python_version == self.python_version:
                msg.extend(
                    [
                        f"Wrong Python version",
                        f"Wheelhouse: {wh_python_version}",
                        f"Expected version: {self.python_version}",
                    ]
                )
                correct_wheelhouse = correct_wheelhouse.replace(wh_python_version, self.python_version)

            if wh_pkg_type != "installer":
                correct_wheelhouse = correct_wheelhouse.replace(f"-{wh_pkg_type}-", "-installer-")
                msg.extend(["", f"This wheelhouse doesn't contain required packages to add PyAEDT buttons."])

            if msg is not []:
                msg.extend(["", f"Please download {correct_wheelhouse}."])
                msg = "\n".join(msg)
                messagebox.showerror("Confirm Action", msg)
                return

            # Check wheelhouse type

            unzipped_path = fpath.parent / fpath.stem
            if unzipped_path.exists():
                shutil.rmtree(unzipped_path, ignore_errors=True)
            with zipfile.ZipFile(fpath, "r") as zip_ref:
                # Extract all contents to a directory. (You can specify a different extraction path if needed.)
                zip_ref.extractall(unzipped_path)

            subprocess.run(
                [
                    self.python_exe,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    "--no-index",
                    f"--find-links=file:///{str(unzipped_path)}",
                    "pyaedt[installer]",
                ],
                check=True,
            )
            self.clicked_refresh(need_restart=True)

    def reset_pyaedt_buttons_in_aedt(self):
        def handle_remove_error(func, path, exc_info):
            # Attempt to fix permission issues
            import stat

            os.chmod(path, stat.S_IWRITE)  # Add write permission
            func(path)  # Retry the operation

        response = messagebox.askquestion("Confirm Action", "Are you sure you want to proceed?")

        if response == "yes":
            toolkit_path = os.path.join(self.personal_lib, "Toolkits")

            if os.path.isdir(toolkit_path) and os.path.exists(toolkit_path):
                msg = [f"Toolkits path {toolkit_path} already exists.", "Are you sure you want to reset toolkits?"]
                msg = "\n".join(msg)
                response = messagebox.askquestion("Confirm Action", msg)
                if response == "yes":
                    shutil.rmtree(toolkit_path, onerror=handle_remove_error)
                else:
                    return

            from ansys.aedt.core.workflows.installer.pyaedt_installer import add_pyaedt_to_aedt

            try:
                add_pyaedt_to_aedt(self.aedt_version, self.personal_lib)
                messagebox.showinfo("Success", "PyAEDT buttons added in AEDT.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error adding buttons to AEDT: {e}")

    def clicked_refresh(self, need_restart=False):
        msg = [f"Venv path: {self.venv_path}", f"Python version: {self.python_version}"]
        msg = "\n".join(msg)
        self.venv_information.set(msg)

        if need_restart is False:
            self.pyaedt_info.set(f"PyAEDT: {self.pyaedt_version} (Latest {get_latest_version('pyaedt')})")
            self.pyedb_info.set(f"PyEDB: {self.pyedb_version} (Latest {get_latest_version('pyedb')})")
            # messagebox.showinfo("Success", msg)
        else:
            self.pyaedt_info.set(f"PyAEDT: {'Please restart'}")
            self.pyedb_info.set(f"PyEDB: {'Please restart'}")
            messagebox.showinfo("Message", "Done")


def get_desktop_info(release_desktop=True):
    port = get_port()
    aedt_version = get_aedt_version()
    aedt_process_id = get_process_id()

    if aedt_process_id is not None:
        new_desktop = False
        ng = False
        close_project = False
        close_on_exit = False
    else:
        new_desktop = True
        ng = True
        close_project = True
        close_on_exit = True

    app = pyaedt.Desktop(new_desktop=new_desktop, version=aedt_version, port=port, non_graphical=ng)
    personal_lib = app.personallib
    if release_desktop:
        app.release_desktop(close_project, close_on_exit)
    return {"desktop": app, "aedt_version": aedt_version, "personal_lib": personal_lib}


if __name__ == "__main__":
    kwargs = get_desktop_info()
    # Initialize tkinter root window and run the app
    root = tk.Tk()
    app = VersionManager(root, **kwargs)
    root.mainloop()
