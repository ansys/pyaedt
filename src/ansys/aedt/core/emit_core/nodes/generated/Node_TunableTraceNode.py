class Node_TunableTraceNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def export_model(self, file_name):
        """Save this data to a file"""
        return self._export_model(file_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def get_input_port(self):
        """Input Port
        "Specifies input port for the plotted outboard component."
        "Value should be greater than 1."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Input Port')
    def set_input_port(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Input Port=' + value])

    @property
    def get_output_port(self):
        """Output Port
        "Specifies output port for the plotted outboard component."
        "Value should be greater than 1."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Output Port')
    def set_output_port(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Output Port=' + value])

    @property
    def get_frequency(self):
        """Frequency
        "Tunable filter center frequency."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Frequency')
    def set_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Frequency=' + value])

    @property
    def get_data_source(self):
        """Data Source
        "Identifies tree node serving as data source for plot trace, click link to find it."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Data Source')
    def set_data_source(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Data Source=' + value])

    @property
    def get_visible(self):
        """Visible
        "Toggle (on/off) display of this plot trace."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Visible')
    def set_visible(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Visible=' + value])

    @property
    def get_custom_legend(self):
        """Custom Legend
        "Enable/disable custom legend entry for this plot trace."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Custom Legend')
    def set_custom_legend(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Custom Legend=' + value])

    @property
    def get_name(self):
        """Name
        "Enter name of plot trace as it will appear in legend."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Name')
    def set_name(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Name=' + value])

    @property
    def get_style(self):
        """Style
        "Specify line style of plot trace."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Style')
    def set_style(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Style=' + value])
    class StyleOption(Enum):
        (
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"
        )

    @property
    def get_line_width(self):
        """Line Width
        "Specify line width of plot trace."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Line Width')
    def set_line_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Line Width=' + value])

    @property
    def get_line_color(self):
        """Line Color
        "Specify line color of plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Line Color')
    def set_line_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Line Color=' + value])

    @property
    def get_symbol(self):
        """Symbol
        "Select symbol to mark points along plot trace."
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
        )

    @property
    def get_symbol_size(self):
        """Symbol Size
        "Set size (in points) of symbols marking points along plot trace."
        "Value should be between 1 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Size')
    def set_symbol_size(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Size=' + value])

    @property
    def get_symbol_color(self):
        """Symbol Color
        "Specify color of symbols marking points along plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Color')
    def set_symbol_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Color=' + value])

    @property
    def get_symbol_line_width(self):
        """Symbol Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Line Width')
    def set_symbol_line_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Line Width=' + value])

    @property
    def get_symbol_filled(self):
        """Symbol Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Filled')
    def set_symbol_filled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Filled=' + value])

