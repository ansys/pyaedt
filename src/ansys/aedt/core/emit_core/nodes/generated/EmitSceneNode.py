from ..EmitNode import *

class EmitSceneNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    def add_group(self):
        """Add a new scene group"""
        return self._add_child_node("Group")

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
        val = self.GroundPlaneNormalOption[val]
        return val

    @ground_plane_normal.setter
    def ground_plane_normal(self, value: GroundPlaneNormalOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Ground Plane Normal=' + value.value])

    @property
    def gp_position_along_normal(self) -> float:
        """GP Position Along Normal
        "Offset of ground plane in direction normal to the ground planes orientation."
        "        """
        val = self._get_property('GP Position Along Normal')
        return val

    @gp_position_along_normal.setter
    def gp_position_along_normal(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['GP Position Along Normal=' + value])

