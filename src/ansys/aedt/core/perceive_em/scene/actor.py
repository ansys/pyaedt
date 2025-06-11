# ruff: noqa: E402

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

import numpy as np

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.perceive_em.modules.material import MaterialManager
from ansys.aedt.core.perceive_em.visualization.load_mesh import MeshLoader


class Scene:
    def __init__(self, app):
        """
        Initialize an Actors instance.

        This class is used to store multiple actors in a scene. It is used to manage the actors in a scene.
        """
        # Private properties
        self.__app = app
        self.__rss = app.radar_sensor_scenario
        self.__api = app.api
        self.__material_manager = app.material_manager

        # Scene Node Root
        self.scene = self.__rss.SceneElement()
        self.__api.addSceneElement(self.scene)

        # Public
        self.actors = {}

    def add_actor(
        self,
        name="actor",
        input_file=None,
        material=None,
        parent_node=None,
    ):
        """
        Add an actor to the scene.

        Parameters:
        ------------
        name : str, optional
            The name of the actor. If not provided, 'actor' will be used. If the name already exists in the scene,
            it will be incremented until a unique name is found.
        input_file : str or :class:`pathlib.Path`, optional
            The filename of the actor's mesh.
        material_name : str, optional
            The material name for the actor.

        Returns:
        --------
        str
            The name of the actor added to the scene.
        """
        if name in self.actors:
            name = generate_unique_name(name)

        if parent_node is None:
            parent_node = self.scene

        if material is None:
            material = "pec"

        actor = Actor(
            app=self.__app,
            name=name,
            input_file=input_file,
            material=material,
            parent_node=parent_node,
        )

        self.actors[name] = actor
        return name


class Actor:
    def __init__(
        self,
        app,
        parent_node,
        name="Actor",
        input_file=None,
        material=None,
        color=None,
        is_antenna=False,
    ):
        """Initialize an Actor instance."""
        if material is None:
            material = "pec"

        self.__app = app

        self.name = name

        self.parts = {}

        self.bounds = None

        if input_file is not None:
            self.add_part(parent_node=parent_node, input_file=input_file, material=material)
        # Actor properties
        # self.color = color
        # self.transparency = transparency

        # self.time = 0
        # self.dt = 0
        #
        # self.bounds = None
        #
        # if is_antenna:
        #     self.actor_type = 'antenna'
        # else:
        #     self.actor_type = 'other'

        #
        # self.mesh = mesh
        # self.h_node = h_node
        # self.scale_mesh = scale_mesh
        # self.usd_actor = None
        # properties used for multi-part actors where they individual parts may have different initial conditions,
        # for example a wind turbine has blades that have a constant angular velocity, but the base of the turbine
        # is static.
        # self.initial_pos = None
        # self.initial_rot = None
        # self.initial_lin = None
        # self.initial_ang = None

        # self.previous_transform = np.eye(4)

        # self.json_base_path = None

        # if coord_sys is None:
        #     self.coord_sys = CoordSys(h_node=self.h_node,
        #                               h_mesh=self.h_mesh,
        #                               parent_h_node=parent_h_node,
        #                               target_ray_spacing=target_ray_spacing)
        # else:
        #     # if coord_sys is provided
        #     self.coord_sys = coord_sys
        # # moving h_node for easier access, but it will exist in both places
        # self.h_node = self.coord_sys.h_node
        # self.dynamic_generator_updates = dynamic_generator_updates

    def add_part(
        self,
        parent_node,
        input_file=None,
        name="geo",
        material=None,
        mesh=None,
        color=None,
        include_texture=False,
        map_texture_to_material=False,
    ):
        """
        Add a part to the actor.

        Parameters:
        ------------
        actor : Actor instance
            The actor to be added as a co-parent.
        """

        # Material must be loaded into api
        self.__app.material_manager.load_material(material)
        if material is None:
            material = "pec"

        if material.lower() == "pec":
            material_index = 0
        else:
            material_index = self.__app.material_manager.materials[material].coating_idx

        mesh_loader = MeshLoader(self.__app)

        h_mesh, mesh = mesh_loader.load_mesh(input_file=input_file, material_index=material_index)
        if hasattr(mesh, "bounds"):
            self._update_actor_bounds(mesh.bounds)

        # if mesh and filename are both none, it will add an empty actor
        self.parts[name] = Actor(
            mesh=mesh,
            h_mesh=h_mesh,
            parent_h_node=parent_h_node,
            color=color,
            include_texture=include_texture,
            map_texture_to_material=map_texture_to_material,
            dynamic_generator_updates=self.dynamic_generator_updates,
        )

        return name

    def _update_actor_bounds(self, part_bounds):
        if part_bounds is None:
            return
        if self.bounds is None:
            self.bounds = part_bounds
        else:
            self.bounds = list(self.bounds)
            self.bounds[0] = np.minimum(self.bounds[0], part_bounds[0])
            self.bounds[1] = np.maximum(self.bounds[1], part_bounds[1])
            self.bounds[2] = np.minimum(self.bounds[2], part_bounds[2])
            self.bounds[3] = np.maximum(self.bounds[3], part_bounds[3])
            self.bounds[4] = np.minimum(self.bounds[4], part_bounds[4])
            self.bounds[5] = np.maximum(self.bounds[5], part_bounds[5])
