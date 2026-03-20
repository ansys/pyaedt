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

# filepath: c:\Users\smorais\src\pyaedt\tests\test_cli.py
"""Tests for PyAEDT CLI functionality."""

import json
from pathlib import Path
import re
from unittest.mock import Mock
from unittest.mock import PropertyMock
from unittest.mock import patch

import psutil
import pytest
import typer
from typer.testing import CliRunner

from ansys.aedt.core.cli import app
import ansys.aedt.core.cli.common as common_mod
from ansys.aedt.core.cli.common import DEFAULT_TEST_CONFIG
from ansys.aedt.core.cli.common import _clear_session
from ansys.aedt.core.cli.common import _display_config
from ansys.aedt.core.cli.common import _get_config_path
from ansys.aedt.core.cli.common import _get_tests_folder
from ansys.aedt.core.cli.common import _load_config
from ansys.aedt.core.cli.common import _load_session
from ansys.aedt.core.cli.common import _output
from ansys.aedt.core.cli.common import _prompt_config_value
from ansys.aedt.core.cli.common import _save_config
from ansys.aedt.core.cli.common import _save_session
from ansys.aedt.core.cli.config import _update_bool_config
from ansys.aedt.core.cli.config import _update_string_config
from ansys.aedt.core.cli.config import test_app


@pytest.fixture
def cli_runner():
    """Create a test runner for CLI commands."""
    return CliRunner()


@pytest.fixture
def mock_aedt_process():
    """Create a mock AEDT process for testing."""
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 12345
    mock_proc.name.return_value = "ansysedt.exe"
    mock_proc.status.return_value = psutil.STATUS_RUNNING
    mock_proc.cmdline.return_value = ["ansysedt.exe", "-grpcsrv", "50051"]
    mock_proc.username.return_value = "dummy_user"
    mock_proc.create_time.return_value = 1234567890.0
    return mock_proc


@pytest.fixture
def mock_add_pyaedt_to_aedt():
    """Mock the add_pyaedt_to_aedt function."""
    with patch("ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt") as mock_func:
        mock_func.return_value = True
        yield mock_func


@pytest.fixture
def mock_installed_versions():
    """Mock aedt_versions.installed_versions with typical installed versions."""
    mock_versions = {
        "2025.2": "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM",
        "2025.1": "C:\\Program Files\\ANSYS Inc\\v251\\AnsysEM",
    }
    with patch(
        "ansys.aedt.core.internal.aedt_versions.AedtVersions.installed_versions",
        new_callable=PropertyMock,
        return_value=mock_versions,
    ):
        yield mock_versions


@pytest.fixture
def mock_online_help():
    """Mock ansys.aedt.core.help.online_help to avoid real browser / network calls."""
    with patch("ansys.aedt.core.help.online_help") as mock_help:
        mock_help.silent = True
        yield mock_help


def test_cli_help_command(cli_runner) -> None:
    """Verify that help command executes without errors."""
    result = cli_runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "CLI for PyAEDT" in result.stdout


# VERSION COMMAND TESTS


@patch("ansys.aedt.core.__version__", "0.22.0")
def test_version_command(cli_runner) -> None:
    """Test version command output."""
    result = cli_runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "PyAEDT version: 0.22.0" in result.stdout


# PROCESSES COMMAND TESTS


@patch("psutil.process_iter")
def test_processes_command_no_aedt(mock_process_iter, cli_runner) -> None:
    """Test processes command when no AEDT is running."""
    result = cli_runner.invoke(app, ["process", "list"])

    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout


@patch("psutil.process_iter")
def test_processes_command_with_aedt(mock_process_iter, cli_runner, mock_aedt_process) -> None:
    """Test processes command when AEDT processes exist."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "list"])

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "PID: 12345" in result.stdout
    assert "Port: 50051" in result.stdout


# STOP COMMAND TESTS


def test_stop_command_no_args(cli_runner) -> None:
    """Test stop command without arguments raises BadParameter."""
    result = cli_runner.invoke(app, ["process", "stop"])

    assert result.exit_code != 0
    assert isinstance(result.exception, (SystemExit, typer.BadParameter)) or result.exception is None


@patch("psutil.process_iter")
def test_stop_all_command_no_processes(mock_process_iter, cli_runner) -> None:
    """Test stop all when no AEDT processes exist."""
    mock_process_iter.return_value = []

    result = cli_runner.invoke(app, ["process", "stop", "--all"])

    assert result.exit_code == 0
    assert "All AEDT processes have been stopped" in result.stdout


@patch("psutil.process_iter")
def test_stop_all_command_with_access_denied(mock_process_iter, cli_runner, mock_aedt_process) -> None:
    """Test stop all when access is denied to some processes."""
    mock_aedt_process.kill.side_effect = psutil.AccessDenied()
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--all"])

    assert result.exit_code == 0
    assert f"✗ Access denied for process with PID {mock_aedt_process.pid}" in result.stdout
    assert "Some AEDT processes could not be stopped" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_all_command_with_process_no_longer_exists(
    mock_process_access, mock_process_iter, cli_runner, mock_aedt_process
) -> None:
    """Test stop all when process no longer exists during operation."""
    mock_aedt_process.kill.side_effect = psutil.NoSuchProcess(mock_aedt_process.pid)
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--all"])

    assert result.exit_code == 0
    assert f"! Process {mock_aedt_process.pid} no longer exists" in result.stdout
    assert "All AEDT processes have been stopped" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_all_command_with_generic_exception(
    mock_process_access, mock_process_iter, cli_runner, mock_aedt_process
) -> None:
    """Test stop all when generic exception occurs during kill."""
    mock_aedt_process.kill.side_effect = Exception("Dummy exception")
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--all"])

    assert result.exit_code == 0
    assert f"✗ Error stopping process {mock_aedt_process.pid}" in result.stdout
    assert "Some AEDT processes could not be stopped" in result.stdout


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_pid_success(mock_process_access, mock_process_class, cli_runner, mock_aedt_process) -> None:
    """Test successfully stopping process by PID."""
    mock_process_class.return_value = mock_aedt_process

    result = cli_runner.invoke(app, ["process", "stop", "--pid", "12345"])

    assert result.exit_code == 0
    assert "Process with PID 12345 has been stopped" in result.stdout
    mock_aedt_process.kill.assert_called_once()


@patch("psutil.Process")
def test_stop_command_by_pid_access_denied(mock_process_class, cli_runner, mock_aedt_process) -> None:
    """Test stopping process by PID when access is denied."""
    mock_process_class.return_value = mock_aedt_process

    result = cli_runner.invoke(app, ["process", "stop", "--pid", "12345"])

    assert result.exit_code == 0
    assert "✗ Access denied for process with PID 12345" in result.stdout


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_pid_not_stoppable_state(mock_access_process, mock_process_class, cli_runner) -> None:
    """Test stopping process by PID when not in stoppable state."""
    mock_proc = Mock()
    mock_proc.status.return_value = psutil.STATUS_ZOMBIE
    mock_process_class.return_value = mock_proc

    result = cli_runner.invoke(app, ["process", "stop", "--pid", "12345"])
    assert result.exit_code == 0
    assert "✗ Process with PID 12345 is not in a stoppable state" in result.stdout


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_pid_generic_exception(
    mock_process_access, mock_process_class, cli_runner, mock_aedt_process
) -> None:
    """Test stopping process by PID when generic exception occurs."""
    mock_aedt_process.kill.side_effect = Exception("Dummy exception")
    mock_process_class.return_value = mock_aedt_process

    result = cli_runner.invoke(app, ["process", "stop", "--pid", "12345"])

    assert result.exit_code == 0
    assert "✗ Error stopping process 12345" in result.stdout


@patch("psutil.Process", side_effect=psutil.NoSuchProcess(999))
def test_stop_command_by_pid_invalid_pid(mock_process, cli_runner) -> None:
    """Test stop command with invalid PID."""
    result = cli_runner.invoke(app, ["process", "stop", "--pid", "999"])

    assert result.exit_code == 0
    assert "! Process 999 no longer exists" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_port_success(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
) -> None:
    """Test successfully stopping process by port."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "Process with PID 12345 listening on port 50051 has been stopped" in result.stdout
    mock_aedt_process.kill.assert_called_once()


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50052)
def test_stop_command_by_port_not_found(mock_get_port, mock_process_iter, cli_runner, mock_aedt_process) -> None:
    """Test stopping process by port when no process found on that port."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "No AEDT process found listening on port 50051" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=False)
def test_stop_command_by_port_access_denied(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
) -> None:
    """Test stopping process by port when access is denied."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "✗ Access denied for process with PID 12345" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_port_no_such_process(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
) -> None:
    """Test stopping process by port when process no longer exists during operation."""
    mock_aedt_process.kill.side_effect = psutil.NoSuchProcess(mock_aedt_process.pid)
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "! Process 12345 no longer exists" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_port_generic_exception(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
) -> None:
    """Test stopping process by port when generic exception occurs."""
    mock_aedt_process.kill.side_effect = Exception("Dummy exception")
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "✗ Error stopping process 12345" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=None)
def test_stop_command_by_port_no_port_info(mock_get_port, mock_process_iter, cli_runner, mock_aedt_process) -> None:
    """Test stopping process by port when process has no port information."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "✗ No AEDT process found listening on port 50051" in result.stdout


# START COMMAND TESTS


@pytest.fixture
def mock_start_command():
    """Mock all dependencies for the start command tests."""
    with (
        patch("ansys.aedt.core.desktop.Desktop") as mock_desktop_class,
        patch("ansys.aedt.core.settings") as mock_settings,
        patch("threading.Thread") as mock_thread,
        patch("time.sleep") as mock_sleep,
    ):
        # Configure mock settings
        mock_settings.enable_logger = False

        # Configure mock Desktop class to return a mock instance
        mock_desktop_instance = Mock()
        mock_desktop_class.return_value = mock_desktop_instance

        yield {
            "desktop_class": mock_desktop_class,
            "desktop_instance": mock_desktop_instance,
            "settings": mock_settings,
            "thread": mock_thread,
            "sleep": mock_sleep,
        }


def test_start_command_default_parameters(cli_runner, mock_start_command) -> None:
    """Test start command with default parameters."""
    result = cli_runner.invoke(app, ["process", "start"])

    assert result.exit_code == 0
    assert "Starting AEDT 2026.1..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_with_version(cli_runner, mock_start_command) -> None:
    """Test start command with specific version."""
    result = cli_runner.invoke(app, ["process", "start", "--version", "2024.2"])

    assert result.exit_code == 0
    assert "Starting AEDT 2024.2..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_non_graphical(cli_runner, mock_start_command) -> None:
    """Test start command in non-graphical mode."""
    result = cli_runner.invoke(app, ["process", "start", "--non-graphical"])

    assert result.exit_code == 0
    assert "Starting in non-graphical mode..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_with_port(cli_runner, mock_start_command) -> None:
    """Test start command with specific port."""
    result = cli_runner.invoke(app, ["process", "start", "--port", "50055"])

    assert result.exit_code == 0
    assert "Using port: 50055" in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_student_version(cli_runner, mock_start_command) -> None:
    """Test start command for student version."""
    result = cli_runner.invoke(app, ["process", "start", "--student"])

    assert result.exit_code == 0
    assert "Starting student version..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


@patch("ansys.aedt.core.desktop.Desktop")
@patch("ansys.aedt.core.settings")
def test_start_command_desktop_exception(mock_settings, mock_desktop, cli_runner) -> None:
    """Test start command when Desktop initialization fails."""
    mock_desktop.side_effect = Exception("Dummy exception")

    result = cli_runner.invoke(app, ["process", "start"])

    assert result.exit_code == 0
    assert "✗ Error starting AEDT: Dummy exception" in result.stdout
    assert "Common issues:" in result.stdout
    assert "- AEDT not installed or not in PATH" in result.stdout
    assert "- Invalid version specified" in result.stdout
    assert "- License server not available" in result.stdout
    assert "- Insufficient permissions" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_get_config_path(mock_get_tests_folder, tmp_path) -> None:
    """Test _get_config_path helper function."""
    mock_get_tests_folder.return_value = tmp_path
    config_path, config = _get_config_path()

    assert config_path == tmp_path / "local_config.json"
    assert isinstance(config, dict)


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_load_config_existing_file(mock_get_tests_folder, tmp_path) -> None:
    """Test loading existing config file."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"
    test_config = {"desktopVersion": "2025.2", "NonGraphical": False}

    with open(config_file, "w") as f:
        json.dump(test_config, f)

    loaded_config = _load_config(config_file)
    assert loaded_config["desktopVersion"] == "2025.2"
    assert loaded_config["NonGraphical"] is False


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_load_config_invalid_file(mock_get_tests_folder, tmp_path) -> None:
    """Test loading invalid config file returns defaults."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"

    with open(config_file, "w") as f:
        f.write("invalid json")

    loaded_config = _load_config(config_file)
    assert loaded_config == DEFAULT_TEST_CONFIG


@pytest.fixture
def temp_personal_lib(tmp_path):
    """Create a temporary PersonalLib directory for testing."""
    personal_lib = tmp_path / "PersonalLib"
    personal_lib.mkdir()
    return personal_lib


def test_panels_add_help(cli_runner) -> None:
    """Test panels add help command."""
    result = cli_runner.invoke(app, ["panels", "add", "--help"])

    assert result.exit_code == 0
    assert "Add PyAEDT panels to AEDT installation" in result.stdout


def test_panels_add_success(cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions) -> None:
    """Test successful panel installation."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Installing PyAEDT panels..." in result.stdout
    assert "✓ PyAEDT panels installed successfully." in result.stdout
    assert "• PyAEDT Utilities (Console, CLI, Jupyter)" in result.stdout
    assert "• Run Script" in result.stdout
    assert "• Extension Manager" in result.stdout
    assert "• Version Manager" in result.stdout
    assert "Restart AEDT to see the new panels" in result.stdout

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        personal_lib=str(temp_personal_lib),
        skip_version_manager=False,
    )


def test_panels_add_with_skip_version_manager(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with skip version manager flag."""
    result = cli_runner.invoke(
        app,
        [
            "panels",
            "add",
            "--personal-lib",
            str(temp_personal_lib),
            "--skip-version-manager",
        ],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Skipping Version Manager tab..." in result.stdout
    assert "✓ PyAEDT panels installed successfully." in result.stdout
    assert "• Version Manager" not in result.stdout

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        personal_lib=str(temp_personal_lib),
        skip_version_manager=True,
    )


def test_panels_add_short_options(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with short option flags."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "-p", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Installing PyAEDT panels..." in result.stdout
    assert "✓ PyAEDT panels installed successfully." in result.stdout

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        personal_lib=str(temp_personal_lib),
        skip_version_manager=False,
    )


def test_panels_add_invalid_personal_lib_none(cli_runner, mock_installed_versions) -> None:
    """Test panel installation with whitespace-only personal_lib."""
    result = cli_runner.invoke(
        app,
        ["panels", "add"],
        input="   \n1\n",  # Whitespace only for path prompt, then selection
    )

    assert result.exit_code == 1
    assert "✗" in result.stdout
    assert "personal_lib" in result.stdout
    assert "invalid" in result.stdout.lower()


def test_panels_add_nonexistent_personal_lib(cli_runner, mock_installed_versions) -> None:
    """Test panel installation with non-existent PersonalLib path."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", "/nonexistent/path/PersonalLib"],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "✗" in result.stdout
    assert "does not exist" in result.stdout
    assert "Common PersonalLib locations:" in result.stdout


def test_panels_add_personal_lib_not_directory(cli_runner, tmp_path, mock_installed_versions) -> None:
    """Test panel installation when PersonalLib path is a file, not directory."""
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("dummy content")

    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(file_path)],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "✗" in result.stdout
    assert "not a directory" in result.stdout


@patch("ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt", return_value=False)
def test_panels_add_installer_returns_false(mock_func, cli_runner, temp_personal_lib, mock_installed_versions) -> None:
    """Test panel installation when installer returns False."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "✗ Failed to install PyAEDT panels" in result.stdout


@patch(
    "ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt",
    side_effect=ImportError("Cannot import installer"),
)
def test_panels_add_import_error(mock_func, cli_runner, temp_personal_lib, mock_installed_versions) -> None:
    """Test panel installation when import fails."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "✗ Import error: Cannot import installer" in result.stdout
    assert "Make sure PyAEDT is properly installed" in result.stdout


@patch(
    "ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt",
    side_effect=Exception("Unexpected error"),
)
def test_panels_add_generic_exception(mock_func, cli_runner, temp_personal_lib, mock_installed_versions) -> None:
    """Test panel installation when generic exception occurs."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "✗ Error installing panels: Unexpected error" in result.stdout


@patch("platform.system", return_value="Windows")
def test_panels_add_nonexistent_path_windows_hint(mock_platform, cli_runner, mock_installed_versions) -> None:
    """Test that Windows-specific path hint is shown on Windows."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", "C:\\nonexistent\\path"],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "Windows: C:\\Users\\<username>\\AppData\\Roaming\\Ansoft\\PersonalLib" in result.stdout


@patch("platform.system", return_value="Linux")
def test_panels_add_nonexistent_path_linux_hint(mock_platform, cli_runner, mock_installed_versions) -> None:
    """Test that Linux-specific path hint is shown on Linux."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", "/nonexistent/path"],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "Linux: /home/<username>/Ansoft/PersonalLib" in result.stdout


def test_panels_add_strips_whitespace(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test that path whitespace is stripped."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", f"  {temp_personal_lib}  "],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Installing PyAEDT panels..." in result.stdout

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        personal_lib=str(temp_personal_lib),
        skip_version_manager=False,
    )


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_save_config(mock_get_tests_folder, tmp_path) -> None:
    """Test saving config file."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "subdir" / "local_config.json"
    test_config = {"desktopVersion": "2025.2", "NonGraphical": True}

    _save_config(config_file, test_config)

    assert config_file.exists()
    with open(config_file, "r") as f:
        saved_config = json.load(f)
    assert saved_config == test_config


def test_display_config(cli_runner) -> None:
    """Test _display_config function."""
    test_config = {
        "desktopVersion": "2025.2",
        "NonGraphical": True,
        "local_example_folder": "",
    }
    descriptions = {
        "desktopVersion": "AEDT version",
        "NonGraphical": "Run without GUI",
    }

    # Just ensure it doesn't crash
    _display_config(test_config, "Test Config", descriptions)


# CONFIG COMMAND TESTS - CLI Integration Tests


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_desktop_version_command(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test desktop_version command."""
    mock_get_tests_folder.return_value = tmp_path
    result = cli_runner.invoke(app, ["config", "test", "desktop-version", "2025.2"])
    assert result.exit_code == 0
    assert "desktopVersion set to '2025.2'" in result.stdout
    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["desktopVersion"] == "2025.2"


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_desktop_version_invalid_format(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test desktop_version command with invalid format."""
    mock_get_tests_folder.return_value = tmp_path
    result = cli_runner.invoke(app, ["config", "test", "desktop-version", "invalid"])
    assert result.exit_code == 0
    assert "Invalid format" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_all_boolean_commands(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test all boolean configuration commands."""
    mock_get_tests_folder.return_value = tmp_path

    # Test all boolean commands
    bool_tests = [
        (["non-graphical", "true"], "NonGraphical set to True"),
        (["new-thread", "false"], "NewThread set to False"),
        (["skip-circuits", "true"], "skip_circuits set to True"),
        (["use-grpc", "false"], "use_grpc set to False"),
        (["close-desktop", "false"], "close_desktop set to False"),
        (["use-local-example-data", "true"], "use_local_example_data"),
        (["skip-modelithics", "false"], "skip_modelithics set to False"),
        (["use-pyedb-grpc", "false"], "use_pyedb_grpc set to False"),
    ]

    for cmd_parts, expected_output in bool_tests:
        result = cli_runner.invoke(app, ["config", "test"] + cmd_parts)
        assert result.exit_code == 0
        assert expected_output in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_local_example_folder_command(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test local_example_folder command."""
    mock_get_tests_folder.return_value = tmp_path
    result = cli_runner.invoke(
        app,
        ["config", "test", "local-example-folder", "/path/to/examples"],
    )
    assert result.exit_code == 0
    assert "local_example_folder set to '/path/to/examples'" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_persists_across_commands(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test that config changes persist across multiple commands."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"

    result1 = cli_runner.invoke(app, ["config", "test", "desktop-version", "2025.2"])
    assert result1.exit_code == 0

    result2 = cli_runner.invoke(app, ["config", "test", "non-graphical", "false"])
    assert result2.exit_code == 0

    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["desktopVersion"] == "2025.2"
    assert config["NonGraphical"] is False


# _get_tests_folder TESTS


def test_get_tests_folder_from_package(tmp_path) -> None:
    """Test _get_tests_folder when package structure exists."""
    # The function should find the tests folder from the package
    tests_folder = _get_tests_folder()
    assert isinstance(tests_folder, Path)


@patch("typer.confirm")
def test_prompt_config_value_bool_change(mock_confirm) -> None:
    """Test _prompt_config_value with boolean value change."""
    mock_confirm.return_value = True
    result = _prompt_config_value("test_key", True)
    assert result is False

    mock_confirm.return_value = False
    result = _prompt_config_value("test_key", True)
    assert result is True


@patch("typer.prompt")
def test_prompt_config_value_string(mock_prompt) -> None:
    """Test _prompt_config_value with string value."""
    mock_prompt.return_value = "new_value"
    result = _prompt_config_value("test_key", "old_value")
    assert result == "new_value"


@patch("typer.prompt")
def test_prompt_config_value_desktop_version_valid(mock_prompt) -> None:
    """Test _prompt_config_value with valid desktop version."""
    mock_prompt.return_value = "2024.2"
    result = _prompt_config_value("desktopVersion", "2025.2")
    assert result == "2024.2"


@patch("typer.prompt")
@patch("typer.secho")
def test_prompt_config_value_desktop_version_invalid_then_valid(mock_secho, mock_prompt) -> None:
    """Test _prompt_config_value with invalid then valid version."""
    mock_prompt.side_effect = ["invalid", "2024.2"]
    result = _prompt_config_value("desktopVersion", "2025.2")
    assert result == "2024.2"
    # Check that error was displayed
    assert mock_secho.call_count >= 1


@patch("typer.prompt")
def test_prompt_config_value_desktop_version_with_quotes(mock_prompt) -> None:
    """Test _prompt_config_value desktop version strips quotes."""
    mock_prompt.return_value = '"2024.2"'
    result = _prompt_config_value("desktopVersion", "2025.2")
    assert result == "2024.2"


@patch("typer.prompt")
def test_prompt_config_value_int(mock_prompt) -> None:
    """Test _prompt_config_value with integer value."""
    mock_prompt.return_value = 42
    result = _prompt_config_value("test_key", 10)
    assert result == 42


def test_prompt_config_value_unknown_type() -> None:
    """Test _prompt_config_value with unknown type."""
    result = _prompt_config_value("test_key", [1, 2, 3])
    assert result == [1, 2, 3]


# _update_bool_config TESTS (Interactive Mode)


@patch("ansys.aedt.core.cli.common._get_tests_folder")
@patch("typer.confirm")
def test_update_bool_config_interactive_change(mock_confirm, mock_get_tests_folder, tmp_path) -> None:
    """Test _update_bool_config interactive mode with change."""
    mock_get_tests_folder.return_value = tmp_path
    mock_confirm.return_value = True

    _update_bool_config("NonGraphical", None, "NonGraphical")

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    # Default is True, should change to False
    assert config["NonGraphical"] is False


@patch("ansys.aedt.core.cli.common._get_tests_folder")
@patch("typer.confirm")
def test_update_bool_config_interactive_no_change(mock_confirm, mock_get_tests_folder, tmp_path) -> None:
    """Test _update_bool_config interactive mode no change."""
    mock_get_tests_folder.return_value = tmp_path
    mock_confirm.return_value = False

    _update_bool_config("NonGraphical", None, "NonGraphical")

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    # Default is True, should stay True
    assert config["NonGraphical"] is True


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_update_bool_config_with_value(mock_get_tests_folder, tmp_path) -> None:
    """Test _update_bool_config with explicit value."""
    mock_get_tests_folder.return_value = tmp_path

    _update_bool_config("skip_circuits", True, "skip_circuits")

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["skip_circuits"] is True


# _update_string_config TESTS (Interactive Mode)


@patch("ansys.aedt.core.cli.common._get_tests_folder")
@patch("typer.prompt")
def test_update_string_config_interactive_no_validator(mock_prompt, mock_get_tests_folder, tmp_path) -> None:
    """Test _update_string_config interactive mode no validator."""
    mock_get_tests_folder.return_value = tmp_path
    mock_prompt.return_value = "/new/path"

    _update_string_config("local_example_folder", None, "local_example_folder")

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["local_example_folder"] == "/new/path"


@patch("ansys.aedt.core.cli.common._get_tests_folder")
@patch("typer.prompt")
def test_update_string_config_interactive_with_validator_valid(mock_prompt, mock_get_tests_folder, tmp_path) -> None:
    """Test _update_string_config interactive mode valid."""
    mock_get_tests_folder.return_value = tmp_path
    mock_prompt.return_value = "2025.2"

    def validator(v):
        if re.match(r"^\d{4}\.\d$", v):
            return True, ""
        return False, "Invalid format"

    _update_string_config("desktopVersion", None, "desktopVersion", validator)

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["desktopVersion"] == "2025.2"


@patch("ansys.aedt.core.cli.common._get_tests_folder")
@patch("typer.prompt")
def test_update_string_config_interactive_validator_invalid_valid(mock_prompt, mock_get_tests_folder, tmp_path) -> None:
    """Test _update_string_config invalid then valid value."""
    mock_get_tests_folder.return_value = tmp_path
    mock_prompt.side_effect = ["invalid", "2025.2"]

    def validator(v):
        if re.match(r"^\d{4}\.\d$", v):
            return True, ""
        return False, "Invalid format"

    _update_string_config("desktopVersion", None, "desktopVersion", validator)

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["desktopVersion"] == "2025.2"


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_update_string_config_with_value_valid(mock_get_tests_folder, tmp_path) -> None:
    """Test _update_string_config with explicit valid value."""
    mock_get_tests_folder.return_value = tmp_path

    def validator(v):
        if re.match(r"^\d{4}\.\d$", v):
            return True, ""
        return False, "Invalid format"

    _update_string_config("desktopVersion", "2023.2", "desktopVersion", validator)

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["desktopVersion"] == "2023.2"


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_update_string_config_with_value_invalid(mock_get_tests_folder, tmp_path) -> None:
    """Test _update_string_config with explicit invalid value."""
    mock_get_tests_folder.return_value = tmp_path

    def validator(v):
        if re.match(r"^\d{4}\.\d$", v):
            return True, ""
        return False, "Invalid format"

    _update_string_config("desktopVersion", "invalid", "desktopVersion", validator)

    config_file = tmp_path / "local_config.json"
    # Config should not be updated with invalid value
    if config_file.exists():
        with open(config_file, "r") as f:
            config = json.load(f)
        # Should still have default value
        assert config["desktopVersion"] == "2025.2"


# config_test COMMAND TESTS


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_show_flag(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test config test command with --show flag."""
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_app, ["--show"])

    assert result.exit_code == 0
    assert "Current Test Configuration" in result.stdout
    assert "2026.1" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_show_flag_short(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test config test command with -s flag."""
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_app, ["-s"])

    assert result.exit_code == 0
    assert "Current Test Configuration" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_interactive_no_modify(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test config test command declining to modify."""
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_app, input="n\n")

    assert result.exit_code == 0
    assert "No changes made" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_interactive_with_modifications(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test config test command with interactive modifications."""
    mock_get_tests_folder.return_value = tmp_path

    # Answer yes to modify, then answer for each config value
    # For desktopVersion: provide new version
    # For bools: press enter to keep or change
    input_data = "y\n2025.2\nn\nn\nn\nn\nn\nn\n\nn\n"

    result = cli_runner.invoke(test_app, input=input_data)

    assert result.exit_code == 0
    assert "Configuration Updated Successfully" in result.stdout

    config_file = tmp_path / "local_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    assert config["desktopVersion"] == "2025.2"


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_creates_config_file(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test config test command creates config file if not exists."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"

    assert not config_file.exists()

    result = cli_runner.invoke(test_app, ["--show"])

    assert result.exit_code == 0
    assert config_file.exists()


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_loads_existing_config(mock_get_tests_folder, tmp_path, cli_runner) -> None:
    """Test config test command loads existing config file."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"

    # Create existing config
    existing_config = {"desktopVersion": "2023.1", "NonGraphical": False}
    with open(config_file, "w") as f:
        json.dump(existing_config, f)

    result = cli_runner.invoke(test_app, ["--show"])

    assert result.exit_code == 0
    assert "2023.1" in result.stdout
    assert "Configuration file found" in result.stdout


# PANELS ADD - NO VERSIONS INSTALLED TEST


@patch(
    "ansys.aedt.core.internal.aedt_versions.AedtVersions.installed_versions",
    new_callable=lambda: property(lambda self: {}),
)
def test_panels_add_no_versions_installed(mock_installed_versions, cli_runner) -> None:
    """Test panels add when no AEDT versions are installed."""
    result = cli_runner.invoke(
        app,
        [
            "panels",
            "add",
            "--personal-lib",
            "dummy",
        ],
    )

    assert result.exit_code == 1
    assert "✗ No AEDT versions found on this system." in result.stdout
    assert "Please install AEDT before running this command." in (result.stdout)


# PANELS ADD WITH RESET OPTION TESTS


def test_panels_add_with_reset_success(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test successful panel installation with reset option."""
    # Create existing Toolkits directory
    toolkits_dir = temp_personal_lib / "Toolkits"
    toolkits_dir.mkdir()
    test_file = toolkits_dir / "test.txt"
    test_file.write_text("test content")

    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib), "--reset"],
        input="1\n",
    )

    assert result.exit_code == 0
    mock_add_pyaedt_to_aedt.assert_called_once()


def test_panels_add_with_reset_short_option(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with reset short option."""
    # Create existing Toolkits directory
    toolkits_dir = temp_personal_lib / "Toolkits"
    toolkits_dir.mkdir()

    result = cli_runner.invoke(
        app,
        ["panels", "add", "-p", str(temp_personal_lib), "-r"],
        input="1\n",
    )

    assert result.exit_code == 0


def test_panels_add_with_reset_no_toolkits(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with reset when Toolkits doesn't exist."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib), "--reset"],
        input="1\n",
    )

    assert result.exit_code == 0
    mock_add_pyaedt_to_aedt.assert_called_once()


def test_panels_add_with_reset_nested_content(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with reset when Toolkits has nested content."""
    # Create Toolkits directory with nested content
    toolkits_dir = temp_personal_lib / "Toolkits"
    toolkits_dir.mkdir()

    nested_dir = toolkits_dir / "SubFolder" / "DeepFolder"
    nested_dir.mkdir(parents=True)
    nested_file = nested_dir / "nested_file.txt"
    nested_file.write_text("nested content")

    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib), "--reset"],
        input="1\n",
    )

    assert result.exit_code == 0
    assert not toolkits_dir.exists() or not nested_dir.exists()  # Either deleted or recreated by installer


@patch("shutil.rmtree", side_effect=PermissionError("Permission denied"))
def test_panels_add_with_reset_permission_error(
    mock_rmtree, cli_runner, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with reset when permission error occurs."""
    # Create Toolkits directory
    toolkits_dir = temp_personal_lib / "Toolkits"
    toolkits_dir.mkdir()

    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib), "--reset"],
        input="1\n",
    )

    assert result.exit_code == 1


@patch("shutil.rmtree", side_effect=Exception("Unexpected error"))
def test_panels_add_with_reset_generic_exception(
    mock_rmtree, cli_runner, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with reset when generic exception occurs."""
    # Create Toolkits directory
    toolkits_dir = temp_personal_lib / "Toolkits"
    toolkits_dir.mkdir()

    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib), "--reset"],
        input="1\n",
    )

    assert result.exit_code == 1


def test_panels_add_with_reset_and_skip_version_manager(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
) -> None:
    """Test panel installation with both reset and skip version manager options."""
    # Create existing Toolkits directory
    toolkits_dir = temp_personal_lib / "Toolkits"
    toolkits_dir.mkdir()

    result = cli_runner.invoke(
        app,
        [
            "panels",
            "add",
            "--personal-lib",
            str(temp_personal_lib),
            "--reset",
            "--skip-version-manager",
        ],
        input="1\n",
    )

    assert result.exit_code == 0

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        personal_lib=str(temp_personal_lib),
        skip_version_manager=True,
    )


# DOC TESTS


def test_doc_group_help(cli_runner) -> None:
    """Ensure doc command group help works."""
    result = cli_runner.invoke(app, ["doc", "--help"])

    assert result.exit_code == 0
    assert "Documentation commands" in result.stdout


def test_doc_examples_command(cli_runner, mock_online_help) -> None:
    """Test doc examples command."""
    result = cli_runner.invoke(app, ["doc", "examples"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.examples.assert_called_once_with()


def test_doc_github_command(cli_runner, mock_online_help) -> None:
    """Test doc github command."""
    result = cli_runner.invoke(app, ["doc", "github"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.github.assert_called_once_with()


def test_doc_user_guide_command(cli_runner, mock_online_help) -> None:
    """Test doc user_guide command."""
    result = cli_runner.invoke(app, ["doc", "user-guide"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.user_guide.assert_called_once_with()


def test_doc_getting_started_command(cli_runner, mock_online_help) -> None:
    """Test doc getting_started command."""
    result = cli_runner.invoke(app, ["doc", "getting-started"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.getting_started.assert_called_once_with()


def test_doc_installation_command(cli_runner, mock_online_help) -> None:
    """Test doc installation command."""
    result = cli_runner.invoke(app, ["doc", "installation"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.installation_guide.assert_called_once_with()


def test_doc_api_reference_command(cli_runner, mock_online_help) -> None:
    """Test doc api_reference command."""
    result = cli_runner.invoke(app, ["doc", "api"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.api_reference.assert_called_once_with()


def test_doc_changelog_command_no_arg(cli_runner, mock_online_help) -> None:
    """Test doc changelog command without version argument."""
    result = cli_runner.invoke(app, ["doc", "changelog"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.changelog.assert_called_once_with(None)


def test_doc_changelog_command_with_version(cli_runner, mock_online_help) -> None:
    """Test doc changelog command with explicit version."""
    result = cli_runner.invoke(app, ["doc", "changelog", "0.22.0"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.changelog.assert_called_once_with("0.22.0")


def test_doc_issues_command(cli_runner, mock_online_help) -> None:
    """Test doc issues command."""
    result = cli_runner.invoke(app, ["doc", "issues"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.issues.assert_called_once_with()


def test_doc_search_command_single_keyword(cli_runner, mock_online_help) -> None:
    """Test doc search command with single keyword."""
    result = cli_runner.invoke(app, ["doc", "search", "Maxwell"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.search.assert_called_once_with("Maxwell")


def test_doc_search_command_multiple_keywords(cli_runner, mock_online_help) -> None:
    """Test doc search command with multiple keywords."""
    result = cli_runner.invoke(app, ["doc", "search", "Maxwell", "3D", "simulation"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.search.assert_called_once_with("Maxwell 3D simulation")


def test_doc_search_command_no_keywords(cli_runner, mock_online_help) -> None:
    """Test doc search command without keywords."""
    result = cli_runner.invoke(app, ["doc", "search"])

    assert result.exit_code == 1
    assert "✗ Error: Please provide at least one search keyword" in result.stdout
    assert "Usage: pyaedt doc search" in result.stdout
    # Should not call online_help.search when no keywords provided
    mock_online_help.search.assert_not_called()


def test_doc_callback_opens_home_and_shows_help(cli_runner, mock_online_help) -> None:
    """Test doc command without subcommand opens home and displays help."""
    result = cli_runner.invoke(app, ["doc"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.home.assert_called_once_with()
    # Verify help text is displayed
    assert "Documentation commands" in result.stdout
    assert "examples" in result.stdout
    assert "github" in result.stdout


# ATTACH TESTS


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
def test_attach_command_no_aedt_processes(mock_find_procs, cli_runner) -> None:
    """Test attach command when no AEDT processes are running."""
    mock_find_procs.return_value = []

    result = cli_runner.invoke(app, ["process", "attach"])

    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout
    assert "Start AEDT first using:" in result.stdout
    assert "pyaedt start" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_single_process_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with single process and user quits."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="q\n")

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "1. PID: 12345" in result.stdout
    assert "Port: 50051" in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=None)
def test_attach_command_process_com_mode(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command displays COM mode for processes without gRPC port."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="q\n")

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "COM mode" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_invalid_input_then_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with invalid input followed by quit."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="abc\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid input. Please enter a number." in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_out_of_range_then_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with out of range selection then quit."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="5\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid selection. Please enter a number between 1 and 1." in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_valid_selection(
    mock_launch_console, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test attach command with valid process selection."""
    # Mock process with version info in cmdline
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="1\n")

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "1. PID: 12345" in result.stdout
    assert "Version: 2025.2" in result.stdout
    assert "Attaching to process 12345..." in result.stdout
    mock_launch_console.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", side_effect=[50051, 50052])
def test_attach_command_multiple_processes(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with multiple AEDT processes."""
    mock_proc2 = Mock(spec=psutil.Process)
    mock_proc2.pid = 67890
    mock_proc2.name.return_value = "ansysedt.exe"
    mock_proc2.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-grpcsrv",
        "50052",
    ]

    mock_find_procs.return_value = [mock_aedt_process, mock_proc2]

    result = cli_runner.invoke(app, ["process", "attach"], input="q\n")

    assert result.exit_code == 0
    assert "Found 2 AEDT process(es)" in result.stdout
    assert "1. PID: 12345" in result.stdout
    assert "2. PID: 67890" in result.stdout
    assert "Select process number (1-2)" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", side_effect=[50051, 50052])
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_select_second_process(
    mock_launch_console, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test attach command selecting second process from list."""
    mock_proc2 = Mock(spec=psutil.Process)
    mock_proc2.pid = 67890
    mock_proc2.name.return_value = "ansysedt.exe"
    mock_proc2.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-grpcsrv",
        "50052",
    ]

    mock_find_procs.return_value = [mock_aedt_process, mock_proc2]

    result = cli_runner.invoke(app, ["process", "attach"], input="2\n")

    assert result.exit_code == 0
    assert "Attaching to process 67890..." in result.stdout
    mock_launch_console.assert_called_once_with(67890, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_version_extraction_unknown(mock_get_port, mock_find_procs, cli_runner) -> None:
    """Test attach command when version cannot be extracted from cmdline."""
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 12345
    mock_proc.name.return_value = "ansysedt.exe"
    mock_proc.cmdline.return_value = ["ansysedt.exe"]  # No version info

    mock_find_procs.return_value = [mock_proc]

    result = cli_runner.invoke(app, ["process", "attach"], input="q\n")

    assert result.exit_code == 0
    assert "Version: unknown" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_with_student_version(mock_launch_console, mock_get_port, mock_find_procs, cli_runner) -> None:
    """Test attach command with AEDT student version process."""
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 99999
    mock_proc.name.return_value = "ansysedtsv.exe"  # Student version
    mock_proc.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedtsv.exe",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_proc]

    result = cli_runner.invoke(app, ["process", "attach"], input="1\n")

    assert result.exit_code == 0
    assert "Attaching to process 99999..." in result.stdout
    mock_launch_console.assert_called_once_with(99999, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_case_insensitive_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command accepts 'Q' (uppercase) to quit."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="Q\n")

    assert result.exit_code == 0
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_zero_selection(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with zero as selection."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="0\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid selection. Please enter a number between 1 and 1." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_negative_selection(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with negative number as selection."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="-1\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid selection. Please enter a number between 1 and 1." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_retries_on_invalid_then_succeeds(
    mock_launch_console, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test attach command retries after multiple invalid inputs."""
    mock_aedt_process.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="abc\n99\n-5\n1\n")

    assert result.exit_code == 0
    assert result.stdout.count("✗ Invalid") >= 2  # Multiple invalid attempts
    assert "Attaching to process 12345..." in result.stdout
    mock_launch_console.assert_called_once()


# LAUNCH CONSOLE SETUP TESTS


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_launch_console_setup_called_with_correct_args(
    mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test that _launch_console_setup is called with correct arguments."""
    mock_aedt_process.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="1\n")

    assert result.exit_code == 0
    mock_launch.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("pathlib.Path")
@patch("subprocess.run", side_effect=KeyboardInterrupt())
def test_launch_console_setup_keyboard_interrupt(
    mock_subprocess, mock_path_class, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test _launch_console_setup handles KeyboardInterrupt."""
    # Mock the console_setup.py path
    mock_console_path = Mock()
    mock_console_path.exists.return_value = True
    mock_console_path.__str__ = lambda self: "/fake/path/console_setup.py"

    mock_path_instance = Mock()
    mock_path_instance.__truediv__ = Mock(
        side_effect=[Mock(__truediv__=Mock(side_effect=[Mock(__truediv__=Mock(return_value=mock_console_path))]))]
    )
    mock_path_class.return_value = mock_path_instance

    mock_aedt_process.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="1\n")

    # Should handle KeyboardInterrupt gracefully
    assert "Interrupted" in result.stdout or result.exit_code == 0


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("pathlib.Path")
@patch("subprocess.run", side_effect=Exception("Subprocess error"))
def test_launch_console_setup_generic_exception(
    mock_subprocess, mock_path_class, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test _launch_console_setup handles generic exceptions."""
    # Mock the console_setup.py path
    mock_console_path = Mock()
    mock_console_path.exists.return_value = True
    mock_console_path.__str__ = lambda self: "/fake/path/console_setup.py"

    mock_path_instance = Mock()
    mock_path_instance.__truediv__ = Mock(
        side_effect=[Mock(__truediv__=Mock(side_effect=[Mock(__truediv__=Mock(return_value=mock_console_path))]))]
    )
    mock_path_class.return_value = mock_path_instance

    mock_aedt_process.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach"], input="1\n")

    # Should display error message
    assert "✗ Error launching console" in result.stdout or result.exit_code == 0


# ATTACH WITH PID OPTION TESTS


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_success(mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with --pid option for successful attachment."""
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-ng",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach", "--pid", "12345"])

    assert result.exit_code == 0
    assert "Attaching to process 12345" in result.stdout
    mock_launch.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_short_option(
    mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test attach command with -p short option."""
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-ng",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach", "-p", "12345"])

    assert result.exit_code == 0
    assert "Attaching to process 12345" in result.stdout
    mock_launch.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
def test_attach_with_pid_not_found(mock_find_procs, cli_runner, mock_aedt_process) -> None:
    """Test attach command with --pid when process not found."""
    mock_aedt_process.pid = 99999
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach", "--pid", "12345"])

    assert result.exit_code == 0
    assert "✗ No AEDT process found with PID 12345" in result.stdout
    assert "Available AEDT processes:" in result.stdout
    assert "PID: 99999" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
def test_attach_with_pid_no_processes_running(mock_find_procs, cli_runner) -> None:
    """Test attach command with --pid when no AEDT processes are running."""
    mock_find_procs.return_value = []

    result = cli_runner.invoke(app, ["process", "attach", "--pid", "12345"])

    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout
    assert "pyaedt start" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_version_extraction(
    mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test attach command extracts version correctly from command line."""
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v241\\AnsysEM\\ansysedt.exe",
        "-ng",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach", "--pid", "12345"])

    assert result.exit_code == 0
    mock_launch.assert_called_once_with(12345, "2024.1")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_unknown_version(
    mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
) -> None:
    """Test attach command handles unknown version."""
    mock_aedt_process.cmdline.return_value = ["ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["process", "attach", "--pid", "12345"])

    assert result.exit_code == 0
    mock_launch.assert_called_once_with(12345, "unknown")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_multiple_processes(mock_launch, mock_get_port, mock_find_procs, cli_runner) -> None:
    """Test attach command with --pid when multiple processes exist."""
    proc1 = Mock(spec=psutil.Process)
    proc1.pid = 12345
    proc1.name.return_value = "ansysedt.exe"
    proc1.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]

    proc2 = Mock(spec=psutil.Process)
    proc2.pid = 67890
    proc2.name.return_value = "ansysedt.exe"
    proc2.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v241\\AnsysEM\\ansysedt.exe"]

    mock_find_procs.return_value = [proc1, proc2]

    result = cli_runner.invoke(app, ["process", "attach", "--pid", "67890"])

    assert result.exit_code == 0
    assert "Attaching to process 67890" in result.stdout
    mock_launch.assert_called_once_with(67890, "2024.1")


# ---------------------------------------------------------------------------
# SESSION MANAGEMENT TESTS
# ---------------------------------------------------------------------------


def test_save_and_load_session(tmp_path):
    """Test saving and loading a session."""
    with (
        patch("ansys.aedt.core.cli.common.SESSION_DIR", tmp_path),
        patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "session.json"),
    ):
        _save_session(50051, "localhost", "2026.1")
        session = _load_session()
        assert session == {"port": 50051, "machine": "localhost", "version": "2026.1"}


def test_load_session_no_file(tmp_path):
    """Test loading session when no file exists."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        assert _load_session() is None


def test_clear_session(tmp_path):
    """Test clearing session file."""
    session_file = tmp_path / "session.json"
    session_file.write_text("{}")
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file):
        _clear_session()
        assert not session_file.exists()


def test_clear_session_no_file(tmp_path):
    """Test clearing session when no file exists (no error)."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        _clear_session()  # Should not raise


def test_json_output_ok(capsys):
    """Test JSON output in OK mode."""
    common_mod._json_mode = True
    try:
        _output(data={"version": "2026.1"})
        out = capsys.readouterr().out
        result = json.loads(out)
        assert result["status"] == "ok"
        assert result["data"]["version"] == "2026.1"
    finally:
        common_mod._json_mode = False


def test_json_output_error(capsys):
    """Test JSON output in error mode."""
    common_mod._json_mode = True
    try:
        _output(error="something failed")
        out = capsys.readouterr().out
        result = json.loads(out)
        assert result["status"] == "error"
        assert result["error"] == "something failed"
    finally:
        common_mod._json_mode = False


def test_json_output_noop_in_human_mode(capsys):
    """Test that _output does nothing in human mode."""
    common_mod._json_mode = False
    _output(data={"test": True})
    out = capsys.readouterr().out
    assert out == ""


# ---------------------------------------------------------------------------
# JSON MODE CALLBACK TEST
# ---------------------------------------------------------------------------


def test_json_flag_sets_json_mode(cli_runner):
    """Test that --json flag sets _json_mode."""
    # Use version command which always works
    result = cli_runner.invoke(app, ["--json", "version"])
    assert result.exit_code == 0
    # Reset after test
    common_mod._json_mode = False


# ---------------------------------------------------------------------------
# CONNECTION & STATUS COMMAND TESTS
# ---------------------------------------------------------------------------


def test_connect_success(cli_runner, tmp_path):
    """Test successful connection."""
    session_file = tmp_path / "session.json"
    mock_desktop = Mock()
    mock_desktop.port = 50051
    mock_desktop.aedt_version_id = "2026.1"
    with (
        patch("ansys.aedt.core.desktop.Desktop", return_value=mock_desktop),
        patch("ansys.aedt.core.settings"),
        patch("ansys.aedt.core.cli.common.SESSION_DIR", tmp_path),
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
    ):
        result = cli_runner.invoke(app, ["session", "connect", "--port", "50051"])
        assert result.exit_code == 0
        assert "Connected" in result.output
        assert session_file.exists()


def test_connect_json(cli_runner, tmp_path):
    """Test connect with JSON output."""
    session_file = tmp_path / "session.json"
    mock_desktop = Mock()
    mock_desktop.port = 50051
    mock_desktop.aedt_version_id = "2026.1"
    with (
        patch("ansys.aedt.core.desktop.Desktop", return_value=mock_desktop),
        patch("ansys.aedt.core.settings"),
        patch("ansys.aedt.core.cli.common.SESSION_DIR", tmp_path),
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
    ):
        result = cli_runner.invoke(app, ["--json", "session", "connect", "--port", "50051"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["data"]["port"] == 50051
    common_mod._json_mode = False


def test_connect_failure(cli_runner):
    """Test connection failure."""
    with (
        patch("ansys.aedt.core.desktop.Desktop", side_effect=Exception("Connection failed")),
        patch("ansys.aedt.core.settings"),
    ):
        result = cli_runner.invoke(app, ["session", "connect", "--port", "50051"])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_disconnect_with_session(cli_runner, tmp_path):
    """Test disconnect when session exists."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common.SESSION_DIR", tmp_path),
        patch("ansys.aedt.core.desktop.Desktop"),
        patch("ansys.aedt.core.settings"),
    ):
        result = cli_runner.invoke(app, ["session", "disconnect"])
        assert result.exit_code == 0
        assert "Disconnected" in result.output


def test_disconnect_no_session(cli_runner, tmp_path):
    """Test disconnect when no session exists."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["session", "disconnect"])
        assert result.exit_code == 0
        assert "Disconnected" in result.output


def test_status_no_session(cli_runner, tmp_path):
    """Test status when no session exists."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["session", "status"])
        assert result.exit_code == 1


def test_status_success(cli_runner, tmp_path):
    """Test status with active connection."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    mock_desktop.aedt_version_id = "2026.1"
    mock_desktop.port = 50051
    mock_odesktop = Mock()
    mock_odesktop.GetProjectList.return_value = ["Project1"]
    mock_odesktop.GetActiveProject.return_value = Mock(GetName=Mock(return_value="Project1"))
    mock_odesktop.GetProcessID.return_value = 12345
    mock_desktop.odesktop = mock_odesktop
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["session", "status"])
        assert result.exit_code == 0
        assert "AEDT Status" in result.output


def test_aedt_versions(cli_runner, mock_installed_versions):
    """Test aedt-versions lists versions."""
    result = cli_runner.invoke(app, ["aedt-versions"])
    assert result.exit_code == 0
    assert "2025.2" in result.output


def test_aedt_versions_json(cli_runner, mock_installed_versions):
    """Test aedt-versions with JSON output."""
    result = cli_runner.invoke(app, ["--json", "aedt-versions"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert "2025.2" in data["data"]["versions"]
    common_mod._json_mode = False


# ---------------------------------------------------------------------------
# PROJECT & DESIGN COMMAND TESTS
# ---------------------------------------------------------------------------


def _mock_desktop_with_session(tmp_path):
    """Create a mock desktop and session file."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    mock_odesktop = Mock()
    mock_desktop.odesktop = mock_odesktop
    return session_file, mock_desktop, mock_odesktop


def test_list_projects(cli_runner, tmp_path):
    """Test list-projects command."""
    session_file, mock_desktop, mock_odesktop = _mock_desktop_with_session(tmp_path)
    mock_odesktop.GetProjectList.return_value = ["Project1", "Project2"]
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Project1" in result.output


def test_list_projects_json(cli_runner, tmp_path):
    """Test list-projects with JSON output."""
    session_file, mock_desktop, mock_odesktop = _mock_desktop_with_session(tmp_path)
    mock_odesktop.GetProjectList.return_value = ["Project1"]
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["--json", "project", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert "Project1" in data["data"]["projects"]
    common_mod._json_mode = False


def test_list_designs(cli_runner, tmp_path):
    """Test list-designs command."""
    session_file, mock_desktop, mock_odesktop = _mock_desktop_with_session(tmp_path)
    mock_proj = Mock()
    mock_proj.GetName.return_value = "TestProject"
    mock_proj.GetTopDesignList.return_value = ["Design1"]
    mock_design = Mock()
    mock_design.GetDesignType.return_value = "HFSS"
    mock_proj.SetActiveDesign.return_value = mock_design
    mock_odesktop.GetActiveProject.return_value = mock_proj
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["project", "list-designs"])
        assert result.exit_code == 0
        assert "Design1" in result.output


def test_open_project(cli_runner, tmp_path):
    """Test open-project command."""
    session_file, mock_desktop, mock_odesktop = _mock_desktop_with_session(tmp_path)
    mock_proj = Mock()
    mock_proj.GetName.return_value = "MyProject"
    mock_odesktop.GetActiveProject.return_value = mock_proj
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["project", "open", "C:/test/project.aedt"])
        assert result.exit_code == 0
        assert "Opened" in result.output


def test_save_project(cli_runner, tmp_path):
    """Test save-project command."""
    session_file, mock_desktop, mock_odesktop = _mock_desktop_with_session(tmp_path)
    mock_proj = Mock()
    mock_proj.GetName.return_value = "MyProject"
    mock_odesktop.GetActiveProject.return_value = mock_proj
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["project", "save"])
        assert result.exit_code == 0
        assert "saved" in result.output


def test_list_projects_no_session(cli_runner, tmp_path):
    """Test list-projects without active session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["project", "list"])
        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# SCRIPT EXECUTION TESTS
# ---------------------------------------------------------------------------


def test_run_script_file_not_found(cli_runner, tmp_path):
    """Test run-script with missing file."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["script", "run", "nonexistent.py"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_run_script_success(cli_runner, tmp_path):
    """Test successful script execution."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    script_file = tmp_path / "test_script.py"
    script_file.write_text("print('hello')")
    mock_desktop = Mock()
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["script", "run", str(script_file)])
        assert result.exit_code == 0
        assert "executed" in result.output


def test_run_code_no_session(cli_runner, tmp_path):
    """Test run-code without session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["script", "code", "result = 42"])
        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# FILE MANAGEMENT TESTS
# ---------------------------------------------------------------------------


def test_list_files_in_dir(cli_runner, tmp_path):
    """Test list-files command."""
    (tmp_path / "test.txt").write_text("hello")
    (tmp_path / "data.csv").write_text("a,b")
    result = cli_runner.invoke(app, ["file", "list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "test.txt" in result.output


def test_list_files_json(cli_runner, tmp_path):
    """Test list-files with JSON output."""
    (tmp_path / "test.txt").write_text("hello")
    result = cli_runner.invoke(app, ["--json", "file", "list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["count"] >= 1
    common_mod._json_mode = False


def test_list_files_nonexistent_dir(cli_runner, tmp_path):
    """Test list-files with nonexistent directory."""
    result = cli_runner.invoke(app, ["file", "list", "--dir", str(tmp_path / "nope")])
    assert result.exit_code == 1


def test_upload_file(cli_runner, tmp_path):
    """Test upload command."""
    src = tmp_path / "source.txt"
    src.write_text("test content")
    dest_dir = tmp_path / "dest"
    result = cli_runner.invoke(app, ["file", "upload", str(src), "--to", str(dest_dir)])
    assert result.exit_code == 0
    assert (dest_dir / "source.txt").exists()


def test_upload_file_not_found(cli_runner, tmp_path):
    """Test upload with missing file."""
    result = cli_runner.invoke(app, ["file", "upload", str(tmp_path / "nope.txt")])
    assert result.exit_code == 1


def test_download_file(cli_runner, tmp_path):
    """Test download command."""
    src = tmp_path / "remote.txt"
    src.write_text("result data")
    dest_dir = tmp_path / "local"
    result = cli_runner.invoke(app, ["file", "download", str(src), "--to", str(dest_dir)])
    assert result.exit_code == 0
    assert (dest_dir / "remote.txt").exists()


def test_download_file_not_found(cli_runner, tmp_path):
    """Test download with missing file."""
    result = cli_runner.invoke(app, ["file", "download", str(tmp_path / "nope.txt")])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# UTILITY COMMAND TESTS
# ---------------------------------------------------------------------------


def test_clear_command(cli_runner, tmp_path):
    """Test clear command."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    mock_odesktop = Mock()
    mock_odesktop.GetProjectList.return_value = ["P1"]
    mock_desktop.odesktop = mock_odesktop
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["utility", "clear"])
        assert result.exit_code == 0
        assert "cleared" in result.output


def test_clear_no_session(cli_runner, tmp_path):
    """Test clear without session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["utility", "clear"])
        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# EXPORT COMMAND TESTS
# ---------------------------------------------------------------------------


def test_screenshot_no_session(cli_runner, tmp_path):
    """Test screenshot without session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["export", "screenshot"])
        assert result.exit_code == 1


def test_export_touchstone_no_session(cli_runner, tmp_path):
    """Test export-touchstone without session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["export", "touchstone", "out.s2p"])
        assert result.exit_code == 1


def test_export_3d_no_session(cli_runner, tmp_path):
    """Test export-3d without session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["export", "3d", "model.step"])
        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# JSON MODE TESTS FOR ALL COMMAND GROUPS
# ---------------------------------------------------------------------------


@patch("ansys.aedt.core.__version__", "0.22.0")
def test_version_json(cli_runner):
    """Test process version with --json returns structured output."""
    result = cli_runner.invoke(app, ["--json", "version"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["version"] == "0.22.0"
    common_mod._json_mode = False


@patch("psutil.process_iter")
def test_processes_json_no_aedt(mock_process_iter, cli_runner):
    """Test process list with --json returns structured output when no AEDT running."""
    mock_process_iter.return_value = []
    result = cli_runner.invoke(app, ["--json", "process", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["processes"] == []
    assert data["data"]["count"] == 0
    common_mod._json_mode = False


@patch("psutil.process_iter")
def test_processes_json_with_aedt(mock_process_iter, cli_runner, mock_aedt_process):
    """Test process list with --json returns process data."""
    mock_process_iter.return_value = [mock_aedt_process]
    result = cli_runner.invoke(app, ["--json", "process", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["count"] == 1
    assert data["data"]["processes"][0]["pid"] == 12345
    assert data["data"]["processes"][0]["port"] == 50051
    common_mod._json_mode = False


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_all_json(mock_access, mock_process_iter, cli_runner, mock_aedt_process):
    """Test process stop --all with --json returns structured output."""
    mock_process_iter.return_value = [mock_aedt_process]
    result = cli_runner.invoke(app, ["--json", "process", "stop", "--all"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert 12345 in data["data"]["stopped"]
    assert data["data"]["errors"] == []
    common_mod._json_mode = False


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_by_pid_json(mock_access, mock_process_class, cli_runner, mock_aedt_process):
    """Test process stop --pid with --json returns structured output."""
    mock_process_class.return_value = mock_aedt_process
    result = cli_runner.invoke(app, ["--json", "process", "stop", "--pid", "12345"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert 12345 in data["data"]["stopped"]
    common_mod._json_mode = False


@patch("ansys.aedt.core.desktop.Desktop")
@patch("ansys.aedt.core.settings")
def test_start_json(mock_settings, mock_desktop, cli_runner):
    """Test process start with --json returns structured output."""
    mock_instance = Mock()
    mock_instance.port = 50051
    mock_desktop.return_value = mock_instance
    result = cli_runner.invoke(app, ["--json", "process", "start"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["port"] == 50051
    common_mod._json_mode = False


@patch("ansys.aedt.core.desktop.Desktop", side_effect=Exception("fail"))
@patch("ansys.aedt.core.settings")
def test_start_json_error(mock_settings, mock_desktop, cli_runner):
    """Test process start with --json returns error on failure."""
    result = cli_runner.invoke(app, ["--json", "process", "start"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert "fail" in data["error"]
    common_mod._json_mode = False


def test_disconnect_json(cli_runner, tmp_path):
    """Test disconnect with --json returns structured output."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "session", "disconnect"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["data"]["disconnected"] is True
    common_mod._json_mode = False


def test_status_json_no_session(cli_runner, tmp_path):
    """Test status with --json when no session exists."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "session", "status"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False


def test_connect_json_error(cli_runner):
    """Test connect with --json on failure."""
    with (
        patch("ansys.aedt.core.desktop.Desktop", side_effect=Exception("conn fail")),
        patch("ansys.aedt.core.settings"),
    ):
        result = cli_runner.invoke(app, ["--json", "session", "connect", "--port", "50051"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
        assert "conn fail" in data["error"]
    common_mod._json_mode = False


def test_list_projects_no_session_json(cli_runner, tmp_path):
    """Test project list with --json when no session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "project", "list"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False


def test_list_designs_json(cli_runner, tmp_path):
    """Test project list-designs with --json."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    mock_proj = Mock()
    mock_proj.GetName.return_value = "TestProject"
    mock_proj.GetTopDesignList.return_value = ["Design1"]
    mock_design = Mock()
    mock_design.GetDesignType.return_value = "HFSS"
    mock_proj.SetActiveDesign.return_value = mock_design
    mock_desktop.odesktop = Mock()
    mock_desktop.odesktop.GetActiveProject.return_value = mock_proj
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["--json", "project", "list-designs"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["data"]["count"] == 1
        assert data["data"]["designs"][0]["name"] == "Design1"
    common_mod._json_mode = False


def test_upload_json(cli_runner, tmp_path):
    """Test file upload with --json."""
    src = tmp_path / "test.txt"
    src.write_text("content")
    dest = tmp_path / "dest"
    result = cli_runner.invoke(app, ["--json", "file", "upload", str(src), "--to", str(dest)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["uploaded"] is True
    common_mod._json_mode = False


def test_download_json(cli_runner, tmp_path):
    """Test file download with --json."""
    src = tmp_path / "remote.txt"
    src.write_text("data")
    dest = tmp_path / "local"
    result = cli_runner.invoke(app, ["--json", "file", "download", str(src), "--to", str(dest)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["downloaded"] is True
    common_mod._json_mode = False


def test_list_files_json_nonexistent_dir(cli_runner, tmp_path):
    """Test file list with --json on missing dir returns error."""
    result = cli_runner.invoke(app, ["--json", "file", "list", "--dir", str(tmp_path / "nope")])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["status"] == "error"
    common_mod._json_mode = False


def test_clear_json(cli_runner, tmp_path):
    """Test utility clear with --json."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    mock_odesktop = Mock()
    mock_odesktop.GetProjectList.return_value = []
    mock_desktop.odesktop = mock_odesktop
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["--json", "utility", "clear"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["data"]["cleared"] is True
    common_mod._json_mode = False


def test_clear_json_no_session(cli_runner, tmp_path):
    """Test utility clear with --json when no session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "utility", "clear"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False


def test_screenshot_json_no_session(cli_runner, tmp_path):
    """Test export screenshot with --json when no session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "export", "screenshot"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False


def test_touchstone_json_no_session(cli_runner, tmp_path):
    """Test export touchstone with --json when no session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "export", "touchstone", "out.s2p"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False


def test_3d_json_no_session(cli_runner, tmp_path):
    """Test export 3d with --json when no session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "export", "3d", "model.step"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False


def test_run_script_json_not_found(cli_runner, tmp_path):
    """Test script run with --json when file not found."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    mock_desktop = Mock()
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["--json", "script", "run", "nonexistent.py"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
        assert "not found" in data["error"]
    common_mod._json_mode = False


def test_run_script_json_success(cli_runner, tmp_path):
    """Test script run with --json on success."""
    session_file = tmp_path / "session.json"
    session_file.write_text('{"port":50051,"machine":"localhost","version":"2026.1"}')
    script_file = tmp_path / "test.py"
    script_file.write_text("print('hello')")
    mock_desktop = Mock()
    with (
        patch("ansys.aedt.core.cli.common.SESSION_FILE", session_file),
        patch("ansys.aedt.core.cli.common._get_desktop", return_value=mock_desktop),
    ):
        result = cli_runner.invoke(app, ["--json", "script", "run", str(script_file)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["data"]["executed"] is True
    common_mod._json_mode = False


def test_run_code_json_no_session(cli_runner, tmp_path):
    """Test script code with --json when no session."""
    with patch("ansys.aedt.core.cli.common.SESSION_FILE", tmp_path / "nope.json"):
        result = cli_runner.invoke(app, ["--json", "script", "code", "result = 42"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "error"
    common_mod._json_mode = False
