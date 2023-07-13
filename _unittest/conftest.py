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
import datetime
import gc
import json
import os
import shutil
import sys
import tempfile
import time

from pyaedt import pyaedt_logger
from pyaedt import settings
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import inside_desktop
from pyaedt.generic.general_methods import is_ironpython

# from pyaedt.generic.general_methods import is_windows

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
from pyaedt.misc.misc import list_installed_ansysem

test_project_name = "test_primitives"

sys.path.append(local_path)

# Initialize default desktop configuration
default_version = "2023.1"
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
    "test_desktops": False,
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
    local_config = {}
    with open(local_config_file) as f:
        local_config = json.load(f)
    config.update(local_config)

settings.non_graphical = config["NonGraphical"]
settings.disable_bounding_box_sat = config["disable_sat_bounding_box"]
settings.enable_local_log_file = False
settings.enable_global_log_file = False
settings.number_of_grpc_api_retries = 6
test_folder = "unit_test" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
for filename in os.listdir(tempfile.gettempdir()):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        if os.path.isfile(file_path) and "tmp" in file_path:
            os.unlink(file_path)
        if (
            os.path.isdir(file_path)
            and "pyaedt" in file_path
            or "scratch" in file_path
            or file_path.startswith("_")
            or ".aedb" in file_path
        ):
            shutil.rmtree(file_path, ignore_errors=True)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))
scratch_path = os.path.join(tempfile.gettempdir(), test_folder)
if not os.path.exists(scratch_path):
    try:
        os.makedirs(scratch_path)
    except:
        pass

logger = pyaedt_logger

NONGRAPHICAL = settings.non_graphical


class BasisTest(object):
    def my_setup(self, launch_desktop=True):
        scratch_path = tempfile.gettempdir()
        self.local_scratch = Scratch(scratch_path)
        self.aedtapps = []
        self.edbapps = []
        self._main = sys.modules["__main__"]
        self.desktop = None
        self._main.desktop_pid = 0
        settings.use_grpc_api = config.get("use_grpc", True)
        if launch_desktop:
            self.desktop = Desktop(desktop_version, NONGRAPHICAL, new_thread)
            self.desktop.disable_autosave()
            self._main.desktop_pid = self.desktop.odesktop.GetProcessID()

    def my_teardown(self):
        try:
            logger.remove_all_project_file_logger()
        except:
            pass
        for edbapp in self.edbapps[::-1]:
            try:
                edbapp.close_edb()
            except:
                pass
        if self.desktop and not is_ironpython:
            self.desktop.release_desktop(False, True)
            try:
                os.kill(self._main.desktop_pid, 9)
            except:
                pass
            try:
                del self._main.desktop_pid
            except:
                pass
        elif self.desktop:
            try:
                oDesktop = self._main.oDesktop
                proj_list = oDesktop.GetProjectList()
            except Exception as e:
                oDesktop = None
                proj_list = []
            if oDesktop and not settings.non_graphical:
                oDesktop.ClearMessages("", "", 3)
            if proj_list:
                for proj in proj_list:
                    try:
                        oDesktop.CloseProject(proj)
                    except:
                        pass
        del self.edbapps
        del self.aedtapps
        self.desktop = None
        try:
            shutil.rmtree(self.local_scratch.path, ignore_errors=True)
        except:
            pass

    def add_app(self, project_name=None, design_name=None, solution_type=None, application=None, subfolder=""):
        # if "oDesktop" not in dir(self._main):

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

    def teardown_method(self):
        """
        Could be redefined
        """
        pass

    def setup_method(self):
        """
        Could be redefined
        """
        pass


# Define desktopVersion explicitly since this is imported by other modules
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]
settings.desktop_launch_timeout = 180


@pytest.fixture(scope="session", autouse=True)
def desktop_init():
    _main = sys.modules["__main__"]

    if is_ironpython:
        desktop = Desktop(desktop_version, settings.non_graphical, new_thread)
        _main.desktop_pid = desktop.odesktop.GetProcessID()
    yield
    if is_ironpython:
        desktop.release_desktop(True, True)
        del desktop
    try:
        os.kill(_main.desktop_pid, 9)
    except:
        pass
    try:
        import pythonnet

        pythonnet.unload()
    except:
        pass
    gc.collect()


@pytest.fixture(scope="function", autouse=True)
def method_init():
    time.sleep(0.01)
    yield
    time.sleep(0.01)
    gc.collect()


@pytest.fixture(scope="module", autouse=True)
def class_init():
    time.sleep(0.5)
    yield
    time.sleep(0.5)
