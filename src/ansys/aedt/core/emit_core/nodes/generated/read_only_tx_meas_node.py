# -*- coding: utf-8 -*-
#
# Copyright(C) 2021 - 2025 ANSYS, Inc. and /or its affiliates.
# SPDX - License - Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode

class ReadOnlyTxMeasNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def file(self) -> str:
        """Name of the measurement source.

        Value should be a full file path.
        """
        val = self._get_property("File")
        return val

    @property
    def source_file(self) -> str:
        """Name of the measurement source.

        Value should be a full file path.
        """
        val = self._get_property("Source File")
        return val

    @property
    def transmit_frequency(self) -> float:
        """Channel associated with the measurement file."""
        val = self._get_property("Transmit Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def use_ams_limits(self) -> bool:
        """Allow AMS to define the frequency limits for the measurements.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use AMS Limits")
        return (val == 'true')

    @property
    def start_frequency(self) -> float:
        """Starting frequency for the measurement sweep.

        Value should be greater than 1e6.
        """
        val = self._get_property("Start Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def stop_frequency(self) -> float:
        """Stopping frequency for the measurement sweep.

        Value should be less than 6e9.
        """
        val = self._get_property("Stop Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def exclude_harmonics_below_noise(self) -> bool:
        """Include/Exclude Harmonics below the noise.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Exclude Harmonics Below Noise")
        return (val == 'true')

