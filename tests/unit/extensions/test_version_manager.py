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

# -*- coding: utf-8 -*-
import os
import platform
import tkinter
from unittest.mock import MagicMock
from unittest.mock import patch
import zipfile

import pytest

import ansys  # noqa: F401  (needed for monkeypatching Desktop)
from ansys.aedt.core.extensions.installer import version_manager as vm
from ansys.aedt.core.generic.general_methods import is_linux


# Provide a lightweight variable class to avoid tkinter dependency
class _Var:
    def __init__(self, value=""):
        self._v = value

    def set(self, value):  # pragma: no cover - trivial
        self._v = value

    def get(self):  # pragma: no cover - trivial
        return self._v


# Helper lambdas/functions to keep lines short


def _yes(*a, **k):  # pragma: no cover - trivial
    return True


def _none(*a, **k):  # pragma: no cover - trivial
    return None


def _latest(ver):  # pragma: no cover - trivial
    return lambda name: ver


@pytest.fixture(autouse=True)
def mock_tk_and_env(monkeypatch):
    """Mock tkinter/ttk/PIL so VersionManager.__init__ can run in tests."""
    # Prevent uv installation logic from running in tests
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")

    # Mock tkinter.Tk so any created root is a MagicMock with needed methods
    fake_tk = MagicMock()
    fake_tk.iconphoto = MagicMock()
    fake_tk.title = MagicMock()
    fake_tk.geometry = MagicMock()
    fake_tk.withdraw = MagicMock()
    fake_tk.destroy = MagicMock()
    monkeypatch.setattr(tkinter, "Tk", lambda *a, **k: fake_tk)

    # Replace tkinter.StringVar used in the version_manager module with lightweight var
    monkeypatch.setattr(vm.tkinter, "StringVar", _Var)

    # Mock ttk.Style on the version_manager module so its Style returns MagicMock
    monkeypatch.setattr(vm.ttk, "Style", lambda *a, **k: MagicMock())

    # Mock common ttk widgets used during initialization to simple factories
    for name in ("Frame", "PanedWindow", "Notebook", "Entry", "Label", "Button"):
        monkeypatch.setattr(vm.ttk, name, lambda *a, **k: MagicMock())

    # Mock PIL.Image.open and PhotoImage on the version_manager module
    monkeypatch.setattr(vm.PIL.Image, "open", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.PIL.ImageTk, "PhotoImage", lambda *a, **k: MagicMock())

    yield


@pytest.fixture
def root():
    return MagicMock()


@pytest.fixture
def simple_desktop(tmp_path):
    d = MagicMock()
    d.aedt_version_id = "2025.2"
    d.personallib = str(tmp_path / "personal")
    d.logger = MagicMock()
    return d


def test_get_latest_version_success_and_failure(monkeypatch):
    # success
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {"info": {"version": "1.2.3"}}
    monkeypatch.setattr(
        vm.requests,
        "get",
        lambda url, timeout=3: fake_resp,
    )  # noqa: E501
    assert vm.get_latest_version("pyaedt") == "1.2.3"

    # non-200
    fake_resp.status_code = 404
    assert vm.get_latest_version("pyaedt") == vm.UNKNOWN_VERSION

    # exception
    def raise_exc(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr(vm.requests, "get", raise_exc)
    assert vm.get_latest_version("pyaedt") == vm.UNKNOWN_VERSION


def test_is_git_available_and_activate_venv(monkeypatch, root, tmp_path):
    # Git not available
    monkeypatch.setattr(vm.shutil, "which", lambda name: None)
    with patch.object(vm.messagebox, "showerror") as mock_err:
        assert vm.VersionManager.is_git_available() is False
        mock_err.assert_called_once()

    # Git available
    monkeypatch.setattr(
        vm.shutil,
        "which",
        lambda name: "C:/Program Files/git/bin/git",
    )
    assert vm.VersionManager.is_git_available() is True

    # activate_venv: ensure PATH is prefixed with venv Scripts
    mgr = vm.VersionManager(root, MagicMock(), "2025.2", str(tmp_path))
    scripts_dir = os.path.join(mgr.venv_path, "Scripts")
    assert mgr.activated_env["VIRTUAL_ENV"] == mgr.venv_path
    assert mgr.activated_env["PATH"].startswith(scripts_dir)


def test_update_pyaedt_calls_pip(monkeypatch, root, simple_desktop, tmp_path):
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    # Simulate installed version greater than latest -> pin to exact
    monkeypatch.setattr(vm, "get_latest_version", _latest("1.0.0"))  # noqa: E501
    monkeypatch.setattr(vm.messagebox, "askyesno", _yes)  # noqa: E501
    # Prevent any info dialogs from showing during the test
    monkeypatch.setattr(vm.messagebox, "showinfo", _none)
    with patch.object(
        mgr,
        "get_installed_version",
        return_value="2.0.0",
    ):
        with patch.object(vm.subprocess, "run") as mock_run:
            mgr.update_pyaedt()
            mock_run.assert_called()


def test_update_pyedb_calls_pip(monkeypatch, root, simple_desktop, tmp_path):
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    monkeypatch.setattr(vm, "get_latest_version", _latest("1.0.0"))  # noqa: E501
    monkeypatch.setattr(vm.messagebox, "askyesno", _yes)  # noqa: E501
    # Prevent any info dialogs from showing during the test
    monkeypatch.setattr(vm.messagebox, "showinfo", _none)
    with patch.object(
        mgr,
        "get_installed_version",
        return_value="2.0.0",
    ):
        with patch.object(vm.subprocess, "run") as mock_run:
            mgr.update_pyedb()
            mock_run.assert_called()


def test_update_from_wheelhouse_no_selection(root, simple_desktop, tmp_path):
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    with patch.object(
        vm.filedialog,
        "askopenfilename",
        return_value="",
    ):
        # Nothing should happen and no exception
        mgr.update_from_wheelhouse()


def test_reset_pyaedt_buttons_in_aedt_invokes_installer(root, simple_desktop, tmp_path):
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    with patch.object(vm.messagebox, "askyesno", return_value=True):
        with patch("ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt") as mock_add:
            with patch.object(vm.messagebox, "showinfo") as mock_info:
                mgr.reset_pyaedt_buttons_in_aedt()
                mock_add.assert_called_once()
                mock_info.assert_called_once()


def test_get_installed_version_various_paths(monkeypatch, root, simple_desktop, tmp_path):
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    # Case 1: importlib.metadata path works
    with patch.object(
        vm.subprocess,
        "check_output",
        return_value="1.2.3\n",
    ):
        assert mgr.get_installed_version("pyaedt") == "1.2.3"

    # Case 2: fallback to pip show
    def side_effect(cmd, env=None, stderr=None, text=None):
        # First call raise, second returns pip show like output
        if "-c" in cmd:
            raise RuntimeError("no importlib")
        return "Name: pyaedt\nVersion: 4.5.6\n"

    monkeypatch.setattr(vm.subprocess, "check_output", side_effect)
    assert mgr.get_installed_version("pyaedt") == "4.5.6"

    # Case 3: both methods fail
    monkeypatch.setattr(
        vm.subprocess,
        "check_output",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert mgr.get_installed_version("pyaedt") == "Please restart"


def test_clicked_refresh_updates_strings(monkeypatch, root, simple_desktop, tmp_path):
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    monkeypatch.setattr(vm, "get_latest_version", _latest("9.9.9"))
    with patch.object(
        mgr,
        "get_installed_version",
        return_value="3.3.3",
    ):
        mgr.clicked_refresh(need_restart=False)
        assert "PyAEDT: 3.3.3" in mgr.pyaedt_info.get()

    # need_restart True path
    with patch.object(
        mgr,
        "get_installed_version",
        return_value="7.7.7",
    ):
        with patch.object(vm.messagebox, "showinfo") as mock_info:
            mgr.clicked_refresh(need_restart=True)
            mock_info.assert_called_once()
            assert "7.7.7" in mgr.pyaedt_info.get()


def test_get_desktop_info(monkeypatch, tmp_path):
    # Cover get_desktop_info path with process id None
    monkeypatch.setattr(vm, "get_port", lambda: 1234)
    monkeypatch.setattr(vm, "get_aedt_version", lambda: "2025.2")
    monkeypatch.setattr(vm, "get_process_id", lambda: None)

    created = []

    def desktop_factory(new_desktop, version, port, non_graphical):
        m = MagicMock()
        m.personallib = str(tmp_path / "personal")
        m.release_desktop = MagicMock()
        m.new_desktop = new_desktop
        m.version = version
        m.port = port
        m.non_graphical = non_graphical
        created.append(m)
        return m

    monkeypatch.setattr(ansys.aedt.core, "Desktop", desktop_factory)
    info = vm.get_desktop_info(release_desktop=True)
    assert "desktop" in info
    assert "aedt_version" in info
    assert "personal_lib" in info
    assert created
    assert created[0].new_desktop is True
    assert created[0].non_graphical is True
    created[0].release_desktop.assert_called_once()


def test_update_from_wheelhouse_valid(monkeypatch, root, simple_desktop, tmp_path):
    pyver = ".".join(platform.python_version().split(".")[:2])
    os_tag = "windows" if vm.is_windows else "ubuntu"
    fname = f"wh-v1.0.0-full-x-{os_tag}-x-{pyver}.zip"
    zpath = tmp_path / fname
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("dummy.txt", "content")

    monkeypatch.setattr(
        vm.filedialog,
        "askopenfilename",
        lambda **k: str(zpath),
    )  # noqa: E501
    monkeypatch.setattr(vm.messagebox, "showerror", MagicMock())
    # Prevent any info/done dialogs from showing during the test
    monkeypatch.setattr(vm.messagebox, "showinfo", _none)
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    with patch.object(vm.subprocess, "run") as mock_run:
        mgr.update_from_wheelhouse()
        mock_run.assert_called()
        vm.messagebox.showerror.assert_not_called()


def test_toggle_theme_switches(monkeypatch, root, simple_desktop, tmp_path):
    vm.root = MagicMock()
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    mgr.style = MagicMock()
    mgr.theme = MagicMock()
    mgr.theme.light = {"widget_bg": "lightbg"}
    mgr.theme.dark = {"widget_bg": "darkbg"}
    mgr.change_theme_button = MagicMock()

    mgr.theme_color = "light"
    mgr.toggle_theme()
    assert mgr.theme_color == "dark"
    mgr.change_theme_button.config.assert_called_with(text="\u2600")

    mgr.change_theme_button.config.reset_mock()
    mgr.toggle_theme()
    assert mgr.theme_color == "light"
    mgr.change_theme_button.config.assert_called_with(text="\u263d")


def test_init_runs_and_creates_ui(monkeypatch, root, simple_desktop, tmp_path):
    # Prevent network and subprocess calls during initialization
    monkeypatch.setattr(vm.VersionManager, "get_installed_version", lambda self, name: "0.0.0")
    monkeypatch.setattr(vm, "get_latest_version", lambda name: "9.9.9")
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    # Basic checks: branch names default to 'main' and venv info was set
    assert mgr.pyaedt_branch_name.get() == "main"
    assert mgr.pyedb_branch_name.get() == "main"
    assert "Venv path" in mgr.venv_information.get()


def test_ui_creation_methods(monkeypatch, root, simple_desktop, tmp_path):
    # Prevent network and subprocess calls during initialization
    monkeypatch.setattr(vm.VersionManager, "get_installed_version", lambda self, name: "0.0.0")
    monkeypatch.setattr(vm, "get_latest_version", lambda name: "9.9.9")
    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))

    # Explicitly call UI creation helpers to increase coverage
    mgr.create_button_menu()
    assert mgr.change_theme_button is not None

    parent = MagicMock()
    mgr.create_ui_basic(parent)
    mgr.create_ui_advanced(parent)

    # Ensure the change_theme_button supports config
    assert hasattr(mgr.change_theme_button, "config")


def _make_wh_zip(tmp_path, pyaedt_version, wh_pkg_type, os_system, pyver="3.10"):
    fname = f"wh-{pyaedt_version}-{wh_pkg_type}-x-{os_system}-x-{pyver}.zip"
    zpath = tmp_path / fname
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("dummy.txt", "content")
    return zpath


def test_update_from_wheelhouse_incorrect_type_triggers_error(monkeypatch, root, simple_desktop, tmp_path):
    # pyaedt version <= 0.15.3 and package type != 'installer' should trigger error
    zpath = _make_wh_zip(
        tmp_path, "v0.15.0", "full", "windows", pyver="".join(platform.python_version().split(".")[:2])
    )
    monkeypatch.setattr(vm.filedialog, "askopenfilename", lambda **k: str(zpath))
    err = MagicMock()
    monkeypatch.setattr(vm.messagebox, "showerror", err)
    # Ensure OS flags - run as linux to trigger replacement for windows
    monkeypatch.setattr(vm, "is_windows", False)
    monkeypatch.setattr(vm, "is_linux", True)

    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    mgr.update_from_wheelhouse()
    assert err.called
    assert "This wheelhouse doesn't contain required packages" in err.call_args[0][1]


def test_update_from_wheelhouse_os_mismatch_triggers_error(monkeypatch, root, simple_desktop, tmp_path):
    # OS tag 'windows' but vm.is_windows False should trigger error
    pyver = ".".join(platform.python_version().split(".")[:2])
    zpath = _make_wh_zip(tmp_path, "v1.0.0", "installer", "windows", pyver=pyver)
    monkeypatch.setattr(vm.filedialog, "askopenfilename", lambda **k: str(zpath))
    err = MagicMock()
    monkeypatch.setattr(vm.messagebox, "showerror", err)
    monkeypatch.setattr(vm, "is_windows", False)
    monkeypatch.setattr(vm, "is_linux", True)

    mgr = vm.VersionManager(root, simple_desktop, "2025.2", str(tmp_path))
    mgr.update_from_wheelhouse()
    assert err.called
    assert "not compatible with your operating system" in err.call_args[0][1]
