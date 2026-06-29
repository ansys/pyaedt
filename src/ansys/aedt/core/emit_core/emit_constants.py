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

"""Enums from the ``EmitApiPython`` module are defined as ``None`` until The module initializes.

This allows IDE auto-complete to find them and ``emit_constants`` to import before the
``EmitApiPython`` module has loaded (typically when a ``ansys.aedt.core.Emit()`` object is created).

Because the members must be reassigned at runtime, the Enum class cannot be used.

Examples
--------
>>> from ansys.aedt.core.emit_core.emit_constants import EMIT_VALID_UNITS
>>> EMIT_VALID_UNITS["Frequency"]

"""


class MutableEnum:
    """Provide mutable enum."""

    @classmethod
    def members(cls):
        members = [
            getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")
        ]
        if members[0] is None:
            raise Exception(
                f"Enum is uninitialized. Create a ansys.aedt.core.Emit() object before using {cls.__name__}."
            )
        return members


class ResultType(MutableEnum):
    """Provide result type."""

    EMI = None
    """EMI option."""
    DESENSE = None
    """Desense option."""
    SENSITIVITY = None
    """Sensitivity option."""
    POWER_AT_RX = None
    """Power at rx option."""


class TxRxMode(MutableEnum):
    """Provide tx rx mode."""

    TX = None
    """Tx option."""
    RX = None
    """Rx option."""
    BOTH = None
    """Both option."""


class InterfererType(MutableEnum):
    """Provide interferer type."""

    TRANSMITTERS = None
    """Transmitters option."""
    EMITTERS = None
    """Emitters option."""
    TRANSMITTERS_AND_EMITTERS = None
    """Transmitters and emitters option."""


class UnitType(MutableEnum):
    """Provide unit type."""

    POWER = None
    """Power option."""
    FREQUENCY = None
    """Frequency option."""
    LENGTH = None
    """Length option."""
    TIME = None
    """Time option."""
    VOLTAGE = None
    """Voltage option."""
    DATA_RATE = None
    """Data rate option."""
    RESISTANCE = None
    """Resistance option."""


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
"""Valid units for each unit type.

Examples
--------
>>> from ansys.aedt.core.emit_core.emit_constants import EMIT_VALID_UNITS
>>> EMIT_VALID_UNITS["Power"]
"""

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
"""Default units for each unit type.

Examples
--------
>>> from ansys.aedt.core.emit_core.emit_constants import EMIT_INTERNAL_UNITS
>>> EMIT_INTERNAL_UNITS["Frequency"]
"""

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
"""EMIT to AEDT units."""

EMIT_FN_ALLOWED_VARS = {"RF", "IF", "LO"}
"""EMIT fn allowed vars."""

EMIT_FN_ALLOWED_FUNCS = {"abs", "trunc"}
"""EMIT fn allowed funcs."""

EMIT_FN_ALLOWED_OPS = {"+", "-", "*", "/"}
"""EMIT fn allowed ops."""


def data_rate_conv(value: float, units: str, to_internal: bool = True) -> float:
    """
    Converts the data rate to (from) the internal units from the
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

    Examples
    --------
    >>> from ansys.aedt.core.emit_core.emit_constants import data_rate_conv
    >>> rate = data_rate_conv(1.5, "Mbps")

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


def emit_unit_type_string_to_enum(unit_string: str) -> UnitType:
    """Return EMIT unit type string to enum."""
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


def emi_cat_enum_to_string(emi_cat_enum) -> str:
    """Return EMI cat enum to string."""
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
    """Provide EMI category filter."""

    IN_CHANNEL_TX_FUNDAMENTAL = None
    """In channel tx fundamental option."""
    IN_CHANNEL_TX_HARMONIC_SPURIOUS = None
    """In channel tx harmonic spurious option."""
    IN_CHANNEL_TX_INTERMOD = None
    """In channel tx intermod option."""
    IN_CHANNEL_TX_BROADBAND = None
    """In channel tx broadband option."""
    OUT_OF_CHANNEL_TX_FUNDAMENTAL = None
    """Out of channel tx fundamental option."""
    OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS = None
    """Out of channel tx harmonic spurious option."""
    OUT_OF_CHANNEL_TX_INTERMOD = None
    """Out of channel tx intermod option."""


if __name__ == "__main__":
    print("Members of EmiCategoryFilter:")
    for m in EmiCategoryFilter.members():
        print(f"    {m}")
