from ..GenericEmitNode import *
class EmitSceneNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def add_group(self):
        """Add a new scene group"""
        return self._add_child_node("sceneGroupNode")

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
    def ground_plane_normal(self):
        """Ground Plane Normal
        "Specifies the axis of the normal to the ground plane."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Ground Plane Normal')
        key_val_pair = [i for i in props if 'Ground Plane Normal=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @ground_plane_normal.setter
    def ground_plane_normal(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Ground Plane Normal=' + value])
    class GroundPlaneNormalOption(Enum):
            XAXIS = "X Axis"
            YAXIS = "Y Axis"
            ZAXIS = "Z Axis"

    @property
    def gp_position_along_normal(self) -> float:
        """GP Position Along Normal
        "Offset of ground plane in direction normal to the ground planes orientation."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'GP Position Along Normal')
        key_val_pair = [i for i in props if 'GP Position Along Normal=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @gp_position_along_normal.setter
    def gp_position_along_normal(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['GP Position Along Normal=' + value])

