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
  "test_desktops": true
}

"""
import gc
import json
import os
import shutil
import sys
import tempfile

from pyaedt import settings
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import inside_desktop
from pyaedt.generic.general_methods import is_ironpython

log_path = os.path.join(tempfile.gettempdir(), "test.log")
if os.path.exists(os.path.join(tempfile.gettempdir(), "test.log")):
    try:
        os.remove(log_path)
    except:
        pass
settings.logger_file_path = log_path
settings.enable_error_handler = False
settings.enable_desktop_logs = False
if is_ironpython:
    import _unittest_ironpython.conf_unittest as pytest
else:
    import pytest


local_path = os.path.dirname(os.path.realpath(__file__))

from pyaedt import Desktop
from pyaedt import Edb
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

test_project_name = "test_primitives"

sys.path.append(local_path)
from _unittest.launch_desktop_tests import run_desktop_tests

# Check for the local config file, otherwise use default desktop configuration
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    with open(local_config_file) as f:
        config = json.load(f)
else:
    default_version = "2022.2"
    if inside_desktop and "oDesktop" in dir(sys.modules["__main__"]):
        default_version = sys.modules["__main__"].oDesktop.GetVersion()[0:6]
    config = {
        "desktopVersion": default_version,
        "NonGraphical": True,
        "NewThread": True,
        "test_desktops": False,
        "build_machine": True,
        "skip_space_claim": False,
        "skip_circuits": False,
        "skip_edb": False,
        "skip_debug": False,
        "local": False,
        "use_grpc": False,
        "disable_sat_bounding_box": False,
    }
settings.use_grpc_api = config.get("use_grpc", False)
settings.non_graphical = config["NonGraphical"]
settings.disable_bounding_box_sat = config["disable_sat_bounding_box"]


class BasisTest(object):
    def my_setup(self):
        scratch_path = tempfile.gettempdir()
        self.local_scratch = Scratch(scratch_path)
        self.aedtapps = []
        self.edbapps = []

    def my_teardown(self):
        try:
            oDesktop = sys.modules["__main__"].oDesktop
        except Exception as e:
            oDesktop = None
        if oDesktop and not settings.non_graphical:
            oDesktop.ClearMessages("", "", 3)
        for edbapp in self.edbapps[::-1]:
            try:
                edbapp.close_edb()
            except:
                pass
        del self.edbapps
        for aedtapp in self.aedtapps[::-1]:
            try:
                aedtapp.close_project(None, False)
            except:
                pass
        del self.aedtapps
        shutil.rmtree(self.local_scratch.path, ignore_errors=True)

    def add_app(self, project_name=None, design_name=None, solution_type=None, application=None, subfolder=""):
        if "oDesktop" not in dir(sys.modules["__main__"]):
            desktop = Desktop(desktop_version, settings.non_graphical, new_thread)
            desktop.disable_autosave()
        if project_name:
            example_project = os.path.join(local_path, "example_models", subfolder, project_name + ".aedt")
            example_folder = os.path.join(local_path, "example_models", subfolder, project_name + ".aedb")
            if os.path.exists(example_project):
                self.test_project = self.local_scratch.copyfile(example_project)
            elif os.path.exists(example_project + "z"):
                example_project = example_project + "z"
                self.test_project = self.local_scratch.copyfile(example_project)
            else:
                self.test_project = os.path.join(self.local_scratch.path, project_name + ".aedt")
            if os.path.exists(example_folder):
                target_folder = os.path.join(self.local_scratch.path, project_name + ".aedb")
                self.local_scratch.copyfolder(example_folder, target_folder)
        else:
            self.test_project = None
        if not application:
            application = Hfss
        self.aedtapps.append(
            application(
                projectname=self.test_project,
                designname=design_name,
                solution_type=solution_type,
                specified_version=desktop_version,
            )
        )
        return self.aedtapps[-1]

    def add_edb(self, project_name=None, subfolder=""):
        if project_name:
            example_folder = os.path.join(local_path, "example_models", subfolder, project_name + ".aedb")
            if os.path.exists(example_folder):
                target_folder = os.path.join(self.local_scratch.path, project_name + ".aedb")
                self.local_scratch.copyfolder(example_folder, target_folder)
            else:
                target_folder = os.path.join(self.local_scratch.path, project_name + ".aedb")
        else:
            target_folder = os.path.join(self.local_scratch.path, generate_unique_name("TestEdb") + ".aedb")
        self.edbapps.append(
            Edb(
                target_folder,
                edbversion=desktop_version,
            )
        )
        return self.edbapps[-1]

    def teardown(self):
        """
        Could be redefined
        """
        pass

    def setup(self):
        """
        Could be redefined
        """
        pass


# Define desktopVersion explicitly since this is imported by other modules
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]


@pytest.fixture(scope="session", autouse=True)
def desktop_init():

    yield
    if not is_ironpython:
        try:
            oDesktop = sys.modules["__main__"].oDesktop
            pid = oDesktop.GetProcessID()
            os.kill(pid, 9)
        except:
            pass

    if config["test_desktops"]:
        run_desktop_tests()


@pytest.fixture
def clean_desktop_messages(desktop_init):
    """Clear all Desktop app messages."""
    desktop_init.logger.clear_messages(level=3)


@pytest.fixture
def clean_desktop(desktop_init):
    """Close all projects, but don't close Desktop app."""
    desktop_init.release_desktop(close_projects=True, close_on_exit=False)
    return desktop_init


@pytest.fixture
def hfss():
    """Create a new Hfss project."""
    # Be sure that the base class constructor "design" exposes oDesktop.
    hfss = Hfss()
    yield hfss
    hfss.close_project(hfss.project_name)
    gc.collect()
