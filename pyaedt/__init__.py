# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

pyaedt_path = os.path.dirname(__file__)

__version__ = "0.8.dev0"

version = __version__
import pyaedt.downloads as downloads
from pyaedt.generic import constants
import pyaedt.generic.DataHandlers as data_handler
import pyaedt.generic.general_methods as general_methods
from pyaedt.generic.general_methods import _pythonver
from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import generate_unique_folder_name
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import generate_unique_project_name
from pyaedt.generic.general_methods import inside_desktop
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.general_methods import is_windows
from pyaedt.generic.general_methods import online_help
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import settings

try:
    from pyaedt.generic.design_types import Hfss3dLayout
except:
    from pyaedt.generic.design_types import Hfss3dLayout

from pyaedt.generic.design_types import Circuit
from pyaedt.generic.design_types import Desktop
from pyaedt.generic.design_types import Edb
from pyaedt.generic.design_types import Emit
from pyaedt.generic.design_types import Hfss
from pyaedt.generic.design_types import Icepak
from pyaedt.generic.design_types import Maxwell2d
from pyaedt.generic.design_types import Maxwell3d
from pyaedt.generic.design_types import MaxwellCircuit
from pyaedt.generic.design_types import Mechanical
from pyaedt.generic.design_types import Q2d
from pyaedt.generic.design_types import Q3d
from pyaedt.generic.design_types import Rmxprt
from pyaedt.generic.design_types import Simplorer
from pyaedt.generic.design_types import Siwave
from pyaedt.generic.design_types import TwinBuilder
from pyaedt.generic.design_types import get_pyaedt_app
from pyaedt.generic.design_types import launch_desktop
from pyaedt.misc import current_student_version
from pyaedt.misc import current_version
from pyaedt.misc import installed_versions
