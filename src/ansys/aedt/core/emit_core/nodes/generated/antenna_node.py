# -*- coding: utf-8 -*-
#
# Copyright(C) 2021 - 2025 ANSYS, Inc. and /or its affiliates.
# SPDX - License - Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
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
        self._set_property(f"Tags", f"{value}")

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates.

        Show antenna position and orientation in parent-node coords (False) or
        relative to placement coords (True).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Relative Coordinates")
        return (val == 'true')

    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value: bool):
        self._set_property(f"Show Relative Coordinates", f"{str(value).lower()}")

    @property
    def position(self):
        """Set position of the antenna in parent-node coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Position")
        return val

    @position.setter
    def position(self, value):
        self._set_property(f"Position", f"{value}")

    @property
    def relative_position(self):
        """Set position of the antenna relative to placement coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Relative Position")
        return val

    @relative_position.setter
    def relative_position(self, value):
        self._set_property(f"Relative Position", f"{value}")

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
        self._set_property(f"Orientation Mode", f"{value.value}")

    @property
    def orientation(self):
        """Set orientation of the antenna relative to parent-node coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Orientation")
        return val

    @orientation.setter
    def orientation(self, value):
        self._set_property(f"Orientation", f"{value}")

    @property
    def relative_orientation(self):
        """Set orientation of the antenna relative to placement coordinates.

        Value format is determined by 'Orientation Mode', in degrees and delimited by spaces.
        """
        val = self._get_property("Relative Orientation")
        return val

    @relative_orientation.setter
    def relative_orientation(self, value):
        self._set_property(f"Relative Orientation", f"{value}")

    @property
    def position_defined(self) -> bool:
        """Toggles on/off the ability to define a position for the antenna.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Position Defined")
        return (val == 'true')

    @position_defined.setter
    def position_defined(self, value: bool):
        self._set_property(f"Position Defined", f"{str(value).lower()}")

    @property
    def antenna_temperature(self) -> float:
        """Antenna noise temperature.

        Value should be between 0 and 100000.
        """
        val = self._get_property("Antenna Temperature")
        return float(val)

    @antenna_temperature.setter
    def antenna_temperature(self, value : float):
        self._set_property(f"Antenna Temperature", f"{value}")

    @property
    def type(self):
        """Defines the type of antenna."""
        val = self._get_property("Type")
        return val

    @type.setter
    def type(self, value):
        self._set_property(f"Type", f"{value}")

    @property
    def antenna_file(self) -> str:
        """Antenna File."""
        val = self._get_property("Antenna File")
        return val

    @antenna_file.setter
    def antenna_file(self, value: str):
        self._set_property(f"Antenna File", f"{value}")

    @property
    def project_name(self) -> str:
        """Name of imported HFSS Antenna project.

        Value should be a full file path.
        """
        val = self._get_property("Project Name")
        return val

    @project_name.setter
    def project_name(self, value: str):
        self._set_property(f"Project Name", f"{value}")

    @property
    def peak_gain(self) -> float:
        """Set peak gain of antenna (dBi).

        Value should be between -200 and 200.
        """
        val = self._get_property("Peak Gain")
        return float(val)

    @peak_gain.setter
    def peak_gain(self, value : float):
        self._set_property(f"Peak Gain", f"{value}")

    class BoresightOption(Enum):
        XAXIS = "+X Axis"
        YAXIS = "+Y Axis"
        ZAXIS = "+Z Axis"

    @property
    def boresight(self) -> BoresightOption:
        """Select peak beam direction in local coordinates."""
        val = self._get_property("Boresight")
        val = self.BoresightOption[val.upper()]
        return val

    @boresight.setter
    def boresight(self, value: BoresightOption):
        self._set_property(f"Boresight", f"{value.value}")

    @property
    def vertical_beamwidth(self) -> float:
        """Set half-power beamwidth in local-coordinates elevation plane.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("Vertical Beamwidth")
        return float(val)

    @vertical_beamwidth.setter
    def vertical_beamwidth(self, value : float):
        self._set_property(f"Vertical Beamwidth", f"{value}")

    @property
    def horizontal_beamwidth(self) -> float:
        """Set half-power beamwidth in local-coordinates azimuth plane.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("Horizontal Beamwidth")
        return float(val)

    @horizontal_beamwidth.setter
    def horizontal_beamwidth(self, value : float):
        self._set_property(f"Horizontal Beamwidth", f"{value}")

    @property
    def extra_sidelobe(self) -> bool:
        """Toggle (on/off) option to define two sidelobe levels.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Extra Sidelobe")
        return (val == 'true')

    @extra_sidelobe.setter
    def extra_sidelobe(self, value: bool):
        self._set_property(f"Extra Sidelobe", f"{str(value).lower()}")

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
    def first_sidelobe_level(self, value : float):
        self._set_property(f"First Sidelobe Level", f"{value}")

    @property
    def first_sidelobe_vert_bw(self) -> float:
        """Set beamwidth of first sidelobe beam in theta direction.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("First Sidelobe Vert. BW")
        return float(val)

    @first_sidelobe_vert_bw.setter
    def first_sidelobe_vert_bw(self, value : float):
        self._set_property(f"First Sidelobe Vert. BW", f"{value}")

    @property
    def first_sidelobe_hor_bw(self) -> float:
        """Set beamwidth of first sidelobe beam in phi direction.

        Value should be between 0.1 and 360.
        """
        val = self._get_property("First Sidelobe Hor. BW")
        return float(val)

    @first_sidelobe_hor_bw.setter
    def first_sidelobe_hor_bw(self, value : float):
        self._set_property(f"First Sidelobe Hor. BW", f"{value}")

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
    def outerbacklobe_level(self, value : float):
        self._set_property(f"Outer/Backlobe Level", f"{value}")

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
    def resonant_frequency(self, value : float|str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property(f"Resonant Frequency", f"{value}")

    @property
    def slot_length(self) -> float:
        """Set slot length of parametric slot.

        Value should be greater than 1e-6.
        """
        val = self._get_property("Slot Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @slot_length.setter
    def slot_length(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property(f"Slot Length", f"{value}")

    @property
    def mouth_width(self) -> float:
        """Set mouth width (along local y-axis) of the horn antenna.

        Value should be between 1e-6 and 100.
        """
        val = self._get_property("Mouth Width")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @mouth_width.setter
    def mouth_width(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property(f"Mouth Width", f"{value}")

    @property
    def mouth_height(self) -> float:
        """Set mouth height (along local x-axis) of the horn antenna.

        Value should be between 1e-6 and 100.
        """
        val = self._get_property("Mouth Height")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @mouth_height.setter
    def mouth_height(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property(f"Mouth Height", f"{value}")

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
    def waveguide_width(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property(f"Waveguide Width", f"{value}")

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
    def width_flare_half_angle(self, value : float):
        self._set_property(f"Width Flare Half-angle", f"{value}")

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
    def height_flare_half_angle(self, value : float):
        self._set_property(f"Height Flare Half-angle", f"{value}")

    @property
    def mouth_diameter(self) -> float:
        """Set aperture (mouth) diameter of horn antenna.

        Value should be between 1e-6 and 100.
        """
        val = self._get_property("Mouth Diameter")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @mouth_diameter.setter
    def mouth_diameter(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property(f"Mouth Diameter", f"{value}")

    @property
    def flare_half_angle(self) -> float:
        """Flare Half-angle.

        Set half-angle (degrees) of conical horn wall measured from boresight
        (z).

        Value should be between 1 and 89.9.
        """
        val = self._get_property("Flare Half-angle")
        return float(val)

    @flare_half_angle.setter
    def flare_half_angle(self, value : float):
        self._set_property(f"Flare Half-angle", f"{value}")

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
    def vswr(self, value : float):
        self._set_property(f"VSWR", f"{value}")

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
        self._set_property(f"Antenna Polarization", f"{value.value}")

    class CrossDipoleModeOption(Enum):
        FREESTANDING = "Freestanding"
        OVER_GROUND_PLANE = "Over Ground Plane"

    @property
    def cross_dipole_mode(self) -> CrossDipoleModeOption:
        """Choose the Cross Dipole type."""
        val = self._get_property("Cross Dipole Mode")
        val = self.CrossDipoleModeOption[val.upper()]
        return val

    @cross_dipole_mode.setter
    def cross_dipole_mode(self, value: CrossDipoleModeOption):
        self._set_property(f"Cross Dipole Mode", f"{value.value}")

    class CrossDipolePolarizationOption(Enum):
        RHCP = "RHCP"
        LHCP = "LHCP"

    @property
    def cross_dipole_polarization(self) -> CrossDipolePolarizationOption:
        """Choose local-coordinates polarization along boresight."""
        val = self._get_property("Cross Dipole Polarization")
        val = self.CrossDipolePolarizationOption[val.upper()]
        return val

    @cross_dipole_polarization.setter
    def cross_dipole_polarization(self, value: CrossDipolePolarizationOption):
        self._set_property(f"Cross Dipole Polarization", f"{value.value}")

    @property
    def override_height(self) -> bool:
        """Override Height.

        Ignores the default placement of quarter design wavelength over the
        ground plane.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Override Height")
        return (val == 'true')

    @override_height.setter
    def override_height(self, value: bool):
        self._set_property(f"Override Height", f"{str(value).lower()}")

    @property
    def offset_height(self) -> float:
        """Offset Height.

        Sets the offset height for the current sources above the ground plane.

        Value should be greater than 0.
        """
        val = self._get_property("Offset Height")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @offset_height.setter
    def offset_height(self, value : float|str):
        value = self._convert_to_internal_units(value, "Length")
        self._set_property(f"Offset Height", f"{value}")

    @property
    def auto_height_offset(self) -> bool:
        """Auto Height Offset.

        Switch on to automatically place slot current at sub-wavelength offset
        height above ground plane.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Auto Height Offset")
        return (val == 'true')

    @auto_height_offset.setter
    def auto_height_offset(self, value: bool):
        self._set_property(f"Auto Height Offset", f"{str(value).lower()}")

    @property
    def conform__adjust_antenna(self) -> bool:
        """Toggle (on/off) conformal adjustment for array antenna elements.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Conform / Adjust Antenna")
        return (val == 'true')

    @conform__adjust_antenna.setter
    def conform__adjust_antenna(self, value: bool):
        self._set_property(f"Conform / Adjust Antenna", f"{str(value).lower()}")

    @property
    def element_offset(self):
        """Element Offset.

        Set vector for shifting element positions in antenna local coordinates.

        Value should be x/y/z, delimited by spaces.
        """
        val = self._get_property("Element Offset")
        return val

    @element_offset.setter
    def element_offset(self, value):
        self._set_property(f"Element Offset", f"{value}")

    class ConformtoPlatformOption(Enum):
        NONE = "None"
        ALONG_NORMAL = "Along Normal"
        PERPENDICULAR_TO_PLANE = "Perpendicular to Plane"

    @property
    def conform_to_platform(self) -> ConformtoPlatformOption:
        """Select method of automated conforming applied after Element Offset."""
        val = self._get_property("Conform to Platform")
        val = self.ConformtoPlatformOption[val.upper()]
        return val

    @conform_to_platform.setter
    def conform_to_platform(self, value: ConformtoPlatformOption):
        self._set_property(f"Conform to Platform", f"{value.value}")

    class ReferencePlaneOption(Enum):
        XY_PLANE = "XY Plane"
        YZ_PLANE = "YZ Plane"
        ZX_PLANE = "ZX Plane"

    @property
    def reference_plane(self) -> ReferencePlaneOption:
        """Select reference plane for determining original element heights."""
        val = self._get_property("Reference Plane")
        val = self.ReferencePlaneOption[val.upper()]
        return val

    @reference_plane.setter
    def reference_plane(self, value: ReferencePlaneOption):
        self._set_property(f"Reference Plane", f"{value.value}")

    @property
    def conform_element_orientation(self) -> bool:
        """Conform Element Orientation.

        Toggle (on/off) re-orientation of elements to conform to curved
        placement surface.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Conform Element Orientation")
        return (val == 'true')

    @conform_element_orientation.setter
    def conform_element_orientation(self, value: bool):
        self._set_property(f"Conform Element Orientation", f"{str(value).lower()}")

    @property
    def show_axes(self) -> bool:
        """Toggle (on/off) display of antenna coordinate axes in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Axes")
        return (val == 'true')

    @show_axes.setter
    def show_axes(self, value: bool):
        self._set_property(f"Show Axes", f"{str(value).lower()}")

    @property
    def show_icon(self) -> bool:
        """Toggle (on/off) display of antenna marker (cone) in 3-D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Icon")
        return (val == 'true')

    @show_icon.setter
    def show_icon(self, value: bool):
        self._set_property(f"Show Icon", f"{str(value).lower()}")

    @property
    def size(self) -> float:
        """Adjust relative size of antenna marker (cone) in 3-D window.

        Value should be between 0.001 and 1.
        """
        val = self._get_property("Size")
        return float(val)

    @size.setter
    def size(self, value : float):
        self._set_property(f"Size", f"{value}")

    @property
    def color(self):
        """Set color of antenna marker (cone) in 3-D window.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Color")
        return val

    @color.setter
    def color(self, value):
        self._set_property(f"Color", f"{value}")

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
        return (val == 'true')

    @property
    def frequency_domain(self):
        """Frequency sample(s) defining antenna."""
        val = self._get_property("Frequency Domain")
        return val

    @property
    def number_of_electric_sources(self) -> int:
        """Number of freestanding electric current sources defining antenna."""
        val = self._get_property("Number of Electric Sources")
        return int(val)

    @property
    def number_of_magnetic_sources(self) -> int:
        """Number of freestanding magnetic current sources defining antenna."""
        val = self._get_property("Number of Magnetic Sources")
        return int(val)

    @property
    def number_of_imaged_electric_sources(self) -> int:
        """Number of Imaged Electric Sources.

        Number of imaged, half-space radiating electric current sources defining
        antenna.
        """
        val = self._get_property("Number of Imaged Electric Sources")
        return int(val)

    @property
    def number_of_imaged_magnetic_sources(self) -> int:
        """Number of Imaged Magnetic Sources.

        Number of imaged, half-space radiating magnetic current sources defining
        antenna.
        """
        val = self._get_property("Number of Imaged Magnetic Sources")
        return int(val)

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
    def aperture_cutoff_frequency(self) -> float:
        """Implied lowest operating frequency of conical horn antenna."""
        val = self._get_property("Aperture Cutoff Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    class SWEModeTruncationOption(Enum):
        DYNAMIC = "Dynamic"
        FIXED_CUSTOM = "Fixed (Custom)"
        NONE = "None"

    @property
    def swe_mode_truncation(self) -> SWEModeTruncationOption:
        """SWE Mode Truncation.

        Select the method for stability-enhancing truncation of spherical wave
        expansion terms.
        """
        val = self._get_property("SWE Mode Truncation")
        val = self.SWEModeTruncationOption[val.upper()]
        return val

    @swe_mode_truncation.setter
    def swe_mode_truncation(self, value: SWEModeTruncationOption):
        self._set_property(f"SWE Mode Truncation", f"{value.value}")

    @property
    def max_n_index(self) -> int:
        """Set maximum allowed index N for spherical wave expansion terms.

        Value should be greater than 1.
        """
        val = self._get_property("Max N Index")
        return int(val)

    @max_n_index.setter
    def max_n_index(self, value: int):
        self._set_property(f"Max N Index", f"{value}")

    @property
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project."""
        val = self._get_property("Notes")
        return val

    @notes.setter
    def notes(self, value: str):
        self._set_property(f"Notes", f"{value}")

    @property
    def show_composite_passband(self) -> bool:
        """Show plot instead of 3D window.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Composite Passband")
        return (val == 'true')

    @show_composite_passband.setter
    def show_composite_passband(self, value: bool):
        self._set_property(f"Show Composite Passband", f"{str(value).lower()}")

    @property
    def use_phase_center(self) -> bool:
        """Use the phase center defined in the HFSS design.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Use Phase Center")
        return (val == 'true')

    @use_phase_center.setter
    def use_phase_center(self, value: bool):
        self._set_property(f"Use Phase Center", f"{str(value).lower()}")

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

