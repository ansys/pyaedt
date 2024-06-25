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

"""
Enums from the ``EmitApiPython`` module are defined as ``None`` until this module initializes.
This allows IDE auto-complete to find them and ``emit_constants`` to import before the
``EmitApiPython`` module has loaded (typically when a ``pyaedt.Emit()`` object is created).

Because the members must be reassigned at runtime, the Enum class cannot be used.
"""


class MutableEnum:
    @classmethod
    def members(cls):
        members = [
            getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")
        ]
        if members[0] is None:
            raise Exception(
                "Enum is uninitialized. Create a pyaedt.Emit() object before using {}.".format(cls.__name__)
            )
        return members


class ResultType(MutableEnum):
    EMI = None
    DESENSE = None
    SENSITIVITY = None
    POWER_AT_RX = None


class TxRxMode(MutableEnum):
    TX = None
    RX = None
    BOTH = None


class InterfererType(MutableEnum):
    TRANSMITTERS = None
    EMITTERS = None
    TRANSMITTERS_AND_EMITTERS = None


class UnitType(MutableEnum):
    POWER = None
    FREQUENCY = None
    LENGTH = None
    TIME = None
    VOLTAGE = None
    DATA_RATE = None
    RESISTANCE = None


EMIT_VALID_UNITS = {
    "Power": ["mW", "W", "kW", "dBm", "dBW"],
    "Frequency": ["Hz", "kHz", "MHz", "GHz", "THz"],
    "Length": ["pm", "nm", "um", "mm", "cm", "dm", "meter", "km", "mil", "in", "ft", "yd", "mile"],
    "Time": ["ps", "ns", "us", "ms", "s"],
    "Voltage": ["mV", "V"],
    "Data Rate": ["bps", "kbps", "Mbps", "Gbps"],
    "Resistance": ["uOhm", "mOhm", "Ohm", "kOhm", "megOhm", "GOhm"],
}
"""Valid units for each unit type."""


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


class EmiCategoryFilter(MutableEnum):
    IN_CHANNEL_TX_FUNDAMENTAL = None
    IN_CHANNEL_TX_HARMONIC_SPURIOUS = None
    IN_CHANNEL_TX_INTERMOD = None
    IN_CHANNEL_TX_BROADBAND = None
    OUT_OF_CHANNEL_TX_FUNDAMENTAL = None
    OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS = None
    OUT_OF_CHANNEL_TX_INTERMOD = None


if __name__ == "__main__":
    print("Members of EmiCategoryFilter:")
    for m in EmiCategoryFilter.members():
        print("    {}".format(m))
