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

"""Session management commands: start, list, stop, attach."""

from __future__ import annotations

import os
import re
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

from ansys.aedt.core.cli import common
from ansys.aedt.core.generic.general_methods import _check_psutil_connections
from ansys.aedt.core.generic.general_methods import _normalize_version_to_string
from ansys.aedt.core.generic.general_methods import active_sessions
from ansys.aedt.core.internal.aedt_versions import aedt_versions

session_app = typer.Typer(help="Session management commands")


def _extract_session_metadata(cmdline: str | None) -> dict[str, object]:
    """Extract display metadata from a process command line."""
    metadata = {"version": "unknown", "non_graphical": None}
    if not cmdline:
        return metadata

    # Match AEDT install paths like ...\v261\... or .../v261/... and capture the 3-digit version token.
    version_match = re.search(r"[\\/]v(?P<version>\d{3})(?=[\\/\s]|$)", cmdline)
    if version_match:
        metadata["version"] = _normalize_version_to_string(version_match.group("version"))

    metadata["non_graphical"] = "-ng" in cmdline.split()
    return metadata


def _discover_aedt_sessions() -> list[dict[str, object]]:
    sessions_by_pid: dict[int, dict[str, object]] = {}
    for student_version in (False, True):
        for pid, port in active_sessions(student_version=student_version).items():
            sessions_by_pid[pid] = {
                "pid": pid,
                "port": None if port == -1 else port,
                "mode": "com" if port == -1 else "grpc",
                "student_version": student_version,
                "version": "unknown",
                "non_graphical": None,
            }

    connections = _check_psutil_connections(list(sessions_by_pid.keys())) if sessions_by_pid else {}
    for pid, session in sessions_by_pid.items():
        cmdline = next(
            (
                connection.get("cmdline")
                for connection in connections.get(pid, [])
                if isinstance(connection.get("cmdline"), str)
            ),
            None,
        )
        session.update(_extract_session_metadata(cmdline))

    return sorted(sessions_by_pid.values(), key=lambda session: int(session["pid"]))


@session_app.command("start")
def start(
    version: str = typer.Option(
        aedt_versions.current_version, "--version", "-v", help="AEDT version to start (e.g. 2026.1)"
    ),
    port: int = typer.Option(50051, "--port", help="gRPC port (0 for auto)"),
    non_graphical: bool = typer.Option(False, "--non-graphical", "-ng", help="Start in non-graphical mode"),
) -> None:
    """Start a new AEDT instance."""
    try:
        if not common.json_mode:
            typer.echo("Starting AEDT ", nl=False)
            typer.secho(version, fg="cyan", nl=False)
            typer.echo("...")
            if non_graphical:
                typer.echo("Starting in non-graphical mode...")

        from ansys.aedt.core import settings
        from ansys.aedt.core.desktop import Desktop

        settings.enable_logger = False

        args = {
            "version": version,
            "non_graphical": non_graphical,
            "new_desktop": True,
            "close_on_exit": False,
        }
        if port > 0:
            args["port"] = port
            if not common.json_mode:
                typer.echo("Using port: ", nl=False)
                typer.secho(f"{port}", fg="cyan")

        progress_running = True

        if not common.json_mode:
            progress_chars = ["|", "/", "-", "\\"]

            def show_progress() -> None:
                i = 0
                while progress_running:
                    sys.stdout.write(f"\r{progress_chars[i % len(progress_chars)]} Initializing AEDT...")
                    sys.stdout.flush()
                    time.sleep(0.2)
                    i += 1
                sys.stdout.write("\r" + " " * 50 + "\r")
                sys.stdout.flush()

            progress_thread = threading.Thread(target=show_progress, daemon=True)
            progress_thread.start()

        d = Desktop(**args)
        progress_running = False

        data = {
            "port": int(d.port) if isinstance(d.port, (int, float)) else 0,
            "version": version,
            "non_graphical": non_graphical,
        }
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"AEDT started successfully on port {d.port}", fg="green")
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error starting AEDT: {str(e)}", fg="red")
        raise typer.Exit(code=1)


@session_app.command("list")
def list_sessions() -> None:
    """List all running AEDT instances."""
    try:
        aedt_sessions = _discover_aedt_sessions()

        if common.json_mode:
            procs_data = []
            for session in aedt_sessions:
                procs_data.append(
                    {
                        "pid": session["pid"],
                        "port": session["port"],
                        "mode": session["mode"],
                        "version": session["version"],
                        "non_graphical": session["non_graphical"],
                        "student_version": bool(session.get("student_version", False)),
                    }
                )
            common.print_output(data={"processes": procs_data, "count": len(procs_data)})
            return

        if not aedt_sessions:
            typer.secho("No AEDT processes currently running.", fg="yellow")
            return

        typer.echo("Found ", nl=False)
        typer.secho(f"{len(aedt_sessions)}", fg="green", nl=False)
        typer.echo(" AEDT instance(s):")
        typer.echo("-" * 60)

        for session in aedt_sessions:
            port = session["port"]
            version = session["version"]
            edition = session.get("student_version", False)
            non_graphical = session.get("non_graphical")
            typer.echo("  PID: ", nl=False)
            typer.secho(f"{session['pid']}", fg="cyan", nl=False)
            typer.echo(" | Version: ", nl=False)
            typer.secho(f"{version}", fg="blue", nl=False)
            if edition:
                typer.echo(" | Edition: ", nl=False)
                typer.secho("Student" if edition else "Standard", fg="magenta", nl=False)
            typer.echo(" | Mode: ", nl=False)
            typer.secho("COM" if session["mode"] == "com" else "gRPC", fg="yellow", nl=False)
            typer.echo(" | UI: ", nl=False)
            if non_graphical is None:
                typer.secho("Unknown", fg="white", nl=False)
            else:
                typer.secho("Non-graphical" if non_graphical else "Graphical", fg="white", nl=False)
            typer.echo(" | Port: ", nl=False)
            if port is not None:
                typer.secho(f"{port}", fg="green")
            else:
                typer.secho("COM mode", fg="yellow")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@session_app.command("stop")
def stop(
    port: int | None = typer.Option(None, "--port", help="Port of the AEDT instance to stop"),
    stop_all: bool = typer.Option(False, "--all", help="Stop all running AEDT instances"),
) -> None:
    """Stop an AEDT instance by port or stop all running instances."""
    try:
        aedt_sessions = _discover_aedt_sessions()
        if stop_all:
            stopped_pids = []
            skipped_pids = []
            for session in aedt_sessions:
                try:
                    psutil.Process(int(session["pid"])).kill()
                    stopped_pids.append(int(session["pid"]))
                except psutil.NoSuchProcess:
                    continue
                except psutil.AccessDenied:
                    skipped_pids.append(int(session["pid"]))
            if common.json_mode:
                common.print_output(data={"stopped": True, "all": True, "pids": stopped_pids, "skipped": skipped_pids})
            else:
                if skipped_pids:
                    typer.secho("Some AEDT processes could not be stopped.", fg="yellow")
                else:
                    typer.secho("All AEDT processes stopped.", fg="green")
            return

        if port is None:
            message = "Either --port or --all must be provided."
            if common.json_mode:
                common.print_output(error=message)
            else:
                typer.secho(message, fg="red")
            raise typer.Exit(code=1)

        target_session = next((session for session in aedt_sessions if session["port"] == port), None)

        if target_session is None:
            if common.json_mode:
                common.print_output(error=f"No AEDT process found on port {port}.")
            else:
                typer.secho(f"No AEDT process found on port {port}.", fg="red")
            raise typer.Exit(code=1)

        pid = int(target_session["pid"])
        try:
            psutil.Process(pid).kill()
        except psutil.AccessDenied:
            if common.json_mode:
                common.print_output(error=f"Access denied for process PID {pid}.")
            else:
                typer.secho(f"Access denied for process PID {pid}.", fg="red")
            raise typer.Exit(code=1)
        except psutil.NoSuchProcess:
            if common.json_mode:
                common.print_output(error=f"AEDT process PID {pid} is no longer running.")
            else:
                typer.secho(f"AEDT process PID {pid} is no longer running.", fg="red")
            raise typer.Exit(code=1)

        if common.json_mode:
            common.print_output(data={"stopped": True, "pid": pid, "port": port})
        else:
            typer.secho(f"AEDT process (PID {pid}, port {port}) stopped.", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@session_app.command("attach")
def attach(
    port: int = typer.Option(None, "--port", help="gRPC port to attach to"),
    project: str = typer.Option(None, "--project", help="Project to activate in the console session"),
    design: str = typer.Option(None, "--design", help="Design to set as active in the console"),
) -> None:
    """
    Attach to a running AEDT instance and open an interactive PyAEDT console.

    If --port is not given, lists available instances for interactive selection.
    """
    try:
        aedt_sessions = _discover_aedt_sessions()

        if not aedt_sessions:
            if common.json_mode:
                common.print_output(error="No AEDT processes currently running.")
                raise typer.Exit(code=1)
            typer.secho("No AEDT processes currently running.", fg="yellow")
            typer.echo("Start AEDT first using: ", nl=False)
            typer.secho("pyaedt session start", fg="cyan")
            return

        if port is not None:
            target_session = next((session for session in aedt_sessions if session["port"] == port), None)

            if target_session is None:
                if common.json_mode:
                    common.print_output(error=f"No AEDT process found on port {port}.")
                    raise typer.Exit(code=1)
                typer.secho(f"No AEDT process found on port {port}.", fg="red")
                typer.echo("Available AEDT instances:")
                for session in aedt_sessions:
                    session_port = session["port"]
                    typer.echo(f"  PID: {session['pid']}, Port: {session_port or 'COM mode'}")
                return

            version = str(target_session["version"])
            if not common.json_mode:
                typer.echo("Attaching to process ", nl=False)
                typer.secho(f"{target_session['pid']}", fg="cyan", nl=False)
                typer.echo(f" (port {port})...")
            _activate_console_context(port=port, project=project, design=design)
            _launch_console(int(target_session["pid"]), version, design)
        else:
            _attach_interactive(aedt_sessions, project, design)
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


def _attach_interactive(aedt_sessions: list[dict[str, object]], project: str | None, design: str | None) -> None:
    """
    Interactive mode to select and attach to an AEDT process.

    Parameters
    ----------
    aedt_sessions : list[dict[str, object]]
        List of available AEDT processes
    project : str or None
        Project name to activate, or None
    design : str or None
        Design name to set active, or None

    """
    typer.echo("Found ", nl=False)
    typer.secho(f"{len(aedt_sessions)}", fg="green", nl=False)
    typer.echo(" AEDT instance(s):\n")

    process_info = []
    for idx, session in enumerate(aedt_sessions, 1):
        port = session["port"]
        version = session["version"]
        process_info.append({"idx": idx, "pid": session["pid"], "port": port, "version": version})

        typer.secho(f"  {idx}", fg="yellow", nl=False)
        typer.echo(". PID: ", nl=False)
        typer.secho(f"{session['pid']}", fg="cyan", nl=False)
        typer.echo(" | Version: ", nl=False)
        typer.secho(f"{version}", fg="blue", nl=False)
        typer.echo(" | Port: ", nl=False)
        if port is not None:
            typer.secho(f"{port}", fg="green")
        else:
            typer.secho("COM mode", fg="yellow")

    typer.echo("")
    choice_idx = None
    while choice_idx is None:
        typer.echo("Select instance (1-", nl=False)
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
                typer.secho(f"Invalid selection. Please enter a number between 1 and {len(process_info)}.", fg="red")
                choice_idx = None
        except ValueError:
            typer.secho("Invalid input. Please enter a number.", fg="red")

    selected = process_info[choice_idx - 1]
    typer.echo("\nAttaching to process ", nl=False)
    typer.secho(f"{selected['pid']}", fg="cyan", nl=False)
    typer.echo("...")
    _activate_console_context(port=selected["port"], project=project, design=design)
    _launch_console(selected["pid"], selected["version"], design)


def _activate_console_context(port: int | None, project: str | None = None, design: str | None = None) -> None:
    """Activate the requested project and design before launching the console."""
    if not project and not design:
        return
    if port is None:
        raise RuntimeError("Using --project or --design with session attach requires a gRPC-enabled AEDT instance.")

    desktop = common.get_desktop(port=port)
    if design:
        common.resolve_project_and_design(desktop, project_name=project, design_name=design)
    else:
        common.resolve_project(desktop, project_name=project)


def _launch_console(pid: int, version: str, design: str | None = None) -> None:
    """
    Launch an interactive PyAEDT console attached to an AEDT process.

    Parameters
    ----------
    pid : int
        Process ID of the AEDT instance
    version : str
        AEDT version string
    design : str or None
        Design name to set as active, or None

    """
    from pathlib import Path
    import subprocess  # nosec B404 - subprocess needed for launching interactive console

    env = os.environ.copy()
    env["PYAEDT_PROCESS_ID"] = str(pid)
    if version and version != "unknown":
        env["PYAEDT_DESKTOP_VERSION"] = version
    else:
        env.pop("PYAEDT_DESKTOP_VERSION", None)
    if design:
        env["PYAEDT_DESIGN"] = design

    try:
        import ansys.aedt.core

        package_dir = Path(ansys.aedt.core.__file__).parent
        console_setup_path = package_dir / "extensions" / "installer" / "console_setup.py"

        if not console_setup_path.exists():
            typer.secho(f"Error: console_setup.py not found at {console_setup_path}", fg="red")
            return
    except Exception as e:
        typer.secho(f"Error locating console_setup.py: {str(e)}", fg="red")
        return

    import importlib.util

    python_exe = sys.executable
    typer.echo("")

    use_ipython = importlib.util.find_spec("IPython") is not None
    if not use_ipython:  # pragma: no cover
        typer.secho("IPython not found — falling back to standard Python interactive console.", fg="yellow")
        typer.echo("For a richer experience, install it with: ", nl=False)
        typer.secho("pip install ipython", fg="cyan")

    cmd = (
        [python_exe, "-m", "IPython", "-i", str(console_setup_path)]
        if use_ipython
        else [python_exe, "-i", str(console_setup_path)]
    )

    try:  # pragma: no cover
        subprocess.run(  # nosec B603 - trusted paths from sys.executable and package location
            cmd, env=env, check=False
        )
    except KeyboardInterrupt:  # pragma: no cover
        typer.echo("\n\nInterrupted.")
    except Exception as e:  # pragma: no cover
        typer.secho(f"Error launching console: {str(e)}", fg="red")
