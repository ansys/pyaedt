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
def list_projects() -> None:
    """List all open projects."""
    try:
        d = common._get_desktop()
        projects = list(d.odesktop.GetProjectList())
        data = {"projects": projects, "count": len(projects)}
        if common._json_mode:
            common._output(data=data)
        else:
            if not projects:
                typer.secho("No projects open.", fg="yellow")
                return
            typer.secho(f"{len(projects)} project(s):", fg="green")
            for p in projects:
                typer.echo(f"  - {p}")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="list-designs")
def list_designs(
    project_name: str = typer.Option(None, "--project", "-p", help="Project name (uses active if omitted)"),
) -> None:
    """List all designs in a project."""
    try:
        d = common._get_desktop()
        odesktop = d.odesktop
        if project_name:
            proj = odesktop.SetActiveProject(project_name)
        else:
            proj = odesktop.GetActiveProject()
        if not proj:
            raise RuntimeError("No active project found.")
        designs = []
        for design_name in proj.GetTopDesignList():
            design = proj.SetActiveDesign(design_name)
            design_type = design.GetDesignType()
            designs.append({"name": design_name, "type": design_type})
        data = {"project": proj.GetName(), "designs": designs, "count": len(designs)}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Designs in '{data['project']}':", fg="green")
            for des in designs:
                typer.echo(f"  - {des['name']} ({des['type']})")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="open")
def open_project(
    project_path: str = typer.Argument(..., help="Path to .aedt project file"),
    design_name: str = typer.Option(None, "--design", "-d", help="Design to activate after opening"),
) -> None:
    """Open an AEDT project file."""
    try:
        d = common._get_desktop()
        d.odesktop.OpenProject(project_path)
        proj = d.odesktop.GetActiveProject()
        proj_name = proj.GetName() if proj else "Unknown"
        if design_name and proj:
            proj.SetActiveDesign(design_name)
        data = {"project": proj_name, "path": project_path, "active_design": design_name}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Opened project '{proj_name}'", fg="green")
            if design_name:
                typer.echo(f"  Active design: {design_name}")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="save")
def save_project(
    project_name: str = typer.Option(None, "--project", "-p", help="Project to save (uses active if omitted)"),
    save_as: str = typer.Option(None, "--save-as", help="New file path for Save As"),
) -> None:
    """Save an AEDT project."""
    try:
        d = common._get_desktop()
        odesktop = d.odesktop
        if project_name:
            proj = odesktop.SetActiveProject(project_name)
        else:
            proj = odesktop.GetActiveProject()
        if not proj:
            raise RuntimeError("No active project found.")
        if save_as:
            proj.SaveAs(save_as, True)
        else:
            proj.Save()
        data = {"project": proj.GetName(), "saved_as": save_as}
        if common._json_mode:
            common._output(data=data)
        else:
            msg = f"Project '{proj.GetName()}' saved"
            if save_as:
                msg += f" as '{save_as}'"
            typer.secho(msg, fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="create-design")
def create_design(
    app_type: AEDTAppType = typer.Argument(..., help="Application type"),
    name: str = typer.Option(None, "--name", "-n", help="Design name"),
    project_name: str = typer.Option(None, "--project", "-p", help="Target project"),
    solution_type: str = typer.Option(None, "--solution-type", "-s", help="Solution type"),
) -> None:
    """Create a new design in AEDT."""
    try:
        import ansys.aedt.core as aedt

        session = common._load_session()
        if session is None:
            if common._json_mode:
                common._output(error="No active session. Run 'pyaedt connect' first.")
            else:
                typer.secho("No active session. Run 'pyaedt connect' first.", fg="red")
            raise typer.Exit(code=1)

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
        cls = app_map[app_type.value]
        kwargs = {
            "version": session["version"],
            "port": session["port"],
            "machine": session.get("machine", "localhost"),
            "new_desktop": False,
            "close_on_exit": False,
        }
        if name:
            kwargs["design"] = name
        if project_name:
            kwargs["project"] = project_name
        if solution_type:
            kwargs["solution_type"] = solution_type

        app_instance = cls(**kwargs)
        data = {
            "design": app_instance.design_name,
            "type": app_type.value,
            "project": app_instance.project_name,
            "solution_type": solution_type,
        }
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Created {app_type.value} design '{data['design']}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@project_app.command(name="analyze")
def analyze(
    setup_name: str = typer.Option(None, "--setup", "-s", help="Setup to analyze (all if omitted)"),
    design_name: str = typer.Option(None, "--design", "-d", help="Target design"),
    num_cores: int = typer.Option(None, "--cores", "-c", help="CPU cores to use"),
) -> None:
    """Run simulation analysis on a design."""
    try:
        import ansys.aedt.core as aedt

        session = common._load_session()
        if session is None:
            if common._json_mode:
                common._output(error="No active session.")
            else:
                typer.secho("No active session. Run 'pyaedt connect' first.", fg="red")
            raise typer.Exit(code=1)

        aedt.settings.enable_logger = False
        app = aedt.get_pyaedt_app(
            version=session["version"],
            port=session["port"],
            machine=session.get("machine", "localhost"),
            new_desktop=False,
            close_on_exit=False,
            design=design_name,
        )
        kwargs = {}
        if setup_name:
            kwargs["setup"] = setup_name
        if num_cores:
            kwargs["num_cores"] = num_cores
        app.analyze(**kwargs)
        data = {"analyzed": True, "design": app.design_name, "setup": setup_name or "all"}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Analysis complete for '{app.design_name}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
