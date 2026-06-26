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

from __future__ import annotations

from typing import Literal
from typing import Sequence
from typing import overload

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError


class CalculatorGeometry(PyAedtBase):
    """Base class for a calculator geometry (line, surface, volume, point)."""

    enter_token: str = ""
    value_op: str = ""
    assignment_type: str = ""

    def __init__(self, assignment) -> None:
        # accept a name or any object exposing ``.name``
        self.assignment = getattr(assignment, "name", assignment)

    def _operations(self) -> list[str]:
        """Return the calculator tokens that push this geometry and its value."""
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
        design_type: list[str] | None = None,
        fields_type: list[str] | None = None,
        assignment_types: list[str] | None = None,
        primary_sweep: str = "Freq",
        solution_type: str = "",
    ) -> None:
        self._operations: list[str] = list(operations)
        self._calculator = calculator
        self._description = description
        self._design_type = design_type
        self._fields_type = fields_type or ["Fields"]
        self._assignment_types = list(assignment_types or [])
        self._primary_sweep = primary_sweep
        self._solution_type = solution_type

    # -- introspection -------------------------------------------------------
    @property
    def operations(self) -> list[str]:
        """Copy of the calculator operation stack this expression compiles to."""
        return list(self._operations)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} ops={len(self._operations)}>"

    def __len__(self) -> int:
        """Number of calculator operations this expression compiles to."""
        return len(self._operations)

    # -- builders ------------------------------------------------------------
    def _spawn(
        self,
        vector: bool,
        complex_: bool,
        extra_ops: Sequence[str],
        *,
        more_assignment_types: list[str] | None = None,
    ) -> "FieldExpression":
        """Build a derived expression with the appended operations."""
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
        """Append a unary calculator operation and return the typed result."""
        return self._spawn(vector, complex_, [f"Operation('{op}')"])

    def _binary(self, other: "FieldExpression", op: str, *, vector: bool, complex_: bool) -> "FieldExpression":
        """Combine with another expression through a binary calculator operation."""
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

    def _reduce(
        self,
        geometry: CalculatorGeometry,
        final_op: str,
        *,
        vector: bool = False,
        complex_: bool | None = None,
    ) -> "FieldExpression":
        """Geometry value + a final reduction op (Integrate / Maximum / ...)."""
        if complex_ is None:
            complex_ = self.is_complex
        ops = geometry._operations()
        if final_op:
            ops.append(f"Operation('{final_op}')")
        return self._spawn(vector, complex_, ops, more_assignment_types=[geometry.assignment_type])

    def _meta(self) -> dict:
        """Metadata kwargs to propagate when constructing sibling expressions."""
        return {
            "calculator": self._calculator,
            "description": self._description,
            "design_type": self._design_type,
            "fields_type": self._fields_type,
            "primary_sweep": self._primary_sweep,
            "solution_type": self._solution_type,
        }

    def __neg__(self) -> "FieldExpression":
        return self._unary("Neg", vector=self.is_vector, complex_=self.is_complex)

    # reflected operators so ``2 * E`` / ``1 - s`` work (constants on the left)
    def __radd__(self, other) -> "FieldExpression":
        return _to_expr(other, self).__add__(self)

    def __rmul__(self, other) -> "FieldExpression":
        return _to_expr(other, self).__mul__(self)

    def __rsub__(self, other) -> "FieldExpression":
        return _to_expr(other, self).__sub__(self)

    def __rtruediv__(self, other) -> "FieldExpression":
        return _to_expr(other, self).__truediv__(self)

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

    # -- well-formedness / size management -----------------------------------
    def stack_depth(self) -> int:
        """Net Fields Calculator stack depth after applying all operations.

        Simulates the reverse-Polish operation stack. A well-formed scalar or
        vector expression resolves to exactly ``1``. Raises
        :class:`~ansys.aedt.core.internal.errors.AEDTRuntimeError` if any
        operation would pop more registers than are available (malformed chain).
        """
        return _resolve_stack_depth(self._operations)

    def verify(self) -> "FieldExpression":
        """Validate that the operation chain is well-formed and return ``self``.

        Useful as a fast, local check before sending a long expression to AEDT,
        where an unbalanced or oversized operation stack can otherwise fail in
        confusing ways. Chainable: ``expr.verify().evaluate(...)``.
        """
        depth = self.stack_depth()
        if depth != 1:
            raise AEDTRuntimeError(
                f"expression does not resolve to a single result (stack depth {depth}); "
                "the operation chain is unbalanced"
            )
        return self

    @pyaedt_function_handler()
    def checkpoint(self, name: str | None = None) -> "FieldExpression":
        """Register this expression and return a single-token reference to it.

        Combining a sub-expression with itself duplicates its operations every
        time (for example ``dot(a, a)`` repeats ``a``), so heavy reuse can grow
        the operation stack very quickly and overflow the calculator. Checkpoint
        the sub-expression once, then continue from the returned reference, whose
        operation stack is a single ``NameOfExpression`` token. This mirrors the
        calculator's own named-expression / ``CopyToStack`` mechanism.

        Parameters
        ----------
        name : str, optional
            Named-expression name. A unique one is generated when not provided.

        Returns
        -------
        FieldExpression
            A new expression of the same kind referencing the registered name.

        Examples
        --------
        A repeated sub-expression such as ``(E.magnitude() * E.magnitude())`` can
        be checkpointed once and then reused through a single
        ``NameOfExpression(...)`` token, avoiding exponential growth of the
        operation stack.
        """
        calc = self._require_calculator()
        name = name or generate_unique_name("fcx")
        self.add(name)
        cls = _LEAF[(self.is_vector, self.is_complex)]
        return cls(
            [f"NameOfExpression('{name}')"],
            calculator=calc,
            description=self._description,
            design_type=self._design_type,
            fields_type=self._fields_type,
            primary_sweep=self._primary_sweep,
            solution_type=self._solution_type,
        )

    def _require_calculator(self):
        """Return the bound calculator, raising if the expression has none."""
        if self._calculator is None:
            raise AEDTRuntimeError(
                "this expression is not bound to a FieldsCalculator; build it from "
                "hfss.post.fields_calculator.expressions"
            )
        return self._calculator

    @pyaedt_function_handler()
    def add(self, name: str, assignment=None) -> str | bool:
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
        calc = self._require_calculator()
        self.verify()  # fail fast and clearly on a malformed/unbalanced stack
        return calc.add_expression(self.to_dict(name), assignment, name=name)

    @pyaedt_function_handler()
    def evaluate(
        self,
        name: str | None = None,
        setup: str | None = None,
        intrinsics: dict | None = None,
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
    def export(self, output_file: str, name: str | None = None, **kwargs):
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


class ScalarReal(FieldExpression):
    """A real scalar Fields Calculator quantity."""

    is_vector = False
    is_complex = False

    def absolute(self) -> "ScalarReal":
        """Absolute value ``|s|`` (calculator ``Abs``)."""
        return self._unary("Abs", vector=False, complex_=False)

    def smooth(self) -> "ScalarReal":
        """Smooth the quantity across the mesh (calculator ``Smooth``)."""
        return self._unary("Smooth", vector=False, complex_=False)

    def gradient(self) -> "VectorReal":
        """Gradient ``∇s`` (calculator ``Grad``)."""
        return self._unary("Grad", vector=True, complex_=False)

    # scalar math
    def sqrt(self) -> "ScalarReal":
        """Square root (calculator ``Sqrt``)."""
        return self._unary("Sqrt", vector=False, complex_=False)

    def power(self, exponent: float) -> "ScalarReal":
        """Raise to a (constant) power (calculator ``Pow``)."""
        return self._spawn(False, False, [f"Scalar_Constant({_num(exponent)})", "Operation('Pow')"])

    def __pow__(self, exponent: float) -> "ScalarReal":
        return self.power(exponent)

    def ln(self) -> "ScalarReal":
        """Natural logarithm (calculator ``ln``)."""
        return self._unary("ln", vector=False, complex_=False)

    def log10(self) -> "ScalarReal":
        """Base-10 logarithm (calculator ``log``)."""
        return self._unary("log", vector=False, complex_=False)

    def _math_func(self, name: str) -> "ScalarReal":
        """Apply a unary math function via the two-argument ``UMathFunc`` token."""
        return self._spawn(False, False, [f"Operation('UMathFunc', '{name}')"])

    def sin(self) -> "ScalarReal":
        """Sine (calculator trig ``Sin``)."""
        return self._math_func("Sin")

    def cos(self) -> "ScalarReal":
        """Cosine (calculator trig ``Cos``)."""
        return self._math_func("Cos")

    def tan(self) -> "ScalarReal":
        """Tangent (calculator trig ``Tan``)."""
        return self._math_func("Tan")

    def asin(self) -> "ScalarReal":
        """Arcsine (calculator trig ``Asin``)."""
        return self._math_func("Asin")

    def acos(self) -> "ScalarReal":
        """Arccosine (calculator trig ``Acos``)."""
        return self._math_func("Acos")

    def atan(self) -> "ScalarReal":
        """Arctangent (calculator trig ``Atan``)."""
        return self._math_func("Atan")

    def derivative(self, axis: str) -> "ScalarReal":
        """Partial derivative ``∂s/∂axis`` for ``axis`` in ``{"x", "y", "z"}``
        (calculator ``d/dx`` / ``d/dy`` / ``d/dz``).
        """
        a = axis.lower()
        if a not in ("x", "y", "z"):
            raise ValueError("axis must be 'x', 'y', or 'z'")
        return self._unary(f"d/d{a}", vector=False, complex_=False)

    # form a vector from this scalar (calculator ``Vec?``)
    def as_vector_x(self) -> "VectorReal":
        """Place this scalar in the x component of a vector (calculator ``VecX``)."""
        return self._unary("VecX", vector=True, complex_=False)

    def as_vector_y(self) -> "VectorReal":
        """Place this scalar in the y component of a vector (calculator ``VecY``)."""
        return self._unary("VecY", vector=True, complex_=False)

    def as_vector_z(self) -> "VectorReal":
        """Place this scalar in the z component of a vector (calculator ``VecZ``)."""
        return self._unary("VecZ", vector=True, complex_=False)

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

    def mean(self, over: CalculatorGeometry) -> "ScalarReal":
        """Mean over a geometry (calculator ``Mean``)."""
        return self._reduce(over, "Mean")

    def std(self, over: CalculatorGeometry) -> "ScalarReal":
        """Standard deviation over a geometry (calculator ``Std``)."""
        return self._reduce(over, "Std")

    def max_position(self, over: CalculatorGeometry) -> "VectorReal":
        """Position of the maximum over a geometry (calculator ``MaxPos``)."""
        return self._reduce(over, "MaxPos", vector=True, complex_=False)

    def min_position(self, over: CalculatorGeometry) -> "VectorReal":
        """Position of the minimum over a geometry (calculator ``MinPos``)."""
        return self._reduce(over, "MinPos", vector=True, complex_=False)

    def value(self, over: CalculatorGeometry) -> "ScalarReal":
        """Sample the quantity on a geometry without integrating."""
        return self._reduce(over, "")

    # build a complex scalar from this real part / imaginary part
    def as_complex_real(self) -> "ScalarComplex":
        """Use this real scalar as the real part of a complex number (calculator ``CmplxR``)."""
        return self._spawn(False, True, ["Operation('CmplxR')"])

    def as_complex_imag(self) -> "ScalarComplex":
        """Use this real scalar as the imaginary part of a complex number (calculator ``CmplxI``)."""
        return self._spawn(False, True, ["Operation('CmplxI')"])


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

    def phase(self) -> "ScalarReal":
        """Phase angle of the complex quantity (calculator ``CmplxPhase``)."""
        return self._unary("CmplxPhase", vector=False, complex_=False)

    def at_phase(self, phase_deg: float) -> "ScalarReal":
        """Real value at a given phase angle in degrees (calculator ``AtPhase``)."""
        return self._spawn(False, False, [f"Scalar_Constant({_num(phase_deg)})", "Operation('AtPhase')"])

    def conjugate(self) -> "ScalarComplex":
        """Complex conjugate (calculator ``Conj``)."""
        return self._unary("Conj", vector=False, complex_=True)

    def smooth(self) -> "ScalarComplex":
        """Smooth the quantity across the mesh (calculator ``Smooth``)."""
        return self._unary("Smooth", vector=False, complex_=True)

    def as_vector_x(self) -> "VectorComplex":
        """Place this scalar in the x component of a vector (calculator ``VecX``)."""
        return self._unary("VecX", vector=True, complex_=True)

    def as_vector_y(self) -> "VectorComplex":
        """Place this scalar in the y component of a vector (calculator ``VecY``)."""
        return self._unary("VecY", vector=True, complex_=True)

    def as_vector_z(self) -> "VectorComplex":
        """Place this scalar in the z component of a vector (calculator ``VecZ``)."""
        return self._unary("VecZ", vector=True, complex_=True)

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

    def mean(self, over: CalculatorGeometry) -> "ScalarComplex":
        """Mean over a geometry (calculator ``Mean``)."""
        return self._reduce(over, "Mean")

    def value(self, over: CalculatorGeometry) -> "ScalarComplex":
        """Sample the quantity on a geometry without integrating."""
        return self._reduce(over, "")


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

    def smooth(self) -> "VectorReal":
        """Smooth the quantity across the mesh (calculator ``Smooth``)."""
        return self._unary("Smooth", vector=True, complex_=False)

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

    def component_magnitude(self) -> "VectorReal":
        """Component-wise complex magnitude as a real vector (calculator ``CmplxMag``)."""
        return self._unary("CmplxMag", vector=True, complex_=False)

    def conjugate(self) -> "VectorComplex":
        """Complex conjugate, component-wise (calculator ``Conj``)."""
        return self._unary("Conj", vector=True, complex_=True)

    def smooth(self) -> "VectorComplex":
        """Smooth the quantity across the mesh (calculator ``Smooth``)."""
        return self._unary("Smooth", vector=True, complex_=True)

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


# Tokens that push a new register onto the calculator stack.
_PUSH_PREFIXES = (
    "Fundamental_Quantity",
    "NameOfExpression",
    "EnterLine",
    "EnterSurface",
    "EnterVolume",
    "EnterPoint",
    "EnterScalar",
    "EnterVector",
    "EnterComplex",
    "Scalar_Constant",
    "Complex_Constant",
    "Vector_Constant",
    "Scalar_Function",
)

#: Operations that consume two registers and push one (net -1). ``Pow`` consumes
#: the base and the exponent constant; ``AtPhase`` consumes the field and the
#: phase constant.
_BINARY_OPS = {"+", "-", "*", "/", "Dot", "Cross", "Pow", "AtPhase"}
#: Geometry value operations that consume the geometry register (net -1).
_VALUE_OPS = {"LineValue", "SurfaceValue", "VolumeValue", "PointValue"}
#: Operations that push a new register (net +1): ``Tangent`` / ``Normal`` push the
#: geometry's unit tangent / normal vector for a subsequent ``Dot``.
_PUSH_OPS = {"Tangent", "Normal"}


def _operation_name(token: str) -> str | None:
    """Return ``X`` from ``Operation('X')``; ``None`` if not an ``Operation``."""
    if token.startswith("Operation(") and "'" in token:
        return token.split("'")[1]
    return None


def _stack_effect(token: str) -> int:
    """Net change a single operation token makes to the calculator stack depth."""
    name = _operation_name(token)
    if name is not None:
        if name in _BINARY_OPS or name in _VALUE_OPS:
            return -1
        if name in _PUSH_OPS:
            return 1
        return 0  # unary operation: pop one, push one
    if token.startswith(_PUSH_PREFIXES):
        return 1
    return 0  # unknown token: assume neutral


def _resolve_stack_depth(operations: Sequence[str]) -> int:
    """Simulate the operation stack and return the final depth.

    Raises :class:`AEDTRuntimeError` if any operation would pop a register that
    is not there (an unbalanced / malformed chain), which is how an
    overly-stacked expression would otherwise fail confusingly in AEDT.
    """
    depth = 0
    for i, token in enumerate(operations):
        effect = _stack_effect(token)
        needed = 2 if effect < 0 else 0
        if depth < needed:
            raise AEDTRuntimeError(
                f"operation #{i} ('{token}') underflows the calculator stack "
                f"(depth {depth}); the expression is malformed"
            )
        depth += effect
    return depth


def _num(value) -> str:
    """Format a number the way AEDT serializes calculator constants (1, 2.5)."""
    return f"{value:g}"


def scalar_constant(value: float, **meta) -> ScalarReal:
    """A real scalar constant (calculator ``Scalar_Constant``)."""
    return ScalarReal([f"Scalar_Constant({_num(value)})"], **meta)


def complex_constant(real: float, imag: float, **meta) -> ScalarComplex:
    """A complex scalar constant (calculator ``Complex_Constant``)."""
    return ScalarComplex([f"Complex_Constant({_num(real)}, {_num(imag)})"], **meta)


def _to_expr(value, proto: FieldExpression) -> FieldExpression:
    """Coerce a Python number into a constant expression carrying proto metadata."""
    if isinstance(value, FieldExpression):
        return value
    if isinstance(value, bool):
        raise TypeError("bool is not a valid field-calculator operand")
    if isinstance(value, complex):
        return complex_constant(value.real, value.imag, **proto._meta())
    if isinstance(value, (int, float)):
        return scalar_constant(value, **proto._meta())
    raise TypeError(f"operand must be a FieldExpression or number, got {type(value).__name__}")


def _both(a: FieldExpression, b: FieldExpression) -> bool:
    """Return ``True`` when either operand is complex."""
    return a.is_complex or b.is_complex


def _scalar_arith(a: FieldExpression, b, op: str) -> FieldExpression:
    """Add or subtract a scalar with another scalar or a number."""
    b = _to_expr(b, a)
    if b.is_vector:
        raise TypeError("cannot add/subtract a scalar and a vector")
    return a._binary(b, op, vector=False, complex_=_both(a, b))


def _scalar_mul(a: FieldExpression, b, op: str) -> FieldExpression:
    """Multiply or divide starting from a scalar operand."""
    b = _to_expr(b, a)
    return a._binary(b, op, vector=b.is_vector, complex_=_both(a, b))


def _vector_arith(a: FieldExpression, b, op: str) -> FieldExpression:
    """Add or subtract two vector expressions."""
    if not isinstance(b, FieldExpression) or not b.is_vector:
        raise TypeError("vector +/- requires another vector expression")
    return a._binary(b, op, vector=True, complex_=_both(a, b))


def _vector_scale(a: FieldExpression, b, op: str) -> FieldExpression:
    """Scale a vector by a scalar operand or number."""
    b = _to_expr(b, a)
    if b.is_vector:
        raise TypeError("vector * vector is undefined; use dot() or cross()")
    return a._binary(b, op, vector=True, complex_=_both(a, b))


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


def cmplx(real: "ScalarReal", imag: "ScalarReal") -> "ScalarComplex":
    """Build a complex scalar from real and imaginary scalar parts.

    Mirrors the calculator ``CmplxR`` / ``CmplxI`` idiom (``real.as_complex_real()
    + imag.as_complex_imag()``).
    """
    if not (isinstance(real, ScalarReal) and isinstance(imag, ScalarReal)):
        raise TypeError("cmplx() requires two real scalar expressions")
    return real.as_complex_real() + imag.as_complex_imag()


class FieldExpressions(PyAedtBase):
    """Builder for AEDT Fields Calculator expressions.

    The AEDT Fields Calculator is driven by a stack of string operations (reverse
    Polish notation), for example ``Fundamental_Quantity('E')``, ``Operation('Real')``,
    ``Operation('Tangent')``, ``Operation('Dot')``. Assembling those strings by hand
    is error-prone and hides which operations are valid for a given quantity.

    This class wraps that operation grammar with four typed expression classes that
    mirror the calculator's register kinds:

    * :class:`ScalarReal`, a real scalar quantity.
    * :class:`ScalarComplex`, a complex scalar quantity.
    * :class:`VectorReal`, a real 3-vector quantity.
    * :class:`VectorComplex`, a complex 3-vector quantity.

    The builder wraps the calculator operations:

    * input: fundamental and named quantities; real / complex scalar constants;
      ``vector_constant``; ``function`` (a design variable / ``Scalar_Function``).
    * general: ``+ - * /`` and negation (numbers are accepted as operands, for
      example ``E * 2``); ``real`` / ``imaginary`` / ``conjugate`` / ``magnitude`` /
      ``component_magnitude`` / ``phase`` / ``at_phase`` / ``smooth`` / ``absolute``;
      ``as_complex_real`` / ``as_complex_imag`` and the :func:`cmplx` helper.
    * scalar: ``sqrt`` / ``power`` / ``ln`` / ``log10`` / ``sin`` / ``cos`` / ``tan``
      / ``asin`` / ``acos`` / ``atan`` / ``derivative`` / ``gradient`` and forming a
      vector with ``as_vector_x`` / ``as_vector_y`` / ``as_vector_z``.
    * vector: components ``scalar_x`` / ``scalar_y`` / ``scalar_z``; ``dot`` /
      ``cross`` / ``curl`` / ``divergence``; and the geometry unit vectors
      ``FieldExpressions.tangent`` / ``FieldExpressions.normal`` (push a unit vector
      to dot a field against, for tangential / flux quantities).
    * output: ``integrate`` / ``maximum`` / ``minimum`` / ``mean`` / ``std`` /
      ``value`` / ``max_position`` / ``min_position`` over a :class:`Line`,
      :class:`Surface`, or :class:`Volume`.

    Examples
    --------
    >>> fx = FieldExpressions(calculator=None)
    >>> e_vector = fx.vector("E")
    >>> energy = (e_vector.magnitude() * e_vector.magnitude()).integrate(Surface("MySheet"))
    >>> energy.operations[-3:]
    ["EnterSurface('MySheet')", "Operation('SurfaceValue')", "Operation('Integrate')"]

    """

    def __init__(self, calculator) -> None:
        """Bind the expression builder to a Fields Calculator instance.

        Parameters
        ----------
        calculator : FieldsCalculator or None
            Calculator used later to register, evaluate, or export expressions.
            When ``None``, expressions can still be composed and validated
            locally, but not materialized into AEDT.
        """
        self._calculator = calculator
        self._design_type = [calculator.design_type] if calculator is not None else None

    @overload
    def _seed(self, vector: Literal[False], complex_: Literal[False], ops: Sequence[str]) -> ScalarReal: ...

    @overload
    def _seed(self, vector: Literal[False], complex_: Literal[True], ops: Sequence[str]) -> ScalarComplex: ...

    @overload
    def _seed(self, vector: Literal[True], complex_: Literal[False], ops: Sequence[str]) -> VectorReal: ...

    @overload
    def _seed(self, vector: Literal[True], complex_: Literal[True], ops: Sequence[str]) -> VectorComplex: ...

    @overload
    def _seed(self, vector: bool, complex_: bool, ops: Sequence[str]) -> FieldExpression: ...

    def _seed(self, vector: bool, complex_: bool, ops: Sequence[str]) -> FieldExpression:
        """Create a typed root expression bound to this builder.

        Parameters
        ----------
        vector : bool
            Whether the seeded expression represents a vector quantity.
        complex_ : bool
            Whether the seeded expression represents a complex quantity.
        ops : Sequence[str]
            Initial calculator-operation tokens for the expression stack.

        Returns
        -------
        FieldExpression
            Concrete typed expression instance selected from the internal leaf
            registry.
        """
        cls = _LEAF[(vector, complex_)]
        return cls(ops, calculator=self._calculator, design_type=self._design_type)

    def vector(self, quantity: str = "E", is_complex: bool = True) -> VectorReal | VectorComplex:
        """Start from a fundamental vector quantity.

        Parameters
        ----------
        quantity : str, optional
            AEDT field quantity name, for example ``"E"`` or ``"H"``.
        is_complex : bool, optional
            Whether the quantity should be treated as complex. The default is
            ``True``, which matches most frequency-domain vector fields.

        Returns
        -------
        VectorReal | VectorComplex
            Typed vector expression seeded with
            ``Fundamental_Quantity('<quantity>')``.

        Examples
        --------
        >>> fx = FieldExpressions(calculator=None)
        >>> e_vector = fx.vector("E")
        >>> e_mag = e_vector.magnitude()
        >>> e_mag.operations
        ["Fundamental_Quantity('E')", "Operation('Mag')"]
        """
        if is_complex:
            return self._seed(True, True, [f"Fundamental_Quantity('{quantity}')"])
        return self._seed(True, False, [f"Fundamental_Quantity('{quantity}')"])

    def scalar(self, quantity: str, is_complex: bool = True) -> ScalarReal | ScalarComplex:
        """Start from a fundamental scalar quantity.

        Parameters
        ----------
        quantity : str
            AEDT scalar quantity name.
        is_complex : bool, optional
            Whether the quantity should be treated as complex.

        Returns
        -------
        ScalarReal | ScalarComplex
            Typed scalar expression seeded with
            ``Fundamental_Quantity('<quantity>')``.
        """
        if is_complex:
            return self._seed(False, True, [f"Fundamental_Quantity('{quantity}')"])
        return self._seed(False, False, [f"Fundamental_Quantity('{quantity}')"])

    def named_expression(self, name: str, is_vector: bool = False, is_complex: bool = True) -> FieldExpression:
        """Start from a previously defined named expression.

        Parameters
        ----------
        name : str
            Existing AEDT named-expression name.
        is_vector : bool, optional
            Whether the named expression returns a vector quantity.
        is_complex : bool, optional
            Whether the named expression returns a complex quantity.

        Returns
        -------
        FieldExpression
            Typed expression seeded with ``NameOfExpression('<name>')``.
        """
        return self._seed(is_vector, is_complex, [f"NameOfExpression('{name}')"])

    def scalar_constant(self, value: float) -> ScalarReal:
        """Create a real scalar constant.

        Parameters
        ----------
        value : float
            Constant value to push on the calculator stack.

        Returns
        -------
        ScalarReal
            Real scalar expression seeded with ``Scalar_Constant``.
        """
        return self._seed(False, False, [f"Scalar_Constant({_num(value)})"])

    def complex_constant(self, real: float, imag: float) -> ScalarComplex:
        """Create a complex scalar constant.

        Parameters
        ----------
        real : float
            Real part of the constant.
        imag : float
            Imaginary part of the constant.

        Returns
        -------
        ScalarComplex
            Complex scalar expression seeded with ``Complex_Constant``.
        """
        return self._seed(False, True, [f"Complex_Constant({_num(real)}, {_num(imag)})"])

    def vector_constant(self, x: float, y: float, z: float) -> VectorReal:
        """Create a constant real vector.

        Parameters
        ----------
        x : float
            X component.
        y : float
            Y component.
        z : float
            Z component.

        Returns
        -------
        VectorReal
            Real vector expression seeded with ``Vector_Constant``.
        """
        return self._seed(True, False, [f"Vector_Constant({_num(x)}, {_num(y)}, {_num(z)})"])

    def function(self, name: str) -> ScalarReal:
        """Create a scalar expression from a design variable or function.

        Parameters
        ----------
        name : str
            Name resolved by AEDT through ``Scalar_Function``, typically a
            design variable or calculator function token.

        Returns
        -------
        ScalarReal
            Real scalar expression seeded with ``Scalar_Function``.
        """
        return self._seed(False, False, [f"Scalar_Function(FuncValue='{name}')"])

    def tangent(self) -> VectorReal:
        """Push the geometry unit tangent vector.

        Returns
        -------
        VectorReal
            Real vector expression seeded with ``Operation('Tangent')`` for
            use in tangential projections such as ``dot(field, fx.tangent())``.
        """
        return self._seed(True, False, ["Operation('Tangent')"])

    def normal(self) -> VectorReal:
        """Push the geometry unit normal vector.

        Returns
        -------
        VectorReal
            Real vector expression seeded with ``Operation('Normal')`` for use
            in normal-flux or projection calculations.
        """
        return self._seed(True, False, ["Operation('Normal')"])
