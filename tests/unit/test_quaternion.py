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
from ansys.aedt.core.generic.quaternion import Quaternion
from ansys.aedt.core.modeler.cad.primitives import CoordinateSystem as cs
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators

tol = MathUtils.EPSILON
is_vector_equal = GeometryOperators.is_vector_equal


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestQuaternion:
    def test_initialization(self) -> None:
        q = Quaternion(1, 2, 3, 4)
        assert q.a == 1
        assert q.b == 2
        assert q.c == 3
        assert q.d == 4

    def test_initialization_default(self) -> None:
        q_default = Quaternion()
        assert q_default.a == 0.0
        assert q_default.b == 0.0
        assert q_default.c == 0.0
        assert q_default.d == 0.0

    def test_initialization_invalid(self) -> None:
        with pytest.raises(TypeError):
            Quaternion("a", 2.0, 3.0, 4.0)

    def test_to_quaternion_with_quaternion(self) -> None:
        # Test with an existing Quaternion object
        q = Quaternion(1, 2, 3, 4)
        result = Quaternion._to_quaternion(q)
        assert result.a == 1
        assert result.b == 2
        assert result.c == 3
        assert result.d == 4

    def test_to_quaternion_with_tuple(self) -> None:
        # Test with a tuple
        q_tuple = (5, 6, 7, 8)
        result = Quaternion._to_quaternion(q_tuple)
        assert result.a == 5
        assert result.b == 6
        assert result.c == 7
        assert result.d == 8

    def test_to_quaternion_with_list(self) -> None:
        # Test with a list
        q_list = [9, 10, 11, 12]
        result = Quaternion._to_quaternion(q_list)
        assert result.a == 9
        assert result.b == 10
        assert result.c == 11
        assert result.d == 12

    def test_to_quaternion_with_invalid_type(self) -> None:
        # Test with an invalid type
        with pytest.raises(TypeError, match="Cannot convert .* to Quaternion."):
            Quaternion._to_quaternion("invalid_input")

    def test_to_quaternion_with_invalid_length(self) -> None:
        # Test with a tuple of invalid length
        with pytest.raises(TypeError, match="Cannot convert .* to Quaternion."):
            Quaternion._to_quaternion((1, 2, 3))

    def test_valid_sequences(self) -> None:
        # Test valid rotation sequences
        assert Quaternion._is_valid_rotation_sequence("xyz") is True
        assert Quaternion._is_valid_rotation_sequence("ZYX") is True
        assert Quaternion._is_valid_rotation_sequence("xYz") is True

    def test_invalid_sequences_length(self) -> None:
        # Test invalid sequences with incorrect length
        assert Quaternion._is_valid_rotation_sequence("xy") is False
        assert Quaternion._is_valid_rotation_sequence("xyzz") is False

    def test_invalid_sequences_characters(self) -> None:
        # Test invalid sequences with unsupported characters
        assert Quaternion._is_valid_rotation_sequence("abc") is False
        assert Quaternion._is_valid_rotation_sequence("123") is False
        assert Quaternion._is_valid_rotation_sequence("x1z") is False

    def test_invalid_type(self) -> None:
        # Test invalid input types
        assert Quaternion._is_valid_rotation_sequence(123) is False
        assert Quaternion._is_valid_rotation_sequence(None) is False
        assert Quaternion._is_valid_rotation_sequence(["x", "y", "z"]) is False

    def test_add_two_quaternions(self) -> None:
        # Test addition of two quaternions
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        result = q1.add(q2)
        assert result.a == 6
        assert result.b == 8
        assert result.c == 10
        assert result.d == 12

    def test_add_quaternion_and_scalar(self) -> None:
        # Test addition of a quaternion and a scalar
        q = Quaternion(1, 2, 3, 4)
        scalar = 5
        result = q.add(scalar)
        assert result.a == 6
        assert result.b == 2
        assert result.c == 3
        assert result.d == 4

    def test_add_scalar_and_quaternion(self) -> None:
        # Test addition of a scalar and a quaternion
        scalar = 3
        q = Quaternion(1, 2, 3, 4)
        result = q + scalar
        assert result.a == 4
        assert result.b == 2
        assert result.c == 3
        assert result.d == 4

    def test_add_quaternion_and_list(self) -> None:
        # Test addition of a quaternion and a list
        q = Quaternion(1, 2, 3, 4)
        other = [5, 6, 7, 8]
        result = q.add(other)
        assert result.a == 6
        assert result.b == 8
        assert result.c == 10
        assert result.d == 12

    def test_add_quaternion_and_tuple(self) -> None:
        # Test addition of a quaternion and a tuple
        q = Quaternion(1, 2, 3, 4)
        other = (5, 6, 7, 8)
        result = q.add(other)
        assert result.a == 6
        assert result.b == 8
        assert result.c == 10
        assert result.d == 12

    def test_addition(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        q3 = q1 + q2
        assert q3.a == 6
        assert q3.b == 8
        assert q3.c == 10
        assert q3.d == 12
        q4 = q1 + 5
        assert q4.a == 6
        assert q4.b == 2
        assert q4.c == 3
        assert q4.d == 4
        q5 = 5 + q1
        assert q5.a == 6
        assert q5.b == 2
        assert q5.c == 3
        assert q5.d == 4

    def test_subtract_two_quaternions(self) -> None:
        # Test subtraction of two quaternions
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        result = q1 - q2
        assert result.a == -4
        assert result.b == -4
        assert result.c == -4
        assert result.d == -4

    def test_negative(self) -> None:
        # Test negation of a quaternion
        q = Quaternion(1, 2, 3, 4)
        result = -q
        assert result.a == -1
        assert result.b == -2
        assert result.c == -3
        assert result.d == -4

    def test_hamilton_prod_general(self) -> None:
        # Test Hamilton product of two general quaternions
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        result = Quaternion.hamilton_prod(q1, q2)
        assert result.a == -60
        assert result.b == 12
        assert result.c == 30
        assert result.d == 24

    def test_hamilton_prod_with_identity(self) -> None:
        # Test Hamilton product with the identity quaternion
        q1 = Quaternion(1, 2, 3, 4)
        identity = Quaternion(1, 0, 0, 0)
        result = Quaternion.hamilton_prod(q1, identity)
        assert result.a == q1.a
        assert result.b == q1.b
        assert result.c == q1.c
        assert result.d == q1.d

    def test_hamilton_prod_with_zero(self) -> None:
        # Test Hamilton product with a zero quaternion
        q1 = Quaternion(1, 2, 3, 4)
        zero = Quaternion(0, 0, 0, 0)
        result = Quaternion.hamilton_prod(q1, zero)
        assert result.a == 0
        assert result.b == 0
        assert result.c == 0
        assert result.d == 0

    def test_hamilton_prod_commutativity(self) -> None:
        # Test non-commutativity of Hamilton product
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        result1 = Quaternion.hamilton_prod(q1, q2)
        result2 = Quaternion.hamilton_prod(q2, q1)
        assert result1 != result2

    def test_q_prod_two_quaternions(self) -> None:
        # Test multiplication of two quaternions
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        result = Quaternion._q_prod(q1, q2)
        assert result.a == -60
        assert result.b == 12
        assert result.c == 30
        assert result.d == 24

    def test_q_prod_quaternion_and_scalar(self) -> None:
        # Test multiplication of a quaternion and a scalar
        q = Quaternion(1, 2, 3, 4)
        scalar = 2
        result = Quaternion._q_prod(q, scalar)
        assert result.a == 2
        assert result.b == 4
        assert result.c == 6
        assert result.d == 8

    def test_q_prod_scalar_and_quaternion(self) -> None:
        # Test multiplication of a scalar and a quaternion
        scalar = 3
        q = Quaternion(1, 2, 3, 4)
        result = Quaternion._q_prod(scalar, q)
        assert result.a == 3
        assert result.b == 6
        assert result.c == 9
        assert result.d == 12

    def test_q_prod_two_scalars(self) -> None:
        # Test multiplication of two scalars
        scalar1 = 3
        scalar2 = 4
        result = Quaternion._q_prod(scalar1, scalar2)
        assert result == 12

    def test_multiplication(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        q3 = q1 * q2
        assert q3.a == -60
        assert q3.b == 12
        assert q3.c == 30
        assert q3.d == 24
        q4 = q1 * 5
        assert q4.a == 5
        assert q4.b == 10
        assert q4.c == 15
        assert q4.d == 20
        q5 = 5 * q1
        assert q5.a == 5
        assert q5.b == 10
        assert q5.c == 15
        assert q5.d == 20

    def test_mul(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(5, 6, 7, 8)
        q3 = q1.mul(q2)
        assert q3.a == -60
        assert q3.b == 12
        assert q3.c == 30
        assert q3.d == 24
        q4 = q1.mul(5)
        assert q4.a == 5
        assert q4.b == 10
        assert q4.c == 15
        assert q4.d == 20

    def test_conjugate(self) -> None:
        # Test conjugate of a general quaternion
        q = Quaternion(1, 2, 3, 4)
        qc = q.conjugate()
        assert qc.a == 1
        assert qc.b == -2
        assert qc.c == -3
        assert qc.d == -4

    def test_conjugate_unit_quaternion(self) -> None:
        # Test conjugate of a unit quaternion
        q = Quaternion(1, 0, 0, 0)
        qc = q.conjugate()
        assert qc.a == 1
        assert qc.b == 0
        assert qc.c == 0
        assert qc.d == 0

    def test_conjugate_zero_quaternion(self) -> None:
        # Test conjugate of a zero quaternion
        q = Quaternion(0, 0, 0, 0)
        qc = q.conjugate()
        assert qc.a == 0
        assert qc.b == 0
        assert qc.c == 0
        assert qc.d == 0

    def test_norm(self) -> None:
        # Test norm of a general quaternion
        q = Quaternion(1, 2, 3, 4)
        expected_norm = math.sqrt(1**2 + 2**2 + 3**2 + 4**2)
        assert MathUtils.is_close(q.norm(), expected_norm)

    def test_norm_unit_quaternion(self) -> None:
        # Test norm of a unit quaternion
        q = Quaternion(1 / math.sqrt(2), 0, 1 / math.sqrt(2), 0)
        assert MathUtils.is_close(q.norm(), 1.0)

    def test_norm_zero_quaternion(self) -> None:
        # Test norm of a zero quaternion
        q = Quaternion(0, 0, 0, 0)
        assert MathUtils.is_close(q.norm(), 0.0)

    def test_normalize(self) -> None:
        # Test normalization of a non-zero quaternion
        q = Quaternion(1, 2, 3, 4)
        qn = q.normalize()
        norm = math.sqrt(1**2 + 2**2 + 3**2 + 4**2)
        assert MathUtils.is_close(qn.a, 1 / norm)
        assert MathUtils.is_close(qn.b, 2 / norm)
        assert MathUtils.is_close(qn.c, 3 / norm)
        assert MathUtils.is_close(qn.d, 4 / norm)
        assert MathUtils.is_close(qn.norm(), 1.0)

    def test_normalize_unit_quaternion(self) -> None:
        # Test normalization of a unit quaternion (should remain unchanged)
        q = Quaternion(1 / math.sqrt(2), 0, 1 / math.sqrt(2), 0)
        qn = q.normalize()
        assert MathUtils.is_close(qn.a, q.a)
        assert MathUtils.is_close(qn.b, q.b)
        assert MathUtils.is_close(qn.c, q.c)
        assert MathUtils.is_close(qn.d, q.d)
        assert MathUtils.is_close(qn.norm(), 1.0)

    def test_normalize_zero_norm(self) -> None:
        # Test normalization of a zero-norm quaternion
        q = Quaternion(0, 0, 0, 0)
        with pytest.raises(ValueError, match="Cannot normalize a quaternion with zero norm."):
            q.normalize()

    def test_inverse(self) -> None:
        # Test inverse of a non-zero quaternion
        q = Quaternion(1, 2, 3, 4)
        qi = q.inverse()
        q_identity = q * qi
        assert MathUtils.is_close(qi.a, 1.0 / 30)
        assert MathUtils.is_close(qi.b, -1.0 / 15)
        assert MathUtils.is_close(qi.c, -1.0 / 10)
        assert MathUtils.is_close(qi.d, -1.0 / 7.5)
        assert MathUtils.is_close(q_identity.a, 1.0)
        assert MathUtils.is_close(q_identity.b, 0.0)
        assert MathUtils.is_close(q_identity.c, 0.0)
        assert MathUtils.is_close(q_identity.d, 0.0)

    def test_inverse_unit_quaternion(self) -> None:
        # Test inverse of a unit quaternion
        q = Quaternion(1, 0, 0, 0)
        qi = q.inverse()
        assert qi.a == 1
        assert qi.b == 0
        assert qi.c == 0
        assert qi.d == 0

    def test_inverse_zero_norm(self) -> None:
        # Test inverse of a zero-norm quaternion
        q = Quaternion(0, 0, 0, 0)
        with pytest.raises(ValueError, match="Cannot compute inverse for a quaternion with zero norm"):
            q.inverse()

    def test_division(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(1, -1, 1, 2)
        q3 = q1 / q2
        assert MathUtils.is_close(q3.a, 10 / 7)
        assert MathUtils.is_close(q3.b, 1 / 7)
        assert MathUtils.is_close(q3.c, 10 / 7)
        assert MathUtils.is_close(q3.d, -3 / 7)
        q4 = q1 / 5
        assert MathUtils.is_close(q4.a, 0.2)
        assert MathUtils.is_close(q4.b, 0.4)
        assert MathUtils.is_close(q4.c, 0.6)
        assert MathUtils.is_close(q4.d, 0.8)
        q5 = 5 / q1
        assert MathUtils.is_close(q5.a, 1 / 6)
        assert MathUtils.is_close(q5.b, -1 / 3)
        assert MathUtils.is_close(q5.c, -0.5)
        assert MathUtils.is_close(q5.d, -2 / 3)

    def test_div(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(1, -1, 1, 2)
        q3 = q1.div(q2)
        assert MathUtils.is_close(q3.a, 10 / 7)
        assert MathUtils.is_close(q3.b, 1 / 7)
        assert MathUtils.is_close(q3.c, 10 / 7)
        assert MathUtils.is_close(q3.d, -3 / 7)
        q4 = q1.div(5)
        assert MathUtils.is_close(q4.a, 0.2)
        assert MathUtils.is_close(q4.b, 0.4)
        assert MathUtils.is_close(q4.c, 0.6)
        assert MathUtils.is_close(q4.d, 0.8)

    def test_division_by_scalar(self) -> None:
        q = Quaternion(1, 2, 3, 4)
        result = Quaternion._q_div(q, 2)
        assert result.a == 0.5
        assert result.b == 1.0
        assert result.c == 1.5
        assert result.d == 2.0

    def test_scalar_division_by_quaternion(self) -> None:
        q = Quaternion(1, 2, 3, 4)
        result = Quaternion._q_div(2, q)
        assert pytest.approx(result.a) == 1 / 15
        assert pytest.approx(result.b) == -2 / 15
        assert pytest.approx(result.c) == -1 / 5
        assert pytest.approx(result.d) == -4 / 15

    def test_quaternion_division(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(1, -1, 1, 2)
        result = Quaternion._q_div(q1, q2)
        assert pytest.approx(result.a) == 10 / 7
        assert pytest.approx(result.b) == 1 / 7
        assert pytest.approx(result.c) == 10 / 7
        assert pytest.approx(result.d) == -3 / 7

    def test_division_by_zero_scalar(self) -> None:
        q = Quaternion(1, 2, 3, 4)
        with pytest.raises(ZeroDivisionError):
            Quaternion._q_div(q, 0)

    def test_division_by_zero_quaternion(self) -> None:
        q1 = Quaternion(1, 2, 3, 4)
        q2 = Quaternion(0, 0, 0, 0)
        with pytest.raises(ValueError, match="Cannot compute inverse for a quaternion with zero norm"):
            Quaternion._q_div(q1, q2)

    def test_division_two_scalar(self) -> None:
        result = Quaternion._q_div(10, 7)
        assert pytest.approx(result) == 10 / 7

    def test_eq_method(self) -> None:
        # Test equality of two identical quaternions
        q1 = Quaternion(1.0, 2.0, 3.0, 4.0)
        q2 = Quaternion(1.0, 2.0, 3.0, 4.0)
        assert q1 == q2

        # Test inequality of two different quaternions
        q3 = Quaternion(1.0, 2.0, 3.0, 5.0)
        assert q1 != q3

        # Test equality with floating-point precision
        q4 = Quaternion(1.0 + 1e-15, 2.0, 3.0, 4.0)
        assert q1 == q4

        # Test inequality with a non-Quaternion object
        assert q1 != (1.0, 2.0, 3.0, 4.0)

    def test_repr_method(self) -> None:
        # Test string representation of a quaternion
        q = Quaternion(1.0, 2.0, 3.0, 4.0)
        expected_repr = "Quaternion(1.0, 2.0, 3.0, 4.0)"
        assert repr(q) == expected_repr

    def test_coefficients(self) -> None:
        # Test with default quaternion
        q = Quaternion()
        assert q.coefficients() == (0.0, 0.0, 0.0, 0.0)

        # Test with positive coefficients
        q = Quaternion(1, 2, 3, 4)
        assert q.coefficients() == (1, 2, 3, 4)

        # Test with negative coefficients
        q = Quaternion(-1, -2, -3, -4)
        assert q.coefficients() == (-1, -2, -3, -4)

        # Test with mixed coefficients
        q = Quaternion(1.5, -2.5, 3.5, -4.5)
        assert q.coefficients() == (1.5, -2.5, 3.5, -4.5)

    def test_from_euler_valid_xyz(self) -> None:
        # Test valid Euler angles with 'xyz' sequence
        angles = [math.pi / 2, 0, 0]
        q = Quaternion.from_euler(angles, "xyz")
        assert MathUtils.is_close(q.a, 0.7071067811865476)
        assert MathUtils.is_close(q.b, 0.7071067811865476)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.0)

    def test_from_euler_valid_zyz_extrinsic(self) -> None:
        # Test valid Euler angles with 'zyz' sequence and extrinsic rotation
        angles = [0, math.pi / 2, math.pi]
        q = Quaternion.from_euler(angles, "zyz", extrinsic=True)
        assert MathUtils.is_close(q.a, 0.0)
        assert MathUtils.is_close(q.b, -0.7071067811865476)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.7071067811865476)

    def test_from_euler_invalid_angles_length(self) -> None:
        # Test invalid angles length
        angles = [math.pi / 2, 0]
        with pytest.raises(ValueError, match="Three rotation angles are required."):
            Quaternion.from_euler(angles, "xyz")

    def test_from_euler_invalid_sequence(self) -> None:
        # Test invalid rotation sequence
        angles = [math.pi / 2, 0, 0]
        with pytest.raises(
            ValueError, match="sequence must be a 3-character string, using only the axes 'x', 'y', or 'z'."
        ):
            Quaternion.from_euler(angles, "abc")

    def test_from_euler_case_insensitivity(self) -> None:
        # Test case insensitivity of the sequence
        angles = [math.pi / 2, 0, 0]
        q = Quaternion.from_euler(angles, "XYZ")
        assert MathUtils.is_close(q.a, 0.7071067811865476)
        assert MathUtils.is_close(q.b, 0.7071067811865476)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.0)

    def test_to_euler_valid_xyz(self) -> None:
        # Test valid quaternion to Euler angles with 'xyz' sequence
        q = Quaternion(0.7071067811865476, 0.7071067811865476, 0, 0)
        angles = q.to_euler("xyz")
        assert MathUtils.is_close(angles[0], math.pi / 2)
        assert MathUtils.is_close(angles[1], 0)
        assert MathUtils.is_close(angles[2], 0)

    def test_to_euler_valid_zyz_extrinsic(self) -> None:
        # Test valid quaternion to Euler angles with 'zyz' sequence and extrinsic rotation
        q = Quaternion(0, -0.7071067811865476, 0, 0.7071067811865476)
        angles = q.to_euler("zyz", extrinsic=True)
        assert MathUtils.is_close(angles[0], 0)
        assert MathUtils.is_close(angles[1], math.pi / 2)
        assert MathUtils.is_close(angles[2], math.pi)

    def test_to_euler_invalid_sequence(self) -> None:
        # Test invalid rotation sequence
        q = Quaternion(1, 0, 0, 0)
        with pytest.raises(
            ValueError, match="sequence must be a 3-character string, using only the axes 'x', 'y', or 'z'."
        ):
            q.to_euler("abc")

    def test_to_euler_zero_norm(self) -> None:
        # Test quaternion with zero norm
        q = Quaternion(0, 0, 0, 0)
        with pytest.raises(ValueError, match="A quaternion with norm 0 cannot be converted."):
            q.to_euler("xyz")

    def test_to_euler_case_insensitivity(self) -> None:
        # Test case insensitivity of the sequence
        q = Quaternion(0.7071067811865476, 0.7071067811865476, 0, 0)
        angles = q.to_euler("XYZ")
        assert MathUtils.is_close(angles[0], math.pi / 2)
        assert MathUtils.is_close(angles[1], 0)
        assert MathUtils.is_close(angles[2], 0)

    def test_to_euler_case_degenarate1_extrinsic(self) -> None:
        # Test case insensitivity of the sequence
        q = Quaternion(0.7071067811865476, 0.7071067811865476, 0, 0)
        angles = q.to_euler("XYZ", extrinsic=True)
        assert MathUtils.is_close(angles[0], math.pi / 2)
        assert MathUtils.is_close(angles[1], 0)
        assert MathUtils.is_close(angles[2], 0)

    def test_to_euler_case_degenarate2_extrinsic(self) -> None:
        # Test case insensitivity of the sequence
        q = Quaternion(0, 0, 1, 1)
        angles = q.to_euler("XYZ", extrinsic=True)
        assert MathUtils.is_close(angles[0], math.pi / 2)
        assert MathUtils.is_close(angles[1], 0)
        assert MathUtils.is_close(angles[2], math.pi)

    def test_from_axis_angle_valid(self) -> None:
        # Test valid axis and angle
        axis = (1, 0, 0)
        angle = math.pi / 2
        q = Quaternion.from_axis_angle(axis, angle)
        assert MathUtils.is_close(q.a, math.sqrt(2) / 2)
        assert MathUtils.is_close(q.b, math.sqrt(2) / 2)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.0)

    def test_from_axis_angle_normalized_axis(self) -> None:
        # Test with a non-normalized axis
        axis = (2, 0, 0)
        angle = math.pi / 2
        q = Quaternion.from_axis_angle(axis, angle)
        assert MathUtils.is_close(q.a, math.sqrt(2) / 2)
        assert MathUtils.is_close(q.b, math.sqrt(2) / 2)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.0)

    def test_from_axis_angle_zero_angle(self) -> None:
        # Test with zero angle
        axis = (0, 1, 0)
        angle = 0
        q = Quaternion.from_axis_angle(axis, angle)
        assert MathUtils.is_close(q.a, 1.0)
        assert MathUtils.is_close(q.b, 0.0)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.0)

    def test_from_axis_angle_invalid_axis_length(self) -> None:
        # Test with an invalid axis length
        axis = (1, 0)
        angle = math.pi / 2
        with pytest.raises(ValueError, match="axis must be a list or tuple containing 3 floats."):
            Quaternion.from_axis_angle(axis, angle)

    def test_from_axis_angle_zero_axis(self) -> None:
        # Test with a zero vector as axis
        axis = (0, 0, 0)
        angle = math.pi / 2
        with pytest.raises(ValueError, match="axis must be a non-zero vector."):
            Quaternion.from_axis_angle(axis, angle)

    def test_to_axis_angle_valid(self) -> None:
        # Test valid quaternion to axis and angle
        q = Quaternion(math.sqrt(2) / 2, math.sqrt(2) / 2, 0, 0)
        axis, angle = q.to_axis_angle()
        assert MathUtils.is_close(axis[0], 1.0)
        assert MathUtils.is_close(axis[1], 0.0)
        assert MathUtils.is_close(axis[2], 0.0)
        assert MathUtils.is_close(angle, math.pi / 2)

    def test_to_axis_angle_zero_rotation(self) -> None:
        # Test quaternion representing zero rotation
        q = Quaternion(1, 0, 0, 0)
        axis, angle = q.to_axis_angle()
        assert MathUtils.is_close(axis[0], 1.0)
        assert MathUtils.is_close(axis[1], 0.0)
        assert MathUtils.is_close(axis[2], 0.0)
        assert MathUtils.is_close(angle, 0.0)

    def test_to_axis_angle_invalid_zero_norm(self) -> None:
        # Test quaternion with zero norm
        q = Quaternion(0, 0, 0, 0)
        with pytest.raises(ValueError, match="A quaternion with norm 0 cannot be converted."):
            q.to_axis_angle()

    def test_to_axis_angle_negative_w(self) -> None:
        # Test quaternion with negative scalar part
        q = Quaternion(-math.sqrt(2) / 2, math.sqrt(2) / 2, 0, 0)
        axis, angle = q.to_axis_angle()
        assert MathUtils.is_close(axis[0], -1.0)
        assert MathUtils.is_close(axis[1], 0.0)
        assert MathUtils.is_close(axis[2], 0.0)
        assert MathUtils.is_close(angle, math.pi / 2)

    def test_to_axis_angle_normalized(self) -> None:
        # Test quaternion normalization before conversion
        q = Quaternion(2, 2, 0, 0)
        axis, angle = q.to_axis_angle()
        assert MathUtils.is_close(axis[0], 1.0)
        assert MathUtils.is_close(axis[1], 0.0)
        assert MathUtils.is_close(axis[2], 0.0)
        assert MathUtils.is_close(angle, math.pi / 2)

    def test_from_rotation_matrix_valid(self) -> None:
        # Test valid rotation matrix
        rotation_matrix = (
            (0.7071067811865476, -0.7071067811865475, 0.0),
            (0.7071067811865475, 0.7071067811865476, 0.0),
            (0.0, 0.0, 1.0),
        )
        q = Quaternion.from_rotation_matrix(rotation_matrix)
        assert MathUtils.is_close(q.a, 0.9238795325112867)
        assert MathUtils.is_close(q.b, 0.0)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.3826834323650898)

    def test_from_rotation_matrix_invalid_non_orthogonal(self) -> None:
        # Test invalid non-orthogonal matrix
        # fmt: off
        rotation_matrix = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 2),  # Not orthogonal
        )
        # fmt: on
        with pytest.raises(ValueError, match="The rotation matrix must be orthogonal."):
            Quaternion.from_rotation_matrix(rotation_matrix)

    def test_from_rotation_matrix_invalid_size(self) -> None:
        # Test invalid matrix size
        # fmt: off
        rotation_matrix = (
            (1, 0),
            (0, 1),
        )
        # fmt: on
        with pytest.raises(
            ValueError, match="rotation_matrix must be a 3x3 matrix defined as a list of lists or a tuple of tuples."
        ):
            Quaternion.from_rotation_matrix(rotation_matrix)

    def test_from_rotation_matrix_identity(self) -> None:
        # Test identity matrix
        # fmt: off
        rotation_matrix = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
        )
        # fmt: on
        q = Quaternion.from_rotation_matrix(rotation_matrix)
        assert MathUtils.is_close(q.a, 1.0)
        assert MathUtils.is_close(q.b, 0.0)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 0.0)

    def test_from_rotation_matrix_180_degree_rotation(self) -> None:
        # Test 180-degree rotation about the Z-axis
        # fmt: off
        rotation_matrix = (
            (-1, 0, 0),
            (0, -1, 0),
            (0, 0, 1),
        )
        # fmt: on
        q = Quaternion.from_rotation_matrix(rotation_matrix)
        assert MathUtils.is_close(q.a, 0.0)
        assert MathUtils.is_close(q.b, 0.0)
        assert MathUtils.is_close(q.c, 0.0)
        assert MathUtils.is_close(q.d, 1.0)

    def test_to_rotation_matrix_valid(self) -> None:
        # Test valid quaternion to rotation matrix
        q = Quaternion(0.9238795325112867, 0.0, 0.0, 0.3826834323650898)
        rotation_matrix = q.to_rotation_matrix()
        expected_matrix = (
            (0.7071067811865476, -0.7071067811865475, 0.0),
            (0.7071067811865475, 0.7071067811865476, 0.0),
            (0.0, 0.0, 1.0),
        )
        for i in range(3):
            for j in range(3):
                assert MathUtils.is_close(rotation_matrix[i][j], expected_matrix[i][j])

    def test_to_rotation_matrix_zero_norm(self) -> None:
        # Test quaternion with zero norm
        q = Quaternion(0, 0, 0, 0)
        with pytest.raises(ValueError, match="A quaternion with norm 0 cannot be converted."):
            q.to_rotation_matrix()

    def test_to_rotation_matrix_normalized(self) -> None:
        # Test quaternion normalization before conversion
        q = Quaternion(2, 0, 0, 2)
        rotation_matrix = q.to_rotation_matrix()
        # fmt: off
        expected_matrix = (
            (0.0, -1.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        # fmt: on
        for i in range(3):
            GeometryOperators.is_vector_equal(rotation_matrix[i], expected_matrix[i])

    def test_to_rotation_matrix_identity(self) -> None:
        # Test identity quaternion
        q = Quaternion(1, 0, 0, 0)
        rotation_matrix = q.to_rotation_matrix()
        # fmt: off
        expected_matrix = (
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        # fmt: on
        for i in range(3):
            GeometryOperators.is_vector_equal(rotation_matrix[i], expected_matrix[i])

    def test_to_rotation_matrix_negative_w(self) -> None:
        # Test quaternion with negative scalar part
        q = Quaternion(-0.9238795325112867, 0.0, 0.0, -0.3826834323650898)
        rotation_matrix = q.to_rotation_matrix()
        expected_matrix = (
            (0.7071067811865476, 0.7071067811865475, 0.0),
            (-0.7071067811865475, 0.7071067811865476, 0.0),
            (0.0, 0.0, 1.0),
        )
        for i in range(3):
            GeometryOperators.is_vector_equal(rotation_matrix[i], expected_matrix[i])

    def test_rotation_matrix_to_axis_valid(self) -> None:
        # Test valid rotation matrix to axes
        rotation_matrix = (
            (0.7071067811865476, 0.0, 0.7071067811865476),
            (0.0, 1.0, 0.0),
            (-0.7071067811865476, 0.0, 0.7071067811865476),
        )
        x, y, z = Quaternion.rotation_matrix_to_axis(rotation_matrix)
        assert MathUtils.is_close(x[0], 0.7071067811865476)
        assert MathUtils.is_close(x[1], 0.0)
        assert MathUtils.is_close(x[2], -0.7071067811865476)
        assert MathUtils.is_close(y[0], 0.0)
        assert MathUtils.is_close(y[1], 1.0)
        assert MathUtils.is_close(y[2], 0.0)
        assert MathUtils.is_close(z[0], 0.7071067811865476)
        assert MathUtils.is_close(z[1], 0.0)
        assert MathUtils.is_close(z[2], 0.7071067811865476)

    def test_rotation_matrix_to_axis_invalid(self) -> None:
        # Test invalid non-orthogonal matrix
        # fmt: off
        rotation_matrix = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 2),  # Not orthogonal
        )
        # fmt: on
        with pytest.raises(ValueError, match="The rotation matrix must be orthogonal."):
            Quaternion.rotation_matrix_to_axis(rotation_matrix)

    def test_axis_to_rotation_matrix_valid(self) -> None:
        # Test valid axes to rotation matrix
        x_axis = (1, 0, 0)
        y_axis = (0, 1, 0)
        z_axis = (0, 0, 1)
        rotation_matrix = Quaternion.axis_to_rotation_matrix(x_axis, y_axis, z_axis)
        # fmt: off
        expected_matrix = (
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        # fmt: on
        for i in range(3):
            for j in range(3):
                assert MathUtils.is_close(rotation_matrix[i][j], expected_matrix[i][j])

    def test_axis_to_rotation_matrix_invalid(self) -> None:
        # Test invalid axes (not orthonormal)
        x_axis = (1, 0, 0)
        y_axis = (1, 1, 0)  # Not orthogonal to x_axis
        z_axis = (0, 0, 1)
        with pytest.raises(ValueError, match="The provided axes must form an orthonormal basis."):
            Quaternion.axis_to_rotation_matrix(x_axis, y_axis, z_axis)

    def test_rotate_vector_valid(self) -> None:
        # Test rotating a vector using a valid quaternion
        q = Quaternion(0.9238795325112867, 0.0, -0.3826834323650898, 0.0)  # 45-degree rotation about Y-axis
        v = (1, 0, 0)  # Vector along X-axis
        rotated_v = q.rotate_vector(v)
        assert MathUtils.is_close(rotated_v[0], 0.7071067811865475)
        assert MathUtils.is_close(rotated_v[1], 0.0)
        assert MathUtils.is_close(rotated_v[2], 0.7071067811865476)

    def test_rotate_vector_zero_quaternion(self) -> None:
        # Test rotating a vector with a zero quaternion
        q = Quaternion(0, 0, 0, 0)
        v = (1, 0, 0)
        with pytest.raises(ValueError, match="Cannot normalize a quaternion with zero norm."):
            q.rotate_vector(v)

    def test_rotate_vector_identity_quaternion(self) -> None:
        # Test rotating a vector with the identity quaternion
        q = Quaternion(1, 0, 0, 0)  # Identity quaternion
        v = (1, 2, 3)  # Arbitrary vector
        rotated_v = q.rotate_vector(v)
        assert MathUtils.is_close(rotated_v[0], 1.0)
        assert MathUtils.is_close(rotated_v[1], 2.0)
        assert MathUtils.is_close(rotated_v[2], 3.0)

    def test_rotate_vector_180_degree_rotation(self) -> None:
        # Test 180-degree rotation about Z-axis
        q = Quaternion(0, 0, 0, 1)  # 180-degree rotation about Z-axis
        v = (1, 0, 0)  # Vector along X-axis
        rotated_v = q.rotate_vector(v)
        assert MathUtils.is_close(rotated_v[0], -1.0)
        assert MathUtils.is_close(rotated_v[1], 0.0)
        assert MathUtils.is_close(rotated_v[2], 0.0)

    def test_rotate_vector_normalized_quaternion(self) -> None:
        # Test rotating a vector with a non-normalized quaternion
        q = Quaternion(2, 0, 0, 2)  # Non-normalized quaternion
        v = (0, 1, 0)  # Vector along Y-axis
        rotated_v = q.rotate_vector(v)
        assert MathUtils.is_close(rotated_v[0], -1.0)
        assert MathUtils.is_close(rotated_v[1], 0.0)
        assert MathUtils.is_close(rotated_v[2], 0.0)

    def test_inverse_rotate_vector_valid(self) -> None:
        # Test inverse rotation of a vector using a valid quaternion
        q = Quaternion(0.9238795325112867, 0.0, -0.3826834323650898, 0.0)  # 45-degree rotation about Y-axis
        v = (0.7071067811865475, 0.0, 0.7071067811865476)  # Rotated vector
        original_v = q.inverse_rotate_vector(v)
        assert MathUtils.is_close(original_v[0], 1.0)
        assert MathUtils.is_close(original_v[1], 0.0)
        assert MathUtils.is_close(original_v[2], 0.0)

    def test_inverse_rotate_vector_zero_quaternion(self) -> None:
        # Test inverse rotation with a zero quaternion
        q = Quaternion(0, 0, 0, 0)
        v = (1, 0, 0)
        with pytest.raises(ValueError, match="Cannot normalize a quaternion with zero norm."):
            q.inverse_rotate_vector(v)

    def test_inverse_rotate_vector_identity_quaternion(self) -> None:
        # Test inverse rotation with the identity quaternion
        q = Quaternion(1, 0, 0, 0)  # Identity quaternion
        v = (1, 2, 3)  # Arbitrary vector
        original_v = q.inverse_rotate_vector(v)
        assert MathUtils.is_close(original_v[0], 1.0)
        assert MathUtils.is_close(original_v[1], 2.0)
        assert MathUtils.is_close(original_v[2], 3.0)

    def test_inverse_rotate_vector_180_degree_rotation(self) -> None:
        # Test 180-degree inverse rotation about Z-axis
        q = Quaternion(0, 0, 0, 1)  # 180-degree rotation about Z-axis
        v = (-1.0, 0.0, 0.0)  # Rotated vector
        original_v = q.inverse_rotate_vector(v)
        assert MathUtils.is_close(original_v[0], 1.0)
        assert MathUtils.is_close(original_v[1], 0.0)
        assert MathUtils.is_close(original_v[2], 0.0)

    def test_inverse_rotate_vector_normalized_quaternion(self) -> None:
        # Test inverse rotation with a non-normalized quaternion
        q = Quaternion(2, 0, 0, 2)  # Non-normalized quaternion
        v = (-1, 0, 0)  # Vector along Y-axis
        original_v = q.inverse_rotate_vector(v)
        assert MathUtils.is_close(original_v[0], 0.0)
        assert MathUtils.is_close(original_v[1], 1.0)
        assert MathUtils.is_close(original_v[2], 0.0)

    # Here we have the old tests from GeometryOperator

    def test_axis_to_euler_zxz(self) -> None:
        x, y, z = cs.pointing_to_axis([1, 0.1, 1], [0.5, 1, 0])
        m = Quaternion.axis_to_rotation_matrix(x, y, z)
        q = Quaternion.from_rotation_matrix(m)
        phi, theta, psi = q.to_euler("zxz")
        assert abs(phi - (-2.0344439357957027)) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - 1.9590019609437583) < tol
        x, y, z = cs.pointing_to_axis([-0.2, -0.3, 0], [-0.2, 0.3, 0])
        m = Quaternion.axis_to_rotation_matrix(x, y, z)
        q = Quaternion.from_rotation_matrix(m)
        phi, theta, psi = q.to_euler("zxz")
        assert abs(phi - (4.124386376837122)) < tol
        assert abs(theta - 3.141592653589793) < tol
        assert abs(psi - 0) < tol
        x, y, z = cs.pointing_to_axis([-0.2, -0.5, 0], [-0.1, -0.4, 0])
        m = Quaternion.axis_to_rotation_matrix(x, y, z)
        q = Quaternion.from_rotation_matrix(m)
        phi, theta, psi = q.to_euler("zxz")
        assert abs(phi - (-1.9513027039072615)) < tol
        assert abs(theta - 0) < tol
        assert abs(psi - 0) < tol

    def test_axis_to_euler_zyz(self) -> None:
        x, y, z = cs.pointing_to_axis([1, 0.1, 1], [0.5, 1, 0])
        m = Quaternion.axis_to_rotation_matrix(x, y, z)
        q = Quaternion.from_rotation_matrix(m)
        phi, theta, psi = q.to_euler("zyz")
        assert abs(phi - 2.677945044588987) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - (-2.7533870194409316)) < tol
        x, y, z = cs.pointing_to_axis([-0.2, -0.3, 0], [-0.2, 0.3, 0])
        m = Quaternion.axis_to_rotation_matrix(x, y, z)
        q = Quaternion.from_rotation_matrix(m)
        phi, theta, psi = q.to_euler("zyz")
        assert abs(phi - 0.982793723247329) < tol
        assert abs(theta - 3.141592653589793) < tol
        assert abs(psi - 0) < tol
        x, y, z = cs.pointing_to_axis([-0.2, -0.5, 0], [-0.1, -0.4, 0])
        m = Quaternion.axis_to_rotation_matrix(x, y, z)
        q = Quaternion.from_rotation_matrix(m)
        phi, theta, psi = q.to_euler("zyz")
        assert abs(phi - (-1.9513027039072615)) < tol
        assert abs(theta - 0) < tol
        assert abs(psi - 0) < tol

    def test_quaternion_to_axis(self) -> None:
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        m = Quaternion(*q).to_rotation_matrix()
        x, y, z = Quaternion.rotation_matrix_to_axis(m)
        assert is_vector_equal(x, [0.7053456158585982, 0.07053456158585963, 0.7053456158585982])
        assert is_vector_equal(y, [0.19470872568244832, 0.937486456989565, -0.2884573713814046])
        assert is_vector_equal(z, [-0.681598176590997, 0.34079908829549865, 0.6475182677614472])

    def test_to_axis_normalized(self) -> None:
        # Test quaternion normalization before conversion
        q = Quaternion(2, 2, 2, 2)
        m = q.to_rotation_matrix()
        x, y, z = Quaternion.rotation_matrix_to_axis(m)
        assert MathUtils.is_close(x[0], 0.0)
        assert MathUtils.is_close(x[1], 1.0)
        assert MathUtils.is_close(x[2], 0.0)
        assert MathUtils.is_close(y[0], 0.0)
        assert MathUtils.is_close(y[1], 0.0)
        assert MathUtils.is_close(y[2], 1.0)
        assert MathUtils.is_close(z[0], 1.0)
        assert MathUtils.is_close(z[1], 0.0)
        assert MathUtils.is_close(z[2], 0.0)

    def test_quaternion_to_axis_angle(self) -> None:
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        u, th = Quaternion(*q).to_axis_angle()
        assert is_vector_equal(u, [-0.41179835953227295, -0.9076445218972716, -0.0812621249808417])
        assert abs(th - 0.8695437956599169) < tol

    def test_axis_angle_to_quaternion(self) -> None:
        u = [-0.41179835953227295, -0.9076445218972716, -0.0812621249808417]
        th = 0.8695437956599169
        q = Quaternion.from_axis_angle(u, th)
        assert is_vector_equal(
            q.coefficients(), [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        )
        assert abs(q.a**2 + q.b**2 + q.c**2 + q.d**2 - 1.0) < tol

    def test_quaternion_to_euler_zxz(self) -> None:
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        phi, theta, psi = Quaternion(*q).to_euler("zxz")
        assert abs(phi - (-2.0344439357957027)) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - 1.9590019609437583) < tol

    def test_euler_zxz_to_quaternion(self) -> None:
        phi = -2.0344439357957027
        theta = 0.8664730673456006
        psi = 1.9590019609437583
        q = Quaternion.from_euler((phi, theta, psi), "zxz")
        assert is_vector_equal(
            q.coefficients(), [0.9069661433330367, -0.17345092325178468, -0.38230307786150497, -0.03422789400943264]
        )
        assert abs(q.a**2 + q.b**2 + q.c**2 + q.d**2 - 1.0) < tol

    def test_quaternion_to_euler_zyz(self) -> None:
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        phi, theta, psi = Quaternion(*q).to_euler("zyz")
        assert abs(phi - 2.677945044588987) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - (-2.7533870194409316)) < tol

    def test_euler_zyz_to_quaternion(self) -> None:
        phi = 2.677945044588987
        theta = 0.8664730673456006
        psi = -2.7533870194409316
        q = Quaternion.from_euler((phi, theta, psi), "zyz")
        assert is_vector_equal(
            q.coefficients(), [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        )
        assert abs(q.a**2 + q.b**2 + q.c**2 + q.d**2 - 1.0) < tol

    def test_bug_6037(self) -> None:
        # Test for bug #6037
        q = Quaternion(0.9801685681070907, 0.0, 0.0, 0.19816553205564127)
        angles = q.to_euler("zxz")
        assert MathUtils.is_close(angles[0], 0.3989719626660737)
        assert MathUtils.is_close(angles[1], 0)
        assert MathUtils.is_close(angles[2], 0)
