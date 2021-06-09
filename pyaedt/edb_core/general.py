"""
General Methods
-------------------

This class manages Edb General Methods and related methods


"""
from __future__ import absolute_import
import warnings


try:
    import clr
    clr.AddReference("System.Collections")
    from System.Collections.Generic import List
    from System import Int32
except ImportError:
    warnings.warn('This module requires pythonnet.')


import inspect
import itertools
import sys
import traceback
from collections import OrderedDict
from functools import wraps
import logging
logger = logging.getLogger(__name__)
from ..generic.general_methods import aedt_exception_handler, generate_unique_name

if "IronPython" in sys.version or ".NETFramework" in sys.version:
    is_ironpython = True
else:
    is_ironpython = False


@aedt_exception_handler
def convert_netdict_to_pydict(dict):
    """

    Parameters
    ----------
    dict :
        

    Returns
    -------

    """
    pydict = {}
    for key in dict.Keys:
        pydict[key] = dict[key]
    return pydict

@aedt_exception_handler
def convert_pydict_to_netdict(dict):
    """

    Parameters
    ----------
    dict :
        

    Returns
    -------

    """
    type = dict[dict.Keys[0]]
    # to be completed

@aedt_exception_handler
def convert_py_list_to_net_list(pylist):
    """

    Parameters
    ----------
    pylist :
        

    Returns
    -------

    """
    if type(pylist) is not list and type(pylist) is not tuple:
        pylist = [pylist]
    ls = list([type(item) for item in pylist])
    if len(ls) > 0:
        net_list = List[ls[0]]()
        for el in pylist:
            net_list.Add(el)
        return net_list

@aedt_exception_handler
def convert_net_list_to_py_list(self, netlist):
    """

    Parameters
    ----------
    netlist :
        

    Returns
    -------

    """
    pylist = []
    for el in netlist:
        pylist.__add__(el)
    return pylist
