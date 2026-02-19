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

from pathlib import Path
import platform
import shutil

try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.internal.aedt_versions import aedt_versions

panels_app = typer.Typer(help="Manage PyAEDT panels in AEDT", no_args_is_help=True)


@panels_app.command("add")
def add_panels(
    personal_lib: str = typer.Option(
        None,
        "--personal-lib",
        "-p",
        help="Path to AEDT PersonalLib folder",
        prompt="Enter path to PersonalLib folder",
    ),
    skip_version_manager: bool = typer.Option(
        False,
        "--skip-version-manager",
        help="Skip installing the Version Manager tab",
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        "-r",
        help="Delete existing Toolkits directory before installing",
    ),
):
    """Add PyAEDT panels to AEDT installation.

    TThis command installs PyAEDT tabs (Console, Jupyter, Run Script, Extension Manager,
    and optionally Version Manager) into your AEDT installation.

    Examples
    --------
        pyaedt panels add --personal-lib "C:\\Users\\username\\AppData\\Roaming\\Ansoft\\PersonalLib"
        pyaedt panels add -p "/home/username/Ansoft/PersonalLib"
        pyaedt panels add --personal-lib "..." --reset  # Delete Toolkits before installing
        pyaedt panels add  # Interactive mode: select from installed versions
    """
    try:
        installed = aedt_versions.installed_versions

        if not installed:
            typer.secho(
                "✗ No AEDT versions found on this system.",
                fg=typer.colors.RED,
                bold=True,
            )
            typer.echo("\nPlease install AEDT before running this command.")
            raise typer.Exit(code=1)

        # Validate personal_lib path
        if not personal_lib or not isinstance(personal_lib, str):
            typer.secho(
                "✗ the 'personal_lib' path is invalid. Provide a valid path",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        personal_lib = personal_lib.strip()
        if not personal_lib:
            typer.secho(
                "✗ The 'personal_lib' path is invalid. Provide a valid path.",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        personal_lib_path = Path(personal_lib)

        if not personal_lib_path.exists():
            typer.secho(
                f"✗ The 'personal_lib' path does not exist: {personal_lib_path}",
                fg=typer.colors.RED,
                bold=True,
            )
            typer.echo("\nCommon PersonalLib locations:")
            if platform.system() == "Windows":
                typer.secho(
                    "  Windows: C:\\Users\\<username>\\AppData\\Roaming\\Ansoft\\PersonalLib",
                    fg=typer.colors.CYAN,
                )
            else:
                typer.secho(
                    "  Linux: /home/<username>/Ansoft/PersonalLib",
                    fg=typer.colors.CYAN,
                )
            raise typer.Exit(code=1)

        if not personal_lib_path.is_dir():
            typer.secho(
                f"✗ The 'personallib' path is not a directory: {personal_lib_path}",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        # Handle reset option - delete Toolkits directory if requested
        if reset:
            toolkits_path = personal_lib_path / "Toolkits"
            if toolkits_path.exists():
                typer.secho(
                    "Deleting existing Toolkits directory...",
                    fg=typer.colors.YELLOW,
                    bold=True,
                )
                typer.secho(f"  {toolkits_path}", fg=typer.colors.CYAN)
                try:
                    shutil.rmtree(toolkits_path)
                    typer.secho(
                        "✓ Toolkits directory deleted successfully.",
                        fg=typer.colors.GREEN,
                    )
                except PermissionError as e:
                    typer.secho(
                        f"✗ Permission denied: {str(e)}",
                        fg=typer.colors.RED,
                        bold=True,
                    )
                    typer.echo("\nMake sure:")
                    typer.echo("  • You have permission to delete files in this directory")
                    typer.echo("  • AEDT is not currently running")
                    typer.echo("  • No files in the Toolkits directory are currently in use")
                    raise typer.Exit(code=1)
                except Exception as e:
                    typer.secho(
                        f"✗ Error deleting Toolkits directory: {str(e)}",
                        fg=typer.colors.RED,
                        bold=True,
                    )
                    raise typer.Exit(code=1)
            else:
                typer.secho(
                    "ℹ Toolkits directory does not exist, nothing to delete.",
                    fg=typer.colors.YELLOW,
                )

        # Import and run the installer
        typer.secho(
            "Installing PyAEDT panels...",
            fg=typer.colors.BLUE,
            bold=True,
        )
        typer.secho(f"PersonalLib location: {personal_lib_path}", fg=typer.colors.CYAN)

        if skip_version_manager:
            typer.secho("Skipping Version Manager tab...", fg=typer.colors.YELLOW)

        from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt

        result = add_pyaedt_to_aedt(
            personal_lib=str(personal_lib_path),
            skip_version_manager=skip_version_manager,
        )

        if not result:
            typer.secho("✗ Failed to install PyAEDT panels.", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        typer.secho("✓ PyAEDT panels installed successfully.", fg=typer.colors.GREEN, bold=True)
        typer.echo("\nInstalled panels:")
        typer.secho("  • PyAEDT Utilities (Console, CLI, Jupyter)", fg=typer.colors.GREEN)
        typer.secho("  • Run Script", fg=typer.colors.GREEN)
        typer.secho("  • Extension Manager", fg=typer.colors.GREEN)
        if not skip_version_manager:
            typer.secho("  • Version Manager", fg=typer.colors.GREEN)
        typer.secho(
            "\nRestart AEDT to see the new panels on the Automation tab.",
            fg=typer.colors.YELLOW,
            bold=True,
        )

    except typer.Exit:
        raise
    except ImportError as e:
        typer.secho(f"✗ Import error: {str(e)}", fg=typer.colors.RED, bold=True)
        typer.echo("Make sure PyAEDT is properly installed.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"✗ Error installing panels: {str(e)}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
