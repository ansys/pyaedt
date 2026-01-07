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
    aedt_version: str = typer.Option(
        None,
        "--version",
        "-v",
        help="AEDT version (such as 2025.2). If not provided, you'll be prompted to select from installed versions.",
    ),
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
):
    """Add PyAEDT panels to AEDT installation.

    This command installs PyAEDT tabs (Console, Jupyter, Run Script, Extension Manager,
    and optionally Version Manager) into your AEDT installation.

    Examples
    --------
        pyaedt panels add --version 2025.2 --personal-lib "C:\\Users\\username\\AppData\\Roaming\\Ansoft\\PersonalLib"
        pyaedt panels add -v 2025.2 -p "/home/username/Ansoft/PersonalLib"
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

        main_versions = [v for v in installed.keys() if not any(suffix in v for suffix in ["AWP", "CL", "SV"])]

        if not main_versions:
            main_versions = list(installed.keys())

        if not aedt_version:
            typer.secho("\nInstalled AEDT versions:", fg=typer.colors.CYAN, bold=True)
            for idx, ver in enumerate(main_versions, 1):
                typer.echo(f"  {idx}. {ver}")

            selection = typer.prompt("\nSelect AEDT version number", type=int, default=1)

            if selection < 1 or selection > len(main_versions):
                typer.secho(
                    f"✗ Invalid selection. Please choose a number between 1 and {len(main_versions)}.",
                    fg=typer.colors.RED,
                    bold=True,
                )
                raise typer.Exit(code=1)

            aedt_version = main_versions[selection - 1]
            typer.secho(f"\nSelected version: {aedt_version}", fg=typer.colors.GREEN)

        # Validate AEDT version format
        if not aedt_version or not isinstance(aedt_version, str):
            typer.secho(
                "✗ Invalid AEDT version. Provide a valid version string (such as 2025.2)",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)

        aedt_version = aedt_version.strip()
        if not aedt_version:
            typer.secho("✗ AEDT version cannot be empty.", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        # Validate that the selected version is installed
        if aedt_version not in installed:
            typer.secho(
                f"✗ AEDT version '{aedt_version}' is not installed on this system.",
                fg=typer.colors.RED,
                bold=True,
            )
            typer.echo("\nInstalled versions:")
            for ver in main_versions:
                typer.secho(f"  • {ver}", fg=typer.colors.CYAN)
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

        # Import and run the installer
        typer.secho(
            f"Installing PyAEDT panels for AEDT {aedt_version}...",
            fg=typer.colors.BLUE,
            bold=True,
        )
        typer.secho(f"PersonalLib location: {personal_lib_path}", fg=typer.colors.CYAN)

        if skip_version_manager:
            typer.secho("Skipping Version Manager tab...", fg=typer.colors.YELLOW)

        from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt

        result = add_pyaedt_to_aedt(
            aedt_version=aedt_version,
            personal_lib=str(personal_lib_path),
            skip_version_manager=skip_version_manager,
            odesktop=None,
        )

        if result is False:
            typer.secho("✗ Failed to install PyAEDT panels.", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        typer.secho("✓ PyAEDT panels installed successfully.", fg=typer.colors.GREEN, bold=True)
        typer.echo("\nInstalled panels:")
        typer.secho("  • Console", fg=typer.colors.GREEN)
        typer.secho("  • Jupyter", fg=typer.colors.GREEN)
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
