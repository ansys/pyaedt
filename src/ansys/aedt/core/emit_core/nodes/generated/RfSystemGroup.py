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

from ..EmitNode import EmitNode


class RfSystemGroup(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enable_passive_noise(self) -> bool:
        """Enable Passive Noise
        "If true, the noise contributions of antennas and passive components are included in cosite simulation. Note: Antenna and passive component noise is always included in link analysis simulation.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enable Passive Noise")
        return val  # type: ignore

    @enable_passive_noise.setter
    def enable_passive_noise(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Enable Passive Noise={value}"])

    @property
    def enforce_thermal_noise_floor(self) -> bool:
        """Enforce Thermal Noise Floor
        "If true, all broadband noise is limited by the thermal noise floor (-174 dBm/Hz)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Enforce Thermal Noise Floor")
        return val  # type: ignore

    @enforce_thermal_noise_floor.setter
    def enforce_thermal_noise_floor(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, [f"Enforce Thermal Noise Floor={value}"]
        )
