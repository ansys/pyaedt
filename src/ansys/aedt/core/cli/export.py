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

import json
import os
import tempfile

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

export_app = typer.Typer(help="Export commands")


@export_app.command("screenshot")
def screenshot(
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
    path: str = typer.Option("screenshot.jpg", "--path", "-o", help="Output file path"),
    project: str = typer.Option(None, "--project", help="Project containing the design to capture"),
    design: str = typer.Option(None, "--design", "-d", help="Design to capture"),
) -> None:
    """Capture a screenshot of the AEDT design view."""
    try:
        _, app, context = common.get_design_app(port=port, project_name=project, design_name=design)
        try:
            app.export_design_preview_to_jpg(path)
        except Exception as export_error:
            raise RuntimeError(
                f"Failed to export screenshot: {export_error}. Try saving the project first before exporting an image."
            ) from export_error
        data = {"screenshot": path, "design": app.design_name, "project": context["project"]}
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Screenshot saved to '{path}'", fg="green")
            typer.echo(f"  Design: {app.design_name}")
            typer.echo(f"  Project: {context['project']}")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@export_app.command("config")
def export_config(
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
    output: str = typer.Option(None, "--output", "-o", help="Output JSON file path (prints to terminal if omitted)"),
    project: str = typer.Option(None, "--project", help="Project containing the design to export"),
    design: str = typer.Option(None, "--design", "-d", help="Design to export config from"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing config file"),
) -> None:
    """Export design configuration (parameters, setup, etc.) as JSON."""
    try:
        temp_config_file = None
        _, app, context = common.get_design_app(port=port, project_name=project, design_name=design)
        if output:
            config_target = output if output.lower().endswith(".json") else f"{output}.json"
        else:
            fd, config_target = tempfile.mkstemp(suffix=".json")
            os.close(fd)
            os.remove(config_target)
            temp_config_file = config_target

        config_file = app.configurations.export_config(config_file=config_target, overwrite=overwrite)
        if not config_file:
            raise RuntimeError("Failed to export configuration.")

        with open(config_file, "r", encoding="utf-8") as f:
            config_content = json.load(f)

        data = {"config": config_content, "design": app.design_name, "project": context["project"]}
        if output:
            data["config_file"] = config_file

        if common.json_mode:
            common.print_output(data=data)
        else:
            if output:
                typer.secho(f"Configuration exported to '{config_file}'", fg="green")
                typer.echo(f"  Design: {app.design_name}")
                typer.echo(f"  Project: {context['project']}")
            else:
                typer.echo(json.dumps(config_content, indent=2))
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
    finally:
        if temp_config_file and os.path.exists(temp_config_file):
            os.remove(temp_config_file)
