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

import json
import os
import random
import shutil
import string
import sys
import tempfile

import pytest

from ansys.aedt.core.generic.settings import settings

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

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.filtersolutions import DistributedDesign
from ansys.aedt.core.filtersolutions import LumpedDesign
from ansys.aedt.core.internal.filesystem import Scratch

local_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(local_path)

# Initialize default desktop configuration
default_version = "2025.1"

config = {
    "desktopVersion": default_version,
    "NonGraphical": True,
    "NewThread": True,
    "skip_desktop_test": False,
    "build_machine": True,
    "skip_space_claim": False,
    "skip_circuits": False,
    "skip_edb": False,
    "skip_debug": False,
    "skip_modelithics": True,
    "local": False,
    "use_grpc": True,
    "disable_sat_bounding_box": True,
}

# Check for the local config file, override defaults if found
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    try:
        with open(local_config_file) as f:
            local_config = json.load(f)
    except Exception:  # pragma: no cover
        local_config = {}
    config.update(local_config)

NONGRAPHICAL = config["NonGraphical"]
settings.disable_bounding_box_sat = config["disable_sat_bounding_box"]
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]
settings.use_grpc_api = config["use_grpc"]

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
    test_folder = os.path.join(tempfile.gettempdir(), test_folder_name)
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


@pytest.fixture(scope="function")
def lumped_design():
    """Fixture for creating a LumpedDesign object."""
    return LumpedDesign(config["desktopVersion"])


@pytest.fixture(scope="function")
def distributed_design():
    """Fixture for creating a DistributedDesign object."""
    return DistributedDesign(config["desktopVersion"])
