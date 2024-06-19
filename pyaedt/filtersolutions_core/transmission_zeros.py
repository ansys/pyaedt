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
from ctypes import c_int
from ctypes import create_string_buffer
from enum import Enum

import pyaedt


class TableFormat(Enum):
    """Enumeration of transmission zeros table.

    Attributes:
    RATIO: Represents transmission zeros ratio table.
    FREQUENCY: Represents transmission zeros frequency table.
    """

    RATIO = 0
    FREQUENCY = 1


class TransmissionZeros:
    """Manipulates access to the entries of ratio and frequency of tranmsission zeros table.

    This class allows you to enter, edit or remove the entries of ratio and frequency of tranmsission zeros table.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        Instance of the ``DllInterface`` class
    table_format: TableFormat
        Whether selects ratio or frequency transmission zeros table.

    Methods
    ----------
    _define_transmission_zeros_dll_functions:
        Define argument types of DLL functions.
    """

    def __init__(self, table_format):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
        self._define_transmission_zeros_dll_functions()
        self.table_format = table_format

    def _define_transmission_zeros_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.getTransmissionZerosTableRowCount.argtypes = [POINTER(c_int), c_bool]
        self._dll.getTransmissionZerosTableRowCount.restype = c_int

        self._dll.getTransmissionZerosTableRow.argtypes = [
            c_int,
            c_char_p,
            c_char_p,
            c_bool,
            c_int,
        ]
        self._dll.getTransmissionZerosTableRow.restype = c_int

        self._dll.updateTransmissionZerosTableRow.argtypes = [
            c_int,
            c_char_p,
            c_char_p,
            c_bool,
        ]
        self._dll.updateTransmissionZerosTableRow.restype = c_int

        self._dll.appendTransmissionZerosTableRow.argtypes = [
            c_char_p,
            c_char_p,
            c_bool,
        ]
        self._dll.appendTransmissionZerosTableRow.restype = c_int

        self._dll.insertTransmissionZerosTableRow.argtypes = [
            c_int,
            c_char_p,
            c_char_p,
            c_bool,
        ]
        self._dll.insertTransmissionZerosTableRow.restype = c_int

        self._dll.removeTransmissionZerosTableRow.argtypes = [c_int, c_bool]
        self._dll.removeTransmissionZerosTableRow.restype = c_int

        self._dll.clearTransmissionZerosTableRow.argtype = c_bool
        self._dll.clearTransmissionZerosTableRow.restype = c_int

        self._dll.defaultPositionEnabled.argtype = c_bool
        self._dll.defaultPositionEnabled.restype = c_int

    def table_format_to_bool(self):
        """Set a flag to recognize ratio or frequency transmission zeros tables.

        Returns
        -------
        bool
        """
        if self.table_format.value == TableFormat.FREQUENCY.value:
            return False
        else:
            return True

    @property
    def row_count(self) -> int:
        """The count of accumulated transmission zeros in the transmission zeros table.
        The default is ``2``.

        Returns
        -------
        int
        """
        table_row_count = c_int()
        status = self._dll.getTransmissionZerosTableRowCount(byref(table_row_count), self.table_format_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index):
        """Export ratios or frequencies at given index of the transmission zeros table.

        Parameters
        ----------
        row_index: int
            The row index on transmission zeros table. Starting value is ``0`` and maximum value is ``9``.

        Returns
        -------
        tuple: The tuple contains
                str:
                    Transmission zero ratio or frequency value.
                str:
                    Position of the element creating transmission zero in the associated circuit.
        """
        zero_value_buffer = create_string_buffer(100)
        position_value_buffer = create_string_buffer(100)
        status = self._dll.getTransmissionZerosTableRow(
            row_index,
            zero_value_buffer,
            position_value_buffer,
            self.table_format_to_bool(),
            100,
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        zero_value_string = zero_value_buffer.value.decode("utf-8")
        position_value_string = position_value_buffer.value.decode("utf-8")
        return zero_value_string, position_value_string

    def update_row(self, row_index, zero="", position=""):
        """Update ratios or frequencies at given index of the transmission zeros table.

        Parameters
        ----------
        row_index: int
            The row index on transmission zeros table. Starting value is ``0`` and maximum value is ``9``.
        zero: str, optional
            Transmission zero ratio or frequency value.
            The default is blank.
        position: str, optional
            Position of the element creating transmission zero in the associated circuit.
            The default is blank.
        """
        zero_bytes_value = bytes(zero, "ascii")
        position_bytes_value = bytes(position, "ascii")
        status = self._dll.updateTransmissionZerosTableRow(
            row_index,
            zero_bytes_value,
            position_bytes_value,
            self.table_format_to_bool(),
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def append_row(self, zero, position=""):
        """Append ratios or frequencies at the end row of transmission zeros table.

        Parameters
        ----------
        zero: str
            Transmission zero ratio or frequency value.
        position: str
            Position of the element creating transmission zero in the associated circuit.
        """
        zero_bytes_value = bytes(zero, "ascii")
        position_bytes_value = bytes(position, "ascii")
        status = self._dll.appendTransmissionZerosTableRow(
            zero_bytes_value, position_bytes_value, self.table_format_to_bool()
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def insert_row(self, row_index, zero, position=""):
        """Insert ratios or frequencies at given index of the transmission zeros table.

        Parameters
        ----------
        row_index: int
            The row index on transmission zeros table. Starting value is ``0`` and maximum value is ``9``.
        zero: str
            Transmission zero ratio or frequency value.
        position: str
            Position of the element creating transmission zero in the associated circuit.
        """
        zero_bytes_value = bytes(zero, "ascii")
        position_bytes_value = bytes(position, "ascii")
        status = self._dll.insertTransmissionZerosTableRow(
            row_index,
            zero_bytes_value,
            position_bytes_value,
            self.table_format_to_bool(),
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def remove_row(self, row_index):
        """Remove ratios or frequencies at given index of the transmission zeros table.

        Parameters
        ----------
        row_index: int
            The row index on transmission zeros table. Starting value is ``0`` and maximum value is ``9``.
        """
        status = self._dll.removeTransmissionZerosTableRow(row_index, self.table_format_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def clear_row(self):
        """Clear all entries of the transmission zeros table."""
        status = self._dll.clearTransmissionZerosTableRow(self.table_format_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def default_position(self):
        """Restore default position of transmissison zeros."""
        status = self._dll.defaultPositionEnabled(self.table_format_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
