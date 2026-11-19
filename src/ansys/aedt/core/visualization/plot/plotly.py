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

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
import math
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
import warnings

import numpy as np

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available

# Check that graphics are available
try:
    check_graphics_available()
    import plotly.graph_objects as go
    import plotly.offline as pyo

except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


class LineStyle(Enum):
    """Line style options for Plotly traces."""

    SOLID = "solid"
    DOT = "dot"
    DASH = "dash"
    LONGDASH = "longdash"
    DASHDOT = "dashdot"
    LONGDASHDOT = "longdashdot"


class ScaleType(Enum):
    """Axis scale types for Plotly plots."""

    LINEAR = "linear"
    LOG = "log"


class DataType(Enum):
    """Data type for trace input."""

    CARTESIAN = 0
    SPHERICAL = 1


class MarkerSymbol(Enum):
    """Marker symbol options for Plotly traces."""

    CIRCLE = "circle"
    SQUARE = "square"
    DIAMOND = "diamond"
    CROSS = "cross"
    X = "x"
    TRIANGLE_UP = "triangle-up"
    TRIANGLE_DOWN = "triangle-down"


@dataclass
class NoteProperties:
    """Properties for customizing a Plotly note/annotation."""

    text: str = ""
    position: Tuple[float, float] = (0, 0)
    background_color: Optional[str] = None
    background_visibility: bool = True
    border_visibility: bool = True
    border_width: float = 1
    border_color: str = "black"
    font_family: str = "Arial"
    font_size: float = 12
    italic: bool = False
    bold: bool = False
    color: str = "black"
    arrow_visible: bool = False
    arrow_color: str = "black"
    arrow_width: float = 1


@dataclass
class TraceProperties:
    """Properties for customizing a Plotly trace."""

    x_label: str = ""
    y_label: str = ""
    z_label: str = ""
    line_style: Union[LineStyle, str] = LineStyle.SOLID
    line_width: float = 2.0
    line_color: Optional[str] = None
    marker_symbol: Union[MarkerSymbol, str] = MarkerSymbol.CIRCLE
    marker_size: float = 8.0
    marker_color: Optional[str] = None
    fill_symbol: bool = False

    def __post_init__(self):
        """Convert string values to enums if needed."""
        if isinstance(self.line_style, str):
            try:
                self.line_style = LineStyle(self.line_style)
            except ValueError:
                # Keep as string if not a valid enum value
                pass

        if isinstance(self.marker_symbol, str):
            try:
                self.marker_symbol = MarkerSymbol(self.marker_symbol)
            except ValueError:
                # Keep as string if not a valid enum value
                pass


@dataclass
class PlotlyTrace:
    """A trace for Plotly plots."""

    name: str = ""
    properties: TraceProperties = field(default_factory=TraceProperties)
    _cartesian_data: Optional[List[np.ndarray]] = field(default=None, init=False)
    _spherical_data: Optional[List[np.ndarray]] = field(default=None, init=False)

    # Convenience properties for backward compatibility and easy access
    @property
    def x_label(self) -> str:
        """X-axis label."""
        return self.properties.x_label

    @x_label.setter
    def x_label(self, value: str) -> None:
        self.properties.x_label = value

    @property
    def y_label(self) -> str:
        """Y-axis label."""
        return self.properties.y_label

    @y_label.setter
    def y_label(self, value: str) -> None:
        self.properties.y_label = value

    @property
    def z_label(self) -> str:
        """Z-axis label."""
        return self.properties.z_label

    @z_label.setter
    def z_label(self, value: str) -> None:
        self.properties.z_label = value

    @property
    def line_style(self) -> Union[LineStyle, str]:
        """Line style."""
        return self.properties.line_style

    @line_style.setter
    def line_style(self, value: Union[LineStyle, str]) -> None:
        self.properties.line_style = value

    @property
    def line_width(self) -> float:
        """Line width."""
        return self.properties.line_width

    @line_width.setter
    def line_width(self, value: float) -> None:
        self.properties.line_width = value

    @property
    def line_color(self) -> Optional[str]:
        """Line color."""
        return self.properties.line_color

    @line_color.setter
    def line_color(self, value: Optional[str]) -> None:
        self.properties.line_color = value

    @property
    def marker_symbol(self) -> Union[MarkerSymbol, str]:
        """Marker symbol."""
        return self.properties.marker_symbol

    @marker_symbol.setter
    def marker_symbol(self, value: Union[MarkerSymbol, str]) -> None:
        self.properties.marker_symbol = value

    @property
    def marker_size(self) -> float:
        """Marker size."""
        return self.properties.marker_size

    @marker_size.setter
    def marker_size(self, value: float) -> None:
        self.properties.marker_size = value

    @property
    def marker_color(self) -> Optional[str]:
        """Marker color."""
        return self.properties.marker_color

    @marker_color.setter
    def marker_color(self, value: Optional[str]) -> None:
        self.properties.marker_color = value

    @property
    def fill_symbol(self) -> bool:
        """Fill marker flag."""
        return self.properties.fill_symbol

    @fill_symbol.setter
    def fill_symbol(self, value: bool) -> None:
        self.properties.fill_symbol = value

    @property
    def cartesian_data(self) -> Optional[List[np.ndarray]]:
        """Cartesian data as [x, y, z]."""
        return self._cartesian_data

    @cartesian_data.setter
    def cartesian_data(self, val: List[Any]) -> None:
        if val is None:
            self._cartesian_data = None
            return

        self._cartesian_data = []
        for el in val:
            if isinstance(el, (float, int, str)):
                self._cartesian_data.append(el)
            else:
                self._cartesian_data.append(np.array(el, dtype=float))

        # Automatically add z=0 for 2D data
        if len(self._cartesian_data) == 2:
            self._cartesian_data.append(np.zeros(len(self._cartesian_data[-1])))

    @property
    def spherical_data(self) -> Optional[List[np.ndarray]]:
        """Spherical data as [r, theta, phi] (angles in degrees)."""
        return self._spherical_data

    @spherical_data.setter
    def spherical_data(self, val: List[Any]) -> None:
        if val is None:
            self._spherical_data = None
            return

        self._spherical_data = []
        for el in val:
            if isinstance(el, (float, int, str)):
                self._spherical_data.append(el)
            else:
                self._spherical_data.append(np.array(el, dtype=float))

    @pyaedt_function_handler()
    def car2spherical(self):
        """Convert cartesian data to spherical and assigns to property spherical data."""
        if self._cartesian_data is None or len(self._cartesian_data) < 3:
            return

        x = np.array(self._cartesian_data[0], dtype=float)
        y = np.array(self._cartesian_data[1], dtype=float)
        z = np.array(self._cartesian_data[2], dtype=float)
        r = np.sqrt(x * x + y * y + z * z)
        theta = np.arccos(z / r) * 180 / math.pi  # to degrees
        phi = np.arctan2(y, x) * 180 / math.pi
        self._spherical_data = [r, theta, phi]

    @pyaedt_function_handler()
    def spherical2car(self):
        """Convert spherical data to cartesian data and assign to cartesian data property."""
        if self._spherical_data is None or len(self._spherical_data) < 3:
            return

        r = np.array(self._spherical_data[0], dtype=float)
        theta = np.array(self._spherical_data[1] * math.pi / 180, dtype=float)  # to radian
        phi = np.array(self._spherical_data[2] * math.pi / 180, dtype=float)
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        self._cartesian_data = [x, y, z]

    @pyaedt_function_handler()
    def car2polar(self, x, y, is_degree=False):
        """Convert cartesian data to polar.

        Parameters
        ----------
        x : array-like
            X coordinates.
        y : array-like
            Y coordinates.
        is_degree : bool, optional
            Whether angles are in degrees. Default is False (radians).

        Returns
        -------
        list
            List of [r, theta].
        """
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        if is_degree:
            theta = theta * 180 / math.pi
        return [r, theta]

    @pyaedt_function_handler()
    def polar2car(self, r, theta):
        """Convert polar data to cartesian data.

        Parameters
        ----------
        r : array-like
            Radial coordinates.
        theta : array-like
            Angular coordinates in degrees.

        Returns
        -------
        list
            List of [x, y].
        """
        r = np.array(r, dtype=float)
        theta = np.array(theta, dtype=float)
        x = r * np.cos(np.radians(theta))
        y = r * np.sin(np.radians(theta))
        return [x, y]


def is_notebook():
    """Return True if running in a Jupyter notebook."""
    try:
        shell = get_ipython().__class__.__name__
        return shell in ["ZMQInteractiveShell"]
    except NameError:
        return False


class LimitLineProperties:
    """Properties for customizing a Plotly limit line."""

    def __init__(self, x=None, y=None, orientation="h", color="red", width=2, dash="dash", name=""):
        self.x = x
        self.y = y
        self.orientation = orientation  # 'h' for horizontal, 'v' for vertical
        self.color = color
        self.width = width
        self.dash = dash
        self.name = name


class PlotlyLimitLine:
    """A limit line for Plotly plots."""

    def __init__(self, properties: LimitLineProperties):
        self.properties = properties
        self.name = properties.name or f"LimitLine_{id(self)}"


class RegionLimitProperties:
    """Properties for customizing a 3D region limit."""

    def __init__(
        self,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        z_min=None,
        z_max=None,
        color="lightblue",
        opacity=0.3,
        name="",
        show_edges=True,
        edge_color="blue",
        edge_width=2,
    ):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max
        self.color = color
        self.opacity = opacity
        self.name = name
        self.show_edges = show_edges
        self.edge_color = edge_color
        self.edge_width = edge_width


class PlotlyRegionLimit:
    """A region limit for 3D Plotly plots."""

    def __init__(self, properties: RegionLimitProperties):
        self.properties = properties
        self.name = properties.name or f"RegionLimit_{id(self)}"


class PlotlyNote:
    """A note/annotation for Plotly plots."""

    def __init__(self, properties: NoteProperties):
        self.properties = properties
        self.name = f"Note_{id(self)}"


class PlotlyPlotter:
    """Manager for creating and displaying Plotly plots."""

    def __init__(
        self,
        title: str = "",
        show_legend: bool = True,
        x_scale: Union[ScaleType, str] = ScaleType.LINEAR,
        y_scale: Union[ScaleType, str] = ScaleType.LINEAR,
        size: Tuple[int, int] = (800, 600),
        grid_color: str = "lightgray",
        background_color: str = "white",
        plot_color: str = "white",
    ):
        """Initialize the PlotlyPlotter."""
        self._traces: Dict[str, PlotlyTrace] = {}
        self._limit_lines: Dict[str, Any] = {}
        self._region_limits: Dict[str, Any] = {}
        self._notes: Dict[str, PlotlyNote] = {}
        self.title = title
        self.show_legend = show_legend
        self.size = size
        self.fig: Optional[Any] = None
        self.grid_color = grid_color
        self.grid_enable_major_x = True
        self.grid_enable_major_y = True
        self.grid_enable_minor_x = False
        self.grid_enable_minor_y = False
        self.background_color = background_color
        self.plot_color = plot_color
        self._x_scale = self._validate_scale(x_scale)
        self._y_scale = self._validate_scale(y_scale)

    @staticmethod
    def _validate_scale(scale: Union[ScaleType, str]) -> ScaleType:
        """Convert scale to ScaleType enum."""
        if isinstance(scale, ScaleType):
            return scale
        if isinstance(scale, str):
            try:
                return ScaleType(scale)
            except ValueError:
                raise ValueError(f"Invalid scale '{scale}'. Valid options: {[s.value for s in ScaleType]}")
        raise TypeError(f"Scale must be ScaleType or str, got {type(scale)}")

    @property
    def traces(self) -> Dict[str, PlotlyTrace]:
        """All traces in the plot."""
        return self._traces

    @property
    def trace_names(self) -> List[str]:
        """Names of all traces."""
        return list(self._traces.keys())

    @property
    def x_scale(self) -> ScaleType:
        """X axis scale type."""
        return self._x_scale

    @x_scale.setter
    def x_scale(self, value: Union[ScaleType, str]) -> None:
        self._x_scale = self._validate_scale(value)

    @property
    def y_scale(self) -> ScaleType:
        """Y axis scale type."""
        return self._y_scale

    @y_scale.setter
    def y_scale(self, value: Union[ScaleType, str]) -> None:
        self._y_scale = self._validate_scale(value)

    @property
    def notes(self) -> Dict[str, PlotlyNote]:
        """All notes in the plot."""
        return self._notes

    @property
    def note_names(self) -> List[str]:
        """Names of all notes."""
        return list(self._notes.keys())

    @pyaedt_function_handler()
    def add_trace(
        self,
        plot_data: List[Any],
        data_type: Union[DataType, int] = DataType.CARTESIAN,
        properties: Optional[Union[TraceProperties, Dict[str, Any]]] = None,
        name: str = "",
        x_label: str = "",
        y_label: str = "",
        z_label: str = "",
        line_style: Union[LineStyle, str] = LineStyle.SOLID,
        line_width: float = 2.0,
        line_color: Optional[str] = None,
        marker_symbol: Union[MarkerSymbol, str] = MarkerSymbol.CIRCLE,
        marker_size: float = 8.0,
        marker_color: Optional[str] = None,
        fill_symbol: bool = False,
    ) -> bool:
        """Add a trace to the plot.

        Accepts a TraceProperties object, a dictionary, or individual parameters.
        """
        # Convert data_type to enum if needed
        if isinstance(data_type, int):
            data_type = DataType(data_type)

        # Generate trace name if not provided
        trace_name = name or f"Trace_{len(self.traces)}"

        # Handle properties in a Pythonic way
        if properties is None:
            # Use individual parameters
            trace_props = TraceProperties(
                x_label=x_label,
                y_label=y_label,
                z_label=z_label,
                line_style=line_style,
                line_width=line_width,
                line_color=line_color,
                marker_symbol=marker_symbol,
                marker_size=marker_size,
                marker_color=marker_color,
                fill_symbol=fill_symbol,
            )
        elif isinstance(properties, TraceProperties):
            # Use provided TraceProperties dataclass
            trace_props = properties
        elif isinstance(properties, dict):
            # Convert dictionary to TraceProperties for backward compatibility
            trace_props = TraceProperties(
                x_label=properties.get("x_label", x_label),
                y_label=properties.get("y_label", y_label),
                z_label=properties.get("z_label", z_label),
                line_style=properties.get("line_style", line_style),
                line_width=properties.get("line_width", line_width),
                line_color=properties.get("line_color", line_color),
                marker_symbol=properties.get("marker_symbol", marker_symbol),
                marker_size=properties.get("marker_size", marker_size),
                marker_color=properties.get("marker_color", marker_color),
                fill_symbol=properties.get("fill_symbol", fill_symbol),
            )
        else:
            raise TypeError(f"Properties must be TraceProperties, dict, or None. Got {type(properties)}")

        # Create trace with the properties
        trace = PlotlyTrace(name=trace_name, properties=trace_props)

        # Set data based on type
        if data_type == DataType.CARTESIAN:
            trace.cartesian_data = plot_data
        else:
            trace.spherical_data = plot_data

        self._traces[trace.name] = trace
        return True

    @pyaedt_function_handler()
    def _retrieve_traces(self, traces):
        """Return traces by name, index, or list."""
        if traces is None:
            return list(self._traces.values())

        if isinstance(traces, str):
            if traces in self._traces:
                return [self._traces[traces]]
            else:
                return []

        if isinstance(traces, int):
            trace_list = list(self._traces.values())
            if 0 <= traces < len(trace_list):
                return [trace_list[traces]]
            else:
                return []

        if isinstance(traces, list):
            result = []
            for trace in traces:
                retrieved = self._retrieve_traces(trace)
                result.extend(retrieved)
            return result

        return []

    @pyaedt_function_handler()
    def add_limit(self, x=None, y=None, orientation="h", color="red", width=2, dash="dash", name="", properties=None):
        """Add a limit line or plane to the plot."""
        if properties is None:
            props = LimitLineProperties(
                x=x, y=y, orientation=orientation, color=color, width=width, dash=dash, name=name
            )
        else:
            props = properties
        limit_line = PlotlyLimitLine(props)
        self._limit_lines[limit_line.name] = limit_line
        return True

    @pyaedt_function_handler()
    def add_region_limit(
        self,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        z_min=None,
        z_max=None,
        color="lightblue",
        opacity=0.3,
        name="",
        show_edges=True,
        edge_color="blue",
        edge_width=2,
        properties=None,
    ):
        """Add a 3D region limit (bounding box) to the plot.

        Parameters
        ----------
        x_min, x_max : float, optional
            X-axis bounds for the region
        y_min, y_max : float, optional
            Y-axis bounds for the region
        z_min, z_max : float, optional
            Z-axis bounds for the region
        color : str, optional
            Fill color for the region box
        opacity : float, optional
            Opacity of the region box (0-1)
        name : str, optional
            Name for the region limit
        show_edges : bool, optional
            Whether to show edge lines
        edge_color : str, optional
            Color of the edge lines
        edge_width : float, optional
            Width of the edge lines
        properties : RegionLimitProperties, optional
            Properties object for the region limit
        """
        if properties is None:
            props = RegionLimitProperties(
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                z_min=z_min,
                z_max=z_max,
                color=color,
                opacity=opacity,
                name=name,
                show_edges=show_edges,
                edge_color=edge_color,
                edge_width=edge_width,
            )
        else:
            props = properties
        region_limit = PlotlyRegionLimit(props)
        self._region_limits[region_limit.name] = region_limit
        return True

    @pyaedt_function_handler()
    def add_note(
        self,
        text: Optional[str] = None,
        position: Tuple[float, float] = (0, 0),
        properties: Optional[NoteProperties] = None,
        background_color: Optional[str] = None,
        background_visibility: bool = True,
        border_visibility: bool = True,
        border_width: float = 1,
        border_color: str = "black",
        font_family: str = "Arial",
        font_size: float = 12,
        italic: bool = False,
        bold: bool = False,
        color: str = "black",
        arrow_visible: bool = False,
        arrow_color: str = "black",
        arrow_width: float = 1,
    ):
        """Add a note/annotation to the plot.

        Parameters
        ----------
        text : str, optional
            The text content of the note. Required when properties is None.
            If both text and properties are provided, text overrides the text in properties.
        position : tuple, optional
            Position of the note as (x, y) coordinates. Default is (0, 0).
            Ignored when properties is provided.
        properties : NoteProperties, optional
            Note properties object. If provided, individual parameters are ignored
            (except text, which overrides the text in properties).
        background_color : str, optional
            Background color of the note. Default is None (transparent).
            Ignored when properties is provided.
        background_visibility : bool, optional
            Whether to show the background. Default is True.
            Ignored when properties is provided.
        border_visibility : bool, optional
            Whether to show the border. Default is True.
            Ignored when properties is provided.
        border_width : float, optional
            Width of the border. Default is 1.
            Ignored when properties is provided.
        border_color : str, optional
            Color of the border. Default is "black".
            Ignored when properties is provided.
        font_family : str, optional
            Font family for the text. Default is "Arial".
            Ignored when properties is provided.
        font_size : float, optional
            Font size for the text. Default is 12.
            Ignored when properties is provided.
        italic : bool, optional
            Whether to use italic font. Default is False.
            Ignored when properties is provided.
        bold : bool, optional
            Whether to use bold font. Default is False.
            Ignored when properties is provided.
        color : str, optional
            Text color. Default is "black".
            Ignored when properties is provided.
        arrow_visible : bool, optional
            Whether to show an arrow pointing to the note. Default is False.
            Ignored when properties is provided.
        arrow_color : str, optional
            Color of the arrow. Default is "black".
            Ignored when properties is provided.
        arrow_width : float, optional
            Width of the arrow. Default is 1.
            Ignored when properties is provided.

        Returns
        -------
        bool
            True if successful.
        """
        if properties is None:
            # When no properties object is provided, text is required
            if text is None:
                raise ValueError("Text is required when properties object is not provided")
            props = NoteProperties(
                text=text,
                position=position,
                background_color=background_color,
                background_visibility=background_visibility,
                border_visibility=border_visibility,
                border_width=border_width,
                border_color=border_color,
                font_family=font_family,
                font_size=font_size,
                italic=italic,
                bold=bold,
                color=color,
                arrow_visible=arrow_visible,
                arrow_color=arrow_color,
                arrow_width=arrow_width,
            )
        else:
            # When properties object is provided, use it directly
            # If text is also provided, it overrides the text in properties
            if text is not None:
                # Create a copy of properties with overridden text
                props = NoteProperties(
                    text=text,
                    position=properties.position,
                    background_color=properties.background_color,
                    background_visibility=properties.background_visibility,
                    border_visibility=properties.border_visibility,
                    border_width=properties.border_width,
                    border_color=properties.border_color,
                    font_family=properties.font_family,
                    font_size=properties.font_size,
                    italic=properties.italic,
                    bold=properties.bold,
                    color=properties.color,
                    arrow_visible=properties.arrow_visible,
                    arrow_color=properties.arrow_color,
                    arrow_width=properties.arrow_width,
                )
            else:
                # Use properties as-is
                props = properties
        note = PlotlyNote(props)
        self._notes[note.name] = note
        return True

    @property
    def limit_lines(self):
        """All limit lines in the plot."""
        return self._limit_lines

    @property
    def limit_line_names(self):
        """Names of all limit lines."""
        return list(self._limit_lines.keys())

    @property
    def region_limits(self):
        """All region limits in the plot."""
        return self._region_limits

    @property
    def region_limit_names(self):
        """Names of all region limits."""
        return list(self._region_limits.keys())

    def _add_limit_to_fig(self, fig, plot_type="2d"):
        """Internal: Add limit lines to the figure."""
        for ll in self._limit_lines.values():
            props = ll.properties
            if plot_type == "2d":
                if props.orientation == "h" and props.y is not None:
                    # Add infinite horizontal line
                    fig.add_hline(
                        y=props.y,
                        line_color=props.color,
                        line_width=props.width,
                        line_dash=props.dash,
                        annotation_text=props.name if props.name else None,
                        annotation_position="top right" if props.name else None,
                    )
                elif props.orientation == "v" and props.x is not None:
                    # Add infinite vertical line
                    fig.add_vline(
                        x=props.x,
                        line_color=props.color,
                        line_width=props.width,
                        line_dash=props.dash,
                        annotation_text=props.name if props.name else None,
                        annotation_position="top right" if props.name else None,
                    )
            elif plot_type == "polar":
                # Add limit lines as Scatterpolar traces
                if props.orientation == "h" and props.y is not None:
                    # Constant radius (r)
                    theta = np.linspace(0, 360, 361)
                    r = np.full_like(theta, props.y)
                    fig.add_trace(
                        go.Scatterpolar(
                            r=r,
                            theta=theta,
                            mode="lines",
                            name=props.name or f"r={props.y}",
                            line=dict(color=props.color, width=props.width, dash=props.dash),
                            showlegend=True,
                        )
                    )
                elif props.orientation == "v" and props.x is not None:
                    # Constant angle (theta) - extend radius from 0 to maximum visible radius
                    # Get the maximum radius from existing traces or use a reasonable default
                    max_radius = 10  # Default fallback
                    try:
                        if hasattr(fig, "data") and fig.data:
                            for trace in fig.data:
                                if hasattr(trace, "r") and trace.r is not None:
                                    max_radius = max(max_radius, np.max(trace.r) * 1.2)
                    except:
                        pass

                    r = np.linspace(0, max_radius, 100)
                    theta = np.full_like(r, props.x)
                    fig.add_trace(
                        go.Scatterpolar(
                            r=r,
                            theta=theta,
                            mode="lines",
                            name=props.name or f"theta={props.x}",
                            line=dict(color=props.color, width=props.width, dash=props.dash),
                            showlegend=True,
                        )
                    )
            elif plot_type == "3d":
                # For 3D plots, create infinite planes and lines
                if props.orientation == "h" and props.y is not None:
                    # Horizontal plane at y = constant (infinite in x and z)
                    # Get the plot bounds to create a large enough plane
                    x_range = [-10, 10]  # Default range
                    z_range = [-10, 10]

                    # Try to get actual data bounds for better scaling
                    try:
                        if hasattr(fig, "data") and fig.data:
                            x_values = []
                            z_values = []
                            for trace in fig.data:
                                if hasattr(trace, "x") and trace.x is not None:
                                    x_values.extend(trace.x)
                                if hasattr(trace, "z") and trace.z is not None:
                                    z_values.extend(trace.z)

                            if x_values:
                                x_min, x_max = min(x_values), max(x_values)
                                x_range = [x_min - abs(x_max - x_min), x_max + abs(x_max - x_min)]
                            if z_values:
                                z_min, z_max = min(z_values), max(z_values)
                                z_range = [z_min - abs(z_max - z_min), z_max + abs(z_max - z_min)]
                    except:
                        pass

                    # Create a grid for the plane
                    x_plane = [x_range[0], x_range[1], x_range[1], x_range[0]]
                    y_plane = [props.y, props.y, props.y, props.y]
                    z_plane = [z_range[0], z_range[0], z_range[1], z_range[1]]

                    # Define triangular faces for the plane
                    i = [0, 0]  # vertex indices
                    j = [1, 2]
                    k = [2, 3]

                    fig.add_trace(
                        go.Mesh3d(
                            x=x_plane,
                            y=y_plane,
                            z=z_plane,
                            i=i,
                            j=j,
                            k=k,
                            color=props.color,
                            opacity=0.4,
                            name=props.name or f"Y={props.y}",
                            showlegend=True,
                            flatshading=True,
                            lighting=dict(ambient=0.9, diffuse=0.9, specular=0.1),
                            lightposition=dict(x=100, y=200, z=0),
                        )
                    )

                elif props.orientation == "v" and props.x is not None:
                    # Vertical plane at x = constant (infinite in y and z)
                    y_range = [-10, 10]
                    z_range = [-10, 10]

                    # Try to get actual data bounds
                    try:
                        if hasattr(fig, "data") and fig.data:
                            y_values = []
                            z_values = []
                            for trace in fig.data:
                                if hasattr(trace, "y") and trace.y is not None:
                                    y_values.extend(trace.y)
                                if hasattr(trace, "z") and trace.z is not None:
                                    z_values.extend(trace.z)

                            if y_values:
                                y_min, y_max = min(y_values), max(y_values)
                                y_range = [y_min - abs(y_max - y_min), y_max + abs(y_max - y_min)]
                            if z_values:
                                z_min, z_max = min(z_values), max(z_values)
                                z_range = [z_min - abs(z_max - z_min), z_max + abs(z_max - z_min)]
                    except:
                        pass

                    # Create a grid for the plane
                    x_plane = [props.x, props.x, props.x, props.x]
                    y_plane = [y_range[0], y_range[1], y_range[1], y_range[0]]
                    z_plane = [z_range[0], z_range[0], z_range[1], z_range[1]]

                    # Define triangular faces for the plane
                    i = [0, 0]
                    j = [1, 2]
                    k = [2, 3]

                    fig.add_trace(
                        go.Mesh3d(
                            x=x_plane,
                            y=y_plane,
                            z=z_plane,
                            i=i,
                            j=j,
                            k=k,
                            color=props.color,
                            opacity=0.4,
                            name=props.name or f"X={props.x}",
                            showlegend=True,
                            flatshading=True,
                            lighting=dict(ambient=0.9, diffuse=0.9, specular=0.1),
                            lightposition=dict(x=100, y=200, z=0),
                        )
                    )

                # Add support for Z-plane limits
                elif hasattr(props, "z") and props.z is not None:
                    # Horizontal plane at z = constant (infinite in x and y)
                    x_range = [-10, 10]
                    y_range = [-10, 10]

                    # Try to get actual data bounds
                    try:
                        if hasattr(fig, "data") and fig.data:
                            x_values = []
                            y_values = []
                            for trace in fig.data:
                                if hasattr(trace, "x") and trace.x is not None:
                                    x_values.extend(trace.x)
                                if hasattr(trace, "y") and trace.y is not None:
                                    y_values.extend(trace.y)

                            if x_values:
                                x_min, x_max = min(x_values), max(x_values)
                                x_range = [x_min - abs(x_max - x_min), x_max + abs(x_max - x_min)]
                            if y_values:
                                y_min, y_max = min(y_values), max(y_values)
                                y_range = [y_min - abs(y_max - y_min), y_max + abs(y_max - y_min)]
                    except:
                        pass

                    # Create a grid for the plane
                    x_plane = [x_range[0], x_range[1], x_range[1], x_range[0]]
                    y_plane = [y_range[0], y_range[0], y_range[1], y_range[1]]
                    z_plane = [props.z, props.z, props.z, props.z]

                    # Define triangular faces for the plane
                    i = [0, 0]
                    j = [1, 2]
                    k = [2, 3]

                    fig.add_trace(
                        go.Mesh3d(
                            x=x_plane,
                            y=y_plane,
                            z=z_plane,
                            i=i,
                            j=j,
                            k=k,
                            color=props.color,
                            opacity=0.4,
                            name=props.name or f"Z={props.z}",
                            showlegend=True,
                            flatshading=True,
                            lighting=dict(ambient=0.9, diffuse=0.9, specular=0.1),
                            lightposition=dict(x=100, y=200, z=0),
                        )
                    )
            elif plot_type == "contour":
                # For contour plots, we can overlay lines on the 2D contour
                if props.orientation == "h" and props.y is not None:
                    fig.add_hline(
                        y=props.y,
                        line_color=props.color,
                        line_width=props.width,
                        line_dash=props.dash,
                        annotation_text=props.name if props.name else None,
                    )
                elif props.orientation == "v" and props.x is not None:
                    fig.add_vline(
                        x=props.x,
                        line_color=props.color,
                        line_width=props.width,
                        line_dash=props.dash,
                        annotation_text=props.name if props.name else None,
                    )

    def _add_region_limits_to_fig(self, fig, plot_type="3d"):
        """Internal: Add region limits to the figure (3D only)."""
        if plot_type != "3d":
            return

        for rl in self._region_limits.values():
            props = rl.properties

            # Create 3D bounding box
            if all(
                v is not None for v in [props.x_min, props.x_max, props.y_min, props.y_max, props.z_min, props.z_max]
            ):
                # Define the 8 vertices of the box
                vertices = [
                    [props.x_min, props.y_min, props.z_min],  # 0
                    [props.x_max, props.y_min, props.z_min],  # 1
                    [props.x_max, props.y_max, props.z_min],  # 2
                    [props.x_min, props.y_max, props.z_min],  # 3
                    [props.x_min, props.y_min, props.z_max],  # 4
                    [props.x_max, props.y_min, props.z_max],  # 5
                    [props.x_max, props.y_max, props.z_max],  # 6
                    [props.x_min, props.y_max, props.z_max],  # 7
                ]

                # Define the 12 triangular faces (2 triangles per face, 6 faces)
                faces = [
                    # Bottom face (z_min)
                    [0, 1, 2],
                    [0, 2, 3],
                    # Top face (z_max)
                    [4, 6, 5],
                    [4, 7, 6],
                    # Front face (y_min)
                    [0, 4, 5],
                    [0, 5, 1],
                    # Back face (y_max)
                    [2, 6, 7],
                    [2, 7, 3],
                    # Left face (x_min)
                    [0, 3, 7],
                    [0, 7, 4],
                    # Right face (x_max)
                    [1, 5, 6],
                    [1, 6, 2],
                ]

                # Extract coordinates
                x_coords = [v[0] for v in vertices]
                y_coords = [v[1] for v in vertices]
                z_coords = [v[2] for v in vertices]

                # Create mesh
                fig.add_trace(
                    go.Mesh3d(
                        x=x_coords,
                        y=y_coords,
                        z=z_coords,
                        i=[f[0] for f in faces],
                        j=[f[1] for f in faces],
                        k=[f[2] for f in faces],
                        color=props.color,
                        opacity=props.opacity,
                        name=props.name or f"Region_{id(rl)}",
                        showlegend=True,
                        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.2),
                        lightposition=dict(x=100, y=200, z=0),
                    )
                )

                # Add edge lines if requested
                if props.show_edges:
                    edges = [
                        # Bottom face edges
                        ([props.x_min, props.x_max], [props.y_min, props.y_min], [props.z_min, props.z_min]),
                        ([props.x_max, props.x_max], [props.y_min, props.y_max], [props.z_min, props.z_min]),
                        ([props.x_max, props.x_min], [props.y_max, props.y_max], [props.z_min, props.z_min]),
                        ([props.x_min, props.x_min], [props.y_max, props.y_min], [props.z_min, props.z_min]),
                        # Top face edges
                        ([props.x_min, props.x_max], [props.y_min, props.y_min], [props.z_max, props.z_max]),
                        ([props.x_max, props.x_max], [props.y_min, props.y_max], [props.z_max, props.z_max]),
                        ([props.x_max, props.x_min], [props.y_max, props.y_max], [props.z_max, props.z_max]),
                        ([props.x_min, props.x_min], [props.y_max, props.y_min], [props.z_max, props.z_max]),
                        # Vertical edges
                        ([props.x_min, props.x_min], [props.y_min, props.y_min], [props.z_min, props.z_max]),
                        ([props.x_max, props.x_max], [props.y_min, props.y_min], [props.z_min, props.z_max]),
                        ([props.x_max, props.x_max], [props.y_max, props.y_max], [props.z_min, props.z_max]),
                        ([props.x_min, props.x_min], [props.y_max, props.y_max], [props.z_min, props.z_max]),
                    ]

                    for i, (x_edge, y_edge, z_edge) in enumerate(edges):
                        fig.add_trace(
                            go.Scatter3d(
                                x=x_edge,
                                y=y_edge,
                                z=z_edge,
                                mode="lines",
                                line=dict(color=props.edge_color, width=props.edge_width),
                                name=f"{props.name}_edge_{i}" if props.name else f"RegionEdge_{i}",
                                showlegend=False,
                                hoverinfo="skip",
                            )
                        )

    def _add_notes_to_fig(self, fig, plot_type="2d"):
        """Internal: Add notes/annotations to the figure."""
        if plot_type == "3d":
            # Notes are not supported in 3D plots
            if self._notes:
                raise ValueError("Notes are not supported in 3D plots. Use 2D or polar plots for annotations.")
            return

        for note in self._notes.values():
            props = note.properties

            # Create annotation dict for Plotly
            annotation = dict(
                text=props.text,
                x=props.position[0],
                y=props.position[1],
                xref="x",
                yref="y",
                showarrow=props.arrow_visible,
                font=dict(family=props.font_family, size=props.font_size, color=props.color),
            )

            # Add font style
            if props.bold and props.italic:
                annotation["font"]["family"] = f"{props.font_family}, bold, italic"
            elif props.bold:
                annotation["font"]["family"] = f"{props.font_family}, bold"
            elif props.italic:
                annotation["font"]["family"] = f"{props.font_family}, italic"

            # Add arrow properties if visible
            if props.arrow_visible:
                annotation.update(dict(arrowcolor=props.arrow_color, arrowwidth=props.arrow_width, arrowhead=2))

            # Add background/border styling if visible
            if props.background_visibility and props.background_color:
                annotation["bgcolor"] = props.background_color

            if props.border_visibility:
                annotation.update(dict(bordercolor=props.border_color, borderwidth=props.border_width))

            # Add annotation to figure
            fig.add_annotation(annotation)

    @pyaedt_function_handler()
    def _get_cartesian_data(self, trace):
        """Get cartesian data for a trace, converting from spherical if necessary."""
        if trace.cartesian_data is not None:
            return trace.cartesian_data
        elif trace.spherical_data is not None:
            # Convert spherical to cartesian temporarily for plotting
            trace.spherical2car()
            return trace.cartesian_data
        else:
            return None

    @pyaedt_function_handler()
    def plot_2d(self, traces=None, snapshot_path=None, show=True):
        """Create a 2D Plotly plot for the given traces."""
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return None

        self.fig = go.Figure()

        for trace in traces_to_plot:
            cartesian_data = self._get_cartesian_data(trace)
            if cartesian_data and len(cartesian_data) >= 2:
                x_data = cartesian_data[0]
                y_data = cartesian_data[1]

                # Handle enum values properly
                line_style = trace.line_style.value if isinstance(trace.line_style, LineStyle) else trace.line_style
                marker_symbol = (
                    trace.marker_symbol.value if isinstance(trace.marker_symbol, MarkerSymbol) else trace.marker_symbol
                )

                self.fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode="lines+markers" if trace.fill_symbol else "lines",
                        name=trace.name,
                        line=dict(color=trace.line_color, width=trace.line_width, dash=line_style),
                        marker=dict(symbol=marker_symbol, size=trace.marker_size, color=trace.marker_color)
                        if trace.fill_symbol
                        else None,
                    )
                )

        # Update layout
        self.fig.update_layout(
            title=self.title,
            xaxis=dict(
                title=traces_to_plot[0].x_label if traces_to_plot else "",
                type=self.x_scale.value,
                showgrid=self.grid_enable_major_x,
                gridcolor=self.grid_color,
            ),
            yaxis=dict(
                title=traces_to_plot[0].y_label if traces_to_plot else "",
                type=self.y_scale.value,
                showgrid=self.grid_enable_major_y,
                gridcolor=self.grid_color,
            ),
            showlegend=self.show_legend,
            plot_bgcolor=self.plot_color,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1],
        )
        self._add_limit_to_fig(self.fig, plot_type="2d")
        self._add_notes_to_fig(self.fig, plot_type="2d")

        if snapshot_path:
            self.fig.write_image(snapshot_path)

        if show:
            self._show_plot(self.fig)

        return self.fig

    @pyaedt_function_handler()
    def plot_polar(self, traces=None, snapshot_path=None, show=True):
        """Create a polar Plotly plot for the given traces."""
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return None

        self.fig = go.Figure()

        for trace in traces_to_plot:
            cartesian_data = self._get_cartesian_data(trace)
            if cartesian_data and len(cartesian_data) >= 2:
                theta = cartesian_data[0]  # Assuming theta in degrees
                r = cartesian_data[1]

                # Handle enum values properly
                line_style = trace.line_style.value if isinstance(trace.line_style, LineStyle) else trace.line_style
                marker_symbol = (
                    trace.marker_symbol.value if isinstance(trace.marker_symbol, MarkerSymbol) else trace.marker_symbol
                )

                self.fig.add_trace(
                    go.Scatterpolar(
                        r=r,
                        theta=theta,
                        mode="lines+markers" if trace.fill_symbol else "lines",
                        name=trace.name,
                        line=dict(color=trace.line_color, width=trace.line_width, dash=line_style),
                        marker=dict(symbol=marker_symbol, size=trace.marker_size, color=trace.marker_color)
                        if trace.fill_symbol
                        else None,
                    )
                )

        # Update layout for polar plot
        self.fig.update_layout(
            title=self.title,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    title=traces_to_plot[0].y_label if traces_to_plot else "",
                    showgrid=self.grid_enable_major_y,
                    gridcolor=self.grid_color,
                ),
                angularaxis=dict(direction="counterclockwise", period=360),
            ),
            showlegend=self.show_legend,
            plot_bgcolor=self.plot_color,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1],
        )
        self._add_limit_to_fig(self.fig, plot_type="polar")
        self._add_notes_to_fig(self.fig, plot_type="polar")

        if snapshot_path:
            self.fig.write_image(snapshot_path)

        if show:
            self._show_plot(self.fig)

        return self.fig

    @pyaedt_function_handler()
    def plot_3d(self, traces=None, snapshot_path=None, show=True):
        """Create a 3D Plotly plot for the given traces."""
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return None

        self.fig = go.Figure()

        for trace_obj in traces_to_plot:
            cartesian_data = self._get_cartesian_data(trace_obj)
            if not cartesian_data or len(cartesian_data) < 3:
                continue

            x_data = cartesian_data[0]
            y_data = cartesian_data[1]
            z_data = cartesian_data[2]

            marker_symbol = (
                trace_obj.marker_symbol.value
                if isinstance(trace_obj.marker_symbol, MarkerSymbol)
                else trace_obj.marker_symbol
            )

            self.fig.add_trace(
                go.Scatter3d(
                    x=x_data,
                    y=y_data,
                    z=z_data,
                    mode="lines+markers" if trace_obj.fill_symbol else "lines",
                    name=trace_obj.name,
                    line=dict(color=trace_obj.line_color, width=trace_obj.line_width),
                    marker=dict(symbol=marker_symbol, size=trace_obj.marker_size, color=trace_obj.marker_color)
                    if trace_obj.fill_symbol
                    else None,
                )
            )

        # Use labels from the first valid trace
        first_valid = next((t for t in traces_to_plot if t.cartesian_data and len(t.cartesian_data) >= 3), None)

        self.fig.update_layout(
            title=self.title,
            scene=dict(
                xaxis_title=first_valid.x_label if first_valid else "",
                yaxis_title=first_valid.y_label if first_valid else "",
                zaxis_title=first_valid.z_label if first_valid else "",
                bgcolor=self.plot_color,
            ),
            showlegend=self.show_legend,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1],
        )
        self._add_limit_to_fig(self.fig, plot_type="3d")
        self._add_region_limits_to_fig(self.fig, plot_type="3d")
        self._add_notes_to_fig(self.fig, plot_type="3d")

        if snapshot_path:
            self.fig.write_image(snapshot_path)

        if show:
            self._show_plot(self.fig)

        return self.fig

    @pyaedt_function_handler()
    def plot_contour(self, trace=0, levels=10, snapshot_path=None, show=True):
        """Create a contour Plotly plot for the given trace."""
        traces_to_plot = self._retrieve_traces(trace)
        if not traces_to_plot:
            return None

        trace_obj = traces_to_plot[0]

        cartesian_data = self._get_cartesian_data(trace_obj)
        if not cartesian_data or len(cartesian_data) < 3:
            return None

        x_data = cartesian_data[0]
        y_data = cartesian_data[1]
        z_data = cartesian_data[2]

        self.fig = go.Figure()

        self.fig.add_trace(
            go.Contour(x=x_data, y=y_data, z=z_data, name=trace_obj.name, ncontours=levels, colorscale="Viridis")
        )

        # Update layout
        self.fig.update_layout(
            title=self.title,
            xaxis_title=trace_obj.x_label,
            yaxis_title=trace_obj.y_label,
            showlegend=self.show_legend,
            plot_bgcolor=self.plot_color,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1],
        )
        self._add_limit_to_fig(self.fig, plot_type="contour")
        self._add_notes_to_fig(self.fig, plot_type="contour")

        if snapshot_path:
            self.fig.write_image(snapshot_path)

        if show:
            self._show_plot(self.fig)

        return self.fig

    @pyaedt_function_handler()
    def _show_plot(self, fig):
        """Display the plot in a notebook or browser."""
        if is_notebook():
            fig.show()
        else:
            from http.server import HTTPServer
            from http.server import SimpleHTTPRequestHandler
            import socket
            import threading
            import time
            import webbrowser

            # Generate HTML content in memory
            html_content = pyo.plot(fig, output_type="div", include_plotlyjs=True)

            # Create a simple HTTP server to serve the content
            class PlotlyHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/" or self.path == "/plot.html":
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(html_content.encode("utf-8"))
                    else:
                        self.send_error(404)

            # Start server on available port
            sock = socket.socket()
            sock.bind(("", 0))
            port = sock.getsockname()[1]
            sock.close()

            server = HTTPServer(("localhost", port), PlotlyHandler)

            # Start server in background thread
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            # Open browser
            webbrowser.open(f"http://localhost:{port}/plot.html")

            # Keep server running for a reasonable time then shut down
            def shutdown_server():
                time.sleep(30)  # Keep server alive for 30 seconds
                server.shutdown()

            shutdown_thread = threading.Thread(target=shutdown_server)
            shutdown_thread.daemon = True
            shutdown_thread.start()
