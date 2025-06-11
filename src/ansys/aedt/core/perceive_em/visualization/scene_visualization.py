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

import json
from pathlib import Path
import sys
import warnings

from scipy.interpolate import RegularGridInterpolator

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.general_methods import conversion_function
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers import decompose_variable_value
from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

current_python_version = sys.version_info[:2]
if current_python_version < (3, 10):  # pragma: no cover
    raise Exception("Python 3.10 or higher is required for Monostatic RCS post-processing.")

try:
    import numpy as np
except ImportError:  # pragma: no cover
    warnings.warn(
        "The NumPy module is required to use module rcs_visualization.py.\nInstall with \n\npip install numpy"
    )
    np = None

# Check that graphics are available
try:
    check_graphics_available()

    import pyvista as pv

    from ansys.tools.visualization_interface import MeshObjectPlot
    from ansys.tools.visualization_interface import Plotter
    from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


try:
    import pandas as pd
except ImportError:  # pragma: no cover
    warnings.warn(
        "The Pandas module is required to use module rcs_visualization.py.\nInstall with \n\npip install pandas"
    )
    pd = None

try:
    import scipy.interpolate
except ImportError:  # pragma: no cover
    warnings.warn(
        "The SciPy module is required to use module rcs_visualization.py.\nInstall with \n\npip install scipy"
    )
