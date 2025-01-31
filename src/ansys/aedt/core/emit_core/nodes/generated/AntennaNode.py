from ..GenericEmitNode import *
class AntennaNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def add_antenna_passband(self):
        """Add a New Passband to this Antenna"""
        return self._add_child_node("AntennaPassband")

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
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Tags')
        key_val_pair = [i for i in props if 'Tags=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @tags.setter
    def tags(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Tags=' + value])

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        "Show antenna position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Relative Coordinates')
        key_val_pair = [i for i in props if 'Show Relative Coordinates=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Relative Coordinates=' + value])

    @property
    def position(self):
        """Position
        "Set position of the antenna in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')
        key_val_pair = [i for i in props if 'Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @position.setter
    def position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def relative_position(self):
        """Relative Position
        "Set position of the antenna relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Position')
        key_val_pair = [i for i in props if 'Relative Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @relative_position.setter
    def relative_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Relative Position=' + value])

    @property
    def orientation_mode(self):
        """Orientation Mode
        "Select the convention (order of rotations) for configuring orientation."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation Mode')
        key_val_pair = [i for i in props if 'Orientation Mode=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @orientation_mode.setter
    def orientation_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Orientation Mode=' + value])
    class OrientationModeOption(Enum):
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"

    @property
    def orientation(self):
        """Orientation
        "Set orientation of the antenna relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation')
        key_val_pair = [i for i in props if 'Orientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @orientation.setter
    def orientation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Orientation=' + value])

    @property
    def relative_orientation(self):
        """Relative Orientation
        "Set orientation of the antenna relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Orientation')
        key_val_pair = [i for i in props if 'Relative Orientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @relative_orientation.setter
    def relative_orientation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Relative Orientation=' + value])

    @property
    def position_defined(self) -> bool:
        """Position Defined
        "Toggles on/off the ability to define a position for the antenna."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position Defined')
        key_val_pair = [i for i in props if 'Position Defined=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @position_defined.setter
    def position_defined(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position Defined=' + value])

    @property
    def antenna_temperature(self) -> float:
        """Antenna Temperature
        "Antenna noise temperature."
        "Value should be between 0 and 100000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Temperature')
        key_val_pair = [i for i in props if 'Antenna Temperature=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @antenna_temperature.setter
    def antenna_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna Temperature=' + value])

    @property
    def type(self):
        """Type
        "Defines the type of antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
        key_val_pair = [i for i in props if 'Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @type.setter
    def type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
            SUBTYPECHOICES = "::SubTypeChoiceLabels"

    @property
    def antenna_file(self) -> str:
        """Antenna File
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna File')
        key_val_pair = [i for i in props if 'Antenna File=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @antenna_file.setter
    def antenna_file(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna File=' + value])

    @property
    def project_name(self) -> str:
        """Project Name
        "Name of imported HFSS Antenna project."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Project Name')
        key_val_pair = [i for i in props if 'Project Name=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @project_name.setter
    def project_name(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Project Name=' + value])

    @property
    def peak_gain(self) -> float:
        """Peak Gain
        "Set peak gain of antenna (dBi)."
        "Value should be between -200 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Peak Gain')
        key_val_pair = [i for i in props if 'Peak Gain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @peak_gain.setter
    def peak_gain(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Peak Gain=' + value])

    @property
    def boresight(self):
        """Boresight
        "Select peak beam direction in local coordinates."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Boresight')
        key_val_pair = [i for i in props if 'Boresight=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @boresight.setter
    def boresight(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Boresight=' + value])
    class BoresightOption(Enum):
            XAXIS = "+X Axis"
            YAXIS = "+Y Axis"
            ZAXIS = "+Z Axis"

    @property
    def vertical_beamwidth(self) -> float:
        """Vertical Beamwidth
        "Set half-power beamwidth in local-coordinates elevation plane."
        "Value should be between 0.1 and 360."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Vertical Beamwidth')
        key_val_pair = [i for i in props if 'Vertical Beamwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @vertical_beamwidth.setter
    def vertical_beamwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Vertical Beamwidth=' + value])

    @property
    def horizontal_beamwidth(self) -> float:
        """Horizontal Beamwidth
        "Set half-power beamwidth in local-coordinates azimuth plane."
        "Value should be between 0.1 and 360."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Horizontal Beamwidth')
        key_val_pair = [i for i in props if 'Horizontal Beamwidth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @horizontal_beamwidth.setter
    def horizontal_beamwidth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Horizontal Beamwidth=' + value])

    @property
    def extra_sidelobe(self) -> bool:
        """Extra Sidelobe
        "Toggle (on/off) option to define two sidelobe levels."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Extra Sidelobe')
        key_val_pair = [i for i in props if 'Extra Sidelobe=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @extra_sidelobe.setter
    def extra_sidelobe(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Extra Sidelobe=' + value])

    @property
    def first_sidelobe_level(self) -> float:
        """First Sidelobe Level
        "Set reduction in the gain of Directive Beam antenna for first sidelobe level."
        "Value should be between 0 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'First Sidelobe Level')
        key_val_pair = [i for i in props if 'First Sidelobe Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @first_sidelobe_level.setter
    def first_sidelobe_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['First Sidelobe Level=' + value])

    @property
    def first_sidelobe_vert_bw(self) -> float:
        """First Sidelobe Vert. BW
        "Set beamwidth of first sidelobe beam in theta direction."
        "Value should be between 0.1 and 360."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'First Sidelobe Vert. BW')
        key_val_pair = [i for i in props if 'First Sidelobe Vert. BW=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @first_sidelobe_vert_bw.setter
    def first_sidelobe_vert_bw(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['First Sidelobe Vert. BW=' + value])

    @property
    def first_sidelobe_hor_bw(self) -> float:
        """First Sidelobe Hor. BW
        "Set beamwidth of first sidelobe beam in phi direction."
        "Value should be between 0.1 and 360."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'First Sidelobe Hor. BW')
        key_val_pair = [i for i in props if 'First Sidelobe Hor. BW=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @first_sidelobe_hor_bw.setter
    def first_sidelobe_hor_bw(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['First Sidelobe Hor. BW=' + value])

    @property
    def outerbacklobe_level(self) -> float:
        """Outer/Backlobe Level
        "Set reduction in gain of Directive Beam antenna for outer/backlobe level."
        "Value should be between 0 and 200."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Outer/Backlobe Level')
        key_val_pair = [i for i in props if 'Outer/Backlobe Level=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @outerbacklobe_level.setter
    def outerbacklobe_level(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Outer/Backlobe Level=' + value])

    @property
    def resonant_frequency(self) -> float:
        """Resonant Frequency
        "Set first resonant frequency of wire dipole, monopole, or parametric antenna."
        "Value should be between 1 and 1e+13."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Resonant Frequency')
        key_val_pair = [i for i in props if 'Resonant Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @resonant_frequency.setter
    def resonant_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Resonant Frequency=' + value])

    @property
    def slot_length(self) -> float:
        """Slot Length
        "Set slot length of parametric slot."
        "Value should be greater than 1e-06."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Slot Length')
        key_val_pair = [i for i in props if 'Slot Length=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @slot_length.setter
    def slot_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Slot Length=' + value])

    @property
    def mouth_width(self) -> float:
        """Mouth Width
        "Set mouth width (along local y-axis) of the horn antenna."
        "Value should be between 1e-06 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mouth Width')
        key_val_pair = [i for i in props if 'Mouth Width=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mouth_width.setter
    def mouth_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mouth Width=' + value])

    @property
    def mouth_height(self) -> float:
        """Mouth Height
        "Set mouth height (along local x-axis) of the horn antenna."
        "Value should be between 1e-06 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mouth Height')
        key_val_pair = [i for i in props if 'Mouth Height=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mouth_height.setter
    def mouth_height(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mouth Height=' + value])

    @property
    def waveguide_width(self) -> float:
        """Waveguide Width
        "Set waveguide width (along local y-axis) where flared horn walls meet the feed, determines cut-off frequency."
        "Value should be between 1e-06 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveguide Width')
        key_val_pair = [i for i in props if 'Waveguide Width=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @waveguide_width.setter
    def waveguide_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Waveguide Width=' + value])

    @property
    def width_flare_half_angle(self) -> float:
        """Width Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local yz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Width Flare Half-angle')
        key_val_pair = [i for i in props if 'Width Flare Half-angle=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @width_flare_half_angle.setter
    def width_flare_half_angle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Width Flare Half-angle=' + value])

    @property
    def height_flare_half_angle(self) -> float:
        """Height Flare Half-angle
        "Set half-angle (degrees) of flared horn walls measured in local xz-plane from boresight (z) axis to either wall."
        "Value should be between 1 and 89.9."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Height Flare Half-angle')
        key_val_pair = [i for i in props if 'Height Flare Half-angle=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @height_flare_half_angle.setter
    def height_flare_half_angle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Height Flare Half-angle=' + value])

    @property
    def mouth_diameter(self) -> float:
        """Mouth Diameter
        "Set aperture (mouth) diameter of horn antenna."
        "Value should be between 1e-06 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mouth Diameter')
        key_val_pair = [i for i in props if 'Mouth Diameter=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @mouth_diameter.setter
    def mouth_diameter(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mouth Diameter=' + value])

    @property
    def flare_half_angle(self) -> float:
        """Flare Half-angle
        "Set half-angle (degrees) of conical horn wall measured from boresight (z)."
        "Value should be between 1 and 89.9."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Flare Half-angle')
        key_val_pair = [i for i in props if 'Flare Half-angle=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @flare_half_angle.setter
    def flare_half_angle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Flare Half-angle=' + value])

    @property
    def vswr(self) -> float:
        """VSWR
        "The Voltage Standing Wave Ratio (VSWR) due to the impedance mismatch between the antenna and the RF System (or outboard component)."
        "Value should be between 1 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'VSWR')
        key_val_pair = [i for i in props if 'VSWR=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @vswr.setter
    def vswr(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['VSWR=' + value])

    @property
    def antenna_polarization(self):
        """Antenna Polarization
        "Choose local-coordinates polarization along boresight."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Polarization')
        key_val_pair = [i for i in props if 'Antenna Polarization=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @antenna_polarization.setter
    def antenna_polarization(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Antenna Polarization=' + value])
    class AntennaPolarizationOption(Enum):
            VERTICAL = "Vertical"
            HORIZONTAL = "Horizontal"
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def cross_dipole_mode(self):
        """Cross Dipole Mode
        "Choose the Cross Dipole type."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Cross Dipole Mode')
        key_val_pair = [i for i in props if 'Cross Dipole Mode=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @cross_dipole_mode.setter
    def cross_dipole_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Cross Dipole Mode=' + value])
    class CrossDipoleModeOption(Enum):
            FREESTANDING = "Freestanding"
            OVER_GROUND_PLANE = "Over Ground Plane"

    @property
    def cross_dipole_polarization(self):
        """Cross Dipole Polarization
        "Choose local-coordinates polarization along boresight."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Cross Dipole Polarization')
        key_val_pair = [i for i in props if 'Cross Dipole Polarization=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @cross_dipole_polarization.setter
    def cross_dipole_polarization(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Cross Dipole Polarization=' + value])
    class CrossDipolePolarizationOption(Enum):
            RHCP = "RHCP"
            LHCP = "LHCP"

    @property
    def override_height(self) -> bool:
        """Override Height
        "Ignores the default placement of quarter design wavelength over the ground plane."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Override Height')
        key_val_pair = [i for i in props if 'Override Height=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @override_height.setter
    def override_height(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Override Height=' + value])

    @property
    def offset_height(self) -> float:
        """Offset Height
        "Sets the offset height for the current sources above the ground plane."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Offset Height')
        key_val_pair = [i for i in props if 'Offset Height=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @offset_height.setter
    def offset_height(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Offset Height=' + value])

    @property
    def auto_height_offset(self) -> bool:
        """Auto Height Offset
        "Switch on to automatically place slot current at sub-wavelength offset height above ground plane."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Auto Height Offset')
        key_val_pair = [i for i in props if 'Auto Height Offset=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @auto_height_offset.setter
    def auto_height_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Auto Height Offset=' + value])

    @property
    def conform__adjust_antenna(self) -> bool:
        """Conform / Adjust Antenna
        "Toggle (on/off) conformal adjustment for array antenna elements."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Conform / Adjust Antenna')
        key_val_pair = [i for i in props if 'Conform / Adjust Antenna=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @conform__adjust_antenna.setter
    def conform__adjust_antenna(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Conform / Adjust Antenna=' + value])

    @property
    def element_offset(self):
        """Element Offset
        "Set vector for shifting element positions in antenna local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Element Offset')
        key_val_pair = [i for i in props if 'Element Offset=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @element_offset.setter
    def element_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Element Offset=' + value])

    @property
    def conform_to_platform(self):
        """Conform to Platform
        "Select method of automated conforming applied after Element Offset."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Conform to Platform')
        key_val_pair = [i for i in props if 'Conform to Platform=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @conform_to_platform.setter
    def conform_to_platform(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Conform to Platform=' + value])
    class ConformtoPlatformOption(Enum):
            NONE = "None"
            ALONG_NORMAL = "Along Normal"
            PERPENDICULAR_TO_PLANE = "Perpendicular to Plane"

    @property
    def reference_plane(self):
        """Reference Plane
        "Select reference plane for determining original element heights."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Reference Plane')
        key_val_pair = [i for i in props if 'Reference Plane=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @reference_plane.setter
    def reference_plane(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Reference Plane=' + value])
    class ReferencePlaneOption(Enum):
            XY_PLANE = "XY Plane"
            YZ_PLANE = "YZ Plane"
            ZX_PLANE = "ZX Plane"

    @property
    def conform_element_orientation(self) -> bool:
        """Conform Element Orientation
        "Toggle (on/off) re-orientation of elements to conform to curved placement surface."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Conform Element Orientation')
        key_val_pair = [i for i in props if 'Conform Element Orientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @conform_element_orientation.setter
    def conform_element_orientation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Conform Element Orientation=' + value])

    @property
    def show_axes(self) -> bool:
        """Show Axes
        "Toggle (on/off) display of antenna coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Axes')
        key_val_pair = [i for i in props if 'Show Axes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @show_axes.setter
    def show_axes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Axes=' + value])

    @property
    def show_icon(self) -> bool:
        """Show Icon
        "Toggle (on/off) display of antenna marker (cone) in 3-D window."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Icon')
        key_val_pair = [i for i in props if 'Show Icon=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @show_icon.setter
    def show_icon(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Icon=' + value])

    @property
    def size(self) -> float:
        """Size
        "Adjust relative size of antenna marker (cone) in 3-D window."
        "Value should be between 0.001 and 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Size')
        key_val_pair = [i for i in props if 'Size=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @size.setter
    def size(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Size=' + value])

    @property
    def color(self):
        """Color
        "Set color of antenna marker (cone) in 3-D window."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Color')
        key_val_pair = [i for i in props if 'Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @color.setter
    def color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Color=' + value])

    @property
    def el_sample_interval(self) -> float:
        """El Sample Interval
        "Space between elevation-angle samples of pattern."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'El Sample Interval')
        key_val_pair = [i for i in props if 'El Sample Interval=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def az_sample_interval(self) -> float:
        """Az Sample Interval
        "Space between azimuth-angle samples of pattern."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Az Sample Interval')
        key_val_pair = [i for i in props if 'Az Sample Interval=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def has_frequency_domain(self) -> bool:
        """Has Frequency Domain
        "False if antenna can be used at any frequency."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Has Frequency Domain')
        key_val_pair = [i for i in props if 'Has Frequency Domain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def frequency_domain(self):
        """Frequency Domain
        "Frequency sample(s) defining antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Frequency Domain')
        key_val_pair = [i for i in props if 'Frequency Domain=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def number_of_electric_sources(self) -> int:
        """Number of Electric Sources
        "Number of freestanding electric current sources defining antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Electric Sources')
        key_val_pair = [i for i in props if 'Number of Electric Sources=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def number_of_magnetic_sources(self) -> int:
        """Number of Magnetic Sources
        "Number of freestanding magnetic current sources defining antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Magnetic Sources')
        key_val_pair = [i for i in props if 'Number of Magnetic Sources=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def number_of_imaged_electric_sources(self) -> int:
        """Number of Imaged Electric Sources
        "Number of imaged, half-space radiating electric current sources defining antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Imaged Electric Sources')
        key_val_pair = [i for i in props if 'Number of Imaged Electric Sources=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def number_of_imaged_magnetic_sources(self) -> int:
        """Number of Imaged Magnetic Sources
        "Number of imaged, half-space radiating magnetic current sources defining antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Imaged Magnetic Sources')
        key_val_pair = [i for i in props if 'Number of Imaged Magnetic Sources=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def waveguide_height(self) -> float:
        """Waveguide Height
        "Implied waveguide height (along local x-axis) where the flared horn walls meet the feed."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveguide Height')
        key_val_pair = [i for i in props if 'Waveguide Height=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def waveguide_cutoff_frequency(self) -> float:
        """Waveguide Cutoff Frequency
        "Implied lowest operating frequency of pyramidal horn antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Waveguide Cutoff Frequency')
        key_val_pair = [i for i in props if 'Waveguide Cutoff Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def aperture_cutoff_frequency(self) -> float:
        """Aperture Cutoff Frequency
        "Implied lowest operating frequency of conical horn antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Aperture Cutoff Frequency')
        key_val_pair = [i for i in props if 'Aperture Cutoff Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def swe_mode_truncation(self):
        """SWE Mode Truncation
        "Select the method for stability-enhancing truncation of spherical wave expansion terms."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SWE Mode Truncation')
        key_val_pair = [i for i in props if 'SWE Mode Truncation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @swe_mode_truncation.setter
    def swe_mode_truncation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['SWE Mode Truncation=' + value])
    class SWEModeTruncationOption(Enum):
            DYNAMIC = "Dynamic"
            CUSTOM = "Fixed (Custom)"
            NONE = "None"

    @property
    def max_n_index(self) -> int:
        """Max N Index
        "Set maximum allowed index N for spherical wave expansion terms."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max N Index')
        key_val_pair = [i for i in props if 'Max N Index=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @max_n_index.setter
    def max_n_index(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max N Index=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
        key_val_pair = [i for i in props if 'Notes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @notes.setter
    def notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def show_composite_passband(self) -> bool:
        """Show Composite Passband
        "Show plot instead of 3D window."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Composite Passband')
        key_val_pair = [i for i in props if 'Show Composite Passband=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @show_composite_passband.setter
    def show_composite_passband(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Composite Passband=' + value])

    @property
    def use_phase_center(self) -> bool:
        """Use Phase Center
        "Use the phase center defined in the HFSS design."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Phase Center')
        key_val_pair = [i for i in props if 'Use Phase Center=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @use_phase_center.setter
    def use_phase_center(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Phase Center=' + value])

    @property
    def coordinate_systems(self) -> str:
        """Coordinate Systems
        "Specifies the coordinate system for the phase center of this antenna."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Coordinate Systems')
        key_val_pair = [i for i in props if 'Coordinate Systems=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def phasecenterposition(self):
        """PhaseCenterPosition
        "Set position of the antennas linked coordinate system.."
        "Value should be x/y/z, delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'PhaseCenterPosition')
        key_val_pair = [i for i in props if 'PhaseCenterPosition=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def phasecenterorientation(self):
        """PhaseCenterOrientation
        "Set orientation of the antennas linked coordinate system.."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'PhaseCenterOrientation')
        key_val_pair = [i for i in props if 'PhaseCenterOrientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

