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

from ..EmitNode import EmitNode


class Terminator(EmitNode):
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
        Name of file defining the Terminator

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val  # type: ignore

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
        return val  # type: ignore

    @noise_temperature.setter
    def noise_temperature(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Noise Temperature={value}"])

    @property
    def notes(self) -> str:
        """Notes
        Expand to view/edit notes stored with the project

        """
        val = self._get_property("Notes")
        return val  # type: ignore

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Notes={value}"])

    class TypeOption(Enum):
        BY_FILE = "By File"  # eslint-disable-line no-eval
        PARAMETRIC = "Parametric"  # eslint-disable-line no-eval

    @property
    def type(self) -> TypeOption:
        """Type
        Type of terminator model to use. Options include: By File (measured or
         simulated) or Parametric

        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val  # type: ignore

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Type={value.value}"])

    class PortLocationOption(Enum):
        RADIO_SIDE = "Radio Side"  # eslint-disable-line no-eval
        ANTENNA_SIDE = "Antenna Side"  # eslint-disable-line no-eval

    @property
    def port_location(self) -> PortLocationOption:
        """Port Location
        Defines the orientation of the terminator.

        """
        val = self._get_property("Port Location")
        val = self.PortLocationOption[val.upper()]
        return val  # type: ignore

    @port_location.setter
    def port_location(self, value: PortLocationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Port Location={value.value}"])

    @property
    def vswr(self) -> float:
        """VSWR
        The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch
         between the terminator and the connected component (RF System, Antenna,
         etc)

        Value should be between 1 and 100.
        """
        val = self._get_property("VSWR")
        return val  # type: ignore

    @vswr.setter
    def vswr(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"VSWR={value}"])

    @property
    def warnings(self) -> str:
        """Warnings
        Warning(s) for this node

        """
        val = self._get_property("Warnings")
        return val  # type: ignore
