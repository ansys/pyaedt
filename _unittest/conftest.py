"""
Unit Test Configuration Module
-------------------------------

Description
===========

This module contains the configuration and fixture for the pytest-based unit tests for pyaedt.

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
import time

import pytest

from pyaedt.generic.settings import settings

settings.enable_local_log_file = False
settings.enable_global_log_file = False
settings.number_of_grpc_api_retries = 6
settings.retry_n_times_time_interval = 0.5
settings.enable_error_handler = False
settings.enable_desktop_logs = False
settings.desktop_launch_timeout = 180


from pyaedt import Edb
from pyaedt import Hfss
from pyaedt.aedt_logger import pyaedt_logger
from pyaedt.desktop import Desktop
from pyaedt.desktop import _delete_objects
from pyaedt.generic.desktop_sessions import _desktop_sessions
from pyaedt.generic.filesystem import Scratch
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import inside_desktop
from pyaedt.misc.misc import list_installed_ansysem

local_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(local_path)

# Initialize default desktop configuration
default_version = "2023.2"
if "ANSYSEM_ROOT{}".format(default_version[2:].replace(".", "")) not in list_installed_ansysem():
    default_version = list_installed_ansysem()[0][12:].replace(".", "")
    default_version = "20{}.{}".format(default_version[:2], default_version[-1])
os.environ["ANSYSEM_FEATURE_SS544753_ICEPAK_VIRTUALMESHREGION_PARADIGM_ENABLE"] = "1"
if inside_desktop and "oDesktop" in dir(sys.modules["__main__"]):
    default_version = sys.modules["__main__"].oDesktop.GetVersion()[0:6]
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
    except:  # pragma: no cover
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
        print("Failed to create {}. Reason: {}".format(test_folder, e))

    yield test_folder

    try:
        shutil.rmtree(test_folder, ignore_errors=True)
    except Exception as e:
        print("Failed to delete {}. Reason: {}".format(test_folder, e))


@pytest.fixture(scope="module", autouse=True)
def local_scratch(init_scratch):
    tmp_path = init_scratch
    scratch = Scratch(tmp_path)
    yield scratch
    scratch.remove()


@pytest.fixture(scope="module", autouse=True)
def desktop():
    _delete_objects()
    keys = list(_desktop_sessions.keys())
    for key in keys:
        del _desktop_sessions[key]
    d = Desktop(desktop_version, NONGRAPHICAL, new_thread)
    d.odesktop.SetTempDirectory(tempfile.gettempdir())
    d.disable_autosave()
    d.odesktop.SetDesktopConfiguration("All")
    d.odesktop.SetSchematicEnvironment(0)
    yield d
    d.release_desktop(True, True)
    time.sleep(1)


@pytest.fixture(scope="module")
def add_app(local_scratch):
    def _method(
        project_name=None, design_name=None, solution_type=None, application=None, subfolder="", just_open=False
    ):
        if project_name and not just_open:
            example_project = os.path.join(local_path, "example_models", subfolder, project_name + ".aedt")
            example_folder = os.path.join(local_path, "example_models", subfolder, project_name + ".aedb")
            if os.path.exists(example_project):
                # Copy unit test project to scratch folder. Return full file path to the project without extension.
                test_project = local_scratch.copyfile(example_project)
            elif os.path.exists(example_project + "z"):
                example_project = example_project + "z"
                test_project = local_scratch.copyfile(example_project)
            else:
                test_project = os.path.join(local_scratch.path, project_name + ".aedt")
            if os.path.exists(example_folder):
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
                local_scratch.copyfolder(example_folder, target_folder)
        elif project_name and just_open:
            test_project = project_name
        else:
            test_project = None
        if not application:
            application = Hfss
        return application(
            projectname=test_project,
            designname=design_name,
            solution_type=solution_type,
            specified_version=desktop_version,
        )

    return _method


@pytest.fixture(scope="module")
def test_project_file(local_scratch):
    def _method(project_name=None, subfolder=None):
        if subfolder:
            project_file = os.path.join(local_path, "example_models", subfolder, project_name + ".aedt")
        else:
            project_file = os.path.join(local_scratch.path, project_name + ".aedt")
        if os.path.exists(project_file):
            return project_file
        else:
            return None

    return _method


@pytest.fixture(scope="module")
def add_edb(local_scratch):
    def _method(project_name=None, subfolder=""):
        if project_name:
            example_folder = os.path.join(local_path, "example_models", subfolder, project_name + ".aedb")
            if os.path.exists(example_folder):
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
                local_scratch.copyfolder(example_folder, target_folder)
            else:
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
        else:
            target_folder = os.path.join(local_scratch.path, generate_unique_name("TestEdb") + ".aedb")
        return Edb(
            target_folder,
            edbversion=desktop_version,
        )

    return _method
