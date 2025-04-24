from ..EmitNode import *

class ReadOnlyEmitSceneNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property('Notes')
        return val

    class GroundPlaneNormalOption(Enum):
            XAXIS = "X Axis"
            YAXIS = "Y Axis"
            ZAXIS = "Z Axis"

    @property
    def ground_plane_normal(self) -> GroundPlaneNormalOption:
        """Ground Plane Normal
        "Specifies the axis of the normal to the ground plane."
        "        """
        val = self._get_property('Ground Plane Normal')
        val = self.GroundPlaneNormalOption[val.upper()]
        return val

    @property
    def gp_position_along_normal(self) -> float:
        """GP Position Along Normal
        "Offset of ground plane in direction normal to the ground planes orientation."
        "        """
        val = self._get_property('GP Position Along Normal')
        val = self._convert_from_internal_units(float(val), "Length")
        return val

