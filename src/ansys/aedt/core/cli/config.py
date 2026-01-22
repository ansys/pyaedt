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


try:
    import typer
except ImportError:  # pragma: no cover
    raise ImportError(
        "typer is required for the CLI. Please install with 'pip install pyaedt[all]' or 'pip install typer'"
    )

from ansys.aedt.core.cli import common
from ansys.aedt.core.cli.common import DEFAULT_TEST_CONFIG
from ansys.aedt.core.cli.common import _display_config
from ansys.aedt.core.cli.common import _get_config_path
from ansys.aedt.core.cli.common import _load_config
from ansys.aedt.core.cli.common import _prompt_config_value
from ansys.aedt.core.cli.common import _save_config

config_app = typer.Typer(help="Configuration management commands")
test_app = typer.Typer(help="Test configuration management commands", invoke_without_command=True)
config_app.add_typer(test_app, name="test")


def _update_bool_config(key: str, value: bool | None, display_name: str = None) -> None:
    """Update a boolean configuration value.

    Parameters
    ----------
    key : str
        Configuration key
    value : bool | None
        New value or None for interactive mode
    display_name : str, optional
        Display name (defaults to key)
    """
    config_path, config = _get_config_path()
    display_name = display_name or key
    default = DEFAULT_TEST_CONFIG.get(key, False)

    if value is None:
        current_value = config.get(key, default)
        typer.echo(f"\nCurrent {display_name}: ", nl=False)
        value_str = "True" if current_value else "False"
        color = "green" if current_value else "red"
        typer.secho(value_str, fg=color)
        typer.echo("")
        value = typer.confirm(f"Set to {not current_value}?", default=True)
        value = not current_value if value else current_value

    config[key] = value
    _save_config(config_path, config)
    typer.secho(f"✓ {display_name} set to {value}", fg="green")


def _update_string_config(key: str, value: str | None, display_name: str = None, validator: callable = None) -> None:
    """Update a string configuration value.

    Parameters
    ----------
    key : str
        Configuration key
    value : str | None
        New value or None for interactive mode
    display_name : str, optional
        Display name (defaults to key)
    validator : callable, optional
        Function to validate the value, should return (is_valid, error_message)
    """
    config_path, config = _get_config_path()
    display_name = display_name or key
    default = DEFAULT_TEST_CONFIG.get(key, "")

    if value is None:
        current_value = config.get(key, default)
        typer.echo(f"\nCurrent {display_name}: ", nl=False)
        if current_value:
            typer.secho(f"'{current_value}'", fg="cyan")
        else:
            typer.secho("(empty)", fg="yellow")

        if validator:
            typer.echo("")
            while True:
                value = typer.prompt("New value", default=current_value)
                value = value.strip().strip('"').strip("'")
                is_valid, error_msg = validator(value)
                if is_valid:
                    break
                else:
                    typer.secho(f"✗ {error_msg}", fg="red")
        else:
            typer.echo("")
            value = typer.prompt("New value", default=current_value)
    else:
        if validator:
            is_valid, error_msg = validator(value)
            if not is_valid:
                typer.secho(f"✗ {error_msg}", fg="red")
                return

    config[key] = value
    _save_config(config_path, config)
    typer.secho(f"✓ {display_name} set to '{value}'", fg="green")


@test_app.callback()
def test_callback(
    ctx: typer.Context,
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration without modifying"),
):
    """Create or modify local_config.json in the tests folder interactively."""
    if ctx.invoked_subcommand is not None:
        return

    tests_folder = common._get_tests_folder()
    config_path = tests_folder / "local_config.json"

    # Configuration descriptions
    config_descriptions = {
        "desktopVersion": "AEDT version to use",
        "NonGraphical": "Run AEDT without GUI",
        "NewThread": "Use new thread for AEDT",
        "skip_circuits": "Skip circuit tests",
        "use_grpc": "Use gRPC for communication",
        "close_desktop": "Close AEDT after tests",
        "use_local_example_data": "Use local example data",
        "local_example_folder": "Path to local examples",
        "skip_modelithics": "Skip Modelithics tests",
    }

    if config_path.exists():
        config = _load_config(config_path)
    else:
        config = DEFAULT_TEST_CONFIG.copy()
        _save_config(config_path, config)

    typer.echo("\n" + "=" * 70)
    typer.secho("  PyAEDT Test Configuration Manager", fg="bright_blue", bold=True)
    typer.echo("=" * 70)
    typer.echo("\n  📁 Tests folder: ", nl=False)
    typer.secho(str(tests_folder), fg="cyan")
    typer.echo("  📄 Config file:  ", nl=False)
    typer.secho(str(config_path), fg="cyan")

    if config_path.exists():
        typer.echo("\n  ", nl=False)
        typer.secho("✓", fg="green", bold=True, nl=False)
        typer.echo(" Configuration file found")
    else:
        typer.echo("\n  ", nl=False)
        typer.secho("✓", fg="green", bold=True, nl=False)
        typer.echo(" Configuration file created with defaults")

    # Display current configuration with descriptions
    _display_config(config, "Current Test Configuration", config_descriptions)

    # If --show flag is used, just display and exit
    if show:
        return

    # Interactive questionnaire
    typer.echo("─" * 70)
    typer.secho("  Would you like to modify the configuration?", fg="yellow", bold=True)
    typer.echo("─" * 70 + "\n")

    modify = typer.confirm("  Modify settings?", default=False)

    if not modify:
        typer.echo("\n  ", nl=False)
        typer.secho("i", fg="blue", bold=True, nl=False)
        typer.echo("  No changes made.\n")
        return

    # Interactive configuration
    typer.echo("\n" + "=" * 70)
    typer.secho("  Interactive Configuration", fg="bright_blue", bold=True)
    typer.echo("=" * 70)
    typer.secho("\n  💡 Tip: Press Enter to keep current value\n", fg="yellow")

    new_config = {}

    for i, (key, value) in enumerate(config.items(), 1):
        typer.echo(f"\n  [{i}/{len(config)}] ", nl=False)
        typer.secho(key, fg="bright_cyan", bold=True)

        description = config_descriptions.get(key, "")
        if description:
            typer.echo("      ", nl=False)
            typer.secho(f"i  {description}", fg="blue")

        if isinstance(value, bool):
            current_display = "True" if value else "False"
            color = "green" if value else "red"
        elif isinstance(value, str):
            current_display = f"'{value}'" if value else "(empty)"
            color = "cyan" if value else "yellow"
        else:
            current_display = str(value)
            color = "white"

        typer.echo("      Current: ", nl=False)
        typer.secho(current_display, fg=color)

        new_value = _prompt_config_value(key, value)
        new_config[key] = new_value

    typer.echo("\n" + "─" * 70)
    typer.echo("  Saving configuration...")
    _save_config(config_path, new_config)

    typer.echo("\n" + "=" * 70)
    typer.secho("  ✓ Configuration Updated Successfully!", fg="green", bold=True)
    typer.echo("=" * 70)

    _display_config(new_config, "Updated Test Configuration", config_descriptions)

    typer.secho("  Configuration saved to:", fg="bright_blue")
    typer.secho(f"  {config_path}\n", fg="cyan")


@test_app.command()
def desktop_version(value: str = typer.Argument(None, help="AEDT version (format: YYYY.R, e.g., 2025.2)")):
    """Set AEDT desktop version."""
    import re

    def validate_version(v: str) -> tuple[bool, str]:
        """Validate version format."""
        if re.match(r"^\d{4}\.\d$", v):
            return True, ""
        return False, "Invalid format. Please use YYYY.R (e.g., 2025.2)"

    _update_string_config("desktopVersion", value, "desktopVersion", validate_version)


@test_app.command()
def non_graphical(value: bool = typer.Argument(None, help="Run AEDT without GUI (true/false)")):
    """Set non-graphical mode."""
    _update_bool_config("NonGraphical", value, "NonGraphical")


@test_app.command()
def new_thread(value: bool = typer.Argument(None, help="Use new thread for AEDT (true/false)")):
    """Set new thread mode."""
    _update_bool_config("NewThread", value, "NewThread")


@test_app.command()
def skip_circuits(value: bool = typer.Argument(None, help="Skip circuit tests (true/false)")):
    """Set skip circuits flag."""
    _update_bool_config("skip_circuits", value, "skip_circuits")


@test_app.command()
def use_grpc(value: bool = typer.Argument(None, help="Use gRPC for communication (true/false)")):
    """Set use gRPC flag."""
    _update_bool_config("use_grpc", value, "use_grpc")


@test_app.command()
def close_desktop(value: bool = typer.Argument(None, help="Close AEDT after tests (true/false)")):
    """Set close desktop flag."""
    _update_bool_config("close_desktop", value, "close_desktop")


@test_app.command()
def use_local_example_data(value: bool = typer.Argument(None, help="Use local example data (true/false)")):
    """Set use local example data flag."""
    _update_bool_config("use_local_example_data", value, "use_local_example_data")


@test_app.command()
def local_example_folder(value: str = typer.Argument(None, help="Path to local examples folder")):
    """Set local example folder path."""
    _update_string_config("local_example_folder", value, "local_example_folder")


@test_app.command()
def skip_modelithics(value: bool = typer.Argument(None, help="Skip Modelithics tests (true/false)")):
    """Set skip Modelithics flag."""
    _update_bool_config("skip_modelithics", value, "skip_modelithics")
