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

from ansys.aedt.core.generic.settings import is_linux
import pytest

from tests.system.solvers.conftest import config


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    no_transmission_zero_msg = "This filter has no transmission zero at row 0"
    no_transmission_zero_update_msg = "This filter has no transmission zero at row 0 to update"
    input_value_blank_msg = "The input value is blank"

    def test_row_count(self, lumped_design):
        assert lumped_design.transmission_zeros_bandwidth.row_count == 0
        assert lumped_design.transmission_zeros_ratio.row_count == 0

    def test_row(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.row(0)
        assert info.value.args[0] == self.no_transmission_zero_msg
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.row(0)
        assert info.value.args[0] == self.no_transmission_zero_msg

    def test_update_row(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.update_row(0, zero="1.3G", position="2")
        assert info.value.args[0] == self.no_transmission_zero_update_msg
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.update_row(0, "1.3", "2")
        assert info.value.args[0] == self.no_transmission_zero_update_msg

    def test_append_row(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.append_row(zero="", position="")
        assert info.value.args[0] == self.input_value_blank_msg
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.append_row("", "")
        assert info.value.args[0] == self.input_value_blank_msg
        lumped_design.transmission_zeros_bandwidth.append_row("1600M")
        assert lumped_design.transmission_zeros_bandwidth.row(0) == ("1600M", "")
        lumped_design.transmission_zeros_bandwidth.clear_table()
        lumped_design.transmission_zeros_bandwidth.append_row(zero="1600M", position="2")
        assert lumped_design.transmission_zeros_bandwidth.row(0) == ("1600M", "2")
        lumped_design.transmission_zeros_bandwidth.clear_table()
        lumped_design.transmission_zeros_ratio.append_row("1.6")
        assert lumped_design.transmission_zeros_ratio.row(0) == ("1.6", "")
        lumped_design.transmission_zeros_ratio.clear_table()
        lumped_design.transmission_zeros_ratio.append_row(zero="1.6", position="2")
        assert lumped_design.transmission_zeros_ratio.row(0) == ("1.6", "2")

    def test_insert_row(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.insert_row(6, zero="1.3G", position="2")
        assert info.value.args[0] == "The given index 6 is larger than zeros order"
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.insert_row(6, "1.3", "2")
        assert info.value.args[0] == "The given index 6 is larger than zeros order"
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.insert_row(0, zero="", position="2")
        assert info.value.args[0] == self.input_value_blank_msg
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.insert_row(0, "", "")
        assert info.value.args[0] == self.input_value_blank_msg
        lumped_design.transmission_zeros_bandwidth.insert_row(0, "1600M")
        assert lumped_design.transmission_zeros_bandwidth.row(0) == ("1600M", "")
        lumped_design.transmission_zeros_bandwidth.insert_row(0, zero="1600M", position="2")
        assert lumped_design.transmission_zeros_bandwidth.row(0) == ("1600M", "2")
        lumped_design.transmission_zeros_bandwidth.clear_table()
        lumped_design.transmission_zeros_ratio.insert_row(0, "1.6")
        assert lumped_design.transmission_zeros_ratio.row(0) == ("1.6", "")
        lumped_design.transmission_zeros_ratio.insert_row(0, zero="1.6", position="2")
        assert lumped_design.transmission_zeros_ratio.row(0) == ("1.6", "2")

    def test_remove_row(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.remove_row(2)
        assert info.value.args[0] == "The given index 2 is larger than zeros order"
        lumped_design.transmission_zeros_bandwidth.append_row(zero="1600M", position="2")
        lumped_design.transmission_zeros_bandwidth.remove_row(0)
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.row(0)
        assert info.value.args[0] == self.no_transmission_zero_msg

    def test_clear_table(self, lumped_design):
        lumped_design.transmission_zeros_bandwidth.insert_row(0, zero="1600M", position="2")
        assert lumped_design.transmission_zeros_bandwidth.row(0) == ("1600M", "2")
        lumped_design.transmission_zeros_bandwidth.clear_table()
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_bandwidth.row(0)
        assert info.value.args[0] == self.no_transmission_zero_msg
        lumped_design.transmission_zeros_ratio.insert_row(0, zero="1.6", position="2")
        assert lumped_design.transmission_zeros_ratio.row(0) == ("1.6", "2")
        lumped_design.transmission_zeros_ratio.clear_table()
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.row(0)
        assert info.value.args[0] == self.no_transmission_zero_msg

    def test_restore_default_positions(self, lumped_design):
        lumped_design.transmission_zeros_bandwidth.insert_row(0, zero="1600M", position="2")
        lumped_design.transmission_zeros_bandwidth.restore_default_positions()
        assert lumped_design.transmission_zeros_bandwidth.row(0) == ("1600M", "3")
        lumped_design.transmission_zeros_ratio.insert_row(0, zero="1.6", position="2")
        lumped_design.transmission_zeros_ratio.restore_default_positions()
        assert lumped_design.transmission_zeros_ratio.row(0) == ("1.6", "3")
