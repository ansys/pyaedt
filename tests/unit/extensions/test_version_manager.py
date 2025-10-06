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
    """Create a VersionManager with UI fully stubbed so no real windows appear.

    Replace only the modules referenced inside version_manager (tkinter, ttk, PIL, messagebox)
    so other tests using real Tk aren’t affected.
    """
    from types import SimpleNamespace

    # --- Fake tkinter with required constants ---
    class _SV:
        def __init__(self, *a, **k):
            self._v = ""

        def set(self, v):
            self._v = v

        def get(self):
            return self._v

    fake_tkinter = SimpleNamespace(
        Tk=lambda *a, **k: MagicMock(),
        StringVar=_SV,
        # orientations
        HORIZONTAL=1,
        VERTICAL=2,
        # sides/fill/anchors (some are strings in Tk, but any value works for the mocks)
        LEFT="left",
        RIGHT="right",
        TOP="top",
        BOTTOM="bottom",
        X="x",
        Y="y",
        BOTH="both",
        N="n",
        S="s",
        E="e",
        W="w",
        NE="ne",
        NW="nw",
        SE="se",
        SW="sw",
        # reliefs
        FLAT="flat",
        RAISED="raised",
        SUNKEN="sunken",
        GROOVE="groove",
        RIDGE="ridge",
        # booleans
        TRUE=True,
        FALSE=False,
    )

    # Fake ttk (only what VersionManager touches)
    fake_ttk = SimpleNamespace(
        Style=lambda *a, **k: MagicMock(),
        PanedWindow=lambda *a, **k: MagicMock(),
        Notebook=lambda *a, **k: MagicMock(),
        Frame=lambda *a, **k: MagicMock(),
        Button=lambda *a, **k: MagicMock(),
        Label=lambda *a, **k: MagicMock(),
        Entry=lambda *a, **k: MagicMock(),
    )

    # Fake PIL as imported by version_manager
    fake_PIL = SimpleNamespace(
        Image=SimpleNamespace(open=lambda *a, **k: MagicMock()),
        ImageTk=SimpleNamespace(PhotoImage=lambda *a, **k: MagicMock()),
    )

    # --- Fake messagebox (don’t block) ---
    fake_messagebox = SimpleNamespace(
        showinfo=lambda *a, **k: None,
        showwarning=lambda *a, **k: None,
        # keep askyesno/showerror behavior overridable per-test
        showerror=vm.messagebox.showerror,
        askyesno=vm.messagebox.askyesno,
    )

    # Apply scoped patches (module-level, only inside version_manager)
    patch("ansys.aedt.core.extensions.installer.version_manager.tkinter", new=fake_tkinter).start()
    patch("ansys.aedt.core.extensions.installer.version_manager.ttk", new=fake_ttk).start()
    patch("ansys.aedt.core.extensions.installer.version_manager.PIL", new=fake_PIL).start()
    patch("ansys.aedt.core.extensions.installer.version_manager.messagebox", new=fake_messagebox).start()

    # Minimal UI object expected by VersionManager
    ui = MagicMock()
    ui.iconphoto = MagicMock()
    ui.title = MagicMock()
    ui.geometry = MagicMock()
    ui.configure = MagicMock()

    # Minimal desktop mock
    desktop = MagicMock()
    desktop.personallib = PERSONAL_LIB

    desktop.release_desktop = MagicMock()

    # Instantiate
    manager = vm.VersionManager(ui)
    manager.update_and_reload = MagicMock()

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
    manager.clicked_refresh(need_restart=True)
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

    def ok_run(cmd, **kwargs):
        class _CP:
            returncode = 0

        return _CP()

    mock_run.side_effect = ok_run
    manager.update_from_wheelhouse()
    assert mock_run.called


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
def test_update_pyaedt_flows(mock_showerror, mock_get_latest, mock_run, mock_askyesno):
    manager = _make_vm()

    # User declines disclaimer
    mock_askyesno.return_value = False

    def should_not_run(*a, **k):
        raise AssertionError("Should not run")

    mock_run.side_effect = should_not_run
    manager.update_pyaedt()

    # User accepts but latest unknown -> showerror
    mock_askyesno.return_value = True
    mock_get_latest.return_value = vm.UNKNOWN_VERSION
    mock_run.side_effect = lambda *a, **k: None
    manager.update_pyaedt()
    assert mock_showerror.called

    # User accepts and install path; test both branch comparisons
    mock_askyesno.return_value = True
    mock_get_latest.return_value = "1.0.0"
    # Simulate installed version > latest to force pinned install
    manager.get_installed_version = lambda pkg: "2.0.0"

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_pyaedt()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]  # First positional argument
    assert any("pyaedt==1.0.0" in str(x) for x in pip_args)

    # Simulate installed version <= latest to force upgrade
    manager.get_installed_version = lambda pkg: "1.0.0"
    manager.update_and_reload.reset_mock()
    manager.update_pyaedt()

    # Check that update_and_reload was called with upgrade arguments
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]  # First positional argument
    assert any("-U" in str(x) or "install" in str(x) for x in pip_args)


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
    manager.get_installed_version = lambda pkg: "2.0.0"

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_pyedb()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]  # First positional argument
    assert any("pyedb==1.0.0" in str(x) for x in pip_args) or any("-U" in str(x) for x in pip_args)


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showinfo")
@patch("ansys.aedt.core.extensions.installer.version_manager.VersionManager.is_git_available")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_get_branch_functions(mock_run, mock_askyesno, mock_is_git_available, _mock_showinfo):
    manager = _make_vm()

    # Early return when git is not available
    mock_is_git_available.return_value = False
    manager.get_pyaedt_branch()

    # User declines
    mock_is_git_available.return_value = True
    mock_askyesno.return_value = False
    manager.get_pyaedt_branch()

    # User accepts: ensure install command contains expected branch
    mock_askyesno.return_value = True
    manager.pyaedt_branch_name.set("feature/foo")

    # Prevent extra subprocess.run calls triggered by clicked_refresh
    manager.clicked_refresh = lambda need_restart: None

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.get_pyaedt_branch()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]  # First positional argument
    expected = "git+https://github.com/ansys/pyaedt.git@feature/foo"
    assert any(expected in str(x) for x in pip_args), f"Expected '{expected}' in pip_args, got: {pip_args!r}"


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showinfo")
@patch("ansys.aedt.core.extensions.installer.version_manager.VersionManager.is_git_available")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_get_pyedb_branch_functions(mock_run, mock_askyesno, mock_is_git_available, _mock_showinfo):
    manager = _make_vm()

    # Early return when git is not available
    mock_is_git_available.return_value = False
    manager.get_pyedb_branch()

    # User declines
    mock_is_git_available.return_value = True
    mock_askyesno.return_value = False
    manager.get_pyedb_branch()

    # User accepts: ensure install command contains expected branch
    mock_askyesno.return_value = True
    manager.pyedb_branch_name.set("feature/bar")

    # Prevent extra subprocess.run calls triggered by clicked_refresh
    manager.clicked_refresh = lambda need_restart: None

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.get_pyedb_branch()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    expected = "git+https://github.com/ansys/pyedb.git@feature/bar"
    assert any(expected in str(x) for x in pip_args), f"Expected '{expected}' in pip_args, got: {pip_args!r}"


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
def test_update_all_flows(mock_showerror, mock_get_latest, mock_askyesno):
    manager = _make_vm()

    # User declines disclaimer
    mock_askyesno.return_value = False
    manager.update_all()

    # User accepts but pyaedt latest unknown -> showerror
    mock_askyesno.return_value = True
    mock_get_latest.side_effect = lambda pkg: vm.UNKNOWN_VERSION if pkg == "pyaedt" else "1.0.0"
    manager.update_all()
    assert mock_showerror.called

    # User accepts but pyedb latest unknown -> showerror
    mock_showerror.reset_mock()
    mock_get_latest.side_effect = lambda pkg: "1.0.0" if pkg == "pyaedt" else vm.UNKNOWN_VERSION
    manager.update_all()
    assert mock_showerror.called

    # User accepts both versions - pin older pyaedt, upgrade pyedb
    mock_askyesno.return_value = True
    mock_get_latest.side_effect = lambda pkg: "1.0.0" if pkg == "pyaedt" else "2.0.0"
    # Simulate installed pyaedt > latest to force pinned install
    # Simulate installed pyedb <= latest to force upgrade
    manager.get_installed_version = lambda pkg: "2.0.0" if pkg == "pyaedt" else "1.5.0"

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_all()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("pyaedt==1.0.0" in str(x) for x in pip_args)
    assert any("pyedb" in str(x) for x in pip_args)

    # User accepts both versions available - both need upgrade
    mock_get_latest.side_effect = lambda pkg: "3.0.0" if pkg == "pyaedt" else "3.5.0"
    # Simulate installed versions <= latest to force upgrade for both
    manager.get_installed_version = lambda pkg: "2.0.0" if pkg == "pyaedt" else "2.5.0"

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_all()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("-U" in str(x) for x in pip_args) and any("pyaedt" in str(x) for x in pip_args)
    assert any("pyedb" in str(x) for x in pip_args)

    # Test exception handling during version comparison
    mock_get_latest.side_effect = lambda pkg: "1.0.0"
    # Make get_installed_version raise exception for testing

    def raise_exception(pkg):
        raise Exception("Version comparison failed")

    manager.get_installed_version = raise_exception

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_all()

    # Check update_and_reload called with fallback upgrade args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("-U" in str(x) for x in pip_args) and any("pyaedt" in str(x) for x in pip_args)
    assert any("pyedb" in str(x) for x in pip_args)
