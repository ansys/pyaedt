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


class MultiplexerBand(EmitNode):
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

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    class TypeOption(Enum):
        BY_FILE = "By File"
        LOW_PASS = "Low Pass"  # nosec
        HIGH_PASS = "High Pass"  # nosec
        BAND_PASS = "Band Pass"  # nosec

    @property
    def type(self) -> TypeOption:
        """Type.

        Type of multiplexer pass band to define. The pass band can be defined by
        file (measured or simulated data) or using one of EMIT's parametric
        models.
        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._set_property("Type", f"{value.value}")

    @property
    def filename(self) -> str:
        """Name of file defining the multiplexer band.

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    def filename(self, value: str):
        self._set_property("Filename", f"{value}")

    @property
    def insertion_loss(self) -> float:
        """Multiplexer pass band insertion loss.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss")
        return float(val)

    @insertion_loss.setter
    def insertion_loss(self, value: float):
        self._set_property("Insertion Loss", f"{value}")

    @property
    def stop_band_attenuation(self) -> float:
        """Stop-band loss (attenuation).

        Value should be between 0 and 200.
        """
        val = self._get_property("Stop band Attenuation")
        return float(val)

    @stop_band_attenuation.setter
    def stop_band_attenuation(self, value: float):
        self._set_property("Stop band Attenuation", f"{value}")

    @property
    def max_pass_band(self) -> float:
        """Maximum pass band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Max Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_pass_band.setter
    def max_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Pass Band", f"{value}")

    @property
    def min_stop_band(self) -> float:
        """Minimum stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Min Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @min_stop_band.setter
    def min_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Min Stop Band", f"{value}")

    @property
    def max_stop_band(self) -> float:
        """Maximum stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Max Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @max_stop_band.setter
    def max_stop_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Max Stop Band", f"{value}")

    @property
    def min_pass_band(self) -> float:
        """Minimum pass band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Min Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @min_pass_band.setter
    def min_pass_band(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Min Pass Band", f"{value}")

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
