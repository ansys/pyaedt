# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import pytest

import ansys.aedt.core
import ansys.aedt.core.filtersolutions
import ansys.aedt.core.filtersolutions_core
from ansys.aedt.core.filtersolutions_core.attributes import FilterType
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import DESKTOP_VERSION
from tests.system.filter_solutions.test_filter import test_transmission_zeros


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_dll_path(self):
        assert os.path.exists(ansys.aedt.core.filtersolutions_core._dll_interface().dll_path)

    def test_version(self):
        assert ansys.aedt.core.filtersolutions_core.api_version() == DESKTOP_VERSION

    def test_string_to_enum(self):
        assert (
            ansys.aedt.core.filtersolutions_core._dll_interface().string_to_enum(FilterType, "gaussian")
            == FilterType.GAUSSIAN
        )

    def test_enum_to_string(self):
        assert ansys.aedt.core.filtersolutions_core._dll_interface().enum_to_string(FilterType.GAUSSIAN) == "gaussian"

    def test_raise_error(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.row(0)
        assert info.value.args[0] == test_transmission_zeros.TestClass.no_transmission_zero_msg

    def test_version_exception(self):
        with pytest.raises(ValueError) as info:
            ansys.aedt.core.filtersolutions_core._dll_interface("2025.0")
            if ansys.aedt.core.filtersolutions_core._dll_interface() is None:
                assert info.value.args[0] == "Specified version 2025.0 is not installed on your system"
