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

from typing import Any
from typing import Literal
from typing import Sequence
from typing import overload

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError

# Tokens that push a new register onto the calculator stack.
PUSH_PREFIXES = (
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
BINARY_OPS = {"+", "-", "*", "/", "Dot", "Cross", "Pow", "AtPhase"}
#: Geometry value operations that consume the geometry register (net -1).
VALUE_OPS = {"LineValue", "SurfaceValue", "VolumeValue", "PointValue"}
#: Operations that push a new register (net +1): ``Tangent`` / ``Normal`` push the
#: geometry's unit tangent / normal vector for a subsequent ``Dot``.
PUSH_OPS = {"Tangent", "Normal"}


class CalculatorGeometry(PyAedtBase):
    """Base class for a calculator geometry (line, surface, volume, point).

    Parameters
    ----------
    assignment : str or object
        Geometry name, or any object exposing a ``name`` attribute.

    Examples
    --------
    Create a geometry entry sequence manually.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import CalculatorGeometry
    >>> clc = CalculatorGeometry("my_line")
    >>> clc.calculator_token = "EnterLine"
    >>> clc.value_op = "LineValue"
    >>> clc.assignment_type = "Line"
    >>> clc.assignment
    'my_line'

    """

    calculator_token: str = ""
    value_op: str = ""
    assignment_type: str = ""

    def __init__(self, assignment: str | Any) -> None:
        self.assignment = getattr(assignment, "name", assignment)

    def _operations(self) -> list[str]:
        """Calculator entries that push this geometry and its value.

        Returns
        -------
        list of str
            Calculator operation entries that push this geometry and its value.

        Examples
        --------
        Build the calculator stack fragment for a line geometry.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import CalculatorGeometry
        >>> clc = CalculatorGeometry("my_line")
        >>> clc.calculator_token = "EnterLine"
        >>> clc.value_op = "LineValue"
        >>> clc.assignment_type = "Line"
        >>> ops = clc._operations()
        >>> ops
        ["EnterLine('my_line')", "Operation('LineValue')"]

        """
        ops = [f"{self.calculator_token}('{self.assignment}')"]
        if self.value_op:
            ops.append(f"Operation('{self.value_op}')")
        return ops


class Line(CalculatorGeometry):
    """A polyline domain (``EnterLine`` and ``LineValue``).

    Examples
    --------
    Create a line geometry for later reductions.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import Line
    >>> clc = Line("my_line")
    >>> clc.assignment
    'my_line'

    """

    calculator_token = "EnterLine"
    value_op = "LineValue"
    assignment_type = "Line"


class Surface(CalculatorGeometry):
    """A surface, sheet, or face domain (``EnterSurface`` and ``SurfaceValue``).

    Examples
    --------
    Create a surface geometry for area-based reductions.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import Surface
    >>> clc = Surface("my_surface")
    >>> clc.assignment_type
    'Surface'

    """

    calculator_token = "EnterSurface"
    value_op = "SurfaceValue"
    assignment_type = "Surface"


class Volume(CalculatorGeometry):
    """A volume, or solid domain (``EnterVolume`` and ``VolumeValue``).

    Examples
    --------
    Create a volume geometry for volumetric integrations.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import Volume
    >>> clc = Volume("my_solid")
    >>> clc.value_op
    'VolumeValue'

    """

    calculator_token = "EnterVolume"
    value_op = "VolumeValue"
    assignment_type = "Volume"


class FieldExpression(PyAedtBase):
    """Base class for a typed Fields Calculator expression.

    Holds the accumulated list of calculator operation entries plus the metadata
    needed to register the expression. Not instantiated directly, use the
    factory methods on :class:`FieldExpressions`.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
    >>> fx = FieldExpressions(calculator=None)
    >>> expr = fx.vector("E").magnitude()
    >>> expr.operations
    ["Fundamental_Quantity('E')", "Operation('Mag')"]

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

    @property
    def operations(self) -> list[str]:
        """Copy of the calculator operation stack this expression compiles to.

        Returns
        -------
        list of str
            Copy of the reverse-Polish calculator entries for the expression.

        Examples
        --------
        Inspect the generated stack entries for a magnitude expression.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").magnitude().operations
        ["Fundamental_Quantity('E')", "Operation('Mag')"]

        """
        return list(self._operations)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} ops={len(self._operations)}>"

    def __len__(self) -> int:
        """Number of calculator operations this expression compiles to.

        Returns
        -------
        int
            Number of entries in the compiled calculator stack.

        Examples
        --------
        Count the entries in a simple vector expression.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> len(fx.vector("E").magnitude())
        2

        """
        return len(self._operations)

    def _spawn(
        self,
        vector: bool,
        is_complex: bool,
        extra_operations: Sequence[str],
        *,
        more_assignment_types: list[str] | None = None,
    ) -> FieldExpression:
        """Build a derived expression with appended calculator operations.

        Parameters
        ----------
        vector : bool
            Whether the derived expression is vector-valued.
        is_complex : bool
            Whether the derived expression is complex-valued.
        extra_operations : Sequence[str]
            Operations appended to the current stack.
        more_assignment_types : list[str], optional
            Additional assignment types propagated to the derived expression.

        Returns
        -------
        FieldExpression
            Derived typed expression containing the appended operations.

        Examples
        --------
        Append a magnitude operation to a vector expression.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> expr = fx.vector("E")._spawn(False, False, ["Operation('Mag')"])
        >>> expr.operations
        ["Fundamental_Quantity('E')", "Operation('Mag')"]

        """
        cls = LEAF[(vector, is_complex)]
        ats = self._assignment_types + list(more_assignment_types or [])
        return cls(
            self._operations + list(extra_operations),
            calculator=self._calculator,
            description=self._description,
            design_type=self._design_type,
            fields_type=self._fields_type,
            assignment_types=ats,
            primary_sweep=self._primary_sweep,
            solution_type=self._solution_type,
        )

    def _unary(self, operation: str, *, vector: bool, is_complex: bool) -> FieldExpression:
        """Append a unary calculator operation and return the typed result.

        Parameters
        ----------
        op : str
            Calculator operation name.
        vector : bool
            Whether the result is vector-valued.
        is_complex : bool
            Whether the result is complex-valued.

        Returns
        -------
        FieldExpression
            Derived expression with the unary operation appended.

        Examples
        --------
        Apply the ``Mag`` calculator operation to a vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> expr = fx.vector("E")._unary("Mag", vector=False, is_complex=False)
        >>> expr.operations[-1]
        "Operation('Mag')"

        """
        return self._spawn(vector, is_complex, [f"Operation('{operation}')"])

    def _binary(
        self, expression: FieldExpression, operation: str, *, vector: bool, is_complex: bool
    ) -> FieldExpression:
        """Combine with another expression through a binary calculator operation.

        Parameters
        ----------
        expression : FieldExpression
            Right-hand expression to combine with.
        operation : str
            Calculator binary operation name.
        vector : bool
            Whether the result is vector-valued.
        is_complex : bool
            Whether the result is complex-valued.

        Returns
        -------
        FieldExpression
            Combined expression with both stacks concatenated in RPN order.

        Examples
        --------
        Concatenate two expressions through addition.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> left = fx.scalar("Phi", is_complex=False)
        >>> expr = left._binary(fx.scalar_constant(2.0), "+", vector=False, is_complex=False)
        >>> expr.operations[-1]
        "Operation('+')"

        """
        if not isinstance(expression, FieldExpression):
            raise TypeError("operand must be a FieldExpression")
        cls = LEAF[(vector, is_complex)]
        return cls(
            self._operations + expression._operations + [f"Operation('{operation}')"],
            calculator=self._calculator or expression._calculator,
            description=self._description,
            design_type=self._design_type or expression._design_type,
            fields_type=self._fields_type,
            assignment_types=self._assignment_types + expression._assignment_types,
            primary_sweep=self._primary_sweep,
            solution_type=self._solution_type,
        )

    def _reduce(
        self,
        geometry: CalculatorGeometry,
        final_operation: str,
        *,
        vector: bool = False,
        is_complex: bool | None = None,
    ) -> FieldExpression:
        """Append a geometry evaluation and optional reduction operation.

        Parameters
        ----------
        geometry : CalculatorGeometry
            Geometry to evaluate on.
        final_operation : str
            Final reduction operation, such as ``"Integrate"`` or ``"Mean"``.
        vector : bool, optional
            Whether the reduced result is vector-valued.
        is_complex : bool, optional
            Whether the reduced result is complex-valued. When ``None``, the
            current expression complexity is preserved.

        Returns
        -------
        FieldExpression
            Expression extended with the geometry stack and optional reduction.

        Examples
        --------
        Integrate a scalar field over a line.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Line
        >>> fx = FieldExpressions(calculator=None)
        >>> expr = fx.scalar("Phi", is_complex=False)._reduce(Line("Polyline1"), "Integrate")
        >>> expr.operations[-3:]
        ["EnterLine('Polyline1')", "Operation('LineValue')", "Operation('Integrate')"]

        """
        if is_complex is None:
            is_complex = self.is_complex
        ops = geometry._operations()
        if final_operation:
            ops.append(f"Operation('{final_operation}')")
        return self._spawn(vector, is_complex, ops, more_assignment_types=[geometry.assignment_type])

    def _meta(self) -> dict:
        """Metadata keyword arguments propagated to sibling expressions.

        Returns
        -------
        dict
            Metadata copied into derived expressions.

        Examples
        --------
        Retrieve the metadata propagated by an expression builder.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> meta = fx.scalar("Phi", is_complex=False)._meta()
        >>> sorted(meta)
        ['calculator', 'description', 'design_type', 'fields_type', 'primary_sweep', 'solution_type']

        """
        return {
            "calculator": self._calculator,
            "description": self._description,
            "design_type": self._design_type,
            "fields_type": self._fields_type,
            "primary_sweep": self._primary_sweep,
            "solution_type": self._solution_type,
        }

    def __neg__(self) -> FieldExpression:
        return self._unary("Neg", vector=self.is_vector, is_complex=self.is_complex)

    def __radd__(self, other) -> FieldExpression:
        return _to_expr(other, self).__add__(self)

    def __rmul__(self, other) -> FieldExpression:
        return _to_expr(other, self).__mul__(self)

    def __rsub__(self, other) -> FieldExpression:
        return _to_expr(other, self).__sub__(self)

    def __rtruediv__(self, other) -> FieldExpression:
        return _to_expr(other, self).__truediv__(self)

    def to_dict(self, name: str, assignment: str = "") -> dict:
        """Compile this expression to a Fields Calculator expression dictionary.

        Parameters
        ----------
        name : str
            Name assigned to the compiled expression.
        assignment : str, optional
            Assignment stored in the exported dictionary.

        Returns
        -------
        dict
            Dictionary payload accepted by :class:`FieldsCalculator`.

        Examples
        --------
        Serialize a magnitude expression to the calculator schema.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> data = fx.vector("E").magnitude().to_dict("e_mag")
        >>> data["name"], data["operations"][-1]
        ('e_mag', "Operation('Mag')")

        """
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

    def stack_depth(self) -> int:
        """Net Fields Calculator stack depth after applying all operations.

        Simulates the reverse-Polish operation stack. A well-formed scalar or
        vector expression resolves to exactly ``1``. Raises
        :class:`~ansys.aedt.core.internal.errors.AEDTRuntimeError` if any
        operation would pop more registers than are available (malformed chain).

        Returns
        -------
        int
            Final stack depth after simulating all operations.

        Examples
        --------
        Check that a simple expression resolves to one value.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").magnitude().stack_depth()
        1

        """
        return _resolve_stack_depth(self._operations)

    def verify(self) -> FieldExpression:
        """Validate that the operation chain is well-formed and return ``self``.

        Useful as a fast, local check before sending a long expression to AEDT,
        where an unbalanced or oversized operation stack can otherwise fail in
        confusing ways. Chainable: ``expr.verify().evaluate(...)``.

        Returns
        -------
        FieldExpression
            The same expression instance when the stack is balanced.

        Examples
        --------
        Validate an expression before materializing it.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> expr = fx.vector("E").magnitude().verify()
        >>> expr.operations[-1]
        "Operation('Mag')"

        """
        depth = self.stack_depth()
        if depth != 1:
            raise AEDTRuntimeError(
                f"expression does not resolve to a single result (stack depth {depth}); "
                "the operation chain is unbalanced"
            )
        return self

    @pyaedt_function_handler()
    def checkpoint(self, name: str | None = None) -> FieldExpression:
        """Register this expression and return a single-entry reference to it.

        Combining a sub-expression with itself duplicates its operations every
        time (for example ``dot(a, a)`` repeats ``a``), so heavy reuse can grow
        the operation stack very quickly and overflow the calculator. Checkpoint
        the sub-expression once, then continue from the returned reference, whose
        operation stack is a single ``NameOfExpression`` entry. This mirrors the
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
        Reuse a named sub-expression through a single entry.

        >>> calc = type(
        ...     "Calc",
        ...     (),
        ...     {
        ...         "design_type": "HFSS",
        ...         "add_expression": staticmethod(lambda *args, **kwargs: kwargs["name"]),
        ...     },
        ... )()
        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calc)
        >>> ref = fx.vector("E").magnitude().checkpoint("e_mag")
        >>> ref.operations
        ["NameOfExpression('e_mag')"]

        """
        calc = self._require_calculator()
        name = name or generate_unique_name("fcx")
        self.add(name)
        cls = LEAF[(self.is_vector, self.is_complex)]
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
        """Return the bound calculator, raising if the expression has none.

        Returns
        -------
        FieldsCalculator
            Calculator bound to the expression.

        Examples
        --------
        Access the calculator attached by the builder.

        >>> calc = type("Calc", (), {"design_type": "HFSS"})()
        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calc)
        >>> fx.vector("E")._require_calculator() is calc
        True

        """
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

        Examples
        --------
        Register a compiled expression through the bound calculator.

        >>> calc = type(
        ...     "Calc",
        ...     (),
        ...     {
        ...         "design_type": "HFSS",
        ...         "add_expression": staticmethod(lambda *args, **kwargs: kwargs["name"]),
        ...     },
        ... )()
        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calc)
        >>> fx.vector("E").magnitude().add("e_mag")
        'e_mag'

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

        Examples
        --------
        Register an expression and forward evaluation to the calculator.

        >>> calc = type(
        ...     "Calc",
        ...     (),
        ...     {
        ...         "design_type": "HFSS",
        ...         "add_expression": staticmethod(lambda *args, **kwargs: kwargs["name"]),
        ...         "evaluate": staticmethod(lambda *args, **kwargs: 3.14),
        ...     },
        ... )()
        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calc)
        >>> fx.vector("E").magnitude().evaluate(name="e_mag")
        3.14

        """
        calc = self._require_calculator()
        name = name or generate_unique_name("fcx")
        self.add(name, assignment)
        return calc.evaluate(name, setup=setup, intrinsics=intrinsics)

    @pyaedt_function_handler()
    def export(self, output_file: str | None, name: str | None = None, **kwargs) -> str | bool:
        """Register and export this expression to a field file.

        Extra keyword arguments are forwarded to
        :meth:`FieldsCalculator.export`(``solution``, ``sample_points``,
        ``grid_type``, ``intrinsics`` ...). ``is_vector`` is set automatically.

        Parameters
        ----------
        output_file : str, optional
            Full path and name to save the file to.
            The default is ``None``, in which case the file is exported
            to the working directory.
        name : str, optional
            Solution name, for example ``"Setup1 : LastAdaptive"``.

        Returns
        -------
        bool or str
            The path to the exported field file when successful, ``False`` when failed.

        Examples
        --------
        Export a field quantity through the bound calculator.

        >>> calc = type(
        ...     "Calc",
        ...     (),
        ...     {
        ...         "design_type": "HFSS",
        ...         "add_expression": staticmethod(lambda *args, **kwargs: kwargs["name"]),
        ...         "export": staticmethod(lambda **kwargs: kwargs["output_file"]),
        ...     },
        ... )()
        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calc)
        >>> fx.vector("E").export("out.fld", name="vec_e")
        'out.fld'

        """
        calc = self._require_calculator()
        name = name or generate_unique_name("fcx")
        self.add(name)
        kwargs.setdefault("is_vector", self.is_vector)
        return calc.export(quantity=name, output_file=output_file, **kwargs)


class ScalarReal(FieldExpression):
    """A real scalar Fields Calculator quantity.

    Examples
    --------
    Start from a real scalar quantity and apply scalar operations.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
    >>> fx = FieldExpressions(calculator=None)
    >>> phi = fx.scalar("Phi", is_complex=False)
    >>> phi.operations
    ["Fundamental_Quantity('Phi')"]

    """

    is_vector = False
    is_complex = False

    def absolute(self) -> ScalarReal:
        """Absolute value ``|s|`` (calculator ``Abs``).

        Returns
        -------
        ScalarReal
            Real scalar expression with ``Operation('Abs')`` appended.

        Examples
        --------
        Take the absolute value of a scalar expression.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).absolute().operations[-1]
        "Operation('Abs')"

        """
        return self._unary("Abs", vector=False, is_complex=False)

    def smooth(self) -> ScalarReal:
        """Smooth the quantity across the mesh (calculator ``Smooth``).

        Returns
        -------
        ScalarReal
            Real scalar expression with mesh smoothing applied.

        Examples
        --------
        Smooth a real scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).smooth().operations[-1]
        "Operation('Smooth')"

        """
        return self._unary("Smooth", vector=False, is_complex=False)

    def gradient(self) -> VectorReal:
        """Gradient (calculator ``Grad``).

        Returns
        -------
        VectorReal
            Real vector expression representing the scalar gradient.

        Examples
        --------
        Convert a real scalar field into its gradient vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).gradient().operations[-1]
        "Operation('Grad')"

        """
        return self._unary("Grad", vector=True, is_complex=False)

    # Scalar math
    def sqrt(self) -> ScalarReal:
        """Square root (calculator ``Sqrt``).

        Returns
        -------
        ScalarReal
            Real scalar expression with ``Operation('Sqrt')`` appended.

        Examples
        --------
        Take the square root of a real scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).sqrt().operations[-1]
        "Operation('Sqrt')"

        """
        return self._unary("Sqrt", vector=False, is_complex=False)

    def power(self, exponent: float) -> ScalarReal:
        """Raise to a constant power (calculator ``Pow``).

        Parameters
        ----------
        exponent : float
            Exponent pushed as a scalar constant before ``Pow``.

        Returns
        -------
        ScalarReal
            Real scalar expression raised to the requested exponent.

        Examples
        --------
        Square a scalar quantity.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).power(2).operations[-2:]
        ['Scalar_Constant(2)', "Operation('Pow')"]

        """
        return self._spawn(False, False, [f"Scalar_Constant({_num(exponent)})", "Operation('Pow')"])

    def __pow__(self, exponent: float) -> ScalarReal:
        return self.power(exponent)

    def ln(self) -> ScalarReal:
        """Natural logarithm (calculator ``ln``).

        Returns
        -------
        ScalarReal
            Real scalar expression with ``Operation('ln')`` appended.

        Examples
        --------
        Apply the natural logarithm to a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).ln().operations[-1]
        "Operation('ln')"

        """
        return self._unary("ln", vector=False, is_complex=False)

    def log10(self) -> ScalarReal:
        """Base-10 logarithm (calculator ``log``).

        Returns
        -------
        ScalarReal
            Real scalar expression with ``Operation('log')`` appended.

        Examples
        --------
        Apply the base-10 logarithm to a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).log10().operations[-1]
        "Operation('log')"

        """
        return self._unary("log", vector=False, is_complex=False)

    def _math_func(self, name: str) -> ScalarReal:
        """Apply a unary math function via ``UMathFunc``.

        Parameters
        ----------
        name : str
            AEDT unary math-function name, such as ``"Sin"`` or ``"Cos"``.

        Returns
        -------
        ScalarReal
            Real scalar expression with the math-function operation appended.

        Examples
        --------
        Append the sine calculator helper explicitly.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False)._math_func("Sin").operations[-1]
        "Operation('UMathFunc', 'Sin')"

        """
        return self._spawn(False, False, [f"Operation('UMathFunc', '{name}')"])

    def sin(self) -> ScalarReal:
        """Sine (calculator trig ``Sin``).

        Returns
        -------
        ScalarReal
            Real scalar expression with a sine transformation applied.

        Examples
        --------
        Compute the sine of a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).sin().operations[-1]
        "Operation('UMathFunc', 'Sin')"

        """
        return self._math_func("Sin")

    def cos(self) -> ScalarReal:
        """Cosine (calculator trig ``Cos``).

        Returns
        -------
        ScalarReal
            Real scalar expression with a cosine transformation applied.

        Examples
        --------
        Compute the cosine of a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).cos().operations[-1]
        "Operation('UMathFunc', 'Cos')"

        """
        return self._math_func("Cos")

    def tan(self) -> ScalarReal:
        """Tangent (calculator trig ``Tan``).

        Returns
        -------
        ScalarReal
            Real scalar expression with a tangent transformation applied.

        Examples
        --------
        Compute the tangent of a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).tan().operations[-1]
        "Operation('UMathFunc', 'Tan')"

        """
        return self._math_func("Tan")

    def asin(self) -> ScalarReal:
        """Arcsine (calculator trig ``Asin``).

        Returns
        -------
        ScalarReal
            Real scalar expression with an arcsine transformation applied.

        Examples
        --------
        Compute the arcsine of a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).asin().operations[-1]
        "Operation('UMathFunc', 'Asin')"

        """
        return self._math_func("Asin")

    def acos(self) -> ScalarReal:
        """Arccosine (calculator trig ``Acos``).

        Returns
        -------
        ScalarReal
            Real scalar expression with an arccosine transformation applied.

        Examples
        --------
        Compute the arccosine of a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).acos().operations[-1]
        "Operation('UMathFunc', 'Acos')"

        """
        return self._math_func("Acos")

    def atan(self) -> ScalarReal:
        """Arctangent (calculator trig ``Atan``).

        Returns
        -------
        ScalarReal
            Real scalar expression with an arctangent transformation applied.

        Examples
        --------
        Compute the arctangent of a scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).atan().operations[-1]
        "Operation('UMathFunc', 'Atan')"

        """
        return self._math_func("Atan")

    def derivative(self, axis: str) -> ScalarReal:
        """Partial derivative ``∂s/∂axis`` for ``axis`` in ``{"x", "y", "z"}``
        (calculator ``d/dx`` / ``d/dy`` / ``d/dz``).

        Parameters
        ----------
        axis : str
            Cartesian axis along which the partial derivative is taken.

        Returns
        -------
        ScalarReal
            Real scalar derivative with the corresponding calculator entry.

        Examples
        --------
        Differentiate a scalar field along the x axis.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).derivative("x").operations[-1]
        "Operation('d/dx')"

        """
        a = axis.lower()
        if a not in ("x", "y", "z"):
            raise ValueError("axis must be 'x', 'y', or 'z'")
        return self._unary(f"d/d{a}", vector=False, is_complex=False)

    # form a vector from this scalar (calculator ``Vec?``)
    def as_vector_x(self) -> VectorReal:
        """Place this scalar in the x component of a vector (calculator ``VecX``).

        Returns
        -------
        VectorReal
            Real vector expression with the scalar in the x component.

        Examples
        --------
        Embed a scalar field into the x component of a vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).as_vector_x().operations[-1]
        "Operation('VecX')"

        """
        return self._unary("VecX", vector=True, is_complex=False)

    def as_vector_y(self) -> VectorReal:
        """Place this scalar in the y component of a vector (calculator ``VecY``).

        Returns
        -------
        VectorReal
            Real vector expression with the scalar in the y component.

        Examples
        --------
        Embed a scalar field into the y component of a vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).as_vector_y().operations[-1]
        "Operation('VecY')"

        """
        return self._unary("VecY", vector=True, is_complex=False)

    def as_vector_z(self) -> VectorReal:
        """Place this scalar in the z component of a vector (calculator ``VecZ``).

        Returns
        -------
        VectorReal
            Real vector expression with the scalar in the z component.

        Examples
        --------
        Embed a scalar field into the z component of a vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).as_vector_z().operations[-1]
        "Operation('VecZ')"

        """
        return self._unary("VecZ", vector=True, is_complex=False)

    # arithmetic
    def __add__(self, other) -> ScalarReal:
        return _scalar_arith(self, other, "+")

    def __sub__(self, other) -> ScalarReal:
        return _scalar_arith(self, other, "-")

    def __mul__(self, other) -> FieldExpression:
        return _scalar_mul(self, other, "*")

    def __truediv__(self, other) -> FieldExpression:
        return _scalar_mul(self, other, "/")

    # geometry reductions
    def integrate(self, over: CalculatorGeometry) -> ScalarReal:
        """Integrate over a geometry ``∫ s dΩ`` (calculator ``Integrate``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the integration.

        Returns
        -------
        ScalarReal
            Real scalar expression with the integration reduction appended.

        Examples
        --------
        Integrate a scalar field over a line.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Line
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).integrate(Line("Polyline1")).operations[-1]
        "Operation('Integrate')"

        """
        return self._reduce(over, "Integrate")

    def maximum(self, over: CalculatorGeometry) -> ScalarReal:
        """Maximum over a geometry (calculator ``Maximum``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        ScalarReal
            Real scalar expression reduced with ``Maximum``.

        Examples
        --------
        Compute the maximum on a surface.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Surface
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).maximum(Surface("Sheet1")).operations[-1]
        "Operation('Maximum')"

        """
        return self._reduce(over, "Maximum")

    def minimum(self, over: CalculatorGeometry) -> ScalarReal:
        """Minimum over a geometry (calculator ``Minimum``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        ScalarReal
            Real scalar expression reduced with ``Minimum``.

        Examples
        --------
        Compute the minimum on a surface.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Surface
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).minimum(Surface("Sheet1")).operations[-1]
        "Operation('Minimum')"

        """
        return self._reduce(over, "Minimum")

    def mean(self, over: CalculatorGeometry) -> ScalarReal:
        """Mean over a geometry (calculator ``Mean``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        ScalarReal
            Real scalar expression reduced with ``Mean``.

        Examples
        --------
        Compute the mean value on a volume.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Volume
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).mean(Volume("Box1")).operations[-1]
        "Operation('Mean')"

        """
        return self._reduce(over, "Mean")

    def std(self, over: CalculatorGeometry) -> ScalarReal:
        """Standard deviation over a geometry (calculator ``Std``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        ScalarReal
            Real scalar expression reduced with ``Std``.

        Examples
        --------
        Compute the standard deviation on a volume.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Volume
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).std(Volume("Box1")).operations[-1]
        "Operation('Std')"

        """
        return self._reduce(over, "Std")

    def max_position(self, over: CalculatorGeometry) -> VectorReal:
        """Position of the maximum over a geometry (calculator ``MaxPos``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        VectorReal
            Real vector expression locating the maximum position.

        Examples
        --------
        Find the maximum position on a surface.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Surface
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).max_position(Surface("Sheet1")).operations[-1]
        "Operation('MaxPos')"

        """
        return self._reduce(over, "MaxPos", vector=True, is_complex=False)

    def min_position(self, over: CalculatorGeometry) -> VectorReal:
        """Position of the minimum over a geometry (calculator ``MinPos``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        VectorReal
            Real vector expression locating the minimum position.

        Examples
        --------
        Find the minimum position on a surface.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Surface
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).min_position(Surface("Sheet1")).operations[-1]
        "Operation('MinPos')"

        """
        return self._reduce(over, "MinPos", vector=True, is_complex=False)

    def value(self, over: CalculatorGeometry) -> ScalarReal:
        """Sample the quantity on a geometry without integrating.

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the field-value lookup.

        Returns
        -------
        ScalarReal
            Real scalar expression evaluated on the provided geometry.

        Examples
        --------
        Sample a scalar quantity on a line.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Line
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).value(Line("Polyline1")).operations[-1]
        "Operation('LineValue')"

        """
        return self._reduce(over, "")

    # build a complex scalar from this real part / imaginary part
    def as_complex_real(self) -> ScalarComplex:
        """Use this real scalar as the real part of a complex number (calculator ``CmplxR``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression using this value as the real component.

        Examples
        --------
        Promote a real scalar to the real part of a complex value.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).as_complex_real().operations[-1]
        "Operation('CmplxR')"

        """
        return self._spawn(False, True, ["Operation('CmplxR')"])

    def as_complex_imag(self) -> ScalarComplex:
        """Use this real scalar as the imaginary part of a complex number (calculator ``CmplxI``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression using this value as the imaginary component.

        Examples
        --------
        Promote a real scalar to the imaginary part of a complex value.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).as_complex_imag().operations[-1]
        "Operation('CmplxI')"

        """
        return self._spawn(False, True, ["Operation('CmplxI')"])


class ScalarComplex(FieldExpression):
    """A complex scalar Fields Calculator quantity.

    Examples
    --------
    Start from a complex scalar quantity and extract derived values.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
    >>> fx = FieldExpressions(calculator=None)
    >>> voltage = fx.scalar("V")
    >>> voltage.operations
    ["Fundamental_Quantity('V')"]

    """

    is_vector = False
    is_complex = True

    def real(self) -> ScalarReal:
        """Real part (calculator ``Real``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the real component.

        Examples
        --------
        Extract the real part of a complex scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").real().operations[-1]
        "Operation('Real')"

        """
        return self._unary("Real", vector=False, is_complex=False)

    def imaginary(self) -> ScalarReal:
        """Imaginary part (calculator ``Imag``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the imaginary component.

        Examples
        --------
        Extract the imaginary part of a complex scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").imaginary().operations[-1]
        "Operation('Imag')"

        """
        return self._unary("Imag", vector=False, is_complex=False)

    def magnitude(self) -> ScalarReal:
        """Complex magnitude ``|s|`` (calculator ``CmplxMag``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the complex magnitude.

        Examples
        --------
        Compute the magnitude of a complex scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").magnitude().operations[-1]
        "Operation('CmplxMag')"

        """
        return self._unary("CmplxMag", vector=False, is_complex=False)

    def phase(self) -> ScalarReal:
        """Phase angle of the complex quantity (calculator ``CmplxPhase``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the phase angle.

        Examples
        --------
        Compute the phase of a complex scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").phase().operations[-1]
        "Operation('CmplxPhase')"

        """
        return self._unary("CmplxPhase", vector=False, is_complex=False)

    def at_phase(self, phase_deg: float) -> ScalarReal:
        """Real value at a given phase angle in degrees (calculator ``AtPhase``).

        Parameters
        ----------
        phase_deg : float
            Phase angle in degrees.

        Returns
        -------
        ScalarReal
            Real scalar expression evaluated at the requested phase.

        Examples
        --------
        Evaluate a complex scalar at a specific phase.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").at_phase(90).operations[-2:]
        ['Scalar_Constant(90)', "Operation('AtPhase')"]

        """
        return self._spawn(False, False, [f"Scalar_Constant({_num(phase_deg)})", "Operation('AtPhase')"])

    def conjugate(self) -> ScalarComplex:
        """Complex conjugate (calculator ``Conj``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression with ``Operation('Conj')`` appended.

        Examples
        --------
        Conjugate a complex scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").conjugate().operations[-1]
        "Operation('Conj')"

        """
        return self._unary("Conj", vector=False, is_complex=True)

    def smooth(self) -> ScalarComplex:
        """Smooth the quantity across the mesh (calculator ``Smooth``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression with mesh smoothing applied.

        Examples
        --------
        Smooth a complex scalar field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").smooth().operations[-1]
        "Operation('Smooth')"

        """
        return self._unary("Smooth", vector=False, is_complex=True)

    def as_vector_x(self) -> VectorComplex:
        """Place this scalar in the x component of a vector (calculator ``VecX``).

        Returns
        -------
        VectorComplex
            Complex vector expression with the scalar in the x component.

        Examples
        --------
        Embed a complex scalar into the x component of a vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").as_vector_x().operations[-1]
        "Operation('VecX')"

        """
        return self._unary("VecX", vector=True, is_complex=True)

    def as_vector_y(self) -> VectorComplex:
        """Place this scalar in the y component of a vector (calculator ``VecY``).

        Returns
        -------
        VectorComplex
            Complex vector expression with the scalar in the y component.

        Examples
        --------
        Embed a complex scalar into the y component of a vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").as_vector_y().operations[-1]
        "Operation('VecY')"

        """
        return self._unary("VecY", vector=True, is_complex=True)

    def as_vector_z(self) -> VectorComplex:
        """Place this scalar in the z component of a vector (calculator ``VecZ``).

        Returns
        -------
        VectorComplex
            Complex vector expression with the scalar in the z component.

        Examples
        --------
        Embed a complex scalar into the z component of a vector.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").as_vector_z().operations[-1]
        "Operation('VecZ')"

        """
        return self._unary("VecZ", vector=True, is_complex=True)

    def __add__(self, other) -> ScalarComplex:
        return _scalar_arith(self, other, "+")

    def __sub__(self, other) -> ScalarComplex:
        return _scalar_arith(self, other, "-")

    def __mul__(self, other) -> FieldExpression:
        return _scalar_mul(self, other, "*")

    def __truediv__(self, other) -> FieldExpression:
        return _scalar_mul(self, other, "/")

    def integrate(self, over: CalculatorGeometry) -> ScalarComplex:
        """Integrate over a geometry ``∫ s dΩ`` (calculator ``Integrate``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the integration.

        Returns
        -------
        ScalarComplex
            Complex scalar expression reduced with ``Integrate``.

        Examples
        --------
        Integrate a complex scalar field over a line.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Line
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").integrate(Line("Polyline1")).operations[-1]
        "Operation('Integrate')"

        """
        return self._reduce(over, "Integrate")

    def mean(self, over: CalculatorGeometry) -> ScalarComplex:
        """Mean over a geometry (calculator ``Mean``).

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the reduction.

        Returns
        -------
        ScalarComplex
            Complex scalar expression reduced with ``Mean``.

        Examples
        --------
        Compute the mean of a complex scalar field on a surface.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Surface
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").mean(Surface("Sheet1")).operations[-1]
        "Operation('Mean')"

        """
        return self._reduce(over, "Mean")

    def value(self, over: CalculatorGeometry) -> ScalarComplex:
        """Sample the quantity on a geometry without integrating.

        Parameters
        ----------
        over : CalculatorGeometry
            Geometry used for the field-value lookup.

        Returns
        -------
        ScalarComplex
            Complex scalar expression evaluated on the provided geometry.

        Examples
        --------
        Sample a complex scalar quantity on a line.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, Line
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("V").value(Line("Polyline1")).operations[-1]
        "Operation('LineValue')"

        """
        return self._reduce(over, "")


class VectorReal(FieldExpression):
    """A real 3-vector Fields Calculator quantity.

    Examples
    --------
    Start from a real vector quantity and derive scalar components.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
    >>> fx = FieldExpressions(calculator=None)
    >>> field = fx.vector("E", is_complex=False)
    >>> field.operations
    ["Fundamental_Quantity('E')"]

    """

    is_vector = True
    is_complex = False

    def scalar_x(self) -> ScalarReal:
        """X component (calculator ``ScalarX``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the x component.

        Examples
        --------
        Extract the x component of a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).scalar_x().operations[-1]
        "Operation('ScalarX')"

        """
        return self._unary("ScalarX", vector=False, is_complex=False)

    def scalar_y(self) -> ScalarReal:
        """Y component (calculator ``ScalarY``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the y component.

        Examples
        --------
        Extract the y component of a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).scalar_y().operations[-1]
        "Operation('ScalarY')"

        """
        return self._unary("ScalarY", vector=False, is_complex=False)

    def scalar_z(self) -> ScalarReal:
        """Z component (calculator ``ScalarZ``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the z component.

        Examples
        --------
        Extract the z component of a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).scalar_z().operations[-1]
        "Operation('ScalarZ')"

        """
        return self._unary("ScalarZ", vector=False, is_complex=False)

    def magnitude(self) -> ScalarReal:
        """Vector magnitude ``‖v‖`` (calculator ``Mag``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the vector magnitude.

        Examples
        --------
        Compute the magnitude of a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).magnitude().operations[-1]
        "Operation('Mag')"

        """
        return self._unary("Mag", vector=False, is_complex=False)

    def smooth(self) -> VectorReal:
        """Smooth the quantity across the mesh (calculator ``Smooth``).

        Returns
        -------
        VectorReal
            Real vector expression with mesh smoothing applied.

        Examples
        --------
        Smooth a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).smooth().operations[-1]
        "Operation('Smooth')"

        """
        return self._unary("Smooth", vector=True, is_complex=False)

    def curl(self) -> VectorReal:
        """Curl ``∇×v`` (calculator ``Curl``).

        Returns
        -------
        VectorReal
            Real vector expression containing the curl.

        Examples
        --------
        Compute the curl of a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).curl().operations[-1]
        "Operation('Curl')"

        """
        return self._unary("Curl", vector=True, is_complex=False)

    def divergence(self) -> ScalarReal:
        """Divergence ``∇·v`` (calculator ``Divg``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the divergence.

        Examples
        --------
        Compute the divergence of a real vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E", is_complex=False).divergence().operations[-1]
        "Operation('Divg')"

        """
        return self._unary("Divg", vector=False, is_complex=False)

    def __add__(self, other) -> VectorReal:
        return _vector_arith(self, other, "+")

    def __sub__(self, other) -> VectorReal:
        return _vector_arith(self, other, "-")

    def __mul__(self, other) -> VectorReal:
        return _vector_scale(self, other, "*")

    def __truediv__(self, other) -> VectorReal:
        return _vector_scale(self, other, "/")


class VectorComplex(FieldExpression):
    """A complex 3-vector Fields Calculator quantity.

    Examples
    --------
    Start from a complex vector quantity and derive scalar projections.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
    >>> fx = FieldExpressions(calculator=None)
    >>> field = fx.vector("E")
    >>> field.operations
    ["Fundamental_Quantity('E')"]

    """

    is_vector = True
    is_complex = True

    def scalar_x(self) -> ScalarComplex:
        """X component (calculator ``ScalarX``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression containing the x component.

        Examples
        --------
        Extract the x component of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").scalar_x().operations[-1]
        "Operation('ScalarX')"

        """
        return self._unary("ScalarX", vector=False, is_complex=True)

    def scalar_y(self) -> ScalarComplex:
        """Y component (calculator ``ScalarY``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression containing the y component.

        Examples
        --------
        Extract the y component of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").scalar_y().operations[-1]
        "Operation('ScalarY')"

        """
        return self._unary("ScalarY", vector=False, is_complex=True)

    def scalar_z(self) -> ScalarComplex:
        """Z component (calculator ``ScalarZ``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression containing the z component.

        Examples
        --------
        Extract the z component of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").scalar_z().operations[-1]
        "Operation('ScalarZ')"

        """
        return self._unary("ScalarZ", vector=False, is_complex=True)

    def real(self) -> VectorReal:
        """Real part, component-wise (calculator ``Real``).

        Returns
        -------
        VectorReal
            Real vector expression containing the real part of each component.

        Examples
        --------
        Extract the real part of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").real().operations[-1]
        "Operation('Real')"

        """
        return self._unary("Real", vector=True, is_complex=False)

    def imaginary(self) -> VectorReal:
        """Imaginary part, component-wise (calculator ``Imag``).

        Returns
        -------
        VectorReal
            Real vector expression containing the imaginary part of each component.

        Examples
        --------
        Extract the imaginary part of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").imaginary().operations[-1]
        "Operation('Imag')"

        """
        return self._unary("Imag", vector=True, is_complex=False)

    def magnitude(self) -> ScalarReal:
        """Complex vector magnitude (calculator ``Mag``).

        Returns
        -------
        ScalarReal
            Real scalar expression containing the vector magnitude.

        Examples
        --------
        Compute the magnitude of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").magnitude().operations[-1]
        "Operation('Mag')"

        """
        return self._unary("Mag", vector=False, is_complex=False)

    def component_magnitude(self) -> VectorReal:
        """Component-wise complex magnitude as a real vector (calculator ``CmplxMag``).

        Returns
        -------
        VectorReal
            Real vector expression with component-wise complex magnitudes.

        Examples
        --------
        Compute per-component magnitudes for a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").component_magnitude().operations[-1]
        "Operation('CmplxMag')"

        """
        return self._unary("CmplxMag", vector=True, is_complex=False)

    def conjugate(self) -> VectorComplex:
        """Complex conjugate, component-wise (calculator ``Conj``).

        Returns
        -------
        VectorComplex
            Complex vector expression with the conjugate of each component.

        Examples
        --------
        Conjugate a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").conjugate().operations[-1]
        "Operation('Conj')"

        """
        return self._unary("Conj", vector=True, is_complex=True)

    def smooth(self) -> VectorComplex:
        """Smooth the quantity across the mesh (calculator ``Smooth``).

        Returns
        -------
        VectorComplex
            Complex vector expression with mesh smoothing applied.

        Examples
        --------
        Smooth a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").smooth().operations[-1]
        "Operation('Smooth')"

        """
        return self._unary("Smooth", vector=True, is_complex=True)

    def curl(self) -> VectorComplex:
        """Curl ``∇×v`` (calculator ``Curl``).

        Returns
        -------
        VectorComplex
            Complex vector expression containing the curl.

        Examples
        --------
        Compute the curl of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").curl().operations[-1]
        "Operation('Curl')"

        """
        return self._unary("Curl", vector=True, is_complex=True)

    def divergence(self) -> ScalarComplex:
        """Divergence ``∇·v`` (calculator ``Divg``).

        Returns
        -------
        ScalarComplex
            Complex scalar expression containing the divergence.

        Examples
        --------
        Compute the divergence of a complex vector field.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector("E").divergence().operations[-1]
        "Operation('Divg')"

        """
        return self._unary("Divg", vector=False, is_complex=True)

    def __add__(self, other) -> VectorComplex:
        return _vector_arith(self, other, "+")

    def __sub__(self, other) -> VectorComplex:
        return _vector_arith(self, other, "-")

    def __mul__(self, other) -> VectorComplex:
        return _vector_scale(self, other, "*")

    def __truediv__(self, other) -> VectorComplex:
        return _vector_scale(self, other, "/")


# These module-level constants centralize type selection and stack-rule lookups
# so the expression builders can stay compact, consistent, and easy to maintain.
# leaf-class registry keyed by (is_vector, is_complex)
LEAF = {
    (False, False): ScalarReal,
    (False, True): ScalarComplex,
    (True, False): VectorReal,
    (True, True): VectorComplex,
}


def _operation_name(entry: str) -> str | None:
    """Return the operation name extracted from a calculator entry.

    Parameters
    ----------
    entry : str
        Calculator entry to inspect.

    Returns
    -------
    str or None
        Operation name when ``entry`` is an ``Operation(...)`` entry, ``None`` otherwise.

    Examples
    --------
    Extract the calculator operation name from an entry.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import _operation_name
    >>> _operation_name("Operation('Mag')")
    'Mag'

    """
    if entry.startswith("Operation(") and "'" in entry:
        return entry.split("'")[1]
    return None


def _stack_effect(entry: str) -> int:
    """Net change a single entry makes to the calculator stack depth.

    Parameters
    ----------
    entry : str
        Calculator entry to inspect.

    Returns
    -------
    int
        Net stack-depth change contributed by the entry.

    Examples
    --------
    Measure the stack effect of a scalar constant entry.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import _stack_effect
    >>> _stack_effect("Scalar_Constant(1)")
    1

    """
    name = _operation_name(entry)
    if name is not None:
        if name in BINARY_OPS or name in VALUE_OPS:
            return -1
        if name in PUSH_OPS:
            return 1
        return 0  # unary operation: pop one, push one
    if entry.startswith(PUSH_PREFIXES):
        return 1
    return 0  # unknown entry: assume neutral


def _resolve_stack_depth(operations: Sequence[str]) -> int:
    """Simulate the operation stack and return the final depth.

    Raises :class:`AEDTRuntimeError` if any operation would pop a register that
    is not there (an unbalanced / malformed chain), which is how an
    overly-stacked expression would otherwise fail confusingly in AEDT.

    Parameters
    ----------
    operations : Sequence[str]
        Calculator entries to simulate in order.

    Returns
    -------
    int
        Final stack depth after all operations are applied.

    Examples
    --------
    Resolve the final depth of a simple scalar expression.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import _resolve_stack_depth
    >>> _resolve_stack_depth(["Fundamental_Quantity('E')", "Operation('Mag')"])
    1

    """
    depth = 0
    for i, entry in enumerate(operations):
        effect = _stack_effect(entry)
        needed = 2 if effect < 0 else 0
        if depth < needed:
            raise AEDTRuntimeError(
                f"operation #{i} ('{entry}') underflows the calculator stack "
                f"(depth {depth}); the expression is malformed"
            )
        depth += effect
    return depth


def _num(value) -> str:
    """Format a number the way AEDT serializes calculator constants.

    Parameters
    ----------
    value : int or float
        Number to serialize.

    Returns
    -------
    str
        Compact decimal representation such as ``"1"`` or ``"2.5"``.

    Examples
    --------
    Format a floating-point value for calculator constants.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import _num
    >>> _num(2.5)
    '2.5'

    """
    return f"{value:g}"


def scalar_constant(value: float, **meta) -> ScalarReal:
    """Create a real scalar constant (calculator ``Scalar_Constant``).

    Parameters
    ----------
    value : float
        Constant value to push on the calculator stack.
    **meta
        Metadata forwarded to :class:`ScalarReal`.

    Returns
    -------
    ScalarReal
        Real scalar constant expression.

    Examples
    --------
    Create a scalar constant expression directly.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import scalar_constant
    >>> scalar_constant(3).operations
    ['Scalar_Constant(3)']

    """
    return ScalarReal([f"Scalar_Constant({_num(value)})"], **meta)


def complex_constant(real: float, imag: float, **meta) -> ScalarComplex:
    """Create a complex scalar constant (calculator ``Complex_Constant``).

    Parameters
    ----------
    real : float
        Real part of the constant.
    imag : float
        Imaginary part of the constant.
    **meta
        Metadata forwarded to :class:`ScalarComplex`.

    Returns
    -------
    ScalarComplex
        Complex scalar constant expression.

    Examples
    --------
    Create a complex constant expression directly.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import complex_constant
    >>> complex_constant(1, 2).operations
    ['Complex_Constant(1, 2)']

    """
    return ScalarComplex([f"Complex_Constant({_num(real)}, {_num(imag)})"], **meta)


def _to_expr(value, proto: FieldExpression) -> FieldExpression:
    """Coerce a Python number into an expression carrying prototype metadata.

    Parameters
    ----------
    value : FieldExpression or number
        Operand to coerce.
    proto : FieldExpression
        Expression whose metadata is copied onto constant operands.

    Returns
    -------
    FieldExpression
        Original expression or newly created constant expression.

    Examples
    --------
    Promote a Python number to a scalar constant expression.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, _to_expr
    >>> fx = FieldExpressions(calculator=None)
    >>> _to_expr(2, fx.scalar("Phi", is_complex=False)).operations
    ['Scalar_Constant(2)']

    """
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
    """Return ``True`` when either operand is complex.

    Parameters
    ----------
    a : FieldExpression
        First operand.
    b : FieldExpression
        Second operand.

    Returns
    -------
    bool
        ``True`` when either operand is complex-valued.

    Examples
    --------
    Detect whether mixed arithmetic should promote to complex.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, _both
    >>> fx = FieldExpressions(calculator=None)
    >>> _both(fx.scalar("Phi", is_complex=False), fx.scalar("V"))
    True

    """
    return a.is_complex or b.is_complex


def _scalar_arith(a: FieldExpression, b, op: str) -> FieldExpression:
    """Add or subtract a scalar with another scalar or a number.

    Parameters
    ----------
    a : FieldExpression
        Left scalar operand.
    b : FieldExpression or number
        Right scalar operand.
    op : str
        Calculator operation name, typically ``"+"`` or ``"-"``.

    Returns
    -------
    FieldExpression
        Compiled scalar arithmetic expression.

    Examples
    --------
    Add a scalar constant to a real scalar field.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, _scalar_arith
    >>> fx = FieldExpressions(calculator=None)
    >>> _scalar_arith(fx.scalar("Phi", is_complex=False), 2, "+").operations[-1]
    "Operation('+')"

    """
    b = _to_expr(b, a)
    if b.is_vector:
        raise TypeError("cannot add/subtract a scalar and a vector")
    return a._binary(b, op, vector=False, is_complex=_both(a, b))


def _scalar_mul(a: FieldExpression, b, op: str) -> FieldExpression:
    """Multiply or divide starting from a scalar operand.

    Parameters
    ----------
    a : FieldExpression
        Left scalar operand.
    b : FieldExpression or number
        Right operand.
    op : str
        Calculator operation name, typically ``"*"`` or ``"/"``.

    Returns
    -------
    FieldExpression
        Compiled multiplication or division expression.

    Examples
    --------
    Multiply a scalar field by a numeric constant.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, _scalar_mul
    >>> fx = FieldExpressions(calculator=None)
    >>> _scalar_mul(fx.scalar("Phi", is_complex=False), 2, "*").operations[-1]
    "Operation('*')"

    """
    b = _to_expr(b, a)
    return a._binary(b, op, vector=b.is_vector, is_complex=_both(a, b))


def _vector_arith(a: FieldExpression, b, op: str) -> FieldExpression:
    """Add or subtract two vector expressions.

    Parameters
    ----------
    a : FieldExpression
        Left vector operand.
    b : FieldExpression
        Right vector operand.
    op : str
        Calculator operation name, typically ``"+"`` or ``"-"``.

    Returns
    -------
    FieldExpression
        Compiled vector arithmetic expression.

    Examples
    --------
    Add two real vector fields.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, _vector_arith
    >>> fx = FieldExpressions(calculator=None)
    >>> v = fx.vector("E", is_complex=False)
    >>> _vector_arith(v, v, "+").operations[-1]
    "Operation('+')"

    """
    if not isinstance(b, FieldExpression) or not b.is_vector:
        raise TypeError("vector +/- requires another vector expression")
    return a._binary(b, op, vector=True, is_complex=_both(a, b))


def _vector_scale(a: FieldExpression, b, op: str) -> FieldExpression:
    """Scale a vector by a scalar operand or number.

    Parameters
    ----------
    a : FieldExpression
        Left vector operand.
    b : FieldExpression or number
        Right scalar operand.
    op : str
        Calculator operation name, typically ``"*"`` or ``"/"``.

    Returns
    -------
    FieldExpression
        Compiled vector scaling expression.

    Examples
    --------
    Scale a real vector field by a constant.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, _vector_scale
    >>> fx = FieldExpressions(calculator=None)
    >>> _vector_scale(fx.vector("E", is_complex=False), 2, "*").operations[-1]
    "Operation('*')"

    """
    b = _to_expr(b, a)
    if b.is_vector:
        raise TypeError("vector * vector is undefined; use dot() or cross()")
    return a._binary(b, op, vector=True, is_complex=_both(a, b))


def dot(u: FieldExpression, v: FieldExpression) -> FieldExpression:
    """Vector dot product ``u·v`` (calculator ``Dot``) -> scalar.

    Algebraic dot, no conjugation (use ``v.conjugate()`` for an inner product).

    Parameters
    ----------
    u : FieldExpression
        Left vector operand.
    v : FieldExpression
        Right vector operand.

    Returns
    -------
    FieldExpression
        Scalar expression representing the dot product.

    Examples
    --------
    Compute the dot product of a field with its conjugate.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, dot
    >>> fx = FieldExpressions(calculator=None)
    >>> dot(fx.vector("E"), fx.vector("E").conjugate()).operations[-1]
    "Operation('Dot')"

    """
    if not (isinstance(u, FieldExpression) and u.is_vector and isinstance(v, FieldExpression) and v.is_vector):
        raise TypeError("dot() requires two vector expressions")
    return u._binary(v, "Dot", vector=False, is_complex=_both(u, v))


def cross(u: FieldExpression, v: FieldExpression) -> FieldExpression:
    """Vector cross product ``u×v`` (calculator ``Cross``) -> vector.

    Parameters
    ----------
    u : FieldExpression
        Left vector operand.
    v : FieldExpression
        Right vector operand.

    Returns
    -------
    FieldExpression
        Vector expression representing the cross product.

    Examples
    --------
    Compute the cross product of two real vector fields.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, cross
    >>> fx = FieldExpressions(calculator=None)
    >>> u = fx.vector("E", is_complex=False)
    >>> cross(u, u).operations[-1]
    "Operation('Cross')"

    """
    if not (isinstance(u, FieldExpression) and u.is_vector and isinstance(v, FieldExpression) and v.is_vector):
        raise TypeError("cross() requires two vector expressions")
    return u._binary(v, "Cross", vector=True, is_complex=_both(u, v))


def cmplx(real: ScalarReal, imag: ScalarReal) -> ScalarComplex:
    """Build a complex scalar from real and imaginary scalar parts.

    Mirrors the calculator ``CmplxR`` / ``CmplxI`` idiom (``real.as_complex_real()
    + imag.as_complex_imag()``).

    Parameters
    ----------
    real : ScalarReal
        Real part of the complex scalar.
    imag : ScalarReal
        Imaginary part of the complex scalar.

    Returns
    -------
    ScalarComplex
        Complex scalar expression assembled from the two inputs.

    Examples
    --------
    Combine two real scalar expressions into a complex scalar.

    >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions, cmplx
    >>> fx = FieldExpressions(calculator=None)
    >>> expr = cmplx(fx.scalar("Phi", is_complex=False), fx.scalar_constant(1.0))
    >>> expr.is_complex
    True

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

        Examples
        --------
        Create an unbound expression builder for local composition.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx._calculator is None
        True

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
            Initial calculator-operation entries for the expression stack.

        Returns
        -------
        FieldExpression
            Concrete typed expression instance selected from the internal leaf
            registry.

        Examples
        --------
        Seed a real scalar expression from an explicit entry.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx._seed(False, False, ["Scalar_Constant(1)"]).operations
        ['Scalar_Constant(1)']

        """
        cls = LEAF[(vector, complex_)]
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

        Examples
        --------
        Create a scalar expression from a fundamental quantity.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar("Phi", is_complex=False).operations
        ["Fundamental_Quantity('Phi')"]

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

        Examples
        --------
        Reuse a named expression as a new starting point.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.named_expression("Poynting", is_vector=True).operations
        ["NameOfExpression('Poynting')"]

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

        Examples
        --------
        Create a scalar constant through the builder.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.scalar_constant(5).operations
        ['Scalar_Constant(5)']

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

        Examples
        --------
        Create a complex constant through the builder.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.complex_constant(1, 2).operations
        ['Complex_Constant(1, 2)']

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

        Examples
        --------
        Create a constant vector through the builder.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.vector_constant(1, 0, 0).operations
        ['Vector_Constant(1, 0, 0)']

        """
        return self._seed(True, False, [f"Vector_Constant({_num(x)}, {_num(y)}, {_num(z)})"])

    def function(self, name: str) -> ScalarReal:
        """Create a scalar expression from a design variable or function.

        Parameters
        ----------
        name : str
            Name resolved by AEDT through ``Scalar_Function``, typically a
            design variable or calculator function entry.

        Returns
        -------
        ScalarReal
            Real scalar expression seeded with ``Scalar_Function``.

        Examples
        --------
        Seed a scalar expression from a design variable.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.function("width").operations
        ["Scalar_Function(FuncValue='width')"]

        """
        return self._seed(False, False, [f"Scalar_Function(FuncValue='{name}')"])

    def tangent(self) -> VectorReal:
        """Push the geometry unit tangent vector.

        Returns
        -------
        VectorReal
            Real vector expression seeded with ``Operation('Tangent')`` for
            use in tangential projections such as ``dot(field, fx.tangent())``.

        Examples
        --------
        Seed a tangent vector for later projections.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.tangent().operations
        ["Operation('Tangent')"]

        """
        return self._seed(True, False, ["Operation('Tangent')"])

    def normal(self) -> VectorReal:
        """Push the geometry unit normal vector.

        Returns
        -------
        VectorReal
            Real vector expression seeded with ``Operation('Normal')`` for use
            in normal-flux or projection calculations.

        Examples
        --------
        Seed a normal vector for later projections.

        >>> from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
        >>> fx = FieldExpressions(calculator=None)
        >>> fx.normal().operations
        ["Operation('Normal')"]

        """
        return self._seed(True, False, ["Operation('Normal')"])
