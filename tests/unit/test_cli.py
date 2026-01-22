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
from unittest.mock import patch

import psutil
import pytest
import typer
from typer.testing import CliRunner

from ansys.aedt.core.cli import app
from ansys.aedt.core.cli.common import DEFAULT_TEST_CONFIG
from ansys.aedt.core.cli.common import _display_config
from ansys.aedt.core.cli.common import _get_config_path
from ansys.aedt.core.cli.common import _get_tests_folder
from ansys.aedt.core.cli.common import _load_config
from ansys.aedt.core.cli.common import _prompt_config_value
from ansys.aedt.core.cli.common import _save_config
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
    from unittest.mock import PropertyMock

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


def test_cli_help_command(cli_runner):
    """Verify that help command executes without errors."""
    result = cli_runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "CLI for PyAEDT" in result.stdout


# VERSION COMMAND TESTS


@patch("ansys.aedt.core.__version__", "0.22.0")
def test_version_command(cli_runner):
    """Test version command output."""
    result = cli_runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "PyAEDT version: 0.22.0" in result.stdout


# PROCESSES COMMAND TESTS


@patch("psutil.process_iter")
def test_processes_command_no_aedt(mock_process_iter, cli_runner):
    """Test processes command when no AEDT is running."""
    result = cli_runner.invoke(app, ["processes"])

    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout


@patch("psutil.process_iter")
def test_processes_command_with_aedt(mock_process_iter, cli_runner, mock_aedt_process):
    """Test processes command when AEDT processes exist."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["processes"])

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "PID: 12345" in result.stdout
    assert "Port: 50051" in result.stdout


# STOP COMMAND TESTS


def test_stop_command_no_args(cli_runner):
    """Test stop command without arguments raises BadParameter."""
    result = cli_runner.invoke(app, ["stop"])

    assert result.exit_code != 0
    assert isinstance(result.exception, (SystemExit, typer.BadParameter)) or result.exception is None


@patch("psutil.process_iter")
def test_stop_all_command_no_processes(mock_process_iter, cli_runner):
    """Test stop all when no AEDT processes exist."""
    mock_process_iter.return_value = []

    result = cli_runner.invoke(app, ["stop", "--all"])

    assert result.exit_code == 0
    assert "All AEDT processes have been stopped" in result.stdout


@patch("psutil.process_iter")
def test_stop_all_command_with_access_denied(mock_process_iter, cli_runner, mock_aedt_process):
    """Test stop all when access is denied to some processes."""
    mock_aedt_process.kill.side_effect = psutil.AccessDenied()
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--all"])

    assert result.exit_code == 0
    assert f"✗ Access denied for process with PID {mock_aedt_process.pid}" in result.stdout
    assert "Some AEDT processes could not be stopped" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_all_command_with_process_no_longer_exists(
    mock_process_access, mock_process_iter, cli_runner, mock_aedt_process
):
    """Test stop all when process no longer exists during operation."""
    mock_aedt_process.kill.side_effect = psutil.NoSuchProcess(mock_aedt_process.pid)
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--all"])

    assert result.exit_code == 0
    assert f"! Process {mock_aedt_process.pid} no longer exists" in result.stdout
    assert "All AEDT processes have been stopped" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_all_command_with_generic_exception(mock_process_access, mock_process_iter, cli_runner, mock_aedt_process):
    """Test stop all when generic exception occurs during kill."""
    mock_aedt_process.kill.side_effect = Exception("Dummy exception")
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--all"])

    assert result.exit_code == 0
    assert f"✗ Error stopping process {mock_aedt_process.pid}" in result.stdout
    assert "Some AEDT processes could not be stopped" in result.stdout


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_pid_success(mock_process_access, mock_process_class, cli_runner, mock_aedt_process):
    """Test successfully stopping process by PID."""
    mock_process_class.return_value = mock_aedt_process

    result = cli_runner.invoke(app, ["stop", "--pid", "12345"])

    assert result.exit_code == 0
    assert "Process with PID 12345 has been stopped" in result.stdout
    mock_aedt_process.kill.assert_called_once()


@patch("psutil.Process")
def test_stop_command_by_pid_access_denied(mock_process_class, cli_runner, mock_aedt_process):
    """Test stopping process by PID when access is denied."""
    mock_process_class.return_value = mock_aedt_process

    result = cli_runner.invoke(app, ["stop", "--pid", "12345"])

    assert result.exit_code == 0
    assert "✗ Access denied for process with PID 12345" in result.stdout


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_pid_not_stoppable_state(mock_access_process, mock_process_class, cli_runner):
    """Test stopping process by PID when not in stoppable state."""
    mock_proc = Mock()
    mock_proc.status.return_value = psutil.STATUS_ZOMBIE
    mock_process_class.return_value = mock_proc

    result = cli_runner.invoke(app, ["stop", "--pid", "12345"])
    assert result.exit_code == 0
    assert "✗ Process with PID 12345 is not in a stoppable state" in result.stdout


@patch("psutil.Process")
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_pid_generic_exception(mock_process_access, mock_process_class, cli_runner, mock_aedt_process):
    """Test stopping process by PID when generic exception occurs."""
    mock_aedt_process.kill.side_effect = Exception("Dummy exception")
    mock_process_class.return_value = mock_aedt_process

    result = cli_runner.invoke(app, ["stop", "--pid", "12345"])

    assert result.exit_code == 0
    assert "✗ Error stopping process 12345" in result.stdout


@patch("psutil.Process", side_effect=psutil.NoSuchProcess(999))
def test_stop_command_by_pid_invalid_pid(mock_process, cli_runner):
    """Test stop command with invalid PID."""
    result = cli_runner.invoke(app, ["stop", "--pid", "999"])

    assert result.exit_code == 0
    assert "! Process 999 no longer exists" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_port_success(mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process):
    """Test successfully stopping process by port."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "Process with PID 12345 listening on port 50051 has been stopped" in result.stdout
    mock_aedt_process.kill.assert_called_once()


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50052)
def test_stop_command_by_port_not_found(mock_get_port, mock_process_iter, cli_runner, mock_aedt_process):
    """Test stopping process by port when no process found on that port."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "No AEDT process found listening on port 50051" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=False)
def test_stop_command_by_port_access_denied(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
):
    """Test stopping process by port when access is denied."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "✗ Access denied for process with PID 12345" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_port_no_such_process(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
):
    """Test stopping process by port when process no longer exists during operation."""
    mock_aedt_process.kill.side_effect = psutil.NoSuchProcess(mock_aedt_process.pid)
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "! Process 12345 no longer exists" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._can_access_process", return_value=True)
def test_stop_command_by_port_generic_exception(
    mock_access, mock_get_port, mock_process_iter, cli_runner, mock_aedt_process
):
    """Test stopping process by port when generic exception occurs."""
    mock_aedt_process.kill.side_effect = Exception("Dummy exception")
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "✗ Error stopping process 12345" in result.stdout


@patch("psutil.process_iter")
@patch("ansys.aedt.core.cli.process._get_port", return_value=None)
def test_stop_command_by_port_no_port_info(mock_get_port, mock_process_iter, cli_runner, mock_aedt_process):
    """Test stopping process by port when process has no port information."""
    mock_process_iter.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["stop", "--port", "50051"])

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


def test_start_command_default_parameters(cli_runner, mock_start_command):
    """Test start command with default parameters."""
    result = cli_runner.invoke(app, ["start"])

    assert result.exit_code == 0
    assert "Starting AEDT 2025.2..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_with_version(cli_runner, mock_start_command):
    """Test start command with specific version."""
    result = cli_runner.invoke(app, ["start", "--version", "2024.2"])

    assert result.exit_code == 0
    assert "Starting AEDT 2024.2..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_non_graphical(cli_runner, mock_start_command):
    """Test start command in non-graphical mode."""
    result = cli_runner.invoke(app, ["start", "--non-graphical"])

    assert result.exit_code == 0
    assert "Starting in non-graphical mode..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_with_port(cli_runner, mock_start_command):
    """Test start command with specific port."""
    result = cli_runner.invoke(app, ["start", "--port", "50055"])

    assert result.exit_code == 0
    assert "Using port: 50055" in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


def test_start_command_student_version(cli_runner, mock_start_command):
    """Test start command for student version."""
    result = cli_runner.invoke(app, ["start", "--student"])

    assert result.exit_code == 0
    assert "Starting student version..." in result.stdout
    assert "✓ AEDT started successfully" in result.stdout


@patch("ansys.aedt.core.desktop.Desktop")
@patch("ansys.aedt.core.settings")
def test_start_command_desktop_exception(mock_settings, mock_desktop, cli_runner):
    """Test start command when Desktop initialization fails."""
    mock_desktop.side_effect = Exception("Dummy exception")

    result = cli_runner.invoke(app, ["start"])

    assert result.exit_code == 0
    assert "✗ Error starting AEDT: Dummy exception" in result.stdout
    assert "Common issues:" in result.stdout
    assert "- AEDT not installed or not in PATH" in result.stdout
    assert "- Invalid version specified" in result.stdout
    assert "- License server not available" in result.stdout
    assert "- Insufficient permissions" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_get_config_path(mock_get_tests_folder, tmp_path):
    """Test _get_config_path helper function."""
    mock_get_tests_folder.return_value = tmp_path
    config_path, config = _get_config_path()

    assert config_path == tmp_path / "local_config.json"
    assert isinstance(config, dict)


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_load_config_existing_file(mock_get_tests_folder, tmp_path):
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
def test_load_config_invalid_file(mock_get_tests_folder, tmp_path):
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


def test_panels_add_help(cli_runner):
    """Test panels add help command."""
    result = cli_runner.invoke(app, ["panels", "add", "--help"])

    assert result.exit_code == 0
    assert "Add PyAEDT panels to AEDT installation" in result.stdout


def test_panels_add_success(cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions):
    """Test successful panel installation."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Installing PyAEDT panels..." in result.stdout
    assert "✓ PyAEDT panels installed successfully." in result.stdout
    assert "• Console" in result.stdout
    assert "• Jupyter" in result.stdout
    assert "• Run Script" in result.stdout
    assert "• Extension Manager" in result.stdout
    assert "• Version Manager" in result.stdout
    assert "Restart AEDT to see the new panels" in result.stdout

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        aedt_version="2025.2",
        personal_lib=str(temp_personal_lib),
        skip_version_manager=False,
        odesktop=None,
    )


def test_panels_add_with_skip_version_manager(
    cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions
):
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
        aedt_version="2025.2",
        personal_lib=str(temp_personal_lib),
        skip_version_manager=True,
        odesktop=None,
    )


def test_panels_add_short_options(cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions):
    """Test panel installation with short option flags."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "-p", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Installing PyAEDT panels..." in result.stdout
    assert "✓ PyAEDT panels installed successfully." in result.stdout


def test_panels_add_invalid_personal_lib_none(cli_runner, mock_installed_versions):
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


def test_panels_add_nonexistent_personal_lib(cli_runner, mock_installed_versions):
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


def test_panels_add_personal_lib_not_directory(cli_runner, tmp_path, mock_installed_versions):
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
def test_panels_add_installer_returns_false(mock_func, cli_runner, temp_personal_lib, mock_installed_versions):
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
def test_panels_add_import_error(mock_func, cli_runner, temp_personal_lib, mock_installed_versions):
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
def test_panels_add_generic_exception(mock_func, cli_runner, temp_personal_lib, mock_installed_versions):
    """Test panel installation when generic exception occurs."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", str(temp_personal_lib)],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "✗ Error installing panels: Unexpected error" in result.stdout


@patch("platform.system", return_value="Windows")
def test_panels_add_nonexistent_path_windows_hint(mock_platform, cli_runner, mock_installed_versions):
    """Test that Windows-specific path hint is shown on Windows."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", "C:\\nonexistent\\path"],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "Windows: C:\\Users\\<username>\\AppData\\Roaming\\Ansoft\\PersonalLib" in result.stdout


@patch("platform.system", return_value="Linux")
def test_panels_add_nonexistent_path_linux_hint(mock_platform, cli_runner, mock_installed_versions):
    """Test that Linux-specific path hint is shown on Linux."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", "/nonexistent/path"],
        input="1\n",
    )

    assert result.exit_code == 1
    assert "Linux: /home/<username>/Ansoft/PersonalLib" in result.stdout


def test_panels_add_strips_whitespace(cli_runner, mock_add_pyaedt_to_aedt, temp_personal_lib, mock_installed_versions):
    """Test that path whitespace is stripped."""
    result = cli_runner.invoke(
        app,
        ["panels", "add", "--personal-lib", f"  {temp_personal_lib}  "],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Installing PyAEDT panels..." in result.stdout

    mock_add_pyaedt_to_aedt.assert_called_once_with(
        aedt_version="2025.2",
        personal_lib=str(temp_personal_lib),
        skip_version_manager=False,
        odesktop=None,
    )


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_save_config(mock_get_tests_folder, tmp_path):
    """Test saving config file."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "subdir" / "local_config.json"
    test_config = {"desktopVersion": "2025.2", "NonGraphical": True}

    _save_config(config_file, test_config)

    assert config_file.exists()
    with open(config_file, "r") as f:
        saved_config = json.load(f)
    assert saved_config == test_config


def test_display_config(cli_runner):
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
def test_desktop_version_command(mock_get_tests_folder, tmp_path, cli_runner):
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
def test_desktop_version_invalid_format(mock_get_tests_folder, tmp_path, cli_runner):
    """Test desktop_version command with invalid format."""
    mock_get_tests_folder.return_value = tmp_path
    result = cli_runner.invoke(app, ["config", "test", "desktop-version", "invalid"])
    assert result.exit_code == 0
    assert "Invalid format" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_all_boolean_commands(mock_get_tests_folder, tmp_path, cli_runner):
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
    ]

    for cmd_parts, expected_output in bool_tests:
        result = cli_runner.invoke(app, ["config", "test"] + cmd_parts)
        assert result.exit_code == 0
        assert expected_output in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_local_example_folder_command(mock_get_tests_folder, tmp_path, cli_runner):
    """Test local_example_folder command."""
    mock_get_tests_folder.return_value = tmp_path
    result = cli_runner.invoke(
        app,
        ["config", "test", "local-example-folder", "/path/to/examples"],
    )
    assert result.exit_code == 0
    assert "local_example_folder set to '/path/to/examples'" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_persists_across_commands(mock_get_tests_folder, tmp_path, cli_runner):
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


def test_get_tests_folder_from_package(tmp_path):
    """Test _get_tests_folder when package structure exists."""
    # The function should find the tests folder from the package
    tests_folder = _get_tests_folder()
    assert isinstance(tests_folder, Path)


@patch("typer.confirm")
def test_prompt_config_value_bool_change(mock_confirm):
    """Test _prompt_config_value with boolean value change."""
    mock_confirm.return_value = True
    result = _prompt_config_value("test_key", True)
    assert result is False

    mock_confirm.return_value = False
    result = _prompt_config_value("test_key", True)
    assert result is True


@patch("typer.prompt")
def test_prompt_config_value_string(mock_prompt):
    """Test _prompt_config_value with string value."""
    mock_prompt.return_value = "new_value"
    result = _prompt_config_value("test_key", "old_value")
    assert result == "new_value"


@patch("typer.prompt")
def test_prompt_config_value_desktop_version_valid(mock_prompt):
    """Test _prompt_config_value with valid desktop version."""
    mock_prompt.return_value = "2024.2"
    result = _prompt_config_value("desktopVersion", "2025.2")
    assert result == "2024.2"


@patch("typer.prompt")
@patch("typer.secho")
def test_prompt_config_value_desktop_version_invalid_then_valid(mock_secho, mock_prompt):
    """Test _prompt_config_value with invalid then valid version."""
    mock_prompt.side_effect = ["invalid", "2024.2"]
    result = _prompt_config_value("desktopVersion", "2025.2")
    assert result == "2024.2"
    # Check that error was displayed
    assert mock_secho.call_count >= 1


@patch("typer.prompt")
def test_prompt_config_value_desktop_version_with_quotes(mock_prompt):
    """Test _prompt_config_value desktop version strips quotes."""
    mock_prompt.return_value = '"2024.2"'
    result = _prompt_config_value("desktopVersion", "2025.2")
    assert result == "2024.2"


@patch("typer.prompt")
def test_prompt_config_value_int(mock_prompt):
    """Test _prompt_config_value with integer value."""
    mock_prompt.return_value = 42
    result = _prompt_config_value("test_key", 10)
    assert result == 42


def test_prompt_config_value_unknown_type():
    """Test _prompt_config_value with unknown type."""
    result = _prompt_config_value("test_key", [1, 2, 3])
    assert result == [1, 2, 3]


# _update_bool_config TESTS (Interactive Mode)


@patch("ansys.aedt.core.cli.common._get_tests_folder")
@patch("typer.confirm")
def test_update_bool_config_interactive_change(mock_confirm, mock_get_tests_folder, tmp_path):
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
def test_update_bool_config_interactive_no_change(mock_confirm, mock_get_tests_folder, tmp_path):
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
def test_update_bool_config_with_value(mock_get_tests_folder, tmp_path):
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
def test_update_string_config_interactive_no_validator(mock_prompt, mock_get_tests_folder, tmp_path):
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
def test_update_string_config_interactive_with_validator_valid(mock_prompt, mock_get_tests_folder, tmp_path):
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
def test_update_string_config_interactive_validator_invalid_valid(mock_prompt, mock_get_tests_folder, tmp_path):
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
def test_update_string_config_with_value_valid(mock_get_tests_folder, tmp_path):
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
def test_update_string_config_with_value_invalid(mock_get_tests_folder, tmp_path):
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
def test_config_test_show_flag(mock_get_tests_folder, tmp_path, cli_runner):
    """Test config test command with --show flag."""
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_app, ["--show"])

    assert result.exit_code == 0
    assert "Current Test Configuration" in result.stdout
    assert "2025.2" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_show_flag_short(mock_get_tests_folder, tmp_path, cli_runner):
    """Test config test command with -s flag."""
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_app, ["-s"])

    assert result.exit_code == 0
    assert "Current Test Configuration" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_interactive_no_modify(mock_get_tests_folder, tmp_path, cli_runner):
    """Test config test command declining to modify."""
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_app, input="n\n")

    assert result.exit_code == 0
    assert "No changes made" in result.stdout


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_interactive_with_modifications(mock_get_tests_folder, tmp_path, cli_runner):
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
def test_config_test_creates_config_file(mock_get_tests_folder, tmp_path, cli_runner):
    """Test config test command creates config file if not exists."""
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"

    assert not config_file.exists()

    result = cli_runner.invoke(test_app, ["--show"])

    assert result.exit_code == 0
    assert config_file.exists()


@patch("ansys.aedt.core.cli.common._get_tests_folder")
def test_config_test_loads_existing_config(mock_get_tests_folder, tmp_path, cli_runner):
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
def test_panels_add_no_versions_installed(mock_installed_versions, cli_runner):
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


def test_doc_group_help(cli_runner):
    """Ensure doc command group help works."""
    result = cli_runner.invoke(app, ["doc", "--help"])

    assert result.exit_code == 0
    assert "Documentation commands" in result.stdout


def test_doc_examples_command(cli_runner, mock_online_help):
    """Test doc examples command."""
    result = cli_runner.invoke(app, ["doc", "examples"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.examples.assert_called_once_with()


def test_doc_github_command(cli_runner, mock_online_help):
    """Test doc github command."""
    result = cli_runner.invoke(app, ["doc", "github"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.github.assert_called_once_with()


def test_doc_user_guide_command(cli_runner, mock_online_help):
    """Test doc user_guide command."""
    result = cli_runner.invoke(app, ["doc", "user-guide"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.user_guide.assert_called_once_with()


def test_doc_getting_started_command(cli_runner, mock_online_help):
    """Test doc getting_started command."""
    result = cli_runner.invoke(app, ["doc", "getting-started"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.getting_started.assert_called_once_with()


def test_doc_installation_command(cli_runner, mock_online_help):
    """Test doc installation command."""
    result = cli_runner.invoke(app, ["doc", "installation"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.installation_guide.assert_called_once_with()


def test_doc_api_reference_command(cli_runner, mock_online_help):
    """Test doc api_reference command."""
    result = cli_runner.invoke(app, ["doc", "api"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.api_reference.assert_called_once_with()


def test_doc_changelog_command_no_arg(cli_runner, mock_online_help):
    """Test doc changelog command without version argument."""
    result = cli_runner.invoke(app, ["doc", "changelog"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.changelog.assert_called_once_with(None)


def test_doc_changelog_command_with_version(cli_runner, mock_online_help):
    """Test doc changelog command with explicit version."""
    result = cli_runner.invoke(app, ["doc", "changelog", "0.22.0"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.changelog.assert_called_once_with("0.22.0")


def test_doc_issues_command(cli_runner, mock_online_help):
    """Test doc issues command."""
    result = cli_runner.invoke(app, ["doc", "issues"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.issues.assert_called_once_with()


def test_doc_search_command_single_keyword(cli_runner, mock_online_help):
    """Test doc search command with single keyword."""
    result = cli_runner.invoke(app, ["doc", "search", "Maxwell"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.search.assert_called_once_with("Maxwell")


def test_doc_search_command_multiple_keywords(cli_runner, mock_online_help):
    """Test doc search command with multiple keywords."""
    result = cli_runner.invoke(app, ["doc", "search", "Maxwell", "3D", "simulation"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.search.assert_called_once_with("Maxwell 3D simulation")


def test_doc_search_command_no_keywords(cli_runner, mock_online_help):
    """Test doc search command without keywords."""
    result = cli_runner.invoke(app, ["doc", "search"])

    assert result.exit_code == 1
    assert "✗ Error: Please provide at least one search keyword" in result.stdout
    assert "Usage: pyaedt doc search" in result.stdout
    # Should not call online_help.search when no keywords provided
    mock_online_help.search.assert_not_called()


def test_doc_callback_opens_home_and_shows_help(cli_runner, mock_online_help):
    """Test doc command without subcommand opens home and displays help."""
    result = cli_runner.invoke(app, ["doc"])

    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.home.assert_called_once_with()
    # Verify help text is displayed
    assert "Documentation commands" in result.stdout
    assert "examples" in result.stdout
    assert "github" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
def test_attach_command_no_aedt_processes(mock_find_procs, cli_runner):
    """Test attach command when no AEDT processes are running."""
    mock_find_procs.return_value = []

    result = cli_runner.invoke(app, ["attach"])

    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout
    assert "Start AEDT first using:" in result.stdout
    assert "pyaedt start" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_single_process_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with single process and user quits."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="q\n")

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "1. PID: 12345" in result.stdout
    assert "Port: 50051" in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=None)
def test_attach_command_process_com_mode(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command displays COM mode for processes without gRPC port."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="q\n")

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "COM mode" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_invalid_input_then_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with invalid input followed by quit."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="abc\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid input. Please enter a number." in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_out_of_range_then_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with out of range selection then quit."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="5\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid selection. Please enter a number between 1 and 1." in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_valid_selection(
    mock_launch_console, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
):
    """Test attach command with valid process selection."""
    # Mock process with version info in cmdline
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="1\n")

    assert result.exit_code == 0
    assert "Found 1 AEDT process(es)" in result.stdout
    assert "1. PID: 12345" in result.stdout
    assert "Version: 2025.2" in result.stdout
    assert "Attaching to process 12345..." in result.stdout
    mock_launch_console.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", side_effect=[50051, 50052])
def test_attach_command_multiple_processes(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
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

    result = cli_runner.invoke(app, ["attach"], input="q\n")

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
):
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

    result = cli_runner.invoke(app, ["attach"], input="2\n")

    assert result.exit_code == 0
    assert "Attaching to process 67890..." in result.stdout
    mock_launch_console.assert_called_once_with(67890, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_version_extraction_unknown(mock_get_port, mock_find_procs, cli_runner):
    """Test attach command when version cannot be extracted from cmdline."""
    mock_proc = Mock(spec=psutil.Process)
    mock_proc.pid = 12345
    mock_proc.name.return_value = "ansysedt.exe"
    mock_proc.cmdline.return_value = ["ansysedt.exe"]  # No version info

    mock_find_procs.return_value = [mock_proc]

    result = cli_runner.invoke(app, ["attach"], input="q\n")

    assert result.exit_code == 0
    assert "Version: unknown" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_with_student_version(mock_launch_console, mock_get_port, mock_find_procs, cli_runner):
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

    result = cli_runner.invoke(app, ["attach"], input="1\n")

    assert result.exit_code == 0
    assert "Attaching to process 99999..." in result.stdout
    mock_launch_console.assert_called_once_with(99999, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_case_insensitive_quit(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command accepts 'Q' (uppercase) to quit."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="Q\n")

    assert result.exit_code == 0
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_zero_selection(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with zero as selection."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="0\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid selection. Please enter a number between 1 and 1." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
def test_attach_command_negative_selection(mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with negative number as selection."""
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="-1\nq\n")

    assert result.exit_code == 0
    assert "✗ Invalid selection. Please enter a number between 1 and 1." in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_command_retries_on_invalid_then_succeeds(
    mock_launch_console, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
):
    """Test attach command retries after multiple invalid inputs."""
    mock_aedt_process.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="abc\n99\n-5\n1\n")

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
):
    """Test that _launch_console_setup is called with correct arguments."""
    mock_aedt_process.cmdline.return_value = ["C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach"], input="1\n")

    assert result.exit_code == 0
    mock_launch.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("pathlib.Path")
@patch("subprocess.run", side_effect=KeyboardInterrupt())
def test_launch_console_setup_keyboard_interrupt(
    mock_subprocess, mock_path_class, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
):
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

    result = cli_runner.invoke(app, ["attach"], input="1\n")

    # Should handle KeyboardInterrupt gracefully
    assert "Interrupted" in result.stdout or result.exit_code == 0


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("pathlib.Path")
@patch("subprocess.run", side_effect=Exception("Subprocess error"))
def test_launch_console_setup_generic_exception(
    mock_subprocess, mock_path_class, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process
):
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

    result = cli_runner.invoke(app, ["attach"], input="1\n")

    # Should display error message
    assert "✗ Error launching console" in result.stdout or result.exit_code == 0


# ATTACH WITH PID OPTION TESTS


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_success(mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with --pid option for successful attachment."""
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-ng",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach", "--pid", "12345"])

    assert result.exit_code == 0
    assert "Attaching to process 12345" in result.stdout
    mock_launch.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_short_option(mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with -p short option."""
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM\\ansysedt.exe",
        "-ng",
        "-grpcsrv",
        "50051",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach", "-p", "12345"])

    assert result.exit_code == 0
    assert "Attaching to process 12345" in result.stdout
    mock_launch.assert_called_once_with(12345, "2025.2")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
def test_attach_with_pid_not_found(mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command with --pid when process not found."""
    mock_aedt_process.pid = 99999
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach", "--pid", "12345"])

    assert result.exit_code == 0
    assert "✗ No AEDT process found with PID 12345" in result.stdout
    assert "Available AEDT processes:" in result.stdout
    assert "PID: 99999" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
def test_attach_with_pid_no_processes_running(mock_find_procs, cli_runner):
    """Test attach command with --pid when no AEDT processes are running."""
    mock_find_procs.return_value = []

    result = cli_runner.invoke(app, ["attach", "--pid", "12345"])

    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout
    assert "pyaedt start" in result.stdout


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_version_extraction(mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command extracts version correctly from command line."""
    mock_aedt_process.cmdline.return_value = [
        "C:\\Program Files\\ANSYS Inc\\v241\\AnsysEM\\ansysedt.exe",
        "-ng",
    ]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach", "--pid", "12345"])

    assert result.exit_code == 0
    mock_launch.assert_called_once_with(12345, "2024.1")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_unknown_version(mock_launch, mock_get_port, mock_find_procs, cli_runner, mock_aedt_process):
    """Test attach command handles unknown version."""
    mock_aedt_process.cmdline.return_value = ["ansysedt.exe"]
    mock_find_procs.return_value = [mock_aedt_process]

    result = cli_runner.invoke(app, ["attach", "--pid", "12345"])

    assert result.exit_code == 0
    mock_launch.assert_called_once_with(12345, "unknown")


@patch("ansys.aedt.core.cli.process._find_aedt_processes")
@patch("ansys.aedt.core.cli.process._get_port", return_value=50051)
@patch("ansys.aedt.core.cli.process._launch_console_setup")
def test_attach_with_pid_multiple_processes(mock_launch, mock_get_port, mock_find_procs, cli_runner):
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

    result = cli_runner.invoke(app, ["attach", "--pid", "67890"])

    assert result.exit_code == 0
    assert "Attaching to process 67890" in result.stdout
    mock_launch.assert_called_once_with(67890, "2024.1")
