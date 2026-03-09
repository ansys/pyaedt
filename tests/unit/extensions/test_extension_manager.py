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

import io
import tkinter
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.installer.extension_manager import ExtensionManager
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.generic.settings import is_linux


@pytest.fixture(autouse=True)
def disable_pyaedt_update_check(monkeypatch):
    # Prevent ExtensionManager from starting the update-check thread during tests
    monkeypatch.setattr(
        "ansys.aedt.core.extensions.installer.extension_manager.ExtensionManager.check_for_pyaedt_update_on_startup",
        lambda self: None,
    )
    yield


@pytest.fixture
def mock_aedt_app():
    """Fixture que crea una aplicación AEDT falsa."""
    mock_desktop = MagicMock()
    mock_desktop.aedt_version_id = "2025.1"
    mock_desktop.personallib = "/dummy/personal"
    mock_desktop.logger = MagicMock()
    mock_desktop.odesktop = MagicMock()

    with patch.object(ExtensionCommon, "desktop", new_callable=PropertyMock) as mock_desktop_property:
        mock_desktop_property.return_value = mock_desktop
        yield mock_desktop


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_init(mock_toolkits, mock_desktop, mock_aedt_app):
    """Extension manager initialization."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {
        "HFSS": {
            "MyExt": {
                "name": "My Extension",
                "script": "dummy.py",
                "icon": None,
            }
        }
    }

    extension = ExtensionManager(withdraw=True)

    assert extension.root.title() == "Extension Manager"
    assert extension.root.theme == "light"
    assert extension.toolkits is not None

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_load_extensions(mock_toolkits, mock_desktop, mock_aedt_app):
    """Load one category."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {
        "HFSS": {
            "MyExt": {
                "name": "My Extension",
                "script": "dummy.py",
                "icon": None,
            }
        }
    }

    extension = ExtensionManager(withdraw=True)
    extension.load_extensions("HFSS")

    canvas = next(w for w in extension.right_panel.winfo_children() if isinstance(w, tkinter.Canvas))

    scroll_frame = canvas.winfo_children()[0].children.values()
    found = any(isinstance(w, tkinter.ttk.Label) and "HFSS Extensions" in w.cget("text") for w in scroll_frame)
    assert found

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_custom_extension_cancel(mock_toolkits, mock_desktop, mock_aedt_app):
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Mock the dialog components to avoid opening real windows
    mock_dialog = MagicMock()
    mock_script_var = MagicMock()
    mock_name_var = MagicMock()
    mock_pin_var = MagicMock()

    # Set up return values for the StringVar and BooleanVar get() calls
    mock_script_var.get.return_value = ""  # Empty script file
    mock_name_var.get.return_value = "Custom Extension"
    mock_pin_var.get.return_value = True

    with (
        patch("tkinter.Toplevel", return_value=mock_dialog),
        patch("tkinter.BooleanVar", return_value=mock_pin_var),
        patch("tkinter.ttk.Label"),
        patch("tkinter.ttk.Entry"),
        patch("tkinter.ttk.Button"),
        patch("tkinter.ttk.Checkbutton"),
        patch("tkinter.filedialog.askopenfilename", return_value=""),
        patch.object(extension.root, "wait_window"),
    ):
        script_file, name = extension.handle_custom_extension()
        assert script_file is None
        assert name is None

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_default_settings(mock_toolkits, mock_desktop, mock_aedt_app):
    """Test extension manager window default settings."""
    from ansys.aedt.core.extensions.installer.extension_manager import EXTENSION_TITLE
    from ansys.aedt.core.extensions.installer.extension_manager import HEIGHT
    from ansys.aedt.core.extensions.installer.extension_manager import MAX_HEIGHT
    from ansys.aedt.core.extensions.installer.extension_manager import MAX_WIDTH
    from ansys.aedt.core.extensions.installer.extension_manager import MIN_HEIGHT
    from ansys.aedt.core.extensions.installer.extension_manager import MIN_WIDTH
    from ansys.aedt.core.extensions.installer.extension_manager import WIDTH

    extension = ExtensionManager(withdraw=True)

    assert EXTENSION_TITLE == "Extension Manager"
    assert WIDTH == 900
    assert HEIGHT == 450
    assert MAX_WIDTH == 900
    assert MAX_HEIGHT == 550
    assert MIN_WIDTH == 600
    assert MIN_HEIGHT == 400

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_start_log_stream_threads_appends_stdout_and_stderr(mock_toolkits, mock_desktop, mock_aedt_app):
    """_start_log_stream_threads should read from process streams and append to buffer."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Prepare fake process with stdout/stderr streams
    out_stream = io.StringIO("out1\nout2\n")
    err_stream = io.StringIO("err1\n")
    fake_process = MagicMock()
    fake_process.stdout = out_stream
    fake_process.stderr = err_stream
    # ensure periodic refresh does not re-schedule repeatedly
    fake_process.poll.return_value = 1

    extension.active_process = fake_process
    # Prevent scheduling the periodic refresh from actually calling the function
    extension.root.after = lambda delay, func: None

    # Patch threading.Thread to run target synchronously on start
    class DummyThread:
        def __init__(self, target=None, args=(), daemon=False):
            self._target = target
            self._args = args
            self._alive = False

        def start(self):
            # execute reader synchronously
            self._target(*self._args)

        def is_alive(self):
            return False

    with patch("threading.Thread", DummyThread):
        extension._start_log_stream_threads()

    # Verify full_log_buffer contains both stdout and stderr lines
    texts = [t for t, _ in extension.full_log_buffer]
    tags = [tag for _, tag in extension.full_log_buffer]
    assert "out1" in texts and "out2" in texts and "err1" in texts
    assert "stderr" in tags and "stdout" in tags

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_append_full_log_truncation(mock_toolkits, mock_desktop, mock_aedt_app):
    """_append_full_log should truncate buffer when it grows beyond 10000 entries."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Add 10005 entries
    total = 10005
    for i in range(total):
        extension._append_full_log(str(i), "stdout")

    # Ensure truncation occurred (length is less than the total added)
    assert len(extension.full_log_buffer) < total
    # Last element should correspond to the last appended value
    assert extension.full_log_buffer[-1][0] == str(total - 1)

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_update_logs_text_widget_inserts_and_autoscroll(mock_toolkits, mock_desktop, mock_aedt_app):
    """_update_logs_text_widget should write buffer into the text widget and call see when at end."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Populate buffer with stdout and stderr entries
    extension.full_log_buffer = [("line1", "stdout"), ("line2", "stderr")]

    # Create a fake text widget
    txt = MagicMock()
    # Simulate being at end (index('end-1c') == index('insert'))
    txt.index.return_value = "1.0"

    extension.logs_text_widget = txt

    extension._update_logs_text_widget()

    # Should have enabled, cleared, inserted and disabled
    txt.configure.assert_any_call(state="normal")
    txt.delete.assert_called_once_with("1.0", "end")
    # Two insert calls (one plain, one with stderr tag)
    insert_calls = [c for c in txt.insert.call_args_list]
    assert any("line1" in str(call) for call in insert_calls)
    assert any("line2" in str(call) for call in insert_calls)
    txt.configure.assert_any_call(state="disabled")
    txt.see.assert_called_once_with("end")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_open_all_logs_window_creates_widgets_and_updates(mock_toolkits, mock_desktop, mock_aedt_app):
    """open_all_logs_window should create a logs window and a Text widget and set it to logs_text_widget."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Ensure update will be called but has empty buffer
    extension.full_log_buffer = []

    fake_toplevel = MagicMock()
    fake_txt = MagicMock()
    fake_txt.index.return_value = "1.0"

    with (
        patch("ansys.aedt.core.extensions.installer.extension_manager.tkinter.Toplevel", return_value=fake_toplevel),
        patch("ansys.aedt.core.extensions.installer.extension_manager.ttk.Frame", return_value=MagicMock()),
        patch("ansys.aedt.core.extensions.installer.extension_manager.ttk.Button", return_value=MagicMock()),
        patch("ansys.aedt.core.extensions.installer.extension_manager.ttk.Scrollbar", return_value=MagicMock()),
        patch("ansys.aedt.core.extensions.installer.extension_manager.tkinter.Text", return_value=fake_txt),
    ):
        extension.open_all_logs_window()

    assert extension.logs_window is fake_toplevel
    assert extension.logs_text_widget is fake_txt

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_clear_logs_and_export_behaviour(mock_toolkits, mock_desktop, mock_aedt_app, tmp_path):
    """Test clearing logs and exporting logs to file as well as exporting when empty."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Test _clear_logs
    extension.full_log_buffer = [("a", "stdout")]
    fake_txt = MagicMock()
    extension.logs_text_widget = fake_txt
    extension._clear_logs()
    assert extension.full_log_buffer == []
    fake_txt.delete.assert_called_once_with("1.0", "end")

    # Test _export_logs when no logs -> showinfo called
    extension.full_log_buffer = []
    with patch("ansys.aedt.core.extensions.installer.extension_manager.messagebox.showinfo") as mock_info:
        extension._export_logs()
        mock_info.assert_called_once()

    # Test _export_logs writes file and shows info
    extension.full_log_buffer = [("ok", "stdout"), ("bad", "stderr")]
    save_file = tmp_path / "out_logs.txt"
    with (
        patch(
            "ansys.aedt.core.extensions.installer.extension_manager.filedialog.asksaveasfilename",
            return_value=str(save_file),
        ),
        patch("ansys.aedt.core.extensions.installer.extension_manager.messagebox.showinfo") as mock_info,
    ):
        extension._export_logs()
        # File should exist and contain expected lines
        assert save_file.exists()
        content = save_file.read_text(encoding="utf-8")
        assert "ok" in content
        assert "[ERR] bad" in content
        mock_info.assert_called_once()

    # Test _export_logs handles writing exception
    extension.full_log_buffer = [("line", "stdout")]
    with (
        patch(
            "ansys.aedt.core.extensions.installer.extension_manager.filedialog.asksaveasfilename",
            return_value=str(tmp_path / "file.txt"),
        ),
        patch("ansys.aedt.core.extensions.installer.extension_manager.open", side_effect=Exception("disk full")),
        patch("ansys.aedt.core.extensions.installer.extension_manager.messagebox.showerror") as mock_err,
    ):
        extension._export_logs()
        mock_err.assert_called_once()

    extension.root.destroy()


@patch("subprocess.Popen")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_extension_manager_launch_extension(mock_desktop, mock_toolkits, mock_popen, mock_aedt_app):
    """Minimal test for launching an extension without UI."""
    mock_desktop.return_value = MagicMock()
    toolkit_data = {"HFSS": {"MyExt": {"name": "My Extension", "script": "dummy.py", "icon": None}}}
    mock_toolkits.return_value = toolkit_data

    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    # Create a minimal ExtensionManager instance without running __init__
    extension = ExtensionManager.__new__(ExtensionManager)
    extension.toolkits = toolkit_data
    extension.python_interpreter = "python"
    extension.desktop = mock_desktop.return_value
    extension.desktop.logger = MagicMock()
    extension.active_process = None
    extension.active_extension = None
    extension.full_log_buffer = []
    extension._log_stream_threads = []
    extension.root = MagicMock()
    extension.root.after = lambda *a, **k: None
    extension.log_message = lambda *a, **k: None
    extension.current_category = "HFSS"

    from pathlib import Path

    script_path = Path("dummy.py")

    with patch(
        "ansys.aedt.core.extensions.installer.extension_manager.get_custom_extension_script",
        return_value=script_path,
    ):
        extension.launch_extension("HFSS", "MyExt")

    mock_popen.assert_called_once()
    assert extension.active_extension == "MyExt"
    assert extension.active_process == mock_process

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.installer.extension_manager.add_script_to_menu")
def test_extension_manager_pin_custom_extension_no_script(mock_add_script, mock_toolkits, mock_desktop, mock_aedt_app):
    """Test pinning a custom extension when no script is selected."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)
    extension.current_category = "HFSS"

    with patch.object(extension, "handle_custom_extension", return_value=(None, None)) as mock_handle_custom:
        extension.pin_extension("HFSS", "custom")
        mock_handle_custom.assert_called_once()
        extension.desktop.logger.info.assert_called_with("No script selected for custom extension. Aborting pin.")
        mock_add_script.assert_not_called()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.installer.extension_manager.add_script_to_menu")
def test_extension_manager_pin_custom_extension_success(mock_add_script, mock_toolkits, mock_desktop, mock_aedt_app):
    """Test successfully pinning a custom extension."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)
    extension.current_category = "HFSS"
    script_file = "path/to/script.py"
    extension_name = "MyCustomExtension"

    with (
        patch.object(
            extension, "handle_custom_extension", return_value=(script_file, extension_name)
        ) as mock_handle_custom,
        patch.object(extension, "load_extensions") as mock_load_extensions,
    ):
        extension.pin_extension("HFSS", "custom")
        mock_handle_custom.assert_called_once()
        mock_add_script.assert_called_once()
        mock_load_extensions.assert_called_once_with("HFSS")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch(
    "ansys.aedt.core.extensions.installer.extension_manager.add_script_to_menu",
    side_effect=Exception("Test error"),
)
@patch("tkinter.messagebox.showerror")
def test_extension_manager_pin_custom_extension_exception(
    mock_showerror, mock_add_script, mock_toolkits, mock_desktop, mock_aedt_app
):
    """Test error handling when pinning a custom extension fails."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)
    extension.current_category = "HFSS"
    script_file = "path/to/script.py"
    extension_name = "MyCustomExtension"

    with patch.object(
        extension, "handle_custom_extension", return_value=(script_file, extension_name)
    ) as mock_handle_custom:
        extension.pin_extension("HFSS", "custom")
        mock_handle_custom.assert_called_once()
        mock_add_script.assert_called_once()
        extension.desktop.logger.error.assert_called_with(
            f"Failed to pin custom extension {extension_name}: Test error"
        )
        mock_showerror.assert_called_once()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_on_pin_click_pinned(mock_toolkits, mock_desktop, mock_aedt_app):
    """Test on_pin_click when the extension is already pinned."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)
    with (
        patch.object(extension, "check_extension_pinned", return_value=True) as mock_check,
        patch.object(extension, "confirm_unpin") as mock_unpin,
    ):
        extension.on_pin_click("HFSS", "MyExt")
        mock_check.assert_called_once_with("HFSS", "MyExt")
        mock_unpin.assert_called_once_with("HFSS", "MyExt")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_on_pin_click_not_pinned(mock_toolkits, mock_desktop, mock_aedt_app):
    """Test on_pin_click when the extension is not pinned."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)
    with (
        patch.object(extension, "check_extension_pinned", return_value=False) as mock_check,
        patch.object(extension, "pin_extension") as mock_pin,
    ):
        extension.on_pin_click("HFSS", "MyExt")
        mock_check.assert_called_once_with("HFSS", "MyExt")
        mock_pin.assert_called_once_with("HFSS", "MyExt")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.installer.extension_manager.add_script_to_menu")
def test_extension_manager_pin_extension(mock_add_script, mock_toolkits, mock_desktop, mock_aedt_app):
    """Test pinning an extension."""
    mock_desktop.return_value = MagicMock()
    toolkit_data = {
        "HFSS": {
            "MyExt": {
                "name": "My Extension",
                "script": "dummy.py",
                "icon": "icon.png",
            }
        }
    }
    mock_toolkits.return_value = toolkit_data
    mock_add_script.return_value = True

    extension = ExtensionManager(withdraw=True)
    # Set the toolkits attribute directly
    extension.toolkits = toolkit_data
    extension.current_category = "HFSS"

    # Mock the desktop.personallib and aedt_version_id
    extension.desktop.personallib = "/fake/path"
    extension.desktop.aedt_version_id = "2025.1"

    with patch.object(extension, "load_extensions") as mock_load:
        extension.pin_extension("HFSS", "MyExt")

    # Verify add_script_to_menu was called
    mock_add_script.assert_called_once()
    # Verify UI was refreshed
    mock_load.assert_called_once_with("HFSS")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_toggle_theme(mock_toolkits, mock_desktop, mock_aedt_app):
    """Test theme toggling."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)
    initial_theme = extension.root.theme

    with patch.object(extension, "add_extension_content") as mock_add_content:
        extension.toggle_theme()

    # Verify theme changed
    assert extension.root.theme != initial_theme
    # Verify content was refreshed
    mock_add_content.assert_called_once()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.installer.extension_manager.is_extension_in_panel")
@patch("tkinter.messagebox.showinfo")
def test_extension_manager_confirm_unpin_not_pinned(
    mock_showinfo,
    mock_is_in_panel,
    mock_toolkits,
    mock_desktop,
    mock_aedt_app,
):
    """Test confirming unpin when extension is not pinned."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}
    mock_is_in_panel.return_value = False

    extension = ExtensionManager(withdraw=True)
    extension.confirm_unpin("HFSS", "MyExt")

    # Should show info message when not pinned
    mock_showinfo.assert_called_once()

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.installer.extension_manager.is_extension_in_panel")
@patch("ansys.aedt.core.extensions.installer.extension_manager.remove_script_from_menu")
@patch("tkinter.messagebox.askyesno")
def test_extension_manager_confirm_unpin_success(
    mock_askyesno,
    mock_remove_script,
    mock_is_in_panel,
    mock_toolkits,
    mock_desktop,
    mock_aedt_app,
):
    """Test successful unpin confirmation."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}
    mock_is_in_panel.return_value = True
    mock_askyesno.return_value = True
    mock_remove_script.return_value = True

    extension = ExtensionManager(withdraw=True)

    with patch.object(extension, "load_extensions") as mock_load:
        extension.confirm_unpin("HFSS", "MyExt")

    # Verify removal was attempted
    mock_remove_script.assert_called_once()
    # Verify UI was refreshed
    mock_load.assert_called_once_with("HFSS")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("webbrowser.open")
def test_extension_manager_launch_web_url(mock_webbrowser, mock_toolkits, mock_desktop, mock_aedt_app):
    """Test launching web URL."""
    mock_desktop.return_value = MagicMock()
    toolkit_data = {
        "HFSS": {
            "MyExt": {
                "name": "My Extension",
                "script": "dummy.py",
                "icon": None,
                "url": "https://example.com",
            }
        }
    }
    mock_toolkits.return_value = toolkit_data

    extension = ExtensionManager(withdraw=True)
    # Set the toolkits attribute directly
    extension.toolkits = toolkit_data

    extension.launch_web_url("HFSS", "MyExt")

    # Verify webbrowser.open was called
    mock_webbrowser.assert_called_once_with("https://example.com")

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.installer.extension_manager.is_extension_in_panel")
def test_extension_manager_check_extension_pinned(mock_is_in_panel, mock_toolkits, mock_desktop, mock_aedt_app):
    """Test checking if extension is pinned."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}
    mock_is_in_panel.return_value = True

    extension = ExtensionManager(withdraw=True)

    # Reset mock after initialization to only track the test call
    mock_is_in_panel.reset_mock()

    result = extension.check_extension_pinned("HFSS", "MyExt")
    # Path adjusted to OS
    path = "\\dummy\\personal\\Toolkits" if not is_linux else "/dummy/personal/Toolkits"
    assert result is True
    mock_is_in_panel.assert_called_once()
    call_args = mock_is_in_panel.call_args[0]
    assert call_args[0] == path
    assert call_args[1].lower() == "hfss"
    assert call_args[2] == "MyExt"

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("tkinter.filedialog.askopenfilename")
def test_extension_manager_handle_custom_extension_with_script(
    mock_askopenfilename, mock_toolkits, mock_desktop, mock_aedt_app
):
    """Test handling custom extension with valid script."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}
    mock_askopenfilename.return_value = "/path/to/script.py"

    extension = ExtensionManager(withdraw=True)

    # Mock the dialog components
    mock_dialog = MagicMock()
    mock_script_var = MagicMock()
    mock_name_var = MagicMock()

    mock_script_var.get.return_value = "/path/to/script.py"
    mock_name_var.get.return_value = "My Custom Extension"

    # Track the on_ok function to simulate the OK button click
    captured_on_ok = []

    def mock_button(*args, **kwargs):
        if "command" in kwargs:
            captured_on_ok.append(kwargs["command"])  # Append the function to a list
        return MagicMock()

    def mock_wait_window(dialog):
        # Simulate the OK button being clicked
        if captured_on_ok:
            captured_on_ok[1]()  # Call the first (and only) function in the list

    with (
        patch("tkinter.Toplevel", return_value=mock_dialog),
        patch(
            "tkinter.StringVar",
            side_effect=[mock_script_var, mock_name_var],
        ),
        patch("tkinter.ttk.Label"),
        patch("tkinter.ttk.Entry"),
        patch("tkinter.ttk.Button", side_effect=mock_button),
        patch.object(
            extension.root,
            "wait_window",
            side_effect=mock_wait_window,
        ),
    ):
        script_file, name = extension.handle_custom_extension()
        assert script_file.as_posix().endswith("/path/to/script.py")
        assert name == "My Custom Extension"

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_category_case_insensitive(mock_toolkits, mock_desktop, mock_aedt_app):
    """Ensure load_extensions maps category names case-insensitively."""
    mock_desktop.return_value = MagicMock()
    # Minimal toolkit structure required for the manager
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Lowercase input
    extension.load_extensions("hfss")
    assert extension.current_category == "HFSS"

    # Mixed-case input
    extension.load_extensions("hFsS")
    assert extension.current_category == "HFSS"

    # Proper-cased input
    extension.load_extensions("HFSS")
    assert extension.current_category == "HFSS"

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch(
    "ansys.aedt.core.extensions.installer.extension_manager.AEDT_APPLICATIONS",
    new={"other": "FOO"},
)
def test_extension_manager_category_in_values(mock_toolkits, mock_desktop, mock_aedt_app):
    """Category present in AEDT_APPLICATIONS.values() branch."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Provide a category string that is in AEDT_APPLICATIONS.values()
    extension.load_extensions("FOO")
    assert extension.current_category == "FOO"

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch(
    "ansys.aedt.core.extensions.installer.extension_manager.AEDT_APPLICATIONS",
    new={"other": "MyApp"},
)
def test_extension_manager_category_matched_by_lower(mock_toolkits, mock_desktop, mock_aedt_app):
    """Case-insensitive matching of AEDT_APPLICATIONS values."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Lowercase input should be matched to 'MyApp' value
    extension.load_extensions("myapp")
    assert extension.current_category == "MyApp"

    extension.root.destroy()


@pytest.fixture(autouse=True)
def _patch_log_threads(monkeypatch, request):
    """Disable real background log-stream threads in most tests to avoid
    hangs and cross-thread interactions with mocks/tkinter. Tests that need
    the real behavior can opt-out by name (listed in ALLOW_REAL).
    """
    ALLOW_REAL = {
        "test_start_log_stream_threads_appends_stdout_and_stderr",
    }

    if request.node.name in ALLOW_REAL:
        # Let that test control threading behavior itself
        yield
        return

    # Replace the ExtensionManager._start_log_stream_threads with a noop
    monkeypatch.setattr(
        "ansys.aedt.core.extensions.installer.extension_manager.ExtensionManager._start_log_stream_threads",
        lambda self: None,
    )

    yield


@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_handle_custom_extension_on_cancel(mock_desktop, mock_toolkits, mock_aedt_app):
    """Ensure Cancel button sets result to None and dialog is closed."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    # Capture button commands
    commands = []

    def mock_button(*args, **kwargs):
        if "command" in kwargs:
            commands.append(kwargs["command"])
        return MagicMock()

    def mock_wait_window(dialog):
        # Call only cancel
        if len(commands) > 2:
            commands[2]()

    with (
        patch("tkinter.Toplevel", return_value=MagicMock()),
        patch("tkinter.StringVar", side_effect=[MagicMock(), MagicMock()]),
        patch("tkinter.ttk.Label"),
        patch("tkinter.ttk.Entry"),
        patch("tkinter.ttk.Button", side_effect=mock_button),
        patch.object(extension.root, "wait_window", side_effect=mock_wait_window),
    ):
        script_file, name = extension.handle_custom_extension()
        assert script_file is None and name is None

    extension.root.destroy()


@patch("webbrowser.open")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_extension_manager_launch_web_url_custom(mock_desktop, mock_toolkits, mock_webbrowser, mock_aedt_app):
    """Custom option should open the PyAEDT documentation URL."""
    mock_desktop.return_value = MagicMock()
    mock_toolkits.return_value = {"HFSS": {}}

    extension = ExtensionManager(withdraw=True)

    result = extension.launch_web_url("HFSS", "Custom")

    mock_webbrowser.assert_called_once_with("https://aedt.docs.pyansys.com/version/stable/User_guide/extensions.html")
    assert result is True

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_extension_manager_launch_web_url_no_url(mock_toolkits, mock_desktop, mock_aedt_app):
    """If no URL is defined, show an info message and return False."""
    mock_desktop.return_value = MagicMock()
    toolkit_data = {"HFSS": {"MyExt": {"name": "My Extension", "script": "dummy.py", "icon": None}}}
    mock_toolkits.return_value = toolkit_data

    extension = ExtensionManager(withdraw=True)
    extension.toolkits = toolkit_data

    with patch("tkinter.messagebox.showinfo") as mock_info:
        result = extension.launch_web_url("HFSS", "MyExt")
        mock_info.assert_called_once()
        assert result is False

    extension.root.destroy()


@patch("webbrowser.open", side_effect=Exception("boom"))
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_extension_manager_launch_web_url_exception(mock_webbrowser, mock_toolkits, mock_desktop, mock_aedt_app):
    """If opening the browser raises, show an error and return False."""
    mock_desktop.return_value = MagicMock()
    toolkit_data = {
        "HFSS": {"MyExt": {"name": "My Extension", "script": "dummy.py", "icon": None, "url": "https://example.com"}}
    }
    mock_toolkits.return_value = toolkit_data

    extension = ExtensionManager(withdraw=True)
    extension.toolkits = toolkit_data
    extension.desktop.logger = MagicMock()

    with patch("tkinter.messagebox.showerror") as mock_err:
        result = extension.launch_web_url("HFSS", "MyExt")
        mock_err.assert_called_once()
        assert result is False

    extension.root.destroy()
