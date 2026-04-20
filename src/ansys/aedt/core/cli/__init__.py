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

"""PyAEDT CLI based on typer."""

try:
    import typer
except ImportError as e:  # pragma: no cover
    from ansys.aedt.core.internal.checks import install_message

    msg = install_message("typer", "all")
    raise ImportError(msg) from e

from ansys.aedt.core.cli import common
from ansys.aedt.core.cli.aedt import session_app
from ansys.aedt.core.cli.config import test_config_app
from ansys.aedt.core.cli.doc import doc_app
from ansys.aedt.core.cli.export import export_app
from ansys.aedt.core.cli.panels import panels_app
from ansys.aedt.core.cli.project import project_app
from ansys.aedt.core.cli.script import run_script

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main_callback(
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON (agent-friendly mode)"),
) -> None:
    """CLI for PyAEDT."""
    if json_output:
        common.json_mode = True


@app.command()
def version() -> None:
    """Display PyAEDT version."""
    import ansys.aedt.core

    ver = ansys.aedt.core.__version__
    if common.json_mode:
        common.print_output(data={"version": ver})
    else:
        typer.echo("PyAEDT version: ", nl=False)
        typer.secho(ver, fg="cyan")


@app.command(name="aedt-versions")
def aedt_versions() -> None:
    """List installed AEDT versions on this machine."""
    try:
        from ansys.aedt.core.internal.aedt_versions import aedt_versions as _aedt_versions

        versions = _aedt_versions.installed_versions
        data = {"versions": {k: str(v) for k, v in versions.items()}, "count": len(versions)}
        if common.json_mode:
            common.print_output(data=data)
        else:
            if not versions:
                typer.secho("No AEDT versions found.", fg="yellow")
                return
            typer.secho(f"Found {len(versions)} installed version(s):", fg="green")
            for ver, path in versions.items():
                typer.echo(f"  {ver}: {path}")
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


app.command(name="run")(run_script)


# Sub-apps
app.add_typer(session_app, name="session")
app.add_typer(project_app, name="project")
app.add_typer(export_app, name="export")
app.add_typer(panels_app, name="panels")
app.add_typer(doc_app, name="doc")
app.add_typer(test_config_app, name="test-config")

if __name__ == "__main__":
    app()
