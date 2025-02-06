# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.core.filtersolutions_core.optimization_goals_table import OptimizationGoalParameter
from ansys.aedt.core.generic.general_methods import is_linux
import pytest

from tests.system.general.conftest import config

from ..resources import resource_path


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_row_count(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        assert lumped_design.optimization_goals_table.row_count == 2

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
        assert lumped_design.optimization_goals_table.row(1) == [
            "1.5849 GHz",
            "1.9019 GHz",
            "-23.01",
            "<=",
            "dB(S(Port2,Port1))",
            "0.5",
            "Y",
        ]
        assert (
            lumped_design.optimization_goals_table.row(0)[OptimizationGoalParameter.PARAMETER_NAME.value]
            == "dB(S(Port1,Port1))"
        )
        assert lumped_design.optimization_goals_table.row(1)[OptimizationGoalParameter.WEIGHT.value] == "0.5"

    def test_update_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.update_row(
            0, lower_frequency="100 MHz", upper_frequency="2 GHz", condition=">", weight="0.7"
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

    def test_append_row(self, lumped_design):
        lumped_design.optimization_goals_table.restore_design_goals()
        lumped_design.optimization_goals_table.append_row(
            "100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "0.3", "Y"
        )
        assert lumped_design.optimization_goals_table.row(2) == [
            "100 MHz",
            "2 GHz",
            "-3",
            ">",
            "dB(S(Port2,Port2))",
            "0.3",
            "Y",
        ]

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
