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


class Cable(EmitNode):
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

    class TypeOption(Enum):
        BY_FILE = "By File"
        CONSTANT_LOSS = "Constant Loss"
        COAXIAL_CABLE = "Coaxial Cable"

    @property
    def type(self) -> TypeOption:
        """Type.

        Type of cable to use. Options include: By File (measured or simulated),
        Constant Loss, or Coaxial Cable.
        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._set_property("Type", f"{value.value}")

    @property
    def length(self) -> float:
        """Length of cable.

        Value should be between 0 and 500.
        """
        val = self._get_property("Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @length.setter
    def length(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Length", f"{value}")

    @property
    def loss_per_length(self) -> float:
        """Cable loss per unit length (dB/meter).

        Value should be between 0 and 20.
        """
        val = self._get_property("Loss Per Length")
        return float(val)

    @loss_per_length.setter
    def loss_per_length(self, value: float):
        self._set_property("Loss Per Length", f"{value}")

    @property
    def measurement_length(self) -> float:
        """Length of the cable used for the measurements.

        Value should be between 0 and 500.
        """
        val = self._get_property("Measurement Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @measurement_length.setter
    def measurement_length(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Measurement Length", f"{value}")

    @property
    def resistive_loss_constant(self) -> float:
        """Coaxial cable resistive loss constant.

        Value should be between 0 and 2.
        """
        val = self._get_property("Resistive Loss Constant")
        return float(val)

    @resistive_loss_constant.setter
    def resistive_loss_constant(self, value: float):
        self._set_property("Resistive Loss Constant", f"{value}")

    @property
    def dielectric_loss_constant(self) -> float:
        """Coaxial cable dielectric loss constant.

        Value should be between 0 and 1.
        """
        val = self._get_property("Dielectric Loss Constant")
        return float(val)

    @dielectric_loss_constant.setter
    def dielectric_loss_constant(self, value: float):
        self._set_property("Dielectric Loss Constant", f"{value}")

    @property
    def warnings(self) -> str:
        """Warning(s) for this node."""
        val = self._get_property("Warnings")
        return val
