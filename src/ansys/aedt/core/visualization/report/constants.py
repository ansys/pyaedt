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

TEMPLATES_BY_DESIGN = {
    "HFSS": [
        "Modal Solution Data",
        "Terminal Solution Data",
        "Eigenmode Parameters",
        "Fields",
        "Far Fields",
        "Emissions",
        "Near Fields",
        "Antenna Parameters",
    ],
    "Maxwell 3D": [
        "Transient",
        "EddyCurrent",
        "Magnetostatic",
        "Electrostatic",
        "DCConduction",
        "ElectroDCConduction",
        "ElectricTransient",
        "Fields",
        "Spectrum",
    ],
    "Maxwell 2D": [
        "Transient",
        "EddyCurrent",
        "Magnetostatic",
        "Electrostatic",
        "ElectricTransient",
        "ElectroDCConduction",
        "Fields",
        "Spectrum",
    ],
    "Icepak": ["Monitor", "Fields"],
    "Circuit Design": ["Standard", "Eye Diagram", "Statistical Eye", "Spectrum", "EMIReceiver"],
    "HFSS 3D Layout": ["Standard", "Fields", "Spectrum"],
    "HFSS 3D Layout Design": ["Standard", "Fields", "Spectrum"],
    "Mechanical": ["Standard", "Fields"],
    "Q3D Extractor": ["Matrix", "CG Fields", "DC R/L Fields", "AC R/L Fields"],
    "2D Extractor": ["Matrix", "CG Fields", "RL Fields"],
    "Twin Builder": ["Standard", "Spectrum"],
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
