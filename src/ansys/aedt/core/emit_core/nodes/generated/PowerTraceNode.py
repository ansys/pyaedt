from ..GenericEmitNode import *
class PowerTraceNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

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
    def direction(self):
        """Direction
        "Direction of power flow (towards or away from the transmitter) to plot."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Direction')
        key_val_pair = [i for i in props if 'Direction=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @direction.setter
    def direction(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Direction=' + value])
    class DirectionOption(Enum):
            AWAY = "Away From Tx"
            TOWARD = "Toward Tx"

    @property
    def data_source(self):
        """Data Source
        "Identifies tree node serving as data source for plot trace, click link to find it."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Data Source')
        key_val_pair = [i for i in props if 'Data Source=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @data_source.setter
    def data_source(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Data Source=' + value])

    @property
    def visible(self) -> bool:
        """Visible
        "Toggle (on/off) display of this plot trace."
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
    def custom_legend(self) -> bool:
        """Custom Legend
        "Enable/disable custom legend entry for this plot trace."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Custom Legend')
        key_val_pair = [i for i in props if 'Custom Legend=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @custom_legend.setter
    def custom_legend(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Custom Legend=' + value])

    @property
    def name(self) -> str:
        """Name
        "Enter name of plot trace as it will appear in legend."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Name')
        key_val_pair = [i for i in props if 'Name=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @name.setter
    def name(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Name=' + value])

    @property
    def style(self):
        """Style
        "Specify line style of plot trace."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Style')
        key_val_pair = [i for i in props if 'Style=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @style.setter
    def style(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Style=' + value])
    class StyleOption(Enum):
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"

    @property
    def line_width(self) -> int:
        """Line Width
        "Specify line width of plot trace."
        "Value should be between 1 and 100."
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
    def line_color(self):
        """Line Color
        "Specify line color of plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Line Color')
        key_val_pair = [i for i in props if 'Line Color=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @line_color.setter
    def line_color(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Line Color=' + value])

    @property
    def symbol(self):
        """Symbol
        "Select symbol to mark points along plot trace."
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

    @property
    def symbol_size(self) -> int:
        """Symbol Size
        "Set size (in points) of symbols marking points along plot trace."
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
        "Specify color of symbols marking points along plot trace."
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
    def symbol_line_width(self) -> int:
        """Symbol Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Line Width')
        key_val_pair = [i for i in props if 'Symbol Line Width=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @symbol_line_width.setter
    def symbol_line_width(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Line Width=' + value])

    @property
    def symbol_filled(self) -> bool:
        """Symbol Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Symbol Filled')
        key_val_pair = [i for i in props if 'Symbol Filled=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @symbol_filled.setter
    def symbol_filled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Symbol Filled=' + value])

