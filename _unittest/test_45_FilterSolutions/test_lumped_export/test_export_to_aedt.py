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

# from pyaedt.filtersolutions_core.export_to_aedt import ExportFormat
from pyaedt.filtersolutions_core.export_to_aedt import PartLibraries
from pyaedt.filtersolutions_core.export_to_aedt import SubstrateEr
from pyaedt.filtersolutions_core.export_to_aedt import SubstrateResistivity
from pyaedt.filtersolutions_core.export_to_aedt import SubstrateType
from pyaedt.generic.general_methods import is_linux

# from ..resources import read_resource_file
# from ..resources import resource_path


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_schematic_name(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.schematic_name = "my_schematic"
        assert lumpdesign.export_to_aedt.schematic_name == "my_schematic"

    def test_simulate_after_export_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.simulate_after_export_enabled == False
        lumpdesign.export_to_aedt.simulate_after_export_enabled = True
        assert lumpdesign.export_to_aedt.simulate_after_export_enabled == True

    def test_include_group_delay_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_group_delay_enabled == False
        lumpdesign.export_to_aedt.include_group_delay_enabled = True
        assert lumpdesign.export_to_aedt.include_group_delay_enabled == True

    def test_include_gt_gain_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_gt_gain_enabled == False
        lumpdesign.export_to_aedt.include_gt_gain_enabled = True
        assert lumpdesign.export_to_aedt.include_gt_gain_enabled == True

    def test_include_vgsl_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_vgsl_enabled == False
        lumpdesign.export_to_aedt.include_vgsl_enabled = True
        assert lumpdesign.export_to_aedt.include_vgsl_enabled == True

    def test_include_vgin_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_vgin_enabled == False
        lumpdesign.export_to_aedt.include_vgin_enabled = True
        assert lumpdesign.export_to_aedt.include_vgin_enabled == True

    def test_include_input_return_loss_s11_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_input_return_loss_s11_enabled == True
        lumpdesign.export_to_aedt.include_input_return_loss_s11_enabled = False
        assert lumpdesign.export_to_aedt.include_input_return_loss_s11_enabled == False

    def test_include_forward_transfer_s21_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_forward_transfer_s21_enabled == True
        lumpdesign.export_to_aedt.include_forward_transfer_s21_enabled = False
        assert lumpdesign.export_to_aedt.include_forward_transfer_s21_enabled == False

    def test_include_reverse_transfer_s12_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_reverse_transfer_s12_enabled == False
        lumpdesign.export_to_aedt.include_reverse_transfer_s12_enabled = True
        assert lumpdesign.export_to_aedt.include_reverse_transfer_s12_enabled == True

    def test_include_output_return_loss_s22_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.include_output_return_loss_s22_enabled == False
        lumpdesign.export_to_aedt.include_output_return_loss_s22_enabled = True
        assert lumpdesign.export_to_aedt.include_output_return_loss_s22_enabled == True

    def test_db_format_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.db_format_enabled == True
        lumpdesign.export_to_aedt.db_format_enabled = False
        assert lumpdesign.export_to_aedt.db_format_enabled == False

    def test_rectangular_plot_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.rectangular_plot_enabled == True
        lumpdesign.export_to_aedt.rectangular_plot_enabled = False
        assert lumpdesign.export_to_aedt.rectangular_plot_enabled == False

    def test_smith_plot_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.smith_plot_enabled == False
        lumpdesign.export_to_aedt.smith_plot_enabled = True
        assert lumpdesign.export_to_aedt.smith_plot_enabled == True

    def test_polar_plot_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.polar_plot_enabled == False
        lumpdesign.export_to_aedt.polar_plot_enabled = True
        assert lumpdesign.export_to_aedt.polar_plot_enabled == True

    def test_table_data_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.table_data_enabled == False
        lumpdesign.export_to_aedt.table_data_enabled = True
        assert lumpdesign.export_to_aedt.table_data_enabled == True

    def test_optimitrics_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.optimitrics_enabled == True
        lumpdesign.export_to_aedt.optimitrics_enabled = False
        assert lumpdesign.export_to_aedt.optimitrics_enabled == False

    def test_optimize_after_export_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.export_to_aedt.optimize_after_export_enabled == False
        lumpdesign.export_to_aedt.optimize_after_export_enabled = True
        assert lumpdesign.export_to_aedt.optimize_after_export_enabled == True

    # def test_load_library_parts_config(self):
    #     lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    #     lumpdesign.export_to_aedt.load_library_parts_config(resource_path("library_parts.cfg"))
    #     assert lumpdesign.export_to_aedt.part_libraries == PartLibraries.MODELITHICS
    #     assert lumpdesign.export_to_aedt.substrate_er == "4.5"
    #     assert lumpdesign.export_to_aedt.substrate_resistivity == "5.8E+07 "
    #     assert lumpdesign.export_to_aedt.substrate_conductor_thickness == "500 nm"
    #     assert lumpdesign.export_to_aedt.substrate_dielectric_height == "2 mm"
    #     assert lumpdesign.export_to_aedt.substrate_loss_tangent == "0.035 "

    # def test_save_library_parts_config(self):
    #     lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    #     lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
    #     lumpdesign.export_to_aedt.substrate_er = "4.5"
    #     lumpdesign.export_to_aedt.substrate_resistivity = "5.8E+07 "
    #     lumpdesign.export_to_aedt.substrate_conductor_thickness = "500 nm"
    #     lumpdesign.export_to_aedt.substrate_dielectric_height = "2 mm"
    #     lumpdesign.export_to_aedt.substrate_loss_tangent = "0.035 "
    #     lumpdesign.export_to_aedt.save_library_parts_config(resource_path("library_parts_test.cfg"))
    #     lumpdesign.export_to_aedt.load_library_parts_config(resource_path("library_parts_test.cfg"))
    #     assert lumpdesign.export_to_aedt.part_libraries == PartLibraries.MODELITHICS
    #     assert lumpdesign.export_to_aedt.substrate_er == "4.5"
    #     assert lumpdesign.export_to_aedt.substrate_resistivity == "5.8E+07 "
    #     assert lumpdesign.export_to_aedt.substrate_conductor_thickness == "500 nm"
    #     assert lumpdesign.export_to_aedt.substrate_dielectric_height == "2 mm"
    #     assert lumpdesign.export_to_aedt.substrate_loss_tangent == "0.035 "

    # def test_import_tuned_variables(self):
    #     lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    #     lumpdesign.export_to_aedt.simulate_after_export_enabled = True
    #     lumpdesign.export_to_aedt.optimize_after_export_enabled = True
    #     lumpdesign.export_to_aedt.overwrite_design_to_aedt(ExportFormat.DIRECT)
    #     assert lumpdesign.export_to_aedt.import_tuned_variables().splitlines() ==
    #     read_resource_file("import_tuned_variables.ckt")

    def test_part_libraries(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.part_libraries == PartLibraries.LUMPED
        assert len(PartLibraries) == 3
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        assert lumpdesign.export_to_aedt.part_libraries == PartLibraries.MODELITHICS

    def test_interconnect_length_to_width_ratio(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_length_to_width_ratio == "2"
        lumpdesign.export_to_aedt.interconnect_length_to_width_ratio = "3"
        assert lumpdesign.export_to_aedt.interconnect_length_to_width_ratio == "3"

    def test_interconnect_minimum_length_to_width_ratio(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_minimum_length_to_width_ratio == "0.5"
        lumpdesign.export_to_aedt.interconnect_minimum_length_to_width_ratio = "0.6"
        assert lumpdesign.export_to_aedt.interconnect_minimum_length_to_width_ratio == "0.6"

    def test_interconnect_maximum_length_to_width_ratio(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_maximum_length_to_width_ratio == "2"
        lumpdesign.export_to_aedt.interconnect_maximum_length_to_width_ratio = "3"
        assert lumpdesign.export_to_aedt.interconnect_maximum_length_to_width_ratio == "3"

    def test_interconnect_line_to_termination_width_ratio(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_line_to_termination_width_ratio == "1"
        lumpdesign.export_to_aedt.interconnect_line_to_termination_width_ratio = "2"
        assert lumpdesign.export_to_aedt.interconnect_line_to_termination_width_ratio == "2"

    def test_interconnect_minimum_line_to_termination_width_ratio(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_minimum_line_to_termination_width_ratio == "0.5"
        lumpdesign.export_to_aedt.interconnect_minimum_line_to_termination_width_ratio = "0.6"
        assert lumpdesign.export_to_aedt.interconnect_minimum_line_to_termination_width_ratio == "0.6"

    def test_interconnect_maximum_line_to_termination_width_ratio(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_maximum_line_to_termination_width_ratio == "2"
        lumpdesign.export_to_aedt.interconnect_maximum_line_to_termination_width_ratio = "3"
        assert lumpdesign.export_to_aedt.interconnect_maximum_line_to_termination_width_ratio == "3"

    def test_interconnect_length_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_length_value == "2.54 mm"
        lumpdesign.export_to_aedt.interconnect_length_value = "3 mm"
        assert lumpdesign.export_to_aedt.interconnect_length_value == "3 mm"

    def test_interconnect_minimum_length_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_minimum_length_value == "1.27 mm"
        lumpdesign.export_to_aedt.interconnect_minimum_length_value = "0.6 mm"
        assert lumpdesign.export_to_aedt.interconnect_minimum_length_value == "0.6 mm"

    def test_interconnect_maximum_length_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_maximum_length_value == "5.08 mm"
        lumpdesign.export_to_aedt.interconnect_maximum_length_value = "6 mm"
        assert lumpdesign.export_to_aedt.interconnect_maximum_length_value == "6 mm"

    def test_interconnect_line_width_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_line_width_value == "1.27 mm"
        lumpdesign.export_to_aedt.interconnect_line_width_value = "2 mm"
        assert lumpdesign.export_to_aedt.interconnect_line_width_value == "2 mm"

    def test_interconnect_minimum_width_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_minimum_width_value == "635 um"
        lumpdesign.export_to_aedt.interconnect_minimum_width_value = "725 um"
        assert lumpdesign.export_to_aedt.interconnect_minimum_width_value == "725 um"

    def test_interconnect_maximum_width_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_maximum_width_value == "2.54 mm"
        lumpdesign.export_to_aedt.interconnect_maximum_width_value = "3 mm"
        assert lumpdesign.export_to_aedt.interconnect_maximum_width_value == "3 mm"

    def test_interconnect_inductor_tolerance_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        assert lumpdesign.export_to_aedt.interconnect_inductor_tolerance_value == "1"
        lumpdesign.export_to_aedt.interconnect_inductor_tolerance_value = "10"
        assert lumpdesign.export_to_aedt.interconnect_inductor_tolerance_value == "10"

    def test_interconnect_capacitor_tolerance_value(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        assert lumpdesign.export_to_aedt.interconnect_capacitor_tolerance_value == "1"
        lumpdesign.export_to_aedt.interconnect_capacitor_tolerance_value = "10"
        assert lumpdesign.export_to_aedt.interconnect_capacitor_tolerance_value == "10"

    def test_interconnect_geometry_optimization_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.interconnect_geometry_optimization_enabled == True
        lumpdesign.export_to_aedt.interconnect_geometry_optimization_enabled = False
        assert lumpdesign.export_to_aedt.interconnect_geometry_optimization_enabled == False

    def test_substrate_type(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_type == SubstrateType.MICROSTRIP
        lumpdesign.export_to_aedt.substrate_type = SubstrateType.STRIPLINE
        assert lumpdesign.export_to_aedt.substrate_type == SubstrateType.STRIPLINE

    def test_substrate_er(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_er == SubstrateEr.ALUMINA
        assert len(SubstrateEr) == 17
        for er in SubstrateEr:
            lumpdesign.export_to_aedt.substrate_er = er
            assert lumpdesign.export_to_aedt.substrate_er == er
        lumpdesign.export_to_aedt.substrate_er = "3.2"
        assert lumpdesign.export_to_aedt.substrate_er == "3.2"

    def test_substrate_resistivity(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_resistivity == SubstrateResistivity.GOLD
        assert len(SubstrateResistivity) == 11
        for resistivity in SubstrateResistivity:
            lumpdesign.export_to_aedt.substrate_resistivity = resistivity
            assert lumpdesign.export_to_aedt.substrate_resistivity == resistivity
        lumpdesign.export_to_aedt.substrate_resistivity = "0.02"
        assert lumpdesign.export_to_aedt.substrate_resistivity == "0.02"

    def test_substrate_loss_tangent(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_loss_tangent == SubstrateEr.ALUMINA
        assert len(SubstrateEr) == 17
        for loss in SubstrateEr:
            lumpdesign.export_to_aedt.substrate_loss_tangent = loss
            assert lumpdesign.export_to_aedt.substrate_loss_tangent == loss
        lumpdesign.export_to_aedt.substrate_loss_tangent = "0.0002"
        assert lumpdesign.export_to_aedt.substrate_loss_tangent == "0.0002"

    def test_substrate_conductor_thickness(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_conductor_thickness == "2.54 um"
        lumpdesign.export_to_aedt.substrate_conductor_thickness = "1.25 um"
        assert lumpdesign.export_to_aedt.substrate_conductor_thickness == "1.25 um"

    def test_substrate_dielectric_height(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_dielectric_height == "1.27 mm"
        lumpdesign.export_to_aedt.substrate_dielectric_height = "1.22 mm"
        assert lumpdesign.export_to_aedt.substrate_dielectric_height == "1.22 mm"

    def test_substrate_unbalanced_lower_dielectric_height(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.substrate_type = SubstrateType.STRIPLINE
        lumpdesign.export_to_aedt.substrate_unbalanced_stripline_enabled = True
        assert lumpdesign.export_to_aedt.substrate_unbalanced_lower_dielectric_height == "6.35 mm"
        lumpdesign.export_to_aedt.substrate_unbalanced_lower_dielectric_height = "5.2 mm"
        assert lumpdesign.export_to_aedt.substrate_unbalanced_lower_dielectric_height == "5.2 mm"

    def test_substrate_suspend_dielectric_height(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.substrate_type = SubstrateType.SUSPEND
        assert lumpdesign.export_to_aedt.substrate_suspend_dielectric_height == "1.27 mm"
        lumpdesign.export_to_aedt.substrate_suspend_dielectric_height = "3.2 mm"
        assert lumpdesign.export_to_aedt.substrate_suspend_dielectric_height == "3.2 mm"

    def test_substrate_cover_height(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.substrate_cover_height_enabled = True
        assert lumpdesign.export_to_aedt.substrate_cover_height == "6.35 mm"
        lumpdesign.export_to_aedt.substrate_cover_height = "2.5 mm"
        assert lumpdesign.export_to_aedt.substrate_cover_height == "2.5 mm"

    def test_substrate_unbalanced_stripline_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.substrate_type = SubstrateType.STRIPLINE
        assert lumpdesign.export_to_aedt.substrate_unbalanced_stripline_enabled == False
        lumpdesign.export_to_aedt.substrate_unbalanced_stripline_enabled = True
        assert lumpdesign.export_to_aedt.substrate_unbalanced_stripline_enabled == True

    def test_substrate_cover_height_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        assert lumpdesign.export_to_aedt.substrate_cover_height_enabled == False
        lumpdesign.export_to_aedt.substrate_cover_height_enabled = True
        assert lumpdesign.export_to_aedt.substrate_cover_height_enabled == True

    def test_modelithics_inductor_list_count(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        assert lumpdesign.export_to_aedt.modelithics_inductor_list_count == 116

    def test_modelithics_inductor_list(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_inductor_selection = "AVX -> IND_AVX_0201_101 Accu-L"
        assert lumpdesign.export_to_aedt.modelithics_inductor_list(0) == "AVX -> IND_AVX_0201_101 Accu-L"

    def test_modelithics_inductor_selection(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_inductor_selection = "AVX -> IND_AVX_0201_101 Accu-L"
        assert lumpdesign.export_to_aedt.modelithics_inductor_selection == "AVX -> IND_AVX_0201_101 Accu-L"

    def test_modelithics_inductor_family_list_count(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("AVX -> IND_AVX_0402_101 AccuL")
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("Wurth -> IND_WTH_0603_003 WE-KI")
        assert lumpdesign.export_to_aedt.modelithics_inductor_family_list_count == 2

    def test_modelithics_inductor_family_list(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("AVX -> IND_AVX_0402_101 AccuL")
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("Wurth -> IND_WTH_0603_003 WE-KI")
        assert lumpdesign.export_to_aedt.modelithics_inductor_family_list(0) == "AVX -> IND_AVX_0402_101 AccuL"
        assert lumpdesign.export_to_aedt.modelithics_inductor_family_list(1) == "Wurth -> IND_WTH_0603_003 WE-KI"

    def test_modelithics_inductor_family_list_add_family(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("AVX -> IND_AVX_0402_101 AccuL")
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("Wurth -> IND_WTH_0603_003 WE-KI")
        assert lumpdesign.export_to_aedt.modelithics_inductor_family_list(0) == "AVX -> IND_AVX_0402_101 AccuL"
        assert lumpdesign.export_to_aedt.modelithics_inductor_family_list(1) == "Wurth -> IND_WTH_0603_003 WE-KI"

    def test_modelithics_inductor_family_list_remove_family(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("AVX -> IND_AVX_0402_101 AccuL")
        lumpdesign.export_to_aedt.modelithics_inductor_add_family("Wurth -> IND_WTH_0603_003 WE-KI")
        lumpdesign.export_to_aedt.modelithics_inductor_remove_family("Wurth -> IND_WTH_0603_003 WE-KI")
        assert lumpdesign.export_to_aedt.modelithics_inductor_family_list_count == 1

    def test_modelithics_capacitor_list_count(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        assert lumpdesign.export_to_aedt.modelithics_capacitor_list_count == 140

    def test_modelithics_capacitor_list(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_capacitor_selection = "Amotech -> CAP_AMH_0201_001 A60Z"
        assert lumpdesign.export_to_aedt.modelithics_capacitor_list(0) == "Amotech -> CAP_AMH_0201_001 A60Z"

    def test_modelithics_capacitor_selection(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_capacitor_selection = "Amotech -> CAP_AMH_0201_001 A60Z"
        assert lumpdesign.export_to_aedt.modelithics_capacitor_selection == "Amotech -> CAP_AMH_0201_001 A60Z"

    def test_modelithics_capacitor_family_list_count(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Amotech -> CAP_AMH_0201_001 A60Z")
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Murata -> CAP_MUR_0805_004 GRM219")
        assert lumpdesign.export_to_aedt.modelithics_capacitor_family_list_count == 2

    def test_modelithics_capacitor_family_list(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Amotech -> CAP_AMH_0201_001 A60Z")
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Murata -> CAP_MUR_0805_004 GRM219")
        assert lumpdesign.export_to_aedt.modelithics_capacitor_family_list(0) == "Amotech -> CAP_AMH_0201_001 A60Z"
        assert lumpdesign.export_to_aedt.modelithics_capacitor_family_list(1) == "Murata -> CAP_MUR_0805_004 GRM219"

    def test_modelithics_capacitor_family_list_add_family(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Amotech -> CAP_AMH_0201_001 A60Z")
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Murata -> CAP_MUR_0805_004 GRM219")
        assert lumpdesign.export_to_aedt.modelithics_capacitor_family_list(0) == "Amotech -> CAP_AMH_0201_001 A60Z"
        assert lumpdesign.export_to_aedt.modelithics_capacitor_family_list(1) == "Murata -> CAP_MUR_0805_004 GRM219"

    def test_modelithics_capacitor_family_list_remove_family(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Amotech -> CAP_AMH_0201_001 A60Z")
        lumpdesign.export_to_aedt.modelithics_capacitor_add_family("Murata -> CAP_MUR_0805_004 GRM219")
        lumpdesign.export_to_aedt.modelithics_capacitor_remove_family("Murata -> CAP_MUR_0805_004 GRM219")
        assert lumpdesign.export_to_aedt.modelithics_capacitor_family_list_count == 1

    def test_modelithics_resistor_list_count(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        assert lumpdesign.export_to_aedt.modelithics_resistor_list_count == 39

    def test_modelithics_resistor_list(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_resistor_selection = "AVX -> RES_AVX_0402_001 UBR0402"
        assert lumpdesign.export_to_aedt.modelithics_resistor_list(0) == "AVX -> RES_AVX_0402_001 UBR0402"

    def test_modelithics_resistor_selection(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_resistor_selection = "AVX -> RES_AVX_0402_001 UBR0402"
        assert lumpdesign.export_to_aedt.modelithics_resistor_selection == "AVX -> RES_AVX_0402_001 UBR0402"

    def test_modelithics_resistor_family_list_count(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("AVX -> RES_AVX_0402_001 UBR0402")
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("Vishay -> RES_VIS_0603_001 D11")
        assert lumpdesign.export_to_aedt.modelithics_resistor_family_list_count == 2

    def test_modelithics_resistor_family_list(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("AVX -> RES_AVX_0402_001 UBR0402")
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("Vishay -> RES_VIS_0603_001 D11")
        assert lumpdesign.export_to_aedt.modelithics_resistor_family_list(0) == "AVX -> RES_AVX_0402_001 UBR0402"
        assert lumpdesign.export_to_aedt.modelithics_resistor_family_list(1) == "Vishay -> RES_VIS_0603_001 D11"

    def test_modelithics_resistor_family_list_add_family(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("AVX -> RES_AVX_0402_001 UBR0402")
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("Vishay -> RES_VIS_0603_001 D11")
        assert lumpdesign.export_to_aedt.modelithics_resistor_family_list(0) == "AVX -> RES_AVX_0402_001 UBR0402"
        assert lumpdesign.export_to_aedt.modelithics_resistor_family_list(1) == "Vishay -> RES_VIS_0603_001 D11"

    def test_modelithics_resistor_family_list_remove_family(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt.open_aedt_export()
        lumpdesign.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("AVX -> RES_AVX_0402_001 UBR0402")
        lumpdesign.export_to_aedt.modelithics_resistor_add_family("Vishay -> RES_VIS_0603_001 D11")
        lumpdesign.export_to_aedt.modelithics_resistor_remove_family("Vishay -> RES_VIS_0603_001 D11")
        assert lumpdesign.export_to_aedt.modelithics_resistor_family_list_count == 1
