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

from ansys.aedt.core.filtersolutions_core.attributes import DiplexerType
from ansys.aedt.core.filtersolutions_core.attributes import FilterClass
from ansys.aedt.core.filtersolutions_core.attributes import FilterType
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import config
from tests.system.filter_solutions.resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_lumped_source_resistance_30(self, lumped_design):
        assert lumped_design.topology.source_resistance == "50"
        lumped_design.topology.source_resistance = "30"
        assert lumped_design.topology.source_resistance == "30"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("source_resistance.ckt", "Lumped")

    def test_lumped_load_resistance_30(self, lumped_design):
        assert lumped_design.topology.load_resistance == "50"
        lumped_design.topology.load_resistance = "30"
        assert lumped_design.topology.load_resistance == "30"
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("laod_resistance.ckt", "Lumped")

    def test_lumped_current_source(self, lumped_design):
        assert lumped_design.topology.current_source is False
        lumped_design.topology.current_source = True
        assert lumped_design.topology.current_source
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.current_source = True
        assert info.value.args[0] == "Current Source topology is not applicable for diplexer filters"

    def test_lumped_first_shunt(self, lumped_design):
        assert lumped_design.topology.first_shunt
        lumped_design.topology.first_shunt = True
        assert lumped_design.topology.first_shunt
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("first_shunt.ckt", "Lumped")
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.first_shunt = True
        assert info.value.args[0] == "First Element topology is not applicable for diplexer filters"

    def test_lumped_first_series(self, lumped_design):
        assert lumped_design.topology.first_shunt
        lumped_design.topology.first_shunt = False
        assert lumped_design.topology.first_shunt is False
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("first_series.ckt", "Lumped")

    def test_lumped_bridge_t(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.bridge_t = True
        assert info.value.args[0] == "BridgeT topology is not applicable for this type of filter"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.bridge_t is False
        lumped_design.topology.bridge_t = True
        assert lumped_design.topology.bridge_t
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("bridge_t.ckt", "Lumped")

    def test_lumped_bridge_t_low(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.bridge_t_low = True
        assert info.value.args[0] == "BridgeT Low topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.HI_LO
        assert lumped_design.attributes.diplexer_type == DiplexerType.HI_LO
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.bridge_t_low is False
        lumped_design.topology.bridge_t_low = True
        assert lumped_design.topology.bridge_t_low
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("bridge_t_low.ckt", "Lumped")

    def test_lumped_bridge_t_high(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.bridge_t_high = True
        assert info.value.args[0] == "BridgeT High topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.HI_LO
        assert lumped_design.attributes.diplexer_type == DiplexerType.HI_LO
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.bridge_t_high is False
        lumped_design.topology.bridge_t_high = True
        assert lumped_design.topology.bridge_t_high
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("bridge_t_high.ckt", "Lumped")

    def test_lumped_equal_inductors(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.equal_inductors = True
        assert info.value.args[0] == "Equal Inductors topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.topology.equal_inductors is False
        lumped_design.topology.equal_inductors = True
        assert lumped_design.topology.equal_inductors
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("equal_inductors.ckt", "Lumped")

    def test_lumped_equal_capacitors(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.equal_capacitors = True
        assert info.value.args[0] == "Equal Capacitors topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.topology.zig_zag = True
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.zig_zag
        assert lumped_design.topology.min_cap is False
        assert lumped_design.topology.equal_capacitors is False
        lumped_design.topology.min_cap = True
        lumped_design.topology.equal_capacitors = True
        assert lumped_design.topology.min_cap
        assert lumped_design.topology.equal_capacitors
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("equal_capacitors.ckt", "Lumped")

    def test_lumped_equal_legs(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.equal_legs = True
        assert info.value.args[0] == "Equal Legs topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.topology.equal_legs is False
        lumped_design.topology.equal_legs = True
        assert lumped_design.topology.equal_legs
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("equal_legs.ckt", "Lumped")

    def test_lumped_high_low_pass(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.high_low_pass = True
        assert info.value.args[0] == "High Low pass topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.topology.high_low_pass is False
        lumped_design.topology.high_low_pass = True
        assert lumped_design.topology.high_low_pass
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("high_low_pass.ckt", "Lumped")

    def test_lumped_high_low_pass_min_ind(self, lumped_design):
        misspelled_error = "High Low pass with Minmum Inductors topology is not applicable for this type of filter"  # codespell:ignore  # noqa: E501
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.high_low_pass_min_ind = True
        if config["desktopVersion"] > "2025.1":
            assert (
                info.value.args[0]
                == "High Low pass with Minimum Inductors topology is not applicable for this type of filter"
            )
        else:
            assert info.value.args[0] == misspelled_error
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.high_low_pass_min_ind is False
        lumped_design.topology.high_low_pass_min_ind = True
        assert lumped_design.topology.high_low_pass_min_ind
        assert lumped_design.topology.netlist().splitlines() == read_resource_file(
            "high_low_pass_min_ind.ckt", "Lumped"
        )

    def test_lumped_zig_zag(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.zig_zag = True
        assert info.value.args[0] == "Zig Zag topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.zig_zag is False
        lumped_design.topology.zig_zag = True
        assert lumped_design.topology.zig_zag
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("zig_zag.ckt", "Lumped")

    def test_lumped_min_ind(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.min_ind = True
        if config["desktopVersion"] > "2025.1":
            assert info.value.args[0] == "Minimum Inductors topology is not applicable for this type of filter"
        else:
            assert info.value.args[0] == "Minimum Inductor topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.topology.zig_zag = True
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.zig_zag
        assert lumped_design.topology.min_ind
        lumped_design.topology.min_ind = True
        assert lumped_design.topology.min_ind
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("min_ind.ckt", "Lumped")

    def test_lumped_min_cap(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.min_cap = True
        if config["desktopVersion"] > "2025.1":
            assert info.value.args[0] == "Minimum Capacitors topology is not applicable for this type of filter"
        else:
            assert info.value.args[0] == "Minimum Capacitor topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.topology.zig_zag = True
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.zig_zag
        assert lumped_design.topology.min_cap is False
        lumped_design.topology.min_cap = True
        assert lumped_design.topology.min_cap
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("min_cap.ckt", "Lumped")

    def test_lumped_set_source_res(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.set_source_res = True
        if config["desktopVersion"] > "2025.1":
            assert info.value.args[0] == "Zig Zag Source Resistance topology is not applicable for this type of filter"
        else:
            assert info.value.args[0] == "Zig Zag Source topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.topology.zig_zag = True
        lumped_design.topology.set_source_res = False
        assert lumped_design.topology.set_source_res is False
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.zig_zag
        lumped_design.topology.set_source_res = True
        assert lumped_design.topology.set_source_res
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("set_source_res.ckt", "Lumped")

    def test_lumped_trap_topology(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.trap_topology = True
        assert info.value.args[0] == "Trap topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.topology.zig_zag = True
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.zig_zag
        assert lumped_design.topology.trap_topology is False
        lumped_design.topology.trap_topology = True
        assert lumped_design.topology.trap_topology
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("trap_topology.ckt", "Lumped")

    def test_lumped_node_cap_ground(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.node_cap_ground = True
        assert (
            info.value.args[0] == "Parasitic Capacitance to Ground topology is not applicable for this type of filter"
        )
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        assert lumped_design.topology.node_cap_ground is False
        lumped_design.topology.node_cap_ground = True
        assert lumped_design.topology.node_cap_ground
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("node_cap_ground.ckt", "Lumped")

    def test_lumped_match_impedance(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.match_impedance = True
        assert info.value.args[0] == "Automatic Matched Impedance topology is not applicable for this type of filter"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.topology.source_resistance = "75"
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        assert lumped_design.topology.source_resistance == "75"
        assert lumped_design.topology.match_impedance is False
        lumped_design.topology.match_impedance = True
        assert lumped_design.topology.match_impedance
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("match_impedance.ckt", "Lumped")

    def test_lumped_complex_termination(self, lumped_design):
        assert lumped_design.topology.complex_termination is False
        lumped_design.topology.complex_termination = True
        assert lumped_design.topology.complex_termination

    def test_complex_element_tune_enabled(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.topology.complex_element_tune_enabled = True
        if config["desktopVersion"] > "2025.1":
            assert info.value.args[0] == "The Complex Termination option is not enabled for this filter"
        else:
            assert info.value.args[0] == "The Butterworth filter does not have complex termination"
        lumped_design.topology.complex_termination = True
        assert lumped_design.topology.complex_element_tune_enabled
        lumped_design.topology.complex_element_tune_enabled = False
        assert lumped_design.topology.complex_element_tune_enabled is False

    def test_lumped_circuit_export(self, lumped_design):
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("netlist.ckt", "Lumped")

    def test_lumped_diplexer1_hi_lo(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.HI_LO
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_1
        assert lumped_design.attributes.diplexer_type == DiplexerType.HI_LO
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("diplexer1_hi_lo.ckt", "Lumped")

    def test_lumped_diplexer1_bp_1(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_1
        assert lumped_design.attributes.diplexer_type == DiplexerType.BP_1
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("diplexer1_bp_1.ckt", "Lumped")

    def test_lumped_diplexer1_bp_2(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_1
        assert lumped_design.attributes.diplexer_type == DiplexerType.BP_2
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("diplexer1_bp_2.ckt", "Lumped")

    def test_lumped_diplexer2_bp_bs(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_2
        lumped_design.attributes.diplexer_type = DiplexerType.BP_BS
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_2
        assert lumped_design.attributes.diplexer_type == DiplexerType.BP_BS
        assert lumped_design.topology.netlist().splitlines() == read_resource_file("diplexer2_bp_bs.ckt", "Lumped")

    def test_lumped_diplexer2_triplexer_1(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_2
        lumped_design.attributes.diplexer_type = DiplexerType.TRIPLEXER_1
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_2
        assert lumped_design.attributes.diplexer_type == DiplexerType.TRIPLEXER_1
        assert lumped_design.topology.netlist().splitlines() == read_resource_file(
            "diplexer2_triplexer_1.ckt", "Lumped"
        )

    def test_lumped_diplexer2_triplexer_2(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_2
        lumped_design.attributes.diplexer_type = DiplexerType.TRIPLEXER_2
        assert lumped_design.attributes.filter_class == FilterClass.DIPLEXER_2
        assert lumped_design.attributes.diplexer_type == DiplexerType.TRIPLEXER_2
        assert lumped_design.topology.netlist().splitlines() == read_resource_file(
            "diplexer2_triplexer_2.ckt", "Lumped"
        )
