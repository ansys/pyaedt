from ..EmitNode import *

class TestNoiseTraceNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

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
    def input_port(self) -> int:
        """Input Port
        "Specifies input port for the plotted outboard component."
        "Value should be greater than 1."
        """
        val = self._get_property('Input Port')
        return val

    @input_port.setter
    def input_port(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Input Port=' + value])

    @property
    def output_port(self) -> int:
        """Output Port
        "Specifies output port for the plotted outboard component."
        "Value should be greater than 1."
        """
        val = self._get_property('Output Port')
        return val

    @output_port.setter
    def output_port(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Output Port=' + value])

    @property
    def data_source(self):
        """Data Source
        "Identifies tree node serving as data source for plot trace, click link to find it."
        "        """
        val = self._get_property('Data Source')
        return val

    @data_source.setter
    def data_source(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Data Source=' + value])

    @property
    def visible(self) -> bool:
        """Visible
        "Toggle (on/off) display of this plot trace."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Visible')
        return val

    @visible.setter
    def visible(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Visible=' + value])

    @property
    def custom_legend(self) -> bool:
        """Custom Legend
        "Enable/disable custom legend entry for this plot trace."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Custom Legend')
        return val

    @custom_legend.setter
    def custom_legend(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Custom Legend=' + value])

    @property
    def name(self) -> str:
        """Name
        "Enter name of plot trace as it will appear in legend."
        "        """
        val = self._get_property('Name')
        return val

    @name.setter
    def name(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Name=' + value])

    class StyleOption(Enum):
            LINES = "Lines"
            DOTTED = "Dotted"
            DASHED = "Dashed"
            DOT_DASH = "Dot-Dash"
            DOT_DOT_DASH = "Dot-Dot-Dash"
            NONE = "None"

    @property
    def style(self) -> StyleOption:
        """Style
        "Specify line style of plot trace."
        "        """
        val = self._get_property('Style')
        val = self.StyleOption[val]
        return val

    @style.setter
    def style(self, value: StyleOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Style=' + value.value])

    @property
    def line_width(self) -> int:
        """Line Width
        "Specify line width of plot trace."
        "Value should be between 1 and 100."
        """
        val = self._get_property('Line Width')
        return val

    @line_width.setter
    def line_width(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Line Width=' + value])

    @property
    def line_color(self):
        """Line Color
        "Specify line color of plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Line Color')
        return val

    @line_color.setter
    def line_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Line Color=' + value])

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
    def symbol(self) -> SymbolOption:
        """Symbol
        "Select symbol to mark points along plot trace."
        "        """
        val = self._get_property('Symbol')
        val = self.SymbolOption[val]
        return val

    @symbol.setter
    def symbol(self, value: SymbolOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Symbol=' + value.value])

    @property
    def symbol_size(self) -> int:
        """Symbol Size
        "Set size (in points) of symbols marking points along plot trace."
        "Value should be between 1 and 1000."
        """
        val = self._get_property('Symbol Size')
        return val

    @symbol_size.setter
    def symbol_size(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Symbol Size=' + value])

    @property
    def symbol_color(self):
        """Symbol Color
        "Specify color of symbols marking points along plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property('Symbol Color')
        return val

    @symbol_color.setter
    def symbol_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Symbol Color=' + value])

    @property
    def symbol_line_width(self) -> int:
        """Symbol Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        val = self._get_property('Symbol Line Width')
        return val

    @symbol_line_width.setter
    def symbol_line_width(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Symbol Line Width=' + value])

    @property
    def symbol_filled(self) -> bool:
        """Symbol Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Symbol Filled')
        return val

    @symbol_filled.setter
    def symbol_filled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Symbol Filled=' + value])

    @property
    def frequency_1(self) -> float:
        """Frequency 1
        "1st test tone frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Frequency 1')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @frequency_1.setter
    def frequency_1(self, value : float|str):
        value = self._convert_to_default_units(value, "Freq Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Frequency 1=' + f"{value}"])

    @property
    def amplitude_1(self) -> float:
        """Amplitude 1
        "1st test tone amplitude."
        "Units options: fW, pW, nW, uW, mW, W, kW, megW, gW, dBm, dBW."
        "Value should be between -100 and 200."
        """
        val = self._get_property('Amplitude 1')
        val = self._convert_from_default_units(float(val), "Power Unit")
        return val

    @amplitude_1.setter
    def amplitude_1(self, value : float|str):
        value = self._convert_to_default_units(value, "Power Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Amplitude 1=' + f"{value}"])

    @property
    def bandwidth_1(self) -> float:
        """Bandwidth 1
        "1st test tone bandwidth."
        "Value should be greater than 1."
        """
        val = self._get_property('Bandwidth 1')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @bandwidth_1.setter
    def bandwidth_1(self, value : float|str):
        value = self._convert_to_default_units(value, "Freq Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Bandwidth 1=' + f"{value}"])

    @property
    def frequency_2(self) -> float:
        """Frequency 2
        "2nd test tone frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property('Frequency 2')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @frequency_2.setter
    def frequency_2(self, value : float|str):
        value = self._convert_to_default_units(value, "Freq Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Frequency 2=' + f"{value}"])

    @property
    def amplitude_2(self) -> float:
        """Amplitude 2
        "2nd test tone amplitude."
        "Units options: fW, pW, nW, uW, mW, W, kW, megW, gW, dBm, dBW."
        "Value should be between -100 and 200."
        """
        val = self._get_property('Amplitude 2')
        val = self._convert_from_default_units(float(val), "Power Unit")
        return val

    @amplitude_2.setter
    def amplitude_2(self, value : float|str):
        value = self._convert_to_default_units(value, "Power Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Amplitude 2=' + f"{value}"])

    @property
    def bandwidth_2(self) -> float:
        """Bandwidth 2
        "2nd test tone bandwidth."
        "Value should be greater than 1."
        """
        val = self._get_property('Bandwidth 2')
        val = self._convert_from_default_units(float(val), "Freq Unit")
        return val

    @bandwidth_2.setter
    def bandwidth_2(self, value : float|str):
        value = self._convert_to_default_units(value, "Freq Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Bandwidth 2=' + f"{value}"])

    @property
    def noise_level(self) -> float:
        """Noise Level
        "Broadband noise level."
        "Value should be between -200 and 0."
        """
        val = self._get_property('Noise Level')
        return val

    @noise_level.setter
    def noise_level(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Noise Level=' + value])

