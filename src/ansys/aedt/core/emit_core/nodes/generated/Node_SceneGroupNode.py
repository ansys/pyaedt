
from ..GenericEmitNode import GenericEmitNode
from enum import Enum

class Node_SceneGroupNode(GenericEmitNode):
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
    def get_show_relative_coordinates(self):
        """Show Relative Coordinates
        "Show Scene Group position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Show Relative Coordinates')
    def set_show_relative_coordinates(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Relative Coordinates=' + value])

    @property
    def get_position(self):
        """Position
        "Set position of the Scene Group in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Position')
    def set_position(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def get_relative_position(self):
        """Relative Position
        "Set position of the Scene Group relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Relative Position')
    def set_relative_position(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Relative Position=' + value])

    @property
    def get_orientation_mode(self):
        """Orientation Mode
        "Select the convention (order of rotations) for configuring orientation."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Orientation Mode')
    def set_orientation_mode(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation Mode=' + value])
    class OrientationModeOption(Enum):
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"

    @property
    def get_orientation(self):
        """Orientation
        "Set orientation of the Scene Group relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Orientation')
    def set_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation=' + value])

    @property
    def get_relative_orientation(self):
        """Relative Orientation
        "Set orientation of the Scene Group relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Relative Orientation')
    def set_relative_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Relative Orientation=' + value])

    @property
    def get_show_axes(self):
        """Show Axes
        "Toggle (on/off) display of Scene Group coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Show Axes')
    def set_show_axes(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Axes=' + value])

    @property
    def get_box_color(self):
        """Box Color
        "Set color of the bounding box of the Scene Group."
        "Color should be in RGB form: #RRGGBB."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Box Color')
    def set_box_color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Box Color=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Notes=' + value])

