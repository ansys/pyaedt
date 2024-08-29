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

import ansys.aedt.core
from ansys.aedt.core.filtersolutions_core.attributes import FilterImplementation
from ansys.aedt.core.filtersolutions_core.optimization_goals_table import OptimizationGoalParameter
from ansys.aedt.core.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_row_count(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        assert lumpdesign.optimization_goals_table.row_count == 2

    def test_row(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        assert lumpdesign.optimization_goals_table.row(0) == [
            "200 MHz",
            "1 GHz",
            "-3.0103",
            "<=",
            "dB(S(Port1,Port1))",
            "1",
            "Y",
        ]
        assert lumpdesign.optimization_goals_table.row(1) == [
            "1.5849 GHz",
            "1.9019 GHz",
            "-23.01",
            "<=",
            "dB(S(Port2,Port1))",
            "0.5",
            "Y",
        ]
        assert (
            lumpdesign.optimization_goals_table.row(0)[OptimizationGoalParameter.PARAMETER_NAME.value]
            == "dB(S(Port1,Port1))"
        )
        assert lumpdesign.optimization_goals_table.row(1)[OptimizationGoalParameter.WEIGHT.value] == "0.5"

    def test_update_row(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        lumpdesign.optimization_goals_table.update_row(
            0, lower_frequency="100 MHz", upper_frequency="2 GHz", condition=">", weight="0.7"
        )
        assert lumpdesign.optimization_goals_table.row(0) == [
            "100 MHz",
            "2 GHz",
            "-3.0103",
            ">",
            "dB(S(Port1,Port1))",
            "0.7",
            "Y",
        ]

    def test_append_row(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        lumpdesign.optimization_goals_table.append_row("100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y")
        assert lumpdesign.optimization_goals_table.row(2) == [
            "100 MHz",
            "2 GHz",
            "-3",
            ">",
            "dB(S(Port2,Port2))",
            "0.3",
            "Y",
        ]

    def test_insert_row(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        lumpdesign.optimization_goals_table.insert_row(
            1, "100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y"
        )
        assert lumpdesign.optimization_goals_table.row(1) == [
            "100 MHz",
            "2 GHz",
            "-3",
            ">",
            "dB(S(Port2,Port2))",
            "0.3",
            "Y",
        ]

    def test_remove_row(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        lumpdesign.optimization_goals_table.remove_row(1)
        assert lumpdesign.optimization_goals_table.row_count == 1
        assert lumpdesign.optimization_goals_table.row(0) == [
            "200 MHz",
            "1 GHz",
            "-3.0103",
            "<=",
            "dB(S(Port1,Port1))",
            "1",
            "Y",
        ]

    def test_adjust_goal_frequency(self):
        lumpdesign = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        lumpdesign.export_to_aedt._open_aedt_export()
        lumpdesign.optimization_goals_table.set_design_goals()
        lumpdesign.optimization_goals_table.adjust_goal_frequency("150 MHz")
        assert lumpdesign.optimization_goals_table.row(0)[OptimizationGoalParameter.LOWER_FREQUENCY.value] == "350 MHz"
        assert lumpdesign.optimization_goals_table.row(0)[OptimizationGoalParameter.UPPER_FREQUENCY.value] == "1.15 GHz"
        assert (
            lumpdesign.optimization_goals_table.row(1)[OptimizationGoalParameter.LOWER_FREQUENCY.value] == "1.7349 GHz"
        )
        assert (
            lumpdesign.optimization_goals_table.row(1)[OptimizationGoalParameter.UPPER_FREQUENCY.value] == "2.0519 GHz"
        )
