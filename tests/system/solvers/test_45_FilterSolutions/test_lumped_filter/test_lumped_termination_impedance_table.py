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

from ansys.aedt.core.filtersolutions_core.lumped_termination_impedance_table import ComplexReactanceType
from ansys.aedt.core.filtersolutions_core.lumped_termination_impedance_table import ComplexTerminationDefinition
from ansys.aedt.core.generic.settings import is_linux
import pytest

from tests.system.solvers.conftest import config


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_row_count(self, lumped_design):
        lumped_design.topology.complex_termination = True
        assert lumped_design.source_impedance_table.row_count == 3
        assert lumped_design.load_impedance_table.row_count == 3

    def test_row(self, lumped_design):
        lumped_design.topology.complex_termination = True
        assert lumped_design.source_impedance_table.row(0) == ("0.100G", "1.000", "0.000")
        assert lumped_design.load_impedance_table.row(0) == ("0.100G", "1.000", "0.000")

    def test_update_row(self, lumped_design):
        lumped_design.topology.complex_termination = True
        with pytest.raises(RuntimeError) as info:
            lumped_design.source_impedance_table.update_row(0)
        assert info.value.args[0] == "There is no input value to update"
        with pytest.raises(RuntimeError) as info:
            lumped_design.load_impedance_table.update_row(0)
        assert info.value.args[0] == "There is no input value to update"
        lumped_design.source_impedance_table.update_row(0, "2G", "22", "11")
        assert lumped_design.source_impedance_table.row(0) == ("2G", "22", "11")
        lumped_design.load_impedance_table.update_row(0, "2G", "22", "11")
        assert lumped_design.load_impedance_table.row(0) == ("2G", "22", "11")
        lumped_design.source_impedance_table.update_row(0, frequency="4G")
        assert lumped_design.source_impedance_table.row(0) == ("4G", "22", "11")
        lumped_design.load_impedance_table.update_row(0, frequency="4G")
        assert lumped_design.load_impedance_table.row(0) == ("4G", "22", "11")
        lumped_design.source_impedance_table.update_row(0, "2G", "50", "0")
        assert lumped_design.source_impedance_table.row(0) == ("2G", "50", "0")
        lumped_design.load_impedance_table.update_row(0, "2G", "50", "0")
        assert lumped_design.load_impedance_table.row(0) == ("2G", "50", "0")

    def test_append_row(self, lumped_design):
        lumped_design.topology.complex_termination = True
        lumped_design.source_impedance_table.append_row("100M", "10", "20")
        assert lumped_design.source_impedance_table.row_count == 4
        assert lumped_design.source_impedance_table.row(3) == ("100M", "10", "20")
        lumped_design.topology.complex_termination = True
        lumped_design.load_impedance_table.append_row("100M", "10", "20")
        assert lumped_design.load_impedance_table.row_count == 4
        assert lumped_design.load_impedance_table.row(3) == ("100M", "10", "20")

    def test_insert_row(self, lumped_design):
        lumped_design.topology.complex_termination = True
        lumped_design.source_impedance_table.insert_row(0, "2G", "50", "0")
        assert lumped_design.source_impedance_table.row(0) == ("2G", "50", "0")
        lumped_design.load_impedance_table.insert_row(0, "2G", "50", "0")
        assert lumped_design.load_impedance_table.row(0) == ("2G", "50", "0")

    def test_remove_row(self, lumped_design):
        lumped_design.topology.complex_termination = True
        lumped_design.source_impedance_table.remove_row(0)
        assert lumped_design.source_impedance_table.row(0) == ("1.000G", "1.000", "0.000")
        with pytest.raises(RuntimeError) as info:
            lumped_design.source_impedance_table.row(2)
        assert info.value.args[0] == "No value is set for this band"
        lumped_design.load_impedance_table.remove_row(0)
        assert lumped_design.load_impedance_table.row(0) == ("1.000G", "1.000", "0.000")
        with pytest.raises(RuntimeError) as info:
            lumped_design.load_impedance_table.row(2)
        assert info.value.args[0] == "No value is set for this band"

    def test_complex_definition(self, lumped_design):
        lumped_design.topology.complex_termination = True
        assert len(ComplexTerminationDefinition) == 4
        assert lumped_design.source_impedance_table.complex_definition == ComplexTerminationDefinition.CARTESIAN
        for cdef in ComplexTerminationDefinition:
            lumped_design.source_impedance_table.complex_definition = cdef
            assert lumped_design.source_impedance_table.complex_definition == cdef
        assert lumped_design.load_impedance_table.complex_definition == ComplexTerminationDefinition.CARTESIAN
        for cdef in ComplexTerminationDefinition:
            lumped_design.load_impedance_table.complex_definition = cdef
            assert lumped_design.load_impedance_table.complex_definition == cdef

    def test_reactance_type(self, lumped_design):
        lumped_design.topology.complex_termination = True
        assert len(ComplexReactanceType) == 3
        assert lumped_design.source_impedance_table.reactance_type == ComplexReactanceType.REAC
        for creac in ComplexReactanceType:
            lumped_design.source_impedance_table.reactance_type = creac
            assert lumped_design.source_impedance_table.reactance_type == creac
        assert lumped_design.load_impedance_table.reactance_type == ComplexReactanceType.REAC
        for creac in ComplexReactanceType:
            lumped_design.load_impedance_table.reactance_type = creac
            assert lumped_design.load_impedance_table.reactance_type == creac

    def test_compensation_enabled(self, lumped_design):
        lumped_design.topology.complex_termination = True
        assert lumped_design.source_impedance_table.compensation_enabled is False
        lumped_design.source_impedance_table.compensation_enabled = True
        assert lumped_design.source_impedance_table.compensation_enabled
        assert lumped_design.load_impedance_table.compensation_enabled is False
        lumped_design.load_impedance_table.compensation_enabled = True
        assert lumped_design.load_impedance_table.compensation_enabled

    def test_compensation_order(self, lumped_design):
        lumped_design.topology.complex_termination = True
        lumped_design.source_impedance_table.compensation_enabled = True
        assert lumped_design.source_impedance_table.compensation_order == 2
        with pytest.raises(RuntimeError) as info:
            lumped_design.source_impedance_table.compensation_order = 0
        assert info.value.args[0] == "The minimum impedance compensation order is 1"
        for i in range(1, 22):
            lumped_design.source_impedance_table.compensation_order = i
            assert lumped_design.source_impedance_table.compensation_order == i
        with pytest.raises(RuntimeError) as info:
            lumped_design.source_impedance_table.compensation_order = 22
        assert info.value.args[0] == "The maximum impedance compensation order is 21"
        lumped_design.load_impedance_table.compensation_enabled = True
        assert lumped_design.load_impedance_table.compensation_order == 2
        with pytest.raises(RuntimeError) as info:
            lumped_design.load_impedance_table.compensation_order = 0
        assert info.value.args[0] == "The minimum impedance compensation order is 1"
        for i in range(1, 22):
            lumped_design.load_impedance_table.compensation_order = i
            assert lumped_design.load_impedance_table.compensation_order == i
        with pytest.raises(RuntimeError) as info:
            lumped_design.load_impedance_table.compensation_order = 22
        assert info.value.args[0] == "The maximum impedance compensation order is 21"
