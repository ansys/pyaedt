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

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.desktop import TransportMode
from ansys.aedt.core.desktop import _check_port
from ansys.aedt.core.desktop import _check_settings
from ansys.aedt.core.desktop import _find_free_port
from ansys.aedt.core.desktop import _is_port_occupied
from ansys.aedt.core.desktop import _ServerArgs
from ansys.aedt.core.generic.settings import Settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError


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


@patch("socket.socket")
def test_is_port_occupied_on_occupied_port(mock_socket_class) -> None:
    """Test _is_port_occupied on an occupied port."""
    mock_socket = MagicMock()
    mock_socket.connect_ex.return_value = 0
    mock_socket_class.return_value.__enter__.return_value = mock_socket

    assert _is_port_occupied(8080)


@patch("socket.socket")
def test_is_port_occupied_on_unoccupied_port(mock_socket_class) -> None:
    """Test _is_port_occupied on an unoccupied port."""
    mock_socket = MagicMock()
    mock_socket.connect_ex.return_value = 1
    mock_socket_class.return_value.__enter__.return_value = mock_socket

    assert not _is_port_occupied(8080)


# Test _find_free_port
@patch("ansys.aedt.core.desktop.active_sessions", return_value={})
@patch("socket.socket")
def test_find_free_port(mock_socket, mock_active_sessions) -> None:
    mock_socket.return_value.getsockname.return_value = ("127.0.0.1", 12345)
    port = _find_free_port()
    assert port == 12345


# Test Desktop.get_available_toolkits() static method
def test_get_available_toolkits() -> None:
    toolkits = Desktop.get_available_toolkits()
    result = ["Circuit", "HFSS", "HFSS3DLayout", "Icepak", "Maxwell3D", "Project", "TwinBuilder"]
    all(elem in toolkits for elem in result)


@patch.object(Settings, "use_grpc_api", new_callable=lambda: True)
@patch("time.sleep", return_value=None)
def test_desktop_odesktop_retries(mock_settings, mock_sleep) -> None:
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


def test_desktop_odesktop_setter() -> None:
    """Test Desktop.odesktop property retries to get the odesktop object."""
    desktop = Desktop()
    aedt_app = MagicMock()

    desktop.grpc_plugin = MagicMock()
    desktop.grpc_plugin.recreate_application = MagicMock()
    desktop.grpc_plugin.odesktop = aedt_app
    desktop.odesktop = aedt_app

    assert desktop.odesktop == aedt_app


def test_desktop_check_settings_failure_with_lsf_num_cores(mock_settings) -> None:
    """Test _check_settings failure due to num_cores value."""
    settings = Settings()
    settings.num_cores = -1

    with pytest.raises(ValueError):
        _check_settings(settings)


def test_desktop_check_settings_failure_with_lsf_ram(mock_settings) -> None:
    """Test _check_settings failure due to lsf_ram value."""
    settings = Settings()
    settings.num_cores = 1
    settings.lsf_ram = -1

    with pytest.raises(ValueError):
        _check_settings(settings)


def test_desktop_check_settings_failure_with_lsf_aedt_command(mock_settings) -> None:
    """Test _check_settings failure due to lsf_aedt_command value."""
    settings = Settings()
    settings.num_cores = 1
    settings.lsf_ram = 1
    settings.lsf_aedt_command = None

    with pytest.raises(ValueError, match="Invalid LSF AEDT command."):
        _check_settings(settings)


def test_desktop_check_port_failure() -> None:
    """Test _check_port failure."""
    port = "twelve"

    with pytest.raises(ValueError):
        _check_port(port)


@patch("ansys.aedt.core.desktop.aedt_versions")
def test_desktop_check_version_failure(mock_aedt_versions, mock_desktop) -> None:
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
def test_desktop_check_version_failure_with_old_specified_version(mock_aedt_versions, mock_desktop) -> None:
    mock_student_version = MagicMock()
    desktop = Desktop()
    specified_version = "2001.6"

    with pytest.raises(
        ValueError, match="PyAEDT supports AEDT version 2021 R1 and later. Recommended version is 2022 R2 or later."
    ):
        desktop._Desktop__check_version(specified_version, mock_student_version)


@patch("ansys.aedt.core.desktop.aedt_versions")
def test_desktop_check_version_failure_with_unknown_specified_version(mock_aedt_versions, mock_desktop) -> None:
    desktop = Desktop()
    specified_version = "2022.6"

    with pytest.raises(ValueError, match=f"Specified version {specified_version} is not installed on your system"):
        desktop._Desktop__check_version(specified_version, False)


@pytest.mark.parametrize(
    ("mode", "port"),
    [(TransportMode.WNUA, None), (TransportMode.WNUA, 12345), (TransportMode.UDS, None), (TransportMode.UDS, 12345)],
)
@patch("ansys.aedt.core.desktop.settings")
def test_grpc_server_args_repr_local(mock_settings, mode, port, monkeypatch) -> None:
    """Test the string representation of _ServerArgs for WNUA and UDS modes."""
    mock_settings.grpc_local = True
    mock_settings.grpc_listen_all = False

    server_args = _ServerArgs(port=port, mode=mode)
    assert f"{server_args}" == "" if port is None else port


@pytest.mark.parametrize("port", [None, 12345])
@patch("ansys.aedt.core.desktop.settings")
def test_grpc_server_args_repr_with_mtls(mock_settings, port, monkeypatch) -> None:
    """Test the string representation of _ServerArgs for MTLS mode."""
    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", "dummy_path")
    mock_settings.grpc_local = True
    mock_settings.grpc_listen_all = False
    host = "127.0.0.1"

    server_args = _ServerArgs(host=host, port=port, mode=TransportMode.MTLS)
    assert f"{server_args}" == f"{host}:{port}:SecureMode" if port is not None else f"{host}:SecureMode"


@pytest.mark.parametrize("port", [None, 12345])
@patch("ansys.aedt.core.desktop.settings")
def test_grpc_server_args_repr_with_insecure(mock_settings, port, monkeypatch) -> None:
    """Test the string representation of _ServerArgs for Insecure mode."""
    mock_settings.grpc_local = True
    mock_settings.grpc_listen_all = False
    host = "127.0.0.1"

    server_args = _ServerArgs(host=host, port=port, mode=TransportMode.INSECURE)
    assert f"{server_args}" == f"{host}:{port}:InsecureMode" if port is not None else f"{host}:InsecureMode"


@pytest.mark.parametrize("port", [None, 12345])
@patch("ansys.aedt.core.desktop.settings")
def test_grpc_server_args_repr_with_insecure_all_interfaces(mock_settings, port, monkeypatch) -> None:
    """Test the string representation of _ServerArgs for Insecure mode with listen on all interfaces."""
    mock_settings.grpc_local = False
    mock_settings.grpc_listen_all = True
    host = "SomeDummyHost"

    server_args = _ServerArgs(host=host, port=port, mode=TransportMode.INSECURE)
    assert f"{server_args}" == f"0.0.0.0:{port}:InsecureMode" if port is not None else "0.0.0.0:InsecureMode"


@patch("ansys.aedt.core.desktop.settings")
def test_grpc_server_args_repr_with_insecure_all_raise_error(mock_settings, monkeypatch) -> None:
    """Test that _ServerArgs raises an error when both local and listen_all are True."""
    mock_settings.grpc_local = True
    mock_settings.grpc_listen_all = True

    with pytest.raises(AEDTRuntimeError):
        str(_ServerArgs(mode=TransportMode.INSECURE))
