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

from ..EmitNode import *


class TxBbEmissionNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name, "Csv")

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def table_data(self):
        """Tx Broadband Noise Profile Table"
        "Table consists of 2 columns."
        "Frequency (MHz):
        "    Value should be a mathematical expression."
        "Amplitude (dBm/Hz):
        "    Value should be between -200 and 150."
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, "enabled")

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, ["enabled=" + value])

    class NoiseBehaviorOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVEBANDWIDTH = "Relative (Bandwidth)"
        RELATIVEOFFSET = "Relative (Offset)"
        BROADBANDEQUATION = "Equation"

    @property
    def noise_behavior(self) -> NoiseBehaviorOption:
        """Noise Behavior
        "Specifies the behavior of the parametric noise profile."
        " """
        val = self._get_property("Noise Behavior")
        val = self.NoiseBehaviorOption[val]
        return val

    @noise_behavior.setter
    def noise_behavior(self, value: NoiseBehaviorOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, ["Noise Behavior=" + value.value])

    @property
    def use_log_linear_interpolation(self) -> bool:
        """Use Log-Linear Interpolation
        "If true, linear interpolation in the log domain is used. If false, linear interpolation in the linear domain is used.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Use Log-Linear Interpolation")
        return val

    @use_log_linear_interpolation.setter
    def use_log_linear_interpolation(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, ["Use Log-Linear Interpolation=" + value]
        )
