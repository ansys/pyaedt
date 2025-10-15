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

import ast
import math
import os
import warnings

import numpy as np

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available

# Check that graphics are available
try:
    check_graphics_available()

    from matplotlib.animation import FuncAnimation
    from matplotlib.colors import Normalize
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


def is_notebook():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell in ["ZMQInteractiveShell"]:  # pragma: no cover
            return True  # Jupyter notebook or qtconsole
        else:
            return False
    except NameError:
        return False  # Probably standard Python interpreter


def is_ipython():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell in ["TerminalInteractiveShell", "SpyderShell"]:
            return True  # Jupyter notebook or qtconsole
        else:  # pragma: no cover
            return False
    except NameError:
        return False  # Probably standard Python interpreter


class Note(PyAedtBase):
    def __init__(self):
        self._position = (0, 0)
        self._text = ""
        self._back_color = None
        self._background_visibility = None
        self._border_visibility = None
        self._border_width = None
        self._font = "Arial"
        self._font_size = 12
        self._italic = False
        self._bold = False
        self._color = (0, 0, 0)

    @property
    def text(self):
        """Note text.

        Returns
        -------
        str
        """
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def background_color(self):
        """Note color.

        Returns
        -------
        tuple or list
        """
        return self._back_color

    @background_color.setter
    def background_color(self, value):
        self._back_color = value

    @property
    def background_visibility(self):
        """Note background visibility.

        Returns
        -------
        bool
        """
        return self._background_visibility

    @background_visibility.setter
    def background_visibility(self, value):
        self._background_visibility = value

    @property
    def border_visibility(self):
        """Note border visibility.

        Returns
        -------
        bool
        """
        return self._border_visibility

    @border_visibility.setter
    def border_visibility(self, value):
        self._border_visibility = value

    @property
    def border_width(self):
        """Note border width.

        Returns
        -------
        float
        """
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        self._border_width = value

    @property
    def font(self):
        """Note font.

        Returns
        -------
        str
        """
        return self._font

    @font.setter
    def font(self, value):
        self._font = value

    @property
    def font_size(self):
        """Note font size.

        Returns
        -------
        bool
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value

    @property
    def color(self):
        """Note font color.

        Returns
        -------
        list
        """
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def bold(self):
        """Note font bold.

        Returns
        -------
        bool
        """
        return self._bold

    @bold.setter
    def bold(self, value):
        self._bold = value

    @property
    def italic(self):
        """Note font italic.

        Returns
        -------
        bool
        """
        return self._italic

    @italic.setter
    def italic(self, value):
        self._italic = value


class Trace(PyAedtBase):
    """Trace class."""

    def __init__(self):
        self.name = ""
        self._cartesian_data = None
        self._spherical_data = None
        self.x_label = ""
        self.y_label = ""
        self.z_label = ""
        self.__trace_style = "-"
        self.__trace_width = 1.5
        self.__trace_color = None
        self.__symbol_style = ""
        self.__fill_symbol = False
        self.__symbol_color = None

    @property
    def trace_style(self):
        """Matplotlib trace style.

        Returns
        -------
        str
        """
        return self.__trace_style

    @property
    def trace_width(self):
        """Trace width.

        Returns
        -------
        float
        """
        return self.__trace_width

    @property
    def trace_color(self):
        """Matplotlib trace color. It can be a tuple or a string of allowed colors.

        Returns
        -------
        str, list
        """
        return self.__trace_color

    @property
    def symbol_style(self):
        """Matplotlib symbol style.

        Returns
        -------
        str
        """
        return self.__symbol_style

    @property
    def fill_symbol(self):
        """Fill symbol.

        Returns
        -------
        bool
        """
        return self.__fill_symbol

    @trace_style.setter
    def trace_style(self, val):
        self.__trace_style = val

    @trace_width.setter
    def trace_width(self, val):
        self.__trace_width = val

    @trace_color.setter
    def trace_color(self, val):
        self.__trace_color = val

    @symbol_style.setter
    def symbol_style(self, val):
        self.__symbol_style = val

    @fill_symbol.setter
    def fill_symbol(self, val):
        self.__fill_symbol = val

    @property
    def cartesian_data(self):
        """Cartesian data [x,y,z].

        Returns
        -------
        list[:class:`numpy.array`]
            List of data.
        """
        return self._cartesian_data

    @cartesian_data.setter
    def cartesian_data(self, val):
        self._cartesian_data = []
        for el in val:
            if not isinstance(el, (float, int, str)):
                self._cartesian_data.append(np.array(el, dtype=float))
            else:
                self._cartesian_data.append(el)
        if len(self._cartesian_data) == 2:
            self._cartesian_data.append(np.zeros(len(val[-1])))
        self.car2spherical()

    @property
    def spherical_data(self):
        """Spherical data [r, theta, phi]. Angles are in degrees.

        Returns
        -------
        list[:class:`numpy.array`]
            List of data.
        """
        return self._spherical_data

    @spherical_data.setter
    def spherical_data(self, rthetaphi):
        self._spherical_data = []
        for el in rthetaphi:
            if not isinstance(el, (float, int, str)):
                self._spherical_data.append(np.array(el, dtype=float))
            else:
                self._spherical_data.append(el)
        self.spherical2car()

    @pyaedt_function_handler()
    def car2polar(self, x, y, is_degree=False):
        """Convert cartesian data to polar.

        Parameters
        ----------
        x : list
            X data.
        y : list
            Y data.
        is_degree : bool, optional
            Whether to return data in degree or radians.

        Returns
        -------
        list, list
            R and theta.
        """
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
        rate = 1
        if not is_degree:
            rate = np.pi / 180
        rho = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x) * rate
        return [rho, phi]

    @pyaedt_function_handler()
    def car2spherical(self):
        """Convert cartesian data to spherical and assigns to property spherical data."""
        x = np.array(self.cartesian_data[0], dtype=float)
        y = np.array(self.cartesian_data[1], dtype=float)
        z = np.array(self.cartesian_data[2], dtype=float)
        r = np.sqrt(x * x + y * y + z * z)
        with np.errstate(invalid="ignore", divide="ignore"):
            ratio = np.where(r != 0, z / r, 0)  # or np.nan if you prefer
            ratio = np.clip(ratio, -1.0, 1.0)  # ensure valid domain for arccos
            theta = np.arccos(ratio) * 180 / math.pi
        phi = np.arctan2(y, x) * 180 / math.pi
        self._spherical_data = [r, theta, phi]

    @pyaedt_function_handler()
    def spherical2car(self):
        """Convert spherical data to cartesian data and assign to cartesian data property."""
        r = np.array(self._spherical_data[0], dtype=float)
        theta = np.array(self._spherical_data[1] * math.pi / 180, dtype=float)  # to radian
        phi = np.array(self._spherical_data[2] * math.pi / 180, dtype=float)
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        self._cartesian_data = [x, y, z]

    @pyaedt_function_handler()
    def polar2car(self, r, theta):
        """Convert polar data to cartesian data.

        Parameters
        ----------
        r : list
        theta : list

        Returns
        -------
        list
            List of [x,y].
        """
        r = np.array(r, dtype=float)
        theta = np.array(theta, dtype=float)
        x = r * np.cos(np.radians(theta))
        y = r * np.sin(np.radians(theta))
        return [x, y]


class LimitLine(Trace):
    """Limit Line class."""

    def __init__(self):
        Trace.__init__(self)
        self.hatch_above = True


class ReportPlotter(PyAedtBase):
    """Matplotlib Report manager."""

    def __init__(self):
        rc_params = {
            "axes.titlesize": 26,  # Use these default settings for Matplotlb axes.
            "axes.labelsize": 20,  # Apply the settings only in this module.
            "xtick.labelsize": 18,
            "ytick.labelsize": 18,
        }
        self.block = settings.block_figure_plot
        self._traces = {}
        self._limit_lines = {}
        self._notes = []
        self.plt_params = plt.rcParams
        self.plt_params.update(rc_params)
        self.show_legend = True
        self.title = ""
        self.fig = None
        self.ax = None
        self.__x_scale = "linear"
        self.__y_scale = "linear"
        self.__grid_color = (0.8, 0.8, 0.8)
        self.__grid_enable_major_x = True
        self.__grid_enable_major_y = True
        self.__grid_enable_minor_x = False
        self.__grid_enable_minor_y = True
        self.__grid_style = "-"
        self.__general_back_color = (1, 1, 1)
        self.__general_plot_color = (1, 1, 1)
        self._style = None
        self.logo = None
        self.show_logo = True
        self.animation = None
        self.y_margin_factor = 0.2
        self.x_margin_factor = 0.2

    @property
    def traces(self):
        """Traces.

        Returns
        -------
         dict[str, :class:`ansys.aedt.core.visualization.plot.matplotlib.Trace`]
        """
        return self._traces

    @property
    def traces_by_index(self):
        """Traces.

        Returns
        -------
         list[:class:`ansys.aedt.core.visualization.plot.matplotlib.Trace`]
        """
        return list(self._traces.values())

    @property
    def trace_names(self):
        """Trace names.

        Returns
        -------
        list
        """
        return list(self._traces.keys())

    @property
    def limit_lines(self):
        """Limit Lines.

        Returns
        -------
         dict[str, :class:`ansys.aedt.core.visualization.plot.matplotlib.LimitLine`]
        """
        return self._limit_lines

    @pyaedt_function_handler()
    def apply_style(self, style_name):
        """Apply a custom matplotlib style (eg. background_dark).

        Parameters
        ----------
        style_name : str
            Matplotlib style name.

        Returns
        -------
        bool
        """
        if style_name in plt.style.available:
            plt.style.use(style_name)
            self._style = style_name
        return True

    @property
    def grid_style(self):
        """Grid style.

        Returns
        -------
        str
        """
        return self.__grid_style

    @grid_style.setter
    def grid_style(self, val):
        self.__grid_style = val

    @property
    def grid_enable_major_x(self):
        """Enable the major grid on x axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_major_x

    @grid_enable_major_x.setter
    def grid_enable_major_x(self, val):
        self.__grid_enable_major_x = val

    @property
    def grid_enable_major_y(self):
        """Enable the major grid on y axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_major_y

    @grid_enable_major_y.setter
    def grid_enable_major_y(self, val):
        self.__grid_enable_major_y = val

    @property
    def grid_enable_minor_x(self):
        """Enable the minor grid on x axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_minor_x

    @grid_enable_minor_x.setter
    def grid_enable_minor_x(self, val):
        self.__grid_enable_minor_x = val

    @property
    def grid_enable_minor_y(self):
        """Enable the minor grid on y axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_minor_y

    @grid_enable_minor_y.setter
    def grid_enable_minor_y(self, val):
        self.__grid_enable_minor_y = val

    @property
    def grid_color(self):
        """Grid color.

        Returns
        -------
        str, list
            Grid color tuple.
        """
        return self.__grid_color

    @grid_color.setter
    def grid_color(self, val):
        if isinstance(val, (list, tuple)):
            if any([i for i in val if i > 1]):
                val = [i / 255 for i in val]
        self.__grid_color = val

    @property
    def general_back_color(self):
        """General background color.

        Returns
        -------
        str, list
        """
        return self.__general_back_color

    @general_back_color.setter
    def general_back_color(self, val):
        if isinstance(val, (list, tuple)):
            if any([i for i in val if i > 1]):
                val = [i / 255 for i in val]
        self.__general_back_color = val

    @property
    def general_plot_color(self):
        """General plot color.

        Returns
        -------
        str, list
        """
        return self.__general_plot_color

    @general_plot_color.setter
    def general_plot_color(self, val):
        if isinstance(val, (list, tuple)):
            if any([i for i in val if i > 1]):
                val = [i / 255 for i in val]
        self.__general_plot_color = val

    @property
    def _has_grid(self):
        return True if self._has_x_axis or self._has_y_axis else False

    @property
    def _has_x_axis(self):
        return True if self.__grid_enable_major_x or self.__grid_enable_minor_x else False

    @property
    def _has_y_axis(self):
        return True if self.__grid_enable_major_y or self.__grid_enable_minor_y else False

    @property
    def _has_major_axis(self):
        return True if self.__grid_enable_major_x or self.__grid_enable_major_y else False

    @property
    def _has_minor_axis(self):
        return True if self.__grid_enable_minor_x or self.__grid_enable_minor_y else False

    # Open an image from a computer
    @pyaedt_function_handler()
    def _open_image_local(self):
        from PIL import Image

        if not self.logo:
            self.logo = os.path.join(os.path.dirname(__file__), "../../misc/Ansys.png")
        image = Image.open(self.logo)  # Open the image
        image_array = np.array(image)  # Convert to a numpy array
        return image_array  # Output

    @pyaedt_function_handler()
    def _update_grid(self):
        if self._has_x_axis and self._has_y_axis:
            axis = "both"
        elif self._has_y_axis:
            axis = "y"
        elif self._has_x_axis:
            axis = "x"
        else:
            axis = "both"
        if self._has_minor_axis and self._has_major_axis:
            which = "both"
        elif self._has_minor_axis:
            which = "minor"
        elif self._has_major_axis:
            which = "major"
        else:
            which = None
        props = {
            "axes.grid": True if self._has_grid else False,
            "axes.grid.axis": axis,
            "axes.grid.which": which,
            "grid.linestyle": self.__grid_style,
        }
        if not self._style:
            props["figure.facecolor"] = self.__general_back_color
            props["axes.facecolor"] = self.__general_plot_color
            props["grid.color"] = self.__grid_color

        self.plt_params.update(props)
        if self.ax:
            self.ax.grid(which=which)
            if self._has_major_axis:
                self.ax.grid(which="major", color=self.__grid_color)
            if self._has_major_axis:
                self.ax.grid(which="minor", color=self.__grid_color)
            if self._has_minor_axis:
                if self.__grid_enable_minor_x:
                    self.ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
                if self.__grid_enable_minor_y:
                    self.ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
            self.ax.tick_params(which="minor", grid_linestyle="--")

    @property
    def y_scale(self):
        """Y axis scale. It can be linear or log.

        Returns
        -------
        str
        """
        return self.__y_scale

    @y_scale.setter
    def y_scale(self, val):
        self.__y_scale = val

    @property
    def x_scale(self):
        """X axis scale. It can be linear or log.

        Returns
        -------
        str
        """
        return self.__x_scale

    @x_scale.setter
    def x_scale(self, val):
        self.__x_scale = val

    @property
    def interactive(self):
        """Enable interactive mode.

        Returns
        -------
        bool
        """
        return plt.isinteractive()

    @interactive.setter
    def interactive(self, val):
        if val:
            plt.ion()
        else:
            plt.ioff()

    def add_note(
        self,
        text,
        position=(0, 1),
        back_color=None,
        background_visibility=None,
        border_width=None,
        font="Arial",
        font_size=12,
        italic=False,
        bold=False,
        color=(0.2, 0.2, 0.2),
    ):
        """Add a note to the report.

        Parameters
        ----------
        text : str
        position : list, optional
        back_color : list, optional
        background_visibility : bool, optional
        border_width : float, optional
        font : str, optional
        font_size : float, optional
        italic : bool, optional
        bold : bool, optional
        color : list, optional

        Returns
        -------
        bool
        """
        note = Note()
        note.text = text
        note.position = position
        note.background_color = back_color
        note.background_visibility = background_visibility
        note.border_width = border_width
        note.font = font
        note.font_size = font_size
        note.italic = italic
        note.bold = bold
        note.color = color
        self._notes.append(note)

    @pyaedt_function_handler()
    def add_limit_line(self, plot_data, hatch_above=True, properties=None, name=""):
        """Add a new limit_line to the chart.

        Parameters
        ----------
        plot_data : list
            Data to be inserted. Data has to be cartesian with x and y.
        properties : dict, optional
            Properties of the trace.
            {x_label:prop,
            y_label:prop,
            trace_style : "-",
            trace_width : 1.5,
            trace_color : None,
            symbol_style : 'v',
            fill_symbol : None,
            symbol_color : "C0"
            }
        name : str
            Line name.

        Returns
        -------
        bool
        """
        nt = LimitLine()
        nt.hatch_above = hatch_above
        nt.name = name if name else f"Trace_{len(self.traces)}"
        nt.x_label = properties.get("x_label", "")
        nt.y_label = properties.get("y_label", "")
        nt.trace_color = properties.get("trace_color", None)
        nt.trace_style = properties.get("trace_style", "-")
        nt.trace_width = properties.get("trace_width", 1.5)
        nt.symbol_style = properties.get("symbol_style", "")
        nt.fill_symbol = properties.get("fill_symbol", False)
        nt.symbol_color = properties.get("symbol_color", None)
        nt.cartesian_data = plot_data
        self._limit_lines[nt.name] = nt
        return True

    @pyaedt_function_handler()
    def add_trace(self, plot_data, data_type=0, properties=None, name=""):
        """Add a new trace to the chart.

        Parameters
        ----------
        plot_data : list
            Data to be inserted.
        data_type : int, optional
            Data format. ``0`` for cartesian, ``1`` for spherical data.
        properties : dict, optional
            Properties of the trace.
            {x_label:prop,
            y_label:prop,
            z_label:prop,
            trace_style : "-",
            trace_width : 1.5,
            trace_color : None,
            symbol_style : 'v',
            fill_symbol : None,
            symbol_color : "C0"
            }
        name : str
            Trace name.

        Returns
        -------
        bool
        """
        nt = Trace()
        nt.name = name if name else f"Trace_{len(self.traces)}"
        nt.x_label = properties.get("x_label", "")
        nt.y_label = properties.get("y_label", "")
        nt.z_label = properties.get("z_label", "")
        nt.trace_color = properties.get("trace_color", None)
        nt.trace_style = properties.get("trace_style", "-")
        nt.trace_width = properties.get("trace_width", 1.5)
        nt.symbol_style = properties.get("symbol_style", "")
        nt.fill_symbol = properties.get("fill_symbol", False)
        nt.symbol_color = properties.get("symbol_color", None)
        if data_type == 0:
            nt.cartesian_data = plot_data
        else:
            nt.spherical_data = plot_data
        self._traces[nt.name] = nt
        return True

    @property
    def size(self):
        """Figure size.

        Returns
        -------
        list
        """
        px = self.plt_params["figure.dpi"]  # pixel in inches
        return [i * px for i in self.plt_params["figure.figsize"]]

    @size.setter
    def size(self, val, is_pixel=True):
        if is_pixel:
            px = 1 / self.plt_params["figure.dpi"]  # pixel in inches
            self.plt_params["figure.figsize"] = [i * px for i in val]
        else:
            self.plt_params["figure.figsize"] = val

    @pyaedt_function_handler()
    def _plot(self, snapshot_path, show):
        self.fig.set_size_inches(
            self.size[0] / self.plt_params["figure.dpi"], self.size[1] / self.plt_params["figure.dpi"]
        )

        self._update_grid()
        if self.show_logo:
            image_xaxis = 0.9
            image_yaxis = 0.95
            image_width = 0.1
            image_height = 0.05
            ax_image = self.fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])
            # Display the image
            ax_image.imshow(self._open_image_local())
            ax_image.axis("off")  # Remove axis of the image

        if snapshot_path:
            if hasattr(self, "animation") and snapshot_path.endswith(".gif"):
                self.animation.save(snapshot_path, writer="pillow", fps=2)
            else:
                self.fig.savefig(snapshot_path)
        if show:  # pragma: no cover
            if is_notebook():
                pass
            elif is_ipython() or "PYTEST_CURRENT_TEST" in os.environ:
                self.fig.show()
            else:
                plt.show(block=self.block)
        return self.fig

    def _set_scale(self, x, y):
        min_y = np.amin(y)
        max_y = np.amax(y)
        min_x = np.amin(x)
        max_x = np.amax(x)
        if self.y_scale:
            if not (self.y_scale == "log" and min_y < 0 or max_y < 0):
                self.ax.set_yscale(self.y_scale)
        if self.x_scale:
            if not (self.x_scale == "log" and min_x < 0 or max_x < 0):
                self.ax.set_xscale(self.x_scale)
        y_range = max_y - min_y
        x_range = max_x - min_x
        if self.y_scale == "log":
            y_range = -1e-12
        if self.x_scale == "log":
            x_range = -1e-12

        y_min = min_y - y_range * self.y_margin_factor
        y_max = max_y + y_range * self.y_margin_factor
        x_min = min_x - x_range * self.x_margin_factor
        x_max = max_x + x_range * self.x_margin_factor
        return y_min, y_max, x_min, x_max

    @pyaedt_function_handler()
    def _retrieve_traces(self, traces):
        if traces is None:
            return self.traces_by_index
        traces_to_plot = []
        if isinstance(traces, (int, str)):
            traces = [traces]
        try:
            for tr in traces:
                if isinstance(tr, int):
                    traces_to_plot.append(list(self.traces.values())[tr])
                elif isinstance(tr, str):
                    traces_to_plot.append(self.traces[tr])
        except (KeyError, IndexError):
            settings.logger.error("Failed to retrieve traces")
            return False
        return traces_to_plot

    @pyaedt_function_handler()
    def plot_polar(self, traces=None, to_polar=False, snapshot_path=None, show=True, is_degree=True, figure=None):
        """Create a Matplotlib polar plot based on a list of data.

        Parameters
        ----------
        traces : int, str, list, optional
            Trace or traces to be plotted. It can be the trace name, the trace id or a list of those.
        to_polar : bool, optional
            Whether if cartesian data has to be converted to polar before the plot or can be used as is.
        snapshot_path : str
            Full path to the image file if a snapshot is needed.
        show : bool, optional
            Whether to render the figure. The default is ``True``. If ``False``, the
            figure is not drawn.
        is_degree : bool, optional
            Whether if data source are in degree or not. Default is ``True``.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` object are created.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return False

        if not figure:
            self.fig, self.ax = plt.subplots(subplot_kw={"projection": "polar"})
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, projection="polar")

        legend = []
        i = 0
        rate = 1
        if is_degree:
            rate = np.pi / 180
        for trace in traces_to_plot:
            if not to_polar:
                theta = trace._cartesian_data[0] * rate
                r = trace._cartesian_data[1]
            else:
                theta, r = trace.car2polar(trace._cartesian_data[0], trace._cartesian_data[1], is_degree=is_degree)
            self.ax.plot(theta, r)
            self.ax.grid(True)
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            legend.append(trace.name)
            if i == 0:
                self.ax.set(xlabel=trace.x_label, ylabel=trace.y_label, title=self.title)
            i += 1

        if self.show_legend:
            self.ax.legend(legend, loc="upper right")
        self._plot(snapshot_path, show)
        return self.fig

    @pyaedt_function_handler()
    def plot_3d(self, trace=0, snapshot_path=None, show=True, color_map_limits=None, is_polar=True):
        """Create a Matplotlib 3D plot based on a list of data.

        Parameters
        ----------
        trace : int, str optional
            Trace index or name on which create the 3D Plot.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
        show : bool, optional
            Whether to show the plot or return the matplotlib object. Default is `True`.
        color_map_limits : list, optional
            Color map minimum and maximum values.
        is_polar : bool, optional
            Whether if the plot will be polar or not. Polar plot will hide axes and grids. Default is ``True``.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        if color_map_limits is None:
            color_map_limits = [0, 1]
        trace_number = self._retrieve_traces(trace)
        if not trace_number:
            return False
        self.fig, self.ax = plt.subplots(subplot_kw={"projection": "3d"})
        tr = trace_number[0]
        if not is_polar:
            self.ax.set_xlabel(tr.x_label, labelpad=20)
            self.ax.set_ylabel(tr.y_label, labelpad=20)
        self.ax.set_title(self.title)
        cmap = plt.get_cmap("jet")
        self.ax.plot_surface(
            tr._cartesian_data[0],
            tr._cartesian_data[1],
            tr._cartesian_data[2],
            rstride=1,
            cstride=1,
            cmap=cmap,
            linewidth=0,
            antialiased=True,
            alpha=0.65,
        )
        if is_polar:
            step = (color_map_limits[1] - color_map_limits[0]) / 10
            ticks = np.arange(color_map_limits[0], color_map_limits[1] + step, step)
            self.fig.colorbar(
                plt.cm.ScalarMappable(norm=Normalize(color_map_limits[0], color_map_limits[1]), cmap=cmap),
                ax=self.ax,
                ticks=ticks,
                shrink=0.7,
            )
            radius = tr._spherical_data[0].max() - tr._spherical_data[0].min()

            X = np.cos(np.arange(-3.14, 3.14, 0.01)) * radius
            Y = np.sin(np.arange(-3.14, 3.14, 0.01)) * radius
            Z = np.zeros(len(Y))
            self.ax.plot(X, Y, Z, color=(0, 0, 0), linewidth=2.5)

            X = np.cos(np.arange(-3.14, 3.14, 0.01)) * 0.6 * radius
            Y = np.sin(np.arange(-3.14, 3.14, 0.01)) * 0.6 * radius
            self.ax.plot(X, Y, Z, linestyle=":", color=(0, 0, 0))
            self.ax.text(
                0,
                radius,
                0.0,
                "Phi",
                fontweight="bold",
                fontsize=15,
            )

            X = np.arange(0, radius, 0.01)
            Y = np.zeros(len(X))
            Z = np.zeros(len(X))

            self.ax.plot(X, Y, Z, linestyle=":", color=(0, 0, 0))
            Y = np.arange(0, radius, 0.01)
            X = np.zeros(len(Y))
            self.ax.plot(X, Y, Z, linestyle=":", color=(0, 0, 0))

            Y = np.sin(np.arange(-3.14, 3.14, 0.01)) * radius
            Z = np.cos(np.arange(-3.14, 3.14, 0.01)) * radius
            X = np.zeros(len(Z))
            self.ax.plot(X, Y, Z, color=(0, 0, 0), linewidth=2.5)
            self.ax.text(
                0,
                0,
                radius,
                "Theta",
                fontweight="bold",
                fontsize=20,
            )

            Y = np.cos(np.arange(-3.14, 3.14, 0.01)) * 0.6 * radius
            Z = np.sin(np.arange(-3.14, 3.14, 0.01)) * 0.6 * radius
            self.ax.plot(X, Y, Z, linestyle=":", color=(0, 0, 0))
            self.ax.set_aspect("equal")
            self.ax.grid(False)

            # Hide axes ticks
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_zticks([])
            self.ax.set_axis_off()

        self._plot(snapshot_path, show)
        return self.fig

    @pyaedt_function_handler()
    def plot_2d(self, traces=None, snapshot_path=None, show=True, figure=None):
        """Create a Matplotlib figure based on a list of data.

        Parameters
        ----------
        traces : int, str, list, optional
            Trace or traces to be plotted. It can be the trace name, the trace id or a list of those.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default value is ``None``.
        show : bool, optional
            Whether to show the plot or return the matplotlib object. Default is `True`.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` object are created.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return False

        if not figure:
            self.fig, self.ax = plt.subplots()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111)

        legend_names = []

        min_x = None
        max_x = None
        min_y = None
        max_y = None

        for trace in traces_to_plot:
            self.ax.plot(
                trace._cartesian_data[0],
                trace._cartesian_data[1],
                f"{trace.symbol_style}{trace.trace_style}",
                fillstyle="full" if trace.fill_symbol else "none",
                markeredgecolor=trace.symbol_color,
                label=trace.name,
                color=trace.trace_color,
            )
            self.ax.set(xlabel=trace.x_label, ylabel=trace.y_label, title=self.title)
            min_y_current, max_y_current, min_x_current, max_x_current = self._set_scale(
                trace._cartesian_data[0], trace._cartesian_data[1]
            )

            if min_x is None or min_x_current < min_x:
                min_x = min_x_current
            if max_x is None or max_x_current > max_x:
                max_x = max_x_current

            if min_y is None or min_y_current < min_y:
                min_y = min_y_current
            if max_y is None or max_y_current > max_y:
                max_y = max_y_current

            self.ax.set_ylim(min_y, max_y)
            self.ax.set_xlim(min_x, max_x)

            legend_names.append(trace.name)
        self._plot_limit_lines()
        self._plot_notes()
        if self.show_legend:
            self.ax.legend(legend_names, loc="upper right")

        self._plot(snapshot_path, show)
        return self.fig

    @pyaedt_function_handler()
    def animate_2d(self, traces=None, snapshot_path=None, show=True, figure=None):
        """Create an animated Matplotlib figure based on a list of data.

        Parameters
        ----------
        traces : int, str, list, optional
            Trace or traces to be plotted. It can be the trace name, the trace id or a list of those.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default value is ``None``.
        show : bool, optional
            Whether to show the plot or return the matplotlib object. Default is `True`.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` object are created.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        self.animation = None

        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return False

        if not figure:
            self.fig, self.ax = plt.subplots()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111)

        def update(i):
            self.ax.clear()
            trace = traces_to_plot[i]
            line = self.ax.plot(
                trace._cartesian_data[0],
                trace._cartesian_data[1],
                f"{trace.symbol_style}{trace.trace_style}",
                fillstyle="full" if trace.fill_symbol else "none",
                markeredgecolor=trace.symbol_color,
                label=trace.name,
                color=trace.trace_color,
            )
            self.ax.set(xlabel=trace.x_label, ylabel=trace.y_label, title=self.title)
            if self.show_legend:
                self.ax.legend(loc="upper right")
            return line

        self.animation = FuncAnimation(self.fig, update, frames=len(traces_to_plot), blit=True, repeat=True)

        self._plot(snapshot_path, show)
        return self.animation

    @pyaedt_function_handler()
    def _plot_notes(self):
        for note in self._notes:
            t = self.ax.text(
                note.position[0],
                note.position[1],
                note.text,
                style="italic" if note.italic else "normal",
                fontweight="bold" if note.bold else "normal",
                color=note.color if note.color else (0, 0, 0),
                fontsize=note.font_size if note.font_size else 10,
                fontfamily=note.font.lower(),
            )
            if note.background_color and note.background_visibility:
                bbox = {
                    "facecolor": note.background_color,
                    "alpha": 0.5,
                    "pad": note.border_width if note.border_width else 1,
                }
                t.set_bbox(bbox)

    @pyaedt_function_handler()
    def _plot_limit_lines(self, convert_to_radians=False):
        rate = 1
        if convert_to_radians:
            rate = np.pi / 180
        for _, trace in self.limit_lines.items():
            min_y = np.amin(trace._cartesian_data[1]) * rate
            max_y = np.amax(trace._cartesian_data[1]) * rate
            delta = (max_y - min_y) / 5
            self.ax.plot(
                trace._cartesian_data[0] * rate,
                trace._cartesian_data[1],
                f"{trace.symbol_style}{trace.trace_style}",
                fillstyle="full" if trace.fill_symbol else "none",
                markeredgecolor=trace.symbol_color,
                label=trace.name,
                color=trace.trace_color,
            )
            if trace.hatch_above:
                y_data = [i + delta for i in trace._cartesian_data[1]]
                self.ax.fill_between(
                    trace._cartesian_data[0] * rate,
                    trace._cartesian_data[1],
                    y_data,
                    alpha=0.3,
                    color=trace.trace_color,
                    hatch="/",
                )
            else:
                y_data = [i - delta for i in trace._cartesian_data[1]]
                self.ax.fill_between(
                    trace._cartesian_data[0] * rate,
                    y_data,
                    trace._cartesian_data[1],
                    alpha=0.3,
                    color=trace.trace_color,
                    hatch="/",
                )

    @pyaedt_function_handler()
    def plot_contour(
        self,
        trace=0,
        polar=False,
        levels=64,
        max_theta=180,
        min_theta=0,
        color_bar=None,
        snapshot_path=None,
        show=True,
        figure=None,
        is_spherical=True,
        normalize=None,
    ):
        """Create a Matplotlib figure contour based on a list of data.

        Parameters
        ----------
        trace : int, str, optional
            Trace index on which create the 3D Plot.
        polar : bool, optional
            Generate the plot in polar coordinates. The default is ``True``. If ``False``, the plot
            generated is rectangular.
        levels : int, optional
            Color map levels. The default is ``64``.
        max_theta : float or int, optional
            Maximum theta angle for plotting. It applies only for polar plots.
            The default is ``180``, which plots the data for all angles.
            Setting ``max_theta`` to 90 limits the displayed data to the upper
            hemisphere, that is (0 < theta < 90).
        min_theta : float or int, optional
            Minimum theta angle for plotting. It applies only for polar plots. The default is ``0``.
        color_bar : str, optional
            Color bar title. The default is ``None`` in which case the color bar is not included.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default value is ``None``.
        show : bool, optional
            Whether to show the plot or return the matplotlib object. Default is ``True``.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` object are created.
        is_spherical : bool, optional
            Whether to use spherical or cartesian data.
        normalize : list, optional
            Normalize the color scale using the provided ``[vmin, vmax]`` values.
            If not provided or invalid, automatic normalization is applied.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        tr = self._retrieve_traces(trace)
        if not tr:
            return False
        else:
            tr = tr[0]

        projection = "polar" if polar else "rectilinear"

        if not figure:
            self.fig, self.ax = plt.subplots(subplot_kw={"projection": projection})
            self.ax = plt.gca()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, polar=polar)

        self.ax.set_xlabel(tr.x_label)
        if polar:
            self.ax.set_rticks(np.linspace(min_theta, max_theta, 3))
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            self.ax.set_thetamin(min_theta)
            self.ax.set_thetamax(max_theta)
        else:
            self.ax.set_ylabel(tr.y_label)

        self.ax.set(title=self.title)

        if not is_spherical:
            ph = tr._cartesian_data[2]
            th = tr._cartesian_data[1]
            data_to_plot = tr._cartesian_data[0]
        else:
            ph = tr._spherical_data[2]
            th = tr._spherical_data[1]
            data_to_plot = tr._spherical_data[0]

        norm = None
        if isinstance(normalize, list) and len(normalize) == 2:
            norm = Normalize(vmin=normalize[0], vmax=normalize[1])

        contour = self.ax.contourf(ph, th, data_to_plot, levels=levels, cmap="jet", norm=norm, extend="both")
        if color_bar:
            cbar = self.fig.colorbar(contour, ax=self.ax)
            cbar.set_label(color_bar, rotation=270, labelpad=20)

        self.ax.yaxis.set_label_coords(-0.1, 0.5)
        self._plot(snapshot_path, show)
        return self.fig

    @pyaedt_function_handler()
    def plot_pcolor(
        self,
        trace=0,
        color_bar=None,
        snapshot_path=None,
        show=True,
        figure=None,
    ):
        """Create a Matplotlib figure pseudo color plot with a non-regular rectangular grid based on a list of data.

        Parameters
        ----------
        trace : int, str, optional
            Trace index on which create the 3D Plot.
        color_bar : str, optional
            Color bar title. The default is ``None`` in which case the color bar is not included.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default value is ``None``.
        show : bool, optional
            Whether to show the plot or return the matplotlib object. Default is ``True``.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` object are created.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        tr = self._retrieve_traces(trace)
        if not tr:
            return False
        else:
            tr = tr[0]
        projection = "rectilinear"

        if not figure:
            self.fig, self.ax = plt.subplots(subplot_kw={"projection": projection})
            self.ax = plt.gca()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, polar=False)

        self.ax.set_xlabel(tr.x_label)
        self.ax.set_ylabel(tr.y_label)

        self.ax.set(title=self.title)
        X = np.array(list(zip(*tr._cartesian_data[2]))[0])
        dxO2 = (X[1] - X[0]) / 2
        X = np.linspace(X[0] - dxO2, X[-1] + dxO2, len(X) + 1)
        Y = np.array(tr._cartesian_data[1][0])
        dyO2 = (Y[1] - Y[0]) / 2
        Y = np.linspace(Y[0] - dyO2, Y[-1] + dyO2, len(Y) + 1)
        data_to_plot = tr._cartesian_data[0]

        contour = self.ax.pcolormesh(X, Y, data_to_plot.T, cmap="jet", shading="flat")
        if color_bar:
            cbar = self.fig.colorbar(contour, ax=self.ax)
            cbar.set_label(color_bar, rotation=270, labelpad=20)

        self.ax.yaxis.set_label_coords(-0.1, 0.5)
        self._plot(snapshot_path, show)
        return self.fig

    @pyaedt_function_handler()
    def animate_contour(
        self,
        trace=0,
        polar=False,
        levels=64,
        max_theta=180,
        min_theta=0,
        color_bar=None,
        snapshot_path=None,
        show=True,
        figure=None,
        is_spherical=True,
        normalize=None,
    ):
        """Create an animated Matplotlib figure contour based on a list of data.

        Parameters
        ----------
        trace : int, str, optional
            Trace index on which create the 3D Plot.
        polar : bool, optional
            Generate the plot in polar coordinates. The default is ``True``. If ``False``, the plot
            generated is rectangular.
        levels : int, optional
            Color map levels. The default is ``64``.
        max_theta : float or int, optional
            Maximum theta angle for plotting. It applies only for polar plots.
            The default is ``180``, which plots the data for all angles.
            Setting ``max_theta`` to 90 limits the displayed data to the upper
            hemisphere, that is (0 < theta < 90).
        min_theta : float or int, optional
            Minimum theta angle for plotting. It applies only for polar plots. The default is ``0``.
        color_bar : str, optional
            Color bar title. The default is ``None`` in which case the color bar is not included.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default value is ``None``.
        show : bool, optional
            Whether to show the plot or return the matplotlib object. Default is ``True``.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` object are created.
        is_spherical : bool, optional
            Whether to use spherical or cartesian data.
        normalize : list, optional
            Normalize the color scale using the provided ``[vmin, vmax]`` values.
            If not provided or invalid, automatic normalization is applied.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        self.animation = None

        traces_to_plot = self._retrieve_traces(trace)
        if not traces_to_plot:
            return False

        projection = "polar" if polar else "rectilinear"

        if not figure:
            self.fig, self.ax = plt.subplots(subplot_kw={"projection": projection})
            self.ax = plt.gca()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, polar=polar)

        def update(i):
            self.ax.clear()
            trace = traces_to_plot[i]
            self.ax.set_xlabel(trace.x_label)
            if polar:
                self.ax.set_rticks(np.linspace(min_theta, max_theta, 3))
                self.ax.set_theta_zero_location("N")
                self.ax.set_theta_direction(-1)
                self.ax.set_thetamin(min_theta)
                self.ax.set_thetamax(max_theta)
            else:
                self.ax.set_ylabel(trace.y_label)

            self.ax.set(title=self.title)

            if not is_spherical:
                ph = trace._cartesian_data[2]
                th = trace._cartesian_data[1]
                data_to_plot = trace._cartesian_data[0]
            else:
                ph = trace._spherical_data[2]
                th = trace._spherical_data[1]
                data_to_plot = trace._spherical_data[0]

            norm = None
            if isinstance(normalize, list) and len(normalize) == 2:
                norm = Normalize(vmin=normalize[0], vmax=normalize[1])

            contour = self.ax.contourf(
                ph,
                th,
                data_to_plot,
                levels=levels,
                cmap="jet",
                norm=norm,
                extend="both",
            )
            if color_bar:
                cbar = self.fig.colorbar(contour, ax=self.ax)
                cbar.set_label(color_bar, rotation=270, labelpad=20)

            self.ax.yaxis.set_label_coords(-0.1, 0.5)
            return contour

        self.animation = FuncAnimation(self.fig, update, frames=len(traces_to_plot), blit=False, repeat=True)

        self._plot(snapshot_path, show)
        return self.animation


@pyaedt_function_handler()
def plot_polar_chart(
    plot_data, size=(1920, 1440), show_legend=True, xlabel="", ylabel="", title="", snapshot_path=None, show=True
):
    """Create a Matplotlib polar plot based on a list of data.

    .. deprecated:: 0.11.1
        Use :class:`ReportPlotter` instead.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        ``[x points, y points, label]``.
    size : tuple, optional
        Image size in pixel (width, height).
    show_legend : bool
        Either to show legend or not.
    xlabel : str
        Plot X label.
    ylabel : str
        Plot Y label.
    title : str
        Plot title label.
    snapshot_path : str
        Full path to the image file if a snapshot is needed.
    show : bool, optional
        Whether to render the figure. The default is ``True``. If ``False``, the
        figure is not drawn.

    Returns
    -------
    :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
        Matplotlib class object.
    """
    new = ReportPlotter()
    new.size = size
    new.show_legend = show_legend
    new.title = title
    props = {"x_label": xlabel, "y_label": ylabel}
    for pdata in plot_data:
        name = pdata[2] if len(pdata) > 2 else "Trace"
        new.add_trace(pdata[:2], 0, props, name=name)
    _ = new.plot_polar(traces=None, snapshot_path=snapshot_path, show=show)
    return new


@pyaedt_function_handler()
def plot_3d_chart(plot_data, size=(1920, 1440), xlabel="", ylabel="", title="", snapshot_path=None, show=True):
    """Create a Matplotlib 3D plot based on a list of data.

    .. deprecated:: 0.11.1
        Use :class:`ReportPlotter` instead.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        ``[x points, y points, z points, label]``.
    size : tuple, optional
        Image size in pixel (width, height).
    xlabel : str, optional
        Plot X label.
    ylabel : str, optional
        Plot Y label.
    title : str, optional
        Plot Title label.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is `True`.

    Returns
    -------
    :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
        Matplotlib class object.
    """
    warnings.warn(
        "`plot_3d_chart` is deprecated. Use class `ReportPlotter` to initialize and `plot_3d` instead.",
        DeprecationWarning,
    )
    new = ReportPlotter()
    new.size = size
    new.show_legend = False
    new.title = title
    props = {"x_label": xlabel, "y_label": ylabel}
    name = plot_data[3] if len(plot_data) > 3 else "Trace"
    new.add_trace(plot_data[:3], 2, props, name)
    _ = new.plot_3d(trace=0, snapshot_path=snapshot_path, show=show)
    return new


@pyaedt_function_handler()
def plot_2d_chart(
    plot_data, size=(1920, 1440), show_legend=True, xlabel="", ylabel="", title="", snapshot_path=None, show=True
):
    """Create a Matplotlib figure based on a list of data.

    .. deprecated:: 0.11.1
        Use :class:`ReportPlotter` instead.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        `[x points, y points, label]`.
    size : tuple, optional
        Image size in pixel (width, height). The default is `(1920,1440)`.
    show_legend : bool, optional
        Either to show legend or not. The default value is ``True``.
    xlabel : str, optional
        Plot X label. The default value is ``""``.
    ylabel : str, optional
        Plot Y label. The default value is ``""``.
    title : str, optional
        Plot Title label. The default value is ``""``.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed.
        The default value is ``None``.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is `True`.

    Returns
    -------
    :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
        Matplotlib class object.
    """
    warnings.warn(
        "`plot_2d_chart` is deprecated. Use class `ReportPlotter` to initialize and `plot_2d` instead.",
        DeprecationWarning,
    )
    new = ReportPlotter()
    new.size = size
    new.show_legend = show_legend
    new.title = title
    from ansys.aedt.core.generic.constants import CSS4_COLORS

    k = 0
    for data in plot_data:
        label = f"{xlabel}_{data[2]}" if len(data) == 3 else xlabel
        props = {"x_label": label, "y_label": ylabel, "line_color": list(CSS4_COLORS.keys())[k]}
        k += 1
        if k == len(list(CSS4_COLORS.keys())):
            k = 0
        name = data[2] if len(data) > 2 else "Trace"
        new.add_trace(data[:2], 0, props, name)
    _ = new.plot_2d(None, snapshot_path, show)
    return new


@pyaedt_function_handler()
def plot_matplotlib(
    plot_data,
    size=(1920, 1440),
    show_legend=True,
    xlabel="",
    ylabel="",
    title="",
    snapshot_path=None,
    x_limits=None,
    y_limits=None,
    axis_equal=False,
    annotations=None,
    show=True,
):  # pragma: no cover
    """Create a matplotlib plot based on a list of data.

    Parameters
    ----------
    plot_data : list of list
        List of plot data. Every item has to be in the following format
        For type ``fill``: `[x points, y points, color, label, alpha, type=="fill"]`.
        For type ``path``: `[vertices, codes, color, label, alpha, type=="path"]`.
        For type ``contour``: `[vertices, codes, color, label, alpha, line_width, type=="contour"]`.
    size : tuple, optional
        Image size in pixel (width, height). Default is `(1920, 1440)`.
    show_legend : bool, optional
        Either to show legend or not. Default is `True`.
    xlabel : str, optional
        Plot X label. Default is `""`.
    ylabel : str, optional
        Plot Y label. Default is `""`.
    title : str, optional
        Plot Title label. Default is `""`.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed. Default is `None`.
    x_limits : list, optional
        List of x limits (left and right). Default is `None`.
    y_limits : list, optional
        List of y limits (bottom and top). Default is `None`.
    axis_equal : bool, optional
         Whether to show the same scale on both axis or have a different scale based on plot size.
        Default is `False`.
    annotations : list, optional
        List of annotations to add to the plot. The format is [x, y, string, dictionary of font options].
        Default is `None`.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is `True`.

    Returns
    -------
    :class:`matplotlib.pyplot.Figure`
        Matplotlib figure object.
    """
    dpi = 100.0
    fig, ax = plt.subplots()
    fig.set_size_inches(size[0] / dpi, size[1] / dpi)

    if isinstance(plot_data, str):
        plot_data = ast.literal_eval(plot_data)
    for points in plot_data:
        if points[-1] == "fill":
            plt.fill(points[0], points[1], c=points[2], label=points[3], alpha=points[4])
        elif points[-1] == "path":
            path = Path(points[0], points[1])
            patch = PathPatch(path, color=points[2], alpha=points[4], label=points[3])
            ax.add_patch(patch)
        elif points[-1] == "contour":
            path = Path(points[0], points[1])
            patch = PathPatch(path, color=points[2], alpha=points[4], label=points[3], fill=False, linewidth=points[5])
            ax.add_patch(patch)

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if show_legend:
        ax.legend(loc="upper right")

    # evaluating the limits
    xmin = ymin = 1e30
    xmax = ymax = -1e30
    for points in plot_data:
        if points[-1] == "fill":
            xmin = min(xmin, min(points[0]))
            xmax = max(xmax, max(points[0]))
            ymin = min(ymin, min(points[1]))
            ymax = max(ymax, max(points[1]))
        else:
            for p in points[0]:
                xmin = min(xmin, p[0])
                xmax = max(xmax, p[0])
                ymin = min(ymin, p[1])
                ymax = max(ymax, p[1])
    if x_limits:
        ax.set_xlim(x_limits)
    else:
        ax.set_xlim([xmin, xmax])
    if y_limits:
        ax.set_ylim(y_limits)
    else:
        ax.set_ylim([ymin, ymax])

    if axis_equal:
        ax.axis("equal")

    if annotations:
        for annotation in annotations:
            plt.text(annotation[0], annotation[1], annotation[2], **annotation[3])

    if snapshot_path:
        plt.savefig(snapshot_path)
    if show:  # pragma: no cover
        plt.show()
    return fig


@pyaedt_function_handler()
def plot_contour(
    plot_data,
    size=(2000, 1600),
    xlabel="",
    ylabel="",
    title="",
    polar=False,
    levels=64,
    max_theta=180,
    color_bar=None,
    snapshot_path=None,
    show=True,
):
    """Create a Matplotlib figure contour based on a list of data.

    .. deprecated:: 0.11.1
        Use :class:`ReportPlotter` instead.

    Parameters
    ----------
    plot_data : list of np.ndarray
        List of plot data. Each item of the list a numpy array. The list has the following format:
        ``[data, x points, y points]``.
    size : tuple, list, optional
        Image size in pixel (width, height). The default is ``(2000,1600)``.
    xlabel : str, optional
        Plot X label. The default value is ``""``.
    ylabel : str, optional
        Plot Y label. The default value is ``""``.
    title : str, optional
        Plot Title label. The default value is ``""``.
    polar : bool, optional
        Generate the plot in polar coordinates. The default is ``True``. If ``False``, the plot
        generated is rectangular.
    levels : int, optional
        Color map levels. The default is ``64``.
    max_theta : float or int, optional
        Maximum theta angle for plotting. It applies only for polar plots.
        The default is ``180``, which plots the data for all angles.
        Setting ``max_theta`` to 90 limits the displayed data to the upper
        hemisphere, that is (0 < theta < 90).
    color_bar : str, optional
        Color bar title. The default is ``None`` in which case the color bar is not included.
    snapshot_path : str, optional
        Full path to image file if a snapshot is needed.
        The default value is ``None``.
    show : bool, optional
        Whether to show the plot or return the matplotlib object. Default is ``True``.

    Returns
    -------
    :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
        Matplotlib class object.
    """
    warnings.warn(
        "`plot_contour` is deprecated. Use class `ReportPlotter` to initialize and `plot_contour` instead.",
        DeprecationWarning,
    )
    new = ReportPlotter()
    new.size = size
    new.show_legend = False
    new.title = title
    props = {
        "x_label": xlabel,
        "y_label": ylabel,
    }

    new.add_trace(plot_data, 2, props)
    _ = new.plot_contour(
        trace=0,
        polar=polar,
        levels=levels,
        max_theta=max_theta,
        color_bar=color_bar,
        snapshot_path=snapshot_path,
        show=show,
    )
    return new
