from ctypes import POINTER
from ctypes import byref
from ctypes import c_char_p
from ctypes import c_int
from ctypes import create_string_buffer

import pyaedt


class MultipleBandsTable:
    """Manipulates access to the entries of multiple bands table.

    This class allows you to enter, edit or remove the entries of multiple bands table.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        Instance of the ``DllInterface`` class

    Methods
    ----------
    _define_multiple_bands_dll_functions:
        Define argument types of DLL functions.
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
        """The count of accumulated frequenices in the multiple bands table.
        The default is ``2``.

        Returns
        -------
        int
        """
        table_row_count = c_int()
        status = self._dll.getMultipleBandsTableRowCount(byref(table_row_count))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index):
        """Export lower and upper frequencies at given index.

        Parameters
        ----------
        row_index: int
            The row index on multiple bands table. Starting value is 0 and maximum value is 6.

        Returns
        -------
        tuple: The tuple contains
                str:
                    Lower frequency value.
                str:
                    Upper frequency value.
        """
        lower_value_buffer = create_string_buffer(100)
        upper_value_buffer = create_string_buffer(100)
        status = self._dll.getMultipleBandsTableRow(row_index, lower_value_buffer, upper_value_buffer, 100)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        lower_value_string = lower_value_buffer.value.decode("utf-8")
        upper_value_string = upper_value_buffer.value.decode("utf-8")
        return lower_value_string, upper_value_string

    def update_row(self, row_index, lower_frequency="", upper_frequency=""):
        """Update lower and upper frequencies at given index.

        Parameters
        ----------
        row_index: int
            The row index on multiple bands table. Starting value is 0 and maximum value is 6.
        lower_frequency: str, optional
            The default is blank.
        upper_frequency: str, optional
            The default is blank.
        """
        lower_bytes_value = bytes(lower_frequency, "ascii")
        upper_bytes_value = bytes(upper_frequency, "ascii")
        status = self._dll.updateMultipleBandsTableRow(row_index, lower_bytes_value, upper_bytes_value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def append_row(self, lower_frequency, upper_frequency):
        """Append lower and upper frequencies at the end row of multiple bands table.

        Parameters
        ----------
        lower_frequency: str
        upper_frequency: str
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
            The row index on multiple bands table. Starting value is ``0`` and maximum value is ``6``.
        lower_frequency: str
        upper_frequency: str
        """
        lower_bytes_value = bytes(lower_frequency, "ascii")
        upper_bytes_value = bytes(upper_frequency, "ascii")
        status = self._dll.insertMultipleBandsTableRow(row_index, lower_bytes_value, upper_bytes_value)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def remove_row(self, row_index):
        """Remove lower and upper frequencies at given index.

        Parameters
        ----------
        row_index: int
            The row index on multiple bands table. Starting value is ``0`` and maximum value is ``6``.
        """
        status = self._dll.removeMultipleBandsTableRow(row_index)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
