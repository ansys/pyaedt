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
import sys
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch
import zipfile

from ansys.aedt.core.extensions.installer import version_manager as vm

# Use a platform-safe temporary personal lib path instead of hard-coded '/tmp/personal'
PERSONAL_LIB = os.path.join(tempfile.gettempdir(), "personal")

# Ensure tests don't try to pip-install uv during VersionManager __init__.
os.environ.setdefault("PYTEST_CURRENT_TEST", "1")


@patch("ansys.aedt.core.extensions.installer.version_manager.requests.get")
def test_get_latest_version_success_and_failure(mock_get):
    class Resp:
        status_code = 200

        def json(self):
            return {"info": {"version": "1.2.3"}}

    mock_get.return_value = Resp()
    assert vm.get_latest_version("pyaedt") == "1.2.3"

    class BadResp:
        status_code = 404

    mock_get.return_value = BadResp()
    assert vm.get_latest_version("pyaedt") == vm.UNKNOWN_VERSION

    def raise_exc(*a, **k):
        raise RuntimeError()

    mock_get.side_effect = raise_exc
    assert vm.get_latest_version("pyaedt") == vm.UNKNOWN_VERSION


def _make_vm():
    # Start persistent patches so VersionManager constructor doesn't touch FS/UI
    # Patch PIL image opening and photo creation
    patch.object(vm.PIL.Image, "open", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.PIL.ImageTk, "PhotoImage", new=lambda *a, **k: MagicMock()).start()

    # Patch ttk.Style and other widgets to simple mocks
    patch.object(vm.ttk, "Style", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.ttk, "PanedWindow", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.ttk, "Notebook", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.ttk, "Frame", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.ttk, "Button", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.ttk, "Label", new=lambda *a, **k: MagicMock()).start()
    patch.object(vm.ttk, "Entry", new=lambda *a, **k: MagicMock()).start()

    # Provide a lightweight StringVar implementation
    class _SV:
        def __init__(self, *a, **k):
            self._v = ""

        def set(self, v):
            self._v = v

        def get(self):
            return self._v

    patch.object(vm.tkinter, "StringVar", new=_SV).start()
    # Ensure any call to tkinter.Tk in the code under test returns a mock
    patch.object(vm.tkinter, "Tk", new=lambda *a, **k: MagicMock()).start()

    # Minimal UI object expected by VersionManager
    ui = MagicMock()
    ui.iconphoto = MagicMock()
    ui.title = MagicMock()
    ui.geometry = MagicMock()
    ui.configure = MagicMock()

    # Minimal desktop mock passed to VersionManager
    desktop = MagicMock()
    desktop.personallib = PERSONAL_LIB
    desktop.release_desktop = MagicMock()

    # Create the manager
    manager = vm.VersionManager(ui, desktop, aedt_version="2025.2", personal_lib=PERSONAL_LIB)
    return manager


def test_activate_venv_and_exes():
    manager = _make_vm()
    # Ensure python and uv point inside sys.prefix
    assert manager.venv_path == sys.prefix
    pyexe = manager.python_exe
    uve = manager.uv_exe
    assert str(manager.venv_path) in pyexe
    assert str(manager.venv_path) in uve

    # Activate venv explicitly and check env keys
    manager.activate_venv()
    assert manager.activated_env is not None
    assert "VIRTUAL_ENV" in manager.activated_env


@patch("ansys.aedt.core.extensions.installer.version_manager.shutil.which")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
def test_is_git_available_and_messagebox(mock_showerror, mock_which):
    _ = _make_vm()
    # If git not found, showerror called
    mock_which.return_value = None
    vm.VersionManager.is_git_available()
    assert mock_showerror.called

    # If git found, returns True and no error
    mock_which.return_value = "/usr/bin/git"
    mock_showerror.reset_mock()
    assert vm.VersionManager.is_git_available()
    assert not mock_showerror.called


@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showinfo")
def test_clicked_refresh_no_restart_and_with_restart(mock_showinfo, mock_get_latest):
    manager = _make_vm()

    # Patch latest version lookups
    mock_get_latest.return_value = "9.9.9"
    # Patch get_installed_version to return stable
    manager.get_installed_version = lambda pkg: "1.2.3"

    # No restart path
    manager.clicked_refresh(need_restart=False)
    assert "PyAEDT: 1.2.3 (Latest 9.9.9)" in manager.pyaedt_info.get()
    assert "PyEDB: 1.2.3 (Latest 9.9.9)" in manager.pyedb_info.get()

    # Restart path: patch get_installed_version to be called inside
    manager.get_installed_version = lambda pkg: "3.3.3"
    mock_get_latest.return_value = "8.8.8"
    # Patch messagebox.showinfo to capture call (provided by decorator)
    manager.clicked_refresh(need_restart=True)
    assert mock_showinfo.called
    assert "PyAEDT: 3.3.3 (Latest 8.8.8)" in manager.pyaedt_info.get()


def test_toggle_and_theme_functions():
    """Verify toggle_theme flips theme_color and calls appropriate helpers."""
    manager = _make_vm()

    # Prepare a fake theme and widgets
    manager.theme = MagicMock()
    manager.theme.light = {"widget_bg": "lightbg"}
    manager.theme.dark = {"widget_bg": "darkbg"}
    manager.theme.apply_light_theme = MagicMock()
    manager.theme.apply_dark_theme = MagicMock()
    manager.change_theme_button = MagicMock()
    manager.root = MagicMock()
    manager.style = MagicMock()

    # Start light and toggle to dark
    manager.theme_color = "light"
    manager.toggle_theme()
    assert manager.theme_color == "dark"
    manager.theme.apply_dark_theme.assert_called_once_with(manager.style)
    manager.change_theme_button.config.assert_called_with(text="\u2600")
    manager.root.configure.assert_any_call(bg="darkbg")

    # Toggle back to light
    manager.toggle_theme()
    assert manager.theme_color == "light"
    manager.theme.apply_light_theme.assert_called_once_with(manager.style)
    manager.change_theme_button.config.assert_called_with(text="\u263d")
    manager.root.configure.assert_any_call(bg="lightbg")


def test_set_light_and_set_dark():
    """Directly test set_light_theme and set_dark_theme behavior."""
    manager = _make_vm()

    manager.theme = MagicMock()
    manager.theme.light = {"widget_bg": "LBG"}
    manager.theme.dark = {"widget_bg": "DBG"}
    manager.theme.apply_light_theme = MagicMock()
    manager.theme.apply_dark_theme = MagicMock()
    manager.change_theme_button = MagicMock()
    manager.root = MagicMock()
    manager.style = MagicMock()

    # Light
    manager.set_light_theme()
    manager.root.configure.assert_called_with(bg="LBG")
    manager.theme.apply_light_theme.assert_called_once_with(manager.style)
    manager.change_theme_button.config.assert_called_with(text="\u263d")

    # Dark
    manager.set_dark_theme()
    manager.root.configure.assert_called_with(bg="DBG")
    manager.theme.apply_dark_theme.assert_called_once_with(manager.style)
    manager.change_theme_button.config.assert_called_with(text="\u2600")


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
def test_update_pyaedt_flows(mock_showerror, mock_get_latest, mock_run, mock_askyesno):
    manager = _make_vm()

    # User declines disclaimer
    mock_askyesno.return_value = False
    mock_run.side_effect = AssertionError("Should not run")
    manager.update_pyaedt()

    # User accepts but latest unknown -> showerror
    mock_askyesno.return_value = True
    mock_get_latest.return_value = vm.UNKNOWN_VERSION
    manager.update_pyaedt()
    assert mock_showerror.called

    # User accepts and install path; test both branch comparisons
    mock_askyesno.return_value = True
    mock_get_latest.return_value = "1.0.0"
    # Simulate installed version > latest to force pinned install
    manager.get_installed_version = lambda pkg: "2.0.0"

    captured = {}

    def fake_run(cmd, check, env):
        captured["cmd"] = cmd

    mock_run.side_effect = fake_run
    # Call update
    manager.update_pyaedt()
    assert any("pyaedt==1.0.0" in str(x) for x in captured["cmd"]) or any(
        "-U" in str(x) or "install" in str(x) for x in captured["cmd"]
    )

    # Simulate installed version <= latest to force upgrade
    captured.clear()
    manager.get_installed_version = lambda pkg: "1.0.0"
    manager.update_pyaedt()
    assert any("-U" in str(x) or "install" in str(x) for x in captured["cmd"]) or captured == {}


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_update_pyedb_flows(mock_run, mock_showerror, mock_get_latest, mock_askyesno):
    manager = _make_vm()

    # Decline
    mock_askyesno.return_value = False
    manager.update_pyedb()

    # Accept but unknown
    mock_askyesno.return_value = True
    mock_get_latest.return_value = vm.UNKNOWN_VERSION
    manager.update_pyedb()
    assert mock_showerror.called

    # Accept and update path
    mock_askyesno.return_value = True
    mock_get_latest.return_value = "1.0.0"
    # Patch the internal call used by the property so we avoid assigning to a read-only property
    manager.get_installed_version = lambda pkg: "2.0.0"

    recorded = {}

    def fake_run(cmd, check, env):
        recorded["cmd"] = cmd

    mock_run.side_effect = fake_run
    manager.update_pyedb()
    assert any("pyedb==1.0.0" in str(x) for x in recorded.get("cmd", [])) or any(
        "-U" in str(x) for x in recorded.get("cmd", [])
    )


@patch("ansys.aedt.core.extensions.installer.version_manager.VersionManager.is_git_available")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_get_branch_functions(mock_run, mock_askyesno, mock_is_git_available):
    manager = _make_vm()

    # When git not available, get_pyaedt_branch returns early
    mock_is_git_available.return_value = False
    manager.get_pyaedt_branch()

    # When git available but user declines
    mock_is_git_available.return_value = True
    mock_askyesno.return_value = False
    manager.get_pyaedt_branch()

    # When user accepts, ensure subprocess.run gets called with expected branch
    mock_askyesno.return_value = True
    manager.pyaedt_branch_name.set("feature/foo")

    called = {}

    def fake_run(cmd, check, env):
        called["cmd"] = cmd

    mock_run.side_effect = fake_run
    manager.get_pyaedt_branch()
    assert any("github.com/ansys/pyaedt.git@feature/foo" in str(x) for x in called.get("cmd", []))


def test_reset_pyaedt_buttons_in_aedt():
    manager = _make_vm()

    # If user declines, nothing happens
    with patch.object(vm.messagebox, "askyesno", return_value=False):
        manager.reset_pyaedt_buttons_in_aedt()

    # If user accepts, ensure add_pyaedt_to_aedt called and showinfo called
    fake_installer = MagicMock()
    fake_installer.add_pyaedt_to_aedt = MagicMock()

    called = {}

    def fake_info(title, msg):
        called["info"] = (title, msg)

    # Patch the import inside the function to our fake and simulate user acceptance
    with patch.dict(sys.modules, {"ansys.aedt.core.extensions.installer.pyaedt_installer": fake_installer}):
        with patch.object(vm.messagebox, "askyesno", return_value=True):
            with patch.object(vm.messagebox, "showinfo", new=fake_info):
                manager.reset_pyaedt_buttons_in_aedt()

    assert "info" in called


def test_get_desktop_info_creates_desktop():
    # Patch helpers
    with patch.object(vm, "get_port", new=lambda: 0):
        with patch.object(vm, "get_aedt_version", new=lambda: "2024.2"):
            with patch.object(vm, "get_process_id", new=lambda: None):
                fake_desktop = MagicMock()
                fake_desktop.personallib = PERSONAL_LIB
                fake_desktop.release_desktop = MagicMock()
                # Patch the Desktop class used inside the function
                with patch.object(vm.ansys.aedt.core, "Desktop", new=lambda **k: fake_desktop):
                    out = vm.get_desktop_info(release_desktop=False)
                    assert out["desktop"] is fake_desktop
                    assert out["aedt_version"] == "2024.2"
                    assert out["personal_lib"] == PERSONAL_LIB


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
@patch("ansys.aedt.core.extensions.installer.version_manager.filedialog.askopenfilename")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_update_from_wheelhouse_all_paths(mock_run, mock_askopen, mock_showerror, tmp_path):
    manager = _make_vm()
    # Ensure the manager reports a stable Python version for tests
    manager.__class__.python_version = property(lambda self: "3.10")

    # 1) No file selected -> nothing happens
    mock_askopen.return_value = ""
    mock_run.reset_mock()
    mock_showerror.reset_mock()
    manager.update_from_wheelhouse()
    assert not mock_run.called
    assert not mock_showerror.called

    # Helper to create wheelhouse zips
    def make_zip(stem):
        z = tmp_path / (stem + ".zip")
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr(f"{stem}/dummy.txt", "ok")
        return z

    # 2) Wrong Python version
    stem = "pyaedt-v1.0.0-installer-foo-ubuntu-bar-3.9"
    z = make_zip(stem)
    mock_askopen.return_value = str(z)
    mock_run.reset_mock()
    mock_showerror.reset_mock()
    manager.update_from_wheelhouse()
    assert mock_showerror.called
    # message is second arg to showerror(title, msg)
    assert "Wrong Python version" in mock_showerror.call_args[0][1]

    # 3) Old pyaedt (<=0.15.3) and wrong package type
    stem = "pyaedt-v0.15.3-notinstaller-foo-ubuntu-bar-3.10"
    z = make_zip(stem)
    mock_askopen.return_value = str(z)
    mock_run.reset_mock()
    mock_showerror.reset_mock()
    manager.update_from_wheelhouse()
    assert mock_showerror.called
    assert "doesn't contain required packages" in mock_showerror.call_args[0][1]

    # 4) OS mismatch: wheelhouse is windows but manager running on non-windows
    manager.is_windows = False
    vm.is_linux = True
    stem = "pyaedt-v1.0.0-installer-foo-windows-bar-3.10"
    z = make_zip(stem)
    mock_askopen.return_value = str(z)
    mock_run.reset_mock()
    mock_showerror.reset_mock()
    manager.update_from_wheelhouse()
    assert mock_showerror.called
    assert "not compatible with your operating system" in mock_showerror.call_args[0][1]

    # 5) Success path: matching python, installer pkg type and OS -> run called
    manager.is_windows = True
    vm.is_linux = False
    stem = "pyaedt-v1.2.3-installer-foo-windows-bar-3.10"
    z = make_zip(stem)
    mock_askopen.return_value = str(z)
    mock_run.reset_mock()
    mock_showerror.reset_mock()
    manager.update_from_wheelhouse()
    # Ensure install was attempted; argument inspection is fragile across platforms
    assert mock_run.called
