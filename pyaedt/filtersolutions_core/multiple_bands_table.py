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
from ctypes import c_char_p
from ctypes import c_int
from ctypes import create_string_buffer

import pyaedt


class MultipleBandsTable:
    """Manipulates access to the entries of multiple bands table.

    This class allows you to enter, edit or remove the entries of multiple bands table.
    The table includes the lower and upper frequencies of the bands.
    To access the multiple bands table, use the ``multiple_bands_table`` attribute of the ``FilterSolutions`` class.
    A valid multiple bands table must include at both lower and upper frequencies for each band.
    """

    def __init__(self):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
        self._define_multiple_bands_dll_functions()

    def _define_multiple_bands_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.getMultipleBandsTableRowCount.argtype = POINTER(c_int)
        self._dll.getMultipleBandsTableRowCount.restype = c_int

        self._dll.getMultipleBandsTableRow.argtypes = [c_int, c_char_p, c_char_p, c_int]
        self._dll.getMultipleBandsTableRow.restype = c_int

        self._dll.updateMultipleBandsTableRow.argtypes = [c_int, c_char_p, c_char_p]
        self._dll.updateMultipleBandsTableRow.restype = c_int

        self._dll.appendMultipleBandsTableRow.argtypes = [c_char_p, c_char_p]
        self._dll.appendMultipleBandsTableRow.restype = c_int

        self._dll.insertMultipleBandsTableRow.argtypes = [c_int, c_char_p, c_char_p]
        self._dll.insertMultipleBandsTableRow.restype = c_int

        self._dll.removeMultipleBandsTableRow.argtype = c_int
        self._dll.removeMultipleBandsTableRow.restype = c_int

    @property
    def row_count(self) -> int:
        """Retrieve the total number of rows present in the multiple bands table.
        The default is ``2``.

        Returns
        -------
        int
            The current number of rows in the multiple bands table.
        """
        table_row_count = c_int()
        status = self._dll.getMultipleBandsTableRowCount(byref(table_row_count))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index):
        """Retrieve the lower and upper frequency values for a specified row in the multiple bands table.

        Parameters
        ----------
        row_index: int
            The index of the row from which to retrieve the frequency values.
            Valid values range from ``0`` to ``6``, inclusive.

        Returns
        -------
            tuple of (str, str)
                A tuple containing the lower and upper frequency values as strings.

        """
        lower_value_buffer = create_string_buffer(100)
        upper_value_buffer = create_string_buffer(100)
        status = self._dll.getMultipleBandsTableRow(row_index, lower_value_buffer, upper_value_buffer, 100)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        lower_value_string = lower_value_buffer.value.decode("utf-8")
        upper_value_string = upper_value_buffer.value.decode("utf-8")
        return lower_value_string, upper_value_string

    def update_row(self, row_index, lower_frequency="", upper_frequency=""):
        """Update lower and upper frequency values for a specified row in the multiple bands table.

        Parameters
        ----------
        row_index: int
            The index of the row to update, with a valid range from ``0`` to ``6`` inclusive.
        lower_frequency: str, optional
            The new lower frequency value to set for the specified row.
            If this value is not provided, the row's lower frequency remains unchanged.
        upper_frequency: str, optional
            The new upper frequency value to set for the specified row.
            If this value is not provided, the row's upper frequency remains unchanged.
        """
        lower_bytes_value = bytes(lower_frequency, "ascii")
        upper_bytes_value = bytes(upper_frequency, "ascii")
        status = self._dll.updateMultipleBandsTableRow(row_index, lower_bytes_value, upper_bytes_value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def append_row(self, lower_frequency, upper_frequency):
        """Appends a new row with specified lower and upper frequency values to the end of the multiple bands table.

        Parameters
        ----------
        lower_frequency: str
            The lower frequency value to append.
        upper_frequency: str
            The upper frequency value to append.
        """
        lower_bytes_value = bytes(lower_frequency, "ascii")
        upper_bytes_value = bytes(upper_frequency, "ascii")
        status = self._dll.appendMultipleBandsTableRow(lower_bytes_value, upper_bytes_value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def insert_row(self, row_index, lower_frequency, upper_frequency):
        """Insert lower and upper frequencies at given index.

        Parameters
        ----------
        row_index: int
            The index of the row to update, with a valid range from ``0`` to ``6`` inclusive.
        lower_frequency: str
            The lower frequency value to insert.
        upper_frequency: str
            The upper frequency value to insert.
        """
        lower_bytes_value = bytes(lower_frequency, "ascii")
        upper_bytes_value = bytes(upper_frequency, "ascii")
        status = self._dll.insertMultipleBandsTableRow(row_index, lower_bytes_value, upper_bytes_value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def remove_row(self, row_index):
        """Remove a row specified by its index from the multiple bands table.

        Parameters
        ----------
        row_index: int
            The index of the row to be removed from the multiple bands table.
            Valid values range from ``0``to ``6``, inclusive.
        """
        status = self._dll.removeMultipleBandsTableRow(row_index)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
