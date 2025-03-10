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

"""
This module contains these classes: `AntennaParameters`, `Fields`, `NearField`, `FarField`, and `Emission`.

This module provides all functionalities for creating and editing reports.

"""
import warnings
import csv
import math
import os

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.report.common import CommonReport
from ansys.aedt.core.visualization.report.standard import Standard
from ansys.aedt.core.generic.file_utils import open_file

try:
    import pyvista as pv

    pyvista_available = True
except ImportError:
    warnings.warn(
        "The PyVista module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install pyvista"
    )


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
        if self._is_created:
            try:
                self._legacy_props["context"]["far_field_sphere"] = self.traces[0].properties["Geometry"]
            except Exception:
                self._post._app.logger.warning("Property `far_field_sphere` not found.")

        return self._legacy_props["context"].get("far_field_sphere", None)

    @far_field_sphere.setter
    def far_field_sphere(self, value):
        self._legacy_props["context"]["far_field_sphere"] = value

    @property
    def _context(self):
        ctxt = ["Context:=", self.far_field_sphere]
        return ctxt


class Fields(CommonReport):
    """Handler to manage fields."""

    # TODO: Allow Fields instance to be initiated by passing a file name with field data.
    @pyaedt_function_handler(
        app="post_app",
    )
    def __init__(self, post_app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, post_app, report_category, setup_name, expressions)
        self.domain = "Sweep"
        self.primary_sweep = "Distance"
        self._polydata = pv.PolyData()  # Use the PyVista PolyData class to save field data.
        self.path = None

    @property
    def point_number(self):
        """Polygon point number.

        Returns
        -------
        str
            Point number.
        """
        return self._legacy_props["context"].get("point_number", 1001)

    @point_number.setter
    def point_number(self, value):
        self._legacy_props["context"]["point_number"] = value

    @property
    def _context(self):
        ctxt = []
        if self.polyline:
            ctxt = ["Context:=", self.polyline, "PointCount:=", self.point_number]
        return ctxt

    @pyaedt_function_handler()
    def read_file(self, filename):  # TODO: Improve checking for file type and validity.
        if not self.path:
            self.path = filename
        else:
            warnings.warn("Path already defined for this field quantity.")
        if ".case" in filename:
            reader = pv.get_reader(os.path.abspath(self.path)).read()
            self._polydata = reader[reader.keys()[0]].extract_surface()

            if (
                hasattr(self._polydata.point_data, "active_vectors")
                and self._polydata.point_data.active_vectors_name
            ):
                self.scalar_name = self._polydata.point_data.active_scalars_name
                vector_scale = (max(self._polydata.bounds) - min(self._polydata.bounds)) / (
                    10
                    * (
                        np.vstack(self._polydata.active_vectors).max()
                        - np.vstack(self._polydata.active_vectors).min()
                    )
                )
                self._polydata["vectors"] = self._polydata.active_vectors * vector_scale

                self.is_vector = True
            else:
                self.scalar_name = self._polydata.point_data.active_scalars_name
        elif ".aedtplt" in self.path:  # pragma no cover
            vertices, faces, scalars, log1 = _parse_aedtplt(self.path)
            if self.convert_fields_in_db:
                scalars = [np.multiply(np.log10(i), self.log_multiplier) for i in scalars]
            fields_vals = pv.PolyData(vertices[0], faces[0])
            self._polydata = fields_vals
            if isinstance(scalars[0], list):
                vector_scale = (max(fields_vals.bounds) - min(fields_vals.bounds)) / (
                    50 * (np.vstack(scalars[0]).max() - np.vstack(scalars[0]).min())
                )

                self._polydata["vectors"] = np.vstack(scalars).T * vector_scale
                self.label = "Vector " + self.label
                self._polydata.point_data[self.label] = np.array(
                    [np.linalg.norm(x) for x in np.vstack(scalars[0]).T]
                )
                try:
                    self.scalar_name = self._polydata.point_data.active_scalars_name + " Magnitude"
                    self.is_vector = True
                except Exception:
                    self.is_vector = False
            else:
                self._polydata.point_data[self.label] = scalars[0]
                self.scalar_name = self._polydata.point_data.active_scalars_name
                self.is_vector = False
            self.log = log1
        else:
            nodes = []
            values = []
            is_vector = False
            with open_file(self.path, "r") as f:
                try:
                    lines = f.read().splitlines()[self.header_lines :]
                    if ".csv" in self.path:
                        sniffer = csv.Sniffer()
                        delimiter = sniffer.sniff(lines[0]).delimiter
                    else:
                        delimiter = " "
                    if len(lines) > 2000 and not self._is_frame:
                        lines = list(dict.fromkeys(lines))
                except Exception:
                    lines = []
                for line in lines:
                    tmp = line.strip().split(delimiter)
                    if len(tmp) < 4:
                        continue
                    nodes.append([float(tmp[0]), float(tmp[1]), float(tmp[2])])
                    if len(tmp) == 6:
                        values.append([float(tmp[3]), float(tmp[4]), float(tmp[5])])
                        is_vector = True
                    elif len(tmp) == 9:
                        values.append([float(tmp[3]), float(tmp[5]), float(tmp[7])])
                        is_vector = True
                    else:
                        values.append(float(tmp[3]))
            if nodes:
                try:
                    conv = 1 / AEDT_UNITS["Length"][self.units]
                except Exception:
                    conv = 1
                vertices = np.array(nodes) * conv
                filedata = pv.PolyData(vertices)
                if is_vector:
                    vector_scale = (max(filedata.bounds) - min(filedata.bounds)) / (
                        20 * (np.vstack(values).max() - np.vstack(values).min())
                    )
                    filedata["vectors"] = np.vstack(values) * vector_scale
                    self.label = "Vector " + self.label
                    filedata.point_data[self.label] = np.array([np.linalg.norm(x) for x in np.vstack(values)])
                    self.scalar_name = self._polydata.point_data.active_scalars_name
                    self.is_vector = True
                else:
                    filedata = filedata.delaunay_2d(tol=self.surface_mapping_tolerance)
                    filedata.point_data[self.label] = np.array(values)
                    self.scalar_name = filedata.point_data.active_scalars_name
                self._polydata = filedata


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
        return self._legacy_props["context"].get("near_field", None)

    @near_field.setter
    def near_field(self, value):
        self._legacy_props["context"]["near_field"] = value


class FarField(CommonReport):
    """Provides for managing far field reports."""

    def __init__(self, app, report_category, setup_name, expressions=None, **variations):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        variation_defaults = {"Phi": ["All"], "Theta": ["All"], "Freq": ["Nominal"]}
        self.domain = "Sweep"
        self.primary_sweep = "Phi"
        self.secondary_sweep = "Theta"
        self.source_context = None
        self.source_group = None
        for key, default_value in variation_defaults.items():
            if key in variations:
                self.variations[key] = variations[key]
            else:
                self.variations[key] = default_value

    @property
    def far_field_sphere(self):
        """Far field sphere name.

        Returns
        -------
        str
            Field name.
        """
        if self._is_created:
            try:
                self._legacy_props["context"]["far_field_sphere"] = self.traces[0].properties["Geometry"]
            except Exception:
                self._post._app.logger.warning("Property `far_field_sphere` not found.")
        return self._legacy_props["context"].get("far_field_sphere", None)

    @far_field_sphere.setter
    def far_field_sphere(self, value):
        self._legacy_props["context"]["far_field_sphere"] = value

    @property
    def _context(self):
        if self.source_context:
            return ["Context:=", self.far_field_sphere, "SourceContext:=", self.source_context]
        if self.source_group:
            return ["Context:=", self.far_field_sphere, "Source Group:=", self.source_group]
        return ["Context:=", self.far_field_sphere]


class Emission(CommonReport):
    """Provides for managing emission reports."""

    def __init__(self, app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, app, report_category, setup_name, expressions)
        self.domain = "Sweep"
