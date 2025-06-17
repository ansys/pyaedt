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

from pathlib import Path
import sys
import warnings

from scipy.interpolate import RegularGridInterpolator

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

current_python_version = sys.version_info[:2]
if current_python_version < (3, 10):  # pragma: no cover
    raise Exception("Python 3.10 or higher is required for Monostatic RCS post-processing.")

try:
    import numpy as np
except ImportError:  # pragma: no cover
    warnings.warn(
        "The NumPy module is required to use module rcs_visualization.py.\nInstall with \n\npip install numpy"
    )
    np = None

# Check that graphics are available
try:
    check_graphics_available()
    import matplotlib.pyplot as plt
    import pyvista as pv
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


try:
    import pandas as pd
except ImportError:  # pragma: no cover
    warnings.warn(
        "The Pandas module is required to use module rcs_visualization.py.\nInstall with \n\npip install pandas"
    )
    pd = None

try:
    import scipy.interpolate
except ImportError:  # pragma: no cover
    warnings.warn(
        "The SciPy module is required to use module rcs_visualization.py.\nInstall with \n\npip install scipy"
    )


class ModelVisualization:
    def __init__(
        self,
        actors,
        size=None,
        output_name=None,
        fps=10,
        camera_orientation=None,
        camera_attachment=None,
        camera_position=None,
    ):
        """
        Provides a 3D visualization tool for dynamic scenes composed of multiple actors using PyVista.

        This class enables animation generation, camera control, and frame-by-frame transformation updates
        for 3D models (actors) with part-based hierarchical structure.

        Parameters
        ----------
        actors : dict
            Dictionary of all actors in the scene, where keys are actor names and values are actor objects.
        size : tuple, optional
            Window size for the PyVista render window. The default is ``(1280, 720)``.
        output_name : str, optional
            Filename for the generated video output. The default is ``"output_geometry.mp4"``.
        fps : int, optional
            Frame rate for the output video. The default is ``10``.
        camera_orientation : str or dict, optional
            Defines the camera's orientation strategy for example ``"follow"``, ``"top"``, ``"side"``.
        camera_attachment : str, optional
            Name of the actor the camera should follow or be attached to.
        camera_position : list, optional
            Custom camera position vector, it overrides the default positioning.
        """
        if size is None:
            size = (1280, 720)

        if output_name is None:
            output_name = f"output_geometry.mp4"

        # All actors in scene
        self.actor = actors

        self.ax = None
        self.fig = None

        # Create a PyVista plotter
        self.pl = pv.Plotter(window_size=size)
        self.pl.open_movie(output_name, framerate=fps)

        # Camera_orientation is a string that can be 'scene_top', 'follow', 'side', 'top', 'front', 'radar'
        self.camera_orientation = camera_orientation
        # Camera_attachment is the name of the actor that the camera will be attached to
        self.camera_attachment = camera_attachment
        self.camera_position = camera_position

        self.scene_index_counter = 0

        if isinstance(actors, dict):
            for actor in actors:
                self._add_parts_to_scene(actors[actor])
        else:
            logger.error("No actors found in scene")

        self._camera_view()

    def update_frame(self, write_frame=True, update_camera_view=True):
        """
        Update the scene by transforming all actors and optionally rendering the frame.

        Parameters
        ----------
        write_frame : bool, optional
            If True, writes the current frame to the output video. If False, opens a live rendering window.
        update_camera_view : bool, optional
            If True, updates the camera based on orientation and attachment logic.

        Returns
        -------
        None
        """
        for actor in list(self.actor.keys()):
            self._update_parts_in_scene(self.actor[actor])

        # only update camera view on the first frame, or if update_camera_view is set to True
        if self.scene_index_counter == 0 or update_camera_view:
            self._camera_view()

        if write_frame:
            self.pl.write_frame()
        else:
            self.pl.show()
        self.scene_index_counter += 1

    def close(self):
        """
        Finalize and close the PyVista movie file.

        Returns
        -------
        None
        """
        self.pl.close()

    def _add_parts_to_scene(self, actor):
        """
        Add mesh parts of an actor to the PyVista scene, applying visual properties like color and transparency.

        Parameters
        ----------
        actor : :class:`ansys.aedt.core.perceive_em.scene.actors.Actor`
            An actor object containing mesh parts and metadata.

        Returns
        -------
        None
        """
        if hasattr(actor, "antenna_devices"):
            for antenna_device in actor.antenna_devices.values():
                active_mode = antenna_device.active_mode
                for antenna_tx in active_mode.antennas_tx.values():
                    options = {}
                    options["cmap"] = "jet"
                    options["show_scalar_bar"] = False
                    antenna_tx.mesh.scale(antenna_tx.scale_mesh, inplace=True)
                    self.pl.add_mesh(antenna_tx.mesh, **options)

                for antenna_rx in active_mode.antennas_rx.values():
                    options = {}
                    options["cmap"] = "jet"
                    options["show_scalar_bar"] = False
                    antenna_rx.mesh.scale(antenna_rx.scale_mesh, inplace=True)
                    self.pl.add_mesh(antenna_rx.mesh, **options)

        else:
            for part in actor.part_names:
                part_actor = actor.parts[part]
                if part_actor and getattr(part_actor, "mesh_properties", None):
                    options = {}

                    if part_actor.mesh_properties.get("color", None) is not None:
                        options["color"] = part_actor.mesh_properties["color"]

                    if part_actor.mesh_properties.get("transparency", None) is not None:
                        options["use_transparency"] = True
                        options["opacity"] = part_actor.mesh_properties["transparency"]

                    part_actor._pv_actor = self.pl.add_mesh(part_actor.mesh, **options)

    def _update_parts_in_scene(self, actor):
        """
        Update the transformation of an actor and its parts based on coordinate system changes.

        Parameters
        ----------
        actor : :class:`ansys.aedt.core.perceive_em.scene.actors.Actor`
            An actor object with parts to be transformed based on coordinate systems.

        Returns
        -------
        None
        """
        if hasattr(actor, "mesh") and actor.mesh is not None:
            T = actor.coordinate_system.transformation_matrix  # current 4x4 transform
            previous_T = actor._previous_transform  # previous 4x4 transform
            total_transform = np.matmul(
                T, np.linalg.inv(previous_T)
            )  # current transform relative to previous transform
            if hasattr(actor, "mesh"):
                if actor.mesh is not None:
                    actor.mesh.transform(total_transform, inplace=True)  # update positions
            actor._previous_transform = T  # store previous transform for next iteration

        if hasattr(actor, "parts"):
            for part_name, part in actor.parts.items():
                T = part.coordinate_system.transformation_matrix  # current 4x4 transform
                previous_T = part._previous_transform  # previous 4x4 transform
                total_transform = np.matmul(
                    T, np.linalg.inv(previous_T)
                )  # current transform relative to previous transform

                if getattr(part, "mesh", None) is not None:
                    part.mesh.transform(total_transform, inplace=True)

                part._previous_transform = T  # store previous transform for next iteration
                if len(part.parts) > 0:
                    for child_part in part.parts:
                        self._update_parts_in_scene(part.parts[child_part])

        if hasattr(actor, "antenna_devices"):
            for device_name, antenna_device in actor.antenna_devices.items():
                active_mode = antenna_device.active_mode
                for antenna_rx in active_mode.antennas_rx.values():
                    self._update_parts_in_scene(antenna_rx)
                for antenna_tx in active_mode.antennas_tx.values():
                    self._update_parts_in_scene(antenna_tx)

    def _camera_view(self, camera_attachment=None):
        """
        Adjust the camera view based on the specified orientation, attachment, and optional static position.

        Parameters
        ----------
        camera_attachment : str, optional
            Override for the default camera attachment target (actor name).

        Returns
        -------
        None
        """
        if self.camera_position is not None:
            self.pl.camera_position = self.camera_position
            return

        # if we did want to change attachment, we would do it here, otherwise it is set when the scene is initialized
        if camera_attachment is None:
            camera_attachment = self.camera_attachment

        if camera_attachment is None and self.camera_orientation is None:
            return
        if camera_attachment not in self.actor.keys():
            print(f"Camera attachment {camera_attachment} not found in scene")
            return
        cam_transform = self.actor[camera_attachment].coord_sys.transformation_matrix
        cam_pos = cam_transform[0:3, 3]
        cam_rot = cam_transform[0:3, 0:3]

        if self.camera_orientation is not None:
            if isinstance(self.camera_orientation, str):
                if self.camera_orientation.lower() == "scene_top":
                    cam_offset = [0, 0, 100]
                    focal_offset = [0, 0, 0]
                    self.pl.camera_position = "xy"
                elif self.camera_orientation.lower() == "follow":
                    cam_offset = [-10, 0, 3]  # Third person view
                    focal_offset = [25, 0, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 80
                elif self.camera_orientation.lower() == "follow2":
                    cam_offset = [-20, 0, 6]  # Third person view
                    focal_offset = [30, 0, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 80
                elif self.camera_orientation.lower() == "follow3":
                    cam_offset = [-30, 0, 9]  # Third person view
                    focal_offset = [50, 0, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 80
                elif self.camera_orientation.lower() == "follow4":
                    cam_offset = [-2, 0, 1]  # Third person view
                    focal_offset = [10, 0, 0.1]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 88
                elif self.camera_orientation.lower() == "follow5":
                    cam_offset = [-2, 0, 2]  # Third person view
                    focal_offset = [10, 0, 0.1]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 80
                elif self.camera_orientation.lower() == "follow6":
                    cam_offset = [-1, 0, 1.5]  # Third person view
                    focal_offset = [10, 0, -0.1]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 75
                elif self.camera_orientation.lower() == "follow7":
                    cam_offset = [-150, 0, 50]  # Third person view
                    focal_offset = [50, 0, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 60
                elif self.camera_orientation.lower() == "follow8":
                    cam_offset = [-0.5, 0, 0.25]  # Third person view
                    focal_offset = [1, 0, 0]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 75
                elif self.camera_orientation.lower() == "side":
                    cam_offset = [1, -8, 1]  # Third person view
                    focal_offset = [0, 25, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                elif self.camera_orientation.lower() == "top":
                    cam_offset = [0, 0, 15]  # Third person view
                    focal_offset = [0, 0, 0]
                    self.pl.camera.up = (1.0, 0.0, 0.0)
                elif self.camera_orientation.lower() == "front":
                    cam_offset = [14, 0, 3]  # Third person view
                    focal_offset = [-10, 0, 0]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                elif self.camera_orientation.lower() == "radar":
                    cam_offset = [0, 0, 0]  #
                    focal_offset = [25, 0, 0]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
                    self.pl.camera.view_angle = 80
                else:
                    cam_offset = [-12, 0, 3]  # Third person view
                    focal_offset = [25, 0, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)
            elif isinstance(self.camera_orientation, dict):
                cam_offset = self.camera_orientation["cam_offset"]
                focal_offset = self.camera_orientation["focal_offset"]
                self.pl.camera.up = self.camera_orientation["up"]
                self.pl.camera.view_angle = self.camera_orientation["view_angle"]

            cam_offset = (
                cam_offset[0] * cam_rot[:3, 0] + cam_offset[1] * cam_rot[:3, 1] + cam_offset[2] * cam_rot[:3, 2]
            )
            camera_pos = cam_pos + cam_offset
            focal_cam_offset = (
                focal_offset[0] * cam_rot[:3, 0] + focal_offset[1] * cam_rot[:3, 1] + focal_offset[2] * cam_rot[:3, 2]
            )
            focal_pos = cam_pos + focal_cam_offset
            self.pl.camera.position = camera_pos
            self.pl.camera.focal_point = focal_pos
