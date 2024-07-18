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

from _unittest.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_minimum_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.minimum_frequency == "200 MHz"
        design.graph_setup.minimum_frequency = "500 MHz"
        assert design.graph_setup.minimum_frequency == "500 MHz"

    def test_maximum_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.maximum_frequency == "5 GHz"
        design.graph_setup.maximum_frequency = "2 GHz"
        assert design.graph_setup.maximum_frequency == "2 GHz"

    def test_minimum_time(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.minimum_time == "0"
        design.graph_setup.minimum_time = "5 ns"
        assert design.graph_setup.minimum_time == "5 ns"

    def test_maximum_time(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.maximum_time == "10n"
        design.graph_setup.maximum_time = "8 ns"
        assert design.graph_setup.maximum_time == "8 ns"
