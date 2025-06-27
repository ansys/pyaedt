# -*- coding: utf-8 -*-
#
# Copyright(C) 2021 - 2025 ANSYS, Inc. and /or its affiliates.
# SPDX - License - Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from enum import Enum
from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode

class ReadOnlyIsolator(EmitNode):
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

    class TypeOption(Enum):
        BY_FILE = "By File"
        PARAMETRIC = "Parametric"

    @property
    def type(self) -> TypeOption:
        """Type.

        Type of isolator model to use. Options include: By File (measured or
        simulated) or Parametric.
        """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    class Port1LocationOption(Enum):
        RADIO_SIDE = "Radio Side"
        ANTENNA_SIDE = "Antenna Side"

    @property
    def port_1_location(self) -> Port1LocationOption:
        """Defines the orientation of the isolator."""
        val = self._get_property("Port 1 Location")
        val = self.Port1LocationOption[val.upper()]
        return val

    @property
    def insertion_loss(self) -> float:
        """Isolator in-band loss in forward direction.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss")
        return float(val)

    @property
    def finite_reverse_isolation(self) -> bool:
        """Finite Reverse Isolation.

        Use a finite reverse isolation. If disabled, the  isolator model is
        ideal (infinite reverse isolation).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Reverse Isolation")
        return (val == 'true')

    @property
    def reverse_isolation(self) -> float:
        """Isolator reverse isolation (i.e., loss in the reverse direction).

        Value should be between 0 and 100.
        """
        val = self._get_property("Reverse Isolation")
        return float(val)

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth.

        Use a finite bandwidth. If disabled, the  isolator model is ideal
        (infinite bandwidth).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Bandwidth")
        return (val == 'true')

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band loss (attenuation).

        Value should be between 0 and 200.
        """
        val = self._get_property("Out-of-band Attenuation")
        return float(val)

    @property
    def lower_stop_band(self) -> float:
        """Lower stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def lower_cutoff(self) -> float:
        """Lower cutoff frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def higher_cutoff(self) -> float:
        """Higher cutoff frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def higher_stop_band(self) -> float:
        """Higher stop band frequency.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def warnings(self) -> str:
        """Warning(s) for this node."""
        val = self._get_property("Warnings")
        return val

