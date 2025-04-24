from ..EmitNode import *

class ReadOnlyAntennaNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def tags(self) -> str:
        """Tags
        "Space delimited list of tags for coupling selections."
        "        """
        val = self._get_property('Tags')
        return val

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        "Show antenna position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Relative Coordinates')
        val = (val == 'true')
        return val

    @property
    def position(self):
        """Position
        "Set position of the antenna in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Position')
        return val

    @property
    def relative_position(self):
        """Relative Position
        "Set position of the antenna relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Relative Position')
        return val

    class OrientationModeOption(Enum):
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"

    @property
    def orientation_mode(self) -> OrientationModeOption:
        """Orientation Mode
        "Select the convention (order of rotations) for configuring orientation."
        "        """
        val = self._get_property('Orientation Mode')
        val = self.OrientationModeOption[val.upper()]
        return val

    @property
    def orientation(self):
        """Orientation
        "Set orientation of the antenna relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Orientation')
        return val

    @property
    def relative_orientation(self):
        """Relative Orientation
        "Set orientation of the antenna relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Relative Orientation')
        return val

    @property
    def position_defined(self) -> bool:
        """Position Defined
        "Toggles on/off the ability to define a position for the antenna."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Position Defined')
        val = (val == 'true')
        return val

    @property
    def antenna_temperature(self) -> float:
        """Antenna Temperature
        "Antenna noise temperature."
        "Value should be between 0 and 100000."
        """
        val = self._get_property('Antenna Temperature')
        return val

    @property
    def type(self):
        """Type
        "Defines the type of antenna."
        "        """
        val = self._get_property('Type')
        return val

    @property
    def antenna_file(self) -> str:
        """Antenna File
        "Value should be a full file path."
        """
        val = self._get_property('Antenna File')
        return val

    @property
    def project_name(self) -> str:
        """Project Name
        "Name of imported HFSS Antenna project."
        "Value should be a full file path."
        """
        val = self._get_property('Project Name')
        return val

    @property
    def peak_gain(self) -> float:
        """Peak Gain
        "Set peak gain of antenna (dBi)."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Peak Gain')
        return val

    class BoresightOption(Enum):
            XAXIS = "+X Axis"
            YAXIS = "+Y Axis"
            ZAXIS = "+Z Axis"

    @property
    def boresight(self) -> BoresightOption:
        """Boresight
        "Select peak beam direction in local coordinates."
        "        """
        val = self._get_property('Boresight')
        val = self.BoresightOption[val.upper()]
        return val

    @property
    def vertical_beamwidth(self) -> float:
        """Vertical Beamwidth
        "Set half-power beamwidth in local-coordinates elevation plane."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('Vertical Beamwidth')
        return val

    @property
    def horizontal_beamwidth(self) -> float:
        """Horizontal Beamwidth
        "Set half-power beamwidth in local-coordinates azimuth plane."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('Horizontal Beamwidth')
        return val

    @property
    def extra_sidelobe(self) -> bool:
        """Extra Sidelobe
        "Toggle (on/off) option to define two sidelobe levels."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Extra Sidelobe')
        val = (val == 'true')
        return val

    @property
    def first_sidelobe_level(self) -> float:
        """First Sidelobe Level
        "Set reduction in the gain of Directive Beam antenna for first sidelobe level."
        "Value should be between 0 and 200."
        """
        val = self._get_property('First Sidelobe Level')
        return val

    @property
    def first_sidelobe_vert_bw(self) -> float:
        """First Sidelobe Vert. BW
        "Set beamwidth of first sidelobe beam in theta direction."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('First Sidelobe Vert. BW')
        return val

    @property
    def first_sidelobe_hor_bw(self) -> float:
        """First Sidelobe Hor. BW
        "Set beamwidth of first sidelobe beam in phi direction."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('First Sidelobe Hor. BW')
        return val

    @property
    def outerbacklobe_level(self) -> float:
        """Outer/Backlobe Level
        "Set reduction in gain of Directive Beam antenna for outer/backlobe level."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Outer/Backlobe Level')
        return val

    @property
    def resonant_frequency(self) -> float:
        """Resonant Frequency
        "Set first resonant frequency of wire dipole, monopole, or parametric antenna."
        "Value should be between 1 and 1e+13."
        """
        val = self._get_property('Resonant Frequency')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def slot_length(self) -> float:
        """Slot Length
        "Set slot length of parametric slot."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Slot Length')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def mouth_width(self) -> float:
        """Mouth Width
        "Set mouth width (along local y-axis) of the horn antenna."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Mouth Width')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def mouth_height(self) -> float:
        """Mouth Height
        "Set mouth height (along local x-axis) of the horn antenna."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Mouth Height')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def waveguide_width(self) -> float:
        """Waveguide Width
        "Set waveguide width (along local y-axis) where flared horn walls meet the feed, determines cut-off frequency."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Waveguide Width')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def width_flare_half_angle(self) -> float:
        """Width Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local yz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        val = self._get_property('Width Flare Half-angle')
        return val

    @property
    def height_flare_half_angle(self) -> float:
        """Height Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local xz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        val = self._get_property('Height Flare Half-angle')
        return val

    @property
    def mouth_diameter(self) -> float:
        """Mouth Diameter
        "Set aperture (mouth) diameter of horn antenna."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Mouth Diameter')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def flare_half_angle(self) -> float:
        """Flare Half-angle
        "Set half-angle (degrees) of conical horn wall measured from boresight (z)."
        "Value should be between 1 and 89.9."
        """
        val = self._get_property('Flare Half-angle')
        return val

    @property
    def vswr(self) -> float:
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the antenna and the RF System (or outboard component)."
        "Value should be between 1 and 100."
        """
        val = self._get_property('VSWR')
        return val

    class AntennaPolarizationOption(Enum):
            VERTICAL = "Vertical"
            HORIZONTAL = "Horizontal"
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def antenna_polarization(self) -> AntennaPolarizationOption:
        """Antenna Polarization
        "Choose local-coordinates polarization along boresight."
        "        """
        val = self._get_property('Antenna Polarization')
        val = self.AntennaPolarizationOption[val.upper()]
        return val

    class CrossDipoleModeOption(Enum):
            FREESTANDING = "Freestanding"
            OVER_GROUND_PLANE = "Over Ground Plane"

    @property
    def cross_dipole_mode(self) -> CrossDipoleModeOption:
        """Cross Dipole Mode
        "Choose the Cross Dipole type."
        "        """
        val = self._get_property('Cross Dipole Mode')
        val = self.CrossDipoleModeOption[val.upper()]
        return val

    class CrossDipolePolarizationOption(Enum):
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def cross_dipole_polarization(self) -> CrossDipolePolarizationOption:
        """Cross Dipole Polarization
        "Choose local-coordinates polarization along boresight."
        "        """
        val = self._get_property('Cross Dipole Polarization')
        val = self.CrossDipolePolarizationOption[val.upper()]
        return val

    @property
    def override_height(self) -> bool:
        """Override Height
        "Ignores the default placement of quarter design wavelength over the ground plane."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Override Height')
        val = (val == 'true')
        return val

    @property
    def offset_height(self) -> float:
        """Offset Height
        "Sets the offset height for the current sources above the ground plane."
        "Value should be greater than 0."
        """
        val = self._get_property('Offset Height')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def auto_height_offset(self) -> bool:
        """Auto Height Offset
        "Switch on to automatically place slot current at sub-wavelength offset height above ground plane."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Auto Height Offset')
        val = (val == 'true')
        return val

    @property
    def conform__adjust_antenna(self) -> bool:
        """Conform / Adjust Antenna
        "Toggle (on/off) conformal adjustment for array antenna elements."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Conform / Adjust Antenna')
        val = (val == 'true')
        return val

    @property
    def element_offset(self):
        """Element Offset
        "Set vector for shifting element positions in antenna local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Element Offset')
        return val

    class ConformtoPlatformOption(Enum):
            NONE = "None"
            ALONG_NORMAL = "Along Normal"
            PERPENDICULAR_TO_PLANE = "Perpendicular to Plane"

    @property
    def conform_to_platform(self) -> ConformtoPlatformOption:
        """Conform to Platform
        "Select method of automated conforming applied after Element Offset."
        "        """
        val = self._get_property('Conform to Platform')
        val = self.ConformtoPlatformOption[val.upper()]
        return val

    class ReferencePlaneOption(Enum):
            XY_PLANE = "XY Plane"
            YZ_PLANE = "YZ Plane"
            ZX_PLANE = "ZX Plane"

    @property
    def reference_plane(self) -> ReferencePlaneOption:
        """Reference Plane
        "Select reference plane for determining original element heights."
        "        """
        val = self._get_property('Reference Plane')
        val = self.ReferencePlaneOption[val.upper()]
        return val

    @property
    def conform_element_orientation(self) -> bool:
        """Conform Element Orientation
        "Toggle (on/off) re-orientation of elements to conform to curved placement surface."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Conform Element Orientation')
        val = (val == 'true')
        return val

    @property
    def show_axes(self) -> bool:
        """Show Axes
        "Toggle (on/off) display of antenna coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Axes')
        val = (val == 'true')
        return val

    @property
    def show_icon(self) -> bool:
        """Show Icon
        "Toggle (on/off) display of antenna marker (cone) in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Icon')
        val = (val == 'true')
        return val

    @property
    def size(self) -> float:
        """Size
        "Adjust relative size of antenna marker (cone) in 3-D window."
        "Value should be between 0.001 and 1."
        """
        val = self._get_property('Size')
        return val

    @property
    def color(self):
        """Color
        "Set color of antenna marker (cone) in 3-D window."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Color')
        return val

    @property
    def el_sample_interval(self) -> float:
        """El Sample Interval
        "Space between elevation-angle samples of pattern."
        "        """
        val = self._get_property('El Sample Interval')
        return val

    @property
    def az_sample_interval(self) -> float:
        """Az Sample Interval
        "Space between azimuth-angle samples of pattern."
        "        """
        val = self._get_property('Az Sample Interval')
        return val

    @property
    def has_frequency_domain(self) -> bool:
        """Has Frequency Domain
        "False if antenna can be used at any frequency."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Has Frequency Domain')
        val = (val == 'true')
        return val

    @property
    def frequency_domain(self):
        """Frequency Domain
        "Frequency sample(s) defining antenna."
        "        """
        val = self._get_property('Frequency Domain')
        return val

    @property
    def number_of_electric_sources(self) -> int:
        """Number of Electric Sources
        "Number of freestanding electric current sources defining antenna."
        "        """
        val = self._get_property('Number of Electric Sources')
        return val

    @property
    def number_of_magnetic_sources(self) -> int:
        """Number of Magnetic Sources
        "Number of freestanding magnetic current sources defining antenna."
        "        """
        val = self._get_property('Number of Magnetic Sources')
        return val

    @property
    def number_of_imaged_electric_sources(self) -> int:
        """Number of Imaged Electric Sources
        "Number of imaged, half-space radiating electric current sources defining antenna."
        "        """
        val = self._get_property('Number of Imaged Electric Sources')
        return val

    @property
    def number_of_imaged_magnetic_sources(self) -> int:
        """Number of Imaged Magnetic Sources
        "Number of imaged, half-space radiating magnetic current sources defining antenna."
        "        """
        val = self._get_property('Number of Imaged Magnetic Sources')
        return val

    @property
    def waveguide_height(self) -> float:
        """Waveguide Height
        "Implied waveguide height (along local x-axis) where the flared horn walls meet the feed."
        "        """
        val = self._get_property('Waveguide Height')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

    @property
    def waveguide_cutoff_frequency(self) -> float:
        """Waveguide Cutoff Frequency
        "Implied lowest operating frequency of pyramidal horn antenna."
        "        """
        val = self._get_property('Waveguide Cutoff Frequency')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def aperture_cutoff_frequency(self) -> float:
        """Aperture Cutoff Frequency
        "Implied lowest operating frequency of conical horn antenna."
        "        """
        val = self._get_property('Aperture Cutoff Frequency')
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    class SWEModeTruncationOption(Enum):
            DYNAMIC = "Dynamic"
            CUSTOM = "Fixed (Custom)"
            NONE = "None"

    @property
    def swe_mode_truncation(self) -> SWEModeTruncationOption:
        """SWE Mode Truncation
        "Select the method for stability-enhancing truncation of spherical wave expansion terms."
        "        """
        val = self._get_property('SWE Mode Truncation')
        val = self.SWEModeTruncationOption[val.upper()]
        return val

    @property
    def max_n_index(self) -> int:
        """Max N Index
        "Set maximum allowed index N for spherical wave expansion terms."
        "Value should be greater than 1."
        """
        val = self._get_property('Max N Index')
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    @property
    def show_composite_passband(self) -> bool:
        """Show Composite Passband
        "Show plot instead of 3D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Composite Passband')
        val = (val == 'true')
        return val

    @property
    def use_phase_center(self) -> bool:
        """Use Phase Center
        "Use the phase center defined in the HFSS design."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Phase Center')
        val = (val == 'true')
        return val

    @property
    def coordinate_systems(self) -> str:
        """Coordinate Systems
        "Specifies the coordinate system for the phase center of this antenna."
        "        """
        val = self._get_property('Coordinate Systems')
        return val

    @property
    def phasecenterposition(self):
        """PhaseCenterPosition
        "Set position of the antennas linked coordinate system.."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('PhaseCenterPosition')
        return val

    @property
    def phasecenterorientation(self):
        """PhaseCenterOrientation
        "Set orientation of the antennas linked coordinate system.."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('PhaseCenterOrientation')
        return val

