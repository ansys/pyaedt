from ..EmitNode import *

class PlotMarkerNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    def __eq__(self, other):
      return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

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
        val = self._get_property('Visible')
        return val
    @visible.setter
    def visible(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Visible=' + value])

    @property
    def attached(self) -> bool:
        """Attached
        "Attach marker to a fixed X-Y point on the plot (True), or to a fixed point on the plot window (False)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Attached')
        return val
    @attached.setter
    def attached(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Attached=' + value])

    @property
    def position(self) -> float:
        """Position
        "Set position of the marker along the X-axis."
        "        """
        val = self._get_property('Position')
        return val
    @position.setter
    def position(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def position(self) -> float:
        """Position
        "Set position of the marker along the Y-axis."
        "        """
        val = self._get_property('Position')
        return val
    @position.setter
    def position(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position=' + value])

    @property
    def floating_label(self) -> bool:
        """Floating Label
        "Allow marker label to be positioned at a fixed point on the plot window (the marker symbol remains fixed to the specified X-Y point)."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Floating Label')
        return val
    @floating_label.setter
    def floating_label(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Floating Label=' + value])

    @property
    def position_from_left(self) -> float:
        """Position from Left
        "Set position of label from left to right as a percentage of the width of the plot window."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Position from Left')
        return val
    @position_from_left.setter
    def position_from_left(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position from Left=' + value])

    @property
    def position_from_top(self) -> float:
        """Position from Top
        "Set position of label from top to bottom as a percentage of the height of the plot window."
        "Value should be between 0 and 100."
        """
        val = self._get_property('Position from Top')
        return val
    @position_from_top.setter
    def position_from_top(self, value: float):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Position from Top=' + value])

    @property
    def text(self) -> str:
        """Text
        "Set the text of the label."
        "        """
        val = self._get_property('Text')
        return val
    @text.setter
    def text(self, value: str):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Text=' + value])

    class HorizontalPositionOption(Enum):
            LEFT = "Left"
            RIGHT = "Right"
            CENTER = "Center"
    @property
    def horizontal_position(self) -> HorizontalPositionOption:
        """Horizontal Position
        "Specify horizontal position of the label as compared to the symbol."
        "        """
        val = self._get_property('Horizontal Position')
        val = self.HorizontalPositionOption[val]
        return val
    @horizontal_position.setter
    def horizontal_position(self, value: HorizontalPositionOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Horizontal Position=' + value.value])

    class VerticalPositionOption(Enum):
            TOP = "Top"
            BOTTOM = "Bottom"
            CENTER = "Center"
    @property
    def vertical_position(self) -> VerticalPositionOption:
        """Vertical Position
        "Specify vertical position of the label as compared to the symbol."
        "        """
        val = self._get_property('Vertical Position')
        val = self.VerticalPositionOption[val]
        return val
    @vertical_position.setter
    def vertical_position(self, value: VerticalPositionOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Vertical Position=' + value.value])

    class TextAlignmentOption(Enum):
            LEFT = "Left"
            RIGHT = "Right"
            CENTER = "Center"
    @property
    def text_alignment(self) -> TextAlignmentOption:
        """Text Alignment
        "Specify justification applied to multi-line text."
        "        """
        val = self._get_property('Text Alignment')
        val = self.TextAlignmentOption[val]
        return val
    @text_alignment.setter
    def text_alignment(self, value: TextAlignmentOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Text Alignment=' + value.value])

    @property
    def font(self):
        """Font
        "Specify font used for the label."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        val = self._get_property('Font')
        return val
    @font.setter
    def font(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Font=' + value])

    @property
    def color(self):
        """Color
        "Specify color of the label text."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Color')
        return val
    @color.setter
    def color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Color=' + value])

    @property
    def background_color(self):
        """Background Color
        "Set color of the label text background."
        "Color should be in RGBA form: #AARRGGBB."
        """
        val = self._get_property('Background Color')
        return val
    @background_color.setter
    def background_color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Background Color=' + value])

    @property
    def border(self) -> bool:
        """Border
        "Display a border around the label text."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Border')
        return val
    @border.setter
    def border(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Border=' + value])

    @property
    def border_width(self) -> int:
        """Border Width
        "Set the width of the border around the label text."
        "Value should be between 1 and 20."
        """
        val = self._get_property('Border Width')
        return val
    @border_width.setter
    def border_width(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Border Width=' + value])

    @property
    def border_color(self):
        """Border Color
        "Set color of the border around the label text."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Border Color')
        return val
    @border_color.setter
    def border_color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Border Color=' + value])

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
    def symbol(self) -> SymbolOption:
        """Symbol
        "Specify symbol displayed next to the label."
        "        """
        val = self._get_property('Symbol')
        val = self.SymbolOption[val]
        return val
    @symbol.setter
    def symbol(self, value: SymbolOption):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Symbol=' + value.value])

    @property
    def arrow_direction(self) -> int:
        """Arrow Direction
        "Set direction of the arrow; zero degrees is up."
        "Value should be between -360 and 360."
        """
        val = self._get_property('Arrow Direction')
        return val
    @arrow_direction.setter
    def arrow_direction(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Arrow Direction=' + value])

    @property
    def symbol_size(self) -> int:
        """Symbol Size
        "Set size of the symbol used for this marker."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('Symbol Size')
        return val
    @symbol_size.setter
    def symbol_size(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Symbol Size=' + value])

    @property
    def symbol_color(self):
        """Symbol Color
        "Set color of the symbol used for this marker."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Symbol Color')
        return val
    @symbol_color.setter
    def symbol_color(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Symbol Color=' + value])

    @property
    def line_width(self) -> int:
        """Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        val = self._get_property('Line Width')
        return val
    @line_width.setter
    def line_width(self, value: int):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Line Width=' + value])

    @property
    def filled(self) -> bool:
        """Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Filled')
        return val
    @filled.setter
    def filled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Filled=' + value])

