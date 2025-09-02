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

from pathlib import Path
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest
import toml

from ansys.aedt.core.extensions.project.resources.via_design.src.template import CFG_PACKAGE_DIFF, CFG_PCB_RF
from ansys.aedt.core.extensions.project.resources.via_design.src.data_classes import ConfigModel


def test_load_config_1():
    """Test loading configuration from dictionary."""
    config = ConfigModel(**CFG_PACKAGE_DIFF)
    data_ = config.model_dump(exclude_none=True)


def test_load_config_2():
    """Test loading configuration from dictionary."""
    config = ConfigModel(**CFG_PCB_RF)
    data_ = config.model_dump(exclude_none=True)


def test_config_methods():
    config = ConfigModel(**CFG_PACKAGE_DIFF)
    assert "GND" in config.signals.keys()
    config.delete_signal("GND")
    assert "GND" not in config.signals.keys()
    config.add_signal(name="S1", data={
        'fanout_trace': [
            {
                "via_index": 0,
                "layer": "PKG_L1",
                "width": "0.05mm",
                "separation": "0.05mm",
                "clearance": "0.05mm",
                "incremental_path_dy": ["0.3mm", "0.3mm"],
                "end_cap_style": "flat",
                "flip_dx": False,
                "flip_dy": False,
                "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
            }
        ],
        "technology": "TYPE_1"
    }
                      )
    assert "S1" in config.signals.keys()

    assert "SIG_1" in config.differential_signals
    config.delete_differential_signal("SIG_1")
    assert "SIG_1" not in config.differential_signals
    config.add_differential_signal("S2", {
        "signals": ["SIG_1_P", "SIG_1_N"],
        "fanout_trace": [
            {
                "via_index": 0,
                "layer": "PKG_L1",
                "width": "0.05mm",
                "separation": "0.05mm",
                "clearance": "0.05mm",
                "incremental_path_dy": ["0.3mm", "0.3mm"],
                "end_cap_style": "flat",
                "flip_dx": False,
                "flip_dy": False,
                "port": {"horizontal_extent_factor": 6, "vertical_extent_factor": 4},
            }
        ],
        "technology": "TYPE_2",
    })
    assert "S2" in config.differential_signals
