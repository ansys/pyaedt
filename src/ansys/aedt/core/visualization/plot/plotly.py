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
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
import warnings

import numpy as np

from ansys.aedt.core.generic.general_methods import (
    pyaedt_function_handler,
)
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
            self._cartesian_data.append(
                np.zeros(len(self._cartesian_data[-1]))
            )

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


def is_notebook():
    """Return True if running in a Jupyter notebook."""
    try:
        shell = get_ipython().__class__.__name__
        return shell in ["ZMQInteractiveShell"]
    except NameError:
        return False


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
        plot_color: str = "white"
    ):
        """Initialize the PlotlyPlotter."""
        self._traces: Dict[str, PlotlyTrace] = {}
        self._limit_lines: Dict[str, Any] = {}
        self._notes: List[str] = []
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
        fill_symbol: bool = False
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
                fill_symbol=fill_symbol
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
                fill_symbol=properties.get("fill_symbol", fill_symbol)
            )
        else:
            raise TypeError(
                f"Properties must be TraceProperties, dict, or None. "
                f"Got {type(properties)}"
            )

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
    def plot_2d(self, traces=None, snapshot_path=None, show=True):
        """Create a 2D Plotly plot for the given traces."""
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return None

        self.fig = go.Figure()

        for trace in traces_to_plot:
            if trace.cartesian_data and len(trace.cartesian_data) >= 2:
                x_data = trace.cartesian_data[0]
                y_data = trace.cartesian_data[1]

                # Handle enum values properly
                line_style = (
                    trace.line_style.value
                    if isinstance(trace.line_style, LineStyle)
                    else trace.line_style
                )
                marker_symbol = (
                    trace.marker_symbol.value
                    if isinstance(trace.marker_symbol, MarkerSymbol)
                    else trace.marker_symbol
                )

                self.fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers' if trace.fill_symbol else 'lines',
                    name=trace.name,
                    line=dict(
                        color=trace.line_color,
                        width=trace.line_width,
                        dash=line_style
                    ),
                    marker=dict(
                        symbol=marker_symbol,
                        size=trace.marker_size,
                        color=trace.marker_color
                    ) if trace.fill_symbol else None
                ))

        # Update layout
        self.fig.update_layout(
            title=self.title,
            xaxis=dict(
                title=traces_to_plot[0].x_label if traces_to_plot else "",
                type=self.x_scale.value,
                showgrid=self.grid_enable_major_x,
                gridcolor=self.grid_color
            ),
            yaxis=dict(
                title=traces_to_plot[0].y_label if traces_to_plot else "",
                type=self.y_scale.value,
                showgrid=self.grid_enable_major_y,
                gridcolor=self.grid_color
            ),
            showlegend=self.show_legend,
            plot_bgcolor=self.plot_color,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1]
        )

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
            if trace.cartesian_data and len(trace.cartesian_data) >= 2:
                theta = trace.cartesian_data[0]  # Assuming theta in degrees
                r = trace.cartesian_data[1]

                # Handle enum values properly
                line_style = (
                    trace.line_style.value
                    if isinstance(trace.line_style, LineStyle)
                    else trace.line_style
                )
                marker_symbol = (
                    trace.marker_symbol.value
                    if isinstance(trace.marker_symbol, MarkerSymbol)
                    else trace.marker_symbol
                )

                self.fig.add_trace(go.Scatterpolar(
                    r=r,
                    theta=theta,
                    mode='lines+markers' if trace.fill_symbol else 'lines',
                    name=trace.name,
                    line=dict(
                        color=trace.line_color,
                        width=trace.line_width,
                        dash=line_style
                    ),
                    marker=dict(
                        symbol=marker_symbol,
                        size=trace.marker_size,
                        color=trace.marker_color
                    ) if trace.fill_symbol else None
                ))

        # Update layout for polar plot
        self.fig.update_layout(
            title=self.title,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    title=traces_to_plot[0].y_label if traces_to_plot else "",
                    showgrid=self.grid_enable_major_y,
                    gridcolor=self.grid_color
                ),
                angularaxis=dict(
                    direction="counterclockwise",
                    period=360
                )
            ),
            showlegend=self.show_legend,
            plot_bgcolor=self.plot_color,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1]
        )

        if snapshot_path:
            self.fig.write_image(snapshot_path)

        if show:
            self._show_plot(self.fig)

        return self.fig

    @pyaedt_function_handler()
    def plot_3d(self, trace=0, snapshot_path=None, show=True):
        """Create a 3D Plotly plot for the given trace."""
        traces_to_plot = self._retrieve_traces(trace)
        if not traces_to_plot:
            return None

        trace_obj = traces_to_plot[0]

        if not trace_obj.cartesian_data or len(trace_obj.cartesian_data) < 3:
            return None

        x_data = trace_obj.cartesian_data[0]
        y_data = trace_obj.cartesian_data[1]
        z_data = trace_obj.cartesian_data[2]

        self.fig = go.Figure()

        # Handle enum values properly
        marker_symbol = (
            trace_obj.marker_symbol.value
            if isinstance(trace_obj.marker_symbol, MarkerSymbol)
            else trace_obj.marker_symbol
        )

        self.fig.add_trace(go.Scatter3d(
            x=x_data,
            y=y_data,
            z=z_data,
            mode='lines+markers' if trace_obj.fill_symbol else 'lines',
            name=trace_obj.name,
            line=dict(
                color=trace_obj.line_color,
                width=trace_obj.line_width
            ),
            marker=dict(
                symbol=marker_symbol,
                size=trace_obj.marker_size,
                color=trace_obj.marker_color
            ) if trace_obj.fill_symbol else None
        ))

        # Update layout for 3D plot
        self.fig.update_layout(
            title=self.title,
            scene=dict(
                xaxis_title=trace_obj.x_label,
                yaxis_title=trace_obj.y_label,
                zaxis_title=trace_obj.z_label,
                bgcolor=self.plot_color
            ),
            showlegend=self.show_legend,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1]
        )

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

        if not trace_obj.cartesian_data or len(trace_obj.cartesian_data) < 3:
            return None

        x_data = trace_obj.cartesian_data[0]
        y_data = trace_obj.cartesian_data[1]
        z_data = trace_obj.cartesian_data[2]

        self.fig = go.Figure()

        self.fig.add_trace(go.Contour(
            x=x_data,
            y=y_data,
            z=z_data,
            name=trace_obj.name,
            ncontours=levels,
            colorscale='Viridis'
        ))

        # Update layout
        self.fig.update_layout(
            title=self.title,
            xaxis_title=trace_obj.x_label,
            yaxis_title=trace_obj.y_label,
            showlegend=self.show_legend,
            plot_bgcolor=self.plot_color,
            paper_bgcolor=self.background_color,
            width=self.size[0],
            height=self.size[1]
        )

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
            from http.server import HTTPServer, SimpleHTTPRequestHandler
            import socket, threading, time, webbrowser

            # Generate HTML content in memory
            html_content = pyo.plot(
                fig, output_type='div', include_plotlyjs=True
            )

            # Create a simple HTTP server to serve the content
            class PlotlyHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/' or self.path == '/plot.html':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(html_content.encode('utf-8'))
                    else:
                        self.send_error(404)

            # Start server on available port
            sock = socket.socket()
            sock.bind(('', 0))
            port = sock.getsockname()[1]
            sock.close()

            server = HTTPServer(('localhost', port), PlotlyHandler)

            # Start server in background thread
            server_thread = threading.Thread(
                target=server.serve_forever
            )
            server_thread.daemon = True
            server_thread.start()

            # Open browser
            webbrowser.open(f'http://localhost:{port}/plot.html')

            # Keep server running for a reasonable time then shut down
            def shutdown_server():
                time.sleep(30)  # Keep server alive for 30 seconds
                server.shutdown()

            shutdown_thread = threading.Thread(target=shutdown_server)
            shutdown_thread.daemon = True
            shutdown_thread.start()
