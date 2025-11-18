# ruff: noqa: E402

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

import os
import sys
import warnings

if os.name == "nt":
    os.environ["PYTHONMALLOC"] = "malloc"

LATEST_DEPRECATED_PYTHON_VERSION = (3, 9)
PYTHON_VERSION_WARNING = (
    "As part of our ongoing efforts to align with the Python Scientific Community's "
    "best practices, we are moving towards adopting SPEC 0000 "
    "(https://scientific-python.org/specs/spec-0000/). To ensure compatibility and "
    "take full advantage of the latest features and improvements, we strongly "
    "recommend updating the Python version being used."
)
DOTNET_LINUX_WARNING = (
    "Due to compatibility issues between .NET Core and libssl on some Linux versions, "
    "for example Ubuntu 22.04, we are going to stop depending on `dotnetcore2`."
    "Instead of using this package which embeds .NET Core 3, users will be required to "
    "install .NET themselves. For more information, see "
    "https://aedt.docs.pyansys.com/version/stable/release_1_0.html#dotnet-changes-in-linux"
)


def deprecation_warning():
    """Warning message informing users that some Python versions are deprecated in PyAEDT."""
    # Store warnings showwarning
    existing_showwarning = warnings.showwarning

    # Define and use custom showwarning
    def custom_show_warning(message, category, filename, lineno, file=None, line=None):
        """Define and use custom warning to remove <stdin>:loc: pattern."""
        print(f"{category.__name__}: {message}")

    warnings.showwarning = custom_show_warning

    current_python_version = sys.version_info[:2]
    if current_python_version <= LATEST_DEPRECATED_PYTHON_VERSION:
        warnings.warn(PYTHON_VERSION_WARNING, FutureWarning)

    # Restore warnings showwarning
    warnings.showwarning = existing_showwarning


deprecation_warning()

#

pyaedt_path = os.path.dirname(__file__)
__version__ = "0.22.2"
version = __version__

# isort: off
# Settings have to be imported before importing other PyAEDT modules
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.generic.settings import inner_project_settings

# isort: on

if ".NETFramework" not in sys.version:  # pragma: no cover
    import ansys.aedt.core.examples.downloads as downloads

from ansys.aedt.core.circuit import Circuit
from ansys.aedt.core.circuit_netlist import CircuitNetlist
from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.edb import Edb
from ansys.aedt.core.edb import Siwave
from ansys.aedt.core.emit import Emit
from ansys.aedt.core.generic import constants
import ansys.aedt.core.generic.data_handlers as data_handler
from ansys.aedt.core.generic.design_types import Simplorer
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.generic.design_types import launch_desktop
from ansys.aedt.core.generic.file_utils import generate_unique_folder_name
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import generate_unique_project_name
import ansys.aedt.core.generic.general_methods as general_methods
from ansys.aedt.core.generic.general_methods import _retry_ntimes
from ansys.aedt.core.generic.general_methods import inside_desktop_ironpython_console
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.generic.general_methods import online_help
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.icepak import Icepak
from ansys.aedt.core.maxwell import Maxwell2d
from ansys.aedt.core.maxwell import Maxwell3d
from ansys.aedt.core.maxwellcircuit import MaxwellCircuit
from ansys.aedt.core.mechanical import Mechanical
from ansys.aedt.core.q3d import Q2d
from ansys.aedt.core.q3d import Q3d
from ansys.aedt.core.rmxprt import Rmxprt
from ansys.aedt.core.twinbuilder import TwinBuilder

__all__ = [
    "settings",
    "inner_project_settings",
    "downloads",
    "Edb",
    "Siwave",
    "constants",
    "data_handler",
    "Circuit",
    "CircuitNetlist",
    "Desktop",
    "Emit",
    "Hfss",
    "Hfss3dLayout",
    "Icepak",
    "Maxwell2d",
    "Maxwell3d",
    "MaxwellCircuit",
    "Mechanical",
    "Q2d",
    "Q3d",
    "Rmxprt",
    "Simplorer",
    "TwinBuilder",
    "get_pyaedt_app",
    "launch_desktop",
    "generate_unique_folder_name",
    "generate_unique_name",
    "generate_unique_project_name",
    "general_methods",
    "_retry_ntimes",
    "inside_desktop_ironpython_console",
    "is_linux",
    "is_windows",
    "online_help",
    "pyaedt_function_handler",
    "Quantity",
]
