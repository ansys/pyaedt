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

"""AEDT connection and status commands."""

from __future__ import annotations

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

session_app = typer.Typer(help="Session management commands")


@session_app.command("connect")
def connect(
    port: int = typer.Option(50051, "--port", "-p", help="gRPC port"),
    machine: str = typer.Option("localhost", "--machine", "-m", help="Hostname or IP"),
    version: str = typer.Option(None, "--version", "-v", help="AEDT version (e.g. 2026.1)"),
    non_graphical: bool = typer.Option(False, "--non-graphical", "-ng", help="Non-graphical mode"),
) -> None:
    """Connect to a running AEDT instance via gRPC."""
    try:
        from ansys.aedt.core import settings
        from ansys.aedt.core.desktop import Desktop

        settings.enable_logger = False
        d = Desktop(
            version=version,
            port=port,
            machine=machine,
            non_graphical=non_graphical,
            new_desktop=False,
            close_on_exit=False,
        )
        actual_version = version or str(d.aedt_version_id)
        common._save_session(port=d.port, machine=machine, version=actual_version)
        data = {"port": d.port, "machine": machine, "version": actual_version}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Connected to AEDT {actual_version} on {machine}:{d.port}", fg="green")
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error connecting: {e}", fg="red")
        raise typer.Exit(code=1)


@session_app.command("disconnect")
def disconnect(
    close_projects: bool = typer.Option(False, "--close-projects", help="Close all projects before disconnecting"),
    port: int = typer.Option(None, "--port", help="Override port to target a specific AEDT instance"),
) -> None:
    """Disconnect from AEDT and clear session."""
    try:
        session = common._load_session()
        if session:
            if port is not None:
                session["port"] = port
            try:
                from ansys.aedt.core import settings
                from ansys.aedt.core.desktop import Desktop

                settings.enable_logger = False
                d = Desktop(
                    version=session["version"],
                    port=session["port"],
                    machine=session.get("machine", "localhost"),
                    new_desktop=False,
                    close_on_exit=False,
                )
                d.release_desktop(close_projects=close_projects, close_on_exit=False)
            except Exception:
                pass  # Best-effort disconnect
        common._clear_session()
        if common._json_mode:
            common._output(data={"disconnected": True})
        else:
            typer.secho("Disconnected from AEDT.", fg="green")
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error disconnecting: {e}", fg="red")
        raise typer.Exit(code=1)


@session_app.command("status")
def status(
    port: int = typer.Option(None, "--port", help="Override port to target a specific AEDT instance"),
) -> None:
    """Show AEDT connection status and info."""
    try:
        d = common._get_desktop(port=port)
        odesktop = d.odesktop
        projects = odesktop.GetProjectList()
        active_project = odesktop.GetActiveProject()
        active_project_name = active_project.GetName() if active_project else None

        data = {
            "connected": True,
            "version": str(d.aedt_version_id),
            "port": d.port,
            "process_id": odesktop.GetProcessID(),
            "projects": list(projects),
            "active_project": active_project_name,
        }
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho("AEDT Status:", fg="bright_blue", bold=True)
            typer.echo(f"  Version: {data['version']}")
            typer.echo(f"  Port: {data['port']}")
            typer.echo(f"  PID: {data['process_id']}")
            typer.echo(f"  Projects: {', '.join(data['projects']) or 'None'}")
            typer.echo(f"  Active project: {data['active_project'] or 'None'}")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
