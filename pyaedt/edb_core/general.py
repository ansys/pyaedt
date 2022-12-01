"""
This module contains EDB general methods and related methods.

"""

from __future__ import absolute_import  # noreorder

import logging

from pyaedt.generic.clr_module import Dictionary
from pyaedt.generic.clr_module import List
from pyaedt.generic.clr_module import Tuple
from pyaedt.generic.general_methods import pyaedt_function_handler

logger = logging.getLogger(__name__)


@pyaedt_function_handler()
def convert_netdict_to_pydict(dict_in):
    """Convert a net dictionary to a Python dictionary.

    Parameters
    ----------
    dict_in : dict
        Net dictionary to convert.

    Returns
    -------
    dict
        Dictionary converted to Python.

    """
    pydict = {}
    for key in dict_in.Keys:
        pydict[key] = dict_in[key]
    return pydict


@pyaedt_function_handler()
def convert_pytuple_to_nettuple(_tuple):
    """Convert a Python tuple into a .NET tuple.
    Parameters
    ----------
    tuple : Python tuple

    Returns
    -------
    .NET tuple.
    """
    return Tuple.Create(_tuple[0], _tuple[1])


@pyaedt_function_handler()
def convert_pydict_to_netdict(input_dict):
    """Convert a Python dictionary to a .NET dictionary.

    Parameters
    ----------
    input_dict : dict
        Python dictionary to convert.


    Returns
    -------
    dict
        Dictionary converted to Net.
    """
    net_dict = Dictionary[type(list(input_dict.keys())[0]), type(list(input_dict.values())[0])]()
    for k1, v1 in input_dict.items():  # pragma: no cover
        net_dict[k1] = v1
    return net_dict
    # to be completed


@pyaedt_function_handler()
def convert_py_list_to_net_list(pylist, list_type=None):
    """Convert a Python list to a Net list.

    Parameters
    ----------
    pylist : list
        Python list to convert.

    Returns
    -------
    list
        List converted to Net.
    """
    if not isinstance(pylist, (list, tuple)):
        pylist = [pylist]
    ls = list([type(item) for item in pylist])
    if len(ls) > 0:
        if list_type:
            net_list = List[list_type]()
        else:
            net_list = List[ls[0]]()
        for el in pylist:
            net_list.Add(el)
        return net_list


@pyaedt_function_handler()
def convert_net_list_to_py_list(netlist):
    """Convert a Net list to a Python list.

    Parameters
    ----------
    netlist : list
       Net list to convert.


    Returns
    -------
    list
        List converted to Python.
    """
    pylist = []
    for el in netlist:
        pylist.__add__(el)
    return pylist
