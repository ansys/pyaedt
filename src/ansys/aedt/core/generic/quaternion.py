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

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.math_utils import MathUtils
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators


class Quaternion(PyAedtBase):
    """
    Implements fundamental quaternion operations.

    Quaternions are created using ``Quaternion(a, b, c, d)``.

    Quaternions are only used to represent rotations in 3D space.
    They are not used to represent translations or other transformations.
    Only methods related to rotations are implemented.

    The quaternion is defined as:
    .. math::
        q = a + bi + cj + dk
    where ``a`` is the scalar part and ``b``, ``c``, and ``d`` are the vector parts.

    This updated class offers enhanced functionality compared to the previous implementation,
    supporting both intrinsic and extrinsic rotations. Note that AEDT coordinate systems use intrinsic rotation.


    References
    ----------
    [1] https://en.wikipedia.org/wiki/Quaternion
    [2] https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    [3] https://www.euclideanspace.com/maths/geometry/rotations/conversions/

    """

    def __init__(self, a=0, b=0, c=0, d=0):
        """Initialize the quaternion.
        Quaternions are created using ``Quaternion(a, b, c, d)``, representing the form q = a + bi + cj + dk.

        Parameters
        ----------
        a, b, c, d : float
            The quaternion coefficients.
        """
        try:
            a, b, c, d = float(a), float(b), float(c), float(d)
        except ValueError:
            raise TypeError("Quaternion coefficients must be convertible to float.")
        self._args = (a, b, c, d)
        # normalize each element in self._args so that if it's "close enough to zero", it's set explicitly to 0.0.
        self._args = tuple(0.0 if MathUtils.is_zero(x) else x for x in self._args)

    @property
    def a(self):
        return self._args[0]

    @property
    def b(self):
        return self._args[1]

    @property
    def c(self):
        return self._args[2]

    @property
    def d(self):
        return self._args[3]

    @classmethod
    @pyaedt_function_handler()
    def _to_quaternion(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (tuple, list)) and len(obj) == 4:
            return cls(*obj)
        else:
            raise TypeError(f"Cannot convert {obj} to {cls.__name__}.")

    @staticmethod
    @pyaedt_function_handler()
    def _is_valid_rotation_sequence(sequence):
        """
        Validates that the input string is a valid 3-character rotation sequence
        using only the axes 'x', 'y', or 'z', case-insensitively.

        Parameters
        ----------
        sequence : str
            The rotation sequence string to validate.

        Returns
        -------
        bool
            ``True`` if valid, ``False`` otherwise.
        """
        if not isinstance(sequence, str):
            return False
        if len(sequence) != 3:
            return False
        return all(char.lower() in {"x", "y", "z"} for char in sequence)

    @classmethod
    @pyaedt_function_handler()
    def from_euler(cls, angles, sequence, extrinsic=False):
        """Creates a normalized rotation quaternion from the Euler angles using the specified rotation sequence.

        Parameters
        ----------
        angles : list, tuple of 3 floats
            The Euler angles in radians.

        sequence : str
            A three-character string indicating the rotation axis sequence (e.g., "xyz" or "ZYX").
            It is case-insensitive and must contain only the characters 'x', 'y', or 'z'.

        extrinsic : bool, optional
            If ``True``, the rotation is treated as extrinsic.
            If ``False`` (default), it is treated as intrinsic.

        Returns
        -------
        Quaternion
            A unit quaternion representing the rotation defined by the Euler angles in the given sequence.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> from math import pi
        >>> q = Quaternion.from_euler([pi / 2, 0, 0], "xyz")
        >>> q
        Quaternion(0.7071067811865476, 0.7071067811865476, 0, 0)

        >>> q = Quaternion.from_euler([0, pi / 2, pi], "zyz", extrinsic=True)
        >>> q
        Quaternion(0, -0.7071067811865476, 0, 0.7071067811865476)

        >>> q = Quaternion.from_euler([0, pi / 2, pi], "zyz")
        >>> q
        Quaternion(0, 0.7071067811865476, 0, 0.7071067811865476)
        """
        if len(angles) != 3:
            raise ValueError("Three rotation angles are required.")

        if not Quaternion._is_valid_rotation_sequence(sequence):
            raise ValueError("sequence must be a 3-character string, using only the axes 'x', 'y', or 'z'.")

        i, j, k = sequence.lower()

        # converting the sequence into indexes
        ei = [1 if n == i else 0 for n in "xyz"]
        ej = [1 if n == j else 0 for n in "xyz"]
        ek = [1 if n == k else 0 for n in "xyz"]

        # evaluate the quaternions
        qi = cls.from_axis_angle(ei, angles[0])
        qj = cls.from_axis_angle(ej, angles[1])
        qk = cls.from_axis_angle(ek, angles[2])

        if extrinsic:
            return qk * qj * qi
        else:
            return qi * qj * qk

    @pyaedt_function_handler()
    def to_euler(self, sequence, extrinsic=False):
        """
        Converts the quaternion to Euler angles using the specified rotation sequence.

        The conversion follows the method described in [1]. In degenerate (gimbal lock) cases,
        the third angle is set to zero for stability.

        Parameters
        ----------
        sequence : str
            A three-character string indicating the rotation axis sequence (e.g., "xyz" or "ZYX").
            It is case-insensitive and must contain only the characters 'x', 'y', or 'z'.

        extrinsic : bool, optional
            If ``True``, the rotation is treated as extrinsic.
            If ``False`` (default), it is treated as intrinsic.

        Note
        ----
        Tait–Bryan angles (Heading, Pitch, Bank) correspond to an intrinsic "ZYX" sequence.

        Returns
        -------
        tuple of float
            A tuple of three Euler angles representing the same rotation as the quaternion.
            Angle in radians.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q = Quaternion(0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274)
        >>> q.to_euler("zxz")
        (-2.0344439357957027, 0.8664730673456006, 1.9590019609437583)
        >>> q.to_euler("zyz")
        (2.677945044588987, 0.8664730673456006, -2.7533870194409316)

        References
        ----------
        [1] https://doi.org/10.1371/journal.pone.0276302
        [2] https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        """
        # fmt: off
        if not Quaternion._is_valid_rotation_sequence(sequence):
            raise ValueError("sequence must be a 3-character string, using only the axes 'x', 'y', or 'z'.")

        if MathUtils.is_zero(self.norm()):
            raise ValueError('A quaternion with norm 0 cannot be converted.')

        angles = [0, 0, 0]

        i, j, k = sequence.lower()

        # converting the sequence into indexes
        i = 'xyz'.index(i) + 1
        j = 'xyz'.index(j) + 1
        k = 'xyz'.index(k) + 1

        if not extrinsic:
            i, k = k, i

        # check if the rotation sequence is symmetric
        symmetric = i == k
        if symmetric:
            k = 6 - i - j

        # determine the parity of the permutation
        sign = (i - j) * (j - k) * (k - i) // 2

        # permutate elements
        elements = [self.a, self.b, self.c, self.d]
        a = elements[0]
        b = elements[i]
        c = elements[j]
        d = elements[k] * sign

        if not symmetric:
            a, b, c, d = a-c, b+d, c+a, d-b

        angles[1] = 2 * MathUtils.atan2(math.sqrt(c*c + d*d), math.sqrt(a*a + b*b))
        if not symmetric:
            angles[1] -= math.pi / 2

        # Check for singularities in some numerical cases
        case = 0
        if MathUtils.is_zero(c) and MathUtils.is_zero(d):
            case = 1
        if MathUtils.is_zero(a) and MathUtils.is_zero(b):
            case = 2

        if case == 0:
            angles[0] = MathUtils.atan2(b, a) + MathUtils.atan2(d, c)
            angles[2] = MathUtils.atan2(b, a) - MathUtils.atan2(d, c)
        else:
            # here we consider any degenerate case
            if extrinsic:
                angles[0] = 0.0
            else:
                angles[2] = 0.0

            if case == 1:
                if extrinsic:
                    angles[2] = 2 * MathUtils.atan2(b, a)
                else:
                    angles[0] = 2 * MathUtils.atan2(b, a)
            else:
                if extrinsic:
                    angles[2] = -2 * MathUtils.atan2(d, c)
                else:
                    angles[0] = 2 * MathUtils.atan2(d, c)

        # for Tait-Bryan angles
        if not symmetric:
            angles[0] *= sign

        if extrinsic:
            return tuple(angles[::-1])
        else:
            return tuple(angles)
        # fmt: on

    @classmethod
    @pyaedt_function_handler()
    def from_axis_angle(cls, axis, angle):
        """Creates a normalized rotation quaternion from a given axis and rotation angle.


        Parameters
        ----------
        axis : List or tuple of float
            A 3D vector representing the axis of rotation.
        angle : float
            The rotation angle in radians.

        Returns
        -------
        Quaternion
            A unit quaternion representing the rotation around the specified axis by the given angle.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> from math import pi, sqrt
        >>> Quaternion.from_axis_angle((sqrt(3) / 3, sqrt(3) / 3, sqrt(3) / 3), 2 * pi / 3)
        Quaternion(0.5, 0.5, 0.5, 0.5)
        """
        if len(axis) != 3:
            raise ValueError("axis must be a list or tuple containing 3 floats.")
        if MathUtils.is_zero(GeometryOperators.v_norm(axis)):
            raise ValueError("axis must be a non-zero vector.")

        (x, y, z) = GeometryOperators.normalize_vector(axis)
        s = math.sin(angle * 0.5)
        a = math.cos(angle * 0.5)
        b = x * s
        c = y * s
        d = z * s
        return cls(a, b, c, d)

    @pyaedt_function_handler()
    def to_axis_angle(self):
        """Convert a quaternion to the axis angle rotation formulation.

        Returns
        -------
        tuple
            ((ux, uy, uz), theta) containing the rotation axes expressed as X, Y, Z components of
            the unit vector ``u`` and the rotation angle theta expressed in radians.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q = Quaternion(1, 1, 1, 1)
        >>> (axis, angle) = q.to_axis_angle()
        >>> axis
        (0.5773502691896257, 0.5773502691896257, 0.5773502691896257)
        >>> angle
        2.0943951023931953

        """
        # fmt: off
        q = self
        if MathUtils.is_zero(q.norm()):
            raise ValueError('A quaternion with norm 0 cannot be converted.')

        if q.a < 0:
            q = q * -1

        q = q.normalize()
        theta = 2 * math.acos(q.a)
        n = math.sqrt(1 - q.a*q.a)  # q.a < 1 in a normalized quaternion
        if MathUtils.is_zero(n):
            # Handle the case where the quaternion is a multiple of (1, 0, 0, 0)
            # which corresponds to no rotation
            return (1.0, 0.0, 0.0), 0.0
        x = q.b / n
        y = q.c / n
        z = q.d / n
        u = (x, y, z)
        return u, theta
        # fmt: on

    @classmethod
    @pyaedt_function_handler()
    def from_rotation_matrix(cls, rotation_matrix):
        """Converts a 3x3 rotation matrix to a quaternion.
        It uses the method described in [1].

        Parameters
        ----------
        rotation_matrix: List or tuple
            Rotation matrix defined as a list of lists or a tuple of tuples.
            The matrix should be 3x3 and orthogonal.
            The matrix is assumed to be in the form:
            ((m00, m01, m02), (m10, m11, m12), (m20, m21, m22))

        Returns
        -------
        Quaternion
            The quaternion defined by the rotation matrix.

        References
        ----------
        [1] https://doi.org/10.1145/325334.325242 (pp. 245-254)

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> x = (0.7053456158585982, 0.07053456158585963, 0.7053456158585982)
        >>> y = (0.19470872568244832, 0.937486456989565, -0.2884573713814046)
        >>> z = (-0.681598176590997, 0.34079908829549865, 0.6475182677614472)
        >>> rotation_matrix = Quaternion.axis_to_rotation_matrix(x, y, z)
        >>> q = Quaternion.from_rotation_matrix(rotation_matrix)
        >>> q
        Quaternion(0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274)

        """
        # fmt: off
        wrong_type = False
        if not isinstance(rotation_matrix, (list, tuple)) or len(rotation_matrix) != 3:
            wrong_type = True
        for row in rotation_matrix:
            if not isinstance(row, (list, tuple)) or len(row) != 3:
                wrong_type = True
        if wrong_type:
            raise ValueError("rotation_matrix must be a 3x3 matrix defined as a list of lists or a tuple of tuples.")

        if not GeometryOperators.is_orthogonal_matrix(rotation_matrix):
            raise ValueError("The rotation matrix must be orthogonal.")

        m00, m01, m02 = rotation_matrix[0]
        m10, m11, m12 = rotation_matrix[1]
        m20, m21, m22 = rotation_matrix[2]

        trace = m00 + m11 + m22

        if trace > 0:
            S = math.sqrt(trace + 1.0) * 2  # S=4*w
            w = 0.25 * S
            x = (m21 - m12) / S
            y = (m02 - m20) / S
            z = (m10 - m01) / S
        elif (m00 > m11) and (m00 > m22):
            S = math.sqrt(1.0 + m00 - m11 - m22) * 2  # S=4*x
            w = (m21 - m12) / S
            x = 0.25 * S
            y = (m01 + m10) / S
            z = (m02 + m20) / S
        elif m11 > m22:
            S = math.sqrt(1.0 + m11 - m00 - m22) * 2  # S=4*y
            w = (m02 - m20) / S
            x = (m01 + m10) / S
            y = 0.25 * S
            z = (m12 + m21) / S
        else:
            S = math.sqrt(1.0 + m22 - m00 - m11) * 2  # S=4*z
            w = (m10 - m01) / S
            x = (m02 + m20) / S
            y = (m12 + m21) / S
            z = 0.25 * S

        return cls(w, x, y, z)
        # fmt: on

    @pyaedt_function_handler()
    def to_rotation_matrix(self):
        """Returns the rotation matrix corresponding to the quaternion.


        Returns
        -------
        tuple
            A 3×3 rotation matrix equivalent to the quaternion's rotation.
            The matrix is provided in the form:
            ((m00, m01, m02), (m10, m11, m12), (m20, m21, m22))

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q = Quaternion(0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274)
        >>> rotation_matrix = q.to_rotation_matrix()
        >>> rotation_matrix
        ((0.7053456158585982, 0.07053456158585963, 0.7053456158585982),
         (0.19470872568244832, 0.937486456989565, -0.2884573713814046),
         (-0.681598176590997, 0.34079908829549865, 0.6475182677614472))

        """
        # fmt: off
        q = self
        if MathUtils.is_zero(q.norm()):
            raise ValueError('A quaternion with norm 0 cannot be converted.')

        s = q.norm() ** -2

        m00 = 1 - 2*s*(q.c**2 + q.d**2)
        m01 = 2*s*(q.b*q.c - q.d*q.a)
        m02 = 2*s*(q.b*q.d + q.c*q.a)

        m10 = 2*s*(q.b*q.c + q.d*q.a)
        m11 = 1 - 2*s*(q.b**2 + q.d**2)
        m12 = 2*s*(q.c*q.d - q.b*q.a)

        m20 = 2*s*(q.b*q.d - q.c*q.a)
        m21 = 2*s*(q.c*q.d + q.b*q.a)
        m22 = 1 - 2*s*(q.b**2 + q.c**2)

        return (m00, m01, m02), (m10, m11, m12), (m20, m21, m22)
        # fmt: on

    @staticmethod
    @pyaedt_function_handler()
    def rotation_matrix_to_axis(rotation_matrix):
        """Convert a rotation matrix to the corresponding axis of rotation.

        Parameters
        ----------
        rotation_matrix : tuple of tuples or list of lists
            A 3x3 rotation matrix defined as a tuple of tuples or a list of lists.
            The matrix should be orthogonal.

        Returns
        -------
        tuple
            The X, Y, and Z axes of the rotated frame.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> rotation_matrix = (
        ...     (0.7071067811865476, 0.0, 0.7071067811865476),
        ...     (0.0, 1.0, 0.0),
        ...     (-0.7071067811865476, 0.0, 0.7071067811865476),
        ... )
        >>> x, y, z = Quaternion.rotation_matrix_to_axis(rotation_matrix)
        >>> x
        (0.7071067811865476, 0.0, -0.7071067811865476)
        >>> y
        (0.0, 1.0, 0.0)
        >>> z
        (-0.7071067811865476, 0.0, 0.7071067811865476)
        """
        if not GeometryOperators.is_orthogonal_matrix(rotation_matrix):
            raise ValueError("The rotation matrix must be orthogonal.")

        m00, m01, m02 = rotation_matrix[0]
        m10, m11, m12 = rotation_matrix[1]
        m20, m21, m22 = rotation_matrix[2]

        x = tuple(GeometryOperators.normalize_vector((m00, m10, m20)))
        y = tuple(GeometryOperators.normalize_vector((m01, m11, m21)))
        z = tuple(GeometryOperators.normalize_vector((m02, m12, m22)))

        return x, y, z

    @staticmethod
    @pyaedt_function_handler()
    def axis_to_rotation_matrix(x_axis, y_axis, z_axis):
        """Construct a rotation matrix from three orthonormal axes.

        Parameters
        ----------
        x_axis : tuple of float
            The X axis of the rotated frame.
        y_axis : tuple of float
            The Y axis of the rotated frame.
        z_axis : tuple of float
            The Z axis of the rotated frame.

        Returns
        -------
        tuple of tuples
            A 3x3 rotation matrix where each column is one of the given axes.

        Raises
        ------
        ValueError
            If the axes do not form an orthonormal basis.
        """
        if not GeometryOperators.is_orthonormal_triplet(x_axis, y_axis, z_axis):
            raise ValueError("The provided axes must form an orthonormal basis.")

        return (
            (x_axis[0], y_axis[0], z_axis[0]),
            (x_axis[1], y_axis[1], z_axis[1]),
            (x_axis[2], y_axis[2], z_axis[2]),
        )

    @pyaedt_function_handler()
    def rotate_vector(self, v):
        """Evaluate the rotation of a vector, defined by a quaternion.

        Evaluated as:
        ``"q = q0 + q' = q0 + q1i + q2j + q3k"``,
        ``"w = qvq* = (q0^2 - |q'|^2)v + 2(q' • v)q' + 2q0(q' x v)"``.

        Parameters
        ----------
        v : tuple or List
            ``(x, y, z)`` coordinates for the vector to be rotated.

        Returns
        -------
        tuple
            ``(w1, w2, w3)`` coordinates for the rotated vector ``w``.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q = Quaternion(0.9238795325112867, 0.0, -0.3826834323650898, 0.0)
        >>> v = (1, 0, 0)
        >>> q.rotate_vector(v)
        (0.7071067811865475, 0.0, 0.7071067811865476)

        """
        q = self
        q = q.normalize()
        q2 = q * Quaternion(0, v[0], v[1], v[2]) * q.conjugate()
        return q2.b, q2.c, q2.d

    @pyaedt_function_handler()
    def inverse_rotate_vector(self, v):
        """Evaluate the inverse rotation of a vector that is defined by a quaternion.
        It can also be the rotation of the coordinate frame with respect to the vector.

            q = q0 + q' = q0 + iq1 + jq2 + kq3
            q* = q0 - q' = q0 - iq1 - jq2 - kq3
            w = q*vq

        Parameters
        ----------
        v : tuple or List
            ``(x, y, z)`` coordinates for the vector to be rotated.

        Returns
        -------
        tuple
            ``(w1, w2, w3)`` coordinates for the rotated vector ``w``.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q = Quaternion(0.9238795325112867, 0.0, -0.3826834323650898, 0.0)
        >>> v = (1, 0, 0)
        >>> q.rotate_vector(v)
        (0.7071067811865475, 0.0, 0.7071067811865476)

        """
        q = self
        q = q.normalize()
        q2 = q.conjugate() * Quaternion(0, v[0], v[1], v[2]) * q
        return q2.b, q2.c, q2.d

    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return self._q_prod(self, other)

    def __rmul__(self, other):
        return self._q_prod(other, self)

    def __neg__(self):
        return Quaternion(-self.a, -self.b, -self.c, -self.d)

    def __truediv__(self, other):
        return self._q_div(self, other)

    def __rtruediv__(self, other):
        return self._q_div(other, self)

    def __eq__(self, other):
        # fmt: off
        if not isinstance(other, Quaternion):
            return False
        return (
            MathUtils.is_equal(self.a, other.a) and
            MathUtils.is_equal(self.b, other.b) and
            MathUtils.is_equal(self.c, other.c) and
            MathUtils.is_equal(self.d, other.d)
        )
        # fmt: on

    def __repr__(self):
        return f"{type(self).__name__}({self.a}, {self.b}, {self.c}, {self.d})"

    @pyaedt_function_handler()
    def add(self, other):
        """Adds another quaternion or compatible value to this quaternion.

        Parameters
        ----------
        other : Quaternion, List, tuple, float, or int
            The value to be added.
            It can be another Quaternion or a sequence that can be interpreted as one.
            It can also be a scalar value (float or int).

        Returns
        -------
        Quaternion
            A new quaternion representing the sum of this quaternion and the provided value.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q1 = Quaternion(1, 2, 3, 4)
        >>> q2 = Quaternion(5, 6, 7, 8)
        >>> q1.add(q2)
        Quaternion(6, 8, 10, 12)
        >>> q1 + 7
        Quaternion(8, 2, 3, 4)

        """
        q1 = self

        # Check what to do with other
        if MathUtils.is_scalar_number(other):
            return Quaternion(q1.a + other, q1.b, q1.c, q1.d)

        q2 = self._to_quaternion(other)
        return Quaternion(q1.a + q2.a, q1.b + q2.b, q1.c + q2.c, q1.d + q2.d)

    @pyaedt_function_handler()
    def mul(self, other):
        """Performs quaternion multiplication with another quaternion or compatible value.

        Parameters
        ----------
        other : Quaternion, List, tuple, float, or int
            The value to multiply with this quaternion.
            It can be another Quaternion or a sequence that can be interpreted as one.
            It can also be a scalar value (float or int).

        Returns
        -------
        Quaternion
            A new quaternion representing the product of this quaternion and the given value.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q1 = Quaternion(1, 2, 3, 4)
        >>> q2 = Quaternion(5, 6, 7, 8)
        >>> q1.mul(q2)
        Quaternion(-60, 12, 30, 24)
        >>> q1.mul(2)
        Quaternion(2, 4, 6, 8)
        """
        return self._q_prod(self, other)

    @staticmethod
    @pyaedt_function_handler()
    def _q_prod(q1, q2):
        """Performs quaternion multiplication with another quaternion or compatible value.
        This internal method has the purpose to deal with cases where one of the two factors is a scalar
        """
        # fmt: off
        # Check what is q1 and q2
        if MathUtils.is_scalar_number(q1) and MathUtils.is_scalar_number(q2):
            return q1*q2
        elif  MathUtils.is_scalar_number(q1):
            nn = q1
            qq = Quaternion._to_quaternion(q2)
            return Quaternion(qq.a*nn, qq.b*nn, qq.c*nn, qq.d*nn)
        elif  MathUtils.is_scalar_number(q2):
            nn = q2
            qq = Quaternion._to_quaternion(q1)
            return Quaternion(qq.a*nn, qq.b*nn, qq.c*nn, qq.d*nn)
        else:
            return Quaternion.hamilton_prod(Quaternion._to_quaternion(q1), Quaternion._to_quaternion(q2))
        # fmt: on

    @staticmethod
    @pyaedt_function_handler()
    def hamilton_prod(q1, q2):
        """Evaluate the Hamilton product of two quaternions, ``q1`` and ``q2``, defined as:
                q1 = p0 + p' = p0 + ip1 + jp2 + kp3
                q2 = q0 + q' = q0 + iq1 + jq2 + kq3
                m = q1*q2 = p0q0 - p' • q' + p0q' + q0p' + p' x q'

        Parameters
        ----------
        q1 : Quaternion, List, tuple
            The value to multiply with this quaternion.
            It can be another Quaternion or a sequence that can be interpreted as one.
        q2 : Quaternion, List, tuple
            The value to multiply with this quaternion.
            It can be another Quaternion or a sequence that can be interpreted as one.

        q1 and q2 must be quaternions or compatible values. Multiplicaiton between quaternions and scalar values is
        handled by the method ``mul``

        Returns
        -------
        Quaternion
            The quaternion result of the multiplication between q1 and q2

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q1 = Quaternion(1, 2, 3, 4)
        >>> q2 = Quaternion(5, 6, 7, 8)
        >>> Quaternion.hamilton_prod(q1, q2)
        Quaternion(-60, 12, 30, 24)
        """
        # fmt: off
        q1 = Quaternion._to_quaternion(q1)
        q2 = Quaternion._to_quaternion(q2)

        return Quaternion(q1.a*q2.a - q1.b*q2.b - q1.c*q2.c - q1.d*q2.d,
                          q1.a*q2.b + q1.b*q2.a + q1.c*q2.d - q1.d*q2.c,
                          q1.a*q2.c - q1.b*q2.d + q1.c*q2.a + q1.d*q2.b,
                          q1.a*q2.d + q1.b*q2.c - q1.c*q2.b + q1.d*q2.a,
                          )
        # fmt: on

    @pyaedt_function_handler()
    def conjugate(self):
        """Returns the conjugate of the quaternion."""
        q = self
        return Quaternion(q.a, -q.b, -q.c, -q.d)

    @pyaedt_function_handler()
    def norm(self):
        """Returns the norm of the quaternion."""
        # fmt: off
        q = self
        return math.sqrt(q.a**2 + q.b**2 + q.c**2 + q.d**2)
        # fmt: on

    @pyaedt_function_handler()
    def normalize(self):
        """Returns the normalized form of the quaternion."""
        # fmt: off
        q = self
        if MathUtils.is_zero(q.norm()):
            raise ValueError("Cannot normalize a quaternion with zero norm.")
        return q * (1/q.norm())
        # fmt: on

    @pyaedt_function_handler()
    def inverse(self):
        """Returns the inverse of the quaternion."""
        # fmt: off
        q = self
        if MathUtils.is_zero(q.norm()):
            raise ValueError("Cannot compute inverse for a quaternion with zero norm.")
        return (1/q.norm()**2) * q.conjugate()
        # fmt: on

    @pyaedt_function_handler()
    def div(self, other):
        """Performs quaternion division with another quaternion or compatible value.

        Parameters
        ----------
        other : Quaternion, List, tuple, float, or int
            The value to divide with this quaternion.
            It can be another Quaternion or a sequence that can be interpreted as one.
            It can also be a scalar value (float or int).

        Returns
        -------
        Quaternion
            A new quaternion representing the division of this quaternion and the given value.

        Examples
        --------
        >>> from ansys.aedt.core.generic.quaternion import Quaternion
        >>> q1 = Quaternion(1, 2, 3, 4)
        >>> q2 = Quaternion(1, -1, 1, 2)
        >>> q1.div(q2)
        Quaternion(10/7, 1/7, 10/7, -3/7)
        >>> q1.div(2)
        Quaternion(0.5, 1, 1.5, 2)
        """
        return self._q_div(self, other)

    @staticmethod
    @pyaedt_function_handler()
    def _q_div(q1, q2):
        """Performs quaternion division with another quaternion or compatible value.
        This internal method has the purpose to deal with cases where one of the two factors is a scalar
        """
        # fmt: off
        # Check what is q1 and q2
        if MathUtils.is_scalar_number(q1) and MathUtils.is_scalar_number(q2):
            return q1*q2**-1
        elif  MathUtils.is_scalar_number(q1):
            nn = q1
            qq = Quaternion._to_quaternion(q2).inverse()
            return Quaternion(qq.a*nn, qq.b*nn, qq.c*nn, qq.d*nn)
        elif  MathUtils.is_scalar_number(q2):
            nn = q2**-1
            qq = Quaternion._to_quaternion(q1)
            return Quaternion(qq.a*nn, qq.b*nn, qq.c*nn, qq.d*nn)
        else:
            return Quaternion.hamilton_prod(Quaternion._to_quaternion(q1), Quaternion._to_quaternion(q2).inverse())
        # fmt: on

    @pyaedt_function_handler()
    def coefficients(self):
        """Returns the coefficients of the quaternion as a tuple."""
        return self.a, self.b, self.c, self.d
