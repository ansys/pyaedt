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

from typing import List

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

doc_app = typer.Typer(help="Documentation commands", no_args_is_help=False)


@doc_app.callback(invoke_without_command=True)
def doc_callback(ctx: typer.Context):
    """Open the home page and display help when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        from ansys.aedt.core.help import online_help

        online_help.silent = False
        online_help.home()

        # Display help in terminal
        typer.echo(ctx.get_help())


@doc_app.command(name="examples", help="Open the online Examples section of the PyAEDT documentation")
def examples():
    """Open Examples url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.examples()


@doc_app.command(name="github", help="Open PyAEDT repository on GitHub")
def github():
    """Open Github url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.github()


@doc_app.command(name="user-guide", help="Open the online user guide section of the PyAEDT documentation")
def user_guide():
    """Open User guide url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.user_guide()


@doc_app.command(name="getting-started", help="Open the online getting started section of the PyAEDT documentation")
def getting_started():
    """Open Getting started url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.getting_started()


@doc_app.command(name="installation", help="Open the online installation section of the PyAEDT documentation")
def installation():
    """Open installation url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.installation_guide()


@doc_app.command(name="api", help="Open the online API reference section of the PyAEDT documentation")
def api():
    """Open api reference url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.api_reference()


@doc_app.command(name="changelog", help="Open the PyAEDT changelog")
def changelog(pyaedt_version: str = typer.Argument(None)):
    """Open API reference changelog."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.changelog(pyaedt_version)


@doc_app.command(name="issues", help="Open the PyAEDT issues")
def issues():
    """Open api reference url."""
    from ansys.aedt.core.help import online_help

    online_help.silent = False
    online_help.issues()


@doc_app.command(name="search", help="One or more search keywords for the documentation")
def search(search_keys: List[str] = typer.Argument(None)):
    """Search the online documentation."""
    if not search_keys:
        typer.secho("✗ Error: Please provide at least one search keyword", fg=typer.colors.RED)
        typer.secho("Usage: pyaedt doc search <keyword1> [keyword2] ...", fg=typer.colors.YELLOW)
        raise typer.Exit(1)

    from ansys.aedt.core.help import online_help

    online_help.silent = False

    query = " ".join(search_keys)
    online_help.search(query)
