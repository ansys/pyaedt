# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import warnings

# Issue deprecation warning
_deprecation_message = (
    "The 'rcs_visualization' module has been deprecated and moved to the radar explorer toolkit. "
    "Advanced RCS features (MonostaticRCSData and MonostaticRCSPlotter) are now available in the "
    "'ansys-aedt-toolkits-radar-explorer' package.\n\n"
    "To continue using RCS visualization features, please install the radar explorer toolkit:\n"
    "    pip install ansys-aedt-toolkits-radar-explorer\n\n"
    "For RCS data export from PyAEDT, use the MonostaticRCSExporter class:\n"
    "    from ansys.aedt.core import Hfss\n"
    "    app = Hfss()\n"
    "    rcs_exporter = app.get_rcs_data(frequencies=frequencies, setup=setup_name)\n\n"
    "For RCS analysis and visualization, use the radar explorer toolkit:\n"
    "    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData\n"
    "    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter\n\n"
    "For complete documentation, visit:\n"
    "https://aedt.radar.explorer.toolkit.docs.pyansys.com/version/stable/toolkit/api.html"
)

warnings.warn(_deprecation_message, DeprecationWarning, stacklevel=2)

raise ImportError(
    "The 'rcs_visualization' module is no longer available in PyAEDT. "
    "RCS functionality has been moved to the 'ansys-aedt-toolkits-radar-explorer' package. "
    "Install it with: pip install ansys-aedt-toolkits-radar-explorer"
)
