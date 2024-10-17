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
import ansys.aedt.core
from ansys.aedt.core.filtersolutions_core.attributes import DiplexerType
from ansys.aedt.core.filtersolutions_core.attributes import FilterClass
from ansys.aedt.core.filtersolutions_core.attributes import FilterImplementation
from ansys.aedt.core.filtersolutions_core.attributes import FilterType
from ansys.aedt.core.generic.general_methods import is_linux
import pytest

from ..resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_lumped_generator_resistor_30(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.generator_resistor == "50"
        lumpdesign.topology.generator_resistor = "30"
        assert lumpdesign.topology.generator_resistor == "30"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("generator_resistor.ckt")

    def test_lumped_load_resistor_30(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.load_resistor == "50"
        lumpdesign.topology.load_resistor = "30"
        assert lumpdesign.topology.load_resistor == "30"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("laod_resistor.ckt")

    def test_lumped_current_source(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.current_source is False
        lumpdesign.topology.current_source = True
        assert lumpdesign.topology.current_source

    def test_lumped_first_shunt(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.first_shunt
        lumpdesign.topology.first_shunt = True
        assert lumpdesign.topology.first_shunt
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("first_shunt.ckt")

    def test_lumped_first_series(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.first_shunt
        lumpdesign.topology.first_shunt = False
        assert lumpdesign.topology.first_shunt is False
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("first_series.ckt")

    def test_lumped_bridge_t(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.bridge_t is False
        lumpdesign.topology.bridge_t = True
        assert lumpdesign.topology.bridge_t
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("bridge_t.ckt")

    def test_lumped_bridge_t_low(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
        lumpdesign.attributes.diplexer_type = DiplexerType.HI_LO
        assert lumpdesign.attributes.diplexer_type == DiplexerType.HI_LO
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.bridge_t_low is False
        lumpdesign.topology.bridge_t_low = True
        assert lumpdesign.topology.bridge_t_low
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("bridge_t_low.ckt")

    def test_lumped_bridge_t_high(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
        lumpdesign.attributes.diplexer_type = DiplexerType.HI_LO
        assert lumpdesign.attributes.diplexer_type == DiplexerType.HI_LO
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.bridge_t_high is False
        lumpdesign.topology.bridge_t_high = True
        assert lumpdesign.topology.bridge_t_high
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("bridge_t_high.ckt")

    def test_lumped_equal_inductors(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.topology.equal_inductors is False
        lumpdesign.topology.equal_inductors = True
        assert lumpdesign.topology.equal_inductors
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("equal_inductors.ckt")

    def test_lumped_equal_capacitors(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        lumpdesign.topology.zig_zag = True
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.zig_zag
        assert lumpdesign.topology.min_cap is False
        assert lumpdesign.topology.equal_capacitors is False
        lumpdesign.topology.min_cap = True
        lumpdesign.topology.equal_capacitors = True
        assert lumpdesign.topology.min_cap
        assert lumpdesign.topology.equal_capacitors
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("equal_capacitors.ckt")

    def test_lumped_equal_legs(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.topology.equal_legs is False
        lumpdesign.topology.equal_legs = True
        assert lumpdesign.topology.equal_legs
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("equal_legs.ckt")

    def test_lumped_high_low_pass(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.topology.high_low_pass is False
        lumpdesign.topology.high_low_pass = True
        assert lumpdesign.topology.high_low_pass
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("high_low_pass.ckt")

    def test_lumped_high_low_pass_min_ind(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.high_low_pass_min_ind is False
        lumpdesign.topology.high_low_pass_min_ind = True
        assert lumpdesign.topology.high_low_pass_min_ind
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("high_low_pass_min_ind.ckt")

    def test_lumped_zig_zag(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.zig_zag is False
        lumpdesign.topology.zig_zag = True
        assert lumpdesign.topology.zig_zag
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("zig_zag.ckt")

    def test_lumped_min_ind(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        lumpdesign.topology.zig_zag = True
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.zig_zag
        assert lumpdesign.topology.min_ind
        lumpdesign.topology.min_ind = True
        assert lumpdesign.topology.min_ind
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("min_ind.ckt")

    def test_lumped_min_cap(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        lumpdesign.topology.zig_zag = True
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.zig_zag
        assert lumpdesign.topology.min_cap is False
        lumpdesign.topology.min_cap = True
        assert lumpdesign.topology.min_cap
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("min_cap.ckt")

    def test_lumped_set_source_res(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        lumpdesign.topology.zig_zag = True
        lumpdesign.topology.set_source_res = False
        assert lumpdesign.topology.set_source_res is False
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.zig_zag
        lumpdesign.topology.set_source_res = True
        assert lumpdesign.topology.set_source_res
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("set_source_res.ckt")

    def test_lumped_trap_topology(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        lumpdesign.topology.zig_zag = True
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.zig_zag
        assert lumpdesign.topology.trap_topology is False
        lumpdesign.topology.trap_topology = True
        assert lumpdesign.topology.trap_topology
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("trap_topology.ckt")

    def test_lumped_node_cap_ground(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
        assert lumpdesign.topology.node_cap_ground is False
        lumpdesign.topology.node_cap_ground = True
        assert lumpdesign.topology.node_cap_ground
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("node_cap_ground.ckt")

    def test_lumped_match_impedance(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
        lumpdesign.topology.generator_resistor = "75"
        assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
        assert lumpdesign.topology.generator_resistor == "75"
        assert lumpdesign.topology.match_impedance is False
        lumpdesign.topology.match_impedance = True
        assert lumpdesign.topology.match_impedance
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("match_impedance.ckt")

    def test_lumped_complex_termination(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.complex_termination is False
        lumpdesign.topology.complex_termination = True
        assert lumpdesign.topology.complex_termination

    def test_complex_element_tune_enabled(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.topology.complex_termination = True
        assert lumpdesign.topology.complex_element_tune_enabled
        lumpdesign.topology.complex_element_tune_enabled = False
        assert lumpdesign.topology.complex_element_tune_enabled is False

    def test_lumped_circuit_export(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("netlist.ckt")

    def test_lumped_diplexer1_hi_lo(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
        lumpdesign.attributes.diplexer_type = DiplexerType.HI_LO
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
        assert lumpdesign.attributes.diplexer_type == DiplexerType.HI_LO
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("diplexer1_hi_lo.ckt")

    def test_lumped_diplexer1_bp_1(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
        lumpdesign.attributes.diplexer_type = DiplexerType.BP_1
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
        assert lumpdesign.attributes.diplexer_type == DiplexerType.BP_1
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("diplexer1_bp_1.ckt")

    def test_lumped_diplexer1_bp_2(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
        lumpdesign.attributes.diplexer_type = DiplexerType.BP_2
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
        assert lumpdesign.attributes.diplexer_type == DiplexerType.BP_2
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("diplexer1_bp_2.ckt")

    def test_lumped_diplexer2_bp_bs(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_2
        lumpdesign.attributes.diplexer_type = DiplexerType.BP_BS
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_2
        assert lumpdesign.attributes.diplexer_type == DiplexerType.BP_BS
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("diplexer2_bp_bs.ckt")

    def test_lumped_diplexer2_triplexer_1(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_2
        lumpdesign.attributes.diplexer_type = DiplexerType.TRIPLEXER_1
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_2
        assert lumpdesign.attributes.diplexer_type == DiplexerType.TRIPLEXER_1
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("diplexer2_triplexer_1.ckt")

    def test_lumped_diplexer2_triplexer_2(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_2
        lumpdesign.attributes.diplexer_type = DiplexerType.TRIPLEXER_2
        assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_2
        assert lumpdesign.attributes.diplexer_type == DiplexerType.TRIPLEXER_2
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("diplexer2_triplexer_2.ckt")
