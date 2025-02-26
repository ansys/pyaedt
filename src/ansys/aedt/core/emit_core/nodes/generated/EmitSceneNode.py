from ..EmitNode import *

class EmitSceneNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Notes=' + value])

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
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Ground Plane Normal=' + value.value])

    @property
    def gp_position_along_normal(self) -> float:
        """GP Position Along Normal
        "Offset of ground plane in direction normal to the ground planes orientation."
        "Units options: pm, nm, um, mm, cm, dm, meter, meters, km, mil, in, ft, yd."
        "        """
        val = self._get_property('GP Position Along Normal')
        val = self._convert_from_default_units(float(val), "Length Unit")
        return val

    @gp_position_along_normal.setter
    def gp_position_along_normal(self, value : float|str):
        value = self._convert_to_default_units(value, "Length Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['GP Position Along Normal=' + f"{value}"])

