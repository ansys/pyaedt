
from ..GenericEmitNode import GenericEmitNode
from enum import Enum

class Node_AntennaNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
    def get_tags(self):
        """Tags
        "Space delimited list of tags for coupling selections."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tags')
    def set_tags(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tags=' + value])

    @property
    def get_show_relative_coordinates(self):
        """Show Relative Coordinates
        "Show antenna position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Relative Coordinates')
    def set_show_relative_coordinates(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Relative Coordinates=' + value])

    @property
    def get_position(self):
        """Position
        "Set position of the antenna in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')
    def set_position(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def get_relative_position(self):
        """Relative Position
        "Set position of the antenna relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Position')
    def set_relative_position(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Relative Position=' + value])

    @property
    def get_orientation_mode(self):
        """Orientation Mode
        "Select the convention (order of rotations) for configuring orientation."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation Mode')
    def set_orientation_mode(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Orientation Mode=' + value])
    class OrientationModeOption(Enum):
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"

    @property
    def get_orientation(self):
        """Orientation
        "Set orientation of the antenna relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation')
    def set_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Orientation=' + value])

    @property
    def get_relative_orientation(self):
        """Relative Orientation
        "Set orientation of the antenna relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Orientation')
    def set_relative_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Relative Orientation=' + value])

    @property
    def get_position_defined(self):
        """Position Defined
        "Toggles on/off the ability to define a position for the antenna."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position Defined')
    def set_position_defined(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position Defined=' + value])

    @property
    def get_antenna_temperature(self):
        """Antenna Temperature
        "Antenna noise temperature."
        "Value should be between 0 and 100000."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Temperature')
    def set_antenna_temperature(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna Temperature=' + value])

    @property
    def get_type(self):
        """Type
        "Defines the type of antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
    def set_type(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
            SUBTYPECHOICES = "::SubTypeChoiceLabels"

    @property
    def get_antenna_file(self):
        """Antenna File
        "Value should be a full file path."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna File')
    def set_antenna_file(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna File=' + value])

    @property
    def get_project_name(self):
        """Project Name
        "Name of imported HFSS Antenna project."
        "Value should be a full file path."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Project Name')
    def set_project_name(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Project Name=' + value])

    @property
    def get_peak_gain(self):
        """Peak Gain
        "Set peak gain of antenna (dBi)."
        "Value should be between -200 and 200."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Peak Gain')
    def set_peak_gain(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Peak Gain=' + value])

    @property
    def get_boresight(self):
        """Boresight
        "Select peak beam direction in local coordinates."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Boresight')
    def set_boresight(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Boresight=' + value])
    class BoresightOption(Enum):
            XAXIS = "+X Axis"
            YAXIS = "+Y Axis"
            ZAXIS = "+Z Axis"

    @property
    def get_vertical_beamwidth(self):
        """Vertical Beamwidth
        "Set half-power beamwidth in local-coordinates elevation plane."
        "Value should be between 0.1 and 360."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Vertical Beamwidth')
    def set_vertical_beamwidth(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Vertical Beamwidth=' + value])

    @property
    def get_horizontal_beamwidth(self):
        """Horizontal Beamwidth
        "Set half-power beamwidth in local-coordinates azimuth plane."
        "Value should be between 0.1 and 360."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Horizontal Beamwidth')
    def set_horizontal_beamwidth(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Horizontal Beamwidth=' + value])

    @property
    def get_extra_sidelobe(self):
        """Extra Sidelobe
        "Toggle (on/off) option to define two sidelobe levels."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Extra Sidelobe')
    def set_extra_sidelobe(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Extra Sidelobe=' + value])

    @property
    def get_first_sidelobe_level(self):
        """First Sidelobe Level
        "Set reduction in the gain of Directive Beam antenna for first sidelobe level."
        "Value should be between 0 and 200."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'First Sidelobe Level')
    def set_first_sidelobe_level(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['First Sidelobe Level=' + value])

    @property
    def get_first_sidelobe_vert_bw(self):
        """First Sidelobe Vert. BW
        "Set beamwidth of first sidelobe beam in theta direction."
        "Value should be between 0.1 and 360."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'First Sidelobe Vert. BW')
    def set_first_sidelobe_vert_bw(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['First Sidelobe Vert. BW=' + value])

    @property
    def get_first_sidelobe_hor_bw(self):
        """First Sidelobe Hor. BW
        "Set beamwidth of first sidelobe beam in phi direction."
        "Value should be between 0.1 and 360."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'First Sidelobe Hor. BW')
    def set_first_sidelobe_hor_bw(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['First Sidelobe Hor. BW=' + value])

    @property
    def get_outerbacklobe_level(self):
        """Outer/Backlobe Level
        "Set reduction in gain of Directive Beam antenna for outer/backlobe level."
        "Value should be between 0 and 200."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Outer/Backlobe Level')
    def set_outerbacklobe_level(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Outer/Backlobe Level=' + value])

    @property
    def get_resonant_frequency(self):
        """Resonant Frequency
        "Set first resonant frequency of wire dipole, monopole, or parametric antenna."
        "Value should be between 1.0 and 1e13."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Resonant Frequency')
    def set_resonant_frequency(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Resonant Frequency=' + value])

    @property
    def get_slot_length(self):
        """Slot Length
        "Set slot length of parametric slot."
        "Value should be greater than 1e-6."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Slot Length')
    def set_slot_length(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Slot Length=' + value])

    @property
    def get_mouth_width(self):
        """Mouth Width
        "Set mouth width (along local y-axis) of the horn antenna."
        "Value should be between 1e-6 and 100."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mouth Width')
    def set_mouth_width(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mouth Width=' + value])

    @property
    def get_mouth_height(self):
        """Mouth Height
        "Set mouth height (along local x-axis) of the horn antenna."
        "Value should be between 1e-6 and 100."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mouth Height')
    def set_mouth_height(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mouth Height=' + value])

    @property
    def get_waveguide_width(self):
        """Waveguide Width
        "Set waveguide width (along local y-axis) where flared horn walls meet the feed, determines cut-off frequency."
        "Value should be between 1e-6 and 100."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveguide Width')
    def set_waveguide_width(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Waveguide Width=' + value])

    @property
    def get_width_flare_half_angle(self):
        """Width Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local yz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Width Flare Half-angle')
    def set_width_flare_half_angle(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Width Flare Half-angle=' + value])

    @property
    def get_height_flare_half_angle(self):
        """Height Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local xz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Height Flare Half-angle')
    def set_height_flare_half_angle(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Height Flare Half-angle=' + value])

    @property
    def get_mouth_diameter(self):
        """Mouth Diameter
        "Set aperture (mouth) diameter of horn antenna."
        "Value should be between 1e-6 and 100."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mouth Diameter')
    def set_mouth_diameter(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mouth Diameter=' + value])

    @property
    def get_flare_half_angle(self):
        """Flare Half-angle
        "Set half-angle (degrees) of conical horn wall measured from boresight (z)."
        "Value should be between 1 and 89.9."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Flare Half-angle')
    def set_flare_half_angle(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Flare Half-angle=' + value])

    @property
    def get_vswr(self):
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the antenna and the RF System (or outboard component)."
        "Value should be between 1 and 100."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'VSWR')
    def set_vswr(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['VSWR=' + value])

    @property
    def get_antenna_polarization(self):
        """Antenna Polarization
        "Choose local-coordinates polarization along boresight."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Polarization')
    def set_antenna_polarization(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna Polarization=' + value])
    class AntennaPolarizationOption(Enum):
            VERTICAL = "Vertical"
            HORIZONTAL = "Horizontal"
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def get_cross_dipole_mode(self):
        """Cross Dipole Mode
        "Choose the Cross Dipole type."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Cross Dipole Mode')
    def set_cross_dipole_mode(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Cross Dipole Mode=' + value])
    class CrossDipoleModeOption(Enum):
            FREESTANDING = "Freestanding"
            OVER_GROUND_PLANE = "Over Ground Plane"

    @property
    def get_cross_dipole_polarization(self):
        """Cross Dipole Polarization
        "Choose local-coordinates polarization along boresight."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Cross Dipole Polarization')
    def set_cross_dipole_polarization(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Cross Dipole Polarization=' + value])
    class CrossDipolePolarizationOption(Enum):
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def get_override_height(self):
        """Override Height
        "Ignores the default placement of quarter design wavelength over the ground plane."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Override Height')
    def set_override_height(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Override Height=' + value])

    @property
    def get_offset_height(self):
        """Offset Height
        "Sets the offset height for the current sources above the ground plane."
        "Value should be greater than 0."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Offset Height')
    def set_offset_height(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Offset Height=' + value])

    @property
    def get_auto_height_offset(self):
        """Auto Height Offset
        "Switch on to automatically place slot current at sub-wavelength offset height above ground plane."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Auto Height Offset')
    def set_auto_height_offset(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Auto Height Offset=' + value])

    @property
    def get_conform__adjust_antenna(self):
        """Conform / Adjust Antenna
        "Toggle (on/off) conformal adjustment for array antenna elements."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Conform / Adjust Antenna')
    def set_conform__adjust_antenna(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Conform / Adjust Antenna=' + value])

    @property
    def get_element_offset(self):
        """Element Offset
        "Set vector for shifting element positions in antenna local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Element Offset')
    def set_element_offset(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Element Offset=' + value])

    @property
    def get_conform_to_platform(self):
        """Conform to Platform
        "Select method of automated conforming applied after Element Offset."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Conform to Platform')
    def set_conform_to_platform(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Conform to Platform=' + value])
    class ConformtoPlatformOption(Enum):
            NONE = "None"
            ALONG_NORMAL = "Along Normal"
            PERPENDICULAR_TO_PLANE = "Perpendicular to Plane"

    @property
    def get_reference_plane(self):
        """Reference Plane
        "Select reference plane for determining original element heights."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Reference Plane')
    def set_reference_plane(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Reference Plane=' + value])
    class ReferencePlaneOption(Enum):
            XY_PLANE = "XY Plane"
            YZ_PLANE = "YZ Plane"
            ZX_PLANE = "ZX Plane"

    @property
    def get_conform_element_orientation(self):
        """Conform Element Orientation
        "Toggle (on/off) re-orientation of elements to conform to curved placement surface."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Conform Element Orientation')
    def set_conform_element_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Conform Element Orientation=' + value])

    @property
    def get_show_axes(self):
        """Show Axes
        "Toggle (on/off) display of antenna coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Axes')
    def set_show_axes(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Axes=' + value])

    @property
    def get_show_icon(self):
        """Show Icon
        "Toggle (on/off) display of antenna marker (cone) in 3-D window."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Icon')
    def set_show_icon(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Icon=' + value])

    @property
    def get_size(self):
        """Size
        "Adjust relative size of antenna marker (cone) in 3-D window."
        "Value should be between 0.001 and 1."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Size')
    def set_size(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Size=' + value])

    @property
    def get_color(self):
        """Color
        "Set color of antenna marker (cone) in 3-D window."
        "Color should be in RGB form: #RRGGBB."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Color')
    def set_color(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Color=' + value])

    @property
    def get_el_sample_interval(self):
        """El Sample Interval
        "Space between elevation-angle samples of pattern."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'El Sample Interval')

    @property
    def get_az_sample_interval(self):
        """Az Sample Interval
        "Space between azimuth-angle samples of pattern."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Az Sample Interval')

    @property
    def get_has_frequency_domain(self):
        """Has Frequency Domain
        "False if antenna can be used at any frequency."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Has Frequency Domain')

    @property
    def get_frequency_domain(self):
        """Frequency Domain
        "Frequency sample(s) defining antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Frequency Domain')

    @property
    def get_number_of_electric_sources(self):
        """Number of Electric Sources
        "Number of freestanding electric current sources defining antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Electric Sources')

    @property
    def get_number_of_magnetic_sources(self):
        """Number of Magnetic Sources
        "Number of freestanding magnetic current sources defining antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Magnetic Sources')

    @property
    def get_number_of_imaged_electric_sources(self):
        """Number of Imaged Electric Sources
        "Number of imaged, half-space radiating electric current sources defining antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Imaged Electric Sources')

    @property
    def get_number_of_imaged_magnetic_sources(self):
        """Number of Imaged Magnetic Sources
        "Number of imaged, half-space radiating magnetic current sources defining antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Imaged Magnetic Sources')

    @property
    def get_waveguide_height(self):
        """Waveguide Height
        "Implied waveguide height (along local x-axis) where the flared horn walls meet the feed."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveguide Height')

    @property
    def get_waveguide_cutoff_frequency(self):
        """Waveguide Cutoff Frequency
        "Implied lowest operating frequency of pyramidal horn antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveguide Cutoff Frequency')

    @property
    def get_aperture_cutoff_frequency(self):
        """Aperture Cutoff Frequency
        "Implied lowest operating frequency of conical horn antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Aperture Cutoff Frequency')

    @property
    def get_swe_mode_truncation(self):
        """SWE Mode Truncation
        "Select the method for stability-enhancing truncation of spherical wave expansion terms."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SWE Mode Truncation')
    def set_swe_mode_truncation(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['SWE Mode Truncation=' + value])
    class SWEModeTruncationOption(Enum):
            DYNAMIC = "Dynamic"
            CUSTOM = "Fixed (Custom)"
            NONE = "None"

    @property
    def get_max_n_index(self):
        """Max N Index
        "Set maximum allowed index N for spherical wave expansion terms."
        "Value should be greater than 1."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max N Index')
    def set_max_n_index(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max N Index=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def get_show_composite_passband(self):
        """Show Composite Passband
        "Show plot instead of 3D window."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Composite Passband')
    def set_show_composite_passband(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Composite Passband=' + value])

    @property
    def get_use_phase_center(self):
        """Use Phase Center
        "Use the phase center defined in the HFSS design."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Phase Center')
    def set_use_phase_center(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Phase Center=' + value])

    @property
    def get_coordinate_systems(self):
        """Coordinate Systems
        "Specifies the coordinate system for the phase center of this antenna."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Coordinate Systems')

    @property
    def get_phasecenterposition(self):
        """PhaseCenterPosition
        "Set position of the antennas linked coordinate system.."
        "Value should be x/y/z, delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'PhaseCenterPosition')

    @property
    def get_phasecenterorientation(self):
        """PhaseCenterOrientation
        "Set orientation of the antennas linked coordinate system.."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'PhaseCenterOrientation')

