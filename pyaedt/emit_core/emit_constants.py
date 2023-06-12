from pyaedt import emit_core

"""
Enums from EmitApiPython are defined as none until the EmitApiPython module initializes.
This allows IDE auto-complete to find them and emit_constants to import before the
EmitApiPython module has loaded (typically when a pyaedt.Emit() object is created).
"""

class ResultType():
    EMI = None
    DESENSE = None
    SENSITIVITY = None
    POWER_AT_RX = None

class TxRxMode():
    TX = None
    RX = None
    BOTH = None

class InterfererType():
    TRANSMITTERS = None
    EMITTERS = None
    TRANSMITTERS_AND_EMITTERS = None

class UnitType():
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
