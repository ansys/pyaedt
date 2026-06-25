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

"""Unit tests for the typed Fields Calculator expression builder.

These exercise the pure-Python compilation to the calculator operation grammar
(no AEDT session needed); the few methods that talk to AEDT are checked against a
mocked :class:`FieldsCalculator`.
"""

from unittest.mock import MagicMock

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.post.field_calculator_expressions import FieldExpressions
from ansys.aedt.core.visualization.post.field_calculator_expressions import Line
from ansys.aedt.core.visualization.post.field_calculator_expressions import ScalarComplex
from ansys.aedt.core.visualization.post.field_calculator_expressions import ScalarReal
from ansys.aedt.core.visualization.post.field_calculator_expressions import Surface
from ansys.aedt.core.visualization.post.field_calculator_expressions import VectorComplex
from ansys.aedt.core.visualization.post.field_calculator_expressions import VectorReal
from ansys.aedt.core.visualization.post.field_calculator_expressions import Volume
from ansys.aedt.core.visualization.post.field_calculator_expressions import cross
from ansys.aedt.core.visualization.post.field_calculator_expressions import dot
from ansys.aedt.core.visualization.post.fields_calculator import FieldsCalculator


@pytest.fixture
def fx():
    """Unbound builder (pure compilation, no calculator)."""
    return FieldExpressions(calculator=None)


# ---------------------------------------------------------------------------
# seeds + unary compilation
# ---------------------------------------------------------------------------
def test_vector_and_scalar_seed_types(fx):
    assert isinstance(fx.vector("E"), VectorComplex)
    assert isinstance(fx.vector("E", complex=False), VectorReal)
    assert isinstance(fx.scalar("Phi"), ScalarComplex)
    assert isinstance(fx.scalar("Phi", complex=False), ScalarReal)
    assert fx.vector("E").operations == ["Fundamental_Quantity('E')"]
    assert fx.named_expression("Poynting", is_vector=True).operations == ["NameOfExpression('Poynting')"]


def test_unary_op_types_and_tokens(fx):
    E = fx.vector("E")
    assert isinstance(E.magnitude(), ScalarReal)
    assert isinstance(E.scalar_x(), ScalarComplex)
    assert isinstance(E.real(), VectorReal)
    assert isinstance(E.imaginary(), VectorReal)
    assert isinstance(E.conjugate(), VectorComplex)
    assert isinstance(E.tangent(), VectorComplex)
    assert isinstance(E.curl(), VectorComplex)
    assert isinstance(E.divergence(), ScalarComplex)
    assert E.magnitude().operations[-1] == "Operation('Mag')"
    assert E.scalar_x().operations[-1] == "Operation('ScalarX')"
    assert E.conjugate().operations[-1] == "Operation('Conj')"
    assert E.divergence().operations[-1] == "Operation('Divg')"


def test_scalar_unary(fx):
    s = fx.scalar("Phi")
    assert isinstance(s.real(), ScalarReal)
    assert isinstance(s.magnitude(), ScalarReal)
    assert s.magnitude().operations[-1] == "Operation('CmplxMag')"
    assert isinstance(s.real().gradient(), VectorReal)
    assert s.real().gradient().operations[-1] == "Operation('Grad')"


# ---------------------------------------------------------------------------
# binary RPN concatenation + promotion
# ---------------------------------------------------------------------------
def test_dot_is_rpn_concatenation(fx):
    E = fx.vector("E")
    d = dot(E, E.conjugate())
    assert isinstance(d, ScalarComplex)
    assert d.operations == [
        "Fundamental_Quantity('E')",
        "Fundamental_Quantity('E')",
        "Operation('Conj')",
        "Operation('Dot')",
    ]


def test_cross_and_real_dot_promotion(fx):
    Er = fx.vector("E", complex=False)
    assert isinstance(cross(Er, Er), VectorReal)
    assert isinstance(dot(Er, Er), ScalarReal)  # real . real -> real
    assert isinstance(dot(Er, fx.vector("H")), ScalarComplex)  # any complex -> complex
    assert cross(Er, Er).operations[-1] == "Operation('Cross')"


def test_scalar_arithmetic_and_scaling(fx):
    E = fx.vector("E")
    me = E.magnitude()  # ScalarReal
    assert isinstance(me + me, ScalarReal)
    assert isinstance(me + E.scalar_x().real(), ScalarReal)
    assert isinstance(me * E, VectorComplex)  # scalar * vector -> vector
    assert (me + me).operations[-1] == "Operation('+')"
    assert (me * E).operations[-1] == "Operation('*')"


def test_negation(fx):
    E = fx.vector("E")
    assert isinstance(-E, VectorComplex)
    assert (-E).operations[-1] == "Operation('Neg')"


# ---------------------------------------------------------------------------
# type guards
# ---------------------------------------------------------------------------
def test_type_guards(fx):
    E = fx.vector("E")
    with pytest.raises(TypeError):
        _ = E * E  # vector * vector
    with pytest.raises(TypeError):
        _ = E + E.magnitude()  # vector + scalar
    with pytest.raises(TypeError):
        dot(E.magnitude(), E)  # dot needs two vectors
    with pytest.raises(TypeError):
        cross(E.magnitude(), E.magnitude())


# ---------------------------------------------------------------------------
# geometry reductions
# ---------------------------------------------------------------------------
def test_integration_over_geometry(fx):
    E = fx.vector("E")
    expr = E.magnitude().integrate(Surface("Sheet1"))
    assert isinstance(expr, ScalarReal)
    assert expr.operations[-3:] == [
        "EnterSurface('Sheet1')",
        "Operation('SurfaceValue')",
        "Operation('Integrate')",
    ]
    assert "Surface" in expr.to_dict("x")["assignment_type"]


@pytest.mark.parametrize(
    "geom,enter,value",
    [
        (Line("Poly1"), "EnterLine('Poly1')", "Operation('LineValue')"),
        (Surface("Sheet1"), "EnterSurface('Sheet1')", "Operation('SurfaceValue')"),
        (Volume("Box1"), "EnterVolume('Box1')", "Operation('VolumeValue')"),
    ],
)
def test_geometry_tokens(fx, geom, enter, value):
    ops = fx.scalar("Phi", complex=False).integrate(geom).operations
    assert enter in ops and value in ops and "Operation('Integrate')" in ops


def test_geometry_accepts_object_with_name(fx):
    obj = MagicMock()
    obj.name = "MyObj"
    expr = fx.scalar("Phi", complex=False).maximum(Volume(obj))
    assert "EnterVolume('MyObj')" in expr.operations


# ---------------------------------------------------------------------------
# to_dict is schema-valid against the real calculator schema
# ---------------------------------------------------------------------------
def test_to_dict_passes_calculator_schema():
    app = MagicMock()
    app.design_type = "HFSS"
    fc = FieldsCalculator(app)  # loads the real schema/catalog
    fx = fc.expressions
    expr = dot(fx.vector("E"), fx.vector("H").conjugate()).real().integrate(Surface("S1"))
    d = expr.to_dict("power_flow_typed")
    # required keys present and validate_expression accepts it
    for key in ("design_type", "fields_type", "primary_sweep", "assignment_type", "operations"):
        assert key in d
    assert fc.validate_expression(d) is not False


# ---------------------------------------------------------------------------
# materialization delegates to FieldsCalculator
# ---------------------------------------------------------------------------
def test_add_invokes_add_expression():
    calc = MagicMock()
    calc.design_type = "HFSS"
    calc.add_expression.return_value = "my_named"
    fx = FieldExpressions(calc)
    res = fx.vector("E").magnitude().add("my_named")
    assert res == "my_named"
    args, kwargs = calc.add_expression.call_args
    assert args[0]["operations"][-1] == "Operation('Mag')"
    assert kwargs["name"] == "my_named"


def test_evaluate_adds_then_evaluates():
    calc = MagicMock()
    calc.design_type = "HFSS"
    calc.evaluate.return_value = 3.14
    fx = FieldExpressions(calc)
    val = fx.vector("E").magnitude().evaluate(name="m", setup="Setup1 : LastAdaptive")
    assert val == 3.14
    calc.add_expression.assert_called_once()
    calc.evaluate.assert_called_once()


def test_export_forwards_is_vector():
    calc = MagicMock()
    calc.design_type = "HFSS"
    calc.export.return_value = "out.fld"
    fx = FieldExpressions(calc)
    out = fx.vector("E").export("out.fld", name="vecE", solution="Setup1 : LastAdaptive")
    assert out == "out.fld"
    assert calc.export.call_args.kwargs["is_vector"] is True


def test_unbound_expression_cannot_materialize(fx):
    with pytest.raises(AEDTRuntimeError):
        fx.vector("E").magnitude().add("x")


# ---------------------------------------------------------------------------
# entry point on FieldsCalculator
# ---------------------------------------------------------------------------
def test_calculator_exposes_expressions_property():
    app = MagicMock()
    app.design_type = "HFSS"
    fc = FieldsCalculator(app)
    assert isinstance(fc.expressions, FieldExpressions)
    assert fc.expressions is fc.expressions  # cached
    assert isinstance(fc.expressions.vector("E"), VectorComplex)


# ---------------------------------------------------------------------------
# long / heavily-stacked expressions must stay well-formed
# ---------------------------------------------------------------------------
def test_well_formed_chains_resolve_to_single_result(fx):
    E, H = fx.vector("E"), fx.vector("H")
    assert dot(E, H).stack_depth() == 1
    flux = cross(E, H.conjugate()).real().normal().magnitude().integrate(Surface("S"))
    assert flux.stack_depth() == 1
    assert flux.verify() is flux
    assert len(flux) == 10


def test_long_unary_chain_is_balanced_and_builds(fx):
    """A 1000-deep unary chain compiles, stays balanced, and produces a valid dict."""
    s = fx.scalar("Phi", complex=False)
    for _ in range(1000):
        s = s.smooth()
    assert len(s) == 1001
    assert s.stack_depth() == 1  # still resolves to a single result
    d = s.to_dict("long_smooth")
    assert len(d["operations"]) == 1001


def test_long_accumulation_chain_is_balanced(fx):
    """Summing many terms keeps the stack balanced regardless of length."""
    term = fx.scalar("Phi", complex=False).smooth()
    total = term
    for _ in range(200):
        total = total + fx.scalar("Phi", complex=False)
    assert total.stack_depth() == 1
    assert total.verify() is total


def test_very_long_chain_does_not_recurse(fx):
    """No recursion: building and serializing a 5000-op chain must not raise."""
    s = fx.scalar("Phi", complex=False)
    for _ in range(5000):
        s = s.smooth()
    assert len(s) == 5001
    assert s.stack_depth() == 1
    assert len(s.operations) == 5001  # property copy works at scale


def test_exponential_reuse_blows_up_but_checkpoint_mitigates():
    """Self-combination doubles the op count; checkpoint() keeps it bounded.

    This reproduces the failure mode behind 'too many stacked operations': reusing
    a sub-expression duplicates its operations, so repeated doubling grows the
    stack as 2^n. The expression stays *correct* (balanced), but becomes huge.
    """
    calc = MagicMock()
    calc.design_type = "HFSS"
    calc.add_expression.return_value = "cp"
    fx = FieldExpressions(calc)

    # without checkpoint: 12 doublings -> 2^13 - 1 operations, but still balanced
    blown = fx.scalar("Phi", complex=False)
    for _ in range(12):
        blown = blown + blown
    assert len(blown) == 2**13 - 1
    assert blown.stack_depth() == 1

    # with a checkpoint after each doubling: the stack stays tiny
    bounded = fx.scalar("Phi", complex=False)
    for _ in range(12):
        bounded = (bounded + bounded).checkpoint()
    assert len(bounded) == 1  # collapsed to a single NameOfExpression reference
    assert bounded.operations[0].startswith("NameOfExpression(")


def test_checkpoint_preserves_type_and_requires_calculator(fx):
    # unbound expression cannot checkpoint
    with pytest.raises(AEDTRuntimeError):
        fx.vector("E").magnitude().checkpoint()
    # bound checkpoint keeps the same typed class
    calc = MagicMock()
    calc.design_type = "HFSS"
    calc.add_expression.return_value = "cp"
    fxb = FieldExpressions(calc)
    cp = fxb.vector("E").checkpoint("vec_cp")
    assert isinstance(cp, VectorComplex)
    assert cp.operations == ["NameOfExpression('vec_cp')"]


def test_malformed_stack_is_detected():
    """A hand-built unbalanced operation list is rejected with a clear error."""
    bad = ScalarReal(["Operation('Dot')"], calculator=None)  # Dot with no operands
    with pytest.raises(AEDTRuntimeError):
        bad.stack_depth()
    with pytest.raises(AEDTRuntimeError):
        bad.verify()


def test_unbalanced_extra_operand_detected():
    """Two pushes with no combiner leaves depth 2 -> verify rejects it."""
    two = ScalarReal(["Fundamental_Quantity('E')", "Fundamental_Quantity('H')"], calculator=None)
    assert two.stack_depth() == 2
    with pytest.raises(AEDTRuntimeError):
        two.verify()


def test_add_verifies_before_sending_to_aedt():
    """add() must not forward a malformed expression to the calculator."""
    calc = MagicMock()
    calc.design_type = "HFSS"
    bad = ScalarReal(["Operation('Dot')"], calculator=calc)
    # the verify guard rejects it before reaching AEDT (raise or falsy, per error
    # handling settings); either way add_expression must never be called
    try:
        bad.add("bad")
    except AEDTRuntimeError:
        pass
    calc.add_expression.assert_not_called()
