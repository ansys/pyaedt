# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

import pyaedt
from pyaedt.filtersolutions_core.graph_setup import GraphSetup


class FrequencyResponseColumn(Enum):
    """Provides an enum of frequency response parameters.

    Attributes:
    MAGNITUDE_DB: Represents the frequency response magnitude in dB.
    PHASE_DEG: Represents the frequency response phase in degree.
    GROUP_DELAY: Represents the frequency response group delay.
    PHASE_RAD: Represents the frequency response phase in radian.
    MAGNITUDE_ARITH: Represents the frequency response magnitude.
    MAGNITUDE_REAL: Represents the real part of frequency response  magnitude .
    MAGNITUDE_IMAG: Represents the imaginary part of frequency response  magnitude.
    PHASE_DEV_DEG: Represents the frequency response phase deviation in degree.
    PHASE_DEV_RAD: Represents the frequency response phase deviation in radian.
    FREQUENCY: Represents the frequency response frequency parameter.
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

    Attributes:
    STEP_RESPONSE: Represents the step time response.
    RAMP_RESPONSE: Represents the ramp time response.
    IMPULSE_RESPONSE: Represents the impulse time response.
    STEP_RESPONSE_DB: Represents the step time response in dB.
    RAMP_RESPONSE_DB: Represents the ramp time response in dB.
    IMPULSE_RESPONSE_DB: Represents the impulse time response in dB.
    TIME: Represents time response the time parameter.
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

    Attributes:
    S21_DB: Represents the S21 parameter in dB.
    S11_DB: Represents the S11 parameter in dB.
    S21_ARITH: Represents the S21 parameter.
    S11_ARITH: Represents the S11 parameter.
    FREQUENCY: Represents the S parameters frequency parameter.
    """

    S21_DB = 0
    S11_DB = 1
    S21_ARITH = 3
    S11_ARITH = 4
    FREQUENCY = 5


class PoleZerosResponseColumn(Enum):
    """Provides an enum of pole zero x and y coordinates of transmission (TX) or reflection (RX) zeros.

    Attributes:
    TX_ZERO_DEN_X: Represents the x coordinate of filter transmission zero denominator.
    TX_ZERO_DEN_Y: Represents the y coordinate of filter transmission zero denominator.
    PROTO_TX_ZERO_DEN_X: Represents the x coordinate of prototype filter transmission zero denominator.
    PROTO_TX_ZERO_DEN_Y: Represents the y coordinate of prototype filter transmission zero denominator.
    TX_ZERO_NUM_X: Represents the x coordinate of filter transmission zero numerator.
    TX_ZERO_NUM_Y: Represents the y coordinate of filter transmission zero numerator.
    PROTO_TX_ZERO_NUM_X: Represents the x coordinate of prototype filter transmission zero numerator.
    PROTO_TX_ZERO_NUM_Y: Represents the y coordinate of prototype filter transmission zero numerator.
    RX_ZERO_DEN_X: Represents the x coordinate of filter reflection zero denominator.
    RX_ZERO_DEN_Y: Represents the y coordinate of filter reflection zero denominator.
    PROTO_RX_ZERO_DEN_X: Represents the x coordinate of prototype filter reflection zero denominator.
    PROTO_RX_ZERO_DEN_Y: Represents the y coordinate of prototype filter reflection zero denominator.
    RX_ZERO_NUM_X: Represents the x coordinate of filter reflection zero numerator.
    RX_ZERO_NUM_Y: Represents the y coordinate of filter reflection zero numerator.
    PROTO_RX_ZERO_NUM_X: Represents the x coordinate of prototype filter reflection zero numerator.
    PROTO_RX_ZERO_NUM_Y: Represents the y coordinate of prototype filter reflection zero numerator.
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
    """Exports the data for available ideal filter responses.
    Includes ``frequency``, ``time``, ``S parameters``, ``transfer function``, or ``pole zero location`` responses.

    This class allows you to construct all the necessary ideal response attributes for the ``FilterDesign`` class.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        Instance of the ``DllInterface`` class
    graph_setup: GraphSetup
        Instance of the ``GraphSetup`` class

    Methods
    ----------
    _define_response_dll_functions:
        Define argument types of DLL functions.
    """

    def __init__(self):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
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
        """Export the ideal filter frequency response.

        Parameters
        ----------
        column: `FrequencyResponseColumn`
            Parameter to export.

        Returns
        -------
        list
            The requested parameter array.
        """
        size = c_int()
        status = self._dll.getIdealFrequencyResponseSize(byref(size))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealFrequencyResponse(array, size.value, column.value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        values = [float(val) for val in array]
        return values

    def _time_response_getter(self, column: TimeResponseColumn):
        """Export the ideal filter time response.

        Parameters
        ----------
        column: `TimeResponseColumn`
            Parameter to export.

        Returns
        -------
        list
            The requested parameter array.
        """
        size = c_int()
        status = self._dll.getIdealTimeResponseSize(byref(size))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealTimeResponse(array, size.value, column.value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        values = [float(val) for val in array]
        return values

    def _sparamaters_response_getter(self, column: SParametersResponseColumn):
        """Export the ideal filter S parameters response.

        Parameters
        ----------
        column: `SParametersResponseColumn`
            Parameter to export.

        Returns
        -------
        list
            The requested parameter array.
        """
        size = c_int()
        status = self._dll.getIdealSParamatersResponseSize(byref(size))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealSParamatersResponse(array, size.value, column.value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        values = [float(val) for val in array]
        return values

    def _pole_zeros_response_getter(self, column: PoleZerosResponseColumn):
        """Export ideal pole zero location parameters.

        Parameters
        ----------
        column: `PoleZerosResponseColumn`
            Parameter to export.

        Returns
        -------
        list
            The requested parameter array.
        """
        size = c_int()
        status = self._dll.getIdealPoleZerosResponseSize(byref(size), column.value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        array = (c_double * size.value)()
        status = self._dll.getIdealPoleZerosResponse(array, size.value, column.value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        values = [float(val) for val in array]
        return values

    def transfer_function_response(self):
        """Export ideal filter transfer function parameters.

        Returns
        -------
        list
            The requested parameter array.
        """
        size = c_int()
        status = self._dll.getIdealTransferFunctionResponseSize(byref(size))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
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
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return bool(vsg_analysis_enabled.value)

    @vsg_analysis_enabled.setter
    def vsg_analysis_enabled(self, filter_vsg_analysis_enabled: bool):
        status = self._dll.setVSGAnalsyis(filter_vsg_analysis_enabled)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def frequency_response(
        self,
        y_axis_parameter=FrequencyResponseColumn.MAGNITUDE_DB,
        minimum_frequency="200 MHz",
        maximum_frequency="5 GHz",
        vsg_analysis_enabled=False,
    ):
        """Export the ideal filter frequency response for the given parameters.

        Parameters
        ----------
        y_axis_parameter: `FrequencyResponseColumn`, optional
            Parameter to export. The default is frequency response magnitude in dB.
        minimum_frequency: str, optional
            The default is ``200 MHz``.
        maximum_frequency: str, optional
            The default is ``5 GHz``.
        vsg_analysis_enabled: bool, optional
            The default is ``False``.

        Returns
        -------
        tuple: The tuple contains
                list of str:
                    The defined frequency range.
                list of str:
                    The requested parameter.
        """
        self.graph_setup.minimum_frequency = minimum_frequency
        self.graph_setup.maximum_frequency = maximum_frequency
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
        minimum_time="0 s",
        maximum_time="10 ns",
        vsg_analysis_enabled=False,
    ):
        """Export the ideal filter time response for the given parameters.

        Parameters
        ----------
        y_axis_parameter: `TimeResponseColumn`, optional
            Parameter to export. The default is step time response.
        minimum_time: str, optional
            The default is ``0 s``.
        maximum_time: str, optional
            The default is ``10 ns``.
        vsg_analysis_enabled: bool, optional
            The default is ``False``.

        Returns
        -------
        tuple: The tuple contains
                list of str:
                    The defined range range.
                list of str:
                    The requested parameter.
        """
        self.graph_setup.minimum_time = minimum_time
        self.graph_setup.maximum_time = maximum_time
        self.vsg_analysis_enabled = vsg_analysis_enabled
        time = self._time_response_getter(TimeResponseColumn.TIME)
        parameter = self._time_response_getter(y_axis_parameter)
        return time, parameter

    def s_parameters(
        self,
        y_axis_parameter=SParametersResponseColumn.S21_DB,
        minimum_frequency="200 MHz",
        maximum_frequency="5 GHz",
    ):
        """Export the ideal filter S parameters response for the given parameters.

        Parameters
        ----------
        y_axis_parameter: `SParametersResponseColumn`, optional
            Parameter to export. The default is S21 parameter response in dB.
        minimum_frequency: str, optional
            The default is ``200 MHz``.
        maximum_frequency: str, optional
            The default is ``5 GHz``.
        vsg_analysis_enabled: bool, optional
            The default is ``False``.

        Returns
        -------
        tuple: The tuple contains
                list of str:
                    The defined frequency range.
                list of str:
                    The requested parameter.
        """
        self.graph_setup.minimum_frequency = minimum_frequency
        self.graph_setup.maximum_frequency = maximum_frequency
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
        """Export the ideal pole zero location for the given parameters.

        Parameters
        ----------
        x_axis_parameter: `PoleZerosResponseColumn`, optional
            Parameter to export. The default is x coordinate of filter transmission zero denominator.
        y_axis_parameter: `PoleZerosResponseColumn`, optional
            Parameter to export. The default is y coordinate of filter transmission zero denominator.

        Returns
        -------
        tuple: The tuple contains
                list of str:
                    The requested parameter.
                list of str:
                    The requested parameter.
        """
        x_parameter = self._pole_zeros_response_getter(x_axis_parameter)
        y_parameter = self._pole_zeros_response_getter(y_axis_parameter)
        return x_parameter, y_parameter
