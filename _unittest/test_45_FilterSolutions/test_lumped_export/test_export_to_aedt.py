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
import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.generic.general_methods import is_linux

# from ..filtersolutions_resources import resource_path
import pytest


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_schematic_name(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.export_to_aedt.schematic_name = "my_schematic"
        assert lumpdesign.export_to_aedt.schematic_name == "my_schematic"

    def test_simulate_after_export_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.simulate_after_export_enabled == False
        lumpdesign.export_to_aedt.simulate_after_export_enabled = True
        assert lumpdesign.export_to_aedt.simulate_after_export_enabled == True

    def test_include_group_delay_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_group_delay_enabled == False
        lumpdesign.export_to_aedt.include_group_delay_enabled = True
        assert lumpdesign.export_to_aedt.include_group_delay_enabled == True

    def test_include_gt_gain_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_gt_gain_enabled == False
        lumpdesign.export_to_aedt.include_gt_gain_enabled = True
        assert lumpdesign.export_to_aedt.include_gt_gain_enabled == True

    def test_include_vgsl_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_vgsl_enabled == False
        lumpdesign.export_to_aedt.include_vgsl_enabled = True
        assert lumpdesign.export_to_aedt.include_vgsl_enabled == True

    def test_include_vgin_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_vgin_enabled == False
        lumpdesign.export_to_aedt.include_vgin_enabled = True
        assert lumpdesign.export_to_aedt.include_vgin_enabled == True

    def test_include_input_return_loss_s11_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_input_return_loss_s11_enabled == True
        lumpdesign.export_to_aedt.include_input_return_loss_s11_enabled = False
        assert lumpdesign.export_to_aedt.include_input_return_loss_s11_enabled == False

    def test_include_forward_transfer_s21_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_forward_transfer_s21_enabled == True
        lumpdesign.export_to_aedt.include_forward_transfer_s21_enabled = False
        assert lumpdesign.export_to_aedt.include_forward_transfer_s21_enabled == False

    def test_include_reverse_transfer_s12_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_reverse_transfer_s12_enabled == False
        lumpdesign.export_to_aedt.include_reverse_transfer_s12_enabled = True
        assert lumpdesign.export_to_aedt.include_reverse_transfer_s12_enabled == True

    def test_include_output_return_loss_s22_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.include_output_return_loss_s22_enabled == False
        lumpdesign.export_to_aedt.include_output_return_loss_s22_enabled = True
        assert lumpdesign.export_to_aedt.include_output_return_loss_s22_enabled == True

    def test_db_format_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.db_format_enabled == True
        lumpdesign.export_to_aedt.db_format_enabled = False
        assert lumpdesign.export_to_aedt.db_format_enabled == False

    def test_rectangular_plot_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.rectangular_plot_enabled == True
        lumpdesign.export_to_aedt.rectangular_plot_enabled = False
        assert lumpdesign.export_to_aedt.rectangular_plot_enabled == False

    def test_smith_plot_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.smith_plot_enabled == False
        lumpdesign.export_to_aedt.smith_plot_enabled = True
        assert lumpdesign.export_to_aedt.smith_plot_enabled == True

    def test_polar_plot_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.polar_plot_enabled == False
        lumpdesign.export_to_aedt.polar_plot_enabled = True
        assert lumpdesign.export_to_aedt.polar_plot_enabled == True

    def test_table_data_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.table_data_enabled == False
        lumpdesign.export_to_aedt.table_data_enabled = True
        assert lumpdesign.export_to_aedt.table_data_enabled == True

    def test_optimitrics_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.optimitrics_enabled == True
        lumpdesign.export_to_aedt.optimitrics_enabled = False
        assert lumpdesign.export_to_aedt.optimitrics_enabled == False

    def test_optimize_after_export_enabled(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        assert lumpdesign.export_to_aedt.optimize_after_export_enabled == False
        lumpdesign.export_to_aedt.optimize_after_export_enabled = True
        assert lumpdesign.export_to_aedt.optimize_after_export_enabled == True
