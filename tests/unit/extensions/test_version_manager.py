# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
from ansys.aedt.core.extensions.misc import get_latest_version

# Use a platform-safe temporary personal lib path instead of hard-coded '/tmp/personal'
PERSONAL_LIB = os.path.join(tempfile.gettempdir(), "personal")

# Ensure tests don't try to pip-install uv during VersionManager __init__.
os.environ.setdefault("PYTEST_CURRENT_TEST", "1")


@patch("ansys.aedt.core.extensions.misc.requests.get")
def test_get_latest_version_success_and_failure(mock_get) -> None:
    class Resp:
        status_code = 200

        def json(self):
            return {"info": {"version": "1.2.3"}}

    mock_get.return_value = Resp()
    assert get_latest_version("pyaedt") == "1.2.3"

    class BadResp:
        status_code = 404

    mock_get.return_value = BadResp()
    assert get_latest_version("pyaedt") == "Unknown"

    def raise_exc(*a, **k):
        raise RuntimeError()

    mock_get.side_effect = raise_exc
    assert get_latest_version("pyaedt") == "Unknown"


def _make_vm():
    """Create a VersionManager with UI fully stubbed so no real windows appear.

    Replace only the modules referenced inside version_manager (tkinter, ttk, PIL, messagebox)
    so other tests using real Tk aren’t affected.
    """
    from types import SimpleNamespace

    # --- Fake tkinter with required constants ---
    class _SV:
        def __init__(self, *a, **k) -> None:
            self._v = ""

        def set(self, v) -> None:
            self._v = v

        def get(self):
            return self._v

    fake_tkinter = SimpleNamespace(
        Tk=lambda *a, **k: MagicMock(),
        Widget=object,
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
    manager = vm.VersionManager(ui, desktop)
    manager.update_and_reload = MagicMock()

    return manager


def test_activate_venv_and_exes() -> None:
    manager = _make_vm()
    # Ensure python and uv point inside sys.prefix
    assert manager.venv_path == sys.prefix
    pyexe = manager.python_exe
    assert str(manager.venv_path) in pyexe

    # Activate venv explicitly and check env keys
    manager.activate_venv()
    assert manager.activated_env is not None
    assert "VIRTUAL_ENV" in manager.activated_env


@patch("ansys.aedt.core.extensions.installer.version_manager.shutil.which")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
def test_is_git_available_and_messagebox(mock_showerror, mock_which) -> None:
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
def test_clicked_refresh_no_restart_and_with_restart(mock_showinfo, mock_get_latest) -> None:
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


def test_toggle_and_theme_functions() -> None:
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


def test_set_light_and_set_dark() -> None:
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


def test_show_loading() -> None:
    """Test show_loading method."""
    manager = _make_vm()

    # Create a mock label
    mock_label = MagicMock()
    manager.loading_labels["test_key"] = mock_label
    manager.root = MagicMock()

    # Call show_loading with valid key
    manager.show_loading("test_key")

    # Verify label was configured with loading emoji
    mock_label.config.assert_called_once_with(text="⏳")
    # Verify root.update_idletasks was called
    manager.root.update_idletasks.assert_called_once()


def test_show_loading_invalid_key() -> None:
    """Test show_loading with invalid key does nothing."""
    manager = _make_vm()
    manager.root = MagicMock()

    # Call show_loading with non-existent key
    manager.show_loading("nonexistent_key")

    # Verify root.update_idletasks was not called
    manager.root.update_idletasks.assert_not_called()


def test_hide_loading() -> None:
    """Test hide_loading method."""
    manager = _make_vm()

    # Create a mock label
    mock_label = MagicMock()
    manager.loading_labels["test_key"] = mock_label
    manager.root = MagicMock()

    # Call hide_loading with valid key
    manager.hide_loading("test_key")

    # Verify label was configured with empty string
    mock_label.config.assert_called_once_with(text="")
    # Verify root.update_idletasks was called
    manager.root.update_idletasks.assert_called_once()


def test_hide_loading_invalid_key() -> None:
    """Test hide_loading with invalid key does nothing."""
    manager = _make_vm()
    manager.root = MagicMock()

    # Call hide_loading with non-existent key
    manager.hide_loading("nonexistent_key")

    # Verify root.update_idletasks was not called
    manager.root.update_idletasks.assert_not_called()


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
@patch("ansys.aedt.core.extensions.installer.version_manager.filedialog.askopenfilename")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_update_from_wheelhouse_all_paths(mock_run, mock_askopen, mock_showerror, tmp_path) -> None:
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
    error_msg = mock_showerror.call_args[0][1]
    assert (
        "Wheelhouse missing required installer packages" in error_msg
        or "This wheelhouse is not compatible with your operating system." in error_msg
    )

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
    assert "This wheelhouse is not compatible with your operating system." in mock_showerror.call_args[0][1]

    # 5) Success path: matching python, installer pkg type and OS
    # run_pip should be called directly (not update_and_reload)
    manager.is_windows = True
    vm.is_linux = False
    stem = "pyaedt-v1.2.3-installer-foo-windows-bar-3.10"
    z = make_zip(stem)
    mock_askopen.return_value = str(z)
    mock_run.reset_mock()
    mock_showerror.reset_mock()

    with patch.object(manager, "run_pip") as mock_run_pip:
        manager.update_from_wheelhouse()

        assert mock_run_pip.called
        pip_args = mock_run_pip.call_args[0][0]
        assert "install" in pip_args
        assert "--force-reinstall" in pip_args
        assert any("pyaedt[all]" in str(x) for x in pip_args)


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
def test_update_pyaedt_flows(mock_showerror, mock_get_latest, mock_run, mock_askyesno) -> None:
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
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("pyaedt[all]==1.0.0" in str(x) for x in pip_args)

    # Simulate installed version <= latest to force upgrade
    manager.get_installed_version = lambda pkg: "1.0.0"
    manager.update_and_reload.reset_mock()
    manager.update_pyaedt()

    # Check that update_and_reload was called with upgrade arguments
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("-U" in str(x) or "install" in str(x) for x in pip_args)


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_latest_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showerror")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_update_pyedb_flows(mock_run, mock_showerror, mock_get_latest, mock_askyesno) -> None:
    manager = _make_vm()

    # User declines disclaimer
    mock_askyesno.return_value = False

    def should_not_run(*a, **k):
        raise AssertionError("Should not run")

    mock_run.side_effect = should_not_run
    manager.update_pyedb()

    # User accepts but latest unknown -> showerror
    mock_askyesno.return_value = True
    mock_get_latest.return_value = vm.UNKNOWN_VERSION
    mock_run.side_effect = lambda *a, **k: None
    manager.update_pyedb()
    assert mock_showerror.called

    # User accepts and install path; test both branch comparisons
    mock_askyesno.return_value = True
    mock_get_latest.return_value = "1.0.0"
    # Simulate installed version > latest to force pinned install
    manager.get_installed_version = lambda pkg: "2.0.0"

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_pyedb()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("pyedb==1.0.0" in str(x) for x in pip_args)

    # Simulate installed version <= latest to force upgrade
    manager.get_installed_version = lambda pkg: "1.0.0"
    manager.update_and_reload.reset_mock()
    manager.update_pyedb()

    # Check that update_and_reload was called with upgrade arguments
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("-U" in str(x) or "install" in str(x) for x in pip_args)


@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.showinfo")
@patch("ansys.aedt.core.extensions.installer.version_manager.VersionManager.is_git_available")
@patch("ansys.aedt.core.extensions.installer.version_manager.messagebox.askyesno")
@patch("ansys.aedt.core.extensions.installer.version_manager.subprocess.run")
def test_get_branch_functions(mock_run, mock_askyesno, mock_is_git_available, _mock_showinfo) -> None:
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
def test_get_pyedb_branch_functions(mock_run, mock_askyesno, mock_is_git_available, _mock_showinfo) -> None:
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
def test_update_all_flows(mock_showerror, mock_get_latest, mock_askyesno) -> None:
    manager = _make_vm()

    # User declines disclaimer
    mock_askyesno.return_value = False
    manager.update_all()

    # Test when pyaedt version is unknown - should show error and NOT call update_and_reload
    mock_askyesno.return_value = True

    def side_effect_unknown_pyaedt(pkg):
        return vm.UNKNOWN_VERSION if pkg == "pyaedt" else "1.0.0"

    mock_get_latest.side_effect = side_effect_unknown_pyaedt
    manager.update_and_reload.reset_mock()
    mock_showerror.reset_mock()
    manager.update_all()
    assert not manager.update_and_reload.called
    assert mock_showerror.called

    mock_askyesno.return_value = True

    def side_effect_unknown_pyedb(pkg):
        return "1.0.0" if pkg == "pyaedt" else vm.UNKNOWN_VERSION

    mock_get_latest.side_effect = side_effect_unknown_pyedb
    manager.update_and_reload.reset_mock()
    mock_showerror.reset_mock()
    manager.update_all()
    assert not manager.update_and_reload.called
    assert mock_showerror.called

    # User accepts both versions - pin older pyaedt, upgrade pyedb
    mock_askyesno.return_value = True

    def side_effect_versions(pkg):
        return "1.0.0" if pkg == "pyaedt" else "2.0.0"

    mock_get_latest.side_effect = side_effect_versions
    # Simulate installed pyaedt > latest to force pinned install
    # Simulate installed pyedb <= latest to force upgrade

    def installed_versions(pkg):
        return "2.0.0" if pkg == "pyaedt" else "1.5.0"

    manager.get_installed_version = installed_versions

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_all()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    assert any("pyaedt[all]==1.0.0" in str(x) for x in pip_args)
    assert any("pyedb" in str(x) for x in pip_args)

    # User accepts both versions available - both need upgrade

    def side_effect_higher_versions(pkg):
        return "3.0.0" if pkg == "pyaedt" else "3.5.0"

    mock_get_latest.side_effect = side_effect_higher_versions
    # Simulate installed versions <= latest to force upgrade for both

    def installed_lower_versions(pkg):
        return "2.0.0" if pkg == "pyaedt" else "2.5.0"

    manager.get_installed_version = installed_lower_versions

    # Reset the mock to capture calls
    manager.update_and_reload.reset_mock()
    manager.update_all()

    # Check that update_and_reload was called with correct pip_args
    assert manager.update_and_reload.called
    pip_args = manager.update_and_reload.call_args[0][0]
    pyaedt_found = any("-U" in str(x) for x in pip_args) and any("pyaedt" in str(x) for x in pip_args)
    assert pyaedt_found
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
    pyaedt_found = any("-U" in str(x) for x in pip_args) and any("pyaedt" in str(x) for x in pip_args)
    assert pyaedt_found
    assert any("pyedb" in str(x) for x in pip_args)


def test_on_close_normal_operation() -> None:
    """Test _on_close method under normal operation."""
    manager = _make_vm()

    # Mock desktop and root objects
    manager.desktop = MagicMock()
    manager.root = MagicMock()

    # Call _on_close
    manager._on_close()

    # Verify desktop.release_desktop was called with correct arguments
    manager.desktop.release_desktop.assert_called_once_with(False, False)

    # Verify root.destroy was called
    manager.root.destroy.assert_called_once()


def test_on_close_desktop_exception() -> None:
    """Test _on_close method when desktop raises an exception."""
    manager = _make_vm()

    # Mock desktop to raise exception and root
    manager.desktop = MagicMock()
    manager.desktop.release_desktop.side_effect = Exception("Desktop release failed")
    manager.root = MagicMock()

    # Call _on_close - should not raise exception
    manager._on_close()

    # Verify desktop.release_desktop was called
    manager.desktop.release_desktop.assert_called_once_with(False, False)

    # Verify root.destroy was still called despite desktop exception
    manager.root.destroy.assert_called_once()


def test_on_close_root_exception() -> None:
    """Test _on_close method when root.destroy raises an exception."""
    manager = _make_vm()

    # Mock desktop and root that raises exception
    manager.desktop = MagicMock()
    manager.root = MagicMock()
    manager.root.destroy.side_effect = Exception("Root destroy failed")

    # Call _on_close - should not raise exception
    manager._on_close()

    # Verify desktop.release_desktop was called
    manager.desktop.release_desktop.assert_called_once_with(False, False)

    # Verify root.destroy was called
    manager.root.destroy.assert_called_once()


def test_on_close_no_desktop() -> None:
    """Test _on_close method when desktop is None."""
    manager = _make_vm()

    # Set desktop to None and mock root
    manager.desktop = None
    manager.root = MagicMock()

    # Call _on_close
    manager._on_close()

    # Verify root.destroy was called
    manager.root.destroy.assert_called_once()


def test_on_close_no_root() -> None:
    """Test _on_close method when root is None."""
    manager = _make_vm()

    # Mock desktop and set root to None
    manager.desktop = MagicMock()
    manager.root = None

    # Call _on_close
    manager._on_close()

    # Verify desktop.release_desktop was called
    manager.desktop.release_desktop.assert_called_once_with(False, False)


def test_on_close_both_exceptions() -> None:
    """Test _on_close when both desktop and root raise exceptions."""
    manager = _make_vm()

    # Mock both to raise exceptions
    manager.desktop = MagicMock()
    manager.desktop.release_desktop.side_effect = Exception("Desktop failed")
    manager.root = MagicMock()
    manager.root.destroy.side_effect = Exception("Root failed")

    # Call _on_close - should not raise exception
    manager._on_close()

    # Verify both were called despite exceptions
    manager.desktop.release_desktop.assert_called_once_with(False, False)
    manager.root.destroy.assert_called_once()


@patch("ansys.aedt.core.extensions.installer.version_manager.threading.Thread")
@patch("ansys.aedt.core.extensions.installer.version_manager.check_for_pyaedt_update")
def test_check_for_pyaedt_update_on_startup_success(mock_check_update, mock_thread) -> None:
    """Test check_for_pyaedt_update_on_startup when update is available."""
    manager = _make_vm()

    # Mock check_for_pyaedt_update to return an update
    mock_check_update.return_value = ("1.5.0", "/path/to/declined.txt")

    # Mock root.after to capture the scheduled callback
    manager.root.after = MagicMock()

    # Call the method
    manager.check_for_pyaedt_update_on_startup()

    # Verify thread was created and started
    assert mock_thread.called
    thread_args = mock_thread.call_args
    assert thread_args[1]["daemon"] is True

    # Get the worker function and call it
    worker_func = thread_args[1]["target"]
    worker_func()

    # Verify check_for_pyaedt_update was called with personal lib path
    mock_check_update.assert_called_once_with(manager.desktop.personallib)

    # Verify root.after was called to schedule notification
    manager.root.after.assert_called_once()
    assert manager.root.after.call_args[0][0] == 0  # First argument should be 0


@patch("ansys.aedt.core.extensions.installer.version_manager.threading.Thread")
@patch("ansys.aedt.core.extensions.installer.version_manager.check_for_pyaedt_update")
def test_check_for_pyaedt_update_on_startup_no_update(mock_check_update, mock_thread) -> None:
    """Test check_for_pyaedt_update_on_startup when no update is needed."""
    manager = _make_vm()

    # Mock check_for_pyaedt_update to return no update
    mock_check_update.return_value = (None, "/path/to/declined.txt")

    # Mock root.after to verify it's not called
    manager.root.after = MagicMock()

    # Call the method
    manager.check_for_pyaedt_update_on_startup()

    # Get the worker function and call it
    worker_func = mock_thread.call_args[1]["target"]
    worker_func()

    # Verify check_for_pyaedt_update was called
    mock_check_update.assert_called_once_with(manager.desktop.personallib)

    # Verify root.after was NOT called since no update available
    manager.root.after.assert_not_called()


@patch("ansys.aedt.core.extensions.installer.version_manager.threading.Thread")
@patch("ansys.aedt.core.extensions.installer.version_manager.check_for_pyaedt_update")
@patch("ansys.aedt.core.extensions.installer.version_manager.logging.getLogger")
def test_check_for_pyaedt_update_on_startup_exception_in_worker(
    mock_get_logger, mock_check_update, mock_thread
) -> None:
    """Test check_for_pyaedt_update_on_startup when worker encounters exception."""
    manager = _make_vm()

    # Mock logger
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Mock check_for_pyaedt_update to raise exception
    mock_check_update.side_effect = Exception("Check update failed")

    # Call the method
    manager.check_for_pyaedt_update_on_startup()

    # Get the worker function and call it
    worker_func = mock_thread.call_args[1]["target"]
    worker_func()

    # Verify exception was logged
    mock_logger.debug.assert_called_with("PyAEDT update check: worker failed.", exc_info=True)


@patch("ansys.aedt.core.extensions.installer.version_manager.threading.Thread")
@patch("ansys.aedt.core.extensions.installer.version_manager.check_for_pyaedt_update")
@patch("ansys.aedt.core.extensions.installer.version_manager.logging.getLogger")
def test_check_for_pyaedt_update_on_startup_exception_in_after(mock_get_logger, mock_check_update, mock_thread) -> None:
    """Test check_for_pyaedt_update_on_startup when root.after fails."""
    manager = _make_vm()

    # Mock logger
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Mock check_for_pyaedt_update to return an update
    mock_check_update.return_value = ("1.5.0", "/path/to/declined.txt")

    # Mock root.after to raise exception
    manager.root.after = MagicMock(side_effect=Exception("After failed"))

    # Call the method
    manager.check_for_pyaedt_update_on_startup()

    # Get the worker function and call it
    worker_func = mock_thread.call_args[1]["target"]
    worker_func()

    mock_check_update.assert_called_once_with(manager.desktop.personallib)


@patch("ansys.aedt.core.extensions.installer.version_manager.get_port")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_aedt_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_process_id")
@patch("ansys.aedt.core.extensions.installer.version_manager.ansys.aedt.core.Desktop")
def test_get_desktop_with_existing_process(
    mock_desktop_class, mock_get_process_id, mock_get_aedt_version, mock_get_port
) -> None:
    """Test get_desktop when AEDT process already exists."""
    mock_get_port.return_value = 12345
    mock_get_aedt_version.return_value = "2024.1"
    mock_get_process_id.return_value = 9876
    mock_desktop_instance = MagicMock()
    mock_desktop_class.return_value = mock_desktop_instance
    result = vm.get_desktop()
    mock_desktop_class.assert_called_once_with(new_desktop=False, version="2024.1", port=12345, non_graphical=False)
    assert result == mock_desktop_instance


@patch("ansys.aedt.core.extensions.installer.version_manager.get_port")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_aedt_version")
@patch("ansys.aedt.core.extensions.installer.version_manager.get_process_id")
@patch("ansys.aedt.core.extensions.installer.version_manager.ansys.aedt.core.Desktop")
def test_get_desktop_without_existing_process(
    mock_desktop_class, mock_get_process_id, mock_get_aedt_version, mock_get_port
) -> None:
    """Test get_desktop when no AEDT process exists."""
    mock_get_port.return_value = 54321
    mock_get_aedt_version.return_value = "2023.2"
    mock_get_process_id.return_value = None
    mock_desktop_instance = MagicMock()
    mock_desktop_class.return_value = mock_desktop_instance
    result = vm.get_desktop()
    mock_desktop_class.assert_called_once_with(new_desktop=True, version="2023.2", port=54321, non_graphical=True)
    assert result == mock_desktop_instance
