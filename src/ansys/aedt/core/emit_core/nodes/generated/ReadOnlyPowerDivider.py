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
from ..EmitNode import EmitNode

class ReadOnlyPowerDivider(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        Name of file defining the Power Divider

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val # type: ignore

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        System Noise temperature (K) of the component

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return val # type: ignore

    @property
    def notes(self) -> str:
        """Notes
        Expand to view/edit notes stored with the project

                """
        val = self._get_property("Notes")
        return val # type: ignore

    class TypeOption(Enum):
        BY_FILE = "By File"
        P3_DB = "P3 dB"
        RESISTIVE = "Resistive"

    @property
    def type(self) -> TypeOption:
        """Type
        Type of Power Divider model to use. Options include: By File (measured
         or simulated), 3 dB (parametric), and Resistive (parametric)

                """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val # type: ignore

    class OrientationOption(Enum):
        DIVIDER = "Divider"
        COMBINER = "Combiner"

    @property
    def orientation(self) -> OrientationOption:
        """Orientation
        Defines the orientation of the Power Divider.

                """
        val = self._get_property("Orientation")
        val = self.OrientationOption[val]
        return val # type: ignore

    @property
    def insertion_loss_above_ideal(self) -> float:
        """Insertion Loss Above Ideal
        Additional loss beyond the ideal insertion loss. The ideal insertion
         loss is 3 dB for the 3 dB Divider and 6 dB for the Resistive Divider.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss Above Ideal")
        return val # type: ignore

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation
        Use a finite isolation between output ports. If disabled, the Power
         Divider isolation is ideal (infinite isolation between output ports).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Isolation")
        return val # type: ignore

    @property
    def isolation(self) -> float:
        """Isolation
        Power Divider isolation between output ports.

        Value should be between 0 and 100.
        """
        val = self._get_property("Isolation")
        return val # type: ignore

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        Use a finite bandwidth. If disabled, the  Power Divider model is ideal
         (infinite bandwidth).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Bandwidth")
        return val # type: ignore

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        Out-of-band loss (attenuation)

        Value should be between 0 and 200.
        """
        val = self._get_property("Out-of-band Attenuation")
        return val # type: ignore

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        Lower stop band frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        Lower cutoff frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        Higher cutoff frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        Higher stop band frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def warnings(self) -> str:
        """Warnings
        Warning(s) for this node

                """
        val = self._get_property("Warnings")
        return val # type: ignore

