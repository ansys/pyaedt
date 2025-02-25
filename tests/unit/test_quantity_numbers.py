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

"""Test Quantity functions.
"""

from ansys.aedt.core.generic.numbers import Quantity


def test_quantity_initialization():
    q = Quantity(10, "m")
    assert q.value == 10.0
    assert q.unit == "m"


def test_quantity_addition():
    q1 = Quantity(10, "m")
    q2 = Quantity(5, "m")
    q3 = q1 + q2
    assert q3.value == 15.0
    assert q3.unit == "m"


def test_quantity_subtraction():
    q1 = Quantity(10, "m")
    q2 = Quantity(5, "m")
    q3 = q1 - q2
    assert q3.value == 5.0
    assert q3.unit == "m"


def test_quantity_multiplication():
    q = Quantity(10, "m")
    q2 = q * 2
    assert q2.value == 20
    assert q2.unit == "m"


def test_quantity_division():
    q = Quantity(10, "m")
    q2 = q / 2
    assert q2.value == 5
    assert q2.unit == "m"


def test_quantity_conversion():
    q = Quantity(1, "km")
    q2 = q.to("meter")
    assert q2.value == 1000.0
    assert q2.unit == "meter"
    q3 = q.to("m")
    assert q3.value == 1000.0
    assert q3.unit == "m"


def test_quantity_equality():
    q1 = Quantity(10, "m")
    q2 = Quantity(10, "m")
    assert q1 == q2


def test_quantity_comparison():
    q1 = Quantity(10, "m")
    q2 = Quantity(5, "m")
    assert q1 > q2
    assert q2 < q1
    assert q1 >= q2
    assert q2 <= q1
