class Node_CADNode(GenericEmitNode):
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
    def get_file(self):
        """File
        "Name of the imported CAD file."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')

    @property
    def get_model_type(self):
        """Model Type
        "Select type of parametric model to create."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Model Type')
    def set_model_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Model Type=' + value])
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
    def get_length(self):
        """Length
        "Length of the model."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Length')
    def set_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Length=' + value])

    @property
    def get_width(self):
        """Width
        "Width of the model."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Width')
    def set_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Width=' + value])

    @property
    def get_height(self):
        """Height
        "Height of the model."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Height')
    def set_height(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Height=' + value])

    @property
    def get_angle(self):
        """Angle
        "Angle (deg) between the plates."
        "Value should be between 0.0 and 360.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Angle')
    def set_angle(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Angle=' + value])

    @property
    def get_top_side(self):
        """Top Side
        "Side of the top of a equilateral triangular cylinder model."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Top Side')
    def set_top_side(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Top Side=' + value])

    @property
    def get_top_radius(self):
        """Top Radius
        "Radius of the top of a tapered cylinder model."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Top Radius')
    def set_top_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Top Radius=' + value])

    @property
    def get_side(self):
        """Side
        "Side of the equilateral triangular cylinder."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Side')
    def set_side(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Side=' + value])

    @property
    def get_radius(self):
        """Radius
        "Radius of the sphere or cylinder."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Radius')
    def set_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Radius=' + value])

    @property
    def get_base_radius(self):
        """Base Radius
        "Radius of the base of a tophat model."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Base Radius')
    def set_base_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Base Radius=' + value])

    @property
    def get_center_radius(self):
        """Center Radius
        "Radius of the raised portion of a tophat model."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Center Radius')
    def set_center_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Center Radius=' + value])

    @property
    def get_x_axis_ellipsoid_radius(self):
        """X Axis Ellipsoid Radius
        "Ellipsoid semi-principal radius for the X axis."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'X Axis Ellipsoid Radius')
    def set_x_axis_ellipsoid_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['X Axis Ellipsoid Radius=' + value])

    @property
    def get_y_axis_ellipsoid_radius(self):
        """Y Axis Ellipsoid Radius
        "Ellipsoid semi-principal radius for the Y axis."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y Axis Ellipsoid Radius')
    def set_y_axis_ellipsoid_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y Axis Ellipsoid Radius=' + value])

    @property
    def get_z_axis_ellipsoid_radius(self):
        """Z Axis Ellipsoid Radius
        "Ellipsoid semi-principal radius for the Z axis."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Z Axis Ellipsoid Radius')
    def set_z_axis_ellipsoid_radius(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Z Axis Ellipsoid Radius=' + value])

    @property
    def get_focal_length(self):
        """Focal Length
        "Focal length of a parabolic reflector (f = 1/4a where y=ax^2)."
        "Value should be greater than 0.000001."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Focal Length')
    def set_focal_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Focal Length=' + value])

    @property
    def get_offset(self):
        """Offset
        "Offset of parabolic reflector."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Offset')
    def set_offset(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Offset=' + value])

    @property
    def get_x_direction_taper(self):
        """X Direction Taper
        "Amount (%) that the prism tapers in the X dimension from one end to the other."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'X Direction Taper')
    def set_x_direction_taper(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['X Direction Taper=' + value])

    @property
    def get_y_direction_taper(self):
        """Y Direction Taper
        "Amount (%) that the prism tapers in the Y dimension from one end to the other."
        "Value should be greater than 0.0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Y Direction Taper')
    def set_y_direction_taper(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Y Direction Taper=' + value])

    @property
    def get_prism_direction(self):
        """Prism Direction
        "Direction vector between the center of the base and center of the top."
        "Value should be x/y/z, delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Prism Direction')
    def set_prism_direction(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Prism Direction=' + value])

    @property
    def get_closed_top(self):
        """Closed Top
        "Control whether the top of the model is closed."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Closed Top')
    def set_closed_top(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Closed Top=' + value])

    @property
    def get_closed_base(self):
        """Closed Base
        "Control whether the base of the model is closed."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Closed Base')
    def set_closed_base(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Closed Base=' + value])

    @property
    def get_mesh_density(self):
        """Mesh Density
        "Unitless mesh density parameter where higher value improves mesh smoothness."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mesh Density')
    def set_mesh_density(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mesh Density=' + value])

    @property
    def get_use_symmetric_mesh(self):
        """Use Symmetric Mesh
        "Convert quads to a symmetric triangle mesh by adding a center point (4 triangles per quad instead of 2)."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use Symmetric Mesh')
    def set_use_symmetric_mesh(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use Symmetric Mesh=' + value])

    @property
    def get_mesh_option(self):
        """Mesh Option
        "Select from different meshing options."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Mesh Option')
    def set_mesh_option(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Mesh Option=' + value])
    class MeshOptionOption(Enum):
        IMPROVED = "Improved"
        LEGACY = "Legacy"

    @property
    def get_coating_index(self):
        """Coating Index
        "Coating index for the parametric model primitive."
        "Value should be between 0 and 100000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Coating Index')
    def set_coating_index(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Coating Index=' + value])

    @property
    def get_show_relative_coordinates(self):
        """Show Relative Coordinates
        "Show CAD model node position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Relative Coordinates')
    def set_show_relative_coordinates(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Relative Coordinates=' + value])

    @property
    def get_position(self):
        """Position
        "Set position of the CAD node in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')
    def set_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def get_relative_position(self):
        """Relative Position
        "Set position of the CAD model node relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Position')
    def set_relative_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Relative Position=' + value])

    @property
    def get_orientation_mode(self):
        """Orientation Mode
        "Select the convention (order of rotations) for configuring orientation."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation Mode')
    def set_orientation_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Orientation Mode=' + value])
    class OrientationModeOption(Enum):
        (
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"
        )

    @property
    def get_orientation(self):
        """Orientation
        "Set orientation of the CAD node in parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation')
    def set_orientation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Orientation=' + value])

    @property
    def get_relative_orientation(self):
        """Relative Orientation
        "Set orientation of the CAD model node relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Orientation')
    def set_relative_orientation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Relative Orientation=' + value])

    @property
    def get_visible(self):
        """Visible
        "Toggle (on/off) display of CAD model in 3-D window."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Visible')
    def set_visible(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Visible=' + value])

    @property
    def get_render_mode(self):
        """Render Mode
        "Select drawing style for surfaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Render Mode')
    def set_render_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Render Mode=' + value])
    class RenderModeOption(Enum):
        (
            FLAT_SHADED = "Flat-Shaded"
            WIRE_FRAME = "Wire-Frame"
            HIDDEN_WIRE_FRAME = "Hidden Wire-Frame"
            OUTLINE = "Outline"
        )

    @property
    def get_show_axes(self):
        """Show Axes
        "Toggle (on/off) display of CAD model coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Axes')
    def set_show_axes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Show Axes=' + value])

    @property
    def get_min(self):
        """Min
        "Minimum x,y,z extents of CAD model in local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Min')

    @property
    def get_max(self):
        """Max
        "Maximum x,y,z extents of CAD model in local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max')

    @property
    def get_number_of_surfaces(self):
        """Number of Surfaces
        "Number of surfaces in the model."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Number of Surfaces')

    @property
    def get_color(self):
        """Color
        "Defines the CAD nodes color."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Color')
    def set_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Color=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

