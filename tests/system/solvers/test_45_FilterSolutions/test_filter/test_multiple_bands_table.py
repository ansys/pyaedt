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
    def test_row_count(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        assert lumped_design.multiple_bands_table.row_count == 2

    def test_row(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        assert lumped_design.multiple_bands_table.row(0) == ("2G", "3G")

    def test_update_row(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        with pytest.raises(RuntimeError) as info:
            lumped_design.multiple_bands_table.update_row(0)
        assert info.value.args[0] == "It is not possible to update table with an empty value"
        lumped_design.multiple_bands_table.update_row(0, lower_frequency="100M")
        assert lumped_design.multiple_bands_table.row(0) == ("100M", "3G")
        lumped_design.multiple_bands_table.update_row(0, upper_frequency="4G")
        assert lumped_design.multiple_bands_table.row(0) == ("100M", "4G")
        lumped_design.multiple_bands_table.update_row(0, "200M", "5G")
        assert lumped_design.multiple_bands_table.row(0) == ("200M", "5G")

    def test_append_row(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.multiple_bands_table.append_row("100M", "500M")
        assert lumped_design.multiple_bands_table.row_count == 3
        assert lumped_design.multiple_bands_table.row(2) == ("100M", "500M")
        with pytest.raises(RuntimeError) as info:
            lumped_design.multiple_bands_table.append_row("", "500M")
        assert info.value.args[0] == "It is not possible to append an empty value"
        with pytest.raises(RuntimeError) as info:
            lumped_design.multiple_bands_table.append_row("100M", "")
        assert info.value.args[0] == "It is not possible to append an empty value"

    def test_insert_row(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.multiple_bands_table.insert_row(0, "200M", "5G")
        assert lumped_design.multiple_bands_table.row(0) == ("200M", "5G")
        lumped_design.multiple_bands_table.insert_row(0, lower_frequency="500M", upper_frequency="2G")
        assert lumped_design.multiple_bands_table.row(0) == ("500M", "2G")
        with pytest.raises(RuntimeError) as info:
            lumped_design.multiple_bands_table.insert_row(22, lower_frequency="500M", upper_frequency="2G")
        assert info.value.args[0] == "The rowIndex must be greater than zero and less than row count"

    def test_remove_row(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.multiple_bands_table.remove_row(0)
        assert lumped_design.multiple_bands_table.row(0) == ("4G", "5G")
        with pytest.raises(RuntimeError) as info:
            lumped_design.multiple_bands_table.row(1)
        assert (
            info.value.args[0]
            == "Either no value is set for this band or the rowIndex must be greater than zero and less than row count"
        )

    def test_clear_table(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        # There are 2 rows in the table by default
        assert lumped_design.multiple_bands_table.row_count == 2
        lumped_design.multiple_bands_table.clear_table()
        assert lumped_design.multiple_bands_table.row_count == 0
        # Check if the table is empty for all 7 rows
        for i in range(7):
            with pytest.raises(RuntimeError) as info:
                lumped_design.multiple_bands_table.row(i)
            assert (
                info.value.args[0] == "Either no value is set for this band or the rowIndex must be greater than "
                "zero and less than row count"
            )
