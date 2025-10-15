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


class EmitSceneNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def add_group(self):
        """Add a new scene group"""
        return self._add_child_node("Group")

    def add_antenna(self):
        """Add a new antenna"""
        return self._add_child_node("Antenna")

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._set_property("Notes", f"{value}")

    class GroundPlaneNormalOption(Enum):
        X_AXIS = "X Axis"
        Y_AXIS = "Y Axis"
        Z_AXIS = "Z Axis"

    @property
    def ground_plane_normal(self) -> GroundPlaneNormalOption:
        """Specifies the axis of the normal to the ground plane."""
        val = self._get_property("Ground Plane Normal")
        val = self.GroundPlaneNormalOption[val.upper()]
        return val

    @ground_plane_normal.setter
    def ground_plane_normal(self, value: GroundPlaneNormalOption):
        self._set_property("Ground Plane Normal", f"{value.value}")

    @property
    def gp_position_along_normal(self) -> float:
        """GP Position Along Normal.

        Offset of ground plane in direction normal to the ground planes
        orientation.
        """
        val = self._get_property("GP Position Along Normal")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @gp_position_along_normal.setter
    def gp_position_along_normal(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("GP Position Along Normal", f"{value}")
