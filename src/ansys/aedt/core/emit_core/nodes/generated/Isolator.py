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

class Isolator(EmitNode):
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
        Name of file defining the outboard component

        Value should be a full file path.
        """
        val = self._get_property("Filename")
        return val # type: ignore

    @filename.setter
    def filename(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Filename={value}"])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        System Noise temperature (K) of the component

        Value should be between 0 and 1000.
        """
        val = self._get_property("Noise Temperature")
        return val # type: ignore

    @noise_temperature.setter
    def noise_temperature(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Noise Temperature={value}"])

    @property
    def notes(self) -> str:
        """Notes
        Expand to view/edit notes stored with the project

                """
        val = self._get_property("Notes")
        return val # type: ignore

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Notes={value}"])

    class TypeOption(Enum):
        BY_FILE = "By File" # eslint-disable-line no-eval
        PARAMETRIC = "Parametric" # eslint-disable-line no-eval

    @property
    def type(self) -> TypeOption:
        """Type
        Type of isolator model to use. Options include: By File (measured or
         simulated) or Parametric

                """
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val # type: ignore

    @type.setter
    def type(self, value: TypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Type={value.value}"])

    class Port1LocationOption(Enum):
        RADIO_SIDE = "Radio Side" # eslint-disable-line no-eval
        ANTENNA_SIDE = "Antenna Side" # eslint-disable-line no-eval

    @property
    def port_1_location(self) -> Port1LocationOption:
        """Port 1 Location
        Defines the orientation of the isolator.

                """
        val = self._get_property("Port 1 Location")
        val = self.Port1LocationOption[val.upper()]
        return val # type: ignore

    @port_1_location.setter
    def port_1_location(self, value: Port1LocationOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Port 1 Location={value.value}"])

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        Isolator in-band loss in forward direction.

        Value should be between 0 and 100.
        """
        val = self._get_property("Insertion Loss")
        return val # type: ignore

    @insertion_loss.setter
    def insertion_loss(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Insertion Loss={value}"])

    @property
    def finite_reverse_isolation(self) -> bool:
        """Finite Reverse Isolation
        Use a finite reverse isolation. If disabled, the  isolator model is
         ideal (infinite reverse isolation).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Reverse Isolation")
        val = (val == 'true')
        return val # type: ignore

    @finite_reverse_isolation.setter
    def finite_reverse_isolation(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Finite Reverse Isolation={value}"])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        Isolator reverse isolation (i.e., loss in the reverse direction).

        Value should be between 0 and 100.
        """
        val = self._get_property("Reverse Isolation")
        return val # type: ignore

    @reverse_isolation.setter
    def reverse_isolation(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Reverse Isolation={value}"])

    @property
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth
        Use a finite bandwidth. If disabled, the  isolator model is ideal
         (infinite bandwidth).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Finite Bandwidth")
        val = (val == 'true')
        return val # type: ignore

    @finite_bandwidth.setter
    def finite_bandwidth(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Finite Bandwidth={value}"])

    @property
    def out_of_band_attenuation(self) -> float:
        """Out-of-band Attenuation
        Out-of-band loss (attenuation)

        Value should be between 0 and 200.
        """
        val = self._get_property("Out-of-band Attenuation")
        return val # type: ignore

    @out_of_band_attenuation.setter
    def out_of_band_attenuation(self, value : float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Out-of-band Attenuation={value}"])

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        Lower stop band frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @lower_stop_band.setter
    def lower_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Lower Stop Band={value}"])

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        Lower cutoff frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @lower_cutoff.setter
    def lower_cutoff(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Lower Cutoff={value}"])

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        Higher cutoff frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @higher_cutoff.setter
    def higher_cutoff(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Higher Cutoff={value}"])

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        Higher stop band frequency

        Value should be between 1 and 1e+11.
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val # type: ignore

    @higher_stop_band.setter
    def higher_stop_band(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, 
                                                  self._node_id, 
                                                  [f"Higher Stop Band={value}"])

    @property
    def warnings(self) -> str:
        """Warnings
        Warning(s) for this node

                """
        val = self._get_property("Warnings")
        return val # type: ignore

