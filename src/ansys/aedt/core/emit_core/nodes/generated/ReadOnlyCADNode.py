from ..EmitNode import *

class ReadOnlyCADNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def file(self) -> str:
        """File
        "Name of the imported CAD file."
        "Value should be a full file path."
        """
        val = self._get_property('File')
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
        """Model Type
        "Select type of parametric model to create."
        "        """
        val = self._get_property('Model Type')
        val = self.ModelTypeOption[val]
        return val

    @property
    def length(self) -> float:
        """Length
        "Length of the model."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Length')
        return val

    @property
    def width(self) -> float:
        """Width
        "Width of the model."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Width')
        return val

    @property
    def height(self) -> float:
        """Height
        "Height of the model."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Height')
        return val

    @property
    def angle(self) -> float:
        """Angle
        "Angle (deg) between the plates."
        "Value should be between 0 and 360."
        """
        val = self._get_property('Angle')
        return val

    @property
    def top_side(self) -> float:
        """Top Side
        "Side of the top of a equilateral triangular cylinder model."
        "Value should be greater than 0."
        """
        val = self._get_property('Top Side')
        return val

    @property
    def top_radius(self) -> float:
        """Top Radius
        "Radius of the top of a tapered cylinder model."
        "Value should be greater than 0."
        """
        val = self._get_property('Top Radius')
        return val

    @property
    def side(self) -> float:
        """Side
        "Side of the equilateral triangular cylinder."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Side')
        return val

    @property
    def radius(self) -> float:
        """Radius
        "Radius of the sphere or cylinder."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Radius')
        return val

    @property
    def base_radius(self) -> float:
        """Base Radius
        "Radius of the base of a tophat model."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Base Radius')
        return val

    @property
    def center_radius(self) -> float:
        """Center Radius
        "Radius of the raised portion of a tophat model."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Center Radius')
        return val

    @property
    def x_axis_ellipsoid_radius(self) -> float:
        """X Axis Ellipsoid Radius
        "Ellipsoid semi-principal radius for the X axis."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('X Axis Ellipsoid Radius')
        return val

    @property
    def y_axis_ellipsoid_radius(self) -> float:
        """Y Axis Ellipsoid Radius
        "Ellipsoid semi-principal radius for the Y axis."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Y Axis Ellipsoid Radius')
        return val

    @property
    def z_axis_ellipsoid_radius(self) -> float:
        """Z Axis Ellipsoid Radius
        "Ellipsoid semi-principal radius for the Z axis."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Z Axis Ellipsoid Radius')
        return val

    @property
    def focal_length(self) -> float:
        """Focal Length
        "Focal length of a parabolic reflector (f = 1/4a where y=ax^2)."
        "Value should be greater than 1e-06."
        """
        val = self._get_property('Focal Length')
        return val

    @property
    def offset(self) -> float:
        """Offset
        "Offset of parabolic reflector."
        "        """
        val = self._get_property('Offset')
        return val

    @property
    def x_direction_taper(self) -> float:
        """X Direction Taper
        "Amount (%) that the prism tapers in the X dimension from one end to the other."
        "Value should be greater than 0."
        """
        val = self._get_property('X Direction Taper')
        return val

    @property
    def y_direction_taper(self) -> float:
        """Y Direction Taper
        "Amount (%) that the prism tapers in the Y dimension from one end to the other."
        "Value should be greater than 0."
        """
        val = self._get_property('Y Direction Taper')
        return val

    @property
    def prism_direction(self):
        """Prism Direction
        "Direction vector between the center of the base and center of the top."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Prism Direction')
        return val

    @property
    def closed_top(self) -> bool:
        """Closed Top
        "Control whether the top of the model is closed."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Closed Top')
        return val

    @property
    def closed_base(self) -> bool:
        """Closed Base
        "Control whether the base of the model is closed."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Closed Base')
        return val

    @property
    def mesh_density(self) -> int:
        """Mesh Density
        "Unitless mesh density parameter where higher value improves mesh smoothness."
        "Value should be between 1 and 100."
        """
        val = self._get_property('Mesh Density')
        return val

    @property
    def use_symmetric_mesh(self) -> bool:
        """Use Symmetric Mesh
        "Convert quads to a symmetric triangle mesh by adding a center point (4 triangles per quad instead of 2)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use Symmetric Mesh')
        return val

    class MeshOptionOption(Enum):
            IMPROVED = "Improved"
            LEGACY = "Legacy"

    @property
    def mesh_option(self) -> MeshOptionOption:
        """Mesh Option
        "Select from different meshing options."
        "        """
        val = self._get_property('Mesh Option')
        val = self.MeshOptionOption[val]
        return val

    @property
    def coating_index(self) -> int:
        """Coating Index
        "Coating index for the parametric model primitive."
        "Value should be between 0 and 100000."
        """
        val = self._get_property('Coating Index')
        return val

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        "Show CAD model node position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Relative Coordinates')
        return val

    @property
    def position(self):
        """Position
        "Set position of the CAD node in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Position')
        return val

    @property
    def relative_position(self):
        """Relative Position
        "Set position of the CAD model node relative to placement coordinates."
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
        val = self.OrientationModeOption[val]
        return val

    @property
    def orientation(self):
        """Orientation
        "Set orientation of the CAD node in parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Orientation')
        return val

    @property
    def relative_orientation(self):
        """Relative Orientation
        "Set orientation of the CAD model node relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Relative Orientation')
        return val

    @property
    def visible(self) -> bool:
        """Visible
        "Toggle (on/off) display of CAD model in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Visible')
        return val

    class RenderModeOption(Enum):
            FLAT_SHADED = "Flat-Shaded"
            WIRE_FRAME = "Wire-Frame"
            HIDDEN_WIRE_FRAME = "Hidden Wire-Frame"
            OUTLINE = "Outline"

    @property
    def render_mode(self) -> RenderModeOption:
        """Render Mode
        "Select drawing style for surfaces."
        "        """
        val = self._get_property('Render Mode')
        val = self.RenderModeOption[val]
        return val

    @property
    def show_axes(self) -> bool:
        """Show Axes
        "Toggle (on/off) display of CAD model coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Axes')
        return val

    @property
    def min(self):
        """Min
        "Minimum x,y,z extents of CAD model in local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Min')
        return val

    @property
    def max(self):
        """Max
        "Maximum x,y,z extents of CAD model in local coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Max')
        return val

    @property
    def number_of_surfaces(self) -> int:
        """Number of Surfaces
        "Number of surfaces in the model."
        "        """
        val = self._get_property('Number of Surfaces')
        return val

    @property
    def color(self):
        """Color
        "Defines the CAD nodes color."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Color')
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

