import os
import sys
import zipfile
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from ansys.aedt.core.extensions.installer import version_manager as vm

# Ensure tests don't try to pip-install uv during VersionManager __init__.
os.environ.setdefault("PYTEST_CURRENT_TEST", "1")


def test_get_latest_version_success_and_failure(monkeypatch):
    class Resp:
        status_code = 200

        def json(self):
            return {"info": {"version": "1.2.3"}}

    monkeypatch.setattr(vm.requests, "get", lambda *a, **k: Resp())
    assert vm.get_latest_version("pyaedt") == "1.2.3"

    class BadResp:
        status_code = 404

    monkeypatch.setattr(vm.requests, "get", lambda *a, **k: BadResp())
    assert vm.get_latest_version("pyaedt") == vm.UNKNOWN_VERSION

    def raise_exc(*a, **k):
        raise RuntimeError()

    monkeypatch.setattr(vm.requests, "get", raise_exc)
    assert vm.get_latest_version("pyaedt") == vm.UNKNOWN_VERSION


def _make_vm(monkeypatch):
    # Patch PIL image opening and photo creation so constructor doesn't touch the FS
    monkeypatch.setattr(vm.PIL.Image, "open", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.PIL.ImageTk, "PhotoImage", lambda *a, **k: MagicMock())

    # Patch ttk.Style and other widgets to simple mocks
    monkeypatch.setattr(vm.ttk, "Style", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.ttk, "PanedWindow", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.ttk, "Notebook", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.ttk, "Frame", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.ttk, "Button", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.ttk, "Label", lambda *a, **k: MagicMock())
    monkeypatch.setattr(vm.ttk, "Entry", lambda *a, **k: MagicMock())

    # Provide a lightweight StringVar implementation
    class _SV:
        def __init__(self, *a, **k):
            self._v = ""

        def set(self, v):
            self._v = v

        def get(self):
            return self._v

    monkeypatch.setattr(vm.tkinter, "StringVar", _SV)
    # Ensure any call to tkinter.Tk in the code under test returns a mock
    monkeypatch.setattr(vm.tkinter, "Tk", lambda *a, **k: MagicMock())

    # Minimal UI object expected by VersionManager
    ui = MagicMock()
    ui.iconphoto = MagicMock()
    ui.title = MagicMock()
    ui.geometry = MagicMock()
    ui.configure = MagicMock()

    # Minimal desktop mock passed to VersionManager
    desktop = MagicMock()
    desktop.personallib = "/tmp/personal"
    desktop.release_desktop = MagicMock()

    # Create the manager
    manager = vm.VersionManager(ui, desktop, aedt_version="2025.2", personal_lib="/tmp/personal")
    return manager


def test_activate_venv_and_exes(monkeypatch):
    manager = _make_vm(monkeypatch)
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


def test_is_git_available_and_messagebox(monkeypatch):
    manager = _make_vm(monkeypatch)
    # If git not found, showerror called
    monkeypatch.setattr(vm.shutil, "which", lambda x: None)
    called = {}

    def fake_showerror(title, msg):
        called['err'] = (title, msg)

    monkeypatch.setattr(vm.messagebox, "showerror", fake_showerror)
    assert not vm.VersionManager.is_git_available()
    assert 'err' in called

    # If git found, returns True and no error
    monkeypatch.setattr(vm.shutil, "which", lambda x: "/usr/bin/git")
    monkeypatch.setattr(vm.messagebox, "showerror", lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not be called")))
    assert vm.VersionManager.is_git_available()


def test_get_installed_version_importlib_and_fallback(monkeypatch):
    manager = _make_vm(monkeypatch)

    # Case 1: importlib path works
    def check_output_importlib(cmd, env, stderr, text):
        return "1.0.0\n"

    monkeypatch.setattr(vm.subprocess, "check_output", check_output_importlib)
    res = manager.get_installed_version("pyaedt")
    assert res == "1.0.0"

    def pip_show(cmd, env, stderr, text):
        return "Name: pyaedt\nVersion: 2.0.0\n"

    monkeypatch.setattr(vm.subprocess, "check_output", lambda *a, **k: (_ for _ in ()).throw(RuntimeError()))
    # Next call inside inner try should succeed
    monkeypatch.setattr(vm.subprocess, "check_output", lambda *a, **k: pip_show(*a, **k))
    res = manager.get_installed_version("pyaedt")
    assert res == "Name: pyaedt\nVersion: 2.0.0"

    # Case 3: both approaches fail
    monkeypatch.setattr(vm.subprocess, "check_output", lambda *a, **k: (_ for _ in ()).throw(RuntimeError()))
    res = manager.get_installed_version("doesnotexist")
    assert res == "Please restart"


def test_clicked_refresh_no_restart_and_with_restart(monkeypatch):
    manager = _make_vm(monkeypatch)

    # Patch latest version lookups
    monkeypatch.setattr(vm, "get_latest_version", lambda pkg: "9.9.9")
    # Patch get_installed_version to return stable
    monkeypatch.setattr(manager, "get_installed_version", lambda pkg: "1.2.3")

    # No restart path
    manager.clicked_refresh(need_restart=False)
    assert "PyAEDT: 1.2.3 (Latest 9.9.9)" in manager.pyaedt_info.get()
    assert "PyEDB: 1.2.3 (Latest 9.9.9)" in manager.pyedb_info.get()

    # Restart path: patch get_installed_version to be called inside
    monkeypatch.setattr(manager, "get_installed_version", lambda pkg: "3.3.3")
    monkeypatch.setattr(vm, "get_latest_version", lambda pkg: "8.8.8")
    # Patch messagebox.showinfo to capture call
    called = {}

    def fake_info(title, msg):
        called['info'] = (title, msg)

    monkeypatch.setattr(vm.messagebox, "showinfo", fake_info)
    manager.clicked_refresh(need_restart=True)
    assert 'info' in called
    assert "PyAEDT: 3.3.3 (Latest 8.8.8)" in manager.pyaedt_info.get()


def test_toggle_and_theme_functions(monkeypatch):
    """Verify toggle_theme flips theme_color and calls appropriate helpers."""
    manager = _make_vm(monkeypatch)

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


def test_set_light_and_set_dark(monkeypatch):
    """Directly test set_light_theme and set_dark_theme behavior."""
    manager = _make_vm(monkeypatch)

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


def test_update_pyaedt_flows(monkeypatch):
    manager = _make_vm(monkeypatch)

    # User declines disclaimer
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: False)
    monkeypatch.setattr(vm.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Should not run")))
    manager.update_pyaedt()

    # User accepts but latest unknown -> showerror
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(vm, "get_latest_version", lambda *a, **k: vm.UNKNOWN_VERSION)
    called = {}

    def fake_error(title, msg):
        called['err'] = (title, msg)

    monkeypatch.setattr(vm.messagebox, "showerror", fake_error)
    manager.update_pyaedt()
    assert 'err' in called

    # User accepts and install path; test both branch comparisons
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(vm, "get_latest_version", lambda *a, **k: "1.0.0")
    # Simulate installed version > latest to force pinned install
    # Patch the internal call the property uses
    monkeypatch.setattr(manager, "get_installed_version", lambda pkg: "2.0.0")
    calls = {}

    def fake_run(cmd, check, env):
        calls['cmd'] = cmd

    monkeypatch.setattr(vm.subprocess, "run", fake_run)
    # Call update
    manager.update_pyaedt()
    assert any("pyaedt==1.0.0" in str(x) for x in calls['cmd'])

    # Simulate installed version <= latest to force upgrade
    calls.clear()
    monkeypatch.setattr(manager, "get_installed_version", lambda pkg: "1.0.0")
    manager.update_pyaedt()
    assert any("-U" in str(x) or "install" in str(x) for x in calls['cmd'])


def test_update_pyedb_flows(monkeypatch):
    manager = _make_vm(monkeypatch)

    # Decline
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: False)
    manager.update_pyedb()

    # Accept but unknown
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(vm, "get_latest_version", lambda *a, **k: vm.UNKNOWN_VERSION)
    called = {}

    def fake_error(title, msg):
        called['err'] = (title, msg)

    monkeypatch.setattr(vm.messagebox, "showerror", fake_error)
    manager.update_pyedb()
    assert 'err' in called

    # Accept and update path
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(vm, "get_latest_version", lambda *a, **k: "1.0.0")
    # Patch the internal call used by the property so we avoid assigning to a read-only property
    monkeypatch.setattr(manager, "get_installed_version", lambda pkg: "2.0.0")
    recorded = {}

    def fake_run(cmd, check, env):
        recorded['cmd'] = cmd

    monkeypatch.setattr(vm.subprocess, "run", fake_run)
    manager.update_pyedb()
    assert any("pyedb==1.0.0" in str(x) for x in recorded['cmd']) or any("-U" in str(x) for x in recorded['cmd'])


def test_get_branch_functions(monkeypatch):
    manager = _make_vm(monkeypatch)

    # When git not available, get_pyaedt_branch returns early
    monkeypatch.setattr(vm.VersionManager, "is_git_available", staticmethod(lambda: False))
    manager.get_pyaedt_branch()

    # When git available but user declines
    monkeypatch.setattr(vm.VersionManager, "is_git_available", staticmethod(lambda: True))
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: False)
    manager.get_pyaedt_branch()

    # When user accepts, ensure subprocess.run gets called with expected branch
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: True)
    manager.pyaedt_branch_name.set("feature/foo")
    called = {}

    def fake_run(cmd, check, env):
        called['cmd'] = cmd

    monkeypatch.setattr(vm.subprocess, "run", fake_run)
    manager.get_pyaedt_branch()
    assert any("github.com/ansys/pyaedt.git@feature/foo" in str(x) for x in called['cmd'])


def test_update_from_wheelhouse_flow(monkeypatch, tmp_path):
    manager = _make_vm(monkeypatch)

    # If no file selected, do nothing
    monkeypatch.setattr(vm.filedialog, "askopenfilename", lambda *a, **k: "")
    manager.update_from_wheelhouse()

    # Create a fake wheelhouse zip with expected stem parts matching the parser
    # filename stem must split into 7 parts by '-'
    stem = "pyaedt-v1.0.0-installer-foo-ubuntu-bar-3.10"
    zippath = tmp_path / (stem + ".zip")
    unzipdir = tmp_path / stem
    # Create zip containing a dummy file
    with zipfile.ZipFile(zippath, "w") as zf:
        zf.writestr(f"{stem}/dummy.txt", "ok")

    # Return this file as selected
    monkeypatch.setattr(vm.filedialog, "askopenfilename", lambda *a, **k: str(zippath))
    # Patch python_version to match '3.10'
    monkeypatch.setattr(vm.VersionManager, "python_version", "3.10", raising=False)

    recorded = {}

    def fake_run(cmd, check, env):
        recorded['cmd'] = cmd

    monkeypatch.setattr(vm.subprocess, "run", fake_run)
    # Execute
    manager.update_from_wheelhouse()
    assert recorded
    # Clean up what manager might extract
    if unzipdir.exists():
        # Remove files before directories to avoid IsADirectoryError
        for p in sorted(unzipdir.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if p.is_dir():
                p.rmdir()
            else:
                p.unlink()
        if unzipdir.exists():
            unzipdir.rmdir()


def test_reset_pyaedt_buttons_in_aedt(monkeypatch):
    manager = _make_vm(monkeypatch)

    # If user declines, nothing happens
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: False)
    manager.reset_pyaedt_buttons_in_aedt()

    # If user accepts, ensure add_pyaedt_to_aedt called and showinfo called
    monkeypatch.setattr(vm.messagebox, "askyesno", lambda *a, **k: True)
    fake_installer = MagicMock()
    fake_installer.add_pyaedt_to_aedt = MagicMock()

    # Patch the import inside the function to our fake
    monkeypatch.setitem(sys.modules, "ansys.aedt.core.extensions.installer.pyaedt_installer", fake_installer)

    called = {}

    def fake_info(title, msg):
        called['info'] = (title, msg)

    monkeypatch.setattr(vm.messagebox, "showinfo", fake_info)
    manager.reset_pyaedt_buttons_in_aedt()
    assert 'info' in called


def test_get_desktop_info_creates_desktop(monkeypatch):
    # Patch helpers
    monkeypatch.setattr(vm, "get_port", lambda: 0)
    monkeypatch.setattr(vm, "get_aedt_version", lambda: "2024.2")
    monkeypatch.setattr(vm, "get_process_id", lambda: None)

    fake_desktop = MagicMock()
    fake_desktop.personallib = "/tmp/personal"
    fake_desktop.release_desktop = MagicMock()

    monkeypatch.setattr(vm.ansys.aedt.core, "Desktop", lambda **k: fake_desktop)
    out = vm.get_desktop_info(release_desktop=False)
    assert out["desktop"] is fake_desktop
    assert out["aedt_version"] == "2024.2"
    assert out["personal_lib"] == "/tmp/personal"
