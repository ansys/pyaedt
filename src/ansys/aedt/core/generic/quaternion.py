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

from ansys.aedt.core.generic.math_utils import MathUtils
import math
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators

def _check_norm(elements, norm):
    """validate if input norm is consistent"""
    if norm is not None and norm.is_number:
        if norm.is_positive is False:
            raise ValueError("Input norm must be positive.")

        numerical = all(i.is_number and i.is_real is True for i in elements)
        if numerical and is_eq(norm**2, sum(i**2 for i in elements)) is False:
            raise ValueError("Incompatible value for norm.")


def _is_extrinsic(seq):
    """validate seq and return True if seq is lowercase and False if uppercase"""
    if type(seq) != str:
        raise ValueError('Expected seq to be a string.')
    if len(seq) != 3:
        raise ValueError("Expected 3 axes, got `{}`.".format(seq))

    intrinsic = seq.isupper()
    extrinsic = seq.islower()
    if not (intrinsic or extrinsic):
        raise ValueError("seq must either be fully uppercase (for extrinsic "
                         "rotations), or fully lowercase, for intrinsic "
                         "rotations).")

    i, j, k = seq.lower()
    if (i == j) or (j == k):
        raise ValueError("Consecutive axes must be different")

    bad = set(seq) - set('xyzXYZ')
    if bad:
        raise ValueError("Expected axes from `seq` to be from "
                         "['x', 'y', 'z'] or ['X', 'Y', 'Z'], "
                         "got {}".format(''.join(bad)))

    return extrinsic


class Quaternion:
    """
    Implements fundamental quaternion operations.

    Quaternions are created using ``Quaternion(a, b, c, d)``, representing the form q = a + bi + cj + dk.

    This updated class offers enhanced functionality compared to the previous implementation,
    supporting both intrinsic and extrinsic rotations. Note that AEDT coordinate systems use intrinsic rotation.


    References
    ==========

    [1] https://en.wikipedia.org/wiki/Quaternion
    [2] https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    [3] https://www.euclideanspace.com/maths/geometry/rotations/conversions/

    """

    is_commutative = False

    def __init__(self, a=0, b=0, c=0, d=0):
        """Initialize quaternion.

        Parameters
        ==========

        a, b, c, d : numbers
            The quaternion elements.
        """
        self._args = (a, b, c, d)

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

    # @property
    # def product_matrix_left(self):
    #     r"""Returns 4 x 4 Matrix equivalent to a Hamilton product from the
    #     left. This can be useful when treating quaternion elements as column
    #     vectors. Given a quaternion $q = a + bi + cj + dk$ where a, b, c and d
    #     are real numbers, the product matrix from the left is:
    #
    #     .. math::
    #
    #         M  =  \begin{bmatrix} a  &-b  &-c  &-d \\
    #                               b  & a  &-d  & c \\
    #                               c  & d  & a  &-b \\
    #                               d  &-c  & b  & a \end{bmatrix}
    #
    #     Examples
    #     ========
    #
    #     >>> from sympy import Quaternion
    #     >>> from sympy.abc import a, b, c, d
    #     >>> q1 = Quaternion(1, 0, 0, 1)
    #     >>> q2 = Quaternion(a, b, c, d)
    #     >>> q1.product_matrix_left
    #     Matrix([
    #     [1, 0,  0, -1],
    #     [0, 1, -1,  0],
    #     [0, 1,  1,  0],
    #     [1, 0,  0,  1]])
    #
    #     >>> q1.product_matrix_left * q2.to_Matrix()
    #     Matrix([
    #     [a - d],
    #     [b - c],
    #     [b + c],
    #     [a + d]])
    #
    #     This is equivalent to:
    #
    #     >>> (q1 * q2).to_Matrix()
    #     Matrix([
    #     [a - d],
    #     [b - c],
    #     [b + c],
    #     [a + d]])
    #     """
    #     return Matrix([
    #             [self.a, -self.b, -self.c, -self.d],
    #             [self.b, self.a, -self.d, self.c],
    #             [self.c, self.d, self.a, -self.b],
    #             [self.d, -self.c, self.b, self.a]])
    #
    # @property
    # def product_matrix_right(self):
    #     r"""Returns 4 x 4 Matrix equivalent to a Hamilton product from the
    #     right. This can be useful when treating quaternion elements as column
    #     vectors. Given a quaternion $q = a + bi + cj + dk$ where a, b, c and d
    #     are real numbers, the product matrix from the left is:
    #
    #     .. math::
    #
    #         M  =  \begin{bmatrix} a  &-b  &-c  &-d \\
    #                               b  & a  & d  &-c \\
    #                               c  &-d  & a  & b \\
    #                               d  & c  &-b  & a \end{bmatrix}
    #
    #
    #     Examples
    #     ========
    #
    #     >>> from sympy import Quaternion
    #     >>> from sympy.abc import a, b, c, d
    #     >>> q1 = Quaternion(a, b, c, d)
    #     >>> q2 = Quaternion(1, 0, 0, 1)
    #     >>> q2.product_matrix_right
    #     Matrix([
    #     [1, 0, 0, -1],
    #     [0, 1, 1, 0],
    #     [0, -1, 1, 0],
    #     [1, 0, 0, 1]])
    #
    #     Note the switched arguments: the matrix represents the quaternion on
    #     the right, but is still considered as a matrix multiplication from the
    #     left.
    #
    #     >>> q2.product_matrix_right * q1.to_Matrix()
    #     Matrix([
    #     [ a - d],
    #     [ b + c],
    #     [-b + c],
    #     [ a + d]])
    #
    #     This is equivalent to:
    #
    #     >>> (q1 * q2).to_Matrix()
    #     Matrix([
    #     [ a - d],
    #     [ b + c],
    #     [-b + c],
    #     [ a + d]])
    #     """
    #     return Matrix([
    #             [self.a, -self.b, -self.c, -self.d],
    #             [self.b, self.a, self.d, -self.c],
    #             [self.c, -self.d, self.a, self.b],
    #             [self.d, self.c, -self.b, self.a]])
    #
    # def to_Matrix(self, vector_only=False):
    #     """Returns elements of quaternion as a column vector.
    #     By default, a ``Matrix`` of length 4 is returned, with the real part as the
    #     first element.
    #     If ``vector_only`` is ``True``, returns only imaginary part as a Matrix of
    #     length 3.
    #
    #     Parameters
    #     ==========
    #
    #     vector_only : bool
    #         If True, only imaginary part is returned.
    #         Default value: False
    #
    #     Returns
    #     =======
    #
    #     Matrix
    #         A column vector constructed by the elements of the quaternion.
    #
    #     Examples
    #     ========
    #
    #     >>> from sympy import Quaternion
    #     >>> from sympy.abc import a, b, c, d
    #     >>> q = Quaternion(a, b, c, d)
    #     >>> q
    #     a + b*i + c*j + d*k
    #
    #     >>> q.to_Matrix()
    #     Matrix([
    #     [a],
    #     [b],
    #     [c],
    #     [d]])
    #
    #
    #     >>> q.to_Matrix(vector_only=True)
    #     Matrix([
    #     [b],
    #     [c],
    #     [d]])
    #
    #     """
    #     if vector_only:
    #         return Matrix(self.args[1:])
    #     else:
    #         return Matrix(self.args)
    #
    # @classmethod
    # def from_Matrix(cls, elements):
    #     """Returns quaternion from elements of a column vector`.
    #     If vector_only is True, returns only imaginary part as a Matrix of
    #     length 3.
    #
    #     Parameters
    #     ==========
    #
    #     elements : Matrix, list or tuple of length 3 or 4. If length is 3,
    #         assume real part is zero.
    #         Default value: False
    #
    #     Returns
    #     =======
    #
    #     Quaternion
    #         A quaternion created from the input elements.
    #
    #     Examples
    #     ========
    #
    #     >>> from sympy import Quaternion
    #     >>> from sympy.abc import a, b, c, d
    #     >>> q = Quaternion.from_Matrix([a, b, c, d])
    #     >>> q
    #     a + b*i + c*j + d*k
    #
    #     >>> q = Quaternion.from_Matrix([b, c, d])
    #     >>> q
    #     0 + b*i + c*j + d*k
    #
    #     """
    #     length = len(elements)
    #     if length != 3 and length != 4:
    #         raise ValueError("Input elements must have length 3 or 4, got {} "
    #                          "elements".format(length))
    #
    #     if length == 3:
    #         return Quaternion(0, *elements)
    #     else:
    #         return Quaternion(*elements)


    @classmethod
    def _to_quaternion(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (tuple, list)) and len(obj) == 4:
            return cls(*obj)
        else:
            raise TypeError(f"Cannot convert {obj} to {cls.__name__}.")


    @classmethod
    def from_euler(cls, angles, seq):
        """Returns quaternion equivalent to rotation represented by the Euler
        angles, in the sequence defined by ``seq``.

        Parameters
        ==========

        angles : list, tuple or Matrix of 3 numbers
            The Euler angles (in radians).
        seq : string of length 3
            Represents the sequence of rotations.
            For extrinsic rotations, seq must be all lowercase and its elements
            must be from the set ``{'x', 'y', 'z'}``
            For intrinsic rotations, seq must be all uppercase and its elements
            must be from the set ``{'X', 'Y', 'Z'}``

        Returns
        =======

        Quaternion
            The normalized rotation quaternion calculated from the Euler angles
            in the given sequence.

        Examples
        ========

        >>> from ansys.geometry import Quaternion
        >>> from sympy import pi
        >>> q = Quaternion.from_euler([pi/2, 0, 0], 'xyz')
        >>> q
        sqrt(2)/2 + sqrt(2)/2*i + 0*j + 0*k

        >>> q = Quaternion.from_euler([0, pi/2, pi] , 'zyz')
        >>> q
        0 + (-sqrt(2)/2)*i + 0*j + sqrt(2)/2*k

        >>> q = Quaternion.from_euler([0, pi/2, pi] , 'ZYZ')
        >>> q
        0 + sqrt(2)/2*i + 0*j + sqrt(2)/2*k

        """

        if len(angles) != 3:
            raise ValueError("3 angles must be given.")

        extrinsic = _is_extrinsic(seq)
        i, j, k = seq.lower()

        # get elementary basis vectors
        ei = [1 if n == i else 0 for n in 'xyz']
        ej = [1 if n == j else 0 for n in 'xyz']
        ek = [1 if n == k else 0 for n in 'xyz']

        # calculate distinct quaternions
        qi = cls.from_axis_angle(ei, angles[0])
        qj = cls.from_axis_angle(ej, angles[1])
        qk = cls.from_axis_angle(ek, angles[2])

        if extrinsic:
            return qk * qj * qi
        else:
            return qi * qj * qk

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
            If ``True``, the rotation is treated as extrinsic. If ``False`` (default), it is treated as intrinsic.

        Note
        ----
        Tait–Bryan angles (Heading, Pitch, Bank) correspond to an intrinsic "ZYX" sequence.

        Returns
        -------
        tuple of float
            A tuple of three Euler angles representing the same rotation as the quaternion.
            Angle in radians.

        References
        ----------

        [1] https://doi.org/10.1371/journal.pone.0276302
        [2] https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles


        """
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
            a, b, c, d = a - c, b + d, c + a, d - b

        angles[1] = 2 * MathUtils.atan2(math.sqrt(c * c + d * d), math.sqrt(a * a + b * b))
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

    @classmethod
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

        """
        (x, y, z) = GeometryOperators.normalize_vector(axis)
        s = math.sin(angle * 0.5)
        a = math.cos(angle * 0.5)
        b = x * s
        c = y * s
        d = z * s
        return cls(a, b, c, d)




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

    def __pow__(self, p):
        return self.pow(p)

    def __neg__(self):
        return Quaternion(-self.a, -self.b, -self.c, -self.d)

    def __truediv__(self, other):
        return self._q_div(self, other)

    def __rtruediv__(self, other):
        return self._q_div(other, self)

    def __repr__(self):
        return f"{type(self).__name__}({self.a}, {self.b}, {self.c}, {self.d})"


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
    def _q_prod(q1, q2):
        """Performs quaternion multiplication with another quaternion or compatible value.
        This internal method has the purpose to deal with cases where one of the two factors is a scalar"""

        # Check what is q1 and q2
        if MathUtils.is_scalar_number(q1) and MathUtils.is_scalar_number(q2):
            return q1*q2
        elif  MathUtils.is_scalar_number(q1):
            nn=q1
            qq = Quaternion._to_quaternion(q2)
            return Quaternion(qq.a * nn, qq.b* nn, qq.c* nn, qq.d* nn)
        elif  MathUtils.is_scalar_number(q2):
            nn=q2
            qq = Quaternion._to_quaternion(q1)
            return Quaternion(qq.a * nn, qq.b* nn, qq.c* nn, qq.d* nn)
        else:
            return Quaternion.hamilton_prod(Quaternion._to_quaternion(q1), Quaternion._to_quaternion(q2))


    @staticmethod
    def hamilton_prod(q1, q2):
        """Evaluate the Hamilton product of two quaternions, ``q1`` and ``q2``, defined as:
                q1 = p0 + p' = p0 + ip1 + jp2 + kp3.
                q2 = q0 + q' = q0 + iq1 + jq2 + kq3.
                m = q1*q2 = p0q0 - p' • q' + p0q' + q0p' + p' x q'.

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
        >>> Quaternion.h_prod(q1,q2)
        Quaternion(-60, 12, 30, 24)
        """
        q1 = Quaternion._to_quaternion(q1)
        q2 = Quaternion._to_quaternion(q2)

        return Quaternion(q1.a*q2.a - q1.b*q2.b - q1.c*q2.c - q1.d*q2.d,
                          q1.a*q2.b + q1.b*q2.a + q1.c*q2.d - q1.d*q2.c,
                          q1.a*q2.c - q1.b*q2.d + q1.c*q2.a + q1.d*q2.b,
                          q1.a*q2.d + q1.b*q2.c - q1.c*q2.b + q1.d*q2.a,
                          )

    def conjugate(self):
        """Returns the conjugate of the quaternion."""
        q = self
        return Quaternion(q.a, -q.b, -q.c, -q.d)

    def norm(self):
        """Returns the norm of the quaternion."""
        q = self
        return math.sqrt(q.a**2 + q.b**2 + q.c**2 + q.d**2)

    def normalize(self):
        """Returns the normalized form of the quaternion."""
        q = self
        return q * (1/q.norm())

    def inverse(self):
        """Returns the inverse of the quaternion."""
        q = self
        if MathUtils.is_zero(q.norm()):
            raise ValueError("Cannot compute inverse for a quaternion with zero norm")
        return (1/q.norm()**2) * q.conjugate()


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
        >>> q2 = Quaternion(5, 6, 7, 8)
        >>> q1.div(q2)
        Quaternion(-60, 12, 30, 24)
        >>> q1.div(2)
        Quaternion(0.5, 1, 1.5, 2)
        """
        return self._q_div(self, other)


    @staticmethod
    def _q_div(q1, q2):
        """Performs quaternion division with another quaternion or compatible value.
        This internal method has the purpose to deal with cases where one of the two factors is a scalar"""

        # Check what is q1 and q2
        if MathUtils.is_scalar_number(q1) and MathUtils.is_scalar_number(q2):
            return q1*q2**-1
        elif  MathUtils.is_scalar_number(q1):
            nn=q1
            qq = Quaternion._to_quaternion(q2).inverse()
            return Quaternion(qq.a * nn, qq.b* nn, qq.c* nn, qq.d* nn)
        elif  MathUtils.is_scalar_number(q2):
            nn=q2**-1
            qq = Quaternion._to_quaternion(q1)
            return Quaternion(qq.a * nn, qq.b* nn, qq.c* nn, qq.d* nn)
        else:
            return Quaternion.hamilton_prod(Quaternion._to_quaternion(q1), Quaternion._to_quaternion(q2).inverse())



    @staticmethod
    def rotate_point(pin, r):
        """Returns the coordinates of the point pin (a 3 tuple) after rotation.

        Parameters
        ==========

        pin : tuple
            A 3-element tuple of coordinates of a point which needs to be
            rotated.
        r : Quaternion or tuple
            Axis and angle of rotation.

            It's important to note that when r is a tuple, it must be of the form
            (axis, angle)

        Returns
        =======

        tuple
            The coordinates of the point after rotation.

        Examples
        ========

        >>> from sympy import Quaternion
        >>> from sympy import symbols, trigsimp, cos, sin
        >>> x = symbols('x')
        >>> q = Quaternion(cos(x/2), 0, 0, sin(x/2))
        >>> trigsimp(Quaternion.rotate_point((1, 1, 1), q))
        (sqrt(2)*cos(x + pi/4), sqrt(2)*sin(x + pi/4), 1)
        >>> (axis, angle) = q.to_axis_angle()
        >>> trigsimp(Quaternion.rotate_point((1, 1, 1), (axis, angle)))
        (sqrt(2)*cos(x + pi/4), sqrt(2)*sin(x + pi/4), 1)

        """
        if isinstance(r, tuple):
            # if r is of the form (vector, angle)
            q = Quaternion.from_axis_angle(r[0], r[1])
        else:
            # if r is a quaternion
            q = r.normalize()
        pout = q * Quaternion(0, pin[0], pin[1], pin[2]) * conjugate(q)
        return (pout.b, pout.c, pout.d)

    def to_axis_angle(self):
        """Returns the axis and angle of rotation of a quaternion.

        Returns
        =======

        tuple
            Tuple of (axis, angle)

        Examples
        ========

        >>> from sympy import Quaternion
        >>> q = Quaternion(1, 1, 1, 1)
        >>> (axis, angle) = q.to_axis_angle()
        >>> axis
        (sqrt(3)/3, sqrt(3)/3, sqrt(3)/3)
        >>> angle
        2*pi/3

        """
        q = self
        if q.a.is_negative:
            q = q * -1

        q = q.normalize()
        angle = trigsimp(2 * acos(q.a))

        # Since quaternion is normalised, q.a is less than 1.
        s = sqrt(1 - q.a*q.a)

        x = trigsimp(q.b / s)
        y = trigsimp(q.c / s)
        z = trigsimp(q.d / s)

        v = (x, y, z)
        t = (v, angle)

        return t

    def to_rotation_matrix(self, v=None, homogeneous=True):
        """Returns the equivalent rotation transformation matrix of the quaternion
        which represents rotation about the origin if ``v`` is not passed.

        Parameters
        ==========

        v : tuple or None
            Default value: None
        homogeneous : bool
            When True, gives an expression that may be more efficient for
            symbolic calculations but less so for direct evaluation. Both
            formulas are mathematically equivalent.
            Default value: True

        Returns
        =======

        tuple
            Returns the equivalent rotation transformation matrix of the quaternion
            which represents rotation about the origin if v is not passed.

        Examples
        ========

        >>> from sympy import Quaternion
        >>> from sympy import symbols, trigsimp, cos, sin
        >>> x = symbols('x')
        >>> q = Quaternion(cos(x/2), 0, 0, sin(x/2))
        >>> trigsimp(q.to_rotation_matrix())
        Matrix([
        [cos(x), -sin(x), 0],
        [sin(x),  cos(x), 0],
        [     0,       0, 1]])

        Generates a 4x4 transformation matrix (used for rotation about a point
        other than the origin) if the point(v) is passed as an argument.
        """

        q = self
        s = q.norm()**-2

        # diagonal elements are different according to parameter normal
        if homogeneous:
            m00 = s*(q.a**2 + q.b**2 - q.c**2 - q.d**2)
            m11 = s*(q.a**2 - q.b**2 + q.c**2 - q.d**2)
            m22 = s*(q.a**2 - q.b**2 - q.c**2 + q.d**2)
        else:
            m00 = 1 - 2*s*(q.c**2 + q.d**2)
            m11 = 1 - 2*s*(q.b**2 + q.d**2)
            m22 = 1 - 2*s*(q.b**2 + q.c**2)

        m01 = 2*s*(q.b*q.c - q.d*q.a)
        m02 = 2*s*(q.b*q.d + q.c*q.a)

        m10 = 2*s*(q.b*q.c + q.d*q.a)
        m12 = 2*s*(q.c*q.d - q.b*q.a)

        m20 = 2*s*(q.b*q.d - q.c*q.a)
        m21 = 2*s*(q.c*q.d + q.b*q.a)

        if not v:
            return Matrix([[m00, m01, m02], [m10, m11, m12], [m20, m21, m22]])

        else:
            (x, y, z) = v

            m03 = x - x*m00 - y*m01 - z*m02
            m13 = y - x*m10 - y*m11 - z*m12
            m23 = z - x*m20 - y*m21 - z*m22
            m30 = m31 = m32 = 0
            m33 = 1

            return Matrix([[m00, m01, m02, m03], [m10, m11, m12, m13],
                          [m20, m21, m22, m23], [m30, m31, m32, m33]])


    def axis(self):
        r"""
        Returns $\mathbf{Ax}(q)$, the axis of the quaternion $q$.

        Explanation
        ===========

        Given a quaternion $q = a + bi + cj + dk$, returns $\mathbf{Ax}(q)$  i.e., the versor of the vector part of that quaternion
        equal to $\mathbf{U}[\mathbf{V}(q)]$.
        The axis is always an imaginary unit with square equal to $-1 + 0i + 0j + 0k$.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(1, 1, 1, 1)
        >>> q.axis()
        0 + sqrt(3)/3*i + sqrt(3)/3*j + sqrt(3)/3*k

        See Also
        ========

        vector_part

        """
        axis = self.vector_part().normalize()

        return Quaternion(0, axis.b, axis.c, axis.d)

    def is_pure(self):
        """
        Returns true if the quaternion is pure, false if the quaternion is not pure
        or returns none if it is unknown.

        Explanation
        ===========

        A pure quaternion (also a vector quaternion) is a quaternion with scalar
        part equal to 0.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(0, 8, 13, 12)
        >>> q.is_pure()
        True

        See Also
        ========
        scalar_part

        """

        return self.a.is_zero

    def is_zero_quaternion(self):
        """
        Returns true if the quaternion is a zero quaternion or false if it is not a zero quaternion
        and None if the value is unknown.

        Explanation
        ===========

        A zero quaternion is a quaternion with both scalar part and
        vector part equal to 0.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(1, 0, 0, 0)
        >>> q.is_zero_quaternion()
        False

        >>> q = Quaternion(0, 0, 0, 0)
        >>> q.is_zero_quaternion()
        True

        See Also
        ========
        scalar_part
        vector_part

        """

        return self.norm().is_zero

    def angle(self):
        r"""
        Returns the angle of the quaternion measured in the real-axis plane.

        Explanation
        ===========

        Given a quaternion $q = a + bi + cj + dk$ where $a$, $b$, $c$ and $d$
        are real numbers, returns the angle of the quaternion given by

        .. math::
            \theta := 2 \operatorname{atan_2}\left(\sqrt{b^2 + c^2 + d^2}, {a}\right)

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(1, 4, 4, 4)
        >>> q.angle()
        2*atan(4*sqrt(3))

        """

        return 2 * atan2(self.vector_part().norm(), self.scalar_part())


    def arc_coplanar(self, other):
        """
        Returns True if the transformation arcs represented by the input quaternions happen in the same plane.

        Explanation
        ===========

        Two quaternions are said to be coplanar (in this arc sense) when their axes are parallel.
        The plane of a quaternion is the one normal to its axis.

        Parameters
        ==========

        other : a Quaternion

        Returns
        =======

        True : if the planes of the two quaternions are the same, apart from its orientation/sign.
        False : if the planes of the two quaternions are not the same, apart from its orientation/sign.
        None : if plane of either of the quaternion is unknown.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q1 = Quaternion(1, 4, 4, 4)
        >>> q2 = Quaternion(3, 8, 8, 8)
        >>> Quaternion.arc_coplanar(q1, q2)
        True

        >>> q1 = Quaternion(2, 8, 13, 12)
        >>> Quaternion.arc_coplanar(q1, q2)
        False

        See Also
        ========

        vector_coplanar
        is_pure

        """
        if (self.is_zero_quaternion()) or (other.is_zero_quaternion()):
            raise ValueError('Neither of the given quaternions can be 0')

        return fuzzy_or([(self.axis() - other.axis()).is_zero_quaternion(), (self.axis() + other.axis()).is_zero_quaternion()])

    @classmethod
    def vector_coplanar(cls, q1, q2, q3):
        r"""
        Returns True if the axis of the pure quaternions seen as 3D vectors
        ``q1``, ``q2``, and ``q3`` are coplanar.

        Explanation
        ===========

        Three pure quaternions are vector coplanar if the quaternions seen as 3D vectors are coplanar.

        Parameters
        ==========

        q1
            A pure Quaternion.
        q2
            A pure Quaternion.
        q3
            A pure Quaternion.

        Returns
        =======

        True : if the axis of the pure quaternions seen as 3D vectors
        q1, q2, and q3 are coplanar.
        False : if the axis of the pure quaternions seen as 3D vectors
        q1, q2, and q3 are not coplanar.
        None : if the axis of the pure quaternions seen as 3D vectors
        q1, q2, and q3 are coplanar is unknown.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q1 = Quaternion(0, 4, 4, 4)
        >>> q2 = Quaternion(0, 8, 8, 8)
        >>> q3 = Quaternion(0, 24, 24, 24)
        >>> Quaternion.vector_coplanar(q1, q2, q3)
        True

        >>> q1 = Quaternion(0, 8, 16, 8)
        >>> q2 = Quaternion(0, 8, 3, 12)
        >>> Quaternion.vector_coplanar(q1, q2, q3)
        False

        See Also
        ========

        axis
        is_pure

        """

        if fuzzy_not(q1.is_pure()) or fuzzy_not(q2.is_pure()) or fuzzy_not(q3.is_pure()):
            raise ValueError('The given quaternions must be pure')

        M = Matrix([[q1.b, q1.c, q1.d], [q2.b, q2.c, q2.d], [q3.b, q3.c, q3.d]]).det()
        return M.is_zero

    def parallel(self, other):
        """
        Returns True if the two pure quaternions seen as 3D vectors are parallel.

        Explanation
        ===========

        Two pure quaternions are called parallel when their vector product is commutative which
        implies that the quaternions seen as 3D vectors have same direction.

        Parameters
        ==========

        other : a Quaternion

        Returns
        =======

        True : if the two pure quaternions seen as 3D vectors are parallel.
        False : if the two pure quaternions seen as 3D vectors are not parallel.
        None : if the two pure quaternions seen as 3D vectors are parallel is unknown.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(0, 4, 4, 4)
        >>> q1 = Quaternion(0, 8, 8, 8)
        >>> q.parallel(q1)
        True

        >>> q1 = Quaternion(0, 8, 13, 12)
        >>> q.parallel(q1)
        False

        """

        if fuzzy_not(self.is_pure()) or fuzzy_not(other.is_pure()):
            raise ValueError('The provided quaternions must be pure')

        return (self*other - other*self).is_zero_quaternion()

    def orthogonal(self, other):
        """
        Returns the orthogonality of two quaternions.

        Explanation
        ===========

        Two pure quaternions are called orthogonal when their product is anti-commutative.

        Parameters
        ==========

        other : a Quaternion

        Returns
        =======

        True : if the two pure quaternions seen as 3D vectors are orthogonal.
        False : if the two pure quaternions seen as 3D vectors are not orthogonal.
        None : if the two pure quaternions seen as 3D vectors are orthogonal is unknown.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(0, 4, 4, 4)
        >>> q1 = Quaternion(0, 8, 8, 8)
        >>> q.orthogonal(q1)
        False

        >>> q1 = Quaternion(0, 2, 2, 0)
        >>> q = Quaternion(0, 2, -2, 0)
        >>> q.orthogonal(q1)
        True

        """

        if fuzzy_not(self.is_pure()) or fuzzy_not(other.is_pure()):
            raise ValueError('The given quaternions must be pure')

        return (self*other + other*self).is_zero_quaternion()

    def index_vector(self):
        r"""
        Returns the index vector of the quaternion.

        Explanation
        ===========

        The index vector is given by $\mathbf{T}(q)$, the norm (or magnitude) of
        the quaternion $q$, multiplied by $\mathbf{Ax}(q)$, the axis of $q$.

        Returns
        =======

        Quaternion: representing index vector of the provided quaternion.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(2, 4, 2, 4)
        >>> q.index_vector()
        0 + 4*sqrt(10)/3*i + 2*sqrt(10)/3*j + 4*sqrt(10)/3*k

        See Also
        ========

        axis
        norm

        """

        return self.norm() * self.axis()

    def mensor(self):
        """
        Returns the natural logarithm of the norm(magnitude) of the quaternion.

        Examples
        ========

        >>> from sympy.algebras.quaternion import Quaternion
        >>> q = Quaternion(2, 4, 2, 4)
        >>> q.mensor()
        log(2*sqrt(10))
        >>> q.norm()
        2*sqrt(10)

        See Also
        ========

        norm

        """

        return ln(self.norm())
