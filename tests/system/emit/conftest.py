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

"""
Unit Test Configuration Module
-------------------------------

Description
===========

This module contains the configuration and fixture for the pytest-based unit tests for PyAEDT.

The default configuration can be changed by placing a file called local_config.json in the same
directory as this module. An example of the contents of local_config.json
{
  "desktopVersion": "2022.2",
  "NonGraphical": false,
  "NewThread": false,
  "skip_desktop_test": false
}

"""

import gc
import json
import os
from pathlib import Path
import random
import shutil
import string
import sys
import tempfile
import time

import pytest

from ansys.aedt.core import Emit
from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions
from ansys.aedt.core.internal.filesystem import Scratch

local_path = Path(__file__).parent
sys.path.append(str(local_path))

# Initialize default desktop configuration
default_version = "2025.2"

config = {
    "desktopVersion": default_version,
    "NonGraphical": True,
    "NewThread": True,
    "use_grpc": True,
    "close_desktop": True,
    "remove_lock": False,
}

# Check for the local config file, override defaults if found
local_config_file = Path(local_path) / "local_config.json"
if local_config_file.exists():
    try:
        with open(local_config_file) as f:
            local_config = json.load(f)
    except Exception:  # pragma: no cover
        local_config = {}
    config.update(local_config)

NONGRAPHICAL = config["NonGraphical"]
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]
settings.use_grpc_api = config["use_grpc"]
close_desktop = config["close_desktop"]
remove_lock = config["remove_lock"]

logger = pyaedt_logger


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.sample(characters, length))
    return random_string


def generate_random_ident():
    ident = "-" + generate_random_string(6) + "-" + generate_random_string(6) + "-" + generate_random_string(6)
    return ident


@pytest.fixture(scope="session", autouse=True)
def init_scratch():
    test_folder_name = "unit_test" + generate_random_ident()
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
    tmp_path = init_scratch
    scratch = Scratch(tmp_path)
    yield scratch
    scratch.remove()


def _delete_objects():
    settings.remote_api = False
    pyaedt_logger.remove_all_project_file_logger()
    try:
        del sys.modules["glob"]
    except Exception:
        logger.debug("Failed to delete glob module")
    gc.collect()


@pytest.fixture(scope="module", autouse=True)
def desktop(local_scratch):
    _delete_objects()
    keys = list(_desktop_sessions.keys())
    for key in keys:
        del _desktop_sessions[key]
    d = Desktop(desktop_version, NONGRAPHICAL, new_thread)
    d.odesktop.SetTempDirectory(str(local_scratch.path))
    d.disable_autosave()
    if desktop_version > "2022.2":
        d.odesktop.SetDesktopConfiguration("All")
        d.odesktop.SetSchematicEnvironment(0)
    yield d
    pid = d.aedt_process_id
    d.close_desktop()
    time.sleep(1)
    try:
        os.kill(pid, 9)
    except OSError:
        pass


@pytest.fixture(scope="module")
def add_app(local_scratch):
    def _method(
        project_name=None, design_name=None, solution_type=None, application=None, subfolder="", just_open=False
    ):
        if project_name and not just_open:
            example_project = Path(local_path) / "example_models" / subfolder / (project_name + ".aedt")
            if example_project.exists():
                test_project = local_scratch.copyfile(str(example_project))
            elif example_project.with_suffix(".aedtz").exists():
                example_project = example_project.with_suffix(".aedtz")
                test_project = local_scratch.copyfile(str(example_project))
            else:
                test_project = Path(local_scratch.path) / (project_name + ".aedt")
        elif project_name and just_open:
            test_project = project_name
        else:
            test_project = None
        if not application:
            application = Emit
        return application(
            project=test_project,
            design=design_name,
            solution_type=solution_type,
            version=desktop_version,
            remove_lock=remove_lock,
            non_graphical=NONGRAPHICAL,
        )

    return _method
