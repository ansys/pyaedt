# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from unittest.mock import patch

import pytest

from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.generic.settings import Settings

ACTIVE_SESSIONS = {
    "261_graphical": {"pid_1": 50051, "pid_2": 50052},
    "261_nongraphical": {"pid_3": 50053, "pid_4": 50054},
    "252_graphical": {"pid_5": 50055, "pid_6": 50056},
    "252_nongraphical": {"pid_7": 50057, "pid_8": 50058},
    "252_graphical_student": {"pid_9": 50059},
    "252_nongraphical_student": {"pid_10": 50060},
}

DEFAULT_PORT = 50051
BASE_PORT = 0
RANDOM_PORT = 12345


class _SmallLogger:
    def debug(self, *a, **k):
        pass

    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


def _make_desktop(port=0, version="2026.1", student_version=False, non_graphical=True, new_desktop=False):
    d = Desktop.__new__(Desktop)
    d._Desktop__port = port
    d._Desktop__machine = "127.0.0.1"
    d._Desktop__aedt_version_id = version
    d._Desktop__student_version = student_version
    d._Desktop__non_graphical = non_graphical
    d._Desktop__new_desktop = new_desktop
    # Use MagicMock for logger so tests can assert logging calls
    d._Desktop__logger = MagicMock()
    d._Desktop__close_on_exit = False
    # Minimal attributes to prevent __del__ from failing in tests/debugger
    d._Desktop__closed = False
    d._Desktop__aedt_process_id = None
    # Whether this Desktop instance uses gRPC API (avoid missing attribute in __del__)
    d._Desktop__is_grpc_api = True
    d.odesktop = None
    d.grpc_plugin = MagicMock()
    d.grpc_plugin.recreate_application = MagicMock()
    return d


@pytest.fixture
def mock_settings(monkeypatch):
    m = MagicMock(spec=Settings)
    m.remote_rpc_session = None
    m.aedt_version = "2026.1"
    m.enable_desktop_logs = False
    m.enable_file_logs = False
    m.enable_screen_logs = False
    m.use_multi_desktop = False
    monkeypatch.setattr("ansys.aedt.core.desktop.settings", m, raising=False)
    return m


@patch("ansys.aedt.core.desktop.all_active_sessions")
def test_new_session_no_active_sessions(all_active_sessions, mock_settings):
    """New AEDT session on port 50051, no active sessions."""
    # Start 2026.1 graphical session (no active sessions yet)
    all_active_sessions.return_value = {}
    d1 = _make_desktop(
        port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=True
    )
    assert d1._validate_port() == DEFAULT_PORT

    # Start 2026.1 non-graphical session (no active sessions yet), new_desktop is False, and PyAEDT will flip it
    d2 = _make_desktop(
        port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False
    )
    all_active_sessions.return_value = {}
    assert d2._validate_port() == DEFAULT_PORT
    assert d2.new_desktop


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_port_0_no_active_sessions(find_free_port, all_active_sessions, mock_settings):
    """New AEDT session on port 0 with no active sessions."""
    # Start 2026.1 (new_desktop=True)
    d1 = _make_desktop(port=BASE_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    all_active_sessions.return_value = {}
    find_free_port.return_value = RANDOM_PORT
    assert d1._validate_port() == 12345
    d1._Desktop__logger.info.assert_called_with("New AEDT session is starting on gRPC port 12345.")


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_port_0_with_new_desktop_false(find_free_port, all_active_sessions, mock_settings):
    """New AEDT session on port 0 with new_desktop=False flips to True."""
    d2 = _make_desktop(port=BASE_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    all_active_sessions.return_value = {}
    find_free_port.return_value = RANDOM_PORT
    assert d2._validate_port() == RANDOM_PORT
    assert d2.new_desktop


@patch("ansys.aedt.core.desktop.all_active_sessions")
def test_new_session_port_0_with_remote_rpc_session(all_active_sessions, mock_settings):
    """New AEDT session on port 0 uses remote RPC session port."""
    mock_settings.remote_rpc_session = MagicMock()
    mock_settings.remote_rpc_session.port = RANDOM_PORT
    d3 = _make_desktop(port=BASE_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    all_active_sessions.return_value = {}
    assert d3._validate_port() == RANDOM_PORT
    d3._Desktop__logger.warning.assert_called_with(
        "Remote AEDT connection without specified port. Trying to use the port from the RPyC connection."
    )
    mock_settings.remote_rpc_session = None


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_port_0_with_active_sessions_different_version(find_free_port, all_active_sessions, mock_settings):
    """New AEDT session on port 0 with active sessions in different versions."""
    # Start 2026.1 (new_desktop=True)
    all_active_sessions.return_value = ACTIVE_SESSIONS
    find_free_port.return_value = RANDOM_PORT
    d4 = _make_desktop(port=BASE_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    assert d4._validate_port() == RANDOM_PORT
    d4._Desktop__logger.info.assert_called_with(f"New AEDT session is starting on gRPC port {RANDOM_PORT}.")


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_port_0_with_active_sessions_and_new_desktop_false(
    find_free_port, all_active_sessions, mock_settings
):
    """New AEDT session on port 0 with active sessions flips new_desktop to True."""
    all_active_sessions.return_value = ACTIVE_SESSIONS
    find_free_port.return_value = RANDOM_PORT
    d5 = _make_desktop(port=BASE_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    assert d5._validate_port() == RANDOM_PORT
    assert d5.new_desktop


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_port_0_with_multi_desktop_enabled(find_free_port, all_active_sessions, mock_settings):
    """New AEDT session on port 0 with multi-desktop enabled."""
    mock_settings.use_multi_desktop = True
    all_active_sessions.return_value = {}
    find_free_port.return_value = RANDOM_PORT
    d = _make_desktop(port=BASE_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    res = d._validate_port()
    assert res == RANDOM_PORT
    d._Desktop__logger.info.assert_called_with(f"New AEDT session is starting on gRPC port {RANDOM_PORT}.")
    mock_settings.use_multi_desktop = False


@patch("ansys.aedt.core.desktop.all_active_sessions")
def test_new_session_with_new_desktop_false_flips_to_true(all_active_sessions, mock_settings):
    """New AEDT session with new_desktop=False flips to True."""
    d2 = _make_desktop(
        port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False
    )
    all_active_sessions.return_value = {}
    assert d2._validate_port() == DEFAULT_PORT
    assert d2.new_desktop


@patch("ansys.aedt.core.desktop.all_active_sessions")
def test_new_session_with_remote_rpc_session_uses_base_port(all_active_sessions, mock_settings):
    """New AEDT session with remote RPC session uses base port."""
    mock_settings.remote_rpc_session = MagicMock()
    d3 = _make_desktop(
        port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False
    )
    all_active_sessions.return_value = {}
    assert d3._validate_port() == DEFAULT_PORT
    mock_settings.remote_rpc_session = None


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_occupied_port_finds_free_port(find_free_port, all_active_sessions, mock_settings):
    """New AEDT session with occupied port finds a free port."""
    # Start 2026.1 (new_desktop=True), but port is occupied
    all_active_sessions.return_value = ACTIVE_SESSIONS
    find_free_port.return_value = RANDOM_PORT
    d4 = _make_desktop(
        port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=True
    )
    assert d4._validate_port() == RANDOM_PORT
    d4._Desktop__logger.warning.assert_called_with(f"Port {DEFAULT_PORT} is already in use. Finding a new free port.")


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_student_version_occupied_by_other_version(find_free_port, all_active_sessions, mock_settings):
    """New student version session when port is occupied by another version."""
    all_active_sessions.return_value = ACTIVE_SESSIONS
    find_free_port.return_value = RANDOM_PORT
    d5 = _make_desktop(
        port=DEFAULT_PORT, version="2025.2", student_version=True, non_graphical=False, new_desktop=False
    )
    assert d5._validate_port() == RANDOM_PORT
    assert d5.new_desktop


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_new_session_unoccupied_port_flips_new_desktop_to_true(find_free_port, all_active_sessions, mock_settings):
    """New session on unoccupied port flips new_desktop to True."""
    base_port = 1
    all_active_sessions.return_value = ACTIVE_SESSIONS
    find_free_port.return_value = RANDOM_PORT
    d6 = _make_desktop(port=base_port, version="2025.2", student_version=True, non_graphical=False, new_desktop=False)
    assert d6._validate_port() == base_port
    assert d6.new_desktop


@patch("ansys.aedt.core.desktop.all_active_sessions")
@patch("ansys.aedt.core.desktop._find_free_port")
def test_connect_session_with_port_finds_session(find_free_port, all_active_sessions, mock_settings):
    """Connect to AEDT session with port finds existing session."""
    all_active_sessions.return_value = ACTIVE_SESSIONS
    find_free_port.return_value = RANDOM_PORT
    d1 = _make_desktop(
        port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False
    )
    assert d1._validate_port() == DEFAULT_PORT
    d1._Desktop__logger.info.assert_called_with(f"Port {DEFAULT_PORT} session has been found.")


@patch("ansys.aedt.core.desktop.grpc_active_sessions")
def test_connect_session_no_port_multiple_sessions(grpc_active_sessions, mock_settings):
    """Connect to AEDT session without port when multiple sessions exist."""
    d2 = _make_desktop(version="2025.2", student_version=True, non_graphical=True, new_desktop=False)
    grpc_active_sessions.return_value = [DEFAULT_PORT, 50052]
    assert d2._validate_port() == DEFAULT_PORT


@patch("ansys.aedt.core.desktop.grpc_active_sessions")
def test_connect_session_no_port_single_session(grpc_active_sessions, mock_settings):
    """Connect to AEDT session without port when single session exists."""
    d3 = _make_desktop(version="2025.2", student_version=True, non_graphical=True, new_desktop=False)
    grpc_active_sessions.return_value = [DEFAULT_PORT]
    assert d3._validate_port() == DEFAULT_PORT


@patch("ansys.aedt.core.generic.general_methods._check_psutil_connections")
@patch("ansys.aedt.core.generic.general_methods._get_target_processes")
def test_connect_session_via_tcp_connections(get_target_processes, check_psutil_connections, mock_settings):
    """Connect to AEDT session using TCP connection analysis."""
    connections = {
        11111: [
            {
                "cmdline": "v261/ansysedt.exe -grpcsrv 50700 -ng",
                "ip": "127.0.0.1",
                "port": 49236,
                "status": "ESTABLISHED",
            },
            {
                "cmdline": "v261/ansysedt.exe -grpcsrv 50700 -ng",
                "ip": "127.0.0.1",
                "port": RANDOM_PORT,
                "status": "LISTEN",
            },
            {"cmdline": "v261/ansysedt.exe -grpcsrv 50700 -ng", "ip": "0.0.0.0", "port": 2002, "status": "LISTEN"},
            {
                "cmdline": "v261/ansysedt.exe -grpcsrv 50700 -ng",
                "ip": "127.0.0.1",
                "port": 49229,
                "status": "ESTABLISHED",
            },
            {"cmdline": "v261/ansysedt.exe -grpcsrv 50700 -ng", "ip": "0.0.0.0", "port": 56621, "status": "LISTEN"},
        ]
    }

    target_process = [(11111, ["v261/ansysedt.exe", "-grpcsrv", f"127.0.0.1:{RANDOM_PORT}", "-ng"])]
    check_psutil_connections.return_value = connections
    get_target_processes.return_value = target_process
    d4 = _make_desktop(
        port=RANDOM_PORT, version="2026.1", student_version=False, non_graphical=False, new_desktop=False
    )
    assert d4._validate_port() == RANDOM_PORT
    d4._Desktop__logger.warning.assert_called_with(
        f"Port {RANDOM_PORT} is already in use in non_graphical mode. Using it."
    )


@patch("ansys.aedt.core.desktop.all_active_sessions")
def test_version_mode_flip_logs_and_changes(all_active_sessions, mock_settings):
    """Port is in use by the opposite mode (graphical vs nongraphical)."""
    # Create a desktop that is non-graphical but the session is graphical
    d = _make_desktop(port=DEFAULT_PORT, version="2026.1", student_version=False, non_graphical=True, new_desktop=False)
    # all_active_sessions contains the opposite mode (graphical)
    sessions = {"261_graphical": {"p": DEFAULT_PORT}}
    all_active_sessions.return_value = sessions
    res = d._validate_port()
    assert res == DEFAULT_PORT
    # Should have flipped non_graphical to False
    assert not d.non_graphical
    # Logger warning about mode usage
    d._Desktop__logger.warning.assert_called_with(f"Port {DEFAULT_PORT} is already in use in graphical mode. Using it.")
