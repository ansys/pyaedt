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
import tempfile
import warnings

import numpy as np

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available

# Check that graphics are available
try:
    check_graphics_available()
    import pyvista as pv
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


class SceneVisualization:
    def __init__(
        self,
        actors,
        size=None,
        output_file=None,
        frame_rate=10,
        camera_orientation=None,
        camera_attachment=None,
        camera_position=None,
        show=True,
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
        output_file : str or :class:`pathlib.Path`, optional
            Full path to the mesh statistics file. The default is ``None``, in which
            case the working directory is used.
        frame_rate : int, optional
            Frame rate for the output video. The default is ``10``.
        camera_orientation : str or dict, optional
            Defines the camera's orientation strategy. Available options are: ``"follow"``, ``"top"``, ``"side"``,
            ``"scene_top"``, ``"front"``, and ``"first_person"``.
        camera_attachment : str, optional
            Name of the actor the camera should follow or be attached to.
        camera_position : list, optional
            Custom camera position vector, it overrides the default positioning.
        show : bool, optional
            Show the plot after generation.  The default value is ``True``.
        """
        if size is None:
            size = (1280, 720)

        if output_file is None:
            output_file = Path(tempfile.gettempdir()) / "output_geometry.mp4"

        off_screen = False
        if not show:
            off_screen = True

        # All actors in scene
        self.__actors = actors

        # Create a PyVista plotter
        self.pl = pv.Plotter(window_size=size, off_screen=off_screen)
        self.pl.open_movie(output_file, framerate=frame_rate)

        # Camera_orientation is a string that can be 'scene_top', 'follow', 'side', 'top', 'front'
        self.__camera_orientation = camera_orientation

        # Camera_attachment is the name of the actor that the camera will be attached to
        self.__camera_attachment = camera_attachment

        self.__camera_position = camera_position

        self.scene_index_counter = 0

        if isinstance(actors, dict):
            for actor in actors:
                self._add_parts_to_scene(actors[actor])
        else:
            logger.error("No actors found in scene")

        self._camera_view()

    @property
    def actors(self):
        """Available actors in the scene."""
        return self.__actors

    @property
    def camera_orientation(self) -> str:
        """Camera orientation"""
        return self.__camera_orientation

    @camera_orientation.setter
    def camera_orientation(self, value):
        if (
            value is not None
            and isinstance(value, str)
            and value not in ["top", "side", "follow", "scene_top", "front", "first_person"]
        ):
            raise ValueError("Invalid camera orientation.")
        self.__camera_orientation = value

    @property
    def camera_attachment(self) -> str:
        """Camera attachment"""
        return self.__camera_attachment

    @camera_attachment.setter
    def camera_attachment(self, value):
        if value is not None and value not in self.actors:
            raise ValueError("Actor not found.")
        self.__camera_attachment = value

    @property
    def camera_position(self):
        """Camera position"""
        return self.__camera_position

    @camera_position.setter
    def camera_position(self, value):
        self.__camera_position = value

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
        for actor in list(self.actors.keys()):
            self._update_parts_in_scene(self.actors[actor])

        # only update camera view on the first frame, or if update_camera_view is set to True
        if self.scene_index_counter == 0 or update_camera_view:
            self._camera_view()

        if write_frame:
            self.pl.write_frame()
        else:  # pragma: no cover
            self.pl.show()
        self.scene_index_counter += 1
        return True

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
                    options = {"cmap": "jet", "show_scalar_bar": False}
                    antenna_tx.mesh.scale(antenna_tx.scale_mesh, inplace=True)
                    self.pl.add_mesh(antenna_tx.mesh, **options)

                for antenna_rx in active_mode.antennas_rx.values():
                    options = {"cmap": "jet", "show_scalar_bar": False}
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
            for _, part in actor.parts.items():
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
            for _, antenna_device in actor.antenna_devices.items():
                active_mode = antenna_device.active_mode
                for antenna_rx in active_mode.antennas_rx.values():
                    self._update_parts_in_scene(antenna_rx)
                for antenna_tx in active_mode.antennas_tx.values():
                    self._update_parts_in_scene(antenna_tx)

    def _camera_view(self):
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
            return True

        if self.camera_attachment is None and self.camera_orientation is None:
            return True

        cam_offset = [0, 0, 0]
        focal_offset = [0, 0, 0]

        if self.camera_orientation is not None:
            if isinstance(self.camera_orientation, str):
                orientation = self.camera_orientation.lower()

                if orientation == "scene_top":
                    self.pl.camera_position = "xy"
                    return True

                elif orientation == "first_person":
                    cam_offset = [0, 0, 0]  # Exact position of the actors
                    focal_offset = [1.0, 0.0, 0.0]  # Forward in local X
                    self.pl.camera.up = (0.0, 0.0, 1.0)

                elif orientation == "side":
                    cam_offset = [1, -8, 1]
                    focal_offset = [0, 25, 0.5]
                    self.pl.camera.up = (0.0, 0.0, 1.0)

                elif orientation == "top":
                    cam_offset = [0, 0, 15]
                    focal_offset = [0, 0, 0]
                    self.pl.camera.up = (1.0, 0.0, 0.0)

                elif orientation == "front":
                    cam_offset = [14, 0, 3]
                    focal_offset = [-10, 0, 0]
                    self.pl.camera.up = (0.0, 0.0, 1.0)

            elif isinstance(self.camera_orientation, dict):
                self.pl.camera.up = self.camera_orientation["up"]
                self.pl.camera.view_angle = self.camera_orientation["view_angle"]
                self.pl.camera.position = self.camera_orientation["position"]
                self.pl.camera.focal_point = self.camera_orientation["focal_point"]
                return True

            # If camera is to be attached to an actors
            if self.camera_attachment is not None:
                if self.camera_attachment not in self.actors:  # pragma: no cover
                    print(f"Camera attachment {self.camera_attachment} not found in scene")
                    return False

                cam_transform = self.actors[self.camera_attachment].coordinate_system.transformation_matrix
                cam_pos = cam_transform[0:3, 3]
                cam_rot = cam_transform[0:3, 0:3]

                cam_offset = (
                    cam_offset[0] * cam_rot[:, 0] + cam_offset[1] * cam_rot[:, 1] + cam_offset[2] * cam_rot[:, 2]
                )

                camera_pos = cam_pos + cam_offset

                focal_cam_offset = (
                    focal_offset[0] * cam_rot[:, 0] + focal_offset[1] * cam_rot[:, 1] + focal_offset[2] * cam_rot[:, 2]
                )
                focal_pos = cam_pos + focal_cam_offset

                self.pl.camera.position = camera_pos
                self.pl.camera.focal_point = focal_pos
                return True
