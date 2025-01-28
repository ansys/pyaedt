class Node_EmiPlotMarkerNode(GenericEmitNode):
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
    def get_visible(self):
        """Visible
        "Toggle (on/off) this marker."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Visible')
    def set_visible(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Visible=' + value])

    @property
    def get_attached(self):
        """Attached
        "Attach marker to a fixed X-Y point on the plot (True), or to a fixed point on the plot window (False)."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Attached')
    def set_attached(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Attached=' + value])

    @property
    def get_position(self):
        """Position
        "Set position of the marker along the X-axis."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')

    @property
    def get_position(self):
        """Position
        "Set position of the marker along the Y-axis."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position')

    @property
    def get_floating_label(self):
        """Floating Label
        "Allow marker label to be positioned at a fixed point on the plot window (the marker symbol remains fixed to the specified X-Y point)."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Floating Label')
    def set_floating_label(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Floating Label=' + value])

    @property
    def get_position_from_left(self):
        """Position from Left
        "Set position of label from left to right as a percentage of the width of the plot window."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position from Left')
    def set_position_from_left(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position from Left=' + value])

    @property
    def get_position_from_top(self):
        """Position from Top
        "Set position of label from top to bottom as a percentage of the height of the plot window."
        "Value should be between 0 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Position from Top')
    def set_position_from_top(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Position from Top=' + value])

    @property
    def get_text(self):
        """Text
        "Set the text of the label."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Text')
    def set_text(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Text=' + value])

    @property
    def get_horizontal_position(self):
        """Horizontal Position
        "Specify horizontal position of the label as compared to the symbol."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Horizontal Position')
    def set_horizontal_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Horizontal Position=' + value])
    class HorizontalPositionOption(Enum):
        (
            LEFT = "Left"
            RIGHT = "Right"
            CENTER = "Center"
        )

    @property
    def get_vertical_position(self):
        """Vertical Position
        "Specify vertical position of the label as compared to the symbol."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Vertical Position')
    def set_vertical_position(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Vertical Position=' + value])
    class VerticalPositionOption(Enum):
        (
            TOP = "Top"
            BOTTOM = "Bottom"
            CENTER = "Center"
        )

    @property
    def get_text_alignment(self):
        """Text Alignment
        "Specify justification applied to multi-line text."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Text Alignment')
    def set_text_alignment(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Text Alignment=' + value])
    class TextAlignmentOption(Enum):
        (
            LEFT = "Left"
            RIGHT = "Right"
            CENTER = "Center"
        )

    @property
    def get_font(self):
        """Font
        "Specify font used for the label."
        "Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Font')
    def set_font(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Font=' + value])

    @property
    def get_color(self):
        """Color
        "Specify color of the label text."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Color')
    def set_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Color=' + value])

    @property
    def get_background_color(self):
        """Background Color
        "Set color of the label text background."
        "Color should be in RGBA form: #AARRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Background Color')
    def set_background_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Background Color=' + value])

    @property
    def get_border(self):
        """Border
        "Display a border around the label text."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Border')
    def set_border(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Border=' + value])

    @property
    def get_border_width(self):
        """Border Width
        "Set the width of the border around the label text."
        "Value should be between 1 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Border Width')
    def set_border_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Border Width=' + value])

    @property
    def get_border_color(self):
        """Border Color
        "Set color of the border around the label text."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Border Color')
    def set_border_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Border Color=' + value])

    @property
    def get_symbol(self):
        """Symbol
        "Specify symbol displayed next to the label."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol')
    def set_symbol(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol=' + value])
    class SymbolOption(Enum):
        (
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
        )

    @property
    def get_arrow_direction(self):
        """Arrow Direction
        "Set direction of the arrow; zero degrees is up."
        "Value should be between -360 and 360."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Arrow Direction')
    def set_arrow_direction(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Arrow Direction=' + value])

    @property
    def get_symbol_size(self):
        """Symbol Size
        "Set size of the symbol used for this marker."
        "Value should be between 1 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Size')
    def set_symbol_size(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Size=' + value])

    @property
    def get_symbol_color(self):
        """Symbol Color
        "Set color of the symbol used for this marker."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Color')
    def set_symbol_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Color=' + value])

    @property
    def get_line_width(self):
        """Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Line Width')
    def set_line_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Line Width=' + value])

    @property
    def get_filled(self):
        """Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filled')
    def set_filled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filled=' + value])

