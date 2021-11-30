# -*- coding: utf-8 -*-

import os

os.environ["ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE"] = "1"
os.environ["ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE"] = "1"

from pyaedt.generic import constants
from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name, _retry_ntimes
from pyaedt.generic.general_methods import is_ironpython, _pythonver, inside_desktop, convert_remote_object
from pyaedt.aedt_logger import AedtLogger
try:
    from pyaedt.generic.design_types import Hfss3dLayout
except:
    from pyaedt.generic.design_types import Hfss3dLayout

from pyaedt.generic.design_types import (Hfss,
                                         Circuit,
                                         Q2d,
                                         Q3d,
                                         Siwave,
                                         Icepak,
                                         Edb,
                                         Maxwell3d,
                                         Maxwell2d,
                                         Mechanical,
                                         Rmxprt,
                                         Simplorer,
                                         Emit,
                                         get_pyaedt_app,
                                         Desktop)




