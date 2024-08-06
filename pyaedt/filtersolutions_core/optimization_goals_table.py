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

import csv
from ctypes import POINTER
from ctypes import byref
from ctypes import c_char_p
from ctypes import c_int
from ctypes import create_string_buffer
from enum import Enum

import pyaedt


class OptimizationGoalParameter(Enum):
    """Enumeration of optimization goals parameters table.

    **Attributes:**

    - RATIO: Represents transmission zeros ratio table.
    - BANDWIDTH: Represents transmission zeros bandwidth table.
    - LOWER_FREQUENCY = Represents lower frequency parameters.
    - UPPER_FREQUENCY = Represents upper frequency parameters.
    - GOAL_VALUE = Represents goal value parameters.
    - CONDITION = Represents condition parameters.
    - PARAMETER_NAME = Represents name of parameters.
    - WEIGHT = Represents weight parameters.
     -ENABLED = Represents status of using the goal parameters.
    """

    LOWER_FREQUENCY = 0
    UPPER_FREQUENCY = 1
    GOAL_VALUE = 2
    CONDITION = 3
    PARAMETER_NAME = 4
    WEIGHT = 5
    ENABLED = 6


class OptimizationGoalsTable:
    """Manipulates access to the entries of optimization goals table.

    This class lets you to enter, edit or remove goal parameters in the optimization goals table.
    The table includes the lower frequency, upper frequency, goal desired value, goal condition,
    parameter name, weight, and enabled status.
    """

    def __init__(self):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
        self._define_multiple_bands_dll_functions()

    def _define_multiple_bands_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.getOptimizationGoalDefinitionRowCount.argtype = POINTER(c_int)
        self._dll.getOptimizationGoalDefinitionRowCount.restype = c_int

        self._dll.getOptimizationGoalDefinitionRow.argtype = [c_int, POINTER(c_char_p), c_int]
        self._dll.getOptimizationGoalDefinitionRow.restype = c_int

        self._dll.updateOptimizationGoalDefinitionRow.argtype = [c_int, c_int, c_char_p]
        self._dll.updateOptimizationGoalDefinitionRow.restype = c_int

        self._dll.appendOptimizationGoalDefinitionRow.argtype = [c_int, c_char_p]
        self._dll.appendOptimizationGoalDefinitionRow.restype = c_int

        self._dll.insertOptimizationGoalDefinitionRow.argtypes = [c_int, c_char_p, c_char_p]
        self._dll.insertOptimizationGoalDefinitionRow.restype = c_int

        self._dll.removeOptimizationGoalDefinitionRow.argtype = c_int
        self._dll.removeOptimizationGoalDefinitionRow.restype = c_int

        self._dll.adjustGoalFrequency.argtype = c_char_p
        self._dll.adjustGoalFrequency.restype = c_int

    @property
    def row_count(self) -> int:
        """Number of golas in the optimization goals table.
        The default is `0`.

        Returns
        -------
        int
        """
        table_row_count = c_int()
        status = self._dll.getOptimizationGoalDefinitionRowCount(byref(table_row_count))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return int(table_row_count.value)

    def row(self, row_index) -> list:
        """Get the row parameters of the optimization goals table as a list.

        Parameters
        ----------
        row_index: int
            Index of the row. Valid values range from ``0`` to ``49``, inclusive.

        Returns
        -------
        list
            A list of strings representing the row parameters.
        """
        row_parameter_buffer = create_string_buffer(1024)
        # Call the DLL function. Assuming it fills the buffer with comma-separated values.
        status = self._dll.getOptimizationGoalDefinitionRow(row_index, byref(row_parameter_buffer), 1024)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        # Decode the buffer to a Python string and split by comma to get a list.
        row_parameters = row_parameter_buffer.value.decode("utf-8").split("|")
        return row_parameters

    def update_row(
        self,
        row_index,
        lower_frequency=None,
        upper_frequency=None,
        goal_value=None,
        condition=None,
        parameter_name=None,
        weight=None,
        enabled=None,
    ):
        """Update the row parameters for a row in the optimization goals table.

        Parameters
        ----------
        row_index: int
            Index of the row. Valid values range from ``0`` to ``49``, inclusive.
        lower_frequency: str, optional
            New lower frequency value to set.
            If no value is specified, the value remains unchanged.
        upper_frequency: str, optional
            New upper frequency value to set.
            If no value is specified, the value remains unchanged.
        goal_value: str, optional
            New goal value to set.
            If no value is specified, the value remains unchanged.
        condition: str, optional
            New condition value to set.
            If no value is specified, the value remains unchanged.
        parameter_name: str, optional
            New parameter name value to set.
            If no value is specified, the value remains unchanged.
        weight: str, optional
            New weight value to set.
            If no value is specified, the value remains unchanged.
        enabled: str, optional
            New enabled value to set.
            If no value is specified, the value remains unchanged.
        """
        if lower_frequency:
            lower_frequency_bytes_value = bytes(lower_frequency, "ascii")
        else:
            lower_frequency_bytes_value = None
        if upper_frequency:
            upper_frequency_bytes_value = bytes(upper_frequency, "ascii")
        else:
            upper_frequency_bytes_value = None
        if goal_value:
            goal_value_bytes_value = bytes(goal_value, "ascii")
        else:
            goal_value_bytes_value = None
        if condition:
            condition_bytes_value = bytes(condition, "ascii")
        else:
            condition_bytes_value = None
        if parameter_name:
            parameter_name_bytes_value = bytes(parameter_name, "ascii")
        else:
            parameter_name_bytes_value = None
        if weight:
            weight_bytes_value = bytes(weight, "ascii")
        else:
            weight_bytes_value = None

        if enabled:
            enabled_bytes_value = bytes(enabled, "ascii")
        else:
            enabled_bytes_value = None
        status = self._dll.updateOptimizationGoalDefinitionRow(
            row_index,
            lower_frequency_bytes_value,
            upper_frequency_bytes_value,
            goal_value_bytes_value,
            condition_bytes_value,
            parameter_name_bytes_value,
            weight_bytes_value,
            enabled_bytes_value,
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def append_row(
        self,
        lower_frequency=None,
        upper_frequency=None,
        goal_value=None,
        condition=None,
        parameter_name=None,
        weight=None,
        enabled=None,
    ):
        """Append a new row of parameters into the optimization goals table.

        Parameters
        ----------
        lower_frequency: str, optional
            Lower frequency value to set.
        upper_frequency: str, optional
            Upper frequency value to set.
        goal_value: str, optional
            Goal value to set.
        condition: str, optional
            Condition value to set.
        parameter_name: str, optional
            Parameter name value to set.
        weight: str, optional
            Weight value to set.
        enabled: str, optional
            Enabled value to set.
        """
        if lower_frequency:
            lower_frequency_bytes_value = bytes(lower_frequency, "ascii")
        else:
            lower_frequency_bytes_value = bytes("", "ascii")
        if upper_frequency:
            upper_frequency_bytes_value = bytes(upper_frequency, "ascii")
        else:
            upper_frequency_bytes_value = bytes("", "ascii")
        if goal_value:
            goal_value_bytes_value = bytes(goal_value, "ascii")
        else:
            goal_value_bytes_value = bytes("", "ascii")
        if condition:
            condition_bytes_value = bytes(condition, "ascii")
        else:
            condition_bytes_value = bytes("", "ascii")
        if parameter_name:
            parameter_name_bytes_value = bytes(parameter_name, "ascii")
        else:
            parameter_name_bytes_value = bytes("", "ascii")
        if weight:
            weight_bytes_value = bytes(weight, "ascii")
        else:
            weight_bytes_value = bytes("", "ascii")
        if enabled:
            enabled_bytes_value = bytes(enabled, "ascii")
        else:
            enabled_bytes_value = bytes("", "ascii")
        status = self._dll.appendOptimizationGoalDefinitionRow(
            lower_frequency_bytes_value,
            upper_frequency_bytes_value,
            goal_value_bytes_value,
            condition_bytes_value,
            parameter_name_bytes_value,
            weight_bytes_value,
            enabled_bytes_value,
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def insert_row(
        self,
        row_index,
        lower_frequency=None,
        upper_frequency=None,
        goal_value=None,
        condition=None,
        parameter_name=None,
        weight=None,
        enabled=None,
    ):
        """Insert a new row of parameters into the optimization goals table.

        Parameters
        ----------
        row_index: int
            Index of the row. Valid values range from ``0`` to ``49``, inclusive.
        lower_frequency: str, optional
            Lower frequency value.
        upper_frequency: str, optional
            Upper frequency value.
        goal_value: str, optional
            Goal value.
        condition: str, optional
            Condition value.
        parameter_name: str, optional
            Parameter name.
        weight: str, optional
            Weight value.
        enabled: str, optional
            Enabled value.
        """
        if lower_frequency:
            lower_frequency_bytes_value = bytes(lower_frequency, "ascii")
        else:
            lower_frequency_bytes_value = None
        if upper_frequency:
            upper_frequency_bytes_value = bytes(upper_frequency, "ascii")
        else:
            upper_frequency_bytes_value = None
        if goal_value:
            goal_value_bytes_value = bytes(goal_value, "ascii")
        else:
            goal_value_bytes_value = None
        if condition:
            condition_bytes_value = bytes(condition, "ascii")
        else:
            condition_bytes_value = None
        if parameter_name:
            parameter_name_bytes_value = bytes(parameter_name, "ascii")
        else:
            parameter_name_bytes_value = None
        if weight:
            weight_bytes_value = bytes(weight, "ascii")
        else:
            weight_bytes_value = None

        if enabled:
            enabled_bytes_value = bytes(enabled, "ascii")
        else:
            enabled_bytes_value = None
        status = self._dll.insertOptimizationGoalDefinitionRow(
            row_index,
            lower_frequency_bytes_value,
            upper_frequency_bytes_value,
            goal_value_bytes_value,
            condition_bytes_value,
            parameter_name_bytes_value,
            weight_bytes_value,
            enabled_bytes_value,
        )
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def remove_row(self, row_index):
        """Remove a row from the optimization goals table.

        Parameters
        ----------
        row_index: int
            Index of the row. Valid values range from ``0`` to ``49``, inclusive.
        """
        status = self._dll.removeOptimizationGoalDefinitionRow(row_index)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def set_design_goals(self):
        """Set the updated design goals definition."""
        status = self._dll.designGoals()
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    def save_goals(self, design, file_path) -> str:
        """Save the optimization goals from a design's optimization goals table to a CSV file.

        Parameters:
        ----------
        design: The design object containing the optimization goals table.
        file_path: The path to the CSV file where the goals will be saved.
        """
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Start Frequency", "Stop Frequency", "Goal Value", "Condition", "Parameter", "Weight", "Enabled"]
            )
            for row_index in range(design.optimization_goals_table.row_count):
                row_data = design.optimization_goals_table.row(row_index)
                writer.writerow(row_data)

    def load_goals(self, file_path) -> str:
        """Load optimization goals from a CSV file into this optimization goals table.

        Parameters:
        ----------
        file_path: The path to the CSV file from which the goals will be loaded.
        """
        try:
            with open(file_path, mode="r", newline="") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    self.append_row(*row)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"An error occurred while loading goals: {e}")

    def adjust_goal_frequency(self, adjust_goal_frequency_string):
        """Adjust the goal frequencies by an entered adjusting frequency value."""
        self._dll_interface.set_string(self._dll.adjustGoalFrequency, adjust_goal_frequency_string)

    def clear_goal_entries(self):
        """Clear the goal entries from optimization goals table."""
        status = self._dll.clearGoalEntries()
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
