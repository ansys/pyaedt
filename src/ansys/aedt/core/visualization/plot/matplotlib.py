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

from __future__ import annotations

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
from ansys.aedt.core.visualization.plot.contour import bin_to_grid
from ansys.aedt.core.visualization.plot.contour import extract_eye_opening_contour_by_center

# Check that graphics are available
try:
    check_graphics_available()

    from matplotlib.animation import FuncAnimation
    from matplotlib.colors import LogNorm
    from matplotlib.colors import Normalize
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


def is_notebook() -> bool:
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


def is_ipython() -> bool:
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
    def __init__(self) -> None:
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
    def text(self) -> str:
        """Note text.

        Returns
        -------
        str
        """
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def background_color(self) -> tuple | list:
        """Note color.

        Returns
        -------
        tuple or list
        """
        return self._back_color

    @background_color.setter
    def background_color(self, value: tuple | list) -> None:
        self._back_color = value

    @property
    def background_visibility(self) -> bool:
        """Note background visibility.

        Returns
        -------
        bool
        """
        return self._background_visibility

    @background_visibility.setter
    def background_visibility(self, value: bool) -> None:
        self._background_visibility = value

    @property
    def border_visibility(self) -> bool:
        """Note border visibility.

        Returns
        -------
        bool
        """
        return self._border_visibility

    @border_visibility.setter
    def border_visibility(self, value: bool) -> None:
        self._border_visibility = value

    @property
    def border_width(self) -> float:
        """Note border width.

        Returns
        -------
        float
        """
        return self._border_width

    @border_width.setter
    def border_width(self, value: float) -> None:
        self._border_width = value

    @property
    def font(self) -> str:
        """Note font.

        Returns
        -------
        str
        """
        return self._font

    @font.setter
    def font(self, value: str) -> None:
        self._font = value

    @property
    def font_size(self) -> str:
        """Note font size.

        Returns
        -------
        str
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font_size = value

    @property
    def color(self) -> tuple | list:
        """Note font color.

        Returns
        -------
        list
        """
        return self._color

    @color.setter
    def color(self, value: tuple | list) -> None:
        self._color = value

    @property
    def bold(self) -> bool:
        """Note font bold.

        Returns
        -------
        bool
        """
        return self._bold

    @bold.setter
    def bold(self, value: bool) -> None:
        self._bold = value

    @property
    def italic(self) -> bool:
        """Note font italic.

        Returns
        -------
        bool
        """
        return self._italic

    @italic.setter
    def italic(self, value: bool) -> None:
        self._italic = value


class Trace(PyAedtBase):
    """Trace class."""

    def __init__(self) -> None:
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
    def trace_style(self) -> str:
        """Matplotlib trace style.

        Returns
        -------
        str
        """
        return self.__trace_style

    @property
    def trace_width(self) -> float:
        """Trace width.

        Returns
        -------
        float
        """
        return self.__trace_width

    @property
    def trace_color(self) -> tuple | str | None:
        """Matplotlib trace color. It can be a tuple or a string of allowed colors.

        Returns
        -------
        str, list
        """
        return self.__trace_color

    @property
    def symbol_style(self) -> str:
        """Matplotlib symbol style.

        Returns
        -------
        str
        """
        return self.__symbol_style

    @property
    def fill_symbol(self) -> bool:
        """Fill symbol.

        Returns
        -------
        bool
        """
        return self.__fill_symbol

    @trace_style.setter
    def trace_style(self, val: str) -> None:
        self.__trace_style = val

    @trace_width.setter
    def trace_width(self, val: float) -> None:
        self.__trace_width = val

    @trace_color.setter
    def trace_color(self, val: tuple | str | None) -> None:
        self.__trace_color = val

    @symbol_style.setter
    def symbol_style(self, val: str) -> None:
        self.__symbol_style = val

    @fill_symbol.setter
    def fill_symbol(self, val: bool) -> None:
        self.__fill_symbol = val

    @property
    def cartesian_data(self) -> list[np.ndarray] | None:
        """Cartesian data [x,y,z].

        Returns
        -------
        list[:class:`numpy.array`]
            List of data.
        """
        return self._cartesian_data

    @cartesian_data.setter
    def cartesian_data(self, val: list[np.ndarray] | list[float] | list[int] | list[str]) -> None:
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
    def spherical_data(self) -> list[np.ndarray] | None:
        """Spherical data [r, theta, phi]. Angles are in degrees.

        Returns
        -------
        list[:class:`numpy.array`]
            List of data.
        """
        return self._spherical_data

    @spherical_data.setter
    def spherical_data(self, rthetaphi: list[np.ndarray] | list[float] | list[int] | list[str]) -> None:
        self._spherical_data = []
        for el in rthetaphi:
            if not isinstance(el, (float, int, str)):
                self._spherical_data.append(np.array(el, dtype=float))
            else:
                self._spherical_data.append(el)
        self.spherical2car()

    @pyaedt_function_handler()
    def car2polar(self, x: list | np.ndarray, y: list | np.ndarray, is_degree: bool = False) -> list:
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
    def car2spherical(self) -> None:
        """Convert cartesian data to spherical and assigns to property spherical data."""
        try:
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
        except ValueError:
            self._spherical_data = []

    @pyaedt_function_handler()
    def spherical2car(self) -> None:
        """Convert spherical data to cartesian data and assign to cartesian data property."""
        r = np.array(self._spherical_data[0], dtype=float)
        theta = np.array(self._spherical_data[1] * math.pi / 180, dtype=float)  # to radian
        phi = np.array(self._spherical_data[2] * math.pi / 180, dtype=float)
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        self._cartesian_data = [x, y, z]

    @pyaedt_function_handler()
    def polar2car(self, r: list | np.ndarray, theta: list | np.ndarray) -> list[np.ndarray]:
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

    def __init__(self) -> None:
        Trace.__init__(self)
        self.hatch_above = True


class EyeMask:
    def __init__(self):
        self.eye_xunits = "ns"
        self.eye_yunits = "mV"
        self.eye_points = []
        self.eye_enable = False
        self.eye_upper = 500
        self.eye_lower = 0.3
        self.eye_transparency = 0.3
        self.eye_color = (0, 128, 0)
        self.eye_xoffset = "0ns"
        self.eye_yoffset = "0V"


class ReportPlotter(PyAedtBase):
    """Matplotlib Report manager."""

    def __init__(self, solution_data=None) -> None:
        rc_params = {
            "axes.titlesize": 26,  # Use these default settings for Matplotlb axes.
            "axes.labelsize": 20,  # Apply the settings only in this module.
            "xtick.labelsize": 18,
            "ytick.labelsize": 18,
        }
        self.block = settings.block_figure_plot
        self._traces = {}
        self._limit_lines = {}
        self._eye_mask = None
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
        self.__text_size = 12
        self.__title_size = 16
        self.__solution_data = solution_data
        self.__dpi = 100
        self.__width = 1200
        self.__height = 800
        self.unit_interval = 0
        self.offset = 0

    @property
    def dpi(self) -> int:
        """Figure dpi."""
        return self.__dpi

    @dpi.setter
    def dpi(self, value: int) -> None:
        self.__dpi = value

    @property
    def width(self) -> int:
        """Figure width."""
        return self.__width

    @width.setter
    def width(self, value: int) -> None:
        self.__width = value

    @property
    def height(self) -> int:
        """Figure height."""
        return self.__height

    @height.setter
    def height(self, value: int) -> None:
        self.__height = value

    @property
    def text_size(self) -> int:
        """Text font size"""
        return self.__text_size

    @text_size.setter
    def text_size(self, size: int) -> None:
        self.__text_size = size

    @property
    def title_size(self) -> int:
        """Title font size"""
        return self.__title_size

    @title_size.setter
    def title_size(self, size: int) -> None:
        self.__title_size = size

    def get_solution_data(self):
        """Mimic the report method to retrieve solution data if available."""
        return self.__solution_data

    @property
    def traces(self) -> dict[str, Trace]:
        """Traces.

        Returns
        -------
         dict[str, :class:`ansys.aedt.core.visualization.plot.matplotlib.Trace`]
        """
        return self._traces

    @property
    def traces_by_index(self) -> list[Trace]:
        """Traces.

        Returns
        -------
         list[:class:`ansys.aedt.core.visualization.plot.matplotlib.Trace`]
        """
        return list(self._traces.values())

    @property
    def trace_names(self) -> list[str]:
        """Trace names.

        Returns
        -------
        list
        """
        return list(self._traces.keys())

    @property
    def limit_lines(self) -> dict[str, LimitLine]:
        """Limit Lines.

        Returns
        -------
         dict[str, :class:`ansys.aedt.core.visualization.plot.matplotlib.LimitLine`]
        """
        return self._limit_lines

    @pyaedt_function_handler()
    def apply_style(self, style_name: str) -> bool:
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
    def grid_style(self) -> str:
        """Grid style.

        Returns
        -------
        str
        """
        return self.__grid_style

    @grid_style.setter
    def grid_style(self, val: str) -> None:
        self.__grid_style = val

    @property
    def grid_enable_major_x(self) -> bool:
        """Enable the major grid on x axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_major_x

    @grid_enable_major_x.setter
    def grid_enable_major_x(self, val: bool) -> None:
        self.__grid_enable_major_x = val

    @property
    def grid_enable_major_y(self) -> bool:
        """Enable the major grid on y axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_major_y

    @grid_enable_major_y.setter
    def grid_enable_major_y(self, val: bool) -> None:
        self.__grid_enable_major_y = val

    @property
    def grid_enable_minor_x(self) -> bool:
        """Enable the minor grid on x axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_minor_x

    @grid_enable_minor_x.setter
    def grid_enable_minor_x(self, val: bool) -> None:
        self.__grid_enable_minor_x = val

    @property
    def grid_enable_minor_y(self) -> bool:
        """Enable the minor grid on y axis.

        Returns
        -------
        bool
        """
        return self.__grid_enable_minor_y

    @grid_enable_minor_y.setter
    def grid_enable_minor_y(self, val: bool) -> None:
        self.__grid_enable_minor_y = val

    @property
    def grid_color(self) -> tuple | str:
        """Grid color.

        Returns
        -------
        str, list
            Grid color tuple.
        """
        return self.__grid_color

    @grid_color.setter
    def grid_color(self, val: tuple | str) -> None:
        if isinstance(val, (list, tuple)):
            if any([i for i in val if i > 1]):
                val = [i / 255 for i in val]
        self.__grid_color = val

    @property
    def general_back_color(self) -> tuple | str:
        """General background color.

        Returns
        -------
        str, list
        """
        return self.__general_back_color

    @general_back_color.setter
    def general_back_color(self, val: tuple | str) -> None:
        if isinstance(val, (list, tuple)):
            if any([i for i in val if i > 1]):
                val = [i / 255 for i in val]
        self.__general_back_color = val

    @property
    def general_plot_color(self) -> tuple | str:
        """General plot color.

        Returns
        -------
        str, list
        """
        return self.__general_plot_color

    @general_plot_color.setter
    def general_plot_color(self, val: tuple | str) -> None:
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
    def _update_grid(self) -> None:
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
            if self.ax:
                self.ax.set_facecolor(self.__general_plot_color)
                self.ax.grid(color=self.__grid_color)
                self.fig.set_facecolor(self.__general_back_color)
            else:
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
            self.ax.tick_params(axis="x", colors=self.__grid_color, labelsize=self.text_size)
            self.ax.tick_params(axis="y", colors=self.__grid_color, labelsize=self.text_size)

    @property
    def y_scale(self) -> str:
        """Y axis scale. It can be linear or log.

        Returns
        -------
        str
        """
        return self.__y_scale

    @y_scale.setter
    def y_scale(self, val: str) -> None:
        self.__y_scale = val

    @property
    def x_scale(self) -> str:
        """X axis scale. It can be linear or log.

        Returns
        -------
        str
        """
        return self.__x_scale

    @x_scale.setter
    def x_scale(self, val: str) -> None:
        self.__x_scale = val

    @property
    def interactive(self) -> bool:
        """Enable interactive mode.

        Returns
        -------
        bool
        """
        return plt.isinteractive()

    @interactive.setter
    def interactive(self, val: bool) -> None:
        if val:
            plt.ion()
        else:
            plt.ioff()

    def add_note(
        self,
        text: str,
        position: tuple = (0, 1),
        back_color: tuple | str = None,
        background_visibility: bool = None,
        border_width: float = None,
        font: str = "Arial",
        font_size: int = 12,
        italic: bool = False,
        bold: bool = False,
        color: tuple = (0.2, 0.2, 0.2),
    ) -> None:
        """Add a note to the report.

        Parameters
        ----------
        text : str
        position : tuple, optional
        back_color : tuple | str, optional
        background_visibility : bool, optional
        border_width : float, optional
        font : str, optional
        font_size : float, optional
        italic : bool, optional
        bold : bool, optional
        color : tuple, optional

        Returns
        -------
        None
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
    def add_limit_line(
        self, plot_data: list, hatch_above: bool = True, properties: dict = None, name: str = ""
    ) -> bool:
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

    def add_eye_mask(self, properties):
        """Add a new eye mask to the chart.

        Parameters
        ----------
        properties : dict, optional
            Properties of the trace.
        """
        self._eye_mask = EyeMask()
        self._eye_mask.eye_points = properties.get("points", [])
        self._eye_mask.eye_xunits = properties.get("xunits", "")
        self._eye_mask.eye_yunits = properties.get("yunits", "")
        self._eye_mask.eye_enable = properties.get("enable_limits", False)
        self._eye_mask.eye_upper = properties.get("upper_limit", 500)
        self._eye_mask.eye_lower = properties.get("lower_limit", -500)
        self._eye_mask.eye_color = properties.get("color", (0, 128, 0))
        self._eye_mask.eye_xoffset = properties.get("X Offset", 0)
        self._eye_mask.eye_yoffset = properties.get("Y Offset", 0)
        self._eye_mask.eye_transparency = properties.get("transparency", 0.3)

    @pyaedt_function_handler()
    def add_trace(self, plot_data: list, data_type: int = 0, properties: dict = None, name: str = "") -> bool:
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
    def size(self) -> list:
        """Figure size.

        Returns
        -------
        list
        """
        px = self.plt_params["figure.dpi"]  # pixel in inches
        return [i * px for i in self.plt_params["figure.figsize"]]

    @size.setter
    def size(self, val: list, is_pixel: bool = True) -> None:
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
                self.fig.savefig(snapshot_path, dpi=self.dpi)
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
    def plot_polar(
        self,
        traces: list | int | str = None,
        to_polar: bool = False,
        snapshot_path: str = None,
        show: bool = True,
        is_degree: bool = True,
        figure: plt.Figure = None,
    ) -> plt.Figure | bool:
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
            self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)

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
    def plot_3d(
        self,
        trace: int = 0,
        snapshot_path: str = None,
        show: bool = True,
        color_map_limits: list = None,
        is_polar: bool = True,
    ) -> plt.Figure | bool:
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
        self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
        tr = trace_number[0]
        if not is_polar:
            self.ax.set_xlabel(tr.x_label, labelpad=20)
            self.ax.set_ylabel(tr.y_label, labelpad=20)
        self.ax.set_title(self.title, color=self.__grid_color, fontsize=self.title_size)
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
    def plot_2d(
        self, traces: list | int | str = None, snapshot_path: str = None, show: bool = True, figure: plt.Figure = None
    ) -> plt.Figure | bool:
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
        :class:`matplotlib.pyplot.Figure` | bool
            Matplotlib figure object.
        """
        traces_to_plot = self._retrieve_traces(traces)
        if not traces_to_plot:
            return False

        if not figure:
            self.fig, self.ax = plt.subplots()
            self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
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

        self.ax.set_xlabel(trace.x_label, color=self.__grid_color, fontsize=self.text_size)
        self.ax.set_ylabel(trace.y_label, color=self.__grid_color, fontsize=self.text_size)
        self.ax.set_title(
            self.title,
            color=self.__grid_color,
            fontsize=self.title_size,
        )
        self._plot(snapshot_path, show)
        return self.fig

    @pyaedt_function_handler()
    def animate_2d(
        self, traces: list | int | str = None, snapshot_path: str = None, show: bool = True, figure: plt.Figure = None
    ) -> plt.Figure | bool:
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
            self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
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
    def plot_eye_diagram(
        self,
        snapshot_path: str = None,
        show: bool = True,
        is_contour=False,
        filter_colormap=1e-6,
        plot_max_height=True,
        plot_eye_mask=True,
    ):
        """Plot Eye diagram and contour plot.

        Parameters
        ----------
        snapshot_path : str, optional
            Path to output image file. If not provided, the plot will not be saved.
        show : bool, optional
            Whether to display the plot. Default is `True`.
        is_contour : bool, optional
            Whether to plot is a BET contour plot.
        filter_colormap : float, optional
            Whether to filter the contour data and start from a specific BER.
        plot_max_height : bool, optional
            Whether to plot the maximum height lines on the eye diagram. Doesn't apply to contour plot.
        plot_eye_mask : bool, optional
            Whether to plot the eye mask on the eye diagram.

        """
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
        self.__grid_enable_minor_y = False
        self.__grid_enable_minor_x = False

        traces_to_plot = self._retrieve_traces(None)[0]
        if not traces_to_plot:
            return False
        if traces_to_plot.x_label == "Time" and self.unit_interval:
            period = 2 * self.unit_interval

            time = traces_to_plot.cartesian_data[0]
            value = traces_to_plot.cartesian_data[1]

            # Ensure time is sorted for interpolation
            t_fold = np.mod(time - self.offset, period)

            # Number of bins
            nx = 300  # time resolution
            ny = 300  # value resolution

            Xc = np.linspace(0, period, nx + 1)  # shape (301,)
            Yc = np.linspace(value.min(), value.max(), ny + 1)  # shape (301,)

            # Create 2D histogram
            Z, _, _ = np.histogram2d(t_fold, value, bins=[Xc, Yc])
            # Z has shape (nx, ny) from np.histogram2d
            # pcolormesh expects Z with shape (ny, nx) when given Xc and Yc
            cmap = plt.cm.nipy_spectral

            # Transpose for pcolormesh
            Z_plot = Z.T
            cmap.set_under(self.__general_plot_color)
            minz = min(Z[np.where(Z > 0)])

            Z_plot = np.ma.masked_less(Z_plot, minz)
            self.ax.pcolormesh(
                Xc,
                Yc,
                Z_plot,
                cmap=cmap,
                vmax=Z_plot.max() if Z_plot.max() / Z_plot.min() < 256 else Z_plot.max() / 50,
                shading="auto",
            )

            # For contour extraction, create grid centers and prepare Z accordingly
            # Bin edges are Xc, Yc; compute bin centers for the function
            Xc = 0.5 * (Xc[:-1] + Xc[1:])
            Yc = 0.5 * (Yc[:-1] + Yc[1:])
            Z = Z_plot  # Use transposed Z with shape (ny, nx)

        elif traces_to_plot.x_label == "UnitInterval":
            xc, yc, zc = (
                traces_to_plot.cartesian_data[0],
                traces_to_plot.cartesian_data[1],
                traces_to_plot.cartesian_data[2],
            )
            minz = min(zc[np.where(zc > 0)])
            minx = min(xc)
            maxx = max(xc)
            miny = min(yc)
            maxy = max(yc)
            grid_size = 300
            if is_contour and filter_colormap:
                mask = zc < filter_colormap
                zc = zc[mask]
                yc = yc[mask]
                xc = xc[mask]
                grid_size = 100
            Xc, Yc, Z = bin_to_grid(xc, yc, zc, nx=grid_size, ny=grid_size)
            if is_contour:
                mesh = self.ax.pcolormesh(Xc, Yc, Z, norm=LogNorm(), shading="auto", cmap="nipy_spectral")
                cbar = self.fig.colorbar(mesh, ax=self.ax)
                cbar.ax.tick_params(labelsize=self.text_size, colors=self.__grid_color)
            else:
                cmap = plt.cm.nipy_spectral
                cmap.set_under(self.__general_plot_color)

                Z = np.ma.masked_less(Z, minz)
                self.ax.pcolormesh(Xc, Yc, Z, cmap=cmap)
            self.ax.set_xlim(minx, maxx)  # set X axis min and max
            self.ax.set_ylim(miny, maxy)  # set Y axis min and max
        else:
            return False

        if self._eye_mask and plot_eye_mask:
            px = [i[0] for i in self._eye_mask.eye_points]
            py = [i[1] for i in self._eye_mask.eye_points]
            eye_center = [np.mean(px), np.mean(py)]
            if not is_contour:
                contour = extract_eye_opening_contour_by_center(
                    Xc,
                    Yc,
                    Z,
                    center=eye_center,
                )
                # contour = prepare_and_extract(xc, yc, zc, center=eye_center, nx=500, ny=500)
                if contour.any():
                    eye_center = [float(np.mean(contour[:, 0])), float(np.mean(contour[:, 1]))]
                    ymaxidx = np.argmax(contour[:, 1])
                    yminidx = np.argmin(contour[:, 1])
                    xmaxidx = np.argmax(contour[:, 0])
                    xminidx = np.argmin(contour[:, 0])
                    eye_height = contour[:, 1][ymaxidx] - contour[:, 1][yminidx]
                    eye_width = contour[:, 0][xmaxidx] - contour[:, 0][xminidx]
                    settings.logger.info(f"Computed Eye Center {eye_center}")
                    settings.logger.info(f"Computed Eye Height {eye_height}")
                    settings.logger.info(f"Computed Eye Width {eye_width}")
                    self.ax.plot(
                        contour[:, 0],
                        contour[:, 1],
                        "r-",
                        lw=2,
                    )
                    if plot_max_height:
                        idx_max = np.argmax(contour[:, 1])
                        max_height = contour[:, 1][idx_max]
                        x_at_max = contour[:, 0][idx_max]

                        self.ax.axvline(x=x_at_max, color="yellow", linestyle="dashdot", label=f"{x_at_max}")
                        self.ax.axhline(y=max_height, color="yellow", linestyle="dashdot", label=f"{max_height}")

            if px and py:
                vertices = list(zip(px, py))

                # Close polygon by repeating the first point at the end
                vertices.append(vertices[0])

                # Define path codes: MOVETO, LINETO ... CLOSEPOLY
                codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]

                # Create the Path and PathPatch
                path = Path(vertices, codes)
                patch = PathPatch(
                    path, color=[i / 255 for i in self._eye_mask.eye_color], alpha=self._eye_mask.eye_transparency
                )
                self.ax.add_patch(patch)
            if self._eye_mask.eye_enable:
                if self._eye_mask.eye_upper < max(Yc):
                    px = [min(Xc), max(Xc), max(Xc), min(Xc)]
                    py = [self._eye_mask.eye_upper, self._eye_mask.eye_upper, max(Yc), max(Yc)]
                    vertices = list(zip(px, py))

                    # Close polygon by repeating the first point at the end
                    vertices.append(vertices[0])

                    # Define path codes: MOVETO, LINETO ... CLOSEPOLY
                    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]

                    # Create the Path and PathPatch
                    path = Path(vertices, codes)
                    patch = PathPatch(
                        path,
                        color=[i / 255 for i in self._eye_mask.eye_color],
                        alpha=self._eye_mask.eye_transparency,
                    )
                    self.ax.add_patch(patch)
                if self._eye_mask.eye_lower > min(Yc):
                    px = [min(Xc), max(Xc), max(Xc), min(Xc)]
                    py = [self._eye_mask.eye_lower, self._eye_mask.eye_lower, min(Yc), min(Yc)]
                    vertices = list(zip(px, py))

                    # Close polygon by repeating the first point at the end
                    vertices.append(vertices[0])

                    # Define path codes: MOVETO, LINETO ... CLOSEPOLY
                    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]

                    # Create the Path and PathPatch
                    path = Path(vertices, codes)
                    patch = PathPatch(
                        path,
                        color=[i / 255 for i in self._eye_mask.eye_color],
                        alpha=self._eye_mask.eye_transparency,
                    )
                    self.ax.add_patch(patch)

        self.ax.set_xlabel(
            f"Unit Interval ({self._eye_mask.eye_xunits})'", color=self.__grid_color, fontsize=self.text_size
        )
        self.ax.set_ylabel(f"Amplitude ({self._eye_mask.eye_yunits})", color=self.__grid_color, fontsize=self.text_size)
        self.ax.set_title(
            "Statistical Eye Diagram" if not is_contour else "Contour Eye Diagram",
            color=self.__grid_color,
            fontsize=self.title_size,
        )

        self._plot(snapshot_path, show)

    @pyaedt_function_handler()
    def _plot_notes(self) -> None:
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
    def _plot_limit_lines(self, convert_to_radians: bool = False):
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
        trace: int = 0,
        polar: bool = False,
        levels: int = 64,
        max_theta: int = 360,
        min_theta: int = 0,
        color_bar: str = None,
        snapshot_path: str = None,
        show: bool = True,
        figure: plt.Figure = None,
        is_spherical: bool = True,
        normalize: list = None,
    ) -> plt.Figure | bool:
        """Create a Matplotlib figure contour based on a list of data.

        Parameters
        ----------
        trace : int, str, optional
            Trace index on which create the 3D Plot.
        polar : bool, optional
            Generate the plot in polar coordinates. The default is ``True``. If ``False``, the plot
            generated is rectangular.
        levels : int, optional
            Number of color map levels. The default is ``64``.
        max_theta : float or int, optional
            Maximum theta angle for plotting polar data.
            The default is ``360``.
        min_theta : float or int, optional
            Minimum theta angle for plotting polar data. The default is ``0``.
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
        if "Bit Error Rate" in tr.name:
            return self.plot_eye_diagram(snapshot_path=snapshot_path, show=show, is_contour=True)
        projection = "polar" if polar else "rectilinear"

        if not figure:
            self.fig, self.ax = plt.subplots(subplot_kw={"projection": projection})
            self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
            self.ax = plt.gca()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, polar=polar)

        self.ax.set_xlabel(tr.x_label, color=self.__grid_color, fontsize=self.text_size)
        if polar:
            self.ax.set_rticks(np.linspace(min_theta, max_theta, 3))
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            self.ax.set_thetamin(min_theta)
            self.ax.set_thetamax(max_theta)
        else:
            self.ax.set_ylabel(tr.y_label, color=self.__grid_color, fontsize=self.text_size)

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
        trace: int = 0,
        color_bar: str = None,
        snapshot_path: str = None,
        show: bool = True,
        figure: plt.Figure = None,
    ) -> plt.Figure | bool:
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
            self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
            self.ax = plt.gca()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, polar=False)

        self.ax.set_xlabel(tr.x_label, color=self.__grid_color, fontsize=self.text_size)
        self.ax.set_ylabel(tr.y_label, color=self.__grid_color, fontsize=self.text_size)

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
        trace: int = 0,
        polar: bool = False,
        levels: int = 64,
        max_theta: int = 180,
        min_theta: int = 0,
        color_bar: str = None,
        snapshot_path: str = None,
        show: bool = True,
        figure: plt.Figure = None,
        is_spherical: bool = True,
        normalize: list = None,
    ) -> plt.Figure | bool:
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
            self.fig.set_size_inches(self.width / self.dpi, self.height / self.dpi)
            self.ax = plt.gca()
        else:
            self.fig = figure
            self.ax = figure.add_subplot(111, polar=polar)

        def update(i):
            self.ax.clear()
            trace = traces_to_plot[i]
            self.ax.set_xlabel(trace.x_label, color=self.__grid_color, fontsize=self.text_size)
            if polar:
                self.ax.set_rticks(np.linspace(min_theta, max_theta, 3))
                self.ax.set_theta_zero_location("N")
                self.ax.set_theta_direction(-1)
                self.ax.set_thetamin(min_theta)
                self.ax.set_thetamax(max_theta)
            else:
                self.ax.set_ylabel(trace.y_label, color=self.__grid_color, fontsize=self.text_size)

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
def plot_matplotlib(
    plot_data: list | str,
    size: tuple = (1920, 1440),
    show_legend: bool = True,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    snapshot_path: str = None,
    x_limits: list = None,
    y_limits: list = None,
    axis_equal: bool = False,
    annotations: list = None,
    show: bool = True,
) -> plt.Figure:  # pragma: no cover
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
        plt.savefig(snapshot_path, dpi=dpi)
    if show:  # pragma: no cover
        plt.show()
    return fig
