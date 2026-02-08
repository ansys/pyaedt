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

"""Script to analyze code changes and determine what jobs should run in CI/CD."""

import argparse
import ast
import os
from pathlib import Path
import re
import shutil
import subprocess  # nosec B404 - validated git calls only
import sys


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
        print(f"[WARN] Syntax Error parsing {filename}. Assuming logic change.", file=sys.stderr)
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
            elif isinstance(value, ast.Constant):
                node.body = node.body[1:]

            return node

    tree = DocstringRemover().visit(tree)
    return ast.dump(tree, include_attributes=False)


def _get_git_executable():
    git_executable = shutil.which("git")
    if not git_executable:
        print("[ERR] Git executable not found in PATH.", file=sys.stderr)
        raise SystemExit(1)
    return git_executable


def _validate_git_ref(ref: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._/\-~^:]+", ref))


def _validate_git_path(path: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._/\-]+", path))


def get_changed_files(base_ref: str = "origin/main"):
    """
    Get list of changed files from git.

    Parameters
    ----------
    base_ref : str, optional
        The git reference to compare against. The default is ``"origin/main"``.

    Returns
    -------
    list
        List of changed file paths.
    """
    try:
        if not _validate_git_ref(base_ref):
            print(f"[ERR] Invalid git reference: {base_ref}", file=sys.stderr)
            raise SystemExit(1)

        git_executable = _get_git_executable()

        # Find merge base if comparing against a branch
        if base_ref not in ["HEAD", "HEAD~1"] and "/" in base_ref:
            try:
                merge_base_result = subprocess.run(  # nosec B603 - controlled git args
                    [git_executable, "merge-base", base_ref, "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                merge_base = merge_base_result.stdout.strip()
                if merge_base:
                    base_ref = merge_base
            except subprocess.CalledProcessError:
                # Fall back to direct comparison if merge-base fails
                pass

        # Get list of changed files compared to base_ref
        result = subprocess.run(  # nosec B603 - controlled git args
            [git_executable, "diff", "--name-only", base_ref, "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        print(f"[ERR] Failed to get changed files from git: {e}", file=sys.stderr)
        raise SystemExit(1)


def _set_ci_env(var_name: str, value: str):
    """Set an environment variable for CI/CD.

    Parameters
    ----------
    var_name : str
        Name of the environment variable.
    value : str
        Value to set.
    """
    os.environ[var_name] = value
    print(f"[CI] Set {var_name}={value}")


def _write_github_output(name: str, value: str):
    """Write output for GitHub Actions.

    Parameters
    ----------
    name : str
        Output name.
    value : str
        Output value.
    """
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
        print(f"[CI] GitHub output: {name}={value}")


def analyze_changes(base_ref: str = "origin/main"):
    """
    Analyze code changes to determine what CI/CD jobs should run.

    This command automatically detects changed files using git and analyzes
    whether the changes affect code logic, are limited to docstrings/comments,
    or only affect documentation. By default, compares current branch against origin/main.

    Exit codes:
    - 0: Success (analysis complete)
    - 1: Error during analysis

    Always runs in CI mode and sets environment variables:
    - SKIP_CODE_TESTS=true (if only docstrings/comments changed)
    - DOC_ONLY=true (if only /doc folder changed)
    - RUN_ALL=true (if code logic or other files changed)

    Also sets module-specific outputs:
    - emit_changed=true/false (if EMIT module changed)
    - extensions_changed=true/false (if extensions module changed)
    - filter_solutions_changed=true/false (if filter solutions module changed)

    Examples
    --------
    >>> python.ci / scripts / analyze_changes.py
    >>> python .ci/scripts/analyze_changes.py --base origin/main
    >>> python .ci/scripts/analyze_changes.py --base HEAD
    """
    if sys.stdout.encoding != "utf-8":
        reconfigure = getattr(sys.stdout, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")

    all_files = get_changed_files(base_ref)

    if not all_files:
        print("No files changed.")
        _set_ci_env("RUN_ALL", "true")
        raise SystemExit(0)

    # Separate Python files and doc files
    python_files = [f for f in all_files if f.endswith(".py") and (f.startswith("tests/") or f.startswith("src/"))]
    doc_files = [f for f in all_files if f.startswith("doc/") or f.startswith("doc\\")]
    other_files = [f for f in all_files if f not in python_files and f not in doc_files]

    # Define module patterns to check for changes
    module_patterns = {
        "emit": [
            "tests/system/emit/",
            "src/ansys/aedt/core/emit_core/",
        ],
        "extensions": [
            "tests/system/extensions/",
            "src/ansys/aedt/core/extensions/",
        ],
        "filter_solutions": [
            "tests/system/filter_solutions/",
            "src/ansys/aedt/core/filtersolutions_core/",
        ],
    }

    # Check for module-specific changes
    print("Checking module-specific:")
    module_changes = {}
    for module_name, patterns in module_patterns.items():
        changed = any(
            any(
                f.replace("\\", "/").startswith(pattern.replace("\\", "/"))
                or f.replace("\\", "/") == pattern.replace("\\", "/")
                for pattern in patterns
            )
            for f in all_files
        )
        module_changes[module_name] = changed
        _write_github_output(f"{module_name}_changed", "true" if changed else "false")
        if changed:
            print(f"[MODULE] {module_name.upper()} module changed")
        else:
            print(f"[MODULE] {module_name.upper()} module NOT changed")

    # Check if ONLY doc files changed
    if doc_files and not python_files and not other_files:
        print(f"Only documentation files changed ({len(doc_files)} file(s)).")
        for f in doc_files:
            print(f"  [DOC] {f}")
        print("-" * 40)
        print("[OK] ONLY DOCUMENTATION CHANGED - Run only doc jobs")
        print("-" * 40)
        _set_ci_env("DOC_ONLY", "true")
        _set_ci_env("SKIP_CODE_TESTS", "true")
        _write_github_output("doc_only", "true")
        _write_github_output("skip_tests", "true")
        raise SystemExit(0)

    if not python_files:
        print("No Python files changed, but non-doc files were modified.")
        print(f"Changed files: {', '.join(all_files)}")
        _set_ci_env("RUN_ALL", "true")
        _write_github_output("run_all", "true")
        raise SystemExit(0)

    logic_changed = False

    print(f"Analyzing {len(python_files)} Python file(s)...")
    if doc_files:
        print(f"Documentation files changed: {len(doc_files)}")
    if other_files:
        print(f"Other files changed: {len(other_files)}")

    for filename in python_files:
        git_path = filename.replace("\\", "/")

        print(f"\nProcessing: {filename}")

        try:
            if not _validate_git_ref(base_ref):
                print(f"[ERR] Invalid git reference: {base_ref}", file=sys.stderr)
                raise SystemExit(1)
            if not _validate_git_path(git_path):
                print(f"[ERR] Invalid git path: {git_path}", file=sys.stderr)
                raise SystemExit(1)

            git_executable = _get_git_executable()
            old_code = subprocess.run(  # nosec B603 - controlled git args
                [git_executable, "show", f"{base_ref}:{git_path}"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            ).stdout
            print(f"  Retrieved {base_ref} version ({len(old_code)} chars)")
        except subprocess.CalledProcessError:
            if Path(filename).exists():
                print(f"[NEW] New file detected: {filename}")
            else:
                print(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            print(f"[ERR] Could not decode {base_ref} version of {filename}", file=sys.stderr)
            logic_changed = True
            continue

        try:
            with open(filename, "r", encoding="utf-8", errors="replace") as f:
                new_code = f.read()
            print(f"  Retrieved working version ({len(new_code)} chars)")
        except FileNotFoundError:
            print(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            print(f"[ERR] Could not decode local version of {filename}", file=sys.stderr)
            logic_changed = True
            continue
        except Exception as e:
            print(f"[ERR] Error reading {filename}: {e}", file=sys.stderr)
            logic_changed = True
            continue

        old_ast = get_ast_dump(old_code, f"{base_ref}:{filename}")
        new_ast = get_ast_dump(new_code, filename)

        if old_ast == "SYNTAX_ERROR" or new_ast == "SYNTAX_ERROR":
            print(f"[ERR] Syntax Error detected in: {filename}", file=sys.stderr)
            logic_changed = True
            continue

        if old_ast != new_ast:
            print(f"[MOD] Logic change detected in: {filename}")
            if len(old_ast) != len(new_ast):
                print(f"  AST size: {len(old_ast)} -> {len(new_ast)} chars")
            logic_changed = True
        else:
            print(f"[OK]  Docstring/Comment/Style only: {filename}")
            print(f"  AST unchanged (both {len(old_ast)} chars)")

    print("-" * 40)
    if logic_changed or other_files:
        if logic_changed:
            print("[!] CODE LOGIC CHANGES DETECTED")
        if other_files:
            print(f"[!] NON-PYTHON FILES CHANGED: {len(other_files)}")
        print("Result: RUN ALL CI/CD JOBS")
        _set_ci_env("RUN_ALL", "true")
        _write_github_output("run_all", "true")
        _write_github_output("skip_tests", "false")
    else:
        print("[OK] ONLY DOCSTRINGS/COMMENTS CHANGED")
        print("Result: SKIP CODE TESTS")
        _set_ci_env("SKIP_CODE_TESTS", "true")
        _write_github_output("skip_tests", "true")
        _write_github_output("doc_only", "false")
    print("-" * 40)

    raise SystemExit(0)


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Analyze code changes to determine what CI/CD jobs should run.",
    )
    parser.add_argument(
        "--base",
        "-b",
        default="origin/main",
        help="Git reference to compare against (e.g., origin/main, HEAD, main)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    analyze_changes(base_ref=args.base)
