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
from ansys.aedt.core.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_row_count(self):
        design = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        assert design.multiple_bands_table.row_count == 2

    def test_row(self):
        design = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        assert design.multiple_bands_table.row(0) == ("2G", "3G")

    def test_update_row(self):
        design = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        with pytest.raises(RuntimeError) as info:
            design.multiple_bands_table.update_row(0)
        assert info.value.args[0] == "It is not possible to update table with an empty value"
        design.multiple_bands_table.update_row(0, lower_frequency="100M")
        assert design.multiple_bands_table.row(0) == ("100M", "3G")
        design.multiple_bands_table.update_row(0, upper_frequency="4G")
        assert design.multiple_bands_table.row(0) == ("100M", "4G")
        design.multiple_bands_table.update_row(0, "200M", "5G")
        assert design.multiple_bands_table.row(0) == ("200M", "5G")

    def test_append_row(self):
        design = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        design.multiple_bands_table.append_row("100M", "500M")
        assert design.multiple_bands_table.row_count == 3
        assert design.multiple_bands_table.row(2) == ("100M", "500M")
        with pytest.raises(RuntimeError) as info:
            design.multiple_bands_table.append_row("", "500M")
        assert info.value.args[0] == "It is not possible to append an empty value"
        with pytest.raises(RuntimeError) as info:
            design.multiple_bands_table.append_row("100M", "")
        assert info.value.args[0] == "It is not possible to append an empty value"

    def test_insert_row(self):
        design = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        design.multiple_bands_table.insert_row(0, "200M", "5G")
        assert design.multiple_bands_table.row(0) == ("200M", "5G")
        design.multiple_bands_table.insert_row(0, lower_frequency="500M", upper_frequency="2G")
        assert design.multiple_bands_table.row(0) == ("500M", "2G")
        with pytest.raises(RuntimeError) as info:
            design.multiple_bands_table.insert_row(22, lower_frequency="500M", upper_frequency="2G")
        assert info.value.args[0] == "The rowIndex must be greater than zero and less than row count"

    def test_remove_row(self):
        design = ansys.aedt.core.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        design.multiple_bands_table.remove_row(0)
        assert design.multiple_bands_table.row(0) == ("4G", "5G")
        with pytest.raises(RuntimeError) as info:
            design.multiple_bands_table.row(1)
        assert (
            info.value.args[0]
            == "Either no value is set for this band or the rowIndex must be greater than zero and less than row count"
        )
