"""
Unit Test Configuration Module
-------------------------------

Description
===========

This module contains the configuration and fixture for the pytest-based unit tests for pyaedt.

The default configuration can be changed by placing a file called local_config.json in the same
directory as this module. An example of the contents of local_config.json
{
  "desktopVersion": "2021.1",
  "NonGraphical": false,
  "NewThread": false,
  "test_desktops": true
}

"""
import tempfile
import pytest
import os
import shutil
import pathlib
import json
from .launch_desktop_tests import run_desktop_tests

from pyaedt import Desktop

local_path = os.path.dirname(os.path.realpath(__file__))
module_path = pathlib.Path(local_path)

# set scratch path and create it if necessary
scratch_path = tempfile.TemporaryDirectory().name
if not os.path.isdir(scratch_path):
    os.mkdir(scratch_path)

# Check for the local config file, otherwise use default desktop configuration
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    with open(local_config_file) as f:
        config = json.load(f)
else:
    config = {
        "desktopVersion": "2021.1",
        "NonGraphical": False,
        "NewThread": True,
        "test_desktops": False,
        "build_machine": True
    }

# Define desktopVersion explicitly since this is imported by other modules
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]
non_graphical = config["NonGraphical"]

@pytest.fixture(scope='session', autouse=True)
def desktop_init():
    desktop = Desktop(desktop_version, non_graphical, new_thread)

    yield desktop

    # If new_thread is set to false by a local_config, then don't close the desktop.
    # Intended for local debugging purposes only
    if new_thread:
        desktop.force_close_desktop()

    p = pathlib.Path(scratch_path).glob('**/scratch*')
    for folder in p:
        shutil.rmtree(folder, ignore_errors=True)

    if config["test_desktops"]:
        run_desktop_tests()