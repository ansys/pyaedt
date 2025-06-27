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

class ReadOnlySceneGroupNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates.

        Show Scene Group position and orientation in parent-node coords (False)
        or relative to placement coords (True).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Relative Coordinates")
        return (val == 'true')

    @property
    def position(self):
        """Set position of the Scene Group in parent-node coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Position")
        return val

    @property
    def relative_position(self):
        """Set position of the Scene Group relative to placement coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Relative Position")
        return val

    class OrientationModeOption(Enum):
        ROLL_PITCH_YAW = "Roll-Pitch-Yaw"
        AZ_EL_TWIST = "Az-El-Twist"

    @property
    def orientation_mode(self) -> OrientationModeOption:
        """Orientation Mode.

        Select the convention (order of rotations) for configuring orientation.
        """
        val = self._get_property("Orientation Mode")
        val = self.OrientationModeOption[val.upper()]
        return val

    @property
    def orientation(self):
        """Orientation.

        Set orientation of the Scene Group relative to parent-node coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Orientation")
        return val

    @property
    def relative_orientation(self):
        """Relative Orientation.

        Set orientation of the Scene Group relative to placement coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Relative Orientation")
        return val

    @property
    def show_axes(self) -> bool:
        """Show Axes.

        Toggle (on/off) display of Scene Group coordinate axes in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Axes")
        return (val == 'true')

    @property
    def box_color(self):
        """Set color of the bounding box of the Scene Group.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Box Color")
        return val

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

