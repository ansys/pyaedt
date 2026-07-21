# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from ansys.aedt.core.internal.checks import min_aedt_version


class SceneGroupNode(EmitNode):
    """Provide scene group node."""

    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.parent

        """
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def add_emitter(self) -> EmitNode:
        """Add a new emitter

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> emitter = scene_group.add_emitter()

        """
        return self._add_child_node("Emitter")

    @min_aedt_version("2025.2")
    def add_group(self) -> EmitNode:
        """Add a new scene group

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> group = scene_group.add_group()

        """
        return self._add_child_node("Group")

    @min_aedt_version("2025.2")
    def import_cad(self, file_name: str, create_antennas: bool = False) -> EmitNode:
        """Add an existing CAD file

        Parameters
        ----------
        file_name : str
            Full path to the file to import.
        create_antennas : bool
            Whether to automatically create antennas for any mounting points
            defined in the CAD file (only applicable to gltf/glb files).

        Returns
        ------
        node : EmitNode
            The node."""
        return self._import(file_name, "CAD", create_antennas=create_antennas)

    @min_aedt_version("2025.2")
    def add_antenna(self) -> EmitNode:
        """Add a new antenna

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> antenna = scene_group.add_antenna()

        """
        return self._add_child_node("Antenna")

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp_copy = grp.duplicate("grp_copy")

        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates.

        Show Scene Group position and orientation in parent-node coords (False)
        or relative to placement coords (True).

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.show_relative_coordinates = True

        """
        val = self._get_property("Show Relative Coordinates")
        return val == "true"

    @show_relative_coordinates.setter
    @min_aedt_version("2025.2")
    def show_relative_coordinates(self, value: bool) -> None:
        self._set_property("Show Relative Coordinates", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def position(self) -> list[float]:
        """Set position of the Scene Group in parent-node coordinates.

        Value should be a list of 3 floats.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.position

        """
        val = self._get_property("Position")
        return val

    @position.setter
    @min_aedt_version("2025.2")
    def position(self, value: list[float] | str) -> None:
        self._set_property("Position", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def relative_position(self) -> list[float]:
        """Set position of the Scene Group relative to placement coordinates.

        Value should be a list of 3 floats.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.relative_position

        """
        val = self._get_property("Relative Position")
        return val

    @relative_position.setter
    @min_aedt_version("2025.2")
    def relative_position(self, value: list[float] | str) -> None:
        self._set_property("Relative Position", f"{value}")

    class OrientationModeOption(Enum):
        ROLL_PITCH_YAW = "rpyDeg"
        AZ_EL_TWIST = "aetDeg"

    @property
    @min_aedt_version("2025.2")
    def orientation_mode(self) -> OrientationModeOption:
        """Orientation Mode.

        Select the convention (order of rotations) for configuring orientation.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.orientation_mode = SceneGroupNode.OrientationModeOption.ROLL_PITCH_YAW

        """
        val = self._get_property("Orientation Mode")
        val = self.OrientationModeOption[val.upper()]
        return val

    @orientation_mode.setter
    @min_aedt_version("2025.2")
    def orientation_mode(self, value: OrientationModeOption) -> None:
        self._set_property("Orientation Mode", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def orientation(self) -> list[float]:
        """Orientation.

        Set orientation of the Scene Group relative to parent-node coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.orientation

        """
        val = self._get_property("Orientation")
        return val

    @orientation.setter
    @min_aedt_version("2025.2")
    def orientation(self, value: list[float] | str) -> None:
        self._set_property("Orientation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def relative_orientation(self) -> list[float]:
        """Relative Orientation.

        Set orientation of the Scene Group relative to placement coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.relative_orientation

        """
        val = self._get_property("Relative Orientation")
        return val

    @relative_orientation.setter
    @min_aedt_version("2025.2")
    def relative_orientation(self, value: list[float] | str) -> None:
        self._set_property("Relative Orientation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def show_axes(self) -> bool:
        """Show Axes.

        Toggle (on/off) display of Scene Group coordinate axes in 3-D window.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.show_axes = True

        """
        val = self._get_property("Show Axes")
        return val == "true"

    @show_axes.setter
    @min_aedt_version("2025.2")
    def show_axes(self, value: bool) -> None:
        self._set_property("Show Axes", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def box_color(self) -> str:
        """Set color of the bounding box of the Scene Group.

        Color should be in RGB form: #RRGGBB.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.box_color = "example_value"

        """
        val = self._get_property("Box Color")
        return val

    @box_color.setter
    @min_aedt_version("2025.2")
    def box_color(self, value: str) -> None:
        self._set_property("Box Color", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def attach_points(self) -> str:
        """Attach Points.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.attach_points

        """
        val = self._get_property("Attach Points")
        return val

    @property
    @min_aedt_version("2025.2")
    def articulation_points(self) -> str:
        """Articulation Points.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.articulation_points

        """
        val = self._get_property("Articulation Points")
        return val

    @property
    @min_aedt_version("2025.2")
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.analyze()
        >>> scene = rev.get_scene_node()
        >>> grp = scene.children[0]
        >>> grp.notes = "example_value"

        """
        val = self._get_property("Notes")
        return val

    @notes.setter
    @min_aedt_version("2025.2")
    def notes(self, value: str) -> None:
        self._set_property("Notes", f"{value}")
