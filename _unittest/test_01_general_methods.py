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

import pytest

from pyaedt.generic.DataHandlers import str_to_bool
from pyaedt.generic.general_methods import number_aware_string_key


@pytest.fixture(scope="module", autouse=True)
def desktop():
    return


class TestClass(object):
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

    def test_02_str_to_bool(self):
        test_list_1 = ["one", "two", "five"]
        bool_values = list(map(str_to_bool, test_list_1))
        assert all(isinstance(b, str) for b in bool_values)  # All strings
        test_list_1.append("True")
        assert True in list(map(str_to_bool, test_list_1))
        test_list_2 = ["Stop", "go", "run", "crawl", "False"]
        assert False in list(map(str_to_bool, test_list_2))
