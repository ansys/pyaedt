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
from pathlib import Path
import platform
import shutil
import subprocess  # nosec
import sys
import threading
import tkinter
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
        return os.path.join(self.venv_path, bin_dir, exe_name)

    @property
    def uv_exe(self):
        # 'uv' is named 'uv.exe' on Windows, 'uv' on POSIX and lives in the venv scripts/bin dir.
        bin_dir = "Scripts" if self.is_windows else "bin"
        uv_name = "uv.exe" if self.is_windows else "uv"
        return os.path.join(self.venv_path, bin_dir, uv_name)

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
        from ansys.aedt.core.extensions.misc import get_aedt_version
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
            if not os.path.exists(self.uv_exe):
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

    def activate_venv(self):
        """Prepare a subprocess environment that has the virtual environment activated.
        """
        try:
            scripts_dir = (
                os.path.join(self.venv_path, "Scripts") if self.is_windows else os.path.join(self.venv_path, "bin")
            )
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
        """Run pip preferring the 'uv' launcher and falling back to 'python -m pip'.

        Arguments:
            pip_args: list of arguments to pip after the pip keyword, e.g. ['install', '-U', 'pyaedt']
            capture_output: when True returns the stdout string (uses check_output)
            check: passed to subprocess.run when not capturing output
        """
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

    def update_and_reload(self, pip_args, modules_to_unload=None): # pragma: no cover
        """Attempt to release processes, unload modules, run pip, and
        reload the modules.
        """        
        # Confirm action
        response = messagebox.askyesno(
            "Confirm Action",
            "This will temporarily unload active modules, perform the "
            "installation, and reload them. Continue?"
        )
        if not response:
            return

        # Default modules to try unloading to free file handles
        modules = modules_to_unload or ["ansys.aedt.core", "pyedb"]

        # Attempt to unload modules in current process to free handles
        try:
            import gc as _gc
            import sys as _sys # nosec

            for m in modules:
                if m in _sys.modules:
                    try:
                        del _sys.modules[m]
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to remove module {m}: {e}")
            _gc.collect()
        except Exception as e:
            # Show error to inform the user that unloading modules failed
            messagebox.showerror("Error", f"Failed to unload modules: {e}")

        # Run pip install/upgrade
        try:
            self.run_uv_pip(pip_args)
        except Exception as exc:
            messagebox.showerror("Error: Installation Failed",
                               f"Installation failed: {exc}")
            return

        # Attempt to reimport the modules that were unloaded
        try:
            import importlib
            for m in modules:
                try:
                    importlib.import_module(m)
                except Exception as e:
                    # Module may not be available or have dependencies — show error
                    messagebox.showerror("Error", f"Failed to import module {m}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reimport modules: {e}")

        try:
            self.reset_pyaedt_buttons_in_aedt(confirm=False)
        except Exception:  # pragma: no cover
            messagebox.showwarning(
                "Warning",
                "PyAEDT panels could not be updated in AEDT. You may "
                "need to reset them manually.",
            )

        # Refresh the UI to show updated version information
        self.clicked_refresh(need_restart=True)

        # Inform user that update is complete
        try:
            messagebox.showinfo(
                "Message",
                "Update completed successfully. Module versions have "
                "been refreshed."
            )
        except Exception as e:
            # If showing the info fails, report it to the user
            messagebox.showerror("Error", f"Failed to show completion message: {e}")

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
                pip_args = ["install", f"pyaedt=={latest_version}"]
            else:
                pip_args = ["install", "-U", "pyaedt"]

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

    def update_all(self): # pragma: no cover
        """Update both pyaedt and pyedb together.

        This follows the same disclaimer and install flow as the individual update
        methods and will attempt to pin to the latest PyPI version when a downgrade
        is required.
        """
        response = messagebox.askyesno("Disclaimer", DISCLAIMER)

        if not response:
            return

        latest_pyaedt = get_latest_version("pyaedt")
        latest_pyedb = get_latest_version("pyedb")

        if latest_pyaedt == UNKNOWN_VERSION or latest_pyedb == UNKNOWN_VERSION:
            messagebox.showerror("Error: Installation Failed", "Could not retrieve latest versions from PyPI.")
            return

        pip_args = ["install"]

        # Decide pyaedt install args (pin if current > latest, else upgrade)
        try:
            if self.pyaedt_version > latest_pyaedt:
                pip_args.append(f"pyaedt=={latest_pyaedt}")
            else:
                pip_args.extend(["-U", "pyaedt"])
        except Exception:
            pip_args.extend(["-U", "pyaedt"])

        # Decide pyedb install args (pin if current > latest, else upgrade)
        try:
            if self.pyedb_version > latest_pyedb:
                pip_args.append(f"pyedb=={latest_pyedb}")
            else:
                pip_args.extend(["pyedb"])
        except Exception:
            pip_args.extend(["pyedb"])

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
                if not self.is_windows:
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

            self.run_uv_pip([
                "install",
                "--force-reinstall",
                "--no-cache-dir",
                "--no-index",
                f"--find-links={unzipped_path.as_uri()}",
                "pyaedt[all]",
            ])

            # Always reset PyAEDT panels after installing from wheelhouse
            try:
                self.reset_pyaedt_buttons_in_aedt(confirm=False)
            except Exception:  # pragma: no cover
                messagebox.showwarning(
                    "Warning",
                    "PyAEDT panels could not be updated in AEDT. You may need to reset them manually.",
                )

            self.clicked_refresh(need_restart=True)

    def reset_pyaedt_buttons_in_aedt(self, confirm=True):
        """Reset PyAEDT panels in AEDT.

        If confirm is True, prompt the user before proceeding and show success/error dialogs.
        If confirm is False, perform the reset silently (no confirmation dialog) and suppress dialogs on errors.
        """
        if confirm:
            response = messagebox.askyesno("Confirm Action", "Are you sure you want to proceed?")
            if not response:
                return

        try:
            from ansys.aedt.core.extensions.installer.pyaedt_installer import (
                add_pyaedt_to_aedt,
            )

            add_pyaedt_to_aedt(self.aedt_version, self.personal_lib)
            if confirm:
                messagebox.showinfo("Success", "PyAEDT panels updated in AEDT.")
        except Exception as e:  # pragma: no cover - best-effort panel reset
            if confirm:
                messagebox.showerror("Error", f"Failed to update PyAEDT panels: {e}")

    def get_installed_version(self, package_name):
        """Return the installed version of package_name inside the virtualenv.

        This runs the venv Python to query the package metadata so we can show
        the updated version without restarting the current process.
        """
        try:
            # Prefer importlib.metadata (Python 3.8+). Use venv python to inspect
            cmd = [self.python_exe, "-c", "import importlib.metadata as m; print(m.version(\"%s\"))" % package_name]
            out = subprocess.check_output(cmd, env=self.activated_env, stderr=subprocess.DEVNULL, text=True)  # nosec
            return out.strip()
        except Exception:
            try:
                # Fallback to 'pip show' and parse Version
                out = self.run_uv_pip(["show", package_name], capture_output=True)
                for line in out.splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
            except Exception:  # pragma: no cover
                return "Please restart"

    def clicked_refresh(self, need_restart=False):
        msg = [f"Venv path: {self.venv_path}", f"Python version: {self.python_version}"]
        msg = "\n".join(msg)
        self.venv_information.set(msg)

        if need_restart is False:
            self.pyaedt_info.set(f"PyAEDT: {self.pyaedt_version} (Latest {get_latest_version('pyaedt')})")
            self.pyedb_info.set(f"PyEDB: {self.pyedb_version} (Latest {get_latest_version('pyedb')})")
        else:
            # Try to detect the newly installed versions inside the venv so we can
            # display the updated version immediately without forcing a restart.
            try:
                pyaedt_installed = self.get_installed_version("pyaedt")
            except Exception:  # pragma: no cover
                pyaedt_installed = "Please restart"

            try:
                pyedb_installed = self.get_installed_version("pyedb")
            except Exception:  # pragma: no cover
                pyedb_installed = "Please restart"

            latest_pyaedt = get_latest_version("pyaedt")
            latest_pyedb = get_latest_version("pyedb")

            self.pyaedt_info.set(f"PyAEDT: {pyaedt_installed} (Latest {latest_pyaedt})")
            self.pyedb_info.set(f"PyEDB: {pyedb_installed} (Latest {latest_pyedb})")
            messagebox.showinfo("Message", "Done")
    def _on_close(self):
        """Best-effort cleanup when the extension window is closed.

        If a Desktop instance was provided, attempt to release it (without
        closing AEDT). Finally, destroy the Tk root window.
        """
        try:
            desktop_obj = getattr(self, "desktop", None)
            if desktop_obj is not None:
                try:
                    # Release desktop without closing projects or AEDT app.
                    desktop_obj.release_desktop(False, False)
                except Exception:
                    # Swallow all exceptions to avoid preventing the UI from closing.
                    logging.getLogger("Global").debug("Failed to release desktop", exc_info=True)
        finally:
            try:
                # Attempt to close the Tk window regardless of desktop release outcome.
                if getattr(self, "root", None) is not None:
                    self.root.destroy()
            except Exception:
                logging.getLogger("Global").debug("Failed to destroy root window", exc_info=True)

    def check_for_pyaedt_update_on_startup(self):
        """Spawn a background thread to check PyPI for a newer PyAEDT release."""
        def worker():
            log = logging.getLogger("Global")
            try:
                latest, declined_file = check_for_pyaedt_update(self.desktop.personallib)
                if not latest:
                    log.debug("PyAEDT update check: no prompt required or latest unavailable.")
                    return
                try:
                    self.root.after(
                        0,
                        lambda: self.show_pyaedt_update_notification(latest, declined_file)
                    )
                except Exception:
                    log.debug("PyAEDT update check: failed to schedule notification.", exc_info=True)
            except Exception:
                log.debug("PyAEDT update check: worker failed.", exc_info=True)

        threading.Thread(target=worker, daemon=True).start()

    def show_pyaedt_update_notification(self, latest_version: str, declined_file_path: Path): # pragma: no cover
        """Display a notification dialog informing the user about a new PyAEDT version."""
        try:
            dlg = tkinter.Toplevel(self.root)
            dlg.title("PyAEDT Update Available")
            dlg.resizable(False, False)

            # Center dialog
            try:
                self.root.update_idletasks()
                width, height = 500, 150
                x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
                y = self.root.winfo_rooty() + (self.root.winfo_height() - height) // 2
                dlg.geometry(f"{width}x{height}+{x}+{y}")
            except Exception:
                logging.getLogger("Global").debug("Failed to center update notification", exc_info=True)

            # Create frame for label and changelog button
            label_frame = ttk.Frame(dlg, style="PyAEDT.TFrame")
            label_frame.pack(
                padx=20, pady=(20, 10), expand=True, fill="both"
            )

            ttk.Label(
                label_frame,
                text=(
                    f"A new version of PyAEDT is available: "
                    f"{latest_version}\n"
                    "You can update it using the buttons in this "
                    "Version Manager."
                ),
                style="PyAEDT.TLabel",
                anchor="center",
                justify="center",
            ).pack(side="left", expand=True, fill="both")

            def open_changelog():
                try:
                    url = ("https://aedt.docs.pyansys.com/version/stable/"
                           "changelog.html")
                    webbrowser.open(str(url))
                    logging.getLogger("Global").info(
                        "Opened PyAEDT changelog."
                    )
                except Exception:
                    logging.getLogger("Global").debug(
                        "Failed to open changelog", exc_info=True
                    )

            changelog_btn = ttk.Button(
                label_frame,
                text="?",
                command=open_changelog,
                style="PyAEDT.TButton",
                width=3
            )
            changelog_btn.pack(side="right", padx=(5, 0))
            ToolTip(changelog_btn, "View changelog")

            btn_frame = ttk.Frame(dlg, style="PyAEDT.TFrame")
            btn_frame.pack(padx=10, pady=(0, 10), fill="x")

            def close_notification():
                # Save the declined version to avoid showing again
                try:
                    declined_file_path.parent.mkdir(parents=True, exist_ok=True)
                    declined_file_path.write_text(latest_version, encoding="utf-8")
                except Exception:
                    logging.getLogger("Global").debug(
                        "PyAEDT update notification: failed to record declined version.",
                        exc_info=True,
                    )
                dlg.destroy()

            ttk.Button(btn_frame, text="Close", command=close_notification, style="PyAEDT.TButton").pack(
                expand=True, fill="x", padx=5
            )

            dlg.transient(self.root)
            dlg.grab_set()
            self.root.wait_window(dlg)
        except Exception:
            logging.getLogger("Global").debug("PyAEDT update notification: failed to display.", exc_info=True)


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
    # Initialize tkinter root window and run the app
    desktop = get_desktop()
    root = tkinter.Tk()
    app = VersionManager(root, desktop)
    root.mainloop()
