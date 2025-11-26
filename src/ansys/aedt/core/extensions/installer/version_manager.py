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

import logging
import os
import platform
import shutil
import subprocess  # nosec
import sys
import tempfile
import threading
import tkinter
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import webbrowser
import zipfile

import defusedxml
import PIL.Image
import PIL.ImageTk

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ToolTip, check_for_pyaedt_update, get_aedt_version, get_latest_version, get_port, get_process_id
from ansys.aedt.core.generic.general_methods import is_linux

defusedxml.defuse_stdlib()

DISCLAIMER = (
    "This script will download and install certain third-party software and/or "
    "open-source software (collectively, 'Third-Party Software'). Such Third-Party "
    "Software is subject to separate terms and conditions and not the terms of your "
    "Ansys software license agreement. Ansys does not warrant or support such "
    "Third-Party Software.\n"
    "Do you want to proceed?\n"
)
UNKNOWN_VERSION = "Unknown"

# Update script templates
WINDOWS_UPDATE_SCRIPT_TEMPLATE = """@echo off
title Ansys Version Manager Update
mode con: cols=120 lines=30
color 0B
cls
echo ==============================================================================
echo.
echo                     Ansys Version Manager - Update Utility
echo.
echo ==============================================================================
echo.
echo Waiting for Version Manager (PID {current_pid}) to close...
:loop
tasklist /FI "PID eq {current_pid}" 2>NUL | find /I /N "{current_pid}">NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 >nul
    goto :loop
)
echo.
echo Version Manager closed.
echo.
echo ------------------------------------------------------------------------------
echo Starting Update Process...
echo Command: "{uv_exe}" pip {uv_pip_args_str}
echo ------------------------------------------------------------------------------
echo.
"{uv_exe}" pip {uv_pip_args_str}
if %errorlevel% neq 0 (
    echo.
    echo ------------------------------------------------------------------------------
    echo [WARNING] UV failed, falling back to pip...
    echo Command: "{python_exe}" -m pip {pip_args_str}
    echo ------------------------------------------------------------------------------
    echo.
    "{python_exe}" -m pip {pip_args_str}
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo ==============================================================================
        echo [ERROR] Update failed with error code %errorlevel%
        echo ==============================================================================
        pause
        exit /b %errorlevel%
    )
)
color 0A
echo.
echo ==============================================================================
echo [SUCCESS] Update Complete.
echo ==============================================================================
echo.
echo Restarting Version Manager in 5 seconds...
timeout /t 5
start "" "{python_exe}" "{script_path}"
del "%~f0"
exit
"""

LINUX_UPDATE_SCRIPT_TEMPLATE = """#!/bin/bash
GREEN='\\033[0;32m'
RED='\\033[0;31m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

clear
echo -e "${{BLUE}}==============================================================================${{NC}}"
echo -e "${{BLUE}}                    Ansys Version Manager - Update Utility${{NC}}"
echo -e "${{BLUE}}==============================================================================${{NC}}"
echo ""
echo "Waiting for Version Manager (PID {current_pid}) to close..."
while kill -0 {current_pid} 2>/dev/null; do
    sleep 1
done
echo ""
echo "Version Manager closed."
echo ""
echo "------------------------------------------------------------------------------"
echo "Starting Update Process..."
echo "Command: '{uv_exe}' pip {uv_pip_args_str}"
echo "------------------------------------------------------------------------------"
echo ""
"{uv_exe}" pip {uv_pip_args_str}
if [ $? -ne 0 ]; then
    echo ""
    echo "------------------------------------------------------------------------------"
    echo -e "${{YELLOW}}[WARNING] UV failed, falling back to pip...${{NC}}"
    echo "Command: '{python_exe}' -m pip {pip_args_str}"
    echo "------------------------------------------------------------------------------"
    echo ""
    "{python_exe}" -m pip {pip_args_str}
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${{RED}}==============================================================================${{NC}}"
        echo -e "${{RED}}[ERROR] Update failed!${{NC}}"
        echo -e "${{RED}}==============================================================================${{NC}}"
        read -p "Press enter to close"
        exit 1
    fi
fi
echo ""
echo -e "${{GREEN}}==============================================================================${{NC}}"
echo -e "${{GREEN}}[SUCCESS] Update Complete.${{NC}}"
echo -e "${{GREEN}}==============================================================================${{NC}}"
echo ""
echo "Restarting Version Manager..."
sleep 2
"{python_exe}" "{script_path}" &
rm "$0"
exit
"""

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
        # Use the venv "Scripts" on Windows and "bin" on POSIX; choose platform-appropriate executable name.
        bin_dir = "Scripts" if self.is_windows else "bin"
        exe_name = "python.exe" if self.is_windows else "python"
        return str(Path(self.venv_path) / bin_dir / exe_name)

    @property
    def uv_exe(self):
        # 'uv' is named 'uv.exe' on Windows, 'uv' on POSIX and lives in the venv scripts/bin dir.
        bin_dir = "Scripts" if self.is_windows else "bin"
        uv_name = "uv.exe" if self.is_windows else "uv"
        return str(Path(self.venv_path) / bin_dir / uv_name)

    @property
    def python_version(self):
        temp = platform.python_version().split(".")[0:2]
        return ".".join(temp)

    @property
    def pyaedt_version(self):
        return self.get_installed_version("pyaedt")

    @property
    def pyedb_version(self):
        return self.get_installed_version("pyedb")

    @property
    def aedt_version(self):
        return get_aedt_version()

    @property
    def personal_lib(self):
        return self.desktop.personallib

    def __init__(self, ui, desktop):
        from ansys.aedt.core.extensions.misc import ExtensionTheme

        self.desktop = desktop
        self.is_linux = is_linux
        self.is_windows = not is_linux
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

        # Prepare subprocess environment so the venv is effectively activated for all runs
        self.activated_env = None
        self.activate_venv()

        # Install uv if not present
        if "PYTEST_CURRENT_TEST" not in os.environ: # pragma: no cover
            if not Path(self.uv_exe).exists():
                print("Installing uv...")
                subprocess.run([self.python_exe, "-m", "pip", "install", "uv"], check=True, env=self.activated_env)  # nosec

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
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Check for PyAEDT updates on startup
        self.check_for_pyaedt_update_on_startup()

    def toggle_theme(self):
        if self.theme_color == "light":
            self.set_dark_theme()
            self.theme_color = "dark"
        else:
            self.set_light_theme()
            self.theme_color = "light"

    def set_light_theme(self):
        self.root.configure(bg=self.theme.light["widget_bg"])
        self.theme.apply_light_theme(self.style)
        self.change_theme_button.config(text="\u263d")

    def set_dark_theme(self):
        self.root.configure(bg=self.theme.dark["widget_bg"])
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
            buttons = [
                ["Update from wheelhouse", self.update_from_wheelhouse],
                ["Update All", self.update_all],
            ]
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

        frame0 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)
        frame1 = ttk.Frame(parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=0)

        frame0.pack(padx=5, pady=5)
        frame1.pack(padx=5, pady=5)

        create_ui_pyaedt(frame0)
        create_ui_pyedb(frame1)

    @staticmethod
    def is_git_available():
        res = shutil.which("git") is not None
        if not res:
            messagebox.showerror("Error: Git Not Found", "Git does not seem to be installed or is not accessible.")
        return res

    def activate_venv(self):
        """Prepare a subprocess environment that has the virtual environment activated.
        """
        try:
            if self.is_windows:
                scripts_dir = str(Path(self.venv_path) / "Scripts")
            else:
                scripts_dir = str(Path(self.venv_path) / "bin")
            env = os.environ.copy()
            # Prepend venv scripts/bin to PATH so executables from the venv are preferred
            env["PATH"] = scripts_dir + os.pathsep + env.get("PATH", "")
            # Mark the virtual environment
            env["VIRTUAL_ENV"] = self.venv_path
            # Unset PYTHONHOME if set to avoid mixing environments
            env.pop("PYTHONHOME", None)
            self.activated_env = env
        except Exception:  # pragma: no cover
            # Fallback to the current environment to avoid breaking functionality
            self.activated_env = os.environ.copy()

    def run_uv_pip(self, pip_args, capture_output=False, check=True):
        """Run pip preferring the 'uv' launcher."""
        try:
            cmd = [self.uv_exe, "pip"] + pip_args
            cmd = [arg.replace("-U", "--upgrade") for arg in cmd]
            if capture_output:
                return subprocess.check_output(cmd, env=self.activated_env, stderr=subprocess.DEVNULL, text=True)  # nosec
            else:
                subprocess.run(cmd, check=check, env=self.activated_env)  # nosec
        except Exception:
            # Fallback to python -m pip which may be necessary in restricted environments
            cmd = [self.python_exe, "-m", "pip"] + pip_args
            if capture_output:
                return subprocess.check_output(cmd, env=self.activated_env, stderr=subprocess.DEVNULL, text=True)  # nosec
            else:
                subprocess.run(cmd, check=check, env=self.activated_env)  # nosec

    def _create_windows_update_script(self, pip_args):
        current_pid = os.getpid()
        script_path = sys.argv[0]

        uv_args = [arg.replace("-U", "--upgrade") for arg in pip_args]
        uv_pip_args_str = " ".join([f'"{arg}"' if " " in arg else arg for arg in uv_args])

        pip_args_str = " ".join([f'"{arg}"' if " " in arg else arg for arg in pip_args])

        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.bat')
        content = WINDOWS_UPDATE_SCRIPT_TEMPLATE.format(
            current_pid=current_pid,
            uv_exe=self.uv_exe,
            uv_pip_args_str=uv_pip_args_str,
            pip_args_str=pip_args_str,
            python_exe=self.python_exe,
            script_path=script_path
        )
        tf.write(content)
        tf.close()
        return tf.name

    def _create_linux_update_script(self, pip_args):
        current_pid = os.getpid()
        script_path = sys.argv[0]
        
        # Create uv-compatible args (use --upgrade instead of -U)
        uv_args = [arg.replace("-U", "--upgrade") for arg in pip_args]
        uv_pip_args_str = " ".join([f'"{arg}"' if " " in arg else arg for arg in uv_args])
        
        # Keep original args for pip fallback (pip supports both -U and --upgrade)
        pip_args_str = " ".join([f'"{arg}"' if " " in arg else arg for arg in pip_args])

        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh')
        content = LINUX_UPDATE_SCRIPT_TEMPLATE.format(
            current_pid=current_pid,
            uv_exe=self.uv_exe,
            uv_pip_args_str=uv_pip_args_str,
            pip_args_str=pip_args_str,
            python_exe=self.python_exe,
            script_path=script_path
        )
        tf.write(content)
        tf.close()
        os.chmod(tf.name, 0o750)  # nosec B103
        return tf.name

    def update_and_reload(self, pip_args):
        response = messagebox.askyesno(
            "Confirm Update",
            "The Version Manager must close to perform this update safely.\n\n"
            "A separate terminal window will open to process the update.\n"
            "The application will restart automatically when finished.\n\n"
            "Proceed?"
        )
        if not response:
            return

        try:
            if self.is_windows:
                updater_script = self._create_windows_update_script(pip_args)
            else:
                updater_script = self._create_linux_update_script(pip_args)
            
            # Release Desktop resources before closing
            if self.desktop:
                try:
                    self.desktop.release_desktop(False, False)
                except Exception as ex:
                    logging.getLogger("Global").debug(
                        "Failed to release desktop: %s", ex
                    )
            
            if self.is_windows:
                # Flags to detach the process and break away from the parent job object
                # CREATE_NEW_CONSOLE (0x10) + CREATE_BREAKAWAY_FROM_JOB (0x01000000)
                flags = 0x00000010 | 0x01000000
                try:
                    subprocess.Popen(  # nosec B603 B607
                        ["cmd.exe", "/c", updater_script],
                        creationflags=flags,
                        close_fds=True
                    )
                except OSError:
                    # Fallback if BREAKAWAY is not allowed
                    subprocess.Popen(  # nosec B603 B607
                        ["cmd.exe", "/c", updater_script],
                        creationflags=0x00000010,
                        close_fds=True
                    )
            else:
                subprocess.Popen(  # nosec B603 B607
                    ["x-terminal-emulator", "-e", updater_script],
                    preexec_fn=os.setsid
                )

            self.root.destroy()
            sys.exit(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initiate update: {e}")

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
                pip_args = ["install", f"pyaedt[all]=={latest_version}"]
            else:
                pip_args = ["install", "-U", "pyaedt[all]"]

            self.update_and_reload(pip_args)

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
                pip_args = ["install", f"pyedb=={latest_version}"]
            else:
                pip_args = ["install", "-U", "pyedb"]

            self.update_and_reload(pip_args)

    def update_all(self):
        response = messagebox.askyesno("Disclaimer", DISCLAIMER)
        if not response:
            return

        latest_pyaedt = get_latest_version("pyaedt")
        latest_pyedb = get_latest_version("pyedb")

        pip_args = ["install"]

        try:
            if latest_pyaedt != UNKNOWN_VERSION and self.pyaedt_version > latest_pyaedt:
                pip_args.append(f"pyaedt[all]=={latest_pyaedt}")
            else:
                pip_args.extend(["-U", "pyaedt[all]"])
        except Exception:
            pip_args.extend(["-U", "pyaedt[all]"])

        try:
            if latest_pyedb != UNKNOWN_VERSION and self.pyedb_version > latest_pyedb:
                pip_args.append(f"pyedb=={latest_pyedb}")
            else:
                pip_args.append("pyedb")
        except Exception:
            pip_args.append("pyedb")

        self.update_and_reload(pip_args)

    def get_pyaedt_branch(self):
        if not self.is_git_available():
            return
        response = messagebox.askyesno("Disclaimer", DISCLAIMER)
        if response:
            branch_name = self.pyaedt_branch_name.get()
            pip_args = ["install", f"git+https://github.com/ansys/pyaedt.git@{branch_name}"]
            self.update_and_reload(pip_args)

    def get_pyedb_branch(self):
        if not self.is_git_available():
            return
        response = messagebox.askyesno("Disclaimer", DISCLAIMER)
        if response:
            branch_name = self.pyedb_branch_name.get()
            pip_args = ["install", f"git+https://github.com/ansys/pyedb.git@{branch_name}"]
            self.update_and_reload(pip_args)

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
            return False

        file_selected = filedialog.askopenfilename(title="Select Wheelhouse")

        if file_selected:
            fpath = Path(file_selected)
            file_name = fpath.stem

            try:
                parts = file_name.split("-")
                pyaedt_version = parts[1].replace("v", "")
                wh_pkg_type = parts[2]
                wh_python_version = parts[-1]
                os_system = parts[4]
            except IndexError:
                messagebox.showerror("Error", "Invalid Wheelhouse filename format.")
                return

            msg = []
            correct_wheelhouse = file_name

            if wh_python_version != self.python_version:
                msg.extend([
                    "Wrong Python version",
                    f"Wheelhouse: {wh_python_version}",
                    f"Expected version: {self.python_version}"
                ])
                correct_wheelhouse = correct_wheelhouse.replace(wh_python_version, self.python_version)

            if version_is_leq(pyaedt_version, "0.15.3"):
                if wh_pkg_type != "installer":
                    correct_wheelhouse = correct_wheelhouse.replace(f"-{wh_pkg_type}-", "-installer-")
                    msg.extend(["", "Wheelhouse missing required installer packages."])

            if os_system == "windows":
                if not self.is_windows:
                    msg.extend(["", "Incompatible OS (Windows vs Linux)."])
            else:
                if not is_linux:
                    msg.extend(["", "Incompatible OS (Linux vs Windows)."])

            if msg:
                msg.extend(["", f"Please download {correct_wheelhouse}."])
                messagebox.showerror("Compatibility Error", "\n".join(msg))
                return

            unzipped_path = fpath.parent / fpath.stem
            if unzipped_path.exists():
                shutil.rmtree(unzipped_path, ignore_errors=True)
            
            try:
                with zipfile.ZipFile(fpath, "r") as zip_ref:
                    zip_ref.extractall(unzipped_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to unzip wheelhouse: {e}")
                return

            pip_args = [
                "install",
                "--force-reinstall",
                "--no-cache-dir",
                "--no-index",
                f"--find-links={unzipped_path.as_uri()}",
                "pyaedt[all]",
            ]
            
            self.update_and_reload(pip_args)

    def get_installed_version(self, package_name):
        try:
            cmd = [self.python_exe, "-c", "import importlib.metadata as m; print(m.version(\"%s\"))" % package_name]
            out = subprocess.check_output(cmd, env=self.activated_env, stderr=subprocess.DEVNULL, text=True)  # nosec B603
            return out.strip()
        except Exception:
            try:
                out = self.run_uv_pip(["show", package_name], capture_output=True)
                for line in out.splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
            except Exception:
                return UNKNOWN_VERSION

    def clicked_refresh(self, need_restart=False):
        msg = [f"Venv path: {self.venv_path}", f"Python version: {self.python_version}"]
        msg = "\n".join(msg)
        self.venv_information.set(msg)

        latest_pyaedt = get_latest_version("pyaedt")
        latest_pyedb = get_latest_version("pyedb")
        
        self.pyaedt_info.set(f"PyAEDT: {self.pyaedt_version} (Latest {latest_pyaedt})")
        self.pyedb_info.set(f"PyEDB: {self.pyedb_version} (Latest {latest_pyedb})")

        if need_restart:
            messagebox.showinfo("Message", "Done")

    def _on_close(self):
        try:
            desktop_obj = getattr(self, "desktop", None)
            if desktop_obj is not None:
                try:
                    desktop_obj.release_desktop(False, False)
                except Exception:
                    logging.getLogger("Global").debug("Failed to release desktop", exc_info=True)
        finally:
            try:
                if getattr(self, "root", None) is not None:
                    self.root.destroy()
            except Exception:
                logging.getLogger("Global").debug("Failed to destroy root window", exc_info=True)

    def check_for_pyaedt_update_on_startup(self):
        def worker():
            log = logging.getLogger("Global")
            try:
                latest, declined_file = check_for_pyaedt_update(self.desktop.personallib)
                if not latest:
                    return
                try:
                    self.root.after(
                        0,
                        lambda: self.show_pyaedt_update_notification(latest, declined_file)
                    )
                except Exception as ex:
                    log.debug("Failed to schedule update notification: %s", ex)
            except Exception:
                log.debug("PyAEDT update check: worker failed.", exc_info=True)

        threading.Thread(target=worker, daemon=True).start()

    def show_pyaedt_update_notification(self, latest_version: str, declined_file_path: Path):
        try:
            dlg = tkinter.Toplevel(self.root)
            dlg.title("Update Available")
            dlg.resizable(False, False)
            
            width, height = 500, 150
            x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
            y = self.root.winfo_rooty() + (self.root.winfo_height() - height) // 2
            dlg.geometry(f"{width}x{height}+{x}+{y}")

            label_frame = ttk.Frame(dlg, style="PyAEDT.TFrame")
            label_frame.pack(padx=20, pady=(20, 10), expand=True, fill="both")

            ttk.Label(
                label_frame,
                text=(f"A new version of PyAEDT is available: {latest_version}\n"),
                style="PyAEDT.TLabel",
                anchor="center",
                justify="center",
            ).pack(side="left", expand=True, fill="both")

            btn_frame = ttk.Frame(dlg, style="PyAEDT.TFrame")
            btn_frame.pack(padx=10, pady=(0, 10), fill="x")

            def close_notification():
                try:
                    declined_file_path.parent.mkdir(parents=True, exist_ok=True)
                    declined_file_path.write_text(latest_version, encoding="utf-8")
                except Exception as ex:
                    logging.getLogger("Global").debug(
                        "Failed to save declined version: %s", ex
                    )
                dlg.destroy()

            ttk.Button(btn_frame, text="Close", command=close_notification, style="PyAEDT.TButton").pack(
                expand=True, fill="x", padx=5
            )

            dlg.transient(self.root)
            dlg.grab_set()
            self.root.wait_window(dlg)
        except Exception:
            logging.getLogger("Global").debug("Notification error.", exc_info=True)


def get_desktop():
    port = get_port()
    aedt_version = get_aedt_version()
    aedt_process_id = get_process_id()

    if aedt_process_id is not None:
        new_desktop = False
        ng = False
    else:
        new_desktop = True
        ng = True

    aedtapp = ansys.aedt.core.Desktop(new_desktop=new_desktop, version=aedt_version, port=port, non_graphical=ng)
    return aedtapp


if __name__ == "__main__": # pragma: no cover
    desktop = get_desktop()
    root = tkinter.Tk()
    app = VersionManager(root, desktop)
    root.mainloop()