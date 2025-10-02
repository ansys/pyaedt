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
from ansys.aedt.core.internal.desktop_sessions import (
    _desktop_sessions,
)
from ansys.aedt.core.internal.filesystem import Scratch
from tests.conftest import config, apply_global_configuration

local_path = Path(__file__).parent
sys.path.append(str(local_path))

# Check for the local config file, override defaults if found
local_config_file = Path(local_path) / "local_config.json"
if local_config_file.exists():
    try:
        with open(local_config_file) as f:
            local_config = json.load(f)
    except Exception:  # pragma: no cover
        local_config = {}
    config.update(local_config)

apply_global_configuration(config)

