import math
import warnings

from pyaedt.emit_core import EMIT_MODULE


def result_type():
    """
    Get a result type.

    Returns
    -------
    :class:`EmitConstants.result_type`
        Result status which can later be assigned a status
        (emi, sensitivity, desense, powerAtRx).

    Examples
    --------
    >>> tx_rx = EmitConstants.result_type()

    """
    try:
        result = EMIT_MODULE.result_type()
    except NameError:
        raise ValueError("An Emit object must be initialized before any static member of EmitConstants is accessed.")
    return result


def tx_rx_mode():
    """
    Get a ``tx_rx_mode`` object.

    Returns
    -------
    :class:`EmitConstants.tx_rx_mode`
        Mode status which can later be assigned a status (tx, rx).

    Examples
    --------
    >>> tx_rx = EmitConstants.tx_rx_mode()

    """
    try:
        tx_rx = EMIT_MODULE.tx_rx_mode()
    except NameError:
        raise ValueError("An Emit object must be initialized before any static member of EmitConstants is accessed.")
    return tx_rx


def interferer_type():
    """Get an ``interferer_type`` object.

    Returns
    -------
    :class:`EmitConstants.interferer_type`
        Type of interferer: transmitters, emitters, or transmitters_and_emitters.

    Examples
    >>> int_type = EmitConstants.interferer_type()
    >>> tx_only = int_type.transmitters
    """
    try:
        inter_type = EMIT_MODULE.interferer_type()
    except NameError:
        raise ValueError("An Emit object must be initialized before any static member of EmitConstants is accessed.")
    return inter_type


def convert_power_to_unit(values, to_unit):
    """Convert power from dBm to specified unit.

    Parameters
    ----------
    values : list
        List of powers in dBm.
    to_unit : str
        Units for the output powers.

    Returns
    -------
    List (floats)
        List of powers in [to_units].
    """
    if to_unit not in EMIT_VALID_UNITS["Power"]:
        warnings.warn("No units found")
        return values
    if isinstance(values, list):
        converted_values = []
        for value in values:
            if to_unit == "dBm":
                converted_values.append(value)
            elif to_unit == "dBW":
                converted_values.append(value - 30)
            elif to_unit == "mW":
                converted_values.append(math.pow(10.0, value / 10.0))
            elif to_unit == "W":
                converted_values.append(math.pow(10.0, value / 10.0 - 3.0))
            elif to_unit == "kW":
                converted_values.append(math.pow(10.0, value / 10.0 - 6.0))
        return converted_values

    if to_unit == "dBm":
        return values
    elif to_unit == "dBW":
        return values - 30
    elif to_unit == "mW":
        return math.pow(10.0, values / 10.0)
    elif to_unit == "W":
        return math.pow(10.0, values / 10.0 - 3.0)
    elif to_unit == "kW":
        return math.pow(10.0, values / 10.0 - 6.0)


def convert_power_dbm(values, from_unit):
    """Convert power to dBm.

    Parameters
    ----------
    values : list
        List of powers to convert to dBm.
    from_unit : str
        Units for the input powers.

    Returns
    -------
    List (floats)
        List of powers in dBm.
    """
    if from_unit not in EMIT_VALID_UNITS["Power"]:
        warnings.warn("No units found")
        return values
    if isinstance(values, list):
        converted_values = []
        for value in values:
            if from_unit == "dBm":
                value = value
            elif from_unit == "dBW":
                value = value + 30
            elif from_unit == "mW":
                value = max(-1000.0, 10.0 * math.log10(value))
            elif from_unit == "W":
                value = max(-1000.0, 10.0 * (math.log10(value) + 3.0))
            elif from_unit == "kW":
                value = max(-1000.0, 10.0 * (math.log10(value) + 6.0))
            converted_values.append(value)

        return converted_values

    if from_unit == "dBm":
        return values
    elif from_unit == "dBW":
        return values + 30
    elif from_unit == "mW":
        return max(-1000.0, 10.0 * math.log10(values))
    elif from_unit == "W":
        return max(-1000.0, 10.0 * (math.log10(values) + 3.0))
    elif from_unit == "kW":
        return max(-1000.0, 10.0 * (math.log10(values) + 6.0))


EMIT_UNIT_TYPE = ["Power", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
"""Valid unit type."""

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
