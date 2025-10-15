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


class PowerDivider(EmitNode):
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
    def filename(self) -> str:
        """Name of file defining the Power Divider.

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

    class TypeOption(Enum):
        BY_FILE = "By File"
        P3_DB = "P3 dB"
        RESISTIVE = "Resistive"

    @property
    def type(self) -> TypeOption:
        """Type.

        Type of Power Divider model to use. Options include: By File (measured
        or simulated), 3 dB (parametric), and Resistive (parametric).
        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._set_property("Type", f"{value.value}")

    @property
    def insertion_loss_above_ideal(self) -> float:
        """Insertion Loss Above Ideal.

        Additional loss beyond the ideal insertion loss. The ideal insertion
        loss is 3 dB for the 3 dB Divider and 6 dB for the Resistive Divider.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss Above Ideal")
        return float(val)

    @insertion_loss_above_ideal.setter
    def insertion_loss_above_ideal(self, value: float):
        self._set_property("Insertion Loss Above Ideal", f"{value}")

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation.

        Use a finite isolation between output ports. If disabled, the Power
        Divider isolation is ideal (infinite isolation between output ports).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Isolation")
        return val == "true"

    @finite_isolation.setter
    def finite_isolation(self, value: bool):
        self._set_property("Finite Isolation", f"{str(value).lower()}")

    @property
    def isolation(self) -> float:
        """Power Divider isolation between output ports.

        Value should be between 0 and 100.
        """
        val = self._get_property("Isolation")
        return float(val)

    @isolation.setter
    def isolation(self, value: float):
        self._set_property("Isolation", f"{value}")

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth.

        Use a finite bandwidth. If disabled, the  Power Divider model is ideal
        (infinite bandwidth).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Bandwidth")
        return val == "true"

    @finite_bandwidth.setter
    def finite_bandwidth(self, value: bool):
        self._set_property("Finite Bandwidth", f"{str(value).lower()}")

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band loss (attenuation).

        Value should be between 0 and 200.
        """
        val = self._get_property("Out-of-band Attenuation")
        return float(val)

    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value: float):
        self._set_property("Out-of-band Attenuation", f"{value}")

    @property
    def lower_stop_band(self) -> float:
        """Lower stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @lower_stop_band.setter
    def lower_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Lower Stop Band", f"{value}")

    @property
    def lower_cutoff(self) -> float:
        """Lower cutoff frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @lower_cutoff.setter
    def lower_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Lower Cutoff", f"{value}")

    @property
    def higher_cutoff(self) -> float:
        """Higher cutoff frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @higher_cutoff.setter
    def higher_cutoff(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Higher Cutoff", f"{value}")

    @property
    def higher_stop_band(self) -> float:
        """Higher stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @higher_stop_band.setter
    def higher_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Higher Stop Band", f"{value}")

    @property
    def warnings(self) -> str:
        """Warning(s) for this node."""
        val = self._get_property("Warnings")
        return val
