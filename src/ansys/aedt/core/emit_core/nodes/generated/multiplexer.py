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


class Multiplexer(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    def add_multiplexer_pass_band(self):
        """Add a New Multiplexer Band to this Multiplexer"""
        return self._add_child_node("Multiplexer Pass Band")

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
        Name of file defining the multiplexer

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

    class TypeOption(Enum):
        BY_PASS_BAND = "By Pass Band"
        BY_FILE = "By File"

    @property
    def type(self) -> TypeOption:
        """Type
        Type of multiplexer model. Options include: By File (one measured or
         simulated file for the device) or By Pass Band (parametric or
         file-based definition for each pass band)

        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Type={value.value}"])

    class Port1LocationOption(Enum):
        RADIO_SIDE = "Radio Side"
        ANTENNA_SIDE = "Antenna Side"

    @property
    def port_1_location(self) -> Port1LocationOption:
        """Port 1 Location
        Defines the orientation of the multiplexer.

        """
        val = self._get_property("Port 1 Location")
        val = self.Port1LocationOption[val.upper()]
        return val

    @port_1_location.setter
    def port_1_location(self, value: Port1LocationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Port 1 Location={value.value}"])

    @property
    def flip_ports_vertically(self) -> bool:
        """Flip Ports Vertically
        Reverses the port order on the multi-port side of the multiplexer.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Flip Ports Vertically")
        return val == true

    @flip_ports_vertically.setter
    def flip_ports_vertically(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Flip Ports Vertically={value}"])

    @property
    def ports(self):
        """Ports
        Assigns the child port nodes to the multiplexers ports

        "A list of values."
        """
        val = self._get_property("Ports")
        return val

    @ports.setter
    def ports(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Ports={value}"])

    @property
    def warnings(self) -> str:
        """Warnings
        Warning(s) for this node

        """
        val = self._get_property("Warnings")
        return val
