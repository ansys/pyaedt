from ..GenericEmitNode import *
class EmiPlotMarkerNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

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
    def visible(self) -> bool:
        """Visible
        "Toggle (on/off) this marker."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Visible')
        key_val_pair = [i for i in props if 'Visible=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @visible.setter
    def visible(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Visible=' + value])

    @property
    def attached(self):
        """Attached
        "Attach marker to a fixed X-Y point on the plot (True), or to a fixed point on the plot window (False)."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Attached')
        key_val_pair = [i for i in props if 'Attached=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @attached.setter
    def attached(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Attached=' + value])

    @property
    def position(self) -> float:
        """Position
        "Set position of the marker along the X-axis."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')
        key_val_pair = [i for i in props if 'Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def position(self) -> float:
        """Position
        "Set position of the marker along the Y-axis."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')
        key_val_pair = [i for i in props if 'Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def floating_label(self) -> bool:
        """Floating Label
        "Allow marker label to be positioned at a fixed point on the plot window (the marker symbol remains fixed to the specified X-Y point)."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Floating Label')
        key_val_pair = [i for i in props if 'Floating Label=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @floating_label.setter
    def floating_label(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Floating Label=' + value])

    @property
    def position_from_left(self) -> float:
        """Position from Left
        "Set position of label from left to right as a percentage of the width of the plot window."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position from Left')
        key_val_pair = [i for i in props if 'Position from Left=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @position_from_left.setter
    def position_from_left(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position from Left=' + value])

    @property
    def position_from_top(self) -> float:
        """Position from Top
        "Set position of label from top to bottom as a percentage of the height of the plot window."
        "Value should be between 0 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position from Top')
        key_val_pair = [i for i in props if 'Position from Top=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @position_from_top.setter
    def position_from_top(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position from Top=' + value])

    @property
    def text(self) -> str:
        """Text
        "Set the text of the label."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Text')
        key_val_pair = [i for i in props if 'Text=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @text.setter
    def text(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Text=' + value])

    @property
    def horizontal_position(self):
        """Horizontal Position
        "Specify horizontal position of the label as compared to the symbol."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Horizontal Position')
        key_val_pair = [i for i in props if 'Horizontal Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @horizontal_position.setter
    def horizontal_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Horizontal Position=' + value])
    class HorizontalPositionOption(Enum):
            LEFT = "Left"
            RIGHT = "Right"
            CENTER = "Center"

    @property
    def vertical_position(self):
        """Vertical Position
        "Specify vertical position of the label as compared to the symbol."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Vertical Position')
        key_val_pair = [i for i in props if 'Vertical Position=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @vertical_position.setter
    def vertical_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Vertical Position=' + value])
    class VerticalPositionOption(Enum):
            TOP = "Top"
            BOTTOM = "Bottom"
            CENTER = "Center"

    @property
    def text_alignment(self):
        """Text Alignment
        "Specify justification applied to multi-line text."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Text Alignment')
        key_val_pair = [i for i in props if 'Text Alignment=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @text_alignment.setter
    def text_alignment(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Text Alignment=' + value])
    class TextAlignmentOption(Enum):
            LEFT = "Left"
            RIGHT = "Right"
            CENTER = "Center"

    @property
    def font(self):
        """Font
        "Specify font used for the label."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Font')
        key_val_pair = [i for i in props if 'Font=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @font.setter
    def font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Font=' + value])

    @property
    def color(self):
        """Color
        "Specify color of the label text."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Color')
        key_val_pair = [i for i in props if 'Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @color.setter
    def color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Color=' + value])

    @property
    def background_color(self):
        """Background Color
        "Set color of the label text background."
        "Color should be in RGBA form: #AARRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Background Color')
        key_val_pair = [i for i in props if 'Background Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @background_color.setter
    def background_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Background Color=' + value])

    @property
    def border(self) -> bool:
        """Border
        "Display a border around the label text."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Border')
        key_val_pair = [i for i in props if 'Border=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @border.setter
    def border(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Border=' + value])

    @property
    def border_width(self) -> int:
        """Border Width
        "Set the width of the border around the label text."
        "Value should be between 1 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Border Width')
        key_val_pair = [i for i in props if 'Border Width=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @border_width.setter
    def border_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Border Width=' + value])

    @property
    def border_color(self):
        """Border Color
        "Set color of the border around the label text."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Border Color')
        key_val_pair = [i for i in props if 'Border Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @border_color.setter
    def border_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Border Color=' + value])

    @property
    def symbol(self):
        """Symbol
        "Specify symbol displayed next to the label."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol')
        key_val_pair = [i for i in props if 'Symbol=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @symbol.setter
    def symbol(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol=' + value])
    class SymbolOption(Enum):
            NOSYMBOL = "NoSymbol"
            ELLIPSE = "Ellipse"
            RECT = "Rect"
            DIAMOND = "Diamond"
            TRIANGLE = "Triangle"
            DTRIANGLE = "DTriangle"
            LTRIANGLE = "LTriangle"
            RTRIANGLE = "RTriangle"
            CROSS = "Cross"
            XCROSS = "XCross"
            HLINE = "HLine"
            VLINE = "VLine"
            STAR1 = "Star1"
            STAR2 = "Star2"
            HEXAGON = "Hexagon"
            ARROW = "Arrow"

    @property
    def arrow_direction(self) -> int:
        """Arrow Direction
        "Set direction of the arrow; zero degrees is up."
        "Value should be between -360 and 360."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Arrow Direction')
        key_val_pair = [i for i in props if 'Arrow Direction=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @arrow_direction.setter
    def arrow_direction(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Arrow Direction=' + value])

    @property
    def symbol_size(self) -> int:
        """Symbol Size
        "Set size of the symbol used for this marker."
        "Value should be between 1 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Size')
        key_val_pair = [i for i in props if 'Symbol Size=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @symbol_size.setter
    def symbol_size(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Size=' + value])

    @property
    def symbol_color(self):
        """Symbol Color
        "Set color of the symbol used for this marker."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Color')
        key_val_pair = [i for i in props if 'Symbol Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @symbol_color.setter
    def symbol_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Color=' + value])

    @property
    def line_width(self) -> int:
        """Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Line Width')
        key_val_pair = [i for i in props if 'Line Width=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @line_width.setter
    def line_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Line Width=' + value])

    @property
    def filled(self) -> bool:
        """Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filled')
        key_val_pair = [i for i in props if 'Filled=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @filled.setter
    def filled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filled=' + value])

