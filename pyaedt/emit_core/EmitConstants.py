import math
import warnings


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
                value = value
            elif to_unit == "dBW":
                value = value - 30
            elif to_unit == "mW":
                value = math.pow(10.0, value / 10.0)
            elif to_unit == "W":
                value = math.pow(10.0, value / 10.0 - 3.0)
            elif to_unit == "kW":
                value = math.pow(10.0, value / 10.0 - 6.0)
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

EMIT_UNIT_SYSTEM = ['Power', 'Frequency', 'Length', 'Time', 'Voltage', 'Data Rate', 'Resistance']  
"""Valid unit system."""      

EMIT_VALID_UNITS = {
    "Power": ["mW", "W", "kW", "dBm", "dBW"],
    "Frequency": ["Hz", "kHz", "MHz", "GHz", "THz"],
    "Length": ["pm", "nm", "um", "mm", "cm", "dm", "meter", "km", "mil", "in", "ft", "yd", "mile"],
    "Time": ["ps", "ns", "us", "ms", "s"],
    "Voltage": ["mV", "V"],
    "Data Rate": ["bps", "kbps", "Mbps", "Gbps"],
    "Resistance": ["uOhm", "mOhm", "Ohm", "kOhm", "megOhm", "GOhm"]
}
"""Valid units for each unit type."""

