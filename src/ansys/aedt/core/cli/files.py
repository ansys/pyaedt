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

"""File management commands."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common

file_app = typer.Typer(help="File management commands")


@file_app.command("list")
def list_files(
    directory: str = typer.Option(None, "--dir", "-d", help="Directory to list (defaults to temp)"),
    pattern: str = typer.Option("*", "--pattern", "-p", help="Glob pattern for filtering"),
) -> None:
    """List files in a directory."""
    try:
        dir_path = Path(directory) if directory else Path(tempfile.gettempdir())
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        entries = []
        for entry in sorted(dir_path.glob(pattern)):
            stat = entry.stat()
            entries.append(
                {
                    "name": entry.name,
                    "path": str(entry),
                    "size": stat.st_size,
                    "is_directory": entry.is_dir(),
                }
            )
        data = {"directory": str(dir_path), "files": entries, "count": len(entries)}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Files in '{dir_path}' ({len(entries)}):", fg="green")
            for e in entries:
                kind = "DIR " if e["is_directory"] else "FILE"
                typer.echo(f"  [{kind}] {e['name']} ({e['size']} bytes)")
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@file_app.command("upload")
def upload(
    local_path: str = typer.Argument(..., help="Source file path"),
    to: str = typer.Option(None, "--to", help="Destination path (defaults to temp dir)"),
) -> None:
    """Copy a file to the AEDT working directory."""
    try:
        src = Path(local_path)
        if not src.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        dest_dir = Path(to) if to else Path(tempfile.gettempdir())
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(str(src), str(dest))
        data = {"uploaded": True, "source": str(src), "destination": str(dest)}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Uploaded '{src.name}' to '{dest}'", fg="green")
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


@file_app.command("download")
def download(
    remote_path: str = typer.Argument(..., help="Source file on AEDT machine"),
    to: str = typer.Option(None, "--to", help="Local destination (defaults to CWD)"),
) -> None:
    """Copy a file from the AEDT working directory."""
    try:
        src = Path(remote_path)
        if not src.exists():
            raise FileNotFoundError(f"File not found: {remote_path}")
        dest_dir = Path(to) if to else Path.cwd()
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(str(src), str(dest))
        data = {"downloaded": True, "source": str(src), "destination": str(dest)}
        if common._json_mode:
            common._output(data=data)
        else:
            typer.secho(f"Downloaded '{src.name}' to '{dest}'", fg="green")
    except Exception as e:
        if common._json_mode:
            common._output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)
