# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import json
import os
from pathlib import Path
import random
import shutil
import string
import sys
import tempfile
from typing import List
from unittest.mock import MagicMock

import pytest

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.filesystem import Scratch

# Test category prefixes for marker assignment
UNIT_TEST_PREFIX = "tests/unit"
INTEGRATION_TEST_PREFIX = "tests/integration"
SYSTEM_TEST_PREFIX = "tests/system"
SYSTEM_SOLVERS_TEST_PREFIX = "tests/system/solvers"
SYSTEM_GENERAL_TEST_PREFIX = "tests/system/general"
VISUALIZATION_GENERAL_TEST_PREFIX = "tests/system/visualization"
EXTENSIONS_GENERAL_TEST_PREFIX = "tests/system/extensions"
FILTER_SOLUTIONS_TEST_PREFIX = "tests/system/filter_solutions"
EMIT_TEST_PREFIX = "tests/system/emit"

# Global settings configuration - applied to all tests
settings.enable_local_log_file = False
settings.enable_global_log_file = False
settings.number_of_grpc_api_retries = 6
settings.retry_n_times_time_interval = 0.5
settings.enable_error_handler = False
settings.enable_desktop_logs = False
settings.desktop_launch_timeout = 180
settings.release_on_exception = False
settings.wait_for_license = True
settings.enable_pandas_output = True

# Initialize default configuration - shared across all test types
default_version = "2025.2"
os.environ["ANSYSEM_FEATURE_SS544753_ICEPAK_VIRTUALMESHREGION_PARADIGM_ENABLE"] = "1"

DEFAULT_CONFIG = {
    "desktopVersion": default_version,
    "NonGraphical": True,
    "NewThread": True,
    "skip_circuits": False,
    "skip_modelithics": True,
    "use_grpc": True,
    "disable_sat_bounding_box": True,
    "close_desktop": True,
    "remove_lock": False,
    "local_example_folder": None,
    "use_local_example_data": False,
}

# Load top-level configuration
local_path = Path(__file__).parent
local_config_file = local_path / "local_config.json"

config = DEFAULT_CONFIG.copy()
if local_config_file.exists():
    try:
        with open(local_config_file) as f:
            local_config = json.load(f)
        config.update(local_config)
    except Exception:  # pragma: no cover
        pass


# Apply global configuration moved into a function for reuse and to support updates from nested conftest files
def apply_global_configuration(cfg: dict):
    """Apply global configuration settings from a configuration dictionary.

    This updates module-level variables, the shared `settings` object and environment
    variables. Defaults are taken from DEFAULT_CONFIG when keys are missing.
    """
    global NONGRAPHICAL, desktop_version, new_thread, close_desktop, remove_lock, logger

    NONGRAPHICAL = cfg.get("NonGraphical", DEFAULT_CONFIG.get("NonGraphical"))
    settings.disable_bounding_box_sat = cfg.get(
        "disable_sat_bounding_box", DEFAULT_CONFIG.get("disable_sat_bounding_box")
    )
    desktop_version = cfg.get("desktopVersion", DEFAULT_CONFIG.get("desktopVersion"))
    new_thread = cfg.get("NewThread", DEFAULT_CONFIG.get("NewThread"))
    settings.use_grpc_api = cfg.get("use_grpc", DEFAULT_CONFIG.get("use_grpc"))
    close_desktop = cfg.get("close_desktop", DEFAULT_CONFIG.get("close_desktop"))
    remove_lock = cfg.get("remove_lock", DEFAULT_CONFIG.get("remove_lock"))
    settings.use_local_example_data = cfg.get("use_local_example_data", DEFAULT_CONFIG.get("use_local_example_data"))
    if settings.use_local_example_data:
        settings.local_example_folder = cfg.get("local_example_folder", DEFAULT_CONFIG.get("local_example_folder"))

    logger = pyaedt_logger
    os.environ["PYAEDT_SCRIPT_VERSION"] = cfg.get("desktopVersion", DEFAULT_CONFIG.get("desktopVersion"))


# Call the function to apply the current config values
apply_global_configuration(config)

# Add current path to sys.path for imports
sys.path.append(str(local_path))


def generate_random_string(length):
    """Generate a random string of specified length."""
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.sample(characters, length))
    return random_string


def generate_random_ident():
    """Generate a random identifier for test folders."""
    ident = "-" + generate_random_string(6) + "-" + generate_random_string(6) + "-" + generate_random_string(6)
    return ident


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
        elif item.nodeid.startswith(EXTENSIONS_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.extensions)
        elif item.nodeid.startswith(FILTER_SOLUTIONS_TEST_PREFIX):
            item.add_marker(pytest.mark.filter_solutions)
        elif item.nodeid.startswith(EMIT_TEST_PREFIX):
            item.add_marker(pytest.mark.emit)


# ================================
# SHARED FIXTURES
# ================================


@pytest.fixture(scope="session", autouse=True)
def init_scratch():
    """Initialize a global scratch directory for all tests."""
    test_folder_name = "pyaedt_test" + generate_random_ident()
    test_folder = Path(tempfile.gettempdir()) / test_folder_name
    try:
        os.makedirs(test_folder, mode=0o777)
    except FileExistsError as e:
        print(f"Failed to create {test_folder}. Reason: {e}")

    yield test_folder

    try:
        shutil.rmtree(test_folder, ignore_errors=True)
    except Exception as e:
        print(f"Failed to delete {test_folder}. Reason: {e}")


@pytest.fixture(scope="module", autouse=True)
def local_scratch(init_scratch):
    """Provide a module-scoped scratch directory."""
    tmp_path = init_scratch
    scratch = Scratch(tmp_path)
    yield scratch
    scratch.remove()


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
