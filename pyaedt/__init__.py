# -*- coding: utf-8 -*-
import os
import sys
import warnings

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

LATEST_DEPRECATED_PYTHON_VERSION = (3, 7)


def deprecation_warning():
    """Warning message informing users that some Python versions are deprecated in PyAEDT."""
    # Store warnings showwarning
    existing_showwarning = warnings.showwarning

    # Define and use custom showwarning
    def custom_show_warning(message, category, filename, lineno, file=None, line=None):
        """Custom warning used to remove <stdin>:loc: pattern."""
        print("{}: {}".format(category.__name__, message))

    warnings.showwarning = custom_show_warning

    current_version = sys.version_info[:2]
    if current_version <= LATEST_DEPRECATED_PYTHON_VERSION:
        str_current_version = "{}.{}".format(*sys.version_info[:2])
        warnings.warn(
            "Current python version ({}) is deprecated in PyAEDT. We encourage you "
            "to upgrade to the latest version to benefit from the latest features "
            "and security updates.".format(str_current_version),
            PendingDeprecationWarning,
        )

    # Restore warnings showwarning
    warnings.showwarning = existing_showwarning


deprecation_warning()

#

pyaedt_path = os.path.dirname(__file__)
__version__ = "0.9.3"
version = __version__

#

import pyaedt.downloads as downloads
from pyaedt.generic import constants
import pyaedt.generic.DataHandlers as data_handler
import pyaedt.generic.general_methods as general_methods
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
except Exception:
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
