from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int
from ctypes import create_string_buffer
from enum import Enum

import pyaedt


class ComplexTerminationDefinition(Enum):
    """Selects type of complex presentation.
    Attributes:
    POLAR: Represents polar definition.
    CARTESIAN: Represents Cartesian definition.
    PARALLEL: Represents parallel definition with real entry parallel to imaginary entry.
    REAL: Represents only real impedance definition.
    """

    POLAR = 0
    CARTESIAN = 1
    PARALLEL = 2
    REAL = 3


class ComplexReactanceType(Enum):
    """Selects type of complex impedance as reactance, equivalent inductance, or equivalent capacitqnce.

    Attributes:
    REAC: Represents pure reactance of complex impedance.
    IND: Represents equivalent inductance in Henrys.
    CAP: Represents equivalent capacitance in Farads.
    """

    REAC = 0
    IND = 1
    CAP = 2


class TerminationType(Enum):
    """Selects either source or load complex impedance table.

    Attributes:
    SOURCE: Represents source impedenace table.
    LOAD: Represents load impedenace table.
    """

    SOURCE = 0
    LOAD = 1


class LumpedTerminationImpedance:
    """Manipulates access to the entries of source and load complex impedance tables.

    This class allows you to enter, edit or remove the entries of source and load complex impedance tables.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        an instance of DllInterface class
        table_type: TerminationType
            Whether selects source or load complex impedance table.

    Methods
    ----------
    _define_termination_impedance_dll_functions:
        Define argument types of DLL function.
    """

    def __init__(self, table_type):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
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

    def table_type_to_bool(self):
        """Set a flag to recognize source and load complex tables.

        Returns
        -------
        bool
        """
        if self.table_type.value == TerminationType.SOURCE.value:
            return False
        else:
            return True

    @property
    def row_count(self) -> int:
        """The count of accumulated complex impedances in the complex impedances tables.
        The default is `3`.

        Returns
        -------
        int
        """
        table_row_count = c_int()
        status = self._dll.getComplexTableRowCount(byref(table_row_count), self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index):
        """Export frequencies and complex impedances at given index of the complex impedances tables.

        Parameters
        ----------
        row_index: int
            The row index on complex impedances tables. Starting value is 0 and maximum value is 99.

        Returns
        -------
        tuple: The tuple contains
                str:
                    Frequency value.
                str:
                    First term of the complex impedances.
                str:
                    Second term of the complex impedances.
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
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        frequency_value_string = frequency_value_buffer.value.decode("utf-8")
        real_value_string = real_value_buffer.value.decode("utf-8")
        imag_value_string = imag_value_buffer.value.decode("utf-8")
        return frequency_value_string, real_value_string, imag_value_string

    def update_row(self, row_index, frequency="", real="", imag=""):
        """Update frequencies and complex impedances at given index of the complex impedances tables.

        Parameters
        ----------
        row_index: int
            The row index on complex impedances tables. Starting value is 0 and maximum value is 99.
        frequency: str, optional
            The default is blank.
        real: str, optional
            First term of the complex impedances.
            The default is blank.
        imag: str, optional
            Second term of the complex impedances.
            The default is blank.
        """
        frequency_bytes_value = bytes(frequency, "ascii")
        real_bytes_value = bytes(real, "ascii")
        imag_bytes_value = bytes(imag, "ascii")
        status = self._dll.updateComplexTableRow(
            row_index,
            frequency_bytes_value,
            real_bytes_value,
            imag_bytes_value,
            self.table_type_to_bool(),
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def append_row(self, frequency, real, imag):
        """Append frequencies and complex impedances at the end row of the source and load complex tables.

        Parameters
        ----------
        frequency: str
        real: str
            First term of the complex impedances.
        imag: str
            Second term of the complex impedances.
        """
        frequency_bytes_value = bytes(frequency, "ascii")
        real_bytes_value = bytes(real, "ascii")
        imag_bytes_value = bytes(imag, "ascii")
        status = self._dll.appendComplexTableRow(
            frequency_bytes_value,
            real_bytes_value,
            imag_bytes_value,
            self.table_type_to_bool(),
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def insert_row(self, row_index, frequency, real, imag):
        """Insert frequencies and complex impedances at given index of the complex impedances tables.

        Parameters
        ----------
        row_index: int
            The row index on complex impedances tables. Starting value is 0 and maximum value is 99.
        frequency: str
        real: str
            First term of the complex impedances.
        imag: str
            Second term of the complex impedances.
        """
        frequency_bytes_value = bytes(frequency, "ascii")
        real_bytes_value = bytes(real, "ascii")
        imag_bytes_value = bytes(imag, "ascii")
        status = self._dll.insertComplexTableRow(
            row_index,
            frequency_bytes_value,
            real_bytes_value,
            imag_bytes_value,
            self.table_type_to_bool(),
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def remove_row(self, row_index):
        """Remove frequencies and complex impedances at given indexof the complex impedances tables.

        Parameters
        ----------
        row_index: int
            The row index on complex impedances tables. Starting value is 0 and maximum value is 99.
        """
        status = self._dll.removeComplexTableRow(row_index, self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def complex_definition(self) -> ComplexTerminationDefinition:
        """The definition type of complex impedances in the complex impedance tables.
        The default is `Cartesian`.

        Returns
        -------
        :enum: ComplexTerminationDefinition
        """
        type_string_buffer = create_string_buffer(100)
        status = self._dll.getLumpedComplexDefinition(
            type_string_buffer,
            self.table_type_to_bool(),
            100,
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        type_string = type_string_buffer.value.decode("utf-8")
        return self._dll_interface.string_to_enum(ComplexTerminationDefinition, type_string)

    @complex_definition.setter
    def complex_definition(self, complex_definition: ComplexTerminationDefinition):
        string_value = self._dll_interface.enum_to_string(complex_definition)
        string_bytes_value = bytes(string_value, "ascii")
        status = self._dll.setLumpedComplexDefinition(string_bytes_value, self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def reactance_type(self) -> ComplexReactanceType:
        """The reactance type of complex impedances in the complex impedance tables.
        The default is `reactance`.

        Returns
        -------
        :enum: ComplexReactanceType
        """

        type_string_buffer = create_string_buffer(100)
        status = self._dll.getLumpedComplexReactanceType(
            type_string_buffer,
            self.table_type_to_bool(),
            100,
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        type_string = type_string_buffer.value.decode("utf-8")
        return self._dll_interface.string_to_enum(ComplexReactanceType, type_string)

    @reactance_type.setter
    def reactance_type(self, reactance_type: ComplexReactanceType):
        string_value = self._dll_interface.enum_to_string(reactance_type)
        string_bytes_value = bytes(string_value, "ascii")
        status = self._dll.setLumpedComplexReactanceType(string_bytes_value, self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def compensation_enabled(self) -> bool:
        """Whether to enable the impedance compnesation option.
        The default is `False`.

        Returns
        -------
        bool
        """
        compensation_enabled = c_bool()
        status = self._dll.getLumpedComplexImpCompensateEnabled(byref(compensation_enabled), self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return bool(compensation_enabled.value)

    @compensation_enabled.setter
    def compensation_enabled(self, compensation_enabled: bool):
        status = self._dll.setLumpedComplexImpCompensateEnabled(compensation_enabled, self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def compensation_order(self) -> int:
        """The order of impedance compnesation.
        The default is `2`.

        Returns
        -------
        int
        """
        compensation_order = c_int()
        status = self._dll.getLumpedComplexCompOrder(byref(compensation_order), self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return int(compensation_order.value)

    @compensation_order.setter
    def compensation_order(self, compensation_order: int):
        status = self._dll.setLumpedComplexCompOrder(compensation_order, self.table_type_to_bool())
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
