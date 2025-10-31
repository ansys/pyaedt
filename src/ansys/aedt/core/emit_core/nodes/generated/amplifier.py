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


from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


class Amplifier(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

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
    def table_data(self):
        """Harmonic Intercept Points, Ref. Input Table.
        Table consists of 2 columns.
        Harmonic:
            Value should be between 2 and 20.
        Intercept Point:
            Value should be between -1000 and 1000.
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def filename(self) -> str:
        """Name of file defining the outboard component.

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    def filename(self, value: str):
        self._set_property("Filename", f"{value}")

    @property
    def noise_temperature(self) -> float:
        """System Noise temperature (K) of the component.

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return float(val)

    @noise_temperature.setter
    def noise_temperature(self, value: float):
        self._set_property("Noise Temperature", f"{value}")

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._set_property("Notes", f"{value}")

    @property
    def gain(self) -> float:
        """Amplifier in-band gain.

        Value should be between 0 and 100.
        """
        val = self._get_property("Gain")
        return float(val)

    @gain.setter
    def gain(self, value: float):
        self._set_property("Gain", f"{value}")

    @property
    def center_frequency(self) -> float:
        """Center frequency of amplifiers operational bandwidth.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Center Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @center_frequency.setter
    def center_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Center Frequency", f"{value}")

    @property
    def bandwidth(self) -> float:
        """Frequency region where the gain applies.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Bandwidth")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bandwidth.setter
    def bandwidth(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Bandwidth", f"{value}")

    @property
    def noise_figure(self) -> float:
        """Amplifier noise figure.

        Value should be between 0 and 100.
        """
        val = self._get_property("Noise Figure")
        return float(val)

    @noise_figure.setter
    def noise_figure(self, value: float):
        self._set_property("Noise Figure", f"{value}")

    @property
    def saturation_level(self) -> float:
        """Saturation level.

        Value should be between -200 and 200.
        """
        val = self._get_property("Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @saturation_level.setter
    def saturation_level(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("Saturation Level", f"{value}")

    @property
    def p1_db_point_ref_input(self) -> float:
        """Incoming signals > this value saturate the amplifier.

        Value should be between -200 and 200.
        """
        val = self._get_property("P1-dB Point, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @p1_db_point_ref_input.setter
    def p1_db_point_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("P1-dB Point, Ref. Input", f"{value}")

    @property
    def ip3_ref_input(self) -> float:
        """3rd order intercept point.

        Value should be between -200 and 200.
        """
        val = self._get_property("IP3, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @ip3_ref_input.setter
    def ip3_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("IP3, Ref. Input", f"{value}")

    @property
    def shape_factor(self) -> float:
        """Ratio defining the selectivity of the amplifier.

        Value should be between 1 and 100.
        """
        val = self._get_property("Shape Factor")
        return float(val)

    @shape_factor.setter
    def shape_factor(self, value: float):
        self._set_property("Shape Factor", f"{value}")

    @property
    def reverse_isolation(self) -> float:
        """Amplifier reverse isolation.

        Value should be between 0 and 200.
        """
        val = self._get_property("Reverse Isolation")
        return float(val)

    @reverse_isolation.setter
    def reverse_isolation(self, value: float):
        self._set_property("Reverse Isolation", f"{value}")

    @property
    def max_intermod_order(self) -> int:
        """Maximum order of intermods to compute.

        Value should be between 3 and 20.
        """
        val = self._get_property("Max Intermod Order")
        return int(val)

    @max_intermod_order.setter
    def max_intermod_order(self, value: int):
        self._set_property("Max Intermod Order", f"{value}")
