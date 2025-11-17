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
panels_app = typer.Typer(help="Manage PyAEDT panels in AEDT", no_args_is_help=True)
app.add_typer(panels_app, name="panels")


def _is_valid_process(proc: psutil.Process) -> bool:
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
    """Discover running AEDT-related processes on the system."""
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


@panels_app.command("add")
def add_panels(
    aedt_version: str = typer.Option(
        None,
        "--version",
        "-v",
        help="AEDT version (such as 2025.2)",
        prompt="Enter AEDT version",
    ),
    personal_lib: str = typer.Option(
        None,
        "--personal-lib",
        "-p",
        help="Path to AEDT PersonalLib folder",
        prompt="Enter path to PersonalLib folder",
    ),
    skip_version_manager: bool = typer.Option(
        False,
        "--skip-version-manager",
        help="Skip installing the Version Manager tab",
    ),
):
    """Add PyAEDT panels to AEDT installation.

    This command installs PyAEDT tabs (Console, Jupyter, Run Script, Extension Manager,
    and optionally Version Manager) into your AEDT installation.

    Examples
    --------
        pyaedt panels add --version 2025.2 --personal-lib "C:\\Users\\username\\AppData\\Roaming\\Ansoft\\PersonalLib"
        pyaedt panels add -v 2025.2 -p "/home/username/Ansoft/PersonalLib"
    """
    try:
        # Validate AEDT version format
        if not aedt_version or not isinstance(aedt_version, str):
            typer.secho(
                "✗ Invalid AEDT version. Provide a valid version string (such as 2025.2)",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        aedt_version = aedt_version.strip()
        if not aedt_version:
            typer.secho("✗ AEDT version cannot be empty.", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        # Validate personal_lib path
        if not personal_lib or not isinstance(personal_lib, str):
            typer.secho(
                "✗ Invalid PersonalLib path. Please provide a valid path",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        personal_lib = personal_lib.strip()
        if not personal_lib:
            typer.secho(
                "✗ Invalid PersonalLib path. Please provide a valid path",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        personal_lib_path = Path(personal_lib)

        if not personal_lib_path.exists():
            typer.secho(
                f"✗ PersonalLib path does not exist: {personal_lib_path}",
                fg=typer.colors.RED,
                bold=True,
            )
            typer.echo("\nCommon PersonalLib locations:")
            if platform.system() == "Windows":
                typer.secho(
                    "  Windows: C:\\Users\\<username>\\AppData\\Roaming\\Ansoft\\PersonalLib",
                    fg=typer.colors.CYAN,
                )
            else:
                typer.secho(
                    "  Linux: /home/<username>/Ansoft/PersonalLib",
                    fg=typer.colors.CYAN,
                )
            raise typer.Exit(code=1)

        if not personal_lib_path.is_dir():
            typer.secho(
                f"✗ PersonalLib path is not a directory: {personal_lib_path}",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        # Import and run the installer
        typer.secho(
            f"Installing PyAEDT panels for AEDT {aedt_version}...",
            fg=typer.colors.BLUE,
            bold=True,
        )
        typer.secho(f"PersonalLib location: {personal_lib_path}", fg=typer.colors.CYAN)

        if skip_version_manager:
            typer.secho("Skipping Version Manager tab...", fg=typer.colors.YELLOW)

        from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt

        result = add_pyaedt_to_aedt(
            aedt_version=aedt_version,
            personal_lib=str(personal_lib_path),
            skip_version_manager=skip_version_manager,
            odesktop=None,
        )

        if result is False:
            typer.secho("✗ Failed to install PyAEDT panels", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        typer.secho("✓ PyAEDT panels installed successfully!", fg=typer.colors.GREEN, bold=True)
        typer.echo("\nInstalled panels:")
        typer.secho("  • Console", fg=typer.colors.GREEN)
        typer.secho("  • Jupyter", fg=typer.colors.GREEN)
        typer.secho("  • Run Script", fg=typer.colors.GREEN)
        typer.secho("  • Extension Manager", fg=typer.colors.GREEN)
        if not skip_version_manager:
            typer.secho("  • Version Manager", fg=typer.colors.GREEN)
        typer.secho(
            "\nRestart AEDT to see the new panels in the Automation tab.",
            fg=typer.colors.YELLOW,
            bold=True,
        )

    except typer.Exit:
        raise
    except ImportError as e:
        typer.secho(f"✗ Import error: {str(e)}", fg=typer.colors.RED, bold=True)
        typer.echo("Make sure PyAEDT is properly installed.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"✗ Error installing panels: {str(e)}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
