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
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import toml

from ansys.aedt.core.extensions.project.via_design import ViaDesignExtension
from ansys.aedt.core.extensions.project.resources.via_design.src.data_classes import ConfigModel
from ansys.aedt.core.extensions.project.resources.via_design.src.template import CFG_PACKAGE_DIFF, CFG_PCB_RF
from ansys.aedt.core.generic.settings import is_linux
from tests.system.extensions.conftest import config


def test_via_design_create_design_from_example_1():
    """Test the creation of a design from examples in the via design extension."""
    extension = ViaDesignExtension(withdraw=True)
    extension.config_model = ConfigModel(**CFG_PACKAGE_DIFF)
    assert extension.create_design()
    extension.root.destroy()


def test_via_design_create_design_from_example_2():
    """Test the creation of a design from examples in the via design extension."""
    extension = ViaDesignExtension(withdraw=True)
    extension.config_model = ConfigModel(**CFG_PCB_RF)
    assert extension.create_design()
    extension.root.destroy()