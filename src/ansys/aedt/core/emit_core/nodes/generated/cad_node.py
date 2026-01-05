# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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


class CADNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def rename(self, new_name: str = ""):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str = ""):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def file(self) -> str:
        """Name of the imported CAD file.

        Value should be a full file path.
        """
        val = self._get_property("File")
        return val

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates.

        Show CAD model node position and orientation in parent-node coords
        (False) or relative to placement coords (True).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Relative Coordinates")
        return val == "true"

    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value: bool):
        self._set_property("Show Relative Coordinates", f"{str(value).lower()}")

    @property
    def position(self):
        """Set position of the CAD node in parent-node coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Position")
        return val

    @position.setter
    def position(self, value):
        self._set_property("Position", f"{value}")

    @property
    def relative_position(self):
        """Relative Position.

        Set position of the CAD model node relative to placement coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Relative Position")
        return val

    @relative_position.setter
    def relative_position(self, value):
        self._set_property("Relative Position", f"{value}")

    class OrientationModeOption(Enum):
        ROLL_PITCH_YAW = "rpyDeg"
        AZ_EL_TWIST = "aetDeg"

    @property
    def orientation_mode(self) -> OrientationModeOption:
        """Orientation Mode.

        Select the convention (order of rotations) for configuring orientation.
        """
        val = self._get_property("Orientation Mode")
        val = self.OrientationModeOption[val.upper()]
        return val

    @orientation_mode.setter
    def orientation_mode(self, value: OrientationModeOption):
        self._set_property("Orientation Mode", f"{value.value}")

    @property
    def orientation(self):
        """Set orientation of the CAD node in parent-node coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Orientation")
        return val

    @orientation.setter
    def orientation(self, value):
        self._set_property("Orientation", f"{value}")

    @property
    def relative_orientation(self):
        """Relative Orientation.

        Set orientation of the CAD model node relative to placement coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Relative Orientation")
        return val

    @relative_orientation.setter
    def relative_orientation(self, value):
        self._set_property("Relative Orientation", f"{value}")

    @property
    def visible(self) -> bool:
        """Toggle (on/off) display of CAD model in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Visible")
        return val == "true"

    @visible.setter
    def visible(self, value: bool):
        self._set_property("Visible", f"{str(value).lower()}")

    class RenderModeOption(Enum):
        FLAT_SHADED = "Flat-shaded"
        WIRE_FRAME = "Wire-frame"
        HIDDEN_WIRE_FRAME = "Hidden wire-frame"
        OUTLINE = "Outline"

    @property
    def render_mode(self) -> RenderModeOption:
        """Select drawing style for surfaces."""
        val = self._get_property("Render Mode")
        val = self.RenderModeOption[val.upper()]
        return val

    @render_mode.setter
    def render_mode(self, value: RenderModeOption):
        self._set_property("Render Mode", f"{value.value}")

    @property
    def show_axes(self) -> bool:
        """Toggle (on/off) display of CAD model coordinate axes in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Axes")
        return val == "true"

    @show_axes.setter
    def show_axes(self, value: bool):
        self._set_property("Show Axes", f"{str(value).lower()}")

    @property
    def min(self):
        """Minimum x,y,z extents of CAD model in local coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Min")
        return val

    @property
    def max(self):
        """Maximum x,y,z extents of CAD model in local coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Max")
        return val

    @property
    def number_of_surfaces(self) -> int:
        """Number of surfaces in the model."""
        val = self._get_property("Number of Surfaces")
        return int(val)

    @property
    def color(self):
        """Defines the CAD nodes color.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Color")
        return val

    @color.setter
    def color(self, value):
        self._set_property("Color", f"{value}")

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._set_property("Notes", f"{value}")
