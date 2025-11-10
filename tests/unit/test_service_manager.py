"""Tests for ServiceManager class in rpyc_services module."""

import os
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

from ansys.aedt.core.rpc import rpyc_services


@patch("time.sleep")
def test_start_service_with_valid_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    port = 18000

    with patch("subprocess.Popen") as mock_popen, patch("ansys.aedt.core.rpc.rpyc_services.check_port") as mock_check_port:
        mock_check_port.return_value = port

        monkeypatch.setenv("PYAEDT_SERVER_AEDT_PATH", tmp_path.as_posix())

        service_manager = rpyc_services.ServiceManager()
        service_manager.on_connect(MagicMock())
        result = service_manager.start_service(port)
        assert result == port

        local_server_file = Path(rpyc_services.__file__).parent / "local_server.py"
        mock_popen.assert_called_once_with(
            [sys.executable, str(local_server_file), str(tmp_path), "1", str(port)],
        )