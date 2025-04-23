# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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


class ReadOnlyTerminator(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the Terminator."
        "Value should be a full file path."
        """
        val = self._get_property("Filename")
        return val  # type: ignore

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Noise Temperature")
        return val  # type: ignore

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        " """
        val = self._get_property("Notes")
        return val  # type: ignore

    class TypeOption(Enum):
        BY_FILE = "By File"
        PARAMETRIC = "Parametric"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of terminator model to use. Options include: By File (measured or simulated) or Parametric."
        " """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val  # type: ignore

    class PortLocationOption(Enum):
        RADIO_SIDE = "Radio Side"
        ANTENNA_SIDE = "Antenna Side"

    @property
    def port_location(self) -> PortLocationOption:
        """Port Location
        "Defines the orientation of the terminator.."
        " """
        val = self._get_property("Port Location")
        val = self.PortLocationOption[val]
        return val  # type: ignore

    @property
    def vswr(self) -> float:
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the terminator and the connected component (RF System, Antenna, etc)."
        "Value should be between 1 and 100."
        """
        val = self._get_property("VSWR")
        return val  # type: ignore

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        " """
        val = self._get_property("Warnings")
        return val  # type: ignore
