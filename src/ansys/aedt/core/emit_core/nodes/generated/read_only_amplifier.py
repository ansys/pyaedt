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


class ReadOnlyAmplifier(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def filename(self) -> str:
        """Name of file defining the outboard component.

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val

    @property
    def noise_temperature(self) -> float:
        """System Noise temperature (K) of the component.

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return float(val)

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    class AmplifierTypeOption(Enum):
        TRANSMIT_AMPLIFIER = "Transmit Amplifier"
        RECEIVE_AMPLIFIER = "Receive Amplifier"

    @property
    def amplifier_type(self) -> AmplifierTypeOption:
        """Configures the amplifier as a Tx or Rx amplifier."""
        val = self._get_property("Amplifier Type")
        val = self.AmplifierTypeOption[val.upper()]
        return val

    @property
    def gain(self) -> float:
        """Amplifier in-band gain.

        Value should be between 0 and 100.
        """
        val = self._get_property("Gain")
        return float(val)

    @property
    def center_frequency(self) -> float:
        """Center frequency of amplifiers operational bandwidth.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Center Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def bandwidth(self) -> float:
        """Frequency region where the gain applies.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def noise_figure(self) -> float:
        """Amplifier noise figure.

        Value should be between 0 and 100.
        """
        val = self._get_property("Noise Figure")
        return float(val)

    @property
    def saturation_level(self) -> float:
        """Saturation level.

        Value should be between -200 and 200.
        """
        val = self._get_property("Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @property
    def p1_db_point_ref_input(self) -> float:
        """Incoming signals > this value saturate the amplifier.

        Value should be between -200 and 200.
        """
        val = self._get_property("P1-dB Point, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @property
    def ip3_ref_input(self) -> float:
        """3rd order intercept point.

        Value should be between -200 and 200.
        """
        val = self._get_property("IP3, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @property
    def shape_factor(self) -> float:
        """Ratio defining the selectivity of the amplifier.

        Value should be between 1 and 100.
        """
        val = self._get_property("Shape Factor")
        return float(val)

    @property
    def reverse_isolation(self) -> float:
        """Amplifier reverse isolation.

        Value should be between 0 and 200.
        """
        val = self._get_property("Reverse Isolation")
        return float(val)

    @property
    def max_intermod_order(self) -> int:
        """Maximum order of intermods to compute.

        Value should be between 3 and 20.
        """
        val = self._get_property("Max Intermod Order")
        return int(val)
