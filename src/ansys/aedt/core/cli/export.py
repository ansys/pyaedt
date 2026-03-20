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

"""Export commands."""

from __future__ import annotations

from enum import Enum

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

export_app = typer.Typer(help="Export commands")


class ExportFormat(str, Enum):
    step = "step"
    iges = "iges"
    sat = "sat"
    stl = "stl"


@export_app.command("screenshot")
def screenshot(
    output: str = typer.Option("screenshot.jpg", "--output", "-o", help="Output file path"),
    design_name: str = typer.Option(None, "--design", "-d", help="Design to capture"),
) -> None:
    """Capture a screenshot of the AEDT design view."""
    try:
        import ansys.aedt.core as aedt

        session = common._load_session()
        if session is None:
            if common._json_mode:
                common._output(error="No active session.")
            else:
                typer.secho("No active session.", fg="red")
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
        app.export_design_preview_to_jpg(output)
        data = {"screenshot": output, "design": app.design_name}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Screenshot saved to '{output}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@export_app.command("touchstone")
def export_touchstone(
    output_path: str = typer.Argument(..., help="Output file path (e.g. results.s2p)"),
    setup_name: str = typer.Option(None, "--setup", "-s", help="Setup to export"),
    sweep_name: str = typer.Option(None, "--sweep", help="Sweep name"),
    design_name: str = typer.Option(None, "--design", "-d", help="Design to export from"),
) -> None:
    """Export S-parameters to Touchstone format."""
    try:
        import ansys.aedt.core as aedt

        session = common._load_session()
        if session is None:
            if common._json_mode:
                common._output(error="No active session.")
            else:
                typer.secho("No active session.", fg="red")
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
        kwargs = {"output_file": output_path}
        if setup_name:
            kwargs["setup"] = setup_name
        if sweep_name:
            kwargs["sweep"] = sweep_name
        app.export_touchstone(**kwargs)
        data = {"exported": True, "path": output_path, "setup": setup_name}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Touchstone exported to '{output_path}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@export_app.command("3d")
def export_3d(
    output_path: str = typer.Argument(..., help="Output file path"),
    export_format: ExportFormat = typer.Option("step", "--format", "-f", help="Export format"),
    design_name: str = typer.Option(None, "--design", "-d", help="Design to export"),
) -> None:
    """Export 3D geometry in CAD formats."""
    try:
        import ansys.aedt.core as aedt

        session = common._load_session()
        if session is None:
            if common._json_mode:
                common._output(error="No active session.")
            else:
                typer.secho("No active session.", fg="red")
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
        app.modeler.export_3d_model(
            file_name=output_path,
            file_format=f".{export_format.value}",
        )
        data = {"exported": True, "path": output_path, "format": export_format.value}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"3D model exported to '{output_path}'", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
