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

import os
from pathlib import Path
import platform
import shutil
import subprocess  # nosec
import sys
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import webbrowser
import zipfile

import defusedxml
import PIL.Image
import PIL.ImageTk
import pyedb
import requests

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id

is_linux = os.name == "posix"
is_windows = not is_linux

defusedxml.defuse_stdlib()

DISCLAIMER = (
    "This script will download and install certain third-party software and/or "
    "open-source software (collectively, 'Third-Party Software'). Such Third-Party "
    "Software is subject to separate terms and conditions and not the terms of your "
    "Ansys software license agreement. Ansys does not warrant or support such "
    "Third-Party Software.\n"
    "Do you want to proceed ?"
)
UNKNOWN_VERSION = "Unknown"


def get_latest_version(package_name, timeout=3):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
        else:
            return UNKNOWN_VERSION
    except Exception:
        return UNKNOWN_VERSION


class VersionManager:
    TITLE = "Version Manager"
    USER_GUIDE = (
        "https://aedt.docs.pyansys.com/version/stable/User_guide/pyaedt_extensions_doc/project/version_manager.html"
    )
    UI_WIDTH = 800
    UI_HEIGHT = 400

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
        return ansys.aedt.core.version

    @property
    def pyedb_version(self):
        return pyedb.version

    def __init__(self, ui, desktop, aedt_version, personal_lib):
        from ansys.aedt.core.extensions.misc import ExtensionTheme

        self.desktop = desktop
        self.aedt_version = aedt_version
        self.personal_lib = personal_lib
        self.change_theme_button = None

        # Configure style for ttk buttons
        self.style = ttk.Style()
        self.theme = ExtensionTheme()

        self.theme.apply_light_theme(self.style)
        self.theme_color = "light"

        self.venv_information = tkinter.StringVar()
        self.pyaedt_info = tkinter.StringVar()
        self.pyedb_info = tkinter.StringVar()
        self.venv_information.set("Venv Information")

        self.pyaedt_branch_name = tkinter.StringVar()
        self.pyaedt_branch_name.set("main")
        self.pyedb_branch_name = tkinter.StringVar()
        self.pyedb_branch_name.set("main")

        self.ini_file_path = os.path.join(os.path.dirname(__file__), "settings.ini")

        # Load the logo for the main window
        icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo.png"
        im = PIL.Image.open(icon_path)
        photo = PIL.ImageTk.PhotoImage(im)

        self.root = ui
        self.root.iconphoto(True, photo)
        self.root.title(self.TITLE)
        self.root.geometry(f"{self.UI_WIDTH}x{self.UI_HEIGHT}")

        # Main panel
        main_frame = ttk.PanedWindow(self.root, orient=tkinter.HORIZONTAL, style="TPanedwindow")
        main_frame.pack(fill=tkinter.BOTH, expand=True)

        top_frame = ttk.Notebook(self.root, style="TNotebook")
        main_frame.add(top_frame, weight=3)

        tab_basic = ttk.Frame(top_frame, style="PyAEDT.TFrame")
        tab_advanced = ttk.Frame(top_frame, style="PyAEDT.TFrame")

        top_frame.add(tab_basic, text="Basic")
        top_frame.add(tab_advanced, text="Advanced")

        self.create_button_menu()
        self.create_ui_basic(tab_basic)
        self.create_ui_advanced(tab_advanced)

        self.clicked_refresh()

    def toggle_theme(self):
        if self.theme_color == "light":
            self.set_dark_theme()
            self.theme_color = "dark"
        else:
            self.set_light_theme()
            self.theme_color = "light"

    def set_light_theme(self):
        root.configure(bg=self.theme.light["widget_bg"])
        self.theme.apply_light_theme(self.style)
        self.change_theme_button.config(text="\u263d")

    def set_dark_theme(self):
        root.configure(bg=self.theme.dark["widget_bg"])
        self.theme.apply_dark_theme(self.style)
        self.change_theme_button.config(text="\u2600")

    def create_button_menu(self):
        menu_bar = ttk.Frame(self.root, height=30, style="PyAEDT.TFrame")
        help_button = ttk.Button(
            menu_bar, text="Help", command=lambda: webbrowser.open(self.USER_GUIDE), style="PyAEDT.TButton"
        )

        self.change_theme_button = ttk.Button(
            menu_bar, text="\u263d", command=self.toggle_theme, style="PyAEDT.TButton"
        )

        self.change_theme_button.pack(side=tkinter.RIGHT, padx=5, pady=5)
        help_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        menu_bar.pack(fill="x")

    def create_ui_basic(self, parent):
        def create_ui_wheelhouse(frame):
            buttons = [["Update from wheelhouse", self.update_from_wheelhouse]]
            for text, cmd in buttons:
                button = ttk.Button(frame, text=text, width=40, command=cmd, style="PyAEDT.TButton")
                button.pack(side="left", padx=10, pady=10)

        def create_ui_pyaedt(frame):
            label = ttk.Label(frame, textvariable=self.pyaedt_info, width=30, style="PyAEDT.TLabel")
            label.pack(side="left")

            buttons = [
                ["Update", self.update_pyaedt],
            ]
            for text, cmd in buttons:
                button = ttk.Button(frame, text=text, width=20, command=cmd, style="PyAEDT.TButton")
                button.pack(side="left", padx=10, pady=10)

        def create_ui_pyedb(frame):
            label = ttk.Label(frame, textvariable=self.pyedb_info, width=30, style="PyAEDT.TLabel")
            label.pack(side="left")

            buttons = [
                ["Update", self.update_pyedb],
            ]
            for text, cmd in buttons:
                button = ttk.Button(frame, text=text, width=20, command=cmd, style="PyAEDT.TButton")
                button.pack(side="left", padx=10, pady=10)

        def create_ui_info(frame):
            label = ttk.Label(frame, textvariable=self.venv_information, style="PyAEDT.TLabel")
            label.pack(anchor="w")

        frame0 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)
        frame1 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)
        frame2 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)
        frame3 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)

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
            label = ttk.Label(frame, text="PyAEDT", width=10, style="PyAEDT.TLabel")
            label.pack(side="left")

            buttons = [
                ["Get Branch", self.get_pyaedt_branch],
            ]
            for text, cmd in buttons:
                button = ttk.Button(frame, text=text, width=20, command=cmd, style="PyAEDT.TButton")
                button.pack(side="left", padx=10, pady=10)
            entry = ttk.Entry(frame, width=30, textvariable=self.pyaedt_branch_name)
            entry.pack(side="left")

        def create_ui_pyedb(frame):
            label = ttk.Label(frame, text="PyEDB", width=10, style="PyAEDT.TLabel")
            label.pack(side="left")

            buttons = [
                ["Get Branch", self.get_pyedb_branch],
            ]
            for text, cmd in buttons:
                button = ttk.Button(frame, text=text, width=20, command=cmd, style="PyAEDT.TButton")
                button.pack(side="left", padx=10, pady=10)
            entry = ttk.Entry(frame, width=30, textvariable=self.pyedb_branch_name)
            entry.pack(side="left")

        def create_ui_pyaedt_buttons(frame):
            buttons = [["Reset AEDT panels", self.reset_pyaedt_buttons_in_aedt]]
            for text, cmd in buttons:
                button = ttk.Button(frame, text=text, width=40, command=cmd, style="PyAEDT.TButton")
                button.pack(side="left", padx=10, pady=10)

        frame0 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)
        frame1 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)
        frame2 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)

        frame0.pack(padx=5, pady=5)
        frame1.pack(padx=5, pady=5)
        frame2.pack(padx=5, pady=5)

        create_ui_pyaedt(frame0)
        create_ui_pyedb(frame1)
        create_ui_pyaedt_buttons(frame2)

    @staticmethod
    def is_git_available():
        res = shutil.which("git") is not None
        if not res:
            messagebox.showerror("Error: Git Not Found", "Git does not seem to be installed or is not accessible.")
        return res

    def update_pyaedt(self):
        response = messagebox.askyesno("Disclaimer", DISCLAIMER)

        if response:
            latest_version = get_latest_version("pyaedt")
            if latest_version == UNKNOWN_VERSION:
                messagebox.showerror(
                    "Error: Installation Failed", "PyAEDT version was not correctly retrieved from PyPI."
                )
                return

            if self.pyaedt_version > latest_version:
                subprocess.run([self.python_exe, "-m", "pip", "install", f"pyaedt=={latest_version}"], check=True)  # nosec
            else:
                subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "pyaedt"], check=True)  # nosec

            self.clicked_refresh(need_restart=True)

    def update_pyedb(self):
        response = messagebox.askyesno("Disclaimer", DISCLAIMER)

        if response:
            print("Updating pyedb version")
            latest_version = get_latest_version("pyedb")
            if latest_version == UNKNOWN_VERSION:
                messagebox.showerror(
                    "Error: Installation Failed", "PyEDB version was not correctly retrieved from PyPI."
                )
                return

            if self.pyedb_version > latest_version:
                subprocess.run([self.python_exe, "-m", "pip", "install", f"pyedb=={latest_version}"], check=True)  # nosec
            else:
                subprocess.run([self.python_exe, "-m", "pip", "install", "-U", "pyedb"], check=True)  # nosec

            print("Pyedb has been updated")
            self.clicked_refresh(need_restart=True)

    def get_pyaedt_branch(self):
        if not self.is_git_available():
            return

        response = messagebox.askyesno("Disclaimer", DISCLAIMER)

        if response:
            branch_name = self.pyaedt_branch_name.get()
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", f"git+https://github.com/ansys/pyaedt.git@{branch_name}"],
                check=True,
            )  # nosec
            self.clicked_refresh(need_restart=True)

    def get_pyedb_branch(self):
        if not self.is_git_available():
            return

        response = messagebox.askyesno("Disclaimer", DISCLAIMER)

        if response:
            branch_name = self.pyedb_branch_name.get()
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", f"git+https://github.com/ansys/pyedb.git@{branch_name}"],
                check=True,
            )  # nosec
            self.clicked_refresh(need_restart=True)

    def update_from_wheelhouse(self):
        def version_is_leq(version, other_version):
            version_parts = [int(part) for part in version.split(".")]
            target_parts = [int(part) for part in other_version.split(".")]
            if version_parts == target_parts:
                return True
            for v, t in zip(version_parts, target_parts):
                if v < t:
                    return True
                elif v > t:
                    return False

        file_selected = filedialog.askopenfilename(title="Select Wheelhouse")

        if file_selected:
            fpath = Path(file_selected)
            file_name = fpath.stem

            _, pyaedt_version, wh_pkg_type, _, os_system, _, wh_python_version = file_name.split("-")
            pyaedt_version = pyaedt_version.replace("v", "")

            msg = []
            correct_wheelhouse = file_name

            # Check Python version
            if not wh_python_version == self.python_version:
                msg.extend(
                    [
                        "Wrong Python version",
                        f"Wheelhouse: {wh_python_version}",
                        f"Expected version: {self.python_version}",
                    ]
                )
                correct_wheelhouse = correct_wheelhouse.replace(wh_python_version, self.python_version)

            # NOTE: For compatibility reasons, we compare with 'installer' install target
            # when PyAEDT's version is 0.15.3 or lower.
            if version_is_leq(pyaedt_version, "0.15.3"):
                if wh_pkg_type != "installer":
                    correct_wheelhouse = correct_wheelhouse.replace(f"-{wh_pkg_type}-", "-installer-")
                    msg.extend(["", "This wheelhouse doesn't contain required packages to add PyAEDT buttons."])

            # Check OS
            if os_system == "windows":
                if not is_windows:
                    msg.extend(["", "This wheelhouse is not compatible with your operating system."])
                    correct_wheelhouse = correct_wheelhouse.replace(f"-{os_system}-", "-windows-")
            else:
                if not is_linux:
                    msg.extend(["", "This wheelhouse is not compatible with your operating system."])
                    correct_wheelhouse = correct_wheelhouse.replace(f"-{os_system}-", "-ubuntu-")

            if msg:
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
                    "--force-reinstall",
                    "--no-cache-dir",
                    "--no-index",
                    f"--find-links=file:///{str(unzipped_path)}",
                    "pyaedt[all]",
                ],
                check=True,
            )  # nosec
            self.clicked_refresh(need_restart=True)

    def reset_pyaedt_buttons_in_aedt(self):
        def handle_remove_error(func, path, exc_info):
            # Attempt to fix permission issues
            import stat

            os.chmod(path, stat.S_IWRITE)  # Add write permission
            func(path)  # Retry the operation

        response = messagebox.askyesno("Confirm Action", "Are you sure you want to proceed?")

        if response:
            from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt

            add_pyaedt_to_aedt(self.aedt_version, self.personal_lib)
            messagebox.showinfo("Success", "PyAEDT panels updated in AEDT.")

    def clicked_refresh(self, need_restart=False):
        msg = [f"Venv path: {self.venv_path}", f"Python version: {self.python_version}"]
        msg = "\n".join(msg)
        self.venv_information.set(msg)

        if need_restart is False:
            self.pyaedt_info.set(f"PyAEDT: {self.pyaedt_version} (Latest {get_latest_version('pyaedt')})")
            self.pyedb_info.set(f"PyEDB: {self.pyedb_version} (Latest {get_latest_version('pyedb')})")
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

    aedtapp = ansys.aedt.core.Desktop(new_desktop=new_desktop, version=aedt_version, port=port, non_graphical=ng)
    personal_lib = aedtapp.personallib
    if release_desktop:
        aedtapp.release_desktop(close_project, close_on_exit)

    return {"desktop": aedtapp, "aedt_version": aedt_version, "personal_lib": personal_lib}


if __name__ == "__main__":
    kwargs = get_desktop_info()
    # Initialize tkinter root window and run the app
    root = tkinter.Tk()
    app = VersionManager(root, **kwargs)
    root.mainloop()
