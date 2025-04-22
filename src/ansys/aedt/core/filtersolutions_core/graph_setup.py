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

from ctypes import c_char_p
from ctypes import c_int

import ansys.aedt.core


class GraphSetup:
    """Defines the frequency and time limits of the exported responses.

    This class allows you to configure the graph limit parameters.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_graph_dll_functions()

    def _define_graph_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setPlotMinimumFrequency.argtype = c_char_p
        self._dll.setPlotMinimumFrequency.restype = c_int
        self._dll.getPlotMinimumFrequency.argtypes = [c_char_p, c_int]
        self._dll.getPlotMinimumFrequency.restype = c_int

        self._dll.setPlotMaximumFrequency.argtype = c_char_p
        self._dll.setPlotMaximumFrequency.restype = c_int
        self._dll.getPlotMaximumFrequency.argtypes = [c_char_p, c_int]
        self._dll.getPlotMaximumFrequency.restype = c_int

        self._dll.setPlotMinimumTime.argtype = c_char_p
        self._dll.setPlotMinimumTime.restype = c_int
        self._dll.getPlotMinimumTime.argtypes = [c_char_p, c_int]
        self._dll.getPlotMinimumTime.restype = c_int

        self._dll.setPlotMaximumTime.argtype = c_char_p
        self._dll.setPlotMaximumTime.restype = c_int
        self._dll.getPlotMaximumTime.argtypes = [c_char_p, c_int]
        self._dll.getPlotMaximumTime.restype = c_int

    @property
    def minimum_frequency(self) -> str:
        """Minimum frequency value for exporting frequency and S parameter responses. The default is ``200 MHz``.

        Returns
        -------
        str
        """
        min_freq_string = self._dll_interface.get_string(self._dll.getPlotMinimumFrequency)
        return min_freq_string

    @minimum_frequency.setter
    def minimum_frequency(self, min_freq_string):
        self._dll_interface.set_string(self._dll.setPlotMinimumFrequency, min_freq_string)

    @property
    def maximum_frequency(self) -> str:
        """Maximum frequency value for exporting frequency and S parameters responses. The default is ``5 GHz``.

        Returns
        -------
        str
        """
        max_freq_string = self._dll_interface.get_string(self._dll.getPlotMaximumFrequency)
        return max_freq_string

    @maximum_frequency.setter
    def maximum_frequency(self, max_freq_string):
        self._dll_interface.set_string(self._dll.setPlotMaximumFrequency, max_freq_string)

    @property
    def minimum_time(self) -> str:
        """Minimum time value for exporting time response. The default is ``0 s``.

        Returns
        -------
        str
        """
        min_time_string = self._dll_interface.get_string(self._dll.getPlotMinimumTime)
        return min_time_string

    @minimum_time.setter
    def minimum_time(self, min_time_string):
        self._dll_interface.set_string(self._dll.setPlotMinimumTime, min_time_string)

    @property
    def maximum_time(self) -> str:
        """Maximum time value for exporting time response. The default is ``10 ns``.

        Returns
        -------
        str
        """
        max_time_string = self._dll_interface.get_string(self._dll.getPlotMaximumTime)
        return max_time_string

    @maximum_time.setter
    def maximum_time(self, max_time_string):
        self._dll_interface.set_string(self._dll.setPlotMaximumTime, max_time_string)
