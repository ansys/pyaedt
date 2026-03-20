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

"""Utility commands."""

from __future__ import annotations

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

utility_app = typer.Typer(help="Utility commands")


@utility_app.command("clear")
def clear(
    close_projects: bool = typer.Option(True, "--close-projects/--no-close-projects", help="Close all projects"),
    port: int = typer.Option(None, "--port", help="Override port to target a specific AEDT instance"),
) -> None:
    """Close all projects and clear AEDT messages."""
    try:
        d = common._get_desktop(port=port)
        if close_projects:
            projects = list(d.odesktop.GetProjectList())
            for proj_name in projects:
                d.odesktop.CloseProject(proj_name)
        d.odesktop.ClearMessages("", "", 3)
        data = {"cleared": True, "projects_closed": close_projects}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho("AEDT cleared.", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@utility_app.command("model-info")
def model_info(
    design_name: str = typer.Option(None, "--design", "-d", help="Design to query (uses active if omitted)"),
    port: int = typer.Option(None, "--port", help="Override port to target a specific AEDT instance"),
) -> None:
    """Get design name, type, and project path."""
    try:
        import ansys.aedt.core as aedt

        session = common._load_session()
        if session is None:
            if common._json_mode:
                common._output(error="No active session.")
            else:
                typer.secho("No active session. Run 'pyaedt connect' first.", fg="red")
            raise typer.Exit(code=1)

        if port is not None:
            session["port"] = port
        aedt.settings.enable_logger = False
        app = aedt.get_pyaedt_app(
            version=session["version"],
            port=session["port"],
            machine=session.get("machine", "localhost"),
            new_desktop=False,
            close_on_exit=False,
            design=design_name,
        )
        data = {
            "design_name": app.design_name,
            "design_type": app.design_type,
            "project_name": app.project_name,
            "project_path": app.project_path,
        }
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho("Model Info:", fg="bright_blue", bold=True)
            typer.echo(f"  Design: {data['design_name']}")
            typer.echo(f"  Type: {data['design_type']}")
            typer.echo(f"  Project: {data['project_name']}")
            typer.echo(f"  Path: {data['project_path']}")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
