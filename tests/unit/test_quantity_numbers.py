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

"""Test Quantity functions."""

import numpy as np
import pandas as pd
import pytest

from ansys.aedt.core.generic.numbers_utils import Quantity


def test_quantity_initialization():
    q = Quantity(10, "meter")
    assert q.value == 10.0
    assert q.unit == "meter"

    q_no_unit_system = Quantity(10, "m")
    assert q_no_unit_system.unit_system is None

    q_zero = Quantity(0, "meter")
    assert q_zero.value == 0.0

    q_negative = Quantity(-5, "meter")
    assert q_negative.value == -5.0


def test_quantity_addition():
    q1 = Quantity(10, "meter")
    q2 = Quantity(5, "meter")
    q3 = q1 + q2
    assert q3.value == 15.0
    assert q3.unit == "meter"

    q4 = Quantity("1GHz")

    with pytest.raises(ValueError):
        _ = q4 + q1

    q5 = Quantity(1000, "mm")
    q6 = Quantity(1, "meter")
    assert q5 + q6 == Quantity(2, "meter")


def test_quantity_subtraction():
    q1 = Quantity(10, "meter")
    q2 = Quantity(5, "meter")
    q3 = q1 - q2
    assert q3.value == 5.0
    assert q3.unit == "meter"

    q4 = Quantity("1GHz")
    with pytest.raises(ValueError):
        _ = q4 - q1


def test_quantity_multiplication():
    q = Quantity(10, "meter")
    q2 = q * 2
    assert q2.value == 20
    assert q2.unit == "meter"

    q3 = Quantity("1GHz")
    q4 = q3 * q
    assert q4.unit == ""


def test_quantity_division():
    q = Quantity(10, "meter")
    q2 = q / 2
    assert q2.value == 5
    assert q2.unit == "meter"

    q3 = Quantity("1GHz")
    q4 = q3 / q
    assert q4.unit == ""


def test_quantity_conversion():
    q = Quantity(1, "km")
    q2 = q.to("meter")
    assert q2.value == 1000.0
    assert q2.unit == "meter"
    q3 = q.to("meter")
    assert q3.value == 1000.0
    assert q3.unit == "meter"


def test_quantity_equality():
    q1 = Quantity(10, "meter")
    q2 = Quantity(10, "meter")
    q3 = Quantity(10000, "mm")

    assert q1 == q2
    assert q1 == q3


def test_quantity_comparison():
    q1 = Quantity(10, "meter")
    q2 = Quantity(5, "meter")
    q3 = Quantity(10, "mm")

    assert q1 > q2
    assert q2 > q3
    assert q1 >= q2
    assert q2 <= q1

    q1 = Quantity(10)
    q2 = Quantity(5)

    assert q1.value == 10.0
    assert q1.unit == ""

    assert q1 > q2
    assert q2 < q1
    assert q1 >= q2
    assert q2 <= q1
    assert q1 != q2


def test_math_operations():
    q = Quantity(4, "meter")
    assert q.sqrt() == Quantity(2, "meter")

    q_rad = Quantity(np.pi / 2, "rad")
    assert np.isclose(q_rad.sin().value, 1.0)
    assert np.isclose(q_rad.cos().value, 0.0)
    assert np.isclose(q_rad.tan().value, np.tan(np.pi / 2))

    q_small = Quantity(0.5, "rad")
    assert np.isclose(q_small.arcsin().value, np.arcsin(0.5))
    assert np.isclose(q_small.arccos().value, np.arccos(0.5))

    q_x = Quantity(1, "meter")
    q_y = Quantity(1, "meter")
    assert np.isclose(q_x.arctan2(q_y).value, np.arctan2(1, 1))


def test_quantity_with_numpy_pandas():
    q1 = Quantity(10, "m")
    q2 = Quantity(5, "m")

    q3_pd = pd.Series([q1, q2])
    q4_pd = pd.Series([q1, q2])

    q3_np = np.array([q1, q2], dtype=Quantity)
    q4_np = np.array([q1, q2], dtype=Quantity)

    q5_np = q3_np + q4_np
    q5_pd = q3_pd + q4_pd

    assert all(q5_np == np.array([Quantity(20, "meter"), Quantity(10, "meter")], dtype=Quantity))
    assert all(q5_pd == pd.Series([Quantity(20, "meter"), Quantity(10, "meter")]))
