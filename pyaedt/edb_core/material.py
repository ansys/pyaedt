
from __future__ import absolute_import  # noreorder

import difflib
import logging
import math
import warnings

from pyaedt.edb_core.EDB_Data import EDBLayers
from pyaedt.edb_core.EDB_Data import SimulationConfiguration
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler

try:
    import clr
except ImportError:
    warnings.warn("This module requires the PythonNET package.")

logger = logging.getLogger(__name__)


class Material(object):

    def __init__(self):
        pass

    @property
    def _material_list(self):
        self.