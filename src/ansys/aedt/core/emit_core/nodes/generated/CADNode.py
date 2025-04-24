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

from ..EmitNode import EmitNode


class CADNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def file(self) -> str:
        """File
        Name of the imported CAD file

        Value should be a full file path.
        """
        val = self._get_property("File")
        return val  # type: ignore

    class ModelTypeOption(Enum):
        PLATE = "Plate"  # eslint-disable-line no-eval
        BOX = "Box"  # eslint-disable-line no-eval
        DIHEDRAL = "Dihedral"  # eslint-disable-line no-eval
        TRIHEDRAL = "Trihedral"  # eslint-disable-line no-eval
        CYLINDER = "Cylinder"  # eslint-disable-line no-eval
        TAPERED_CYLINDER = "Tapered Cylinder"  # eslint-disable-line no-eval
        CONE = "Cone"  # eslint-disable-line no-eval
        SPHERE = "Sphere"  # eslint-disable-line no-eval
        ELLIPSOID = "Ellipsoid"  # eslint-disable-line no-eval
        CIRCULAR_PLATE = "Circular Plate"  # eslint-disable-line no-eval
        PARABOLA = "Parabola"  # eslint-disable-line no-eval
        PRISM = "Prism"  # eslint-disable-line no-eval
        TAPERED_PRISM = "Tapered Prism"  # eslint-disable-line no-eval
        TOPHAT = "Tophat"  # eslint-disable-line no-eval

    @property
    def model_type(self) -> ModelTypeOption:
        """Model Type
        Select type of parametric model to create

        """
        val = self._get_property("Model Type")
        val = self.ModelTypeOption[val]
        return val  # type: ignore

    @model_type.setter
    def model_type(self, value: ModelTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Model Type={value.value}"])

    @property
    def length(self) -> float:
        """Length
        Length of the model

        Value should be greater than 1e-06.
        """
        val = self._get_property("Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @length.setter
    def length(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Length={value}"])

    @property
    def width(self) -> float:
        """Width
        Width of the model

        Value should be greater than 1e-06.
        """
        val = self._get_property("Width")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @width.setter
    def width(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Width={value}"])

    @property
    def height(self) -> float:
        """Height
        Height of the model

        Value should be greater than 1e-06.
        """
        val = self._get_property("Height")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @height.setter
    def height(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Height={value}"])

    @property
    def angle(self) -> float:
        """Angle
        Angle (deg) between the plates

        Value should be between 0 and 360.
        """
        val = self._get_property("Angle")
        return val  # type: ignore

    @angle.setter
    def angle(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Angle={value}"])

    @property
    def top_side(self) -> float:
        """Top Side
        Side of the top of a equilateral triangular cylinder model

        Value should be greater than 0.
        """
        val = self._get_property("Top Side")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @top_side.setter
    def top_side(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Top Side={value}"])

    @property
    def top_radius(self) -> float:
        """Top Radius
        Radius of the top of a tapered cylinder model

        Value should be greater than 0.
        """
        val = self._get_property("Top Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @top_radius.setter
    def top_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Top Radius={value}"])

    @property
    def side(self) -> float:
        """Side
        Side of the equilateral triangular cylinder

        Value should be greater than 1e-06.
        """
        val = self._get_property("Side")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @side.setter
    def side(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Side={value}"])

    @property
    def radius(self) -> float:
        """Radius
        Radius of the sphere or cylinder

        Value should be greater than 1e-06.
        """
        val = self._get_property("Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @radius.setter
    def radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Radius={value}"])

    @property
    def base_radius(self) -> float:
        """Base Radius
        Radius of the base of a tophat model

        Value should be greater than 1e-06.
        """
        val = self._get_property("Base Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @base_radius.setter
    def base_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Base Radius={value}"])

    @property
    def center_radius(self) -> float:
        """Center Radius
        Radius of the raised portion of a tophat model

        Value should be greater than 1e-06.
        """
        val = self._get_property("Center Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @center_radius.setter
    def center_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Center Radius={value}"])

    @property
    def x_axis_ellipsoid_radius(self) -> float:
        """X Axis Ellipsoid Radius
        Ellipsoid semi-principal radius for the X axis

        Value should be greater than 1e-06.
        """
        val = self._get_property("X Axis Ellipsoid Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @x_axis_ellipsoid_radius.setter
    def x_axis_ellipsoid_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"X Axis Ellipsoid Radius={value}"])

    @property
    def y_axis_ellipsoid_radius(self) -> float:
        """Y Axis Ellipsoid Radius
        Ellipsoid semi-principal radius for the Y axis

        Value should be greater than 1e-06.
        """
        val = self._get_property("Y Axis Ellipsoid Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @y_axis_ellipsoid_radius.setter
    def y_axis_ellipsoid_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Y Axis Ellipsoid Radius={value}"])

    @property
    def z_axis_ellipsoid_radius(self) -> float:
        """Z Axis Ellipsoid Radius
        Ellipsoid semi-principal radius for the Z axis

        Value should be greater than 1e-06.
        """
        val = self._get_property("Z Axis Ellipsoid Radius")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @z_axis_ellipsoid_radius.setter
    def z_axis_ellipsoid_radius(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Z Axis Ellipsoid Radius={value}"])

    @property
    def focal_length(self) -> float:
        """Focal Length
        Focal length of a parabolic reflector (f = 1/4a where y=ax^2)

        Value should be greater than 1e-06.
        """
        val = self._get_property("Focal Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @focal_length.setter
    def focal_length(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Focal Length={value}"])

    @property
    def offset(self) -> float:
        """Offset
        Offset of parabolic reflector

        """
        val = self._get_property("Offset")
        val = self._convert_from_internal_units(float(val), "Length")
        return val  # type: ignore

    @offset.setter
    def offset(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Offset={value}"])

    @property
    def x_direction_taper(self) -> float:
        """X Direction Taper
        Amount (%) that the prism tapers in the X dimension from one end to the
         other

        Value should be greater than 0.
        """
        val = self._get_property("X Direction Taper")
        return val  # type: ignore

    @x_direction_taper.setter
    def x_direction_taper(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"X Direction Taper={value}"])

    @property
    def y_direction_taper(self) -> float:
        """Y Direction Taper
        Amount (%) that the prism tapers in the Y dimension from one end to the
         other

        Value should be greater than 0.
        """
        val = self._get_property("Y Direction Taper")
        return val  # type: ignore

    @y_direction_taper.setter
    def y_direction_taper(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Y Direction Taper={value}"])

    @property
    def prism_direction(self):
        """Prism Direction
        Direction vector between the center of the base and center of the top

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Prism Direction")
        return val  # type: ignore

    @prism_direction.setter
    def prism_direction(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Prism Direction={value}"])

    @property
    def closed_top(self) -> bool:
        """Closed Top
        Control whether the top of the model is closed

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Closed Top")
        return val  # type: ignore

    @closed_top.setter
    def closed_top(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Closed Top={value}"])

    @property
    def closed_base(self) -> bool:
        """Closed Base
        Control whether the base of the model is closed

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Closed Base")
        return val  # type: ignore

    @closed_base.setter
    def closed_base(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Closed Base={value}"])

    @property
    def mesh_density(self) -> int:
        """Mesh Density
        Unitless mesh density parameter where higher value improves mesh
         smoothness

        Value should be between 1 and 100.
        """
        val = self._get_property("Mesh Density")
        return val  # type: ignore

    @mesh_density.setter
    def mesh_density(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Mesh Density={value}"])

    @property
    def use_symmetric_mesh(self) -> bool:
        """Use Symmetric Mesh
        Convert quads to a symmetric triangle mesh by adding a center point (4
         triangles per quad instead of 2)

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Symmetric Mesh")
        return val  # type: ignore

    @use_symmetric_mesh.setter
    def use_symmetric_mesh(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Use Symmetric Mesh={value}"])

    class MeshOptionOption(Enum):
        IMPROVED = "Improved"  # eslint-disable-line no-eval
        LEGACY = "Legacy"  # eslint-disable-line no-eval

    @property
    def mesh_option(self) -> MeshOptionOption:
        """Mesh Option
        Select from different meshing options

        """
        val = self._get_property("Mesh Option")
        val = self.MeshOptionOption[val]
        return val  # type: ignore

    @mesh_option.setter
    def mesh_option(self, value: MeshOptionOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Mesh Option={value.value}"])

    @property
    def coating_index(self) -> int:
        """Coating Index
        Coating index for the parametric model primitive

        Value should be between 0 and 100000.
        """
        val = self._get_property("Coating Index")
        return val  # type: ignore

    @coating_index.setter
    def coating_index(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Coating Index={value}"])

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        Show CAD model node position and orientation in parent-node coords
         (False) or relative to placement coords (True)

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Relative Coordinates")
        return val  # type: ignore

    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, [f"Show Relative Coordinates={value}"]
        )

    @property
    def position(self):
        """Position
        Set position of the CAD node in parent-node coordinates

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Position")
        return val  # type: ignore

    @position.setter
    def position(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Position={value}"])

    @property
    def relative_position(self):
        """Relative Position
        Set position of the CAD model node relative to placement coordinates

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Relative Position")
        return val  # type: ignore

    @relative_position.setter
    def relative_position(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Relative Position={value}"])

    class OrientationModeOption(Enum):
        ROLL_PITCH_YAW = "Roll-Pitch-Yaw"  # eslint-disable-line no-eval
        AZ_EL_TWIST = "Az-El-Twist"  # eslint-disable-line no-eval

    @property
    def orientation_mode(self) -> OrientationModeOption:
        """Orientation Mode
        Select the convention (order of rotations) for configuring orientation

        """
        val = self._get_property("Orientation Mode")
        val = self.OrientationModeOption[val]
        return val  # type: ignore

    @orientation_mode.setter
    def orientation_mode(self, value: OrientationModeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Orientation Mode={value.value}"])

    @property
    def orientation(self):
        """Orientation
        Set orientation of the CAD node in parent-node coordinates

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Orientation")
        return val  # type: ignore

    @orientation.setter
    def orientation(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Orientation={value}"])

    @property
    def relative_orientation(self):
        """Relative Orientation
        Set orientation of the CAD model node relative to placement coordinates

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Relative Orientation")
        return val  # type: ignore

    @relative_orientation.setter
    def relative_orientation(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Relative Orientation={value}"])

    @property
    def visible(self) -> bool:
        """Visible
        Toggle (on/off) display of CAD model in 3-D window

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Visible")
        return val  # type: ignore

    @visible.setter
    def visible(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Visible={value}"])

    class RenderModeOption(Enum):
        FLAT_SHADED = "Flat-Shaded"  # eslint-disable-line no-eval
        WIRE_FRAME = "Wire-Frame"  # eslint-disable-line no-eval
        HIDDEN_WIRE_FRAME = "Hidden Wire-Frame"  # eslint-disable-line no-eval
        OUTLINE = "Outline"  # eslint-disable-line no-eval

    @property
    def render_mode(self) -> RenderModeOption:
        """Render Mode
        Select drawing style for surfaces

        """
        val = self._get_property("Render Mode")
        val = self.RenderModeOption[val]
        return val  # type: ignore

    @render_mode.setter
    def render_mode(self, value: RenderModeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Render Mode={value.value}"])

    @property
    def show_axes(self) -> bool:
        """Show Axes
        Toggle (on/off) display of CAD model coordinate axes in 3-D window

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Axes")
        return val  # type: ignore

    @show_axes.setter
    def show_axes(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Show Axes={value}"])

    @property
    def min(self):
        """Min
        Minimum x,y,z extents of CAD model in local coordinates

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Min")
        return val  # type: ignore

    @property
    def max(self):
        """Max
        Maximum x,y,z extents of CAD model in local coordinates

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Max")
        return val  # type: ignore

    @property
    def number_of_surfaces(self) -> int:
        """Number of Surfaces
        Number of surfaces in the model

        """
        val = self._get_property("Number of Surfaces")
        return val  # type: ignore

    @property
    def color(self):
        """Color
        Defines the CAD nodes color

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Color")
        return val  # type: ignore

    @color.setter
    def color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Color={value}"])

    @property
    def notes(self) -> str:
        """Notes
        Expand to view/edit notes stored with the project

        """
        val = self._get_property("Notes")
        return val  # type: ignore

    @notes.setter
    def notes(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Notes={value}"])
