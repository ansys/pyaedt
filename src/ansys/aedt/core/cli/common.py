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

import getpass
import json
from pathlib import Path
import platform

import psutil

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

# Default configuration for local_config.json
DEFAULT_TEST_CONFIG = {
    "desktopVersion": "2025.2",
    "NonGraphical": True,
    "NewThread": True,
    "skip_circuits": False,
    "use_grpc": True,
    "close_desktop": True,
    "use_local_example_data": False,
    "local_example_folder": "",
    "skip_modelithics": True,
}


def _get_tests_folder() -> Path:
    """Find the tests folder in the repository.

    Returns
    -------
    Path
        Path to the tests folder
    """
    try:
        import ansys.aedt.core

        package_dir = Path(ansys.aedt.core.__file__).parent
        # Go up from src/ansys/aedt/core to the repo root
        repo_root = package_dir.parent.parent.parent.parent
        tests_folder = repo_root / "tests"
        if tests_folder.exists():
            return tests_folder
    except Exception:
        typer.echo("! Error finding tests folder, fallbacking to current working directory.")
    # Fallback: search from current working directory
    cwd = Path.cwd()
    return cwd / "tests"


def _load_config(config_path: Path) -> dict:
    """Load configuration from JSON file.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file

    Returns
    -------
    dict
        Configuration dictionary
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        # Filter to only include known keys
        return {k: config.get(k, v) for k, v in DEFAULT_TEST_CONFIG.items()}
    except Exception:
        return DEFAULT_TEST_CONFIG.copy()


def _save_config(config_path: Path, config: dict) -> None:
    """Save configuration to JSON file.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file
    config : dict
        Configuration dictionary to save
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def _prompt_config_value(key: str, current_value) -> any:
    """Prompt user to modify a configuration value.

    Parameters
    ----------
    key : str
        Configuration key
    current_value : any
        Current value

    Returns
    -------
    any
        New value or current value if unchanged
    """
    if isinstance(current_value, bool):
        typer.echo("      ", nl=False)
        choice = typer.confirm(f"Change to {not current_value}?", default=False)
        return not current_value if choice else current_value
    elif isinstance(current_value, str):
        typer.echo("      ", nl=False)

        # Special handling for desktopVersion
        if key == "desktopVersion":
            while True:
                new_value = typer.prompt(
                    "New value (format: YYYY.R, e.g., 2025.2)", default=current_value, show_default=False
                )
                # Remove quotes if user entered them
                new_value = new_value.strip().strip('"').strip("'")

                # Validate format: 4 digits + "." + 1 digit
                import re

                if re.match(r"^\d{4}\.\d$", new_value):
                    return new_value
                else:
                    typer.secho("      ✗ Invalid format. Please use YYYY.R (e.g., 2025.2)", fg="red")
                    typer.echo("      ", nl=False)
        else:
            new_value = typer.prompt("New value", default=current_value, show_default=False)
        return new_value
    elif isinstance(current_value, int):
        typer.echo("      ", nl=False)
        new_value = typer.prompt("New value", default=current_value, type=int, show_default=False)
        return new_value
    else:
        return current_value


def _display_config(config: dict, title: str = "Configuration", descriptions: dict = None) -> None:
    """Display configuration in a pretty formatted way.

    Parameters
    ----------
    config : dict
        Configuration dictionary to display
    title : str
        Title to display above the configuration
    descriptions : dict, optional
        Dictionary of key descriptions to display
    """
    typer.echo(f"\n{title}:")
    typer.echo()

    for key, value in config.items():
        if isinstance(value, bool):
            value_str = "True" if value else "False"
            color = "green" if value else "red"
        elif isinstance(value, str):
            if value == "":
                value_str = "(empty)"
                color = "yellow"
            else:
                value_str = f"{value}"
                color = "cyan"
        else:
            value_str = str(value)
            color = "white"

        # Display as bullet point
        typer.echo(f"  - {key}: ", nl=False)
        typer.secho(value_str, fg=color)

        # Display description if provided
        if descriptions and key in descriptions:
            desc = descriptions[key]
            typer.secho(f"    {desc}", fg="bright_black")

    typer.echo()


def _is_valid_process(proc: psutil.Process) -> bool:
    """Check if a process is a valid AEDT process.

    Parameters
    ----------
    proc : psutil.Process
        Process to check

    Returns
    -------
    bool
        True if process is a valid running AEDT process
    """
    valid_status = proc.status() in [
        psutil.STATUS_RUNNING,
        psutil.STATUS_IDLE,
        psutil.STATUS_SLEEPING,
    ]

    proc_name = proc.name().lower()
    valid_ansysem_process = proc_name in ("ansysedt.exe", "ansysedt")
    return valid_status and valid_ansysem_process


def _find_aedt_processes() -> list[psutil.Process]:
    """Discover running AEDT-related processes on the system.

    Returns
    -------
    list[psutil.Process]
        List of AEDT processes
    """
    aedt_processes = []

    for proc in psutil.process_iter():
        try:
            if _is_valid_process(proc):
                aedt_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return aedt_processes


def _can_access_process(proc: psutil.Process) -> bool:
    """Check if we have permission to access and kill a process.

    Returns True if:
    1. We can access the process information (no AccessDenied)
    2. The process belongs to the current user

    Parameters
    ----------
    proc : psutil.Process
        The process to check

    Returns
    -------
    bool
        True if we can safely access and kill the process
    """
    try:
        # Check if we can access basic process info and if it belongs to current user
        current_user = getpass.getuser().lower()
        process_user = proc.username().lower()
        # Handle Windows domain format (DOMAIN\username)
        if platform.system() == "Windows" and "\\" in process_user:
            return current_user == process_user.split("\\")[-1]
        return current_user == process_user
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        # Cannot access process or process doesn't exist
        return False


def _get_port(proc: psutil.Process) -> int | None:
    """Get the listening port for a given AEDT process.

    Parameters
    ----------
    proc : psutil.Process
        The AEDT process

    Returns
    -------
    int | None
        The listening port, or None if not found
    """
    res = None
    cmd_line = proc.cmdline()
    if "-grpcsrv" in cmd_line:
        res = int(cmd_line[cmd_line.index("-grpcsrv") + 1])
    else:
        # Look in the typical port range for AEDT
        for i in psutil.net_connections():
            if i.pid == proc.pid and i.status == "LISTEN" and 50000 <= i.laddr.port <= 50100:
                res = i.laddr.port
                break
    return res


def _get_config_path() -> tuple[Path, dict]:
    """Get the configuration path and load config.

    Returns
    -------
    tuple[Path, dict]
        Configuration file path and loaded config
    """
    tests_folder = _get_tests_folder()
    config_path = tests_folder / "local_config.json"
    config = _load_config(config_path) if config_path.exists() else DEFAULT_TEST_CONFIG.copy()
    return config_path, config
