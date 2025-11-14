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
"""PyAEDT CLI based on typer."""

import json
from pathlib import Path
import platform
import sys
import threading
import time

import psutil

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

app = typer.Typer(help="CLI for PyAEDT", no_args_is_help=True)
config_app = typer.Typer(help="Configuration management commands")
test_app = typer.Typer(help="Test configuration management commands", invoke_without_command=True)
app.add_typer(config_app, name="config")
config_app.add_typer(test_app, name="test")

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
        print("Error finding tests folder")
    # Fallback: search from current working directory
    cwd = Path.cwd()
    if cwd.name == "tests":
        return cwd

    tests_folder = cwd / "tests"
    if tests_folder.exists():
        return tests_folder

    for parent in [cwd] + list(cwd.parents):
        tests_folder = parent / "tests"
        if tests_folder.exists():
            return tests_folder

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
        choice = typer.confirm(
            f"Change to {not current_value}?",
            default=False
        )
        return not current_value if choice else current_value
    elif isinstance(current_value, str):
        typer.echo("      ", nl=False)
        
        # Special handling for desktopVersion
        if key == "desktopVersion":
            while True:
                new_value = typer.prompt(
                    "New value (format: YYYY.R, e.g., 2025.2)",
                    default=current_value,
                    show_default=False
                )
                # Remove quotes if user entered them
                new_value = new_value.strip().strip('"').strip("'")
                
                # Validate format: 4 digits + "." + 1 digit
                import re
                if re.match(r'^\d{4}\.\d$', new_value):
                    return new_value
                else:
                    typer.secho(
                        "      ✗ Invalid format. Please use YYYY.R (e.g., 2025.2)",
                        fg="red"
                    )
                    typer.echo("      ", nl=False)
        else:
            new_value = typer.prompt(
                "New value",
                default=current_value,
                show_default=False
            )
        return new_value
    elif isinstance(current_value, int):
        typer.echo("      ", nl=False)
        new_value = typer.prompt(
            "New value",
            default=current_value,
            type=int,
            show_default=False
        )
        return new_value
    else:
        return current_value


def _display_config(
    config: dict,
    title: str = "Configuration",
    descriptions: dict = None
) -> None:
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
    # Box drawing characters
    typer.echo("\n┌" + "─" * 68 + "┐")
    typer.echo(f"│  {title:64}  │")
    typer.echo("├" + "─" * 68 + "┤")

    for key, value in config.items():
        if isinstance(value, bool):
            value_str = "✓ True" if value else "✗ False"
            color = "green" if value else "red"
        elif isinstance(value, str):
            if value == "":
                value_str = "(empty)"
                color = "yellow"
            else:
                value_str = f"'{value}'"
                color = "cyan"
        else:
            value_str = str(value)
            color = "white"

        # Format key with proper spacing
        key_display = f"  {key}:"
        spacing = " " * (35 - len(key_display))
        typer.echo(f"│{key_display}{spacing}", nl=False)
        typer.secho(value_str, fg=color, nl=False)
        remaining_space = 68 - len(key_display) - len(spacing) - len(value_str)
        typer.echo(" " * remaining_space + "│")
        
        # Display description if provided
        if descriptions and key in descriptions:
            desc = descriptions[key]
            typer.echo(f"│    ", nl=False)
            typer.secho(f"→ {desc}", fg="bright_black", nl=False)
            desc_space = 68 - 4 - len(f"→ {desc}")
            typer.echo(" " * desc_space + "│")

    typer.echo("└" + "─" * 68 + "┘\n")


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
    import psutil

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
    import psutil

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
    import getpass

    import psutil

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
    import psutil

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


def _update_bool_config(key: str, value: bool | None, display_name: str = None) -> None:
    """Update a boolean configuration value.
    
    Parameters
    ----------
    key : str
        Configuration key
    value : bool | None
        New value or None for interactive mode
    display_name : str, optional
        Display name (defaults to key)
    """
    config_path, config = _get_config_path()
    display_name = display_name or key
    default = DEFAULT_TEST_CONFIG.get(key, False)
    
    if value is None:
        current_value = config.get(key, default)
        typer.echo(f"\nCurrent {display_name}: ", nl=False)
        value_str = "✓ True" if current_value else "✗ False"
        color = "green" if current_value else "red"
        typer.secho(value_str, fg=color)
        typer.echo("")
        value = typer.confirm(f"Set to {not current_value}?", default=True)
        value = not current_value if value else current_value
    
    config[key] = value
    _save_config(config_path, config)
    typer.secho(f"✓ {display_name} set to {value}", fg="green")


def _update_string_config(
    key: str,
    value: str | None,
    display_name: str = None,
    validator: callable = None
) -> None:
    """Update a string configuration value.
    
    Parameters
    ----------
    key : str
        Configuration key
    value : str | None
        New value or None for interactive mode
    display_name : str, optional
        Display name (defaults to key)
    validator : callable, optional
        Function to validate the value, should return (is_valid, error_message)
    """
    config_path, config = _get_config_path()
    display_name = display_name or key
    default = DEFAULT_TEST_CONFIG.get(key, "")
    
    if value is None:
        current_value = config.get(key, default)
        typer.echo(f"\nCurrent {display_name}: ", nl=False)
        if current_value:
            typer.secho(f"'{current_value}'", fg="cyan")
        else:
            typer.secho("(empty)", fg="yellow")
        
        if validator:
            typer.echo("")
            while True:
                value = typer.prompt("New value", default=current_value)
                value = value.strip().strip('"').strip("'")
                is_valid, error_msg = validator(value)
                if is_valid:
                    break
                else:
                    typer.secho(f"✗ {error_msg}", fg="red")
        else:
            typer.echo("")
            value = typer.prompt("New value", default=current_value)
    else:
        if validator:
            is_valid, error_msg = validator(value)
            if not is_valid:
                typer.secho(f"✗ {error_msg}", fg="red")
                return
    
    config[key] = value
    _save_config(config_path, config)
    typer.secho(f"✓ {display_name} set to '{value}'", fg="green")


@test_app.callback()
def test_callback(
    ctx: typer.Context,
    show: bool = typer.Option(
        False,
        "--show",
        "-s",
        help="Show current configuration without modifying"
    ),
):
    """Create or modify local_config.json in the tests folder interactively."""
    if ctx.invoked_subcommand is not None:
        return
    
    tests_folder = _get_tests_folder()
    config_path = tests_folder / "local_config.json"
    
    # Configuration descriptions
    config_descriptions = {
        "desktopVersion": "AEDT version to use",
        "NonGraphical": "Run AEDT without GUI",
        "NewThread": "Use new thread for AEDT",
        "skip_circuits": "Skip circuit tests",
        "use_grpc": "Use gRPC for communication",
        "close_desktop": "Close AEDT after tests",
        "use_local_example_data": "Use local example data",
        "local_example_folder": "Path to local examples",
        "skip_modelithics": "Skip Modelithics tests",
    }
 
    if config_path.exists():
        config = _load_config(config_path)
    else:
        config = DEFAULT_TEST_CONFIG.copy()
        _save_config(config_path, config)
    
    typer.echo("\n" + "=" * 70)
    typer.secho("  PyAEDT Test Configuration Manager", fg="bright_blue", bold=True)
    typer.echo("=" * 70)
    typer.echo("\n  📁 Tests folder: ", nl=False)
    typer.secho(str(tests_folder), fg="cyan")
    typer.echo("  📄 Config file:  ", nl=False)
    typer.secho(str(config_path), fg="cyan")

    if config_path.exists():
        typer.echo("\n  ", nl=False)
        typer.secho("✓", fg="green", bold=True, nl=False)
        typer.echo(" Configuration file found")
    else:
        typer.echo("\n  ", nl=False)
        typer.secho("✓", fg="green", bold=True, nl=False)
        typer.echo(" Configuration file created with defaults")

    # Display current configuration with descriptions
    _display_config(config, "Current Test Configuration", config_descriptions)

    # If --show flag is used, just display and exit
    if show:
        return

    # Interactive questionnaire
    typer.echo("─" * 70)
    typer.secho("  Would you like to modify the configuration?", fg="yellow", bold=True)
    typer.echo("─" * 70 + "\n")

    modify = typer.confirm("  Modify settings?", default=False)

    if not modify:
        typer.echo("\n  ", nl=False)
        typer.secho("i", fg="blue", bold=True, nl=False)
        typer.echo("  No changes made.\n")
        return

    # Interactive configuration
    typer.echo("\n" + "=" * 70)
    typer.secho("  Interactive Configuration", fg="bright_blue", bold=True)
    typer.echo("=" * 70)
    typer.secho("\n  💡 Tip: Press Enter to keep current value\n", fg="yellow")

    new_config = {}

    for i, (key, value) in enumerate(config.items(), 1):
        typer.echo(f"\n  [{i}/{len(config)}] ", nl=False)
        typer.secho(key, fg="bright_cyan", bold=True)

        description = config_descriptions.get(key, "")
        if description:
            typer.echo("      ", nl=False)
            typer.secho(f"i  {description}", fg="blue")

        if isinstance(value, bool):
            current_display = "✓ True" if value else "✗ False"
            color = "green" if value else "red"
        elif isinstance(value, str):
            current_display = f"'{value}'" if value else "(empty)"
            color = "cyan" if value else "yellow"
        else:
            current_display = str(value)
            color = "white"

        typer.echo("      Current: ", nl=False)
        typer.secho(current_display, fg=color)

        new_value = _prompt_config_value(key, value)
        new_config[key] = new_value

    typer.echo("\n" + "─" * 70)
    typer.echo("  Saving configuration...")
    _save_config(config_path, new_config)

    typer.echo("\n" + "=" * 70)
    typer.secho("  ✓ Configuration Updated Successfully!", fg="green", bold=True)
    typer.echo("=" * 70)

    _display_config(new_config, "Updated Test Configuration", config_descriptions)

    typer.secho("  Configuration saved to:", fg="bright_blue")
    typer.secho(f"  {config_path}\n", fg="cyan")


@test_app.command()
def desktop_version(value: str = typer.Argument(None, help="AEDT version (format: YYYY.R, e.g., 2025.2)")):
    """Set AEDT desktop version."""
    import re
    
    def validate_version(v: str) -> tuple[bool, str]:
        """Validate version format."""
        if re.match(r'^\d{4}\.\d$', v):
            return True, ""
        return False, "Invalid format. Please use YYYY.R (e.g., 2025.2)"
    
    _update_string_config("desktopVersion", value, "desktopVersion", validate_version)


@test_app.command()
def non_graphical(value: bool = typer.Argument(None, help="Run AEDT without GUI (true/false)")):
    """Set non-graphical mode."""
    _update_bool_config("NonGraphical", value, "NonGraphical")


@test_app.command()
def new_thread(value: bool = typer.Argument(None, help="Use new thread for AEDT (true/false)")):
    """Set new thread mode."""
    _update_bool_config("NewThread", value, "NewThread")


@test_app.command()
def skip_circuits(value: bool = typer.Argument(None, help="Skip circuit tests (true/false)")):
    """Set skip circuits flag."""
    _update_bool_config("skip_circuits", value, "skip_circuits")


@test_app.command()
def use_grpc(value: bool = typer.Argument(None, help="Use gRPC for communication (true/false)")):
    """Set use gRPC flag."""
    _update_bool_config("use_grpc", value, "use_grpc")


@test_app.command()
def close_desktop(value: bool = typer.Argument(None, help="Close AEDT after tests (true/false)")):
    """Set close desktop flag."""
    _update_bool_config("close_desktop", value, "close_desktop")


@test_app.command()
def use_local_example_data(value: bool = typer.Argument(None, help="Use local example data (true/false)")):
    """Set use local example data flag."""
    _update_bool_config("use_local_example_data", value, "use_local_example_data")


@test_app.command()
def local_example_folder(value: str = typer.Argument(None, help="Path to local examples folder")):
    """Set local example folder path."""
    _update_string_config("local_example_folder", value, "local_example_folder")


@test_app.command()
def skip_modelithics(value: bool = typer.Argument(None, help="Skip Modelithics tests (true/false)")):
    """Set skip Modelithics flag."""
    _update_bool_config("skip_modelithics", value, "skip_modelithics")


@app.command()
def version():
    """Display PyAEDT version."""
    import ansys.aedt.core

    version = ansys.aedt.core.__version__
    typer.echo(f"PyAEDT version: {version}")


@app.command()
def processes():
    """Display all running AEDT-related processes."""
    aedt_procs: list[psutil.Process] = _find_aedt_processes()

    if not aedt_procs:
        typer.echo("No AEDT processes currently running.")
        return

    typer.echo(f"Found {len(aedt_procs)} AEDT process(es):")
    typer.echo("-" * 80)

    for proc in aedt_procs:
        typer.echo(f"PID: {proc.pid}")
        typer.echo(f"Name: {proc.name()}")
        cmd_line = proc.cmdline()
        if cmd_line:
            extra = "" if len(cmd_line) < 100 else "..."
            typer.echo(f"Command: {cmd_line[:100]}{extra}")
            port = _get_port(proc)
            if port is None:
                port = "not found"
            typer.echo(f"Port: {port}")
        typer.echo("-" * 40)


@app.command()
def start(
    version: str = typer.Option("2025.2", "--version", "-v", help="AEDT version to start (e.g., 2025.1, 2025.2)"),
    non_graphical: bool = typer.Option(False, "--non-graphical", "-ng", help="Start AEDT in non-graphical mode"),
    port: int = typer.Option(0, "--port", "-p", help="Port for AEDT connection (0 for auto)"),
    student_version: bool = typer.Option(False, "--student", help="Start AEDT Student version"),
):
    """Start a new AEDT process."""
    try:
        typer.echo(f"Starting AEDT {version}...")

        from ansys.aedt.core import settings
        from ansys.aedt.core.desktop import Desktop

        settings.enable_logger = False

        args = {
            "version": version,
            "non_graphical": non_graphical,
            "new_desktop_session": True,
            "student_version": student_version,
            "close_on_exit": False,
        }

        # Add port if specified
        if port > 0:
            args["port"] = port
            typer.echo(f"Using port: {port}")

        if non_graphical:
            typer.echo("Starting in non-graphical mode...")

        if student_version:
            typer.echo("Starting student version...")

        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        progress_running = True

        def show_progress():
            """Display animated progress indicator"""
            i = 0
            while progress_running:
                sys.stdout.write(f"\r{progress_chars[i % len(progress_chars)]} Initializing AEDT...")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
            sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
            sys.stdout.flush()

        progress_thread = threading.Thread(target=show_progress, daemon=True)
        progress_thread.start()

        _ = Desktop(**args)

        progress_running = False
        time.sleep(0.2)  # Give time for thread to finish

        typer.echo("✓ AEDT started successfully")
        return
    except Exception as e:
        typer.echo(f"✗ Error starting AEDT: {str(e)}")
        typer.echo("Common issues:")
        typer.echo("  - AEDT not installed or not in PATH")
        typer.echo("  - Invalid version specified")
        typer.echo("  - License server not available")
        typer.echo("  - Insufficient permissions")
        return


@app.command()
def stop(
    pids: list[int] = typer.Option([], "--pid", help="Stop process by PID (can be used multiple times)"),
    ports: list[int] = typer.Option([], "--port", help="Stop process by port (can be used multiple times)"),
    stop_all: bool = typer.Option(False, "--all", "-a", help="Stop all running AEDT processes"),
):
    """Stop running AEDT process(es)."""
    import psutil

    # List of process statuses considered OK for termination
    PROCESS_OK_STATUS = [
        psutil.STATUS_RUNNING,
        psutil.STATUS_SLEEPING,
        psutil.STATUS_DISK_SLEEP,
        psutil.STATUS_DEAD,
        psutil.STATUS_PARKED,  # (Linux)
        psutil.STATUS_IDLE,  # (Linux)
    ]

    if not pids and not ports and not stop_all:
        typer.echo("Please provide PID(s), port(s), or use --all to stop all AEDT processes.")
        typer.echo("Examples:")
        typer.echo("  pyaedt stop --pid 1234")
        typer.echo("  pyaedt stop --pid 1234 --pid 5678")
        typer.echo("  pyaedt stop --port 50051")
        typer.echo("  pyaedt stop --all")
        return

    if stop_all:
        aedt_procs = _find_aedt_processes()
        failed = False
        for proc in aedt_procs:
            try:
                if not _can_access_process(proc):
                    failed = True
                    typer.echo(f"✗ Access denied for process with PID {proc.pid}.")
                    continue
                proc.kill()
            except psutil.NoSuchProcess:
                typer.echo(f"! Process {proc.pid} no longer exists")
            except Exception:
                failed = True
                typer.echo(f"✗ Error stopping process {proc.pid}")
        if failed:
            typer.echo("Some AEDT processes could not be stopped.")
        else:
            typer.echo("All AEDT processes have been stopped.")
        return

    if pids:
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                if not _can_access_process(proc):
                    typer.echo(f"✗ Access denied for process with PID {pid}.")
                    continue
                if proc.status() not in PROCESS_OK_STATUS:
                    typer.echo(f"✗ Process with PID {pid} is not in a stoppable state.")
                    continue
                proc.kill()
                typer.echo(f"Process with PID {pid} has been stopped.")
            except psutil.NoSuchProcess:
                typer.echo(f"! Process {pid} no longer exists.")
            except Exception:
                typer.echo(f"✗ Error stopping process {pid}.")

    if ports:
        aedt_procs = _find_aedt_processes()
        for port in ports:
            target_proc = None
            for proc in aedt_procs:
                proc_port = _get_port(proc)
                if proc_port == port:
                    target_proc = proc
                    break

            if target_proc is None:
                typer.echo(f"✗ No AEDT process found listening on port {port}.")
                return

            if not _can_access_process(target_proc):
                typer.echo(f"✗ Access denied for process with PID {target_proc.pid}.")
                return

            try:
                target_proc.kill()
                typer.echo(f"Process with PID {target_proc.pid} listening on port {port} has been stopped.")
            except psutil.NoSuchProcess:
                typer.echo(f"! Process {target_proc.pid} no longer exists.")
            except Exception:
                typer.echo(f"✗ Error stopping process {target_proc.pid}.")

    return


if __name__ == "__main__":
    app()
