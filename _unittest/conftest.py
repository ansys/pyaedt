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
import os
import shutil
import json
import gc
import sys

if "IronPython" in sys.version or ".NETFramework" in sys.version:
    import _unittest_ironpython.conf_unittest as pytest
else:
    import pytest
    if "UNITTEST_CURRENT_TEST" in os.environ:
        os.environ.pop("UNITTEST_CURRENT_TEST")

local_path = os.path.dirname(os.path.realpath(__file__))

from pyaedt import Desktop
# Import required modules
from pyaedt import Hfss
from pyaedt.application.Design import DesignCache
from pyaedt.generic.filesystem import Scratch
test_project_name = "test_primitives"

local_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(local_path)
from launch_desktop_tests import run_desktop_tests

# set scratch path and create it if necessary
scratch_path = tempfile.gettempdir()
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
        "build_machine": True,
        "skip_space_claim": False,
        "skip_circuits": False,
        "skip_edb": False,
        "skip_debug": False
    }
    config["local"] = False


class BasisTest:

    def setup_class(self, project_name=None, design_name=None, solution_type=None, application=None):

        with Scratch(scratch_path) as self.local_scratch:
            if project_name:
                example_project = os.path.join(local_path, 'example_models', project_name + '.aedt')
                if os.path.exists(example_project):
                    self.test_project = self.local_scratch.copyfile(example_project)
                else:
                    self.test_project = None
            else:
                self.test_project = None
            if not application:
                application = Hfss

            self.aedtapp = application(projectname=self.test_project, designname=design_name,
                                           solution_type=solution_type, specified_version=desktop_version,
                                           AlwaysNew=new_thread, NG=non_graphical)
            #TODO do we need this ?
            if project_name:
                if design_name:
                    self.aedtapp.design_name = design_name

            self.cache = DesignCache(self.aedtapp)

    def teardown_class(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

# Define desktopVersion explicitly since this is imported by other modules
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]
non_graphical = config["NonGraphical"]

@pytest.fixture(scope='session', autouse=True)
def desktop_init():
    desktop = Desktop(desktop_version, non_graphical, new_thread)
    desktop.disable_autosave()
    yield desktop

    # If new_thread is set to false by a local_config, then don't close the desktop.
    # Intended for local debugging purposes only
    if new_thread:
        desktop.force_close_desktop()
    p = [x[0] for x in os.walk(scratch_path) if "scratch" in x[0]]
    #p = pathlib.Path(scratch_path).glob('**/scratch*')
    for folder in p:
        shutil.rmtree(folder, ignore_errors=True)

    if config["test_desktops"]:
        run_desktop_tests()


from functools import wraps

def pyaedt_unittest_check_desktop_error(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        #args[0].aedtapp._messenger("Test Function Here")
        args[0].cache.update()
        ret_val = func(*args, **kwargs)
        try:
            pass
        except Exception as e:
            pytest.exit("Desktop Crashed - Aborting the test!")
        args[0].cache.update()
        #model_report = args[0].aedtapp.modeler.primitives.model_consistency_report
        #assert not model_report["Missing Objects"]
        #assert not model_report["Non-Existent Objects"]
        assert args[0].cache.no_new_errors
        return ret_val

    return inner_function


#
# def pyaedt_unittest_same_design(func):
#     @wraps(func)
#     def inner_function(*args, **kwargs):
#         args[0].cache.update()
#         func(*args, **kwargs)
#         try:
#             args[0].aedtapp.design_name
#         except Exception as e:
#             pytest.exit("Desktop Crashed - Aborting the test!")
#         args[0].cache.update()
#         assert args[0].cache.no_new_errors
#         assert args[0].cache.no_change
#
#     return inner_function
#
# def pyaedt_unittest_duplicate_design(func):
#     @wraps(func)
#     def inner_function(*args, **kwargs):
#         time.sleep(0.5)
#         args[0].aedtapp.duplicate_design(label=generate_unique_name("pytest"))
#         time.sleep(0.5)
#         args[0].cache.update()
#         func(*args, **kwargs)
#         try:
#             if args[0].aedtapp.design_name:
#                 args[0].aedtapp.delete_design()
#         except Exception as e:
#             pytest.exit("Desktop Crashed - Aborting the test!")
#         args[0].cache.update()
#         assert args[0].cache.no_new_errors
#
#     return inner_function
#
# def pyaedt_unittest_new_design(func):
#     @wraps(func)
#     def inner_function(*args, **kwargs):
#         args[0].aedtapp.insert_design(design_name=generate_unique_name("pytest"))
#         args[0].cache.update()
#         func(*args, **kwargs)
#         try:
#             if args[0].aedtapp.design_name:
#                 args[0].aedtapp.delete_design()
#         except Exception as e:
#             pytest.exit("Desktop Crashed - Aborting the test!")
#         args[0].cache.update()
#         assert args[0].cache.no_new_errors
#
#     return inner_function
