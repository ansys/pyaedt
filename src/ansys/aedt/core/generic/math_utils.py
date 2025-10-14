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

import math
from sys import float_info

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class MathUtils(PyAedtBase):
    """MathUtils is a utility class that provides methods for numerical comparisons and checks."""

    EPSILON = float_info.epsilon * 10.0

    @staticmethod
    @pyaedt_function_handler()
    def is_zero(x: float, eps: float = EPSILON) -> bool:
        """Check if a number is close to zero within a small epsilon tolerance.

        Parameters
        ----------
            x: float
                Number to check.
            eps : float
                Tolerance for the comparison. Default is ``EPSILON``.

        Returns
        -------
            bool
                ``True`` if the number is numerically zero, ``False`` otherwise.

        """
        return abs(x) < eps

    @staticmethod
    @pyaedt_function_handler()
    def is_close(a: float, b: float, relative_tolerance: float = 1e-9, absolute_tolerance: float = 0.0) -> bool:
        """Whether two numbers are close to each other given relative and absolute tolerances.

        Parameters
        ----------
        a : float, int
            First number to compare.
        b : float, int
            Second number to compare.
        relative_tolerance : float
            Relative tolerance. The default value is ``1e-9``.
        absolute_tolerance : float
            Absolute tolerance. The default value is ``0.0``.

        Returns
        -------
        bool
            ``True`` if the two numbers are closed, ``False`` otherwise.
        """
        return abs(a - b) <= max(relative_tolerance * max(abs(a), abs(b)), absolute_tolerance)

    @staticmethod
    @pyaedt_function_handler()
    def is_equal(a: float, b: float, eps: float = EPSILON) -> bool:
        """
        Return True if numbers a and b are equal within a small epsilon tolerance.

        Parameters
        ----------
            a: float
                First number.
            b: float
                Second number.
            eps : float
                Tolerance for the comparison. Default is ``EPSILON``.

        Returns
        -------
            bool
                ``True`` if the absolute difference between a and b is less than epsilon, ``False`` otherwise.
        """
        return abs(a - b) < eps

    @staticmethod
    @pyaedt_function_handler()
    def atan2(y: float, x: float) -> float:
        """Implementation of atan2 that does not suffer from the following issues:
        math.atan2(0.0, 0.0) = 0.0
        math.atan2(-0.0, 0.0) = -0.0
        math.atan2(0.0, -0.0) = 3.141592653589793
        math.atan2(-0.0, -0.0) = -3.141592653589793
        and returns always 0.0.

        Parameters
        ----------
        y : float
            Y-axis value for atan2.

        x : float
            X-axis value for atan2.

        Returns
        -------
        float

        """
        if abs(y) < MathUtils.EPSILON:
            y = 0.0
        if abs(x) < MathUtils.EPSILON:
            x = 0.0
        return math.atan2(y, x)

    @staticmethod
    @pyaedt_function_handler()
    def is_scalar_number(x):
        """Check if a value is a scalar number (int or float).

        Parameters
        ----------
        x : object
            Value to check.

        Returns
        -------
        bool
            ``True`` if x is a scalar number, ``False`` otherwise.
        """
        return isinstance(x, (int, float))

    @staticmethod
    @pyaedt_function_handler()
    def fix_negative_zero(value):
        """Fix the negative zero.
        It supports lists (and nested lists).

        Parameters
        ----------
        value : float, List
            Value to be fixed.

        Returns
        -------
        float, List
            Fixed value.

        """
        if isinstance(value, list):
            return [MathUtils.fix_negative_zero(item) for item in value]
        return 0.0 if value == 0.0 and math.copysign(1.0, value) == -1.0 else value
