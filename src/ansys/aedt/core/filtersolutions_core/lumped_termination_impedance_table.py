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
from ctypes import c_int
from ctypes import create_string_buffer
from enum import Enum

import ansys.aedt.core


class ComplexTerminationDefinition(Enum):
    """Selects type of complex presentation.

    **Attributes:**

    - POLAR: Represents polar definition.
    - CARTESIAN: Represents Cartesian definition.
    - PARALLEL: Represents parallel definition with real entry parallel to imaginary entry.
    - REAL: Represents only real impedance definition.
    """

    POLAR = 0
    CARTESIAN = 1
    PARALLEL = 2
    REAL = 3


class ComplexReactanceType(Enum):
    """Selects type of complex impedance as reactance, equivalent inductance, or equivalent capacitance.

    **Attributes:**

    - REAC: Represents pure reactance of complex impedance.
    - IND: Represents equivalent inductance in henries.
    - CAP: Represents equivalent capacitance in farads.
    """

    REAC = 0
    IND = 1
    CAP = 2


class TerminationType(Enum):
    """Selects either source or load complex impedance table.

    **Attributes:**

    - SOURCE: Represents source impedenace table.
    - LOAD: Represents load impedenace table.
    """

    SOURCE = 0
    LOAD = 1


class LumpedTerminationImpedance:
    """Manipulates access to the entries of source and load complex impedance table.

    This class allows you to enter, edit, or remove the entries of source and load complex impedance table.
    """

    def __init__(self, table_type):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_termination_impedance_dll_functions()
        self.table_type = table_type

    def _define_termination_impedance_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.getComplexTableRowCount.argtypes = [POINTER(c_int), c_bool]
        self._dll.getComplexTableRowCount.restype = c_int

        self._dll.getComplexTableRow.argtypes = [
            c_int,
            c_char_p,
            c_char_p,
            c_char_p,
            c_bool,
            c_int,
        ]
        self._dll.getComplexTableRow.restype = c_int

        self._dll.updateComplexTableRow.argtypes = [
            c_int,
            c_char_p,
            c_char_p,
            c_char_p,
            c_bool,
        ]
        self._dll.updateComplexTableRow.restype = c_int

        self._dll.appendComplexTableRow.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_bool,
        ]
        self._dll.appendComplexTableRow.restype = c_int

        self._dll.insertComplexTableRow.argtypes = [
            c_int,
            c_char_p,
            c_char_p,
            c_char_p,
            c_bool,
        ]
        self._dll.insertComplexTableRow.restype = c_int

        self._dll.removeComplexTableRow.argtypes = [c_int, c_bool]
        self._dll.removeComplexTableRow.restype = c_int

        self._dll.setLumpedComplexDefinition.argtypes = [c_char_p, c_bool]
        self._dll.setLumpedComplexDefinition.restype = c_int
        self._dll.getLumpedComplexDefinition.argtypes = [c_char_p, c_bool, c_int]
        self._dll.getLumpedComplexDefinition.restype = c_int

        self._dll.setLumpedComplexReactanceType.argtypes = [c_char_p, c_bool]
        self._dll.setLumpedComplexReactanceType.restype = c_int
        self._dll.getLumpedComplexReactanceType.argtypes = [c_char_p, c_bool, c_int]
        self._dll.getLumpedComplexReactanceType.restype = c_int

        self._dll.setLumpedComplexElementTuneEnabled.argtype = c_bool
        self._dll.setLumpedComplexElementTuneEnabled.restype = c_int
        self._dll.getLumpedComplexElementTuneEnabled.argtype = POINTER(c_bool)
        self._dll.getLumpedComplexElementTuneEnabled.restype = c_int

        self._dll.setLumpedComplexImpCompensateEnabled.argtypes = [c_bool, c_bool]
        self._dll.setLumpedComplexImpCompensateEnabled.restype = c_int
        self._dll.getLumpedComplexImpCompensateEnabled.argtypes = [
            POINTER(c_bool),
            c_bool,
        ]
        self._dll.getLumpedComplexImpCompensateEnabled.restype = c_int

        self._dll.setLumpedComplexCompOrder.argtypes = [c_int, c_bool]
        self._dll.setLumpedComplexCompOrder.restype = c_int
        self._dll.getLumpedComplexCompOrder.argtypes = [POINTER(c_int), c_bool]
        self._dll.getLumpedComplexCompOrder.restype = c_int

    def _bytes_or_none(self, str_value):
        if str_value:
            return bytes(str_value, "ascii")
        return None

    def table_type_to_bool(self):
        """Set a flag to recognize source and load complex table.

        Returns
        -------
        bool
        """
        if self.table_type.value == TerminationType.SOURCE.value:
            return False
        elif self.table_type.value == TerminationType.LOAD.value:
            return True

    @property
    def row_count(self) -> int:
        """Count of the accumulated complex impedances in the complex impedances's table.

        The default is ``3``.

        Returns
        -------
        int
        """
        table_row_count = c_int()
        status = self._dll.getComplexTableRowCount(byref(table_row_count), self.table_type_to_bool())
        self._dll_interface.raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index):
        """Get frequency and complex impedance values from a row in the complex impedance table.

        Parameters
        ----------
        row_index: int
            Row index on complex impedance table, starting at ``0`` and with a maximum value of ``149``.

        Returns
        -------
        tuple
            The tuple contains three strings. The first is the frequency value,
            the second is the real part of the complex impedance,
            and the third is the imaginary part of the complex impedance.
        """
        frequency_value_buffer = create_string_buffer(100)
        real_value_buffer = create_string_buffer(100)
        imag_value_buffer = create_string_buffer(100)
        status = self._dll.getComplexTableRow(
            row_index,
            frequency_value_buffer,
            real_value_buffer,
            imag_value_buffer,
            self.table_type_to_bool(),
            100,
        )
        self._dll_interface.raise_error(status)
        frequency_value_string = frequency_value_buffer.value.decode("utf-8")
        real_value_string = real_value_buffer.value.decode("utf-8")
        imag_value_string = imag_value_buffer.value.decode("utf-8")
        return frequency_value_string, real_value_string, imag_value_string

    def update_row(self, row_index, frequency=None, real=None, imag=None):
        """Update frequency and complex impedance at a specified index in the complex impedance table.

        Parameters
        ----------
        row_index: int
            Row index on complex impedance table, starting at ``0`` and with a maximum value of ``149``.
        frequency: str, optional
            The frequency value to update. If not specified, it remains unchanged.
        real: str, optional
            The real part of the complex impedance to update. If not specified, it remains unchanged.
        imag: str, optional
            The imaginary part of the complex impedance to update. If not specified, it remains unchanged.
        """
        status = self._dll.updateComplexTableRow(
            row_index,
            self._bytes_or_none(frequency),
            self._bytes_or_none(real),
            self._bytes_or_none(imag),
            self.table_type_to_bool(),
        )
        self._dll_interface.raise_error(status)

    def append_row(self, frequency=None, real=None, imag=None):
        """Append frequency and complex impedance values to the last row of
        both the source and load complex impedance table.


        Parameters
        ----------
        frequency: str
            The frequency value to append.
        real: str
            The real part of the complex impedance to append.
        imag: str
            The imaginary part of the complex impedance to append.
        """
        status = self._dll.appendComplexTableRow(
            self._bytes_or_none(frequency),
            self._bytes_or_none(real),
            self._bytes_or_none(imag),
            self.table_type_to_bool(),
        )
        self._dll_interface.raise_error(status)

    def insert_row(self, row_index, frequency=None, real=None, imag=None):
        """Insert frequency and complex impedance values at a specified index in the complex impedance table.

        Parameters
        ----------
        row_index : int
            Row index in the complex impedance table, starting at ``0`` and with a maximum value of ``149``.
        frequency : str
            The frequency value to insert.
        real : str
            The real part of the complex impedance to insert.
        imag : str
            The imaginary part of the complex impedance to insert.
        """
        status = self._dll.insertComplexTableRow(
            row_index,
            self._bytes_or_none(frequency),
            self._bytes_or_none(real),
            self._bytes_or_none(imag),
            self.table_type_to_bool(),
        )
        self._dll_interface.raise_error(status)

    def remove_row(self, row_index):
        """Remove frequency and complex impedance at a specified index from the complex impedance table.

        Parameters
        ----------
        row_index : int
            Row index in the complex impedance table, starting at ``0`` and with a maximum value of ``149``.
        """
        status = self._dll.removeComplexTableRow(row_index, self.table_type_to_bool())
        self._dll_interface.raise_error(status)

    @property
    def complex_definition(self) -> ComplexTerminationDefinition:
        """Definition type of complex impedance in the complex impedance table.
        The default is ``Cartesian``.

        Returns
        -------
        :enum:`ComplexTerminationDefinition`
        """
        type_string_buffer = create_string_buffer(100)
        status = self._dll.getLumpedComplexDefinition(
            type_string_buffer,
            self.table_type_to_bool(),
            100,
        )
        self._dll_interface.raise_error(status)
        type_string = type_string_buffer.value.decode("utf-8")
        return self._dll_interface.string_to_enum(ComplexTerminationDefinition, type_string)

    @complex_definition.setter
    def complex_definition(self, complex_definition: ComplexTerminationDefinition):
        string_value = self._dll_interface.enum_to_string(complex_definition)
        string_bytes_value = bytes(string_value, "ascii")
        status = self._dll.setLumpedComplexDefinition(string_bytes_value, self.table_type_to_bool())
        self._dll_interface.raise_error(status)

    @property
    def reactance_type(self) -> ComplexReactanceType:
        """Reactance type of complex impedance in the complex impedance table.

        The default is ``reactance``.

        Returns
        -------
        :enum:`ComplexReactanceType`
        """
        type_string_buffer = create_string_buffer(100)
        status = self._dll.getLumpedComplexReactanceType(
            type_string_buffer,
            self.table_type_to_bool(),
            100,
        )
        self._dll_interface.raise_error(status)
        type_string = type_string_buffer.value.decode("utf-8")
        return self._dll_interface.string_to_enum(ComplexReactanceType, type_string)

    @reactance_type.setter
    def reactance_type(self, reactance_type: ComplexReactanceType):
        string_value = self._dll_interface.enum_to_string(reactance_type)
        string_bytes_value = bytes(string_value, "ascii")
        status = self._dll.setLumpedComplexReactanceType(string_bytes_value, self.table_type_to_bool())
        self._dll_interface.raise_error(status)

    @property
    def element_tune_enabled(self) -> bool:
        """Flag indicating if the element tune is enabled.

        Returns
        -------
        bool
        """
        element_tune_enabled = c_bool()
        status = self._dll.getLumpedComplexElementTuneEnabled(byref(element_tune_enabled))
        self._dll_interface.raise_error(status)
        return bool(element_tune_enabled.value)

    @element_tune_enabled.setter
    def element_tune_enabled(self, element_tune_enabled):
        status = self._dll.setLumpedComplexElementTuneEnabled(element_tune_enabled)
        self._dll_interface.raise_error(status)

    @property
    def compensation_enabled(self) -> bool:
        """Flag indicating if the impedance compensation is enabled.

        Returns
        -------
        bool
        """
        compensation_enabled = c_bool()
        status = self._dll.getLumpedComplexImpCompensateEnabled(byref(compensation_enabled), self.table_type_to_bool())
        self._dll_interface.raise_error(status)
        return bool(compensation_enabled.value)

    @compensation_enabled.setter
    def compensation_enabled(self, compensation_enabled: bool):
        status = self._dll.setLumpedComplexImpCompensateEnabled(compensation_enabled, self.table_type_to_bool())
        self._dll_interface.raise_error(status)

    @property
    def compensation_order(self) -> int:
        """Order of impedance compensation.

        The default is` ``2``.

        Returns
        -------
        int
        """
        compensation_order = c_int()
        status = self._dll.getLumpedComplexCompOrder(byref(compensation_order), self.table_type_to_bool())
        self._dll_interface.raise_error(status)
        return int(compensation_order.value)

    @compensation_order.setter
    def compensation_order(self, compensation_order: int):
        status = self._dll.setLumpedComplexCompOrder(compensation_order, self.table_type_to_bool())
        self._dll_interface.raise_error(status)
