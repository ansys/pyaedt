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

from ansys.aedt.core.filtersolutions_core.distributed_topology import TopologyType
from ansys.aedt.core.generic.general_methods import is_linux
from tests.conftest import config
from tests.system.filter_solutions.resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not applicable on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.2", reason="Skipped on versions earlier than 2025.2")
class TestClass:
    def test_distributed_capacitor_q_100(self, distributed_design):
        distributed_design.topology.topology_type = TopologyType.INDUCTOR_TRANSLATION
        assert distributed_design.parasitics.capacitor_q == "Inf"
        distributed_design.parasitics.capacitor_q = "100"
        assert distributed_design.parasitics.capacitor_q == "100"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "capacitor_q_100.ckt", "Distributed"
        )

    def test_distributed_capacitor_rs_1(self, distributed_design):
        assert distributed_design.parasitics.capacitor_rs == "0"
        distributed_design.parasitics.capacitor_rs = "1"
        assert distributed_design.parasitics.capacitor_rs == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "capacitor_rs_1.ckt", "Distributed"
        )

    def test_distributed_capacitor_rp_1000(self, distributed_design):
        assert distributed_design.parasitics.capacitor_rp == "Inf"
        distributed_design.parasitics.capacitor_rp = "1000"
        assert distributed_design.parasitics.capacitor_rp == "1000"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "capacitor_rp_1000.ckt", "Distributed"
        )

    def test_distributed_capacitor_ls_1n(self, distributed_design):
        assert distributed_design.parasitics.capacitor_ls == "0"
        distributed_design.parasitics.capacitor_ls = "1n"
        assert distributed_design.parasitics.capacitor_ls == "1n"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "capacitor_ls_1n.ckt", "Distributed"
        )

    def test_distributed_inductor_q_100(self, distributed_design):
        assert distributed_design.parasitics.inductor_q == "Inf"
        distributed_design.parasitics.inductor_q = "100"
        assert distributed_design.parasitics.inductor_q == "100"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "inductor_q_100.ckt", "Distributed"
        )

    def test_distributed_inductor_rs_1(self, distributed_design):
        assert distributed_design.parasitics.inductor_rs == "0"
        distributed_design.parasitics.inductor_rs = "1"
        assert distributed_design.parasitics.inductor_rs == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "inductor_rs_1.ckt", "Distributed"
        )

    def test_distributed_inductor_rp_1000(self, distributed_design):
        assert distributed_design.parasitics.inductor_rp == "Inf"
        distributed_design.parasitics.inductor_rp = "1000"
        assert distributed_design.parasitics.inductor_rp == "1000"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "inductor_rp_1000.ckt", "Distributed"
        )

    def test_distributed_inductor_cp_1n(self, distributed_design):
        assert distributed_design.parasitics.inductor_cp == "0"
        distributed_design.parasitics.inductor_cp = "1n"
        assert distributed_design.parasitics.inductor_cp == "1n"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "inductor_cp_1n.ckt", "Distributed"
        )

    def test_line_odd_resistance_1(self, distributed_design):
        assert distributed_design.parasitics.line_odd_resistance == "0"
        distributed_design.parasitics.line_odd_resistance = "1"
        assert distributed_design.parasitics.line_odd_resistance == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "line_odd_resistance_1.ckt", "Distributed"
        )

    def test_line_even_resistance_1(self, distributed_design):
        assert distributed_design.parasitics.line_even_resistance == "0"
        distributed_design.parasitics.line_even_resistance = "1"
        assert distributed_design.parasitics.line_even_resistance == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "line_even_resistance_1.ckt", "Distributed"
        )

    def test_line_odd_conductance_1(self, distributed_design):
        assert distributed_design.parasitics.line_odd_conductance == "0"
        distributed_design.parasitics.line_odd_conductance = "1"
        assert distributed_design.parasitics.line_odd_conductance == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "line_odd_conductance_1.ckt", "Distributed"
        )

    def test_line_even_conductance_1(self, distributed_design):
        assert distributed_design.parasitics.line_even_conductance == "0"
        distributed_design.parasitics.line_even_conductance = "1"
        assert distributed_design.parasitics.line_even_conductance == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "line_even_conductance_1.ckt", "Distributed"
        )

    def test_line_min_segment_lengths_1(self, distributed_design):
        assert distributed_design.parasitics.line_min_segment_lengths == "0"
        distributed_design.parasitics.line_min_segment_lengths = "1"
        assert distributed_design.parasitics.line_min_segment_lengths == "1"
        assert distributed_design.topology.netlist().splitlines() == read_resource_file(
            "line_min_segment_lengths_1.ckt", "Distributed"
        )
