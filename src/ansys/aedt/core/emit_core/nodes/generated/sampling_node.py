# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
from ansys.aedt.core.internal.checks import min_aedt_version


class SamplingNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    @property
    @min_aedt_version("2025.2")
    def table_data(self):
        """Frequency Ranges Table.
        Table consists of 2 columns.
        Min:
            Value should be between 1.0 and 100e9.
        Max:
            Value should be between 1.0 and 100e9.
        """
        return self._get_table_data()

    @table_data.setter
    @min_aedt_version("2025.2")
    def table_data(self, value) -> None:
        self._set_table_data(value)

    class SamplingTypeOption(Enum):
        SAMPLE_ALL_CHANNELS_IN_RANGES = "SampleAllChannels"
        RANDOM_SAMPLING = "RandomSampling"
        UNIFORM_SAMPLING = "UniformSampling"

    @property
    @min_aedt_version("2025.2")
    def sampling_type(self) -> SamplingTypeOption:
        """Sampling to apply to this configuration."""
        val = self._get_property("Sampling Type")
        val = self.SamplingTypeOption[val.upper()]
        return val

    @sampling_type.setter
    @min_aedt_version("2025.2")
    def sampling_type(self, value: SamplingTypeOption) -> None:
        self._set_property("Sampling Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def specify_percentage(self) -> bool:
        """Specify Percentage.

        Specify the number of channels to simulate via a percentage of the total
        available band channels.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Specify Percentage")
        return val == "true"

    @specify_percentage.setter
    @min_aedt_version("2025.2")
    def specify_percentage(self, value: bool) -> None:
        self._set_property("Specify Percentage", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def percentage_of_channels(self) -> float:
        """Percentage of the Band Channels to simulate.

        Value should be between 1 and 100.
        """
        val = self._get_property("Percentage of Channels")
        return float(val)

    @percentage_of_channels.setter
    @min_aedt_version("2025.2")
    def percentage_of_channels(self, value: float) -> None:
        self._set_property("Percentage of Channels", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def max_channels_range_band(self) -> int:
        """Maximum number of Band Channels to simulate.

        Value should be between 1 and 100000.
        """
        val = self._get_property("Max # Channels/Range/Band")
        return int(val)

    @max_channels_range_band.setter
    @min_aedt_version("2025.2")
    def max_channels_range_band(self, value: int) -> None:
        self._set_property("Max # Channels/Range/Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def seed(self) -> int:
        """Seed for random channel generator.

        Value should be greater than 0.
        """
        val = self._get_property("Seed")
        return int(val)

    @seed.setter
    @min_aedt_version("2025.2")
    def seed(self, value: int) -> None:
        self._set_property("Seed", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def total_tx_channels(self) -> int:
        """Total Tx Channels.

        Total number of transmit channels this configuration is capable of
        operating on.
        """
        val = self._get_property("Total Tx Channels")
        return int(val)

    @property
    @min_aedt_version("2025.2")
    def total_rx_channels(self) -> int:
        """Total Rx Channels.

        Total number of receive channels this configuration is capable of
        operating on.
        """
        val = self._get_property("Total Rx Channels")
        return int(val)

    @property
    @min_aedt_version("2025.2")
    def warnings(self) -> str:
        """Warning(s) for this node."""
        val = self._get_property("Warnings")
        return val
