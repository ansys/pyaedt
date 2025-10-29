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
  "desktopVersion": "2025.2",
  "NonGraphical": false,
  "NewThread": false,
}

"""

import gc
import os
import sys
import tempfile
import time

import pytest

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions
from tests.conftest import config
from tests.conftest import logger

settings.objects_lazy_load = False


def _delete_objects():
    settings.remote_api = False
    pyaedt_logger.remove_all_project_file_logger()
    try:
        del sys.modules["glob"]
    except Exception:
        logger.debug("Failed to delete glob module")
    gc.collect()


@pytest.fixture(scope="module", autouse=True)
def desktop():
    _delete_objects()
    keys = list(_desktop_sessions.keys())
    for key in keys:
        del _desktop_sessions[key]
    d = Desktop(config["desktopVersion"], config["NonGraphical"], config["NewThread"])
    d.odesktop.SetTempDirectory(tempfile.gettempdir())
    d.disable_autosave()
    if config["desktopVersion"] > "2022.2":
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
