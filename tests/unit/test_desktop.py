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
from ansys.aedt.core.desktop import _check_port
from ansys.aedt.core.desktop import _check_settings
from ansys.aedt.core.desktop import _find_free_port
from ansys.aedt.core.desktop import _is_port_occupied
from ansys.aedt.core.generic.settings import Settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
import pytest


@pytest.fixture(scope="module", autouse=True)
def mock_desktop():
    """Fixture used to mock the creation of a Desktop instance."""
    with patch("ansys.aedt.core.desktop.Desktop.__init__", lambda x: None):
        yield


@pytest.fixture(scope="module", autouse=True)
def mock_settings():
    """Fixture used to mock the creation of a Settings instance."""
    with patch("ansys.aedt.core.generic.settings.Settings.__init__", lambda x: None):
        yield


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


# Test Desktop.get_available_toolkits() static method
def test_get_available_toolkits():
    toolkits = Desktop.get_available_toolkits()
    result = ["Circuit", "HFSS", "HFSS3DLayout", "Icepak", "Maxwell3D", "Project", "TwinBuilder"]
    all(elem in toolkits for elem in result)


@patch.object(Settings, "use_grpc_api", new_callable=lambda: True)
@patch("time.sleep", return_value=None)
def test_desktop_odesktop_retries(mock_settings, mock_sleep):
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


def test_desktop_odesktop_setter():
    """Test Desktop.odesktop property retries to get the odesktop object."""
    desktop = Desktop()
    aedt_app = MagicMock()

    desktop.odesktop = aedt_app

    assert desktop._odesktop == aedt_app


def test_desktop_check_setttings_failure_with_lsf_num_cores(mock_settings):
    """Test _check_setttings failure due to lsf_num_cores value."""
    settings = Settings()
    settings.lsf_num_cores = -1

    with pytest.raises(ValueError):
        _check_settings(settings)


def test_desktop_check_setttings_failure_with_lsf_ram(mock_settings):
    """Test _check_setttings failure due to lsf_ram value."""
    settings = Settings()
    settings.lsf_num_cores = 1
    settings.lsf_ram = -1

    with pytest.raises(ValueError):
        _check_settings(settings)


def test_desktop_check_setttings_failure_with_lsf_aedt_command(mock_settings):
    """Test _check_setttings failure due to lsf_aedt_command value."""
    settings = Settings()
    settings.lsf_num_cores = 1
    settings.lsf_ram = 1
    settings.lsf_aedt_command = None

    with pytest.raises(ValueError, match="Invalid LSF AEDT command."):
        _check_settings(settings)


def test_desktop_check_port_failure():
    """Test _check_port failure."""
    port = "twelve"

    with pytest.raises(ValueError):
        _check_port(port)


@patch("ansys.aedt.core.desktop.aedt_versions")
def test_desktop_check_version_failure(mock_aedt_versions, mock_desktop):
    mock_specified_version = MagicMock()
    mock_student_version = MagicMock()
    mock_aedt_versions.latest_version = ""
    mock_aedt_versions.current_version = ""
    desktop = Desktop()

    with pytest.raises(
        AEDTRuntimeError, match="AEDT is not installed on your system. Install AEDT version 2022 R2 or higher."
    ):
        desktop._Desktop__check_version(mock_specified_version, mock_student_version)


@patch("ansys.aedt.core.desktop.aedt_versions")
def test_desktop_check_version_failure_with_old_specified_version(mock_aedt_versions, mock_desktop):
    mock_student_version = MagicMock()
    desktop = Desktop()
    specified_version = "1989.6"

    with pytest.raises(
        ValueError, match="PyAEDT supports AEDT version 2021 R1 and later. Recommended version is 2022 R2 or later."
    ):
        desktop._Desktop__check_version(specified_version, mock_student_version)


@patch("ansys.aedt.core.desktop.aedt_versions")
def test_desktop_check_version_failure_with_unknown_specified_version(mock_aedt_versions, mock_desktop):
    desktop = Desktop()
    specified_version = "2022.6"

    with pytest.raises(ValueError, match=f"Specified version {specified_version} is not installed on your system"):
        desktop._Desktop__check_version(specified_version, False)
