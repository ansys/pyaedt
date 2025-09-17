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

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


class ResultPlotNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def add_marker(self):
        """Add an icon and/or label to this plot"""
        return self._add_child_node("Plot Marker")

    def export_model(self, file_name):
        """Save this data to a file"""
        return self._export_model(file_name)

    @property
    def title(self) -> str:
        """Enter title at the top of the plot, room will be made for it."""
        val = self._get_property("Title")
        return val

    @title.setter
    def title(self, value: str):
        self._set_property("Title", f"{value}")

    @property
    def title_font(self):
        """Configure title font family, typeface, and size.

        Value formatted like 'Sans Serif,10,-1,5,50,0,0,0,0,0'.
        """
        val = self._get_property("Title Font")
        return val

    @title_font.setter
    def title_font(self, value):
        self._set_property("Title Font", f"{value}")

    @property
    def show_legend(self) -> bool:
        """Toggle (on/off) display of plot legend.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show Legend")
        return val == "true"

    @show_legend.setter
    def show_legend(self, value: bool):
        self._set_property("Show Legend", f"{str(value).lower()}")

    @property
    def legend_font(self):
        """Configure legend font family, typeface, and size.

        Value formatted like 'Sans Serif,10,-1,5,50,0,0,0,0,0'.
        """
        val = self._get_property("Legend Font")
        return val

    @legend_font.setter
    def legend_font(self, value):
        self._set_property("Legend Font", f"{value}")

    @property
    def show_emi_thresholds(self) -> bool:
        """Toggles on/off visibility of the EMI Thresholds.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Show EMI Thresholds")
        return val == "true"

    @show_emi_thresholds.setter
    def show_emi_thresholds(self, value: bool):
        self._set_property("Show EMI Thresholds", f"{str(value).lower()}")

    @property
    def display_cad_overlay(self) -> bool:
        """Toggle on/off overlay of CAD model in plot.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Display CAD Overlay")
        return val == "true"

    @display_cad_overlay.setter
    def display_cad_overlay(self, value: bool):
        self._set_property("Display CAD Overlay", f"{str(value).lower()}")

    @property
    def opacity(self) -> float:
        """Adjust opacity of CAD model overlay: 0 Transparent - 1 Opaque.

        Value should be between 0 and 100.
        """
        val = self._get_property("Opacity")
        return float(val)

    @opacity.setter
    def opacity(self, value: float):
        self._set_property("Opacity", f"{value}")

    @property
    def vertical_offset(self) -> float:
        """Adjust vertical position of CAD model overlay."""
        val = self._get_property("Vertical Offset")
        return float(val)

    @vertical_offset.setter
    def vertical_offset(self, value: float):
        self._set_property("Vertical Offset", f"{value}")

    @property
    def range_axis_rotation(self) -> float:
        """Range Axis Rotation.

        Adjust view angle for CAD model overlay by rotating it about plot
        horizontal axis.

        Value should be between -180 and 180.
        """
        val = self._get_property("Range Axis Rotation")
        return float(val)

    @range_axis_rotation.setter
    def range_axis_rotation(self, value: float):
        self._set_property("Range Axis Rotation", f"{value}")

    @property
    def lock_axes(self) -> bool:
        """Lock Axes.

        Allow or prevent changing of axes when displayed plot traces are
        updated.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Lock Axes")
        return val == "true"

    @lock_axes.setter
    def lock_axes(self, value: bool):
        self._set_property("Lock Axes", f"{str(value).lower()}")

    @property
    def x_axis_min(self) -> float:
        """Set lower extent of horizontal axis."""
        val = self._get_property("X-axis Min")
        return float(val)

    @x_axis_min.setter
    def x_axis_min(self, value: float):
        self._set_property("X-axis Min", f"{value}")

    @property
    def x_axis_max(self) -> float:
        """Set upper extent of horizontal axis."""
        val = self._get_property("X-axis Max")
        return float(val)

    @x_axis_max.setter
    def x_axis_max(self, value: float):
        self._set_property("X-axis Max", f"{value}")

    @property
    def y_axis_min(self) -> float:
        """Set lower extent of vertical axis."""
        val = self._get_property("Y-axis Min")
        return float(val)

    @y_axis_min.setter
    def y_axis_min(self, value: float):
        self._set_property("Y-axis Min", f"{value}")

    @property
    def y_axis_max(self) -> float:
        """Set upper extent of vertical axis."""
        val = self._get_property("Y-axis Max")
        return float(val)

    @y_axis_max.setter
    def y_axis_max(self, value: float):
        self._set_property("Y-axis Max", f"{value}")

    @property
    def y_axis_range(self) -> float:
        """Y-axis Range.

        Adjust dB span of vertical axis, makes corresponding adjustment in
        Y-axis Min.

        Value should be greater than 0.
        """
        val = self._get_property("Y-axis Range")
        return float(val)

    @y_axis_range.setter
    def y_axis_range(self, value: float):
        self._set_property("Y-axis Range", f"{value}")

    @property
    def max_major_ticks_x(self) -> int:
        """Max Major Ticks X.

        Set maximum number of major tick-mark intervals along horizontal axis.

        Value should be between 1 and 30.
        """
        val = self._get_property("Max Major Ticks X")
        return int(val)

    @max_major_ticks_x.setter
    def max_major_ticks_x(self, value: int):
        self._set_property("Max Major Ticks X", f"{value}")

    @property
    def max_minor_ticks_x(self) -> int:
        """Max Minor Ticks X.

        Set maximum number of minor tick-mark intervals between major ticks
        along horizontal axis.

        Value should be between 0 and 100.
        """
        val = self._get_property("Max Minor Ticks X")
        return int(val)

    @max_minor_ticks_x.setter
    def max_minor_ticks_x(self, value: int):
        self._set_property("Max Minor Ticks X", f"{value}")

    @property
    def max_major_ticks_y(self) -> int:
        """Max Major Ticks Y.

        Set maximum number of major tick-mark intervals along vertical axis.

        Value should be between 1 and 30.
        """
        val = self._get_property("Max Major Ticks Y")
        return int(val)

    @max_major_ticks_y.setter
    def max_major_ticks_y(self, value: int):
        self._set_property("Max Major Ticks Y", f"{value}")

    @property
    def max_minor_ticks_y(self) -> int:
        """Max Minor Ticks Y.

        Set maximum number of minor tick-mark intervals between major ticks
        along vertical axis.

        Value should be between 0 and 100.
        """
        val = self._get_property("Max Minor Ticks Y")
        return int(val)

    @max_minor_ticks_y.setter
    def max_minor_ticks_y(self, value: int):
        self._set_property("Max Minor Ticks Y", f"{value}")

    @property
    def axis_label_font(self):
        """Configure axis text labels font family, typeface, and size.

        Value formatted like 'Sans Serif,10,-1,5,50,0,0,0,0,0'.
        """
        val = self._get_property("Axis Label Font")
        return val

    @axis_label_font.setter
    def axis_label_font(self, value):
        self._set_property("Axis Label Font", f"{value}")

    @property
    def axis_tick_label_font(self):
        """Configure axis tick numeric labels font family, typeface, and size.

        Value formatted like 'Sans Serif,10,-1,5,50,0,0,0,0,0'.
        """
        val = self._get_property("Axis Tick Label Font")
        return val

    @axis_tick_label_font.setter
    def axis_tick_label_font(self, value):
        self._set_property("Axis Tick Label Font", f"{value}")

    class MajorGridLineStyleOption(Enum):
        LINES = "Lines"
        DOTTED = "Dotted"
        DASHED = "Dashed"
        DOT_DASH = "Dot-Dash"
        DOT_DOT_DASH = "Dot-Dot-Dash"
        NONE = "None"

    @property
    def major_grid_line_style(self) -> MajorGridLineStyleOption:
        """Select line style of major-tick grid lines."""
        val = self._get_property("Major Grid Line Style")
        val = self.MajorGridLineStyleOption[val.upper()]
        return val

    @major_grid_line_style.setter
    def major_grid_line_style(self, value: MajorGridLineStyleOption):
        self._set_property("Major Grid Line Style", f"{value.value}")

    @property
    def major_grid_color(self):
        """Set color of major-tick grid lines.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Major Grid Color")
        return val

    @major_grid_color.setter
    def major_grid_color(self, value):
        self._set_property("Major Grid Color", f"{value}")

    class MinorGridLineStyleOption(Enum):
        LINES = "Lines"
        DOTTED = "Dotted"
        DASHED = "Dashed"
        DOT_DASH = "Dot-Dash"
        DOT_DOT_DASH = "Dot-Dot-Dash"
        NONE = "None"

    @property
    def minor_grid_line_style(self) -> MinorGridLineStyleOption:
        """Select line style of minor-tick grid lines."""
        val = self._get_property("Minor Grid Line Style")
        val = self.MinorGridLineStyleOption[val.upper()]
        return val

    @minor_grid_line_style.setter
    def minor_grid_line_style(self, value: MinorGridLineStyleOption):
        self._set_property("Minor Grid Line Style", f"{value.value}")

    @property
    def minor_grid_color(self):
        """Set color of minor-tick grid lines.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Minor Grid Color")
        return val

    @minor_grid_color.setter
    def minor_grid_color(self, value):
        self._set_property("Minor Grid Color", f"{value}")

    @property
    def background_color(self):
        """Set background color of entire plot.

        Color should be in RGB form: #RRGGBB.
        """
        val = self._get_property("Background Color")
        return val

    @background_color.setter
    def background_color(self, value):
        self._set_property("Background Color", f"{value}")

    class BBPowerforPlotsUnitOption(Enum):
        HERTZ = "hertz"
        KILOHERTZ = "kilohertz"
        MEGAHERTZ = "megahertz"
        GIGAHERTZ = "gigahertz"

    @property
    def bb_power_for_plots_unit(self) -> BBPowerforPlotsUnitOption:
        """Units to use for plotting broadband power densities."""
        val = self._get_property("BB Power for Plots Unit")
        val = self.BBPowerforPlotsUnitOption[val.upper()]
        return val

    @bb_power_for_plots_unit.setter
    def bb_power_for_plots_unit(self, value: BBPowerforPlotsUnitOption):
        self._set_property("BB Power for Plots Unit", f"{value.value}")

    @property
    def bb_power_bandwidth(self) -> float:
        """Resolution bandwidth for broadband power.

        Value should be between 1.0 and 100e9.
        """
        val = self._get_property("BB Power Bandwidth")
        val = self._convert_from_internal_units(float(val), "")
        return float(val)

    @bb_power_bandwidth.setter
    def bb_power_bandwidth(self, value: float | str):
        value = self._convert_to_internal_units(value, "")
        self._set_property("BB Power Bandwidth", f"{value}")

    @property
    def log_scale(self) -> bool:
        """Toggles on/off using a log scale for the X-Axis.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Log Scale")
        return val == "true"

    @log_scale.setter
    def log_scale(self, value: bool):
        self._set_property("Log Scale", f"{str(value).lower()}")
