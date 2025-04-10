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

import ansys.aedt.core.visualization.report.emi
import ansys.aedt.core.visualization.report.eye
import ansys.aedt.core.visualization.report.field
import ansys.aedt.core.visualization.report.spectral
import ansys.aedt.core.visualization.report.standard

TEMPLATES_BY_DESIGN = {
    "Twin Builder": {"Standard": ansys.aedt.core.visualization.report.standard.Standard},
    "RMxprtSolution": {"RMxprt": ansys.aedt.core.visualization.report.standard.Standard},
    "Circuit Design": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "Spectrum": ansys.aedt.core.visualization.report.spectral.Spectral,
        "EMIReceiver": ansys.aedt.core.visualization.report.emi.EMIReceiver,
        "Eye Diagram": ansys.aedt.core.visualization.report.eye.EyeDiagram,
        "Statistical Eye": ansys.aedt.core.visualization.report.eye.AMIEyeDiagram,
        "AMI Contour": ansys.aedt.core.visualization.report.eye.AMIConturEyeDiagram,
    },
    "HFSS": {
        "Standard": ansys.aedt.core.visualization.report.standard.HFSSStandard,
        "Modal Solution Data": ansys.aedt.core.visualization.report.standard.HFSSStandard,
        "Terminal Solution Data": ansys.aedt.core.visualization.report.standard.HFSSStandard,
        "Far Fields": ansys.aedt.core.visualization.report.field.FarField,
        "Near Fields": ansys.aedt.core.visualization.report.field.NearField,
        "Eigenmode Parameters": ansys.aedt.core.visualization.report.standard.HFSSStandard,
        "Fields": ansys.aedt.core.visualization.report.field.Fields,
        "Emission Test": ansys.aedt.core.visualization.report.standard.EmissionTest,
        "Antenna Parameters": ansys.aedt.core.visualization.report.field.AntennaParameters,
    },
    "HFSS 3D Layout": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "Fields": ansys.aedt.core.visualization.report.field.Fields,
    },
    "Icepak": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "Fields": ansys.aedt.core.visualization.report.field.Fields,
        "Monitor": ansys.aedt.core.visualization.report.standard.Standard,
    },
    "Mechanical": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "Fields": ansys.aedt.core.visualization.report.field.Fields,
    },
    "Q3D Extractor": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "CG Fields": ansys.aedt.core.visualization.report.field.Fields,
        "DC R/L Fields": ansys.aedt.core.visualization.report.field.Fields,
        "AC R/L Fields": ansys.aedt.core.visualization.report.field.Fields,
        "Matrix": ansys.aedt.core.visualization.report.standard.Standard,
    },
    "2D Extractor": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "CG Fields": ansys.aedt.core.visualization.report.field.Fields,
        "AC R/L Fields": ansys.aedt.core.visualization.report.field.Fields,
        "Matrix": ansys.aedt.core.visualization.report.standard.Standard,
    },
    "Maxwell 3D": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "EddyCurrent": ansys.aedt.core.visualization.report.standard.Standard,
        "Fields": ansys.aedt.core.visualization.report.field.Fields,
    },
    "Maxwell 2D": {
        "Standard": ansys.aedt.core.visualization.report.standard.Standard,
        "EddyCurrent": ansys.aedt.core.visualization.report.standard.Standard,
        "Fields": ansys.aedt.core.visualization.report.field.Fields,
    },
}


ORIENTATION_TO_VIEW = {
    "isometric": "iso",
    "top": "XY",
    "bottom": "XY",
    "right": "XZ",
    "left": "XZ",
    "front": "YZ",
    "back": "YZ",
}
