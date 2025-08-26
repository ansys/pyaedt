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

from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_double
from ctypes import c_int
from enum import Enum
import math

import ansys.aedt.core
from ansys.aedt.core.filtersolutions_core.graph_setup import GraphSetup


class FrequencyResponseColumn(Enum):
    """Provides an enum of frequency response parameters.

    **Attributes:**

    - MAGNITUDE_DB: Represents the frequency response magnitude in dB.
    - PHASE_DEG: Represents the frequency response phase in degree.
    - GROUP_DELAY: Represents the frequency response group delay.
    - PHASE_RAD: Represents the frequency response phase in radian.
    - MAGNITUDE_ARITH: Represents the frequency response magnitude.
    - MAGNITUDE_REAL: Represents the real part of frequency response magnitude.
    - MAGNITUDE_IMAG: Represents the imaginary part of frequency response magnitude.
    - PHASE_DEV_DEG: Represents the frequency response phase deviation in degrees.
    - PHASE_DEV_RAD: Represents the frequency response phase deviation in radian.
    - FREQUENCY: Represents frequency parameter of the frequency response .
    """

    MAGNITUDE_DB = 0
    PHASE_DEG = 1
    GROUP_DELAY = 2
    PHASE_RAD = 4
    MAGNITUDE_ARITH = 3
    MAGNITUDE_REAL = 5
    MAGNITUDE_IMAG = 6
    PHASE_DEV_DEG = 7
    PHASE_DEV_RAD = 8
    FREQUENCY = 9


class TimeResponseColumn(Enum):
    """Provides an enum of time response parameters.

    **Attributes:**

    - STEP_RESPONSE: Represents the step time response.
    - RAMP_RESPONSE: Represents the ramp time response.
    - IMPULSE_RESPONSE: Represents the impulse time response.
    - STEP_RESPONSE_DB: Represents the step time response in dB.
    - RAMP_RESPONSE_DB: Represents the ramp time response in dB.
    - IMPULSE_RESPONSE_DB: Represents the impulse time response in dB.
    - TIME: Represents time parameter of the time response .
    """

    STEP_RESPONSE = 0
    RAMP_RESPONSE = 1
    IMPULSE_RESPONSE = 2
    STEP_RESPONSE_DB = 3
    RAMP_RESPONSE_DB = 4
    IMPULSE_RESPONSE_DB = 5
    TIME = 6


class SParametersResponseColumn(Enum):
    """Provides an enum of S parameters.

    **Attributes:**

    - S21_DB: Represents the S21 parameter in dB.
    - S11_DB: Represents the S11 parameter in dB.
    - S21_ARITH: Represents the S21 parameter.
    - S11_ARITH: Represents the S11 parameter.
    - FREQUENCY: Represents the S parameters' frequency parameter.
    """

    S21_DB = 0
    S11_DB = 1
    S21_ARITH = 3
    S11_ARITH = 4
    FREQUENCY = 5


class PoleZerosResponseColumn(Enum):
    """Provides an enum of pole zero x and y coordinates of transmission (TX) or reflection (RX) zeros.

    **Attributes:**

    - TX_ZERO_DEN_X: Represents the x coordinate of the filter transmission zero denominator.
    - TX_ZERO_DEN_Y: Represents the y coordinate of the filter transmission zero denominator.
    - PROTO_TX_ZERO_DEN_X: Represents the x coordinate of the prototype filter transmission zero denominator.
    - PROTO_TX_ZERO_DEN_Y: Represents the y coordinate of the prototype filter transmission zero denominator.
    - TX_ZERO_NUM_X: Represents the x coordinate of the filter transmission zero numerator.
    - TX_ZERO_NUM_Y: Represents the y coordinate of the filter transmission zero numerator.
    - PROTO_TX_ZERO_NUM_X: Represents the x coordinate of the prototype filter transmission zero numerator.
    - PROTO_TX_ZERO_NUM_Y: Represents the y coordinate of the prototype filter transmission zero numerator.
    - RX_ZERO_DEN_X: Represents the x coordinate of the filter reflection zero denominator.
    - RX_ZERO_DEN_Y: Represents the y coordinate of the filter reflection zero denominator.
    - PROTO_RX_ZERO_DEN_X: Represents the x coordinate of the prototype filter reflection zero denominator.
    - PROTO_RX_ZERO_DEN_Y: Represents the y coordinate of the prototype filter reflection zero denominator.
    - RX_ZERO_NUM_X: Represents the x coordinate of the filter reflection zero numerator.
    - RX_ZERO_NUM_Y: Represents the y coordinate of the filter reflection zero numerator.
    - PROTO_RX_ZERO_NUM_X: Represents the x coordinate of the prototype filter reflection zero numerator.
    - PROTO_RX_ZERO_NUM_Y: Represents the y coordinate of the prototype filter reflection zero numerator.
    """

    TX_ZERO_DEN_X = 0
    TX_ZERO_DEN_Y = 1
    PROTO_TX_ZERO_DEN_X = 2
    PROTO_TX_ZERO_DEN_Y = 3
    TX_ZERO_NUM_X = 4
    TX_ZERO_NUM_Y = 5
    PROTO_TX_ZERO_NUM_X = 6
    PROTO_TX_ZERO_NUM_Y = 7
    RX_ZERO_DEN_X = 8
    RX_ZERO_DEN_Y = 9
    PROTO_RX_ZERO_DEN_X = 10
    PROTO_RX_ZERO_DEN_Y = 11
    RX_ZERO_NUM_X = 12
    RX_ZERO_NUM_Y = 13
    PROTO_RX_ZERO_NUM_X = 14
    PROTO_RX_ZERO_NUM_Y = 15


class IdealResponse:
    """Returns the data for available ideal filter responses.

    Types of responses Include ``frequency``, ``time``, ``S parameters``, ``transfer function``,
    and ``pole zero location``.

    This class allows you to define and modify the ideal response parameters for the designed filter.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_response_dll_functions()
        self.graph_setup = GraphSetup()

    def _define_response_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.getIdealFrequencyResponseSize.argtype = POINTER(c_int)
        self._dll.getIdealFrequencyResponseSize.restype = c_int
        self._dll.getIdealFrequencyResponse.argtypes = [POINTER(c_double), c_int, c_int]
        self._dll.getIdealFrequencyResponse.restype = c_int

        self._dll.getIdealTimeResponseSize.argtype = POINTER(c_int)
        self._dll.getIdealTimeResponseSize.restype = c_int
        self._dll.getIdealTimeResponse.argtypes = [POINTER(c_double), c_int, c_int]
        self._dll.getIdealTimeResponse.restype = c_int

        self._dll.getIdealSParamatersResponseSize.argtype = POINTER(c_int)
        self._dll.getIdealSParamatersResponseSize.restype = c_int
        self._dll.getIdealSParamatersResponse.argtypes = [
            POINTER(c_double),
            c_int,
            c_int,
        ]
        self._dll.getIdealSParamatersResponse.restype = c_int

        self._dll.getIdealPoleZerosResponseSize.argtypes = [POINTER(c_int), c_int]
        self._dll.getIdealPoleZerosResponseSize.restype = c_int
        self._dll.getIdealPoleZerosResponse.argtypes = [POINTER(c_double), c_int, c_int]
        self._dll.getIdealPoleZerosResponse.restype = c_int

        self._dll.getIdealTransferFunctionResponseSize.argtype = POINTER(c_int)
        self._dll.getIdealTransferFunctionResponseSize.restype = c_int
        self._dll.getIdealTransferFunctionResponse.argtypes = [c_char_p, c_int]
        self._dll.getIdealTransferFunctionResponse.restype = c_int

        self._dll.setVSGAnalsyis.argtype = c_bool
        self._dll.setVSGAnalsyis.restype = c_int
        self._dll.getVSGAnalsyis.argtype = POINTER(c_bool)
        self._dll.getVSGAnalsyis.restype = c_int

    def _frequency_response_getter(self, column: FrequencyResponseColumn):
        """Get the ideal filter frequency response.

        Parameters
        ----------
        column: `FrequencyResponseColumn`
            Frequency response column to get.

        Returns
        -------
        list
            List of values for the requested frequency response column (such as magnitude or phase).
        """
        size = c_int()
        status = self._dll.getIdealFrequencyResponseSize(byref(size))
        self._dll_interface.raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealFrequencyResponse(array, size.value, column.value)
        self._dll_interface.raise_error(status)
        values = [float(val) for val in array]
        return values

    def _time_response_getter(self, column: TimeResponseColumn):
        """Get the ideal filter time response.

        Parameters
        ----------
        column: `TimeResponseColumn`
            Time response column to get.

        Returns
        -------
        list
            List of values for the requested time response column (such as step or pulse).
        """
        size = c_int()
        status = self._dll.getIdealTimeResponseSize(byref(size))
        self._dll_interface.raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealTimeResponse(array, size.value, column.value)
        self._dll_interface.raise_error(status)
        values = [float(val) for val in array]
        return values

    def _sparamaters_response_getter(self, column: SParametersResponseColumn):
        """Get the ideal filter S parameter's response.

        Parameters
        ----------
        column: `SParametersResponseColumn`
            S parameter's response column to get.

        Returns
        -------
        list
            List of values for the requested S parameter's response column (such as S11 or S21).
        """
        size = c_int()
        status = self._dll.getIdealSParamatersResponseSize(byref(size))
        self._dll_interface.raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealSParamatersResponse(array, size.value, column.value)
        self._dll_interface.raise_error(status)
        values = [float(val) for val in array]
        return values

    def _pole_zeros_response_getter(self, column: PoleZerosResponseColumn):
        """Get the ideal pole zero's location parameters (such as the x coordinate of
        the denominator of transmission zeros).

        Parameters
        ----------
        column: `PoleZerosResponseColumn`
            Pole zero's response column to get.

        Returns
        -------
        list
            List of values for the requested pole zero's response column.
        """
        size = c_int()
        status = self._dll.getIdealPoleZerosResponseSize(byref(size), column.value)
        self._dll_interface.raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealPoleZerosResponse(array, size.value, column.value)
        self._dll_interface.raise_error(status)
        values = [float(val) for val in array]
        return values

    def transfer_function_response(self):
        """Get the ideal filter transfer function's parameters.

        Returns
        -------
        str
            Requested parameter array.

            str
                Multi-line string where each line contains a coefficient from
                the numerator and/or the denominator of the transfer function.
                The coefficient for the highest-order term is first, and the terms are in decreasing order.
        """
        size = c_int()
        status = self._dll.getIdealTransferFunctionResponseSize(byref(size))
        self._dll_interface.raise_error(status)
        transfer_function_response_string = self._dll_interface.get_string(
            self._dll.getIdealTransferFunctionResponse, max_size=size.value
        )
        return transfer_function_response_string

    @property
    def vsg_analysis_enabled(self) -> bool:
        """Flag indicating if the offset due to source resistor in frequency and time responses is enabled.

        Returns
        -------
        bool
        """
        vsg_analysis_enabled = c_bool()
        status = self._dll.getVSGAnalsyis(byref(vsg_analysis_enabled))
        self._dll_interface.raise_error(status)
        return bool(vsg_analysis_enabled.value)

    @vsg_analysis_enabled.setter
    def vsg_analysis_enabled(self, filter_vsg_analysis_enabled: bool):
        status = self._dll.setVSGAnalsyis(filter_vsg_analysis_enabled)
        self._dll_interface.raise_error(status)

    def frequency_response(
        self,
        y_axis_parameter=FrequencyResponseColumn.MAGNITUDE_DB,
        minimum_frequency=None,
        maximum_frequency=None,
        vsg_analysis_enabled=False,
    ):
        """Get the ideal filter frequency response for the given parameters.

        Parameters
        ----------
        y_axis_parameter: `FrequencyResponseColumn`, optional
             Frequency response column to return. The default is the frequency response magnitude in dB.
        minimum_frequency: str, optional
            Minimum frequency to set for the frequency response.
            If the minimum frequency is not given, the existing minimum frequency of the graph is used.
        maximum_frequency: str, optional
            Maximum frequency to set for the frequency response.
            If the maximum frequency is not given, the existing maximum frequency of the graph is used.
        vsg_analysis_enabled: bool, optional
            The default is ``False``.

        Returns
        -------
        tuple
            The tuple contains two lists of strings. The first is a list
            of the defined frequency ranges, and the second is a
            list of the requested parameters.
        """
        if maximum_frequency is not None:
            self.graph_setup.maximum_frequency = maximum_frequency
        if minimum_frequency is not None:
            self.graph_setup.minimum_frequency = minimum_frequency
        self.vsg_analysis_enabled = vsg_analysis_enabled
        frequency = self._frequency_response_getter(FrequencyResponseColumn.FREQUENCY)
        frequency_hz = []
        for freq in frequency:
            frequency_hz.append(freq / (2 * math.pi))
        parameter = self._frequency_response_getter(y_axis_parameter)
        return frequency_hz, parameter

    def time_response(
        self,
        y_axis_parameter=TimeResponseColumn.STEP_RESPONSE,
        minimum_time=None,
        maximum_time=None,
        vsg_analysis_enabled=False,
    ):
        """Get the ideal filter time response for the given parameters.

        Parameters
        ----------
        y_axis_parameter: `TimeResponseColumn`, optional
            Time response column to get. The default is the step time response.
        minimum_time: str, optional
            Minimum time to set for the time response.
            If the minimum time is not given, the existing minimum time of the graph is used.
        maximum_time: str, optional
            Maximum time to set for the time response.
            If the maximum time is not given, the existing maximum time of the graph is used.
        vsg_analysis_enabled: bool, optional
            The default is ``False``.

        Returns
        -------
        tuple
            The tuple contains two lists of strings. The first is a list
            of the defined time ranges, and the second is a
            list of the requested parameters.
        """
        if maximum_time is not None:
            self.graph_setup.maximum_time = maximum_time
        if minimum_time is not None:
            self.graph_setup.minimum_time = minimum_time
        self.vsg_analysis_enabled = vsg_analysis_enabled
        time = self._time_response_getter(TimeResponseColumn.TIME)
        parameter = self._time_response_getter(y_axis_parameter)
        return time, parameter

    def s_parameters(
        self,
        y_axis_parameter=SParametersResponseColumn.S21_DB,
        minimum_frequency=None,
        maximum_frequency=None,
    ):
        """Get the ideal filter S parameters response for the given parameters.

        Parameters
        ----------
        y_axis_parameter: `SParametersResponseColumn`, optional
            S parameter's response column to get. The default is the S21 parameter response in dB.
        minimum_frequency: str, optional
            Minimum frequency to set for the S parameters response.
            If the minimum frequency is not given, the existing minimum frequency of the graph is used.
        maximum_frequency: str, optional
            Maximum frequency to set for the S parameters response.
            If the maximum frequency is not given, the existing maximum frequency of the graph is used.
        vsg_analysis_enabled: bool, optional
            The default is ``False``.

        Returns
        -------
        tuple
            The tuple contains two lists of strings. The first is a list
            of the defined frequency ranges, and the second is a
            list of the requested parameters.
        """
        if maximum_frequency is not None:
            self.graph_setup.maximum_frequency = maximum_frequency
        if minimum_frequency is not None:
            self.graph_setup.minimum_frequency = minimum_frequency
        frequency = self._sparamaters_response_getter(SParametersResponseColumn.FREQUENCY)
        frequency_hz = []
        for freq in frequency:
            frequency_hz.append(freq / (2 * math.pi))
        parameter = self._sparamaters_response_getter(y_axis_parameter)
        return frequency_hz, parameter

    def pole_zero_locations(
        self,
        x_axis_parameter=PoleZerosResponseColumn.TX_ZERO_DEN_X,
        y_axis_parameter=PoleZerosResponseColumn.TX_ZERO_DEN_Y,
    ):
        """Get the ideal pole zero location for the given parameters.

        Parameters
        ----------
        x_axis_parameter: `PoleZerosResponseColumn`, optional
            X axis parameter of the pole zeros response column to get. The default is the x coordinate
            of the filter transmission zero denominator.
        y_axis_parameter: `PoleZerosResponseColumn`, optional
            Y axis parameter of the pole zeros response column to get. The default is the y coordinate
            of the filter transmission zero denominator.

        Returns
        -------
        tuple
            The tuple contains two lists of strings. The first is a list
            of the x coordinates of the requested parameter, and the second is a
            list of the y coordinates of the requested parameter.
        """
        x_parameter = self._pole_zeros_response_getter(x_axis_parameter)
        y_parameter = self._pole_zeros_response_getter(y_axis_parameter)
        return x_parameter, y_parameter
