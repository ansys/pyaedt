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

from __future__ import absolute_import

from enum import IntEnum
from enum import auto
import math
import warnings

from ansys.aedt.core.generic.settings import settings

RAD2DEG = 180.0 / math.pi
"""Rad 2 deg."""
DEG2RAD = math.pi / 180
"""Deg 2 rad."""
HOUR2SEC = 3600.0
"""Hour 2 sec."""
MIN2SEC = 60.0
"""Min 2 sec."""
SEC2MIN = 1 / 60.0
"""Sec 2 min."""
SEC2HOUR = 1 / 3600.0
"""Sec 2 hour."""
INV2PI = 0.5 / math.pi
"""Inv 2 pi."""
V2PI = 2.0 * math.pi
"""V 2 pi."""
METER2IN = 0.0254
"""Meter 2 in."""
METER2MILES = 1609.344051499
"""Meter 2 miles."""
MILS2METER = 39370.078740157
"""Mils 2 meter."""
SpeedOfLight = 299792458.0
"""Value for speed of light."""


def db20(x: float, inverse: bool = True) -> float:
    """
    Convert db20 to decimal and vice versa.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import db20
    >>> db20(0.5)

    """
    if inverse:
        return 20 * math.log10(x)
    else:
        return math.pow(10, x / 20.0)


def db10(x: float, inverse: bool = True) -> float:
    """
    Convert db10 to decimal and vice versa.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import db10
    >>> db10(10.0)

    """
    if inverse:
        return 10 * math.log10(x)
    else:
        return math.pow(10, x / 10.0)


def dbw(x: float, inverse: bool = True) -> float:
    """
    Convert W to decimal and vice versa.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import dbw
    >>> dbw(1.0)

    """
    if inverse:
        return 10 * math.log10(x)
    else:
        return math.pow(10, x / 10.0)


def dbm(x: float, inverse: bool = True) -> float:
    """
    Convert W to decimal and vice versa.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import dbm
    >>> dbm(1.0)

    """
    if inverse:
        return 10 * math.log10(x) + 30
    else:
        return math.pow(10, x / 10.0) / 1000


def fah2kel(val: float, inverse: bool = True) -> float:
    """
    Convert a temperature from Fahrenheit to Kelvin.

    Parameters
    ----------
    val : float
        Temperature value in Fahrenheit.
    inverse : bool, optional
        The default is ``True``.

    Returns
    -------
    float
        Temperature value converted to Kelvin.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import fah2kel
    >>> fah2kel(32.0, inverse=False)

    """
    if inverse:
        return (val - 273.15) * 9 / 5 + 32
    else:
        return (val - 32) * 5 / 9 + 273.15


def cel2kel(val: float, inverse: bool = True) -> float:
    """
    Convert a temperature from Celsius to Kelvin.

    Parameters
    ----------
    val : float
        Temperature value in Celsius.
    inverse : bool, optional
        The default is ``True``.

    Returns
    -------
    float
        Temperature value converted to Kelvin.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import cel2kel
    >>> cel2kel(25.0, inverse=False)

    """
    if inverse:
        return val - 273.15
    else:
        return val + 273.15


def unit_system(units: str) -> str | bool:
    """
    Retrieve the name of the unit system associated with a unit string.

    Parameters
    ----------
    units : str
        Units for retrieving the associated unit system name.

    Returns
    -------
    str
        Key from the ``AEDT_units`` when successful. For example, ``"AngularSpeed"``.
    ``False`` when the units specified are not defined in AEDT units.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import unit_system
    >>> unit_system("mm")

    """
    for unit_type, unit_dict in AEDT_UNITS.items():
        if units.lower() in [i.lower() for i in unit_dict.keys()]:
            return unit_type

    return False


def _resolve_unit_system(unit_system_1: str, unit_system_2: str, operation: str) -> str:
    """
    Retrieve the unit string of an arithmetic operation on ``Variable`` objects.

    If no resulting unit system is defined for a specific operation (in unit_system_operations),
    an empty string is returned.

    Parameters
    ----------
    unit_system_1 : str
        Name of a unit system, which is a key of ``AEDT_units``.
    unit_system_2 : str
        Name of another unit system, which is a key of ``AEDT_units``.
    operation : str
        Name of an operator within the data set of ``["multiply" ,"divide"]``.

    Returns
    -------
    str
        Unit system when successful, ``""`` when failed.
    """
    try:
        key = f"{unit_system_1}_{operation}_{unit_system_2}"
        result_unit_system = UNIT_SYSTEM_OPERATIONS[key]
        return SI_UNITS[result_unit_system]
    except KeyError:
        return ""


def unit_converter(
    values: float | list, unit_system: str = "Length", input_units: str = "meter", output_units: str = "mm"
) -> float | list:
    """
    Convert unit in specified unit system.

    Parameters
    ----------
    values : float, list
        Values to convert.
    unit_system : str
        Unit system. Default is `"Length"`.
    input_units : str
        Input units. Default is `"meter"`.
    output_units : str
        Output units. Default is `"mm"`.

    Returns
    -------
    float, list
        Converted value.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import unit_converter
    >>> unit_converter(1.0, unit_system="Length", input_units="meter", output_units="mm")

    """
    if unit_system in AEDT_UNITS:
        if input_units not in AEDT_UNITS[unit_system]:
            warnings.warn(f"Unknown units: '{input_units}'")
            return values
        elif output_units not in AEDT_UNITS[unit_system]:
            warnings.warn(f"Unknown units: '{output_units}'")
            return values
        else:
            input_is_list = isinstance(values, list)
            if not input_is_list:
                values = [values]
            converted_values = []
            for value in values:
                if unit_system == "Temperature":
                    value = AEDT_UNITS[unit_system][input_units](value, False)
                    value = AEDT_UNITS[unit_system][output_units](value, output_units != "kel")
                elif not callable(AEDT_UNITS[unit_system][input_units]) and not callable(
                    AEDT_UNITS[unit_system][output_units]
                ):
                    value = value * AEDT_UNITS[unit_system][input_units] / AEDT_UNITS[unit_system][output_units]
                elif not callable(AEDT_UNITS[unit_system][input_units]) and callable(
                    AEDT_UNITS[unit_system][output_units]
                ):
                    value = value * AEDT_UNITS[unit_system][input_units]
                    value = AEDT_UNITS[unit_system][output_units](value, True)
                elif callable(AEDT_UNITS[unit_system][input_units]) and not callable(
                    AEDT_UNITS[unit_system][output_units]
                ):
                    value = AEDT_UNITS[unit_system][input_units](value, False) / AEDT_UNITS[unit_system][output_units]
                else:
                    value = AEDT_UNITS[unit_system][input_units](value, False)
                    value = AEDT_UNITS[unit_system][output_units](value, True)

                converted_values.append(value)
            if input_is_list:
                return converted_values
            else:
                return converted_values[0]
    warnings.warn("No system unit found")
    return values


def scale_units(scale_to_unit: str) -> float:
    """
    Find the scale_to_unit into main system unit.

    Parameters
    ----------
    scale_to_unit : str
        Unit to Scale.

    Returns
    -------
    float
        Return the scaling factor if any.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import scale_units
    >>> scale_units("mm")

    """
    sunit = 1.0
    for val in list(AEDT_UNITS.values()):
        for unit, scale_val in val.items():
            if scale_to_unit.lower() == unit.lower():
                sunit = scale_val
                break
        else:
            continue
        break
    return sunit


def validate_enum_class_value(cls, value: int) -> bool:
    """
    Check whether the value for the class ``enumeration-class`` is valid.

    Parameters
    ----------
    cls : class
        Enumeration-style class with integer members in range(0, N) where cls.Invalid equals N-1.
    value : int
        Value to check.

    Returns
    -------
    bool
        ``True`` when the value is valid for the ``enumeration-class``, ``False`` otherwise.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import validate_enum_class_value
    >>> class ExampleEnum:
    ...     A = 0
    ...     B = 1
    ...     Invalid = 2
    >>> validate_enum_class_value(ExampleEnum, 1)

    """
    return isinstance(value, int) and value >= 0 and value < cls.Invalid


AEDT_UNITS = {
    "AngularSpeed": {
        "deg_per_hr": HOUR2SEC * DEG2RAD,
        "rad_per_hr": HOUR2SEC,
        "deg_per_min": MIN2SEC * DEG2RAD,
        "rad_per_min": MIN2SEC,
        "deg_per_sec": DEG2RAD,
        "rad_per_sec": 1.0,
        "rev_per_sec": V2PI,
        "per_sec": V2PI,
        "rpm": SEC2MIN * V2PI,
    },
    "Angle": {"deg": DEG2RAD, "rad": 1.0, "degmin": DEG2RAD * SEC2MIN, "degsec": DEG2RAD * SEC2HOUR},
    "Area": {
        "fm2": 1e-30,
        "pm2": 1e-24,
        "nm2": 1e-18,
        "um2": 1e-12,
        "mm2": 1e-6,
        "cm2": 1e-4,
        "dm2": 1e-2,
        "m2": 1.0,
        "meter2": 1.0,
        "km2": 1e6,
        "uin2": METER2IN * 1e-12,
        "mil2": METER2IN * 1e-6,
        "in2": METER2IN,
        "ft2": METER2IN * 24,
        "yd2": METER2IN * 288,
    },
    "Capacitance": {"fF": 1e-15, "pF": 1e-12, "nF": 1e-9, "uF": 1e-6, "mF": 1e-3, "F": 1.0},
    "Conductance": {"fSie": 1e-15, "pSie": 1e-12, "nSie": 1e-9, "uSie": 1e-6, "mSie": 1e-3, "Sie": 1.0},
    "Current": {
        "fA": 1e-15,
        "pA": 1e-12,
        "nA": 1e-9,
        "uA": 1e-6,
        "mA": 1e-3,
        "A": 1.0,
        "kA": 1e3,
        "MegA": 1e6,
        "gA": 1e9,
        "dBA": (db20,),
    },
    "Flux": {"Wb": 1.0, "mx": 1e-8, "vh": 3600, "vs": 1.0},
    "Force": {
        "fNewton": 1e-15,
        "pNewton": 1e-12,
        "nNewton": 1e-9,
        "uNewton": 1e-6,
        "mNewton": 1e-3,
        "newton": 1.0,
        "kNewton": 1e3,
        "megNewton": 1e6,
        "gNewton": 1e9,
        "dyne": 1e-5,
        "kp": 9.80665,
        "PoundsForce": 4.44822,
    },
    "Freq": {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9, "THz": 1e12, "rps": 1.0, "per_sec": 1.0},
    "Frequency": {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9, "THz": 1e12, "rps": 1.0, "per_sec": 1.0},
    "Inductance": {"fH": 1e-15, "pH": 1e-12, "nH": 1e-9, "uH": 1e-6, "mH": 1e-3, "H": 1.0},
    "Length": {
        "fm": 1e-15,
        "pm": 1e-12,
        "nm": 1e-9,
        "um": 1e-6,
        "mm": 1e-3,
        "cm": 1e-2,
        "dm": 1e-1,
        "meter": 1.0,
        "km": 1e3,
        "uin": METER2IN * 1e-6,
        "mil": METER2IN * 1e-3,
        "in": METER2IN,
        "ft": METER2IN * 12,
        "yd": METER2IN * 36,
        "mile": METER2IN * 63360,
    },
    "Mass": {"ug": 1e-9, "mg": 1e-6, "g": 1e-3, "kg": 1.0, "ton": 1000, "oz": 0.0283495, "lb": 0.453592},
    "None": {
        "f": 1e-15,
        "p": 1e-12,
        "n": 1e-9,
        "u": 1e-6,
        "m": 1e-3,
        "": 1.0,
        "k": 1e3,
        "meg": 1e6,
        "g": 1e9,
        "t": 1e12,
    },
    "Resistance": {"uOhm": 1e-6, "mOhm": 1e-3, "ohm": 1.0, "kOhm": 1e3, "megohm": 1e6, "GOhm": 1e9},
    "Speed": {
        "mm_per_sec": 1e-3,
        "cm_per_sec": 1e-2,
        "m_per_sec": 1.0,
        "km_per_sec": 1e3,
        "inches_per_sec": METER2IN,
        "feet_per_sec": METER2IN * 12,
        "feet_per_min": METER2IN * 12 * SEC2MIN,
        "km_per_min": 60e3,
        "m_per_h": 3600,
        "miles_per_hour": METER2MILES * SEC2HOUR,
        "miles_per_minute": METER2MILES * SEC2MIN,
        "miles_per_sec": METER2MILES,
    },
    "Time": {
        "fs": 1e-15,
        "ps": 1e-12,
        "ns": 1e-9,
        "us": 1e-6,
        "ms": 1e-3,
        "s": 1,
        "min": 60,
        "hour": 3600,
        "day": 3600 * 12,
    },
    "Torque": {
        "fNewtonMeter": 1e-15,
        "pNewtonMeter": 1e-12,
        "nNewtonMeter": 1e-9,
        "uNewtonMeter": 1e-6,
        "mNewtonMeter": 1e-3,
        "cNewtonMeter": 1e-2,
        "NewtonMeter": 1,
        "kNewtonMeter": 1e3,
        "megNewtonMeter": 1e6,
        "gNewtonMeter": 1e9,
    },
    "Voltage": {
        "fV": 1e-15,
        "pV": 1e-12,
        "nV": 1e-9,
        "uV": 1e-6,
        "mV": 1e-3,
        "V": 1.0,
        "kV": 1e3,
        "MegV": 1e6,
        "gV": 1e9,
        "dBV": db20,
    },
    "Temperature": {"kel": lambda x, y: x, "cel": cel2kel, "fah": fah2kel},
    "Power": {
        "fW": 1e-15,
        "pW": 1e-12,
        "nW": 1e-9,
        "uW": 1e-6,
        "mW": 1e-3,
        "W": 1.0,
        "kW": 1e3,
        "megW": 1e6,
        "gW": 1e9,
        "Btu_per_hr": 3.4129693,
        "Btu_per_sec": 9.48047e-4,
        "dBm": dbm,
        "dBW": dbw,
        "HP": 1.34102e-3,
        "erg_per_sec": 1e7,
    },
    "Pressure": {
        "n_per_meter_sq": 1.0,
        "kn_per_meter_sq": 1e3,
        "megn_per_meter_sq": 1e6,
        "gn_per_meter_sq": 1e9,
        "lbf_per_ft2": 2.09e-2,
        "psi": 1.45e-4,
    },
    "B-field": {
        "ftesla": 1e-15,
        "ptesla": 1e-12,
        "ntesla": 1e-9,
        "utesla": 1e-6,
        "mtesla": 1e-3,
        "tesla": 1.0,
        "ktesla": 1e3,
        "megtesla": 1e6,
        "gtesla": 1e9,
    },
    "E-field": {
        "fV_per_m": 1e-15,
        "pV_per_m": 1e-12,
        "nV_per_m": 1e-9,
        "uV_per_m": 1e-6,
        "mV_per_m": 1e-3,
        "V_per_m": 1.0,
        "kV_per_m": 1e3,
        "megV_per_m": 1e6,
        "gV_per_m": 1e9,
        "fV_per_meter": 1e-15,
        "pV_per_meter": 1e-12,
        "nV_per_meter": 1e-9,
        "uV_per_meter": 1e-6,
        "mV_per_meter": 1e-3,
        "V_per_meter": 1.0,
        "kV_per_meter": 1e3,
        "megV_per_meter": 1e6,
        "gV_per_meter": 1e9,
    },
    "H-field": {
        "fA_per_m": 1e-15,
        "pA_per_m": 1e-12,
        "nA_per_m": 1e-9,
        "uA_per_m": 1e-6,
        "mA_per_m": 1e-3,
        "A_per_m": 1.0,
        "kA_per_m": 1e3,
        "megA_per_m": 1e6,
        "gA_per_m": 1e9,
        "fA_per_meter": 1e-15,
        "pA_per_meter": 1e-12,
        "nA_per_meter": 1e-9,
        "uA_per_meter": 1e-6,
        "mA_per_meter": 1e-3,
        "A_per_meter": 1.0,
        "kA_per_meter": 1e3,
        "megA_per_meter": 1e6,
        "gA_per_meter": 1e9,
    },
    "SurfaceHeat": {
        "uW_per_m2": 1e-6,
        "mW_per_m2": 1e-3,
        "irrad_W_per_m2": 1.0,
        "W_per_m2": 1.0,
        "kW_per_m2": 1e3,
        "megW_per_m2": 1e6,
        "irrad_W_per_cm2": 1e4,
        "W_per_cm2": 1e4,
        "W_per_in2": 1550,
        "erg_per_s_per_cm2": 1e-3,
        "btu_per_hr_per_ft2": 3.15,
        "btu_per_s_per_ft2": 11356.53,
        "irrad_W_per_mm2": 1e6,
        "irrad_met": 1.0,
    },
    "J-field": {
        "fA_per_m2": 1e-15,
        "pA_per_m2": 1e-12,
        "nA_per_m2": 1e-9,
        "uA_per_m2": 1e-6,
        "mA_per_m2": 1e-3,
        "A_per_m2": 1.0,
        "kA_per_m2": 1e3,
        "megA_per_m2": 1e6,
        "gA_per_m2": 1e9,
        "fA_per_meter2": 1e-15,
        "pA_per_meter2": 1e-12,
        "nA_per_meter2": 1e-9,
        "uA_per_meter2": 1e-6,
        "mA_per_meter2": 1e-3,
        "A_per_meter2": 1.0,
        "kA_per_meter2": 1e3,
        "megA_per_meter2": 1e6,
        "gA_per_meter2": 1e9,
    },
}
"""AEDT units."""
SI_UNITS = {
    "AngularSpeed": "rad_per_sec",
    "Angle": "rad",
    "Area": "m2",
    "Capacitance": "F",
    "Conductance": "Sie",
    "Current": "A",
    "Flux": "vs",
    "Force": "newton",
    "Freq": "Hz",
    "Inductance": "H",
    "Length": "meter",
    "Mass": "kg",
    "None": "",
    "Resistance": "ohm",
    "Speed": "m_per_sec",
    "SurfaceHeat": "W_per_m2",
    "Time": "s",
    "Torque": "NewtonMeter",
    "Voltage": "V",
    "Temperature": "kel",
    "Power": "W",
    "B-field": "tesla",
    "E-field": "V_per_meter",
    "H-field": "A_per_meter",
    "J-field": "A_per_m2",
}
"""Si units."""
UNIT_SYSTEM_OPERATIONS = {
    # Multiplication of physical domains
    "Voltage_multiply_Current": "Power",
    "Torque_multiply_AngularSpeed": "Power",
    "AngularSpeed_multiply_Time": "Angle",
    "Current_multiply_Resistance": "Voltage",
    "AngularSpeed_multiply_Inductance": "Resistance",
    "Speed_multiply_Time": "Length",
    # Division of Physical Domains
    "Power_divide_Voltage": "Current",
    "Power_divide_Current": "Voltage",
    "Power_divide_AngularSpeed": "Torque",
    "Power_divide_Torque": "AngularSpeed",
    "Angle_divide_AngularSpeed": "Time",
    "Angle_divide_Time": "AngularSpeed",
    "Voltage_divide_Current": "Resistance",
    "Voltage_divide_Resistance": "Current",
    "Resistance_divide_AngularSpeed": "Inductance",
    "Resistance_divide_Inductance": "AngularSpeed",
    "None_divide_Freq": "Time",
    "None_divide_Time": "Freq",
    "Length_divide_Time": "Speed",
    "Length_divide_Speed": "Time",
}
"""Unit system operations."""

CSS4_COLORS = {
    "chocolate": "#D2691E",
    "darkgreen": "#006400",
    "orangered": "#FF4500",
    "darkseagreen": "#8FBC8F",
    "darkmagenta": "#8B008B",
    "saddlebrown": "#8B4513",
    "mediumaquamarine": "#66CDAA",
    "limegreen": "#32CD32",
    "blue": "#0000FF",
    "mediumseagreen": "#3CB371",
    "peru": "#CD853F",
    "turquoise": "#40E0D0",
    "darkcyan": "#008B8B",
    "olivedrab": "#6B8E23",
    "cyan": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "powderblue": "#B0E0E6",
    "hotpink": "#FF69B4",
    "palegreen": "#98FB98",
    "darkturquoise": "#00CED1",
    "magenta": "#FF00FF",
    "slateblue": "#6A5ACD",
    "lightgreen": "#90EE90",
    "sienna": "#A0522D",
    "darkorchid": "#9932CC",
    "orange": "#FFA500",
    "forestgreen": "#228B22",
    "palegoldenrod": "#EEE8AA",
    "blueviolet": "#8A2BE2",
    "royalblue": "#4169E1",
    "teal": "#008080",
    "darkgoldenrod": "#B8860B",
    "lightskyblue": "#87CEFA",
    "lime": "#00FF00",
    "orchid": "#DA70D6",
    "mediumorchid": "#BA55D3",
    "indigo": "#4B0082",
    "mediumspringgreen": "#00FA9A",
    "tomato": "#FF6347",
    "mediumblue": "#0000CD",
    "midnightblue": "#191970",
    "deepskyblue": "#00BFFF",
    "salmon": "#FA8072",
    "rosybrown": "#BC8F8F",
    "mediumslateblue": "#7B68EE",
    "moccasin": "#FFE4B5",
    "paleturquoise": "#AFEEEE",
    "darkblue": "#00008B",
    "navy": "#000080",
    "steelblue": "#4682B4",
    "crimson": "#DC143C",
    "red": "#FF0000",
    "bisque": "#FFE4C4",
    "darkslategray": "#2F4F4F",
    "maroon": "#800000",
    "mediumpurple": "#9370DB",
    "darkslateblue": "#483D8B",
    "darksalmon": "#E9967A",
    "deeppink": "#FF1493",
    "seagreen": "#2E8B57",
    "mediumvioletred": "#C71585",
    "greenyellow": "#ADFF2F",
    "springgreen": "#00FF7F",
    "sandybrown": "#F4A460",
    "brown": "#A52A2A",
    "lightpink": "#FFB6C1",
    "olive": "#808000",
    "burlywood": "#DEB887",
    "dodgerblue": "#1E90FF",
    "darkolivegreen": "#556B2F",
    "lightsalmon": "#FFA07A",
    "aqua": "#00FFFF",
    "khaki": "#F0E68C",
    "pink": "#FFC0CB",
    "green": "#008000",
    "darkorange": "#FF8C00",
    "rebeccapurple": "#663399",
    "coral": "#FF7F50",
    "darkviolet": "#9400D3",
    "purple": "#800080",
    "palevioletred": "#DB7093",
    "lightseagreen": "#20B2AA",
    "indianred": "#CD5C5C",
    "darkkhaki": "#BDB76B",
    "lightcoral": "#F08080",
    "mediumturquoise": "#48D1CC",
    "peachpuff": "#FFDAB9",
    "skyblue": "#87CEEB",
    "fuchsia": "#FF00FF",
    "navajowhite": "#FFDEAD",
    "lawngreen": "#7CFC00",
    "cornflowerblue": "#6495ED",
    "tan": "#D2B48C",
    "darkred": "#8B0000",
    "firebrick": "#B22222",
    "gold": "#FFD700",
    "yellow": "#FFFF00",
    "wheat": "#F5DEB3",
    "chartreuse": "#7FFF00",
    "goldenrod": "#DAA520",
    "violet": "#EE82EE",
    "yellowgreen": "#9ACD32",
    "cadetblue": "#5F9EA0",
    "plum": "#DDA0DD",
}
"""Css4 colors."""


class DynamicMeta(type):
    """Provide dynamic meta."""

    def __hash__(cls):
        return hash((cls.__module__, cls.__qualname__))

    def __getitem__(cls, key):
        # Route __getitem__ through __getattribute__ for consistency
        return cls.__getattribute__(key)

    def __call__(cls, value, *args, **kwargs):
        # Case-insensitive value resolution
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return super().__call__(value, *args, **kwargs)

    def __getattribute__(cls, name: str):
        var = settings.aedt_version if settings.aedt_version else ""
        clname = super().__getattribute__("__name__")
        try:
            ver_dict = dict(sorted(super().__getattribute__(f"_{clname}__versioned").items()))
            versioned = {}
            if var in ver_dict:
                versioned = ver_dict[var]
            elif ver_dict and var:
                for k, v in ver_dict.items():
                    if var <= k:
                        versioned = v

            if versioned and name in versioned:
                return versioned[name]
                # new_emum = Enum(cls.__name__, versioned, module=cls.__module__)
                # return getattr(new_emum, name)
        except AttributeError:
            pass
        return super().__getattribute__(name)

    def __repr__(cls) -> str:
        try:
            return cls.NAME
        except AttributeError:
            return super().__getattribute__("__name__")

    def __str__(cls) -> str:
        try:
            return cls.NAME
        except AttributeError:
            return super().__getattribute__("__name__")

    def __contains__(cls, item) -> bool:
        try:
            super().__getattribute__(item)
            return True
        except AttributeError:
            return False

    def __eq__(cls, other):
        return True if str(cls) == other else False


class InfiniteSphereType(metaclass=DynamicMeta):
    """
    Infinite sphere type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import InfiniteSphereType
    >>> InfiniteSphereType.ThetaPhi

    """

    ThetaPhi = "Theta-Phi"
    """Value for theta phi."""
    AzOverEl = "Az Over El"
    """Value for az over el."""
    ElOverAz = "El Over Az"
    """Value for el over az."""


class Fillet(metaclass=DynamicMeta):
    """
    Fillet enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import Fillet
    >>> Fillet.Round

    """

    (Round, Mitered) = range(2)


class Axis(metaclass=DynamicMeta):
    """
    Coordinate system axis enum class.

    This static class defines integer constants corresponding to the
    Cartesian axes: X, Y, and Z. Attributes can be
    assigned to the `orientation` keyword argument for
    geometry creation methods of
    the :class:`ansys.aedt.core.modeler.modeler_3d.Modeler3D` and
    :class:`ansys.aedt.core.modeler.modeler_2d.Modeler2D` classes.

    Attributes
    ----------
    X : int
        Axis index corresponding to the X axis (typically 0).
    Y : int
        Axis index corresponding to the Y axis (typically 1).
    Z : int
        Axis index corresponding to the Z axis (typically 2).

    Examples
    --------
    >>> from ansys.aedt.core.generic import constants
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> cylinder1 = hfss.modeler.create_cylinder(
    ...     orientation=constants.Axis.Z,
    ...     origin=[0, 0, 0],
    ...     radius="0.5mm",
    ...     height="3cm",
    ... )

    """

    (X, Y, Z) = range(3)


class Plane(metaclass=DynamicMeta):
    """
    Coordinate system plane enum class.

    This static class defines integer constants corresponding to the
    Y-Z, Z-X, and X-Y planes of the current coordinate system.

    Attributes
    ----------
    YZ : int
        Y-Z plane (typically 0).
    ZX : int
        Z-X plane (typically 1).
    XY : int
        X-Y plane (typically 2).

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> from ansys.aedt.core.generic import constants
    >>> hfss = Hfss()
    >>> hfss.modeler.create_rectangle(constants.Plane.XY, [0, 0, 0], [10, 5])

    """

    (YZ, ZX, XY) = range(3)


class Gravity(metaclass=DynamicMeta):
    """
    Gravity direction enum class.

    This static class defines integer constants corresponding to the
    positive direction of gravity force.

    Attributes
    ----------
    XNeg : int
        Positive gravity force is in the -X direction.
    YNeg : int
        Positive gravity force is in the -Y direction.
    ZNeg : int
        Positive gravity force is in the -Z direction.
    XPos : int
        Positive gravity force is in the +X direction.
    YPos : int
        Positive gravity force is in the +Y direction.
    ZPos : int
        Positive gravity force is in the +Z direction.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import Gravity
    >>> Gravity.ZNeg

    """

    (XNeg, YNeg, ZNeg, XPos, YPos, ZPos) = range(6)


class View(metaclass=DynamicMeta):
    """
    View enum class.

    This static class defines integer constants corresponding to the
    X-Y, Y-Z, and Z-X planes of the current coordinate system, and
    ISO for isometric view.

    Attributes
    ----------
    XY : int
        Set the view along the Z-Axis (view of the XY plane).
    YZ : int
        Set the view along the X-Axis (view of the YZ plane).
    ZX : int
        Set the view along the Y-Axis (view of the ZX plane).
    ISO : int
        Isometric view from the (x=1, y=1, z=1) direction.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import View
    >>> View.ISO

    """

    (XY, YZ, ZX, ISO) = ("XY", "YZ", "ZX", "iso")


class GlobalCS(metaclass=DynamicMeta):
    """
    Global coordinate system enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import GlobalCS
    >>> GlobalCS.XY

    """

    (XY, YZ, ZX) = ("Global:XY", "Global:YZ", "Global:XZ")


class MatrixOperationsQ3D(metaclass=DynamicMeta):
    """
    Matrix operations for Q3D.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import MatrixOperationsQ3D
    >>> MatrixOperationsQ3D.JoinSeries

    """

    (JoinSeries, JoinParallel, FloatNet, GroundNet, FloatTerminal, FloatInfinity, ReturnPath, AddSink, MoveSink) = (
        "JoinSeries",
        "JoinParallel",
        "FloatNet",
        "GroundNet",
        "FloatTerminal",
        "FloatInfinity",
        "ReturnPath",
        "AddSink",
        "MoveSink",
    )


class MatrixOperationsQ2D(metaclass=DynamicMeta):
    """
    Matrix operations for Q2D.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import MatrixOperationsQ2D
    >>> MatrixOperationsQ2D.DiffPair

    """

    (AddGround, SetReferenceGround, Float, Parallel, DiffPair) = (
        "AddGround",
        "SetReferenceGround",
        "Float",
        "Parallel",
        "DiffPair",
    )


class PlotCategoriesQ3D(metaclass=DynamicMeta):
    """
    Plot categories for Q3D.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import PlotCategoriesQ3D
    >>> PlotCategoriesQ3D.C

    """

    (C, G, DCL, DCR, ACL, ACR) = ("C", "G", "DCL", "DCR", "ACL", "ACR")


class PlotCategoriesQ2D(metaclass=DynamicMeta):
    """
    Plot categories for Q2D.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import PlotCategoriesQ2D
    >>> PlotCategoriesQ2D.CMatrix

    """

    (
        CMatrix,
        GMatrix,
        RMatrix,
        LMatrix,
        LumpedC,
        LumpedG,
        LumpedR,
        LumpedL,
        CharacteristicImpedance,
        CrossTalkForward,
        LumpedCrossTalkForward,
        CrossTalkBackward,
    ) = ("C", "G", "R", "L", "lumpC", "lumpG", "lumpR", "lumpL", "Z0", "Kf", "lumpKf", "Kb")


class CSMode(metaclass=DynamicMeta):
    """
    Coordinate system mode enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import CSMode
    >>> CSMode.Axis

    """

    (View, Axis, ZXZ, ZYZ, AXISROTATION) = ("view", "axis", "zxz", "zyz", "axisrotation")


class SegmentType(metaclass=DynamicMeta):
    """
    Segment type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SegmentType
    >>> SegmentType.Line

    """

    (Line, Arc, Spline, AngularArc) = range(0, 4)


class CrossSection(metaclass=DynamicMeta):
    """
    Cross section enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import CrossSection
    >>> CrossSection.Circle

    """

    (NONE, Line, Circle, Rectangle, Trapezoid) = range(0, 5)


class SweepDraft(metaclass=DynamicMeta):
    """
    Sweep draft type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SweepDraft
    >>> SweepDraft.Round

    """

    (Extended, Round, Natural, Mixed) = range(0, 4)


class FlipChipOrientation(metaclass=DynamicMeta):
    """
    Flip chip orientation enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import FlipChipOrientation
    >>> FlipChipOrientation.Up

    """

    (Up, Down) = range(0, 2)


class SolverType(metaclass=DynamicMeta):
    """
    Provides solver type classes.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolverType
    >>> SolverType.Hfss

    """

    (Hfss, Siwave, Q3D, Maxwell, Nexxim, TwinBuilder, Hfss3dLayout, SiwaveSYZ, SiwaveDC) = range(0, 9)


class CutoutSubdesignType(metaclass=DynamicMeta):
    """
    Cutout subdesign type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import CutoutSubdesignType
    >>> CutoutSubdesignType.Conformal

    """

    (BoundingBox, Conformal, ConvexHull, Invalid) = range(0, 4)


class RadiationBoxType(metaclass=DynamicMeta):
    """
    Radiation box type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import RadiationBoxType
    >>> RadiationBoxType.Polygon

    """

    (BoundingBox, Conformal, ConvexHull, Polygon, Invalid) = range(0, 5)


class SweepType(metaclass=DynamicMeta):
    """
    Sweep type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SweepType
    >>> SweepType.Linear

    """

    (Linear, LogCount, Invalid) = range(0, 3)


class BasisOrder(metaclass=DynamicMeta):
    """
    HFSS basis order settings enum class.

    Warning: the value ``single`` has been renamed to ``Single`` for consistency. Please update references to
    ``single``.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import BasisOrder
    >>> BasisOrder.Single

    """

    (Mixed, Zero, Single, Double, Invalid) = (-1, 0, 1, 2, 3)


class NodeType(metaclass=DynamicMeta):
    """
    Enum class on the type of node for source creation.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import NodeType
    >>> NodeType.Positive

    """

    (Positive, Negative, Floating) = range(0, 3)


class SourceType(metaclass=DynamicMeta):
    """
    Type of excitation enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SourceType
    >>> SourceType.CoaxPort

    """

    (CoaxPort, CircPort, LumpedPort, Vsource, Isource, Rlc, DcTerminal) = range(0, 7)


class SolutionsHfss(metaclass=DynamicMeta):
    """
    HFSS solution types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolutionsHfss
    >>> SolutionsHfss.DrivenModal

    """

    (DrivenModal, DrivenTerminal, EigenMode, Transient, SBR, CharacteristicMode) = (
        "Modal",
        "Terminal",
        "Eigenmode",
        "Transient Network",
        "SBR+",
        "Characteristic Mode",
    )


class SolutionsMaxwell3D(metaclass=DynamicMeta):
    """
    Maxwell 3D solution types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> SolutionsMaxwell3D.Transient

    """

    (
        Transient,
        Magnetostatic,
        EddyCurrent,
        ElectroStatic,
        DCConduction,
        ElectroDCConduction,
        ACConduction,
        ElectricTransient,
        TransientAPhiFormulation,
        DCBiasedEddyCurrent,
        ACMagnetic,
        ACMagneticAPhi,
        TransientAPhi,
        ElectricDCConduction,
        ACMagneticwithDC,
    ) = (
        "Transient",
        "Magnetostatic",
        "AC Magnetic",
        "Electrostatic",
        "DC Conduction",
        "Electric DC Conduction",
        "AC Conduction",
        "Electric Transient",
        "Transient APhi",
        "AC Magnetic with DC",
        "AC Magnetic",
        "AC Magnetic APhi",
        "Transient APhi",
        "Electric DC Conduction",
        "AC Magnetic with DC",
    )
    __versioned = {
        "2025.1": {
            "ACConduction": "ACConduction",
            "DCConduction": "DCConduction",
            "EddyCurrent": "EddyCurrent",
            "ACMagnetic": "EddyCurrent",
            "ElectroDCConduction": "ElectroDCConduction",
            "TransientAPhiFormulation": "TransientAPhiFormulation",
            "TransientAPhi": "TransientAPhiFormulation",
            "ElectricDCConduction": "ElectroDCConduction",
            "ACMagneticwithDC": "DCBiasedEddyCurrent",
            "ElectricTransient": "ElectricTransient",
            "DCBiasedEddyCurrent": "DCBiasedEddyCurrent",
        }
    }


class SolutionsMaxwell2D(metaclass=DynamicMeta):
    """
    Maxwell 2D solution types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
    >>> SolutionsMaxwell2D.MagnetostaticXY

    """

    (
        TransientXY,
        TransientZ,
        Transient,
        MagnetostaticXY,
        MagnetostaticZ,
        Magnetostatic,
        EddyCurrentXY,
        EddyCurrentZ,
        EddyCurrent,
        ACMagneticXY,
        ACMagneticZ,
        ACMagnetic,
        ElectroStaticXY,
        ElectroStaticZ,
        ElectroStatic,
        DCConductionXY,
        DCConductionZ,
        DCConduction,
        ACConductionXY,
        ACConductionZ,
        ACConduction,
    ) = (
        "TransientXY",
        "TransientZ",
        "Transient",
        "MagnetostaticXY",
        "MagnetostaticZ",
        "Magnetostatic",
        "AC MagneticXY",
        "AC MagneticZ",
        "AC Magnetic",
        "AC MagneticXY",
        "AC MagneticZ",
        "AC Magnetic",
        "ElectrostaticXY",
        "ElectrostaticZ",
        "Electrostatic",
        "DC ConductionXY",
        "DC ConductionZ",
        "DC Conduction",
        "AC ConductionXY",
        "AC ConductionZ",
        "AC Conduction",
    )
    __versioned = {
        "2025.1": {
            "ACMagneticXY": "EddyCurrentXY",
            "ACMagneticZ": "EddyCurrentZ",
            "ACMagnetic": "EddyCurrent",
            "EddyCurrentXY": "EddyCurrentXY",
            "EddyCurrentZ": "EddyCurrentZ",
            "EddyCurrent": "EddyCurrent",
            "DCConductionXY": "DCConductionXY",
            "DCConductionZ": "DCConductionZ",
            "DCConduction": "DCConduction",
            "ACConductionXY": "ACConductionXY",
            "ACConductionZ": "ACConductionZ",
            "ACConduction": "ACConduction",
        }
    }


class SolutionsIcepak(metaclass=DynamicMeta):
    """
    Icepak solution types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolutionsIcepak
    >>> SolutionsIcepak.SteadyState

    """

    (SteadyState, Transient) = (
        "SteadyState",
        "Transient",
    )


class SolutionsCircuit(metaclass=DynamicMeta):
    """
    Circuit solution types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolutionsCircuit
    >>> SolutionsCircuit.NexximTransient

    """

    (
        NexximLNA,
        NexximDC,
        NexximTransient,
        NexximQuickEye,
        NexximVerifEye,
        NexximAMI,
        NexximOscillatorRSF,
        NexximOscillator1T,
        NexximOscillatorNT,
        NexximHarmonicBalance1T,
        NexximHarmonicBalanceNT,
        NexximSystem,
        NexximTVNoise,
        HSPICE,
        TR,
    ) = (
        "NexximLNA",
        "NexximDC",
        "NexximTransient",
        "NexximQuickEye",
        "NexximVerifEye",
        "NexximAMI",
        "NexximOscillatorRSF",
        "NexximOscillator1T",
        "NexximOscillatorNT",
        "NexximHarmonicBalance1T",
        "NexximHarmonicBalanceNT",
        "NexximSystem",
        "NexximTVNoise",
        "HSPICE",
        "TR",
    )


class SolutionsMechanical(metaclass=DynamicMeta):
    """
    Mechanical solution types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SolutionsMechanical
    >>> SolutionsMechanical.Structural

    """

    (Thermal, Structural, Modal, SteadyStateThermal, TransientThermal) = (
        "Thermal",
        "Structural",
        "Modal",
        "Steady-State Thermal",
        "Transient Thermal",
    )


class Setups(metaclass=DynamicMeta):
    """
    Setup types enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import Setups
    >>> Setups.HFSSDrivenDefault

    """

    HFSSDrivenAuto = 0
    """Value for HFSS driven auto."""
    HFSSDrivenDefault = 1
    """Value for HFSS driven default."""
    HFSSEigen = 2
    """Value for HFSS eigen."""
    HFSSTransient = 3
    """Value for HFSS transient."""
    HFSSSBR = 4
    """Hfsssbr."""
    MaxwellTransient = 5
    """Value for maxwell transient."""
    Magnetostatic = 6
    """Value for magnetostatic."""
    EddyCurrent = 7
    """Value for eddy current."""
    Electrostatic = 8
    """Value for electrostatic."""
    ElectrostaticDC = 9
    """Value for electrostatic dc."""
    ElectricTransient = 10
    """Value for electric transient."""
    SteadyState = 11
    """Value for steady state."""
    # SteadyState = 10
    # SteadyState = 10
    Matrix = 14
    """Value for matrix."""
    NexximLNA = 15
    """Value for nexxim lna."""
    NexximDC = 16
    """Value for nexxim dc."""
    NexximTransient = 17
    """Value for nexxim transient."""
    NexximQuickEye = 18
    """Value for nexxim quick eye."""
    NexximVerifEye = 19
    """Value for nexxim verif eye."""
    NexximAMI = 20
    """Value for nexxim AMI."""
    NexximOscillatorRSF = 21
    """Value for nexxim oscillator rsf."""
    NexximOscillator1T = 22
    """Value for nexxim oscillator 1 T."""
    NexximOscillatorNT = 23
    """Value for nexxim oscillator nt."""
    NexximHarmonicBalance1T = 24
    """Value for nexxim harmonic balance 1 T."""
    NexximHarmonicBalanceNT = 25
    """Value for nexxim harmonic balance nt."""
    NexximSystem = 26
    """Value for nexxim system."""
    NexximTVNoise = 27
    """Value for nexxim tv noise."""
    HSPICE = 28
    """Hspice."""
    HFSS3DLayout = 29
    """Value for HFSS 3 D layout."""
    Open = 30
    """Value for open."""
    Close = 31
    """Value for close."""
    MechTerm = 32
    """Value for mech term."""
    MechModal = 33
    """Value for mech modal."""
    GRM = 34
    """Grm."""
    TR = 35
    """Tr."""
    Transient = 36
    """Value for transient."""
    # Transient,
    # Transient,
    DFIG = 39
    """Dfig."""
    TPIM = 40
    """Tpim."""
    SPIM = 41
    """Spim."""
    TPSM = 42
    """Tpsm."""
    BLDC = 43
    """Bldc."""
    ASSM = 44
    """Assm."""
    PMDC = 45
    """Pmdc."""
    SRM = 46
    """Srm."""
    LSSM = 47
    """Lssm."""
    UNIM = 48
    """Unim."""
    DCM = 49
    """Dcm."""
    CPSM = 50
    """Cpsm."""
    NSSM = 51
    """Nssm."""


class LineStyle(metaclass=DynamicMeta):
    """
    Line style enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import LineStyle
    >>> LineStyle.Dash

    """

    (Solid, Dot, ShortDash, DotShortDash, Dash, DotDash, DotDot, DotDotDash, LongDash) = (
        "Solid",
        "Dot",
        "ShortDash",
        "DotShortDash",
        "Dash",
        "DotDash",
        "DotDot",
        "DotDotDash",
        "LongDash",
    )


class TraceType(metaclass=DynamicMeta):
    """
    Trace type enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import TraceType
    >>> TraceType.Continuous

    """

    (Continuous, Discrete, StickZero, StickInfinity, BarZero, BarInfinity, Histogram, Step, Stair, Digital) = (
        "Continuous",
        "Discrete",
        "Stick Zero",
        "Stick Infinity",
        "Bar Zero",
        "Bar Infinity",
        "Histogram",
        "Step",
        "Stair",
        "Digital",
    )


class SymbolStyle(metaclass=DynamicMeta):
    """
    Symbol style enum class.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SymbolStyle
    >>> SymbolStyle.Circle

    """

    (
        Box,
        Circle,
        VerticalEllipse,
        HorizontalEllipse,
        VerticalUpTriangle,
        VerticalDownTriangle,
        HorizontalLeftTriangle,
        HorizontalRightTriangle,
    ) = (
        "Box",
        "Circle",
        "VerticalEllipse",
        "HorizontalEllipse",
        "VerticalUpTriangle",
        "VerticalDownTriangle",
        "HorizontalLeftTriangle",
        "HorizontalRightTriangle",
    )


class DisplayFamiliesType(metaclass=DynamicMeta):
    """Display families type enum class."""

    (
        Histogram,
        Statistics,
        Cumulative,
    ) = (
        "DisplayHistogram",
        "DisplayStatistics",
        "CumulativeDistribute",
    )


class IncidentWaveType(metaclass=DynamicMeta):
    """Incident wave field type constants."""

    (
        Total,
        Incident,
        Scattered,
    ) = (
        "TotalFields",
        "IncidentFields",
        "ScatteredFields",
    )


class IntEnumProps(IntEnum):
    """Provide int enum props."""

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)


class EnumUnits(IntEnumProps):
    """Provide enum units."""

    # Frequency
    hz = 0
    """Value for hz."""
    khz = auto()
    """Value for khz."""
    mhz = auto()
    """Value for mhz."""
    ghz = auto()
    """Value for ghz."""
    thz = auto()
    """Value for thz."""
    rps = auto()
    """Value for rps."""
    dbFrequency = auto()
    """Value for db frequency."""
    # Resistance
    mohm = auto()
    """Value for mohm."""
    ohm = auto()
    """Value for ohm."""
    kohm = auto()
    """Value for kohm."""
    megohm = auto()
    """Value for megohm."""
    gohm = auto()
    """Value for gohm."""
    dbResistance = auto()
    """Value for db resistance."""
    # Conductance
    fsie = auto()
    """Value for fsie."""
    psie = auto()
    """Value for psie."""
    nsie = auto()
    """Value for nsie."""
    usie = auto()
    """Value for usie."""
    msie = auto()
    """Value for msie."""
    sie = auto()
    """Value for sie."""
    dbConductance = auto()
    """Value for db conductance."""
    # Inductance
    fh = auto()
    """Value for fh."""
    ph = auto()
    """Value for ph."""
    nh = auto()
    """Value for nh."""
    uh = auto()
    """Value for uh."""
    mh = auto()
    """Value for mh."""
    h = auto()
    """Value for h."""
    dbInductance = auto()
    """Value for db inductance."""
    # Capacitance
    ff = auto()
    """Value for ff."""
    pf = auto()
    """Value for pf."""
    nf = auto()
    """Value for nf."""
    uf = auto()
    """Value for uf."""
    mf = auto()
    """Value for mf."""
    farad = auto()
    """Value for farad."""
    dbCapacitance = auto()
    """Value for db capacitance."""
    # Length
    nm = auto()
    """Value for nm."""
    um = auto()
    """Value for um."""
    mm = auto()
    """Value for mm."""
    meter = auto()
    """Value for meter."""
    cm = auto()
    """Value for cm."""
    ft = auto()
    """Value for ft."""
    inch = auto()  # actually it is "in" but would not be valid
    """Value for inch."""
    mil = auto()
    """Value for mil."""
    uin = auto()
    """Value for uin."""
    dbLength = auto()
    """Value for db length."""
    # Time
    fs = auto()
    """Value for fs."""
    ps = auto()
    """Value for ps."""
    ns = auto()
    """Value for ns."""
    us = auto()
    """Value for us."""
    ms = auto()
    """Value for ms."""
    s = auto()
    """Value for s."""
    dbTime = auto()
    """Value for db time."""
    # Angle
    deg = auto()
    """Value for deg."""
    rad = auto()
    """Value for rad."""
    dbAngle = auto()
    """Value for db angle."""
    # Power
    fw = auto()
    """Value for fw."""
    pw = auto()
    """Value for pw."""
    nw = auto()
    """Value for nw."""
    uw = auto()
    """Value for uw."""
    mw = auto()
    """Value for mw."""
    w = auto()
    """Value for w."""
    dbm = auto()
    """Value for dbm."""
    dbw = auto()
    """Value for dbw."""
    dbPower = auto()
    """Value for db power."""
    # Voltage
    fv = auto()
    """Value for fv."""
    pv = auto()
    """Value for pv."""
    nv = auto()
    """Value for nv."""
    uv = auto()
    """Value for uv."""
    mv = auto()
    """Value for mv."""
    v = auto()
    """Value for v."""
    kv = auto()
    """Value for kv."""
    dbv = auto()
    """Value for dbv."""
    dbVoltage = auto()
    """Value for db voltage."""
    # Current
    fa = auto()
    """Value for fa."""
    pa = auto()
    """Value for pa."""
    na = auto()
    """Value for na."""
    ua = auto()
    """Value for ua."""
    ma = auto()
    """Value for ma."""
    a = auto()
    """Value for a."""
    dbCurrent = auto()
    """Value for db current."""
    # Temperature
    kel = auto()
    """Value for kel."""
    cel = auto()
    """Value for cel."""
    fah = auto()
    """Value for fah."""
    dbTemperature = auto()
    """Value for db temperature."""
    # Noise spectrum (dBc/Hz)
    dbchz = auto()
    """Value for dbchz."""
    dbNoiseSpectrum = auto()
    """Value for db noise spectrum."""
    # Mass (obsolete:  replaced with new enum below)
    oz_obsolete = auto()
    """Value for oz obsolete."""
    dbWeight_obsolete = auto()
    """Value for dbWeight obsolete."""
    # Volume
    L = auto()
    """L."""
    ml = auto()
    """Value for ml."""
    dbVolume = auto()
    """Value for db volume."""
    # Magnetic Induction
    gauss = auto()
    """Value for gauss."""
    ugauss = auto()
    """Value for ugauss."""
    tesla = auto()
    """Value for tesla."""
    utesla = auto()
    """Value for utesla."""
    dbMagInduction = auto()
    """Value for db mag induction."""
    # Magnetic Field Strength
    oersted = auto()
    """Value for oersted."""
    a_per_meter = auto()
    """Value for a per meter."""
    dbMagFieldStrength = auto()
    """Value for db mag field strength."""
    # Force
    fnewton = auto()
    """Value for fnewton."""
    pnewton = auto()
    """Value for pnewton."""
    nnewton = auto()
    """Value for nnewton."""
    unewton = auto()
    """Value for unewton."""
    mnewton = auto()
    """Value for mnewton."""
    newton = auto()
    """Value for newton."""
    knewton = auto()
    """Value for knewton."""
    megnewton = auto()
    """Value for megnewton."""
    gnewton = auto()
    """Value for gnewton."""
    lbForce = auto()
    """Value for lb force."""
    dbForce = auto()
    """Value for db force."""
    # Torque
    fnewtonmeter = auto()
    """Value for fnewtonmeter."""
    pnewtonmeter = auto()
    """Value for pnewtonmeter."""
    nnewtonmeter = auto()
    """Value for nnewtonmeter."""
    unewtonmeter = auto()
    """Value for unewtonmeter."""
    mnewtonmeter = auto()
    """Value for mnewtonmeter."""
    newtonmeter = auto()
    """Value for newtonmeter."""
    knewtonmeter = auto()
    """Value for knewtonmeter."""
    megnewtonmeter = auto()
    """Value for megnewtonmeter."""
    gnewtonmeter = auto()
    """Value for gnewtonmeter."""
    OzIn = auto()
    """Value for oz in."""
    LbIn = auto()
    """Value for lb in."""
    ftlb = auto()
    """Value for ftlb."""
    GmCm = auto()
    """Value for gm cm."""
    KgCm = auto()
    """Value for kg cm."""
    KgMeter = auto()
    """Value for kg meter."""
    dbTorque = auto()
    """Value for db torque."""
    # Speed (mph is meter_per_hour)
    mmps = auto()
    """Value for mmps."""
    cmps = auto()
    """Value for cmps."""
    mps = auto()
    """Value for mps."""
    mph = auto()
    """Value for mph."""
    fps = auto()
    """Value for fps."""
    fpm = auto()
    """Value for fpm."""
    miph = auto()
    """Value for miph."""
    dbSpeed = auto()
    """Value for db speed."""
    # AngularSpeed
    rpm = auto()
    """Value for rpm."""
    degps = auto()
    """Value for degps."""
    degpm = auto()
    """Value for degpm."""
    degph = auto()
    """Value for degph."""
    radps = auto()
    """Value for radps."""
    radpm = auto()
    """Value for radpm."""
    radph = auto()
    """Value for radph."""
    dbAngularSpeed = auto()
    """Value for db angular speed."""
    # Flux
    weber = auto()
    """Value for weber."""
    dbFlux = auto()
    """Value for db flux."""
    # ElectricFieldStrength
    vpm = auto()
    """Value for vpm."""
    # Mass (replaces obsolete previous)
    ugram = auto()
    """Value for ugram."""
    mgram = auto()
    """Value for mgram."""
    gram = auto()
    """Value for gram."""
    kgram = auto()
    """Value for kgram."""
    oz = auto()
    """Value for oz."""
    lb = auto()
    """Value for lb."""
    dbMass = auto()
    """Value for db mass."""
    # More Length
    km = auto()
    """Value for km."""
    # More Voltage
    megv = auto()
    """Value for megv."""
    # More Current
    ka = auto()
    """Value for ka."""
    # More MagneticInduction
    mtesla = auto()
    """Value for mtesla."""
    mgauss = auto()
    """Value for mgauss."""
    kgauss = auto()
    """Value for kgauss."""
    ktesla = auto()
    """Value for ktesla."""
    # More MagneticFieldStrength
    ka_per_meter = auto()
    """Value for ka per meter."""
    koersted = auto()
    """Value for koersted."""
    # More power units
    kw = auto()
    """Value for kw."""
    horsepower = auto()
    """Value for horsepower."""
    btu_per_hr = auto()
    """Value for btu per hr."""
    # More speed units
    km_per_hr = auto()
    """Value for km per hr."""
    km_per_min = auto()
    """Value for km per min."""
    km_per_sec = auto()
    """Value for km per sec."""
    mi_per_min = auto()
    """Value for mi per min."""
    mi_per_sec = auto()
    """Value for mi per sec."""
    in_per_sec = auto()
    """Value for in per sec."""
    # Pressure units
    n_per_msq = auto()
    """Value for n per msq."""
    kn_per_msq = auto()
    """Value for kn per msq."""
    megn_per_msq = auto()
    """Value for megn per msq."""
    gn_per_msq = auto()
    """Value for gn per msq."""
    psi = auto()
    """Value for psi."""
    kpsi = auto()
    """Value for kpsi."""
    megpsi = auto()
    """Value for megpsi."""
    gpsi = auto()
    """Value for gpsi."""
    #
    upascal = auto()
    """Value for upascal."""
    mpascal = auto()
    """Value for mpascal."""
    cpascal = auto()
    """Value for cpascal."""
    dpascal = auto()
    """Value for dpascal."""
    pascal = auto()
    """Value for pascal."""
    hpascal = auto()
    """Value for hpascal."""
    kpascal = auto()
    """Value for kpascal."""
    megpascal = auto()
    """Value for megpascal."""
    gpascal = auto()
    """Value for gpascal."""
    # kAcceleration
    inps2 = auto()
    """Value for inps 2."""
    mmps2 = auto()
    """Value for mmps 2."""
    cmps2 = auto()
    """Value for cmps 2."""
    mps2 = auto()
    """Value for mps 2."""
    # kAIGB
    aigb2 = auto()
    """Value for aigb 2."""
    aigb1 = auto()
    """Value for aigb 1."""
    # kAmountOfSubstance
    nmol = auto()
    """Value for nmol."""
    umol = auto()
    """Value for umol."""
    mmol = auto()
    """Value for mmol."""
    mol = auto()
    """Value for mol."""
    kmol = auto()
    """Value for kmol."""
    # kAngle
    degsec = auto()
    """Value for degsec."""
    degmin = auto()
    """Value for degmin."""
    # kAngleCoefficient
    perdeg = auto()
    """Value for perdeg."""
    perrad = auto()
    """Value for perrad."""
    vpervperdeg = auto()
    """Value for vpervperdeg."""
    vpervperrad = auto()
    """Value for vpervperrad."""
    # kAngularAcceleration
    degpers2 = auto()
    """Value for degpers 2."""
    pers2 = auto()
    """Value for pers 2."""
    radpers2 = auto()
    """Value for radpers 2."""
    # kAngularDamping
    dmsperrad = auto()
    """Value for dmsperrad."""
    nmsperrad = auto()
    """Value for nmsperrad."""
    kmsperrad = auto()
    """Value for kmsperrad."""
    # kAngularJerk
    jerk_degpers2 = auto()
    """Value for jerk degpers2."""
    jerk_radpers2 = auto()
    """Value for jerk radpers2."""
    # kAngularMomentum
    kgm2pers = auto()
    """Value for kgm 2 pers."""
    newtonmetersec = auto()
    """Value for newtonmetersec."""
    # kAngularSpeed
    AngRps = auto()
    """Value for ang rps."""
    AngSpers = auto()
    """Value for ang spers."""
    # kAngularStiffness
    newtonmeterperdeg = auto()
    """Value for newtonmeterperdeg."""
    newtonmeterperrad = auto()
    """Value for newtonmeterperrad."""
    # kAngularWindage
    kgm2perrad2 = auto()
    """Value for kgm 2 perrad 2."""
    nms2perrad2 = auto()
    """Value for nms 2 perrad 2."""
    # kArea
    in2 = auto()
    """Value for in 2."""
    ft2 = auto()
    """Value for ft 2."""
    um2 = auto()
    """Value for um 2."""
    mm2 = auto()
    """Value for mm 2."""
    cm2 = auto()
    """Value for cm 2."""
    m2 = auto()
    """Value for m 2."""
    km2 = auto()
    """Value for km 2."""
    # kAreaCoefficient
    percm2 = auto()
    """Value for percm 2."""
    perm2 = auto()
    """Value for perm 2."""
    # kArealFlowRate (also Diffusivity)
    m2perhour = auto()
    """Value for m 2 perhour."""
    m2permin = auto()
    """Value for m 2 permin."""
    m2pers = auto()
    """Value for m 2 pers."""
    # kAreaPerPower
    m2perJs = auto()
    """Value for m 2 per js."""
    m2perw = auto()
    """Value for m 2 perw."""
    # kAreaPerVoltage
    Am2perkW = auto()
    """Value for am 2 perk W."""
    Am2perW = auto()
    """Value for am 2 per W."""
    m2perkV = auto()
    """Value for m 2 perk V."""
    m2perV = auto()
    """Value for m 2 per V."""
    # kAreaPerVoltageTemperature
    Am2perWKel = auto()
    """Value for am 2 per W kel."""
    m2perVKel = auto()
    """Value for m 2 per V kel."""
    # kBIGB
    bigB1 = auto()
    """Value for big B 1."""
    bigB2 = auto()
    """Value for big B 2."""
    # kCapacitancePerArea
    Fpercm2 = auto()
    """Value for fpercm 2."""
    nFperm2 = auto()
    """Value for n fperm 2."""
    uFperm2 = auto()
    """Value for u fperm 2."""
    mFperm2 = auto()
    """Value for m fperm 2."""
    Fperm2 = auto()
    """Value for fperm 2."""
    # kCapacitancePerAreaPerVoltage
    pFperVm2 = auto()
    """Value for p fper vm 2."""
    nFperVm2 = auto()
    """Value for n fper vm 2."""
    uFperVm2 = auto()
    """Value for u fper vm 2."""
    mFperVm2 = auto()
    """Value for m fper vm 2."""
    FperVm2 = auto()
    """Value for fper vm 2."""
    # kCapacitancePerLength
    pFperm = auto()
    """Value for p fperm."""
    nFperm = auto()
    """Value for n fperm."""
    uFperm = auto()
    """Value for u fperm."""
    mFperm = auto()
    """Value for m fperm."""
    Fperm = auto()
    """Value for fperm."""
    # kCapacitanceTemperatureCoeff
    nFperCel = auto()
    """Value for n fper cel."""
    uFperCel = auto()
    """Value for u fper cel."""
    FperCel = auto()
    """Value for fper cel."""
    pFperFah = auto()
    """Value for p fper fah."""
    nFperFah = auto()
    """Value for n fper fah."""
    uFperFah = auto()
    """Value for u fper fah."""
    mFperFah = auto()
    """Value for m fper fah."""
    FperFah = auto()
    """Value for fper fah."""
    mFperCel = auto()
    """Value for m fper cel."""
    pFperCel = auto()
    """Value for p fper cel."""
    pFperKel = auto()
    """Value for p fper kel."""
    nFperKel = auto()
    """Value for n fper kel."""
    uFperKel = auto()
    """Value for u fper kel."""
    mFperKel = auto()
    """Value for m fper kel."""
    FperKel = auto()
    """Value for fper kel."""
    # kCharge
    As = auto()
    """Value for as."""
    Ah = auto()
    """Value for ah."""
    nC = auto()
    """Value for n C."""
    uC = auto()
    """Value for u C."""
    mC = auto()
    """Value for m C."""
    C = auto()
    """C."""
    kC = auto()
    """Value for k C."""
    # kCompliance
    inperlbf = auto()
    """Value for inperlbf."""
    cmperN = auto()
    """Value for cmper N."""
    mperN = auto()
    """Value for mper N."""
    # kConductance
    mho = auto()
    """Value for mho."""
    inverseohm = auto()
    """Value for inverseohm."""
    apv = auto()
    """Value for apv."""
    ksie = auto()
    """Value for ksie."""
    megsie = auto()
    """Value for megsie."""
    # kConductancePerLength
    uSperm = auto()
    """Value for u sperm."""
    mSperm = auto()
    """Value for m sperm."""
    cSperm = auto()
    """Value for c sperm."""
    Sperm = auto()
    """Value for sperm."""
    kSperm = auto()
    """Value for k sperm."""
    # kCurrentChangeRate
    Apermin = auto()
    """Value for apermin."""
    Aperhour = auto()
    """Value for aperhour."""
    uApers = auto()
    """Value for u apers."""
    mApers = auto()
    """Value for m apers."""
    Apers = auto()
    """Value for apers."""
    kApers = auto()
    """Value for k apers."""
    # kCurrentDensity
    uApercm2 = auto()
    """Value for u apercm 2."""
    mApercm2 = auto()
    """Value for m apercm 2."""
    Apercm2 = auto()
    """Value for apercm 2."""
    uAperm2 = auto()
    """Value for u aperm 2."""
    mAperm2 = auto()
    """Value for m aperm 2."""
    Aperm2 = auto()
    """Value for aperm 2."""
    Apermm2 = auto()
    """Value for apermm 2."""
    # kCurrentGain
    ApermA = auto()
    """Value for aperm A."""
    mAperA = auto()
    """Value for m aper A."""
    AperA = auto()
    """Value for aper A."""
    # kCurrentLengthPerVoltage
    uAmperV = auto()
    """Value for u amper V."""
    mAmperV = auto()
    """Value for m amper V."""
    AmperV = auto()
    """Value for amper V."""
    # kCurrentPerCharge
    AperC = auto()
    """Value for aper C."""
    AperAhour = auto()
    """Value for aper ahour."""
    AperAs = auto()
    """Value for aper as."""
    # kCurrentPerIrradiance
    uAperWperm2 = auto()
    """Value for u aper wperm 2."""
    mAperWperm2 = auto()
    """Value for m aper wperm 2."""
    AperWperm2 = auto()
    """Value for aper wperm 2."""
    kAperWperm2 = auto()
    """Value for k aper wperm 2."""
    # kCurrentPerLength
    uAperm = auto()
    """Value for u aperm."""
    mAperm = auto()
    """Value for m aperm."""
    Aperm = auto()
    """Value for aperm."""
    kAperm = auto()
    """Value for k aperm."""
    # kCurrentPerTemperature2_half
    AperKel2half = auto()
    """Value for aper kel 2 half."""
    # kCurrentPerTemperatureCubed
    AperKel3 = auto()
    """Value for aper kel 3."""
    # kCurrentPerTemperatureDiffCubed
    AperCelDiff3 = auto()
    """Value for aper cel diff 3."""
    AperKelDiff3 = auto()
    """Value for aper kel diff 3."""
    # kCurrentSquaredTime
    mA2s = auto()
    """Value for m A 2 s."""
    A2s = auto()
    """Value for A 2 s."""
    # kCurrentTemperatureCoeff
    uAperCel = auto()
    """Value for u aper cel."""
    mAperCel = auto()
    """Value for m aper cel."""
    AperCel = auto()
    """Value for aper cel."""
    mAperFah = auto()
    """Value for m aper fah."""
    AperFah = auto()
    """Value for aper fah."""
    uAperKel = auto()
    """Value for u aper kel."""
    mAperKel = auto()
    """Value for m aper kel."""
    AperKel = auto()
    """Value for aper kel."""
    kAperKel = auto()
    """Value for k aper kel."""
    # kDamping
    mNsperm = auto()
    """Value for m nsperm."""
    cNsperm = auto()
    """Value for c nsperm."""
    dNsperm = auto()
    """Value for d nsperm."""
    Nsperm = auto()
    """Value for nsperm."""
    kNsperm = auto()
    """Value for k nsperm."""
    # kDensity
    gpcm3 = auto()
    """Value for gpcm 3."""
    gpl = auto()
    """Value for gpl."""
    kgpl = auto()
    """Value for kgpl."""
    kgpdm3 = auto()
    """Value for kgpdm 3."""
    kgpm3 = auto()
    """Value for kgpm 3."""
    # kElectricFieldStrength
    vpcm = auto()
    """Value for vpcm."""
    # kElectricFluxDensity
    nCperm2 = auto()
    """Value for n cperm 2."""
    uCperm2 = auto()
    """Value for u cperm 2."""
    mCperm2 = auto()
    """Value for m cperm 2."""
    Cperm2 = auto()
    """Value for cperm 2."""
    # kEnergy
    Whour = auto()
    """Value for whour."""
    kWhour = auto()
    """Value for k whour."""
    eV = auto()
    """Value for e V."""
    erg = auto()
    """Value for erg."""
    Ws = auto()
    """Value for ws."""
    uJ = auto()
    """Value for u J."""
    mJ = auto()
    """Value for m J."""
    J = auto()
    """J."""
    kJ = auto()
    """Value for k J."""
    megJ = auto()
    """Value for meg J."""
    GJ = auto()
    """Gj."""
    # kFluidicCapacitance
    cm3perPa = auto()
    """Value for cm 3 per pa."""
    m3perPa = auto()
    """Value for m 3 per pa."""
    # kFluidicConductance
    cm3perPas = auto()
    """Value for cm 3 per pas."""
    m3perPas = auto()
    """Value for m 3 per pas."""
    # kFluidicResistance
    Nsperm5 = auto()
    """Value for nsperm 5."""
    Pasperm3 = auto()
    """Value for pasperm 3."""
    # kFlux
    maxwell = auto()
    """Value for maxwell."""
    vh = auto()
    """Value for vh."""
    vs = auto()
    """Value for vs."""
    # kForce
    dyne = auto()
    """Value for dyne."""
    kpond = auto()
    """Value for kpond."""
    # kFrequency
    persec = auto()
    """Value for persec."""
    # kIlluminance
    lmperm2 = auto()
    """Value for lmperm 2."""
    lmpercm2 = auto()
    """Value for lmpercm 2."""
    Wperm2 = auto()
    """Value for wperm 2."""
    Wpercm2 = auto()
    """Value for wpercm 2."""
    lmperin2 = auto()
    """Value for lmperin 2."""
    lx = auto()
    """Value for lx."""
    klx = auto()
    """Value for klx."""
    meglx = auto()
    """Value for meglx."""
    # kInductancePerLength
    pHperm = auto()
    """Value for p hperm."""
    nHperm = auto()
    """Value for n hperm."""
    uHperm = auto()
    """Value for u hperm."""
    mHperm = auto()
    """Value for m hperm."""
    Hperm = auto()
    """Value for hperm."""
    # kInertance
    kgperm4 = auto()
    """Value for kgperm 4."""
    Ns2perm5 = auto()
    """Value for ns 2 perm 5."""
    Pas2perm3 = auto()
    """Value for pas 2 perm 3."""
    # kIrradiance
    IrradWpercm2 = auto()
    """Value for irrad wpercm 2."""
    Wperin2 = auto()
    """Value for wperin 2."""
    uWperm2 = auto()
    """Value for u wperm 2."""
    mWperm2 = auto()
    """Value for m wperm 2."""
    IrradWperm2 = auto()
    """Value for irrad wperm 2."""
    kWperm2 = auto()
    """Value for k wperm 2."""
    megWperm2 = auto()
    """Value for meg wperm 2."""
    # kJerk
    inpers3 = auto()
    """Value for inpers 3."""
    nmpers3 = auto()
    """Value for nmpers 3."""
    umpers3 = auto()
    """Value for umpers 3."""
    mmpers3 = auto()
    """Value for mmpers 3."""
    cmpers3 = auto()
    """Value for cmpers 3."""
    mpers3 = auto()
    """Value for mpers 3."""
    # kLength
    yd = auto()
    """Value for yd."""
    mileUS = auto()
    """Value for mile us."""
    ltyr = auto()
    """Value for ltyr."""
    mileNaut = auto()
    """Value for mile naut."""
    fm = auto()
    """Value for fm."""
    pm = auto()
    """Value for pm."""
    dm = auto()
    """Value for dm."""
    mileTerr = auto()
    """Value for mile terr."""
    # kLength2PerVoltage2
    m2perV2 = auto()
    """Value for m 2 per V 2."""
    # kLengthCoefficient
    percm = auto()
    """Value for percm."""
    permm = auto()
    """Value for permm."""
    perum = auto()
    """Value for perum."""
    perkm = auto()
    """Value for perkm."""
    perin = auto()
    """Value for perin."""
    VperVperm = auto()
    """Value for vper vperm."""
    VperVperin = auto()
    """Value for vper vperin."""
    perm = auto()
    """Value for perm."""
    # kLengthPerVoltage
    umperV = auto()
    """Value for umper V."""
    mmperV = auto()
    """Value for mmper V."""
    cmperV = auto()
    """Value for cmper V."""
    dmperV = auto()
    """Value for dmper V."""
    mperV = auto()
    """Value for mper V."""
    kmperV = auto()
    """Value for kmper V."""
    # kLengthPerVoltageRoot
    umperVhalf = auto()
    """Value for umper vhalf."""
    mmperVhalf = auto()
    """Value for mmper vhalf."""
    cmperVhalf = auto()
    """Value for cmper vhalf."""
    dmperVhalf = auto()
    """Value for dmper vhalf."""
    mperVhalf = auto()
    """Value for mper vhalf."""
    kmperVhalf = auto()
    """Value for kmper vhalf."""
    # kLuminousFlux
    gm2pers3 = auto()
    """Value for gm 2 pers 3."""
    mlm = auto()
    """Value for mlm."""
    lm = auto()
    """Value for lm."""
    klm = auto()
    """Value for klm."""
    meglm = auto()
    """Value for meglm."""
    # kLuminousIntensity
    mCd = auto()
    """Value for m cd."""
    Cd = auto()
    """Value for cd."""
    kCd = auto()
    """Value for k cd."""
    megCd = auto()
    """Value for meg cd."""
    GCd = auto()
    """Value for G cd."""
    # kMagneticReluctance
    AperVs = auto()
    """Value for aper vs."""
    AperWb = auto()
    """Value for aper wb."""
    # kMassFlowRate
    gpers = auto()
    """Value for gpers."""
    kgpers = auto()
    """Value for kgpers."""
    # kMolarDensity
    molperdm3 = auto()
    """Value for molperdm 3."""
    molpercm3 = auto()
    """Value for molpercm 3."""
    molperl = auto()
    """Value for molperl."""
    molperm3 = auto()
    """Value for molperm 3."""
    # kMolarEnergy
    uJpermol = auto()
    """Value for u jpermol."""
    mJpermol = auto()
    """Value for m jpermol."""
    Jpermol = auto()
    """Value for jpermol."""
    kJpermol = auto()
    """Value for k jpermol."""
    megJpermol = auto()
    """Value for meg jpermol."""
    gJpermol = auto()
    """Value for g jpermol."""
    # kMolarVelocity
    umolpers = auto()
    """Value for umolpers."""
    mmolpers = auto()
    """Value for mmolpers."""
    cmolpers = auto()
    """Value for cmolpers."""
    molpers = auto()
    """Value for molpers."""
    kmolpers = auto()
    """Value for kmolpers."""
    # kMolarViscosity
    Paspermol = auto()
    """Value for paspermol."""
    # kMomentInertia
    lbin2 = auto()
    """Value for lbin 2."""
    lbft2 = auto()
    """Value for lbft 2."""
    kgm2 = auto()
    """Value for kgm 2."""
    # kMomentum
    gmpers = auto()
    """Value for gmpers."""
    kgmpers = auto()
    """Value for kgmpers."""
    # kPercentage
    percent = auto()
    """Value for percent."""
    # kPercentagePerTime
    percentperm = auto()
    """Value for percentperm."""
    percentperhour = auto()
    """Value for percentperhour."""
    percentperday = auto()
    """Value for percentperday."""
    pers = auto()
    """Value for pers."""
    permin = auto()
    """Value for permin."""
    perhour = auto()
    """Value for perhour."""
    perday = auto()
    """Value for perday."""
    percentpers = auto()
    """Value for percentpers."""
    # kPermeance
    VsperA = auto()
    """Value for vsper A."""
    WbperA = auto()
    """Value for wbper A."""
    # kPower
    megw = auto()
    """Value for megw."""
    gw = auto()
    """Value for gw."""
    # kPressure
    mbar = auto()
    """Value for mbar."""
    bar = auto()
    """Value for bar."""
    mmh2o = auto()
    """Value for mmh 2 o."""
    mmhg = auto()
    """Value for mmhg."""
    techAtm = auto()
    """Value for tech atm."""
    torr = auto()
    """Value for torr."""
    stAtm = auto()
    """Value for st atm."""
    # kPressureChangeRate
    psipermin = auto()
    """Value for psipermin."""
    statmpermin = auto()
    """Value for statmpermin."""
    techatmpermin = auto()
    """Value for techatmpermin."""
    mmH2Opermin = auto()
    """Value for mm H 2 opermin."""
    torrpermin = auto()
    """Value for torrpermin."""
    Paperhour = auto()
    """Value for paperhour."""
    mbarperhour = auto()
    """Value for mbarperhour."""
    barperhour = auto()
    """Value for barperhour."""
    psiperhour = auto()
    """Value for psiperhour."""
    statmperhour = auto()
    """Value for statmperhour."""
    techatmperhour = auto()
    """Value for techatmperhour."""
    mbarpers = auto()
    """Value for mbarpers."""
    barpers = auto()
    """Value for barpers."""
    mmH2Operhour = auto()
    """Value for mm H 2 operhour."""
    torrperhour = auto()
    """Value for torrperhour."""
    psipers = auto()
    """Value for psipers."""
    statmpers = auto()
    """Value for statmpers."""
    techatmpers = auto()
    """Value for techatmpers."""
    mmH2Opers = auto()
    """Value for mm H 2 opers."""
    torrpers = auto()
    """Value for torrpers."""
    Papermin = auto()
    """Value for papermin."""
    mbarpermin = auto()
    """Value for mbarpermin."""
    barpermin = auto()
    """Value for barpermin."""
    Papers = auto()
    """Value for papers."""
    # kPressureCoefficient
    perbar = auto()
    """Value for perbar."""
    permbar = auto()
    """Value for permbar."""
    perpsi = auto()
    """Value for perpsi."""
    perstatm = auto()
    """Value for perstatm."""
    pertechatm = auto()
    """Value for pertechatm."""
    permmHg = auto()
    """Value for permm hg."""
    permmH2O = auto()
    """Value for permm H 2 O."""
    VperVperPa = auto()
    """Value for vper vper pa."""
    perPa = auto()
    """Value for per pa."""
    # kRatio
    bel = auto()
    """Value for bel."""
    # kReciprocalPower
    permegW = auto()
    """Value for permeg W."""
    permW = auto()
    """Value for perm W."""
    perkW = auto()
    """Value for perk W."""
    pergW = auto()
    """Value for perg W."""
    perJs = auto()
    """Value for per js."""
    perW = auto()
    """Value for per W."""
    # kReciprocalResistanceCharge
    perOhmAs = auto()
    """Value for per ohm as."""
    perOhmAh = auto()
    """Value for per ohm ah."""
    perOhmC = auto()
    """Value for per ohm C."""
    # kReciprocalResistanceTime
    perOhmmin = auto()
    """Value for per ohmmin."""
    perOhmhour = auto()
    """Value for per ohmhour."""
    perOhms = auto()
    """Value for per ohms."""
    # kResistance
    uohm = auto()
    """Value for uohm."""
    # kResistancePerCharge
    OhmperAs = auto()
    """Value for ohmper as."""
    OhmperAhour = auto()
    """Value for ohmper ahour."""
    nOhmperC = auto()
    """Value for n ohmper C."""
    uOhmperC = auto()
    """Value for u ohmper C."""
    mOhmperC = auto()
    """Value for m ohmper C."""
    OhmperC = auto()
    """Value for ohmper C."""
    kOhmperC = auto()
    """Value for k ohmper C."""
    megOhmperC = auto()
    """Value for meg ohmper C."""
    gOhmperC = auto()
    """Value for g ohmper C."""
    # kResistancePerLength
    Ohmperum = auto()
    """Value for ohmperum."""
    uOhmperm = auto()
    """Value for u ohmperm."""
    mOhmperm = auto()
    """Value for m ohmperm."""
    Ohmperm = auto()
    """Value for ohmperm."""
    kOhmperm = auto()
    """Value for k ohmperm."""
    megOhmperm = auto()
    """Value for meg ohmperm."""
    # kResistanceTemperatureCoeff
    OhmperCel = auto()
    """Value for ohmper cel."""
    mOhmperKel = auto()
    """Value for m ohmper kel."""
    OhmperKel = auto()
    """Value for ohmper kel."""
    kOhmperKel = auto()
    """Value for k ohmper kel."""
    # kResistivity
    Ohmmm2permm = auto()
    """Value for ohmmm 2 permm."""
    Ohmum = auto()
    """Value for ohmum."""
    Ohmcm = auto()
    """Value for ohmcm."""
    Ohmm = auto()
    """Value for ohmm."""
    # kSpecificHeatCapacity
    mJperKelkg = auto()
    """Value for m jper kelkg."""
    JperKelkg = auto()
    """Value for jper kelkg."""
    kJperKelkg = auto()
    """Value for k jper kelkg."""
    # kStiffness
    Npercm = auto()
    """Value for npercm."""
    lbfperin = auto()
    """Value for lbfperin."""
    Nperm = auto()
    """Value for nperm."""
    kNperm = auto()
    """Value for k nperm."""
    # kSurfaceChargeDensity
    SufCDAsperm2 = auto()
    """Value for suf cd asperm 2."""
    SufCDnCperm2 = auto()
    """Value for suf C dn cperm 2."""
    SufCDuCperm2 = auto()
    """Value for suf C du cperm 2."""
    SufCDmCperm2 = auto()
    """Value for suf C dm cperm 2."""
    SufCDCperm2 = auto()
    """Value for suf cd cperm 2."""
    # kSurfaceMobility
    cm2perVs = auto()
    """Value for cm 2 per vs."""
    m2perVs = auto()
    """Value for m 2 per vs."""
    # kSurfaceMobilityPerVoltage
    cm2pV2s = auto()
    """Value for cm 2 p V 2 s."""
    m2pV2s = auto()
    """Value for m 2 p V 2 s."""
    # kTemperature
    mkel = auto()
    """Value for mkel."""
    ckel = auto()
    """Value for ckel."""
    dkel = auto()
    """Value for dkel."""
    # kTemperatureAreaPerPower
    kelm2pw = auto()
    """Value for kelm 2 pw."""
    celm2pw = auto()
    """Value for celm 2 pw."""
    # kTemperatureCoefficient
    perCel = auto()
    """Value for per cel."""
    perFah = auto()
    """Value for per fah."""
    percentperKel = auto()
    """Value for percentper kel."""
    percentperCel = auto()
    """Value for percentper cel."""
    percentperFah = auto()
    """Value for percentper fah."""
    perKel = auto()
    """Value for per kel."""
    # kTemperatureCoefficient2
    perCel2 = auto()
    """Value for per cel 2."""
    perFah2 = auto()
    """Value for per fah 2."""
    perKel2 = auto()
    """Value for per kel 2."""
    # kTemperatureDifference
    celdiff = auto()
    """Value for celdiff."""
    mkeldiff = auto()
    """Value for mkeldiff."""
    keldiff = auto()
    """Value for keldiff."""
    # kThermalCapacitance
    WsperKel = auto()
    """Value for wsper kel."""
    JperKel = auto()
    """Value for jper kel."""
    # kThermalConductance
    mWperCel = auto()
    """Value for m wper cel."""
    WperCel = auto()
    """Value for wper cel."""
    kWperCel = auto()
    """Value for k wper cel."""
    mWperKel = auto()
    """Value for m wper kel."""
    WperKel = auto()
    """Value for wper kel."""
    kWperKel = auto()
    """Value for k wper kel."""
    # kThermalConductivity
    mWperKelm = auto()
    """Value for m wper kelm."""
    WperKelm = auto()
    """Value for wper kelm."""
    # kThermalConvection
    wpcm2kel = auto()
    """Value for wpcm 2 kel."""
    wpm2kel = auto()
    """Value for wpm 2 kel."""
    # kThermalRadiationCoeff
    mWperKel4 = auto()
    """Value for m wper kel 4."""
    WperKel4 = auto()
    """Value for wper kel 4."""
    kWperKel4 = auto()
    """Value for k wper kel 4."""
    # kThermalRadiationConstant
    Wpercm2Kel4 = auto()
    """Value for wpercm 2 kel 4."""
    Wperm2Kel4 = auto()
    """Value for wperm 2 kel 4."""
    # kThermalResistance
    KelsperJ = auto()
    """Value for kelsper J."""
    KelperW = auto()
    """Value for kelper W."""
    # kTime
    min = auto()
    """Value for min."""
    hour = auto()
    """Value for hour."""
    day = auto()
    """Value for day."""
    # kTimePerAngle
    sperdeg = auto()
    """Value for sperdeg."""
    sperrev = auto()
    """Value for sperrev."""
    msperrad = auto()
    """Value for msperrad."""
    sperrad = auto()
    """Value for sperrad."""
    # kTimeSqPerAngleSq
    s2perdeg2 = auto()
    """Value for s 2 perdeg 2."""
    s2perrad2 = auto()
    """Value for s 2 perrad 2."""
    # kTorque
    cnewtonmeter = auto()
    """Value for cnewtonmeter."""
    # kTransconductanceParameter
    mAperV = auto()
    """Value for m aper V."""
    AperV = auto()
    """Value for aper V."""
    kAperV = auto()
    """Value for k aper V."""
    # kTransistorConstant
    mAperV2 = auto()
    """Value for m aper V 2."""
    AperV2 = auto()
    """Value for aper V 2."""
    # kTranslationalAcceleration
    inpers2 = auto()
    """Value for inpers 2."""
    cmpers2 = auto()
    """Value for cmpers 2."""
    dmpers2 = auto()
    """Value for dmpers 2."""
    mpers2 = auto()
    """Value for mpers 2."""
    # kVelocitySaturation
    VelSatumperV = auto()
    """Value for vel satumper V."""
    VelSatmmperV = auto()
    """Value for vel satmmper V."""
    VelSatcmperV = auto()
    """Value for vel satcmper V."""
    VelSatmperV = auto()
    """Value for vel satmper V."""
    # kVelocitySaturationPerVoltage
    umperV2 = auto()
    """Value for umper V 2."""
    mmperV2 = auto()
    """Value for mmper V 2."""
    cmperV2 = auto()
    """Value for cmper V 2."""
    mperV2 = auto()
    """Value for mper V 2."""
    # kViscocity
    Nsperm2 = auto()
    """Value for nsperm 2."""
    cpoise = auto()
    """Value for cpoise."""
    poise = auto()
    """Value for poise."""
    uPas = auto()
    """Value for u pas."""
    mPas = auto()
    """Value for m pas."""
    cPas = auto()
    """Value for c pas."""
    dPas = auto()
    """Value for d pas."""
    Pas = auto()
    """Value for pas."""
    hPas = auto()
    """Value for h pas."""
    kPas = auto()
    """Value for k pas."""
    # kViscousFriction
    VisFricmNsperm = auto()
    """Value for vis fricm nsperm."""
    VisFricCNsperm = auto()
    """Value for vis fric C nsperm."""
    VisFricNsperm = auto()
    """Value for vis fric nsperm."""
    VisFrickNsperm = auto()
    """Value for vis frick nsperm."""
    # kVoltage
    gv = auto()
    """Value for gv."""
    # kVoltageAccelerationCoefficient
    mVperm2pers2 = auto()
    """Value for m vperm 2 pers 2."""
    Vperm2pers2 = auto()
    """Value for vperm 2 pers 2."""
    # kVoltageChangeRate
    Vpermin = auto()
    """Value for vpermin."""
    Vperhour = auto()
    """Value for vperhour."""
    mVpers = auto()
    """Value for m vpers."""
    Vpers = auto()
    """Value for vpers."""
    kVpers = auto()
    """Value for k vpers."""
    # kVoltageCoefficient
    permV = auto()
    """Value for perm V."""
    perkV = auto()
    """Value for perk V."""
    perV = auto()
    """Value for per V."""
    # kVoltageCoefficient2
    perV2 = auto()
    """Value for per V 2."""
    # kVoltageCubed
    mV3 = auto()
    """Value for m V 3."""
    V3 = auto()
    """V 3."""
    # kVoltageGain
    VpermV = auto()
    """Value for vperm V."""
    mVperV = auto()
    """Value for m vper V."""
    VperV = auto()
    """Value for vper V."""
    # kVoltageJerkCoefficient
    mVpermpers3 = auto()
    """Value for m vpermpers 3."""
    Vpermpers3 = auto()
    """Value for vpermpers 3."""
    # kVoltageLength
    uVm = auto()
    """Value for u vm."""
    mVm = auto()
    """Value for m vm."""
    Vm = auto()
    """Value for vm."""
    kVm = auto()
    """Value for k vm."""
    # kVoltagePerCell
    pVpercell = auto()
    """Value for p vpercell."""
    nVpercell = auto()
    """Value for n vpercell."""
    uVpercell = auto()
    """Value for u vpercell."""
    mVpercell = auto()
    """Value for m vpercell."""
    Vpercell = auto()
    """Value for vpercell."""
    kVpercell = auto()
    """Value for k vpercell."""
    megVpercell = auto()
    """Value for meg vpercell."""
    gVpercell = auto()
    """Value for g vpercell."""
    # kVoltagePerLengthRoot
    Vpermhalf = auto()
    """Value for vpermhalf."""
    # kVoltagePressureRootCoeff
    mVperPahalf = auto()
    """Value for m vper pahalf."""
    VperPahalf = auto()
    """Value for vper pahalf."""
    # kVoltageRoot
    Vhalf = auto()
    """Value for vhalf."""
    # kVoltageRootCoefficient
    perVhalf = auto()
    """Value for per vhalf."""
    # kVoltageTemperature10Coeff
    uVperCel10 = auto()
    """Value for u vper cel 10."""
    mVperCel10 = auto()
    """Value for m vper cel 10."""
    VperCel10 = auto()
    """Value for vper cel 10."""
    uVperKel10 = auto()
    """Value for u vper kel 10."""
    mVperKel10 = auto()
    """Value for m vper kel 10."""
    VperKel10 = auto()
    """Value for vper kel 10."""
    # kVoltageTemperature11Coeff
    uVperCel11 = auto()
    """Value for u vper cel 11."""
    mVperCel11 = auto()
    """Value for m vper cel 11."""
    VperCel11 = auto()
    """Value for vper cel 11."""
    uVperKel11 = auto()
    """Value for u vper kel 11."""
    mVperKel11 = auto()
    """Value for m vper kel 11."""
    VperKel11 = auto()
    """Value for vper kel 11."""
    # kVoltageTemperature12Coeff
    uVperCel12 = auto()
    """Value for u vper cel 12."""
    mVperCel12 = auto()
    """Value for m vper cel 12."""
    VperCel12 = auto()
    """Value for vper cel 12."""
    uVperKel12 = auto()
    """Value for u vper kel 12."""
    mVperKel12 = auto()
    """Value for m vper kel 12."""
    VperKel12 = auto()
    """Value for vper kel 12."""
    # kVoltageTemperature13Coeff
    uVperCel13 = auto()
    """Value for u vper cel 13."""
    mVperCel13 = auto()
    """Value for m vper cel 13."""
    VperCel13 = auto()
    """Value for vper cel 13."""
    uVperKel13 = auto()
    """Value for u vper kel 13."""
    mVperKel13 = auto()
    """Value for m vper kel 13."""
    VperKel13 = auto()
    """Value for vper kel 13."""
    # kVoltageTemperature14Coeff
    uVperCel14 = auto()
    """Value for u vper cel 14."""
    mVperCel14 = auto()
    """Value for m vper cel 14."""
    VperCel14 = auto()
    """Value for vper cel 14."""
    uVperKel14 = auto()
    """Value for u vper kel 14."""
    mVperKel14 = auto()
    """Value for m vper kel 14."""
    VperKel14 = auto()
    """Value for vper kel 14."""
    # kVoltageTemperature15Coeff
    uVperCel15 = auto()
    """Value for u vper cel 15."""
    mVperCel15 = auto()
    """Value for m vper cel 15."""
    VperCel15 = auto()
    """Value for vper cel 15."""
    uVperKel15 = auto()
    """Value for u vper kel 15."""
    mVperKel15 = auto()
    """Value for m vper kel 15."""
    VperKel15 = auto()
    """Value for vper kel 15."""
    # kVoltageTemperature2Coeff
    uVperCel2 = auto()
    """Value for u vper cel 2."""
    mVperCel2 = auto()
    """Value for m vper cel 2."""
    VperCel2 = auto()
    """Value for vper cel 2."""
    uVperKel2 = auto()
    """Value for u vper kel 2."""
    mVperKel2 = auto()
    """Value for m vper kel 2."""
    VperKel2 = auto()
    """Value for vper kel 2."""
    # kVoltageTemperature3Coeff
    uVperCel3 = auto()
    """Value for u vper cel 3."""
    mVperCel3 = auto()
    """Value for m vper cel 3."""
    VperCel3 = auto()
    """Value for vper cel 3."""
    uVperKel3 = auto()
    """Value for u vper kel 3."""
    mVperKel3 = auto()
    """Value for m vper kel 3."""
    VperKel3 = auto()
    """Value for vper kel 3."""
    # kVoltageTemperature4Coeff
    uVperCel4 = auto()
    """Value for u vper cel 4."""
    mVperCel4 = auto()
    """Value for m vper cel 4."""
    VperCel4 = auto()
    """Value for vper cel 4."""
    uVperKel4 = auto()
    """Value for u vper kel 4."""
    mVperKel4 = auto()
    """Value for m vper kel 4."""
    VperKel4 = auto()
    """Value for vper kel 4."""
    # kVoltageTemperature5Coeff
    uVperCel5 = auto()
    """Value for u vper cel 5."""
    mVperCel5 = auto()
    """Value for m vper cel 5."""
    VperCel5 = auto()
    """Value for vper cel 5."""
    uVperKel5 = auto()
    """Value for u vper kel 5."""
    mVperKel5 = auto()
    """Value for m vper kel 5."""
    VperKel5 = auto()
    """Value for vper kel 5."""
    # kVoltageTemperature6Coeff
    uVperCel6 = auto()
    """Value for u vper cel 6."""
    mVperCel6 = auto()
    """Value for m vper cel 6."""
    VperCel6 = auto()
    """Value for vper cel 6."""
    uVperKel6 = auto()
    """Value for u vper kel 6."""
    mVperKel6 = auto()
    """Value for m vper kel 6."""
    VperKel6 = auto()
    """Value for vper kel 6."""
    # kVoltageTemperature7Coeff
    uVperCel7 = auto()
    """Value for u vper cel 7."""
    mVperCel7 = auto()
    """Value for m vper cel 7."""
    VperCel7 = auto()
    """Value for vper cel 7."""
    uVperKel7 = auto()
    """Value for u vper kel 7."""
    mVperKel7 = auto()
    """Value for m vper kel 7."""
    VperKel7 = auto()
    """Value for vper kel 7."""
    # kVoltageTemperature8Coeff
    uVperCel8 = auto()
    """Value for u vper cel 8."""
    mVperCel8 = auto()
    """Value for m vper cel 8."""
    VperCel8 = auto()
    """Value for vper cel 8."""
    uVperKel8 = auto()
    """Value for u vper kel 8."""
    mVperKel8 = auto()
    """Value for m vper kel 8."""
    VperKel8 = auto()
    """Value for vper kel 8."""
    # kVoltageTemperature9Coeff
    uVperCel9 = auto()
    """Value for u vper cel 9."""
    mVperCel9 = auto()
    """Value for m vper cel 9."""
    VperCel9 = auto()
    """Value for vper cel 9."""
    uVperKel9 = auto()
    """Value for u vper kel 9."""
    mVperKel9 = auto()
    """Value for m vper kel 9."""
    VperKel9 = auto()
    """Value for vper kel 9."""
    # kVoltageTemperatureCoeff
    uVperCel = auto()
    """Value for u vper cel."""
    mVperCel = auto()
    """Value for m vper cel."""
    VperCel = auto()
    """Value for vper cel."""
    uVperKel = auto()
    """Value for u vper kel."""
    mVperKel = auto()
    """Value for m vper kel."""
    VperKel = auto()
    """Value for vper kel."""
    # kVolume
    mm3 = auto()
    """Value for mm 3."""
    m3 = auto()
    """Value for m 3."""
    galUK = auto()
    """Value for gal uk."""
    cup = auto()
    """Value for cup."""
    galUS = auto()
    """Value for gal us."""
    # kVolumeCoefficient
    percm3 = auto()
    """Value for percm 3."""
    perm3 = auto()
    """Value for perm 3."""
    # kVolumeFlowConductance
    VolFConcm3perPas = auto()
    """Value for vol F concm 3 per pas."""
    VolFConm3perPas = auto()
    """Value for vol F conm 3 per pas."""
    # kVolumeFlowPerPressureRoot
    m3persPahalf = auto()
    """Value for m 3 pers pahalf."""
    # kVolumeFlowRate
    m3permin = auto()
    """Value for m 3 permin."""
    m3perhour = auto()
    """Value for m 3 perhour."""
    cm3pers = auto()
    """Value for cm 3 pers."""
    m3pers = auto()
    """Value for m 3 pers."""
    ltrpermin = auto()
    """Value for ltrpermin."""
    # kVolumeFlowRateChangeRate
    cm3pers2 = auto()
    """Value for cm 3 pers 2."""
    m3pers2 = auto()
    """Value for m 3 pers 2."""
    # kMass
    mton = auto()
    """Value for mton."""
    # kWireCrossSection
    Wirein2 = auto()
    """Value for wirein 2."""
    Wireft2 = auto()
    """Value for wireft 2."""
    Wireum2 = auto()
    """Value for wireum 2."""
    Wiremm2 = auto()
    """Value for wiremm 2."""
    Wirecm2 = auto()
    """Value for wirecm 2."""
    Wirem2 = auto()
    """Value for wirem 2."""
    # kEnergyDensity
    JPerM3 = auto()
    """Value for J per M 3."""
    kJPerM3 = auto()
    """Value for k J per M 3."""
    # Additional Volume Units
    cm3 = auto()
    """Value for cm 3."""
    inch3 = auto()
    """Value for inch 3."""
    foot3 = auto()
    """Value for foot 3."""
    yard3 = auto()
    """Value for yard 3."""
    # Magnetomotive Force
    at = auto()
    """Value for at."""
    uat = auto()
    """Value for uat."""
    nat = auto()
    """Value for nat."""
    mat = auto()
    """Value for mat."""
    kat = auto()
    """Value for kat."""
    # additional kPercentage
    Fraction = auto()
    """Value for fraction."""
    # delta temperature
    fah_diff = auto()
    """Value for fah diff."""
    # Delta Fahrenheit
    ckel_diff = auto()
    """Value for ckel diff."""
    dkel_diff = auto()
    """Value for dkel diff."""
    # Delta Kelvin
    # Additional units for Areal Flow Rate (e.g. Diffusivity)
    ft2pers = auto()
    """Value for ft 2 pers."""
    cm2pers = auto()
    """Value for cm 2 pers."""
    # kMolarMass
    kgpermol = auto()
    """Value for kgpermol."""
    gpermol = auto()
    """Value for gpermol."""
    # Additional units for kViscocity
    kgperms = auto()
    """Value for kgperms."""
    lbmperfts = auto()
    """Value for lbmperfts."""
    slugperfts = auto()
    """Value for slugperfts."""
    # Additions for kTemperatureAreaPerPower (e.g. Thermal Impedance)
    celin2pw = auto()
    """Value for celin 2 pw."""
    # C-in2/W
    celmm2pw = auto()
    """Value for celmm 2 pw."""
    # C-mm2/W
    # Additions for kIrradiance (e.g. Heat Flux Density)
    btupspft2 = auto()
    """Value for btupspft 2."""
    # BTU/s-ft2
    btuphrpft2 = auto()
    """Value for btuphrpft 2."""
    # BTU/h-ft2
    ergpspcm2 = auto()
    """Value for ergpspcm 2."""
    # erg/s-cm2
    # Additional units for area
    micron2 = auto()
    """Value for micron 2."""
    mil2 = auto()
    """Value for mil 2."""
    # Additional units for thermal conductance
    btuPerFahSec = auto()
    """Value for btu per fah sec."""
    btuPerRankSec = auto()
    """Value for btu per rank sec."""
    btuPerFahHr = auto()
    """Value for btu per fah hr."""
    btuPerRankHr = auto()
    """Value for btu per rank hr."""
    # Additional units for thermal conductivity
    btuPerFahFtSec = auto()
    """Value for btu per fah ft sec."""
    btuPerRankFtSec = auto()
    """Value for btu per rank ft sec."""
    btuPerFahFtHr = auto()
    """Value for btu per fah ft hr."""
    btuPerRankFtHr = auto()
    """Value for btu per rank ft hr."""
    calpersmCel = auto()
    """Value for calpersm cel."""
    calpersmKel = auto()
    """Value for calpersm kel."""
    ergperscmKel = auto()
    """Value for ergperscm kel."""
    wPerCelM = auto()
    """Value for w per cel M."""
    # Additional units for density
    lbmPerFt3 = auto()
    """Value for lbm per ft 3."""
    slugPerFt3 = auto()
    """Value for slug per ft 3."""
    # Additional units for thermal convection
    btuPerFahSecFt2 = auto()
    """Value for btu per fah sec ft 2."""
    btuPerFahHrFt2 = auto()
    """Value for btu per fah hr ft 2."""
    btuPerRankSecFt2 = auto()
    """Value for btu per rank sec ft 2."""
    btuPerRankHrFt2 = auto()
    """Value for btu per rank hr ft 2."""
    wPerCelM2 = auto()
    """Value for w per cel M 2."""
    # Additional unit(s) for length
    copperOzPerFt2 = auto()
    """Value for copper oz per ft 2."""
    # Additional units for mass flow rate
    lbmPerSec = auto()
    """Value for lbm per sec."""
    lbmPerMin = auto()
    """Value for lbm per min."""
    # Additional units for power
    btuPerSec = auto()
    """Value for btu per sec."""
    ergPerSec = auto()
    """Value for erg per sec."""
    # Additional units for power-per-area (surface heat)
    IrradWPerMm2 = auto()
    """Value for irrad W per mm 2."""
    IrradMet = auto()
    """Value for irrad met."""
    # Power per volume
    btuPerSecFt3 = auto()
    """Value for btu per sec ft 3."""
    btuPerHrFt3 = auto()
    """Value for btu per hr ft 3."""
    ergPerSecCm3 = auto()
    """Value for erg per sec cm 3."""
    wPerM3 = auto()
    """Value for w per M 3."""
    # Additional unit(s) for pressure
    lbfPerFt2 = auto()
    """Value for lbf per ft 2."""
    # Additional units for thermal resistance
    celPerW = auto()
    """Value for cel per W."""
    fahSecPerBtu = auto()
    """Value for fah sec per btu."""
    # Additional units for specific heat capacity
    btuPerLbmFah = auto()
    """Value for btu per lbm fah."""
    btuPerLbmRank = auto()
    """Value for btu per lbm rank."""
    calPerGKel = auto()
    """Value for cal per G kel."""
    calPerGCel = auto()
    """Value for cal per G cel."""
    ergPerGKel = auto()
    """Value for erg per G kel."""
    JPerCelKg = auto()
    """Value for J per cel kg."""
    kcalPerKgKel = auto()
    """Value for kcal per kg kel."""
    kcalPerKgCel = auto()
    """Value for kcal per kg cel."""
    # Additional units for temperature and delta-temperature (Rankine)
    rank = auto()
    """Value for rank."""
    rankdiff = auto()
    """Value for rankdiff."""
    # Turbulent dissipation rate
    m2PerSec3 = auto()
    """Value for m 2 per sec 3."""
    ft2PerSec3 = auto()
    """Value for ft 2 per sec 3."""
    # Turbulent kinetic energy
    m2PerSec2 = auto()
    """Value for m 2 per sec 2."""
    ft2PerSec2 = auto()
    """Value for ft 2 per sec 2."""
    # Specific turbulence dissipation rate
    dissPerSec = auto()
    """Value for diss per sec."""
    # Additional unit for temperature coefficient (volumetric expansion coefficient)
    perRank = auto()
    """Value for per rank."""
    percentperRank = auto()
    """Value for percentper rank."""
    # Additional units for volumetric flow rate
    ft3PerMin = auto()
    """Value for ft 3 per min."""
    ft3PerSec = auto()
    """Value for ft 3 per sec."""
    cfm = auto()
    """Value for cfm."""
    # Additional unit for pressure
    pressWaterInches = auto()
    """Value for press water inches."""
    # Additional unit for kCharge
    q = auto()
    """Value for q."""
    # change of a proton (negative for electron)
    # data rate units of bits/sec (added for EMIT)
    bps = auto()
    """Value for bps."""
    kbps = auto()
    """Value for kbps."""
    mbps = auto()
    """Value for mbps."""
    gbps = auto()
    """Value for gbps."""
    # kMassFlux
    kgpersm2 = auto()
    """Value for kgpersm 2."""
    lbmperminft2 = auto()
    """Value for lbmperminft 2."""
    gperscm2 = auto()
    """Value for gperscm 2."""
    # kThermalConductancePerArea
    Wperm2perCel = auto()
    """Value for wperm 2 per cel."""
    Wperin2perCel = auto()
    """Value for wperin 2 per cel."""
    Wpermm2perCel = auto()
    """Value for wpermm 2 per cel."""
    # kAttenutation
    dBperm = auto()
    """Value for d bperm."""
    dBpercm = auto()
    """Value for d bpercm."""
    dBperdm = auto()
    """Value for d bperdm."""
    dBperkm = auto()
    """Value for d bperkm."""
    dBperft = auto()
    """Value for d bperft."""
    dBpermi = auto()
    """Value for d bpermi."""
    Nppercm = auto()
    """Value for nppercm."""
    Npperdm = auto()
    """Value for npperdm."""
    Npperft = auto()
    """Value for npperft."""
    Npperkm = auto()
    """Value for npperkm."""
    Npperm = auto()
    """Value for npperm."""
    Nppermi = auto()
    """Value for nppermi."""


class AllowedMarkers(IntEnumProps):
    """Provide allowed markers."""

    Octahedron = 12
    """Value for octahedron."""
    Tetrahedron = 11
    """Value for tetrahedron."""
    Sphere = 9
    """Value for sphere."""
    Box = 10
    """Value for box."""
    Arrow = 0
    """Value for arrow."""


class SubstrateType(IntEnumProps):
    """
    Substrate type constants for AEDT ``AddSubstrateDataBlock`` COM API.

    The integer values map directly to the ``Type`` field accepted by
    ``oModule.AddSubstrateDataBlock``.

    Examples
    --------
    >>> from ansys.aedt.core.generic.constants import SubstrateType
    >>> SubstrateType.Microstrip
    0
    >>> int(SubstrateType.Microstrip)
    0

    """

    Microstrip = 0
    """Microstrip — single conductor on top of a dielectric, ground below."""

    Stripline = 1
    """Stripline — conductor embedded between two dielectric layers."""

    OffsetStripline = 2
    """Offset stripline — asymmetric stripline with conductor offset from centre."""

    CoplanarWaveguide = 3
    """Coplanar waveguide (CPW) — conductor and ground planes on the same surface."""

    GroundedCoplanarWaveguide = 4
    """Grounded coplanar waveguide (GCPW) — CPW with an additional ground plane below."""

    SuspendedStripline = 5
    """Suspended stripline — conductor suspended above the ground plane with an air gap."""

    Slotline = 6
    """Slotline — narrow slot cut in a metallic plane on a dielectric substrate."""

    RectangularWaveguide = 9
    """Rectangular waveguide — hollow metallic tube with rectangular cross-section."""

    SubstrateReference = 10
    """Substrate reference — named reference substrate used by transmission-line models."""
