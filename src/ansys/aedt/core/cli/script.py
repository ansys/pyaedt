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

"""Script execution commands."""

from __future__ import annotations

from pathlib import Path

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

script_app = typer.Typer(help="Script execution commands")


@script_app.command("run")
def run_script(
    script_path: str = typer.Argument(..., help="Path to .py script file"),
) -> None:
    """Execute a Python script file inside AEDT."""
    try:
        path = Path(script_path)
        if not path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        d = common._get_desktop()
        d.odesktop.RunScript(str(path.resolve()))
        data = {"executed": True, "script": str(path.resolve())}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Script executed: {path.name}", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@script_app.command("code")
def run_code(
    code: str = typer.Argument(..., help="Python code to execute"),
) -> None:
    """Execute inline Python code with access to the AEDT desktop object."""
    try:
        d = common._get_desktop()
        namespace = {"desktop": d, "odesktop": d.odesktop, "result": None}
        exec(code, namespace)  # nosec B102 - user-provided code execution is the intended feature
        result_val = namespace.get("result")
        data = {"executed": True, "result": str(result_val) if result_val is not None else None}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho("Code executed.", fg="green")
            if result_val is not None:
                typer.echo(f"Result: {result_val}")
    except typer.Exit:
        raise
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
