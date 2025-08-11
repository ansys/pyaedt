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

import tkinter
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.installer.extension_manager import ExtensionManager
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.generic.settings import is_linux


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
        patch(
            "tkinter.StringVar",
            side_effect=[mock_script_var, mock_name_var],
        ),
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
        assert name == "Custom Extension"

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
def test_extension_manager_constants(mock_toolkits, mock_desktop, mock_aedt_app):
    """Test extension manager constants."""
    from ansys.aedt.core.extensions.installer.extension_manager import AEDT_APPLICATIONS
    from ansys.aedt.core.extensions.installer.extension_manager import EXTENSION_TITLE
    from ansys.aedt.core.extensions.installer.extension_manager import HEIGHT
    from ansys.aedt.core.extensions.installer.extension_manager import MAX_HEIGHT
    from ansys.aedt.core.extensions.installer.extension_manager import MAX_WIDTH
    from ansys.aedt.core.extensions.installer.extension_manager import MIN_HEIGHT
    from ansys.aedt.core.extensions.installer.extension_manager import MIN_WIDTH
    from ansys.aedt.core.extensions.installer.extension_manager import WIDTH

    # Test constants
    assert EXTENSION_TITLE == "Extension Manager"
    assert WIDTH == 800
    assert HEIGHT == 450
    assert MAX_WIDTH == 800
    assert MAX_HEIGHT == 550
    assert MIN_WIDTH == 600
    assert MIN_HEIGHT == 400

    # Test AEDT applications list
    expected_apps = [
        "Project",
        "HFSS",
        "Maxwell3D",
        "Icepak",
        "Q3D",
        "Maxwell2D",
        "Q2D",
        "HFSS3DLayout",
        "Mechanical",
        "Circuit",
        "EMIT",
        "TwinBuilder",
    ]
    assert AEDT_APPLICATIONS == expected_apps


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch("ansys.aedt.core.extensions.customize_automation_tab.available_toolkits")
@patch("subprocess.Popen")
def test_extension_manager_launch_extension(mock_popen, mock_toolkits, mock_desktop, mock_aedt_app):
    """Test launching an extension."""
    mock_desktop.return_value = MagicMock()
    toolkit_data = {
        "HFSS": {
            "MyExt": {
                "name": "My Extension",
                "script": "dummy.py",
                "icon": None,
            }
        }
    }
    mock_toolkits.return_value = toolkit_data

    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    extension = ExtensionManager(withdraw=True)
    # Set the toolkits attribute directly
    extension.toolkits = toolkit_data

    # Mock the script file path resolution
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.suffix", ".py"):
            extension.launch_extension("HFSS", "MyExt")

    # Verify process was started
    mock_popen.assert_called_once()
    assert extension.active_extension == "MyExt"
    assert extension.active_process == mock_process

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
    mock_is_in_panel.assert_called_once_with(path, "HFSS", "MyExt")

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
        nonlocal captured_on_ok
        if "command" in kwargs:
            captured_on_ok.append(kwargs["command"])  # Append the function to a list
        return MagicMock()

    def mock_wait_window(dialog):
        # Simulate the OK button being clicked
        if captured_on_ok:
            captured_on_ok[0]()  # Call the first (and only) function in the list

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

        assert script_file.as_posix() == "/path/to/script.py"
        assert name == "My Custom Extension"

    extension.root.destroy()
