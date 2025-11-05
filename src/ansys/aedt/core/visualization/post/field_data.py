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

from abc import abstractmethod
from collections import defaultdict
import csv
import os
import shutil
import sys
import tempfile
import warnings

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import AllowedMarkers
from ansys.aedt.core.generic.constants import EnumUnits
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import check_and_download_file
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.internal.load_aedt_file import load_keyword_in_aedt_file
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    warnings.warn(
        "The Pandas module is required to run functionalities of ansys.aedt.core.visualization.post.field_data.\n"
        "Install with \n"
        """>> pip install pandas"""
    )
    pd = None


class BaseFolderPlot(PyAedtBase):
    @abstractmethod
    def to_dict(self):
        """Convert the settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing settings.
        """

    @abstractmethod
    def from_dict(self, dictionary):
        """Initialize the settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration settings.
            Dictionary syntax must be the same of the AEDT file.
        """


class ColorMapSettings(BaseFolderPlot):
    """Provides methods and variables for editing color map folder settings.

    Parameters
    ----------
    map_type : str, optional
        The type of colormap to use. Must be one of the allowed types
        (`"Spectrum"`, `"Ramp"`, `"Uniform"`).
        Default is `"Spectrum"`.
    color : str or list[float], optional
        Color to use. If "Spectrum" color map, a string is expected.
        Else a list of 3 values (R,G,B). Default is `"Rainbow"`.
    """

    def __init__(self, map_type="Spectrum", color="Rainbow"):
        self._map_type = None
        self.map_type = map_type

        # Default color settings
        self._color_spectrum = "Rainbow"
        self._color_ramp = [255, 127, 127]
        self._color_uniform = [127, 255, 255]

        # User-provided color settings
        self.color = color

    @property
    def map_type(self):
        """Get the color map type for the field plot."""
        return self._map_type

    @map_type.setter
    def map_type(self, value):
        """Set the type of color mapping for the field plot.

        Parameters
        ----------
        value : str
            The type of mapping to set. Must be one of 'Spectrum', 'Ramp', or 'Uniform'.

        Raises
        ------
        ValueError
            If the provided `value` is not valid, raises a ``ValueError`` with an appropriate message.
        """
        if value not in ["Spectrum", "Ramp", "Uniform"]:
            raise ValueError(f"{value} is not valid. Only 'Spectrum', 'Ramp', and 'Uniform' are accepted.")
        self._map_type = value

    @property
    def color(self):
        """Get the color based on the map type.

        Returns
        -------
            str or list of float: The color scheme based on the map type.
        """
        if self.map_type == "Spectrum":
            return self._color_spectrum
        elif self.map_type == "Ramp":
            return self._color_ramp
        elif self.map_type == "Uniform":
            return self._color_uniform

    @color.setter
    def color(self, v):
        """Set the colormap based on the map type.

        Parameters
        ----------
        v : str or list[float]
            The color value to be set. If a string, it should represent a valid color
            spectrum specification (`"Magenta"`, `"Rainbow"`, `"Temperature"` or `"Gray"`).
            If a tuple, it should contain three elements representing RGB values.

        Raises
        ------
            ValueError: If the provided color value is not valid for the specified map type.
        """
        if self.map_type == "Spectrum":
            self._validate_color_spectrum(v)
            if v == "Magenta":
                v = "Megenta"
            self._color_spectrum = v
        else:
            self._validate_color(v)
            if self.map_type == "Ramp":
                self._color_ramp = v
            else:
                self._color_uniform = v

    @staticmethod
    def _validate_color_spectrum(value):
        if value not in ["Magenta", "Rainbow", "Temperature", "Grayscale"]:
            raise ValueError(
                f"{value} is not valid. Only 'Magenta', 'Rainbow', 'Temperature', and 'Grayscale' are accepted."
            )

    @staticmethod
    def _validate_color(value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError(f"{value} is not valid. Three values (R, G, B) must be passed.")

    def __repr__(self):
        color_repr = self.color
        return f"ColorMapSettings(map_type='{self.map_type}', color={color_repr})"

    def to_dict(self):
        """Convert the color map settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the color map settings
            for the folder field plot settings.
        """
        return {
            "ColorMapSettings": {
                "ColorMapType": self.map_type,
                {"Spectrum": "SpectrumType", "Uniform": "UniformColor", "Ramp": "RampColor"}[self.map_type]: self.color,
            }
        }

    def from_dict(self, settings):
        """Initialize the number format settings of the colormap settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for colormap settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self._map_type = settings["ColorMapType"]
        self._color_spectrum = settings["SpectrumType"]
        self._color_ramp = settings["RampColor"]
        self._color_uniform = settings["UniformColor"]


class AutoScale(BaseFolderPlot):
    """Provides methods and variables for editing automatic scale folder settings.

    Parameters
    ----------
    n_levels : int, optional
        Number of color levels of the scale. Default is `10`.
    limit_precision_digits : bool, optional
        Whether to limit precision digits. Default is `False`.
    precision_digits : int, optional
        Precision digits. Default is `3`.
    use_current_scale_for_animation : bool, optional
        Whether to use the scale for the animation. Default is `False`.
    """

    def __init__(
        self, n_levels=10, limit_precision_digits=False, precision_digits=3, use_current_scale_for_animation=False
    ):
        self.n_levels = n_levels
        self.limit_precision_digits = limit_precision_digits
        self.precision_digits = precision_digits
        self.use_current_scale_for_animation = use_current_scale_for_animation

    def __repr__(self):
        return (
            f"AutoScale(n_levels={self.n_levels}, "
            f"limit_precision_digits={self.limit_precision_digits}, "
            f"precision_digits={self.precision_digits}, "
            f"use_current_scale_for_animation={self.use_current_scale_for_animation})"
        )

    def to_dict(self):
        """Convert the auto-scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the auto-scale settings
            for the folder field plot settings.
        """
        return {
            "m_nLevels": self.n_levels,
            "LimitFieldValuePrecision": self.limit_precision_digits,
            "FieldValuePrecisionDigits": self.precision_digits,
            "AnimationStaticScale": self.use_current_scale_for_animation,
        }

    def from_dict(self, dictionary):
        """Initialize the auto-scale settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for auto-scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.n_levels = dictionary["m_nLevels"]
        self.limit_precision_digits = dictionary["LimitFieldValuePrecision"]
        self.precision_digits = dictionary["FieldValuePrecisionDigits"]
        self.use_current_scale_for_animation = dictionary["AnimationStaticScale"]


class MinMaxScale(BaseFolderPlot):
    """Provides methods and variables for editing min-max scale folder settings.

    Parameters
    ----------
    n_levels : int, optional
        Number of color levels of the scale. Default is `10`.
    min_value : float, optional
        Minimum value of the scale. Default is `0`.
    max_value : float, optional
        Maximum value of the scale. Default is `1`.
    """

    def __init__(self, n_levels=10, min_value=0, max_value=1):
        self.n_levels = n_levels
        self.min_value = min_value
        self.max_value = max_value

    def __repr__(self):
        return f"MinMaxScale(n_levels={self.n_levels}, min_value={self.min_value}, max_value={self.max_value})"

    def to_dict(self):
        """Convert the min-max scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the min-max scale settings
            for the folder field plot settings.
        """
        return {"minvalue": self.min_value, "maxvalue": self.max_value, "m_nLevels": self.n_levels}

    def from_dict(self, dictionary):
        """Initialize the min-max scale settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for min-max scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.min_value = dictionary["minvalue"]
        self.max_value = dictionary["maxvalue"]
        self.n_levels = dictionary["m_nLevels"]


class SpecifiedScale(PyAedtBase):
    """Provides methods and variables for editing min-max scale folder settings.

    Parameters
    ----------
    scale_values : int, optional
        Scale levels. Default is `None`.
    """

    def __init__(self, scale_values=None):
        if scale_values is None:
            scale_values = []
        if not isinstance(scale_values, list):
            raise ValueError("scale_values must be a list.")
        self.scale_values = scale_values

    def __repr__(self):
        return f"SpecifiedScale(scale_values={self.scale_values})"

    def to_dict(self):
        """Convert the specified scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the specified scale settings
            for the folder field plot settings.
        """
        return {"UserSpecifyValues": [len(self.scale_values)] + self.scale_values}

    def from_dict(self, dictionary):
        """Initialize the specified scale settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for specified scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.scale_values = dictionary["UserSpecifyValues"][:-1]


class NumberFormat(BaseFolderPlot):
    """Provides methods and variables for editing number format folder settings.

    Parameters
    ----------
    format_type : int, optional
        Scale levels. Default is `None`.
    width : int, optional
        Width of the numbers space. Default is `4`.
    precision : int, optional
        Precision of the numbers. Default is `4`.
    """

    def __init__(self, format_type="Automatic", width=4, precision=4):
        self._format_type = format_type
        self.width = width
        self.precision = precision
        self._accepted = ["Automatic", "Scientific", "Decimal"]

    @property
    def format_type(self):
        """Get the current number format type."""
        return self._format_type

    @format_type.setter
    def format_type(self, v):
        """Set the numeric format type of the scale.

        Parameters
        ----------
        v (str): The new format type to be set. Must be one of the accepted values
            ("Automatic", "Scientific" or "Decimal").

        Raises
        ------
        ValueError: If the provided value is not in the list of accepted values.
        """
        if v is not None and v in self._accepted:
            self._format_type = v
        else:
            raise ValueError(f"{v} is not valid. Accepted values are {', '.join(self._accepted)}.")

    def __repr__(self):
        return f"NumberFormat(format_type={self.format_type}, width={self.width}, precision={self.precision})"

    def to_dict(self):
        """Convert the number format settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the number format settings
            for the folder field plot settings.
        """
        return {
            "ValueNumberFormatTypeAuto": self._accepted.index(self.format_type),
            "ValueNumberFormatTypeScientific": self.format_type == "Scientific",
            "ValueNumberFormatWidth": self.width,
            "ValueNumberFormatPrecision": self.precision,
        }

    def from_dict(self, dictionary):
        """Initialize the number format settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for number format settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self._format_type = self._accepted[dictionary["ValueNumberFormatTypeAuto"]]
        self.width = dictionary["ValueNumberFormatWidth"]
        self.precision = dictionary["ValueNumberFormatPrecision"]


class Scale3DSettings(BaseFolderPlot):
    """Provides methods and variables for editing scale folder settings.

    Parameters
    ----------
    scale_type : str, optional
        Scale type. Default is `"Auto"`.
    scale_settings : :class:`ansys.aedt.core.modules.post_general.AutoScale`,
                     :class:`ansys.aedt.core.modules.post_general.MinMaxScale` or
                     :class:`ansys.aedt.core.modules.post_general.SpecifiedScale`, optional
        Scale settings. Default is `AutoScale()`.
    log : bool, optional
        Whether to use a log scale. Default is `False`.
    db : bool, optional
        Whether to use dB scale. Default is `False`.
    unit : int, optional
        Unit to use in the scale. Default is `None`.
    number_format : :class:`ansys.aedt.core.modules.post_general.NumberFormat`, optional
        Number format settings. Default is `NumberFormat()`.
    """

    def __init__(
        self,
        scale_type="Auto",
        scale_settings=AutoScale(),
        log=False,
        db=False,
        unit=None,
        number_format=NumberFormat(),
    ):
        self._scale_type = None  # Initialize with None to use the setter for validation
        self._scale_settings = None
        self._unit = None
        self._auto_scale = AutoScale()
        self._minmax_scale = MinMaxScale()
        self._specified_scale = SpecifiedScale()
        self._accepted = ["Auto", "MinMax", "Specified"]
        self.number_format = number_format
        self.log = log
        self.db = db
        self.unit = unit
        self.scale_type = scale_type  # This will trigger the setter and validate the scale_type
        self.scale_settings = scale_settings

    @property
    def unit(self):
        """Get unit used in the plot."""
        return EnumUnits(self._unit).name

    @unit.setter
    def unit(self, v):
        """Set unit used in the plot.

        Parameters
        ----------
        v: str
            Unit to be set.
        """
        if v is not None:
            try:
                self._unit = EnumUnits[v].value
            except KeyError:
                raise KeyError(f"{v} is not a valid unit.")

    @property
    def scale_type(self):
        """Get type of scale used for the field plot."""
        return self._scale_type

    @scale_type.setter
    def scale_type(self, value):
        """Set the scale type used for the field plot.

        Parameters
        ----------
            value : str
                The type of scaling to set.
                Must be one of the accepted values ("Auto", "MinMax" or "Specified").

        Raises
        ------
            ValueError
               If the provided value is not in the list of accepted values.
        """
        if value is not None and value not in self._accepted:
            raise ValueError(f"{value} is not valid. Accepted values are {', '.join(self._accepted)}.")
        self._scale_type = value
        # Automatically adjust scale_settings based on scale_type
        if value == "Auto":
            self._scale_settings = self._auto_scale
        elif value == "MinMax":
            self._scale_settings = self._minmax_scale
        elif value == "Specified":
            self._scale_settings = self._specified_scale

    @property
    def scale_settings(self):
        """Get the current scale settings based on the scale type."""
        self.scale_type = self.scale_type  # update correct scale settings
        return self._scale_settings

    @scale_settings.setter
    def scale_settings(self, value):
        """Set the current scale settings based on the scale type."""
        if self.scale_type == "Auto":
            if isinstance(value, AutoScale):
                self._scale_settings = value
                return
        elif self.scale_type == "MinMax":
            if isinstance(value, MinMaxScale):
                self._scale_settings = value
                return
        elif self.scale_type == "Specified":
            if isinstance(value, SpecifiedScale):
                self._scale_settings = value
                return
        raise ValueError("Invalid scale settings for current scale type.")

    def __repr__(self):
        return (
            f"Scale3DSettings(scale_type='{self.scale_type}', scale_settings={self.scale_settings}, "
            f"log={self.log}, db={self.db})"
        )

    def to_dict(self):
        """Convert the scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all scale settings
            for the folder field plot settings.
        """
        arg_out = {
            "Scale3DSettings": {
                "unit": self._unit,
                "ScaleType": self._accepted.index(self.scale_type),
                "log": self.log,
                "dB": self.db,
            }
        }
        arg_out["Scale3DSettings"].update(self.number_format.to_dict())
        arg_out["Scale3DSettings"].update(self.scale_settings.to_dict())
        return arg_out

    def from_dict(self, dictionary):
        """Initialize the scale settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self._scale_type = self._accepted[dictionary["ScaleType"]]
        self.number_format = NumberFormat()
        self.number_format.from_dict(dictionary)
        self.log = dictionary["log"]
        self.db = dictionary["dB"]
        self.unit = EnumUnits(int(dictionary["unit"])).name
        self._auto_scale = AutoScale()
        self._auto_scale.from_dict(dictionary)
        self._minmax_scale = MinMaxScale()
        self._minmax_scale.from_dict(dictionary)
        self._specified_scale = SpecifiedScale()
        self._specified_scale.from_dict(dictionary)


class MarkerSettings(BaseFolderPlot):
    """Provides methods and variables for editing marker folder settings.

    Parameters
    ----------
    marker_type : str, optional
        The type of maker to use. Must be one of the allowed types
        (`"Octahedron"`, `"Tetrahedron"`, `"Sphere"`, `"Box"`, `"Arrow"`).
        Default is `"Box"`.
    marker_size : float, optional
        Size of the marker. Default is `0.005`.
    map_size : bool, optional
        Whether to map the field magnitude to the arrow type. Default is `False`.
    map_color : bool, optional
        Whether to map the field magnitude to the arrow color. Default is `True`.
    """

    def __init__(self, marker_type="Box", map_size=False, map_color=True, marker_size=0.005):
        self._marker_type = None
        self.marker_type = marker_type
        self.map_size = map_size
        self.map_color = map_color
        self.marker_size = marker_size

    @property
    def marker_type(self):
        """Get the type of maker to use."""
        return AllowedMarkers(self._marker_type).name

    @marker_type.setter
    def marker_type(self, v):
        """Set the type of maker to use.

        Parameters
        ----------
        v : str
            Marker type. Must be one of the allowed types
            (`"Octahedron"`, `"Tetrahedron"`, `"Sphere"`, `"Box"`, `"Arrow"`).
        """
        try:
            self._marker_type = AllowedMarkers[v].value
        except KeyError:
            raise KeyError(f"{v} is not a valid marker type.")

    def __repr__(self):
        return (
            f"MarkerSettings(marker_type='{self.marker_type}', map_size={self.map_size}, "
            f"map_color={self.map_color}, marker_size={self.marker_size})"
        )

    def to_dict(self):
        """Convert the marker settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the marker settings
            for the folder field plot settings.
        """
        return {
            "Marker3DSettings": {
                "MarkerType": self._marker_type,
                "MarkerMapSize": self.map_size,
                "MarkerMapColor": self.map_color,
                "MarkerSize": self.marker_size,
            }
        }

    def from_dict(self, dictionary):
        """Initialize the marker settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for marker settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.marker_type = AllowedMarkers(int(dictionary["MarkerType"])).name
        self.map_size = dictionary["MarkerMapSize"]
        self.map_color = dictionary["MarkerMapColor"]
        self.marker_size = dictionary["MarkerSize"]


class ArrowSettings(BaseFolderPlot):
    """Provides methods and variables for editing arrow folder settings.

    Parameters
    ----------
    arrow_type : str, optional
        The type of arrows to use. Must be one of the allowed types
        (`"Line"`, `"Cylinder"`, `"Umbrella"`). Default is `"Line"`.
    arrow_size : float, optional
        Size of the arrow. Default is `0.005`.
    map_size : bool, optional
        Whether to map the field magnitude to the arrow type. Default is `False`.
    map_color : bool, optional
        Whether to map the field magnitude to the arrow color. Default is `True`.
    show_arrow_tail : bool, optional
        Whether to show the arrow tail. Default is `False`.
    magnitude_filtering : bool, optional
        Whether to filter the field magnitude for plotting vectors. Default is `False`.
    magnitude_threshold : bool, optional
        Threshold value for plotting vectors. Default is `0`.
    min_magnitude : bool, optional
        Minimum value for plotting vectors. Default is `0`.
    max_magnitude : bool, optional
        Maximum value for plotting vectors. Default is `0.5`.
    """

    def __init__(
        self,
        arrow_type="Line",
        arrow_size=0.005,
        map_size=False,
        map_color=True,
        show_arrow_tail=False,
        magnitude_filtering=False,
        magnitude_threshold=0,
        min_magnitude=0,
        max_magnitude=0.5,
    ):
        self._arrow_type = None
        self._allowed_arrow_types = ["Line", "Cylinder", "Umbrella"]
        self.arrow_type = arrow_type
        self.arrow_size = arrow_size
        self.map_size = map_size
        self.map_color = map_color
        self.show_arrow_tail = show_arrow_tail
        self.magnitude_filtering = magnitude_filtering
        self.magnitude_threshold = magnitude_threshold
        self.min_magnitude = min_magnitude
        self.max_magnitude = max_magnitude

    @property
    def arrow_type(self):
        """Get the type of arrows used in the field plot."""
        return self._arrow_type

    @arrow_type.setter
    def arrow_type(self, v):
        """Set the type of arrows for the field plot.

        Parameters
        ----------
            v : str
                The type of arrows to use. Must be one of the allowed types ("Line", "Cylinder", "Umbrella").

        Raises
        ------
            ValueError
                If the provided value is not in the list of allowed arrow types.
        """
        if v in self._allowed_arrow_types:
            self._arrow_type = v
        else:
            raise ValueError(f"{v} is not valid. Accepted values are {','.join(self._allowed_arrow_types)}.")

    def __repr__(self):
        return (
            f"Arrow3DSettings(arrow_type='{self.arrow_type}', arrow_size={self.arrow_size}, "
            f"map_size={self.map_size}, map_color={self.map_color}, "
            f"show_arrow_tail={self.show_arrow_tail}, magnitude_filtering={self.magnitude_filtering}, "
            f"magnitude_threshold={self.magnitude_threshold}, min_magnitude={self.min_magnitude}, "
            f"max_magnitude={self.max_magnitude})"
        )

    def to_dict(self):
        """Convert the arrow settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the arrow settings
            for the folder field plot settings.
        """
        return {
            "Arrow3DSettings": {
                "ArrowType": self._allowed_arrow_types.index(self.arrow_type),
                "ArrowMapSize": self.map_size,
                "ArrowMapColor": self.map_color,  # Missing option in ui
                "ShowArrowTail": self.show_arrow_tail,
                "ArrowSize": self.arrow_size,
                "ArrowMinMagnitude": self.min_magnitude,
                "ArrowMaxMagnitude": self.max_magnitude,
                "ArrowMagnitudeThreshold": self.magnitude_threshold,
                "ArrowMagnitudeFilteringFlag": self.magnitude_filtering,
            }
        }

    def from_dict(self, dictionary):
        """Initialize the arrow settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for arrow settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.arrow_type = self._allowed_arrow_types[dictionary["ArrowType"]]
        self.arrow_size = dictionary["ArrowType"]
        self.map_size = dictionary["ArrowMapSize"]
        self.map_color = dictionary["ArrowMapColor"]
        self.show_arrow_tail = dictionary["ShowArrowTail"]
        self.magnitude_filtering = dictionary["ArrowMagnitudeFilteringFlag"]
        self.magnitude_threshold = dictionary["ArrowMagnitudeThreshold"]
        self.min_magnitude = dictionary["ArrowMinMagnitude"]
        self.max_magnitude = dictionary["ArrowMaxMagnitude"]


class FolderPlotSettings(BaseFolderPlot):
    """Provides methods and variables for editing field plots folder settings.

    Parameters
    ----------
    postprocessor : :class:`ansys.aedt.core.modules.post_general.PostProcessor`
    folder_name : str
        Name of the plot field folder.
    arrow_settings : :class:`ansys.aedt.core.modules.solution.ArrowSettings`, optional
        Arrow settings. Default is `None`.
    marker_settings : :class:`ansys.aedt.core.modules.solution.MarkerSettings`, optional
        Marker settings. Default is `None`.
    scale_settings : :class:`ansys.aedt.core.modules.solution.Scale3DSettings`, optional
        Scale settings. Default is `None`.
    color_map_settings : :class:`ansys.aedt.core.modules.solution.ColorMapSettings`, optional
        Colormap settings. Default is `None`.
    """

    def __init__(
        self,
        postprocessor,
        folder_name,
        arrow_settings=None,
        marker_settings=None,
        scale_settings=None,
        color_map_settings=None,
    ):
        self.arrow_settings = arrow_settings
        self.marker_settings = marker_settings
        self.scale_settings = scale_settings
        self.color_map_settings = color_map_settings
        self._postprocessor = postprocessor
        self._folder_name = folder_name

    def update(self):
        """Update folder plot settings."""
        out = []
        _dict2arg(self.to_dict(), out)
        self._postprocessor.ofieldsreporter.SetPlotFolderSettings(self._folder_name, out[0])

    def to_dict(self):
        """Convert the field plot settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the settings for the field plot,
            including arrow settings, marker settings,
            scale settings, and color map settings.
        """
        out = {}
        out.update(self.arrow_settings.to_dict())
        out.update(self.marker_settings.to_dict())
        out.update(self.scale_settings.to_dict())
        out.update(self.color_map_settings.to_dict())
        return {"FieldsPlotSettings": out}

    def from_dict(self, dictionary):
        """Initialize the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for the color map,
            scale, arrow, and marker settings. Dictionary syntax must
            be the same of the AEDT file.
        """
        cmap = ColorMapSettings()
        cmap.from_dict(dictionary["ColorMapSettings"])
        self.color_map_settings = cmap
        scale = Scale3DSettings()
        scale.from_dict(dictionary["Scale3DSettings"])
        self.scale_settings = scale
        arrow = ArrowSettings()
        arrow.from_dict(dictionary["Arrow3DSettings"])
        marker = MarkerSettings()
        marker.from_dict(dictionary["Marker3DSettings"])
        self.arrow_settings = arrow
        self.marker_settings = marker


class FieldPlot(PyAedtBase):
    """Provides for creating and editing field plots.

    Parameters
    ----------
    postprocessor : :class:`ansys.aedt.core.modules.post_general.PostProcessor`
    objects : list
        List of objects.
    solution : str
        Name of the solution.
    quantity : str
        Name of the plot or the name of the object.
    intrinsics : dict, optional
        Name of the intrinsic dictionary. The default is ``{}``.

    """

    @pyaedt_function_handler(
        objlist="objects",
        surfacelist="surfaces",
        linelist="lines",
        cutplanelist="cutplanes",
        solutionName="solution",
        quantityName="quantity",
        IntrinsincList="intrinsics",
        seedingFaces="seeding_faces",
        layers_nets="layer_nets",
        layers_plot_type="layer_plot_type",
    )
    def __init__(
        self,
        postprocessor,
        objects=None,
        surfaces=None,
        lines=None,
        cutplanes=None,
        solution="",
        quantity="",
        intrinsics=None,
        seeding_faces=None,
        layer_nets=None,
        layer_plot_type="LayerNetsExtFace",
    ):
        self._postprocessor = postprocessor
        self.oField = postprocessor.ofieldsreporter
        self.volumes = [] if objects is None else objects
        self.surfaces = [] if surfaces is None else surfaces
        self.lines = [] if lines is None else lines
        self.cutplanes = [] if cutplanes is None else cutplanes
        self.layer_nets = [] if layer_nets is None else layer_nets
        self.layer_plot_type = layer_plot_type
        self.seeding_faces = [] if seeding_faces is None else seeding_faces
        self.solution = solution
        self.quantity = quantity
        self.intrinsics = {} if intrinsics is None else intrinsics
        self.name = "Field_Plot"
        self.plot_folder = "Field_Plot"
        self.Filled = False
        self.IsoVal = "Fringe"
        self.SmoothShade = True
        self.AddGrid = False
        self.MapTransparency = True
        self.Refinement = 0
        self.Transparency = 0
        self.SmoothingLevel = 0
        self.ArrowUniform = True
        self.ArrowSpacing = 0
        self.MinArrowSpacing = 0
        self.MaxArrowSpacing = 0
        self.GridColor = [255, 255, 255]
        self.PlotIsoSurface = True
        self.PointSize = 1
        self.CloudSpacing = 0.5
        self.CloudMinSpacing = -1
        self.CloudMaxSpacing = -1
        self.LineWidth = 4
        self.LineStyle = "Cylinder"
        self.IsoValType = "Tone"
        self.NumofPoints = 100
        self.TraceStepLength = "0.001mm"
        self.UseAdaptiveStep = True
        self.SeedingSamplingOption = True
        self.SeedingPointsNumber = 15
        self.FractionOfMaximum = 0.8
        self._filter_boxes = []
        self.field_type = None
        self._folder_settings = None

    def _parse_folder_settings(self):
        """Parse the folder settings for the field plot from the AEDT file.

        Returns
        -------
            FolderPlotSettings or None: An instance of FolderPlotSettings if found, otherwise None.
        """
        folder_settings_data = load_keyword_in_aedt_file(
            self._postprocessor._app.project_file,
            "FieldsPlotManagerID",
            design_name=self._postprocessor._app.design_name,
        )
        relevant_settings = [
            d
            for d in folder_settings_data["FieldsPlotManagerID"].values()
            if isinstance(d, dict) and d.get("PlotFolder", False) and d["PlotFolder"] == self.plot_folder
        ]

        if not relevant_settings:
            self._postprocessor._app.logger.error(
                "Could not find settings data in the design properties."
                " Define the `FolderPlotSettings` class from scratch or save the project file and try again."
            )
            return None
        else:
            fps = FolderPlotSettings(self._postprocessor, self.plot_folder)
            fps.from_dict(relevant_settings[0])
            return fps

    @property
    def folder_settings(self):
        """Get the folder settings."""
        if self._folder_settings is None:
            self._folder_settings = self._parse_folder_settings()
        return self._folder_settings

    @folder_settings.setter
    def folder_settings(self, v):
        """Set the fieldplot folder settings.

        Parameters
        ----------
        v : FolderPlotSettings
            The new folder plot settings to be set.

        Raises
        ------
        ValueError
            If the provided value is not an instance of `FolderPlotSettings`.
        """
        if isinstance(v, FolderPlotSettings):
            self._folder_settings = v
        else:
            raise ValueError("Invalid type for `folder_settings`, use `FolderPlotSettings` class.")

    @property
    def filter_boxes(self):
        """Volumes on which filter the plot."""
        return self._filter_boxes

    @filter_boxes.setter
    def filter_boxes(self, val):
        if isinstance(val, str):
            val = [val]
        self._filter_boxes = val

    @property
    def plotGeomInfo(self):
        """Plot geometry information."""
        idx = 0
        if self.volumes:
            idx += 1
        if self.surfaces:
            idx += 1
        if self.cutplanes:
            idx += 1
        if self.lines:
            idx += 1
        if self.layer_nets:
            idx += 1

        info = [idx]
        if self.volumes:
            info.append("Volume")
            info.append("ObjList")
            info.append(len(self.volumes))
            for index in self.volumes:
                info.append(str(index))
        if self.surfaces:
            model_faces = []
            nonmodel_faces = []
            if self._postprocessor._app.design_type == "HFSS 3D Layout Design":
                model_faces = [str(i) for i in self.surfaces]
            else:
                models = self._postprocessor._app.modeler.model_objects
                for index in self.surfaces:
                    try:
                        if isinstance(index, FacePrimitive):
                            index = index.id
                        oname = self._postprocessor._app.modeler.oeditor.GetObjectNameByFaceID(index)
                        if oname in models:
                            model_faces.append(str(index))
                        else:
                            nonmodel_faces.append(str(index))
                    except Exception:
                        self._postprocessor.logger.debug(f"Something went wrong while processing surface {index}.")
            info.append("Surface")
            if model_faces:
                info.append("FacesList")
                info.append(len(model_faces))
                for index in model_faces:
                    info.append(index)
            if nonmodel_faces:
                info.append("NonModelFaceList")
                info.append(len(nonmodel_faces))
                for index in nonmodel_faces:
                    info.append(index)
        if self.cutplanes:
            info.append("Surface")
            info.append("CutPlane")
            info.append(len(self.cutplanes))
            for index in self.cutplanes:
                info.append(str(index))
        if self.lines:
            info.append("Line")
            info.append(len(self.lines))
            for index in self.lines:
                info.append(str(index))
        if self.layer_nets:
            if self.layer_plot_type == "LayerNets":
                info.append("Volume")
                info.append("LayerNets")
            else:
                info.append("Surface")
                info.append("LayerNetsExtFace")
            info.append(len(self.layer_nets))
            for index in self.layer_nets:
                info.append(index[0])
                info.append(len(index[1:]))
                info.extend(index[1:])
        return info

    @property
    def intrinsicVar(self):
        """Intrinsic variable.

        Returns
        -------
        list or dict
            Variables for the field plot.
        """
        var = ""
        for a in self.intrinsics:
            var += a + "='" + str(self.intrinsics[a]) + "' "
        return var

    @property
    def plotsettings(self):
        """Plot settings.

        Returns
        -------
        list
            List of plot settings.
        """
        if self.surfaces or self.cutplanes or (self.layer_nets and self.layer_plot_type == "LayerNetsExtFace"):
            if self.quantity == "Flux_Lines":
                self.IsoVal = "Line"
            arg = [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=",
                self.Filled,
                "IsoValType:=",
                self.IsoVal,
                "SmoothShade:=",
                self.SmoothShade,
                "AddGrid:=",
                self.AddGrid,
                "MapTransparency:=",
                self.MapTransparency,
                "Refinement:=",
                self.Refinement,
                "Transparency:=",
                self.Transparency,
                "SmoothingLevel:=",
                self.SmoothingLevel,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
                "GridColor:=",
                self.GridColor,
            ]
        elif self.lines:
            arg = [
                "NAME:PlotOnLineSettings",
                ["NAME:LineSettingsID", "Width:=", self.LineWidth, "Style:=", self.LineStyle],
                "IsoValType:=",
                self.IsoValType,
                "ArrowUniform:=",
                self.ArrowUniform,
                "NumofArrow:=",
                self.NumofPoints,
                "Refinement:=",
                self.Refinement,
            ]
        else:
            arg = [
                "NAME:PlotOnVolumeSettings",
                "PlotIsoSurface:=",
                self.PlotIsoSurface,
                "PointSize:=",
                self.PointSize,
                "Refinement:=",
                self.Refinement,
                "CloudSpacing:=",
                self.CloudSpacing,
                "CloudMinSpacing:=",
                self.CloudMinSpacing,
                "CloudMaxSpacing:=",
                self.CloudMaxSpacing,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
            ]
        return arg

    @pyaedt_function_handler()
    def get_points_value(self, points, filename=None, visibility=False):  # pragma: no cover
        """
        Get points data from field plot.

        .. note::
           This method is working only if the associated field plot is currently visible.

        .. note::
           This method does not work in non-graphical mode.

        Parameters
        ----------
        points : list, list of lists or dict
            List with [x,y,z] coordinates of a point or list of lists of points or
            dictionary with keys containing point names and for each key the point
            coordinates [x,y,z].
        filename : str or pathlib.Path, optional
            Full path or relative path with filename.
            Default is ``None`` in which case no file is exported.
        visibility : bool, optional
            Whether to keep the markers visible in the UI. Default is ``False``.

        Returns
        -------
        dict or pd.DataFrame
            Dict containing 5 keys: point names, x,y,z coordinates and the quantity probed.
            Each key is associated with a list with the same length of the argument points.
            If pandas is installed, the output is a pandas DataFrame with point names as
            index and coordinates and quantity as columns.
        """
        self.oField.ClearAllMarkers()

        # Clean inputs
        if isinstance(points, dict):
            points_name, points_value = list(points.keys()), list(points.values())
        elif isinstance(points, list):
            points_name = None
            if not isinstance(points[0], list):
                points_value = [points]
            else:
                points_value = points
        else:
            raise AttributeError("``points`` argument is invalid.")

        # Convert pathlib.Path to string if needed
        if filename is not None and hasattr(filename, "__fspath__"):
            filename = str(filename)

        if filename is not None:
            if not os.path.isdir(os.path.dirname(filename)):
                raise AttributeError(f"Specified path ({filename}) does not exist")

        # Create markers
        u = self._postprocessor._app.modeler.model_units
        added_points_name = []
        for pt_name_idx, pt in enumerate(points_value):
            try:
                pt = [c if isinstance(c, str) else f"{c}{u}" for c in pt]
                self.oField.AddMarkerToPlot(pt, self.name)
                if points_name is not None:
                    added_points_name.append(points_name[pt_name_idx])
            except (GrpcApiError, SystemExit) as e:  # pragma: no cover
                self._postprocessor.logger.error(f"Point {str(pt)} not added. Check if it lies inside the plot.")
                raise e

        # Export data
        temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv")
        temp_file.close()
        self.oField.ExportMarkerTable(temp_file.name)
        with open_file(temp_file.name, "r") as f:
            reader = csv.DictReader(f)
            out_dict = defaultdict(list)
            for row in reader:
                for key in row.keys():
                    if key == "Name":
                        val = row[key]
                    else:
                        val = float(row[key].lstrip())
                    out_dict[key.lstrip()].append(val)

        # Modify data if needed
        if points_name is not None:
            out_dict["Name"] = added_points_name
            # Export data
            if filename is not None:
                with open(filename, mode="w") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=out_dict.keys())
                    writer.writeheader()
                    for i in range(len(out_dict["Name"])):
                        row = {field: out_dict[field][i] for field in out_dict}
                        writer.writerow(row)
        elif filename is not None:
            # Export data
            shutil.copy2(temp_file.name, filename)
        os.remove(temp_file.name)

        if not visibility:
            self.oField.ClearAllMarkers()

        # Convert to pandas
        if pd is not None:
            df = pd.DataFrame(out_dict, columns=out_dict.keys())
            df = df.set_index("Name")
            return df
        else:
            return out_dict

    @property
    def surfacePlotInstruction(self):
        """Surface plot settings.

        Returns
        -------
        list
            List of surface plot settings.
        """
        out = [
            "NAME:" + self.name,
            "SolutionName:=",
            self.solution,
            "QuantityName:=",
            self.quantity,
            "PlotFolder:=",
            self.plot_folder,
        ]
        if self.field_type:
            out.extend(["FieldType:=", self.field_type])
        out.extend(
            [
                "UserSpecifyName:=",
                1,
                "UserSpecifyFolder:=",
                1,
                "StreamlinePlot:=",
                False,
                "AdjacentSidePlot:=",
                False,
                "FullModelPlot:=",
                False,
                "IntrinsicVar:=",
                self.intrinsicVar,
                "PlotGeomInfo:=",
                self.plotGeomInfo,
                "FilterBoxes:=",
                [len(self.filter_boxes)] + self.filter_boxes,
                self.plotsettings,
                "EnableGaussianSmoothing:=",
                False,
                "SurfaceOnly:=",
                True if self.surfaces or self.cutplanes else False,
            ]
        )
        return out

    @property
    def surfacePlotInstructionLineTraces(self):
        """Surface plot settings for field line traces.

        ..note::
            ``Specify seeding points on selections`` is by default set to ``by sampling``.

        Returns
        -------
        list
            List of plot settings for line traces.
        """
        out = [
            "NAME:" + self.name,
            "SolutionName:=",
            self.solution,
            "UserSpecifyName:=",
            0,
            "UserSpecifyFolder:=",
            0,
            "QuantityName:=",
            "QuantityName_FieldLineTrace",
            "PlotFolder:=",
            self.plot_folder,
        ]
        if self.field_type:
            out.extend(["FieldType:=", self.field_type])
        out.extend(
            [
                "IntrinsicVar:=",
                self.intrinsicVar,
                "Trace Step Length:=",
                self.TraceStepLength,
                "Use Adaptive Step:=",
                self.UseAdaptiveStep,
                "Seeding Faces:=",
                self.seeding_faces,
                "Seeding Markers:=",
                [0],
                "Surface Tracing Objects:=",
                self.surfaces,
                "Volume Tracing Objects:=",
                self.volumes,
                "Seeding Sampling Option:=",
                self.SeedingSamplingOption,
                "Seeding Points Number:=",
                self.SeedingPointsNumber,
                "Fractional of Maximal:=",
                self.FractionOfMaximum,
                "Discrete Seeds Option:=",
                "Marker Point",
                [
                    "NAME:InceptionEvaluationSettings",
                    "Gas Type:=",
                    0,
                    "Gas Pressure:=",
                    1,
                    "Use Inception:=",
                    True,
                    "Potential U0:=",
                    0,
                    "Potential K:=",
                    0,
                    "Potential A:=",
                    1,
                ],
                self.field_line_trace_plot_settings,
            ]
        )
        return out

    @property
    def field_plot_settings(self):
        """Field Plot Settings.

        Returns
        -------
        list
            Field Plot Settings.
        """
        return [
            "NAME:FieldsPlotItemSettings",
            [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=",
                self.Filled,
                "IsoValType:=",
                self.IsoVal,
                "AddGrid:=",
                self.AddGrid,
                "MapTransparency:=",
                self.MapTransparency,
                "Refinement:=",
                self.Refinement,
                "Transparency:=",
                self.Transparency,
                "SmoothingLevel:=",
                self.SmoothingLevel,
                "ShadingType:=",
                self.SmoothShade,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
                "GridColor:=",
                self.GridColor,
            ],
        ]

    @property
    def field_line_trace_plot_settings(self):
        """Settings for the field line traces in the plot.

        Returns
        -------
        list
            List of settings for the field line traces in the plot.
        """
        return [
            "NAME:FieldLineTracePlotSettings",
            ["NAME:LineSettingsID", "Width:=", self.LineWidth, "Style:=", self.LineStyle],
            "IsoValType:=",
            self.IsoValType,
        ]

    @pyaedt_function_handler()
    def create(self):
        """Create a field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.seeding_faces:
                self.oField.CreateFieldPlot(self.surfacePlotInstructionLineTraces, "FieldLineTrace")
            else:
                self.oField.CreateFieldPlot(self.surfacePlotInstruction, "Field")
            if (
                "Maxwell" in self._postprocessor._app.design_type
                and "Transient" in self._postprocessor.post_solution_type
            ):
                self._postprocessor.ofieldsreporter.SetPlotsViewSolutionContext(
                    [self.name], self.solution, "Time:" + self.intrinsics["Time"]
                )
            if self.name not in self._postprocessor.field_plot_names:
                return False
            self._postprocessor.field_plots[self.name] = self
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def update(self):
        """Update the field plot.

        .. note::
           This method works on any plot created inside PyAEDT.
           For Plot already existing in AEDT Design it may produce incorrect results.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.seeding_faces:
                if self.seeding_faces[0] != len(self.seeding_faces) - 1:
                    for face in self.seeding_faces[1:]:
                        if not isinstance(face, int):
                            self._postprocessor.logger.error("Provide valid object id for seeding faces.")
                            return False
                        else:
                            if face not in list(self._postprocessor._app.modeler.objects.keys()):
                                self._postprocessor.logger.error("Invalid object id.")
                                self.seeding_faces.remove(face)
                                return False
                    self.seeding_faces[0] = len(self.seeding_faces) - 1
                if self.volumes[0] != len(self.volumes) - 1:
                    for obj in self.volumes[1:]:
                        if not isinstance(obj, int):
                            self._postprocessor.logger.error("Provide valid object id for in-volume object.")
                            return False
                        else:
                            if obj not in list(self._postprocessor._app.modeler.objects.keys()):
                                self._postprocessor.logger.error("Invalid object id.")
                                self.volumes.remove(obj)
                                return False
                    self.volumes[0] = len(self.volumes) - 1
                if self.surfaces[0] != len(self.surfaces) - 1:
                    for obj in self.surfaces[1:]:
                        if not isinstance(obj, int):
                            self._postprocessor.logger.error("Provide valid object id for surface object.")
                            return False
                        else:
                            if obj not in list(self._postprocessor._app.modeler.objects.keys()):
                                self._postprocessor.logger.error("Invalid object id.")
                                self.surfaces.remove(obj)
                                return False
                    self.surfaces[0] = len(self.surfaces) - 1
                self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstructionLineTraces)
            else:
                self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstruction)
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def update_field_plot_settings(self):
        """Modify the field plot settings.

        .. note::
            This method is not available for field plot line traces.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.oField.SetFieldPlotSettings(self.name, ["NAME:FieldsPlotItemSettings", self.plotsettings])
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the field plot."""
        self.oField.DeleteFieldPlot([self.name])
        self._postprocessor.field_plots.pop(self.name, None)

    @pyaedt_function_handler()
    def change_plot_scale(self, minimum_value, maximum_value, is_log=False, is_db=False, scale_levels=None):
        """Change Field Plot Scale.

        .. deprecated:: 0.10.1
           Use :class:`FieldPlot.folder_settings` methods instead.

        Parameters
        ----------
        minimum_value : str, float
            Minimum value of the scale.
        maximum_value : str, float
            Maximum value of the scale.
        is_log : bool, optional
            Set to ``True`` if Log Scale is setup.
        is_db : bool, optional
            Set to ``True`` if dB Scale is setup.
        scale_levels : int, optional
            Set number of color levels. The default is ``None``, in which case the
            setting is not changed.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.SetPlotFolderSettings
        """
        return self._postprocessor.change_field_plot_scale(
            self.plot_folder, minimum_value, maximum_value, is_log, is_db, scale_levels
        )

    @pyaedt_function_handler()
    def export_image(
        self,
        full_path=None,
        width=1920,
        height=1080,
        orientation="isometric",
        display_wireframe=True,
        selections=None,
        show_region=True,
        show_axis=True,
        show_grid=True,
        show_ruler=True,
    ):
        """Export the active plot to an image file.

        .. note::
           There are some limitations on HFSS 3D Layout plots.

        full_path : str or pathlib.Path, optional
            Path for saving the image file. PNG and GIF formats are supported.
            The default is ``None`` which export file in working_directory.
        width : int, optional
            Plot Width.
        height : int, optional
            Plot height.
        orientation : str, optional
            View of the exported plot. Options are ``isometric``,
            ``top``, ``bottom``, ``right``, ``left``, ``front``,
            ``back``, and any custom orientation.
        display_wireframe : bool, optional
            Whether the objects has to be put in wireframe mode. Default is ``True``.
        selections : str or List[str], optional
            Objects to fit for the zoom on the exported image.
            Default is None in which case all the objects in the design will be shown.
            One important note is that, if the fieldplot extension is larger than the
            selection extension, the fieldplot extension will be the one considered
            for the zoom of the exported image.
        show_region : bool, optional
            Whether to include the air region in the exported image. Default is ``True``.
        show_grid : bool, optional
            Whether to display the background grid in the exported image.
            Default is ``True``.
        show_axis : bool, optional
            Whether to display the axis triad in the exported image. Default is ``True``.
        show_ruler : bool, optional
            Whether to display the ruler in the exported image. Default is ``True``.

        Returns
        -------
        str
            Full path to exported file if successful.

        References
        ----------
        >>> oModule.ExportPlotImageToFile
        >>> oModule.ExportModelImageToFile
        >>> oModule.ExportPlotImageWithViewToFile
        """
        self.oField.UpdateQuantityFieldsPlots(self.plot_folder)

        # Convert pathlib.Path to string if needed
        if full_path is not None and hasattr(full_path, "__fspath__"):
            full_path = str(full_path)

        if not full_path:
            full_path = os.path.join(self._postprocessor._app.working_directory, self.name + ".png")
        status = self._postprocessor.export_field_jpg(
            full_path,
            self.name,
            self.plot_folder,
            orientation=orientation,
            width=width,
            height=height,
            display_wireframe=display_wireframe,
            selections=selections,
            show_region=show_region,
            show_axis=show_axis,
            show_grid=show_grid,
            show_ruler=show_ruler,
        )
        full_path = check_and_download_file(full_path)
        if status:
            return full_path
        else:
            return False

    @pyaedt_function_handler()
    def export_image_from_aedtplt(
        self, export_path=None, view="isometric", plot_mesh=False, scale_min=None, scale_max=None
    ):
        """Save an image of the active plot using PyVista.

        .. note::
            This method only works if the CPython with PyVista module is installed.

        Parameters
        ----------
        export_path : str or pathlib.Path, optional
            Path where image will be saved.
            The default is ``None`` which export file in working_directory.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
        plot_mesh : bool, optional
            Plot mesh.
        scale_min : float, optional
            Scale output min.
        scale_max : float, optional
            Scale output max.

        Returns
        -------
        str
            Full path to exported file if successful.

        References
        ----------
        >>> oModule.UpdateAllFieldsPlots
        >>> oModule.UpdateQuantityFieldsPlots
        >>> oModule.ExportFieldPlot
        """
        # Convert pathlib.Path to string if needed
        if export_path is not None and hasattr(export_path, "__fspath__"):
            export_path = str(export_path)

        if not export_path:
            export_path = self._postprocessor._app.working_directory
        if sys.version_info.major > 2:
            return self._postprocessor.plot_field_from_fieldplot(
                self.name,
                project_path=export_path,
                meshplot=plot_mesh,
                imageformat="jpg",
                view=view,
                plot_label=self.quantity,
                show=False,
                scale_min=scale_min,
                scale_max=scale_max,
            )
        else:
            self._postprocessor.logger.info("This method works only on CPython with PyVista")
            return False
