from ..EmitNode import *

class AntennaNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def add_antenna_passband(self):
        """Add a New Passband to this Antenna"""
        return self._add_child_node("Antenna Passband")

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
    def tags(self) -> str:
        """Tags
        "Space delimited list of tags for coupling selections."
        "        """
        val = self._get_property('Tags')
        return val

    @tags.setter
    def tags(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Tags=' + value])

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        "Show antenna position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Relative Coordinates')
        return val

    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Relative Coordinates=' + value])

    @property
    def position(self):
        """Position
        "Set position of the antenna in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Position')
        return val

    @position.setter
    def position(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def relative_position(self):
        """Relative Position
        "Set position of the antenna relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Relative Position')
        return val

    @relative_position.setter
    def relative_position(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Relative Position=' + value])

    class OrientationModeOption(Enum):
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"

    @property
    def orientation_mode(self) -> OrientationModeOption:
        """Orientation Mode
        "Select the convention (order of rotations) for configuring orientation."
        "        """
        val = self._get_property('Orientation Mode')
        val = self.OrientationModeOption[val]
        return val

    @orientation_mode.setter
    def orientation_mode(self, value: OrientationModeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation Mode=' + value.value])

    @property
    def orientation(self):
        """Orientation
        "Set orientation of the antenna relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Orientation')
        return val

    @orientation.setter
    def orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation=' + value])

    @property
    def relative_orientation(self):
        """Relative Orientation
        "Set orientation of the antenna relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Relative Orientation')
        return val

    @relative_orientation.setter
    def relative_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Relative Orientation=' + value])

    @property
    def position_defined(self) -> bool:
        """Position Defined
        "Toggles on/off the ability to define a position for the antenna."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Position Defined')
        return val

    @position_defined.setter
    def position_defined(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position Defined=' + value])

    @property
    def antenna_temperature(self) -> float:
        """Antenna Temperature
        "Antenna noise temperature."
        "Value should be between 0 and 100000."
        """
        val = self._get_property('Antenna Temperature')
        return val

    @antenna_temperature.setter
    def antenna_temperature(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna Temperature=' + value])

    @property
    def type(self):
        """Type
        "Defines the type of antenna."
        "        """
        val = self._get_property('Type')
        return val

    @type.setter
    def type(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Type=' + value])

    @property
    def antenna_file(self) -> str:
        """Antenna File
        "Value should be a full file path."
        """
        val = self._get_property('Antenna File')
        return val

    @antenna_file.setter
    def antenna_file(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna File=' + value])

    @property
    def project_name(self) -> str:
        """Project Name
        "Name of imported HFSS Antenna project."
        "Value should be a full file path."
        """
        val = self._get_property('Project Name')
        return val

    @project_name.setter
    def project_name(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Project Name=' + value])

    @property
    def peak_gain(self) -> float:
        """Peak Gain
        "Set peak gain of antenna (dBi)."
        "Value should be between -200 and 200."
        """
        val = self._get_property('Peak Gain')
        return val

    @peak_gain.setter
    def peak_gain(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Peak Gain=' + value])

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
        val = self.BoresightOption[val]
        return val

    @boresight.setter
    def boresight(self, value: BoresightOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Boresight=' + value.value])

    @property
    def vertical_beamwidth(self) -> float:
        """Vertical Beamwidth
        "Set half-power beamwidth in local-coordinates elevation plane."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('Vertical Beamwidth')
        return val

    @vertical_beamwidth.setter
    def vertical_beamwidth(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Vertical Beamwidth=' + value])

    @property
    def horizontal_beamwidth(self) -> float:
        """Horizontal Beamwidth
        "Set half-power beamwidth in local-coordinates azimuth plane."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('Horizontal Beamwidth')
        return val

    @horizontal_beamwidth.setter
    def horizontal_beamwidth(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Horizontal Beamwidth=' + value])

    @property
    def extra_sidelobe(self) -> bool:
        """Extra Sidelobe
        "Toggle (on/off) option to define two sidelobe levels."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Extra Sidelobe')
        return val

    @extra_sidelobe.setter
    def extra_sidelobe(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Extra Sidelobe=' + value])

    @property
    def first_sidelobe_level(self) -> float:
        """First Sidelobe Level
        "Set reduction in the gain of Directive Beam antenna for first sidelobe level."
        "Value should be between 0 and 200."
        """
        val = self._get_property('First Sidelobe Level')
        return val

    @first_sidelobe_level.setter
    def first_sidelobe_level(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['First Sidelobe Level=' + value])

    @property
    def first_sidelobe_vert_bw(self) -> float:
        """First Sidelobe Vert. BW
        "Set beamwidth of first sidelobe beam in theta direction."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('First Sidelobe Vert. BW')
        return val

    @first_sidelobe_vert_bw.setter
    def first_sidelobe_vert_bw(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['First Sidelobe Vert. BW=' + value])

    @property
    def first_sidelobe_hor_bw(self) -> float:
        """First Sidelobe Hor. BW
        "Set beamwidth of first sidelobe beam in phi direction."
        "Value should be between 0.1 and 360."
        """
        val = self._get_property('First Sidelobe Hor. BW')
        return val

    @first_sidelobe_hor_bw.setter
    def first_sidelobe_hor_bw(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['First Sidelobe Hor. BW=' + value])

    @property
    def outerbacklobe_level(self) -> float:
        """Outer/Backlobe Level
        "Set reduction in gain of Directive Beam antenna for outer/backlobe level."
        "Value should be between 0 and 200."
        """
        val = self._get_property('Outer/Backlobe Level')
        return val

    @outerbacklobe_level.setter
    def outerbacklobe_level(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Outer/Backlobe Level=' + value])

    @property
    def resonant_frequency(self) -> float:
        """Resonant Frequency
        "Set first resonant frequency of wire dipole, monopole, or parametric antenna."
        "Value should be between 1 and 1e+13."
        """
        val = self._get_property('Resonant Frequency')
        return val

    @resonant_frequency.setter
    def resonant_frequency(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Resonant Frequency=' + value])

    @property
    def slot_length(self) -> float:
        """Slot Length
        "Set slot length of parametric slot."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Slot Length')
        return val

    @slot_length.setter
    def slot_length(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Slot Length=' + value])

    @property
    def mouth_width(self) -> float:
        """Mouth Width
        "Set mouth width (along local y-axis) of the horn antenna."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Mouth Width')
        return val

    @mouth_width.setter
    def mouth_width(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Mouth Width=' + value])

    @property
    def mouth_height(self) -> float:
        """Mouth Height
        "Set mouth height (along local x-axis) of the horn antenna."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Mouth Height')
        return val

    @mouth_height.setter
    def mouth_height(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Mouth Height=' + value])

    @property
    def waveguide_width(self) -> float:
        """Waveguide Width
        "Set waveguide width (along local y-axis) where flared horn walls meet the feed, determines cut-off frequency."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Waveguide Width')
        return val

    @waveguide_width.setter
    def waveguide_width(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Waveguide Width=' + value])

    @property
    def width_flare_half_angle(self) -> float:
        """Width Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local yz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        val = self._get_property('Width Flare Half-angle')
        return val

    @width_flare_half_angle.setter
    def width_flare_half_angle(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Width Flare Half-angle=' + value])

    @property
    def height_flare_half_angle(self) -> float:
        """Height Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local xz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        val = self._get_property('Height Flare Half-angle')
        return val

    @height_flare_half_angle.setter
    def height_flare_half_angle(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Height Flare Half-angle=' + value])

    @property
    def mouth_diameter(self) -> float:
        """Mouth Diameter
        "Set aperture (mouth) diameter of horn antenna."
        "Value should be between 1e-06 and 100."
        """
        val = self._get_property('Mouth Diameter')
        return val

    @mouth_diameter.setter
    def mouth_diameter(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Mouth Diameter=' + value])

    @property
    def flare_half_angle(self) -> float:
        """Flare Half-angle
        "Set half-angle (degrees) of conical horn wall measured from boresight (z)."
        "Value should be between 1 and 89.9."
        """
        val = self._get_property('Flare Half-angle')
        return val

    @flare_half_angle.setter
    def flare_half_angle(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Flare Half-angle=' + value])

    @property
    def vswr(self) -> float:
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the antenna and the RF System (or outboard component)."
        "Value should be between 1 and 100."
        """
        val = self._get_property('VSWR')
        return val

    @vswr.setter
    def vswr(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['VSWR=' + value])

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
        val = self.AntennaPolarizationOption[val]
        return val

    @antenna_polarization.setter
    def antenna_polarization(self, value: AntennaPolarizationOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna Polarization=' + value.value])

    class CrossDipoleModeOption(Enum):
            FREESTANDING = "Freestanding"
            OVER_GROUND_PLANE = "Over Ground Plane"

    @property
    def cross_dipole_mode(self) -> CrossDipoleModeOption:
        """Cross Dipole Mode
        "Choose the Cross Dipole type."
        "        """
        val = self._get_property('Cross Dipole Mode')
        val = self.CrossDipoleModeOption[val]
        return val

    @cross_dipole_mode.setter
    def cross_dipole_mode(self, value: CrossDipoleModeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Cross Dipole Mode=' + value.value])

    class CrossDipolePolarizationOption(Enum):
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def cross_dipole_polarization(self) -> CrossDipolePolarizationOption:
        """Cross Dipole Polarization
        "Choose local-coordinates polarization along boresight."
        "        """
        val = self._get_property('Cross Dipole Polarization')
        val = self.CrossDipolePolarizationOption[val]
        return val

    @cross_dipole_polarization.setter
    def cross_dipole_polarization(self, value: CrossDipolePolarizationOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Cross Dipole Polarization=' + value.value])

    @property
    def override_height(self) -> bool:
        """Override Height
        "Ignores the default placement of quarter design wavelength over the ground plane."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Override Height')
        return val

    @override_height.setter
    def override_height(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Override Height=' + value])

    @property
    def offset_height(self) -> float:
        """Offset Height
        "Sets the offset height for the current sources above the ground plane."
        "Value should be greater than 0."
        """
        val = self._get_property('Offset Height')
        return val

    @offset_height.setter
    def offset_height(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Offset Height=' + value])

    @property
    def auto_height_offset(self) -> bool:
        """Auto Height Offset
        "Switch on to automatically place slot current at sub-wavelength offset height above ground plane."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Auto Height Offset')
        return val

    @auto_height_offset.setter
    def auto_height_offset(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Auto Height Offset=' + value])

    @property
    def conform__adjust_antenna(self) -> bool:
        """Conform / Adjust Antenna
        "Toggle (on/off) conformal adjustment for array antenna elements."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Conform / Adjust Antenna')
        return val

    @conform__adjust_antenna.setter
    def conform__adjust_antenna(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Conform / Adjust Antenna=' + value])

    @property
    def element_offset(self):
        """Element Offset
        "Set vector for shifting element positions in antenna local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Element Offset')
        return val

    @element_offset.setter
    def element_offset(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Element Offset=' + value])

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
        val = self.ConformtoPlatformOption[val]
        return val

    @conform_to_platform.setter
    def conform_to_platform(self, value: ConformtoPlatformOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Conform to Platform=' + value.value])

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
        val = self.ReferencePlaneOption[val]
        return val

    @reference_plane.setter
    def reference_plane(self, value: ReferencePlaneOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Reference Plane=' + value.value])

    @property
    def conform_element_orientation(self) -> bool:
        """Conform Element Orientation
        "Toggle (on/off) re-orientation of elements to conform to curved placement surface."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Conform Element Orientation')
        return val

    @conform_element_orientation.setter
    def conform_element_orientation(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Conform Element Orientation=' + value])

    @property
    def show_axes(self) -> bool:
        """Show Axes
        "Toggle (on/off) display of antenna coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Axes')
        return val

    @show_axes.setter
    def show_axes(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Axes=' + value])

    @property
    def show_icon(self) -> bool:
        """Show Icon
        "Toggle (on/off) display of antenna marker (cone) in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Icon')
        return val

    @show_icon.setter
    def show_icon(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Icon=' + value])

    @property
    def size(self) -> float:
        """Size
        "Adjust relative size of antenna marker (cone) in 3-D window."
        "Value should be between 0.001 and 1."
        """
        val = self._get_property('Size')
        return val

    @size.setter
    def size(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Size=' + value])

    @property
    def color(self):
        """Color
        "Set color of antenna marker (cone) in 3-D window."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Color')
        return val

    @color.setter
    def color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Color=' + value])

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
        return val

    @property
    def waveguide_cutoff_frequency(self) -> float:
        """Waveguide Cutoff Frequency
        "Implied lowest operating frequency of pyramidal horn antenna."
        "        """
        val = self._get_property('Waveguide Cutoff Frequency')
        return val

    @property
    def aperture_cutoff_frequency(self) -> float:
        """Aperture Cutoff Frequency
        "Implied lowest operating frequency of conical horn antenna."
        "        """
        val = self._get_property('Aperture Cutoff Frequency')
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
        val = self.SWEModeTruncationOption[val]
        return val

    @swe_mode_truncation.setter
    def swe_mode_truncation(self, value: SWEModeTruncationOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['SWE Mode Truncation=' + value.value])

    @property
    def max_n_index(self) -> int:
        """Max N Index
        "Set maximum allowed index N for spherical wave expansion terms."
        "Value should be greater than 1."
        """
        val = self._get_property('Max N Index')
        return val

    @max_n_index.setter
    def max_n_index(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Max N Index=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    @notes.setter
    def notes(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def show_composite_passband(self) -> bool:
        """Show Composite Passband
        "Show plot instead of 3D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Composite Passband')
        return val

    @show_composite_passband.setter
    def show_composite_passband(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Composite Passband=' + value])

    @property
    def use_phase_center(self) -> bool:
        """Use Phase Center
        "Use the phase center defined in the HFSS design."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Phase Center')
        return val

    @use_phase_center.setter
    def use_phase_center(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Use Phase Center=' + value])

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

