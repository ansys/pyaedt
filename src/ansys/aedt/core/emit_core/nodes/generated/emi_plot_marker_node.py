# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.internal.checks import min_aedt_version


class EmiPlotMarkerNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node."""
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    @property
    @min_aedt_version("2025.2")
    def visible(self) -> bool:
        """Toggle (on/off) this marker.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Visible")
        return val == "true"

    @visible.setter
    @min_aedt_version("2025.2")
    def visible(self, value: bool) -> None:
        self._set_property("Visible", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def position_x(self) -> float:
        """Position of the marker on the X-axis (frequency axis)."""
        val = self._get_property("Position X")
        return float(val)

    @property
    @min_aedt_version("2025.2")
    def position_y(self) -> float:
        """Position of the marker on the Y-axis (result axis)."""
        val = self._get_property("Position Y")
        return float(val)

    @property
    @min_aedt_version("2025.2")
    def floating_label(self) -> bool:
        """Floating Label.

        Allow marker label to be positioned at a fixed point on the plot window
        (the marker symbol remains fixed to the specified X-Y point).

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Floating Label")
        return val == "true"

    @floating_label.setter
    @min_aedt_version("2025.2")
    def floating_label(self, value: bool) -> None:
        self._set_property("Floating Label", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def position_from_left(self) -> float:
        """Position from Left.

        Set position of label from left to right as a percentage of the width of
        the plot window.

        Value should be between 0 and 100.
        """
        val = self._get_property("Position from Left")
        return float(val)

    @position_from_left.setter
    @min_aedt_version("2025.2")
    def position_from_left(self, value: float) -> None:
        self._set_property("Position from Left", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def position_from_top(self) -> float:
        """Position from Top.

        Set position of label from top to bottom as a percentage of the height
        of the plot window.

        Value should be between 0 and 100.
        """
        val = self._get_property("Position from Top")
        return float(val)

    @position_from_top.setter
    @min_aedt_version("2025.2")
    def position_from_top(self, value: float) -> None:
        self._set_property("Position from Top", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def text(self) -> str:
        """Set the text of the label."""
        val = self._get_property("Text")
        return val

    @text.setter
    @min_aedt_version("2025.2")
    def text(self, value: str) -> None:
        self._set_property("Text", f"{value}")

    class HorizontalPositionOption(Enum):
        LEFT = "Left"
        RIGHT = "Right"
        CENTER = "Center"

    @property
    @min_aedt_version("2025.2")
    def horizontal_position(self) -> HorizontalPositionOption:
        """Specify horizontal position of the label as compared to the symbol."""
        val = self._get_property("Horizontal Position")
        val = self.HorizontalPositionOption[val.upper()]
        return val

    @horizontal_position.setter
    @min_aedt_version("2025.2")
    def horizontal_position(self, value: HorizontalPositionOption) -> None:
        self._set_property("Horizontal Position", f"{value.value}")

    class VerticalPositionOption(Enum):
        TOP = "Top"
        BOTTOM = "Bottom"
        CENTER = "Center"

    @property
    @min_aedt_version("2025.2")
    def vertical_position(self) -> VerticalPositionOption:
        """Specify vertical position of the label as compared to the symbol."""
        val = self._get_property("Vertical Position")
        val = self.VerticalPositionOption[val.upper()]
        return val

    @vertical_position.setter
    @min_aedt_version("2025.2")
    def vertical_position(self, value: VerticalPositionOption) -> None:
        self._set_property("Vertical Position", f"{value.value}")

    class TextAlignmentOption(Enum):
        LEFT = "Left"
        RIGHT = "Right"
        CENTER = "Center"

    @property
    @min_aedt_version("2025.2")
    def text_alignment(self) -> TextAlignmentOption:
        """Specify justification applied to multi-line text."""
        val = self._get_property("Text Alignment")
        val = self.TextAlignmentOption[val.upper()]
        return val

    @text_alignment.setter
    @min_aedt_version("2025.2")
    def text_alignment(self, value: TextAlignmentOption) -> None:
        self._set_property("Text Alignment", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def font(self) -> str:
        """Specify font used for the label.

        Value formatted like 'Sans Serif,10,-1,5,50,0,0,0,0,0'.
        """
        val = self._get_property("Font")
        return val

    @font.setter
    @min_aedt_version("2025.2")
    def font(self, value: str) -> None:
        self._set_property("Font", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def color(self) -> str:
        """Specify color of the label text.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Color")
        return val

    @color.setter
    @min_aedt_version("2025.2")
    def color(self, value: str) -> None:
        self._set_property("Color", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def background_color(self) -> str:
        """Set color of the label text background.

        Color should be in RGBA form: #AARRGGBB.
        """
        val = self._get_property("Background Color")
        return val

    @background_color.setter
    @min_aedt_version("2025.2")
    def background_color(self, value: str) -> None:
        self._set_property("Background Color", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def border(self) -> bool:
        """Display a border around the label text.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Border")
        return val == "true"

    @border.setter
    @min_aedt_version("2025.2")
    def border(self, value: bool) -> None:
        self._set_property("Border", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def border_width(self) -> int:
        """Set the width of the border around the label text.

        Value should be between 1 and 20.
        """
        val = self._get_property("Border Width")
        return int(val)

    @border_width.setter
    @min_aedt_version("2025.2")
    def border_width(self, value: int) -> None:
        self._set_property("Border Width", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def border_color(self) -> str:
        """Set color of the border around the label text.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Border Color")
        return val

    @border_color.setter
    @min_aedt_version("2025.2")
    def border_color(self, value: str) -> None:
        self._set_property("Border Color", f"{value}")

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
    @min_aedt_version("2025.2")
    def symbol(self) -> SymbolOption:
        """Specify symbol displayed next to the label."""
        val = self._get_property("Symbol")
        val = self.SymbolOption[val.upper()]
        return val

    @symbol.setter
    @min_aedt_version("2025.2")
    def symbol(self, value: SymbolOption) -> None:
        self._set_property("Symbol", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def arrow_direction(self) -> int:
        """Set direction of the arrow; zero degrees is up.

        Value should be between -360 and 360.
        """
        val = self._get_property("Arrow Direction")
        return int(val)

    @arrow_direction.setter
    @min_aedt_version("2025.2")
    def arrow_direction(self, value: int) -> None:
        self._set_property("Arrow Direction", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def symbol_size(self) -> int:
        """Set size of the symbol used for this marker.

        Value should be between 1 and 1000.
        """
        val = self._get_property("Symbol Size")
        return int(val)

    @symbol_size.setter
    @min_aedt_version("2025.2")
    def symbol_size(self, value: int) -> None:
        self._set_property("Symbol Size", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def symbol_color(self) -> str:
        """Set color of the symbol used for this marker.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Symbol Color")
        return val

    @symbol_color.setter
    @min_aedt_version("2025.2")
    def symbol_color(self, value: str) -> None:
        self._set_property("Symbol Color", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def line_width(self) -> int:
        """Set the width of the line used to draw the symbol.

        Value should be between 1 and 20.
        """
        val = self._get_property("Line Width")
        return int(val)

    @line_width.setter
    @min_aedt_version("2025.2")
    def line_width(self, value: int) -> None:
        self._set_property("Line Width", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def filled(self) -> bool:
        """Filled.

        If true, the interior of the symbol is filled - has no effect for some
        symbol types.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Filled")
        return val == "true"

    @filled.setter
    @min_aedt_version("2025.2")
    def filled(self, value: bool) -> None:
        self._set_property("Filled", f"{str(value).lower()}")
