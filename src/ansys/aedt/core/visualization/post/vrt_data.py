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

import os

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class VRTFieldPlot(PyAedtBase):
    """Creates and edits VRT field plots for SBR+ and Creeping Waves.

    Parameters
    ----------
    postprocessor : :class:`ansys.aedt.core.modules.post_general.PostProcessor`
    is_creeping_wave : bool
        Whether it is a creeping wave model or not.
    quantity : str, optional
        Name of the plot or the name of the object.
    max_frequency : str, optional
        Maximum Frequency. The default is ``"1GHz"``.
    ray_density : int, optional
        Ray Density. The default is ``2``.
    bounces : int, optional
        Maximum number of bounces. The default is ``5``.
    intrinsics : dict, optional
        Name of the intrinsic dictionary. The default is ``{}``.

    """

    @pyaedt_function_handler(quantity_name="quantity")
    def __init__(
        self,
        postprocessor,
        is_creeping_wave=False,
        quantity="QuantityName_SBR",
        max_frequency="1GHz",
        ray_density=2,
        bounces=5,
        intrinsics=None,
    ):
        self.is_creeping_wave = is_creeping_wave
        self._postprocessor = postprocessor
        self._ofield = postprocessor.ofieldsreporter
        self.quantity = quantity
        self.intrinsics = {} if intrinsics is None else intrinsics
        self.name = "Field_Plot"
        self.plot_folder = "Field_Plot"
        self.max_frequency = max_frequency
        self.ray_density = ray_density
        self.number_of_bounces = bounces
        self.multi_bounce_ray_density_control = False
        self.mbrd_max_subdivision = 2
        self.shoot_utd_rays = False
        self.shoot_type = "All Rays"
        self.start_index = 0
        self.stop_index = 1
        self.step_index = 1
        self.is_plane_wave = True
        self.incident_theta = "0deg"
        self.incident_phi = "0deg"
        self.vertical_polarization = False
        self.custom_location = [0, 0, 0]
        self.ray_box = None
        self.ray_elevation = "0deg"
        self.ray_azimuth = "0deg"
        self.custom_coordinatesystem = 1
        self.ray_cutoff = 40
        self.sample_density = 10
        self.irregular_surface_tolerance = 50

    @property
    def intrinsicVar(self):
        """Intrinsic variable.

        Returns
        -------
        str
            Variables for the field plot.
        """
        var = ""
        for a in self.intrinsics:
            var += a + "='" + str(self.intrinsics[a]) + "' "
        return var

    @pyaedt_function_handler()
    def _create_args(self):
        args = [
            "NAME:" + self.name,
            "UserSpecifyName:=",
            0,
            "UserSpecifyFolder:=",
            0,
            "QuantityName:=",
            self.quantity,
            "PlotFolder:=",
            "Visual Ray Trace SBR",
            "IntrinsicVar:=",
            self.intrinsicVar,
            "MaxFrequency:=",
            self.max_frequency,
            "RayDensity:=",
            self.ray_density,
            "NumberBounces:=",
            self.number_of_bounces,
            "Multi-Bounce Ray Density Control:=",
            self.multi_bounce_ray_density_control,
            "MBRD Max sub divisions:=",
            self.mbrd_max_subdivision,
            "Shoot UTD Rays:=",
            self.shoot_utd_rays,
            "ShootFilterType:=",
            self.shoot_type,
        ]
        if self.shoot_type == "Rays by index":
            args.extend(
                [
                    "start index:=",
                    self.start_index,
                    "stop index:=",
                    self.stop_index,
                    "index step:=",
                    self.step_index,
                ]
            )
        elif self.shoot_type == "Rays in box":
            box_id = None
            if isinstance(self.ray_box, int):
                box_id = self.ray_box
            elif isinstance(self.ray_box, str):
                box_id = self._postprocessor._primitives.objects[self.ray_box].id
            else:
                box_id = self.ray_box.id
            args.extend("FilterBoxID:=", box_id)
        elif self.shoot_type == "Single ray":
            args.extend("Ray elevation:=", self.ray_elevation, "Ray azimuth:=", self.ray_azimuth)
        args.append("LaunchFrom:=")
        if self.is_plane_wave:
            args.append("Launch from Plane-Wave")
            args.append("Incident direction theta:=")
            args.append(self.incident_theta)
            args.append("Incident direction phi:=")
            args.append(self.incident_phi)
            args.append("Vertical Incident Polarization:=")
            args.append(self.vertical_polarization)
        else:
            args.append("Launch from Custom")
            args.append("LaunchFromPointID:=")
            args.append(-1)
            args.append("CustomLocationCoordSystem:=")
            args.append(self.custom_coordinatesystem)
            args.append("CustomLocation:=")
            args.append(self.custom_location)
        return args

    @pyaedt_function_handler()
    def _create_args_creeping(self):
        args = [
            "NAME:" + self.name,
            "UserSpecifyName:=",
            0,
            "UserSpecifyFolder:=",
            0,
            "QuantityName:=",
            self.quantity,
            "PlotFolder:=",
            "Visual Ray Trace CW",
            "IntrinsicVar:=",
            "",
            "MaxFrequency:=",
            self.max_frequency,
            "SampleDensity:=",
            self.sample_density,
            "RayCutOff:=",
            self.ray_cutoff,
            "Irregular Surface Tolerance:=",
            self.irregular_surface_tolerance,
            "LaunchFrom:=",
        ]
        if self.is_plane_wave:
            args.append("Launch from Plane-Wave")
            args.append("Incident direction theta:=")
            args.append(self.incident_theta)
            args.append("Incident direction phi:=")
            args.append(self.incident_phi)
            args.append("Vertical Incident Polarization:=")
            args.append(self.vertical_polarization)
        else:
            args.append("Launch from Custom")
            args.append("LaunchFromPointID:=")
            args.append(-1)
            args.append("CustomLocationCoordSystem:=")
            args.append(self.custom_coordinatesystem)
            args.append("CustomLocation:=")
            args.append(self.custom_location)
        args.append("SBRRayDensity:=")
        args.append(self.ray_density)
        return args

    @pyaedt_function_handler()
    def create(self):
        """Create a field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.is_creeping_wave:
                self._ofield.CreateFieldPlot(self._create_args_creeping(), "CreepingWave_VRT")
            else:
                self._ofield.CreateFieldPlot(self._create_args(), "VRT")
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def update(self):
        """Update the field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.is_creeping_wave:
                self._ofield.ModifyFieldPlot(self.name, self._create_args_creeping())

            else:
                self._ofield.ModifyFieldPlot(self.name, self._create_args())
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def delete(self):
        """Delete the field plot."""
        self._ofield.DeleteFieldPlot([self.name])
        return True

    @pyaedt_function_handler(path_to_hdm_file="path")
    def export(self, path=None):
        """Export the Visual Ray Tracing to ``hdm`` file.

        Parameters
        ----------
        path : str, optional
            Full path to the output file. The default is ``None``, in which case the file is
            exported to the working directory.

        Returns
        -------
        str
            Path to the file.
        """
        if not path:
            path = os.path.join(self._postprocessor._app.working_directory, self.name + ".hdm")
        self._ofield.ExportFieldPlot(self.name, False, path)
        return path
