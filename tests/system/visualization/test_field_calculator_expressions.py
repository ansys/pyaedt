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

import pytest

import ansys.aedt.core as pyaedt
from ansys.aedt.core.visualization.post.field_calculator_expressions import Line
from ansys.aedt.core.visualization.post.field_calculator_expressions import ScalarReal
from ansys.aedt.core.visualization.post.field_calculator_expressions import VectorComplex


@pytest.fixture(
    params=[
        pyaedt.Hfss,
        pyaedt.Hfss3dLayout,
        pyaedt.Maxwell3d,
        pyaedt.Maxwell2d,
        pyaedt.Icepak,
        pyaedt.Q3d,
        pyaedt.Q2d,
    ],
    ids=[
        "hfss",
        "hfss3d_layout",
        "maxwell_3d",
        "maxwell_2d",
        "icepak",
        "q3d",
        "q2d",
    ],
)
def aedtapp(request, add_app):
    app = add_app(application=request.param)
    yield app
    app.close_project(app.project_name)


def test_expressions_builder_registers(aedtapp) -> None:
    """Test registering a typed Fields Calculator expression as a named expression."""
    if aedtapp.design_type in ["HFSS 3D Layout Design"]:
        aedtapp.modeler.layers.add_layer("TOP")
        poly = aedtapp.modeler.create_line("TOP", [[0, 0], [100, 0]], 0.5, name="Polyline1")
    else:
        poly = aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")

    fx = aedtapp.post.fields_calculator.expressions
    aedtapp.create_setup()

    field = fx.vector("E")
    if aedtapp.design_type in ["Maxwell 3D", "Maxwell 2D"]:
        field = fx.vector("H")
    elif aedtapp.design_type == "Icepak":
        field = fx.vector("Temp")

    assert isinstance(field, VectorComplex)

    # Field magnitude integrated along the line, built as a typed chain instead of a string stack
    expr = field.magnitude().integrate(Line(poly.name))
    assert isinstance(expr, ScalarReal)

    name = expr.add("typed_voltage")
    assert name == "typed_voltage"
    assert aedtapp.post.fields_calculator.is_expression_defined("typed_voltage")


def test_expressions_constants_and_math_load(aedtapp) -> None:
    """Test that constant and math operation tokens load through the .clc path."""
    poly = aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
    fx = aedtapp.post.fields_calculator.expressions

    # exercises Scalar_Constant, Pow and a geometry reduction in one registration
    mag = fx.vector("E").magnitude()
    expr = (mag.power(2) * fx.scalar_constant(0.5)).integrate(Line(poly.name))
    name = expr.add("typed_energy")
    assert name == "typed_energy"
    assert aedtapp.post.fields_calculator.is_expression_defined("typed_energy")


def test_expressions_verify_rejects_malformed(aedtapp) -> None:
    """Test that a malformed expression is rejected before reaching AEDT."""
    fx = aedtapp.post.fields_calculator.expressions
    # a balanced, well-formed expression verifies successfully
    expr = fx.vector("E").magnitude()
    assert expr.verify() is expr
    # dot() requires two vectors -> a type error, never a malformed stack
    with pytest.raises(TypeError):
        from ansys.aedt.core.visualization.post.field_calculator_expressions import dot

        dot(fx.vector("E").magnitude(), fx.vector("E"))
