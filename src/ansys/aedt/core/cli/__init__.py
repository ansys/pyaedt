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
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli.config import config_app
from ansys.aedt.core.cli.doc import doc_app
from ansys.aedt.core.cli.panels import panels_app
from ansys.aedt.core.cli.process import processes
from ansys.aedt.core.cli.process import start
from ansys.aedt.core.cli.process import stop
from ansys.aedt.core.cli.process import version

app = typer.Typer(help="CLI for PyAEDT", no_args_is_help=True)

# Register sub-apps
app.add_typer(config_app, name="config")
app.add_typer(panels_app, name="panels")
app.add_typer(doc_app, name="doc")

# Register top-level commands
app.command()(version)
app.command()(processes)
app.command()(start)
app.command()(stop)

if __name__ == "__main__":
    app()
