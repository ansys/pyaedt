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


class Amplifier(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def filename(self) -> str:
        """Filename
        Name of file defining the outboard component

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Filename={value}"])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        System Noise temperature (K) of the component

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return float(val)

    @noise_temperature.setter
    def noise_temperature(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Noise Temperature={value}"])

    @property
    def notes(self) -> str:
        """Notes
        Expand to view/edit notes stored with the project

        """
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Notes={value}"])

    class AmplifierTypeOption(Enum):
        TRANSMIT_AMPLIFIER = "Transmit Amplifier"
        RECEIVE_AMPLIFIER = "Receive Amplifier"

    @property
    def amplifier_type(self) -> AmplifierTypeOption:
        """Amplifier Type
        Configures the amplifier as a Tx or Rx amplifier

        """
        val = self._get_property("Amplifier Type")
        val = self.AmplifierTypeOption[val.upper()]
        return val

    @amplifier_type.setter
    def amplifier_type(self, value: AmplifierTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Amplifier Type={value.value}"])

    @property
    def gain(self) -> float:
        """Gain
        Amplifier in-band gain

        Value should be between 0 and 100.
        """
        val = self._get_property("Gain")
        return float(val)

    @gain.setter
    def gain(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Gain={value}"])

    @property
    def center_frequency(self) -> float:
        """Center Frequency
        Center frequency of amplifiers operational bandwidth

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Center Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @center_frequency.setter
    def center_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Center Frequency={value}"])

    @property
    def bandwidth(self) -> float:
        """Bandwidth
        Frequency region where the gain applies

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bandwidth.setter
    def bandwidth(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Bandwidth={value}"])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        Amplifier noise figure

        Value should be between 0 and 100.
        """
        val = self._get_property("Noise Figure")
        return float(val)

    @noise_figure.setter
    def noise_figure(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Noise Figure={value}"])

    @property
    def saturation_level(self) -> float:
        """Saturation Level
        Saturation level

        Value should be between -200 and 200.
        """
        val = self._get_property("Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @saturation_level.setter
    def saturation_level(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Saturation Level={value}"])

    @property
    def p1_db_point_ref_input(self) -> float:
        """P1-dB Point, Ref. Input
        Incoming signals > this value saturate the amplifier

        Value should be between -200 and 200.
        """
        val = self._get_property("P1-dB Point, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @p1_db_point_ref_input.setter
    def p1_db_point_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"P1-dB Point, Ref. Input={value}"])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        3rd order intercept point

        Value should be between -200 and 200.
        """
        val = self._get_property("IP3, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @ip3_ref_input.setter
    def ip3_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"IP3, Ref. Input={value}"])

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        Ratio defining the selectivity of the amplifier

        Value should be between 1 and 100.
        """
        val = self._get_property("Shape Factor")
        return float(val)

    @shape_factor.setter
    def shape_factor(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Shape Factor={value}"])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        Amplifier reverse isolation

        Value should be between 0 and 200.
        """
        val = self._get_property("Reverse Isolation")
        return float(val)

    @reverse_isolation.setter
    def reverse_isolation(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Reverse Isolation={value}"])

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        Maximum order of intermods to compute

        Value should be between 3 and 20.
        """
        val = self._get_property("Max Intermod Order")
        return int(val)

    @max_intermod_order.setter
    def max_intermod_order(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Max Intermod Order={value}"])
