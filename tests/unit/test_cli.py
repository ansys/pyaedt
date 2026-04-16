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

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import PropertyMock
from unittest.mock import patch

import psutil
import pytest
from typer.testing import CliRunner

from ansys.aedt.core.cli import app
import ansys.aedt.core.cli.aedt as aedt_mod
import ansys.aedt.core.cli.common as common_mod
from ansys.aedt.core.cli.common import DEFAULT_TEST_CONFIG
from ansys.aedt.core.cli.common import display_config
from ansys.aedt.core.cli.common import get_tests_folder
from ansys.aedt.core.cli.common import load_config
from ansys.aedt.core.cli.common import print_output
from ansys.aedt.core.cli.common import prompt_config_value
from ansys.aedt.core.cli.common import save_config
from ansys.aedt.core.cli.config import test_config_app
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.internal.aedt_versions import aedt_versions


@pytest.fixture(autouse=True)
def reset_json_mode():
    common_mod.json_mode = False
    yield
    common_mod.json_mode = False


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_online_help():
    with patch("ansys.aedt.core.help.online_help") as mock_help:
        mock_help.silent = True
        yield mock_help


@pytest.fixture
def mock_installed_versions():
    if is_windows:
        mock_versions = {
            "2026.1": r"C:\\Program Files\\ANSYS Inc\\v261\\AnsysEM",
            "2025.2": r"C:\\Program Files\\ANSYS Inc\\v252\\AnsysEM",
        }
    else:
        mock_versions = {
            "2026.1": "/opt/ansys_inc/v261/AnsysEM",
            "2025.2": "/opt/ansys_inc/v252/AnsysEM",
        }
    with patch(
        "ansys.aedt.core.internal.aedt_versions.AedtVersions.installed_versions",
        new_callable=PropertyMock,
        return_value=mock_versions,
    ):
        yield mock_versions


@pytest.fixture
def temp_personal_lib(tmp_path):
    personal_lib = tmp_path / "PersonalLib"
    personal_lib.mkdir()
    return personal_lib


def test_cli_help_command(cli_runner):
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI for PyAEDT" in result.stdout


@patch("ansys.aedt.core.__version__", "0.22.0")
def test_version_command(cli_runner):
    result = cli_runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "PyAEDT version: 0.22.0" in result.stdout


@patch("ansys.aedt.core.__version__", "0.22.0")
def test_version_json(cli_runner):
    result = cli_runner.invoke(app, ["--json", "version"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["version"] == "0.22.0"


def test_aedt_versions(cli_runner, mock_installed_versions):
    result = cli_runner.invoke(app, ["aedt-versions"])
    assert result.exit_code == 0
    assert "2025.2" in result.output


def test_aedt_versions_json(cli_runner, mock_installed_versions):
    result = cli_runner.invoke(app, ["--json", "aedt-versions"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert "2025.2" in data["data"]["versions"]


@patch(
    "ansys.aedt.core.internal.aedt_versions.AedtVersions.installed_versions",
    new_callable=PropertyMock,
    return_value={},
)
def test_aedt_versions_no_versions(_mock_versions, cli_runner):
    result = cli_runner.invoke(app, ["aedt-versions"])
    assert result.exit_code == 0
    assert "No AEDT versions found" in result.stdout


@patch("ansys.aedt.core.cli.aedt._discover_aedt_sessions", return_value=[])
def test_session_list_no_aedt(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "list"])
    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout


@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_session_list_with_aedt(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "list"])
    assert result.exit_code == 0
    assert "Found 1 AEDT instance" in result.stdout
    assert "PID: 12345" in result.stdout
    assert "Port: 50051" in result.stdout


@patch("ansys.aedt.core.cli.aedt._discover_aedt_sessions", return_value=[])
def test_session_stop_no_args(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "stop"])
    assert result.exit_code == 1
    assert "Either --port or --all must be provided" in result.stdout


@patch("psutil.Process")
@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_session_stop_all_success(mock_discover, mock_process_cls, cli_runner):
    mock_process = Mock()
    mock_process_cls.return_value = mock_process

    result = cli_runner.invoke(app, ["session", "stop", "--all"])

    assert result.exit_code == 0
    assert "All AEDT processes stopped" in result.stdout
    mock_process.kill.assert_called_once()


@patch("psutil.Process")
@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_session_stop_by_port_success(mock_discover, mock_process_cls, cli_runner):
    mock_process = Mock()
    mock_process_cls.return_value = mock_process

    result = cli_runner.invoke(app, ["session", "stop", "--port", "50051"])

    assert result.exit_code == 0
    assert "AEDT process (PID 12345, port 50051) stopped" in result.stdout


@patch("ansys.aedt.core.cli.aedt._discover_aedt_sessions", return_value=[])
def test_session_stop_by_port_not_found(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "stop", "--port", "50051"])
    assert result.exit_code == 1
    assert "No AEDT process found on port 50051" in result.stdout


@pytest.fixture
def mock_start_command():
    with (
        patch("ansys.aedt.core.desktop.Desktop") as mock_desktop_class,
        patch("ansys.aedt.core.settings") as mock_settings,
        patch("threading.Thread") as mock_thread,
        patch("time.sleep") as mock_sleep,
    ):
        mock_desktop_instance = Mock()
        mock_desktop_instance.port = 50051
        mock_desktop_class.return_value = mock_desktop_instance
        yield {
            "desktop_class": mock_desktop_class,
            "desktop_instance": mock_desktop_instance,
            "settings": mock_settings,
            "thread": mock_thread,
            "sleep": mock_sleep,
        }


def test_session_start_default_parameters(cli_runner, mock_start_command):
    result = cli_runner.invoke(app, ["--json", "session", "start"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["version"] == aedt_versions.current_version
    assert data["data"]["port"] == 50051


@patch("ansys.aedt.core.desktop.Desktop")
@patch("ansys.aedt.core.settings")
def test_session_start_exception(_mock_settings, mock_desktop, cli_runner):
    mock_desktop.side_effect = Exception("Dummy exception")
    result = cli_runner.invoke(app, ["--json", "session", "start"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"] == "Dummy exception"


@patch("ansys.aedt.core.cli.aedt._discover_aedt_sessions", return_value=[])
def test_attach_no_aedt_sessions(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "attach"])
    assert result.exit_code == 0
    assert "No AEDT processes currently running" in result.stdout
    assert "pyaedt session start" in result.stdout


@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_attach_invalid_input_then_quit(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "attach"], input="abc\nq\n")
    assert result.exit_code == 0
    assert "Invalid input. Please enter a number" in result.stdout
    assert "Cancelled." in result.stdout


@patch("ansys.aedt.core.cli.aedt._launch_console")
@patch("ansys.aedt.core.cli.aedt._activate_console_context")
@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_attach_valid_interactive_selection(mock_discover, mock_activate, mock_launch, cli_runner):
    result = cli_runner.invoke(app, ["session", "attach"], input="1\n")
    assert result.exit_code == 0
    assert "Attaching to process 12345" in result.stdout
    mock_activate.assert_called_once_with(port=50051, project=None, design=None)
    mock_launch.assert_called_once_with(12345, "2026.1", None)


@patch("ansys.aedt.core.cli.aedt._launch_console")
@patch("ansys.aedt.core.cli.aedt._activate_console_context")
@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_attach_by_port(mock_discover, mock_activate, mock_launch, cli_runner):
    result = cli_runner.invoke(app, ["session", "attach", "--port", "50051"])
    assert result.exit_code == 0
    mock_activate.assert_called_once_with(port=50051, project=None, design=None)
    mock_launch.assert_called_once_with(12345, "2026.1", None)


@patch("ansys.aedt.core.cli.aedt._discover_aedt_sessions", return_value=[])
def test_attach_json_empty_sessions(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["--json", "session", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["processes"] == []


@patch("psutil.Process")
@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50051, "version": "2026.1", "student_version": False}],
)
def test_session_stop_by_port_access_denied_json(mock_discover, mock_process_cls, cli_runner):
    mock_process = Mock()
    mock_process.kill.side_effect = psutil.AccessDenied(pid=12345)
    mock_process_cls.return_value = mock_process

    result = cli_runner.invoke(app, ["--json", "session", "stop", "--port", "50051"])

    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert "Access denied" in data["error"]


@patch(
    "ansys.aedt.core.cli.aedt._discover_aedt_sessions",
    return_value=[{"pid": 12345, "name": "ansysedt.exe", "port": 50052, "version": "2026.1", "student_version": False}],
)
def test_attach_by_port_not_found_lists_available(_mock_discover, cli_runner):
    result = cli_runner.invoke(app, ["session", "attach", "--port", "50051"])
    assert result.exit_code == 0
    assert "No AEDT process found on port 50051" in result.stdout
    assert "PID: 12345, Port: 50052" in result.stdout


def test_load_config_existing_file(tmp_path):
    config_file = tmp_path / "local_config.json"
    test_config = {"desktopVersion": "2026.1", "NonGraphical": False}

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(test_config, f)

    loaded_config = load_config(config_file)
    assert loaded_config["desktopVersion"] == "2026.1"
    assert loaded_config["NonGraphical"] is False


def test_load_config_invalid_file(tmp_path):
    config_file = tmp_path / "local_config.json"
    config_file.write_text("invalid json", encoding="utf-8")
    loaded_config = load_config(config_file)
    assert loaded_config == DEFAULT_TEST_CONFIG


def test_load_config_filters_unknown_keys(tmp_path):
    config_file = tmp_path / "local_config.json"
    config_file.write_text(json.dumps({"desktopVersion": "2025.2", "unexpected": True}), encoding="utf-8")

    loaded_config = load_config(config_file)

    assert loaded_config["desktopVersion"] == "2025.2"
    assert "unexpected" not in loaded_config


def test_save_config(tmp_path):
    config_file = tmp_path / "subdir" / "local_config.json"
    config = {"desktopVersion": "2026.1", "NonGraphical": True}

    save_config(config_file, config)

    with open(config_file, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved == config


def test_display_config_does_not_crash():
    display_config(
        {"desktopVersion": "2026.1", "NonGraphical": True},
        "Test Config",
        {"desktopVersion": "AEDT version", "NonGraphical": "Run without GUI"},
    )


@patch("typer.confirm")
def test_prompt_config_value_bool_change(mock_confirm):
    mock_confirm.return_value = True
    assert prompt_config_value("test_key", True) is False


@patch("typer.prompt")
def test_prompt_config_value_desktop_version_valid(mock_prompt):
    mock_prompt.return_value = "2024.2"
    assert prompt_config_value("desktopVersion", "2026.1") == "2024.2"


@patch("typer.prompt")
@patch("typer.secho")
def test_prompt_config_value_desktop_version_retries(mock_secho, mock_prompt):
    mock_prompt.side_effect = ["bad", "2025.2"]

    assert prompt_config_value("desktopVersion", "2026.1") == "2025.2"
    assert mock_secho.called


@patch("typer.prompt")
def test_prompt_config_value_string(mock_prompt):
    mock_prompt.return_value = "updated"
    assert prompt_config_value("local_example_folder", "") == "updated"


@patch("typer.prompt")
def test_prompt_config_value_int(mock_prompt):
    mock_prompt.return_value = 42
    assert prompt_config_value("retries", 10) == 42


def test_common_design_helpers():
    design = Mock()
    design.GetDesignType.return_value = "HFSS"
    project = Mock()
    project.GetTopDesignList.return_value = ["HFSS;D1"]
    project.SetActiveDesign.return_value = design
    project.GetActiveDesign.return_value = Mock(GetName=Mock(return_value="HFSS;D1"))

    designs = common_mod.get_project_designs(project)

    assert common_mod.normalize_design_name("HFSS;D1") == "D1"
    assert common_mod.get_active_design_name(project) == "D1"
    assert designs == [{"name": "D1", "type": "HFSS"}]


def test_list_projects_with_designs_restores_active_context():
    active_project = Mock()
    active_project.GetName.return_value = "Project2"
    active_project.GetActiveDesign.return_value = Mock(GetName=Mock(return_value="HFSS;Design2"))

    project1 = Mock()
    project1.GetTopDesignList.return_value = []

    design = Mock()
    design.GetDesignType.return_value = "HFSS"
    project2 = Mock()
    project2.GetTopDesignList.return_value = ["HFSS;Design2"]
    project2.SetActiveDesign.return_value = design

    project_map = {"Project1": project1, "Project2": project2}
    odesktop = Mock()
    odesktop.GetProjectList.return_value = ["Project1", "Project2"]
    odesktop.GetActiveProject.return_value = active_project
    odesktop.SetActiveProject.side_effect = lambda name: project_map[name]

    projects = common_mod.list_projects_with_designs(odesktop)

    assert projects == [
        {"name": "Project1", "designs": [], "count": 0},
        {"name": "Project2", "designs": [{"name": "Design2", "type": "HFSS"}], "count": 1},
    ]
    project2.SetActiveDesign.assert_called_with("Design2")


def test_resolve_project_requires_explicit_selection_when_multiple_open():
    odesktop = Mock()
    odesktop.GetProjectList.return_value = ["Project1", "Project2"]

    with pytest.raises(RuntimeError, match="Multiple projects are open"):
        common_mod.resolve_project(odesktop)


def test_resolve_project_and_design_resolves_single_design():
    design = Mock()
    design.GetDesignType.return_value = "HFSS"
    project = Mock()
    project.GetName.return_value = "Project1"
    project.GetTopDesignList.return_value = ["HFSS;Design1"]
    project.SetActiveDesign.return_value = design

    odesktop = Mock()
    odesktop.GetProjectList.return_value = ["Project1"]
    odesktop.SetActiveProject.return_value = project

    context = common_mod.resolve_project_and_design(odesktop)

    assert context == {"project": "Project1", "design": "Design1"}
    project.SetActiveDesign.assert_called_with("Design1")


@patch("ansys.aedt.core.cli.common.get_desktop")
@patch("ansys.aedt.core.get_pyaedt_app")
@patch(
    "ansys.aedt.core.cli.common.resolve_project_and_design", return_value={"project": "Project1", "design": "Design1"}
)
def test_get_design_app_uses_resolved_context(mock_resolve, mock_get_pyaedt_app, mock_get_desktop):
    desktop = Mock()
    app_instance = Mock()
    mock_get_desktop.return_value = desktop
    mock_get_pyaedt_app.return_value = app_instance

    resolved_desktop, resolved_app, context = common_mod.get_design_app(port=50051)

    assert resolved_desktop is desktop
    assert resolved_app is app_instance
    assert context == {"project": "Project1", "design": "Design1"}
    mock_resolve.assert_called_once_with(desktop.odesktop, project_name=None, design_name=None)
    mock_get_pyaedt_app.assert_called_once_with(project_name="Project1", design_name="Design1", desktop=desktop)


def test_extract_version_from_cmdline_parses_windows_paths():
    assert aedt_mod._extract_version_from_cmdline([r"C:\Program Files\ANSYS Inc\v261\AnsysEM\ansysedt.exe"]) == "2026.1"
    assert aedt_mod._extract_version_from_cmdline([]) == "unknown"


@pytest.mark.parametrize(
    ("on_linux", "expected_name", "expected_sv_name"),
    [
        (False, "ansysedt.exe", "ansysedtsv.exe"),
        (True, "ansysedt", "ansysedtsv"),
    ],
)
def test_discover_aedt_sessions_collects_versions(on_linux, expected_name, expected_sv_name):
    def active_sessions_side_effect(student_version=False):
        return {22: -1} if student_version else {11: 50051}

    with (
        patch("ansys.aedt.core.cli.aedt.is_linux", on_linux),
        patch("ansys.aedt.core.cli.aedt.active_sessions", side_effect=active_sessions_side_effect),
        patch(
            "ansys.aedt.core.cli.aedt._check_psutil_connections",
            return_value={11: [{"cmdline": r"C:\Program Files\ANSYS Inc\v261\AnsysEM\ansysedt.exe"}], 22: []},
        ),
    ):
        sessions = aedt_mod._discover_aedt_sessions()

    assert sessions == [
        {"pid": 11, "port": 50051, "student_version": False, "name": expected_name, "version": "2026.1"},
        {"pid": 22, "port": None, "student_version": True, "name": expected_sv_name, "version": "unknown"},
    ]


def test_activate_console_context_requires_grpc_port_for_design():
    with pytest.raises(RuntimeError, match="requires a gRPC-enabled AEDT instance"):
        aedt_mod._activate_console_context(port=None, design="Design1")


@patch("ansys.aedt.core.cli.common.resolve_project")
@patch("ansys.aedt.core.cli.common.get_desktop")
def test_activate_console_context_project_only(mock_get_desktop, mock_resolve_project):
    desktop = Mock()
    mock_get_desktop.return_value = desktop

    aedt_mod._activate_console_context(port=50051, project="Project1")

    mock_resolve_project.assert_called_once_with(desktop.odesktop, project_name="Project1")


def test_launch_console_reports_missing_setup_file(tmp_path, capsys):
    package_init = tmp_path / "__init__.py"
    package_init.write_text("", encoding="utf-8")

    with patch("ansys.aedt.core.__file__", str(package_init)):
        aedt_mod._launch_console(12345, "2026.1")

    assert "console_setup.py not found" in capsys.readouterr().out


@patch("ansys.aedt.core.cli.config.get_tests_folder")
def test_test_config_show_flag(mock_get_tests_folder, tmp_path, cli_runner):
    mock_get_tests_folder.return_value = tmp_path
    result = cli_runner.invoke(test_config_app, ["--show"])
    assert result.exit_code == 0
    assert "Current Test Configuration" in result.stdout


@patch("ansys.aedt.core.cli.config.get_tests_folder")
def test_test_config_creates_file(mock_get_tests_folder, tmp_path, cli_runner):
    mock_get_tests_folder.return_value = tmp_path
    config_file = tmp_path / "local_config.json"
    assert not config_file.exists()

    result = cli_runner.invoke(test_config_app, ["--show"])

    assert result.exit_code == 0
    assert config_file.exists()


@patch("ansys.aedt.core.cli.config.get_tests_folder")
def test_test_config_json_show(mock_get_tests_folder, tmp_path, cli_runner):
    mock_get_tests_folder.return_value = tmp_path

    with (
        patch("ansys.aedt.core.cli.config.json_mode", True),
        patch.object(common_mod, "json_mode", True),
    ):
        result = cli_runner.invoke(test_config_app, ["--show"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "ok"
    assert data["data"]["config"]["desktopVersion"] == DEFAULT_TEST_CONFIG["desktopVersion"]


@patch("ansys.aedt.core.cli.config.get_tests_folder")
def test_test_config_interactive_no_changes(mock_get_tests_folder, tmp_path, cli_runner):
    mock_get_tests_folder.return_value = tmp_path

    result = cli_runner.invoke(test_config_app, input="n\n")

    assert result.exit_code == 0
    assert "No changes made" in result.stdout


@patch("ansys.aedt.core.cli.config.prompt_config_value")
@patch("ansys.aedt.core.cli.config.get_tests_folder")
def test_test_config_interactive_updates_values(mock_get_tests_folder, mock_prompt_value, tmp_path, cli_runner):
    mock_get_tests_folder.return_value = tmp_path
    mock_prompt_value.side_effect = ["2025.2", False, False, True, False, False, True, "examples", False]

    result = cli_runner.invoke(test_config_app, input="y\n")

    assert result.exit_code == 0
    saved = json.loads((tmp_path / "local_config.json").read_text(encoding="utf-8"))
    assert saved["desktopVersion"] == "2025.2"
    assert saved["skip_circuits"] is True
    assert saved["local_example_folder"] == "examples"


def test_panels_add_help(cli_runner):
    result = cli_runner.invoke(app, ["panels", "add", "--help"])
    assert result.exit_code == 0
    assert "Add PyAEDT panels to AEDT installation" in result.stdout


def test_panels_add_success(cli_runner, temp_personal_lib, mock_installed_versions):
    with patch(
        "ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt", return_value=True
    ) as mock_add:
        result = cli_runner.invoke(app, ["panels", "add", "--personal-lib", str(temp_personal_lib)])

    assert result.exit_code == 0
    assert "PyAEDT panels installed successfully" in result.stdout
    mock_add.assert_called_once()


def test_panels_add_nonexistent_personal_lib(cli_runner, mock_installed_versions):
    result = cli_runner.invoke(app, ["panels", "add", "--personal-lib", "/nonexistent/path/PersonalLib"])
    assert result.exit_code == 1
    assert "does not exist" in result.stdout


@patch(
    "ansys.aedt.core.internal.aedt_versions.AedtVersions.installed_versions",
    new_callable=PropertyMock,
    return_value={},
)
def test_panels_add_without_installed_versions(_mock_versions, cli_runner):
    result = cli_runner.invoke(app, ["panels", "add", "--personal-lib", "C:/Temp/PersonalLib"])
    assert result.exit_code == 1
    assert "No AEDT versions found on this system" in result.stdout


def test_panels_add_reset_and_skip_version_manager(cli_runner, temp_personal_lib, mock_installed_versions):
    toolkits_path = temp_personal_lib / "Toolkits"
    toolkits_path.mkdir()
    (toolkits_path / "stale.txt").write_text("old", encoding="utf-8")

    with patch(
        "ansys.aedt.core.extensions.installer.pyaedt_installer.add_pyaedt_to_aedt", return_value=True
    ) as mock_add:
        result = cli_runner.invoke(
            app,
            ["panels", "add", "--personal-lib", str(temp_personal_lib), "--reset", "--skip-version-manager"],
        )

    assert result.exit_code == 0
    assert "Deleting existing Toolkits directory" in result.stdout
    assert "Skipping Version Manager tab" in result.stdout
    assert not toolkits_path.exists()
    mock_add.assert_called_once()
    assert mock_add.call_args.kwargs["personal_lib"] == str(temp_personal_lib)
    assert mock_add.call_args.kwargs["skip_version_manager"] is True
    assert mock_add.call_args.kwargs["skip_extension_manager"] is False
    assert mock_add.call_args.kwargs["light"] is False


def test_doc_group_help(cli_runner):
    result = cli_runner.invoke(app, ["doc", "--help"])
    assert result.exit_code == 0
    assert "Documentation commands" in result.stdout


def test_doc_examples_command(cli_runner, mock_online_help):
    result = cli_runner.invoke(app, ["doc", "examples"])
    assert result.exit_code == 0
    assert mock_online_help.silent is False
    mock_online_help.examples.assert_called_once_with()


def test_doc_callback_opens_home_and_shows_help(cli_runner, mock_online_help):
    result = cli_runner.invoke(app, ["doc"])
    assert result.exit_code == 0
    assert "Documentation commands" in result.stdout
    mock_online_help.home.assert_called_once_with()


@pytest.mark.parametrize(
    ("command", "method_name", "arguments"),
    [
        ("github", "github", []),
        ("user-guide", "user_guide", []),
        ("getting-started", "getting_started", []),
        ("installation", "installation_guide", []),
        ("api", "api_reference", []),
        ("issues", "issues", []),
        ("changelog", "changelog", ["0.22.0"]),
    ],
)
def test_doc_subcommands(cli_runner, mock_online_help, command, method_name, arguments):
    result = cli_runner.invoke(app, ["doc", command] + arguments)
    assert result.exit_code == 0
    if command == "changelog":
        getattr(mock_online_help, method_name).assert_called_once_with(*arguments)
    else:
        getattr(mock_online_help, method_name).assert_called_once_with()


def test_doc_search_command_with_keywords(cli_runner, mock_online_help):
    result = cli_runner.invoke(app, ["doc", "search", "hfss", "waveport"])
    assert result.exit_code == 0
    mock_online_help.search.assert_called_once_with("hfss waveport")


def test_doc_search_command_no_keywords(cli_runner, mock_online_help):
    result = cli_runner.invoke(app, ["doc", "search"])
    assert result.exit_code == 1
    assert "Please provide at least one search keyword" in result.stdout
    mock_online_help.search.assert_not_called()


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_list(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_get_desktop.return_value = mock_desktop
    with patch(
        "ansys.aedt.core.cli.common.list_projects_with_designs",
        return_value=[{"name": "Project1", "designs": [], "count": 0}],
    ):
        result = cli_runner.invoke(app, ["project", "list", "--port", "50051"])

    assert result.exit_code == 0
    assert "Project1" in result.output


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_open(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_desktop.odesktop.GetActiveProject.return_value = Mock(GetName=Mock(return_value="MyProject"))
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["project", "open", "C:/test/project.aedt", "--port", "50051"])

    assert result.exit_code == 0
    assert "Opened project 'MyProject'" in result.output


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_save(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_proj = Mock()
    mock_proj.GetName.return_value = "MyProject"
    mock_desktop.odesktop.GetActiveProject.return_value = mock_proj
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["project", "save", "--port", "50051"])

    assert result.exit_code == 0
    assert "Project 'MyProject' saved" in result.output


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_list_json(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_get_desktop.return_value = mock_desktop

    with patch(
        "ansys.aedt.core.cli.common.list_projects_with_designs",
        return_value=[{"name": "Project1", "designs": [{"name": "D1", "type": "HFSS"}], "count": 1}],
    ):
        result = cli_runner.invoke(app, ["--json", "project", "list", "--port", "50051"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["data"]["projects"][0]["name"] == "Project1"


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_save_as(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_proj = Mock()
    mock_proj.GetName.return_value = "MyProject"
    mock_desktop.odesktop.GetActiveProject.return_value = mock_proj
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["project", "save", "--port", "50051", "--path", "C:/tmp/MyProject.aedt"])

    assert result.exit_code == 0
    mock_proj.SaveAs.assert_called_once_with("C:/tmp/MyProject.aedt", True)


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_create_project(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_project = Mock()
    mock_project.GetName.return_value = "RenamedProject"
    mock_desktop.odesktop.GetActiveProject.return_value = mock_project
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["project", "create", "--port", "50051", "--project", "RenamedProject"])

    assert result.exit_code == 0
    mock_desktop.odesktop.NewProject.assert_called_once_with()
    mock_project.Rename.assert_called_once_with("RenamedProject", True)


@patch("ansys.aedt.core.settings")
@patch("ansys.aedt.core.Hfss")
def test_project_create_design(mock_hfss, _mock_settings, cli_runner):
    app_instance = Mock(project_name="Project1", design_name="Design1")
    mock_hfss.return_value = app_instance

    result = cli_runner.invoke(
        app,
        ["project", "create", "--port", "50051", "--project", "Project1", "--design", "Design1", "--type", "Hfss"],
    )

    assert result.exit_code == 0
    mock_hfss.assert_called_once_with(
        port=50051,
        project="Project1",
        design="Design1",
        new_desktop=False,
        close_on_exit=False,
    )


def test_project_create_requires_project(cli_runner):
    result = cli_runner.invoke(app, ["project", "create", "--port", "50051"])
    assert result.exit_code == 1
    assert "--project is required" in result.output


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_project_close_active(mock_get_desktop, cli_runner):
    mock_desktop = Mock()
    mock_project = Mock()
    mock_project.GetName.return_value = "Project1"
    mock_desktop.odesktop.GetActiveProject.return_value = mock_project
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["project", "close", "--port", "50051"])

    assert result.exit_code == 0
    mock_desktop.odesktop.CloseProject.assert_called_once_with("Project1")


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_script_run_file_not_found(mock_get_desktop, cli_runner):
    mock_get_desktop.return_value = Mock()
    result = cli_runner.invoke(app, ["script", "run", "nonexistent.py", "--port", "50051"])
    assert result.exit_code == 1
    assert "Script not found" in result.output


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_script_run_success(mock_get_desktop, cli_runner, tmp_path):
    script_file = tmp_path / "test_script.py"
    script_file.write_text("print('hello')", encoding="utf-8")

    mock_desktop = Mock()
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["script", "run", str(script_file), "--port", "50051"])

    assert result.exit_code == 0
    assert "Script executed" in result.output


@patch("ansys.aedt.core.cli.common.get_desktop")
def test_script_run_json(mock_get_desktop, cli_runner, tmp_path):
    script_file = tmp_path / "test_script.py"
    script_file.write_text("print('hello')", encoding="utf-8")
    mock_desktop = Mock()
    mock_get_desktop.return_value = mock_desktop

    result = cli_runner.invoke(app, ["--json", "script", "run", str(script_file), "--port", "50051"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["data"]["executed"] is True


@patch("ansys.aedt.core.cli.common.get_design_app")
def test_export_screenshot_success(mock_get_design_app, cli_runner, tmp_path):
    mock_app = Mock()
    mock_app.design_name = "D1"
    mock_get_design_app.return_value = (Mock(), mock_app, {"project": "P1"})

    out = tmp_path / "shot.jpg"
    result = cli_runner.invoke(app, ["export", "screenshot", "--port", "50051", "--path", str(out)])

    assert result.exit_code == 0
    assert "Screenshot saved" in result.output


@patch("ansys.aedt.core.cli.common.get_design_app")
def test_export_screenshot_failure(mock_get_design_app, cli_runner, tmp_path):
    mock_app = Mock()
    mock_app.design_name = "D1"
    mock_app.export_design_preview_to_jpg.side_effect = RuntimeError("save first")
    mock_get_design_app.return_value = (Mock(), mock_app, {"project": "P1"})

    result = cli_runner.invoke(app, ["export", "screenshot", "--port", "50051", "--path", str(tmp_path / "shot.jpg")])

    assert result.exit_code == 1
    assert "Failed to export screenshot" in result.output


@patch("ansys.aedt.core.cli.common.get_design_app")
def test_export_config_to_file(mock_get_design_app, cli_runner, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"solver": "hfss"}', encoding="utf-8")

    mock_app = Mock()
    mock_app.design_name = "D1"
    mock_app.configurations.export_config.return_value = str(config_file)
    mock_get_design_app.return_value = (Mock(), mock_app, {"project": "P1"})

    result = cli_runner.invoke(app, ["export", "config", "--port", "50051", "--output", str(tmp_path / "config")])

    assert result.exit_code == 0
    assert "Configuration exported to" in result.output
    mock_app.configurations.export_config.assert_called_once_with(
        config_file=str(tmp_path / "config.json"), overwrite=False
    )


@patch("ansys.aedt.core.cli.common.get_design_app")
def test_export_config_to_stdout(mock_get_design_app, cli_runner):
    mock_app = Mock()
    mock_app.design_name = "D1"

    def export_config_side_effect(config_file, overwrite):
        Path(config_file).write_text('{"solver": "hfss"}', encoding="utf-8")
        return config_file

    mock_app.configurations.export_config.side_effect = export_config_side_effect
    mock_get_design_app.return_value = (Mock(), mock_app, {"project": "P1"})

    result = cli_runner.invoke(app, ["export", "config", "--port", "50051"])

    assert result.exit_code == 0
    assert '"solver": "hfss"' in result.output


@patch("ansys.aedt.core.cli.common.get_design_app")
def test_export_config_failure(mock_get_design_app, cli_runner):
    mock_app = Mock()
    mock_app.design_name = "D1"
    mock_app.configurations.export_config.return_value = None
    mock_get_design_app.return_value = (Mock(), mock_app, {"project": "P1"})

    result = cli_runner.invoke(app, ["export", "config", "--port", "50051"])

    assert result.exit_code == 1
    assert "Failed to export configuration" in result.output


def test_print_output_json_ok(capsys):
    common_mod.json_mode = True
    print_output(data={"version": "2026.1"})
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["status"] == "ok"


def test_print_output_json_error(capsys):
    common_mod.json_mode = True
    print_output(error="boom")
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload == {"status": "error", "error": "boom"}


def test_print_output_human_noop(capsys):
    common_mod.json_mode = False
    print_output(data={"x": 1})
    assert capsys.readouterr().out == ""


def test_get_tests_folder_from_package():
    folder = get_tests_folder()
    assert isinstance(folder, Path)
