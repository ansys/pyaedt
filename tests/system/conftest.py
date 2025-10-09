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

import os
import tempfile

import pytest

from ansys.aedt.core import Desktop
from ansys.aedt.core.edb import Edb
from ansys.aedt.core.filtersolutions import DistributedDesign
from ansys.aedt.core.filtersolutions import LumpedDesign
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.hfss import Hfss
from tests import TESTS_GENERAL_PATH
from tests import TESTS_SOLVERS_PATH
from tests import TESTS_VISUALIZATION_PATH
from tests import TESTS_EXTENSIONS_PATH
from tests import TESTS_FILTER_SOLUTIONS_PATH
from tests.conftest import NONGRAPHICAL
from tests.conftest import config

# Initialize default configuration - shared across all test types
os.environ["ANSYSEM_FEATURE_SS544753_ICEPAK_VIRTUALMESHREGION_PARADIGM_ENABLE"] = "1"


@pytest.fixture(scope="module", autouse=True)
def desktop():
    d = Desktop(config["desktopVersion"], NONGRAPHICAL, config["NewThread"])
    d.odesktop.SetTempDirectory(tempfile.gettempdir())
    d.disable_autosave()

    yield d
    try:
        d.close_desktop()
    except Exception:
        return False


def _get_test_path_from_caller():
    """Determine the appropriate test path based on the calling test's location."""
    import inspect
    
    # Get the calling frame (skip this function and the fixture)
    frame = inspect.currentframe()
    try:
        # Go up the call stack to find the test file
        while frame:
            filename = frame.f_code.co_filename
            if 'test_' in os.path.basename(filename) and 'tests' in filename:
                if 'visualization' in filename:
                    return TESTS_VISUALIZATION_PATH
                elif 'solvers' in filename:
                    return TESTS_SOLVERS_PATH
                elif 'extensions' in filename:
                    return TESTS_EXTENSIONS_PATH
                elif 'filter_solutions' in filename:
                    return TESTS_FILTER_SOLUTIONS_PATH
                else:
                    return TESTS_GENERAL_PATH
            frame = frame.f_back
    finally:
        del frame
    
    # Default fallback
    return TESTS_GENERAL_PATH


@pytest.fixture(scope="module")
def add_app(local_scratch):
    def _method(
        project_name=None, design_name=None, solution_type=None, application=None, subfolder="", just_open=False
    ):
        if project_name and not just_open:
            # Dynamically determine the correct test path
            test_path = _get_test_path_from_caller()
            
            example_project = os.path.join(test_path, "example_models", subfolder, project_name + ".aedt")
            example_folder = os.path.join(test_path, "example_models", subfolder, project_name + ".aedb")
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

        args = {
            "project": test_project,
            "design": design_name,
            "version": config["desktopVersion"],
            "non_graphical": NONGRAPHICAL,
            "remove_lock": True,
        }
        if solution_type:
            args["solution_type"] = solution_type
        return application(**args)

    return _method


@pytest.fixture(scope="module")
def test_project_file(local_scratch):
    def _method(project_name=None, subfolder=None):
        if subfolder:
            # Dynamically determine the correct test path
            test_path = _get_test_path_from_caller()
            project_file = os.path.join(test_path, "example_models", subfolder, project_name + ".aedt")
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
            # Dynamically determine the correct test path
            test_path = _get_test_path_from_caller()
            example_folder = os.path.join(test_path, "example_models", subfolder, project_name + ".aedb")
            if os.path.exists(example_folder):
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
                local_scratch.copyfolder(example_folder, target_folder)
            else:
                target_folder = os.path.join(local_scratch.path, project_name + ".aedb")
        else:
            target_folder = os.path.join(local_scratch.path, generate_unique_name("TestEdb") + ".aedb")
        return Edb(
            target_folder,
            edbversion=config["desktopVersion"],
        )

    return _method


@pytest.fixture(scope="function")
def lumped_design():
    """Fixture for creating a LumpedDesign object."""
    return LumpedDesign(config["desktopVersion"])


@pytest.fixture(scope="function")
def distributed_design():
    """Fixture for creating a DistributedDesign object."""
    return DistributedDesign(config["desktopVersion"])
