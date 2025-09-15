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


class CADNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

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
    def file(self) -> str:
        """Name of the imported CAD file.

        Value should be a full file path.
        """
        val = self._get_property("File")
        return val

    class ModelTypeOption(Enum):
        PLATE = "Plate"
        BOX = "Box"
        DIHEDRAL = "Dihedral"
        TRIHEDRAL = "Trihedral"
        CYLINDER = "Cylinder"
        TAPERED_CYLINDER = "Tapered Cylinder"
        CONE = "Cone"
        SPHERE = "Sphere"
        ELLIPSOID = "Ellipsoid"
        CIRCULAR_PLATE = "Circular Plate"
        PARABOLA = "Parabola"
        PRISM = "Prism"
        TAPERED_PRISM = "Tapered Prism"
        TOPHAT = "Tophat"

    @property
    def model_type(self) -> ModelTypeOption:
        """Select type of parametric model to create."""
        val = self._get_property("Model Type")
        val = self.ModelTypeOption[val.upper()]
        return val

    @model_type.setter
    def model_type(self, value: ModelTypeOption):
        self._set_property("Model Type", f"{value.value}")

    @property
    def length(self) -> float:
        """Length of the model.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @length.setter
    def length(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Length", f"{value}")

    @property
    def width(self) -> float:
        """Width of the model.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Width")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @width.setter
    def width(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Width", f"{value}")

    @property
    def height(self) -> float:
        """Height of the model.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Height")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @height.setter
    def height(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Height", f"{value}")

    @property
    def angle(self) -> float:
        """Angle (deg) between the plates.

        Value should be between 0.0 and 360.0.
        """
        val = self._get_property("Angle")
        return float(val)

    @angle.setter
    def angle(self, value: float):
        self._set_property("Angle", f"{value}")

    @property
    def top_side(self) -> float:
        """Side of the top of a equilateral triangular cylinder model.

        Value should be greater than 0.0.
        """
        val = self._get_property("Top Side")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @top_side.setter
    def top_side(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Top Side", f"{value}")

    @property
    def top_radius(self) -> float:
        """Radius of the top of a tapered cylinder model.

        Value should be greater than 0.0.
        """
        val = self._get_property("Top Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @top_radius.setter
    def top_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Top Radius", f"{value}")

    @property
    def side(self) -> float:
        """Side of the equilateral triangular cylinder.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Side")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @side.setter
    def side(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Side", f"{value}")

    @property
    def radius(self) -> float:
        """Radius of the sphere or cylinder.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @radius.setter
    def radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Radius", f"{value}")

    @property
    def base_radius(self) -> float:
        """Radius of the base of a tophat model.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Base Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @base_radius.setter
    def base_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Base Radius", f"{value}")

    @property
    def center_radius(self) -> float:
        """Radius of the raised portion of a tophat model.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Center Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @center_radius.setter
    def center_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Center Radius", f"{value}")

    @property
    def x_axis_ellipsoid_radius(self) -> float:
        """Ellipsoid semi-principal radius for the X axis.

        Value should be greater than 0.000001.
        """
        val = self._get_property("X Axis Ellipsoid Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @x_axis_ellipsoid_radius.setter
    def x_axis_ellipsoid_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("X Axis Ellipsoid Radius", f"{value}")

    @property
    def y_axis_ellipsoid_radius(self) -> float:
        """Ellipsoid semi-principal radius for the Y axis.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Y Axis Ellipsoid Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @y_axis_ellipsoid_radius.setter
    def y_axis_ellipsoid_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Y Axis Ellipsoid Radius", f"{value}")

    @property
    def z_axis_ellipsoid_radius(self) -> float:
        """Ellipsoid semi-principal radius for the Z axis.

        Value should be greater than 0.000001.
        """
        val = self._get_property("Z Axis Ellipsoid Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @z_axis_ellipsoid_radius.setter
    def z_axis_ellipsoid_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Z Axis Ellipsoid Radius", f"{value}")

    @property
    def focal_length(self) -> float:
        """Focal length of a parabolic reflector (f = 1/4a where y=ax^2).

        Value should be greater than 0.000001.
        """
        val = self._get_property("Focal Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @focal_length.setter
    def focal_length(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Focal Length", f"{value}")

    @property
    def offset(self) -> float:
        """Offset of parabolic reflector."""
        val = self._get_property("Offset")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @offset.setter
    def offset(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Offset", f"{value}")

    @property
    def x_direction_taper(self) -> float:
        """X Direction Taper.

        Amount (%) that the prism tapers in the X dimension from one end to the
        other.

        Value should be greater than 0.0.
        """
        val = self._get_property("X Direction Taper")
        return float(val)

    @x_direction_taper.setter
    def x_direction_taper(self, value: float):
        self._set_property("X Direction Taper", f"{value}")

    @property
    def y_direction_taper(self) -> float:
        """Y Direction Taper.

        Amount (%) that the prism tapers in the Y dimension from one end to the
        other.

        Value should be greater than 0.0.
        """
        val = self._get_property("Y Direction Taper")
        return float(val)

    @y_direction_taper.setter
    def y_direction_taper(self, value: float):
        self._set_property("Y Direction Taper", f"{value}")

    @property
    def prism_direction(self):
        """Prism Direction.

        Direction vector between the center of the base and center of the top.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Prism Direction")
        return val

    @prism_direction.setter
    def prism_direction(self, value):
        self._set_property("Prism Direction", f"{value}")

    @property
    def closed_top(self) -> bool:
        """Control whether the top of the model is closed.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Closed Top")
        return val == "true"

    @closed_top.setter
    def closed_top(self, value: bool):
        self._set_property("Closed Top", f"{str(value).lower()}")

    @property
    def closed_base(self) -> bool:
        """Control whether the base of the model is closed.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Closed Base")
        return val == "true"

    @closed_base.setter
    def closed_base(self, value: bool):
        self._set_property("Closed Base", f"{str(value).lower()}")

    @property
    def mesh_density(self) -> int:
        """Mesh Density.

        Unitless mesh density parameter where higher value improves mesh
        smoothness.

        Value should be between 1 and 100.
        """
        val = self._get_property("Mesh Density")
        return int(val)

    @mesh_density.setter
    def mesh_density(self, value: int):
        self._set_property("Mesh Density", f"{value}")

    @property
    def use_symmetric_mesh(self) -> bool:
        """Use Symmetric Mesh.

        Convert quads to a symmetric triangle mesh by adding a center point (4
        triangles per quad instead of 2).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Symmetric Mesh")
        return val == "true"

    @use_symmetric_mesh.setter
    def use_symmetric_mesh(self, value: bool):
        self._set_property("Use Symmetric Mesh", f"{str(value).lower()}")

    class MeshOptionOption(Enum):
        IMPROVED = "Improved"
        LEGACY = "Legacy"

    @property
    def mesh_option(self) -> MeshOptionOption:
        """Select from different meshing options."""
        val = self._get_property("Mesh Option")
        val = self.MeshOptionOption[val.upper()]
        return val

    @mesh_option.setter
    def mesh_option(self, value: MeshOptionOption):
        self._set_property("Mesh Option", f"{value.value}")

    @property
    def coating_index(self) -> int:
        """Coating index for the parametric model primitive.

        Value should be between 0 and 100000.
        """
        val = self._get_property("Coating Index")
        return int(val)

    @coating_index.setter
    def coating_index(self, value: int):
        self._set_property("Coating Index", f"{value}")

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
        FLAT_SHADED = "Flat-Shaded"
        WIRE_FRAME = "Wire-Frame"
        HIDDEN_WIRE_FRAME = "Hidden Wire-Frame"
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
