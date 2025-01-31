from ..GenericEmitNode import *
class ReadOnlySceneGroupNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def show_relative_coordinates(self) -> bool:
        """Show Relative Coordinates
        "Show Scene Group position and orientation in parent-node coords (False) or relative to placement coords (True)."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Relative Coordinates')
        key_val_pair = [i for i in props if 'Show Relative Coordinates=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def position(self):
        """Position
        "Set position of the Scene Group in parent-node coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')
        key_val_pair = [i for i in props if 'Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def relative_position(self):
        """Relative Position
        "Set position of the Scene Group relative to placement coordinates."
        "Value should be x/y/z, delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Position')
        key_val_pair = [i for i in props if 'Relative Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

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
    class OrientationModeOption(Enum):
            RPYDEG = "Roll-Pitch-Yaw"
            AETDEG = "Az-El-Twist"

    @property
    def orientation(self):
        """Orientation
        "Set orientation of the Scene Group relative to parent-node coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Orientation')
        key_val_pair = [i for i in props if 'Orientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def relative_orientation(self):
        """Relative Orientation
        "Set orientation of the Scene Group relative to placement coordinates."
        "Value format is determined by 'Orientation Mode', in degrees and delimited by spaces."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Relative Orientation')
        key_val_pair = [i for i in props if 'Relative Orientation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def show_axes(self) -> bool:
        """Show Axes
        "Toggle (on/off) display of Scene Group coordinate axes in 3-D window."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Show Axes')
        key_val_pair = [i for i in props if 'Show Axes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def box_color(self):
        """Box Color
        "Set color of the bounding box of the Scene Group."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Box Color')
        key_val_pair = [i for i in props if 'Box Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

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

