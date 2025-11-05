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


class TxBbEmissionNode(EmitNode):
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
        """Tx Broadband Noise Profile Table.
        Table consists of 2 columns.
        Frequency, Bandwidth, or Offset:
            Value should be between -100e9 and 100e9.
        Amplitude:
            Value should be between -1000 and 200.
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

    class NoiseBehaviorOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVE_BANDWIDTH = "Relative (Bandwidth)"
        RELATIVE_OFFSET = "Relative (Offset)"
        EQUATION = "Equation"

    @property
    def noise_behavior(self) -> NoiseBehaviorOption:
        """Specifies the behavior of the parametric noise profile."""
        val = self._get_property("Noise Behavior")
        val = self.NoiseBehaviorOption[val.upper()]
        return val

    @noise_behavior.setter
    def noise_behavior(self, value: NoiseBehaviorOption):
        self._set_property("Noise Behavior", f"{value.value}")

    @property
    def use_log_linear_interpolation(self) -> bool:
        """Use Log-Linear Interpolation.

        If true, linear interpolation in the log domain is used. If false,
        linear interpolation in the linear domain is used.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Log-Linear Interpolation")
        return val == "true"

    @use_log_linear_interpolation.setter
    def use_log_linear_interpolation(self, value: bool):
        self._set_property("Use Log-Linear Interpolation", f"{str(value).lower()}")
