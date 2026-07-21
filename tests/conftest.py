# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

import fnmatch
import inspect
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
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
    "desktopVersion": "2026.1",
    "NonGraphical": True,
    "NewThread": True,
    "use_grpc": True,
    "close_desktop": True,
    "use_local_example_data": False,
    "local_example_folder": None,
    "skip_circuits": False,
    "skip_modelithics": True,
    "use_pyedb_grpc": True,
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
USE_PYEDB_GRPC = config.get("use_pyedb_grpc", DEFAULT_CONFIG.get("use_pyedb_grpc"))

os.environ["PYAEDT_DESKTOP_VERSION"] = DESKTOP_VERSION

# ================================
# Shared markers
# ================================

# Mark tests as xfail when PYAEDT_EDB_XFAIL=1
# NOTE: Remove marker below if 26R1 SP2 is installed or later version of AEDT is used.
edb_xfail = pytest.mark.xfail(
    condition=os.environ.get("PYAEDT_EDB_XFAIL") == "1",
    reason="PyEDB tests are unstable",
)

# ================================
# PyAEDT settings
# ================================

settings.aedt_version = DESKTOP_VERSION
settings.use_grpc_api = USE_GRPC
settings.use_local_example_data = USE_LOCAL_EXAMPLE_DATA
if settings.use_local_example_data and USE_LOCAL_EXAMPLE_FOLDER:
    settings.local_example_folder = USE_LOCAL_EXAMPLE_FOLDER
settings.pyedb_use_grpc = USE_PYEDB_GRPC
# NOTE: Additional environment configuration for error handling when the tests are
# run locally and not in a CI environment.
if "PYAEDT_LOCAL_SETTINGS_PATH" not in os.environ:
    settings.enable_error_handler = False
    settings.release_on_exception = False
else:
    print("PYAEDT_LOCAL_SETTINGS_PATH found")
    settings._update_settings()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
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
def clean_old_pytest_temps(tmp_path_factory) -> None:
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

    desktop_app.temp_directory = base
    yield desktop_app

def is_student_version():
    return False
