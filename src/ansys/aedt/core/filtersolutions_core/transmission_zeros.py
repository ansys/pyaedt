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


class TableFormat(Enum):
    """Enumeration of transmission zeros table.

    **Attributes:**

    - RATIO: Represents transmission zeros ratio.
    - BANDWIDTH: Represents transmission zeros bandwidth.
    """

    RATIO = 0
    BANDWIDTH = 1


class TransmissionZeros:
    """Manipulates access to ratio and bandwidth entries in the tranmsission zeros table.

    This class lets you to enter, edit, or remove ratio and bandwidth entries
    in the tranmsission zeros table.
    The table includes the ratio or bandwidth and the position of the element creating
    the transmission zero in the associated circuit.
    The position of the transmission zero is the position of the element in
    the associated circuit that creates the transmission zero.
    The position is defined automatically if no value is provided.
    """

    def __init__(self, table_format):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
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
        """Check if the entry format of the transmission zeros tables is ratio.
        If ``False``, the entry format is bandwidth.

        Returns
        -------
        bool
        """
        if self.table_format.value == TableFormat.BANDWIDTH.value:
            return False
        else:
            return True

    def _bytes_or_none(self, str_value):
        if str_value:
            return bytes(str_value, "ascii")
        return None

    @property
    def row_count(self) -> int:
        """Number of transmission zeros in the transmission zeros table.

        The default is ``2``.

        Returns
        -------
        int
        """
        table_row_count = c_int()
        status = self._dll.getTransmissionZerosTableRowCount(byref(table_row_count), self.table_format_to_bool())
        self._dll_interface.raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index):
        """Get the transmission zero ratio or bandwidth and the position of the element
        causing the transmission zero from a row in the transmission zeros table.

        Parameters
        ----------
        row_index: int
            Index of the row. Valid values range from ``0`` to ``9``, inclusive.

        Returns
        -------
        tuple
            The tuple contains two strings.The first is the transmission zero ratio or bandwidth value,
            and the second is the position of the element causing the transmission zero.
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
        self._dll_interface.raise_error(status)
        zero_value_string = zero_value_buffer.value.decode("utf-8")
        position_value_string = position_value_buffer.value.decode("utf-8")
        return zero_value_string, position_value_string

    def update_row(self, row_index, zero=None, position=None):
        """Update the transmission zero ratio or bandwidth and its position for a row in the transmission zeros table.

        Parameters
        ----------
        row_index: int
            Index of the row. Valid values range from ``0`` to ``9``, inclusive.
        zero: str, optional
            New transmission zero ratio or bandwidth value to set.
            If no value is specified, the value remains unchanged.
        position: str, optional
            New position of the element causing the transmission zero in the circuit.
            If no value is specified, the value remains unchanged.
        """
        status = self._dll.updateTransmissionZerosTableRow(
            row_index,
            self._bytes_or_none(zero),
            self._bytes_or_none(position),
            self.table_format_to_bool(),
        )
        self._dll_interface.raise_error(status)

    def append_row(self, zero=None, position=None):
        """Append a new row that includes the ratio or bandwidth and position.

        Parameters
        ----------
        zero: str
            Transmission zero ratio or bandwidth value.
        position: str
            Position of the element creating transmission zero in the associated circuit.
        """
        status = self._dll.appendTransmissionZerosTableRow(
            self._bytes_or_none(zero),
            self._bytes_or_none(position),
            self.table_format_to_bool(),
        )
        self._dll_interface.raise_error(status)

    def insert_row(self, row_index, zero=None, position=None):
        """Insert a new row that includes the ratio or bandwidth and the position.

        Parameters
        ----------
        row_index: int
            Index for the new row in the transmission zeros table. Valid values range from ``0`` to ``9``, inclusive.
        zero: str
            Transmission zero ratio or bandwidth value.
        position: str
            Position of the element creating transmission zero in the associated circuit.
        """
        status = self._dll.insertTransmissionZerosTableRow(
            row_index,
            self._bytes_or_none(zero),
            self._bytes_or_none(position),
            self.table_format_to_bool(),
        )
        self._dll_interface.raise_error(status)

    def remove_row(self, row_index):
        """Remove a row, including the ratio or bandwidth and the position.

        Parameters
        ----------
        row_index: int
            Row index in the transmission zeros table. Valid values range from ``0`` to ``9``, inclusive.
        """
        status = self._dll.removeTransmissionZerosTableRow(row_index, self.table_format_to_bool())
        self._dll_interface.raise_error(status)

    def clear_table(self):
        """Clear all entries in the transmission zeros table."""
        status = self._dll.clearTransmissionZerosTableRow(self.table_format_to_bool())
        self._dll_interface.raise_error(status)

    def restore_default_positions(self):
        """Restore default positions of transmissison zeros."""
        status = self._dll.defaultPositionEnabled(self.table_format_to_bool())
        self._dll_interface.raise_error(status)
