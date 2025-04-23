# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from enum import Enum

from ..EmitNode import EmitNode


class OutboardTraceNode(EmitNode):
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
        val = self._get_property("Input Port")
        return val  # type: ignore

    @input_port.setter
    def input_port(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Input Port={value}"])

    @property
    def output_port(self) -> int:
        """Output Port
        "Specifies output port for the plotted outboard component."
        "Value should be greater than 1."
        """
        val = self._get_property("Output Port")
        return val  # type: ignore

    @output_port.setter
    def output_port(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Output Port={value}"])

    @property
    def data_source(self):
        """Data Source
        "Identifies tree node serving as data source for plot trace, click link to find it."
        " """
        val = self._get_property("Data Source")
        return val  # type: ignore

    @data_source.setter
    def data_source(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Data Source={value}"])

    @property
    def visible(self) -> bool:
        """Visible
        "Toggle (on/off) display of this plot trace."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Visible")
        return val  # type: ignore

    @visible.setter
    def visible(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Visible={value}"])

    @property
    def custom_legend(self) -> bool:
        """Custom Legend
        "Enable/disable custom legend entry for this plot trace."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Custom Legend")
        return val  # type: ignore

    @custom_legend.setter
    def custom_legend(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Custom Legend={value}"])

    @property
    def name(self) -> str:
        """Name
        "Enter name of plot trace as it will appear in legend."
        " """
        val = self._get_property("Name")
        return val  # type: ignore

    @name.setter
    def name(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Name={value}"])

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
        " """
        val = self._get_property("Style")
        val = self.StyleOption[val]
        return val  # type: ignore

    @style.setter
    def style(self, value: StyleOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Style={value.value}"])

    @property
    def line_width(self) -> int:
        """Line Width
        "Specify line width of plot trace."
        "Value should be between 1 and 100."
        """
        val = self._get_property("Line Width")
        return val  # type: ignore

    @line_width.setter
    def line_width(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Line Width={value}"])

    @property
    def line_color(self):
        """Line Color
        "Specify line color of plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property("Line Color")
        return val  # type: ignore

    @line_color.setter
    def line_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Line Color={value}"])

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
        " """
        val = self._get_property("Symbol")
        val = self.SymbolOption[val]
        return val  # type: ignore

    @symbol.setter
    def symbol(self, value: SymbolOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol={value.value}"])

    @property
    def symbol_size(self) -> int:
        """Symbol Size
        "Set size (in points) of symbols marking points along plot trace."
        "Value should be between 1 and 1000."
        """
        val = self._get_property("Symbol Size")
        return val  # type: ignore

    @symbol_size.setter
    def symbol_size(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol Size={value}"])

    @property
    def symbol_color(self):
        """Symbol Color
        "Specify color of symbols marking points along plot trace."
        "Color should be in RGB form: #RRGGBB."
        """
        val = self._get_property("Symbol Color")
        return val  # type: ignore

    @symbol_color.setter
    def symbol_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol Color={value}"])

    @property
    def symbol_line_width(self) -> int:
        """Symbol Line Width
        "Set the width of the line used to draw the symbol."
        "Value should be between 1 and 20."
        """
        val = self._get_property("Symbol Line Width")
        return val  # type: ignore

    @symbol_line_width.setter
    def symbol_line_width(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol Line Width={value}"])

    @property
    def symbol_filled(self) -> bool:
        """Symbol Filled
        "If true, the interior of the symbol is filled - has no effect for some symbol types."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property("Symbol Filled")
        return val  # type: ignore

    @symbol_filled.setter
    def symbol_filled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol Filled={value}"])
