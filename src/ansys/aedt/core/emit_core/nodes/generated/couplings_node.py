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

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


class CouplingsNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def import_touchstone(self, file_name):
        """Open an Existing S-Matrix Data File"""
        return self._import(file_name, "TouchstoneCoupling")

    def add_custom_coupling(self):
        """Add a new node to define custom coupling between antennas"""
        return self._add_child_node("Custom Coupling")

    def add_path_loss_coupling(self):
        """Add a new node to define path loss coupling between antennas"""
        return self._add_child_node("Path Loss Coupling")

    def add_two_ray_path_loss_coupling(self):
        """Add a new node to define two ray ground reflection coupling between antennas"""
        return self._add_child_node("Two Ray Path Loss Coupling")

    def add_log_distance_coupling(self):
        """Add a new node to define coupling between antennas using the Log Distance model"""
        return self._add_child_node("Log Distance Coupling")

    def add_hata_coupling(self):
        """Add a new node to define coupling between antennas using the Hata COST 231 model"""
        return self._add_child_node("Hata Coupling")

    def add_walfisch_ikegami_coupling(self):
        """Add a new node to define coupling between antennas using the Walfisch-Ikegami model"""
        return self._add_child_node("Walfisch-Ikegami Coupling")

    def add_erceg_coupling(self):
        """Add a new node to define coupling between antennas using the Erceg coupling model"""
        return self._add_child_node("Erceg Coupling")

    def add_indoor_propagation_coupling(self):
        """Add a new node to define coupling between antennas using the ITU Indoor Propagation model"""
        return self._add_child_node("Indoor Propagation Coupling")

    def add_5g_channel_model_coupling(self):
        """Add a new node to define coupling between antennas using the 5G channel coupling model"""
        return self._add_child_node("5G Channel Model Coupling")

    @property
    def minimum_allowed_coupling(self) -> float:
        """Minimum Allowed Coupling.

        Global minimum allowed coupling value. All computed coupling within this
        project will be >= this value.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Minimum Allowed Coupling")
        return float(val)

    @minimum_allowed_coupling.setter
    def minimum_allowed_coupling(self, value: float):
        self._set_property("Minimum Allowed Coupling", f"{value}")

    @property
    def global_default_coupling(self) -> float:
        """Default antenna-to-antenna coupling loss value.

        Value should be between -1000 and 0.
        """
        val = self._get_property("Global Default Coupling")
        return float(val)

    @global_default_coupling.setter
    def global_default_coupling(self, value: float):
        self._set_property("Global Default Coupling", f"{value}")

    @property
    def antenna_tags(self) -> str:
        """All tags currently used by all antennas in the project."""
        val = self._get_property("Antenna Tags")
        return val
