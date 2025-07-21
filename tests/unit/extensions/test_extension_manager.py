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
