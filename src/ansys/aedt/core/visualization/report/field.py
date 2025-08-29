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

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.report.common import CommonReport
from ansys.aedt.core.visualization.report.standard import Standard


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

    @pyaedt_function_handler(
        app="post_app",
    )
    def __init__(self, post_app, report_category, setup_name, expressions=None):
        CommonReport.__init__(self, post_app, report_category, setup_name, expressions)
        self.domain = "Sweep"
        self.primary_sweep = "Distance"

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
        elif self._app.solution_type in ["Q3D Extractor", "2D Extractor"] and self.matrix:
            ctxt = self.matrix
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
