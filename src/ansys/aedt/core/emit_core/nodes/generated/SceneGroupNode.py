from ..EmitNode import *

class SceneGroupNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def add_group(self):
        """Add a new scene group"""
        return self._add_child_node("sceneGroupNode")

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
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        "Show Scene Group position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Relative Coordinates')
        return val
    @show_relative_coordinates.setter
    def show_relative_coordinates(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Relative Coordinates=' + value])

    @property
    def position(self):
        """Position
        "Set position of the Scene Group in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Position')
        return val
    @position.setter
    def position(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def relative_position(self):
        """Relative Position
        "Set position of the Scene Group relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        val = self._get_property('Relative Position')
        return val
    @relative_position.setter
    def relative_position(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Relative Position=' + value])

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
    @orientation_mode.setter
    def orientation_mode(self, value: OrientationModeOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation Mode=' + value.value])

    @property
    def orientation(self):
        """Orientation
        "Set orientation of the Scene Group relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Orientation')
        return val
    @orientation.setter
    def orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Orientation=' + value])

    @property
    def relative_orientation(self):
        """Relative Orientation
        "Set orientation of the Scene Group relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        val = self._get_property('Relative Orientation')
        return val
    @relative_orientation.setter
    def relative_orientation(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Relative Orientation=' + value])

    @property
    def show_axes(self) -> bool:
        """Show Axes
        "Toggle (on/off) display of Scene Group coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Show Axes')
        return val
    @show_axes.setter
    def show_axes(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Show Axes=' + value])

    @property
    def box_color(self):
        """Box Color
        "Set color of the bounding box of the Scene Group."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Box Color')
        return val
    @box_color.setter
    def box_color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Box Color=' + value])

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

