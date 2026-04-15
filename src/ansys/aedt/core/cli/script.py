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

from contextlib import nullcontext
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO
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
    port: int = typer.Option(..., "--port", help="gRPC port of the AEDT instance"),
) -> None:
    """Execute a Python script file inside AEDT.

    The desktop is kept alive after execution and verbose logging is enabled.
    """
    try:
        path = Path(script_path)
        if not path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        from ansys.aedt.core import settings

        settings.enable_logger = True

        d = common.get_desktop(port=port)
        script_globals = {"__file__": str(path.resolve()), "desktop": d}
        stream = StringIO()
        stdout_context = redirect_stdout(stream) if common.json_mode else nullcontext()
        stderr_context = redirect_stderr(stream) if common.json_mode else nullcontext()
        with stdout_context, stderr_context:
            exec(compile(path.read_text(encoding="utf-8"), str(path.resolve()), "exec"), script_globals)  # noqa: S102
        data = {"executed": True, "script": str(path.resolve())}
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
