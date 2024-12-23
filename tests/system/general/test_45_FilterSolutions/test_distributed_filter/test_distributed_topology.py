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

import ansys.aedt.core
import ansys.aedt.core.filtersolutions
from ansys.aedt.core.filtersolutions_core.attributes import FilterClass
from ansys.aedt.core.filtersolutions_core.attributes import FilterType
from ansys.aedt.core.filtersolutions_core.distributed_topology import TapPosition
from ansys.aedt.core.filtersolutions_core.distributed_topology import TopologyList
from ansys.aedt.core.generic.general_methods import is_linux
import pytest

from tests.system.general.conftest import config

from ..resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_distributed_generator_resistor_30(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        assert design.topology.generator_resistor == "50"
        design.topology.generator_resistor = "30"
        assert design.topology.generator_resistor == "30"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "generator_resistor.ckt", "Distributed"
        )

    def test_distributed_load_resistor_30(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        assert design.topology.load_resistor == "50"
        design.topology.load_resistor = "30"
        assert design.topology.load_resistor == "30"
        assert design.topology.circuit_response().splitlines() == read_resource_file("load_resistor.ckt", "Distributed")

    def test_distributed_first_shunt(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        assert design.topology.first_shunt
        design.topology.first_shunt = True
        assert design.topology.first_shunt
        assert design.topology.circuit_response().splitlines() == read_resource_file("first_shunt.ckt", "Distributed")

    def test_distributed_first_series(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        assert design.topology.first_shunt
        design.topology.first_shunt = False
        assert design.topology.first_shunt is False
        assert design.topology.circuit_response().splitlines() == read_resource_file("first_series.ckt", "Distributed")

    def test_distributed_first_fat(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.first_fat = True
        assert info.value.args[0] == "The First Segment Fat or Thin property is not supported for the selected topology"
        design.topology.topology_list = TopologyList.STEPPED_IMPEDANCE
        assert design.topology.first_fat
        design.topology.first_fat = True
        assert design.topology.first_fat
        assert design.topology.circuit_response().splitlines() == read_resource_file("first_fat.ckt", "Distributed")

    def test_distributed_first_thin(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.first_fat = False
        assert info.value.args[0] == "The First Segment Fat or Thin property is not supported for the selected topology"
        design.topology.topology_list = TopologyList.STEPPED_IMPEDANCE
        assert design.topology.first_fat
        design.topology.first_fat = False
        assert design.topology.first_fat is False
        assert design.topology.circuit_response().splitlines() == read_resource_file("first_thin.ckt", "Distributed")

    def test_distributed_use_series_caps(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.use_series_caps = True
        assert info.value.args[0] == "The Series Caps property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        assert design.topology.use_series_caps is False
        design.topology.use_series_caps = True
        assert design.topology.use_series_caps
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "use_series_caps.ckt", "Distributed"
        )

    def test_distributed_combine_stubs(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.combine_stubs = True
        assert info.value.args[0] == "The Combine Stubs property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        assert design.topology.combine_stubs is False
        design.topology.combine_stubs = True
        assert design.topology.combine_stubs
        assert design.topology.circuit_response().splitlines() == read_resource_file("combine_stubs.ckt", "Distributed")

    def test_use_coupled_lines(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.use_coupled_lines = True
        assert info.value.args[0] == "The Coupled Lines property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert design.topology.use_coupled_lines is False
        design.topology.use_coupled_lines = True
        assert design.topology.use_coupled_lines
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "use_coupled_lines.ckt", "Distributed"
        )

    def test_equal_width_approx(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.equal_width_approx = True
        assert info.value.args[0] == "The Equal Width property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.INTERDIGITAL
        assert design.topology.equal_width_approx
        design.topology.equal_width_approx = False
        assert design.topology.equal_width_approx is False
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "equal_width_approx.ckt", "Distributed"
        )

    def test_open_stub_ground(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.open_stub_ground = True
        assert info.value.args[0] == "The Open Stub Ground property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_STOP
        design.topology.topology_list = TopologyList.NOTCH_RESONATORS
        assert design.topology.open_stub_ground is False
        design.topology.open_stub_ground = True
        assert design.topology.open_stub_ground
        design.topology.open_stub_ground = False
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "open_stub_ground.ckt", "Distributed"
        )

    def test_left_ground_side(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.left_ground_side = True
        assert info.value.args[0] == "The Left Ground Side property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_STOP
        design.topology.topology_list = TopologyList.NOTCH_RESONATORS
        assert design.topology.left_ground_side
        design.topology.left_ground_side = False
        assert design.topology.left_ground_side is False
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "left_ground_side.ckt", "Distributed"
        )

    def test_equal_stub_widths(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.equal_stub_widths = True
        assert info.value.args[0] == "The Equal Stub Widths property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.SHUNT_STUB_RESONATORS
        assert design.topology.equal_stub_widths is False
        design.topology.equal_stub_widths = True
        assert design.topology.equal_stub_widths
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "equal_stub_widths.ckt", "Distributed"
        )

    def test_center_z0_impedance(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.center_z0_impedance = "55"
        assert info.value.args[0] == "The Center Z0 property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.SHUNT_STUB_RESONATORS
        design.topology.equal_stub_widths = False
        assert design.topology.center_z0_impedance == "75"
        design.topology.center_z0_impedance = "55"
        assert design.topology.center_z0_impedance == "55"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "center_z0_impedance.ckt", "Distributed"
        )

    def test_equal_width_conductors(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.equal_width_conductors = True
        assert info.value.args[0] == "The Equal Width property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.PARALLEL_EDGE_COUPLED
        assert design.topology.equal_width_conductors
        design.topology.equal_width_conductors = False
        assert design.topology.equal_width_conductors is False
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "equal_width_conductors.ckt", "Distributed"
        )

    def test_tapped(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.tapped = True
        assert info.value.args[0] == "The Tapped property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.PARALLEL_EDGE_COUPLED
        assert design.topology.tapped
        design.topology.tapped = False
        assert design.topology.tapped is False
        assert design.topology.circuit_response().splitlines() == read_resource_file("tapped.ckt", "Distributed")

    def test_pinned(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.pinned = True
        assert info.value.args[0] == "The Pinned property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.PARALLEL_EDGE_COUPLED
        assert design.topology.pinned is False
        design.topology.pinned = True
        assert design.topology.pinned
        assert design.topology.equal_width_conductors is False
        assert design.topology.circuit_response().splitlines() == read_resource_file("pinned.ckt", "Distributed")

    def test_stub_taps(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.stub_taps = True
        assert info.value.args[0] == "The Stub Taps property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.PARALLEL_EDGE_COUPLED
        assert design.topology.stub_taps is False
        design.topology.stub_taps = True
        assert design.topology.stub_taps
        assert design.topology.circuit_response().splitlines() == read_resource_file("stub_taps.ckt", "Distributed")

    def test_via_ends(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.via_ends = True
        assert info.value.args[0] == "The Via Ends property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.PARALLEL_EDGE_COUPLED
        assert design.topology.via_ends is False
        design.topology.via_ends = True
        assert design.topology.via_ends
        assert design.topology.equal_width_conductors is False
        assert design.topology.circuit_response().splitlines() == read_resource_file("via_ends.ckt", "Distributed")

    def test_resonator_line_width(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.resonator_line_width = "1.27 mm"
        assert info.value.args[0] == "The Line Width property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.HAIRPIN
        assert design.topology.resonator_line_width == "1.27 mm"
        design.topology.resonator_line_width = "5 mm"
        assert design.topology.resonator_line_width == "5 mm"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "resonator_line_width.ckt", "Distributed"
        )

    def test_resonator_rotation_angle(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.resonator_rotation_angle = "0"
        assert info.value.args[0] == "The Rotation Angle property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.PARALLEL_EDGE_COUPLED
        assert design.topology.resonator_rotation_angle == "0"
        design.topology.resonator_rotation_angle = "5"
        assert design.topology.resonator_rotation_angle == "5"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "resonator_rotation_angle.ckt", "Distributed"
        )

    def test_mitered_corners(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.mitered_corners = True
        assert info.value.args[0] == "The Mitered Corners property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.HAIRPIN
        assert design.topology.mitered_corners is False
        design.topology.mitered_corners = True
        assert design.topology.mitered_corners
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "mitered_corners.ckt", "Distributed"
        )

    def test_hairpin_gap_width(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.hairpin_gap_width = "0.127 mm"
        assert info.value.args[0] == "The Gap Width property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.HAIRPIN
        assert design.topology.hairpin_gap_width == "2.54 mm"
        design.topology.hairpin_gap_width = "4 mm"
        assert design.topology.hairpin_gap_width == "4 mm"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "hairpin_gap_width.ckt", "Distributed"
        )

    def test_miniature_hairpin_gap_width(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.miniature_hairpin_gap_width = "635 um"
        assert info.value.args[0] == "The Gap Width property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.MINIATURE_HAIRPIN
        assert design.topology.miniature_hairpin_gap_width == "635 um"
        design.topology.miniature_hairpin_gap_width = "450 um"
        assert design.topology.miniature_hairpin_gap_width == "450 um"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "miniature_hairpin_gap_width.ckt", "Distributed"
        )

    def test_ring_resonator_gap_width(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.ring_resonator_gap_width = "635 um"
        assert info.value.args[0] == "The Gap Width property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.RING_RESONATOR
        assert design.topology.ring_resonator_gap_width == "635 um"
        design.topology.ring_resonator_gap_width = "450 um"
        assert design.topology.ring_resonator_gap_width == "450 um"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "ring_resonator_gap_width.ckt", "Distributed"
        )

    def test_hairpin_extension_length(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.hairpin_extension_length = "0 mm"
        assert info.value.args[0] == "The Tuning Extension property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.HAIRPIN
        assert design.topology.hairpin_extension_length == "0 um"
        design.topology.hairpin_extension_length = "2 mm"
        assert design.topology.hairpin_extension_length == "2 mm"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "hairpin_extension_length.ckt", "Distributed"
        )

    def test_miniature_hairpin_end_curl_extension(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.miniature_hairpin_end_curl_extension = "0 mm"
        assert info.value.args[0] == "The Tuning Extension property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.MINIATURE_HAIRPIN
        assert design.topology.miniature_hairpin_end_curl_extension == "0 um"
        design.topology.miniature_hairpin_end_curl_extension = "2 mm"
        assert design.topology.miniature_hairpin_end_curl_extension == "2 mm"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "miniature_hairpin_end_curl_extension.ckt", "Distributed"
        )

    def test_ring_resonator_end_gap_extension(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.ring_resonator_end_gap_extension = "0 mm"
        assert info.value.args[0] == "The Tuning Extension property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.RING_RESONATOR
        assert design.topology.ring_resonator_end_gap_extension == "0 um"
        design.topology.ring_resonator_end_gap_extension = "2 mm"
        assert design.topology.ring_resonator_end_gap_extension == "2 mm"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "ring_resonator_end_gap_extension.ckt", "Distributed"
        )

    def test_tuning_type_1(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.tuning_type_1 = True
        assert info.value.args[0] == "The Tuning Type property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.HAIRPIN
        assert design.topology.tuning_type_1
        design.topology.tuning_type_1 = False
        assert design.topology.tuning_type_1 is False
        assert design.topology.circuit_response().splitlines() == read_resource_file("tuning_type_1.ckt", "Distributed")

    def test_tuning_type_2(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.tuning_type_1 = True
        assert info.value.args[0] == "The Tuning Type property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.HAIRPIN
        assert design.topology.tuning_type_1
        assert design.topology.circuit_response().splitlines() == read_resource_file("tuning_type_2.ckt", "Distributed")

    def test_tap_position(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.tap_position = TapPosition.AUTO
        assert info.value.args[0] == "The Tap Position property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.MINIATURE_HAIRPIN
        assert design.topology.tap_position == TapPosition.AUTO
        design.topology.tap_position = TapPosition.SIDES
        assert design.topology.tap_position == TapPosition.SIDES
        assert design.topology.circuit_response().splitlines() == read_resource_file("tap_position.ckt", "Distributed")

    def test_wide_band(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.wide_band = True
        assert info.value.args[0] == "The Wide Band property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.INTERDIGITAL
        assert design.topology.wide_band is False
        design.topology.wide_band = True
        design.topology.pinned = True
        assert design.topology.wide_band
        assert design.topology.circuit_response().splitlines() == read_resource_file("wide_band.ckt", "Distributed")

    def test_open_ends(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.open_ends = True
        assert info.value.args[0] == "The Open Ends property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.INTERDIGITAL
        assert design.topology.open_ends is False
        design.topology.open_ends = True
        assert design.topology.open_ends
        assert design.topology.circuit_response().splitlines() == read_resource_file("open_ends.ckt", "Distributed")

    def test_combline_half_length_frequency(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.combline_half_length_frequency = "4G"
        assert info.value.args[0] == "The 1/2 Length Frequency property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.COMBLINE
        assert design.topology.combline_half_length_frequency == "4G"
        design.topology.combline_half_length_frequency = "2 GHz"
        assert design.topology.combline_half_length_frequency == "2 GHz"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "combline_half_length_frequency.ckt", "Distributed"
        )

    def test_coupled_segments_quarter_length_frequency(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])

        with pytest.raises(RuntimeError) as info:
            design.topology.coupled_segments_quarter_length_frequency = "4G"
        assert info.value.args[0] == "The 1/4 Length Frequency property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.HIGH_PASS
        design.topology.topology_list = TopologyList.COUPLED_SEGMENTS
        assert design.topology.coupled_segments_quarter_length_frequency == "4G"
        design.topology.coupled_segments_quarter_length_frequency = "2 GHz"
        assert design.topology.coupled_segments_quarter_length_frequency == "2 GHz"
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "coupled_segments_quarter_length_frequency.ckt", "Distributed"
        )

    def test_circuit_response(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])
        assert design.topology.circuit_response().splitlines() == read_resource_file("default.ckt", "Distributed")

    def test_quick_optimize(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])
        assert design.topology.quick_optimize is False
        design.topology.quick_optimize = True
        assert design.topology.quick_optimize
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "quick_optimize.ckt", "Distributed"
        )

    def test_resonator_length_extension(self):
        design = ansys.aedt.core.filtersolutions.DistributedDesign(config["desktopVersion"])
        with pytest.raises(RuntimeError) as info:
            design.topology.resonator_length_extension = True
        assert info.value.args[0] == "The Enable Extension property is not supported for the selected topology"
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.topology.topology_list = TopologyList.INTERDIGITAL
        assert design.topology.resonator_length_extension is False
        design.topology.resonator_length_extension = True
        assert design.topology.resonator_length_extension
        assert design.topology.circuit_response().splitlines() == read_resource_file(
            "resonator_length_extension.ckt", "Distributed"
        )
