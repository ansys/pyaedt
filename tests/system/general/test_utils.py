# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Test utility functions of PyAEDT.
"""

from pathlib import Path

from ansys.aedt.core.generic.settings import Settings


def test_settings_load_default_yaml(tmp_path):
    """Test loading the default YAML file in docs/source/Resources."""
    default_settings = Settings()

    settings = Settings()
    project_root = Path(__file__).resolve().parents[3]
    pyaedt_settings_path = project_root / "doc" / "source" / "Resources" / "pyaedt_settings.yaml"
    settings.load_yaml_configuration(str(pyaedt_settings_path))

    # Compare everything except for the global log filename which is generated randomly
    assert {
        key: value for key, value in default_settings.__dict__.items() if key != "_Settings__global_log_file_name"
    } == {key: value for key, value in settings.__dict__.items() if key != "_Settings__global_log_file_name"}
