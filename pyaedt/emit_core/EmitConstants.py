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


def unit_type():
    """Get an ``unit_type`` object.

    Returns
    -------
    :class:`EmitConstants.unit_type`
        Type of unit: Power, Frequency, Length, Time, Voltage, DataRate, Resistance.

    Examples
    >>> unit_type = EmitConstants.unit_type()
    """
    try:
        unit_type = EMIT_MODULE.unit_type()
    except NameError:
        raise ValueError("An Emit object must be initialized before any static member of EmitConstants is accessed.")
    return unit_type


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

EMIT_UNIT_TYPE_STRING_TO_ENUM = {
    "Power": unit_type().power,
    "Frequency": unit_type().frequency,
    "Length": unit_type().length,
    "Time": unit_type().time,
    "Voltage": unit_type().voltage,
    "Data Rate": unit_type().dataRate,
    "Resistance": unit_type().resistance,
}
