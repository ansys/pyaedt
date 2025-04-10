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


class NamedExpressions:
    """Provides named expressions based on the AEDT application."""

    Maxwell2DExpressions = [
        "Flux_Lines",
        "Mag_H",
        "Mag_B",
        "Jz",
        "A_Vector",
        "H_Vector",
        "B_Vector",
        "J_Vector",
        "energy",
        "coEnergy",
        "appEnergy",
        "Ohmic_Loss",
        "surfaceForceDensity",
        "edgeForceDensity",
        "Temperature",
        "DemagCoef",
        "MagDisplacement",
        "Displacement_Vector",
    ]

    Maxwell3DExpressions = [
        "Mag_H",
        "Mag_B",
        "Mag_J",
        "Mag_Jsurf",
        "Mag_E",
        "Mag_D",
        "ComplexMag_H",
        "ComplexMag_B",
        "ComplexMag_J",
        "ComplexMag_Jsurf",
        "ComplexMag_E",
        "ComplexMag_D",
        "Vector_H",
        "Vector_B",
        "Vector_J",
        "Vector_Jsurf",
        "Vector_E",
        "Vector_D",
        "Energy",
        "Ohmic_Loss",
        "Hysteresis_Loss",
        "Dielectric_Loss",
        "Core_Loss",
        "EM_Loss",
        "Surface_Loss_Density",
        "Temperature",
        "Volume_Force_Density",
        "Surface_Force_Density",
        "Volume_AC_Force_Density",
        "Surface_AC_Force_Density",
        "Volume_Max_Force_Density",
        "Surface_Max_Force_Density",
        "Mag_Displacement",
        "Displacement_Vector",
    ]
