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


def test_new_session_no_active_sessions(mock_settings):
    """New AEDT session on port 50051, no active sessions."""
    base_port = 50051

    # Start 2026.1 graphical session (no active sessions yet)
    d1 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        assert d1._validate_port() == base_port

    # Start 2026.1 non-graphical session (no active sessions yet), new_desktop is False, and PyAEDT will flip it
    d2 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        assert d2._validate_port() == base_port
        assert d2.new_desktop


def test_new_session_port_0(mock_settings):
    """New AEDT session on port 0."""
    base_port = 0
    random_port = 12345

    # No sessions

    # Start 2026.1
    d1 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d1._validate_port() == 12345
            d1._Desktop__logger.info.assert_called_with("New AEDT session is starting on gRPC port 12345.")

    # Start 2026.1, new_desktop False
    d2 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d2._validate_port() == random_port
            assert d2.new_desktop

    # Start 2026.1, remote_rpc_session
    mock_settings.remote_rpc_session = MagicMock()
    mock_settings.remote_rpc_session.port = random_port
    d3 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        assert d3._validate_port() == random_port
        d3._Desktop__logger.warning.assert_called_with(
            "Remote AEDT connection without specified port. Trying to use the port from the RPyC connection."
        )
    mock_settings.remote_rpc_session = None

    # Two sessions in different versions

    # Start 2026.1
    d4 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=ACTIVE_SESSIONS):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d4._validate_port() == random_port
            d4._Desktop__logger.info.assert_called_with(f"New AEDT session is starting on gRPC port {random_port}.")

    # Start 2026.1, new_desktop False
    d5 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=ACTIVE_SESSIONS):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d5._validate_port() == random_port
            assert d5.new_desktop

    # Ensure mock settings enables multi desktop
    mock_settings.use_multi_desktop = True

    d = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            res = d._validate_port()
            assert res == random_port
            d._Desktop__logger.info.assert_called_with(f"New AEDT session is starting on gRPC port {random_port}.")
            mock_settings.use_multi_desktop = False


def test_new_session(mock_settings):
    """New AEDT session."""
    base_port = 50051
    random_port = 12345

    # No sessions

    # Start 2026.1
    d1 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        assert d1._validate_port() == base_port

    # Start 2026.1, new_desktop False
    d2 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        assert d2._validate_port() == base_port
        assert d2.new_desktop

    # Start 2026.1, remote_rpc_session
    mock_settings.remote_rpc_session = MagicMock()
    d3 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value={}):
        assert d3._validate_port() == base_port
    mock_settings.remote_rpc_session = None

    # Two sessions in different versions

    # Start 2026.1, trying base_port with new_desktop True, but it is occupied
    d4 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=True)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=ACTIVE_SESSIONS):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d4._validate_port() == random_port
            d4._Desktop__logger.warning.assert_called_with(
                f"Port {base_port} is already in use. Finding a new free port."
            )

    # Start student version, but port is occupied by another version
    d5 = _make_desktop(port=base_port, version="2025.2", student_version=True, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=ACTIVE_SESSIONS):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d5._validate_port() == random_port
            assert d5.new_desktop

    # Start 2026.1 in a port not occupied by another version, but new_desktop is False, so it will flip to True
    d6 = _make_desktop(port=1, version="2025.2", student_version=True, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=ACTIVE_SESSIONS):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d6._validate_port() == 1
            assert d6.new_desktop


def test_connect_session(mock_settings):
    """New connect AEDT session."""
    base_port = 50051
    random_port = 12345

    # Sessions in different versions

    # Connect 2026.1, trying base_port with new_desktop False
    d1 = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False)
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=ACTIVE_SESSIONS):
        with patch("ansys.aedt.core.desktop._find_free_port", return_value=random_port):
            assert d1._validate_port() == base_port
            d1._Desktop__logger.info.assert_called_with(f"Port {base_port} session has been found.")

    # Connect 2026.1 not passing port, this is using grpc_active_sessions, with multiple sessions
    d2 = _make_desktop(version="2025.2", student_version=True, non_graphical=True, new_desktop=False)
    with patch("ansys.aedt.core.desktop.grpc_active_sessions", return_value=[base_port, 50052]):
        assert d2._validate_port() == base_port

    # Connect 2026.1 not passing port, this is using grpc_active_sessions, with multiple sessions
    d3 = _make_desktop(version="2025.2", student_version=True, non_graphical=True, new_desktop=False)
    with patch("ansys.aedt.core.desktop.grpc_active_sessions", return_value=[base_port]):
        assert d3._validate_port() == base_port

    # Connect 2026.1, not found ports with get_target_processes, and then using _check_grpc_connection
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
                "port": random_port,
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

    target_process = [(11111, ["v261/ansysedt.exe", "-grpcsrv", f"127.0.0.1:{random_port}", "-ng"])]
    d4 = _make_desktop(
        port=random_port, version="2026.1", student_version=False, non_graphical=False, new_desktop=False
    )
    with patch("ansys.aedt.core.generic.general_methods._check_psutil_connections", return_value=connections):
        with patch("ansys.aedt.core.generic.general_methods._get_target_processes", return_value=target_process):
            assert d4._validate_port() == random_port
            d4._Desktop__logger.warning.assert_called_with(
                f"Port {random_port} is already in use in non_graphical mode. Using it."
            )


def test_version_mode_flip_logs_and_changes(mock_settings):
    """Port is in use by the opposite mode (graphical vs nongraphical)."""
    base_port = 50051

    # Create a desktop that is non-graphical but the session is graphical
    d = _make_desktop(port=base_port, version="2026.1", student_version=False, non_graphical=True, new_desktop=False)
    # all_active_sessions contains the opposite mode (graphical)
    sessions = {"261_graphical": {"p": base_port}}
    with patch("ansys.aedt.core.desktop.all_active_sessions", return_value=sessions):
        res = d._validate_port()
        assert res == base_port
        # Should have flipped non_graphical to False
        assert not d.non_graphical
        # Logger warning about mode usage
        d._Desktop__logger.warning.assert_called_with(
            f"Port {base_port} is already in use in graphical mode. Using it."
        )
