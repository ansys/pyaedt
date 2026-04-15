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

"""Project and design management commands."""

from __future__ import annotations

from enum import Enum

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

project_app = typer.Typer(help="Project and design management commands")


class AEDTAppType(str, Enum):
    Hfss = "Hfss"
    Maxwell2d = "Maxwell2d"
    Maxwell3d = "Maxwell3d"
    Q3d = "Q3d"
    Q2d = "Q2d"
    Icepak = "Icepak"
    Circuit = "Circuit"
    TwinBuilder = "TwinBuilder"
    Mechanical = "Mechanical"
    Emit = "Emit"
    Rmxprt = "Rmxprt"
    Hfss3dLayout = "Hfss3dLayout"
    MaxwellCircuit = "MaxwellCircuit"


@project_app.command(name="list")
def list_projects(
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
) -> None:
    """List open projects together with their designs."""
    try:
        d = common.get_desktop(port=port)
        projects = common.list_projects_with_designs(d.odesktop)
        data = {"projects": projects, "count": len(projects)}
        if common.json_mode:
            common.print_output(data=data)
        else:
            if not projects:
                typer.secho("No projects open.", fg="yellow")
                return
            typer.secho(f"{len(projects)} project(s):", fg="green")
            for project in projects:
                typer.echo(f"  - {project['name']}")
                if project["designs"]:
                    for design in project["designs"]:
                        typer.echo(f"      - {design['name']} ({design['type']})")
                else:
                    typer.echo("      - (no designs)")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="open")
def open_project(
    path: str = typer.Argument(..., help="Path to .aedt project file"),
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
    non_graphical: bool = typer.Option(False, "--non-graphical", "-ng", help="Open in non-graphical mode"),
) -> None:
    """Open an AEDT project file."""
    try:
        d = common.get_desktop(port=port)
        d.odesktop.OpenProject(path)
        proj = d.odesktop.GetActiveProject()
        proj_name = proj.GetName() if proj else "Unknown"
        data = {"project": proj_name, "path": path}
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Opened project '{proj_name}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="save")
def save_project(
    path: str = typer.Option(None, "--path", help="Save-as path ending with .aedt (omit to save in place)"),
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
) -> None:
    """Save the active AEDT project. Use --path for Save As."""
    try:
        d = common.get_desktop(port=port)
        proj = d.odesktop.GetActiveProject()
        if not proj:
            raise RuntimeError("No active project found.")
        if path:
            if not path.lower().endswith(".aedt"):
                raise typer.BadParameter("--path must end with .aedt when provided.")
            proj.SaveAs(path, True)
        else:
            proj.Save()
        data = {"project": proj.GetName(), "saved_as": path}
        if common.json_mode:
            common.print_output(data=data)
        else:
            msg = f"Project '{proj.GetName()}' saved"
            if path:
                msg += f" as '{path}'"
            typer.secho(msg, fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="create")
def create_project(
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
    project: str = typer.Option(None, "--project", help="Project name to create/use"),
    design: str = typer.Option(None, "--design", "-d", help="Design name to create"),
    design_type: AEDTAppType = typer.Option(None, "--type", "-t", help="Design type (required with --design)"),
) -> None:
    """Create a project, or create a design in a specified project."""
    try:
        if not project:
            raise typer.BadParameter("--project is required.")
        if design and not design_type:
            raise typer.BadParameter("--type is required when --design is specified.")
        if design_type and not design:
            raise typer.BadParameter("--design is required when --type is specified.")

        if design:
            import ansys.aedt.core as aedt

            aedt.settings.enable_logger = False
            app_map = {
                "Hfss": aedt.Hfss,
                "Maxwell2d": aedt.Maxwell2d,
                "Maxwell3d": aedt.Maxwell3d,
                "Q3d": aedt.Q3d,
                "Q2d": aedt.Q2d,
                "Icepak": aedt.Icepak,
                "Circuit": aedt.Circuit,
                "TwinBuilder": aedt.TwinBuilder,
                "Mechanical": aedt.Mechanical,
                "Emit": aedt.Emit,
                "Rmxprt": aedt.Rmxprt,
                "Hfss3dLayout": aedt.Hfss3dLayout,
                "MaxwellCircuit": aedt.MaxwellCircuit,
            }
            cls = app_map[design_type.value]
            app_instance = cls(
                port=port,
                project=project,
                design=design,
                new_desktop=False,
                close_on_exit=False,
            )
            data = {
                "project": app_instance.project_name,
                "design": app_instance.design_name,
                "type": design_type.value,
            }
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(
                    f"Created {design_type.value} design '{data['design']}' in project '{data['project']}'",
                    fg="green",
                )
        else:
            d = common.get_desktop(port=port)
            d.odesktop.NewProject()
            proj = d.odesktop.GetActiveProject()
            if proj:
                proj.Rename(project, True)
            proj_name = proj.GetName() if proj else project
            data = {"project": proj_name}
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(f"Created project '{proj_name}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="close")
def close_project(
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
    project: str = typer.Option(None, "--project", help="Project name to close (closes active if omitted)"),
) -> None:
    """Close an AEDT project."""
    try:
        d = common.get_desktop(port=port)
        odesktop = d.odesktop
        if project:
            odesktop.CloseProject(project)
            closed_name = project
        else:
            proj = odesktop.GetActiveProject()
            if not proj:
                raise RuntimeError("No active project to close.")
            closed_name = proj.GetName()
            odesktop.CloseProject(closed_name)

        if common.json_mode:
            common.print_output(data={"closed": closed_name})
        else:
            typer.secho(f"Project '{closed_name}' closed.", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
