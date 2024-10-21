# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from typing import Any
from typing import List
from typing import Literal
from typing import Union

from pyaedt.modules.FieldCalculator import Abs
from pyaedt.modules.FieldCalculator import Acos
from pyaedt.modules.FieldCalculator import Asin
from pyaedt.modules.FieldCalculator import AtPhase
from pyaedt.modules.FieldCalculator import Atan
from pyaedt.modules.FieldCalculator import Atan2
from pyaedt.modules.FieldCalculator import CmplxImag
from pyaedt.modules.FieldCalculator import CmplxMag
from pyaedt.modules.FieldCalculator import CmplxPeak
from pyaedt.modules.FieldCalculator import CmplxReal
from pyaedt.modules.FieldCalculator import Conj
from pyaedt.modules.FieldCalculator import Cos
from pyaedt.modules.FieldCalculator import DerivativeX
from pyaedt.modules.FieldCalculator import DerivativeY
from pyaedt.modules.FieldCalculator import DerivativeZ
from pyaedt.modules.FieldCalculator import Domain
from pyaedt.modules.FieldCalculator import FieldCalculator
from pyaedt.modules.FieldCalculator import FieldExpressionArgument
from pyaedt.modules.FieldCalculator import Fraction
from pyaedt.modules.FieldCalculator import Grad
from pyaedt.modules.FieldCalculator import Imag
from pyaedt.modules.FieldCalculator import Integrate
from pyaedt.modules.FieldCalculator import Phase
from pyaedt.modules.FieldCalculator import Pow
from pyaedt.modules.FieldCalculator import Real
from pyaedt.modules.FieldCalculator import Sin
from pyaedt.modules.FieldCalculator import Smooth
from pyaedt.modules.FieldCalculator import Sqrt
from pyaedt.modules.FieldCalculator import StackBasedCalculator
from pyaedt.modules.FieldCalculator import Tan
from pyaedt.modules.FieldCalculator import VecX
from pyaedt.modules.FieldCalculator import VecY
from pyaedt.modules.FieldCalculator import VecZ
from pyaedt.modules.FieldCalculator import Vector
from pyaedt.modules.FieldCalculator import expression
from pyaedt.modules.FieldCalculator import line
from pyaedt.modules.FieldCalculator import ln
from pyaedt.modules.FieldCalculator import log
from pyaedt.modules.FieldCalculator import point
from pyaedt.modules.FieldCalculator import quantity
from pyaedt.modules.FieldCalculator import scalar
from pyaedt.modules.FieldCalculator import surface
from pyaedt.modules.FieldCalculator import volume


class MockCalculator(StackBasedCalculator):

    def __init__(self):
        self._call_sequence: List[List[Any]] = []

    @property
    def call_sequence(self) -> List[List[Any]]:
        return self._call_sequence

    def AddNamedExpression(self, expression_name: str, field_type: str) -> None:
        self._call_sequence.append(["AddNamedExpression", expression_name, field_type])

    def CalcOp(self, op: str) -> None:
        self._call_sequence.append(["CalcOp", op])

    def ClcMaterial(self, material: str, op: Union[Literal["mult"], Literal["div"]]) -> None:
        self._call_sequence.append(["ClcMaterial", material, op])

    def EnterComplex(self, complex: str):
        self._call_sequence.append(["EnterComplex", complex])

    def EnterComplexVector(self, complex_vector: List[str]):
        self._call_sequence.append(["EnterComplexVector", complex_vector])

    def EnterLine(self, name: str):
        self._call_sequence.append(["EnterLine", name])

    def EnterPoint(self, name: str):
        self._call_sequence.append(["EnterPoint", name])

    def EnterQty(self, name: str):
        self._call_sequence.append(["EnterQty", name])

    def EnterScalar(self, num: float):
        self._call_sequence.append(["EnterScalar", num])

    def EnterScalarFunc(self, name: str):
        self._call_sequence.append(["EnterScalarFunc", name])

    def EnterSurface(self, name: str):
        self._call_sequence.append(["EnterSurface", name])

    def EnterVector(self, vector: List[float]):
        self._call_sequence.append(["EnterVector", vector])

    def EnterVectorFunc(self, vector: List[str]):
        self._call_sequence.append(["EnterVectorFunc", vector])

    def EnterVol(self, name: str):
        self._call_sequence.append(["EnterVol", name])

    def CopyNamedExprToStack(self, name: str) -> None:
        self._call_sequence.append(["CopyNamedExprToStack", name])


def check_call_sequence(arg: FieldExpressionArgument, expected_call_sequence: List[List[Any]]) -> None:
    mock_calculator = MockCalculator()
    calculator = FieldCalculator(mock_calculator)
    calculator.add_named_expression("x", arg)
    expected_call_sequence.append(["AddNamedExpression", "x", "Fields"])
    assert mock_calculator.call_sequence == expected_call_sequence


def test_float():
    check_call_sequence(99.99, [["EnterScalar", 99.99]])


def test_int():
    check_call_sequence(99, [["EnterScalar", 99.00]])


def test_complex():
    check_call_sequence(complex(4, 5), [["EnterComplex", "4.0 + 5.0j"]])


def test_vector():
    check_call_sequence(Vector(2, 3, 4), [["EnterVector", [2.0, 3.0, 4.0]]])


def test_complex_vector():
    check_call_sequence(
        Vector(complex(4, 5), complex(6, 7), complex(8, 9)),
        [["EnterComplexVector", ["4.0 + 5.0j", "6.0 + 7.0j", "8.0 + 9.0j"]]],
    )


def test_quantity():
    check_call_sequence(quantity.A, [["EnterQty", "A"]])


def test_point():
    check_call_sequence(point.A, [["EnterPoint", "A"]])


def test_line():
    check_call_sequence(line.A, [["EnterLine", "A"]])


def test_surface():
    check_call_sequence(surface.A, [["EnterSurface", "A"]])


def test_volume():
    check_call_sequence(volume.A, [["EnterVol", "A"]])


def test_add():
    check_call_sequence(quantity.A + quantity.B, [["EnterQty", "A"], ["EnterQty", "B"], ["CalcOp", "+"]])


def test_add_float_left():
    check_call_sequence(99.99 + quantity.B, [["EnterScalar", 99.99], ["EnterQty", "B"], ["CalcOp", "+"]])


def test_add_float_right():
    check_call_sequence(quantity.A + 99.99, [["EnterQty", "A"], ["EnterScalar", 99.99], ["CalcOp", "+"]])


def test_sub():
    check_call_sequence(quantity.A - quantity.B, [["EnterQty", "A"], ["EnterQty", "B"], ["CalcOp", "-"]])


def test_sub_float_left():
    check_call_sequence(99.99 - quantity.B, [["EnterScalar", 99.99], ["EnterQty", "B"], ["CalcOp", "-"]])


def test_sub_float_right():
    check_call_sequence(quantity.A - 99.99, [["EnterQty", "A"], ["EnterScalar", 99.99], ["CalcOp", "-"]])


def test_mul():
    check_call_sequence(quantity.A * quantity.B, [["EnterQty", "A"], ["EnterQty", "B"], ["CalcOp", "*"]])


def test_mul_float_left():
    check_call_sequence(99.99 * quantity.B, [["EnterScalar", 99.99], ["EnterQty", "B"], ["CalcOp", "*"]])


def test_mul_float_right():
    check_call_sequence(quantity.A * 99.99, [["EnterQty", "A"], ["EnterScalar", 99.99], ["CalcOp", "*"]])


def test_div():
    check_call_sequence(quantity.A / quantity.B, [["EnterQty", "A"], ["EnterQty", "B"], ["CalcOp", "/"]])


def test_div_float_left():
    check_call_sequence(99.99 / quantity.B, [["EnterScalar", 99.99], ["EnterQty", "B"], ["CalcOp", "/"]])


def test_div_float_right():
    check_call_sequence(quantity.A / 99.99, [["EnterQty", "A"], ["EnterScalar", 99.99], ["CalcOp", "/"]])


def test_fraction_int():
    check_call_sequence(1 / quantity.B, [["EnterQty", "B"], ["CalcOp", "1/"]])


def test_fraction_float():
    check_call_sequence(1.0 / quantity.B, [["EnterQty", "B"], ["CalcOp", "1/"]])


def test_neg():
    check_call_sequence(-quantity.A, [["EnterQty", "A"], ["CalcOp", "Neg"]])


def test_pow():
    check_call_sequence(quantity.A**2, [["EnterQty", "A"], ["EnterScalar", 2], ["CalcOp", "Pow"]])


def test_powr():
    check_call_sequence(2**quantity.A, [["EnterScalar", 2], ["EnterQty", "A"], ["CalcOp", "Pow"]])


def test_vector_mul():
    check_call_sequence(Vector(1, 2, 3) * 2, [["EnterVector", [1.0, 2.0, 3.0]], ["EnterScalar", 2], ["CalcOp", "*"]])


def test_scalar_func():
    check_call_sequence(scalar.A, [["EnterScalarFunc", "A"]])


def test_scalar_vector_func():
    check_call_sequence(Vector(scalar.A, scalar.B, scalar.C), [["EnterVectorFunc", ["A", "B", "C"]]])


def test_abs():
    check_call_sequence(Abs(quantity.A), [["EnterQty", "A"], ["CalcOp", "Abs"]])


def test_smooth():
    check_call_sequence(Smooth(quantity.A), [["EnterQty", "A"], ["CalcOp", "Smooth"]])


def test_real():
    check_call_sequence(Real(quantity.A), [["EnterQty", "A"], ["CalcOp", "Real"]])


def test_imag():
    check_call_sequence(Imag(quantity.A), [["EnterQty", "A"], ["CalcOp", "Imag"]])


def test_cmplxmag():
    check_call_sequence(CmplxMag(quantity.A), [["EnterQty", "A"], ["CalcOp", "CmplxMag"]])


def test_domain():
    check_call_sequence(Domain(quantity.A), [["EnterQty", "A"], ["CalcOp", "Domain"]])


def test_phase():
    check_call_sequence(Phase(quantity.A), [["EnterQty", "A"], ["CalcOp", "Phase"]])


def test_conj():
    check_call_sequence(Conj(quantity.A), [["EnterQty", "A"], ["CalcOp", "Conj"]])


def test_at_phase():
    check_call_sequence(AtPhase(quantity.A), [["EnterQty", "A"], ["CalcOp", "AtPhase"]])


def test_complxr():
    check_call_sequence(CmplxReal(quantity.A), [["EnterQty", "A"], ["CalcOp", "CmplxR"]])


def test_complxi():
    check_call_sequence(CmplxImag(quantity.A), [["EnterQty", "A"], ["CalcOp", "CmplxI"]])


def test_complx_peak():
    check_call_sequence(CmplxPeak(quantity.A), [["EnterQty", "A"], ["CalcOp", "CmplxPeak"]])


def test_vec_x():
    check_call_sequence(VecX(quantity.A), [["EnterQty", "A"], ["CalcOp", "VecX"]])


def test_vec_y():
    check_call_sequence(VecY(quantity.A), [["EnterQty", "A"], ["CalcOp", "VecY"]])


def test_vec_z():
    check_call_sequence(VecZ(quantity.A), [["EnterQty", "A"], ["CalcOp", "VecZ"]])


def test_fraction():
    check_call_sequence(Fraction(quantity.A), [["EnterQty", "A"], ["CalcOp", "1/"]])


def test_pow_function():
    check_call_sequence(Pow(quantity.A, quantity.B), [["EnterQty", "A"], ["EnterQty", "B"], ["CalcOp", "Pow"]])


def test_sqrt():
    check_call_sequence(Sqrt(quantity.A), [["EnterQty", "A"], ["CalcOp", "Sqrt"]])


def test_sin():
    check_call_sequence(Sin(quantity.A), [["EnterQty", "A"], ["CalcOp", "Sin"]])


def test_cos():
    check_call_sequence(Cos(quantity.A), [["EnterQty", "A"], ["CalcOp", "Cos"]])


def test_tan():
    check_call_sequence(Tan(quantity.A), [["EnterQty", "A"], ["CalcOp", "Tan"]])


def test_asin():
    check_call_sequence(Asin(quantity.A), [["EnterQty", "A"], ["CalcOp", "Asin"]])


def test_acos():
    check_call_sequence(Acos(quantity.A), [["EnterQty", "A"], ["CalcOp", "Acos"]])


def test_atan():
    check_call_sequence(Atan(quantity.A), [["EnterQty", "A"], ["CalcOp", "Atan"]])


def test_atan2():
    check_call_sequence(Atan2(quantity.A, quantity.B), [["EnterQty", "A"], ["EnterQty", "B"], ["CalcOp", "Atan2"]])


def test_d_dx():
    check_call_sequence(DerivativeX(quantity.A), [["EnterQty", "A"], ["CalcOp", "d/dx"]])


def test_d_dy():
    check_call_sequence(DerivativeY(quantity.A), [["EnterQty", "A"], ["CalcOp", "d/dy"]])


def test_d_dz():
    check_call_sequence(DerivativeZ(quantity.A), [["EnterQty", "A"], ["CalcOp", "d/dz"]])


def test_integrate():
    check_call_sequence(Integrate(line.A, quantity.B), [["EnterLine", "A"], ["EnterQty", "B"], ["CalcOp", "Integrate"]])


def test_grad():
    check_call_sequence(Grad(quantity.A), [["EnterQty", "A"], ["CalcOp", "Grad"]])


def test_ln():
    check_call_sequence(ln(quantity.A), [["EnterQty", "A"], ["CalcOp", "ln"]])


def test_log():
    check_call_sequence(log(quantity.A), [["EnterQty", "A"], ["CalcOp", "log"]])


def test_use_of_named_expression():
    check_call_sequence(expression.A, [["CopyNamedExprToStack", "A"]])


def test_complicated_expression():
    check_call_sequence(
        (
            Integrate(quantity.Energy, surface.HV) * scalar.HV_mean_turn_length
            + Integrate(quantity.Energy, surface.LV) * scalar.LV_mean_turn_length
            + Integrate(quantity.Energy, surface.region) * scalar.HV_LV_gap_length
        )
        * 2
        / (scalar.HV_current * scalar.HV_current),
        [
            ["EnterQty", "Energy"],
            ["EnterSurface", "HV"],
            ["CalcOp", "Integrate"],
            ["EnterScalarFunc", "HV_mean_turn_length"],
            ["CalcOp", "*"],
            ["EnterQty", "Energy"],
            ["EnterSurface", "LV"],
            ["CalcOp", "Integrate"],
            ["EnterScalarFunc", "LV_mean_turn_length"],
            ["CalcOp", "*"],
            ["CalcOp", "+"],
            ["EnterQty", "Energy"],
            ["EnterSurface", "region"],
            ["CalcOp", "Integrate"],
            ["EnterScalarFunc", "HV_LV_gap_length"],
            ["CalcOp", "*"],
            ["CalcOp", "+"],
            ["EnterScalar", 2],
            ["CalcOp", "*"],
            ["EnterScalarFunc", "HV_current"],
            ["EnterScalarFunc", "HV_current"],
            ["CalcOp", "*"],
            ["CalcOp", "/"],
        ],
    )
