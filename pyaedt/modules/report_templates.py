# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from collections import OrderedDict
import copy
import os
import re

from pyaedt.generic.constants import LineStyle
from pyaedt.generic.constants import SymbolStyle
from pyaedt.generic.constants import TraceType
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.geometry_operators import GeometryOperators


def _props_with_default(dict_in, key, default_value=None):
    return dict_in[key] if dict_in.get(key, None) is not None else default_value


class LimitLine(object):
    """Line Limit Management Class."""

    def __init__(self, report_setup, trace_name):
        self._oreport_setup = report_setup
        self.line_name = trace_name
        self.LINESTYLE = LineStyle()

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Limit Line", ["NAME:PropServers", self.line_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_line_properties(
        self, style=None, width=None, hatch_above=None, violation_emphasis=None, hatch_pixels=None, color=None
    ):
        """Set trace properties.

        Parameters
        ----------
        style : str, optional
            Style for the limit line. The default is ``None``. You can also use
            the ``LIFESTYLE`` property.
        width : int, optional
            Width of the limit line. The default is ``None``.
        hatch_above : bool
           Whether the hatch is above the limit line. The default is ``None``.
        violation_emphasis : bool
            Whether to add violation emphasis. The default is ``None``.
        hatch_pixels : int
            Number of pixels for the hatch. The default is ``None``.
        color : tuple, list
            Trace color as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if style:
            props.append(["NAME:Line Style", "Value:=", style])
        if width and isinstance(width, (int, float, str)):
            props.append(["NAME:Line Width", "Value:=", str(width)])
        if hatch_above is not None and isinstance(hatch_pixels, (int, str)):
            props.append(["NAME:Hatch Above", "Value:=", hatch_above])
        if hatch_pixels and isinstance(hatch_pixels, (int, str)):
            props.append(["NAME:Hatch Pixels", "Value:=", str(hatch_pixels)])
        if violation_emphasis:
            props.append(["NAME:Violation Emphasis", "Value:=", violation_emphasis])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)


class Note(object):
    """Note Management Class."""

    def __init__(self, report_setup, plot_note_name):
        self._oreport_setup = report_setup
        self.plot_note_name = plot_note_name

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        prop_server_name = self.plot_note_name
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Note", ["NAME:PropServers", prop_server_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_note_properties(
        self,
        text=None,
        back_color=None,
        background_visibility=None,
        border_color=None,
        border_visibility=None,
        border_width=None,
        font="Arial",
        font_size=12,
        italic=False,
        bold=False,
        color=(0, 0, 0),
    ):
        """Set note properties.

        Parameters
        ----------
        text : str, optional
            Style for the limit line. The default is ``None``. You can also use
            the ``LIFESTYLE`` property.
        back_color : int
            Background color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.
        background_visibility : bool
            Whether to view background. The default is ``None``.
        border_color : int
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.
        border_visibility : bool
            Whether to view text border. The default is ``None``.
            The default is ``None``.
        border_width : int
            Text boarder width.
            The default is ``None``.
        font : str, optional
            The default is ``None``.
        font_size : int, optional
            The default is ``None``.
        italic : bool
            Whether the text is italic.
            The default is ``None``.
        bold : bool
            Whether the text is bold.
            The default is ``None``.
        color : int =(0, 0, 0)
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if text:
            props.append(["NAME:Note Text", "Value:=", text])
        if back_color and isinstance(back_color, (list, tuple)) and len(back_color) == 3:
            props.append(["NAME:Back Color", "R:=", back_color[0], "G:=", back_color[1], "B:=", back_color[2]])
        if background_visibility is not None:
            props.append(["NAME:Background Visibility", "Value:=", background_visibility])
        if border_color and isinstance(border_color, (list, tuple)) and len(border_color) == 3:
            props.append(["NAME:Border Color", "R:=", border_color[0], "G:=", border_color[1], "B:=", border_color[2]])
        if border_visibility is not None:
            props.append(["NAME:Border Visibility", "Value:=", border_visibility])
        if border_width and isinstance(border_width, (int, float)):
            props.append(["NAME:Border Width", "Value:=", str(border_width)])

        font_props = [
            "NAME:Note Font",
            "Height:=",
            -1 * font_size - 2,
            "Width:=",
            0,
            "Escapement:=",
            0,
            "Orientation:=",
            0,
            "Weight:=",
            700 if bold else 400,
            "Italic:=",
            255 if italic else 0,
            "Underline:=",
            0,
            "StrikeOut:=",
            0,
            "CharSet:=",
            0,
            "OutPrecision:=",
            3,
            "ClipPrecision:=",
            2,
            "Quality:=",
            1,
            "PitchAndFamily:=",
            34,
            "FaceName:=",
            font,
            "R:=",
            color[0],
            "G:=",
            color[1],
            "B:=",
            color[2],
        ]
        props.append(font_props)
        return self._change_property(props)


class Trace(object):
    """Provides trace management."""

    def __init__(self, report_setup, aedt_name):
        self._oreport_setup = report_setup
        self.aedt_name = aedt_name
        self._name = None
        self.LINESTYLE = LineStyle()
        self.TRACETYPE = TraceType()
        self.SYMBOLSTYLE = SymbolStyle()

    @property
    def name(self):
        """Trace name.

        Returns
        -------
        str
            Trace name.
        """
        report_name = self.aedt_name.split(":")[0]
        traces_in_report = self._oreport_setup.GetReportTraceNames(report_name)
        for trace in traces_in_report:
            if trace + ":" in self.aedt_name:
                self._name = trace
        return self._name

    @name.setter
    def name(self, value):
        report_name = self.aedt_name.split(":")[0]
        prop_name = report_name + ":" + self.name

        self._oreport_setup.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Trace",
                    ["NAME:PropServers", prop_name],
                    ["NAME:ChangedProps", ["NAME:Specify Name", "Value:=", True]],
                ],
            ]
        )
        self._oreport_setup.ChangeProperty(
            [
                "NAME:AllTabs",
                ["NAME:Trace", ["NAME:PropServers", prop_name], ["NAME:ChangedProps", ["NAME:Name", "Value:=", value]]],
            ]
        )
        self.aedt_name.replace(self.name, value)
        self._name = value

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Attributes", ["NAME:PropServers", self.aedt_name], props_value]]
        )
        return True

    @pyaedt_function_handler(trace_style="style")
    def set_trace_properties(self, style=None, width=None, trace_type=None, color=None):
        """Set trace properties.

        Parameters
        ----------
        style : str, optional
            Style for the trace line. The default is ``None``. You can also use
            the ``LINESTYLE`` property.
        width : int, optional
            Width of the trace line. The default is ``None``.
        trace_type : str
            Type of the trace line. The default is ``None``. You can also use the ``TRACETYPE``
            property.
        color : tuple, list
            Trace line color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if style:
            props.append(["NAME:Line Style", "Value:=", style])
        if width and isinstance(width, (int, float, str)):
            props.append(["NAME:Line Width", "Value:=", str(width)])
        if trace_type:
            props.append(["NAME:Trace Type", "Value:=", trace_type])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)

    @pyaedt_function_handler()
    def set_symbol_properties(self, show=True, style=None, show_arrows=None, fill=None, color=None):
        """Set symbol properties.

        Parameters
        ----------
        show : bool, optional
            Whether to show the symbol. The default is ``True``.
        style : str, optional
           Style of the style. The default is ``None``. You can also use the ``SYMBOLSTYLE``
           property.
        show_arrows : bool, optional
            Whether to show arrows. The default is ``None``.
        fill : bool, optional
            Whether to fill the symbol with a color. The default is ``None``.
        color : tuple, list
            Symbol fill color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps", ["NAME:Show Symbol", "Value:=", show]]
        if style:
            props.append(["NAME:Symbol Style", "Value:=", style])
        if show_arrows:
            props.append(["NAME:Show Arrows", "Value:=", show_arrows])
        if fill:
            props.append(["NAME:Fill Symbol", "Value:=", fill])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Symbol Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)


class CommonReport(object):
    """Provides common reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        self._post = app
        self.props = OrderedDict()
        self.props["report_category"] = report_category
        self.setup = setup_name
        self.props["report_type"] = "Rectangular Plot"
        self.props["context"] = OrderedDict()
        self.props["context"]["domain"] = "Sweep"
        self.props["context"]["primary_sweep"] = "Freq"
        self.props["context"]["primary_sweep_range"] = ["All"]
        self.props["context"]["secondary_sweep_range"] = ["All"]
        self.props["context"]["variations"] = {"Freq": ["All"]}
        for el, k in self._post._app.available_variations.nominal_w_values_dict.items():
            self.props["context"]["variations"][el] = k
        self.props["expressions"] = None
        self.props["plot_name"] = None
        if expressions:
            self.expressions = expressions
        self._is_created = False
        self.siwave_dc_category = 0

    @pyaedt_function_handler()
    def delete(self):
        """Delete current report."""
        self._post.oreportsetup.DeleteReports([self.plot_name])
        for i in self._post.plots:
            if i.plot_name == self.plot_name:
                del i
                break
        return True

    @property
    def differential_pairs(self):
        """Differential pairs flag.

        Returns
        -------
        bool
            ``True`` when differential pairs is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("differential_pairs", False)

    @differential_pairs.setter
    def differential_pairs(self, value):
        self.props["context"]["differential_pairs"] = value

    @property
    def matrix(self):
        """Maxwell 2D/3D or Q2D/Q3D matrix name.

        Returns
        -------
        str
            Matrix name.
        """
        return self.props["context"].get("matrix", None)

    @matrix.setter
    def matrix(self, value):
        self.props["context"]["matrix"] = value

    @property
    def reduced_matrix(self):
        """Maxwell 2D/3D reduced matrix name for eddy current solvers.

        Returns
        -------
        str
            Reduced matrix name.
        """
        return self.props["context"].get("reduced_matrix", None)

    @reduced_matrix.setter
    def reduced_matrix(self, value):
        self.props["context"]["reduced_matrix"] = value

    @property
    def polyline(self):
        """Polyline name for the field report.

        Returns
        -------
        str
            Polyline name.
        """
        return self.props["context"].get("polyline", None)

    @polyline.setter
    def polyline(self, value):
        self.props["context"]["polyline"] = value

    @property
    def expressions(self):
        """Expressions.

        Returns
        -------
        str
            Expressions.
        """
        if self.props.get("expressions", None) is None:
            return []
        return [k.get("name", None) for k in self.props["expressions"] if k.get("name", None) is not None]

    @expressions.setter
    def expressions(self, value):
        if isinstance(value, dict):
            self.props["expressions"].append(value)
        elif isinstance(value, list):
            self.props["expressions"] = []
            for el in value:
                if isinstance(el, dict):
                    self.props["expressions"].append(el)
                else:
                    self.props["expressions"].append({"name": el})
        elif isinstance(value, str):
            if isinstance(self.props["expressions"], list):
                self.props["expressions"].append({"name": value})
            else:
                self.props["expressions"] = [{"name": value}]

    @property
    def report_category(self):
        """Report category.

        Returns
        -------
        str
            Report category.
        """
        return self.props["report_category"]

    @report_category.setter
    def report_category(self, value):
        self.props["report_category"] = value

    @property
    def report_type(self):
        """Report type. Options are ``"3D Polar Plot"``, ``"3D Spherical Plot"``,
        ``"Radiation Pattern"``, ``"Rectangular Plot"``, ``"Data Table"``,
        ``"Smith Chart"``, and ``"Rectangular Contour Plot"``.

        Returns
        -------
        str
            Report type.
        """
        return self.props["report_type"]

    @report_type.setter
    def report_type(self, report):
        self.props["report_type"] = report
        if not self.primary_sweep:
            if self.props["report_type"] in ["3D Polar Plot", "3D Spherical Plot"]:
                self.primary_sweep = "Phi"
                self.secondary_sweep = "Theta"
            elif self.props["report_type"] == "Radiation Pattern":
                self.primary_sweep = "Phi"
            elif self.domain == "Sweep":
                self.primary_sweep = "Freq"
            elif self.domain == "Time":
                self.primary_sweep = "Time"

    @property
    def traces(self):
        """List of available traces in the report.

        .. note::
            This property works in version 2022 R1 and later. However, it works only in
            non-graphical mode in version 2022 R2 and later.

        Returns
        -------
        List of :class:`pyaedt.modules.report_templates.Trace`
        """
        _traces = []
        try:
            oo = self._post.oreportsetup.GetChildObject(self.plot_name)
            oo_names = self._post.oreportsetup.GetChildObject(self.plot_name).GetChildNames()
        except Exception:
            return _traces
        for el in oo_names:
            if el in ["Legend", "Grid", "AxisX", "AxisY1", "Header", "General", "CartesianDisplayTypeProperty"]:
                continue
            try:
                oo1 = oo.GetChildObject(el).GetChildNames()

                for i in oo1:
                    _traces.append(Trace(self._post.oreportsetup, "{}:{}:{}".format(self.plot_name, el, i)))
            except Exception:
                pass
        return _traces

    @pyaedt_function_handler()
    def _update_traces(self):
        for trace in self.traces[::]:
            trace_name = trace.aedt_name.split(":")[1]
            if "expressions" in self.props and trace_name in self.props["expressions"]:
                trace_val = self.props["expressions"][trace_name]
                trace_style = _props_with_default(trace_val, "trace_style")
                trace_width = _props_with_default(trace_val, "width")
                trace_type = _props_with_default(trace_val, "trace_type")
                trace_color = _props_with_default(trace_val, "color")
                symbol_show = _props_with_default(trace_val, "show_symbols", False)
                symbol_style = _props_with_default(trace_val, "symbol_style", None)
                symbol_arrows = _props_with_default(trace_val, "show_arrows", None)
                symbol_fill = _props_with_default(trace_val, "symbol_fill", False)
                symbol_color = _props_with_default(trace_val, "symbol_color", None)
                trace.set_trace_properties(
                    style=trace_style, width=trace_width, trace_type=trace_type, color=trace_color
                )
                if self.report_category in ["Eye Diagram", "Spectrum"]:
                    continue
                trace.set_symbol_properties(
                    show=symbol_show,
                    style=symbol_style,
                    show_arrows=symbol_arrows,
                    fill=symbol_fill,
                    color=symbol_color,
                )
        if (
            "eye_mask" in self.props
            and self.report_category in ["Eye Diagram", "Statistical Eye"]
            or ("quantity_type" in self.props and self.report_type == "Rectangular Contour Plot")
        ):
            eye_xunits = _props_with_default(self.props["eye_mask"], "xunits", "ns")
            eye_yunits = _props_with_default(self.props["eye_mask"], "yunits", "mV")
            eye_points = _props_with_default(self.props["eye_mask"], "points")
            eye_enable = _props_with_default(self.props["eye_mask"], "enable_limits", False)
            eye_upper = _props_with_default(self.props["eye_mask"], "upper_limit", 500)
            eye_lower = _props_with_default(self.props["eye_mask"], "lower_limit", 0.3)
            eye_transparency = _props_with_default(self.props["eye_mask"], "transparency", 0.3)
            eye_color = _props_with_default(self.props["eye_mask"], "color", (0, 128, 0))
            eye_xoffset = _props_with_default(self.props["eye_mask"], "X Offset", "0ns")
            eye_yoffset = _props_with_default(self.props["eye_mask"], "Y Offset", "0V")
            if "quantity_type" in self.props and self.report_type == "Rectangular Contour Plot":
                if "contours_number" in self.props.get("general", {}):
                    self._change_property(
                        "Contour",
                        " Plot {}".format(self.traces[0].name),
                        [
                            "NAME:ChangedProps",
                            ["NAME:Num. Contours", "Value:=", str(self.props["general"]["contours_number"])],
                        ],
                    )
                if "contours_scale" in self.props.get("general", {}):
                    self._change_property(
                        "Contour",
                        " Plot {}".format(self.traces[0].name),
                        [
                            "NAME:ChangedProps",
                            ["NAME:Axis Scale", "Value:=", str(self.props["general"]["contours_scale"])],
                        ],
                    )
                if "enable_contours_auto_limit" in self.props.get("general", {}):
                    self._change_property(
                        "Contour",
                        " Plot {}".format(self.traces[0].name),
                        ["NAME:ChangedProps", ["NAME:Scale Type", "Value:=", "Auto Limits"]],
                    )
                elif "contours_min_limit" in self.props.get("general", {}):
                    self._change_property(
                        "Contour",
                        " Plot {}".format(self.traces[0].name),
                        [
                            "NAME:ChangedProps",
                            ["NAME:Min", "Value:=", str(self.props["general"]["contours_min_limit"])],
                        ],
                    )
                elif "contours_max_limit" in self.props.get("general", {}):
                    self._change_property(
                        "Contour",
                        " Plot {}".format(self.traces[0].name),
                        [
                            "NAME:ChangedProps",
                            ["NAME:Max", "Value:=", str(self.props["general"]["contours_max_limit"])],
                        ],
                    )
            self.eye_mask(
                points=eye_points,
                xunits=eye_xunits,
                yunits=eye_yunits,
                enable_limits=eye_enable,
                upper_limit=eye_upper,
                lower_limit=eye_lower,
                color=eye_color,
                transparency=eye_transparency,
                xoffset=eye_xoffset,
                yoffset=eye_yoffset,
            )
        if "limitLines" in self.props and self.report_category not in ["Eye Diagram", "Statistical Eye"]:
            for line in self.props["limitLines"].values():
                if "equation" in line:
                    line_start = _props_with_default(line, "start")
                    line_stop = _props_with_default(line, "stop")
                    line_step = _props_with_default(line, "step")
                    line_equation = _props_with_default(line, "equation")
                    line_axis = _props_with_default(line, "y_axis", 1)
                    if not line_start or not line_step or not line_stop or not line_equation:
                        self._post._app.logger.error(
                            "Equation Limit Lines needs Start, Stop, Step and Equation fields."
                        )
                        continue
                    self.add_limit_line_from_equation(
                        start_x=line_start, stop_x=line_stop, step=line_step, equation=line_equation, y_axis=line_axis
                    )
                else:
                    line_x = _props_with_default(line, "xpoints")
                    line_y = _props_with_default(line, "ypoints")
                    line_xunits = _props_with_default(line, "xunits")
                    line_yunits = _props_with_default(line, "yunits", "")
                    line_axis = _props_with_default(line, "y_axis", "Y1")
                    self.add_limit_line_from_points(line_x, line_y, line_xunits, line_yunits, line_axis)
                line_style = _props_with_default(line, "trace_style")
                line_width = _props_with_default(line, "width")
                line_hatchabove = _props_with_default(line, "hatch_above")
                line_viol = _props_with_default(line, "violation_emphasis")
                line_hatchpix = _props_with_default(line, "hatch_pixels")
                line_color = _props_with_default(line, "color")
                self.limit_lines[-1].set_line_properties(
                    style=line_style,
                    width=line_width,
                    hatch_above=line_hatchabove,
                    violation_emphasis=line_viol,
                    hatch_pixels=line_hatchpix,
                    color=line_color,
                )
        if "notes" in self.props:
            for note in self.props["notes"].values():
                note_text = _props_with_default(note, "text")
                note_position = _props_with_default(note, "position", [0, 0])
                self.add_note(note_text, note_position[0], note_position[1])
                note_back_color = _props_with_default(note, "background_color")
                note_background_visibility = _props_with_default(note, "background_visibility")
                note_border_color = _props_with_default(note, "border_color")
                note_border_visibility = _props_with_default(note, "border_visibility")
                note_border_width = _props_with_default(note, "border_width")
                note_font = _props_with_default(note, "font", "Arial")
                note_font_size = _props_with_default(note, "font_size", 12)
                note_italic = _props_with_default(note, "italic")
                note_bold = _props_with_default(note, "bold")
                note_color = _props_with_default(note, "color", (0, 0, 0))

                self.notes[-1].set_note_properties(
                    back_color=note_back_color,
                    background_visibility=note_background_visibility,
                    border_color=note_border_color,
                    border_visibility=note_border_visibility,
                    border_width=note_border_width,
                    font=note_font,
                    font_size=note_font_size,
                    italic=note_italic,
                    bold=note_bold,
                    color=note_color,
                )
        if "general" in self.props:
            if "show_rectangular_plot" in self.props["general"] and self.report_category in ["Eye Diagram"]:
                eye_rectangular = _props_with_default(self.props["general"], "show_rectangular_plot", True)
                self.rectangular_plot(eye_rectangular)
            if "legend" in self.props["general"] and self.report_type != "Rectangular Contour Plot":
                legend = self.props["general"]["legend"]
                legend_sol_name = _props_with_default(legend, "show_solution_name", True)
                legend_var_keys = _props_with_default(legend, "show_variation_key", True)
                leend_trace_names = _props_with_default(legend, "show_trace_name", True)
                legend_color = _props_with_default(legend, "back_color", (255, 255, 255))
                legend_font_color = _props_with_default(legend, "font_color", (0, 0, 0))
                self.edit_legend(
                    show_solution_name=legend_sol_name,
                    show_variation_key=legend_var_keys,
                    show_trace_name=leend_trace_names,
                    back_color=legend_color,
                    font_color=legend_font_color,
                )
            if "grid" in self.props["general"]:
                grid = self.props["general"]["grid"]
                grid_major_color = _props_with_default(grid, "major_color", (200, 200, 200))
                grid_minor_color = _props_with_default(grid, "minor_color", (230, 230, 230))
                grid_enable_major_x = _props_with_default(grid, "major_x", True)
                grid_enable_major_y = _props_with_default(grid, "major_y", True)
                grid_enable_minor_x = _props_with_default(grid, "minor_x", True)
                grid_enable_minor_y = _props_with_default(grid, "minor_y", True)
                grid_style_minor = _props_with_default(grid, "style_minor", "Solid")
                grid_style_major = _props_with_default(grid, "style_major", "Solid")
                self.edit_grid(
                    minor_x=grid_enable_minor_x,
                    minor_y=grid_enable_minor_y,
                    major_x=grid_enable_major_x,
                    major_y=grid_enable_major_y,
                    minor_color=grid_minor_color,
                    major_color=grid_major_color,
                    style_minor=grid_style_minor,
                    style_major=grid_style_major,
                )
            if "appearance" in self.props["general"]:
                general = self.props["general"]["appearance"]
                general_back_color = _props_with_default(general, "background_color", (255, 255, 255))
                general_plot_color = _props_with_default(general, "plot_color", (255, 255, 255))
                enable_y_stripes = _props_with_default(general, "enable_y_stripes", True)
                general_field_width = _props_with_default(general, "field_width", 4)
                general_precision = _props_with_default(general, "precision", 4)
                general_use_scientific_notation = _props_with_default(general, "use_scientific_notation", True)
                self.edit_general_settings(
                    background_color=general_back_color,
                    plot_color=general_plot_color,
                    enable_y_stripes=enable_y_stripes,
                    field_width=general_field_width,
                    precision=general_precision,
                    use_scientific_notation=general_use_scientific_notation,
                )
            if "header" in self.props["general"]:
                header = self.props["general"]["header"]
                company_name = _props_with_default(header, "company_name", "")
                show_design_name = _props_with_default(header, "show_design_name", True)
                header_font = _props_with_default(header, "font", "Arial")
                header_title_size = _props_with_default(header, "title_size", 12)
                header_subtitle_size = _props_with_default(header, "subtitle_size", 12)
                header_italic = _props_with_default(header, "italic", False)
                header_bold = _props_with_default(header, "bold", False)
                header_color = _props_with_default(header, "color", (0, 0, 0))
                self.edit_header(
                    company_name=company_name,
                    show_design_name=show_design_name,
                    font=header_font,
                    title_size=header_title_size,
                    subtitle_size=header_subtitle_size,
                    italic=header_italic,
                    bold=header_bold,
                    color=header_color,
                )

            for i in list(self.props["general"].keys()):
                if "axis" in i:
                    axis = self.props["general"][i]
                    axis_font = _props_with_default(axis, "font", "Arial")
                    axis_size = _props_with_default(axis, "font_size", 12)
                    axis_italic = _props_with_default(axis, "italic", False)
                    axis_bold = _props_with_default(axis, "bold", False)
                    axis_color = _props_with_default(axis, "color", (0, 0, 0))
                    axis_label = _props_with_default(axis, "label")
                    axis_linear_scaling = _props_with_default(axis, "linear_scaling", True)
                    axis_min_scale = _props_with_default(axis, "min_scale")
                    axis_max_scale = _props_with_default(axis, "max_scale")
                    axis_min_trick_div = _props_with_default(axis, "minor_tick_divs", 5)
                    specify_spacing = _props_with_default(axis, "specify_spacing", True)
                    if not specify_spacing:
                        axis_min_spacing = None
                    else:
                        axis_min_spacing = _props_with_default(axis, "min_spacing")
                    axis_units = _props_with_default(axis, "units")
                    if i == "axisx":
                        self.edit_x_axis(
                            font=axis_font,
                            font_size=axis_size,
                            italic=axis_italic,
                            bold=axis_bold,
                            color=axis_color,
                            label=axis_label,
                        )
                        if self.report_category in ["Eye Diagram", "Statistical Eye"]:
                            continue
                        self.edit_x_axis_scaling(
                            linear_scaling=axis_linear_scaling,
                            min_scale=axis_min_scale,
                            max_scale=axis_max_scale,
                            minor_tick_divs=axis_min_trick_div,
                            min_spacing=axis_min_spacing,
                            units=axis_units,
                        )
                    else:
                        self.edit_y_axis(
                            font=axis_font,
                            font_size=axis_size,
                            italic=axis_italic,
                            bold=axis_bold,
                            color=axis_color,
                            label=axis_label,
                        )
                        if self.report_category in ["Eye Diagram", "Statistical Eye"]:
                            continue
                        self.edit_y_axis_scaling(
                            name=i.replace("axis", "").upper(),
                            linear_scaling=axis_linear_scaling,
                            min_scale=axis_min_scale,
                            max_scale=axis_max_scale,
                            minor_tick_divs=axis_min_trick_div,
                            min_spacing=axis_min_spacing,
                            units=axis_units,
                        )

    @property
    def limit_lines(self):
        """List of available limit lines in the report.

        .. note::
            This property works in version 2022 R1 and later. However, it works only in
            non-graphical mode in version 2022 R2 and later.

        Returns
        -------
        List of :class:`pyaedt.modules.report_templates.LimitLine`
        """
        _traces = []
        oo_names = self._post._app.get_oo_name(self._post.oreportsetup, self.plot_name)
        for el in oo_names:
            if "LimitLine" in el:
                _traces.append(LimitLine(self._post.oreportsetup, "{}:{}".format(self.plot_name, el)))

        return _traces

    @property
    def notes(self):
        """List of available notes in the report.

        .. note::
            This property works in version 2022 R1 and later. However, it works only in
            non-graphical mode in version 2022 R2 and later.

        Returns
        -------
        List of :class:`pyaedt.modules.report_templates.Note`
        """
        _notes = []
        try:
            oo_names = self._post.oreportsetup.GetChildObject(self.plot_name).GetChildNames()
        except Exception:
            return _notes
        for el in oo_names:
            if "Note" in el:
                _notes.append(Note(self._post.oreportsetup, "{}:{}".format(self.plot_name, el)))

        return _notes

    @property
    def plot_name(self):
        """Plot name.

        Returns
        -------
        str
            Plot name.
        """
        return self.props["plot_name"]

    @plot_name.setter
    def plot_name(self, name):
        if self._is_created:
            if name not in self._post.oreportsetup.GetAllReportNames():
                self._post.oreportsetup.RenameReport(self.props["plot_name"], name)
        self.props["plot_name"] = name

    @property
    def variations(self):
        """Variations.

        Returns
        -------
        str
            Variations.
        """
        return self.props["context"]["variations"]

    @variations.setter
    def variations(self, value):
        self.props["context"]["variations"] = value

    @property
    def primary_sweep(self):
        """Primary sweep report.

        Returns
        -------
        str
            Primary sweep.
        """
        return self.props["context"]["primary_sweep"]

    @primary_sweep.setter
    def primary_sweep(self, value):
        if value == self.props["context"].get("secondary_sweep", None):
            self.props["context"]["secondary_sweep"] = self.props["context"]["primary_sweep"]
        self.props["context"]["primary_sweep"] = value
        if value == "Time":
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif value == "Freq":
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @property
    def secondary_sweep(self):
        """Secondary sweep report.

        Returns
        -------
        str
            Secondary sweep.
        """
        return self.props["context"].get("secondary_sweep", None)

    @secondary_sweep.setter
    def secondary_sweep(self, value):
        if value == self.props["context"]["primary_sweep"]:
            self.props["context"]["primary_sweep"] = self.props["context"]["secondary_sweep"]
        self.props["context"]["secondary_sweep"] = value
        if value == "Time":
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif value == "Freq":
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @property
    def primary_sweep_range(self):
        """Primary sweep range report.

        Returns
        -------
        str
            Primary sweep range.
        """
        return self.props["context"]["primary_sweep_range"]

    @primary_sweep_range.setter
    def primary_sweep_range(self, value):
        self.props["context"]["primary_sweep_range"] = value

    @property
    def secondary_sweep_range(self):
        """Secondary sweep range report.

        Returns
        -------
        str
            Secondary sweep range.
        """
        return self.props["context"]["secondary_sweep_range"]

    @secondary_sweep_range.setter
    def secondary_sweep_range(self, value):
        self.props["context"]["secondary_sweep_range"] = value

    @property
    def _context(self):
        return []

    @pyaedt_function_handler()
    def update_expressions_with_defaults(self, quantities_category=None):
        """Update the list of expressions by taking all quantities from a given category.

        Parameters
        ----------
        quantities_category : str, optional
            Quantities category to use. The default is ``None``, in which case the default
            category for the specified report is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.expressions = self._post.available_report_quantities(
            self.report_category, self.report_type, self.setup, quantities_category
        )

    @property
    def _trace_info(self):
        if not self.expressions:
            self.update_expressions_with_defaults()
        if isinstance(self.expressions, list):
            expr = self.expressions
        else:
            expr = [self.expressions]
        arg = ["X Component:=", self.primary_sweep, "Y Component:=", expr]
        if self.report_type in ["3D Polar Plot", "3D Spherical Plot"]:
            arg = [
                "Phi Component:=",
                self.primary_sweep,
                "Theta Component:=",
                self.secondary_sweep,
                "Mag Component:=",
                expr,
            ]
        elif self.report_type == "Radiation Pattern":
            arg = ["Ang Component:=", self.primary_sweep, "Mag Component:=", expr]
        elif self.report_type in ["Smith Chart", "Polar Plot"]:
            arg = ["Polar Component:=", expr]
        elif self.report_type == "Rectangular Contour Plot":
            arg = [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self.secondary_sweep,
                "Z Component:=",
                expr,
            ]
        return arg

    @property
    def domain(self):
        """Plot domain.

        Returns
        -------
        str
            Plot domain.
        """
        return self.props["context"]["domain"]

    @domain.setter
    def domain(self, domain):
        self.props["context"]["domain"] = domain
        if self._post._app.design_type in ["Maxwell 3D", "Maxwell 2D"]:
            return
        if self.primary_sweep == "Freq" and domain == "Time":
            self.primary_sweep = "Time"
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif self.primary_sweep == "Time" and domain == "Sweep":
            self.primary_sweep = "Freq"
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @property
    def use_pulse_in_tdr(self):
        """Defines if the TDR should use a pulse or step.

        Returns
        -------
        bool
            ``True`` when option is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("use_pulse_in_tdr", False)

    @use_pulse_in_tdr.setter
    def use_pulse_in_tdr(self, val):
        self.props["context"]["use_pulse_in_tdr"] = val

    @pyaedt_function_handler()
    def _convert_dict_to_report_sel(self, sweeps):
        if not sweeps:
            return []
        sweep_list = []
        if self.primary_sweep:
            sweep_list.append(self.primary_sweep + ":=")
            if self.primary_sweep_range == ["All"] and self.primary_sweep in self.variations:
                sweep_list.append(self.variations[self.primary_sweep])
            else:
                sweep_list.append(self.primary_sweep_range)
        if self.secondary_sweep:
            sweep_list.append(self.secondary_sweep + ":=")
            if self.secondary_sweep_range == ["All"] and self.secondary_sweep in self.variations:
                sweep_list.append(self.variations[self.primary_sweep])
            else:
                sweep_list.append(self.secondary_sweep_range)
        for el in sweeps:
            if el in [self.primary_sweep, self.secondary_sweep]:
                continue
            sweep_list.append(el + ":=")
            if isinstance(sweeps[el], list):
                sweep_list.append(sweeps[el])
            else:
                sweep_list.append([sweeps[el]])
        for el in list(self._post._app.available_variations.nominal_w_values_dict.keys()):
            if el not in sweeps:
                sweep_list.append(el + ":=")
                sweep_list.append(["Nominal"])
        return sweep_list

    @pyaedt_function_handler(plot_name="name")
    def create(self, name=None):
        """Create a report.

        Parameters
        ----------
        name : str, optional
            Name for the plot. The default is ``None``, in which case the
            default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        if self.setup not in self._post._app.existing_analysis_sweeps and "AdaptivePass" not in self.setup:
            self._post._app.logger.error("Setup doesn't exist in this design.")
            return False
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            self.report_category,
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            self._trace_info,
        )
        self._post.plots.append(self)
        self._is_created = True
        return True

    @pyaedt_function_handler()
    def get_solution_data(self):
        """Get the report solution data.

        Returns
        -------
        :class:`pyaedt.modules.solutions.SolutionData`
            Solution data object.
        """
        if not self.expressions:
            self.update_expressions_with_defaults()
        solution_data = self._post.get_solution_data_per_variation(
            self.report_category, self.setup, self._context, self.variations, self.expressions
        )
        if not solution_data:
            self._post._app.logger.warning("No Data Available. Check inputs")
            return False
        if self.primary_sweep:
            solution_data.primary_sweep = self.primary_sweep
        return solution_data

    @pyaedt_function_handler()
    def add_limit_line_from_points(self, x_list, y_list, x_units="", y_units="", y_axis="Y1"):  # pragma: no cover
        """Add a Cartesian limit line from point lists. This method works only in graphical mode.

        Parameters
        ----------
        x_list : list
            List of float inputs.
        y_list : list
            List of float y values.
        x_units : str, optional
            Units for the ``x_list`` parameter. The default is ``""``.
        y_units : str, optional
            Units for the ``y_list`` parameter. The default is ``""``.
        y_axis : int, optional
            Y axis. The default is `"Y1"`.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        x_list = [GeometryOperators.parse_dim_arg(str(i) + x_units) for i in x_list]
        y_list = [GeometryOperators.parse_dim_arg(str(i) + y_units) for i in y_list]
        if self.plot_name and self._is_created:
            xvals = ["NAME:XValues"]
            xvals.extend(x_list)
            yvals = ["NAME:YValues"]
            yvals.extend(y_list)
            self._post.oreportsetup.AddCartesianLimitLine(
                self.plot_name,
                [
                    "NAME:CartesianLimitLine",
                    xvals,
                    "XUnits:=",
                    x_units,
                    yvals,
                    "YUnits:=",
                    y_units,
                    "YAxis:=",
                    y_axis,
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_limit_line_from_equation(
        self, start_x, stop_x, step, equation="x", units="GHz", y_axis=1
    ):  # pragma: no cover
        """Add a Cartesian limit line from point lists. This method works only in graphical mode.

        Parameters
        ----------
        start_x : float
            Start X value.
        stop_x : float
            Stop X value.
        step : float
            X step value.
        equation : str, optional
            Y equation to apply. The default is Y=X.
        units : str
            Units for the X axis. The default is ``"GHz"``.
        y_axis : str, int, optional
            Y axis. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.plot_name and self._is_created:
            self._post.oreportsetup.AddCartesianLimitLineFromEquation(
                self.plot_name,
                [
                    "NAME:CartesianLimitLineFromEquation",
                    "YAxis:=",
                    int(str(y_axis).replace("Y", "")),
                    "Start:=",
                    self._post._app.value_with_units(start_x, units),
                    "Stop:=",
                    self._post._app.value_with_units(stop_x, units),
                    "Step:=",
                    self._post._app.value_with_units(step, units),
                    "Equation:=",
                    equation,
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_note(self, text, x_position=0, y_position=0):  # pragma: no cover
        """Add a note at a position.

        Parameters
        ----------
        text : string
            Text of the note.
        x_position : float, optional
            x position of the note. The default is ``0.0``.
        y_position : float, optional
            y position of the note. The default is ``0.0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        note_name = generate_unique_name("Note", n=3)
        if self.plot_name and self._is_created:
            self._post.oreportsetup.AddNote(
                self.plot_name,
                [
                    "NAME:NoteDataSource",
                    [
                        "NAME:NoteDataSource",
                        "SourceName:=",
                        note_name,
                        "HaveDefaultPos:=",
                        True,
                        "DefaultXPos:=",
                        x_position,
                        "DefaultYPos:=",
                        y_position,
                        "String:=",
                        text,
                    ],
                ],
            )
            return True
        return False

    @pyaedt_function_handler(val="value")
    def add_cartesian_x_marker(self, value, name=None):  # pragma: no cover
        """Add a cartesian X marker.

        .. note::
           This method only works in graphical mode.

        Parameters
        ----------
        value : str
            Value to apply with units.
        name : str, optional
            Marker name. The default is ``None``.

        Returns
        -------
        str
            Marker name if created.
        """
        if not name:
            name = generate_unique_name("MX")
            self._post.oreportsetup.AddCartesianXMarker(self.plot_name, name, GeometryOperators.parse_dim_arg(value))
            return name
        return ""

    @pyaedt_function_handler(val="value")
    def add_cartesian_y_marker(self, value, name=None, y_axis=1):  # pragma: no cover
        """Add a cartesian Y marker.

        .. note::
           This method only works in graphical mode.

        Parameters
        ----------
        value : str, float
            Value to apply with units.
        name : str, optional
            Marker name. The default is ``None``.
        y_axis : str, optional
            Y axis. The default is ``"Y1"``.

        Returns
        -------
        str
            Marker name if created.
        """
        if not name:
            name = generate_unique_name("MY")
            self._post.oreportsetup.AddCartesianYMarker(
                self.plot_name, name, "Y{}".format(y_axis), GeometryOperators.parse_dim_arg(value), ""
            )
            return name
        return ""

    @pyaedt_function_handler(tabname="tab_name")
    def _change_property(self, tab_name, property_name, property_val):
        if not self._is_created:
            self._post._app.logger.error("Plot has not been created. Create it and then change the properties.")
            return False
        arg = [
            "NAME:AllTabs",
            ["NAME:" + tab_name, ["NAME:PropServers", "{}:{}".format(self.plot_name, property_name)], property_val],
        ]
        self._post.oreportsetup.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def edit_grid(
        self,
        minor_x=True,
        minor_y=True,
        major_x=True,
        major_y=True,
        style_minor="Solid",
        style_major="Solid",
        minor_color=(0, 0, 0),
        major_color=(0, 0, 0),
    ):
        """Edit the grid settings for the plot.

        Parameters
        ----------
        minor_x : bool, optional
            Whether to enable the minor X grid. The default is ``True``.
        minor_y : bool, optional
            Whether to enable the minor Y grid. The default is ``True``.
        major_x : bool, optional
            Whether to enable the major X grid. The default is ``True``.
        major_y : bool, optional
            Whether to enable the major Y grid. The default is ``True``.
        style_minor : str, optional
            Minor grid style. The default is ``"Solid"``.
        style_major : str, optional
            Major grid style. The default is ``"Solid"``.
        minor_color : tuple, optional
            Minor grid (R, G, B) color. The default is ``(0, 0, 0)``.
            Each color value must be an integer in a range from 0 to 255.
        major_color : tuple, optional
            Major grid (R, G, B) color. The default is ``(0, 0, 0)``.
            Each color value must be an integer in a range from 0 to 255.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:ChangedProps",
            ["NAME:Show minor X grid", "Value:=", minor_x],
            ["NAME:Show minor Y grid", "Value:=", minor_y],
            ["NAME:Show major X grid", "Value:=", major_x],
            ["NAME:Show major Y grid", "Value:=", major_y],
            ["NAME:Minor grid line style", "Value:=", style_minor],
            ["NAME:Major grid line style", "Value:=", style_major],
            ["NAME:Minor grid line color", "R:=", minor_color[0], "G:=", minor_color[1], "B:=", minor_color[2]],
            ["NAME:Major grid line color", "R:=", major_color[0], "G:=", major_color[1], "B:=", major_color[2]],
        ]
        return self._change_property("Grid", "Grid", props)

    @pyaedt_function_handler()
    def edit_x_axis(self, font="Arial", font_size=12, italic=False, bold=False, color=(0, 0, 0), label=None):
        """Edit the X-axis settings.

        Parameters
        ----------
        font : str, optional
            Font name. The default is ``"Arial"``.
        font_size : int, optional
            Font size. The default is ``12``.
        italic : bool, optional
            Whether to use italic type. The default is ``False``.
        bold : bool, optional
            Whether to use bold type. The default is ``False``.
        color : tuple, optional
            Font (R, G, B) color. The default is ``(0, 0, 0)``. Each color value
            must be an integer in a range from 0 to 255.
        label : str, optional
            Label for the Y axis. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:ChangedProps",
            [
                "NAME:Text Font",
                "Height:=",
                -1 * font_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
        ]
        if label:
            props.append(["NAME:Name", "Value:=", label])
        props.append(["NAME:Axis Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property("Axis", "AxisX", props)

    @pyaedt_function_handler()
    def edit_x_axis_scaling(
        self, linear_scaling=True, min_scale=None, max_scale=None, minor_tick_divs=5, min_spacing=None, units=None
    ):
        """Edit the X-axis scaling settings.

        Parameters
        ----------
        linear_scaling : bool, optional
            Whether to use the linear scale. The default is ``True``.
            When ``False``, the log scale is used.
        min_scale : str, optional
            Minimum scale value with units. The default is ``None``.
        max_scale : str, optional
            Maximum scale value with units. The default is ``None``.
        minor_tick_divs : int, optional
            Minor tick division. The default is ``5``.
        min_spacing : str, optional
            Minimum spacing with units. The default is ``None``.
        units : str, optional
            Units in the plot. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if linear_scaling:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Linear"]]
        else:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Log"]]
        if min_scale:
            props.append(["NAME:Min", "Value:=", min_scale])
        if max_scale:
            props.append(["NAME:Max", "Value:=", max_scale])
        if minor_tick_divs and linear_scaling:
            props.append(["NAME:Minor Tick Divs", "Value:=", str(minor_tick_divs)])
        if min_spacing:
            props.append(["NAME:Spacing", "Value:=", min_spacing])
        if units:
            props.append((["NAME:Auto Units", "Value:=", False]))
            props.append(["NAME:Units", "Value:=", units])
        return self._change_property("Scaling", "AxisX", props)

    @pyaedt_function_handler()
    def edit_legend(
        self,
        show_solution_name=True,
        show_variation_key=True,
        show_trace_name=True,
        back_color=(255, 255, 255),
        font_color=(0, 0, 0),
    ):
        """Edit the plot legend.

        Parameters
        ----------
        show_solution_name : bool, optional
            Whether to show the solution name. The default is ``True``.
        show_variation_key : bool, optional
            Whether to show the variation key. The default is ``True``.
        show_trace_name : bool, optional
            Whether to show the trace name. The default is ``True``.
        back_color : tuple, optional
            Background (R, G, B) color. The default is ``(255, 255, 255)``. Each color value
            must be an integer in a range from 0 to 255.
        font_color : tuple, optional
            Legend font (R, G, B) color. The default is ``(0, 0, 0)``. Each color value
            must be an integer in a range from 0 to 255.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:ChangedProps",
            ["NAME:Show Solution Name", "Value:=", show_solution_name],
            ["NAME:Show Variation Key", "Value:=", show_variation_key],
            ["NAME:Show Trace Name", "Value:=", show_trace_name],
            ["NAME:Back Color", "R:=", back_color[0], "G:=", back_color[1], "B:=", back_color[2]],
            ["NAME:Font", "R:=", font_color[0], "G:=", font_color[1], "B:=", font_color[2]],
        ]
        return self._change_property("legend", "legend", props)

    @pyaedt_function_handler(font_height="font_size")
    def hide_legend(self, solution_name=True, trace_name=True, variation_key=True, font_size=1):
        """Hide the Legend.

        Parameters
        ----------
        solution_name : bool, optional
            Whether to show or hide the solution name. Default is ``True``.
        trace_name : bool, optional
            Whether to show or hide the trace name. Default is ``True``.
        variation_key : bool, optional
            Whether to show or hide the variations. Default is ``True``.
        font_size : int
            Font size. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            legend = self._post.oreportsetup.GetChildObject(self.plot_name).GetChildObject("Legend")
            legend.Show_Solution_Name = not solution_name
            legend.Show_Trace_Name = not trace_name
            legend.Show_Variation_Key = not variation_key
            legend.SetPropValue("Font/Height", font_size)
            legend.SetPropValue("Header Row Font/Height", font_size)
            return True
        except Exception:
            self._post._app.logger.error("Failed to hide legend.")
            return False

    @pyaedt_function_handler(axis_name="name")
    def edit_y_axis(self, name="Y1", font="Arial", font_size=12, italic=False, bold=False, color=(0, 0, 0), label=None):
        """Edit the Y-axis settings.

        Parameters
        ----------
        name : str, optional
            Name for the main Y axis. The default is ``"Y1"``.
        font : str, optional
            Font name. The default is ``"Arial"``.
        font_size : int, optional
            Font size. The default is ``12``.
        italic : bool, optional
            Whether to use italic type. The default is ``False``.
        bold : bool, optional
            Whether to use bold type. The default is ``False``.
        color : tuple, optional
            Font (R, G, B) color. The default is ``(0, 0, 0)``. Each color value
            must be an integer in a range from 0 to 255.
        label : str, optional
            Label for the Y axis. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:ChangedProps",
            [
                "NAME:Text Font",
                "Height:=",
                -1 * font_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
        ]
        if label:
            props.append(["NAME:Name", "Value:=", label])
        props.append(["NAME:Axis Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property("Axis", "Axis" + name, props)

    @pyaedt_function_handler(axis_name="name")
    def edit_y_axis_scaling(
        self,
        name="Y1",
        linear_scaling=True,
        min_scale=None,
        max_scale=None,
        minor_tick_divs=5,
        min_spacing=None,
        units=None,
    ):
        """Edit the Y-axis scaling settings.

        Parameters
        ----------
        axis name : str, optional
            Axis name. The default is ``Y``.
        linear_scaling : bool, optional
            Whether to use the linear scale. The default is ``True``.
            When ``False``, the log scale is used.
        min_scale : str, optional
            Minimum scale value with units. The default is ``None``.
        max_scale : str, optional
            Maximum scale value with units. The default is ``None``.
        minor_tick_divs : int, optional
            Minor tick division. The default is ``5``.
        min_spacing : str, optional
            Minimum spacing with units. The default is ``None``.
        units : str, optional
            Units in the plot. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if linear_scaling:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Linear"]]
        else:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Log"]]
        if min_scale:
            props.append(["NAME:Min", "Value:=", min_scale])
        if max_scale:
            props.append(["NAME:Max", "Value:=", max_scale])
        if minor_tick_divs and linear_scaling:
            props.append(["NAME:Minor Tick Divs", "Value:=", str(minor_tick_divs)])
        if min_spacing:
            props.append(["NAME:Spacing", "Value:=", min_spacing])
        if units:
            props.append((["NAME:Auto Units", "Value:=", False]))
            props.append(["NAME:Units", "Value:=", units])
        return self._change_property("Scaling", "Axis" + name, props)

    @pyaedt_function_handler()
    def edit_general_settings(
        self,
        background_color=(255, 255, 255),
        plot_color=(255, 255, 255),
        enable_y_stripes=True,
        field_width=4,
        precision=4,
        use_scientific_notation=True,
    ):
        """Edit general settings for the plot.

        Parameters
        ----------
        background_color : tuple, optional
            Backgoround (R, G, B) color. The default is ``(255, 255, 255)``. Each color value
            must be an integer in a range from 0 to 255.
        plot_color : tuple, optional
            Plot (R, G, B) color. The default is ``(255, 255, 255)``. Each color value
            must be an integer in a range from 0 to 255.
        enable_y_stripes : bool, optional
            Whether to enable Y stripes. The default is ``True``.
        field_width : int, optional
            Field width. The default is ``4``.
        precision : int, optional
            Field precision. The default is ``4``.
        use_scientific_notation : bool, optional
            Whether to enable scientific notation. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:ChangedProps",
            ["NAME:Back Color", "R:=", background_color[0], "G:=", background_color[1], "B:=", background_color[2]],
            ["NAME:Plot Area Color", "R:=", plot_color[0], "G:=", plot_color[1], "B:=", plot_color[2]],
            ["NAME:Enable Y Axis Stripes", "Value:=", enable_y_stripes],
            ["NAME:Field Width", "Value:=", str(field_width)],
            ["NAME:Precision", "Value:=", str(precision)],
            ["NAME:Use Scientific Notation", "Value:=", use_scientific_notation],
        ]
        return self._change_property("general", "general", props)

    @pyaedt_function_handler()
    def edit_header(
        self,
        company_name="PyAEDT",
        show_design_name=True,
        font="Arial",
        title_size=12,
        subtitle_size=12,
        italic=False,
        bold=False,
        color=(0, 0, 0),
    ):
        """Edit the plot header.

        Parameters
        ----------
        company_name : str, optional
            Company name. The default is ``PyAEDT``.
        show_design_name : bool, optional
            Whether to show the design name in the plot. The default is ``True``.
        font : str, optional
            Font name. The default is ``"Arial"``.
        title_size : int, optional
            Title font size. The default is ``12``.
        subtitle_size : int, optional
            Subtitle font size. The default is ``12``.
        italic : bool, optional
            Whether to use italic type. The default is ``False``.
        bold : bool, optional
            Whether to use bold type. The default is ``False``.
        color : tuple, optional
            Title (R, G, B) color. The default is ``(0, 0, 0)``.
            Each color value must be an integer in a range from 0 to 255.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:ChangedProps",
            [
                "NAME:Title Font",
                "Height:=",
                -1 * title_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
            [
                "NAME:Sub Title Font",
                "Height:=",
                -1 * subtitle_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
            ["NAME:Company Name", "Value:=", company_name],
            ["NAME:Show Design Name", "Value:=", show_design_name],
        ]
        return self._change_property("Header", "Header", props)

    @pyaedt_function_handler(file_path="input_file")
    def import_traces(self, input_file, plot_name):
        """Import report data from a file into a specified report.

        Parameters
        ----------
        input_file : str
            Path for the file to import. The extensions supported are ``".csv"``,
            ``".tab"``, ``".dat"``, and ``".rdat"``.
        plot_name : str
            Name of the plot to import the file data into.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not os.path.exists(input_file):
            msg = "File does not exist."
            raise FileExistsError(msg)

        if not plot_name:
            msg = "Plot name can't be None."
            raise ValueError(msg)
        else:
            if plot_name not in self._post.all_report_names:
                msg = "Plot name provided doesn't exists in current report."
                raise ValueError(msg)
            self.plot_name = plot_name

        split_path = os.path.splitext(input_file)
        extension = split_path[1]

        supported_ext = [".csv", ".tab", ".dat", ".rdat"]
        if extension not in supported_ext:
            msg = "Extension {} is not supported. Use one of {}".format(extension, ", ".join(supported_ext))
            raise ValueError(msg)

        try:
            if extension == ".rdat":
                self._post.oreportsetup.ImportReportDataIntoReport(self.plot_name, input_file)
            else:
                self._post.oreportsetup.ImportIntoReport(self.plot_name, input_file)
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def delete_traces(self, plot_name, traces_list):
        """Delete an existing trace or traces.

        Parameters
        ----------
        plot_name : str
            Plot name.
        traces_list : list
            List of one or more traces to delete.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if plot_name not in self._post.all_report_names:
            raise ValueError("Plot does not exist in current project.")

        for trace in traces_list:
            if trace not in self._trace_info[3]:
                raise ValueError("Trace does not exist in the selected plot.")

        props = ["{}:=".format(plot_name), traces_list]
        try:
            self._post.oreportsetup.DeleteTraces(props)
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def add_trace_to_report(self, traces, setup_name=None, variations=None, context=None):
        """Add a trace to a specific report.

        Parameters
        ----------
        traces : list
            List of traces to add.
        setup_name : str, optional
            Name of the setup. The default is ``None`` which automatically take ``nominal_adaptive`` setup.
            Please make sure to build a setup string in the form of ``"SetupName : SetupSweep"``
            where ``SetupSweep`` is the Sweep name to use in the export or ``LastAdaptive``.
        variations : dict, optional
            Dictionary of variations. The default is ``None``.
        context : list, optional
            List of solution context.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        expr = copy.deepcopy(self.expressions)
        self.expressions = traces

        try:
            self._post.oreportsetup.AddTraces(
                self.plot_name,
                setup_name if setup_name else self.setup,
                context if context else self._context,
                self._convert_dict_to_report_sel(variations if variations else self.variations),
                self._trace_info,
            )
            return True
        except Exception:
            return False
        finally:
            self.expressions = expr

    @pyaedt_function_handler()
    def update_trace_in_report(self, traces, setup_name=None, variations=None, context=None):
        """Update a trace in a specific report.

        Parameters
        ----------
        traces : list
            List of traces to add.
        setup_name : str, optional
            Name of the setup. The default is ``None``.
        variations : dict, optional
            Dictionary of variations. The default is ``None``.
        context : list, optional
            List of solution context.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        expr = copy.deepcopy(self.expressions)
        self.expressions = traces

        try:
            self._post.oreportsetup.UpdateTraces(
                self.plot_name,
                traces,
                setup_name if setup_name else self.setup,
                context if context else self._context,
                self._convert_dict_to_report_sel(variations if variations else self.variations),
                self._trace_info,
            )
            return True
        except Exception:
            return False
        finally:
            self.expressions = expr


class Standard(CommonReport):
    """Provides a reporting class that fits most of the app's standard reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)

    @property
    def sub_design_id(self):
        """Sub design ID for a Circuit or HFSS 3D Layout sub design.

        Returns
        -------
        int
            Number of the sub design ID.
        """
        return self.props["context"].get("Sub Design ID", None)

    @sub_design_id.setter
    def sub_design_id(self, value):
        self.props["context"]["Sub Design ID"] = value

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start value.
        """
        return self.props["context"].get("time_start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["context"]["time_start"] = value

    @property
    def time_stop(self):
        """Time stop value.

        Returns
        -------
        str
            Time stop value.
        """
        return self.props["context"].get("time_stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["context"]["time_stop"] = value

    @property
    def _did(self):
        if self.domain == "Sweep":
            return 3
        elif self.domain == "Clock Times":
            return 55827
        else:
            return 1

    @property
    def pulse_rise_time(self):
        """Value of Pulse rise time for TDR plot.

        Returns
        -------
        float
            Pulse rise time.
        """
        return self.props["context"].get("pulse_rise_time", 0) if self.domain == "Time" else 0

    @pulse_rise_time.setter
    def pulse_rise_time(self, val):
        self.props["context"]["pulse_rise_time"] = val

    @property
    def time_windowing(self):
        """Returns the TDR time windowing. Options are:
             * ``0`` : Rectangular
            * ``1`` : Bartlett
            * ``2`` : Blackman
            * ``3`` : Hamming
            * ``4`` : Hanning
            * ``5`` : Kaiser
            * ``6`` : Welch
            * ``7`` : Weber
            * ``8`` : Lanzcos.

        Returns
        -------
        int
            Time windowing.
        """
        _time_windowing = self.props["context"].get("time_windowing", 0)
        return _time_windowing if self.domain == "Time" and self.pulse_rise_time != 0 else 0

    @time_windowing.setter
    def time_windowing(self, val):
        available_values = {
            "rectangular": 0,
            "bartlett": 1,
            "blackman": 2,
            "hamming": 3,
            "hanning": 4,
            "kaiser": 5,
            "welch": 6,
            "weber": 7,
            "lanzcos": 8,
        }
        if isinstance(val, int):
            self.props["context"]["time_windowing"] = val
        elif isinstance(val, str) and val.lower in available_values:
            self.props["context"]["time_windowing"] = available_values[val.lower()]

    @property
    def _context(self):
        ctxt = []
        if self._post.post_solution_type in ["TR", "AC", "DC"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0],
            ]
        elif self._post._app.design_type in ["Q3D Extractor", "2D Extractor"]:
            if not self.matrix:
                ctxt = ["Context:=", "Original"]
            else:
                ctxt = ["Context:=", self.matrix]
        elif (
            self._post._app.design_type in ["Maxwell 2D", "Maxwell 3D"]
            and self._post._app.solution_type == "EddyCurrent"
        ):
            if not self.matrix:
                ctxt = ["Context:=", "Original"]
            elif not self.reduced_matrix:
                ctxt = ["Context:=", self.matrix]
            elif self.reduced_matrix:
                ctxt = ["Context:=", self.matrix, "Matrix:=", self.reduced_matrix]
        elif self._post.post_solution_type in ["HFSS3DLayout"]:
            if self.domain == "DCIR":
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        37010,
                        0,
                        2,
                        0,
                        False,
                        False,
                        -1,
                        1,
                        0,
                        1,
                        1,
                        "",
                        0,
                        0,
                        "DCIRID",
                        False,
                        str(self.siwave_dc_category),
                        "IDIID",
                        False,
                        "1",
                    ],
                ]
            elif self.differential_pairs:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        self._did,
                        0,
                        2,
                        self.pulse_rise_time,
                        self.use_pulse_in_tdr if self.pulse_rise_time else False,
                        False,
                        -1,
                        1,
                        self.time_windowing,
                        1,
                        1,
                        "",
                        self.pulse_rise_time / 5,
                        self.pulse_rise_time * 100,
                        "EnsDiffPairKey",
                        False,
                        "1",
                        "IDIID",
                        False,
                        "1" if not self.pulse_rise_time else "3",
                    ],
                ]
            else:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        self._did,
                        0,
                        2,
                        self.pulse_rise_time,
                        self.use_pulse_in_tdr if self.pulse_rise_time else False,
                        False,
                        -1,
                        1,
                        self.time_windowing,
                        1,
                        1,
                        "",
                        self.pulse_rise_time / 5,
                        self.pulse_rise_time * 100,
                        "IDIID",
                        False,
                        "1" if not self.pulse_rise_time else "3",
                    ],
                ]
        elif self._post.post_solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [
                    self._did,
                    0,
                    2,
                    self.pulse_rise_time,
                    self.use_pulse_in_tdr if self.pulse_rise_time else False,
                    False,
                    -1,
                    1,
                    self.time_windowing,
                    1,
                    1,
                    "",
                    self.pulse_rise_time / 5,
                    self.pulse_rise_time * 100,
                ],
            ]
            if self.sub_design_id:
                ctxt_temp = ["NUMLEVELS", False, "1", "SUBDESIGNID", False, str(self.sub_design_id)]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.differential_pairs:
                ctxt_temp = ["USE_DIFF_PAIRS", False, "1"]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.domain == "Time":
                if self.time_start:
                    ctxt[2].extend(["WS", False, self.time_start])
                if self.time_stop:
                    ctxt[2].extend(["WE", False, self.time_stop])
        elif self._post.post_solution_type in ["NexximAMI"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "NUMLEVELS", False, "1"],
            ]
            qty = re.sub("<[^>]+>", "", self.expressions[0])
            if qty == "InitialWave":
                ctxt_temp = ["QTID", False, "0", "SCID", False, "-1", "SID", False, "0"]
            elif qty == "WaveAfterSource":
                ctxt_temp = ["QTID", False, "1", "SCID", False, "-1", "SID", False, "0"]
            elif qty == "WaveAfterChannel":
                ctxt_temp = [
                    "PCID",
                    False,
                    "-1",
                    "PID",
                    False,
                    "0",
                    "QTID",
                    False,
                    "2",
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ]
            elif qty == "WaveAfterProbe":
                ctxt_temp = [
                    "PCID",
                    False,
                    "-1",
                    "PID",
                    False,
                    "0",
                    "QTID",
                    False,
                    "3",
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ]
            elif qty == "ClockTics":
                ctxt_temp = ["PCID", False, "-1", "PID", False, "0"]
            else:
                return None
            for el in ctxt_temp:
                ctxt[2].append(el)

        elif self.differential_pairs:
            ctxt = ["Diff:=", "differential_pairs", "Domain:=", self.domain]
        else:
            ctxt = ["Domain:=", self.domain]
        return ctxt


class AntennaParameters(Standard):
    """Provides a reporting class that fits antenna parameter reports in an HFSS plot."""

    def __init__(self, app, report_category, setup_name, far_field_sphere=None, expressions=None):
        Standard.__init__(self, app, report_category, setup_name, expressions)
        self.far_field_sphere = far_field_sphere

    @property
    def far_field_sphere(self):
        """Far field sphere name.

        Returns
        -------
        str
            Name of the far field sphere.
        """
        return self.props["context"].get("far_field_sphere", None)

    @far_field_sphere.setter
    def far_field_sphere(self, value):
        self.props["context"]["far_field_sphere"] = value

    @property
    def _context(self):
        ctxt = ["Context:=", self.far_field_sphere]
        return ctxt


class Fields(CommonReport):
    """Provides for managing fields."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Sweep"
        self.polyline = None
        self.point_number = 1001
        self.primary_sweep = "Distance"

    @property
    def point_number(self):
        """Polygon point number.

        Returns
        -------
        str
            Point number.
        """
        return self.props["context"].get("point_number", None)

    @point_number.setter
    def point_number(self, value):
        self.props["context"]["point_number"] = value

    @property
    def _context(self):
        ctxt = []
        if self.polyline:
            ctxt = ["Context:=", self.polyline, "PointCount:=", self.point_number]
        return ctxt


class NearField(CommonReport):
    """Provides for managing near field reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Sweep"

    @property
    def _context(self):
        return ["Context:=", self.near_field]

    @property
    def near_field(self):
        """Near field name.

        Returns
        -------
        str
            Field name.
        """
        return self.props["context"].get("near_field", None)

    @near_field.setter
    def near_field(self, value):
        self.props["context"]["near_field"] = value


class FarField(CommonReport):
    """Provides for managing far field reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Sweep"
        self.primary_sweep = "Phi"
        self.secondary_sweep = "Theta"
        self.source_context = None
        self.source_group = None
        if "Phi" not in self.variations:
            self.variations["Phi"] = ["All"]
        if "Theta" not in self.variations:
            self.variations["Theta"] = ["All"]
        if "Freq" not in self.variations:
            self.variations["Freq"] = ["Nominal"]

    @property
    def far_field_sphere(self):
        """Far field sphere name.

        Returns
        -------
        str
            Field name.
        """
        return self.props.get("far_field_sphere", None)

    @far_field_sphere.setter
    def far_field_sphere(self, value):
        self.props["far_field_sphere"] = value

    @property
    def _context(self):
        if self.source_context:
            return ["Context:=", self.far_field_sphere, "SourceContext:=", self.source_context]
        if self.source_group:
            return ["Context:=", self.far_field_sphere, "Source Group:=", self.source_group]
        return ["Context:=", self.far_field_sphere]


class AMIConturEyeDiagram(CommonReport):
    """Provides for managing eye contour diagram reports in AMI analysis."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Time"
        self.props["report_type"] = "Rectangular Contour Plot"
        self.variations.pop("Time", None)
        self.props["context"]["variations"]["__UnitInterval"] = "All"
        self.props["context"]["variations"]["__Amplitude"] = "All"
        self.props["context"]["variations"]["__EyeOpening"] = "0"
        self.quantity_type = 0
        self.min_latch_overlay = "0"
        self.noise_floor = "1e-16"
        self.enable_jitter_distribution = False
        self.rx_rj = "0"
        self.rx_dj = "0"
        self.rx_sj = "0"
        self.rx_dcd = "0"
        self.rx_gaussian_noise = "0"
        self.rx_uniform_noise = "0"

    @property
    def expressions(self):
        """Expressions.

        Returns
        -------
        str
        """
        if self.props.get("expressions", None) is None:
            return []
        expr_head = "Eye"
        new_exprs = []
        for expr_dict in self.props["expressions"]:
            expr = expr_dict["name"]
            if not ".int_ami" in expr:
                qtype = int(self.quantity_type)
                if qtype == 0:
                    new_exprs.append("Initial{}(".format(expr_head) + expr + ".int_ami_tx)<Bit Error Rate>")
                elif qtype == 1:
                    new_exprs.append("{}AfterSource(".format(expr_head) + expr + ".int_ami_tx)<Bit Error Rate>")
                elif qtype == 2:
                    new_exprs.append("{}AfterChannel(".format(expr_head) + expr + ".int_ami_rx)<Bit Error Rate>")
                elif qtype == 3:
                    new_exprs.append("{}AfterProbe(".format(expr_head) + expr + ".int_ami_rx)<Bit Error Rate>")
        return new_exprs

    @expressions.setter
    def expressions(self, value):
        if isinstance(value, dict):
            self.props["expressions"].append = value
        elif isinstance(value, list):
            self.props["expressions"] = []
            for el in value:
                if isinstance(el, dict):
                    self.props["expressions"].append(el)
                else:
                    self.props["expressions"].append({"name": el})
        elif isinstance(value, str):
            if isinstance(self.props["expressions"], list):
                self.props["expressions"].append({"name": value})
            else:
                self.props["expressions"] = [{"name": value}]

    @property
    def quantity_type(self):
        """Quantity type used in the AMI analysis plot.

        Returns
        -------
        int
            Quantity type.
        """
        return self.props.get("quantity_type", 0)

    @quantity_type.setter
    def quantity_type(self, value):
        self.props["quantity_type"] = value

    @property
    def report_category(self):
        """Report category.

        Returns
        -------
        str
            Report category.
        """
        return self.props["report_category"]

    @property
    def _context(self):
        sim_context = [
            55819,
            0,
            2,
            0,
            False,
            False,
            -1,
            1,
            0,
            1,
            1,
            "",
            0,
            0,
            "MLO",
            False,
            str(self.min_latch_overlay),
            "NUMLEVELS",
            False,
            "1",
            "ORJ",
            False,
            "1",
            "PCID",
            False,
            "-1",
            "PID",
            False,
            "0",
            "PRIDIST",
            False,
            "0",
            "QTID",
            False,
            str(self.quantity_type),
            "USE_PRI_DIST",
            False,
            "0" if not self.enable_jitter_distribution else "1",
            "SID",
            False,
            "0",
        ]
        if self.enable_jitter_distribution and str(self.quantity_type) == "3":
            sim_context = [
                55819,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "DCD",
                False,
                str(self.rx_dcd),
                "DJ",
                False,
                str(self.rx_dj),
                "GNOI",
                False,
                "3.5",
                "MLO",
                False,
                str(self.min_latch_overlay),
                "NF",
                False,
                str(self.noise_floor),
                "NUMLEVELS",
                False,
                "1",
                "ORJ",
                False,
                "1",
                "PCID",
                False,
                "-1",
                "PID",
                False,
                "0",
                "SID",
                False,
                "0",
                "PRIDIST",
                False,
                "0",
                "QTID",
                False,
                str(self.quantity_type),
                "RJ",
                False,
                str(self.rx_rj),
                "SJ",
                False,
                str(self.rx_sj),
                "UNOI",
                False,
                str(self.rx_uniform_noise),
                "USE_PRI_DIST",
                False,
                "0" if not self.enable_jitter_distribution else "1",
            ]

        arg = [
            "NAME:Context",
            "SimValueContext:=",
            sim_context,
        ]
        if len(self.expressions) == 1:
            sid = 0
            pid = 0
            expr = self.expressions[0]
            category = "Eye"
            found = False
            while not found:
                available_quantities = self._post.available_report_quantities(
                    self.report_category, self.report_type, self.setup, category, arg
                )
                if len(available_quantities) == 1 and available_quantities[0].lower() == expr.lower():
                    found = True
                else:
                    sid += 1
                    pid += 1
                    arg[2][arg[2].index("SID") + 2] = str(sid)
                    arg[2][arg[2].index("PID") + 2] = str(pid)
                # Limited maximum iterations to 1000 in While loop (Too many probes to analyze even in a single design)
                if sid > 1000:
                    self._post.logger.error(
                        "Failed to find right context for expression : {}".format(",".join(self.expressions))
                    )
                    # arg[2][arg[2].index("SID") + 2] = "0"
                    # arg[2][arg[2].index("PID") + 2] = "0"
                    break
        return arg

    @property
    def _trace_info(self):
        new_exprs = self.expressions if isinstance(self.expressions, list) else [self.expressions]
        return ["X Component:=", "__UnitInterval", "Y Component:=", "__Amplitude", "Z Component:=", new_exprs]

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create an eye diagram report.

        Parameters
        ----------
        name : str, optional
            Plot name. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            self.report_category,
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            self._trace_info,
        )
        self._post.plots.append(self)
        self._is_created = True

        return True

    @pyaedt_function_handler(xunits="x_units", yunits="y_units", xoffset="x_offset", yoffset="y_offset")
    def eye_mask(
        self,
        points,
        x_units="ns",
        y_units="mV",
        enable_limits=False,
        upper_limit=500,
        lower_limit=-500,
        color=(0, 255, 0),
        x_offset="0ns",
        y_offset="0V",
        transparency=0.3,
    ):
        """Create an eye diagram in the plot.

        Parameters
        ----------
        points : list
            Points of the eye mask in the format ``[[x1,y1,],[x2,y2],...]``.
        x_units : str, optional
            X points units. The default is ``"ns"``.
        y_units : str, optional
            Y points units. The default is ``"mV"``.
        enable_limits : bool, optional
            Whether to enable the upper and lower limits. The default is ``False``.
        upper_limit : float, optional
            Upper limit if limits are enabled. The default is ``500``.
        lower_limit : str, optional
            Lower limit if limits are enabled. The default is ``-500``.
        color : tuple, optional
            Mask in (R, G, B) color. The default is ``(0, 255, 0)``.
            Each color value must be an integer in a range from 0 to 255.
        x_offset : str, optional
            Mask time offset with units. The default is ``"0ns"``.
        y_offset : str, optional
            Mask value offset with units. The default is ``"0V"``.
        transparency : float, optional
            Mask transparency. The default is ``0.3``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if "quantity_type" in dir(self) and self.report_type == "Rectangular Contour Plot":
            props = [
                "NAME:AllTabs",
                ["NAME:Mask", ["NAME:PropServers", "{}: Plot {}".format(self.plot_name, self.traces[0].name)]],
            ]
        else:
            props = [
                "NAME:AllTabs",
                ["NAME:Mask", ["NAME:PropServers", "{}:EyeDisplayTypeProperty".format(self.plot_name)]],
            ]
        arg = [
            "NAME:Mask",
            "Version:=",
            1,
            "ShowLimits:=",
            enable_limits,
            "UpperLimit:=",
            upper_limit if upper_limit else 1,
            "LowerLimit:=",
            lower_limit if lower_limit else 0,
            "XUnits:=",
            x_units,
            "YUnits:=",
            y_units,
        ]
        mask_points = ["NAME:MaskPoints"]
        for point in points:
            mask_points.append(point[0])
            mask_points.append(point[1])
        arg.append(mask_points)
        args = ["NAME:ChangedProps", arg]
        if not ("quantity_type" in dir(self) and self.report_type == "Rectangular Contour Plot"):
            args.append(["NAME:Mask Fill Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
            args.append(["NAME:X Offset", "Value:=", x_offset])
            args.append(["NAME:Y Offset", "Value:=", y_offset])
            args.append(["NAME:Mask Trans", "Transparency:=", transparency])
        props[1].append(args)
        self._post.oreportsetup.ChangeProperty(props)

        return True

    @pyaedt_function_handler(value="enable")
    def rectangular_plot(self, enable=True):
        """Enable or disable the rectangular plot on the chart.

        Parameters
        ----------
        enable : bool
            Whether to enable the rectangular plot. The default is ``True``. If
            ``False``, the rectangular plot is disabled.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:AllTabs",
            ["NAME:Eye", ["NAME:PropServers", "{}:EyeDisplayTypeProperty".format(self.plot_name)]],
        ]
        args = ["NAME:ChangedProps", ["NAME:Rectangular Plot", "Value:=", enable]]
        props[1].append(args)
        self._post.oreportsetup.ChangeProperty(props)

        return True

    @pyaedt_function_handler()
    def add_all_eye_measurements(self):
        """Add all eye measurements to the plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._post.oreportsetup.AddAllEyeMeasurements(self.plot_name)
        return True

    @pyaedt_function_handler()
    def clear_all_eye_measurements(self):
        """Clear all eye measurements from the plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._post.oreportsetup.ClearAllTraceCharacteristics(self.plot_name)
        return True

    @pyaedt_function_handler(trace_name="name")
    def add_trace_characteristics(self, name, arguments=None, solution_range=None):
        """Add a trace characteristic to the plot.

        Parameters
        ----------
        name : str
            Name of the trace characteristic.
        arguments : list, optional
            Arguments if any. The default is ``None``.
        solution_range : list, optional
            Output range. The default is ``None``, in which case
            the full range is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not arguments:
            arguments = []
        if not solution_range:
            solution_range = ["Full"]
        self._post.oreportsetup.AddTraceCharacteristics(self.plot_name, name, arguments, solution_range)
        return True

    @pyaedt_function_handler(out_file="output_file")
    def export_mask_violation(self, output_file=None):
        """Export the eye diagram mask violations to a TAB file.

        Parameters
        ----------
        output_file : str, optional
            Full path to the TAB file. The default is ``None``, in which case
            the violations are exported to a TAB file in the working directory.

        Returns
        -------
        str
            Output file path if a TAB file is created.
        """
        if not output_file:
            output_file = os.path.join(self._post._app.working_directory, "{}_violations.tab".format(self.plot_name))
        self._post.oreportsetup.ExportEyeMaskViolation(self.plot_name, output_file)
        return output_file


class AMIEyeDiagram(CommonReport):
    """Provides for managing eye diagram reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Time"
        if report_category == "Statistical Eye":
            self.props["report_type"] = "Statistical Eye Plot"
            self.variations.pop("Time", None)
            self.variations["__UnitInterval"] = "All"
            self.variations["__Amplitude"] = "All"
        self.unit_interval = "0s"
        self.offset = "0ms"
        self.auto_delay = True
        self.manual_delay = "0ps"
        self.auto_cross_amplitude = True
        self.cross_amplitude = "0mV"
        self.auto_compute_eye_meas = True
        self.eye_measurement_point = "5e-10s"
        self.quantity_type = 0

    @property
    def expressions(self):
        """Expressions.

        Returns
        -------
        str
        """
        if self.props.get("expressions", None) is None:
            return []
        expr_head = "Wave"
        if self.report_category == "Statistical Eye":
            expr_head = "Eye"
        new_exprs = []
        for expr_dict in self.props["expressions"]:
            expr = expr_dict["name"]
            if not ".int_ami" in expr:
                qtype = int(self.quantity_type)
                if qtype == 0:
                    new_exprs.append("Initial{}<".format(expr_head) + expr + ".int_ami_tx>")
                elif qtype == 1:
                    new_exprs.append("{}AfterSource<".format(expr_head) + expr + ".int_ami_tx>")
                elif qtype == 2:
                    new_exprs.append("{}AfterChannel<".format(expr_head) + expr + ".int_ami_rx>")
                elif qtype == 3:
                    new_exprs.append("{}AfterProbe<".format(expr_head) + expr + ".int_ami_rx>")
        return new_exprs

    @expressions.setter
    def expressions(self, value):
        if isinstance(value, dict):
            self.props["expressions"].append = value
        elif isinstance(value, list):
            self.props["expressions"] = []
            for el in value:
                if isinstance(el, dict):
                    self.props["expressions"].append(el)
                else:
                    self.props["expressions"].append({"name": el})
        elif isinstance(value, str):
            if isinstance(self.props["expressions"], list):
                self.props["expressions"].append({"name": value})
            else:
                self.props["expressions"] = [{"name": value}]

    @property
    def quantity_type(self):
        """Quantity type used in the AMI analysis plot.

        Returns
        -------
        int
            Quantity type.
        """
        return self.props.get("quantity_type", 0)

    @quantity_type.setter
    def quantity_type(self, value):
        self.props["quantity_type"] = value

    @property
    def report_category(self):
        """Report category.

        Returns
        -------
        str
            Report category.
        """
        return self.props["report_category"]

    @report_category.setter
    def report_category(self, value):
        self.props["report_category"] = value
        if self.props["report_category"] == "Statistical Eye" and self.report_type == "Rectangular Plot":
            self.props["report_type"] = "Statistical Eye Plot"
            self.variations.pop("Time", None)
            self.variations["__UnitInterval"] = "All"
            self.variations["__Amplitude"] = "All"
        elif self.props["report_category"] == "Eye Diagram" and self.report_type == "Statistical Eye Plot":
            self.props["report_type"] = "Rectangular Plot"
            self.variations.pop("__UnitInterval", None)
            self.variations.pop("__Amplitude", None)
            self.variations["Time"] = "All"

    @property
    def unit_interval(self):
        """Unit interval value.

        Returns
        -------
        str
            Unit interval.
        """
        return self.props["context"].get("unit_interval", None)

    @unit_interval.setter
    def unit_interval(self, value):
        self.props["context"]["unit_interval"] = value

    @property
    def offset(self):
        """Offset value.

        Returns
        -------
        str
            Offset value.
        """
        return self.props["context"].get("offset", None)

    @offset.setter
    def offset(self, value):
        self.props["context"]["offset"] = value

    @property
    def auto_delay(self):
        """Auto-delay flag.

        Returns
        -------
        bool
            ``True`` if auto-delay is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("auto_delay", None)

    @auto_delay.setter
    def auto_delay(self, value):
        self.props["context"]["auto_delay"] = value

    @property
    def manual_delay(self):
        """Manual delay value when ``auto_delay=False``.

        Returns
        -------
        str
            ``True`` if manual-delay is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("manual_delay", None)

    @manual_delay.setter
    def manual_delay(self, value):
        self.props["context"]["manual_delay"] = value

    @property
    def auto_cross_amplitude(self):
        """Auto-cross amplitude flag.

        Returns
        -------
        bool
            ``True`` if auto-cross amplitude is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("auto_cross_amplitude", None)

    @auto_cross_amplitude.setter
    def auto_cross_amplitude(self, value):
        self.props["context"]["auto_cross_amplitude"] = value

    @property
    def cross_amplitude(self):
        """Cross-amplitude value when ``auto_cross_amplitude=False``.

        Returns
        -------
        str
            Cross-amplitude.
        """
        return self.props["context"].get("cross_amplitude", None)

    @cross_amplitude.setter
    def cross_amplitude(self, value):
        self.props["context"]["cross_amplitude"] = value

    @property
    def auto_compute_eye_meas(self):
        """Flag for automatically computing eye measurements.

        Returns
        -------
        bool
            ``True`` to compute eye measurements, ``False`` otherwise.
        """
        return self.props["context"].get("auto_compute_eye_meas", None)

    @auto_compute_eye_meas.setter
    def auto_compute_eye_meas(self, value):
        self.props["context"]["auto_compute_eye_meas"] = value

    @property
    def eye_measurement_point(self):
        """Eye measurement point.

        Returns
        -------
        str
            Eye measurement point.
        """
        return self.props["context"].get("eye_measurement_point", None)

    @eye_measurement_point.setter
    def eye_measurement_point(self, value):
        self.props["context"]["eye_measurement_point"] = value

    @property
    def _context(self):
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                1,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "-1",
                False,
                "0",
                "NUMLEVELS",
                False,
                "1",
                "PCID",
                False,
                "-1",
                "PID",
                False,
                "0",
                "QTID",
                False,
                str(self.quantity_type),
                "SCID",
                False,
                "-1",
                "SID",
                False,
                "0",
            ],
        ]
        if self.report_category == "Statistical Eye":
            arg = [
                "NAME:Context",
                "SimValueContext:=",
                [
                    55819,
                    0,
                    2,
                    0,
                    False,
                    False,
                    -1,
                    1,
                    0,
                    1,
                    1,
                    "",
                    0,
                    0,
                    "NUMLEVELS",
                    False,
                    "1",
                    "PCID",
                    False,
                    "-1",
                    "PID",
                    False,
                    "0",
                    "QTID",
                    False,
                    str(self.quantity_type),
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ],
            ]
        if len(self.expressions) == 1:
            sid = 0
            pid = 0
            expr = self.expressions[0]
            category = "Wave"
            if self.report_category == "Statistical Eye":
                category = "Eye"
            if self.report_category == "Eye Diagram" and self.report_type == "Rectangular Plot":
                category = "Voltage"
            found = False
            while not found:
                available_quantities = self._post.available_report_quantities(
                    self.report_category, self.report_type, self.setup, category, arg
                )
                if len(available_quantities) == 1 and available_quantities[0].lower() == expr.lower():
                    found = True
                else:
                    sid += 1
                    pid += 1
                    arg[2][arg[2].index("SID") + 2] = str(sid)
                    arg[2][arg[2].index("PID") + 2] = str(pid)
                # Limited maximum iterations to 1000 in While loop (Too many probes to analyze even in a single design)
                if sid > 1000:
                    self._post.logger.error(
                        "Failed to find right context for expression : {}".format(",".join(self.expressions))
                    )
                    # arg[2][arg[2].index("SID") + 2] = "0"
                    # arg[2][arg[2].index("PID") + 2] = "0"
                    break
        return arg

    @property
    def _trace_info(self):
        new_exprs = self.expressions if isinstance(self.expressions, list) else [self.expressions]
        if self.report_category == "Statistical Eye":
            return [
                "X Component:=",
                "__UnitInterval",
                "Y Component:=",
                "__Amplitude",
                "Eye Diagram Component:=",
                new_exprs,
            ]
        return ["Component:=", new_exprs]

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create an eye diagram report.

        Parameters
        ----------
        name : str, optional
            Plot name. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        options = [
            "Unit Interval:=",
            self.unit_interval,
            "Offset:=",
            self.offset,
            "Auto Delay:=",
            self.auto_delay,
            "Manual Delay:=",
            self.manual_delay,
            "AutoCompCrossAmplitude:=",
            self.auto_cross_amplitude,
            "CrossingAmplitude:=",
            self.cross_amplitude,
            "AutoCompEyeMeasurementPoint:=",
            self.auto_compute_eye_meas,
            "EyeMeasurementPoint:=",
            self.eye_measurement_point,
        ]
        if self.report_category == "Statistical Eye":
            self._post.oreportsetup.CreateReport(
                self.plot_name,
                self.report_category,
                self.report_type,
                self.setup,
                self._context,
                self._convert_dict_to_report_sel(self.variations),
                self._trace_info,
            )
        else:
            self._post.oreportsetup.CreateReport(
                self.plot_name,
                self.report_category,
                self.report_type,
                self.setup,
                self._context,
                self._convert_dict_to_report_sel(self.variations),
                self._trace_info,
                options,
            )
        self._post.plots.append(self)
        self._is_created = True

        return True

    @pyaedt_function_handler(xunits="x_units", yunits="y_units", xoffset="x_offset", yoffset="y_offset")
    def eye_mask(
        self,
        points,
        x_units="ns",
        y_units="mV",
        enable_limits=False,
        upper_limit=500,
        lower_limit=-500,
        color=(0, 255, 0),
        x_offset="0ns",
        y_offset="0V",
        transparency=0.3,
    ):
        """Create an eye diagram in the plot.

        Parameters
        ----------
        points : list
            Points of the eye mask in the format ``[[x1,y1,],[x2,y2],...]``.
        x_units : str, optional
            X points units. The default is ``"ns"``.
        y_units : str, optional
            Y points units. The default is ``"mV"``.
        enable_limits : bool, optional
            Whether to enable the upper and lower limits. The default is ``False``.
        upper_limit : float, optional
            Upper limit if limits are enabled. The default is ``500``.
        lower_limit : str, optional
            Lower limit if limits are enabled. The default is ``-500``.
        color : tuple, optional
            Mask in (R, G, B) color. The default is ``(0, 255, 0)``.
            Each color value must be an integer in a range from 0 to 255.
        x_offset : str, optional
            Mask time offset with units. The default is ``"0ns"``.
        y_offset : str, optional
            Mask value offset with units. The default is ``"0V"``.
        transparency : float, optional
            Mask transparency. The default is ``0.3``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = [
            "NAME:AllTabs",
            ["NAME:Mask", ["NAME:PropServers", "{}:EyeDisplayTypeProperty".format(self.plot_name)]],
        ]
        arg = [
            "NAME:Mask",
            "Version:=",
            1,
            "ShowLimits:=",
            enable_limits,
            "UpperLimit:=",
            upper_limit if upper_limit else 1,
            "LowerLimit:=",
            lower_limit if lower_limit else 0,
            "XUnits:=",
            x_units,
            "YUnits:=",
            y_units,
        ]
        mask_points = ["NAME:MaskPoints"]
        for point in points:
            mask_points.append(point[0])
            mask_points.append(point[1])
        arg.append(mask_points)
        args = ["NAME:ChangedProps", arg]
        args.append(["NAME:Mask Fill Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        args.append(["NAME:X Offset", "Value:=", x_offset])
        args.append(["NAME:Y Offset", "Value:=", y_offset])
        args.append(["NAME:Mask Trans", "Transparency:=", transparency])
        props[1].append(args)
        self._post.oreportsetup.ChangeProperty(props)

        return True

    @pyaedt_function_handler(value="enable")
    def rectangular_plot(self, enable=True):
        """Enable or disable the rectangular plot on the chart.

        Parameters
        ----------
        enable : bool
            Whether to enable the rectangular plot. The default is ``True``. When
            ``False``, the rectangular plot is disabled.

        Returns
        -------
        bool
        """
        props = [
            "NAME:AllTabs",
            ["NAME:Eye", ["NAME:PropServers", "{}:EyeDisplayTypeProperty".format(self.plot_name)]],
        ]
        args = ["NAME:ChangedProps", ["NAME:Rectangular Plot", "Value:=", enable]]
        props[1].append(args)
        self._post.oreportsetup.ChangeProperty(props)

        return True

    @pyaedt_function_handler()
    def add_all_eye_measurements(self):
        """Add all eye measurements to the plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._post.oreportsetup.AddAllEyeMeasurements(self.plot_name)
        return True

    @pyaedt_function_handler()
    def clear_all_eye_measurements(self):
        """Clear all eye measurements from the plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._post.oreportsetup.ClearAllTraceCharacteristics(self.plot_name)
        return True

    @pyaedt_function_handler(trace_name="name")
    def add_trace_characteristics(self, name, arguments=None, solution_range=None):
        """Add a trace characteristic to the plot.

        Parameters
        ----------
        name : str
            Name of the trace characteristic.
        arguments : list, optional
            Arguments if any. The default is ``None``.
        solution_range : list, optional
            Output range. The default is ``None``, in which case
            the full range is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not arguments:
            arguments = []
        if not solution_range:
            solution_range = ["Full"]
        self._post.oreportsetup.AddTraceCharacteristics(self.plot_name, name, arguments, solution_range)
        return True

    @pyaedt_function_handler(out_file="output_file")
    def export_mask_violation(self, output_file=None):
        """Export the eye diagram mask violations to a TAB file.

        Parameters
        ----------
        output_file : str, optional
            Full path to the TAB file. The default is ``None``, in which case
            the violations are exported to a TAB file in the working directory.

        Returns
        -------
        str
            Output file path if a TAB file is created.
        """
        if not output_file:
            output_file = os.path.join(self._post._app.working_directory, "{}_violations.tab".format(self.plot_name))
        self._post.oreportsetup.ExportEyeMaskViolation(self.plot_name, output_file)
        return output_file


class EyeDiagram(AMIEyeDiagram):
    """Provides for managing eye diagram reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        AMIEyeDiagram.__init__(self, app, report_category, setup_name, expressions)
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self.thinning = False
        self.dy_dx_tolerance = 0.001
        self.thinning_points = 500000000

    @property
    def expressions(self):
        """Expressions.

        Returns
        -------
        str
            Expressions.
        """
        if self.props.get("expressions", None) is None:
            return []
        return [k.get("name", None) for k in self.props["expressions"] if k.get("name", None) is not None]

    @expressions.setter
    def expressions(self, value):
        if isinstance(value, dict):
            self.props["expressions"].append = value
        elif isinstance(value, list):
            self.props["expressions"] = []
            for el in value:
                if isinstance(el, dict):
                    self.props["expressions"].append(el)
                else:
                    self.props["expressions"].append({"name": el})
        elif isinstance(value, str):
            if isinstance(self.props["expressions"], list):
                self.props["expressions"].append({"name": value})
            else:
                self.props["expressions"] = [{"name": value}]

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start.
        """
        return self.props["context"].get("time_start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["context"]["time_start"] = value

    @property
    def time_stop(self):
        """Time stop value.

        Returns
        -------
        str
            Time stop.
        """
        return self.props["context"].get("time_stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["context"]["time_stop"] = value

    @property
    def thinning(self):
        """Thinning flag.

        Returns
        -------
        bool
            ``True`` if thinning is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("thinning", None)

    @thinning.setter
    def thinning(self, value):
        self.props["context"]["thinning"] = value

    @property
    def dy_dx_tolerance(self):
        """DY DX tolerance.

        Returns
        -------
        float
            DY DX tolerance.
        """
        return self.props["context"].get("dy_dx_tolerance", None)

    @dy_dx_tolerance.setter
    def dy_dx_tolerance(self, value):
        self.props["context"]["dy_dx_tolerance"] = value

    @property
    def thinning_points(self):
        """Number of thinning points.

        Returns
        -------
        int
            Number of thinning points.
        """
        return self.props["context"].get("thinning_points", None)

    @thinning_points.setter
    def thinning_points(self, value):
        self.props["context"]["thinning_points"] = value

    @property
    def _context(self):
        if self.thinning:
            val = "1"
        else:
            val = "0"
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                1,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "DE",
                False,
                val,
                "DP",
                False,
                str(self.thinning_points),
                "DT",
                False,
                str(self.dy_dx_tolerance),
                "NUMLEVELS",
                False,
                "0",
                "WE",
                False,
                self.time_stop,
                "WM",
                False,
                "200ns",
                "WN",
                False,
                "0ps",
                "WS",
                False,
                self.time_start,
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return ["Component:=", self.expressions]
        else:
            return ["Component:=", [self.expressions]]


class Emission(CommonReport):
    """Provides for managing emission reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Sweep"


class Spectral(CommonReport):
    """Provides for managing spectral reports from transient data."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Spectrum"
        self.algorithm = "FFT"
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self.window = "Rectangular"
        self.kaiser_coeff = 0
        self.adjust_coherent_gain = True
        self.max_frequency = "10MHz"
        self.plot_continous_spectrum = False
        self.primary_sweep = "Spectrum"

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start.
        """
        return self.props["context"].get("time_start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["context"]["time_start"] = value

    @property
    def time_stop(self):
        """Time stop value.

        Returns
        -------
        str
            Time stop.
        """
        return self.props["context"].get("time_stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["context"]["time_stop"] = value

    @property
    def window(self):
        """Window value.

        Returns
        -------
        str
            Window.
        """
        return self.props["context"].get("window", None)

    @window.setter
    def window(self, value):
        self.props["context"]["window"] = value

    @property
    def kaiser_coeff(self):
        """Kaiser value.

        Returns
        -------
        str
            Kaiser coefficient.
        """
        return self.props["context"].get("kaiser_coeff", None)

    @kaiser_coeff.setter
    def kaiser_coeff(self, value):
        self.props["context"]["kaiser_coeff"] = value

    @property
    def adjust_coherent_gain(self):
        """Coherent gain flag.

        Returns
        -------
        bool
            ``True`` if coherent gain is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("adjust_coherent_gain", None)

    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value):
        self.props["context"]["adjust_coherent_gain"] = value

    @property
    def plot_continous_spectrum(self):
        """Continuous spectrum flag.

        Returns
        -------
        bool
            ``True`` if continuous spectrum is enabled, ``False`` otherwise.
        """
        return self.props["context"].get("plot_continous_spectrum", None)

    @plot_continous_spectrum.setter
    def plot_continous_spectrum(self, value):
        self.props["context"]["plot_continous_spectrum"] = value

    @property
    def max_frequency(self):
        """Maximum spectrum frequency.

        Returns
        -------
        str
            Maximum spectrum frequency.
        """
        return self.props["context"].get("max_frequency", None)

    @max_frequency.setter
    def max_frequency(self, value):
        self.props["context"]["max_frequency"] = value

    @property
    def _context(self):
        if self.algorithm == "FFT":
            it = "1"
        elif self.algorithm == "Fourier Integration":
            it = "0"
        else:
            it = "2"
        WT = {
            "Rectangular": "0",
            "Bartlett": "1",
            "Blackman": "2",
            "Hamming": "3",
            "Hanning": "4",
            "Kaiser": "5",
            "Welch": "6",
            "Weber": "7",
            "Lanzcos": "8",
        }
        wt = WT[self.window]
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                2,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "CP",
                False,
                "1" if self.plot_continous_spectrum else "0",
                "IT",
                False,
                it,
                "MF",
                False,
                self.max_frequency,
                "NUMLEVELS",
                False,
                "0",
                "TE",
                False,
                self.time_stop,
                "TS",
                False,
                self.time_start,
                "WT",
                False,
                wt,
                "WW",
                False,
                "100",
                "KP",
                False,
                str(self.kaiser_coeff),
                "CG",
                False,
                "1" if self.adjust_coherent_gain else "0",
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return self.expressions
        else:
            return [self.expressions]

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create an eye diagram report.

        Parameters
        ----------
        name : str, optional
            Plot name. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            "Standard",
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self._trace_info,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True
        return True


class EMIReceiver(CommonReport):
    """Provides for managing EMI receiver reports."""

    def __init__(self, app, setup_name, expressions=None):
        CommonReport.__init__(self, app, "EMIReceiver", setup_name, expressions)
        self.logger = app.logger
        self.domain = "EMI Receiver"
        self.available_nets = []
        self._net = "0"
        for comp in app.modeler.components.components.values():
            if comp.name == "CompInst@EMI_RCVR":
                self.available_nets.append(comp.pins[0].net)
        if self.available_nets:
            self._net = self.available_nets[0]
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self._emission = "CE"
        self.overlap_rate = 95
        self.band = "0"
        self.primary_sweep = "Freq"

    @property
    def net(self):
        """Net attached to the EMI receiver.

        Returns
        -------
        str
            Net name.
        """
        return self._net

    @net.setter
    def net(self, value):
        if value not in self.available_nets:
            self.logger.error("Net not available.")
        else:
            self._net = value

    @property
    def band(self):
        """Band attached to the EMI receiver.

        Returns
        -------
        str
            Band name.
        """
        return self.props["context"].get("band", None)

    @band.setter
    def band(self, value):
        self.props["context"]["band"] = value

    @property
    def emission(self):
        """Emission test.

        Options are ``"CE"`` and ``"RE"``.

        Returns
        -------
        str
            Emission.
        """
        return self._emission

    @emission.setter
    def emission(self, value):
        if value == "CE":
            self._emission = value
            self.props["context"]["emission"] = "0"
        elif value == "RE":
            self._emission = value
            self.props["context"]["emission"] = "1"
        else:
            self.logger.error("Emission must be 'CE' or 'RE', value '{}' is not valid.".format(value))

    @property
    def time_start(self):
        """Time start value.

        Returns
        -------
        str
            Time start.
        """
        return self.props["context"].get("time_start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["context"]["time_start"] = value

    @property
    def time_stop(self):
        """Time stop value.

        Returns
        -------
        str
            Time stop.
        """
        return self.props["context"].get("time_stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["context"]["time_stop"] = value

    @property
    def _context(self):

        if self.emission == "CE":
            em = "0"
        else:
            em = "1"

        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                55830,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                self.net,
                0,
                0,
                "BAND",
                False,
                self.band,
                "CG",
                False,
                "1",
                "EM",
                False,
                em,
                "KP",
                False,
                "0",
                "NUMLEVELS",
                False,
                "0",
                "OR",
                False,
                str(self.overlap_rate),
                "RBW",
                False,
                "9000Hz",
                "SIG",
                False,
                "0",
                "TCT",
                False,
                "1ms",
                "TDT",
                False,
                "160ms",
                "TE",
                False,
                self.time_stop,
                "TS",
                False,
                self.time_start,
                "WT",
                False,
                "6",
                "WW",
                False,
                "100",
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return self.expressions
        else:
            return [self.expressions]

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create an EMI receiver report.

        Parameters
        ----------
        name : str, optional
            Plot name. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not name:
            self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            "Standard",
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self._trace_info,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True
        return self
