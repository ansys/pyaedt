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

import fnmatch
import inspect
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import List
from unittest.mock import MagicMock

import pytest

from ansys.aedt.core import Desktop
from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.file_utils import available_file_name
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.hfss import Hfss

# ================================
# Category prefixes
# ================================
UNIT_TEST_PREFIX = "tests/unit"
INTEGRATION_TEST_PREFIX = "tests/integration"
SYSTEM_TEST_PREFIX = "tests/system"
SYSTEM_SOLVERS_TEST_PREFIX = "tests/system/solvers"
SYSTEM_GENERAL_TEST_PREFIX = "tests/system/general"
VISUALIZATION_GENERAL_TEST_PREFIX = "tests/system/visualization"
SYSTEM_ICEPAK_TEST_PREFIX = "tests/system/icepak"
SYSTEM_LAYOUT_TEST_PREFIX = "tests/system/layout"
EXTENSIONS_GENERAL_TEST_PREFIX = "tests/system/extensions"
FILTER_SOLUTIONS_TEST_PREFIX = "tests/system/filter_solutions"
EMIT_TEST_PREFIX = "tests/system/emit"

# ================================
# Default test configuration
# ================================

DEFAULT_CONFIG = {
    "desktopVersion": "2025.2",
    "NonGraphical": True,
    "NewThread": True,
    "use_grpc": True,
    "close_desktop": True,
    "use_local_example_data": False,
    "local_example_folder": None,
    "skip_circuits": False,
    "skip_modelithics": True,
}

local_path = Path(__file__).parent
local_config_file = local_path / "local_config.json"

config = DEFAULT_CONFIG.copy()

if local_config_file.exists():
    try:
        with open(local_config_file) as f:
            local_config = json.load(f)
        config.update(local_config)
    except Exception as e:  # pragma: no cover
        # Failed to load local_config.json; report error
        print(f"Failed to load local_config.json ({local_config_file}): {e}")

DESKTOP_VERSION = config.get("desktopVersion", DEFAULT_CONFIG.get("desktopVersion"))
NON_GRAPHICAL = config.get("NonGraphical", DEFAULT_CONFIG.get("NonGraphical"))
NEW_THREAD = config.get("NewThread", DEFAULT_CONFIG.get("NewThread"))
CLOSE_DESKTOP = config.get("close_desktop", DEFAULT_CONFIG.get("close_desktop"))
USE_GRPC = config.get("use_grpc", DEFAULT_CONFIG.get("use_grpc"))
USE_LOCAL_EXAMPLE_DATA = config.get("use_local_example_data", DEFAULT_CONFIG.get("use_local_example_data"))
USE_LOCAL_EXAMPLE_FOLDER = config.get("local_example_folder", DEFAULT_CONFIG.get("local_example_folder"))
SKIP_CIRCUITS = config.get("skip_circuits", DEFAULT_CONFIG.get("skip_circuits"))
SKIP_MODELITHICS = config.get("skip_modelithics", DEFAULT_CONFIG.get("skip_modelithics"))

os.environ["PYAEDT_SCRIPT_VERSION"] = DESKTOP_VERSION

# ================================
# PyAEDT settings
# ================================

settings.use_grpc_api = USE_GRPC
settings.use_local_example_data = USE_LOCAL_EXAMPLE_DATA
if settings.use_local_example_data and USE_LOCAL_EXAMPLE_FOLDER:
    settings.local_example_folder = USE_LOCAL_EXAMPLE_FOLDER

# NOTE: Additional environment configuration for error handling when the tests are
# run locally and not in a CI environment.
if "PYAEDT_LOCAL_SETTINGS_PATH" not in os.environ:
    settings.enable_error_handler = False
    settings.release_on_exception = False
else:
    print("PYAEDT_LOCAL_SETTINGS_PATH found")
    settings._update_settings()


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    """Hook used to apply marker on tests."""
    for item in items:
        # Mark unit, integration and system tests
        if item.nodeid.startswith(UNIT_TEST_PREFIX):
            item.add_marker(pytest.mark.unit)
        elif item.nodeid.startswith(INTEGRATION_TEST_PREFIX):
            item.add_marker(pytest.mark.integration)
        elif item.nodeid.startswith(SYSTEM_TEST_PREFIX):
            item.add_marker(pytest.mark.system)
        # Finer markers for system tests
        if item.nodeid.startswith(SYSTEM_SOLVERS_TEST_PREFIX):
            item.add_marker(pytest.mark.solvers)
        elif item.nodeid.startswith(SYSTEM_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.general)
        elif item.nodeid.startswith(VISUALIZATION_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.visualization)
        elif item.nodeid.startswith(SYSTEM_ICEPAK_TEST_PREFIX):
            item.add_marker(pytest.mark.icepak)
        elif item.nodeid.startswith(SYSTEM_LAYOUT_TEST_PREFIX):
            item.add_marker(pytest.mark.layout)
        elif item.nodeid.startswith(EXTENSIONS_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.extensions)
        elif item.nodeid.startswith(FILTER_SOLUTIONS_TEST_PREFIX):
            item.add_marker(pytest.mark.filter_solutions)
        elif item.nodeid.startswith(EMIT_TEST_PREFIX):
            item.add_marker(pytest.mark.emit)


# ================================
# SESSION FIXTURES
# ================================


@pytest.fixture(scope="session", autouse=True)
def clean_old_pytest_temps(tmp_path_factory):
    """Delete previous pytest temp dirs before starting a new session."""
    # Clean pytest temp dirs
    base = tmp_path_factory.getbasetemp().parent
    current = tmp_path_factory.getbasetemp().name
    for entry in base.iterdir():
        if entry.is_dir() and entry.name.startswith("pytest-") and entry.name != current:
            try:
                shutil.rmtree(entry, ignore_errors=True)
            except Exception as e:
                pyaedt_logger.debug(f"Error {type(e)} occurred while deleting pytest directory: {e}")

    # Clean pkg- temp dirs from system temp
    temp_dir = Path(tempfile.gettempdir())
    for entry in temp_dir.iterdir():
        if entry.is_dir() and entry.name.startswith("pkg-"):
            try:
                shutil.rmtree(entry, ignore_errors=True)
            except Exception as e:
                pyaedt_logger.debug(f"Error {type(e)} occurred while deleting temp directory: {e}")


@pytest.fixture(scope="session", autouse=True)
def cleanup_all_tmp_at_end(tmp_path_factory):
    """Cleanup: Remove all files and directories under pytest's basetemp at session end."""
    base = tmp_path_factory.getbasetemp()
    temp_dir = Path(tempfile.gettempdir())

    yield

    # Now the session is over, try to remove everything inside `base`
    try:
        for log_file in base.glob("*.log"):
            try:
                log_file.unlink()
            except Exception as e:
                pyaedt_logger.debug(f"Failed to delete {log_file}: {e}")
    except Exception:
        pyaedt_logger.warning(f"Failed to cleanup logs in {base}")

    # Remove pkg- temp dirs from system temp
    try:
        for entry in temp_dir.iterdir():
            if entry.is_dir() and entry.name.startswith("pkg-"):
                shutil.rmtree(entry, ignore_errors=True)
            elif entry.is_file():
                if fnmatch.fnmatch(entry.name, "pyaedt_*.log") or fnmatch.fnmatch(entry.name, "pyedb_*.log"):
                    try:
                        entry.unlink()
                    except Exception as e:
                        pyaedt_logger.debug(f"Error deleting log: {e}")
    except Exception:
        pyaedt_logger.warning(f"Failed to cleanup {temp_dir}")


# ================================
# MODULE FIXTURES
# ================================


@pytest.fixture(scope="module")
def file_tmp_root(tmp_path_factory, request):
    module_path = Path(request.fspath)
    name = module_path.stem
    root = tmp_path_factory.mktemp(f"{name}-")
    yield root
    try:
        shutil.rmtree(root, ignore_errors=True)
    except Exception:
        pyaedt_logger.warning(f"Failed to cleanup temporary directory {root}")


@pytest.fixture(scope="module")
def desktop(tmp_path_factory, request):
    """
    Creates a Desktop instance for each test worker (xdist) or module.
    Module scope ensures only one Desktop is used by test file.
    """
    # New temp directory for the test session
    base = tmp_path_factory.getbasetemp()

    if "popen-gw" in str(base):
        base = base.parent

    desktop_app = Desktop(DESKTOP_VERSION, NON_GRAPHICAL, NEW_THREAD)

    desktop_app.odesktop.SetTempDirectory(str(base))
    desktop_app.odesktop.SetProjectDirectory(str(base))

    desktop_app.disable_autosave()

    yield desktop_app

    try:
        desktop_app.release_desktop(close_projects=True, close_on_exit=CLOSE_DESKTOP)
    except Exception as e:
        raise Exception("Failed to close Desktop instance") from e


# ================================
# COMMON FIXTURES
# ================================


@pytest.fixture
def test_tmp_dir(file_tmp_root, request):
    d = file_tmp_root / request.node.name.split("[", 1)[0]

    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def add_app(test_tmp_dir, desktop, tmp_path_factory):
    def _method(
        project: str | None = None,
        design: str | None = None,
        solution_type: str | None = None,
        application=None,
        close_projects=True,
    ):
        if close_projects and desktop and desktop.project_list:
            projects = desktop.project_list.copy()
            for project_name in projects:
                desktop.odesktop.CloseProject(project_name)

        if project is None:
            project = "pyaedt_test"

        if project and Path(project).is_file():
            project_file = Path(project)
        elif close_projects:
            project_file = available_file_name(test_tmp_dir / f"{project}.aedt")
        else:
            project_file = test_tmp_dir / f"{project}.aedt"

        # Application selection
        application_cls = application or Hfss

        # Build args
        args = _build_app_args(
            project=str(project_file),
            design_name=design,
            solution_type=solution_type,
        )

        app = application_cls(**args)

        return app

    return _method


@pytest.fixture
def add_app_example(test_tmp_dir, desktop, tmp_path_factory):
    def _method(
        subfolder: str | Path,
        project: str | None = None,
        design: str | None = None,
        solution_type: str | None = None,
        application=None,
        is_edb=False,
        close_projects=True,
    ):
        if close_projects and desktop and desktop.project_list:
            projects = desktop.project_list.copy()
            for project_name in projects:
                desktop.odesktop.CloseProject(project_name)

        if Path(subfolder).exists():
            base = Path(subfolder)
        else:
            test_path = _get_test_path_from_caller()
            base = test_path / "example_models" / subfolder

        if not is_edb:
            aedt_project = base / f"{project}.aedt"
            if aedt_project.exists():
                dst = test_tmp_dir / aedt_project.name
                shutil.copy2(aedt_project, dst)
                test_project = dst
            elif aedt_project.with_suffix(aedt_project.suffix + "z").exists():
                example_project_z = aedt_project.with_suffix(aedt_project.suffix + "z")
                dst = test_tmp_dir / example_project_z.name
                shutil.copy2(example_project_z, dst)
                test_project = dst
            else:
                raise Exception(f"Could not find {aedt_project}")
        else:
            aedt_project = base / f"{project}.aedb"
            if aedt_project.exists():
                test_project = test_tmp_dir / aedt_project.name
                shutil.copytree(aedt_project, test_project, dirs_exist_ok=True)
            else:
                raise Exception(f"Could not find {aedt_project}")

        # Application selection
        application_cls = application or Hfss

        # Build args
        args = _build_app_args(
            project=test_project,
            design_name=design,
            solution_type=solution_type,
        )
        app = application_cls(**args)

        return app

    return _method


@pytest.fixture
def touchstone_file(tmp_path):
    """Create a dummy touchstone file for testing."""
    file_path = tmp_path / "dummy.s2p"
    file_content = """
! Terminal data exported
! Port[1] = Port1
! Port[2] = Port2
0.1                            0.1 0.2
"""

    file_path.write_text(file_content)
    return file_path


@pytest.fixture()
def patch_graphics_modules(monkeypatch):
    """Patch graphics modules to avoid headless env issues."""
    modules = [
        "matplotlib",
        "matplotlib.pyplot",
        "pyvista",
        "imageio",
        "meshio",
        "vtk",
        "ansys.tools.visualization_interface",
        "ansys.tools.visualization_interface.backends",
        "ansys.tools.visualization_interface.backends.pyvista",
    ]

    mocks = {}
    for module in modules:
        mock = MagicMock(name=f"mock_{module}")
        mocks[module] = mock
        monkeypatch.setitem(sys.modules, module, mock)

    # Specific action to make a mock an attribute of another mock
    mocks["matplotlib"].pyplot = mocks["matplotlib.pyplot"]
    viz_interface = mocks["ansys.tools.visualization_interface"]
    viz_backends = mocks["ansys.tools.visualization_interface.backends"]
    viz_interface.backends = viz_backends
    viz_backends.pyvista = mocks["ansys.tools.visualization_interface.backends.pyvista"]

    yield mocks


def _build_app_args(
    project: str | None,
    design_name: str | None,
    solution_type: str | None,
) -> dict:
    """Build the kwargs dict for the AEDT application constructor."""
    args: dict = {
        "project": project,
        "design": design_name,
        "version": settings.aedt_version if hasattr(settings, "aedt_version") else None,
        "non_graphical": settings.non_graphical if hasattr(settings, "non_graphical") else True,
        "remove_lock": True,
        "new_desktop": False,
    }
    if solution_type:
        args["solution_type"] = solution_type
    return args


def _get_test_path_from_caller():
    """Return directory of the test file that called add_app."""
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    return Path(module.__file__).parent
