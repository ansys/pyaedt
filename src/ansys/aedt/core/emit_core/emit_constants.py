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

"""Enums and constants for EMIT API.

These enums are defined directly from the ``EmitDataTypes.h`` header file
and provide type-safe constants for use with EMIT operations.
"""


class MutableEnum:
    """Base class for EMIT enum types.
    
    Provides a members() method to retrieve all enum values.
    """
    @classmethod
    def members(cls):
        """Return all enum members."""
        members = [
            getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")
        ]
        return members


class ResultType(MutableEnum):
    EMI = 0
    DESENSE = 1
    SENSITIVITY = 2
    POWER_AT_RX = 3


class TxRxMode(MutableEnum):
    TX = 0
    RX = 1
    BOTH = 2


class InterfererType(MutableEnum):
    TRANSMITTERS = 0
    EMITTERS = 1
    TRANSMITTERS_AND_EMITTERS = 2


class UnitType(MutableEnum):
    POWER = 0
    FREQUENCY = 1
    LENGTH = 2
    TIME = 3
    VOLTAGE = 4
    DATA_RATE = 5
    RESISTANCE = 6


EMIT_VALID_UNITS = {
    "Power": ["mW", "W", "kW", "dBm", "dBW"],
    "Frequency": ["Hz", "kHz", "MHz", "GHz", "THz"],
    "Freq": ["Hz", "kHz", "MHz", "GHz", "THz"],
    "Length": ["pm", "nm", "um", "mm", "cm", "dm", "meter", "meters", "km", "mil", "in", "ft", "yd", "mile"],
    "Time": ["ps", "ns", "us", "ms", "s"],
    "Voltage": ["nV", "uV", "mV", "V", "kV", "MegV"],
    "Data Rate": ["bps", "kbps", "Mbps", "Gbps"],
    "Resistance": ["uOhm", "mOhm", "Ohm", "kOhm", "megOhm", "GOhm"],
}
"""Valid units for each unit type."""

EMIT_INTERNAL_UNITS = {
    "Power": "dBm",
    "Frequency": "Hz",
    "Freq": "Hz",
    "Length": "meter",
    "Time": "s",
    "Voltage": "V",
    "Data Rate": "bps",
    "Resistance": "ohm",
}
"""Default units for each unit type."""

EMIT_TO_AEDT_UNITS = {
    "picometers": "pm",
    "nanometers": "nm",
    "micrometers": "um",
    "millimeters": "mm",
    "centimeters": "cm",
    "decimeters": "dm",
    "meters": "meter",
    "kilometers": "km",
    "inches": "in",
    "mils": "mil",
    "feet": "ft",
    "yards": "yd",
    "miles": "mile",
    "hertz": "Hz",
    "kilohertz": "kHz",
    "megahertz": "MHz",
    "gigahertz": "GHz",
    "terahertz": "THz",
    "picoseconds": "ps",
    "nanoseconds": "ns",
    "microseconds": "us",
    "milliseconds": "ms",
    "seconds": "s",
    "microohms": "uOhm",
    "milliohms": "mOhm",
    "ohms": "ohm",
    "kiloohms": "kOhm",
    "megaohms": "megohm",
    "gigaohms": "GOhm",
    "dBm": "dBm",
    "dBW": "dBW",
    "watts": "W",
    "milliwatts": "mW",
    "kilowatts": "kW",
    "nanovolts": "nV",
    "microvolts": "uV",
    "millivolts": "mV",
    "volts": "V",
    "kilovolts": "kV",
    "megavolts": "MegV",
    "bps": "bps",
    "kbps": "kbps",
    "Mbps": "Mbps",
    "Gbps": "Gbps",
}

EMIT_FN_ALLOWED_VARS = {"RF", "IF", "LO"}

EMIT_FN_ALLOWED_FUNCS = {"abs", "trunc"}

EMIT_FN_ALLOWED_OPS = {"+", "-", "*", "/"}


def data_rate_conv(value: float, units: str, to_internal: bool = True):
    """Converts the data rate to (from) the internal units from the
    specified units.

    Args:
        value (float): numeric value of the data rate
        units (str): units to convert to (from)
        to_internal (bool, optional): Converts from the specified units
            to the internal units OR from the internal units to the
            specified units. Defaults to True.

    Returns
    -------
        value: data rate converted to/from the internal units
    """
    mult = 1.0

    if units not in ("bps", "kbps", "Mbps", "Gbps"):
        raise ValueError(f"{units} are not valid units for data rate.")
    if to_internal:
        if units == "bps":
            mult = 1.0
        elif units == "kbps":
            mult = 1e3
        elif units == "Mbps":
            mult = 1e6
        elif units == "Gbps":
            mult = 1e9
    else:
        if units == "bps":
            mult = 1.0
        elif units == "kbps":
            mult = 1e-3
        elif units == "Mbps":
            mult = 1e-6
        elif units == "Gbps":
            mult = 1e-9
    return value * mult


def emit_unit_type_string_to_enum(unit_string):
    EMIT_UNIT_TYPE_STRING_TO_ENUM = {
        "Power": UnitType.POWER,
        "Frequency": UnitType.FREQUENCY,
        "Length": UnitType.LENGTH,
        "Time": UnitType.TIME,
        "Voltage": UnitType.VOLTAGE,
        "Data Rate": UnitType.DATA_RATE,
        "Resistance": UnitType.RESISTANCE,
    }
    return EMIT_UNIT_TYPE_STRING_TO_ENUM[unit_string]


def emi_cat_enum_to_string(emi_cat_enum):
    EMI_CAT_ENUM_TO_STR = {
        EmiCategoryFilter.IN_CHANNEL_TX_FUNDAMENTAL: "In-Channel Tx Fundamental",
        EmiCategoryFilter.IN_CHANNEL_TX_HARMONIC_SPURIOUS: "In-Channel Tx Harmonic/Spurious",
        EmiCategoryFilter.IN_CHANNEL_TX_INTERMOD: "In-Channel Intermod",
        EmiCategoryFilter.IN_CHANNEL_TX_BROADBAND: "In-Channel Broadband",
        EmiCategoryFilter.OUT_OF_CHANNEL_TX_FUNDAMENTAL: "Out-of-Channel Tx Fundamental",
        EmiCategoryFilter.OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS: "Out-of-Channel Tx Harmonic/Spurious",
        EmiCategoryFilter.OUT_OF_CHANNEL_TX_INTERMOD: "Out-of-Channel Intermod",
    }
    return EMI_CAT_ENUM_TO_STR[emi_cat_enum]


class EmiCategoryFilter(MutableEnum):
    """EMI category filter from EmitDataTypes.h"""
    IN_CHANNEL_TX_FUNDAMENTAL = 0
    IN_CHANNEL_TX_HARMONIC_SPURIOUS = 1
    IN_CHANNEL_TX_INTERMOD = 2
    IN_CHANNEL_TX_BROADBAND = 3
    OUT_OF_CHANNEL_TX_FUNDAMENTAL = 4
    OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS = 5
    OUT_OF_CHANNEL_TX_INTERMOD = 6


if __name__ == "__main__":
    print("Members of EmiCategoryFilter:")
    for m in EmiCategoryFilter.members():
        print(f"    {m}")
