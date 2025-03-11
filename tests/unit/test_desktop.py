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

import socket
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.desktop import _find_free_port
from ansys.aedt.core.desktop import _is_port_occupied
from ansys.aedt.core.desktop import run_process
from ansys.aedt.core.generic.settings import Settings
import pytest


@pytest.fixture
def mock_desktop():
    """Fixture used to mock the creation of a Desktop instance."""
    with patch("ansys.aedt.core.desktop.Desktop.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Desktop)
        yield mock_instance


# Test _is_port_occupied
def test_is_port_occupied_free_port():
    with patch("socket.socket") as mock_socket:
        mock_socket.return_value.connect.side_effect = socket.error
        assert not _is_port_occupied(5000)


def test_is_port_occupied_used_port():
    with patch("socket.socket") as mock_socket:
        mock_socket.return_value.connect.return_value = None
        assert _is_port_occupied(5000)


# Test _find_free_port
@patch("ansys.aedt.core.desktop.active_sessions", return_value={})
@patch("socket.socket")
def test_find_free_port(mock_socket, mock_active_sessions):
    mock_socket.return_value.getsockname.return_value = ("127.0.0.1", 12345)
    port = _find_free_port()
    assert port == 12345


# Test run_process
@patch("subprocess.call")
def test_run_process(mock_call):
    command = "dummy_command"
    run_process(command)
    mock_call.assert_called_once_with(command)


# Test Desktop.get_available_toolkits() static method
def test_get_available_toolkits():
    toolkits = Desktop.get_available_toolkits()
    result = ["Circuit", "HFSS", "HFSS3DLayout", "Icepak", "Maxwell3D", "Project", "TwinBuilder"]
    all(elem in toolkits for elem in result)


@patch.object(Settings, "use_grpc_api", new_callable=lambda: True)
@patch("time.sleep", return_value=None)
def test_desktop_odesktop_retries(mock_settings, mock_sleep, mock_desktop):
    """Test Desktop.odesktop property retries to get the odesktop object."""
    desktop = Desktop()
    desktop.grpc_plugin = MagicMock()
    aedt_app = MagicMock()
    mock_odesktop = PropertyMock(name="oui", side_effect=[Exception("Failure"), aedt_app])
    # NOTE: Use of type(...) is required for odesktop to be defined as a property and
    # not an attribute. Without it, the side effect does not work.
    type(desktop.grpc_plugin).odesktop = mock_odesktop

    assert aedt_app == desktop.odesktop
    assert mock_odesktop.call_count == 2


def test_desktop_odesktop_setter(mock_desktop):
    """Test Desktop.odesktop property retries to get the odesktop object."""
    desktop = Desktop()
    aedt_app = MagicMock()

    desktop.odesktop = aedt_app

    assert desktop._odesktop == aedt_app
