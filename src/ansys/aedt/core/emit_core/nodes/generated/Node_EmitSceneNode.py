
from ..GenericEmitNode import GenericEmitNode
from enum import Enum

class Node_EmitSceneNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    @notes.setter
    def set_notes(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def get_ground_plane_normal(self):
        """Ground Plane Normal
        "Specifies the axis of the normal to the ground plane."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Ground Plane Normal')
    def set_ground_plane_normal(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Ground Plane Normal=' + value])
    class GroundPlaneNormalOption(Enum):
            XAXIS = "X Axis"
            YAXIS = "Y Axis"
            ZAXIS = "Z Axis"

    @property
    def get_gp_position_along_normal(self):
        """GP Position Along Normal
        "Offset of ground plane in direction normal to the ground planes orientation."
        "Value should be between unbounded and unbounded."
        """
        return self._oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'GP Position Along Normal')
    def set_gp_position_along_normal(self, value):
        self._oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['GP Position Along Normal=' + value])

