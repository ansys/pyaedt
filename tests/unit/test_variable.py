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

import pytest

from ansys.aedt.core.application.variables import Variable
from ansys.aedt.core.application.variables import generate_validation_errors
from ansys.aedt.core.generic.numbers_utils import decompose_variable_value
from ansys.aedt.core.generic.numbers_utils import is_close


@pytest.fixture()
def validation_input():
    property_names = [
        "+X Padding Type",
        "+X Padding Data",
        "-X Padding Type",
        "-X Padding Data",
        "+Y Padding Type",
        "+Y Padding Data",
        "-Y Padding Type",
        "-Y Padding Data",
        "+Z Padding Type",
        "+Z Padding Data",
        "-Z Padding Type",
        "-Z Padding Data",
    ]
    expected_settings = [
        "Absolute Offset",
        "10mm",
        "Percentage Offset",
        "100",
        "Transverse Percentage Offset",
        "100",
        "Percentage Offset",
        "10",
        "Absolute Offset",
        "50mm",
        "Absolute Position",
        "-600mm",
    ]
    actual_settings = list(expected_settings)
    return property_names, expected_settings, actual_settings


@pytest.fixture()
def validation_float_input():
    property_names = ["+X Padding Data", "-X Padding Data", "+Y Padding Data"]
    expected_settings = [100, 200.1, 300]
    actual_settings = list(expected_settings)
    return property_names, expected_settings, actual_settings


def test_variable_class():
    v = Variable("4mm")
    num_value = v.numeric_value
    assert num_value == 4.0

    v = v.rescale_to("meter")
    assert v.evaluated_value == "0.004meter"
    assert v.numeric_value == 0.004
    assert v.si_value == v.numeric_value

    v = Variable("100cel")
    assert v.numeric_value == 100.0
    assert v.evaluated_value == "100.0cel"
    assert v.si_value == 373.15
    v.rescale_to("fah")
    assert v.numeric_value == 212.0

    v = Variable("30dBW")
    assert v.numeric_value == 30.0
    assert v.evaluated_value == "30.0dBW"
    assert v.si_value == 1000
    v.rescale_to("megW")
    assert v.numeric_value == 0.001
    assert v.evaluated_value == "0.001megW"
    assert v.si_value == 1000

    v = Variable("10dBm")
    assert v.numeric_value == 10.0
    assert v.evaluated_value == "10.0dBm"
    assert v.si_value == 0.01
    v.rescale_to("W")
    assert v.numeric_value == 0.01
    assert v.evaluated_value == "0.01W"
    assert v.si_value == 0.01

    with pytest.raises(ValueError):
        _ = Variable("4", units="invented")


def test_multiplication():
    v1 = Variable("10mm")
    v2 = Variable(3)
    v3 = Variable("3mA")
    v4 = Variable("40V")
    v5 = Variable("100NewtonMeter")
    v6 = Variable("1000rpm")
    tol = 1e-4
    result_1 = v1 * v2

    result_2 = v2 * v3
    result_3 = v3 * v4
    result_4 = v4 * v3
    result_5 = v4 * 24.0 * v3
    result_6 = v5 * v6
    result_7 = v6 * v5
    result_8 = (v5 * v6).rescale_to("kW")
    assert result_1.numeric_value == 30.0
    assert result_1.unit_system == "Length"

    assert result_2.numeric_value == 9.0
    assert result_2.units == "mA"
    assert result_2.unit_system == "Current"

    assert result_3.numeric_value == 0.12
    assert result_3.units == "W"
    assert result_3.unit_system == "Power"

    assert result_4.numeric_value == 0.12
    assert result_4.units == "W"
    assert result_4.unit_system == "Power"

    assert result_5.numeric_value == 2.88
    assert result_5.units == "W"
    assert result_5.unit_system == "Power"

    assert abs(result_6.numeric_value - 10471.9755) / result_6.numeric_value < tol
    assert result_6.units == "W"
    assert result_6.unit_system == "Power"

    assert abs(result_7.numeric_value - 10471.9755) / result_4.numeric_value < tol
    assert result_7.units == "W"
    assert result_7.unit_system == "Power"

    assert abs(result_8.numeric_value - 10.4719755) / result_8.numeric_value < tol
    assert result_8.units == "kW"
    assert result_8.unit_system == "Power"


def test_addition():
    v1 = Variable("10mm")
    v2 = Variable(3)
    v3 = Variable("3mA")
    v4 = Variable("10A")
    with pytest.raises(ValueError):
        _ = v1 + v2

    with pytest.raises(ValueError):
        _ = v2 + v1
    result_1 = v2 + v2
    result_2 = v3 + v4
    result_3 = v3 + v3

    assert result_1.numeric_value == 6.0
    assert result_1.unit_system == "None"

    assert result_2.numeric_value == 10.003
    assert result_2.units == "A"
    assert result_2.unit_system == "Current"

    assert result_3.numeric_value == 6.0
    assert result_3.units == "mA"
    assert result_3.unit_system == "Current"


def test_subtraction():
    v1 = Variable("10mm")
    v2 = Variable(3)
    v3 = Variable("3mA")
    v4 = Variable("10A")

    with pytest.raises(ValueError):
        _ = v1 - v2

    with pytest.raises(ValueError):
        _ = v2 - v1

    result_1 = v2 - v2
    result_2 = v3 - v4
    result_3 = v3 - v3

    assert result_1.numeric_value == 0.0
    assert result_1.unit_system == "None"

    assert result_2.numeric_value == -9.997
    assert result_2.units == "A"
    assert result_2.unit_system == "Current"

    assert result_3.numeric_value == 0.0
    assert result_3.units == "mA"
    assert result_3.unit_system == "Current"


def test_specify_units():
    # Scaling of the unit system "Angle"
    angle = Variable("1rad")
    angle.rescale_to("deg")
    assert is_close(angle.numeric_value, 57.29577951308232)
    angle.rescale_to("degmin")
    assert is_close(angle.numeric_value, 57.29577951308232 * 60.0)
    angle.rescale_to("degsec")
    assert is_close(angle.numeric_value, 57.29577951308232 * 3600.0)

    # Convert 200Hz to Angular speed numerically
    omega = Variable(200 * math.pi * 2, "rad_per_sec")
    assert omega.unit_system == "AngularSpeed"
    assert is_close(omega.si_value, 1256.6370614359173)
    omega.rescale_to("rpm")
    assert is_close(omega.numeric_value, 12000.0)
    omega.rescale_to("rev_per_sec")
    assert is_close(omega.numeric_value, 200.0)

    # test speed times time equals diestance
    v = Variable("100m_per_sec")
    assert v.unit_system == "Speed"
    v.rescale_to("feet_per_sec")
    assert is_close(v.numeric_value, 328.08398950131)
    v.rescale_to("feet_per_min")
    assert is_close(v.numeric_value, 328.08398950131 * 60)
    v.rescale_to("miles_per_sec")
    assert is_close(v.numeric_value, 0.06213711723534)
    v.rescale_to("miles_per_minute")
    assert is_close(v.numeric_value, 3.72822703412)
    v.rescale_to("miles_per_hour")
    assert is_close(v.numeric_value, 223.69362204724)

    t = Variable("20s")
    distance = v * t
    assert distance.unit_system == "Length"
    assert distance.evaluated_value == "2000.0meter"
    distance.rescale_to("in")
    assert is_close(distance.numeric_value, 2000 / 0.0254)


def test_division():
    """
    'Power_divide_Voltage': 'Current',
    'Power_divide_Current': 'Voltage',
    'Power_divide_AngularSpeed': 'Torque',
    'Power_divide_Torque': 'Angular_Speed',
    'Angle_divide_AngularSpeed': 'Time',
    'Angle_divide_Time': 'AngularSpeed',
    'Voltage_divide_Current': 'Resistance',
    'Voltage_divide_Resistance': 'Current',
    'Resistance_divide_AngularSpeed': 'Inductance',
    'Resistance_divide_Inductance': 'AngularSpeed',
    'None_divide_Freq': 'Time',
    'None_divide_Time': 'Freq',
    'Length_divide_Time': 'Speed',
    'Length_divide_Speed': 'Time'
    """
    v1 = Variable("10W")
    v2 = Variable("40V")
    v3 = Variable("1s")
    v4 = Variable("5mA")
    v5 = Variable("100NewtonMeter")
    v6 = Variable("1000rpm")
    tol = 1e-4

    result_1 = v1 / v2
    assert result_1.numeric_value == 0.25
    assert result_1.units == "A"
    assert result_1.unit_system == "Current"

    result_2 = v2 / result_1
    assert result_2.numeric_value == 160.0
    assert result_2.units == "ohm"
    assert result_2.unit_system == "Resistance"

    result_3 = 3 / v3
    assert result_3.numeric_value == 3.0
    assert result_3.units == "Hz"
    assert result_3.unit_system == "Freq"

    result_4 = v3 / 2
    assert abs(result_4.numeric_value - 0.5) < tol
    assert result_4.units == "s"
    assert result_4.unit_system == "Time"

    result_5 = v4 / v5
    assert abs(result_5.numeric_value - 0.00005) < tol
    assert result_5.units == ""
    assert result_5.unit_system == "None"

    result_6 = v1 / v5 + v6
    assert abs(result_6.numeric_value - 104.8198) / result_6.numeric_value < tol
    assert result_6.units == "rad_per_sec"
    assert result_6.unit_system == "AngularSpeed"


def test_decompose_variable_value():
    assert decompose_variable_value("3.123456m") == (3.123456, "m")
    assert decompose_variable_value("3m") == (3, "m")
    assert decompose_variable_value("3") == (3, "")
    assert decompose_variable_value("3.") == (3.0, "")
    assert decompose_variable_value("3.123456m2") == (3.123456, "m2")
    assert decompose_variable_value("3.123456Nm-2") == (3.123456, "Nm-2")
    assert decompose_variable_value("3.123456kg2m2") == (3.123456, "kg2m2")
    assert decompose_variable_value("3.123456kgm2") == (3.123456, "kgm2")


def test_validator_exact_match(validation_input):
    property_names, expected_settings, actual_settings = validation_input
    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)
    assert len(validation_errors) == 0


def test_validator_tolerance(validation_input):
    property_names, expected_settings, actual_settings = validation_input

    # Small difference should produce no validation errors
    actual_settings[1] = "10.0000000001mm"
    actual_settings[3] = "100.0000000001"
    actual_settings[5] = "100.0000000001"
    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 0


def test_validator_invalidate_offset_type(validation_input):
    property_names, expected_settings, actual_settings = validation_input

    # Are expected to be "Absolute Offset"
    actual_settings[0] = "Percentage Offset"

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 1


def test_validator_invalidate_value(validation_input):
    property_names, expected_settings, actual_settings = validation_input

    # Above tolerance
    actual_settings[1] = "10.000002mm"

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 1


def test_validator_invalidate_unit(validation_input):
    property_names, expected_settings, actual_settings = validation_input

    actual_settings[1] = "10in"

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 1


def test_validator_invalidate_multiple(validation_input):
    property_names, expected_settings, actual_settings = validation_input

    actual_settings[0] = "Percentage Offset"
    actual_settings[1] = "22mm"
    actual_settings[2] = "Transverse Percentage Offset"

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 3


def test_validator_invalidate_wrong_type(validation_input):
    property_names, expected_settings, actual_settings = validation_input

    actual_settings[1] = "nonnumeric"

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 1


def test_validator_float_type(validation_float_input):
    property_names, expected_settings, actual_settings = validation_float_input

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 0


def test_validator_float_type_tolerance(validation_float_input):
    property_names, expected_settings, actual_settings = validation_float_input

    # Set just below the tolerance to pass the check
    actual_settings[0] *= 1 + 0.99 * 1e-9
    actual_settings[1] *= 1 - 0.99 * 1e-9
    actual_settings[2] *= 1 + 0.99 * 1e-9

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 0


def test_validator_float_type_invalidate(validation_float_input):
    property_names, expected_settings, actual_settings = validation_float_input

    # Set just above the tolerance to fail the check
    actual_settings[0] *= 1 + 1.01 * 1e-9
    actual_settings[1] *= 1 + 1.01 * 1e-9
    actual_settings[2] *= 1 + 1.01 * 1e-9

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 3


def test_validator_float_type_invalidate_zeros(validation_float_input):
    property_names, expected_settings, actual_settings = validation_float_input

    actual_settings[0] *= 2

    validation_errors = generate_validation_errors(property_names, expected_settings, actual_settings)

    assert len(validation_errors) == 1
