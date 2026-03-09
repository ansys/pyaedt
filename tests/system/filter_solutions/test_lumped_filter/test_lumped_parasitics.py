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

import pytest

from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import config
from tests.system.filter_solutions.resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_lumped_capacitor_q(self, lumped_design):
        assert lumped_design.parasitics.capacitor_q == "Inf"
        lumped_design.parasitics.capacitor_q = "100"
        assert lumped_design.parasitics.capacitor_q == "100"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("capacitor_q.ckt", "Lumped")

    def test_lumped_capacitor_rs(self, lumped_design):
        assert lumped_design.parasitics.capacitor_rs == "0"
        lumped_design.parasitics.capacitor_rs = "1"
        assert lumped_design.parasitics.capacitor_rs == "1"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("capacitor_rs.ckt", "Lumped")

    def test_lumped_capacitor_rp(self, lumped_design):
        assert lumped_design.parasitics.capacitor_rp == "Inf"
        lumped_design.parasitics.capacitor_rp = "1000"
        assert lumped_design.parasitics.capacitor_rp == "1000"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("capacitor_rp.ckt", "Lumped")

    def test_lumped_capacitor_ls(self, lumped_design):
        assert lumped_design.parasitics.capacitor_ls == "0"
        lumped_design.parasitics.capacitor_ls = "1n"
        assert lumped_design.parasitics.capacitor_ls == "1n"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("capacitor_ls.ckt", "Lumped")

    def test_lumped_inductor_q(self, lumped_design):
        assert lumped_design.parasitics.inductor_q == "Inf"
        lumped_design.parasitics.inductor_q = "100"
        assert lumped_design.parasitics.inductor_q == "100"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("inductor_q.ckt", "Lumped")

    def test_lumped_inductor_rs(self, lumped_design):
        assert lumped_design.parasitics.inductor_rs == "0"
        lumped_design.parasitics.inductor_rs = "1"
        assert lumped_design.parasitics.inductor_rs == "1"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("inductor_rs.ckt", "Lumped")

    def test_lumped_inductor_rp(self, lumped_design):
        assert lumped_design.parasitics.inductor_rp == "Inf"
        lumped_design.parasitics.inductor_rp = "1000"
        assert lumped_design.parasitics.inductor_rp == "1000"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("inductor_rp.ckt", "Lumped")

    def test_lumped_inductor_cp(self, lumped_design):
        assert lumped_design.parasitics.inductor_cp == "0"
        lumped_design.parasitics.inductor_cp = "1n"
        assert lumped_design.parasitics.inductor_cp == "1n"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("inductor_cp.ckt", "Lumped")
