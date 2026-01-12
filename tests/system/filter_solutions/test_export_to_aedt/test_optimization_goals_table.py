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
import os

import pytest

from ansys.aedt.core.filtersolutions_core.optimization_goals_table import OptimizationGoalParameter
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import DESKTOP_VERSION
from tests.system.filter_solutions.resources import resource_path


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    empty_paramter_update_err_msg = "It is not possible to update the table with empty values"
    empty_paramter_append_err_msg = "Unable to append a new row, one or more required parameters are missing"
    if DESKTOP_VERSION > "2025.1":
        row_excess_insert_err_msg = (
            "The Optimization Goals Table supports up to 50 rows, the input index must be less than 50"
        )
    else:
        row_excess_insert_err_msg = "The rowIndex is greater than row count"
    empty_paramter_insert_err_msg = "Unable to insert a new row, one or more required parameters are missing"
    empty_row_index_err_msg = "The rowIndex is greater than row count or less than zero"

    def test_row_count(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        assert lumped_design.optimization_goals_table.row_count == 2
        lumped_design.export_to_aedt.optimitrics_enabled = False
        if DESKTOP_VERSION > "2025.1":
            with pytest.raises(RuntimeError) as info:
                assert lumped_design.optimization_goals_table.row_count == 2
            assert info.value.args[0] == "The optimetric export to AEDT is not enabled"

    def test_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        assert lumped_design.optimization_goals_table.row(0) == [
            "200 MHz",
            "1 GHz",
            "-3.0103",
            "<=",
            "dB(S(Port1,Port1))",
            "1",
            "Y",
        ]
        row_1 = lumped_design.optimization_goals_table.row(1)
        assert row_1[:5] == [
            "1.5849 GHz",
            "1.9019 GHz",
            "-23.01",
            "<=",
            "dB(S(Port2,Port1))",
        ]
        assert row_1[5] in ["0.5", "0,5"]
        assert row_1[6] == "Y"
        assert (
            lumped_design.optimization_goals_table.row(0)[OptimizationGoalParameter.PARAMETER_NAME.value]
            == "dB(S(Port1,Port1))"
        )
        assert lumped_design.optimization_goals_table.row(1)[OptimizationGoalParameter.WEIGHT.value] == "0.5"
        with pytest.raises(RuntimeError) as info:
            lumped_design.optimization_goals_table.row(5)
        assert info.value.args[0] == "The rowIndex is greater than row count or less than zero"

    def test_update_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.update_row(
            0,
            lower_frequency="100 MHz",
            upper_frequency="2 GHz",
            condition=">",
            weight="0.7",
        )
        assert lumped_design.optimization_goals_table.row(0) == [
            "100 MHz",
            "2 GHz",
            "-3.0103",
            ">",
            "dB(S(Port1,Port1))",
            "0.7",
            "Y",
        ]
        if DESKTOP_VERSION > "2025.1":
            with pytest.raises(RuntimeError) as info:
                lumped_design.optimization_goals_table.update_row(
                    0,
                    lower_frequency="",
                    upper_frequency="",
                    goal_value="",
                    condition="",
                    parameter_name="",
                    weight="",
                    enabled="",
                )
            assert info.value.args[0] == self.empty_paramter_update_err_msg

    def test_append_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.append_row(
            "100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y"
        )
        assert lumped_design.optimization_goals_table.row_count == 3
        assert lumped_design.optimization_goals_table.row(2) == [
            "100 MHz",
            "2 GHz",
            "-3",
            ">",
            "dB(S(Port2,Port2))",
            "0.3",
            "Y",
        ]
        if DESKTOP_VERSION > "2025.1":
            with pytest.raises(RuntimeError) as info:
                lumped_design.optimization_goals_table.append_row(
                    "100 MHz", "2 GHz", "", ">", "dB(S(Port2,Port2))", "0.3", "Y"
                )
            assert info.value.args[0] == self.empty_paramter_append_err_msg

    def test_insert_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.insert_row(
            1, "100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y"
        )
        assert lumped_design.optimization_goals_table.row(1) == [
            "100 MHz",
            "2 GHz",
            "-3",
            ">",
            "dB(S(Port2,Port2))",
            "0.3",
            "Y",
        ]
        with pytest.raises(RuntimeError) as info:
            lumped_design.optimization_goals_table.insert_row(
                51, "100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y"
            )
        assert info.value.args[0] == self.row_excess_insert_err_msg
        if DESKTOP_VERSION > "2025.1":
            with pytest.raises(RuntimeError) as info:
                lumped_design.optimization_goals_table.insert_row(
                    0, "100 MHz", "2 GHz", "", ">", "dB(S(Port2,Port2))", "0.3", "Y"
                )
            assert info.value.args[0] == self.empty_paramter_insert_err_msg
            with pytest.raises(RuntimeError) as info:
                lumped_design.optimization_goals_table.insert_row(
                    5, "100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y"
                )
            assert info.value.args[0] == self.empty_row_index_err_msg

    def test_remove_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.remove_row(1)
        assert lumped_design.optimization_goals_table.row_count == 1
        assert lumped_design.optimization_goals_table.row(0) == [
            "200 MHz",
            "1 GHz",
            "-3.0103",
            "<=",
            "dB(S(Port1,Port1))",
            "1",
            "Y",
        ]
        with pytest.raises(RuntimeError) as info:
            lumped_design.optimization_goals_table.remove_row(5)
        assert info.value.args[0] == "The rowIndex is greater than row count or less than zero"

    def test_save_goals(self, lumped_design):
        lumped_design.optimization_goals_table.clear_goal_entries()
        lumped_design.optimization_goals_table.append_row(
            "100 MHz", "3 GHz", "-3.5", ">", "dB(S(Port1,Port2))", "0.2", "Y"
        )
        temp_save_path = resource_path("goals.cfg")
        lumped_design.optimization_goals_table.save_goals(temp_save_path)
        assert os.path.exists(temp_save_path)
        with open(temp_save_path, mode="r", newline="") as file:
            lines = file.readlines()
            for line in lines:
                row = line.strip().split("/")
                assert row in [["100 MHz", "3 GHz", "-3.5", ">", "dB(S(Port1,Port2))", "0.2", "Y"]]
        os.remove(temp_save_path)

    def test_load_goals(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        temp_save_path = resource_path("goals.cfg")
        lumped_design.optimization_goals_table.save_goals(temp_save_path)
        lumped_design.optimization_goals_table.load_goals(temp_save_path)
        assert lumped_design.optimization_goals_table.row_count == 2
        assert lumped_design.optimization_goals_table.row(0) == [
            "200 MHz",
            "1 GHz",
            "-3.0103",
            "<=",
            "dB(S(Port1,Port1))",
            "1",
            "Y",
        ]
        assert lumped_design.optimization_goals_table.row(1) == [
            "1.5849 GHz",
            "1.9019 GHz",
            "-23.01",
            "<=",
            "dB(S(Port2,Port1))",
            "0.5",
            "Y",
        ]
        os.remove(temp_save_path)

    def test_clear_goal_entries(self, lumped_design):
        lumped_design.optimization_goals_table.clear_goal_entries()
        assert lumped_design.optimization_goals_table.row_count == 0

    def test_adjust_goal_frequency(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.adjust_goal_frequency("150 MHz")
        assert (
            lumped_design.optimization_goals_table.row(0)[OptimizationGoalParameter.LOWER_FREQUENCY.value] == "350 MHz"
        )
        assert (
            lumped_design.optimization_goals_table.row(0)[OptimizationGoalParameter.UPPER_FREQUENCY.value] == "1.15 GHz"
        )
        assert (
            lumped_design.optimization_goals_table.row(1)[OptimizationGoalParameter.LOWER_FREQUENCY.value]
            == "1.7349 GHz"
        )
        assert (
            lumped_design.optimization_goals_table.row(1)[OptimizationGoalParameter.UPPER_FREQUENCY.value]
            == "2.0519 GHz"
        )