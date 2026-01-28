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

"""CLI command to check if changes are only docstrings/comments."""

import ast
from pathlib import Path
import subprocess
import sys

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )


def get_ast_dump(source_code, filename="<unknown>"):
    """
    Parse source code into an AST, remove docstrings, and return string dump.

    Parameters
    ----------
    source_code : str
        The Python source code to parse.
    filename : str, optional
        The filename for error reporting. The default is ``"<unknown>"``.

    Returns
    -------
    str
        AST dump as a string, or ``"SYNTAX_ERROR"`` if parsing fails.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        typer.echo(f"[WARN] Syntax Error parsing {filename}. Assuming logic change.", err=True)
        return "SYNTAX_ERROR"

    class DocstringRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)

        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)

        def visit_ClassDef(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)

        def visit_Module(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)

        def _remove_docstring(self, node):
            """Remove docstring from a node if it exists."""
            if not node.body:
                return node

            first_stmt = node.body[0]
            if not isinstance(first_stmt, ast.Expr):
                return node

            value = first_stmt.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                node.body = node.body[1:]
            elif isinstance(value, ast.Str):
                node.body = node.body[1:]

            return node

    tree = DocstringRemover().visit(tree)
    return ast.dump(tree, include_attributes=False)


def get_changed_files(base_ref: str = "HEAD"):
    """
    Get list of changed Python files from git.

    Parameters
    ----------
    base_ref : str, optional
        The git reference to compare against. The default is ``"HEAD"``.

    Returns
    -------
    list
        List of changed Python file paths.
    """
    try:
        # Get list of changed files compared to base_ref
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip().endswith(".py")]
        return files
    except subprocess.CalledProcessError as e:
        typer.echo(f"[ERR] Failed to get changed files from git: {e}", err=True)
        raise typer.Exit(code=1)


def check_docstrings(
    base_ref: str = typer.Option("HEAD", "--base", "-b", help="Git reference to compare against (e.g., HEAD, main)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Save AST dumps for debugging"),
):
    """
    Check if Python file changes are logic changes or just docstrings/comments.

    This command automatically detects changed Python files using git and analyzes
    whether the changes affect code logic or are limited to docstrings, comments,
    and formatting.

    Examples
    --------
    >>> pyaedt check-docstrings
    >>> pyaedt check-docstrings --base main
    >>> pyaedt check-docstrings --verbose --debug
    """
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    files = get_changed_files(base_ref)

    if not files:
        typer.echo("No Python files changed.")
        raise typer.Exit(code=0)

    logic_changed = False

    typer.echo(f"Checking {len(files)} file(s)...")
    if verbose:
        typer.echo("Verbose mode: ON")
        typer.echo(f"Debug mode: {'ON' if debug else 'OFF'}")

    for filename in files:
        git_path = filename.replace("\\", "/")

        if verbose:
            typer.echo(f"\nProcessing: {filename}")

        try:
            old_code = subprocess.check_output(
                ["git", "show", f"{base_ref}:{git_path}"],
                stderr=subprocess.DEVNULL,
                encoding="utf-8",
                errors="replace",
            )
            if verbose:
                typer.echo(f"  Retrieved {base_ref} version ({len(old_code)} chars)")
        except subprocess.CalledProcessError:
            if Path(filename).exists():
                typer.echo(f"[NEW] New file detected: {filename}")
            else:
                typer.echo(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            typer.echo(f"[ERR] Could not decode {base_ref} version of {filename}", err=True)
            logic_changed = True
            continue

        try:
            with open(filename, "r", encoding="utf-8", errors="replace") as f:
                new_code = f.read()
            if verbose:
                typer.echo(f"  Retrieved working version ({len(new_code)} chars)")
        except FileNotFoundError:
            typer.echo(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            typer.echo(f"[ERR] Could not decode local version of {filename}", err=True)
            logic_changed = True
            continue
        except Exception as e:
            typer.echo(f"[ERR] Error reading {filename}: {e}", err=True)
            logic_changed = True
            continue

        old_ast = get_ast_dump(old_code, f"{base_ref}:{filename}")
        new_ast = get_ast_dump(new_code, filename)

        if old_ast == "SYNTAX_ERROR" or new_ast == "SYNTAX_ERROR":
            typer.echo(f"[ERR] Syntax Error detected in: {filename}", err=True)
            logic_changed = True
            continue

        if debug:
            debug_dir = Path.cwd() / ".ast_debug"
            debug_dir.mkdir(exist_ok=True)

            safe_name = filename.replace("\\", "_").replace("/", "_").replace(":", "")
            old_ast_file = debug_dir / f"{safe_name}.old.ast"
            new_ast_file = debug_dir / f"{safe_name}.new.ast"

            old_ast_file.write_text(old_ast, encoding="utf-8")
            new_ast_file.write_text(new_ast, encoding="utf-8")

            if verbose:
                typer.echo(f"  Saved AST dumps to {debug_dir}")

        if old_ast != new_ast:
            typer.echo(f"[MOD] Logic change detected in: {filename}")
            if verbose:
                if len(old_ast) != len(new_ast):
                    typer.echo(f"  AST size: {len(old_ast)} -> {len(new_ast)} chars")
            logic_changed = True
        else:
            typer.echo(f"[OK]  Docstring/Comment/Style only: {filename}")
            if verbose:
                typer.echo(f"  AST unchanged (both {len(old_ast)} chars)")

    typer.echo("-" * 40)
    if logic_changed:
        typer.echo("[!] COMMIT CONTAINS LOGIC CHANGES")
    else:
        typer.echo("[OK] ONLY DOCSTRINGS/COMMENTS! (Tests could be skipped)")
    typer.echo("-" * 40)

    raise typer.Exit(code=0)
