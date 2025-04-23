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

class ReadOnlyTR_Switch(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property("Filename")
        return val # type: ignore

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Noise Temperature")
        return val # type: ignore

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property("Notes")
        return val # type: ignore

    class TxPortOption(Enum):
        PORT_1 = "Port 1"
        PORT_2 = "Port 2"

    @property
    def tx_port(self) -> TxPortOption:
        """Tx Port
        "Specifies which port on the TR Switch is part of the Tx path.."
        "        """
        val = self._get_property("Tx Port")
        val = self.TxPortOption[val]
        return val # type: ignore

    class CommonPortLocationOption(Enum):
        RADIO_SIDE = "Radio Side"
        ANTENNA_SIDE = "Antenna Side"

    @property
    def common_port_location(self) -> CommonPortLocationOption:
        """Common Port Location
        "Defines the orientation of the tr switch.."
        "        """
        val = self._get_property("Common Port Location")
        val = self.CommonPortLocationOption[val]
        return val # type: ignore

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "TR Switch in-band loss in forward direction.."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Insertion Loss")
        return val # type: ignore

    @property
    def finite_isolation(self) -> bool:
        """Finite Isolation
        "Use a finite isolation. If disabled, the  tr switch model is ideal (infinite isolation).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Finite Isolation")
        return val # type: ignore

    @property
    def isolation(self) -> float:
        """Isolation
        "TR Switch reverse isolation (i.e., loss between the Tx/Rx ports).."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Isolation")
        return val # type: ignore

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        "Use a finite bandwidth. If disabled, the  tr switch model is ideal (infinite bandwidth).."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Finite Bandwidth")
        return val # type: ignore

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        "Out-of-band loss (attenuation)."
        "Value should be between 0 and 200."
        """
        val = self._get_property("Out-of-band Attenuation")
        return val # type: ignore

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

