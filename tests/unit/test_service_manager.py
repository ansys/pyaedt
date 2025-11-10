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

from pathlib import Path
import re
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.rpc import rpyc_services

LOCAL_SERVER_FILE = Path(rpyc_services.__file__).parent / "local_server.py"


@patch("ansys.aedt.core.rpc.rpyc_services.time.sleep")
def test_start_service_with_valid_path_in_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    port = 18000

    monkeypatch.setenv("PYAEDT_SERVER_AEDT_PATH", str(tmp_path))

    with (
        patch("ansys.aedt.core.rpc.rpyc_services.subprocess.Popen") as mock_popen,
        patch("ansys.aedt.core.rpc.rpyc_services.check_port", return_value=port),
    ):
        service_manager = rpyc_services.ServiceManager()
        service_manager.on_connect(MagicMock())
        result = service_manager.start_service(port)
        assert result == port
        mock_popen.assert_called_once_with([sys.executable, str(LOCAL_SERVER_FILE), str(tmp_path), "1", str(port)])


def test_start_service_with_invalid_path_in_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    port = 18000
    inexistent_dir = tmp_path / "non_existent_directory"

    monkeypatch.setenv("PYAEDT_SERVER_AEDT_PATH", str(inexistent_dir))

    with (
        patch("ansys.aedt.core.rpc.rpyc_services.subprocess.Popen") as mock_popen,
        patch("ansys.aedt.core.rpc.rpyc_services.check_port", return_value=port),
    ):
        service_manager = rpyc_services.ServiceManager()
        service_manager.on_connect(MagicMock())
        with pytest.raises(
            FileNotFoundError, match=re.escape(f"The ANSYSEM path '{str(inexistent_dir)}' does not exist.")
        ):
            service_manager.start_service(port)
        mock_popen.assert_not_called()


@patch("ansys.aedt.core.rpc.rpyc_services.time.sleep")
def test_start_service_without_env_var_defaults_to_latest_installed_path(monkeypatch: pytest.MonkeyPatch):
    port = 18000
    fallback_path_latest = "/path/to/ansys/v252"
    fallback_path_previous = "/path/to/ansys/v251"

    monkeypatch.delenv("PYAEDT_SERVER_AEDT_PATH", raising=False)
    monkeypatch.setenv("ANSYSEM_ROOT252", fallback_path_latest)
    monkeypatch.setenv("ANSYSEM_ROOT251", fallback_path_previous)

    with (
        patch("ansys.aedt.core.rpc.rpyc_services.subprocess.Popen") as mock_popen,
        patch("ansys.aedt.core.rpc.rpyc_services.check_port", return_value=port),
        patch("ansys.aedt.core.rpc.rpyc_services.time.sleep"),
        patch("ansys.aedt.core.rpc.rpyc_services.aedt_versions") as mock_aedt_versions,
    ):
        mock_aedt_versions.list_installed_ansysem = ["ANSYSEM_ROOT252", "ANSYSEM_ROOT251"]

        service_manager = rpyc_services.ServiceManager()
        service_manager.on_connect(MagicMock())
        result = service_manager.start_service(port)
        assert result == port
        mock_popen.assert_called_once_with(
            [sys.executable, str(LOCAL_SERVER_FILE), str(fallback_path_latest), "1", str(port)]
        )


def test_start_service_without_env_var_and_no_installed_path(monkeypatch: pytest.MonkeyPatch):
    port = 18000

    monkeypatch.delenv("PYAEDT_SERVER_AEDT_PATH", raising=False)

    with (
        patch("ansys.aedt.core.rpc.rpyc_services.subprocess.Popen") as mock_popen,
        patch("ansys.aedt.core.rpc.rpyc_services.check_port", return_value=port),
        patch("ansys.aedt.core.rpc.rpyc_services.aedt_versions") as mock_aedt_versions,
    ):
        mock_aedt_versions.list_installed_ansysem = []

        service_manager = rpyc_services.ServiceManager()
        service_manager.on_connect(MagicMock())
        with pytest.raises(Exception, match="No ANSYSEM_ROOTXXX environment variable is defined."):
            service_manager.start_service(port)
        mock_popen.assert_not_called()
