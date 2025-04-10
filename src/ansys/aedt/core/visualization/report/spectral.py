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

"""
This module contains this class: `Spectral`.

This module provides all functionalities for creating and editing reports.

"""

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.visualization.report.common import CommonReport


class Spectral(CommonReport):
    """Provides for managing spectral reports from transient data."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Spectrum"
        self.algorithm = "FFT"
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self.window = "Rectangular"
        self.kaiser_coeff = 0
        self.adjust_coherent_gain = True
        self.max_frequency = "10MHz"
        self.plot_continous_spectrum = False
        self.primary_sweep = "Spectrum"

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start.
        """
        return self._legacy_props["context"].get("time_start", "0s")

    @time_start.setter
    def time_start(self, value):
        self._legacy_props["context"]["time_start"] = value

    @property
    def time_stop(self):
        """Time stop value.

        Returns
        -------
        str
            Time stop.
        """
        return self._legacy_props["context"].get("time_stop", "100ns")

    @time_stop.setter
    def time_stop(self, value):
        self._legacy_props["context"]["time_stop"] = value

    @property
    def window(self):
        """Window value.

        Returns
        -------
        str
            Window.
        """
        return self._legacy_props["context"].get("window", "Rectangular")

    @window.setter
    def window(self, value):
        self._legacy_props["context"]["window"] = value

    @property
    def kaiser_coeff(self):
        """Kaiser value.

        Returns
        -------
        str
            Kaiser coefficient.
        """
        return self._legacy_props["context"].get("kaiser_coeff", 0)

    @kaiser_coeff.setter
    def kaiser_coeff(self, value):
        self._legacy_props["context"]["kaiser_coeff"] = value

    @property
    def adjust_coherent_gain(self):
        """Coherent gain flag.

        Returns
        -------
        bool
            ``True`` if coherent gain is enabled, ``False`` otherwise.
        """
        return self._legacy_props["context"].get("adjust_coherent_gain", False)

    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value):
        self._legacy_props["context"]["adjust_coherent_gain"] = value

    @property
    def plot_continous_spectrum(self):
        """Continuous spectrum flag.

        Returns
        -------
        bool
            ``True`` if continuous spectrum is enabled, ``False`` otherwise.
        """
        return self._legacy_props["context"].get("plot_continous_spectrum", False)

    @plot_continous_spectrum.setter
    def plot_continous_spectrum(self, value):
        self._legacy_props["context"]["plot_continous_spectrum"] = value

    @property
    def max_frequency(self):
        """Maximum spectrum frequency.

        Returns
        -------
        str
            Maximum spectrum frequency.
        """
        return self._legacy_props["context"].get("max_frequency", "10GHz")

    @max_frequency.setter
    def max_frequency(self, value):
        self._legacy_props["context"]["max_frequency"] = value

    @property
    def _context(self):
        if self.algorithm == "FFT":
            it = "1"
        elif self.algorithm == "Fourier Integration":
            it = "0"
        else:
            it = "2"
        WT = {
            "Rectangular": "0",
            "Bartlett": "1",
            "Blackman": "2",
            "Hamming": "3",
            "Hanning": "4",
            "Kaiser": "5",
            "Welch": "6",
            "Weber": "7",
            "Lanzcos": "8",
        }
        wt = WT[self.window]
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                2,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "CP",
                False,
                "1" if self.plot_continous_spectrum else "0",
                "IT",
                False,
                it,
                "MF",
                False,
                self.max_frequency,
                "NUMLEVELS",
                False,
                "0",
                "TE",
                False,
                self.time_stop,
                "TS",
                False,
                self.time_start,
                "WT",
                False,
                wt,
                "WW",
                False,
                "100",
                "KP",
                False,
                str(self.kaiser_coeff),
                "CG",
                False,
                "1" if self.adjust_coherent_gain else "0",
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return self.expressions
        else:
            return [self.expressions]

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create an eye diagram report.

        Parameters
        ----------
        name : str, optional
            Plot name. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            "Standard",
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self._trace_info,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True
        oo = self._post.oreportsetup.GetChildObject(self._legacy_props["plot_name"])
        if oo:
            BinaryTreeNode.__init__(self, self.plot_name, oo, False, app=self._app)
        return True
