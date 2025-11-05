# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2021 - 2025 ANSYS, Inc. and /or its affiliates.
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

from enum import Enum

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


class TxNbEmissionNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name, "Csv")

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def table_data(self):
        """Tx Emissions Profile Table.
        Table consists of 2 columns.
        Bandwidth or Frequency:
            Value should be between 1 and 100e9.
        Attenuation or Power:
            Value should be between -1000 and 1000.
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._get_property("Enabled")

    @enabled.setter
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")

    class NarrowbandBehaviorOption(Enum):
        ABSOLUTE_FREQS_AND_POWER = "Absolute Freqs and Power"
        RELATIVE_FREQS_AND_ATTENUATION = "Relative Freqs and Attenuation"

    @property
    def narrowband_behavior(self) -> NarrowbandBehaviorOption:
        """Specifies the behavior of the parametric narrowband emissions mask."""
        val = self._get_property("Narrowband Behavior")
        val = self.NarrowbandBehaviorOption[val.upper()]
        return val

    @narrowband_behavior.setter
    def narrowband_behavior(self, value: NarrowbandBehaviorOption):
        self._set_property("Narrowband Behavior", f"{value.value}")

    @property
    def measurement_frequency(self) -> float:
        """Measurement frequency for the absolute freq/amp pairs."""
        val = self._get_property("Measurement Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @measurement_frequency.setter
    def measurement_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Measurement Frequency", f"{value}")
