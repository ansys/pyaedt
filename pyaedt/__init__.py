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
__version__ = "0.9.6"
version = __version__

#
if not ("IronPython" in sys.version or ".NETFramework" in sys.version):  # pragma: no cover
    import pyaedt.downloads as downloads
from pyaedt.edb import Edb  # nosec
from pyaedt.edb import Siwave  # nosec
from pyaedt.generic import constants
import pyaedt.generic.DataHandlers as data_handler
from pyaedt.generic.design_types import Circuit
from pyaedt.generic.design_types import Desktop
from pyaedt.generic.design_types import Emit
from pyaedt.generic.design_types import Hfss
from pyaedt.generic.design_types import Hfss3dLayout
from pyaedt.generic.design_types import Icepak
from pyaedt.generic.design_types import Maxwell2d
from pyaedt.generic.design_types import Maxwell3d
from pyaedt.generic.design_types import MaxwellCircuit
from pyaedt.generic.design_types import Mechanical
from pyaedt.generic.design_types import Q2d
from pyaedt.generic.design_types import Q3d
from pyaedt.generic.design_types import Rmxprt
from pyaedt.generic.design_types import Simplorer
from pyaedt.generic.design_types import TwinBuilder
from pyaedt.generic.design_types import get_pyaedt_app
from pyaedt.generic.design_types import launch_desktop
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
from pyaedt.misc import current_student_version
from pyaedt.misc import current_version
from pyaedt.misc import installed_versions
