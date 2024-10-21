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

import ast
from decimal import Decimal
import math
import random
import re
import secrets
import string
import unicodedata
import warnings

from ansys.aedt.core.generic.filesystem import read_json
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modeler.cad.elements_3d import EdgePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import VertexPrimitive

json_to_dict = read_json


@pyaedt_function_handler()
def _dict_items_to_list_items(d, k, idx="name"):
    if d.get(k, []):
        if isinstance(d[k], dict) and idx in d[k].keys():
            d[k] = [d[k]]
        else:
            new_list = []
            if isinstance(d[k], dict):
                for keyname, keyval in d[k].items():
                    new_dict = {idx: keyname}
                    for valname, valp in keyval.items():
                        new_dict[valname] = valp
                    new_list.append(new_dict)
            else:
                new_list = d[k]
            d[k] = new_list
    else:
        d[k] = []


@pyaedt_function_handler()
def _tuple2dict(t, d):
    """

    Parameters
    ----------
    t :

    d :


    Returns
    -------

    """
    k = t[0]
    v = t[1]
    if isinstance(v, list) and len(t) > 2:
        d[k] = v
    elif isinstance(v, list) and len(t) == 2 and not v:
        d[k] = None
    elif (
        isinstance(v, list) and isinstance(v[0], tuple) and len(t) == 2
    ):  # len check is to avoid expanding the list with a 3rd element=None
        if k in d:
            if not isinstance(d[k], list):
                d[k] = [d[k]]
            d1 = {}
            for tt in v:
                _tuple2dict(tt, d1)
            d[k].append(d1)
        else:
            d[k] = {}
            for tt in v:
                _tuple2dict(tt, d[k])
    else:
        d[k] = v


@pyaedt_function_handler()
def _dict2arg(d, arg_out):
    """Create a valid string of name-value pairs for the native AEDT API.

    Prepend the argument string in `arg_out` using the dictionary ``d``
    to create a valid input string as an argument for the native AEDT API.

    Parameters
    ----------
    d : dict
        Dictionary to use for prepending to the argument string being built
        for the native AEDT API.

    arg_out : str.
        String of the name/value pair to be built as an argument
        for the native AEDT API.

    """
    for k, v in d.items():
        if "_pyaedt" in k:
            continue
        if k == "Point" or k == "DimUnits":
            if isinstance(v[0], (list, tuple)):
                for e in v:
                    arg = ["NAME:" + k, e[0], e[1]]
                    arg_out.append(arg)
            else:
                arg = ["NAME:" + k, v[0], v[1]]
                arg_out.append(arg)
        elif k == "Range":
            if isinstance(v[0], (list, tuple)):
                for e in v:
                    arg_out.append(k + ":=")
                    arg_out.append([i for i in e])
            else:
                arg_out.append(k + ":=")
                arg_out.append([i for i in v])
        elif isinstance(v, dict):
            arg = ["NAME:" + k]
            _dict2arg(v, arg)
            arg_out.append(arg)
        elif v is None:
            arg_out.append(["NAME:" + k])
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            for el in v:
                arg = ["NAME:" + k]
                _dict2arg(el, arg)
                arg_out.append(arg)

        else:
            arg_out.append(k + ":=")
            if type(v) is EdgePrimitive or type(v) is FacePrimitive or type(v) is VertexPrimitive:
                arg_out.append(v.id)
            else:
                arg_out.append(v)


@pyaedt_function_handler()
def _arg2dict(arg, dict_out):
    if arg[0] == "NAME:DimUnits" or "NAME:Point" in arg[0]:
        if arg[0][5:] in dict_out:
            if isinstance(dict_out[arg[0][5:]][0], (list, tuple)):
                dict_out[arg[0][5:]].append(list(arg[1:]))
            else:
                dict_out[arg[0][5:]] = [dict_out[arg[0][5:]]]
                dict_out[arg[0][5:]].append(list(arg[1:]))
        else:
            dict_out[arg[0][5:]] = list(arg[1:])
    elif arg[0][:5] == "NAME:":
        top_key = arg[0][5:]
        dict_in = {}
        i = 1
        while i < len(arg):
            if arg[i][0][:5] == "NAME:" and (
                isinstance(arg[i], (list, tuple)) or str(type(arg[i])) == r"<type 'List'>"
            ):
                _arg2dict(list(arg[i]), dict_in)
                i += 1
            elif arg[i][-2:] == ":=":
                if str(type(arg[i + 1])) == r"<type 'List'>":
                    if arg[i][:-2] in dict_in:
                        dict_in[arg[i][:-2]].append(list(arg[i + 1]))
                    else:
                        dict_in[arg[i][:-2]] = list(arg[i + 1])
                else:
                    if arg[i][:-2] in dict_in:
                        if isinstance(dict_in[arg[i][:-2]], list):
                            dict_in[arg[i][:-2]].append(arg[i + 1])
                        else:
                            dict_in[arg[i][:-2]] = [dict_in[arg[i][:-2]]]
                            dict_in[arg[i][:-2]].append(arg[i + 1])
                    else:
                        dict_in[arg[i][:-2]] = arg[i + 1]

                i += 2
            else:
                raise ValueError("Incorrect data argument format")
        if top_key in dict_out:
            if isinstance(dict_out[top_key], list):
                dict_out[top_key].append(dict_in)
            else:
                dict_out[top_key] = [dict_out[top_key], dict_in]
        else:
            dict_out[top_key] = dict_in
    else:
        raise ValueError("Incorrect data argument format")


@pyaedt_function_handler()
def create_list_for_csharp(input_list, return_strings=False):
    """

    Parameters
    ----------
    input_list :

    return_strings :
         (Default value = False)

    Returns
    -------

    """
    from ansys.aedt.core.generic.clr_module import Double
    from ansys.aedt.core.generic.clr_module import List

    if return_strings:
        col = List[str]()
    else:
        col = List[Double]()

    for el in input_list:
        if return_strings:
            col.Add(str(el))
        else:
            col.Add(el)
    return col


@pyaedt_function_handler()
def create_table_for_csharp(input_list_of_list, return_strings=True):
    """

    Parameters
    ----------
    input_list_of_list :

    return_strings :
         (Default value = True)

    Returns
    -------

    """
    from ansys.aedt.core.generic.clr_module import List

    new_table = List[List[str]]()
    for col in input_list_of_list:
        newcol = create_list_for_csharp(col, return_strings)
        new_table.Add(newcol)
    return new_table


@pyaedt_function_handler()
def format_decimals(el):
    """

    Parameters
    ----------
    el :


    Returns
    -------

    """
    if float(el) > 1000:
        num = "{:,.0f}".format(Decimal(el))
    elif float(el) > 1:
        num = "{:,.3f}".format(Decimal(el))
    else:
        num = "{:.3E}".format(Decimal(el))
    return num


@pyaedt_function_handler()
def random_string(length=6, only_digits=False, char_set=None):
    """Generate a random string

    Parameters
    ----------
    length :
        length of the random string (Default value = 6)
    only_digits : bool, optional
        ``True`` if only digits are to be included.
    char_set : str, optional
        Custom character set to pick the characters from.  By default chooses from
        ASCII and digit characters or just digits if ``only_digits`` is ``True``.

    Returns
    -------
    type
        random string

    """
    if not char_set:
        if only_digits:
            char_set = string.digits
        else:
            char_set = string.ascii_uppercase + string.digits
    random_str = "".join(random.choice(char_set) for _ in range(int(length)))
    return random_str


@pyaedt_function_handler()
def unique_string_list(element_list, only_string=True):
    """Return a unique list of strings from an element list.

    Parameters
    ----------
    element_list :

    only_string :
         (Default value = True)

    Returns
    -------

    """
    if element_list:
        if isinstance(element_list, list):
            element_list = set(element_list)
        elif isinstance(element_list, str):
            element_list = [element_list]
        else:
            error_message = "Invalid list data"
            try:
                error_message += " {}".format(element_list)
            except Exception:
                pass
            raise Exception(error_message)

        if only_string:
            non_string_entries = [x for x in element_list if not isinstance(x, str)]
            assert not non_string_entries, "Invalid list entries {} are not a string!".format(non_string_entries)

    return element_list


@pyaedt_function_handler()
def string_list(element_list):
    """

    Parameters
    ----------
    element_list :


    Returns
    -------

    """
    if isinstance(element_list, str):
        element_list = [element_list]
    else:
        assert isinstance(element_list, str), "Input must be a list or a string"
    return element_list


@pyaedt_function_handler()
def ensure_list(element_list):
    """

    Parameters
    ----------
    element_list :


    Returns
    -------

    """
    if not isinstance(element_list, list):
        element_list = [element_list]
    return element_list


@pyaedt_function_handler()
def variation_string_to_dict(variation_string, separator="="):
    """Helper function to convert a list of "="-separated strings into a dictionary

    Returns
    -------
    dict
    """
    var_data = variation_string.split()
    variation_dict = {}
    for var in var_data:
        pos_eq = var.find("=")
        var_name = var[0:pos_eq]
        var_value = var[pos_eq + 1 :].replace("'", "")
        variation_dict[var_name] = var_value
    return variation_dict


RKM_MAPS = {
    # Resistors
    "L": "m",
    "R": "",
    "E": "",
    "k": "k",
    "K": "k",
    "M": "M",
    "G": "G",
    "T": "T",
    "f": "f",
    # Capacitors/Inductors
    "F": "",
    "H": "",
    "h": "",
    "m": "m",
    "u": "μ",
    "μ": "μ",
    "U": "μ",
    "n": "n",
    "N": "n",
    "p": "p",
    "P": "p",
    "mF": "m",
    "uF": "μ",
    "μF": "μ",
    "UF": "μ",
    "nF": "n",
    "NF": "n",
    "pF": "p",
    "PF": "p",
    "mH": "m",
    "uH": "μ",
    "μH": "μ",
    "UH": "μ",
    "nH": "n",
    "NH": "n",
    "pH": "p",
    "PH": "p",
}
AEDT_MAPS = {"μ": "u"}


@pyaedt_function_handler()
def from_rkm(code):
    """Convert an RKM code string to a string with a decimal point.

    Parameters
    ----------
    code : str
        RKM code string.

    Returns
    -------
    str
        String with a decimal point and an R value.

    Examples
    --------
    >>> from ansys.aedt.core.generic.data_handlers import from_rkm
    >>> from_rkm('R47')
    '0.47'

    >>> from_rkm('4R7')
    '4.7'

    >>> from_rkm('470R')
    '470'

    >>> from_rkm('4K7')
    '4.7k'

    >>> from_rkm('47K')
    '47k'

    >>> from_rkm('47K3')
    '47.3k'

    >>> from_rkm('470K')
    '470k'

    >>> from_rkm('4M7')
    '4.7M'

    """

    # Matches RKM codes that start with a digit.
    # fd_pattern = r'([0-9]+)([LREkKMGTFmuµUnNpP]+)([0-9]*)'
    fd_pattern = r"([0-9]+)([{}]+)([0-9]*)".format(
        "".join(RKM_MAPS.keys()),
    )
    # matches rkm codes that end with a digit
    # ld_pattern = r'([0-9]*)([LREkKMGTFmuµUnNpP]+)([0-9]+)'
    ld_pattern = r"([0-9]*)([{}]+)([0-9]+)".format("".join(RKM_MAPS.keys()))

    fd_regex = re.compile(fd_pattern, re.I)
    ld_regex = re.compile(ld_pattern, re.I)

    for regex in [fd_regex, ld_regex]:
        m = regex.match(code)
        if m:
            fd, base, ld = m.groups()
            ps = RKM_MAPS[base]

            if ld:
                return_str = "".join([fd, ".", ld, ps])
            else:
                return_str = "".join([fd, ps])
            return return_str
    return code


@pyaedt_function_handler()
def to_aedt(code):
    """

    Parameters
    ----------
    code : str

    Returns
    -------
    str

    """
    pattern = r"([{}]{})".format("".join(AEDT_MAPS.keys()), "{1}")
    regex = re.compile(pattern, re.I)
    return_code = regex.sub(lambda m: AEDT_MAPS.get(m.group(), m.group()), code)
    return return_code


def str_to_bool(s):
    """Convert a ``"True"`` or ``"False"`` string to its corresponding Boolean value.

    If the passed arguments are not relevant in the context of conversion, the argument
    itself is returned. This method can be called using the ``map()`` function to
    ensure conversion of Boolean strings in a list.

    Parameters
    ----------
    s: str

    Returns
    -------
    bool or str
         The method is not case-sensitive.
         - ``True`` is returned  if the input is ``"true"``, ``"1"``,
           `"yes"``, or ``"y"``,
         - ``False`` is returned if the input is ``"false"``, ``"no"``,
           ``"n``,  or ``"0"``.
         - Otherwise, the input value is passed through the method unchanged.

    """
    if isinstance(s, str):
        if s.lower() in ["true", "yes", "y", "1"]:
            return True
        elif s.lower() in ["false", "no", "n", "0"]:
            return False
        else:
            return s
    elif isinstance(s, int):
        return False if s == 0 else True


@pyaedt_function_handler()
def from_rkm_to_aedt(code):
    """

    Parameters
    ----------
    code : str


    Returns
    -------
    str

    """
    return to_aedt(from_rkm(code))


unit_val = {
    "": 1.0,
    "uV": 1e-6,
    "mV": 1e-3,
    "V": 1.0,
    "kV": 1e3,
    "MegV": 1e6,
    "ns": 1e-9,
    "us": 1e-6,
    "ms": 1e-3,
    "s": 1.0,
    "min": 60,
    "hour": 3600,
    "rad": 1.0,
    "deg": math.pi / 180,
    "Hz": 1.0,
    "kHz": 1e3,
    "MHz": 1e6,
    "nm": 1e-9,
    "um": 1e-6,
    "mm": 1e-3,
    "in": 0.0254,
    "inches": 0.0254,
    "mil": 2.54e-5,
    "cm": 1e-2,
    "dm": 1e-1,
    "meter": 1.0,
    "km": 1e3,
}

resynch_maxwell2D_control_program_for_design = """
from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.maxwell import Maxwell2d
design_name = os.getenv('design')
setup = os.getenv('setup')

with Desktop() as d:
    maxwell_2d = Maxwell2d(design=design_name, name=setup)
    maxwell_2d.setup_ctrlprog(keep_modifications=True )
    d.logger.info("Successfully updated project definitions")
    maxwell_2d.save_project()
"""


@pyaedt_function_handler()
def float_units(val_str, units=""):
    """Retrieve units for a value.

    Parameters
    ----------
    val_str : str
        Name of the float value.

    units : str, optional
         The default is ``""``.

    Returns
    -------

    """
    if not units in unit_val:
        raise Exception("Specified unit string " + units + " not known!")

    loc = re.search("[a-zA-Z]", val_str)
    try:
        b = loc.span()[0]
        var = [float(val_str[0:b]), val_str[b:]]
        val = var[0] * unit_val[var[1]]
    except Exception:
        val = float(val_str)

    val = val / unit_val[units]
    return val


@pyaedt_function_handler()
def normalize_string_format(text):

    equivalence_table = {
        "$": "S",
        "€": "E",
        "£": "L",
        "@": "at",
        "&": "and",
    }

    def _remove_accents(input_str):
        # Normalize the input string to decompose accents and diacritics
        nfkd_form = unicodedata.normalize("NFKD", input_str)
        # Filter out diacritical marks (combining characters)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    # Step 1: Remove accents and diacritics
    text = _remove_accents(text)

    # Step 2: Replace specific characters like " ", "-", " -", "- ", " - ", and multiple spaces with "_"
    text = re.sub(r"[\s\-]+", "_", text)

    # Step 3: Replace using the equivalence table
    for a, b in equivalence_table.items():
        text = text.replace(a, b)

    # Step 4: Remove unsupported characters, keeping only letters, numbers, and underscores
    text = re.sub(r"[^a-zA-Z0-9_]", "", text)

    # Step 5: Replace multiple underscores with a single underscore
    text = re.sub(r"_+", "_", text)

    # Finally, remove leading or trailing underscores
    text = text.strip("_")

    return text


def _check_types(arg):
    if "netref.builtins.list" in str(type(arg)):
        return "list"
    elif "netref.builtins.dict" in str(type(arg)):
        return "dict"
    elif "netref.__builtin__.list" in str(type(arg)):
        return "list"
    elif "netref.__builtin__.dict" in str(type(arg)):
        return "dict"
    return ""


@pyaedt_function_handler()
def check_numeric_equivalence(a, b, relative_tolerance=1e-7):
    """Check if two numeric values are equivalent to within a relative tolerance.

    Parameters
    ----------
    a : int, float
        Reference value to compare to.
    b : int, float
        Secondary value for the comparison.
    relative_tolerance : float, optional
        Relative tolerance for the equivalence test. The difference is relative to the first value.
        The default is ``1E-7``.

    Returns
    -------
    bool
        ``True`` if the two passed values are equivalent, ``False`` otherwise.
    """
    if abs(a) > 0.0:
        reldiff = abs(a - b) / a
    else:
        reldiff = abs(b)
    return True if reldiff < relative_tolerance else False


@pyaedt_function_handler(rootname="root_name")
def generate_unique_name(root_name=None, suffix="", n=6):
    """Generate a new name given a root name and optional suffix.

    Parameters
    ----------
    root_name : str, optional
        Root name to add random characters to.
        The default is ``"NewObject_"``.
    suffix : string, optional
        Suffix to add.
        The default is ``""``.
    n : int, optional
        Number of random characters to add to the name. The default value is ``6``.

    Returns
    -------
    str
        Newly generated name.
    """
    alphabet = string.ascii_uppercase + string.digits
    uName = "".join(secrets.choice(alphabet) for _ in range(n))
    if root_name in None:
        root_name = "NewObject"
    unique_name = root_name + "_" + uName
    if suffix:
        unique_name += "_" + suffix
    return unique_name


@pyaedt_function_handler(rel_tol="relative_tolerance", abs_tol="absolute_tolerance")
def is_close(a, b, relative_tolerance=1e-9, absolute_tolerance=0.0):
    """Whether two numbers are close to each other given relative and absolute tolerances.

    Parameters
    ----------
    a : float, int
        First number to compare.
    b : float, int
        Second number to compare.
    relative_tolerance : float
        Relative tolerance. The default value is ``1e-9``.
    absolute_tolerance : float
        Absolute tolerance. The default value is ``0.0``.

    Returns
    -------
    bool
        ``True`` if the two numbers are closed, ``False`` otherwise.
    """
    return abs(a - b) <= max(relative_tolerance * max(abs(a), abs(b)), absolute_tolerance)


def isclose(*args, **kwargs):
    """Old method name that triggers a deprecation warning."""
    warnings.warn("`isclose` is deprecated. Use `is_close` method instead.", DeprecationWarning)
    # Call the new method
    return is_close(*args, **kwargs)


@pyaedt_function_handler()
def is_number(a):
    """Whether the given input is a number.

    Parameters
    ----------
    a : float, int, str
        Number to check.

    Returns
    -------
    bool
        ``True`` if it is a number, ``False`` otherwise.
    """
    if isinstance(a, float) or isinstance(a, int):
        return True
    elif isinstance(a, str):
        try:
            float(a)
            return True
        except ValueError:
            return False
    else:
        return False


@pyaedt_function_handler()
def is_array(a):
    """Whether the given input is an array.

    Parameters
    ----------
    a : str
        String containing the list to check.

    Returns
    -------
    bool
        ``True`` if it is an array, ``False`` otherwise.
    """
    try:
        v = list(ast.literal_eval(a))
    except (ValueError, TypeError, NameError, SyntaxError):
        return False
    else:
        if isinstance(v, list):
            return True
        else:
            return False


@pyaedt_function_handler(search_key1="search_key_1", search_key2="search_key_2")
def filter_tuple(value, search_key_1, search_key_2):
    """Filter a tuple of two elements with two search keywords."""
    ignore_case = True

    def _create_pattern(k1, k2):
        k1a = re.sub(r"\?", r".", k1)
        k1b = re.sub(r"\*", r".*?", k1a)
        k2a = re.sub(r"\?", r".", k2)
        k2b = re.sub(r"\*", r".*?", k2a)
        pattern = r".*\({},{}\)".format(k1b, k2b)
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key_1, search_key_2), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key_1, search_key_2))

    m = compiled_re.search(value)
    if m:
        return True
    return False


@pyaedt_function_handler(search_key1="search_key_1")
def filter_string(value, search_key_1):
    """Filter a string"""
    ignore_case = True

    def _create_pattern(k1):
        k1a = re.sub(r"\?", r".", k1.replace("\\", "\\\\"))
        k1b = re.sub(r"\*", r".*?", k1a)
        pattern = r"^{}$".format(k1b)
        return pattern

    if ignore_case:
        compiled_re = re.compile(_create_pattern(search_key_1), re.IGNORECASE)
    else:
        compiled_re = re.compile(_create_pattern(search_key_1))  # pragma: no cover

    m = compiled_re.search(value)
    if m:
        return True
    return False


@pyaedt_function_handler()
def number_aware_string_key(s):
    """Get a key for sorting strings that treats embedded digit sequences as integers.

    Parameters
    ----------
    s : str
        String to calculate the key from.

    Returns
    -------
    tuple
        Tuple of key entries.
    """

    def is_digit(c):
        return "0" <= c <= "9"

    result = []
    i = 0
    while i < len(s):
        if is_digit(s[i]):
            j = i + 1
            while j < len(s) and is_digit(s[j]):
                j += 1
            key = int(s[i:j])
            result.append(key)
            i = j
        else:
            j = i + 1
            while j < len(s) and not is_digit(s[j]):
                j += 1
            key = s[i:j]
            result.append(key)
            i = j
    return tuple(result)


@pyaedt_function_handler(time_vals="time_values", value="data_values")
def compute_fft(time_values, data_values, window=None):  # pragma: no cover
    """Compute FFT of input transient data.

    Parameters
    ----------
    time_values : `pandas.Series`
        Time points corresponding to the x-axis of the input transient data.
    data_values : `pandas.Series`
        Points corresponding to the y-axis.
    time_values : `pandas.Series`
    data_values : `pandas.Series`
    window : str, optional
        Fft window. Options are "hamming", "hanning", "blackman", "bartlett".

    Returns
    -------
    tuple
        Frequency and Values.
    """
    try:
        import numpy as np
    except ImportError:
        settings.logger.error("NumPy is not available. Install it.")
        return False

    deltaT = time_values[-1] - time_values[0]
    num_points = len(time_values)
    win = None
    if window:

        if window == "hamming":
            win = np.hamming(num_points)
        elif window == "hanning":
            win = np.hanning(num_points)
        elif window == "bartlett":
            win = np.bartlett(num_points)
        elif window == "blackman":
            win = np.blackman(num_points)
    if win is not None:
        valueFFT = np.fft.fft(data_values * win, num_points)
    else:
        valueFFT = np.fft.fft(data_values, num_points)
    Npoints = int(len(valueFFT) / 2)
    valueFFT = valueFFT[:Npoints]
    valueFFT = 2 * valueFFT / len(valueFFT)
    n = np.arange(num_points)
    freq = n / deltaT
    return freq, valueFFT


@pyaedt_function_handler(function_str="function")
def conversion_function(data, function=None):  # pragma: no cover
    """Convert input data based on a specified function string.

    The available functions are:

    - `"dB10"`: Converts the data to decibels using base 10 logarithm.
    - `"dB20"`: Converts the data to decibels using base 20 logarithm.
    - `"abs"`: Computes the absolute value of the data.
    - `"real"`: Computes the real part of the data.
    - `"imag"`: Computes the imaginary part of the data.
    - `"norm"`: Normalizes the data to have values between 0 and 1.
    - `"ang"`: Computes the phase angle of the data in radians.
    - `"ang_deg"`: Computes the phase angle of the data in degrees.

    If an invalid function string is specified, the method returns ``False``.

    Parameters
    ----------
    data : list, numpy.array
        Numerical values to convert. The format can be ``list`` or ``numpy.array``.
    function : str, optional
        Conversion function. The default is `"dB10"`.

    Returns
    -------
    numpy.array or bool
        Converted data, ``False`` otherwise.

    Examples
    --------
    >>> values = [1, 2, 3, 4]
    >>> conversion_function(values,"dB10")
    array([-inf, 0., 4.77, 6.02])

    >>> conversion_function(values,"abs")
    array([1, 2, 3, 4])

    >>> conversion_function(values,"ang_deg")
    array([ 0., 0., 0., 0.])
    """
    try:
        import numpy as np
    except ImportError:
        settings.logger.error("NumPy is not available. Install it.")
        return False

    function = function or "dB10"
    available_functions = {
        "dB10": lambda x: 10 * np.log10(np.abs(x)),
        "dB20": lambda x: 20 * np.log10(np.abs(x)),
        "abs": np.abs,
        "real": np.real,
        "imag": np.imag,
        "norm": lambda x: np.abs(x) / np.max(np.abs(x)),
        "ang": np.angle,
        "ang_deg": lambda x: np.angle(x, deg=True),
    }

    if function not in available_functions:
        settings.logger.error("Specified conversion is not available.")
        return False

    data = available_functions[function](data)
    return data


class PropsManager(object):
    def __getitem__(self, item):
        """Get the `self.props` key value.

        Parameters
        ----------
        item : str
            Key to search
        """
        item_split = item.split("/")
        if len(item_split) == 1:
            item_split = item_split[0].split("__")
        props = self.props
        found_el = []
        matching_percentage = 1
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = self._recursive_search(props, item_value, matching_percentage)
                # found_el = difflib.get_close_matches(item_value, list(props.keys()), 1, matching_percentage)
                if found_el:
                    props = found_el[1][found_el[2]]
                    # props = props[found_el[0]]
            if found_el:
                return props
            else:
                matching_percentage -= 0.02
        self._app.logger.warning("Key %s not found.Check one of available keys in self.available_properties", item)
        return None

    def __setitem__(self, key, value):
        """Set the `self.props` key value.

        Parameters
        ----------
        key : str
            Key to apply.
        value : int, float, bool, str, dict
            Value to apply.
        """
        item_split = key.split("/")
        if len(item_split) == 1:
            item_split = item_split[0].split("__")
        found_el = []
        props = self.props
        matching_percentage = 1
        key_path = []
        while matching_percentage >= 0.4:
            for item_value in item_split:
                found_el = self._recursive_search(props, item_value, matching_percentage)
                if found_el:
                    props = found_el[1][found_el[2]]
                    key_path.append(found_el[2])
            if found_el:
                if matching_percentage < 1:
                    self._app.logger.info(
                        "Key %s matched internal key '%s' with confidence of %s.",
                        key,
                        "/".join(key_path),
                        round(matching_percentage * 100),
                    )
                matching_percentage = 0

            else:
                matching_percentage -= 0.02
        if found_el:
            found_el[1][found_el[2]] = value
            self.update()
        else:
            props[key] = value
            self.update()
            self._app.logger.warning("Key %s not found. Trying to applying new key ", key)

    @pyaedt_function_handler()
    def _recursive_search(self, dict_in, key="", matching_percentage=0.8):
        f = difflib.get_close_matches(key, list(dict_in.keys()), 1, matching_percentage)
        if f:
            return True, dict_in, f[0]
        else:
            for v in list(dict_in.values()):
                if isinstance(v, dict):
                    out_val = self._recursive_search(v, key, matching_percentage)
                    if out_val:
                        return out_val
                elif isinstance(v, list) and isinstance(v[0], dict):
                    for val in v:
                        out_val = self._recursive_search(val, key, matching_percentage)
                        if out_val:
                            return out_val
        return False

    @pyaedt_function_handler()
    def _recursive_list(self, dict_in, prefix=""):
        available_list = []
        for k, v in dict_in.items():
            if prefix:
                name = prefix + "/" + k
            else:
                name = k
            available_list.append(name)
            if isinstance(v, dict):
                available_list.extend(self._recursive_list(v, name))
        return available_list

    @property
    def available_properties(self):
        """Available properties.

        Returns
        -------
        list
        """
        if self.props:
            return self._recursive_list(self.props)
        return []

    @pyaedt_function_handler()
    def update(self):
        """Update method."""
        pass
