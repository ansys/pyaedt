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

from contextlib import suppress
import json
from pathlib import Path

try:
    import typer
except ImportError as e:  # pragma: no cover
    from ansys.aedt.core.internal.checks import install_message

    msg = install_message("typer", "all", level="module")
    raise ImportError(msg) from e

# ---------------------------------------------------------------------------
# JSON output mode
# ---------------------------------------------------------------------------

json_mode = False


def print_output(data=None, error=None):
    """Print structured output. In JSON mode prints JSON; in human mode does nothing."""
    if not json_mode:
        return
    if error:
        typer.echo(json.dumps({"status": "error", "error": str(error)}))
    else:
        typer.echo(json.dumps({"status": "ok", "data": data}))


def get_desktop(port: int):
    """
    Connect to a running AEDT instance by gRPC port.

    Parameters
    ----------
    port : int
        gRPC port of the AEDT instance.

    """
    if port is None:
        if json_mode:
            print_output(error="--port is required.")
        else:
            typer.secho("--port is required.", fg="red")
        raise typer.Exit(code=1)

    from ansys.aedt.core import settings
    from ansys.aedt.core.desktop import Desktop

    settings.enable_logger = False
    d = Desktop(
        port=port,
        new_desktop=False,
        close_on_exit=False,
    )
    return d


def get_project_designs(desktop, project_name: str) -> list[dict]:
    """Return the designs available in a project."""
    designs = []
    for design_name in desktop.design_list(project_name):
        design_type = desktop.design_type(project_name=project_name, design_name=design_name)
        designs.append({"name": design_name, "type": design_type or None})
    return designs


def list_projects_with_designs(desktop) -> list[dict]:
    """Return all open projects together with their designs."""
    project_names = list(desktop.project_list)
    active_project_name = desktop.active_project_name
    active_design_name = desktop.active_design_name
    projects = []

    try:
        for project_name in project_names:
            designs = get_project_designs(desktop, project_name)
            projects.append({"name": project_name, "designs": designs, "count": len(designs)})
    finally:
        if active_project_name:
            restored_project = desktop.active_project(active_project_name)
            if restored_project and active_design_name:
                with suppress(Exception):
                    desktop.active_design(restored_project, active_design_name)

    return projects


def resolve_project(desktop, project_name: str | None = None):
    """Resolve a project, requiring an explicit choice when multiple are open."""
    project_names = list(desktop.project_list)

    if project_name:
        if project_name not in project_names:
            raise RuntimeError(f"Project '{project_name}' is not open in the AEDT instance.")
        project = desktop.active_project(project_name)
        if not project:
            raise RuntimeError(f"Project '{project_name}' could not be activated.")
        return project

    if not project_names:
        raise RuntimeError("No projects are open in the AEDT instance.")
    if len(project_names) > 1:
        raise RuntimeError("Multiple projects are open. Provide --project to select one.")

    project = desktop.active_project(project_names[0])
    if not project:
        raise RuntimeError(f"Project '{project_names[0]}' could not be activated.")
    return project


def resolve_project_and_design(desktop, project_name: str | None = None, design_name: str | None = None) -> dict:
    """Resolve a unique project and design selection for design-scoped commands."""
    project = resolve_project(desktop, project_name=project_name)
    resolved_project_name = project.GetName()
    designs = get_project_designs(desktop, resolved_project_name)
    design_names = [design["name"] for design in designs]

    if design_name:
        if design_name not in design_names:
            raise RuntimeError(f"Design '{design_name}' is not present in project '{resolved_project_name}'.")
        design = desktop.active_design(project, design_name)
        if not design:
            raise RuntimeError(f"Design '{design_name}' could not be activated in project '{resolved_project_name}'.")
        resolved_design_name = design_name
    else:
        if not design_names:
            raise RuntimeError(f"Project '{resolved_project_name}' does not contain any designs.")
        if len(design_names) > 1:
            raise RuntimeError(
                f"Project '{resolved_project_name}' contains multiple designs. Provide --design to select one."
            )
        resolved_design_name = design_names[0]
        desktop.active_design(project, resolved_design_name)

    return {"project": resolved_project_name, "design": resolved_design_name}


def get_design_app(port: int, project_name: str | None = None, design_name: str | None = None):
    """Return a Desktop and PyAEDT app for the resolved project and design."""
    import ansys.aedt.core as aedt

    aedt.settings.enable_logger = False
    desktop = get_desktop(port=port)
    context = resolve_project_and_design(desktop, project_name=project_name, design_name=design_name)
    app = aedt.get_pyaedt_app(project_name=context["project"], design_name=context["design"], desktop=desktop)
    return desktop, app, context


# ---------------------------------------------------------------------------
# Test configuration helpers
# ---------------------------------------------------------------------------

DEFAULT_TEST_CONFIG = {
    "desktopVersion": "2026.1",
    "NonGraphical": True,
    "NewThread": True,
    "skip_circuits": False,
    "use_grpc": True,
    "close_desktop": True,
    "use_local_example_data": False,
    "local_example_folder": "",
    "skip_modelithics": True,
}


def get_tests_folder() -> Path:
    """Find the tests folder in the repository.

    Returns
    -------
    Path
        Path to the tests folder
    """
    try:
        import ansys.aedt.core

        package_dir = Path(ansys.aedt.core.__file__).parent
        # Go up from src/ansys/aedt/core to the repo root
        repo_root = package_dir.parent.parent.parent.parent
        tests_folder = repo_root / "tests"
        if tests_folder.exists():
            return tests_folder
    except Exception:
        typer.echo("! Error finding tests folder, fallbacking to current working directory.")
    # Fallback: search from current working directory
    cwd = Path.cwd()
    return cwd / "tests"


def load_config(config_path: Path) -> dict:
    """Load configuration from JSON file.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file

    Returns
    -------
    dict
        Configuration dictionary
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        # Filter to only include known keys
        return {k: config.get(k, v) for k, v in DEFAULT_TEST_CONFIG.items()}
    except Exception:
        return DEFAULT_TEST_CONFIG.copy()


def save_config(config_path: Path, config: dict) -> None:
    """Save configuration to JSON file.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file
    config : dict
        Configuration dictionary to save
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def prompt_config_value(key: str, current_value) -> any:
    """Prompt user to modify a configuration value.

    Parameters
    ----------
    key : str
        Configuration key
    current_value : any
        Current value

    Returns
    -------
    any
        New value or current value if unchanged
    """
    if isinstance(current_value, bool):
        typer.echo("      ", nl=False)
        choice = typer.confirm(f"Change to {not current_value}?", default=False)
        return not current_value if choice else current_value
    elif isinstance(current_value, str):
        typer.echo("      ", nl=False)

        # Special handling for desktopVersion
        if key == "desktopVersion":
            while True:
                new_value = typer.prompt(
                    "New value (format: YYYY.R, e.g., 2026.1)", default=current_value, show_default=False
                )
                # Remove quotes if user entered them
                new_value = new_value.strip().strip('"').strip("'")

                # Validate format: 4 digits + "." + 1 digit
                import re

                if re.match(r"^\d{4}\.\d$", new_value):
                    return new_value
                else:
                    typer.secho("      Invalid format. Please use YYYY.R (e.g., 2026.1)", fg="red")
                    typer.echo("      ", nl=False)
        else:
            new_value = typer.prompt("New value", default=current_value, show_default=False)
        return new_value
    elif isinstance(current_value, int):
        typer.echo("      ", nl=False)
        new_value = typer.prompt("New value", default=current_value, type=int, show_default=False)
        return new_value
    else:
        return current_value


def display_config(config: dict, title: str = "Configuration", descriptions: dict = None) -> None:
    """Display configuration in a pretty formatted way.

    Parameters
    ----------
    config : dict
        Configuration dictionary to display
    title : str
        Title to display above the configuration
    descriptions : dict, optional
        Dictionary of key descriptions to display
    """
    typer.echo(f"\n{title}:")
    typer.echo()

    for key, value in config.items():
        if isinstance(value, bool):
            value_str = "True" if value else "False"
            color = "green" if value else "red"
        elif isinstance(value, str):
            if value == "":
                value_str = "(empty)"
                color = "yellow"
            else:
                value_str = f"{value}"
                color = "cyan"
        else:
            value_str = str(value)
            color = "white"

        # Display as bullet point
        typer.echo(f"  - {key}: ", nl=False)
        typer.secho(value_str, fg=color)

        # Display description if provided
        if descriptions and key in descriptions:
            desc = descriptions[key]
            typer.secho(f"    {desc}", fg="bright_black")

    typer.echo()
