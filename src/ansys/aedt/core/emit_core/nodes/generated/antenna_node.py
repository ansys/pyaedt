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


class AntennaNode(EmitNode):
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

    def add_antenna_passband(self):
        """Add a New Passband to this Antenna"""
        return self._add_child_node("Antenna Passband")

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
    def tags(self) -> str:
        """Space delimited list of tags for coupling selections."""
        val = self._get_property("Tags")
        return val

    @tags.setter
    def tags(self, value: str):
        self._set_property("Tags", f"{value}")

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates.

        Show antenna position and orientation in parent-node coords (False) or
        relative to placement coords (True).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Relative Coordinates")
        return val == "true"

    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value: bool):
        self._set_property("Show Relative Coordinates", f"{str(value).lower()}")

    @property
    def position(self):
        """Set position of the antenna in parent-node coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Position")
        return val

    @position.setter
    def position(self, value):
        self._set_property("Position", f"{value}")

    @property
    def relative_position(self):
        """Set position of the antenna relative to placement coordinates.

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
        """Set orientation of the antenna relative to parent-node coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Orientation")
        return val

    @orientation.setter
    def orientation(self, value):
        self._set_property("Orientation", f"{value}")

    @property
    def relative_orientation(self):
        """Set orientation of the antenna relative to placement coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Relative Orientation")
        return val

    @relative_orientation.setter
    def relative_orientation(self, value):
        self._set_property("Relative Orientation", f"{value}")

    @property
    def position_defined(self) -> bool:
        """Toggles on/off the ability to define a position for the antenna.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Position Defined")
        return val == "true"

    @position_defined.setter
    def position_defined(self, value: bool):
        self._set_property("Position Defined", f"{str(value).lower()}")

    @property
    def antenna_temperature(self) -> float:
        """Antenna noise temperature.

        Value should be between 0 and 100000.
        """
        val = self._get_property("Antenna Temperature")
        return float(val)

    @antenna_temperature.setter
    def antenna_temperature(self, value: float):
        self._set_property("Antenna Temperature", f"{value}")

    class TypeOption(Enum):
        ISOTROPIC = "Isotropic"
        BY_FILE = "By File"
        HEMITROPIC = "Hemitropic"
        SHORT_DIPOLE = "Short Dipole"
        HALF_WAVE_DIPOLE = "Half-wave Dipole"
        QUARTER_WAVE_MONOPOLE = "Quarter-wave Monopole"
        WIRE_DIPOLE = "Wire Dipole"
        WIRE_MONOPOLE = "Wire Monopole"
        SMALL_LOOP = "Small Loop"
        DIRECTIVE_BEAM = "Directive Beam"
        PYRAMIDAL_HORN = "Pyramidal Horn"

    @property
    def type(self) -> TypeOption:
        """Defines the type of antenna."""
        val = self._get_property("Type")
        val = self.TypeOption[val.upper()]
        return val

    @type.setter
    def type(self, value: TypeOption):
        self._set_property("Type", f"{value.value}")

    @property
    def antenna_file(self) -> str:
        """Antenna File."""
        val = self._get_property("Antenna File")
        return val

    @antenna_file.setter
    def antenna_file(self, value: str):
        self._set_property("Antenna File", f"{value}")

    @property
    def project_name(self) -> str:
        """Name of imported HFSS Antenna project.

        Value should be a full file path.
        """
        val = self._get_property("Project Name")
        return val

    @project_name.setter
    def project_name(self, value: str):
        self._set_property("Project Name", f"{value}")

    @property
    def peak_gain(self) -> float:
        """Set peak gain of antenna (dBi).

        Value should be between -200 and 200.
        """
        val = self._get_property("Peak Gain")
        return float(val)

    @peak_gain.setter
    def peak_gain(self, value: float):
        self._set_property("Peak Gain", f"{value}")

    @property
    def vertical_beamwidth(self) -> float:
        """Set half-power beamwidth in local-coordinates elevation plane.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("Vertical Beamwidth")
        return float(val)

    @vertical_beamwidth.setter
    def vertical_beamwidth(self, value: float):
        self._set_property("Vertical Beamwidth", f"{value}")

    @property
    def horizontal_beamwidth(self) -> float:
        """Set half-power beamwidth in local-coordinates azimuth plane.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("Horizontal Beamwidth")
        return float(val)

    @horizontal_beamwidth.setter
    def horizontal_beamwidth(self, value: float):
        self._set_property("Horizontal Beamwidth", f"{value}")

    @property
    def extra_sidelobe(self) -> bool:
        """Toggle (on/off) option to define two sidelobe levels.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Extra Sidelobe")
        return val == "true"

    @extra_sidelobe.setter
    def extra_sidelobe(self, value: bool):
        self._set_property("Extra Sidelobe", f"{str(value).lower()}")

    @property
    def first_sidelobe_level(self) -> float:
        """First Sidelobe Level.

        Set reduction in the gain of Directive Beam antenna for first sidelobe
        level.

        Value should be between 0 and 200.
        """
        val = self._get_property("First Sidelobe Level")
        return float(val)

    @first_sidelobe_level.setter
    def first_sidelobe_level(self, value: float):
        self._set_property("First Sidelobe Level", f"{value}")

    @property
    def first_sidelobe_vert_bw(self) -> float:
        """Set beamwidth of first sidelobe beam in theta direction.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("First Sidelobe Vert. BW")
        return float(val)

    @first_sidelobe_vert_bw.setter
    def first_sidelobe_vert_bw(self, value: float):
        self._set_property("First Sidelobe Vert. BW", f"{value}")

    @property
    def first_sidelobe_hor_bw(self) -> float:
        """Set beamwidth of first sidelobe beam in phi direction.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("First Sidelobe Hor. BW")
        return float(val)

    @first_sidelobe_hor_bw.setter
    def first_sidelobe_hor_bw(self, value: float):
        self._set_property("First Sidelobe Hor. BW", f"{value}")

    @property
    def outerbacklobe_level(self) -> float:
        """Outer/Backlobe Level.

        Set reduction in gain of Directive Beam antenna for outer/backlobe
        level.

        Value should be between 0 and 200.
        """
        val = self._get_property("Outer/Backlobe Level")
        return float(val)

    @outerbacklobe_level.setter
    def outerbacklobe_level(self, value: float):
        self._set_property("Outer/Backlobe Level", f"{value}")

    @property
    def resonant_frequency(self) -> float:
        """Resonant Frequency.

        Set first resonant frequency of wire dipole, monopole, or parametric
        antenna.

        Value should be between 1.0 and 1e13.
        """
        val = self._get_property("Resonant Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @resonant_frequency.setter
    def resonant_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Resonant Frequency", f"{value}")

    @property
    def mouth_width(self) -> float:
        """Set mouth width (along local y-axis) of the horn antenna.

        Value should be between 1e-6 and 100.
        """
        val = self._get_property("Mouth Width")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @mouth_width.setter
    def mouth_width(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Mouth Width", f"{value}")

    @property
    def mouth_height(self) -> float:
        """Set mouth height (along local x-axis) of the horn antenna.

        Value should be between 1e-6 and 100.
        """
        val = self._get_property("Mouth Height")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @mouth_height.setter
    def mouth_height(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Mouth Height", f"{value}")

    @property
    def waveguide_width(self) -> float:
        """Waveguide Width.

        Set waveguide width (along local y-axis) where flared horn walls meet
        the feed, determines cut-off frequency.

        Value should be between 1e-6 and 100.
        """
        val = self._get_property("Waveguide Width")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @waveguide_width.setter
    def waveguide_width(self, value: float | str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Waveguide Width", f"{value}")

    @property
    def width_flare_half_angle(self) -> float:
        """Width Flare Half-angle.

        Set half-angle (degrees) of flared horn walls measured in local yz-plane
        from boresight (z) axis to either wall.

        Value should be between 1 and 89.9.
        """
        val = self._get_property("Width Flare Half-angle")
        return float(val)

    @width_flare_half_angle.setter
    def width_flare_half_angle(self, value: float):
        self._set_property("Width Flare Half-angle", f"{value}")

    @property
    def height_flare_half_angle(self) -> float:
        """Height Flare Half-angle.

        Set half-angle (degrees) of flared horn walls measured in local xz-plane
        from boresight (z) axis to either wall.

        Value should be between 1 and 89.9.
        """
        val = self._get_property("Height Flare Half-angle")
        return float(val)

    @height_flare_half_angle.setter
    def height_flare_half_angle(self, value: float):
        self._set_property("Height Flare Half-angle", f"{value}")

    @property
    def vswr(self) -> float:
        """VSWR.

        The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch
        between the antenna and the RF System (or outboard component).

        Value should be between 1 and 100.
        """
        val = self._get_property("VSWR")
        return float(val)

    @vswr.setter
    def vswr(self, value: float):
        self._set_property("VSWR", f"{value}")

    class AntennaPolarizationOption(Enum):
        VERTICAL = "Vertical"
        HORIZONTAL = "Horizontal"
        RHCP = "RHCP"
        LHCP = "LHCP"

    @property
    def antenna_polarization(self) -> AntennaPolarizationOption:
        """Choose local-coordinates polarization along boresight."""
        val = self._get_property("Antenna Polarization")
        val = self.AntennaPolarizationOption[val.upper()]
        return val

    @antenna_polarization.setter
    def antenna_polarization(self, value: AntennaPolarizationOption):
        self._set_property("Antenna Polarization", f"{value.value}")

    @property
    def show_axes(self) -> bool:
        """Toggle (on/off) display of antenna coordinate axes in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Axes")
        return val == "true"

    @show_axes.setter
    def show_axes(self, value: bool):
        self._set_property("Show Axes", f"{str(value).lower()}")

    @property
    def show_icon(self) -> bool:
        """Toggle (on/off) display of antenna marker (cone) in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Icon")
        return val == "true"

    @show_icon.setter
    def show_icon(self, value: bool):
        self._set_property("Show Icon", f"{str(value).lower()}")

    @property
    def size(self) -> float:
        """Adjust relative size of antenna marker (cone) in 3-D window.

        Value should be between 0.001 and 1.
        """
        val = self._get_property("Size")
        return float(val)

    @size.setter
    def size(self, value: float):
        self._set_property("Size", f"{value}")

    @property
    def color(self):
        """Set color of antenna marker (cone) in 3-D window.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Color")
        return val

    @color.setter
    def color(self, value):
        self._set_property("Color", f"{value}")

    @property
    def el_sample_interval(self) -> float:
        """Space between elevation-angle samples of pattern."""
        val = self._get_property("El Sample Interval")
        return float(val)

    @property
    def az_sample_interval(self) -> float:
        """Space between azimuth-angle samples of pattern."""
        val = self._get_property("Az Sample Interval")
        return float(val)

    @property
    def has_frequency_domain(self) -> bool:
        """False if antenna can be used at any frequency.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Has Frequency Domain")
        return val == "true"

    @property
    def frequency_domain(self):
        """Frequency sample(s) defining antenna."""
        val = self._get_property("Frequency Domain")
        return val

    @property
    def waveguide_height(self) -> float:
        """Waveguide Height.

        Implied waveguide height (along local x-axis) where the flared horn
        walls meet the feed.
        """
        val = self._get_property("Waveguide Height")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @property
    def waveguide_cutoff_frequency(self) -> float:
        """Implied lowest operating frequency of pyramidal horn antenna."""
        val = self._get_property("Waveguide Cutoff Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._set_property("Notes", f"{value}")

    @property
    def show_composite_passband(self) -> bool:
        """Show plot instead of 3D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Composite Passband")
        return val == "true"

    @show_composite_passband.setter
    def show_composite_passband(self, value: bool):
        self._set_property("Show Composite Passband", f"{str(value).lower()}")

    @property
    def use_phase_center(self) -> bool:
        """Use the phase center defined in the HFSS design.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Phase Center")
        return val == "true"

    @use_phase_center.setter
    def use_phase_center(self, value: bool):
        self._set_property("Use Phase Center", f"{str(value).lower()}")

    @property
    def coordinate_systems(self) -> str:
        """Coordinate Systems.

        Specifies the coordinate system for the phase center of this antenna.
        """
        val = self._get_property("Coordinate Systems")
        return val

    @property
    def phasecenterposition(self):
        """Set position of the antennas linked coordinate system.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("PhaseCenterPosition")
        return val

    @property
    def phasecenterorientation(self):
        """Set orientation of the antennas linked coordinate system.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("PhaseCenterOrientation")
        return val
