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

import pytest

from ansys.aedt.core.generic.general_methods import normalize_version_to_string
from ansys.aedt.core.generic.general_methods import number_aware_string_key


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestGeneralMethods:
    def test_00_number_aware_string_key(self):
        assert number_aware_string_key("C1") == ("C", 1)
        assert number_aware_string_key("1234asdf") == (1234, "asdf")
        assert number_aware_string_key("U100") == ("U", 100)
        assert number_aware_string_key("U100X0") == ("U", 100, "X", 0)

    def test_01_number_aware_string_key(self):
        component_names = ["U10", "U2", "C1", "Y1000", "Y200"]
        expected_sort_order = ["C1", "U2", "U10", "Y200", "Y1000"]
        assert sorted(component_names, key=number_aware_string_key) == expected_sort_order
        assert sorted(component_names + [""], key=number_aware_string_key) == [""] + expected_sort_order

    def test_valid_full_year_float(self):
        assert normalize_version_to_string(2023.2) == "2023.2"
        assert normalize_version_to_string("2024.5") == "2024.5"

    def test_valid_short_year_float(self):
        assert normalize_version_to_string(23.4) == "2023.4"
        assert normalize_version_to_string("25.9") == "2025.9"

    def test_valid_int_formats(self):
        assert normalize_version_to_string(232) == "2023.2"
        assert normalize_version_to_string("245") == "2024.5"

    def test_valid_string_R_formats(self):
        assert normalize_version_to_string("2025R2") == "2025.2"
        assert normalize_version_to_string("2025 R2") == "2025.2"
        assert normalize_version_to_string("25R2") == "2025.2"
        assert normalize_version_to_string("25 R2") == "2025.2"

    def test_invalid_types(self):
        with pytest.raises(ValueError):
            normalize_version_to_string([2023.2])  # list not allowed
        with pytest.raises(ValueError):
            normalize_version_to_string({"year": 2023.2})  # dict not allowed
        with pytest.raises(ValueError):
            normalize_version_to_string(None)

    def test_invalid_formats(self):
        with pytest.raises(ValueError):
            normalize_version_to_string("20232")  # too many digits
        with pytest.raises(ValueError):
            normalize_version_to_string("2023.23")  # too many decimals
        with pytest.raises(ValueError):
            normalize_version_to_string("23")  # too short
        with pytest.raises(ValueError):
            normalize_version_to_string("1999.2")  # not 20XX
        with pytest.raises(ValueError):
            normalize_version_to_string("20A3.2")  # invalid chars
        with pytest.raises(ValueError):
            normalize_version_to_string("2025 R")  # missing digit after R

    def test_edge_cases(self):
        assert normalize_version_to_string("2000.0") == "2000.0"  # earliest year
        assert normalize_version_to_string("2099.9") == "2099.9"  # latest year
        assert normalize_version_to_string("00.1") == "2000.1"  # short float lowest
        assert normalize_version_to_string("99.9") == "2099.9"  # short float highest
        assert normalize_version_to_string("000") == "2000.0"  # int lowest
        assert normalize_version_to_string("999") == "2099.9"  # int highest
        assert normalize_version_to_string("00R1") == "2000.1"  # short R format
        assert normalize_version_to_string("99R9") == "2099.9"  # short R format max
        assert normalize_version_to_string("2000R1") == "2000.1"  # long R format
        assert normalize_version_to_string("2099R9") == "2099.9"  # long R format max
