import tempfile
import pytest
import os
import shutil
import pathlib
import json
from .launch_desktop_tests import run_desktop_tests

from pyaedt import Desktop

default_config = {
    "desktopVersion": "2021.1",
    "NonGraphical": False,
    "NewThread": False,
    "test_desktops": False
}

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
    default_config = {
        "desktopVersion": "2021.1",
        "NonGraphical": False,
        "NewThread": False,
        "test_desktops": False
    }

# Define desktopVersion explicitly since this is imported by other modules
desktop_version = config["desktopVersion"]

@pytest.fixture(scope='session', autouse=True)
def desktop_init():
    desktop = Desktop(desktop_version, config["NonGraphical"], config["NewThread"])

    yield desktop

    desktop.force_close_desktop()
    p = pathlib.Path(scratch_path).glob('**/scratch*')
    for folder in p:
        shutil.rmtree(folder, ignore_errors=True)

    if config["test_desktops"]:
        run_desktop_tests()