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

from __future__ import annotations

import os
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

from ansys.aedt.core.cli.common import _can_access_process
from ansys.aedt.core.cli.common import _find_aedt_processes
from ansys.aedt.core.cli.common import _get_port

app = typer.Typer(help="Process management commands")


@app.command()
def version() -> None:
    """Display PyAEDT version."""
    import ansys.aedt.core

    version = ansys.aedt.core.__version__
    typer.echo("PyAEDT version: ", nl=False)
    typer.secho(version, fg="cyan")


@app.command()
def processes() -> None:
    """Display all running AEDT-related processes."""
    aedt_procs: list[psutil.Process] = _find_aedt_processes()

    if not aedt_procs:
        typer.secho("No AEDT processes currently running.", fg="yellow")
        return

    typer.echo("Found ", nl=False)
    typer.secho(f"{len(aedt_procs)}", fg="green", nl=False)
    typer.echo(" AEDT process(es):")
    typer.echo("-" * 80)

    for proc in aedt_procs:
        typer.echo("PID: ", nl=False)
        typer.secho(f"{proc.pid}", fg="cyan")
        typer.echo(f"Name: {proc.name()}")
        cmd_line = proc.cmdline()
        if cmd_line:
            extra = "" if len(cmd_line) < 100 else "..."
            typer.echo(f"Command: {cmd_line[:100]}{extra}")
            port = _get_port(proc)
            if port is None:
                typer.echo("Port: ", nl=False)
                typer.secho("not found", fg="yellow")
            else:
                typer.echo("Port: ", nl=False)
                typer.secho(f"{port}", fg="cyan")
        typer.echo("-" * 40)


@app.command()
def start(
    version: str = typer.Option("2025.2", "--version", "-v", help="AEDT version to start (latest 2025.2)"),
    non_graphical: bool = typer.Option(False, "--non-graphical", "-ng", help="Start AEDT in non-graphical mode"),
    port: int = typer.Option(0, "--port", "-p", help="Port for AEDT connection (0 for auto)"),
    student_version: bool = typer.Option(False, "--student", help="Start AEDT Student version"),
) -> None:
    """Start a new AEDT process."""
    try:
        typer.echo("Starting AEDT ", nl=False)
        typer.secho(version, fg="cyan", nl=False)
        typer.echo("...")

        from ansys.aedt.core import settings
        from ansys.aedt.core.desktop import Desktop

        settings.enable_logger = False

        args = {
            "version": version,
            "non_graphical": non_graphical,
            "new_desktop": True,
            "student_version": student_version,
            "close_on_exit": False,
        }

        # Add port if specified
        if port > 0:
            args["port"] = port
            typer.echo("Using port: ", nl=False)
            typer.secho(f"{port}", fg="cyan")

        if non_graphical:
            typer.echo("Starting in non-graphical mode...")

        if student_version:
            typer.echo("Starting student version...")

        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        progress_running = True

        def show_progress() -> None:
            """Display animated progress indicator"""
            i = 0
            while progress_running:
                sys.stdout.write(f"\r{progress_chars[i % len(progress_chars)]} Initializing AEDT...\n")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
            sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
            sys.stdout.flush()

        progress_thread = threading.Thread(target=show_progress, daemon=True)
        progress_thread.start()

        d = Desktop(**args)

        progress_running = False

        typer.secho(f"✓ AEDT started successfully in port {d.port}", fg="green")
        return
    except Exception as e:
        typer.secho(f"✗ Error starting AEDT: {str(e)}", fg="red")
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
) -> None:
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
        raise typer.BadParameter("Please provide at least one option: --pid, --port, or --all")

    if stop_all:
        aedt_procs = _find_aedt_processes()
        failed = False
        for proc in aedt_procs:
            try:
                if not _can_access_process(proc):
                    failed = True
                    typer.secho(f"✗ Access denied for process with PID {proc.pid}.", fg="red")
                    continue
                proc.kill()
            except psutil.NoSuchProcess:
                typer.secho(f"! Process {proc.pid} no longer exists", fg="yellow")
            except Exception:
                failed = True
                typer.secho(f"✗ Error stopping process {proc.pid}", fg="red")
        if failed:
            typer.secho("Some AEDT processes could not be stopped.", fg="yellow")
        else:
            typer.secho("All AEDT processes have been stopped.", fg="green")
        return

    if pids:
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                if not _can_access_process(proc):
                    typer.secho(f"✗ Access denied for process with PID {pid}.", fg="red")
                    continue
                if proc.status() not in PROCESS_OK_STATUS:
                    typer.secho(f"✗ Process with PID {pid} is not in a stoppable state.", fg="red")
                    continue
                proc.kill()
                typer.secho(f"✓ Process with PID {pid} has been stopped.", fg="green")
            except psutil.NoSuchProcess:
                typer.secho(f"! Process {pid} no longer exists.", fg="yellow")
            except Exception:
                typer.secho(f"✗ Error stopping process {pid}.", fg="red")

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
            typer.secho(f"✗ No AEDT process found listening on port {port}.", fg="red")
            return

        if not _can_access_process(target_proc):
            typer.secho(f"✗ Access denied for process with PID {target_proc.pid}.", fg="red")
            return

        try:
            target_proc.kill()
            typer.secho(f"✓ Process with PID {target_proc.pid} listening on port {port} has been stopped.", fg="green")
        except psutil.NoSuchProcess:
            typer.secho(f"! Process {target_proc.pid} no longer exists.", fg="yellow")
        except Exception:
            typer.secho(f"✗ Error stopping process {target_proc.pid}.", fg="red")

    return


@app.command()
def attach(
    pid: int = typer.Option(None, "--pid", "-p", help="Process ID to attach to directly"),
) -> None:
    """Attach to a running AEDT process and launch an interactive PyAEDT console."""
    aedt_procs: list[psutil.Process] = _find_aedt_processes()

    if not aedt_procs:
        typer.secho("No AEDT processes currently running.", fg="yellow")
        typer.echo("Start AEDT first using: ", nl=False)
        typer.secho("pyaedt start", fg="cyan")
        return

    if pid is not None:
        _attach_to_pid(pid, aedt_procs)
        return

    _attach_interactive(aedt_procs)


def _extract_version_from_cmdline(cmd_line: list) -> str:
    """Extract AEDT version from command line arguments.

    Parameters
    ----------
    cmd_line : list
        Command line arguments

    Returns
    -------
    str
        Version string (e.g., "2025.2") or "unknown"
    """
    if not cmd_line:
        return "unknown"

    for part in cmd_line:
        if "\\v" in part or "/v" in part:
            version_parts = part.split("\\v" if "\\" in part else "/v")
            if len(version_parts) > 1:
                version = version_parts[1][:3] if len(version_parts[1]) >= 3 else version_parts[1]
                if len(version) == 3 and version.isdigit():
                    return f"20{version[0:2]}.{version[2]}"
    return "unknown"


def _attach_to_pid(pid: int, aedt_procs: list[psutil.Process]) -> None:
    """Attach to a specific AEDT process by PID.

    Parameters
    ----------
    pid : int
        Process ID to attach to
    aedt_procs : list[psutil.Process]
        List of available AEDT processes
    """
    target_proc = next((proc for proc in aedt_procs if proc.pid == pid), None)

    if target_proc is None:
        typer.secho(f"✗ No AEDT process found with PID {pid}.", fg="red")
        typer.echo("Available AEDT processes:")
        for proc in aedt_procs:
            typer.echo("  • PID: ", nl=False)
            typer.secho(f"{proc.pid}", fg="cyan")
        return

    version = _extract_version_from_cmdline(target_proc.cmdline())
    typer.echo("Attaching to process ", nl=False)
    typer.secho(f"{pid}", fg="cyan", nl=False)
    typer.echo("...")
    _launch_console_setup(pid, version)


def _attach_interactive(aedt_procs: list[psutil.Process]) -> None:
    """Interactive mode to select and attach to an AEDT process.

    Parameters
    ----------
    aedt_procs : list[psutil.Process]
        List of available AEDT processes
    """
    typer.echo("Found ", nl=False)
    typer.secho(f"{len(aedt_procs)}", fg="green", nl=False)
    typer.echo(" AEDT process(es):\n")

    # Build and display process info
    process_info = []
    for idx, proc in enumerate(aedt_procs, 1):
        port = _get_port(proc)
        version = _extract_version_from_cmdline(proc.cmdline())
        process_info.append({"idx": idx, "proc": proc, "pid": proc.pid, "port": port, "version": version})

        typer.secho(f"  {idx}", fg="yellow", nl=False)
        typer.echo(". PID: ", nl=False)
        typer.secho(f"{proc.pid}", fg="cyan", nl=False)
        typer.echo(" | Version: ", nl=False)
        typer.secho(f"{version}", fg="blue", nl=False)
        typer.echo(" | Port: ", nl=False)
        if port:
            typer.secho(f"{port}", fg="green")
        else:
            typer.secho("COM mode", fg="yellow")

    typer.echo("")
    choice_idx = None
    while choice_idx is None:
        typer.echo("Select process number (1-", nl=False)
        typer.secho(f"{len(process_info)}", fg="yellow", nl=False)
        typer.echo(") or '", nl=False)
        typer.secho("q", fg="red", nl=False)
        typer.echo("' to quit: ", nl=False)
        choice = input().strip()

        if choice.lower() == "q":
            typer.echo("Cancelled.")
            return

        try:
            choice_idx = int(choice)
            if choice_idx < 1 or choice_idx > len(process_info):
                typer.secho(f"✗ Invalid selection. Please enter a number between 1 and {len(process_info)}.", fg="red")
                choice_idx = None
        except ValueError:
            typer.secho("✗ Invalid input. Please enter a number.", fg="red")

    # Attach to selected process
    selected = process_info[choice_idx - 1]
    typer.echo("\nAttaching to process ", nl=False)
    typer.secho(f"{selected['pid']}", fg="cyan", nl=False)
    typer.echo("...")
    _launch_console_setup(selected["pid"], selected["version"])


def _launch_console_setup(pid: int, version: str) -> None:
    """Launch console_setup.py script to attach to an AEDT process.

    Parameters
    ----------
    pid : int
        Process ID of the AEDT instance
    version : str
        AEDT version string
    """
    from pathlib import Path
    import subprocess  # nosec B404 - subprocess needed for launching interactive console

    env = os.environ.copy()
    # Set environment variables
    env["PYAEDT_PROCESS_ID"] = str(pid)
    env["PYAEDT_DESKTOP_VERSION"] = version

    try:
        import ansys.aedt.core

        package_dir = Path(ansys.aedt.core.__file__).parent
        console_setup_path = package_dir / "extensions" / "installer" / "console_setup.py"

        if not console_setup_path.exists():
            typer.secho(f"✗ Error: console_setup.py not found at {console_setup_path}", fg="red")
            return
    except Exception as e:
        typer.secho(f"✗ Error locating console_setup.py: {str(e)}", fg="red")
        return

    # Check for IPython
    import importlib.util

    if importlib.util.find_spec("IPython") is None:  # pragma: no cover
        typer.secho("✗ IPython is required for the interactive console.", fg="red")
        typer.echo("Install it with: ", nl=False)
        typer.secho("pip install ipython", fg="cyan")
        return

    # Get Python executable
    python_exe = sys.executable

    typer.echo("")

    # Launch console_setup.py in interactive mode using subprocess.Popen
    try:  # pragma: no cover
        subprocess.run([python_exe, "-i", str(console_setup_path)], env=env, check=False)  # nosec B603 - trusted paths from sys.executable and package location
    except KeyboardInterrupt:  # pragma: no cover
        typer.echo("\n\nInterrupted.")
    except Exception as e:  # pragma: no cover
        typer.secho(f"✗ Error launching console: {str(e)}", fg="red")
