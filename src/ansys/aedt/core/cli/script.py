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

import os
from pathlib import Path
import subprocess  # nosec
import sys

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common


def run_script(
    script_path: str = typer.Argument(..., help="Path to .py script file"),
    port: int | None = typer.Option(None, "--port", help="gRPC port of the AEDT instance"),
    ironpython: bool = typer.Option(False, "--ironpython", help="Run an Ironpython script"),
) -> None:
    """
    Execute a Python script file in a subprocess.

    The current environment variables are copied into the child process.
    """
    try:
        path = Path(script_path)
        if not path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        script_path_resolved = str(path.resolve())

        if ironpython:
            if not port:
                data = {"executed": False, "script": script_path_resolved}
                raise RuntimeError("No port provided")

            d = common.get_desktop(port=port)
            d.odesktop.RunScript(script_path_resolved)
            data = {"executed": True, "script": script_path_resolved}
        else:
            env = os.environ.copy()

            result = subprocess.run(
                [sys.executable, script_path_resolved],
                env=env,
                capture_output=common.json_mode,
                text=True,
            )  # nosec

            if result.returncode != 0:
                stderr_output = result.stderr if common.json_mode else ""
                raise RuntimeError(
                    f"Script exited with code {result.returncode}" + (f": {stderr_output}" if stderr_output else "")
                )

            data = {"executed": True, "script": script_path_resolved}
            if common.json_mode and result.stdout:
                data["stdout"] = result.stdout

        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Script executed: {path.name}", fg="green")
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
