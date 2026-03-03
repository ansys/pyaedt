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

import math

import pytest

from ansys.aedt.core.generic.math_utils import MathUtils


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestMathUtils:
    def test_is_zero(self) -> None:
        assert MathUtils.is_zero(0.0) is True
        assert MathUtils.is_zero(1e-15) is True
        assert MathUtils.is_zero(1e-5) is False

    def test_is_close(self) -> None:
        assert MathUtils.is_close(1.0, 1.0 + 1e-10) is True
        assert MathUtils.is_close(1.0, 1.1) is False
        assert MathUtils.is_close(1.0, 1.0, relative_tolerance=0.0, absolute_tolerance=0.1) is True

    def test_is_equal(self) -> None:
        assert MathUtils.is_equal(1.0, 1.0 + 1e-15) is True
        assert MathUtils.is_equal(1.0, 1.1) is False

    def test_atan2(self) -> None:
        assert MathUtils.atan2(0.0, 0.0) == 0.0
        assert MathUtils.atan2(-0.0, 0.0) == 0.0
        assert MathUtils.atan2(0.0, -0.0) == 0.0
        assert MathUtils.atan2(-0.0, -0.0) == 0.0
        assert MathUtils.atan2(1, 2) == math.atan2(1, 2)

    def test_is_scalar_number(self) -> None:
        assert MathUtils.is_scalar_number(1) is True
        assert MathUtils.is_scalar_number(1.0) is True
        assert MathUtils.is_scalar_number("string") is False
        assert MathUtils.is_scalar_number([1, 2, 3]) is False

    def test_fix_negative_zero(self) -> None:
        assert MathUtils.fix_negative_zero(-0.0) == 0.0
        assert MathUtils.fix_negative_zero(0.0) == 0.0
        assert MathUtils.fix_negative_zero([-0.0, 0.0, -1.0]) == [0.0, 0.0, -1.0]
        assert MathUtils.fix_negative_zero([[-0.0], [0.0, -1.0]]) == [[0.0], [0.0, -1.0]]
