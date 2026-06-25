# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Strongly-typed, fluent builder for AEDT Fields Calculator expressions.

The AEDT Fields Calculator is driven by a stack of string operations (reverse
Polish notation), for example ``Fundamental_Quantity('E')``, ``Operation('Real')``,
``Operation('Tangent')``, ``Operation('Dot')``. Assembling those strings by hand
is error-prone and hides which operations are valid for a given quantity.

This module wraps that operation grammar with four typed expression classes that
mirror the calculator's register kinds:

* :class:`ScalarReal`     — a real scalar quantity.
* :class:`ScalarComplex`  — a complex scalar quantity.
* :class:`VectorReal`     — a real 3-vector quantity.
* :class:`VectorComplex`  — a complex 3-vector quantity.

Each class exposes only the unary ``.method()`` operations that are valid for it,
annotated with the concrete type they produce, so an editor / type checker guides
the user. Binary operations are Python operators (``+ - * /``) and the free
functions :func:`dot` and :func:`cross`. Every method simply appends the matching
calculator operation token; nothing is sent to AEDT until the expression is
materialized with :meth:`FieldExpression.add`, :meth:`FieldExpression.evaluate`,
or :meth:`FieldExpression.export`, which reuse the existing
:class:`~ansys.aedt.core.visualization.post.fields_calculator.FieldsCalculator`.

No raw binary field data is read — this is purely a typed front end for the
calculator's own operation stack.

Examples
--------
>>> from ansys.aedt.core import Hfss
>>> hfss = Hfss()
>>> fx = hfss.post.fields_calculator.expressions
>>> # |E| integrated over a surface, as a typed chain instead of a string stack
>>> E = fx.vector("E")                  # VectorComplex
>>> energy = (E.magnitude() * E.magnitude()).integrate(Surface("MySheet"))
>>> value = energy.evaluate(setup="Setup1 : LastAdaptive")
>>> hfss.release_desktop()
"""

from __future__ import annotations

from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError


# ---------------------------------------------------------------------------
# geometry (integration / evaluation domains)
# ---------------------------------------------------------------------------
class CalculatorGeometry(PyAedtBase):
    """Base class for a calculator geometry (line, surface, volume, point)."""

    enter_token: str = ""
    value_op: str = ""
    assignment_type: str = ""

    def __init__(self, assignment) -> None:
        # accept a name or any object exposing ``.name``
        self.assignment = getattr(assignment, "name", assignment)

    def _operations(self) -> List[str]:
        ops = [f"{self.enter_token}('{self.assignment}')"]
        if self.value_op:
            ops.append(f"Operation('{self.value_op}')")
        return ops


class Line(CalculatorGeometry):
    """A polyline domain (``EnterLine`` / ``LineValue``)."""

    enter_token = "EnterLine"
    value_op = "LineValue"
    assignment_type = "Line"


class Surface(CalculatorGeometry):
    """A surface / sheet / face domain (``EnterSurface`` / ``SurfaceValue``)."""

    enter_token = "EnterSurface"
    value_op = "SurfaceValue"
    assignment_type = "Surface"


class Volume(CalculatorGeometry):
    """A volume / solid domain (``EnterVolume`` / ``VolumeValue``)."""

    enter_token = "EnterVolume"
    value_op = "VolumeValue"
    assignment_type = "Volume"


# ---------------------------------------------------------------------------
# base expression
# ---------------------------------------------------------------------------
class FieldExpression(PyAedtBase):
    """Base class for a typed Fields Calculator expression.

    Holds the accumulated list of calculator operation tokens plus the metadata
    needed to register the expression. Not instantiated directly — use the
    factory methods on :class:`FieldExpressions`.
    """

    is_vector: bool = False
    is_complex: bool = False

    def __init__(
        self,
        operations: Sequence[str],
        *,
        calculator=None,
        description: str = "",
        design_type: Optional[List[str]] = None,
        fields_type: Optional[List[str]] = None,
        assignment_types: Optional[List[str]] = None,
        primary_sweep: str = "Freq",
        solution_type: str = "",
    ) -> None:
        self._operations: List[str] = list(operations)
        self._calculator = calculator
        self._description = description
        self._design_type = design_type
        self._fields_type = fields_type or ["Fields"]
        self._assignment_types = list(assignment_types or [])
        self._primary_sweep = primary_sweep
        self._solution_type = solution_type

    # -- introspection -------------------------------------------------------
    @property
    def operations(self) -> List[str]:
        """Copy of the calculator operation stack this expression compiles to."""
        return list(self._operations)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} ops={len(self._operations)}>"

    # -- builders ------------------------------------------------------------
    def _spawn(
        self,
        vector: bool,
        complex_: bool,
        extra_ops: Sequence[str],
        *,
        more_assignment_types: Optional[List[str]] = None,
    ) -> "FieldExpression":
        cls = _LEAF[(vector, complex_)]
        ats = self._assignment_types + list(more_assignment_types or [])
        return cls(
            self._operations + list(extra_ops),
            calculator=self._calculator,
            description=self._description,
            design_type=self._design_type,
            fields_type=self._fields_type,
            assignment_types=ats,
            primary_sweep=self._primary_sweep,
            solution_type=self._solution_type,
        )

    def _unary(self, op: str, *, vector: bool, complex_: bool) -> "FieldExpression":
        return self._spawn(vector, complex_, [f"Operation('{op}')"])

    def _binary(self, other: "FieldExpression", op: str, *, vector: bool, complex_: bool) -> "FieldExpression":
        if not isinstance(other, FieldExpression):
            raise TypeError("operand must be a FieldExpression")
        cls = _LEAF[(vector, complex_)]
        return cls(
            self._operations + other._operations + [f"Operation('{op}')"],
            calculator=self._calculator or other._calculator,
            description=self._description,
            design_type=self._design_type or other._design_type,
            fields_type=self._fields_type,
            assignment_types=self._assignment_types + other._assignment_types,
            primary_sweep=self._primary_sweep,
            solution_type=self._solution_type,
        )

    def _reduce(self, geometry: CalculatorGeometry, final_op: str) -> "FieldExpression":
        """Geometry value + a final reduction op (Integrate / Maximum / ...)."""
        ops = geometry._operations()
        if final_op:
            ops.append(f"Operation('{final_op}')")
        return self._spawn(False, self.is_complex, ops, more_assignment_types=[geometry.assignment_type])

    def __neg__(self) -> "FieldExpression":
        return self._unary("Neg", vector=self.is_vector, complex_=self.is_complex)

    # -- materialize (reuse the existing FieldsCalculator) -------------------
    def to_dict(self, name: str, assignment: str = "") -> dict:
        """Compile this expression to a Fields Calculator expression dictionary."""
        return {
            "name": name,
            "description": self._description or name,
            "design_type": self._design_type or ["HFSS"],
            "fields_type": self._fields_type,
            "solution_type": self._solution_type,
            "primary_sweep": self._primary_sweep,
            "assignment": assignment,
            "assignment_type": self._assignment_types or ["Line"],
            "operations": self.operations,
            "dependent_expressions": [],
            "report": ["Data Table"],
        }

    def _require_calculator(self):
        if self._calculator is None:
            raise AEDTRuntimeError(
                "this expression is not bound to a FieldsCalculator; build it from "
                "hfss.post.fields_calculator.expressions"
            )
        return self._calculator

    @pyaedt_function_handler()
    def add(self, name: str, assignment=None) -> Union[str, bool]:
        """Register this expression as an AEDT named expression.

        Parameters
        ----------
        name : str
            Name of the named expression to create.
        assignment : optional
            Object assignment passed through to
            :meth:`FieldsCalculator.add_expression`. Geometry referenced through
            :class:`Line` / :class:`Surface` / :class:`Volume` is already embedded
            in the operation stack, so this is usually ``None``.

        Returns
        -------
        str or bool
            The named-expression name when successful, ``False`` otherwise.
        """
        return self._require_calculator().add_expression(self.to_dict(name), assignment, name=name)

    @pyaedt_function_handler()
    def evaluate(
        self,
        name: Optional[str] = None,
        setup: Optional[str] = None,
        intrinsics: Optional[dict] = None,
        assignment=None,
    ) -> float:
        """Register and evaluate this expression to a single value.

        Parameters
        ----------
        name : str, optional
            Named-expression name. A unique one is generated when not provided.
        setup : str, optional
            Solution name, for example ``"Setup1 : LastAdaptive"``.
        intrinsics : dict, optional
            Intrinsic variables (``Freq`` / ``Time`` / ``Phase``).
        assignment : optional
            Forwarded to :meth:`add`.

        Returns
        -------
        float
            The evaluated value.
        """
        calc = self._require_calculator()
        name = name or generate_unique_name("fcx")
        self.add(name, assignment)
        return calc.evaluate(name, setup=setup, intrinsics=intrinsics)

    @pyaedt_function_handler()
    def export(self, output_file: str, name: Optional[str] = None, **kwargs):
        """Register and export this expression to a field file.

        Extra keyword arguments are forwarded to
        :meth:`FieldsCalculator.export` (``solution``, ``sample_points``,
        ``grid_type``, ``intrinsics`` ...). ``is_vector`` is set automatically.
        """
        calc = self._require_calculator()
        name = name or generate_unique_name("fcx")
        self.add(name)
        kwargs.setdefault("is_vector", self.is_vector)
        return calc.export(quantity=name, output_file=output_file, **kwargs)


# ---------------------------------------------------------------------------
# scalar real
# ---------------------------------------------------------------------------
class ScalarReal(FieldExpression):
    """A real scalar Fields Calculator quantity."""

    is_vector = False
    is_complex = False

    def absolute(self) -> "ScalarReal":
        """Absolute value ``|s|`` (calculator ``Mag``)."""
        return self._unary("Mag", vector=False, complex_=False)

    def smooth(self) -> "ScalarReal":
        """Smooth the quantity across the mesh (calculator ``Smooth``)."""
        return self._unary("Smooth", vector=False, complex_=False)

    def gradient(self) -> "VectorReal":
        """Gradient ``∇s`` (calculator ``Grad``)."""
        return self._unary("Grad", vector=True, complex_=False)

    # arithmetic
    def __add__(self, other) -> "ScalarReal":
        return _scalar_arith(self, other, "+")

    def __sub__(self, other) -> "ScalarReal":
        return _scalar_arith(self, other, "-")

    def __mul__(self, other) -> "FieldExpression":
        return _scalar_mul(self, other, "*")

    def __truediv__(self, other) -> "FieldExpression":
        return _scalar_mul(self, other, "/")

    # geometry reductions
    def integrate(self, over: CalculatorGeometry) -> "ScalarReal":
        """Integrate over a geometry ``∫ s dΩ`` (calculator ``Integrate``)."""
        return self._reduce(over, "Integrate")

    def maximum(self, over: CalculatorGeometry) -> "ScalarReal":
        """Maximum over a geometry (calculator ``Maximum``)."""
        return self._reduce(over, "Maximum")

    def minimum(self, over: CalculatorGeometry) -> "ScalarReal":
        """Minimum over a geometry (calculator ``Minimum``)."""
        return self._reduce(over, "Minimum")

    def value(self, over: CalculatorGeometry) -> "ScalarReal":
        """Sample the quantity on a geometry without integrating."""
        return self._reduce(over, "")


# ---------------------------------------------------------------------------
# scalar complex
# ---------------------------------------------------------------------------
class ScalarComplex(FieldExpression):
    """A complex scalar Fields Calculator quantity."""

    is_vector = False
    is_complex = True

    def real(self) -> "ScalarReal":
        """Real part (calculator ``Real``)."""
        return self._unary("Real", vector=False, complex_=False)

    def imaginary(self) -> "ScalarReal":
        """Imaginary part (calculator ``Imag``)."""
        return self._unary("Imag", vector=False, complex_=False)

    def magnitude(self) -> "ScalarReal":
        """Complex magnitude ``|s|`` (calculator ``CmplxMag``)."""
        return self._unary("CmplxMag", vector=False, complex_=False)

    def conjugate(self) -> "ScalarComplex":
        """Complex conjugate (calculator ``Conj``)."""
        return self._unary("Conj", vector=False, complex_=True)

    def smooth(self) -> "ScalarComplex":
        """Smooth the quantity across the mesh (calculator ``Smooth``)."""
        return self._unary("Smooth", vector=False, complex_=True)

    def __add__(self, other) -> "ScalarComplex":
        return _scalar_arith(self, other, "+")

    def __sub__(self, other) -> "ScalarComplex":
        return _scalar_arith(self, other, "-")

    def __mul__(self, other) -> "FieldExpression":
        return _scalar_mul(self, other, "*")

    def __truediv__(self, other) -> "FieldExpression":
        return _scalar_mul(self, other, "/")

    def integrate(self, over: CalculatorGeometry) -> "ScalarComplex":
        """Integrate over a geometry ``∫ s dΩ`` (calculator ``Integrate``)."""
        return self._reduce(over, "Integrate")

    def value(self, over: CalculatorGeometry) -> "ScalarComplex":
        """Sample the quantity on a geometry without integrating."""
        return self._reduce(over, "")


# ---------------------------------------------------------------------------
# vector real
# ---------------------------------------------------------------------------
class VectorReal(FieldExpression):
    """A real 3-vector Fields Calculator quantity."""

    is_vector = True
    is_complex = False

    def scalar_x(self) -> "ScalarReal":
        """X component (calculator ``ScalarX``)."""
        return self._unary("ScalarX", vector=False, complex_=False)

    def scalar_y(self) -> "ScalarReal":
        """Y component (calculator ``ScalarY``)."""
        return self._unary("ScalarY", vector=False, complex_=False)

    def scalar_z(self) -> "ScalarReal":
        """Z component (calculator ``ScalarZ``)."""
        return self._unary("ScalarZ", vector=False, complex_=False)

    def magnitude(self) -> "ScalarReal":
        """Vector magnitude ``‖v‖`` (calculator ``Mag``)."""
        return self._unary("Mag", vector=False, complex_=False)

    def tangent(self) -> "VectorReal":
        """Tangential component on the active surface (calculator ``Tangent``)."""
        return self._unary("Tangent", vector=True, complex_=False)

    def normal(self) -> "VectorReal":
        """Normal component on the active surface (calculator ``Normal``)."""
        return self._unary("Normal", vector=True, complex_=False)

    def curl(self) -> "VectorReal":
        """Curl ``∇×v`` (calculator ``Curl``)."""
        return self._unary("Curl", vector=True, complex_=False)

    def divergence(self) -> "ScalarReal":
        """Divergence ``∇·v`` (calculator ``Divg``)."""
        return self._unary("Divg", vector=False, complex_=False)

    def __add__(self, other) -> "VectorReal":
        return _vector_arith(self, other, "+")

    def __sub__(self, other) -> "VectorReal":
        return _vector_arith(self, other, "-")

    def __mul__(self, other) -> "VectorReal":
        return _vector_scale(self, other, "*")

    def __truediv__(self, other) -> "VectorReal":
        return _vector_scale(self, other, "/")


# ---------------------------------------------------------------------------
# vector complex
# ---------------------------------------------------------------------------
class VectorComplex(FieldExpression):
    """A complex 3-vector Fields Calculator quantity."""

    is_vector = True
    is_complex = True

    def scalar_x(self) -> "ScalarComplex":
        """X component (calculator ``ScalarX``)."""
        return self._unary("ScalarX", vector=False, complex_=True)

    def scalar_y(self) -> "ScalarComplex":
        """Y component (calculator ``ScalarY``)."""
        return self._unary("ScalarY", vector=False, complex_=True)

    def scalar_z(self) -> "ScalarComplex":
        """Z component (calculator ``ScalarZ``)."""
        return self._unary("ScalarZ", vector=False, complex_=True)

    def real(self) -> "VectorReal":
        """Real part, component-wise (calculator ``Real``)."""
        return self._unary("Real", vector=True, complex_=False)

    def imaginary(self) -> "VectorReal":
        """Imaginary part, component-wise (calculator ``Imag``)."""
        return self._unary("Imag", vector=True, complex_=False)

    def magnitude(self) -> "ScalarReal":
        """Complex vector magnitude (calculator ``Mag``)."""
        return self._unary("Mag", vector=False, complex_=False)

    def conjugate(self) -> "VectorComplex":
        """Complex conjugate, component-wise (calculator ``Conj``)."""
        return self._unary("Conj", vector=True, complex_=True)

    def tangent(self) -> "VectorComplex":
        """Tangential component on the active surface (calculator ``Tangent``)."""
        return self._unary("Tangent", vector=True, complex_=True)

    def normal(self) -> "VectorComplex":
        """Normal component on the active surface (calculator ``Normal``)."""
        return self._unary("Normal", vector=True, complex_=True)

    def curl(self) -> "VectorComplex":
        """Curl ``∇×v`` (calculator ``Curl``)."""
        return self._unary("Curl", vector=True, complex_=True)

    def divergence(self) -> "ScalarComplex":
        """Divergence ``∇·v`` (calculator ``Divg``)."""
        return self._unary("Divg", vector=False, complex_=True)

    def __add__(self, other) -> "VectorComplex":
        return _vector_arith(self, other, "+")

    def __sub__(self, other) -> "VectorComplex":
        return _vector_arith(self, other, "-")

    def __mul__(self, other) -> "VectorComplex":
        return _vector_scale(self, other, "*")

    def __truediv__(self, other) -> "VectorComplex":
        return _vector_scale(self, other, "/")


# leaf-class registry keyed by (is_vector, is_complex)
_LEAF = {
    (False, False): ScalarReal,
    (False, True): ScalarComplex,
    (True, False): VectorReal,
    (True, True): VectorComplex,
}


# ---------------------------------------------------------------------------
# binary helpers (type promotion mirrors the data-level semantics)
# ---------------------------------------------------------------------------
def _both(a: FieldExpression, b: FieldExpression) -> bool:
    return a.is_complex or b.is_complex


def _scalar_arith(a: FieldExpression, b, op: str) -> FieldExpression:
    if not isinstance(b, FieldExpression):
        raise TypeError("operand must be a FieldExpression (constants not yet supported)")
    if b.is_vector:
        raise TypeError("cannot add/subtract a scalar and a vector")
    return a._binary(b, op, vector=False, complex_=_both(a, b))


def _scalar_mul(a: FieldExpression, b, op: str) -> FieldExpression:
    if not isinstance(b, FieldExpression):
        raise TypeError("operand must be a FieldExpression (constants not yet supported)")
    return a._binary(b, op, vector=b.is_vector, complex_=_both(a, b))


def _vector_arith(a: FieldExpression, b, op: str) -> FieldExpression:
    if not isinstance(b, FieldExpression) or not b.is_vector:
        raise TypeError("vector +/- requires another vector expression")
    return a._binary(b, op, vector=True, complex_=_both(a, b))


def _vector_scale(a: FieldExpression, b, op: str) -> FieldExpression:
    if not isinstance(b, FieldExpression):
        raise TypeError("operand must be a FieldExpression (constants not yet supported)")
    if b.is_vector:
        raise TypeError("vector * vector is undefined; use dot() or cross()")
    return a._binary(b, op, vector=True, complex_=_both(a, b))


# ---------------------------------------------------------------------------
# binary free functions (do not read well as methods)
# ---------------------------------------------------------------------------
def dot(u: FieldExpression, v: FieldExpression) -> FieldExpression:
    """Vector dot product ``u·v`` (calculator ``Dot``) -> scalar.

    Algebraic dot, no conjugation (use ``v.conjugate()`` for an inner product).
    """
    if not (isinstance(u, FieldExpression) and u.is_vector and isinstance(v, FieldExpression) and v.is_vector):
        raise TypeError("dot() requires two vector expressions")
    return u._binary(v, "Dot", vector=False, complex_=_both(u, v))


def cross(u: FieldExpression, v: FieldExpression) -> FieldExpression:
    """Vector cross product ``u×v`` (calculator ``Cross``) -> vector."""
    if not (isinstance(u, FieldExpression) and u.is_vector and isinstance(v, FieldExpression) and v.is_vector):
        raise TypeError("cross() requires two vector expressions")
    return u._binary(v, "Cross", vector=True, complex_=_both(u, v))


# ---------------------------------------------------------------------------
# builder / entry point
# ---------------------------------------------------------------------------
class FieldExpressions(PyAedtBase):
    """Factory for typed Fields Calculator expressions, bound to a calculator.

    Obtain it through ``hfss.post.fields_calculator.expressions``. The factory
    methods seed the operation stack with a fundamental quantity, a previously
    defined named expression, or a constant, and return the matching typed
    expression to chain from.
    """

    def __init__(self, calculator) -> None:
        self._calculator = calculator
        self._design_type = [calculator.design_type] if calculator is not None else None

    def _seed(self, vector: bool, complex_: bool, ops: List[str]) -> FieldExpression:
        cls = _LEAF[(vector, complex_)]
        return cls(ops, calculator=self._calculator, design_type=self._design_type)

    def vector(self, quantity: str = "E", complex: bool = True) -> Union[VectorReal, VectorComplex]:
        """Start from a fundamental vector quantity (for example ``"E"``)."""
        return self._seed(True, complex, [f"Fundamental_Quantity('{quantity}')"])

    def scalar(self, quantity: str, complex: bool = True) -> Union[ScalarReal, ScalarComplex]:
        """Start from a fundamental scalar quantity."""
        return self._seed(False, complex, [f"Fundamental_Quantity('{quantity}')"])

    def named_expression(self, name: str, is_vector: bool = False, is_complex: bool = True) -> FieldExpression:
        """Start from a previously defined named expression."""
        return self._seed(is_vector, is_complex, [f"NameOfExpression('{name}')"])
