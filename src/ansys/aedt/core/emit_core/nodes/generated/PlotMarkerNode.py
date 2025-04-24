# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2021 - 2025 ANSYS, Inc. and /or its affiliates.
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


class PlotMarkerNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

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
        Toggle (on/off) this marker

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Visible")
        return val  # type: ignore

    @visible.setter
    def visible(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Visible={value}"])

    @property
    def attached(self) -> bool:
        """Attached
        Attach marker to a fixed X-Y point on the plot (True), or to a fixed
         point on the plot window (False)

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Attached")
        return val  # type: ignore

    @attached.setter
    def attached(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Attached={value}"])

    @property
    def position_x(self) -> float:
        """Position X
        Position of the marker on the X-axis (frequency axis).

        """
        val = self._get_property("Position X")
        return val  # type: ignore

    @position_x.setter
    def position_x(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Position X={value}"])

    @property
    def position_y(self) -> float:
        """Position Y
        Position of the marker on the Y-axis (result axis).

        """
        val = self._get_property("Position Y")
        return val  # type: ignore

    @position_y.setter
    def position_y(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Position Y={value}"])

    @property
    def floating_label(self) -> bool:
        """Floating Label
        Allow marker label to be positioned at a fixed point on the plot window
         (the marker symbol remains fixed to the specified X-Y point)

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Floating Label")
        return val  # type: ignore

    @floating_label.setter
    def floating_label(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Floating Label={value}"])

    @property
    def position_from_left(self) -> float:
        """Position from Left
        Set position of label from left to right as a percentage of the width of
         the plot window

        Value should be between 0 and 100.
        """
        val = self._get_property("Position from Left")
        return val  # type: ignore

    @position_from_left.setter
    def position_from_left(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Position from Left={value}"])

    @property
    def position_from_top(self) -> float:
        """Position from Top
        Set position of label from top to bottom as a percentage of the height
         of the plot window

        Value should be between 0 and 100.
        """
        val = self._get_property("Position from Top")
        return val  # type: ignore

    @position_from_top.setter
    def position_from_top(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Position from Top={value}"])

    @property
    def text(self) -> str:
        """Text
        Set the text of the label

        """
        val = self._get_property("Text")
        return val  # type: ignore

    @text.setter
    def text(self, value: str):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Text={value}"])

    class HorizontalPositionOption(Enum):
        LEFT = "Left"  # eslint-disable-line no-eval
        RIGHT = "Right"  # eslint-disable-line no-eval
        CENTER = "Center"  # eslint-disable-line no-eval

    @property
    def horizontal_position(self) -> HorizontalPositionOption:
        """Horizontal Position
        Specify horizontal position of the label as compared to the symbol

        """
        val = self._get_property("Horizontal Position")
        val = self.HorizontalPositionOption[val]
        return val  # type: ignore

    @horizontal_position.setter
    def horizontal_position(self, value: HorizontalPositionOption):
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, [f"Horizontal Position={value.value}"]
        )

    class VerticalPositionOption(Enum):
        TOP = "Top"  # eslint-disable-line no-eval
        BOTTOM = "Bottom"  # eslint-disable-line no-eval
        CENTER = "Center"  # eslint-disable-line no-eval

    @property
    def vertical_position(self) -> VerticalPositionOption:
        """Vertical Position
        Specify vertical position of the label as compared to the symbol

        """
        val = self._get_property("Vertical Position")
        val = self.VerticalPositionOption[val]
        return val  # type: ignore

    @vertical_position.setter
    def vertical_position(self, value: VerticalPositionOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Vertical Position={value.value}"])

    class TextAlignmentOption(Enum):
        LEFT = "Left"  # eslint-disable-line no-eval
        RIGHT = "Right"  # eslint-disable-line no-eval
        CENTER = "Center"  # eslint-disable-line no-eval

    @property
    def text_alignment(self) -> TextAlignmentOption:
        """Text Alignment
        Specify justification applied to multi-line text

        """
        val = self._get_property("Text Alignment")
        val = self.TextAlignmentOption[val]
        return val  # type: ignore

    @text_alignment.setter
    def text_alignment(self, value: TextAlignmentOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Text Alignment={value.value}"])

    @property
    def font(self):
        """Font
        Specify font used for the label

        Value formated like 'Sans Serif,10,-1,5,50,0,0,0,0,0'.
        """
        val = self._get_property("Font")
        return val  # type: ignore

    @font.setter
    def font(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Font={value}"])

    @property
    def color(self):
        """Color
        Specify color of the label text

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Color")
        return val  # type: ignore

    @color.setter
    def color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Color={value}"])

    @property
    def background_color(self):
        """Background Color
        Set color of the label text background

        Color should be in RGBA form: #AARRGGBB.
        """
        val = self._get_property("Background Color")
        return val  # type: ignore

    @background_color.setter
    def background_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Background Color={value}"])

    @property
    def border(self) -> bool:
        """Border
        Display a border around the label text

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Border")
        return val  # type: ignore

    @border.setter
    def border(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Border={value}"])

    @property
    def border_width(self) -> int:
        """Border Width
        Set the width of the border around the label text

        Value should be between 1 and 20.
        """
        val = self._get_property("Border Width")
        return val  # type: ignore

    @border_width.setter
    def border_width(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Border Width={value}"])

    @property
    def border_color(self):
        """Border Color
        Set color of the border around the label text

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Border Color")
        return val  # type: ignore

    @border_color.setter
    def border_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Border Color={value}"])

    class SymbolOption(Enum):
        NOSYMBOL = "NoSymbol"  # eslint-disable-line no-eval
        ELLIPSE = "Ellipse"  # eslint-disable-line no-eval
        RECT = "Rect"  # eslint-disable-line no-eval
        DIAMOND = "Diamond"  # eslint-disable-line no-eval
        TRIANGLE = "Triangle"  # eslint-disable-line no-eval
        DTRIANGLE = "DTriangle"  # eslint-disable-line no-eval
        LTRIANGLE = "LTriangle"  # eslint-disable-line no-eval
        RTRIANGLE = "RTriangle"  # eslint-disable-line no-eval
        CROSS = "Cross"  # eslint-disable-line no-eval
        XCROSS = "XCross"  # eslint-disable-line no-eval
        HLINE = "HLine"  # eslint-disable-line no-eval
        VLINE = "VLine"  # eslint-disable-line no-eval
        STAR1 = "Star1"  # eslint-disable-line no-eval
        STAR2 = "Star2"  # eslint-disable-line no-eval
        HEXAGON = "Hexagon"  # eslint-disable-line no-eval
        ARROW = "Arrow"  # eslint-disable-line no-eval

    @property
    def symbol(self) -> SymbolOption:
        """Symbol
        Specify symbol displayed next to the label

        """
        val = self._get_property("Symbol")
        val = self.SymbolOption[val]
        return val  # type: ignore

    @symbol.setter
    def symbol(self, value: SymbolOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol={value.value}"])

    @property
    def arrow_direction(self) -> int:
        """Arrow Direction
        Set direction of the arrow; zero degrees is up

        Value should be between -360 and 360.
        """
        val = self._get_property("Arrow Direction")
        return val  # type: ignore

    @arrow_direction.setter
    def arrow_direction(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Arrow Direction={value}"])

    @property
    def symbol_size(self) -> int:
        """Symbol Size
        Set size of the symbol used for this marker

        Value should be between 1 and 1000.
        """
        val = self._get_property("Symbol Size")
        return val  # type: ignore

    @symbol_size.setter
    def symbol_size(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol Size={value}"])

    @property
    def symbol_color(self):
        """Symbol Color
        Set color of the symbol used for this marker

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Symbol Color")
        return val  # type: ignore

    @symbol_color.setter
    def symbol_color(self, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Symbol Color={value}"])

    @property
    def line_width(self) -> int:
        """Line Width
        Set the width of the line used to draw the symbol

        Value should be between 1 and 20.
        """
        val = self._get_property("Line Width")
        return val  # type: ignore

    @line_width.setter
    def line_width(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Line Width={value}"])

    @property
    def filled(self) -> bool:
        """Filled
        If true, the interior of the symbol is filled - has no effect for some
         symbol types

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Filled")
        return val  # type: ignore

    @filled.setter
    def filled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Filled={value}"])
