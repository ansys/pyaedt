# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Explicit HFSS modeling of routed, twisted, shielded cable bundles.

This subpackage builds a fully explicit three-dimensional HFSS model of a cable harness from a
configuration file, which makes it complementary to
:class:`~ansys.aedt.core.modules.cable_modeling.Cable`, which drives the native implicit cable
harness modeler of Ansys Electronics Desktop.

The subpackage is organized as follows:

* :class:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration.CableBundleConfig`
  provides a typed and validated view of the configuration file.
* :mod:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.geometry` implements the
  Electronics Desktop independent mathematics, such as rotation-minimizing frames, twisted
  centerlines, and profile faceting.
* :mod:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.transfer_impedance` implements the
  closed-form foil and braid transfer-impedance models.
* :mod:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models` adapts a shield
  definition to a transfer-impedance model and supports injecting measured data.
* :class:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.bundle.RoutedCableBundle` creates the
  explicit HFSS geometry, the shield boundaries, the ports, and the differential pairs.

Examples
--------
>>> from ansys.aedt.core import Hfss
>>> from ansys.aedt.core.modeler.advanced_cad.cable_harness import RoutedCableBundle
>>> hfss = Hfss(solution_type="Terminal")  # doctest: +SKIP
>>> bundle = RoutedCableBundle.from_file("cat6a_sstp_awg25.yaml", hfss)  # doctest: +SKIP
>>> bundle.build()  # doctest: +SKIP
>>> bundle.create_setup()  # doctest: +SKIP
"""

from ansys.aedt.core.modeler.advanced_cad.cable_harness.bundle import BuildArtifacts
from ansys.aedt.core.modeler.advanced_cad.cable_harness.bundle import RoutedCableBundle
from ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration import CableBundleConfig
from ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models import MeasuredShield
from ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models import ShieldModel
from ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models import build_shield_model

__all__ = [
    "BuildArtifacts",
    "CableBundleConfig",
    "MeasuredShield",
    "RoutedCableBundle",
    "ShieldModel",
    "build_shield_model",
]
