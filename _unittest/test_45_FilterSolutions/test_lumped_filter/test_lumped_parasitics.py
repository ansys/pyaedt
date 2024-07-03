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

from ..resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_lumped_capacitor_q(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.capacitor_q == "Inf"
        lumpdesign.parasitics.capacitor_q = "100"
        assert lumpdesign.parasitics.capacitor_q == "100"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("capacitor_q.ckt")

    def test_lumped_capacitor_rs(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.capacitor_rs == "0"
        lumpdesign.parasitics.capacitor_rs = "1"
        assert lumpdesign.parasitics.capacitor_rs == "1"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("capacitor_rs.ckt")

    def test_lumped_capacitor_rp(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.capacitor_rp == "Inf"
        lumpdesign.parasitics.capacitor_rp = "1000"
        assert lumpdesign.parasitics.capacitor_rp == "1000"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("capacitor_rp.ckt")

    def test_lumped_capacitor_ls(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.capacitor_ls == "0"
        lumpdesign.parasitics.capacitor_ls = "1n"
        assert lumpdesign.parasitics.capacitor_ls == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("capacitor_ls.ckt")

    def test_lumped_inductor_q(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.inductor_q == "Inf"
        lumpdesign.parasitics.inductor_q = "100"
        assert lumpdesign.parasitics.inductor_q == "100"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("inductor_q.ckt")

    def test_lumped_inductor_rs(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.inductor_rs == "0"
        lumpdesign.parasitics.inductor_rs = "1"
        assert lumpdesign.parasitics.inductor_rs == "1"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("inductor_rs.ckt")

    def test_lumped_inductor_rp(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.inductor_rp == "Inf"
        lumpdesign.parasitics.inductor_rp = "1000"
        assert lumpdesign.parasitics.inductor_rp == "1000"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("inductor_rp.ckt")

    def test_lumped_inductor_cp(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.parasitics.inductor_cp == "0"
        lumpdesign.parasitics.inductor_cp = "1n"
        assert lumpdesign.parasitics.inductor_cp == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("inductor_cp.ckt")
