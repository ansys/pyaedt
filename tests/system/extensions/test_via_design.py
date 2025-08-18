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

from unittest.mock import patch

import pytest
import toml

from ansys.aedt.core.extensions.project.via_design import EXPORT_EXAMPLES
from ansys.aedt.core.extensions.project.via_design import ViaDesignExtension
from ansys.aedt.core.generic.settings import is_linux
from tests.system.extensions.conftest import config
from ansys.aedt.core.extensions.project.resources.via_design.src.template import CFG_PACKAGE_DIFF
from ansys.aedt.core.extensions.project.resources.via_design.src.data_classes import ConfigModel


def test_batch(tmp_path):
    from ansys.aedt.core.extensions.project.via_design import batch
    cfg = ConfigModel(**CFG_PACKAGE_DIFF)
    json_str = cfg.model_dump_json()
    file = tmp_path / "config.json"
    file.write_text(json_str, encoding="utf-8")
    assert batch(file)


def test_call_back_create_design():
    extension = ViaDesignExtension(withdraw=True)
    assert extension.create_design()
