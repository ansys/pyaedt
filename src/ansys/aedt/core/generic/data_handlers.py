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

from decimal import Decimal
import math
import re
import secrets
import string
import unicodedata

from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
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
            if isinstance(v[0], dict):
                for rr in v:
                    arg_out.append("Range:=")
                    new_range = []
                    for rk, ri in rr.items():
                        new_range.append(rk + ":=")
                        new_range.append(ri)
                    arg_out.append(new_range)
            elif isinstance(v[0], (list, tuple)):
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
        elif isinstance(v, Quantity):
            arg_out.append(k + ":=")
            arg_out.append(str(v))
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
    elif "NAME:Ranges" in arg[0]:
        dict_out["Ranges"] = {"Range": []}
        for el, val in enumerate(arg[1:]):
            if val == "Range:=":
                rr = {}
                vals = arg[el + 2]
                k = 0
                while k < len(vals):
                    rr[vals[k][:-2]] = vals[k + 1]
                    k += 2
                dict_out["Ranges"]["Range"].append(rr)

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
def format_decimals(el):
    """Provide a formatted string for a decimal number.

    Parameters
    ----------
    el : float, int, str
        Decimal number to be formatted.

    Returns
    -------
    str
    """
    if float(el) > 1000:
        num = f"{Decimal(el):,.0f}"
    elif float(el) > 1:
        num = f"{Decimal(el):,.3f}"
    else:
        num = f"{Decimal(el):.3E}"
    return num


@pyaedt_function_handler()
def random_string(length=6, only_digits=False, char_set=None):
    """Generate a random string.

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
    random_str = "".join(secrets.choice(char_set) for _ in range(int(length)))
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
    if isinstance(element_list, str):
        element_list = [element_list]

    if only_string and any(not isinstance(x, str) for x in element_list):
        raise TypeError("Invalid list entries, some elements are not of type string.")

    return list(set(element_list))


@pyaedt_function_handler()
def string_list(element_list):
    """Convert a string to a list if it is not already a list.

    Input must be a list or a string.

    Parameters
    ----------
    element_list : list, str
        List or strings to be converted to a list.

    Returns
    -------
    list

    """
    if not isinstance(element_list, (str, list)):
        raise TypeError("Input must be a list or a string")
    if isinstance(element_list, str):
        element_list = [element_list]
    return element_list


@pyaedt_function_handler()
def ensure_list(element_list):
    """Ensure that an object is a list.

    If it is not, it will be converted to a list.

    Parameters
    ----------
    element_list : object
        Object to be checked.

    Returns
    -------
    None
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
    >>> from_rkm("R47")
    '0.47'

    >>> from_rkm("4R7")
    '4.7'

    >>> from_rkm("470R")
    '470'

    >>> from_rkm("4K7")
    '4.7k'

    >>> from_rkm("47K")
    '47k'

    >>> from_rkm("47K3")
    '47.3k'

    >>> from_rkm("470K")
    '470k'

    >>> from_rkm("4M7")
    '4.7M'

    """
    # Matches RKM codes that start with a digit.
    # fd_pattern = r'([0-9]+)([LREkKMGTFmuµUnNpP]+)([0-9]*)'
    fd_pattern = f"([0-9]+)([{''.join(RKM_MAPS.keys())}]+)([0-9]*)"
    # matches rkm codes that end with a digit
    # ld_pattern = r'([0-9]*)([LREkKMGTFmuµUnNpP]+)([0-9]+)'
    ld_pattern = f"([0-9]*)([{''.join(RKM_MAPS.keys())}]+)([0-9]+)"

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
    pattern = f"([{''.join(AEDT_MAPS.keys())}]{'{1}'})"
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
    if units not in unit_val:
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
